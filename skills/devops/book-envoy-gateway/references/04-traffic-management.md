# Traffic Management

Source: Concepts/load-balancing, Concepts/rate-limiting, and Tasks/traffic index.

Configured mainly via `BackendTrafficPolicy` (and `ClientTrafficPolicy` for
downstream). Apply to `Gateway`, `HTTPRoute`, `GRPCRoute` via `targetRefs` or
`targetSelectors`.

## Load balancing

Types (set `spec.loadBalancer.type`):

| Type | Behavior |
| --- | --- |
| `RoundRobin` | Sequential across backends |
| `Random` | Random backend |
| `LeastRequest` | Fewest active requests — **default** |
| `ConsistentHash` | Hash (client IP/header) for session affinity |
| `BackendUtilization` | ORCA metrics weighted; falls back to even RR without metrics |

Example:

```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: BackendTrafficPolicy
metadata: { name: round-robin-policy, namespace: default }
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: round-robin-route
  loadBalancer:
    type: RoundRobin
```

### Backend Utilization (ORCA)

- Backend reports load in `endpoint-load-metrics` (JSON/TEXT) or
  `endpoint-load-metrics-bin` (base64 proto) headers/trailers.
- EG auto-removes these headers by default when `BackendUtilization` is enabled;
  keep them with `backendUtilization.keepResponseHeaders: true`.

## Rate limiting

Two kinds via `BackendTrafficPolicy.spec.rateLimit`:

- **Global** — shared across all Envoy instances via external Rate Limit
  Service (needs Redis). Enforced centrally.
- **Local** — per-instance, no external service, fast first-line defense.

Note: limits are **per route** even when the policy targets a `Gateway`
(3 routes => each gets its own 100r/s bucket).

Combined: local evaluated first, then global; request must pass both.

```yaml
# Global example
rateLimit:
  global:
    rules:
    - limit: { requests: 100, unit: Minute }
# Local example
rateLimit:
  local:
    rules:
    - limit: { requests: 50, unit: Minute }
```

`unit` values: `Second`, `Minute`, `Hour`, `Day`. Global rules support
`clientSelectors` (e.g. `sourceCIDR` with `type: Distinct`) and `shared`.

## Other traffic tasks (referenced by Tasks/traffic)

Routing: HTTP routing, gRPC routing, TCP/UDP routing, TLS passthrough, URL
rewrite, redirects, request mirroring, traffic splitting, session persistence,
zone-aware routing, multicluster, routing outside Kubernetes, backend routing.

Resilience/perf: circuit breakers, failover, fault injection, retries, HTTP
timeouts, gRPC timeouts, connection limit, bandwidth limit, request buffering,
response compression, response override, direct response, host header
normalization, HTTP/3, HTTP CONNECT tunnels, client traffic policy, gateway
address, gateway API support.

## Retry / circuit breaker / failover

- Configured under `BackendTrafficPolicy` (`retry`, `circuitBreaker`,
  `failover`). See `references/10-api-extension-types.md` for field names.
