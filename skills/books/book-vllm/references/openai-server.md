# OpenAI-Compatible Server (vLLM)

Source: <https://docs.vllm.ai/en/latest/serving/online_serving/>

## Start

```bash
vllm serve <model> --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 2 --enable-prefix-caching
# One-shot ephemeral env:
uv run --with vllm vllm serve <model>
```

## Endpoints

OpenAI-compatible:

- `/v1/completions` — text gen models only; `suffix` param NOT supported.
- `/v1/chat/completions` — needs chat template; `user` param ignored.
  `parallel_tool_calls=false` → at most one tool call.
- `/v1/chat/completions/batch` — batch chat.
- `/v1/responses`, `/v1/responses/{id}`, `/v1/responses/{id}/cancel` — Responses
  API (text gen only).
- `/v1/embeddings` — embedding/pooling models.

Other interfaces:

- Anthropic: `/v1/messages`, `/v1/messages/count_tokens`
- Cohere: `/v2/embed`, `/rerank`, `/v1/rerank`, `/v2/rerank`
- Pooling: `/classify`, `/pooling`, `/score`, `/v1/score`
- Speech: `/v1/audio/transcriptions`, `/v1/audio/translations`, `/v1/realtime`
- Generative scoring: `/generative_scoring`

Instrumentation:

- `/health` — liveness. `/version` — version. `/load` — server load.
  `/v1/models` — list models.
- `/metrics` — Prometheus (`vllm:` prefix). See references/metrics.md.

## Client (OpenAI SDK)

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
# chat
client.chat.completions.create(model="<served-model-name>",
    messages=[{"role":"user","content":"Hi"}])
# streaming
stream = client.chat.completions.create(model=..., stream=True, messages=...)
# embeddings
client.embeddings.create(model=..., input="text")
```

## Structured Outputs (xgrammar / guidance backend)

Backend default `auto`; set `--structured-outputs-config.backend`
(`auto|guidance|xgrammar|...`). Deprecated `guided_*` fields removed in v0.12.0
— use `structured_outputs`:

```python
# choice
extra_body={"structured_outputs": {"choice": ["positive","negative"]}}
# regex
extra_body={"structured_outputs": {"regex": r"\w+@\w+\.com\n"}}
# json (Pydantic -> schema, or raw JSON Schema)
response_format={"type":"json_schema","json_schema":{"name":"x","schema":CarDescription.model_json_schema()}}
# grammar (EBNF)
extra_body={"structured_outputs": {"grammar": simplified_sql_grammar}}
# structural_tag
extra_body={"structured_outputs": {"structural_tag": ...}}
```

Params: `choice`, `regex`, `json`, `grammar`, `structural_tag`,
`whitespace_pattern`. Regex dialect depends on backend
(xgrammar/guidance/outlines use Rust-style; lm-format-enforcer uses Python
`re`).

## Tool Calling & Reasoning

- Tool calls: returned per chat request; `parallel_tool_calls` controls count
  (model-dependent).
- Reasoning parsers: `--reasoning-parser` (per-model) + `--reasoning-config` for
  reasoning-model output formatting into OpenAI format.

## Online serving flags (subset; full set in references/engine-args.md)

- `--served-model-name` — API/model name (≠ `--model` path).
- `--chat-template`, `--chat-template-content-format` (use `string` for
  interleaved MM).
- `--enable-lora`, `--max-loras` — adapter serving.
- `--enable-prefix-caching`, `--enable-chunked-prefill` — latency/throughput.
- `--max-num-seqs`, `--max-num-batched-tokens`, `--gpu-memory-utilization`.
- `--quantization`, `--kv-cache-dtype`, `--speculative-config`.
- `--structured-outputs-config.backend`, `--reasoning-parser`.
- `--otlp-traces-endpoint`, `--enable-log-requests`, `--disable-log-stats`.
- `--api-key`, `--allowed-local-media-path` (security), `--ssl-*` (transport).

## Notes

- `api_key` can be any non-empty string (e.g. `EMPTY` or `token`); vLLM does not
  validate against a real key by default unless `--api-key` set.
- Multimodal: limits via `--limit-mm-per-prompt` (e.g.
  `{"image":16,"video":{"count":1,"num_frames":32}}`).
