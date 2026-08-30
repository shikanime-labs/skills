# Ingestion & Integrations

Distilled from <https://docs.victoriametrics.com/victoriametrics/integrations/> and the single-node page.
Reference: <https://docs.victoriametrics.com/victoriametrics/integrations/>

## Prometheus (remote_write)

- Single-node: add to prometheus.yml:

  ```yaml
  remote_write:
    - url: http://<vm-addr>:8428/api/v1/write
  ```

- Cluster: `http://<vminsert-addr>:8480/insert/<tenant>/prometheus` (load-balance across vminserts).
- Hot-reload: `kill -HUP $(pidof prometheus)`.
- Multi-instance: set `global.external_labels` (e.g. `datacenter`) so series are distinguishable.
- High load (200k+ sps): `queue_config.max_samples_per_send: 10000`, `capacity: 20000`, `max_shards: 30`. Remote_write adds ~25% Prometheus memory; lower those two if too high.
- Upgrade Prometheus to v2.12.0+ (older remote_write issues).
- **Native histograms** auto-converted to VM histogram format with `vmrange` labels (v1.143.0+); query with standard `histogram_quantile()`.
- **Remote Write 2.0** = experimental, NOT supported.

## Grafana

- VM is a drop-in for Prometheus datasource (supports Prometheus querying API). Use `http://<vm>:8428` as the datasource URL.

## InfluxDB line protocol

- Over HTTP, TCP, and UDP. Compatible agents: Telegraf.

## Graphite

- Plaintext protocol with tags; Graphite API (render/metrics/tags). VM can be a Graphite datasource in Grafana. Selectors via `{__graphite__="foo.*.bar"}` in MetricsQL.

## OpenTSDB

- `telnet put` protocol and HTTP `/api/put` requests.

## OpenTelemetry

- Native OTel metrics ingestion (protocol, naming, histogram conversion). OpenTelemetry Collector config under data-ingestion/opentelemetry-collector.

## DataDog / DogStatsD

- Agent or DogStatsD.

## NewRelic

- Infrastructure agent.

## JSON line / CSV / Native binary

- Direct import endpoints (`/api/v1/import/*`); see retention-backfilling for import paths.

## Zabbix

- Zabbix Connector streaming format.

## vmagent push endpoints (for LB)

- `/prometheus/api/v1/write`, `/influx/write`, `/api/v1/import`, `/api/v1/import/.*`.

## When to load this

Load when wiring a specific data source into VM (Prometheus remote_write, Grafana, InfluxDB, Graphite, OTel, DataDog, NewRelic, Zabbix).
