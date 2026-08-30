# Overview, Roles, and Resource Model

Distilled from `gateway-api.sigs.k8s.io` Introduction, API Overview, and Roles & Personas.

## What Gateway API is

- Official Kubernetes project for **L4/L7 routing** — the next generation of Ingress, Load Balancing, and Service Mesh APIs.
- Generic, expressive, **role-oriented**, and **portable** (many implementations, like Ingress).
- API group `gateway.networking.k8s.io`; resources are CRDs. All unqualified resource names are in this group.
- Serves both **north/south** (ingress) and **east/west** (mesh) traffic with the same configuration model.

## Design goals

- **Role-oriented**: API resources model the organizational roles that use/configure service networking.
- **Portable**: spec supported by many implementations (stay universal like Ingress).
- **Expressive**: header-based matching, traffic weighting, and more — things only possible in Ingress via custom annotations.
- **Extensible**: custom resources linkable at various API layers for granular customization.

## Personas (three roles)

| Persona | Role | Concerns |
| --- | --- | --- |
| **Ian** (he/him) | Infrastructure Provider | Cares for infra serving multiple isolated clusters/tenants; often a cloud/PaaS provider. Writes GatewayClass. |
| **Chihiro** (they/them) | Cluster Operator | Manages a single cluster: policies, network access, app permissions. Writes Gateways. |
| **Ana** (she/her) | Application Developer | Owns an app's business needs; wants config (timeouts, matching/filters) and service composition (path routing). Writes Routes. |

Notes:

- One human may occupy multiple roles (small startup = self-service; large org = distinct people).
- Each persona maps roughly to a Kubernetes RBAC `Role` (see `06-security-namespaces.md`).

## Resource model (three core object types)

- **GatewayClass** — defines a set of Gateways with common config/behavior; handled by a single controller. Cluster-scoped. Analogy: `IngressClass` / `StorageClass`.
- **Gateway** — requests a point where traffic is translated to in-cluster Services. Binds one or more **Addresses** to one or more **Listeners**.
- **Routes** — protocol-specific rules mapping Gateway traffic to Services.

Combined `GatewayClass` + `Gateway` + `xRoute` + `Service`(s) = an implementable load balancer.

## Request flow (north/south, reverse-proxy example)

1. Client requests `http://foo.example.com`.
2. DNS resolves to a `Gateway` address.
3. Reverse proxy receives on a `Listener`, matches an `HTTPRoute` via the Host header.
4. Optionally matches request headers/path per `match` rules.
5. Optionally modifies the request (headers) per `filter` rules.
6. Forwards to one or more `Service` backends per `backendRefs`.

## Channels quick map (full detail in `08-versioning-conformance.md`)

- Standard Channel (GA/Beta) — stable, recommended default.
- Experimental Channel — alpha resources/fields; no backwards-compat guarantees.
