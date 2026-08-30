# Alerting (vmalert) & LogQL→LogsQL Migration

Sources:

- Alerting: <https://docs.victoriametrics.com/victorialogs/vmalert/>
- Migration: <https://docs.victoriametrics.com/victorialogs/logql-to-logsql/>
- FAQ: <https://docs.victoriametrics.com/victorialogs/faq/>

## Alerting with vmalert

vmalert integrates via the Prometheus-compatible stats APIs
`/select/logsql/stats_query` and `/select/logsql/stats_query_range`.

### Run vmalert

```sh
./bin/vmalert \
  -rule=alert.rules \
  -datasource.url=http://victorialogs:9428 \
  -notifier.url=http://alertmanager:9093 \
  -remoteWrite.url=http://victoriametrics:8428 \
  -remoteRead.url=http://victoriametrics:8428
```

- Rules are `type: vlogs` per group, OR set `-rule.defaultRuleType=vlogs`.
- Default rule type is `prometheus`; LogsQL rules need `vlogs`.

### Rule group shape

```yaml
groups:
- name: ServiceLog
  type: vlogs
  interval: 5m
  rules:
  - alert: HasMoreThan10ErrorLogs
    expr: '{env=prod} status:in(error,warn) | stats by (k8s.pod.name) count() as error_logs | filter error_logs:>10'
    annotations:
      description: 'Too many errors on pod {{ index .Labels "k8s.pod.name" }}: {{$value}}'
```

- `expr` MUST contain a `stats` pipe computing a metric, then `filter` for threshold.
- Use `stats by (...)`, `math` (extra calc), `fields` (keep needed metrics).
- Recording rule example:

  ```yaml
  - record: nginxRequestCount
    expr: '{env=test,service=nginx} | stats count(*) as requests'
  ```

### Multitenancy in rules

Per-group `headers: ["AccountID: 123"]` + `tenant: "123"`. (VictoriaLogs tenants via
`AccountID`/`ProjectID` HTTP headers, not URL path.)

### One vmalert for both VictoriaLogs + VictoriaMetrics

Use `vmauth` to route by path: `/api/v1/query.*` → VictoriaMetrics,
`/select/logsql/.*` → VictoriaLogs; set vmalert `-datasource.url=http://vmauth:8427/`.
VM cluster: rewrite Prometheus path to `vmselect:8481/select/<accountID>/prometheus`.
Grafana Alerting UI cannot show datasource-managed VictoriaLogs rules (datasource
limitation).

## LogQL → LogsQL conversion

### Data model note

- Loki and VictoriaLogs both have log streams; VictoriaLogs is optimized for wide events
  (hundreds of labels) and high-cardinality labels (`trace_id`, `user_id`, `ip`) — store
  them as separate fields, NOT packed JSON in the message (1000x faster filter, better compression).

### Stream selector

- Loki `{app="nginx",host="host-42"}` → identical in LogsQL `{app="nginx",host="host-42"}`.
- Required in Loki, optional in VictoriaLogs.

### Line filters

- `|= "text"` → `"text"` (word/phrase; matches whole words, not substrings).
  Sequence `{...} |= "foo" |= "bar"` → `{...} "foo" "bar"`.
- `!= "text"` → `-"text"`.
- `|~ "re"` → `~"re"`; `!~ "re"` → `NOT ~"re"`.
- Substring/word-prefix cases: use `prefix` filter or `regexp` filter if Loki substring
  matched inside words.

### Label filters

- `| label = value` / `== value` → `label:=value`.
- `| label != value` → `-label:=value`.
- `> >= < <=` → `label:>value` etc.
- `|~=` → `label:~value`; `!~=` → `-label:~value`.
- VictoriaLogs expects `:` after label names. Combine with `and`/`or`/`not`/`(...)`.

### IP / JSON / logfmt

- IP ranges → `ipv4_range("10.0.0.0/8")` / `ipv6_range(...)`.
- JSON packed in message: Loki `{...} | unpack | trace_id=="x"` →
  VictoriaLogs `{...} trace_id:=x` (store separately!). If already packed:
  `{...} | unpack_json fields (trace_id) | trace_id:=x` (slower).
- JSON arrays: `tags:json_array_contains_any("prod")` (avoids `tags=~".*prod.*"` false positives).
- logfmt: `{...} | logfmt` → `{...} | unpack_logfmt`.

### Metric queries

- `rate({...}[d])` → `_time:d {...} | stats by (_stream) count()` (or `| rate()`).
- `count_over_time({...}[d])` → `_time:d {...} | stats by (_stream) count()`.
  For Grafana hits graph, drop `_time:d` (Grafana supplies `step`).
- `sum(count_over_time({...}[d]))` → `{...} | count()`.
- `func({...} | unwrap label)` → pass label into stats func directly;
  group by stream with `... | stats by (_stream) ...`.
- `topk(K, ...)` → `... | first K (label desc)`; `bottomk` → `... | first K (label)`.
- `approx_topk` → `sample` pipe.
- Arithmetic `a op b` → `math` pipe.
- Playground auto-converter: <https://play-logql.victoriametrics.com/>

## FAQ highlights

- Production-ready since v1.0.0.
- vs Elasticsearch: up to 30x less RAM, 15x less disk, no index tuning, full-text on all
  fields out of the box.
- vs Loki: up to 1000x faster full-text; native high-cardinality support; easier LogsQL.
- vs ClickHouse: purpose-built for logs/any schema out of the box; ClickHouse needs
  pre-known schema for peak efficiency.
- Internals: columnar per-field blocks, bloom filters for word/phrase skipping, custom
  encodings (IP→4 bytes), stream grouping, sparse time index. Inspired by ClickHouse.
- Export: query `/select/logsql/query` with a time filter → stream of JSON lines.
- No `_msg` field: filled with `-defaultMsgValue`.
- Subqueries supported: `_time:1h _stream_id:in(_time:1h | top 3 (_stream_id) | keep _stream_id) | count_uniq(user_id)`.
- Resource estimate: ingest 1–10% of prod logs, run typical queries, measure, extrapolate.
  "Lightweight" narrow-stream queries are cheap at high rps; "heavy" long-range analytics
  with no stream filter may need hundreds of cores / TB RAM (still runs, just slower).
