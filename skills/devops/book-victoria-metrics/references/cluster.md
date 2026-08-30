# VictoriaMetrics Cluster

Distilled from <https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/>
Reference: <https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/>

## Architecture (shared-nothing)

Three independently scalable services:

- **vmstorage** (port **8482**) — stores raw data, returns queried data for a time range + label filters.
- **vminsert** (port **8480**) — accepts ingested data, spreads it across vmstorage nodes via consistent hashing over metric name + all labels.
- **vmselect** (port **8481**) — performs queries by fetching needed data from all vmstorage nodes.

vmstorage nodes do not communicate with each other (shared-nothing) → high availability, easy scaling/maintenance.

## URL format (multitenancy)

- Write: `http://<vminsert>:8480/insert/<accountID[:projectID]>/<suffix>`
- Read: `http://<vmselect>:8481/select/<accountID[:projectID]>/<suffix>`
- Prometheus-compatible write suffix: `/insert/<tenant>/prometheus/api/v1/write`
- vmui per select: `http://<vmselect>:8481/select/<accountID>/vmui/`

## Multitenancy

- Tenants = `accountID` and optional `projectID`, 32-bit ints in `[0 .. 2^32)`. Auto-created on first write. `projectID` defaults to 0.
- Data evenly spread across vmstorage regardless of tenant → load balanced.
- Performance depends on total active series across tenants, not tenant count.
- List tenants: `http://<vmselect>:8481/admin/tenants`.
- **Via headers** (`--enableMultitenancyViaHeaders`, default-on since v1.150.0; introduced v1.143.0): set `AccountID` / `ProjectID` HTTP headers; simplified URLs `/insert/<suffix>` and `/select/prometheus/<suffix>`. Missing headers → `0:0`. Header `AccountID: multitenant` enables label-based tenancy.
- **Via labels**: `vm_account_id` / `vm_project_id` labels on ingest/query.
- Auth tokens / limits / accounting live in a front proxy (vmauth / vmgateway).

## Scaling & limits

- Cluster scales vertically AND horizontally: billions of active series, hundreds of millions of samples/sec (real usage).
- Single-node ceiling: ~100M active series, ~2M samples/sec. Use single-node for < 1M dps.
- **Replication**: supported (replication and data safety section).
- **HA**: supported (cluster HA section).

## Flags

- vmstorage uses `-storageDataPath` (like single-node). vminsert/vmselect have their own flags (`-storageNode` for select/insert to reach storage).
- Cluster-only enterprise flags: `-retentionFilter`, mTLS, TLS autocert.

## When to load this

Load when designing/operating a cluster: choosing node roles, wiring multitenancy, or deciding single-node vs cluster.
