# Provider-specific quirks (verified live on nishir)

## nous (inference-api.nousresearch.com)

- Base: `https://inference-api.nousresearch.com/v1/chat/completions`
- `/v1/models` returns 342 models (same catalog as openrouter) — pass-through ids
- Key types: portal OAuth (JWT) for chat; the `apiKey=` in `.enc.env` is a
  portal-issued key. A placeholder key 401s "invalid, blocked or out of
  funds" — that is a credentials issue, NOT a manifests defect.
- `api.nousresearch.com` is NXDOMAIN — never route to it.

## openrouter (openrouter.ai)

- Base: `https://openrouter.ai/api/v1/chat/completions` (NOT `/v1` — that hits
  the web root → HTML 404)
- Serves the same catalog as nous; deepseek v4 flash id is
  `deepseek/deepseek-v4-flash-latest` (NOT `deepseek/deepseek-chat`)
- Cloudflare — needs explicit `tls.sni: openrouter.ai`

## z.ai (api.z.ai)

- Base: `https://api.z.ai/api/coding/paas/v4/chat/completions` (CODING-PLAN
  key). Plain `/api/v1` and `/api/paas/v4` both reject a coding key with 401
  "token expired or incorrect".
- z.ai returns HTTP 200 with a JSON error body
  `{"code":401,"msg":"token expired or incorrect"}` instead of a real 401 —
  check the body, not just the status.
- A valid coding key that hit its quota returns
  `rate_limit_exceeded: Usage limit reached for 5 hour. Your limit will reset
  at <timestamp>`.
- Cloudflare — needs explicit `tls.sni: api.z.ai`
- API key method: `AIServiceBackend` (not `BackendSecurityPolicy`). The
  `zai-key` AIServiceBackend uses secret `inference-zai` with data key
  `apiKey`. This pattern is used because per-provider API key isolation
  requires one `AIServiceBackend` per provider; the `BackendSecurityPolicy`
  approach does not allow per-provider key targeting.

## openrouter (openrouter.ai)

- Base: `https://api.z.ai/api/coding/paas/v4/chat/completions` (CODING-PLAN
  key). Plain `/api/v1` and `/api/paas/v4` both reject a coding key with 401
  "token expired or incorrect".
- z.ai returns HTTP 200 with a JSON error body
  `{"code":401,"msg":"token expired or incorrect"}` instead of a real 401 —
  check the body, not just the status.
- A valid coding key that hit its quota returns
  `rate_limit_exceeded: Usage limit reached for 5 hour. Your limit will reset
  at <timestamp>`.
- Cloudflare — needs explicit `tls.sni: api.z.ai`

## Local llama-cpp floors

- Serve their GGUF ids (e.g. `unsloth/Qwen3.8-27B-GGUF:Q8_0`,
  `unsloth/DeepSeek-V4-Flash-0731-GGUF:Q4_K_M`) — get these from the sts args
  (`-hf unsloth/...`).
- Plain HTTP on port 8080 (no TLS).
- No API key, never 429s — fleet convention places them at `priority: 0`
  (drain unlimited local capacity first).
