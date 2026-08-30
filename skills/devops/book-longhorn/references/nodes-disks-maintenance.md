# Nodes, Disks & Maintenance (Longhorn 1.12.1)

## Disk types

- **Filesystem-type** (`diskType: filesystem`): V1 engine. Extent FS (ext4/xfs) mounted to a
  host dir. Default disk auto-created at `/var/lib/longhorn`.
- **Block-type** (`diskType: block`): V2 engine. Raw block device, no filesystem.
  Drivers: `nvme` (path may be BDF `0000:05:00.0`), `virtio-blk` (BDF), `aio` (standard path).
  `diskDriver: auto` detects. Prefer stable `/dev/disk/by-id/` paths over `/dev/sdb`/`/dev/nvmeXnY`.

## Add disks

- Filesystem: format+ mount on host, then add path to `spec.disks` on `node.longhorn.io`
  (UI Edit Disks, or `kubectl edit node.longhorn.io <node>`).
  Cannot add a path already used / same filesystem ID as another disk on the node.
- Block: V2 enabled; **clean disk first** (`wipefs -a /path/to/device`). Do NOT nest a V2
  volume/device-mapper path as a block disk (cascading failures).
  Add with `diskType: block`, `diskDriver: auto|aio|nvme|virtio-blk`.

## Disk scheduling settings

- `StorageOverProvisioningPercentage` (default **100**): scheduled/usable =
  Scheduled / (Max − Reserved).
- `StorageMinimalAvailablePercentage` (default **25**): free/Max must stay above this to
  schedule new replicas (not fully enforceable — snapshots + over-provisioning can breach).

## Node Drain Policy (maintenance guide)

Five options; default = **Block If Contains Last Replica**. IMPORTANT: triggers on **cordon**,
not just drain.

- `block-if-contains-last-replica` (default): protects last healthy replica; blocks drain.
- `allow-if-last-replica-stopped`: allows drain if last replica is stopped.
- `always-allow`: always allow (use with care).
- `block-for-eviction`: block until all replicas relocated; auto-evicts.
- `block-for-eviction-if-contains-last-replica`: default protection + auto-evict; enable only
  during planned maintenance / single-replica automation.

## Planned maintenance (node OS/runtime upgrade)

1. Cordon node (Longhorn auto-disables scheduling).
2. `kubectl drain <NODE> --ignore-daemonsets [--delete-emptydir-data]`. Manually attached
   (non-CSI) volumes won't auto-move — detach them manually to unblock.
3. Maintain/reboot. Drain `--timeout` must exceed replica rebuild time (or 0 = never timeout).
4. Uncordon; Longhorn re-enables scheduling, reuses existing replicas to speed rebuilds.

## In-place Kubernetes upgrade

- Upgrade nodes in batches smaller than each volume's replica count (keep >=1 healthy replica
  live). Set Node Drain Policy `allow-if-replica-is-stopped` for single-replica volumes.

## Graceful node removal

1. `kubectl cordon <NODE>` then `kubectl drain <NODE> --ignore-daemonsets --delete-emptydir-data --force --grace-period=-1 --timeout=300s`.
2. Disable scheduling + request eviction:
   `kubectl patch node.longhorn.io <NODE> -n longhorn-system --type=merge -p '{"spec":{"allowScheduling":false,"evictionRequested":true}}'`.
3. Wait until every disk reports `scheduledReplicas: 0` and `scheduledBackingImages: 0`
   (`kubectl get node.longhorn.io <NODE> -o json` → `.status.diskStatus`). Works for attached
   - detached volumes (auto-attaches detached to migrate).
4. `kubectl delete node <NODE>` (Longhorn needs k8s node gone before allowing Longhorn node delete).
5. `kubectl -n longhorn-system delete nodes.longhorn.io <NODE>`.

- Eviction stuck causes: insufficient space, anti-affinity (all other nodes already hold a
  replica → enable Replica Node Level Soft Anti-Affinity), or volume already `Faulted`.

## Remove a disk

Disable scheduling → evict all replicas/backing images → delete disk. Use
`disks-or-nodes-eviction` to evict. Reusing a node name: remove old disks then re-add.
