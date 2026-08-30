# Backup & Restore

Distilled from <https://docs.victoriametrics.com/victoriametrics/vmbackup/> and vmrestore/vmbackupmanager.
Reference: <https://docs.victoriametrics.com/victoriametrics/vmbackup/>

## vmbackup

- Backs up from **instant snapshots** (no need to stop VM). Process is resumable — restart with same args continues.
- Restore with **vmrestore**.

### Single-node

```sh
./vmbackup -storageDataPath=</path/to/victoria-metrics-data> \
  -snapshot.createURL=http://localhost:8428/snapshot/create \
  -dst=gs://<bucket>/<path/to/new/backup>
```

- `vmbackup` creates the snapshot, backs up, then auto-removes it.

### Cluster

- Run `vmbackup` on **each vmstorage node**; write to separate `-dst` dirs per node (e.g. `gs://<bucket>/vmstorage-1`).
- `-snapshot.createURL=http://vmstorageN:8482/snapshot/create`.
- Kubernetes: run as a sidecar in the vmstorage pod.

## Supported `-dst` storage types

- GCS `gs://<bucket>/<path>`, S3 `s3://...`, Azure `azblob://...`, S3-compatible (MinIO/Ceph), local `fs://</absolute/path>`.
- `vmbackup` refuses to write into `-storageDataPath` itself.

## Backup types

- **Incremental**: if `-dst` already has a backup, only new data is uploaded.
- **Full with server-side copy**: `-origin=gs://<bucket>/<existing>` makes a server-side copy of shared data (saves transfer).
- **Smart backup** (recommended): hourly incremental to `latest` + daily server-side copy to `YYYYMMDD` folder.
  - Hourly: `./vmbackup ... -dst=gs://<bucket>/latest`
  - Daily: `./vmbackup -origin=gs://<bucket>/latest -dst=gs://<bucket>/<YYYYMMDD>`
  - Don't run hourly while daily copy runs; delete old backups to save cost.

## vmbackupmanager (enterprise)

- Built on vmbackup; automates hourly/daily/weekly/monthly backups. Free trial license available.

## vmrestore

- Restores a backup created by vmbackup into `-storageDataPath`. Mirror of backup flags (`-src`, `-storageDataPath`).

## When to load this

Load when planning backup strategy (smart/incremental), cluster backup topology, or a restore procedure.
