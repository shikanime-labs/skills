---
name: book-vllm
description: "Run vLLM: offline LLM, OpenAI API server, quant, spec decode, parallel."
version: 0.1.0
license: Apache-2.0
author: Hermes Agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [vLLM, Inference Serving, OpenAI API, Quantization, Speculative Decoding, Tensor Parallelism, Production]

---

# vLLM — High-Throughput LLM Serving

Distilled working knowledge of the vLLM documentation (docs.vllm.ai, latest).
Covers offline batch inference, the OpenAI-compatible server, engine
configuration, quantization, speculative decoding, distributed serving, and
observability. The source is large and fast-moving; the bulk lives in
`references/` files loaded on demand with `skill_view`
(`file_path="references/<file>"`).

This skill does NOT replace the upstream docs for deep API detail — it captures
the commands, flags, and decision rules you actually reach for. Every value
below was read from the docs; do not invent flags.

## Scope (covered vs. not)

**Covered (distilled from docs.vllm.ai, latest):** offline `LLM` inference, the
OpenAI-compatible server (`vllm serve`), engine args, quantization, speculative
decoding, distributed/parallel serving, Prometheus metrics, install, and
supported models.

**NOT covered — go to upstream docs or state you lack it:**

- Training / RLHF and the weight-transfer APIs beyond the one-line `LLM` hooks
  (<https://docs.vllm.ai/en/latest/training/>).
- Developer/contributor guide, benchmarking CLI and perf methodology
  (<https://docs.vllm.ai/en/latest/benchmarking/>).
- Per-feature deep dives (e.g. full disaggregated prefill, encoder cache,
  diffusion LLMs, reasoning parsers) — only the flags are noted here.
- Version-specific behavior: defaults/channels move fast; always confirm with
  `vllm serve --help` on the installed version before asserting a default.

## When to Use

- Deploying or operating an OpenAI-compatible LLM API server (`vllm serve`).
- Running offline/batch generation with the `LLM` class.
- Choosing a quantization format or speculative-decoding method.
- Sizing tensor/pipeline/data/expert parallelism for a model across GPUs.
- Debugging OOM, low throughput, high TTFT, or KV-cache pressure.
- Wiring Prometheus metrics or structured (JSON/grammar) outputs.

## Prerequisites

- Linux host with NVIDIA (primary), AMD ROCm, Intel XPU, TPU, or other supported
  backend. macOS works only via
  [vLLM-Metal](https://github.com/vllm-project/vllm-metal) (MLX backend, needs
  `mlx-community` models).
- Python 3.10–3.13. Recommended installer: `uv` (`uv venv --python 3.12 --seed
  && source .venv/bin/activate && uv pip install vllm --torch-backend=auto`).
- CUDA driver present for NVIDIA; `uv` auto-selects the PyTorch index via
  `--torch-backend=auto` (or `UV_TORCH_BACKEND=cu126`).
- Optional: `HF_TOKEN` for gated/private models; `docker` for the official image
  `vllm/vllm-openai`.

## How to Run

Invoking vLLM is always through the `terminal` tool. Core entrypoints:

```bash
# Offline generation (Python) — see references/offline-inference.md
uv run --with vllm python my_script.py

# OpenAI-compatible server
vllm serve <model> --host 0.0.0.0 --port 8000

# Inspect every flag (source of truth for types/defaults)
vllm serve --help
vllm serve --help | grep -A2 <flag>
```

Load a chapter only when the task needs it:

```text
skill_view(name="book-serving-llms-vllm", file_path="references/engine-args.md")
```

## Quick Reference

- Install: `uv pip install vllm --torch-backend=auto`
- Offline: `from vllm import LLM, SamplingParams` → `llm.generate(prompts,
  sampling)`
- Serve: `vllm serve meta-llm/Llama-3-8B-Instruct --tensor-parallel-size 2`
- Chat client: `OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")`
- Metrics: `GET /metrics` (Prometheus, `vllm:` prefix); `/health`, `/v1/models`,
  `/version`, `/load`
- Quantize: `--quantization awq|gptq|fp8` (+ `--kv-cache-dtype fp8` for KV)
- Speculate: `--speculative-config
  '{"method":"draft_model","model":"<draft>","num_speculative_tokens":5}'`
- Parallel: `-tp` tensor, `-pp` pipeline, `-dp` data, `-ep` expert (MoE)
- Prefix cache: `--enable-prefix-caching`; chunked prefill:
  `--enable-chunked-prefill`

## Procedure

1. Install vLLM in an isolated env (`terminal`): `uv venv --python 3.12 --seed
   && source .venv/bin/activate && uv pip install vllm --torch-backend=auto`.
2. Pick an entrypoint: offline `LLM` class (single process) or `vllm serve`
   (HTTP server, OpenAI-compatible).
3. Set model load flags: `--model`, `--dtype auto`, `--max-model-len`,
   `--tensor-parallel-size` for multi-GPU, `--gpu-memory-utilization 0.92`
   (default).
4. Add optimizations as needed: `--enable-prefix-caching`,
   `--enable-chunked-prefill`, `--quantization`, `--speculative-config`.
   Reference `references/engine-args.md` for the full flag set.
5. For online serving, point an OpenAI SDK at `http://host:8000/v1` with
   `api_key="EMPTY"`. See `references/openai-server.md`.
6. Verify health (`curl /health`) and check `/metrics` for
   `vllm:num_requests_running`, `vllm:kv_cache_usage_perc`,
   `vllm:time_to_first_token_seconds`.

## Pitfalls

- `--gpu-memory-utilization` is per-instance; two instances on one GPU each at
  0.5 coexist. Default 0.92.
- Tensor-parallel size must be a power of two for best results (or sized to GPU
  count); `mp` backend auto-used when `tp*pp <= gpus`.
- `--trust-remote-code` is required for custom HF models;
  `--allowed-local-media-path` is a security risk (only in trusted envs).
- `generation_config="vllm"` disables the model's HF `generation_config.json`
  defaults; otherwise vLLM applies the model creator's recommended sampling
  params.
- Deprecated `guided_*` structured-output fields were removed in v0.12.0 — use
  `structured_outputs` (`extra_body={"structured_outputs":{"json":...}}`).
- `--speculative-model` was replaced by `--speculative-config` (JSON).
- macOS/Apple Silicon uses vLLM-Metal (MLX), not the CUDA build; many features
  differ.
- Engine args are the same dataclass for `LLM(...)` (kwargs) and `vllm serve`
  (CLI flags).

## Verification

```bash
# Server is up and lists models
curl -s http://localhost:8000/health && curl -s http://localhost:8000/v1/models
# Metrics present
curl -s http://localhost:8000/metrics | grep -E 'vllm:(num_requests_running|kv_cache_usage_perc|time_to_first_token_seconds)'
```

A 200 from `/health` and non-empty `vllm:*` metrics confirms the engine is
serving.

## Reference Index (load on demand)

- `references/engine-args.md` — full engine-argument reference by config group
  (Model/Load/Parallel/Cache/Scheduler/Spec/LoRA). Load when tuning the CLI or
  `LLM(...)` kwargs.
- `references/openai-server.md` — endpoints, online-serving flags, structured
  outputs, tool calling. Load when standing up or querying the HTTP API.
- `references/offline-inference.md` — `LLM` class APIs
  (generate/chat/embed/classify/score), async queue, sleep mode, profiling.
- `references/quantization.md` — formats, hardware compatibility matrix, when to
  pick each.
- `references/speculative-decoding.md` — methods, `--speculative-config` schema,
  selection table.
- `references/distributed-serving.md` — TP/PP/DP/EP, context parallel,
  data-parallel LB modes, multi-node.
- `references/metrics.md` — Prometheus metric names, dashboards, tracing.
- `references/installation.md` — per-backend install
  (CUDA/ROCm/XPU/TPU/Ascend/Metal), Docker.
- `references/models.md` — supported architectures, Transformers backend, custom
  models.
- `references/deployment.md` — Docker image flags, production notes, common
  failure modes.
