---
name: book-k8s-gateway-api
description: "Gateway API reference: resources, routes, TLS, mesh."
version: 0.1.0
author: Hermes
metadata:
  hermes.tags:
    - Kubernetes
    - Networking
    - Ingress
    - GatewayAPI
---

# Kubernetes Gateway API

Distilled reference for the Kubernetes [Gateway API](https://gateway-api.sigs.k8s.io/) (`gateway.networking.k8s.io`): its role-oriented resource model, routing, TLS, mesh (GAMMA), security/cross-namespace boundaries, versioning, and conformance. Use it to author, review, and debug Gateway API manifests and to map Ingress concepts onto it.

This skill codifies the **standard concepts, structure, and field semantics** of the API. It is not an implementation guide — exact CRD fields and supported feature sets vary by controller (Envoy Gateway, Istio, nginx, etc.). For implementation-specific behavior, consult that controller's docs.

## When to Use

- "Write a Gateway + HTTPRoute for <app>"
- "Why is my HTTPRoute not attaching / 404ing?"
- "How do I do TLS termination / passthrough / mTLS upstream?"
- "Migrate this Ingress to Gateway API"
- "Configure traffic splitting / canary / rewrites / redirects"
- "Attach a Route from another namespace" / "set up ReferenceGrant"
- "Route east-west traffic with Gateway API (GAMMA)"
- "What's the difference between GatewayClass, Gateway, Listener, ListenerSet?"

## Prerequisites

- `kubectl` with cluster access and a Gateway API controller installed (provides a `GatewayClass`).
- Gateway API CRDs installed (standard channel shown):
  - `kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.1/standard-install.yaml`
  - Experimental channel (TLSRoute/TCPRoute/UDPRoute): replace with `experimental-install.yaml`.
- Reference the live API spec at `https://gateway-api.sigs.k8s.io/reference/api-spec/main/spec/` for field-level detail.

## How to Run

- Author manifests with `write_file`; apply and inspect with `terminal` (`kubectl apply`, `kubectl get gateway/httproute -o yaml`, `kubectl describe`).
- Verify route attachment via `kubectl get httproute -o jsonpath='{.status.parents[*].conditions}'` (look for `Accepted`/`ResolvedRefs`).
- Load a specific reference file on demand with `skill_view(name="book-k8s-gateway-api", file_path="references/<file>")`.

## Quick Reference

- API group: `gateway.networking.k8s.io`. Core kinds: `GatewayClass`, `Gateway`, `HTTPRoute`, `GRPCRoute`, `TLSRoute`, `TCPRoute`, `UDPRoute`, `ReferenceGrant`, `ListenerSet`, `BackendTLSPolicy`.
- Personas: **Ian** (infra provider), **Chihiro** (cluster operator), **Ana** (app developer).
- Listener distinctiveness keys: `TCP`/`UDP` = (protocol, port); `TLS` = (protocol, port, hostname); `HTTP` = (protocol, port, hostname); `HTTPS` = same + a TLS Secret ref.
- Standard channel GA since: GatewayClass/Gateway/HTTPRoute v0.5.0 → v1 at v1.0; GAMMA mesh v1.1.0; TLSRoute v1.5.0; TCPRoute v1.6.0.
- Traffic must match exactly **one** Listener; if no Route matches, it is dropped (e.g. 404), never falls through to another Listener.

## Procedure

1. Pick/confirm the `GatewayClass` your controller provides (`kubectl get gatewayclass`).
2. Define a `Gateway` with `gatewayClassName` + one `listeners[]` entry (name, protocol, port, optional hostname, tls, allowedRoutes).
3. Define an `xRoute` with `spec.parentRefs[].name` pointing at the Gateway (or `sectionName`/`port` to target a specific listener).
4. Add `hostnames[]` + `rules[].matches[]` + `rules[].backendRefs[]` (with `weight` for splitting).
5. For cross-namespace refs, add `allowedRoutes.namespaces` on the listener and/or a `ReferenceGrant` in the target namespace.
6. Apply; check `Gateway.status.addresses` and each Route's `status.parents[].conditions` for `Accepted`/`ResolvedRefs`.
7. For TLS: terminate on the listener (`tls.mode: Terminate` + `certificateRefs`); for upstream re-encryption use `BackendTLSPolicy`; for frontend mTLS use `Gateway.spec.tls.frontend`.

## Pitfalls

- **Single-listener matching**: a request that fails to match any Route on its Listener is dropped — it does NOT fall back to a wildcard Listener. `specific.example.com/other` returns 404 even if `*.example.com` exists on another Listener.
- **Non-distinct Listeners → invalid Gateway**: a Gateway with two non-distinct Listeners never reaches `Accepted`.
- **ReferenceGrant required for cross-namespace refs** (Secrets, Service backends) — except Gateway→Route attachment, which uses listener `allowedRoutes` instead.
- **Experimental fields gated by VAP**: setting an experimental field without the magic annotation yields standard-channel behavior only.
- **Listener limit**: a Gateway supports at most 64 listeners; use `ListenerSet` (Extended) for more.
- **BackendTLS/GRPCRoute v1alpha2 upgrade**: standard channel excludes alpha versions; upgrade controller first, then CRDs.
- **Route merging** across Routes on the same Gateway only works when they don't conflict; match precedence favors the most specific rule.

## Verification

```bash
kubectl get gateway,gatewayclass,httproute -A
kubectl get httproute <name> -o jsonpath='{.status.parents[0].conditions}'
# Should contain Accepted=True and ResolvedRefs=True
```

## Reference Index

Load on demand with `skill_view(name="book-k8s-gateway-api", file_path="references/<file>")`:

- `references/01-overview-roles.md` — design goals, personas, resource model, request flow.
- `references/02-gateway-listeners.md` — Gateway/Listener spec, distinctiveness, listener selection, attaching routes.
- `references/03-http-route.md` — HTTPRoute matching, filters, redirects/rewrites, traffic splitting, merging.
- `references/04-other-routes.md` — GRPCRoute, TLSRoute, TCPRoute, UDPRoute.
- `references/05-tls.md` — downstream/upstream TLS, BackendTLSPolicy, frontend/backend mTLS.
- `references/06-security-namespaces.md` — RBAC, cross-namespace, ReferenceGrant, hostname hijacking, VAP.
- `references/07-mesh-gamma.md` — GAMMA service-mesh routing, producer/consumer routes.
- `references/08-versioning-conformance.md` — release channels, API versions, conformance, support levels.
- `references/09-listenerset-deploy.md` — ListenerSet, installation, the simple-gateway getting-started example.
- `references/10-glossary.md` — key definitions (north/south, east/west, endpoints, facets).
