# Metrics & Observability (vLLM)

Source: <https://docs.vllm.ai/en/latest/design/metrics/>

vLLM (V1 engine) exposes Prometheus-compatible metrics at `/metrics` with the
`vllm:` prefix. Mental model: server-level metrics explain request-level metrics
(the SLOs an SRE tracks).

## Server-level (Gauges/Counters)

- `vllm:num_requests_running` — requests currently running.
- `vllm:num_requests_waiting`, `vllm:num_requests_swapped` — queue/ swapped
  states.
- `vllm:kv_cache_usage_perc` — fraction of KV blocks used (0–1).
- `vllm:prefix_cache_queries`, `vllm:prefix_cache_hits` — prefix-cache reuse.
- `vllm:prompt_tokens_total`, `vllm:generation_tokens_total` — cumulative
  tokens.
- `vllm:request_success_total` — finished by finish reason (EOS / max len).
- `vllm:gpu_cache_usage_perc`, `vllm:cpu_cache_usage_perc`.

## Request-level (Histograms — the SLOs)

- `vllm:time_to_first_token_seconds` (TTFT)
- `vllm:inter_token_latency_seconds` (TPOT)
- `vllm:e2e_request_latency_seconds`
- `vllm:request_prefill_time_seconds`, `vllm:request_decode_time_seconds`
- `vllm:request_queue_time_seconds`
- `vllm:request_prompt_tokens`, `vllm:request_generation_tokens`
- `vllm:request_max_num_generation_tokens`

## Grafana dashboard (reference)

Subset exposed in the bundled dashboard indicates the most important signals:
e2e latency bucket, prompt/generation tokens, ITL, TTFT, running/waiting/swapped
counts, KV usage %, request success, queue/prefill/decode time. Reference
example: `examples/observability/prometheus_grafana/README.md`.

## HTTP metrics

`prometheus_fastapi_instrumentator` adds `http_requests_total`,
`http_request_size_bytes`, `http_response_size_bytes`,
`http_request_duration_seconds` (by handler/method/status). Query:

```bash
curl -s http://localhost:8000/metrics | grep -P '^http_(?!.*(_bucket|_created|_sum)).*'
```

## Enabling extras (CLI)

- `--otlp-traces-endpoint <url>` + `--collect-detailed-traces model|worker|all`
  — OTLP traces.
- `--enable-mfu-metrics` — Model FLOPs Utilization.
- `--kv-cache-metrics` (+ `--kv-cache-metrics-sample`, default 0.01) — KV
  residency (needs log-stats on).
- `--cudagraph-metrics` — CUDA graph dispatch modes.
- `--show-hidden-metrics-for-version 0.7` — re-enable deprecated metrics during
  migration.
- `--disable-log-stats` off by default; required for some metrics.

## Offline

`LLM.get_metrics()` returns a Prometheus snapshot (see
references/offline-inference.md).
