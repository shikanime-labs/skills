# Upstream Security (Envoy AI Gateway)

Source: aigateway.envoyproxy.io/docs — capabilities/security/upstream-auth.
Two distinct auth layers; do not conflate them.

## Two security layers

1. **Client → Gateway authentication** — enforced by Envoy Gateway
   `SecurityPolicy` (apiKey / OIDC / JWT / mTLS). See the `envoy-gateway` skill's
   Security chapter and EG's tasks/security docs. This is where inbound auth
   (e.g. the fleet's `x-api-key` + client-cert mTLS) lives.
2. **Gateway → Upstream authentication** — enforced by AI Gateway
   `BackendSecurityPolicy` (credential injection into the upstream request).
   This is "Upstream Authentication".

## Upstream Authentication (gateway → provider)

### Automated credential management (short-lived tokens)
The control plane integrates with each provider's identity system per request:
- **AWS Bedrock** — OIDC → AWS STS temporary credentials.
- **Azure OpenAI** — Entra ID (ex-Azure AD) short-lived tokens.
- **GCP Vertex AI** — GCP workload federation → Google STS temporary creds.

ai-gateway auto-manages these; each request carries a short-lived proof.

### Manual credential management (long-lived API keys)
For providers with long-lived credentials (OpenAI, etc.): store the key in a
Kubernetes Secret, reference it from a `BackendSecurityPolicy`:
```yaml
apiVersion: aigateway.envoyproxy.io/v1alpha1
kind: BackendSecurityPolicy
metadata: { name: openai-auth }
spec:
  targetRefs:
    - group: aigateway.envoyproxy.io
      kind: AIServiceBackend
      name: openai-backend
  type: APIKey
  apiKey:
    secretRef: { name: openai-secret, namespace: default }
```
ai-gateway retrieves the key from the Secret and attaches it to each upstream
request. Secret data key must be `apiKey` (no key selector).

## Why it matters (upstream's framing)
- Security: one auth mechanism between gateway and providers; stops credential
  sprawl across teams.
- Credential management: central store/rotate/revoke.
- Compliance: controlled usage of AI resources.

## When to load this file
- Wiring upstream provider auth (API key vs AWS/Entra/GCP federation).
- Distinguishing client-auth (EG SecurityPolicy) from upstream-auth (BSP).
