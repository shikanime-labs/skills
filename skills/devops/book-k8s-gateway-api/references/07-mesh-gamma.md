# Service Mesh with Gateway API (GAMMA)

Distilled from the GAMMA / mesh documentation.

## GAMMA initiative

- Defines how Gateway API configures **service mesh** (east/west traffic).
- Standard Channel GA since **v1.1.0**.
- Key idea: when configuring a mesh, there's usually one mesh, so **Gateway/GatewayClass are NOT used**. Instead, Route resources attach **directly to a Service**.

## Why Service, not Gateway

- The Service resource is the most universal binding point for routing in a mesh.
- GAMMA formally defines Service **frontend** (name + cluster IP) and **backend** (collection of endpoint IPs) facets to be exact about mesh routing without duplicating Service.

## Attaching Routes to Services

- Route `spec.parentRefs` points at a Service instead of a Gateway:

```yaml
kind: HTTPRoute
spec:
  parentRefs:
    - name: smiley
      kind: Service
      group: core
      port: 80
  rules: [...]
```

- Which Routes attach is controlled by the Routes themselves (with Kubernetes RBAC).
- **Requests that match no attached Route are rejected.**
- If no Routes are attached to a Service, requests proceed with the mesh's default behavior (as if mesh absent).

## Producer vs Consumer Routes

- **Producer Route**: Route in the **same namespace** as its Service. Created by the workload's owner to define acceptable use. Affects **all** clients of that Service from any namespace.
- **Consumer Route**: Route in a **different namespace** than its Service. Refines how that consumer uses the workload (e.g. custom timeouts). Affects **only** clients in the Route's namespace.

```yaml
# Consumer route: 100ms timeout for clients in fast-clients ns
spec:
  parentRefs: [{ name: smiley, namespace: faces, kind: Service, group: core, port: 80 }]
  rules:
    - timeouts: { request: 100ms }
```

- Multiple Routes for the same Service in one Namespace (producer or consumer) are combined per HTTPRoute merging rules.
- **Limitation**: cannot define distinct consumer routes for multiple consumers in the **same** Namespace (e.g. `blender` and `mixer` both in `foodprep` calling `oven`). Move them to separate Namespaces to differentiate.

## Mesh request flow

1. Client workload requests `http://foo.ns.service.cluster.local`.
2. Mesh data plane intercepts; identifies traffic for Service `foo` in ns `ns`.
3. Locates Routes associated with `foo`:
   a. No Routes → request always allowed; `foo` workload is destination.
   b. Routes exist and request matches ≥1 → highest-priority matching Route's `backendRefs` selects destination.
   c. Routes exist but request matches none → **rejected**.
4. Data plane routes onward (usually endpoint routing, allowed service routing).
