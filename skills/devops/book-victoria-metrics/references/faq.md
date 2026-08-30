# FAQ & Capacity Planning

Distilled from <https://docs.victoriametrics.com/victoriametrics/faq/>
Reference: <https://docs.victoriametrics.com/victoriametrics/faq/>

## Scalability limits

- **Single-node**: vertical scaling. Up to ~100M active time series and ~2M samples/sec (real usage).
- **Cluster**: vertical + horizontal. Billions of active series, hundreds of millions of samples/sec.
- Use single-node for ingestion < 1M samples/sec; it's simpler to operate.

## Replace Prometheus?

- Yes, mostly: vmagent + single-node can scrape, vmagent/vmalert cover alerting/recording rules, Grafana queries via Prometheus API.

## vmagent vs Prometheus

- vmagent: less CPU/RAM/disk-IO at scale; independent disk-backed buffer per remote storage; supports pull + push protocols; no backfill limit; horizontal scaling of scrapers; better remote_write compression; improved relabeling; per-target metric limit; Kafka read/write.
- Prometheus agent: more limited; only reads scrape config from local FS.

## High cardinality

- Number of unique time series. Too many → more RAM, bigger indexdb, slower queries.
- Fixes: drop unneeded labels (relabeling), aggregate (recording rules / stream aggregation), use series limiter.
- indexdb grows with series count AND total label length. K8s pods add ~30-40 labels (~1KB/series) and restart churn → indexdb can exceed data folder 2x.
  - Disable per-day index for constant series sets (low-churn index tuning).
  - Deduplication/downsampling reduce raw samples but NOT series count → don't shrink indexdb.

## High churn rate

- Series appearing/disappearing rapidly (pod restarts in K8s). Optimize index; aggregate; use stream aggregation.

## Replication & HA

- Cluster: replication + data safety supported; HA for single-node and cluster.
- vmagent replication to multiple remote storages for HA.

## Disk space sizing

- See the "understand your setup size" guide: retention period × disk space per workload.
- Storage optimized for high-latency/low-IOPS (HDD, network storage).

## When to load this

Load when justifying single-node vs cluster, diagnosing memory/index growth, or planning capacity/cardinality control.
