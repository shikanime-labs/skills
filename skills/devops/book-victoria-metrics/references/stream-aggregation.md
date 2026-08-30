# Stream Aggregation

Distilled from <https://docs.victoriametrics.com/victoriametrics/stream-aggregation/>
Reference: <https://docs.victoriametrics.com/victoriametrics/stream-aggregation/>

## What it is

- vmagent and single-node VM aggregate incoming samples **by time** and **by labels** before writing to remote/local storage.
- Reduces stored series / samples, and accelerates expensive queries that would otherwise scan huge series counts.

## Features & limitations

- Applies to all ingestion protocols + scraped targets.
- Can drop raw input matched by aggregation rules (`-streamAggr.keepInput` / `-streamAggr.dropInput`).
- Horizontally scalable.
- By default ignores input timestamps, processes on ingestion time (see "ignore old samples" option).
- **Aggregation state is in process memory → lost on restart.**

## Config shape

```yaml
- match: '<series selector>'
  interval: <duration>     # set >= 2x the matched metrics' collection interval
  without: [label, ...]    # labels removed from output (grouping dims dropped)
  by: [label, ...]         # labels kept
  outputs: [list, of, outputs]
```

### Output metric naming

- `<metric>:<interval>_without_<labels>_<output>` e.g. `http_requests_total:30s_without_path_user_total`
- `<metric>:<interval>_<output>` e.g. `some_metric:5m_count_samples`

### Common outputs (subset)

`total`, `total_prometheus`, `count_samples`, `sum_samples`, `min`, `max`, `rate_avg`, `rate_sum`, `increase`, `last`, `stddev`, `stdvar`, `quantiles`, `unique_samples`, `histogram_bucket`.
(See configuration page for the full list and histogram aggregation.)

## Use cases

- **Statsd alternative**: count/sum/quantile/histogram over input metrics.
- **Recording-rules alternative**: pre-aggregate at ingest. Example — replace slow `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[2m])) without (instance))` with:

  ```yaml
  - match: 'http_request_duration_seconds_bucket'
    interval: 1m
    without: [instance]
    outputs: [rate_sum]
  ```

  Then `histogram_quantile(0.99, avg_over_time(http_request_duration_seconds_bucket:1m_without_instance_rate_sum[5m])) > 0.5`.
- **Reduce stored samples** (downsampling): set `interval: 5m`, `outputs: [count_samples, sum_samples, min, max]` for non-`_total`; `[total]` for `_total`.
- **Reduce stored series**: `without: [high-cardinality labels]` to collapse dims.

## When to load this

Load when cutting cardinality/cost, replacing statsd or slow recording rules, or downsampling at ingest.
