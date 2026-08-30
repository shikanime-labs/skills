# Volumes & Volume Operations (Longhorn 1.12.1)

## Access modes

- RWO (default), RWOP (single pod), RWX (NFS share-manager), ROX unsupported.
- RWX = each volume gets `share-manager-<vol>` pod + Service (NFSv4.1). Requirements:
  unique node hostnames, NFSv4 client on every client node.
- **Migratable RWX** (KubeVirt live migration): needs `volumeMode: Block`,
  StorageClass `migratable: "true"` (sets `volume.spec.migratable=true`), ReadWriteMany.
  Non-migratable RWX cannot live-migrate.

## Create volumes

- V1: StorageClass `provisioner: driver.longhorn.io`, filesystem-type disk present.
- V2: StorageClass `parameters.dataEngine: "v2"`, block-type disk present; optional
  `dataLayout.type: replicated`, `dataLayout.mode: raid1`.
- Bind to PVC to Pod; dynamic provisioning reads `numberOfReplicas`, `fsType`, etc.
- Scheduling failure surfaced in PV annotation `longhorn.io/volume-scheduling-error`
  (e.g. `insufficient storage;disks are unavailable;tags not fulfilled`).

## Expansion

- Online V1 >= v1.4.0; online V2 >= v1.10.0 requires **NVMe (NVMf) or Block Device**
  frontend; **UBLK frontend not supported for online expansion** (as of v1.10.0).
- Prereq: PVC StorageClass `allowVolumeExpansion: true`. Edit PVC
  `spec.resources.requests.storage` larger to resize replicas + filesystem
  (ext4/xfs, blockdev frontend; max ext4 16 TiB).
- RWX online auto since v1.8.0 (needs share-manager upgraded; if down-rev, delete the
  `share-manager-<vol>` pod to recreate at current version).
- Offline: detach (scale workload to 0), confirm `state: detached`, expand, scale up.
- Revert-to-smaller-snapshot: frontend keeps expanded size; manually `mount`/`umount` then
  `resize2fs` (ext4) or `xfs_growfs` (xfs) on the attached node.

## Trim filesystem

- Reclaims space from deleted files; volume attached + mounted; filesystem ext4/xfs.
- RWO mount point = workload pod or manually attached node. RWX = inside
  `share-manager-<vol>` pod at `/export/<vol>` then `fstrim /export/<vol>`.
- RecurringJob task `filesystem-trim`. Volume field `UnmapMarkSnapChainRemoved`
  (disabled/enabled/ignored) overrides global `Remove Snapshots During Filesystem Trim`.
- Not effective during rebuild or expansion; remount to retry.
- Encrypted: enable `cryptsetup --allow-discards --persistent refresh <vol>` on host first.

## Encrypted volumes

- Linux `dm_crypt` + `cryptsetup` + Kubernetes Secret (in `longhorn-system`):
  `CRYPTO_KEY_VALUE`, `CRYPTO_KEY_PROVIDER: secret`, `CRYPTO_KEY_CIPHER: aes-xts-plain64`,
  `CRYPTO_KEY_HASH: sha256`, `CRYPTO_KEY_SIZE: 256`, `CRYPTO_PBKDF: argon2i`,
  `CRYPTO_PBKDF_FORCE_ITERATIONS: 200000`, `CRYPTO_PBKDF_MEMORY: 0`.
- StorageClass: `encrypted: "true"` + `csi.storage.k8s.io/provisioner-secret-name`(-namespace),
  `node-publish-secret-*`, `node-stage-secret-*`, `node-expand-secret-*`.
- Online expansion of encrypted volumes: needs `node-expand-secret-*` (k8s >=1.29 native,
  or `CSINodeExpandSecret` feature gate on 1.25-1.28). PVC stays `Pending` until the secret
  is retrievable. Backups of encrypted volumes are encrypted.

## V2 specifics

- Engine live upgrade NOT supported; detach volume before upgrading V2 engine.
- Scheduled only to block-type disks; sharded layout drops backup/clone/DR/live-migration.
