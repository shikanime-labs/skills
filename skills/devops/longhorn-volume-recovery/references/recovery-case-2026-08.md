# Worked case: nishir Longhorn XFS recovery, 2026-08-28

Three volumes surfaced dirty XFS logs after a storage-class migration churn
(the 7-PVC transient migration + engine relocations). All three repaired;
content verified intact through live mounts. Reproduced here so the failure
signatures and repair paths are recognizable, not re-derived.

## Failure signatures (in order of appearance)

1. `sharemanager` CR stuck `state=starting`, owner node's manager logs loop
   between `No share-manager pod yet to attach the volume` and
   `Skipping pod creation ... will retry after backoff of 2m0s`.
2. SM pod reaches `Failed` on mount; SM controller sets `error` state and
   recreates the pod (chicken-and-egg: pod never attaches, so it never
   starts).
3. Engine node dmesg:
   `XFS (sdj): Failed to recover intents` + `log mount finish failed`.
4. Direct RW mount attempt returns `mount system call failed: Structure needs
   cleaning`.

## Repair matrix (which path each volume took)

| Volume | Tier | Repair path | Result |
|---|---|---|---|
| `sukebe-doujins-data` | transient | SM delete once + `xfs_repair -o ag_stride=32` (no `-L`) | EXIT=0, 7 phases, content OK |
| `timeline-data` | nearline (forever) | quiesce (immich→0, replicas→1) + `xfs_repair` (no `-L`) | EXIT=0, log cycle 94 |
| `downloads-whisparr-data` | ephemeral | mount-replay failed → `xfs_repair -L` | EXIT=0, inode nlink resets, content OK |

## Key mistakes made (so you do not repeat them)

- **Delete-loop watchdog on the SM pod was the saboteur.** Each SM-pod
  deletion triggers a re-attach on a fresh node (SM controller picks the new
  owner), which unmounts the device mid-repair → `xfs_repair: read failed:
  No such device` at `can't read btree block 1/16695311`. Repair keeps failing
  until the engine node stays put across the whole run. Delete the SM pod
  ONCE and let the ~2 min controller backoff be your window.
- **Engine node moves silently.** After a failed repair, re-check
  `engines.longhorn.io .spec.nodeID` — the volume will have migrated (e.g.
  minish → ashira → nalsha). Run the repair from the CURRENT engine node's
  manager pod; a stale manager pod says `No such file or directory`.
- **`/host/tmp` does not exist** in the longhorn-manager container — redirect
  to `/tmp` or the backgrounded child dies instantly and the log never
  appears (looks like "still running" forever).
- **Hidden consumers keep the SM loop alive.** `timeline-data` had a second
  consumer, `immich-0`, that was crash-looping hourly and re-triggering SM
  remounts. Enumerate every pod that references the claim
  (`kubectl get pods -A -o json | jq` on `persistentVolumeClaim.claimName`)
  before quiescing, and scale each to zero.
- **Volume can fully detach while consumers are down** (no attachments at
  all) → device vanishes (`fatal error -- couldn't initialize XFS library`).
  Re-attach first: `patch volume <vol> --type merge -p '{"spec":{"nodeID":"<node>"}}'`
  and wait for the device to appear.

## Kubelet pod-worker wedge (whisparr case)

- Symptom: sts pod `Pending`, `initContainerStatuses` stuck
  `{waiting:{reason:PodInitializing}}`, `.status.volumes` empty, zero
  `SuccessfulMountVolume` events, while the node CSI plugin log shows
  `NodeStageVolume` + `NodePublishVolume` rsp `{}` for the pod's exact UID.
- Root cause: kubelet pod-worker latched onto the wedged CSI node socket from
  before a `longhorn-csi-plugin` restart (its own `DeadlineExceeded` from the
  old RPC).
- In-place pod delete did NOT clear it (new pod, same node, same wedge).
  A fresh probe pod on the same node ran fine → kubelet itself was healthy;
  the wedge was pod-specific.
- Fix: cordon the node, delete the sts pod (reschedules onto a healthy node),
  uncordon. No node SSH available (tailnet policy denies all users), so this
  is the only lever.
- Probe-pod note: on this cluster the `default` namespace enforces
  PodSecurity `restricted`, so a raw `kubectl run` is Forbidden — craft a
  compliant pod (runAsNonRoot, drop ALL caps, seccomp RuntimeDefault) to test
  node kubelet health.

## RWO-Pod attach churn (whisparr-config)

`ReadWriteOncePod` PVC: until the old holder releases, attach fails with
`rpc error: code = Aborted desc = volume whisparr-config is not ready for
workloads`. Releasing = old pod fully gone. On sts: delete old pod, let the
new one attach.

## Normal (do not chase)

- Degraded volume with 1 RW replica + one `stopped` replica: self-healing.
  Rebuilds are serialized per node (concurrent limit 1); several volumes
  queue behind each other. Watch for `reaches or exceeds the concurrent
  limit` warnings — informational.
- Post-migration app crashloops (immich startup-probe) unrelated to storage.
