# Upstream Traffic: Rate Limiting & Quotas (Envoy AI Gateway)

Source: aigateway.envoyproxy.io/docs — capabilities/traffic/
{usage-based-ratelimiting,quota-policy}. Verbatim config from upstream.

## Two controls, distinct purpose
- **Usage-based Rate Limiting** — controls **request velocity** (tokens per
  window). Uses EG's Global Rate Limit API + Redis.
- **QuotaPolicy** — caps **total consumption budgets** (tokens per window). Also
  Redis-backed. Use when you need cumulative spend caps, not velocity.

Prereqs for both: a Redis instance + Envoy Gateway installed with rate limiting
enabled (addon values) pointing at that Redis.

## Usage-based rate limiting

### 1. Track tokens (per-route `llmRequestCosts`)
```yaml
spec:
  llmRequestCosts:
    - metadataKey: llm_input_token
      type: InputToken
    - metadataKey: llm_cached_input_token
      type: CachedInputToken
    - metadataKey: llm_output_token
      type: OutputToken
    - metadataKey: llm_total_token
      type: TotalToken
    # Advanced:
    # - metadataKey: custom_cost
    #   type: CEL
    #   cel: "(input_tokens - cached_input_tokens) + (cached_input_tokens * 0.1) + output_tokens * 1.5"
```
Token types: `InputToken`, `CachedInputToken`, `OutputToken`, `TotalToken`,
`CEL`. Counts stored in per-request dynamic metadata under namespace
`io.envoy.ai_gateway`. Scoped per-route (same metadata keys on different routes
are calculated independently).

### 2. Enforce via EG `BackendTrafficPolicy` (Global rate limit)
```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: BackendTrafficPolicy
metadata: { name: model-specific-token-limit-policy, namespace: default }
spec:
  targetRefs:
    - name: envoy-ai-gateway-token-ratelimit
      kind: Gateway
      group: gateway.networking.k8s.io
  rateLimit:
    type: Global
    global:
      rules:
        - clientSelectors:
            - headers:
                - { name: x-tenant-id, type: Distinct }
                - { name: x-ai-eg-model, type: Exact, value: gpt-4 }
          limit: { requests: 1000, unit: Hour }
          cost:
            request: { from: Number, number: 0 }   # only token usage counts
            response:
              from: Metadata
              metadata: { namespace: io.envoy.ai_gateway, key: llm_total_token }
```
**Rules (verbatim warnings from upstream):**
- Set request cost `number: 0` so ONLY token usage counts.
- Use both user (`x-tenant-id`) and model (`x-ai-eg-model`) identifiers.
- `x-ai-eg-model` is inserted by the AI Gateway filter with the model extracted
  from the request body.

### Timing / streaming behavior
- Token usage is charged **after** the response completes. On arrival, if already
  charged usage exceeds the limit → reject with **429**; else admit and charge.
- **Streaming**: usage only known at stream end. An admitted stream is NOT
  interrupted if it overshoots; it completes, charges at end, and later matching
  requests are 429'd until the window recovers. Example: 1000-token/hr limit, an
  empty-bucket request streams 1200 tokens successfully, then subsequent requests
  denied until capacity returns.

### Per-tenant limits without per-tenant policies
Read the limit value from **dynamic metadata** (`limit.fromMetadata`) so one
shared `BackendTrafficPolicy` serves every tenant; the tenant's number arrives
with the request. A `requests_per_unit` of `0` **suspends** that tenant (real
limit, not a fallback) — omit the field entirely for "no opinion".

## QuotaPolicy (token budgets)
```yaml
apiVersion: aigateway.envoyproxy.io/v1alpha1
kind: QuotaPolicy
metadata: { name: full-quota-policy }
spec:
  targetRefs:
    - group: aigateway.envoyproxy.io
      kind: AIServiceBackend
      name: my-backend
  perModelQuotas:
    - modelName: gpt-4
      quota:
        costExpression: "input_tokens + cached_input_tokens / 10u + output_tokens * 6u"
        mode: Shared
        defaultBucket: { limit: 10000, duration: "1h" }
        bucketRules:
          - clientSelectors:
              - { headers: [ { name: x-tenant-id, type: Exact, value: premium-tenant } ] }
            quota: { limit: 50000, duration: "1h" }
          - clientSelectors:
              - { headers: [ { name: x-tenant-id, type: Distinct } ] }
            quota: { limit: 5000, duration: "1h" }
            shadowMode: true   # evaluate, do not enforce
```
- `costExpression` variables: `input_tokens`, `cached_input_tokens`,
  `cache_creation_input_tokens`, `output_tokens`, `reasoning_tokens`,
  `total_tokens`, `model`, `backend`, `route_name` (all `uint` except strings).
- `mode`: only `Shared` today. Buckets: `defaultBucket` + `bucketRules`.
- `shadowMode: true` — evaluate without rejecting (safe rollout).

## When to load this file
- Adding token-based rate limiting or cost quotas to an AI Gateway.
- Debugging 429s, streaming over-limit, or per-tenant quota wiring.
