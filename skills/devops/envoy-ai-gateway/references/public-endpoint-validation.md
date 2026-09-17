# Public endpoint validation (verified live)

Verified by real curl probes from the hermes-agent pod on nishir (2026-09-06).

## Canonical public endpoint

`https://inference.shikanime.studio` — the Envoy AI Gateway public endpoint with
a Let's Encrypt cert (post-#1946). This is the endpoint Hermes consumers
(hermes-agent, honcho, Open WebUI) route through.

### OpenAI-compatible path

```
POST https://inference.shikanime.studio/v1/chat/completions
Authorization: Bearer <SKS_API_KEY>
Content-Type: application/json

{"model":"poolside/laguna-s-2.1:free","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}
```

Verified response (HTTP 200):

```json
{"id":"gen-1788678151-VCXzHpqdETyLgTaTgk6j","object":"chat.completion",
 "created":1788678151,"model":"poolside/laguna-s-2.1:free","provider":"Poolside",
 "choices":[{"index":0,"finish_reason":"length","message":{"role":"assistant",
   "content":"Hello! How can I help you today?"}}]}
```

### Z.ai / GLM via Anthropic-format path

Z.ai's GLM is **NOT** OpenAI chat/completions-compatible (returns 403 on `/v1/chat/completions`).
Through the gateway, use the `/anthropic` prefix:

```
POST https://inference.shikanime.studio/anthropic/v1/messages
Authorization: Bearer <SKS_API_KEY>
anthropic-version: 2023-06-01
Content-Type: application/json

{"model":"z-ai/glm-5.3-flash","max_tokens":10,"messages":[{"role":"user","content":"Hello"}]}
```

Verified response (HTTP 200):

```json
{"id":"gen-1788678173-m42U5FvwItL0asg8ACGh","type":"message","role":"assistant",
 "content":[{"type":"text","text":"Hello! How can I help you today?"}],
 "model":"poolside/laguna-s-2.1:free","stop_reason":"max_tokens",
 "usage":{"input_tokens":44,"output_tokens":10}}
```

**Client-side rule:** use `/anthropic/v1/messages` (NOT `/v1/messages` — that 404s
with "unsupported path") for GLM/Z.ai models. The `/v1/chat/completions` path on
the `z-ai` backend still 500s with "unsupported API schema: Anthropic" in
ai-gateway v1.1.0. See SKILL.md "Z.ai GLM protocol" section for the full matrix.

## Credential format

Hermes consumers inject `SKS_API_KEY` as a `Bearer` token. The key format is
`sk-inference-<id>:<secret>` (or `sk-lm-<id>:<secret>` for the aperture egress
layer). It is stored in the hermes-agent `.enc.env` and mounted into consumer
deployments as an env var — NOT hardcoded in config.yaml.

## Key rotation note

The `inference-tailnet` TLS cert was rotated 2026-09-05 (nishir CA).
`cert-manager` does NOT auto-reissue when the issuer CA rotates — you must delete
the Certificate secrets that reference the old CA and let cert-manager reissue.
This is pre-existing operational knowledge, not session-specific.

## Dead model: tencent/hy3:free

`POST https://inference.shikanime.studio/v1/chat/completions` with
`{"model":"tencent/hy3:free"}` via the catch-all route returns:

```json
{"status": 404, "message": "This model is unavailable for free"}
```

`tencent/hy3` (paid) works fine through the catch-all. If you need a free
model through the gateway, use `qwen/qwen3.8-flash` (runs on the local floor)
or another free OpenRouter slug. See provider-quirks.md.