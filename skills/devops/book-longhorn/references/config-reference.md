# Configuration Reference (Longhorn 1.12.1)

## StorageClass parameters (verbatim defaults)

Provisioner is always `driver.longhorn.io`. StorageClass params OVERRIDE global settings for
new volumes only; changes are NOT retroactive to existing volumes.

| Parameter | Default | Notes |
| --- | --- | --- |
| `allowVolumeExpansion` | `true` | built-in k8s field |
| `reclaimPolicy` | `Delete` | |
| `volumeBindingMode` | `Immediate` | use `WaitForFirstConsumer` for strictTopology |
| `numberOfReplicas` | `"3"` | 1–20 |
| `staleReplicaTimeout` | `"30"` | minutes before unhealthy replica dropped |
| `fromBackup` | `""` | e.g. `s3://bucket@region?volume=..&backup=..` |
| `fsType` | `"ext4"` | ext4 / xfs |
| `migratable` | `false` | needs RWX + volumeMode Block |
| `encrypted` | `false` | |
| `dataLocality` | `"disabled"` | disabled / best-effort / strict-local |
| `replicaAutoBalance` | `"ignored"` | ignored / disabled / least-effort / best-effort |
| `diskSelector` | `""` | comma tags |
| `nodeSelector` | `""` | comma tags |
| `recurringJobSelector` | `""` | JSON list of {name,isGroup} |
| `backupTargetName` | `"default"` | |
| `strictTopology` | `"false"` | needs `csi-allowed-topology-keys` |
| `dataEngine` | `"v1"` | v1 / v2 |
| `freezeFilesystemForSnapshot` | `"ignored"` | ignored / enabled / disabled |
| `unmapMarkSnapChainRemoved` | `"ignored"` | disabled / enabled / ignored |
| `nfsOptions` | `""` | e.g. `soft,timeo=150,retrans=3` |
| `mkfsParams` | `""` | since v1.4.0 |
| `backingImageName` / `backingImageChecksum` / `backingImageDataSourceType` / `backingImageDataSourceParameters` | `""` | V1 only |
| `dataLayout.type` / `.mode` / `.dataChunks` / `.parityChunks` / `.stripSizeKB` | — | V2 only (sharding) |

> Conflicts: do NOT combine `allowedTopologies` (StorageClass) with
> `dataLocality: strict-local` — immutable PV nodeAffinity fights Longhorn pinning.

## Helm values (selected)

- `persistence.createStorageClass` (true), `persistence.defaultClass` (true),
  `persistence.defaultClassReplicaCount` (3), `persistence.defaultDataLocality` (disabled),
  `persistence.defaultFsType` (ext4), `persistence.reclaimPolicy` (Delete).
- `defaultSettings.v1DataEngine` / `v2DataEngine` (enable engines).
- `defaultSettings.v2DataEngineGuaranteedInstanceManagerCPU` — **"1250"** (millicpu);
  also `v2DataEngineHugepageLimit` (MiB).
- `defaultBackupStore.backupTarget` / `.backupTargetCredentialSecret` / `.pollInterval`.
- `networkPolicies.enabled` (false — UI ingress), `networkPolicies.restrictInternalTraffic` (true).

## Key global settings (verbatim names + defaults)

- `Default Replica Count` — **3**.
- `Default Data Locality` — **disabled**.
- `Storage Over Provisioning Percentage` — **100** (scheduled/usable).
- `Storage Minimal Available Percentage` — **25**.
- `Storage Reserved Percentage For Default Disk` — reserved on each new node.
- `Snapshot Maximum Count` — **2–250**.
- `Snapshot Heavy Task Concurrent Limit` — **5** (<1 = unlimited; purge/clone per-node cap).
- `Concurrent Replica Rebuild Per Node Limit` — rebuild concurrency cap.
- `Concurrent Volume Backup Restore Per Node Limit`.
- `Guaranteed Instance Manager CPU` — **12%** (V2 SPDK polling reservation).
- `Replica Auto Balance` — disabled / least-effort / best-effort.
- `Node Drain Policy` — see nodes-disks-maintenance.
- `Allow Volume Creation with Degraded Availability` — false (prod).
- `Automatic Salvage` — recover faulty replicas.
- `Pod Deletion Policy When Node is Down` — auto force-delete terminating pods.
- `Allow Recurring Job While Volume Is Detached` — false.

Edit defaults via Helm `defaultSettings.*`, the `longhorn-default-resource` ConfigMap, or UI
Settings. Do NOT edit the default `longhorn` StorageClass after install (breaks upgrades).
