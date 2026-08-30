# ExternalDNS Key Flags Reference

Distilled from README, docs/flags, charts values, and tutorials. Every flag has an
`EXTERNAL_DNS_*` env equivalent (e.g. `--dry-run` → `EXTERNAL_DNS_DRY_RUN=1`).

## Core control flow

| Flag | Default | Purpose |
| --- | --- | --- |
| `--source` | service,ingress | K8s object kinds to watch (repeatable) |
| `--provider` | (required) | DNS backend (cloudflare, aws, ...) |
| `--policy` | upsert-only | `upsert-only` (no delete) / `sync` (reconcile+delete) / `create-only` |
| `--registry` | txt | `txt` / `noop` / `aws-sd` / `dynamodb` (ownership tracking) |
| `--txt-owner-id` | — | unique per cluster/instance; REQUIRED for safe multi-instance + non-empty zones |
| `--txt-prefix` / `--txt-suffix` | — | prefix/suffix for TXT ownership records (mutually exclusive; changing loses ownership) |
| `--dry-run` | false | log changes, make none |
| `--once` | false | single sync then exit (pair with `--dry-run` for validation; alone = applies) |
| `--interval` | 1m | reconcile interval |
| `--trigger-loop-on-event` | false | also reconcile on create/update/delete events |

## Scope / filtering

| Flag | Purpose |
| --- | --- |
| `--domain-filter` | plain suffix include (repeatable) |
| `--exclude-domains` | plain suffix exclude |
| `--regex-domain-filter` | RE2; overrides plain filters when set |
| `--regex-domain-exclusion` | regex exclude; standalone = exclusion-only |
| `--zone-id-filter` | limit to specific zone IDs (also tightens API scope) |
| `--service-type-filter` | Limit watched Service types (also trims informers) |
| `--label-filter` / `--annotation-filter` | limit cached objects |
| `--ignore-hostname-annotation` | ignore `hostname` annotation |
| `--annotation-prefix` | custom prefix for split-horizon (must end `/`) |
| `--target-net-filter` / `--exclude-target-net` | filter generated targets by CIDR |

## Ownership / safety decisions

- **Registry**: use `txt` unless you have a reason (aws-sd/dynamodb for AWS-native ownership,
  `noop` only for fire-and-forget with no conflict risk).
- **Policy**: `upsert-only` (Helm default) NEVER deletes — use `sync` if you want garbage collection.
- **txt-owner-id**: set a stable, cluster-unique value. Changing it or `--txt-prefix` forfeits
  ownership of existing records.
- **CNAME/TXT clash on ELB/ALB**: `--txt-prefix` (CNAME can't co-exist with other records).
- **Force CNAME for ELB/ALB instead of ALIAS**: `--aws-prefer-cname`.

## Provider / API tuning

| Flag | Purpose |
| --- | --- |
| `--kube-api-request-timeout` | per-request API timeout (default 30s) |
| `--kube-api-qps` / `--kube-api-burst` | API client rate (default 5 QPS / 10 burst) |
| `--cloudflare-dns-records-per-page` | up to 5000 |
| `--batch-change-size` / `--batch-change-interval` | batch API chunk size / pause |
| `--zone-cache` / `--provider-cache-time` | zone list / record caching TTLs |
| `--aws-assume-role` | cross-account zone management |
| `--aws-zone-type` | public/private (Route 53) |
| `--resolve-service-load-balancer-hostname` | resolve LB hostname to IPs |
| `--listen-endpoint-events` | reconcile on Endpoint changes (more API calls) |
| `--managed-record-types` | enable non-default types (SRV, NS, TXT, DNAME) |

## Helm chart key values

`provider.name`, `domainFilters`, `excludeDomains`, `sources`, `policy`, `registry`,
`txtOwnerId`, `txtPrefix`/`txtSuffix`, `annotationPrefix`, `interval`, `env`, `extraArgs`,
`rbac.create`, `serviceMonitor.enabled`, `namespaced`, `sourceNamespace`, `managedRecordTypes`,
`provider.webhook.*` (for webhook providers). Default `policy` in chart is `upsert-only`.

## Dry-run validation pattern (CI/staging)

```bash
external-dns --provider cloudflare --source service --once --dry-run
# exit 0 + logs planned CREATE/UPDATE/DELETE → safe to promote
# NEVER run --once without --dry-run in validation; it applies for real
```
