---
name: book-victoria-metrics
description: "VictoriaMetrics reference: metrics, queries, cluster, ops."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [VictoriaMetrics, Monitoring, TSDB, Prometheus]
---

# VictoriaMetrics Docs

Knowledge base distilled from the official VictoriaMetrics documentation
(<https://docs.victoriametrics.com>). Covers architecture, the MetricsQL query
language, single-node and cluster deployment, the vm* components, data
ingestion protocols, relabeling, stream aggregation, backups, retention, and
Kubernetes (Operator/Helm).

It does NOT replace the live docs for version-specific flags — always confirm
flag defaults against the relevant page or `-help` for your binary version.

## When to Use

- "How do I deploy VictoriaMetrics (single-node vs cluster)?"
- "What is the MetricsQL syntax for <query>?"
- "How do I scrape/ingest with vmagent, or write alerting rules with vmalert?"
- "How do I set up vmbackup / vmrestore / vmbackupmanager?"
- "How does VictoriaMetrics cluster (vminsert/vmselect/vmstorage) work?"
- "How do I send data from Prometheus, Grafana, InfluxDB, OpenTelemetry, ...?"
- "What is high cardinality / high churn and how do I fix it?"

## How to Run

Load a reference on demand with `skill_view`
(file_path="references/<file>.md"). Sources were gathered via `web_extract`
from docs.victoriametrics.com.

## Quick Reference

- Docs root: <https://docs.victoriametrics.com/>
- Single-node main: <https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/>
- Cluster: <https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/>
- MetricsQL: <https://docs.victoriametrics.com/victoriametrics/metricsql/>
- Query port (default): 8428
- Storage path flag: `-storageDataPath` (default `victoria-metrics-data`)
- Retention flag: `-retentionPeriod` (default 1 month, min 24h)

## Reference Index

- references/key-concepts.md — mental models: metrics, samples, time series, storage, global query view, scrape vs push
- references/metricsql.md — MetricsQL syntax, functions, vs PromQL
- references/single-node.md — single-node deploy, flags, monitoring, tuning
- references/cluster.md — vminsert/vmselect/vmstorage, multitenancy, scaling
- references/vmagent.md — scraping, relabeling, remote write, capacity
- references/vmalert.md — alerting/recording rules, Rule, Group, Alert
- references/vmauth-vmgateway.md — auth proxies, load balancing, rate limiting
- references/stream-aggregation.md — downsampling, statsd alternative
- references/ingest-integrations.md — Prometheus, Grafana, InfluxDB, Graphite, OpenTSDB, OTel, DataDog, NewRelic, Zabbix
- references/relabeling.md — relabel config, labels, filters
- references/backup-restore.md — vmbackup/vmrestore/vmbackupmanager, snapshots
- references/retention-backfilling.md — retention, backfill, delete series
- references/faq.md — high cardinality, churn, capacity planning, sizing
- references/kubernetes.md — Operator, Helm charts, vmcluster

## Procedure

1. Identify the topic from the user's question.
2. Load the matching reference via `skill_view` (file_path=...).
3. Apply the verbatim flags/endpoints/config from the reference.
4. For version-specific details, cross-check the linked docs page.

## Pitfalls

- Single-node flags differ from cluster component flags (vmstorage uses
  `-storageDataPath`; vminsert/vmselect have their own).
- `-retentionPeriod` minimum is 24h; large values use `m`/`y` suffixes.
- Enterprise-only flags (TLS autocert, some query stats) are gated to
  enterprise binaries.

## Verification

- After applying a config, confirm the process starts and exposes
  `http://localhost:8428/metrics` (or `/health`). Load a reference and re-read
  the relevant flag name if a flag is rejected.
