# Key Concepts

Distilled from <https://docs.victoriametrics.com/victoriametrics/keyconcepts/>

## Data model

- A **metric** is a numeric observation. Name should clarify what is measured (e.g. `requests_success_total`).
- **Labels** are `string` key-value pairs in `{...}`. The data model is schemaless — no need to predefine names/labels.
- The metric name is itself a label with key `__name__`. Since v1.111.0 the key may be omitted: `requests_total{code="200"}` == `{"requests_total", code="200"}`.
- A **time series** = metric name + its label set. `requests_total{code="200"}` and `{code="403"}` are two different series.
- **Cardinality** = number of unique time series. Too many = "high cardinality" → more resource usage.
- A **raw sample** = `(value, timestamp)`. Value stored as float64 with extra compression: up to 12 significant decimal digits (more precise digits may be lost). Timestamp is Unix time with **millisecond** precision.

## Resolution

- Minimum interval between raw samples of a series. In the **pull model** it equals `scrape_interval` (set by server). In the **push model** it is the client's sample interval.
- Keep resolution consistent; some MetricsQL functions expect it.

## Metric types (logical, not enforced by storage)

- **Counter**: only increases (except counter reset on restart). Use `rate()` / `increase()`. Suggested suffixes `_total`, `_sum`, `_count`.
- **Gauge**: value goes up and down (memory, temp, state `0/1`). Use aggregation / rollup functions.
- **Histogram**: set of counters for buckets (`_bucket`, `_sum`, `_count`).
- **Summary**: client-side quantiles.

## Global query view & pull/push

- Multiple data sources (Prometheus instances, agents) can ingest into one VictoriaMetrics; query all via a single query.
- **Pull**: VictoriaMetrics / vmagent scrape `/metrics` targets (Prometheus-compatible).
- **Push**: data sent via remote_write or ingestion protocols (InfluxDB, Graphite, OpenTSDB, OTel, etc.).

## Visualization & modification

- Built-in UI **vmui** at `http://<vm>:8428/vmui`.
- Storage uses MergeTree-like structures → no direct in-place data modification.
- **Deletion**: see `references/retention-backfilling.md` (delete_series).
- **Relabeling**: modify series before write, for pull and push. See `references/relabeling.md`.
- **Deduplication**: supported (see single-node `-dedup.minScrapeInterval` style flags on the component page).
- **Downsampling**: query-time rollup aggregation; does NOT reduce stored series count (only raw samples).

## Timestamp range

- Samples accepted in `[1970-01-02T00:00:00.000Z, 2262-03-31T23:59:59.999Z]`, millisecond precision.

## When to load this

Load when explaining what a metric/series/cardinality is, choosing counter vs gauge, or reasoning about pull vs push ingestion.
