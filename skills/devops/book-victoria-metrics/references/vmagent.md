# vmagent

Distilled from <https://docs.victoriametrics.com/victoriametrics/vmagent/>
Reference: <https://docs.victoriametrics.com/victoriametrics/vmagent/>

## What it is

- Tiny agent: collects metrics (pull + push), relabels/filters, ships to VictoriaMetrics or any remote_write storage.
- Drop-in for Prometheus scraping; usually less CPU/RAM/disk-IO than Prometheus. Single-node VM can also scrape directly (no vmagent needed).

## Key flags

- `-promscrape.config` — path or HTTP URL to Prometheus scrape config. Use `-promscrape.config.strictParse=false` to ignore unsupported sections.
- `-remoteWrite.url` — Prometheus-compatible remote storage endpoint (e.g. `https://host:8428/api/v1/write`). May be a DNS SRV record. Repeat for multiple backends.
- `-remoteWrite.tmpDataPath` — on-disk buffer when remote storage is down.
- `-remoteWrite.maxDiskUsagePerURL` — cap buffer disk usage (IoT/edge).
- `-remoteWrite.relabelConfig` — applied to all metrics before any remote write (v1.129+).
- `-remoteWrite.urlRelabelConfig` — per-destination relabeling (v1.129+).
- Config can be loaded from multiple files; scrape configs from HTTP(S) URLs.

## Use cases

- IoT/edge monitoring with unreliable links (disk-backed buffer, retries).
- Drop-in Prometheus replacement (scrape + forward).
- **Statsd alternative** when stream aggregation is enabled.
- Flexible metrics relay / replication / HA (multiple `-remoteWrite.url` = independent disk-backed buffers per destination).
- Sharding among remote storages; splitting streams to multiple systems.
- Relabeling & filtering; cardinality limiter (`-cardinalityLimiter` style) at scrape time.
- Kafka / Google PubSub read+write.

## Capacity & reliability

- Spreads big target sets across multiple vmagent instances (least-loaded).
- Independent buffer per `-remoteWrite.url` → slow/unavailable storage doesn't block healthy ones (Prometheus uses one shared 2h buffer).
- Better remote_write compression via the VictoriaMetrics remote_write protocol.

## When to load this

Load when configuring scraping, remote_write pipelines, relabeling at the agent, or HA/replication of ingestion.
