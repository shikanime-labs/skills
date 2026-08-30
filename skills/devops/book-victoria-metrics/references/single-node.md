# Single-node VictoriaMetrics

Distilled from <https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/>
Reference: <https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/>

## When to use

- Recommended for ingestion < 1 million data points/sec. Scales vertically with CPU/RAM/storage and supports HA mode.
- A single node can substitute moderately sized Thanos/M3DB/Cortex/InfluxDB/TimescaleDB clusters.

## Key flags

- `-storageDataPath` — directory for all data (default `victoria-metrics-data` in CWD).
- `-retentionPeriod` — data retention; default **1 month (31d)**, minimum 24h (or `1d`). Suffixes `d`, `w`, `m`, `y` allowed.
- HTTP listen on port **8428** by default (Prometheus querying API + ingestion).
- `-promscrape.config` — Prometheus-compatible scrape config (local path or HTTP URL). Single-node can scrape directly, no vmagent required.
- `-selfScrapeInterval` — scrape itself for monitoring.

## Operations

- **Upgrade/downgrade**: send `SIGINT` to stop gracefully, wait for exit, start new binary. Safe to skip versions unless release notes say otherwise.
- **Environment variables**: `%{ENV_VAR}` expansion in flags and yaml configs (e.g. `-metricsAuthKey=%{KEY}`). Recursively expands. Enable env-var flags with `-envflag.enable`; `.` in flag name → `_`; optional prefix via `-envflag.prefix`.
- **vmui**: `http://<host>:8428/vmui`.
- **Monitoring**: scrape VictoriaMetrics itself; exposed at `/metrics`.

## Storage tuning

- **IndexDB** grows with total series count and total label length. In Kubernetes (many labels, pod restarts) it can exceed the `data` folder by up to 2x.
  - Drop unneeded labels before storage (relabeling) — see `references/relabeling.md`.
  - Aggregate to fewer series (recording rules / stream aggregation) — see `references/stream-aggregation.md`.
  - For constant series sets, **disable per-day index** (low-churn-rate index tuning) to slow indexdb growth.
- **Deduplication** and **downsampling** reduce raw samples per series but do **NOT** reduce the number of stored series (so they don't shrink indexdb).

## Data safety

- Survives unclean shutdown (OOM, `kill -9`) thanks to storage architecture.
- Backups via instant snapshots + `vmbackup`/`vmrestore` — see `references/backup-restore.md`.

## When to load this

Load when deploying/operating a single-node instance: choosing flags, tuning index size, upgrading, or enabling scraping without vmagent.
