# Retention, Backfilling & Deletion

Distilled from the single-node and key-concepts docs.
Reference: <https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/>

## Retention

- `-retentionPeriod` (single-node) / cluster equivalent. Default **1 month (31d)**, minimum **24h** (or `1d`). Suffixes: `d`, `w`, `m`, `y`.
- Older data auto-deleted.
- Enterprise: `-retentionFilter` per-label retention, e.g. `{env="dev"}:3d`.

## Backfilling (historical data)

- VM accepts backfilled samples via ingestion protocols (remote_write, native, etc.). vmagent has **no backfill limits** (unlike Prometheus agent).
- Import endpoints (single-node, port 8428):
  - Prometheus exposition: `/api/v1/import/prometheus` (POST text)
  - Native: `/api/v1/import` (native binary)
  - JSON line: `/api/v1/import/jsonline`
  - CSV: `/api/v1/import/csv`
  - InfluxDB: `/api/v1/import/influx`
  - OpenTSDB: `/api/v1/import/opentsdb` and `/api/v1/import/opentsdbtcp`
- Timestamps outside `[1970-01-02, 2262-03-31]` (ms) are rejected.
- vmagent can also receive/backfill via its push protocols.

## Deleting time series

- Delete via the admin delete API (e.g. `/api/v1/admin/tsdb/delete_series?match[]=<selector>`) on single-node; cluster uses the vmselect admin endpoint.
- Deletion rewrites the block containing the series (MergeTree-like) — no in-place edit.
- Deduplication/downsampling reduce raw samples per series but do **not** delete series or shrink indexdb.

## Snapshots

- Instant snapshots for backup: `POST /snapshot/create` → returns snapshot name; `GET /snapshot/list`; `DELETE /snapshot/free?snapshot=<name>`.
- Backups use `-snapshot.createURL` (vmbackup auto-creates + frees).

## When to load this

Load when setting retention, importing historical data, deleting series, or scripting snapshots.
