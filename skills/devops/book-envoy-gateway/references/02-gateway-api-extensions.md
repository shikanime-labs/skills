# Gateway API Extensions & Policy Model

Source: Concepts/gateway_api_extensions, SecurityPolicy, BackendTrafficPolicy,
ClientTrafficPolicy pages.

## Policy attachment model

- EG extensions are **type-safe CRDs** (unlike Ingress annotations).
- Policies attach to standard Gateway API resources **without modifying the
  core API** — separation of concerns across teams.

## Targeting

Two mechanisms (all policies):

1. **Direct reference (`targetRefs`)** — by name + kind.
2. **Label selection (`targetSelectors`)** — match by Kubernetes labels.

- A policy can **only target resources in the same namespace** as the policy.
- `ListenerSet` target + `sectionName` => applies to a single listener in that
  ListenerSet only.

## Precedence hierarchy

Route-specific first, then parent scope:

1. Route **rule-level** (HTTPRoute/GRPCRoute/TCPRoute with `sectionName` on a rule)
2. Route-level (no `sectionName`)
3. Then by attachment path:
   - Via ListenerSet: ListenerSet listener-level → ListenerSet-level → Gateway-level
   - Via Gateway: Gateway listener-level → Gateway-level

- Gateway listener-level and ListenerSet listeners are **sibling scopes**; a
  Gateway listener policy does NOT apply to ListenerSet-attached routes.

### Same-level tie-break

1. **Creation time** (earliest `creationTimestamp` wins)
2. **Name sort** (alphabetical namespaced name if timestamps tie)

## Policy merging (`mergeType`)

- Unset => no merge; only the most specific policy takes effect.
- `mergeType` can ONLY be set on child-targeting policies (e.g. HTTPRoute),
  never on parent (Gateway/ListenerSet) policies.
- Merge types:
  - **StrategicMerge** — Kubernetes strategic merge patch semantics (arrays merged intelligently)
  - **JSONMerge** — RFC 7396 JSON Merge Patch (arrays replaced entirely)
- Merging combines parent + child; child config wins for a duplicated feature.
- Secret/backend refs resolve against the **namespace of the policy that set the
  field** (route or parent), even after merge.

## Extension CRDs (full list)

`Backend`, `BackendTrafficPolicy`, `ClientTrafficPolicy`, `EnvoyExtensionPolicy`,
`EnvoyGateway`, `EnvoyPatchPolicy`, `EnvoyProxy`, `HTTPRouteFilter`,
`SecurityPolicy`. All translate to xDS via the control plane.

## TCPRoute limitation

SecurityPolicy on TCPRoute is limited to **IP allow/deny (authorization)** only.
JWT, API key, basic auth, OIDC do not apply to TCPRoute.
