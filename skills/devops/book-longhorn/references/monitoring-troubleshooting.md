# Monitoring & Troubleshooting (Longhorn 1.12.1)

## Metrics (Prometheus; all in `longhorn-system`)

Key series (labels: node, pvc, pvc_namespace, volume):

- Volume: `longhorn_volume_actual_size_bytes`, `longhorn_volume_capacity_bytes`,
  `longhorn_volume_state{state=attached|detached|...}`, `longhorn_volume_robustness{state=healthy|degraded|faulted}`,
  `longhorn_volume_read/write_throughput`, `longhorn_volume_read/write_iops`,
  `longhorn_volume_read/write_latency` (ns), `longhorn_volume_file_system_read_only`,
  `longhorn_volume_last_backup_at` (unix ts).
- Node: `longhorn_node_status{condition=ready}`, `longhorn_node_storage_capacity_bytes`,
  `longhorn_node_storage_usage_bytes`, `longhorn_node_storage_reservation_bytes`, CPU/mem.
- Replica: `longhorn_replica_state{state=running|stopped|error}`, `longhorn_replica_info`.
- Engine: `longhorn_engine_state`, `longhorn_engine_replica_mode{mode=RW|WO|ERR}`,
  `longhorn_engine_rebuild_progress` (0–100, during rebuild).
- Disk: `longhorn_disk_capacity_bytes`, `longhorn_disk_usage_bytes`,
  `longhorn_disk_health` (1/0), `longhorn_disk_health_attribute_raw` (SMART, when supported),
  throughput/iops/latency.
- Instance Manager: cpu/mem usage + requests (millicpu/bytes).
- CSI sidecars expose histogram `csi_sidecar_operations_seconds_bucket` (driver_name
  `driver.longhorn.io`).

## Support bundle

- Since v1.4.0 uses rancher support-bundle-kit. UI **Generate Support Bundle** (bottom) downloads
  a zip of manifests + logs. Creates a `longhorn-support-bundle` Deployment with cluster-admin SA.
- Limitation: **not concurrent** — wait for in-progress; a new one overwrites the old.
- `dmesg` must be pulled from each node manually (not in bundle).

## Troubleshooting flow

- UI first: attach/mount a volume manually on a node to check content; check Warning-level
  event logs.
- Manager/engine logs: `kubetail longhorn-manager -n longhorn-system`; also instance-manager
  pods (`instance-manager-*` / `-e-*` / `-r-*`).
- CSI: `csi-attacher-0`, `csi-provisioner-0`, `longhorn-csi-plugin-*` containers.
- FlexVolume (deprecated v0.8.0): check `longhorn-driver-deployer` logs + kubelet
  (`journalctl -u kubelet` or `docker logs kubelet`); enable `/var/log/longhorn_driver.log`.

## Common issues

- Volume attaches in UI but k8s pod can't use it: check FlexVolume `--volume-plugin-dir`
  (`ps aux | grep kubelet`; default `/usr/libexec/kubernetes/kubelet-plugins/volume/exec/`;
  GKE uses `/home/kubernetes/flexvolume`).
- Debian `linux-modules-extra-<uname -r>` no candidate: install an available version from
  pkgs.org instead of relying on `uname -r` (e.g. `linux-modules-extra-5.15.0-76-generic`).
- Block disk "Invalid argument": disk size not a multiple of 4096 (AIO `bdev_aio_create`
  error -22). Remove, `fdisk` partition to a 4096-multiple size, re-add.
- SPDK "Failed to bind NVMe disk" / error -22: NVMe shares IOMMU group with PCIe bridge →
  switch disk to **AIO** mode in UI (`lspci -t` / `/sys/kernel/iommu_groups/` to confirm).

## Data recovery

- **Corrupted replica** (intermittent IO errors, bad disk): scale workload to detach; find
  replica dirs (`/var/lib/longhorn/replicas/<pvc>-<id>`); `sha512sum` every file per replica;
  the divergent/erroring one is corrupt → remove via UI; scale up.
- **Restore without system** (no Longhorn installed): `restore-to-file` pod from
  `examples/restore_to_file.yaml.template` (or `scripts/restore-backup-to-file.sh`) outputs a
  `raw`/`qcow2` image from an S3/NFS backup URL to a host path (`/tmp/restore`). Needs
  S3 credential secret in `longhorn-system`.
- Snapshot data integrity: hashes snapshot disk files, detects bit-rot (filesystem-unaware
  corruption). Per-volume / global setting.
