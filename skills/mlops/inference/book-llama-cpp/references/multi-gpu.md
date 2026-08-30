# Multi-GPU (docs/multi-gpu.md)

Distilled structure for running llama.cpp across multiple GPUs. CLI flags
below apply to `llama-cli`, `llama-server`, and most other binaries.

## When to use multi-GPU

- Model doesn't fit one GPU's VRAM (spread weights across GPUs).
- More throughput desired (distribute compute; gains depend on interconnect).

## Split modes (`--split-mode` / `-sm`)

| Mode | Behavior | Use when |
|---|---|---|
| `none` | single GPU, pick with `--main-gpu` | confine to one GPU despite others visible |
| `layer` (default) | pipeline parallelism; each GPU holds contiguous layers; KV for layer *l* lives on its GPU | need more memory + fast prefill; slow interconnect OK |
| `row` | **deprecated** old row-split tensor-parallel; superseded by `tensor` | avoid |
| `tensor` | **experimental** tensor parallelism; splits weights *and* KV via meta device | need more memory + fast token gen; fast interconnect |

Pipeline (`layer`) minimizes GPU transfers but needs many tokens to scale.
Tensor (`tensor`) parallelizes any workload but is interconnect-bound.
Pipeline maximizes batch throughput; tensor minimizes latency.

## Key flags

| Short | Long | Values | Default | Notes |
|---|---|---|---|---|
| `-sm` | `--split-mode` | none\|layer\|tensor | layer | |
| `-ts` | `--tensor-split` | `3,1` proportions | auto | order follows `--device`; `3,1` = 75/25 |
| `-mg` | `--main-gpu` | int | 0 | GPU for `split-mode none` |
| `-ngl` | `--n-gpu-layers` | int\|auto\|all | auto | `999`/`all` pushes everything to GPU |
| `-dev` | `--device` | names or `none` | auto | restrict devices; see `--list-devices` |
| | `--list-devices` | - | - | print devices + memory; run first |
| `-fa` | `--flash-attn` | on\|off\|auto | auto | required for `tensor` + quantized V cache |
| `-ctk` | `--cache-type-k` | f32\|f16\|bf16\|q8_0\|q4_0\|... | f16 | KV cache K type |
| `-ctv` | `--cache-type-v` | same as `-ctk` | f16 | KV cache V type |
| `-fit` | `--fit` | on\|off | on | auto-fit unset args to device memory; **not** with `tensor` |

`CUDA_VISIBLE_DEVICES` (any CUDA program) hides GPUs from llama.cpp entirely;
`--device` selects among those visible (works for any backend).

## Recipes

```bash
# 1. default pipeline-parallel across all visible GPUs (--fit sizes automatically)
llama-cli -m model.gguf

# 2. custom split ratio (GPU0 3 parts, GPU1 1 part)
llama-cli -m model.gguf -ts 3,1

# 3. single-GPU, specific device
llama-cli --list-devices
llama-cli -m model.gguf -dev CUDA1

# 4. tensor parallelism (experimental)
llama-cli -m model.gguf -sm tensor -ctk f16 -ctv f16

# 5. NCCL (build-time -DGGML_CUDA_NCCL=ON, default); ROCm uses -DGGML_HIP_RCCL=ON
# 6. CUDA peer-to-peer
GGML_CUDA_P2P=1 llama-cli -m model.gguf -sm tensor
```

## Tensor-mode constraints

- `-fa off` (or unsupported) is a hard error; needs `f16`/`bf16`/`f32` KV.
- `--fit` disabled; may need manual `--ctx-size` to fit.
- Not implemented for: MoE/hybrid (Grok, MPT, OLMoE, DeepSeek2, GLM-DSA,
  Nemotron-H[-MoE], Granite-Hybrid, LFM2-MoE, Minimax-M2, Mistral4, Kimi-Linear,
  Jamba, Falcon-H1), state-space/RWKV (Mamba, Mamba2), and PLAMO2, MiniCPM3,
  Gemma-3n, OLMo2, BitNet, T5. Falls back to `--split-mode layer`.
- RCCL disabled by default for ROCm (unlike NCCL).

## Troubleshooting

| Symptom | Fix |
|---|---|
| "SPLIT_MODE_TENSOR requires flash_attn" | add `-fa on` |
| "simultaneous use of SPLIT_MODE_TENSOR and KV cache quantization" | `-ctk f16 -ctv f16` |
| "LLAMA_SPLIT_MODE_TENSOR not implemented for 'X'" | use `--split-mode layer` |
| "NCCL unavailable, multi GPU performance suboptimal" | install NCCL + rebuild |
| CUDA OOM in `tensor` | lower `-c`, `-np` (server), then `-ngl` |
| worse with multi-GPU | interconnect-bound; verify NCCL; try `layer` |
| GPU unused | `-ngl` too low / `CUDA_VISIBLE_DEVICES=-1` / backend missing |
| crashes after `GGML_CUDA_P2P=1` | unset it (IOMMU/BIOS issue) |
