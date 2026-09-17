---
name: longhorn-volume-recovery
description: Use when a Longhorn volume fails: pods stuck Pending/Init on mounts, share-manager crash-loops, dirty XFS log, or volumes stuck degraded/faulted/detached — diagnose and recover.
version: 1.0.0
author: hermes
license: CC-BY-4.0
metadata:
  hermes:
    tags: [kubernetes, longhorn, xfs, storage, recovery, nishir]
    related_skills: [verify-k8s-crds, tailnet-acl]
---

# Longhorn Volume Recovery (nishir cluster)

## When to Use

Use when a Longhorn-backed workload on the `nishir` cluster (context `nishir-k8s-operator.taila659a.ts.net`) has: pods stuck `Pending`/`Init` on volume mounts, share-manager pods crash-looping `starting`/`Failed`, mount errors mentioning XFS or `Failed to recover intents`, or a kubelet that stages CSI volumes but never starts containers. Also before any storage-class migration that detaches RWX volumes — the dirty-log failure mode is that migration's aftermath. RWX volumes serve through share-manager pods over NFS; RWO/RWO-Pod volumes serve block devices.

## Signature: dirty XFS log (most common)

A share-manager cycling `starting`→`Failed` with mount errors means the underlying XFS filesystem has a dirty/aborted log (after unclean shutdowns, crashes, or storage-class churn migrations). Confirm before touching anything:
```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
# sharemanager state + SM pod recycling
$K -n longhorn-system get sharemanager <vol> -o jsonpath='state={.status.state}{"\n"}'
# dmesg on the engine node shows the real cause
#   "Failed to recover intents" + "log mount finish failed" = dirty log
```

## Repair procedure (ordered, exact)

1. **Find the engine node** (the only manager whose pod can see the device):
   ```bash
   $K -n longhorn-system get engines.longhorn.io -o json | jq -r \
     '.items[] | select(.spec.volumeName=="<vol>") | .spec.nodeID'
   MGR=$($K -n longhorn-system get pods -o json | jq -r \
     '.items[] | select(.spec.nodeName=="<node>" and (.metadata.name|test("longhorn-manager"))) | .metadata.name')
   ```
2. **Dry-run first** — verdict via EXIT marker, not the stream (tailnet drops exec stdout under load; the `-n` run is read-only so it is harmless):
   ```bash
   $K -n longhorn-system exec $MGR -c longhorn-manager -- sh -c \
     'setsid sh -c "xfs_repair -n /host/dev/longhorn/<vol> > /tmp/dry.log 2>&1; echo EXIT=\$? >> /tmp/dry.log" < /dev/null > /dev/null 2>&1 &'
   # poll /tmp/dry.log until EXIT= appears
   ```
   `/host/tmp` does NOT exist in the manager container — use `/tmp`.
3. **RWX volumes: flip accessMode RWX→RWO FIRST — this IS the maintenance-mode blockdev attach.** A RWX volume's block device is owned by the ShareManager CR, which the volume controller recreates whenever it exists, so deleting the share-manager *pod* is futile: the CR respawns it and drags the engine to a fresh node mid-repair (`No such device` / `read only 0 of 4096`). `nodeID` pin, `disableFrontend:true`, Longhorn `allowScheduling=false`, and node cordons ALL fail to stop the pod. Only removing the RWX frontend (to RWO) deletes the ShareManager CR and makes `/dev/longhorn/<vol>` a stable, unmounted block device. (Doc basis: longhorn.io KB troubleshooting-volume-filesystem-corruption + discussion #4682 — read BEFORE improvising; the UI "maintenance mode" attach alone does NOT create the block device for an RWX volume.)
   ```bash
   # 1) snapshot for safety (KB warning: an incorrect fix can lose data)
   $K -n longhorn-system create -f - <<EOF
   apiVersion: longhorn.io/v1beta2
   kind: Snapshot
   metadata:
     name: <vol>-prerepair-$(date +%Y%m%d-%H%M%S)
     namespace: longhorn-system
   spec:
     volume: <vol>
     labels: {intent: pre-xfs-repair}
   EOF
   # 2) flip RWX->RWO (deletes ShareManager CR; volume detaches, re-attaches RWO)
   $K -n longhorn-system patch volume <vol> --type=merge -p '{"spec":{"accessMode":"rwo","nodeID":""}}'
   # 3) confirm: SM CR + pod GONE, volume attached RWO, device present + unmounted
   $K -n longhorn-system get sharemanager <vol>            # expect NotFound
   $K -n longhorn-system get pod share-manager-<vol>       # expect NotFound
   NODE=$($K -n longhorn-system get volume <vol> -o jsonpath='{.status.currentNodeID}')
   $K -n longhorn-system patch volume <vol> --type=merge -p "{\"spec\":{\"nodeID\":\"$NODE\"}}"
   ```
   On that node's manager pod verify: `ls -la /host/dev/longhorn/<vol>` exists AND `mount | grep <vol>` shows NOT MOUNTED. (RWO/RWO-Pod volumes: no ShareManager CR — skip the flip; ensure the volume is attached to one node with consumers scaled to 0, then repair.)
4. **Repair** (no `-L` unless step 5 fails) against the raw block device:
   ```bash
   $K -n longhorn-system exec $MGR -c longhorn-manager -- sh -c \
     'setsid sh -c "xfs_repair -o ag_stride=32 /host/dev/longhorn/<vol> > /tmp/fix.log 2>&1; echo EXIT=\$? >> /tmp/fix.log" < /dev/null > /dev/null 2>&1 &'
   ```
   A 1Ti repair runs several minutes and holds the device open the whole time. A second `xfs_repair` on the same device returning `Device or resource busy` means the FIRST repair is still running — not failed. Poll `/tmp/fix.log` for `EXIT=`; completion prints `Phase 7 ... Format log to cycle NN`. A dry-run verdict `Maximum metadata LSN ... is ahead of log ... Would format log to cycle NN` with `EXIT=1` (NOT EXIT=2) means plain repair succeeds (EXIT=0).

   **Supervisor false-exit pitfall:** a background `kubectl exec` (e.g. via `terminal(background=true)`) may be reported `exited` by the host supervisor while the in-pod `xfs_repair` still runs (log shows only `Phase 1`/`Phase 2`). Verify with (a) the log contains `EXIT=` (`read_file` on `/tmp/fix*.log`, not the supervisor preview), or (b) a fresh `xfs_repair -n` returns `Device or resource busy`. If neither, wait and re-probe.

   **Background-exec PATH pitfall:** a host-side `terminal(background=true)` subshell does NOT inherit the host PATH — bare `kubectl` fails with `exit 127` / `kubectl: command not found`. Use the **absolute** kubectl path (e.g. `/nix/store/<hash>-kubectl-<ver>/bin/kubectl`) in any scripted/background `kubectl exec`. The in-pod `setsid` form avoids this.
5. **If EXIT=2** (log holds valuable metadata changes): try mount-replay first (read-write mount replays the log):
   ```bash
   $K -n longhorn-system exec $MGR -c longhorn-manager -- sh -c \
     'mkdir -p /tmp/wmount && mount /host/dev/longhorn/<vol> /tmp/wmount && { echo MOUNT-OK; umount /tmp/wmount; }'
   ```
   **EXIT=2 clarity:** a plain `xfs_repair` (no `-n`, no `-L`) on a dirty log returns EXIT=2 and modifies **nothing** — a non-destructive abort ("log needs replay, mount or use -L"), NOT a failure, never a regression. If mount-replay yields `Failed to recover intents`, escalate to `xfs_repair -L` (destroys the log) — but ONLY for ephemeral/reproducible tiers (servarr-regenerated downloads-*, movies-data, shows-data). Never `-L` a nearline/forever volume; instead repair against the replica whose engine stays put (quiesce first, below).
6. **Quiesce before repairing big volumes**: scale consumers to zero AND pin to 1 replica (`patch volume <vol> spec.numberOfReplicas=1`) so rebuild churn can't detach the device. Verify EVERY consumer first — `kubectl get pods -A -o json | jq` on the claimName; hidden consumers (e.g. immich also mounts timeline-data) will keep the share-manager loop alive. Restore replicas/consumers after EXIT=0.

## RWX share stuck `shareState=starting` / "Waiting for volume share to be available"

Symptom: consumer pod `Pending`/`ContainerCreating` with `FailedAttachVolume ... failed to attach to node <X> ... Waiting for volume share to be available`; `volume.status.shareState` sticks at `starting`; the `share-manager-<vol>` pod crash-loops (readiness fails with `cat: /var/run/ganesha.pid: No such file or directory`). Root cause is downstream of the attach: the share-manager mounts the block device to export it — when that mount fails (dirty XFS log, bad superblock: `mount -t xfs /dev/longhorn/<vol> /export/<vol>` returns `wrong fs type, bad superblock`, exit 32), the share never becomes available and CSI reports the "waiting for share" error. The share-manager's own log is the diagnostic — it prints the full mount command, exit code, and the dmesg hint; no node-debug pod needed (PodSecurity `restricted` blocks those anyway). Co-location of engine and share-manager is NOT the differentiator (2026-09-05 archives-data: both on fushi, superblock failure was real FS corruption). Go straight to the XFS flow above.

Dead ends (2026-09-05, confirmed twice):
- Deleting the stale `VolumeAttachment` — re-attaches into the same share-state loop.
- `kubectl -n longhorn-system patch volume <vol> --type=merge -p '{"spec":{"frontend":"nfs"}}'` — **rejected**: `spec.frontend: Unsupported value: "nfs": supported values: "blockdev", "iscsi"`. The nfs frontend is controller-managed via accessMode.
- Node debug pods for `dmesg` — blocked by PodSecurity `restricted`.

Recovery = the standard RWX flip (RWX→RWO, snapshot, `xfs_repair`, flip back); runbook `docs/runbooks/longhorn-rwx-xfs-recovery.md` in the manifests repo mirrors it. Do NOT improvise `xfs_repair -L` on user-data volumes without the owner's explicit go-ahead — `-L` discards the log's unflushed metadata. Present the diagnosis and options instead.

## Force-attach when no consumer exists (replicas stopped, empty attachmentTickets)

If the volume will not attach at all — `volume status.state=detached`, replicas `currentState=stopped`/`desireState=stopped`, `VolumeAttachment.attachmentTickets: {}` (no consumer) — the ShareManager CR reads `state: stopped` and Longhorn refuses to start a replica. The RWX→RWO flip (step 3) alone will NOT attach it: there is no consumer to request the device. Force one with a debug pod:
```bash
cat > /tmp/<vol>-debug.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: <vol>-debug-mount
  namespace: shikanime
spec:
  containers:
  - name: debug
    image: busybox:1.36
    command: ["sh", "-c", "sleep 3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: <vol>
  restartPolicy: Never
EOF
$K apply -f /tmp/<vol>-debug.yaml
# poll until Running -> AttachVolume.Attach succeeded -> replica starts
```
For RWX, do NOT repair with the debug pod up: the ShareManager remounts the FS at host level and holds the device busy (`xfs_repair ... Device or resource busy`). Delete the debug pod, then flip to RWO pinned to the now-running replica's node (step 3), leaving the device present but **host-unmounted** — repair runs. For RWOP the volume attaches directly once a consumer exists; in a no-consumer deadlock the same debug-pod force is required.

Verify host-unmounted before repairing:
```bash
NODE=$($K -n longhorn-system get volume <vol> -o jsonpath='{.status.currentNodeID}')
MGR=$($K -n longhorn-system get pods -o jsonpath='{.items[?(@.spec.nodeName=="'$NODE'" && contains(@.metadata.name,"longhorn-manager")].metadata.name}')
$K -n longhorn-system exec $MGR -c longhorn-manager -- sh -c \
  'ls -la /host/dev/longhorn/<vol>; mount | grep <vol> || echo HOST_UNMOUNTED'
# ls succeeds AND grep shows nothing => safe to xfs_repair
```
Full worked case (deadlock signature, debug-pod, the RWX flip-back miss): `references/force-attach-no-consumer-2026-08-31.md`.

## Replica reduction by recurring-job class

Select the live scope by the Longhorn recurring-job-group label, not by name alone:
```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
$K -n longhorn-system get volumes.longhorn.io -o json | jq -r \
  '.items[] | select(.metadata.labels["recurring-job-group.longhorn.io/ephemeral"]=="enabled") | [.metadata.name,.spec.numberOfReplicas,.status.state,.status.robustness] | @tsv'
```
Rules:
- Patch only volumes whose current `spec.numberOfReplicas` differs; verify none remains mismatched.
- Reducing a healthy 2-replica volume to 1 is a data-redundancy change — do not force-delete the extra replica or interfere with the active one.
- A volume may stay `degraded` transiently while replica state is removed/rebuilt; verify the active engine and serving replica stay healthy.
- The StorageClass parameter controls future provisioning only: existing volumes do not inherit a change. Change it in GitOps as well as the live volume objects; keep unrelated worktree changes unstaged.
- A dashboard row may show a replica `Detached` while the authoritative volume is healthy and attached. Check in order: volume `.status.state`/`.status.robustness`, engine `.status.currentState`, engine `.status.replicaModeMap`, active replica, PVC phase, VolumeAttachment, consuming pod. A stopped replica with `failedAt` on an old node is stale history when `spec.numberOfReplicas: 1` — do not delete the active replica or force-detach because the UI is stale.

## Post-repair: restore RWX + the `diskSelector` trap

After `EXIT=0`, flip back to RWX and restore the desired replica count:
```bash
# re-enable RWX (ShareManager CR + share-manager pod recreated automatically)
$K -n longhorn-system patch volume <vol> --type=merge -p '{"spec":{"accessMode":"rwx"}}'
# restore desired replicas (most fleet volumes: 2)
$K -n longhorn-system patch volume <vol> --type=merge -p '{"spec":{"numberOfReplicas":2}}'
# scale consumers back
$K -n shikanime scale sts copyparty jellyfin syncthing --replicas=1
```

**Pitfall — forgetting to flip back to RWX wedges every consumer (2026-08-31).** Resuming consumers while the volume is still `rwo`: the CSI attacher publishes it as `MULTI_NODE_MULTI_WRITER` (from the PVC's `ReadWriteMany`) and Longhorn rejects the mode change on an attached volume — `ControllerPublishVolume: err: ... Action [updateAccessMode] not available on <vol>` — so the VolumeAttachment never reaches `attached=True` and pods sit `FailedAttachVolume ... timed out waiting for external-attacher`; csi-attacher logs show `Changing volume <vol> access mode to rwx` then `Failed to change volume <vol> access mode to rwx`. Diagnose by comparing `volume spec.accessMode` (`rwo`) against `pvc spec.accessModes` (`ReadWriteMany`). Fix: detach + set RWX, then CSI reattaches cleanly:
```bash
$K -n longhorn-system patch volume <vol> --type=merge \
  -p '{"spec":{"accessMode":"rwx","nodeID":""}}'
# wait for VA attached=True; consumers start
```
Flip back to native mode (RWX/RWOP) BEFORE unsuspending the Flux Kustomization / scaling the StatefulSet up — mandatory, not optional. Verify: `share-manager-<vol>` reaches `Ready=True` and nfs-ganesha logs print `NFS SERVER INITIALIZED` (dirty log gone, FS mounts cleanly). `robustness=degraded` transiently while the second replica syncs is expected, NOT a regression.

**`Scheduled=False` / `tags not fulfilled` — verify the premise before editing the StorageClass.** "No `nearline` disk is tagged" is frequently FALSE (2026-08-31 `sukebe-doujins-data`: handoff claimed it, but `nearline` WAS tagged on a disk on ALL six nodes; real cause was a phantom replica diskID). Before editing `configs/longhorn/overlays/nishir/storageclass.yaml`, confirm the tag on cluster disks:
```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
$K -n longhorn-system get nodes.longhorn.io -o json | jq -r \
  '.items[] | .metadata.name as $n | (.spec.disks[]?.tags[]? // empty) | "\($n) \(.)"'
```
1. **A StorageClass `diskSelector` change does NOT repair an existing bound volume** — it only constrains NEWLY-provisioned PVCs. A PR shipping `nearline`→`standard` "to fix degraded" is a provisioning fix, not a heal.
2. **The real cause is usually a phantom replica diskID** (see section below), independent of the XFS repair and the StorageClass selector.

If the tag genuinely is absent: fix in GitOps (tag the intended disks via Longhorn Node/Disk CRs) or restore the removed disk (phantom-disk pitfall). Do NOT drop `numberOfReplicas` to hide it — flag to the user, don't loop on the volume.
```bash
$K -n longhorn-system get volume <vol> -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{"\n"}{end}'
# Scheduled=False + ReplicaSchedulingFailure => diskSelector tag missing
```

## Cordon warning (do NOT pin volumes by cordoning nodes)

Cordons do not stop the share-manager pod (a k8s pod scheduled by the SM controller, not bound by Longhorn Node `allowScheduling`), and cordoning 5/6 nodes here broke the API server (`dial tcp 100.121.211.56:443: i/o timeout`). Never cordon to pin a volume; pin via `.spec.nodeID` **after** the RWX→RWO flip.

## Kubelet queue wedges (NFS share, stale ClusterIP)

Pod sits `ContainerCreating`/`Init` forever; `.status.volumes` empty; CSI plugin logs show NO `NodeStageVolume`/`NodePublishVolume` for the volume — silence, not starvation. Root cause: the nested-pending-operation (NPO) queue holds a dead volume lock. Two modes:

**1. CSI-socket wedge** — kubelet's cached fd points at a dead CSI plugin node-socket (plugin restarted). Fix: cordon + delete pod + uncordon (forces kubelet to rebuild the plugin connection).

**2. NPO-queue wedge** (2026-08-28) — a deleted pod's subpath cleanup failed `device is busy`; the NPO queue kept the volume lock forever; stale NFS mounts pointed at a stale ClusterIP; the lazy unmount landed AFTER the retry window closed, so kubelet never retried. Fix: SSH to the node, lazy-unmount the stale mounts, restart kubelet (clears the in-memory NPO queue), delete the stuck pod. Full diagnostic + how to distinguish the two wedges in kubelet logs: `references/nfs-stale-clusterip-2026-08.md`.

## RWO-Pod attach churn

`ReadWriteOncePod` PVCs fail attach with `volume <name> is not ready for workloads` until the previous holder pod releases the claim. On sts pods: delete the old pod first, then the new one attaches.

## Orphaned RWO-Pod attach under a pod recreate loop

A `ReadWriteOncePod` volume is **attached** on a **live** node but Longhorn has dropped ownership (`metadata.ownerID=null` + `status.currentAttachedBy=null`), while the k8s `VolumeAttachment` still exists `Attached=true`, held by a now-dead pod UID. Kubelet recreates the consumer pod dozens of times, each rejected by the RWO-Pod gate (`...already in use by another pod`); init container stuck `PodInitializing`; `Events: <none>`; CSI plugin logs show **no** `NodeStageVolume` (the call never reaches CSI). The engine stays `running` — only the attach orchestration wedged. Probe + full recovery: `references/orphaned-attachment-rwo-recreate-loop-2026-09-01.md`.

## Normal vs broken (do not chase these)

- **Degraded volume with 1 RW replica + a `stopped` second replica** = normal self-healing; rebuilds are per-node concurrent-limited (limit 1), so volumes queue. Check `status.replicaModeMap` and rebuild-gating warnings first. `reaches or exceeds the concurrent limit` warnings are informational, not errors.
- **Stuck vs slow (mass-degradation storm):** after a node reboot (check `Ready` lastTransitionTime) a wave of replicas drops at the same timestamp — still self-healing *unless it isn't progressing*: sample the degraded count twice ~30s apart — steady = the per-node rebuild slot is timeout-looping on big snapshot chains (not healing); falling = fine, wait.
- **`ContainerCreating` + `FailedMount ... attacher.MountDevice ... DeadlineExceeded` with EMPTY csi-plugin logs** = the node's CSI path is saturated by rebuild churn (the call dies at the kubelet→CSI boundary before the plugin logs). Not a per-volume fault; "silence = kubelet not calling it" is only half the map — silence can also mean starvation. Heal the storm (raise rebuild concurrency / let it finish), then recreate the pod; its volume (1/2 RW replica) is data-safe.
- App-level crashloops (immich startup-probe failure) are unrelated to storage — verify via logs before attributing to the migration.

## Ganesha NFSd export loss (pod stuck ContainerCreating on NFS share)

Symptom: pod stuck `ContainerCreating` with `FailedMount ... attacher.MountDevice ... DeadlineExceeded` or the NFS mount not progressing; the CSI block-device path (xfs/iscsi) is healthy — the failure is on the NFS share export from another node. Root cause: ganesha.nfsd on the provider node has an empty exports table (`/tmp/vfs.conf` or `/etc/exports` missing) — the daemon runs with zero export definitions, so the CSI mount (e.g. `10.x.x.x:/downloads-whisparr-data`) reaches the server but the path is not exported: timeout or `ENOENT`/access-denied. Empty CSI plugin logs on the consumer node confirm. Confirm via SSH:
```bash
# NFS mount reachable but path does not exist
ls -la <nfs-server-ip>:/downloads-whisparr-data 2>&1
# → "No such file or directory" = the server responds but has no export

# ganesha config check (on the provider node)
ls -la /tmp/vfs.conf /etc/exports /var/lib/nfs/etab 2>/dev/null || echo "MISSING"
# → if vfs.conf and etab are missing, exports are empty
```
Fix: restore the ganesha config (`/tmp/vfs.conf`) or `/etc/exports` on the provider node, restart ganesha. The provider node is the host running the Longhorn engine — find it via `kubectl --context nishir-k8s-operator.taila659a.ts.net -n longhorn-system get engines.longhorn.io <vol> -o jsonpath='{.spec.nodeID}'`; re-export that host's `/dev/longhorn/<vol>` path. Verify with `showmount -e <provider-node>` from the consumer node. The pod will not auto-recover — recreate it after the mount is confirmed up.

## Stale `spec.nodeID` pin after a node outage (ContainerCreating wedge)

Symptom: after a node goes down and comes back, a consumer pod sits `ContainerCreating` with `FailedAttachVolume ... the volume is currently attached to different node <X>` where `<X>` is the node that was down — Longhorn still holds `spec.nodeID` pinned there, so CSI refuses to attach elsewhere. Patterns: 2026-08-23 (forgejo-data pinned to manash, wanted minish), 2026-08-30 (manash offline); mass version after a reboot: many volumes show `spec.nodeID=<down-node>`.

Confirm (do NOT force-detach a volume a running pod still uses):
```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
# all volumes still pinned to the down node
$K -n longhorn-system get volumes.longhorn.io -o jsonpath='{range .items[*]}{.metadata.name}{" node="}{.spec.nodeID}{"\n"}{end}' | grep <down-node>
# the stuck consumer (ContainerCreating on a DIFFERENT live node)
$K get pod -A -o wide | grep <vol>
# CRITICAL safety gate: confirm NO pod on any node actually uses it on <down-node>
$K get pods -A -o wide | grep <vol>   # expect only the ContainerCreating one
```

Fix per volume (only after the safety gate passes):
```bash
V=<vol>
$K -n longhorn-system patch volumes.longhorn.io $V --type merge \
  -p '{"spec":{"disableAttachmentConfirmation":true}}'
$K -n longhorn-system patch volumes.longhorn.io $V --type merge \
  -p '{"spec":{"nodeID":""}}'
# wait, then confirm pin gone + consumer starts
$K -n longhorn-system get volumes.longhorn.io $V -o jsonpath='node={.spec.nodeID}{"\n"}'
```
`disableAttachmentConfirmation: true` lets Longhorn break the stuck attachment despite believing the volume attached to the dead node; clearing `spec.nodeID` releases the pin so the attachdetach controller reattaches to a live node. If it still won't attach, delete the stale `VolumeAttachment` (it recreates pointed at the right node) — only after re-confirming no pod consumes it. Full diagnostics + exact CSI error transcript: `references/stale-nodeid-pin-2026-08.md`.

## Phantom replica diskIDs — perpetual `degraded` (2026-08-31)

A volume stays `robustness=degraded` with one `running` replica + a 2nd replica `currentState=stopped`, EVEN THOUGH the `diskSelector` tag (e.g. `nearline`) IS present on real disks on all nodes. Do NOT attribute to a missing selector — verify the tag first (premise-check above).

**Detection — replica pinned to a disk that exists nowhere:**
```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
$K -n longhorn-system get replicas.longhorn.io -o json | jq -r \
  '.items[] | "\(.metadata.name)\t\(.spec.diskID)\t\(.spec.nodeID)"' | \
  while IFS=$'\t' read -r r d n; do
    if ! $K -n longhorn-system get nodes.longhorn.io "$n" -o json \
         | jq -e --arg d "$d" '.spec.disks | has($d)' >/dev/null; then
      echo "PHANTOM: $r disk=$d node=$n"
    fi
  done
```
2026-08-31 case: disk IDs `e35af170-…` (ashira) and `316df5ad-…` (nalsha) appeared as replica `spec.diskID` but in NO node's `spec.disks`/`status.diskStatus` — 15 replicas across 8 degraded volumes (`sukebe-doujins-data`, `shows-data`, `sukebe-videos-data`, `forgejo-data`, `staging-data`, `sync-data`, `timeline-data`, `sukebe-games-data`); `movies-data` healthy, proving the `nearline` selector works.

**What did NOT heal it (don't loop):**
- Delete phantom replica + `patch volume … replicaAutoBalance: best-effort` — Longhorn rescheduled the new replica onto the SAME phantom disk ID.
- Edit StorageClass `diskSelector` (`nearline`→`standard`) — only affects NEW PVCs.

**Root cause / fix:** the disk was likely removed upstream in the **NixOS machines repo** (source of truth for node disks); the manifests-repo StorageClass selector is a red herring. Restore the disk upstream so phantom IDs resolve, OR remediate the scheduler pin at the Longhorn layer. Full transcript: `references/phantom-disk-degraded-2026-08-31.md`.

## Dirty XFS log without ShareManager (RWO block volumes, direct node repair)

For plain RWO volumes (servarr config PVCs) the engine block device appears directly on the engine node's host (`/dev/longhorn/<vol>`); no RWX flip needed. Worked case 2026-09-04 (radarr-config, lidarr-config on minish): pods stuck `ContainerCreating` with `MountVolume.MountDevice failed ... wrong fs type, bad option, bad superblock`; `blkid` showed valid XFS; `xfs_repair -n` showed `Maximum metadata LSN ... is ahead of log ... Would format log to cycle NN`. Repair directly over SSH as root on the engine node (volume attached there, no running consumer):
```bash
ssh root@<engine-node> 'xfs_repair -L /dev/longhorn/<vol> 2>&1 | tail -2
  M=/mnt/<vol>-fix; mkdir -p $M; mount /dev/longhorn/<vol> $M && umount $M && echo CLEAN'
```
`-L` was required because mount-replay itself failed with the same bad-superblock error (log too far ahead). Verify by watching the consumer pod start without any pod delete — kubelet's retry loop picks up the repaired device. Same-incident wrinkle: a stale kubelet globalmount dir on the node (`mkdir ... file exists`) also blocks MountDevice; `umount <dir> 2>/dev/null; rm -rf <dir>` over SSH clears it. Restarting the node's longhorn-csi-plugin pod was NOT needed once the FS was clean.

## Failed replica (`spec.failedAt`) + faulted volume + engine `desiredState=stopped` (2026-09-13)

Signature: consumer pod stuck `Pending`/`ContainerCreating` with `FailedMount ... volume <vol> hasn't been attached yet`; volume `status.state=detached`, `robustness=faulted`, `currentNodeID` empty, `spec.nodeID=""`, `spec.desiredState=""`; engine `desireState=stopped`/`currentState=stopped` with no node; the (single) replica `status.currentState=stopped`, `started=false`, and **`spec.failedAt=<timestamp>`** — `spec.failedAt`, not `status.failedAt`. Node healthy (`DiskPressure=False`, ample `storageAvailable`) means process-level failure (killed under memory/IO pressure), not disk space.

Longhorn never auto-restarts a replica whose `spec.failedAt` is set, and with `numberOfReplicas=1` there is no healthy source to rebuild from. Two cuts, in order:
1. Salvage the replica (clears the stamp, keeps on-disk data): `kubectl -n longhorn-system patch replicas.longhorn.io <vol>-r-<hash> --type=merge -p '{"spec":{"failedAt":null}}'`
2. Something must *request* the attach: delete a stale `VolumeAttachment` if present (see orphaned-attachment section), then **recycle the holder pod** (`kubectl delete pod <holder>`). Clearing the stamp alone is not enough — the engine stays `desireState=stopped` because nothing asks for the device. On the fresh pod the volume attaches within ~30 s (engine `running`, replica `started=true`, `robustness=healthy`).

Observed on the llama-cpp cache volume (648 GiB), 2026-09-13: faulted at 00:47Z, consumer `Pending` ~7h, recovered `attached/healthy` with **no** `xfs_repair` and no data loss. Suspected trigger: concurrent multi-model load pushing the node past its RAM ceiling (unproven).

## Diagnostic quick-map

- SM CR: `get sharemanager <vol> -o jsonpath='{.status.state}'` + owner node.
- CSI node plugin activity: `logs longhorn-csi-plugin-<node> -c longhorn-csi-plugin` (NodeStage/NodePublish = mounts flowing; silence = kubelet not calling it).
- Volume health: `get volume <vol>` `status.robustness` + `status.conditions`. `metadata.ownerID=null` + `status.currentAttachedBy=null` + `state=attached` = orphaned attach (see orphaned-attachment section), NOT a dirty-FS case.
- Replica map: `get engines.longhorn.io` `status.replicaModeMap` (RW=serving).

References (each with its load condition):
- `references/recovery-case-2026-08.md` — full worked case: three volumes, all three repair paths, exact failure signatures.
- `references/nfs-stale-clusterip-2026-08.md` — NPO-queue wedge incident.
- `references/sukebe-doujins-rwx-2026-08.md` — RWX→RWO flip incident (the method that actually repairs a 1Ti RWX volume after the delete-pod-once window proved too short).
- `references/force-attach-no-consumer-2026-08-31.md` — no-consumer deadlock (replicas stopped, empty `attachmentTickets`) + the RWX flip-back miss that wedges consumers with `Action [updateAccessMode] not available`.
- `references/stale-nodeid-pin-2026-08.md` — post-outage `spec.nodeID` pin wedging consumer pods `ContainerCreating`.
- `references/phantom-disk-degraded-2026-08-31.md` — phantom-replica-diskID perpetual-degraded case (diskSelector tag IS present on real disks — NOT a StorageClass selector failure, NOT healed by editing it).
- `references/orphaned-attachment-rwo-recreate-loop-2026-09-01.md` — RWO-Pod volume where Longhorn dropped ownership (`ownerID=null`, `currentAttachedBy=null`) while a stale `VolumeAttachment` stays `Attached=true` on a live node and kubelet recreates the consumer pod in a rejection loop.
