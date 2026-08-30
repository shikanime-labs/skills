# V2 Data Engine (Longhorn 1.12.1)

## What V2 is

SPDK-based data plane using huge pages + user-space NVMe drivers (zero-copy, highly parallel).
V1 = Linux process + sparse files (iSCSI). Enable only one engine per cluster unless both
needed (each adds a guaranteed-CPU instance-manager pod; V2 `spdk_tgt` alone >=1 core).

## Requirements (summary)

- 3 nodes; +1 CPU core/node for `spdk_tgt` (polling); +2 GiB/node for huge pages; local NVMe SSDs.
- Kernel >=5.19 (NVMe/TCP), >=6.7 recommended (stability, avoids SPDK #3116).
- Modules `vfio_pci`, `uio_pci_generic`, `nvme_tcp`; AMD64 SSE4.2.
- Huge pages: default **1024 x 2 MiB** pages per node; reserve via kernel boot / `hugepagesz` +
  `hugepages=`; persist in `/etc/default/grub` or k8s node config.

## Huge page config

- `data-engine-hugepage-enabled` (e.g. `{"v2":"true"}`); `data-engine-memory-size` (default
  `{"v2":"2048"}` MiB — must be <= allocated huge pages).
- Disable: `data-engine-hugepage-enabled: {"v2":"false"}` → SPDK uses anonymous memory
  (lower perf, more flexible). Changing memory size requires all V2 volumes detached.

## Disk drivers

`diskDriver: auto|nvme|virtio-blk|aio`. NVMe/virtio paths may be BDF notation. After binding,
device no longer appears as `/dev/nvmeXnY` / `/dev/vdX`. Avoid kernel names for stable paths.

## Sharding / Erasure Coding (EXPERIMENTAL, V2 only)

Alternative to replication. Encodes data into `k` data + `m` parity chunks across nodes.

- Capacity: `k/(k+m)` of disk space (vs `1/replicas` for RAID1). e.g. 2+1 = 66% usable,
  survives 1 failure; 4+2 = 66%, survives 2.
- Req: >= `k+m` nodes with schedulable V2 disks. No node holds a full copy.
- StorageClass params: `dataLayout.type: sharded`, `dataLayout.mode: erasureCoding`,
  `dataLayout.dataChunks` (>=1), `dataLayout.parityChunks` (>=1, tolerates `m` failures),
  `dataLayout.stripSizeKB` (power of 2, 4–1024). Total chunks <= 32. Auto-sets
  `numberOfReplicas: 1`, `dataLocality: disabled`. Immutable after creation.
- Supported: CRUD, attach/detach, RWX, snapshots (create/delete/revert/purge), online+offline
  expansion up to **10x original size** (fixed EC metadata — no shard-group growth), volume
  encryption, survives up to `m` chunk failures (rebuilds in background).
- NOT supported: backup/restore, volume cloning, backing images, DR volumes, live migration,
  snapshot data integrity check, replica-count change/rebuild. UI creation unavailable — use
  StorageClass manifest.
- Inspect: `kubectl -n longhorn-system get shardgroup,shard` (ShardGroup `healthy|degraded|
  offline|rebuilding|growing`; Shard role `data|parity`, state `normal|failed|replacing`).

## Feature parity gaps vs V1

- V2: no revision counter, no engine live upgrade (detach first), no strict-local data
  locality, no offline fast rebuilding, no backing images (use CDI). V2 adds fast cloning, QoS,
  sharding.
- V1 engine live-upgrade v1.11.x→v1.12.1 supported; V2 must detach for any patch upgrade.
