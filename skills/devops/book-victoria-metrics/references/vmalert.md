# vmalert

Distilled from <https://docs.victoriametrics.com/victoriametrics/vmalert/>
Reference: <https://docs.victoriametrics.com/victoriametrics/vmalert/>

## What it is

- Executes alerting and recording rules against `-datasource.url`. Sends notifications via Alertmanager (`-notifier.url`). Persists recording-rule results via `-remoteWrite.url`.
- Compatible with Prometheus rule syntax. Keeps alert state on restarts.

## Key flags

- `-rule` — path/URL/glob to rules file (S3/GCS in enterprise). Validate with `-dryRun`.
- `-datasource.url` — storage to evaluate queries against (VM, VictoriaLogs, VictoriaTraces, Graphite, Prometheus).
- `-notifier.url` — Alertmanager URL (repeat for replicas; supports Consul/DNS SD via notifier config file).
- `-remoteWrite.url` — persist recording-rule/alert state (required for recording rules). Can differ from datasource (aggregate short-term → long-term).
- `-remoteRead.url` — restore alert state.
- `-external.label` — label applied to each rule result; conflicts renamed with `exported_` prefix.

## Rule file structure

```yaml
groups:
  - name: <unique>
    interval: <duration>        # default = -evaluationInterval
    eval_offset: <duration>     # align eval within [0..interval]; cannot use with eval_delay
    eval_delay: <duration>      # compensate datasource query delay
    limit: <int>                # 0 = no limit; marks rule errored if exceeded
    concurrency: <int>          # rules eval in parallel within group (default 1)
    type: prometheus|graphite|vlogs   # override -rule.defaultRuleType
    eval_alignment: <bool>      # default true (v1.95+)
    params:                     # HTTP URL params for all rule requests
      nocache: ["1"]
      denyPartialResponse: ["true"]
      extra_label: ["env=dev"]
    headers: ["CustomHeader: foo"]
    notifier_headers: ["TenantID: foo"]
    rules:
      - alert: <name>           # alerting rule
        expr: <query>
        for: <duration>
        labels: {...}
        annotations: {...}
      - record: <name>          # recording rule
        expr: <query>
```

## Limitations & notes

- Rules in a group eval **sequentially**; persistence is async → do NOT chain recording rules within a group (use chaining-groups pattern or stream aggregation instead).
- Network reliability risk: thresholds should tolerate failed requests.
- Recording/alerting rules **backfilling** ("replay") supported.
- Reusable annotation templates supported.
- Rules loadable from local FS, URL, GCS, S3.

## When to load this

Load when authoring alerting/recording rules, wiring Alertmanager, or debugging rule evaluation/grouping.
