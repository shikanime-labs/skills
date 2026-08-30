---
name: book-envoy-gateway
description: "Reference for Envoy Gateway concepts, install, and tasks."
version: 0.1.0
author: Hermes
license: Apache-2.0
metadata:
  hermes:
    tags:
      - Kubernetes
      - GatewayAPI
      - Envoy
      - Ingress
      - TrafficManagement
    related_skills:
      - envoy-ai-gateway
      - envoy-byod-gateway
---

# Envoy Gateway Reference

Envoy Gateway is a Kubernetes-native API gateway and reverse proxy control plane.
It manages Envoy Proxy (data plane) from standard Kubernetes Gateway API
resources plus its own CRD extensions. This skill distills the upstream docs
(<https://gateway.envoyproxy.io/docs/>, v1.9.1) into load-on-demand reference
files. It does NOT replace the live docs for exact field schemas — use
`skill_view` to pull the relevant chapter before authoring manifests.

## When to Use

- "Install Envoy Gateway" / "EG via Helm or Flux"
- "Configure an HTTPRoute / GRPCRoute / TLSRoute / TCPRoute / UDPRoute"
- "Add rate limiting / load balancing / circuit breaker / retry to a route"
- "Set up auth: OIDC, JWT, API key, basic auth, mTLS, external auth"
- "Apply a SecurityPolicy / ClientTrafficPolicy / BackendTrafficPolicy"
- "Why is my Gateway not Programmed / route returning 500?"
- "Enable WASM / ext-proc / Lua / EnvoyPatchPolicy extension"
- "Merge gateways, multi-tenancy, namespace mode, egctl usage"

## Prerequisites

- A Kubernetes cluster (check the compatibility matrix:
  <https://gateway.envoyproxy.io/news/releases/matrix/>).
- `kubectl`, `helm`, and optionally `flux` CLI.
- A LoadBalancer implementation (e.g. MetalLB) so `Gateway` gets an Address.
- `egctl` for debugging: <https://gateway.envoyproxy.io/docs/install/install-egctl/>
- CRDs delivered by the Gateway API (standard or experimental channel) and
  Envoy Gateway CRDs (installed by the Helm chart by default).

## How to Run

- Install: invoke `helm install` / `kubectl apply` of Flux resources via the
  `terminal` tool (see references/03-installation.md).
- Author manifests with `write_file`; validate with `kubectl apply --dry-run=server`
  or `egctl x translate`.
- Inspect status: `egctl x status all -A` via `terminal`.
- Load a chapter on demand: `skill_view(name="book-envoy-gateway", file_path="references/04-traffic-management.md")`.

## Quick Reference

- Chart: `oci://docker.io/envoyproxy/gateway-helm` (version `v1.9.1`).
- Namespace: `envoy-gateway-system`.
- Core resources: `GatewayClass`, `Gateway`, `HTTPRoute`/`GRPCRoute`/`TLSRoute`/`TCPRoute`/`UDPRoute`.
- EG extensions (CRDs): `EnvoyProxy`, `EnvoyPatchPolicy`, `ClientTrafficPolicy`,
  `SecurityPolicy`, `BackendTrafficPolicy`, `EnvoyExtensionPolicy`, `Backend`, `HTTPRouteFilter`.
- Policy targeting: `targetRefs` (direct) or `targetSelectors` (label match).
- Default load balancer: **Least Request**. Default port mapping: privileged
  ports (<1024) are remapped internally to unprivileged.
- EG control plane ports: xDS 18000, RateLimit 18001, Admin 19000, Metrics 19001, Health 8081.

## Procedure

1. Install the Gateway API + Envoy Gateway CRDs (Helm or CRDs-only chart).
2. Create a `GatewayClass` (controllerName `gateway.envoyproxy.io/gatewayclass-controller`,
   optionally a `parametersRef` to an `EnvoyProxy`).
3. Create a `Gateway` with listeners (protocol/port/hostname).
4. Create `HTTPRoute` (etc.) with `parentRefs` to the Gateway and `rules`.
5. Apply security/traffic policies by attaching them via `targetRefs`.
6. Verify with `egctl x status all -A` and a `curl` through `GATEWAY_HOST`.

## Pitfalls

- A policy can only target resources in the **same namespace** as the policy.
- Multiple policies at the same level resolve by creation time, then name.
- When `mergeType` is unset, only the most specific policy wins (no merge).
- Unaccepted config => Envoy assigns a `direct_response` => clients see **HTTP 500**.
- Helm does NOT upgrade CRDs in `/crds`; upgrade CRDs before the chart, or TCP/UDP
  routes are silently skipped (Gateway API v1.6 moved them to `v1`).
- `v1alpha2` TCP/UDPRoute manifests break on standard channel v1.6 — migrate to `v1`.

## Verification

- `egctl x status all -A` shows all resources `Accepted`/`Programmed`/`ResolvedRefs=True`.
- `curl --header "Host: www.example.com" http://$GATEWAY_HOST/get` returns 200.

---

## Reference Index (load on demand with `skill_view`)

- `references/01-architecture-resources.md` — layers, resource table, what EG does/doesn't do.
- `references/02-gateway-api-extensions.md` — policy attachment model, precedence, merging, all extension CRDs.
- `references/03-installation.md` — Helm, Flux, CRD-only, ports, customization, upgrades.
- `references/04-traffic-management.md` — load balancing, rate limiting, routing, retries, circuit breakers, session persistence.
- `references/05-security.md` — SecurityPolicy, OIDC/JWT/API-key/basic/mTLS/external auth, CORS, TLS.
- `references/06-extensibility.md` — WASM, ext-proc, Lua, dynamic modules, EnvoyPatchPolicy, extension server.
- `references/07-observability.md` — metrics, access logs, tracing, Grafana, rate-limit observability.
- `references/08-operations.md` — deployment modes, multi-tenancy, namespace mode, egctl, graceful shutdown.
- `references/09-troubleshooting.md` — config issues, status checks, admin console, access logs.
- `references/10-api-extension-types.md` — key CRD field references (SecurityPolicy, rate limit, LB, health check).
