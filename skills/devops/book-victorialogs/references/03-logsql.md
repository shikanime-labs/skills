# LogsQL — VictoriaLogs Query Language

Source: <https://docs.victoriametrics.com/victorialogs/logsql/>
Playground: <https://play-vmlogs.victoriametrics.com/>

## Basics

- A query is one or more `filters` joined by implicit or explicit `AND`, then
  optional `|` `pipes` for processing.
- Simplest query: a `word` searched in `_msg` by default → `error`.
- Quote words/phrases/fields that clash with keywords: `"and"`, `"error: cannot find file"`.
- Field prefix: `field:filter`. Default field is `_msg`. `log.level:error`.
- Multi-field search: `kubernetes.*:nginx` (prefix), `*:nginx` (any field).
  Prefer full field names — `*` scans all matching fields (slower).
- A single `_time` filter at top level is recommended for perf.
- Multi-line + comments allowed:

  ```logsql
  _time:5m
    # per-host error rate
    | stats by (host) count() logs, count() if (error) errors
    | math (errors / logs) as error_rate
    | filter error_rate:>0.1
  ```

  `;` optional terminator.

## Logical filters

- Implicit AND between space-separated filters: `_time:5m error` == `_time:5m AND error`.
- `NOT` / `-` / `!` negate. `=`/`~` negated shortcuts: `!=`, `!~`.
- `OR` inside parentheses. Precedence: `NOT > AND > OR`.
  - `error -buggy OR foobar` == `(error AND NOT buggy) OR foobar` → usually NOT intended.
  - Always parenthesize: `_time:5m error -(buggy_app OR foobar)`.
- Field prefix can be hoisted: `_time:5m log.level:error -app:(buggy_app OR foobar)`.

## Filters (cheat list)

- `word` — full word in field (default `_msg`). `error`.
- `phrase` — `"cannot open file"`.
- `prefix` — `foo*` (word/phrase prefix).
- `substring` — `:contains("...")` style / substring filter.
- `exact` — `field:=value`.
- `exact_prefix` — `field:="val*"`.
- `multi_exact` — `field:in(v1,v2)`.
- `regexp` — `field:~"a.+b"`, negated `!~`.
- `range` / `range_comparison` — `field:>v`, `field:>=v`, `field:<v`, `field:<=v`.
- `empty` — `field:""` (missing/empty), any-value `field:*`.
- `contains_all` / `contains_any` — `field:contains_any("a","b")`.
- `json_array_contains_any` — `tags:json_array_contains_any("prod")`.
- `ipv4_range` / `ipv6_range` — `field:ipv4_range("10.0.0.0/8")`.
- `sequence` — ordered words/phrases.
- `case_insensitive` / `equals_common_case` / `contains_common_case`.
- `subquery` — `field:in(<subquery>)`.
- `_stream` filter — `{app="nginx",host="host-42"}` (Loki-style selector, optional in LogsQL).
- `_stream_id` filter — `_stream_id:in(...)`.
- `time` / `day_range` / `week_range` — see Time below.

## Time filter `_time:`

- Duration relative: `_time:5m`, `_time:2.5d15m42.345s`, `_time:1y` → `[now-dur, now)`.
- Comparisons: `_time:>5m` (older than 5m), `_time:<5m`, `_time:>=1h`, `_time:<=1d`.
- Absolute UTC day/month/year/hour/min/sec: `_time:2023-04-25Z`, `_time:2023-04Z`,
  `_time:2023Z`, `_time:2023-04-25T22Z`, `_time:2023-04-25T22:45Z`.
- Range: `_time:[2023-04-01Z, 2023-04-30Z]` (inclusive), `_time:[a,b)` (excl b).
- Timezone suffix: `_time:2023-04-25+05:30`.
- Offset: `_time:5m offset 1h` → `(now-1h5m, now-1h]`; `time_offset` query option applies
  to all `_time` filters.

## Pipes (delimited by `|`)

- `stats` / `stats by (fields)` — aggregate. Functions below.
- `sort by (field)` / `sort by (field) desc` — sorts in memory; pair with `limit`.
- `limit N` / `offset N` — limit/random-skip rows.
- `fields f1, f2` — keep only listed fields, in order.
- `extract "pattern (<name>)"` — regex-extract fields at query time.
- `math (expr) as name` — arithmetic over stats results.
- `filter field:op value` — row-level filter on computed metrics.
- `top N by (field)` / `first N (field)` — top/bottom K (Loki topk/bottomk).
- `uniq` — deduplicate.
- `keep` / `drop` — keep/drop fields.
- `stream_context before N after M` — surrounding logs (stacktrace context).
- `unpack_json fields (...)` / `unpack_logfmt` — parse JSON/logfmt in a field.
- `sample` — probabilistic (approx_topk replacement).
- `block_stats` — per-field disk/row cost profiling.
- `query_stats` — data read/processed by the query (profiling).
- `time_add` — add duration to a field.

## Stats functions (in `stats` pipe)

`count()`, `count() if (cond)`, `count_uniq(field)`, `sum(field)`, `avg(field)`,
`min(field)`, `max(field)`, `median(field)`, `quantile(p, field)`, `rate()` (per-step rate
for Grafana `stats_query_range`), `values_bytes`, `rows`.
Group with `stats by (field1, field2)`.

## Performance tips

- Always add a top-level `_time` filter (narrows daily partitions skipped).
- Use exact field names, not `*` prefixes.
- Prefer positive/precise filters over negative phrase filters (`-"cannot open file"`
  can be slow → use `contains_any("a","b")`).
- `sort` without `limit` buffers all rows in RAM — add `limit`.
- `count_uniq()` and big `stats by (...)` track unique values in memory → reduce groups.
- Regex/JSON parsing are expensive — extract with `phrase`/`extract` first, then pipe.
- Profile incrementally: `_time:5m | count()`, add filters one at a time, then pipes;
  append `| query_stats` to see bytes/rows read.

## Examples

```logsql
_time:5m error | sort by (_time) desc | limit 10
_time:5m error -(buggy_app OR foobar)
_time:5m log.level:error {app not_in (buggy_app, foobar)}
_time:5m error | stats by (host) count() as errors
_time:1d ERROR | stats max(_time) as t | math round((now()-t)/1s) as secs_since
_time:5m stacktrace | stream_context before 10 after 100
```
