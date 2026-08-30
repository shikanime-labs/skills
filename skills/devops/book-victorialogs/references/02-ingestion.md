# Data Ingestion — VictoriaLogs

Source: <https://docs.victoriametrics.com/victorialogs/data-ingestion/>

## Supported collectors

Syslog/Rsyslog/Syslog-ng, Filebeat, Fluent Bit, Fluentd, Logstash, Vector,
Promtail (Loki/Grafana Agent/Alloy), Telegraf, OpenTelemetry Collector,
Journald, DataDog, Splunk. Also `vlagent` for shipping/replication/buffering.

## HTTP ingestion APIs

- Elasticsearch bulk: `POST /insert/elasticsearch/_bulk` (ES/OpenSearch bulk JSON).
  Stops on first error. `_time:"0"` ⇒ server-side current timestamp.
- JSON stream (ndjson): `POST /insert/jsonline` with
  `Content-Type: application/stream+json`. Streams unlimited lines; skips invalid
  JSON lines (increments `vl_http_errors_total{path="/insert/jsonline"}`).
- Loki JSON: `POST /insert/loki/api/v1/push`. Stream labels ⇒ stream fields
  (unless overridden by `_stream_fields`). `message`/`time` auto-extracted.
- OpenTelemetry: `POST /insert/opentelemetry/v1/logs`.
- Journald export, Splunk also supported.

### Example: ndjson

```sh
echo '{ "log":{"level":"info","message":"hello"}, "date":"0", "stream":"s1" }
{ "log":{"level":"error","message":"oh no!"}, "date":"0", "stream":"s1" }' \
| curl -X POST -H 'Content-Type: application/stream+json' --data-binary @- \
  'http://localhost:9428/insert/jsonline?_stream_fields=stream&_time_field=date&_msg_field=log.message'
```

### Verify ingestion

```sh
curl http://localhost:9428/select/logsql/query -d 'query=*' | head
curl http://localhost:9428/select/logsql/query -d 'query=host.name:host123'
```

## HTTP parameters (query string OR headers)

Query-string args (priority over headers):

- `_msg_field` — field holding the message (usually `message` for Filebeat/Logstash).
  Comma list; first non-empty used. Falls back to `_msg`, then `-defaultMsgValue`.
- `_time_field` — field holding timestamp (usually `@timestamp`). Comma list.
  Falls back to `_time`, then ingestion time.
- `_stream_fields` — comma list of fields uniquely identifying the stream. If unset,
  taken from `_stream` field labels; if that's absent ⇒ default `{}` stream.
- `ignore_fields` — comma list to drop (supports `prefix*` wildcard).
- `decolorize_fields` — strip ANSI codes from listed fields (`prefix*` allowed).
- `extra_fields` — `field=value` pairs added to every log (override existing).
- `preserve_json_keys` — keep listed JSON keys unflattened (e.g. `host.os`).
- `debug=1` — don't store; log ingested rows instead (`vl_rows_dropped_total++`).

Headers (`VL-*`):

- `VL-Msg-Field`, `VL-Time-Field` — mirror `_msg_field`/`_time_field`.
- `VL-Preserve-JSON-Keys`, `VL-Decolorize-Fields` — mirrors of the args above.
- `AccountID`, `ProjectID` — multitenancy targeting (see multitenancy docs).

## Decolorizing

Drop ANSI codes before storage (collector-side or `decolorize_fields`).

## Troubleshooting

- `-logNewStreams` — log every newly registered stream (debug high cardinality).
- `-logIngestedRows` — log every ingested entry.
- Metrics: `vl_rows_ingested_total` (ingested since restart; rising ⇒ OK),
  `vl_streams_created_total` (rapid growth ⇒ cardinality issue),
  `vl_rows_dropped_total` (when `debug=1`).
- `curl .../select/logsql/query -d 'query=*' | head` confirms data stored.
