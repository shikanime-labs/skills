# Backups & Disaster Recovery (Longhorn 1.12.1)

## Backup target

- Set in UI **Settings > Backup Target** (or Helm `defaultBackupStore.*`, or ConfigMap
  `longhorn-default-resource` keys `backup-target` / `backup-target-credential-secret` /
  `backupstore-poll-interval`).
- Types: NFS, SMB/CIFS, Azure Blob, S3-compatible. Default target `default` auto-created on
  fresh install. Multiple backupstores supported since **v1.8.0**.
- Lifecycle of backups in the store is managed ENTIRELY by Longhorn — never apply a
  retention policy directly on the store.
- S3 secret must be in `longhorn-system`:

  ```bash
  kubectl create secret generic <aws-secret> --from-literal=AWS_ACCESS_KEY_ID=<id> \
    --from-literal=AWS_SECRET_ACCESS_KEY=<key> -n longhorn-system
  ```

  IAM perms: `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`, `s3:DeleteObject`.

## Backup (incremental / full)

- `Backup` CR: `spec.backupMode: incremental|full`, `snapshotName`, `labels`.
- Incremental (default, "delta"): uploads only blocks changed since last backup.
- Full (since **v1.7.0**): re-uploads all blocks, overwriting corrupted ones in store.
- Periodic full: RecurringJob `full-backup-interval` (0 = always incremental).
- Status: `status.newlyUploadDataSize` (first-time blocks), `status.reUploadDataSize`
  (overwritten during full).

## Recurring jobs

- `RecurringJob` CR: `spec.cron` (cron expr), `task`
  (`backup` | `backup-force-create` | `snapshot` | `snapshot-force-create` |
  `snapshot-cleanup` | `snapshot-delete` | `filesystem-trim`), `groups`,
  `retain` (≥1), `concurrency` (≥1), `labels`.
- `groups: [default]` auto-schedules to any volume with no recurring job.
- Apply to volume: `kubectl -n longhorn-system label volume/<V> recurring-job.longhorn.io/<NAME>=enabled`
  (PVC source label `recurring-job.longhorn.io/source=enabled` to sync from PVC).
- StorageClass `recurringJobSelector` JSON lists jobs for all future volumes.

## Restore from backup

- UI: Backup → Restore Latest Backup → name volume.
- CLI: create `Volume` CR with `spec.size` = EXACT byte count as a **quoted string**
  (`"1073741824"`; `1Gi`/raw int → admission error), `fromBackup`,
  `numberOfReplicas`, `frontend`, `dataEngine`; confirm `restoreRequired: false` and
  `state: detached`; then create PV (`volumeHandle` = Volume CR name) + PVC.

## DR (standby) volumes

- Same backup target configured on BOTH clusters. Create `Volume` CR with `standby: true`
  from a source backup URL. Stays passive (gray = restoring, blue = synced, ready).
- Activate (failover): UI button, or
  `kubectl patch volume <V> -n longhorn-system --type=json -p='[{"op":"replace","path":"/spec/Standby","value":false},{"op":"replace","path":"/spec/frontend","value":"blockdev"}]'`.
- Pre-activation limits: no snapshot/backup/PV/PVC operations until activated. If degraded
  and `Allow Volume Creation with Degraded Availability` is off, activation sticks in Attached.

## System backup / restore

- `SystemBackup` CR: `spec.volumeBackupPolicy` (`if-not-present` | `always` | `disabled`).
  RecurringJob task `system-backup`. Uses the **default** backup target. Bundle includes
  Volumes/PVs/PVCs/Settings/CRDs/StorageClasses/etc. — NOT `Nodes`, and NOT V2 backing images.
- `SystemRestore` CR: `spec.systemBackup`. **All existing volumes must be detached first.**
  Does NOT restore `ConfigMap/longhorn-default-setting` or configurable settings
  (Concurrent volume backup restore / replica rebuild per-node limits).
- Cross major/minor version restore unsupported except for upgrade failures (e.g. 1.4.x→1.5).
- Restart restore = delete SystemRestore then recreate (rolls out remaining resources).
