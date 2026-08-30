# Glossary

Key definitions from the Gateway API glossary and concepts pages.

- **North/South traffic** — traffic from outside a cluster to inside (and vice versa). Ingress use case.
- **East/West traffic** — workload-to-workload traffic within a cluster. Service mesh use case.
- **Gateway Controller** — software managing infrastructure for routing via Gateway API (cf. ingress controller). Often runs in-cluster.
- **Service mesh** — software managing security/reliability/observability for east/west communications, usually by intercepting at a low level (proxies next to Pods).
- **Service frontend** — the Service's name + cluster IP (DNS record allocation). East/west often targets the frontend.
- **Service backend** — the Service's set of endpoints (Pod IPs). Some east/west targets specific endpoints directly.
- **Service routing** — send to a Service frontend; underlying network (kube-proxy or mesh) chooses the endpoint.
- **Endpoint routing** — send directly to a specific Service endpoint, bypassing network routing decisions (e.g. sticky sessions).
- **Workload** — an instance of computation in a cluster: the Pods + the owner (Deployment/Job/ReplicaSet).
- **Producer Route** — a Route in the same Namespace as its Service, defining acceptable use; affects all clients (see `07-mesh-gamma.md`).
- **Consumer Route** — a Route in a different Namespace than its Service, refining one consumer's use; affects only that namespace's clients.
- **Listener** — a Gateway's port/protocol/hostname binding that receives traffic.
- **Distinct Listeners** — Listeners that don't conflict (see `02-gateway-listeners.md` for per-protocol keys).
- **Conflicted Listeners** — non-distinct Listeners on one Gateway; invalidates the Gateway.
- **Relevant Listener** — the set of Listeners a Route may attach to, given its `parentRef`/`sectionName` and listener `allowedRoutes`.
- **GatewayClass** — cluster-scoped template defining a family of Gateways (controller-bound).
- **ReferenceGrant** — cross-namespace trust object permitting inbound object references (see `06-security-namespaces.md`).
- **ListenerSet** — (Extended) a child resource contributing listeners to a parent Gateway, for multitenancy/scale (see `09-listenerset-deploy.md`).
- **BackendTLSPolicy** — configures upstream (Gateway→backend) TLS (see `05-tls.md`).
- **AddressType** — how a network address is represented: `IPAddress`, `Hostname` (Extended), or domain-prefixed implementation-specific strings (`NamedAddress` deprecated).
- **Support levels** — Core / Extended / Implementation-specific (see `08-versioning-conformance.md`).
- **Release channels** — Standard (stable) / Experimental (alpha, no compat guarantees).
