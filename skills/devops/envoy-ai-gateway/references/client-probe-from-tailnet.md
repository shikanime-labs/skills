# Probing the inference gateway from a client host (tailnet → remote node)

Verified 2026-09-07 from telsha against a model running on sashina via
`https://inference.i.shikanime.studio`. Use when asked to confirm a model is
live/serving/reachable from a workstation, or when a client call returns a
silent empty error. Complements the loopback `llama-cpp:8080` check in
`book-llama-cpp-inference`.

## Endpoint & pre-checks

- `inference.i.shikanime.studio` → Tailscale IP (`100.110.197.5`), TCP 443.
- Sequence: `dig +short` (expect a `100.x` address) → `nc -zvw5 ... 443` →
  `curl -sS -o /dev/null -w '%{http_code}\n' https://inference.i.shikanime.studio/`
  → expect `401` (gateway auth enforced = correct). `000` = TLS/mTLS gate or
  unreachable; see `mtls-vs-dns-diagnosis.md`.

## Auth

Client credential is `SKS_API_KEY` (exported in the devenv shell).
- OpenAI-style routes: `Authorization: Bearer $SKS_API_KEY`
- Anthropic-style routes: `x-api-key: $SKS_API_KEY` AND `anthropic-version: 2023-06-01`

## List models (auth required)

- OpenAI: `curl -sS https://inference.i.shikanime.studio/v1/models -H "Authorization: Bearer $SKS_API_KEY"`
- Anthropic: `curl -sS https://inference.i.shikanime.studio/anthropic/v1/models -H "x-api-key: $SKS_API_KEY" -H "anthropic-version: 2023-06-01"`

Both return the same catalog, `owned_by: Shikanime Studio`.

## CRITICAL: model IDs are namespaced — a bare id fails SILENTLY

Every route key is `<vendor>/<model>`: `z-ai/glm-5.3-flash`, `qwen/qwen3.8-27b`,
`qwen/qwen3.8-flash`, `deepseek/deepseek-v4-flash`, `qwen/qwen3-embedding-8b`,
`mistral/labs-leanstral-1-5`, `z-ai/glm-5.3`, `poolside/laguna-s-2.1`.

Requesting a **bare** name (`glm-5.3-flash`) returns an EMPTY error object —
no diagnostic message:
`{"error":{"message":"","type":""},"request_id":"","type":"error"}`.

RULE: never hand-type or truncate the model id. Copy it verbatim from the
`/v1/models` or `/anthropic/v1/models` list; the vendor prefix is part of the key.

## Working completion path

Anthropic route WORKS:
```
curl -sS -m 40 https://inference.i.shikanime.studio/anthropic/v1/messages \
  -H "x-api-key: $SKS_API_KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"z-ai/glm-5.3-flash","max_tokens":64,"messages":[{"role":"user","content":"Reply with exactly: pong"}]}'
```
→ `{"type":"message","role":"assistant","content":[...],"stop_reason":"end_turn"}`.

OpenAI `/v1/chat/completions` returns an EMPTY body here — the gateway build
does not translate OpenAI→Anthropic, so `/v1` 500s/empties. Do NOT read an
empty OpenAI completion as "server down"; use the `/anthropic` prefix. (Same
rule as the GLM note in the SKILL.md body; applies to all models, not just GLM.)

## Smoke proof

A `pong` round-trip on `z-ai/glm-5.3-flash` via the Anthropic route is
sufficient end-to-end proof that a model runs on the node and is reachable
through the gateway from the client host.
