# Key Concepts — VictoriaLogs Data Model

Source: <https://docs.victoriametrics.com/victorialogs/keyconcepts/>

## Data model

- Every log entry is a single-level JSON object with string keys and string values.
- Every entry MUST contain at least a `_msg` field (the log message). Arbitrary
  extra `key=value` fields are allowed.
- Empty values are treated identically to missing values.
- Multi-level (nested) JSON is auto-flattened at ingestion:
  - nested dicts: keys concatenated with `.` → `{"host":{"name":"x"}}` ⇒ `host.name`.
  - arrays, numbers, booleans: converted to strings → `tags=["a","b"]` ⇒ `"[\"a\",\"b\"]"`.
- Field names and values may contain arbitrary characters (JSON-encoded at ingest).
- All fields are indexed automatically → full-text search works across every field.
- Preserve original JSON for chosen keys via `preserve_json_keys` query arg or
  `VL-Preserve-JSON-Keys` header.

## Special fields

### `_msg` (message field)

- Expected on every entry. If missing, filled from `-defaultMsgValue` flag.
- Custom source field via `_msg_field` query arg or `VL-Msg-Field` header
  (comma-separated list; first non-empty used).
- Selection logic: `_msg_field` set? → use first non-empty listed field. Else `_msg`
  present? → use it. Else → `-defaultMsgValue`.

### `_time` (time field)

- Formats accepted: ISO8601 / RFC3339 (`2023-06-20T15:32:10Z`,
  `2023-06-20 15:32:10.123456789+02:00`), or Unix seconds/ms/µs/ns
  (`1686026893`, `1686026893735`, ...).
- Missing timezone parsed in VictoriaLogs host local timezone.
- Custom source via `_time_field` / `VL-Time-Field` (comma list, first parseable used).
- If `_time` missing / `0` / `-` → ingestion time is used.
- Used by the `_time` filter for fast time-range narrowing.

### `_stream` / `_stream_id` (stream fields)

- A log stream = all entries from one application instance.
- `_stream_id`: unique numeric id for the stream; query with `_stream_id:...`.
- `_stream`: stream labels in Prometheus-style `{field="value",...}`, e.g.
  `{host="host-123",app="my-app"}`. Search with stream filters.
- Default `_stream` is `{}` if not configured → suboptimal storage/perf.
- Define stream fields via `_stream_fields` query arg at ingestion.

## Choosing stream fields (high cardinality)

- Stream fields MUST uniquely identify the app instance: `container`, `instance`,
  `host`, plus constant-during-lifetime fields like `namespace`, `node`, `pod`, `job`.
- Do NOT add all constant fields — wastes resources on ingest and query.
- NEVER add non-constant / high-cardinality fields (`ip`, `user_id`, `trace_id`)
  to streams → causes stream explosion:
  - ingestion/query perf degradation, more RAM/CPU/disk, more disk I/O.
- Metric guardrail: `vl_streams_created_total` (since last restart). Rapid growth
  ⇒ high-cardinality problem. Use `-logNewStreams` to log every new stream.

## Other fields

- Arbitrary fields (`level`, `ip`, `user_id`, `trace_id`) speed up search vs
  scanning `_msg`. `trace_id:=xxxx` is faster than `_msg:"trace_id=xxxx"`.
- VictoriaLogs handles high-cardinality fields fine — as long as they stay OUT of streams.

## Mental model

- message + time + stream are the three core axes.
- Columnar storage: each field is a column; queries read only referenced fields.
- Streams physically group same-source logs → better compression + faster stream-scoped queries.
