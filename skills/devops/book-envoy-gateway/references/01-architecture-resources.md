# Architecture & Resources

Source: Concepts overview, Proxy, Gateway API pages (gateway.envoyproxy.io/docs/concepts).

## What Envoy Gateway is

- Kubernetes-native **API gateway + reverse proxy control plane** that manages
  Envoy Proxy as a data plane.
- Uses the standard **Kubernetes Gateway API** plus EG's own CRD extensions.
- Succeeds the legacy Ingress API (regex path matching, type-safety, portability
  were its weak points; Ingress needed custom annotations that fragmented
  implementations).

## The three layers

| Layer | Role |
| --- | --- |
| User Configuration | Gateway API resources + EG CRDs (optional) |
| Envoy Gateway Controller | Control plane: watches resources, translates, produces Envoy config (xDS) |
| Envoy Proxy (Data Plane) | High-performance proxy handling live traffic |

- Control plane translates Gateway API + EG resources into **xDS configuration**
  and runs/updates the Envoy Proxy instances in-cluster.
- Envoy Proxy is a CNCF-graduated, L3/L4/L7 proxy (originally Lyft).

## Resource inventory

### Kubernetes Gateway API (required)

| Resource | Purpose |
| --- | --- |
| `GatewayClass` | Defines a class of Gateways with common config |
| `Gateway` | How traffic enters the cluster |
| `HTTPRoute` / `GRPCRoute` / `TLSRoute` / `TCPRoute` / `UDPRoute` | Routing rules per traffic type (collectively "Route") |

### Envoy Gateway CRDs (optional, "Customize & Extend")

| Resource | Targets | Purpose |
| --- | --- | --- |
| `EnvoyProxy` | GatewayClass, Gateway | Deployment/config of the Envoy proxy itself |
| `EnvoyPatchPolicy` | GatewayClass, Gateway | Custom xDS patches |
| `ClientTrafficPolicy` | Gateway, ListenerSet | Downstream client connection behavior (TLS, timeouts, HTTP/3, headers) |
| `BackendTrafficPolicy` | Gateway, Route, ListenerSet | Upstream behavior (LB, rate limit, circuit breaker, retries) |
| `SecurityPolicy` | Gateway, Route, ListenerSet | AuthN/Z, CORS, external auth |
| `BackendTLSPolicy` | Service | TLS settings for backend connections |
| `EnvoyExtensionPolicy` | Gateway, Route, Backend | Envoy proxy extensions (WASM, ext-proc, Lua) |
| `Backend` | — | Cluster-external backends via FQDN/IP; UDS external processes |
| `HTTPRouteFilter` | HTTPRoute | Extra request/response processing |

- **Most specific configuration wins** for `BackendTrafficPolicy`,
  `SecurityPolicy`, `ClientTrafficPolicy`, `EnvoyProxy`, `EnvoyPatchPolicy`,
  `EnvoyExtensionPolicy`.

## What the skill does NOT cover in depth

- Exact per-field API schemas (thousands of fields) — use
  `references/10-api-extension-types.md` for the common ones and the upstream
  API reference for the rest.
- AI Gateway (separate product, see `envoy-ai-gateway` skill).
