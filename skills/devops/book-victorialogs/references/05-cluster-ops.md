# Cluster, Operations & Ops — VictoriaLogs

Sources:

- Cluster: <https://docs.victoriametrics.com/victorialogs/cluster/>
- README ops (retention, tuning, monitoring, upgrade): <https://docs.victoriametrics.com/victorialogs/>
- Metrics: <https://docs.victoriametrics.com/victorialogs/metrics/>

## Single-node vs cluster

- Prefer single-node on bigger hardware when it fits — simpler, faster (no network hops).
- Cluster only when single-node vertical limit is hit. Migration is trivial: add the
  node's TCP address to `-storageNode` on `vlinsert`/`vlselect`.

## Cluster architecture (3 components, same binary)

- `vlinsert` — accepts all ingest protocols; shards logs across `vlstorage` nodes (`-storageNode`).
- `vlselect` — accepts all query endpoints; runs queries in parallel across `vlstorage`,
  merges results.
- `vlstorage` — stores logs (`-storageDataPath`); executes queries from `vlselect`.
- Role switching via flags on the single binary:

  ```sh
  ./victoria-logs-prod -storageNode=vlstorage-1:9428,vlstorage-2:9428   # both insert+select
  ./victoria-logs-prod -storageNode=... -insert.disable                   # select only
  ./victoria-logs-prod -storageNode=... -select.disable                   # insert only
  ./victoria-logs-prod                                                   # vlstorage (no -storageNode)
  ```

- Inter-component comms: HTTP on `-httpListenAddr` (9428). `vlinsert`→
  `vlstorage` at `/internal/insert`; `vlselect`→`vlstorage` at `/internal/select/*`.
  Reverse proxies can add auth/routing/TLS.
- Run separate `vlinsert` and `vlselect` node sets so ingest load doesn't perturb queries.
- Each `vlstorage` is independently queryable: `curl http://localhost:9491/select/logsql/query -d 'query=* | count()'`.

## High availability

- Ingestion HA: if some `vlstorage` down, `vlinsert` spreads to remaining nodes — no loss.
  Ensure remaining nodes have capacity headroom.
- Query path: unavailable/incompatible `vlstorage` → `502 Bad Gateway` (consistent responses).
  Incompatible API usually = rolling upgrade mismatch (check changelog).
- Partial responses possible via querying docs (`partial-responses`) if 502 is undesirable.
- Real HA (ingest+query) requires copies in independent AZs via `vlagent` (replicate+buffer)
  and `vmauth` (route queries to healthy cluster). No consensus/magic-coordination.

## Replication

- `vlinsert` SHARDS (not replicates) across `vlstorage`. Linear capacity scaling.
- No intra-cluster replication → rely on regular backups of every `vlstorage`
  (`backup-and-restore` docs) for disaster recovery.

## Capacity planning (spare headroom)

- 50% free RAM (avoid OOM/slowdowns on spikes).
- 50% free CPU (spikes).
- ≥20% free disk at `vlstorage` (`-storageDataPath`) — too little slows merges.

## Performance tuning (usually none needed)

- Defaults auto-adapt. Constrained-resource knobs:
  - `vlinsert`: `-insert.concurrency` (higher ingest rate, more RAM); `-insert.disableCompression`
    (less CPU, more network).
  - `vlselect`: `-select.disableCompression` (less CPU, more network).

## Retention & storage

- Default retention 7 days (`[now-7d, now]`); configure `-retentionPeriod`
  (`1d`..`100y`, Prometheus duration format).
- Storage dir `-storageDataPath` (default `victoria-logs-data`).
- Filesystem `ext4` recommended; for >1TB `ext4` pass
  `mkfs.ext4 ... -O 64bit,huge_file,extent -T huge`.
- OS: raise open-files limit; defaults otherwise fine.

## Monitoring

- Metrics at `http://localhost:9428/metrics` (Prometheus format). Scrape via
  VictoriaMetrics/vmagent/Prometheus.
- Grafana dashboards: single-node 22084, cluster 23274.
- Alerts: `alerts-vlogs.yml`, `alerts-health.yml` via vmalert/Prometheus.
- Key metrics: `vl_rows_ingested_total`, `vl_streams_created_total` (cardinality guard),
  `vl_http_requests_total{path=...}`, `vl_http_request_duration_seconds{path=...}`,
  `vl_live_tailing_requests`, `vl_http_errors_total{path=...}`, `vl_rows_dropped_total`.

## Upgrading

- Safe to upgrade/downgrade/skip versions unless release notes say otherwise; SIGINT
  to stop gracefully, wait, start new version. Restart `vlstorage` nodes for rolling upgrades.

## Tuning summary

- No manual tuning required; flags auto-adjust to CPU/RAM. Only raise open-file limit.
