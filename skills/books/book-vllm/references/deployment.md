# Deployment & Troubleshooting (vLLM)

Source: <https://docs.vllm.ai/en/latest/deployment/docker/> + engine-args +
metrics.

## Docker (production)

```bash
docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HF_TOKEN=$HF_TOKEN" -p 8000:8000 --ipc=host \
  vllm/vllm-openai:latest --model Qwen/Qwen3-0.6B
# Podman:
podman run --device nvidia.com/gpu=all -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HF_TOKEN=$HF_TOKEN" -p 8000:8000 --ipc=host \
  docker.io/vllm/vllm-openai:latest --model Qwen/Qwen3-0.6B
```

- `--ipc=host` (or `--shm-size`) required: PyTorch shares data via shared
  memory, esp. for TP.
- Add any engine args after the image tag.
- Optional deps omitted for licensing; add a layer: `FROM
  vllm/vllm-openai:v0.11.0\nRUN uv pip install --system vllm[audio]==0.11.0`.
- Dev image: override entrypoint (`--entrypoint /bin/bash`).

### CUDA compatibility (old host drivers)

Set `VLLM_ENABLE_CUDA_COMPATIBILITY=1` — configures `LD_LIBRARY_PATH` to compat
libs. CUDA 13 images: R535 kernel min Linux 3.10, R570/R580 min Linux 4.15.

### AMD ROCm

```bash
docker run --rm --group-add=video --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  --device /dev/kfd --device /dev/dri \
  -v ~/.cache/huggingface:/root/.cache/huggingface --env "HF_TOKEN=$HF_TOKEN" \
  -p 8000:8000 --ipc=host vllm/vllm-openai-rocm:<tag> --model Qwen/Qwen3-0.6B
```

AMD's `rocm/vllm` images are deprecated in favor of the official
`vllm/vllm-openai-rocm`.

## Failure modes & fixes

- **OOM at load** — lower `--gpu-memory-utilization` (e.g. 0.7), shrink
  `--max-model-len`, or `--quantization awq|gptq|fp8`, or `--cpu-offload-gb`.
- **High TTFT** — `--enable-prefix-caching`; for long prompts
  `--enable-chunked-prefill`; raise `--max-num-batched-tokens`.
- **Model not found / custom arch** — `--trust-remote-code`; or use Transformers
  backend `--model-impl transformers`.
- **Low throughput (<50 req/s)** — raise `--max-num-seqs`; check `nvidia-smi`
  GPU util (>80% target); verify TP is power-of-two (`-tp 4` not 3).
- **KV thrash / preemption** — set `--watermark` > 0 (free-KV headroom);
  `--scheduler-reserve-full-isl` (default True) prevents over-admission with
  chunked prefill.
- **Multimodal OOM at init** — `--skip-mm-profiling` shifts peak-memory estimate
  to the user (faster startup, risk).
- **Slow first requests** — CUDA graph / torch.compile warmup;
  `--optimization-level 2` (default) or `-O3` for perf; `-O0` fastest startup.

## Sizing heuristics

- 7–13B: 1× A10 (24GB) / A100 (40GB).
- 30–40B: 2× A100 (40GB) + TP.
- 70B+: 4× A100 (40GB) or 2× A100 (80GB) + AWQ/GPTQ.
- Supported HW: NVIDIA (primary), AMD ROCm, Intel XPU, TPU, Gaudi, Ascend, Apple
  Silicon (Metal), plus plugins (Intel Gaudi, IBM Spyre, Huawei Ascend,
  Rebellions, MetaX).

## Verification

```bash
curl -s http://localhost:8000/health        # 200 = alive
curl -s http://localhost:8000/v1/models     # lists served model
curl -s http://localhost:8000/metrics | grep -E 'vllm:(num_requests_running|kv_cache_usage_perc|time_to_first_token_seconds)'
```
