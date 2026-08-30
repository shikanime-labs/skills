# Gateway and Listeners

Distilled from API Overview (GatewayClass/Gateway section), Traffic Matching, and the API spec.

## GatewayClass

- Cluster-scoped. At least one must exist for functional Gateways.
- Each `GatewayClass` handled by a single controller; a controller may handle multiple classes.
- Controller provides the `GatewayClass` resource users reference from their `Gateway.spec.gatewayClassName`.
- A cluster may have multiple GatewayClasses with different purposes (e.g. one forcing internal-only load balancers).

## Gateway

- `spec.gatewayClassName` (required) + `spec.listeners[]`.
- Binds one or more **Addresses** (how the Gateway is reached — usually IP; some impls use domain names) to **Listeners**.
- `spec` may omit fields (addresses, TLS) — the controller supplies them; this is made clear in `GatewayClass` Status (portability).
- Hard limit: **64 listeners per Gateway**. Exceed via `ListenerSet` (Extended, see `09-listenerset-deploy.md`).

### Listener fields

- `name` (string, referenced by route `sectionName`)
- `port` (integer)
- `protocol` — `TCP`, `UDP`, `TLS`, `HTTP`, `HTTPS`, `GRPC*` per route type supported.
- `hostname` (optional, for HTTP/HTTPS/TLS and their Routes; SNI for TLS).
- `tls` — termination mode + `certificateRefs` (HTTPS→`kubernetes.io/tls` Secret).
- `allowedRoutes` — restrict which Routes may attach (kinds + namespaces).

## Distinctiveness (critical)

Listeners must be **distinct** or they are **Conflicted**; a Gateway with conflicted listeners is invalid and never reaches `Accepted`.

| Protocol | Distinctness key | Notes |
| --- | --- | --- |
| TCP / UDP | (protocol, port) | Two UDP+TCP on same port are distinct; two TCP on same port are NOT. |
| TLS | (protocol, port, hostname) | hostname = SNI; `tls` stanza irrelevant to distinctness. |
| HTTP | (protocol, port, hostname) | |
| HTTPS | (protocol, port, hostname) + a TLS Secret ref | Different hostnames may share or use different Secrets. |

Consequence: traffic flowing through a Gateway **must only match a single Listener**. Once a Listener is chosen, the traffic **must** be routable via an attached Route **or be dropped** (no fall-through to another Listener).

## Attaching Routes to Gateways

- A Route attaches via `spec.parentRefs[].name` (and optional `sectionName`/`port`).
- Without `sectionName`, the Route attempts to attach to **all** Listeners on that Gateway.
- With `sectionName`, only the Listener whose `name` matches is **relevant**; empty match = that parentRef ignored.

### Listener restrictions on attachment (`allowedRoutes`)

- `kinds` (`RouteGroupKind[]`, max 8): which Route groups/kinds may bind (e.g. only `HTTPRoute`). Unknown kind → `ResolvedRefs=False` with `InvalidRouteKinds` reason.
- `namespaces` (`RouteNamespaces`, default `{from: Same}`):
  - `Same` — only the Gateway's namespace.
  - `All` — any namespace.
  - `Selector` — namespaces matching a label selector. Prefer `kubernetes.io/metadata.name` label (consistently set); custom labels can be spoofed.

On success, the Route counts in the Listener's `status.attachedRoutes`.

## Traffic matching (single-Listener rule)

- Traffic → IP selects a Gateway (only Gateways have addresses).
- On that IP/port → selects one or more Listeners; `hostname` further discriminates for HTTP/HTTPS/TLS.
- One candidate Route is chosen. **On Route match conflicts, the oldest Route's match wins.**
- If traffic matches no Route, it cannot select another Listener for rerouting — it is dropped (e.g. 404).

Example pitfall: Gateway with `specific.example.com` and `*.example.com` HTTP listeners on port 80; a request to `specific.example.com/other` matches no Route on the `specific` listener → 404, even though it could match the wildcard listener.
