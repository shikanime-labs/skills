# Cloud and Deployment Hunting

Use when the repository defines cloud identity, infrastructure,
containers, Kubernetes, service mesh, serverless functions, edge workers,
ingress, object storage, managed services, or environment-specific
configuration: whether deployed components receive the intended identity,
isolation, network reachability, secrets, and policy. Source often
expresses intent rather than live fact — separate source-confirmed
defects from deployment validation needs.

## Core Discipline

- Do not infer a live exposure from a manifest alone. Establish which
  environment consumes it, what defaults or overlays modify it, and
  whether the source path is active.
- Map each workload identity to specific operations and resources. Broad
  policy is a finding only when lower-trust input can reach an
  unauthorized action.
- Ingress, proxies, service mesh, metadata services, and admission policy
  are real boundaries, but count a control only when its configuration
  and attachment are visible.
- Secret references are not secret disclosure. Require a lower-trust
  reader, output, artifact, log path, or unsafe fallback.
- `confirmed` for active in-repo configurations plus local rendering or
  policy validation. Account policy, network attachment, runtime
  admission, hosted metadata, and drift needing owner observation are
  `needs_validation`.

## Identity and IAM Classes

- **Workload identity overreach**: a workload, pod, function, or node
  identity acting on tenants, accounts, resources, or APIs beyond its
  role, with untrusted request or job input selecting the target. Review
  policy conditions, resource patterns, service-account attachment,
  namespace mapping, fallback credentials.
- **Cross-account role confusion**: role assumption, external IDs, token
  exchange, workload federation, or resource policies accepting identity
  claims not bound to the intended source account, audience, repository,
  namespace, or workload. Establish both trust policy and the
  caller-controlled claim.
- **Authorization delegated to cloud metadata**: an application trusting
  caller-supplied identity headers, tags, labels, account IDs, or
  resource metadata without verifying origin from the control plane or a
  trusted proxy. Cloud IAM and application authorization are separate
  checks.

## Network and Control-Plane Classes

- **Unexpected reachability**: an ingress, service, listener, security
  group, load-balancer annotation, port mapping, or bind exposing an
  admin, debug, metrics, node, control-plane, or internal API to a
  lower-trust network. Missing network controls alone are
  `needs_validation`; a repository-controlled public route to a
  sensitive handler can be `confirmed`.
- **Trusted-proxy and mesh bypass**: a backend accepting forwarded
  identity, mTLS subject, or authorization metadata from peers outside
  the intended ingress or sidecar; alternate ports and health or legacy
  paths bypassing the mesh. Verify header stripping, peer reachability,
  and fail-open behavior when the proxy is absent.
- **Metadata and internal-service reachability**: an untrusted URL,
  destination, or protocol selection reaching instance or container
  metadata, control-plane sockets, or internal APIs with workload
  credentials.

## Container and Orchestration Classes

- **Host or control-plane exposure**: a lower-trust workload selecting
  privileged mode, capabilities, host namespaces, host paths, device
  mounts, runtime sockets, or service-account tokens crossing into node
  or control-plane authority. Absent seccomp or read-only filesystem
  alone is hardening unless a reachable operation crosses the boundary.
- **Admission and policy inconsistency**: one deployment route enforcing
  image identity, namespace, resource, secret, or privilege policy while
  another controller, job, upgrade, restore, or compatibility path does
  not. Confirm the alternate route and the resulting deployed object.
- **Namespace and label trust**: network, admission, secret, or identity
  policy relying on labels, annotations, names, or namespaces a
  less-trusted principal can set. Compare who controls selectors with
  what authority matching grants.

## Configuration and Secret Classes

- **Control precedence drift**: development values, chart defaults,
  environment variables, flags, feature gates, or per-region overlays
  disabling authentication, transport security, tenant scoping, or audit
  policy in a deployed environment. Render the final configuration per
  environment, not just the base file.
- **Secret exposure across boundaries**: secrets entering logs, crash
  reports, process arguments, shared environments, broad volumes, build
  outputs, service discovery, or read APIs accessible to another workload
  or tenant. Check secret type and authority; a public endpoint or key ID
  is not a credential.
- **Credential renewal and outage fallback**: failure to mount, refresh,
  rotate, or revoke a workload credential leaving stale credentials
  active, or an app accepting a less trusted identity mode. Review
  startup, readiness, reconnect, cached-client behavior.

## Managed Service and Edge Classes

- **Object and signed-URL policy confusion**: bucket policy, object keys,
  CDN origins, or signed URLs failing to bind principal, operation,
  object namespace, audience, or expiry. Review list, version, and write
  paths as well as reads.
- **Event-source identity confusion**: a function or worker trusting
  event body fields as source identity without validating the
  provider-signed envelope, subscription, topic, account, region, or
  replay state. Compare push, pull, retry, dead-letter paths.
- **Edge and runtime boundary mismatch**: an edge or serverless runtime
  assuming secrets, APIs, filesystem, isolation, or tenant policy that
  differs from the origin runtime, with origin fallback changing
  authority or cache behavior.

## Moves and Validation

Render every maintained environment and build a matrix of external port,
workload identity, network peers, mounted secrets, and cloud resources;
differences require an owner or policy explanation. Follow a lower-trust
request, object, label, or event into cloud policy, showing which
workload credential performs the final operation and what condition
should scope it. Diff normal deploy, migration, restore, node maintenance,
failover, and emulator paths; review behavior when mesh, admission,
identity, secret, or policy services are unavailable.

Before reporting: establish the active source path and the effective
deployment object, else `needs_validation` naming the missing rendered
manifest or owner-observed attachment; name the lower-trust caller or
workload, cloud or application identity, controllable selector, affected
resource, and the unauthorized operation or disclosure; verify provider
and orchestrator defaults at the pinned version — never assume a public
IP, reachable metadata service, permissive firewall, or absent admission
attachment. Local validation may render templates, evaluate policy,
inspect namespaces in an isolated fixture, or run an emulator with dummy
identities; never probe live endpoints or alter shared cloud resources.
