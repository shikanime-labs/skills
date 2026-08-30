# Architecture & Concepts (Longhorn 1.12.1)

## Components

- **Longhorn Manager** — control plane. Runs as a DaemonSet on every node. Creates/owns
  Longhorn CRs (Volume, Engine, Replica, Node, Disk, Backup, RecurringJob, SystemBackup,
  ShardGroup/Shard). Talks to the Kubernetes API server and the Longhorn CSI plugin via the
  Longhorn API.
- **Longhorn Engine** — per-volume data plane (storage controller). V1 = Linux process
  writing sparse files; V2 = SPDK RAID block device (bdev). Runs on the SAME node as the
  pod using the volume; synchronously replicates to replicas.
- **Instance Manager** — manages lifecycle of engine + replica instances; separate pods for
  V1 and V2 when both engines enabled.
- **CSI driver** — name `driver.longhorn.io`. `longhorn-csi-plugin` + sidecars
  (csi-attacher, csi-provisioner, csi-resizer, csi-snapshotter, node-driver-registrar,
  liveness-probe). Formats/mounts block device; kubelet bind-mounts into pod.
- **Share Manager** — `share-manager-<volume>` pod + Service; serves RWX volumes over NFSv4.1.
- **Longhorn UI** — complements k8s; manages snapshots/backups/nodes/disks.

## Design model

- Two layers: data plane (Engine) + control plane (Manager). One Engine per volume isolates
  failure domains; a controller crash affects only its volume.
- Replica = thin-provisioned chain of snapshots on a node. N replicas → tolerate **N−1**
  replica failures (need ≥1 healthy). Default **3** replicas, spread across nodes/disks.
- Read/write: Engine replicates synchronously across replicas; multiple data paths = HA.
- V1 uses iSCSI (needs `open-iscsi`/`iscsiadm`); V2 uses NVMe-TCP / UBLK / block device.

## Volumes & access modes

- RWO (ReadWriteOnce, default), RWOP (ReadWriteOncePod — single pod, strongest isolation),
  RWX (ReadWriteMany via NFS share-manager). **ROX not supported** (use RWX + read-only mount).
- Thin provisioning: a 20 GiB volume holding 1 GiB uses 1 GiB on disk.

## Snapshots vs Backups

- **Snapshot** — point-in-time, stored on replica chain in the cluster. Incremental,
  crash-consistent. Deleting parent of `volume-head`:
  - V1: snapshot marked `removed`, stays in list; purge deferred (separate operation,
    limited by `Snapshot Heavy Task Concurrent Limit`, default **5**).
  - V2: snapshot + CR deleted immediately (live merge into volume-head).
- **Backup** — object in external backupstore (NFS/SMB/S3). 2 MiB blocks by default.
  Does NOT include snapshot chain. Backups are delta (changed blocks only) unless full.
- **Revision counter** — V1 only (tracks latest replica update for salvage). **V2 does not
  support it.**

## Terminology key terms

- Frontend: block device exposed by a volume (`/dev/longhorn/<vol>`).
- Maintenance Mode: attach without frontend (revert from snapshot).
- Backupstore: NFS / CIFS / S3-compatible external store. Backup Target: endpoint to it.
- DR volume: standby volume in a secondary cluster kept synced from backups.
- Salvage: auto-pick usable replicas when all become faulty.
- Strict-local data locality: only 1 replica, co-located with workload.

## V1 ↔ V2 feature parity (selected)

- V2 adds: fast volume cloning, QoS, storage sharding (erasure coding, experimental).
- V2 lacks vs V1: revision counter, engine live upgrade (must detach), strict-local data
  locality, offline fast rebuilding, backing images (use CDI instead), and (sharded layout)
  backup/restore, cloning, DR, live migration, snapshot integrity check.
- V2 volumes are scheduled ONLY on block-type disks; V1 ONLY on filesystem-type disks.
