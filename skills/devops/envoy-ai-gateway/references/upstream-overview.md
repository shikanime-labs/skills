# Upstream Overview (Envoy AI Gateway, docs v1.1)

Source: aigateway.envoyproxy.io/docs — home, concepts/architecture/*.
Distilled for the agent; not a copy of the upstream docs.

## What it is

Envoy AI Gateway is an open-source, Kubernetes-native **GenAI traffic
management** layer built ON TOP of Envoy Gateway. It exposes a unified,
OpenAI-compatible AI API to clients and routes to multiple LLM providers
(OpenAI, Anthropic, AWS Bedrock, Azure OpenAI, GCP Vertex AI, Mistral, Gemini,
self-hosted) and self-hosted models with failover, token-based rate limiting,
and usage/cost policy control.

### Key objectives (from upstream)
- Unified routing/management layer for LLM/AI traffic.
- Automatic failover across providers / self-hosted models.
- End-to-end security: upstream authz for LLM traffic, client authn.
- Policy framework for usage limiting (rate limiting, quotas).
- Extensible on Envoy's extensibility (ext-proc, dynamic modules).

## Architecture: two planes

### Control plane
- **Kubernetes API Server** — config interface (CRDs).
- **AI Gateway Controller** — manages AI-specific resources + configures the
  ext-proc and fine-tunes xDS via the Envoy Gateway extension-server mechanism.
- **Envoy Gateway Controller** — core proxy config + xDS, and the Rate Limit
  Service.

### Data plane
- **Envoy Proxy** — routes all incoming traffic; integrates ext-proc + RL service.
- **AI Gateway External Processor (ExtProc)** — the AI-specific brain. Three jobs:
  1. Request processing: model selection/validation, route to provider,
     provider auth, multi-format support (OpenAI, AWS Bedrock...).
  2. Token management: tracks usage (streaming + non-streaming), feeds RL.
  3. Provider integration: request/response transformation + normalization.
- **Rate Limit Service** — token-based rate limiting budget enforcement.

## Request/response flow (why two ext-proc phases)

The ext-proc runs in **two phases** per the upstream's explicit rationale:
- **Router-level** ext-proc: before routing — extracts model name, sets route.
- **Upstream-level** ext-proc: runs on retry/fallback (after the router filter).
  Because Envoy retry/fallback happens at the upstream level for 5xx, and a
  fallback may go to a *different* provider (OpenAI → Bedrock), the request
  transform + upstream authn must be re-done there. This is the core reason
  ai-gateway uses ext-proc rather than a single router filter.

Version note: built on Envoy Gateway; docs target v1.1 (ai-gateway-helm
v1.1.0 / gateway-helm v1.8.1+).

## When to load this file
- Grounding "what is Envoy AI Gateway / how is it architected" questions.
- Explaining why failover/transform logic lives in the ext-proc, not the route.
