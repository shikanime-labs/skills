# Engine Arguments Reference (vLLM)

Source: <https://docs.vllm.ai/en/latest/configuration/engine_args/>

Engine args are one dataclass (`EngineArgs` / `AsyncEngineArgs`) shared by:

- offline `LLM(...)` — passed as Python kwargs,
- online `vllm serve` — passed as CLI flags.

`vllm serve --help` is the source of truth for types and defaults. JSON CLI
args: `--json-arg '{"key":"v"}'` ≡ `--json-arg.key v`; lists via
`--json-arg.key4+ v3`.

## ModelConfig

- `--model` — HF name or path (default `Qwen/Qwen3-0.6B`). Also the metrics
  `model_name` tag unless `--served-model-name` set.
- `--served-model-name` — API name(s); first is used in responses and metrics.
- `--tokenizer`, `--tokenizer-mode`
  (`auto|hf|slow|mistral|cohere|deepseek_v32|deepseek_v4|kimi_k3|...`).
- `--dtype` (`auto|bfloat16|float16|half|float32|float`) — `auto`: FP16 for
  FP32/FP16 models, BF16 for BF16.
- `--max-model-len` — accepts human suffixes (`1k`=1000, `1K`=1024,
  `25.6k`=25600); `-1`/`auto` fits largest len to GPU.
- `--quantization`/`-q` — format name; if None, reads model
  `quantization_config`.
- `--revision`, `--tokenizer-revision`, `--code-revision` — HF
  branch/tag/commit.
- `--trust-remote-code` — required for custom HF models.
- `--hf-token` — bearer token for remote files (`True` uses
  `~/.cache/huggingface/token`).
- `--generation-config` (`auto|vllm|<dir>`) — `vllm` = no HF config, vLLM
  defaults. `--override-generation-config '{"temperature":0.5}'`.
- `--model-impl` (`auto|vllm|transformers|terratorch`) — `auto` prefers vLLM
  impl, falls back to Transformers.
- `--seed` — global seed; must be set so TP workers sample identically.
- `--enforce-eager` — disable CUDA graphs (eager mode) for debugging.
- `--runner` (`auto|draft|generate|pooling`), `--convert`
  (`auto|classify|embed|none`).
- `--allowed-local-media-path`, `--allowed-media-domains` — multimodal input
  allowlist (security-sensitive).

## LoadConfig

- `--load-format`
  (`auto|safetensors|pt|dummy|tensorizer|sharded_state|mistral|npcache|instanttensor|runai_streamer|...`).
- `--download-dir` — weights cache dir.
- `--safetensors-load-strategy` (`None|lazy|eager|prefetch|torchao`) — `eager`
  recommended on NFS/Lustre; `None` auto-prefetches on NFS if checkpoint < 90%
  RAM.
- `--ignore-patterns` (default `['original/**/*']`) — skip files when loading.

## ParallelConfig (distributed)

- `--tensor-parallel-size`/`-tp` (default 1), `--pipeline-parallel-size`/`-pp`
  (default 1).
- `--distributed-executor-backend` (`mp|ray|uni|external_launcher`) — `mp` auto
  when `tp*pp <= gpus`. TPU supports only Ray.
- `--data-parallel-size`/`-dp` — MoE sharded by `tp*pcp*dp`.
  `--data-parallel-rank`/`-dpr` enables external-LB mode (MoE only; else run
  independent instances).
- `--data-parallel-hybrid-lb`/`-dph`, `--data-parallel-external-lb`/`-dpe` — LB
  modes for online serving.
- `--enable-expert-parallel`/`-ep` — use EP instead of TP for MoE.
  `--enable-eplb` load balances experts.
- `--prefill-context-parallel-size`/`-pcp`,
  `--decode-context-parallel-size`/`-dcp` — shard prefill/decode compute/KV.
- Multi-node (mp backend): `--nnodes`/`-n`, `--node-rank`/`-r`, `--master-addr`,
  `--master-port`. `--device-ids` selects physical GPUs (avoids
  CUDA_VISIBLE_DEVICES, keeps topology for NIC affinity).

## CacheConfig (KV cache)

- `--gpu-memory-utilization` (default `0.92`) — per-instance fraction; two
  instances coexist at 0.5 each.
- `--kv-cache-memory-bytes` — overrides util-based sizing when set (ignores
  `--gpu-memory-utilization`).
- `--kv-cache-dtype` (`auto|fp8|fp8_e4m3|nvfp4|int8_per_token_head|...`) — KV
  quantization (e.g. `fp8` on CUDA 11.8+). DeepSeekV3.2 defaults to fp8.
- `--block-size` — tokens per KV block.
- `--enable-prefix-caching` — reuse prefix KV (hits from
  `vllm:prefix_cache_hits`); `--prefix-caching-hash-algo` (`sha256` default |
  `xxhash` faster, non-cryptographic).
- `--kv-offloading-size` + `--kv-offloading-backend` (`native|lmcache`) — CPU
  offload of KV.
- `--kv-cache-metrics` — residency metrics (needs log-stats on).

## SchedulerConfig

- `--max-num-seqs` — max concurrent sequences per iteration.
- `--max-num-batched-tokens` — max tokens scheduled/prefilled per iteration
  (human suffixes allowed).
- `--max-num-scheduled-tokens` — ≤ batched tokens; smaller for spec-decode
  appends.
- `--enable-chunked-prefill` — chunk long prefills to fit
  `max_num_batched_tokens`.
- `--scheduling-policy` (`fcfs|priority`) — priority by request priority value.
- `--watermark` (default 0.0) — free-KV fraction kept to avoid
  thrash/preemption.
- `--async-scheduling` (default on) — avoids GPU idle gaps.
- `--long-prefill-token-threshold` (0 disables) — chunked-prefill long-prompt
  cutoff.
- `--stream-interval` (default 1) — tokens buffered before streaming.

## LoRAConfig

- `--enable-lora`, `--max-loras` (default 1), `--max-lora-rank` (`1..512`,
  default 16), `--lora-dtype auto`, `--max-cpu-loras`, `--fully-sharded-loras`.
- `--lora-target-modules` — restrict to module suffixes (e.g.
  `["o_proj","qkv_proj"]`).

## SpeculativeConfig (see references/speculative-decoding.md)

- `--speculative-config`/`-sc` (JSON), `--spec-method`, `--spec-model`,
  `--spec-tokens`.

## CompilationConfig

- `--optimization-level` (`-O0`..`-O3`, default 2) — startup cost vs perf.
- `--performance-mode` (`balanced|interactivity|throughput`),
  `--compilation-config`/`-cc` (`{"mode":3,...}`), `--cudagraph-capture-sizes`,
  `--max-cudagraph-capture-size` (cap 512, 1024 on DC Blackwell).

## ObservabilityConfig

- `--otlp-traces-endpoint` — OTLP traces; `--collect-detailed-traces`
  (`model|worker|all`).
- `--enable-mfu-metrics` — Model FLOPs Utilization. `--kv-cache-metrics`,
  `--cudagraph-metrics`.

## AsyncEngineArgs (server-only extras)

- `--enable-log-requests` — log request params (INFO) / prompts (DEBUG); gate
  via `VLLM_LOGGING_LEVEL`.

## CLI flag notes

- Defaults shown assume latest docs; always confirm with `vllm serve --help` on
  the installed version.
- JSON scalar flags (`--quantization-config`, `--pooler-config`,
  `--speculative-config`, `--kv-transfer-config`, `--reasoning-config`,
  `--attention-config`, `--structured-outputs-config`) accept a JSON string OR
  dotted key form (`--speculative-config.method draft_model`).
