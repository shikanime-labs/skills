# Orphaned RWOP attachment under a pod recreate loop (2026-09-01)

## Signature — OPPOSITE of the "no consumer" deadlock

The volume is **attached** but Longhorn lost controller ownership of it, while
kubelet keeps destroying and recreating the consumer pod:

- `volume status.state=attached` + `status.robustness=degraded`
- `volume spec.nodeID` and `status.currentNodeID` = the **live** node (e.g.
  `ashira`), NOT a dead/replaced node — so the `stale-nodeID-pin` section does
  NOT apply.
- `volume metadata.ownerID=null` and `volume status.currentAttachedBy=null`
  (Longhorn's attach controller has dropped its ownership bookkeeping).
- A `VolumeAttachment` object **still exists** and is
  `Attached=true` on that live node — but it is **orphaned**: the VA's holder
  is a pod UID that no longer exists.
- kubelet events (on the consumer pod):
  `FailedMount ... volume uses the ReadWriteOncePod access mode and is already
  in use by another pod` — i.e. the *orphaned* attach from the old pod is
  blocking the *new* (recreated) pod.
- The init container (or main container) sits `PodInitializing` with `Reason:
  PodInitializing` and `Restart Count: 0`; kubelet **recreates the pod dozens
  of times** (x73 over ~146m in the field case), each with a **fresh
  `metadata.uid`**.
- `kubectl describe pod` shows `Events: <none>` and a PVC/ClaimName that is
  present in `.spec.volumes` but the attach is rejected before `NodeStage`.
- CSI plugin logs on that node show **no** `NodeStageVolume` for the failing
  volume (the call never reaches CSI — kubelet's RWOP attach gate rejects it
  first). Other volumes on the same node stage/publish normally.

## How this differs from the other wedges

| Section | Trigger | Volume state | Owner bookkeeping | VA state |
|---|---|---|---|---|
| `stale-nodeID-pin` | node outage/reboot | attached | intact | attached, pinned to DEAD node |
| `force-attach-no-consumer` | no pod ever held it | detached | n/a | absent / `attachmentTickets:{}` |
| **this file** | controller dropped ownership mid-flight | attached (stale) | `ownerID=null`, `currentAttachedBy=null` | **present + Attached=true**, holder dead |

The distinguishing probe: `get volumes.longhorn.io <vol> -o json` shows
`status.state=attached` AND `metadata.ownerID=null`. That combination does not
appear in either of the two cases above.

## Root cause

A Longhorn attach-controller ownership loss while the CSI attacher still has
the VA live on the node. Common triggers:

- Longhorn manager/controller pod churn (CRD reconcile loop restart) while a
  pod that was previously `Running` on this volume got deleted — the controller
  forgets the holder but the CSI `VolumeAttachment` is never detached.
- A pod that was `Running` got recreated (e.g. by a liveness/restart, a Flux
  reconciliation flipping the StatefulSet spec, or a user `rollout restart`)
  before the old attach was torn down. The new pod is rejected by kubelet's
  RWOP gate because the orphaned VA still claims the volume; Longhorn never
  releases it because it no longer tracks a consumer → deadlock.

## Diagnostic one-liner (run before any fix)

```bash
K="kubectl --context nishir-k8s-operator.taila659a.ts.net"
V=whisparr-config
$K -n longhorn-system get volumes.longhorn.io $V -o json | \
  jq '{state:.status.state, robust:.status.robustness, ownerID:.metadata.ownerID, \
       attachedBy:.status.currentAttachedBy, currentNode:.status.currentNodeID, \
       accessMode:.spec.accessMode, workloadsStatus:.status.kubernetesStatus.workloadsStatus}'
# ownerID=null + attachedBy=null + state=attached  => orphaned attach
VA=$($K get volumeattachment -n longhorn-system -o jsonpath="{.items[?(@.spec.source.csi.volumeHandle==\"$V\")]" --no-headers 2>/dev/null | head -1)
if [ -z "$VA" ]; then
  VA=$($K get volumeattachments --all-namespaces -o jsonpath="{.items[?(@.spec.source.csi.volumeHandle==\"$V\" && @.spec.source.csi.driver==\"driver.longhorn.io\")].metadata.name}{'\n'}" | head -1)
fi
echo "VA=$VA"
[ -n "$VA" ] && $K get volumeattachment "$VA" -o jsonpath='attached={.status.attached}{"\n"}'
# also: kubelet recreations, fresh uid each time
$K get pods -n shikanime -l app.kubernetes.io/name=whisparr -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.uid}{"\t"}{.status.phase}{"\n"}{end}'
```

> NOTE: `VolumeAttachment` objects are **cluster-scoped** and are **not** in the
> `longhorn-system` namespace — `get volumeattachment -n longhorn-system`
> succeeds only because the VA carries no namespace field. When grepping, search
> `--all-namespaces` or filter by `spec.source.csi.volumeHandle` on the
> cluster-scoped list. A `grep -i <vol> | get volumeattachment -n <ns> -o name`
> can silently return EMPTY (as it did in the field case) even though a VA
> exists — do not trust a missing VA until you've searched cluster-wide.

## Recovery (ordered)

1. **Stop the recreate loop.** Scale the consumer StatefulSet to 0:
   ```bash
   $K -n shikanime scale sts whisparr --replicas=0
   ```
   This prevents kubelet from burning dozens of new attach attempts on the
   orphaned VA while we repair. Flux will not fight this if its `Kustomization`
   is suspended or the STS is paused; otherwise suspend it first.

2. **Clear the orphaned attach.** Two complementary cuts — both are needed
   because the two bookkeeping layers disagree:
   ```bash
   # (a) Longhorn volume: release the node pin so the attach controller
   #     drops its (stale) belief and the engine detaches cleanly.
   $K -n longhorn-system patch volumes.longhorn.io whisparr-config \
     --type=merge -p '{"spec":{"nodeID":""}}'
   # (b) Kubernetes VA: force-delete the orphaned object. The
   #     external-attacher / Longhorn controller will recreate it
   #     (pointed at the correct holder) on the next consumer.
   $K delete volumeattachment csi-<the-VA-name>
   ```
   Wait ~30s and confirm: `get volumes.longhorn.io whisparr-config -o jsonpath`
   → `state` should flip to `detached` (or briefly `attaching`) and
   `ownerID` clears. A fresh VA should NOT yet exist (no consumer).

3. **Confirm detached + no holder.**
   ```bash
   $K get volumeattachment csi-<the-VA-name>            # NotFound
   $K -n longhorn-system get volumes.longhorn.io whisparr-config -o jsonpath=\
     '{state=\(.status.state) owner=\(.metadata.ownerID) attachedBy=\(.status.currentAttachedBy)}'   # state!=attached
   ```

4. **Resume.** Scale the StatefulSet back to 1. The StatefulSet controller
   creates a fresh pod; Longhorn re-creates the VA against the new UID; the
   RWOP gate is satisfied because there is no orphaned VA; the volume attaches
   and the init container runs.

## What did NOT work (do not loop on)

- Deleting just the consumer pod (without fixing the VA) → a fresh pod appears
  with a new UID and is immediately rejected by the same orphaned attach.
- `kubectl delete pod whisparr-0 --force --grace-period=0` → same: new UID,
  same rejection, same `Events: <none>`.
- `patch volume ... disableAttachmentConfirmation:true` (from the
  `stale-nodeID-pin` section) → that flag is for detaching while a holder is
  believed alive; here the holder is already orphaned so it is a no-op on the
  VA.

## Data safety

The volume's engine `whisparr-config-e-0` stayed `running` on ashira throughout
(the replica set was healthy) — only the **attach/detach orchestration** wedged,
not the data path. No XFS repair or RRX→RWO flip is required. The block device
is intact on ashira; this is a metadata/ownership repair, not a filesystem
repair.

See also: `references/stale-nodeid-pin-2026-08.md` (different failure: pin to a
DEAD node) and `references/force-attach-no-consumer-2026-08-31.md` (different
failure: volume will NOT attach because nothing requests it).
