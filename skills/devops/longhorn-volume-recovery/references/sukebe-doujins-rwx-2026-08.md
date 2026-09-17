# sukebe-doujins-data RWX dirty-XFS recovery (2026-08-29)

Volume: `sukebe-doujins-data` (nishir, ns `shikanime`, 1Ti, RWX over NFS
share-manager; consumers: copyparty, jellyfin, syncthing).

Symptom: `share-manager-sukebe-doujins-data` pod stuck `Running`/`starting`;
longhorn-manager logs `share manager gRPC server is not running` → underlying
XFS dirty/aborted log (post-migration aftermath).

## Failed approaches (do NOT repeat)

- `spec.nodeID` pin alone — cleared/overridden after attach; engine migrated.
- Longhorn Node CR `allowScheduling=false` — does NOT stop the SM pod (it is a
  regular k8s pod, not bound by the replica scheduler).
- `spec.disableFrontend:true` — SM pod recreated anyway; engine kept migrating.
- delete SM pod once + immediate repair — only works for SMALL volumes inside
  the ~2-minute recreate window; for 1Ti the pod respawned and dragged the
  engine off-node mid-repair (`EXIT=134` / `No such device` at a btree block).
- cordon 5/6 nodes — briefly broke API reachability; did not stop the SM pod.

Root cause of all failures: the **ShareManager CR** (`ownerReferences` → Volume)
is reconciled by longhorn-manager on the engine node and recreates the SM pod.
Nothing except removing the RWX frontend stops it.

## Working method (verified)

Basis: longhorn.io KB `troubleshooting-volume-filesystem-corruption` + GitHub
discussion #4682 ("change the access mode on the longhorn volume from RWX to RWO
temporarily").

1. Snapshot (safety): `longhorn.io/v1beta2` `Snapshot`, `spec.volume=<vol>`.
2. `patch volume <vol> --type=merge -p '{"spec":{"accessMode":"rwo","nodeID":""}}'`
   → deletes ShareManager CR; volume detaches then re-attaches as RWO;
   `/dev/longhorn/<vol>` blockdev appears, unmounted.
3. Pin `spec.nodeID` to `status.currentNodeID`.
4. `xfs_repair /host/dev/longhorn/<vol>` (no `-L`).
   Dry-run verdict: `Maximum metadata LSN (68:1566) is ahead of log (1:2).
   Would format log to cycle 71.` with `EXIT=1` (NOT `EXIT=2`) ⇒ plain repair
   reaches `Phase 7 ... Format log to cycle 71` and `EXIT=0`.
5. Flip `accessMode` back to `rwx`; scale consumers to 1; verify `healthy`.

## Notes

- The Longhorn UI "maintenance mode" attach = attach without enabling the
  frontend. For RWX it only creates the share endpoint, NOT the block device —
  so the RWX→RWO flip is the required prerequisite to get a repairable device.
- The `kubectl longhorn` plugin is NOT installed in this environment; use raw
  CR patches. `xfs_repair` v6.7.0 lives in the `longhorn-manager` container.
- A 1Ti `xfs_repair` holds the device open the whole run; a concurrent
  `xfs_repair` on the same device returns `Device or resource busy` (first run
  still in flight, not failed).

Doc URLs:
- https://longhorn.io/kb/troubleshooting-volume-filesystem-corruption/
- https://github.com/longhorn/longhorn/discussions/4682
