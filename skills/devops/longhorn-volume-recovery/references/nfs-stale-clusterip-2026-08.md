---
name: longhorn-volume-recovery
type: reference
description: NPO-queue wedge + stale ClusterIP diagnosis — 2026-08-28 nishir incident.
parent_skill: longhorn-volume-recovery
---

# NPO-queue wedge: nishir cluster, 2026-08-28

## Incident summary

Both `qbittorrent-0` and `whisparr-0` (pod UIDs `55cf2b35` and
`00486449`) stuck in `ContainerCreating` on nalsha after the share-manager
pod for `downloads-whisparr-data` restarted ~5h33m ago, changing its
Service ClusterIP. Root cause: kubelet's nested-pending-operation (NPO)
queue held a dead volume lock from a failed subpath cleanup; the retry
window closed before the lazy unmount completed.

## Failure chain

1. **share-manager restart → stale ClusterIP.** The SM pod restarted
   2026-08-28T05:44, Service got a new ClusterIP (`10.109.237.62` vs
   old `10.104.70.211`).
2. **NFS mounts stale.** All kubelet NFS mounts on nalsha still pointed
   at the old IP. Direct `mount -t nfs4` test against old IP: no response
   (no export at old IP, not just stale cache).
3. **Deleted pod subpath cleanup failure.** Pod `1998f065` (qbittorrent-0
   predecessor) had subpath mounts at
   `/var/lib/kubelet/pods/1998f065/volume-subpaths/downloads-whisparr-data/qbittorrent/`
   . Lazy unmount (`-l`) cleared these. But the `kubelet` pod-worker log
   showed `"device is busy"` at 19:34:17 when trying to clean them
   *without* `-l` — the synchronous unmount hit the active nfs4 mount and
   failed.
4. **NPO queue permanently wedged.** Kubelet's NPO queue records each
   volume operation with a retry-after timestamp. When the failed subpath
   cleanup's retry window closed (no more retries permitted), the entry
   became permanently dead. All subsequent mount attempts for that volume —
   even from completely different pods with fresh UIDs — are queued behind
   the dead entry and never reach the CSI plugin.
5. **Multiple pods blocked simultaneously.** Both qbittorrent-0 (UID
   `55cf2b35`) and whisparr-0 (UID `00486449`) are blocked — the stale mounts
   affect every pod that needs the volume, not just one.

## Key log signatures

### NPO queue failure (the permanent lock)

```
E0828 19:34:17.585514 nestedpendingoperations.go:348] \
  Operation for "{volumeName:kubernetes.io/csi/driver.longhorn.io^downloads-whisparr-data podName:1998f065-97f8-467c-a9c3-5f23fed8c440 nodeName:}" failed. \
  No retries permitted until 2026-08-28 19:34:18.085294397 +0000 UTC. \
  (durationBeforeRetry 500ms). Error: error cleaning subPath mounts for volume...\
  ...: error cleaning subpath mount /var/lib/kubelet/pods/.../qbittorrent/7: \
  unmount failed: exit status 16\n  Unmounting arguments: .../qbittorrent/7\n  Output: umount.nfs4: .../qbittorrent/7: device is busy
```

### Pod sync loop (repeated, no progress)

```
E0828 19:34:44 pod_workers.go:1324] "Error syncing pod, skipping" \
  err="unmounted volumes=[downloads-whisparr-data], unattached volumes=[], \
  failed to process volumes=[]: context canceled" pod="shikanime/qbittorrent-0"
E0828 19:35:18 pod_workers.go:1324] "Error syncing pod, skipping" \
  err="...context deadline exceeded" pod="shikanime/whisparr-0"
```

### CSI plugin silence

No `NodeStageVolume`/`NodePublishVolume` line for `downloads-whisparr-data`
in the kubelet log for either pod UID. Not even a failing call. The CSI
plugin was never invoked.

## Verification checklist (before touching anything)

```bash
export K="kubectl --context nishir-k8s-operator.taila659a.ts.net"

# 1. Current ClusterIP vs mounted IP
$K -n longhorn-system get svc downloads-whisparr-data \
  -o jsonpath='{.spec.clusterIP}'   # should be 10.109.237.62
ssh nalsha 'mount | grep downloads-whisparr'
# → stale mounts show 10.104.70.211; this is the gap.

# 2. share-manager health
$K -n longhorn-system get pod share-manager-downloads-whisparr-data
# → must be Running; if not, fix that first.

# 3. Dry reachability test (no side effect)
ssh nalsha \
  'mount -t nfs4 -o vers=4.1,soft,timeo=3,retrans=2,noresvport \
  10.109.237.62:/downloads-whisparr-data /tmp/nfs-test && \
  ls /tmp/nfs-test && \
  umount -l /tmp/nfs-test'
# → data visible; confirms share-manager + current ClusterIP are healthy.

# 4. NPO wedge signature
ssh nalsha \
  'grep -i downloads-whisparr /var/lib/rancher/rke2/agent/logs/kubelet.log | tail -30'
# → look for: repeated pod_workers "context deadline exceeded" + one
#   nestedpendingoperations "device is busy" referencing a DELETED pod UID.
```

## Remediation (ordered)

```bash
# Step 1: lazy-unmount stale NFS mounts
ssh nalsha
umount -l /var/lib/kubelet/pods/1998f065-*/volume-subpaths/downloads-whisparr-data 2>/dev/null || true
# Verify: mount | grep 10.104.70.211 → gone

# Step 2: restart kubelet (clears NPO queue + pending-operation backlog)
# On RKE2, this is done via rke2-server restart.
# Safe on a control-plane node when cluster has ≥3 CP nodes.
ssh nalsha
systemctl restart rke2-server
# Wait for node Ready: $K get node nalsha

# Step 3: recreate stuck pods
$K -n shikanime delete pod qbittorrent-0 whisparr-0
# StatefulSet recreates them; verify 1/1 Running.

# Step 4: verify mount + data
ssh nalsha 'mount | grep downloads-whisparr'
# → shows current ClusterIP
$K -n shikanime exec qbittorrent-0 -- ls /downloads/whisparr/
# → data visible
```

## Why kubelet doesn't retry (the queue model)

Each kubelet volume operation has three state transitions:

1. **Enqueued** — kubelet adds the operation to the NPO queue with a
   `retry-after` timestamp derived from exponential backoff.
2. **Retries** — while `now < retry-after`, the operation is retried
   (e.g. mount, attach, subpath cleanup). Each retry is a new queue entry.
3. **No more retries** — when `now >= retry-after`, the operation is
   permanently marked failed. A new operation for the same volume (even with
   a different pod UID, different CSI volume handle, or fresh mounts) is
   added to the queue AFTER the dead entry. It will never be dispatched
   because the queue iterator reaches the dead entry first and stops.

The failed subpath cleanup's retry window closed at 19:34:18. The lazy
unmount (physical umount) happened ~2 minutes later at 19:36. By then, the
queue was permanently blocked.

A restart of kubelet clears the entire NPO queue and the pending-operation
backlog, which is why it's the fix — not just for the NPO-wedge, but for
any case where kubelet's in-memory volume operation state has become
corrupted.
