# MetricsQL

Distilled from <https://docs.victoriametrics.com/victoriametrics/metricsql/>
Reference: <https://docs.victoriametrics.com/victoriametrics/metricsql/>

## Relationship to PromQL

- MetricsQL is a **superset** of PromQL — backwards compatible. Grafana dashboards on a Prometheus datasource work unchanged after switching to VictoriaMetrics.
- Intentional differences that improve UX (do NOT assume Prometheus behavior):
  - `rate()` / `increase()` include the last raw sample **before** the lookbehind window → exact `increase(metric[$__interval])` results.
  - No **extrapolation**: `increase()` over a slow integer counter returns integer results (Prometheus can return fractional).
  - Returns non-empty for `rate()` even when Grafana/vmui pass `step` smaller than the raw-sample interval.
  - `scalar` is treated the same as an instant vector without labels.
  - All `NaN` values are removed from output (Grafana draws nothing for NaN anyway).
  - Functions that don't change meaning keep the metric name (e.g. `min_over_time(foo)`, `round(foo)` keep `foo`). Use `keep_metric_names` to keep names after `rate()`.

## Extra syntax (not in PromQL)

- Graphite filters: `{__graphite__="foo.*.bar"}`.
- Lookbehind window in `[...]` for rollup functions may be **omitted**; VM auto-selects based on `step` / scrape interval. `rate(node_network_receive_bytes_total)` is valid.
- Numeric underscores for readability: `1_234_567_890`.
- Multiple `or` filters: `{env="prod",job="a" or env="dev",job="b"}`.
- Match multiple numeric constants: `status_code == (300, 301, 304)`.
- `group_left(*)` / `group_right(*)` copy all labels from the `one` side; optional `prefix "ns_"` to avoid clashes.
- Aggregate functions accept arbitrary number of args: `avg(q1, q2, q3)`.
- `@` modifier anywhere: `sum(foo) @ end()`; arbitrary subexpression: `foo @ (end() - 1h)`.
- `offset` anywhere: `sum(foo) offset 24h`. Fractional offsets/windows allowed: `rate(m[1.5m] offset 0.5d)`.
- Duration suffix optional — seconds if missing: `rate(m[300] offset 1800)` == `rate(m[5m]) offset 30m`.
- Size suffixes `K, Ki, M, Mi, G, Gi, T, Ti`.
- Trailing commas allowed in label filters, function args, `WITH` expressions.

## Implicit rollup conversion

- Bare series selectors are wrapped in `default_rollup`: `foo` → `default_rollup(foo)`.
- `rate` / `default_rollup` use `max(step, scrape_interval)` to avoid gaps when step < scrape_interval.
- Other rollups auto-use `max(step, scrape_interval)` (aka `$__interval` / `1i`).
- Disable/log implicit conversion with `-search.disableImplicitConversion` / `-search.logImplicitConversion` (v1.102.0-rc2+).

## Common functions (verify signatures on the page)

- `rate(m[d])` — per-second average increase; counters only.
- `increase(m[d])` — growth over window.
- `keep_metric_names` — modifier after a function to preserve the metric name.

## When to load this

Load when writing or debugging a MetricsQL/PromQL query, especially counter rates, `group_left`, or implicit rollup behavior.
