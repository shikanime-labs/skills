# Upstream Resources & API (Envoy AI Gateway)

Source: aigateway.envoyproxy.io/docs — concepts/resources, api/,
getting-started/connect-providers. Field names verbatim from the API reference.

## The three core CRDs (and how they relate)

```
AIGatewayRoute ──routes to──▶ AIServiceBackend ──references──▶ Backend (EG) / K8s Service
                                    │
                                    └──references──▶ BackendSecurityPolicy ──▶ Secret (apiKey/AWS)
```

- **AIGatewayRoute** — unified AI API + routing rules for a Gateway. Defines the
  client-facing input API schema, routing rules, request/response transforms, and
  optional LLM cost tracking.
- **AIServiceBackend** — one AI backend with a specific API schema. References an
  EG `Backend` (or K8s Service) and optionally a `BackendSecurityPolicy`.
- **BackendSecurityPolicy** — authn/z for backend access (API Key, AWS creds).

## AIGatewayRoute (spec shape)
- `parentRefs` — the `Gateway` (group `gateway.networking.k8s.io`) it attaches to.
- `schema` (APISchema) — input schema the client uses (e.g. OpenAI v1). Drives
  request→backend transform.
- `rules[]`:
  - `matches[]` — subset of HTTPRouteMatch; typically `headers` on `x-ai-eg-model`
    (Exact / RegularExpression for catch-all `.*`).
  - `backendRefs[]` — `AIGatewayRouteRuleBackendRef` (see below).
  - `modelsOwnedBy` / `modelsCreatedAt` — exported in `/models` when the rule
    matches `x-ai-eg-model`.
  - `timeouts` — per-request HTTP timeouts (default 60s, vs EG's 15s default).
  - `llmRequestCosts[]` — token cost tracking config (see upstream-traffic.md).
- `filterConfig` — config for the ext-proc filter (required in v1alpha1 shapes).

### AIGatewayRouteRuleBackendRef (priority + transforms)
- `name` — backend resource (AIServiceBackend by default).
- `namespace` — cross-namespace refs supported (needs ReferenceGrant). Local
  namespace if empty.
- `group` / `kind` — default `aigateway.envoyproxy.io` / `AIServiceBackend`;
  `InferencePool` from Gateway API Inference Extension is the other supported kind.
- `modelNameOverride` — sets the model name sent upstream; **ignored** for
  InferencePool refs. (Fleet note: v1.1.0 does NOT expand `${header.x-ai-eg-model}`
  / `${request.body.model}` — it sends them verbatim; omit to forward the body model.)
- `headerMutation` / `bodyMutation` — request transforms per backend; route-level
  takes precedence over backend-level on conflict.
- `weight` — traffic distribution (default 1).
- `priority` — endpoint priority (default 0). Drives failover order; **overrides**
  the underlying EG Backend's `failover`. Ignored for InferencePool.

### Multiple AIGatewayRoutes on one Gateway
ai-gateway MERGES all `AIGatewayRoute`s sharing a `parentRefs` Gateway. Use a
dedicated route for an isolated, auditable failover path. **Never match the same
`x-ai-eg-model` value from two routes** — the merge is ambiguous.

## AIServiceBackend (spec shape)
- `schema` (VersionedAPISchema) — `name` (OpenAI / AzureOpenAI / AWSBedrock /
  Anthropic / ...) + `version`.
- `backendRef` — the EG `Backend` (or K8s Service) it maps to. CEL-blocked from
  arbitrary Service refs; must be an EG `Backend`.
- `backendSecurityPolicyRef` — name of the attached `BackendSecurityPolicy`.

## BackendSecurityPolicy
- `targetRefs` — points at the **AIServiceBackend name** (not the Secret name).
- `type` — `APIKey` or `AWSCredentials`.
- `apiKey.secretRef` — Secret containing the key; data key must be `apiKey`.

## v1beta1 note
`AIGatewayRoute` v1beta1 has **no `failover` field** — a 4xx (e.g. 403) is
terminal; only 5xx/transport errors trigger priority-based failover.

## When to load this file
- Authoring/validating AIGatewayRoute / AIServiceBackend / BackendSecurityPolicy.
- Questions on priority, modelNameOverride, header/body mutation, merging routes.
