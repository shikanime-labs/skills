# ListenerSet and Getting Started

Distilled from the ListenerSet guide and Deploying a Simple Gateway.

## ListenerSet (Extended support)

Enables delegated listener management for high-scale / multi-tenant setups; lifts the 64-listener Gateway limit.

- A `Gateway` does **not** allow ListenerSets by default. Enable with `spec.allowedListeners`:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
spec:
  allowedListeners:
    namespaces: { from: Same }     # or Selector with matchLabels
```

- A `ListenerSet` references its parent Gateway via `spec.parentRef`:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: ListenerSet
spec:
  parentRef: { name: parent-gateway, kind: Gateway, group: gateway.networking.k8s.io }
  listeners:
    - name: first
      hostname: first.foo.com
      protocol: HTTPS
      port: 443
      tls: { mode: Terminate, certificateRefs: [{ kind: Secret, name: first-workload-cert }] }
```

- Routes attach to a ListenerSet via `parentRefs` (`kind: ListenerSet`, `sectionName`).

### Listener conflicts across ListenerSets

- A Listener must be **distinct** across the Gateway + all attached ListenerSets (key: Port, Protocol, and Hostname per protocol).
- Precedence on conflict: (1) parent Gateway listeners win; (2) earliest creation time; (3) first alphabetically.
- Winner → `Accepted: true`; losers → `Accepted: false`, `Conflicted: true`. New conflicting ListenerSets never take over existing config (traffic stability).

## Install / getting started

Install CRDs (standard channel, v1.6.1 shown):

```bash
kubectl apply --server-side -f \
  https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.1/standard-install.yaml
# experimental (TLSRoute/TCPRoute/UDPRoute):
kubectl apply --server-side -f \
  https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.1/experimental-install.yaml
```

- Many controllers install the CRDs for you; pick a controller + its `GatewayClass` from the implementations list.
- Cleanup: replace `apply` with `delete` (only if not in use / not installed by a controller).

## Simple Gateway example (simplest deployment)

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: prod-web }
spec:
  gatewayClassName: example          # substitute your controller's class
  listeners:
    - { protocol: HTTP, port: 80, name: prod-web-gw, allowedRoutes: { namespaces: { from: Same } } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: foo }
spec:
  parentRefs: [{ name: prod-web }]
  rules:
    - backendRefs: [{ name: foo-svc, port: 8080 }]
```

- Gateway gets an IP in `status.addresses` after deploy (controller-assigned).
- Route receives traffic because same-namespace attachment is trusted by default.
- This single-owner model mirrors Ingress self-service.

## Typical guide path for new users

simple-gateway → http-routing → http-redirect-rewrite → traffic-splitting → multiple-ns → tls → tcp → grpc-routing → listener-set.
Migrating from Ingress: see the "Migrating from Ingress" / "Ingress-NGINX Welcome Guide" pages.
