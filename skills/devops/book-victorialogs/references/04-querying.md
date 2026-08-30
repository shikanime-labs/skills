# Querying VictoriaLogs

Source: <https://docs.victoriametrics.com/victorialogs/querying/>

## Ways to query

- Web UI (vmui): `http://localhost:9428/select/vmui`.
- `vlogscli` — interactive CLI (recommended; auto URL-encodes).
- Command-line: pipe `curl .../select/logsql/query` into `grep`, `jq`, `sort`,
  `less`, `head`, `wc`.
- HTTP API (below).
- Grafana plugin (`integrations/grafana`).

## HTTP query API — endpoints

- `/select/logsql/query` — main logs query (stream of JSON lines).
- `/select/logsql/tail` — live tailing (`tail -f` style).
- `/select/logsql/hits` — hits stats over time range (hits graph).
- `/select/logsql/facets` — most frequent values per field.
- `/select/logsql/stats_query` — instant log stats (Prometheus-compatible, for vmalert).
- `/select/logsql/stats_query_range` — range log stats (`step` from Grafana).
- `/select/logsql/stream_ids` / `streams` — stream ids / streams.
- `/select/logsql/stream_field_names` / `stream_field_values` — stream label names/values.
- `/select/logsql/field_names` / `field_values` — log field names/values.
- `/select/tenant_ids` — tenants across stored data.

## Querying logs (`/select/logsql/query`)

```sh
curl http://localhost:9428/select/logsql/query -d 'query=error'
curl http://localhost:9428/select/logsql/query -d 'query=error' -d 'limit=10'
curl http://localhost:9428/select/logsql/query -d 'query=error | limit 10'
curl http://localhost:9428/select/logsql/query -d 'query=error' -d 'timeout=4.2s'
curl http://localhost:9428/select/logsql/query -d 'query=error' -d 'format=csv'
```

- `query` arg: GET url or POST `x-www-form-urlencoded` body (POST for long queries).
  Must be percent-encoded when passed to `curl`.
- Response: stream of JSON lines `{field:"value",...}`; fields alphabetical unless a
  `fields`/`stats` pipe fixes order. Results NOT sorted by default (streaming).
- Limit results: close connection (safe with `*`), `limit=N` arg (+optional `offset=M`
  for pagination of most-recent N), `limit` pipe (random N), `_time` filter, tighter filters.
- `timeout` query arg overrides `-search.maxQueryDuration`.
- Multitenancy: `AccountID` / `ProjectID` headers (default tenant `0/0`).
- Pagination `limit=N&offset=M` returns up to N most-recent, skipping M most-recent.
- Response headers: `VL-Request-Duration-Seconds`, `AccountID`, `ProjectID`.
- `format=csv` returns CSV; specify fields via `fields`/`stats` pipe to avoid extra scan.
- Metric: `vl_http_requests_total{path="/select/logsql/query"}`.

## Live tailing (`/select/logsql/tail`)

```sh
curl -N http://localhost:9428/select/logsql/tail -d 'query=error'
curl -N http://localhost:9428/select/logsql/tail -d 'query=*' -d 'start_offset=1h'
curl -N http://localhost:9428/select/logsql/tail -d 'query=*' -d 'offset=30s'
curl -N http://localhost:9428/select/logsql/tail -d 'query=*' -d 'refresh_interval=10s'
```

- `-N` to curl is essential (disables buffering).
- Forbidden pipes in tail: `stats`, `uniq`, `top`, `sort`, `limit`, `offset`.
- Must select `_time`; returning `_stream_id` improves cross-stream accuracy.
- `start_offset=<d>` returns historical logs from last `<d>` before tail start.
- `offset` (default 5s) delays new logs so collectors can deliver (raise if gaps).
- `refresh_interval` (default 1s) sets poll frequency (don't set too low).
- Order preserved only within a single stream; across streams out-of-order.
- Best for ≤1K matching logs/sec (human-paced). Add filters if too fast.
- Metric: `vl_live_tailing_requests`.

## Command-line integration

- `curl .../query -d 'query=error' | head -10` — reads 10 then closes stream;
  VictoriaLogs cancels the query (frees CPU/RAM/IO). Iterate: refine → re-run.
- `less` suspends query when not scrolling; `jq` + `sort` for post-processing:

  ```sh
  curl .../query -d 'query=error' | jq -r '._time + " " + ._msg' | sort | less
  curl .../query -d 'query=_time:5m log.level:*' | jq -r '."log.level"' | sort | uniq -c
  ```

- Prefer `stats` pipe for server-side aggregation:
  `_time:5m log.level:* | stats by (log.level) count() matching_logs`.

## Web UI / Grafana

- vmui auto-applies the selected time range (no explicit `_time` needed there).
- Grafana plugin sends `step` for `stats_query_range` graphs.
