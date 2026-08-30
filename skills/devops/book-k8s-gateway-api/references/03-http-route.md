# HTTPRoute

Distilled from HTTPRoute API spec, HTTP routing, traffic splitting, and redirect/rewrite guides.

## Purpose

- For multiplexing HTTP or terminated HTTPS; inspects the HTTP stream (use headers, methods, paths for routing or in-flight modification).
- GA / Standard Channel since v0.5.0; graduated to `v1` at v1.0.

## Structure

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
spec:
  parentRefs:                # attach to Gateway (or ListenerSet)
    - name: example-gateway
      sectionName: http      # optional: target one listener
  hostnames:                 # matched before any rule matching; single set
    - example.com
  rules:
    - matches: [...]         # AND within a match group; OR across match groups
      filters: [...]         # RequestRedirect, URLRewrite, RequestHeaderModifier, etc.
      backendRefs:           # weighted backends
        - name: example-svc
          port: 80
          weight: 90
    - backendRefs: [...]     # a rule with no matches = catch-all
```

## Matching

- `hostnames[]` — matched first; one set per Route. Different hosts → separate Routes.
- `rules[].matches[]` — each match has `path`, `headers`, `queryParams`, `method`. Fields within a match are ANDed; multiple matches are ORed.
- Path types: `Exact`, `PathPrefix`, `RegularExpression`.
- Header/query matches: `type: Exact|Prefix|RegularExpression`, `name`, `value`.

### Routing precedence

- Most specific match wins. Put specific routes (e.g. `env: canary` header, exact path) before generic catch-alls.
- Rule with no `matches` matches everything (catch-all) — place last.

## Traffic splitting / weighting

- `backendRefs[].weight` is a **proportional** split (sum = denominator). If unspecified, defaults to 1.
- Single backend → 100% regardless of weight.
- Canary: send test traffic via a header-matched rule to v2; then add v1/v2 as weighted backends in the same rule.
- Blue-green: set v1 `weight: 0`, v2 `weight: 1` to fully shift; revert quickly by flipping.
- If multiple Route rules target the same backend, weights are per-rule (not global).

## Filters

- Applied per route **rule**. Redirect and rewrite filters are **mutually incompatible** (cannot use both in one rule).
- **RequestRedirect** (status codes 301/302/303/307/308):
  - 301 permanent, 302 temporary (default), 303 POST→GET, 307/308 method-preserving.
  - Components independently substituted: `scheme`, `hostname`, `path` (`ReplaceFullPath`/`ReplacePrefixMatch`), `port`, `statusCode`.
  - HTTP→HTTPS: HTTP listener Route with `requestRedirect: {scheme: https, statusCode: 301}`; HTTPS listener Route forwards to backend.
- **URLRewrite**: change upstream `hostname` and/or `path` (same `ReplaceFullPath`/`ReplacePrefixMatch` modifiers) before proxying.
- **RequestHeaderModifier** / **ResponseHeaderModifier**: add/set/remove headers.
- **RequestMirror** (`mirror`/Extended): duplicate traffic to a backend for testing.

## Route merging

- Multiple Routes can bind the same Gateway and merge when they don't conflict.
- Merge semantics follow most-specific-wins; conflicts resolved per spec.
- Reference: HTTPRoute spec "Merging" rules (`https://gateway-api.sigs.k8s.io/reference/api-types/httproute/#merging`).

## Status / debugging

- `status.parents[].conditions`: `Accepted`, `ResolvedRefs`.
- `ResolvedRefs=False` causes: invalid backend ref (no ReferenceGrant for cross-ns), unknown Route kind (`InvalidRouteKinds`), missing Secret.
