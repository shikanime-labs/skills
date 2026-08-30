---
name: book-victorialogs
description: "VictoriaLogs: data model, LogsQL, ingestion, querying, ops."
version: 0.1.0
author: Hermes
license: Apache-2.0
metadata:
  hermes:
    tags: [VictoriaLogs, LogsQL, Logging, Observability]
---

# VictoriaLogs Reference

Distilled notes from the official VictoriaLogs documentation
(<https://docs.victoriametrics.com/victorialogs/>). Covers the data model,
LogsQL query language, data ingestion, querying (HTTP/web UI/CLI), cluster
architecture, and alerting via vmalert. This is a knowledge base: the SKILL.md
index below points at per-topic `references/` files that must be loaded on
demand with `skill_view` (file_path="references/<file>"). It does NOT contain
the full docs — load a chapter only when a question needs it.

## When to Use

- "How do I query VictoriaLogs?" / "write a LogsQL query for ..."
- "How do I ingest logs into VictoriaLogs from <collector>?"
- "What is the `_stream` / `_time` / `_msg` field?"
- "Migrate this Loki/LogQL query to VictoriaLogs."
- "How does VictoriaLogs cluster scale / HA / replication work?"
- "Set up alerting on logs with vmalert."
- "Why is my VictoriaLogs ingestion slow / high cardinality?"

## Quick Reference (endpoints & ports)

- Listen: `http://localhost:9428` by default; storage at `victoria-logs-data`.
- Ingest: `/insert/jsonline`, `/insert/elasticsearch/_bulk`,
  `/insert/loki/api/v1/push`, `/insert/opentelemetry/v1/logs`.
- Query: `/select/logsql/query`, `/select/logsql/tail` (live),
  `/select/logsql/stats_query`, `/select/logsql/stats_query_range`,
  `/select/logsql/hits`, `/select/logsql/facets`, `/select/logsql/streams`,
  `/select/logsql/field_names`, `/select/logsql/field_values`.
- Web UI: `http://localhost:9428/select/vmui`. Metrics: `http://localhost:9428/metrics`.
- Cluster binaries are the same executable; flags `-storageNode`,
  `-insert.disable`, `-select.disable` switch the `vlinsert`/`vlselect`/`vlstorage` role.

## Procedure (typical task)

1. Run single-node: `./victoria-logs-prod` (or Docker
   `docker.io/victoriametrics/victoria-logs:v1.52.0`).
2. Ingest: POST ndjson to `/insert/jsonline?_msg_field=...&_time_field=...&_stream_fields=...`.
3. Query via Web UI `select/vmui`, `vlogscli`, or
   `curl http://localhost:9428/select/logsql/query -d 'query=error _time:5m'`.
4. Alert via vmalert pointing `-datasource.url` at VictoriaLogs with `type: vlogs` rules.

## Reference Files (load on demand)

- `references/01-keyconcepts.md` — data model: `_msg`, `_time`, `_stream`,
  `_stream_id`, high-cardinality rules. Load when reasoning about fields/streams.
- `references/02-ingestion.md` — HTTP APIs, all collectors, ingestion HTTP
  params (`_msg_field`, `_time_field`, `_stream_fields`, ...). Load before
  writing an ingest command or collector config.
- `references/03-logsql.md` — full LogsQL: filters, logical operators,
  pipes (`stats`, `sort`, `limit`, `fields`, `extract`, `math`, `top`, ...),
  stats functions, time formats, performance tips. Load when writing any query.
- `references/04-querying.md` — HTTP query API details, live tail, CSV,
  multitenancy headers, command-line/`head`/`less` integration, web UI.
- `references/05-cluster-ops.md` — cluster components/HA/replication,
  capacity planning, performance tuning, retention, upgrade, monitoring.
- `references/06-alerting-logql-migration.md` — vmalert integration (rules,
  flags, groups), LogQL→LogsQL conversion table, FAQ highlights.

## Pitfalls

- NEVER put high-cardinality fields (`ip`, `user_id`, `trace_id`) in
  `_stream_fields` — causes high-cardinality stream explosion.
- Queries without a `_time` filter scan all stored logs; add `_time:5m` etc.
- `time_filter`/`logical` precedence: `error -buggy OR foobar` parses as
  `(error AND NOT buggy) OR foobar`; wrap in parentheses.
- Cluster does NOT replicate; `vlinsert` shards across `vlstorage`. Use vlagent
  - vmauth across AZs for real HA.
- Loki substring `|= "error"` matches inside words; VictoriaLogs `error` matches
  whole words only.

## Verification

After the skill is created, confirm the index reconciles with the reference
files: all six `references/*.md` files exist and `skill_view` returns each.
