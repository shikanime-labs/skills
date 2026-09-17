# Caddy reverse_proxy → Gateway API migration

Replace a Caddy-based reverse proxy with native Gateway API resources. **Proven
in production on `apps/synapse-proxy` (PR #2057, 2026-09-01).**

## When to use

- "Refactor <app>/Caddyfile to gateway api"
- Replacing a Caddy sidecar/carrier pod that routes to multiple backends
- Caddy is doing path-based routing, header rewrites, static responses, or
  TLS termination that Gateway API can handle natively

## Mapping Caddy → Gateway API

### reverse_proxy → HTTPRoute + URLRewrite (rewrite Host)

Caddy's `reverse_proxy https://backend:port { header_up Host ... }` becomes an
HTTPRoute with a `URLRewrite` filter that rewrites the Host header:

```yaml
# Caddy: reverse_proxy https://synapse.shikanime.svc.cluster.local:8448 { header_up Host matrix.taila659a.ts.net }
# Gateway API:
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: matrix
spec:
  rules:
    - backendRefs:
        - name: synapse
          port: 8448
      filters:
        - type: URLRewrite
          urlRewrite:
            hostname: matrix.taila659a.ts.net
```

**Do NOT use `RequestHeaderModifier.set {name: Host}` to rewrite the upstream
Host.** EG v1.9 rejects it — `Host` is a reserved header the filter may not
set. The rule is dropped as `PartiallyInvalid: Dropped Rule(s) [N]` and that
rule returns HTTP 500; EG logs `RequestHeaderModifier Filter did not provide
valid configuration to add/set/remove any headers`. Use `URLRewrite`
(`urlRewrite.hostname`) or, when the installed CRD exposes it,
`backendRefs[].hostRewrite` (shikanime's HTTPRoute CRD v1.6.1 does not).
Verify the route reports `ResolvedRefs=True` with no `PartiallyInvalid`
after applying. (This exact pattern slipped through review on `apps/synapse`
in Sept 2026 and broke both `matrix` and `matrix-discord-media` fallback
rules post-merge; a follow-up URLRewrite PR fixed it after live validation.)

### Path-based routing → HTTPRoute matches

Caddy's `@isX path /a /b /c` + `handle @isX { ... }` becomes an HTTPRoute rule
with `matches` for each path prefix:

```yaml
# Caddy: @isDiscordDirectMediaApi path /.well-known/matrix/server /_matrix/media/*
# Gateway API:
- matches:
    - path:
        type: PathPrefix
        value: /.well-known/matrix/server
    - path:
        type: PathPrefix
        value: /_matrix/media
  backendRefs:
    - name: mautrix-discord
      port: 29334
```

Multiple rules in one HTTPRoute handle the fallback (second rule with no
matches catches everything else).

### Static responses → HTTPRouteFilter (directResponse)

Caddy's `respond '...' 200` has no core Gateway API equivalent. Use Envoy
Gateway's native `HTTPRouteFilter` (gateway.envoyproxy.io/v1alpha1) with a
`directResponse`, referenced from the route via an `ExtensionRef` filter.
This is stable and preferred over `EnvoyPatchPolicy`:

```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: HTTPRouteFilter
metadata:
  name: matrix-mautrix-wellknown
spec:
  directResponse:
    contentType: application/json
    statusCode: 200
    body:
      type: Inline
      inline: '{"fi.mau.bridges":[...]}'
```
```yaml
# in the HTTPRoute rule
filters:
  - type: ExtensionRef
    extensionRef:
      group: gateway.envoyproxy.io
      kind: HTTPRouteFilter
      name: matrix-mautrix-wellknown
```
Caveats: direct-response `body` is capped at 4096 bytes; a plain
`HTTPRouteFilter` is simpler and version-stable than `EnvoyPatchPolicy`
(whose `local_reply_config` JSONPatch against the listener breaks as xDS
resource names change across EG versions).

### Backend TLS → BackendTLSPolicy

When the upstream serves TLS (Caddy's `reverse_proxy https://...` with
`tls_server_name`), add a BackendTLSPolicy on the Service:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
metadata:
  name: synapse
spec:
  targetRefs:
    - name: synapse
      group: ""
      kind: Service
      sectionName: https
  validation:
    hostname: synapse.shikanime.svc.cluster.local
    caCertificateRefs:
      - name: nishir-ca-certificates.crt
        group: ""
        kind: ConfigMap
```

The `sectionName` must match the Service port name (e.g. `https` for port
8448). The `hostname` must match the upstream cert's SAN.

### HTTP→HTTPS redirect → HTTPRoute with RequestRedirect

Caddy's `:8008` listener redirecting to `:8448` becomes a separate HTTPRoute
attached to the Gateway's `http` listener with a `RequestRedirect` filter:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: matrix-redirect
spec:
  hostnames:
    - matrix.i.shikanime.studio
  parentRefs:
    - name: synapse-proxy
      sectionName: http
  rules:
    - filters:
        - type: RequestRedirect
          requestRedirect:
            scheme: https
            statusCode: 301
```

## Cleanup checklist

When removing the Caddy pod:

1. **Delete the workload**: StatefulSet/Deployment, Service, PVC, VPA,
   NetworkPolicy, and any `components/tls` that mounted the Caddy cert.
2. **Delete the Caddy cert**: The Certificate that Caddy used for its own
   TLS (not the backend cert — that's separate).
3. **Delete the Caddyfile ConfigMap**: The `configMapGenerator` in the
   overlay that produced the Caddyfile.
4. **Remove stale healthChecks**: The cluster overlay `ks.yaml` may have a
   `healthChecks` entry for the deleted StatefulSet — remove it or Flux will
   hang waiting for a pod that no longer exists.
5. **Remove stale netpol patches**: If the Caddy pod had a `patch-netpol.yaml`
   allowing ingress from `envoy-gateway-system`, remove it (the gateway now
   routes directly to the backend, not through Caddy).

## End-state structure

```
apps/<app>/
  base/
    httproute.yaml          # all routes (matrix, matrix-discord-media, redirect)
    kustomization.yaml      # resources: [httproute.yaml]
  overlays/nishir/
    backendtlspolicy.yaml   # if upstream serves TLS
    gateway.yaml            # Gateway with http + https listeners
    patch-httproute.yaml    # hostnames + parentRefs
    kustomization.yaml      # resources: [../../base, backendtlspolicy, gateway]
  overlays/nishir-tailnet/
    httproutefilter.yaml    # static responses (if any; HTTPRouteFilter directResponse)
    envoyproxy.yaml         # EnvoyProxy (tailscale LB)
    gatewayclass.yaml       # GatewayClass
    kustomization.yaml      # resources: [../nishir, gatewayclass, envoyproxy, httproutefilter]
```

The app no longer has its own workload — it's pure Gateway API config that
routes to existing backend Services.
