# Security and Cross-Namespace Boundaries

Distilled from Security, Roles & Personas, and Traffic Matching.

## RBAC model (write permissions)

Gateway API enables granular, role-oriented authorization via Kubernetes RBAC.

3-tier (simple):

| Role | GatewayClass | Gateway | Route |
| --- | --- | --- | --- |
| Infrastructure Provider | Yes | Yes | Yes |
| Cluster Operators | No | Yes | Yes |
| Application Developers | No | No | Yes |

4-tier (advanced) adds Application Admins: Route/Gateway writes only in specified namespaces.

- Gateway creation should be treated as a **privileged** permission (provisions LB + DNS). Restrict via Roles/RoleBindings; don't let regular users edit Gateway API status.
- Limit which namespaces can use a `GatewayClass` via ValidatingAdmissionPolicy.

## Crossing namespace boundaries — the handshake rule

Every cross-namespace capability requires an explicit handshake.

### 1. Route Binding (Gateway ↔ Route in different ns)

- Gateway owner explicitly allows it via listener `allowedRoutes.namespaces`.
- Prefer `Selector` with the `kubernetes.io/metadata.name` label (consistently set). Custom labels can be spoofed by anyone able to label namespaces.

```yaml
allowedRoutes:
  namespaces:
    from: Selector
    selector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: In
          values: [foo, bar]
```

### 2. ReferenceGrant (object refs across ns)

- Required for Gateway→Secret refs, Route→backend Service refs (and similar), in the **target** namespace.
- All cross-namespace references (except Gateway↔Route attachment) require a ReferenceGrant.
- Implementations MUST deny refs without a grant and revoke access when a grant is removed.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: ReferenceGrant
metadata: { name: allow-prod-traffic }
spec:
  from: [{ group: gateway.networking.k8s.io, kind: HTTPRoute, namespace: prod }]
  to:   [{ group: "", kind: Service }]
```

Minimize grants: specify `to` fully (`group`, `kind`, **and** `name`); never leave `name` open without strong reason (blanket grant).

## Avoiding hostname/domain hijacking

- Distinct Routes/ListenerSets can claim the same hostname; controllers resolve conflicts **first-come, first-served** (oldest creationTimestamp wins).
- Risk: an older Route that later adds a hostname already used by a newer Route hijacks it.
- Mitigation: delegate hostnames to specific namespaces via listener `allowedRoutes.namespaces` with `Selector` (good) instead of `All` (insecure).
- >64 listeners → use `ListenerSet` and gate hostnames with `ValidatingAdmissionPolicy`.

### Example ValidatingAdmissionPolicy (hostname allow-list)

- Reads allowed domains from a comma-separated `domains` annotation on the namespace.
- Denies HTTPRoute creation/update if any `spec.hostnames[]` entry isn't authorized.
- Cluster-admin must annotate: `kubectl annotate ns default domains=www.dom1.tld,www.dom2.tld`.
- (Example only — tune per environment; don't copy verbatim.)

### Limiting ReferenceGrant creation

- A `ValidatingAdmissionPolicy` can restrict which namespaces (label `referencegrants=allow`) may create ReferenceGrants, and constrain `from`/`to` kinds.

## Security checklist

- Gateway creation = privileged; gate it with RBAC.
- Use `kubernetes.io/metadata.name` selector for cross-ns Route binding.
- Always scope ReferenceGrant `to.name`.
- Delegate hostnames per namespace; avoid `allowedRoutes.namespaces.from: All` on shared Gateways.
