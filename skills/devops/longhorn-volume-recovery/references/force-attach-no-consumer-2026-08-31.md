# Force-attach when no consumer exists + RWX flip-back miss (2026-08-31)

## Deadlock signature (volume will NOT attach at all)

Root cause that blocks repair before step 1 even runs:

- `volume status.state=detached`
- replicas `status.currentState=stopped` / `spec.desireState=stopped`
- `VolumeAttachment.attachmentTickets: {}` (no consumer requested it)
- ShareManager CR `state: stopped` (for RWX)

Longhorn refuses to start a replica because nothing holds the claim. The
RWX→RWO flip (SKILL step 3) alone will NOT attach it — there is still no
consumer to request the block device.

### Fix: force a consumer with a debug pod

```yaml
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
```

`kubectl apply`, poll until `Running` + `AttachVolume.Attach succeeded` → the
replica starts and `/host/dev/longhorn/<vol>` appears on the engine node.

### Then expose a host-unmounted device for xfs_repair

For RWX the ShareManager remounts the FS at host level and holds the device
busy, so `xfs_repair` on the present device fails with
`Device or resource busy`. Sequence that works:

1. `kubectl delete pod <vol>-debug-mount` (frees the pod-level mount).
2. Flip volume to RWO pinned to the running replica's node (SKILL step 3):
   `patch volume <vol> --type=merge -p '{"spec":{"accessMode":"rwo","nodeID":"<node>"}}'`
3. On that node's manager: `ls /host/dev/longhorn/<vol>` exists AND
   `mount | grep <vol>` shows nothing (HOST_UNMOUNTED). Safe to repair.
4. `xfs_repair -L /host/dev/longhorn/<vol>` → EXIT=0.

(RWOP attaches directly once any consumer exists; same debug-pod force applies
during a no-consumer deadlock.)

## RWX flip-back miss (the pitfall that wedged jellyfin/sonarr/bazarr)

After step 4 on an RWX volume, if you unsuspend the Flux Kustomization /
scale the STS back up while the volume is STILL `rwo`, the CSI attacher
publishes as `MULTI_NODE_MULTI_WRITER` (from the PVC's `ReadWriteMany`) and
Longhorn rejects the mode change on an attached volume. csi-attacher logs:

```
level=info msg="Changing volume shows-data access mode to rwx"
level=error msg="Failed to change volume shows-data access mode to rwx"
  error="Action [updateAccessMode] not available on [&{shows-data volume ...}]"
level=error msg="ControllerPublishVolume: err: rpc error: code = Internal
  desc = Action [updateAccessMode] not available on [&{shows-data ...}]"
```

Symptom: `VolumeAttachment` never reaches `attached=True`; pods sit
`FailedAttachVolume ... timed out waiting for external-attacher of driver.longhorn.io`.

Diagnose: `volume spec.accessMode` reads `rwo` but `pvc spec.accessModes` is
`ReadWriteMany`.

Fix: detach + set RWX, then CSI reattaches cleanly:
`patch volume <vol> --type=merge -p '{"spec":{"accessMode":"rwx","nodeID":""}}'`

Rule: always flip the volume back to its NATIVE mode (RWX/RWOP) BEFORE resuming
consumers. The post-repair restore is mandatory, not optional.
