# ExternalDNS Operational Best Practices

Distilled from docs/advanced/operational-best-practices.md (production readiness, memory, scaling, observability).

## Production readiness checklist

**Resource scope**

- `--service-type-filter=LoadBalancer` (or only the types you publish). Default watches Pods,
  EndpointSlices, Nodes unnecessarily.
- Add `--label-filter` / `--annotation-filter` to shrink the cached object set.

**Source configuration**

- Only enable `--source=` types whose CRDs are installed AND `ESTABLISHED` (`kubectl get crd <name>`).
- Grant RBAC `list` AND `watch` for every resource each source needs. `watch` missing → starts
  "healthy" but view frozen; DNS drifts silently, no crash, no warning.
- Scope RBAC to configured sources (excess hides misconfiguration).
- Per-cluster source lists in multi-cluster (Helm/ArgoCD values differ by CRD profile).
- Validate in staging with `--dry-run --once` before rollout.

**Scaling**

- Scope at every level: service type, label, annotation, domain, zone ID.
- Split large zone/source sets into instances with distinct `--txt-owner-id` + non-overlapping
  `--domain-filter` / `--zone-id-filter`.
- Tune reconcile interval; raise `--kube-api-request-timeout` (default 30s) on slow API servers.
- `--kube-api-qps` / `--kube-api-burst` if throttled or sharing API quota.

**Observability**

- Alert on `external_dns_controller_consecutive_soft_errors` > 0 for >1 reconcile cycle.
- Alert on sustained rise in `external_dns_source_errors_total` / `external_dns_registry_errors_total`.
- `--events-emit=RecordError` surfaces misconfigured endpoints on the responsible K8s resource.
- Watch `kube_pod_container_status_restarts_total` for crashloop (soft errors don't always crash).

**Registry/ownership**

- Unique `--txt-owner-id` per instance; avoid overlapping `--domain-filter`. Conflicts → errors,
  possible hard exit → crashloop.

**Provider**

- Set batch change size/interval for large or churny zones (see rate-limits doc).
- Enable zone caching (`--zone-cache`/provider flag) — zone enumeration is an API call per reconcile.
- Scope credentials to only managed zones (filters aren't the boundary).

## Informer scope & memory

`service` source registers informers for Services (always), Pods+EndpointSlices (NodePort/ClusterIP
in scope), Nodes (NodePort in scope).

| `--service-type-filter` | Informers removed |
| --- | --- |
| LoadBalancer | Pods, EndpointSlices, Nodes |
| LoadBalancer,ExternalName | Pods, EndpointSlices, Nodes |
| ClusterIP | Nodes |
| NodePort | none (all required) |

- Steady-state memory: without filter, external-dns caches every Pod/EndpointSlice/Node, not just
  DNS-relevant ones.
- Startup memory burst: classic LIST fetches all objects at once. Mitigated by `WatchListClient`
  feature gate (default true in recent client-go / latest external-dns). Use the latest release.

## Source validation failure modes (subtle symptoms)

| Misconfig | Symptom | Why subtle |
| --- | --- | --- |
| CRD not installed | `context deadline exceeded` ~60s | informer blocks on cache sync; no "CRD not found" |
| No LIST perm | `403 Forbidden` → exit | usually clean, but error path hard to map to source |
| LIST ok, WATCH denied | starts, never updates | frozen view, no crash, no log |
| Admission webhook misconfig | source inits, changes silently rejected | no error seen |

External-dns fails fast on a broken source by design (crashloop = clear signal). Silent staleness
comes from RBAC/watch gaps, not from source init.

## Scaling principles

1. Scope resources (every filter level). 2. Split instances (smaller blast radius, distinct owner
ID). 3. Reduce reconcile pressure (event-driven reconcile via `--trigger-loop-on-event`, slower
background polling, higher API timeout/QPS).

## State conflicts & ownership

On conflict errors: ensure ONE instance owns each zone/record set (distinct `--txt-owner-id`,
non-overlapping filters); remove conflicting records in the provider directly; fix invalid
definitions (CNAME+A/AAAA same name, self-pointing CNAME); check for other controllers writing the
zone. During migration/incident, scale external-dns to zero until state reconciles.

## Provider notes

- Zone list caching: in-memory cache of zone list for a TTL (e.g. `1h`); distinct from record
  caching (`--provider-cache-time`). Both can combine.
- Batch API: reduces API calls from linear-in-records to linear-in-batches; on batch failure,
  providers fall back to per-record calls so one bad record doesn't block the rest.
