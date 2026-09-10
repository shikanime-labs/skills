# Installation (vLLM)

Source: <https://docs.vllm.ai/en/latest/getting_started/quickstart/> +
installation guide.

Prerequisites: Linux (macOS only via vLLM-Metal). Python 3.10–3.13.

## NVIDIA CUDA (recommended)

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto   # picks PyTorch index from CUDA driver
# one-shot: uv run --with vllm vllm --help
```

`--torch-backend=auto` (or `UV_TORCH_BACKEND=cu126`) lets uv select the right
index at runtime. `conda` also supported (`conda create -n myenv python=3.12 -y
&& conda activate myenv && pip install --upgrade uv && uv pip install vllm
--torch-backend=auto`).

## AMD ROCm

```bash
uv venv --python 3.12 --seed && source .venv/bin/activate
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

Supports Python 3.12, ROCm 7.0, glibc ≥ 2.35. Nightly:
`vllm/vllm-openai-rocm:nightly`.

## Intel XPU

Official Docker from v0.26.0 (`vllm/vllm-openai-xpu:nightly`); prebuilt XPU
wheels coming. See GPU install guide "Intel XPU" tab.

## Google TPU

```bash
uv pip install vllm-tpu
```

Full docs: <https://docs.vllm.ai/projects/tpu/en/latest/> (Docker, source build,
troubleshooting).

## Ascend NPU

Community plugin [vLLM Ascend](https://github.com/vllm-project/vllm-ascend);
quick start at <https://docs.vllm.ai/projects/ascend/en/latest/quick_start.html>.

## Apple Silicon (Mac)

[vLLM-Metal](https://github.com/vllm-project/vllm-metal) — MLX backend (NOT
PyTorch), needs `mlx-community` models from HF. See GPU install guide "Apple
Silicon" tab.

## Docker (see references/deployment.md)

`vllm/vllm-openai:latest` (CUDA), `vllm/vllm-openai-rocm:<tag>` (AMD),
`vllm/vllm-openai-xpu:nightly` (Intel). Add engine args after the image tag.
Optional deps (audio etc.) omitted for licensing — add via a custom Dockerfile
layer `RUN uv pip install --system vllm[audio]==<ver>`.

## Notes

- For non-CUDA platforms, the [installation
  guide](https://docs.vllm.ai/en/latest/getting_started/installation/) has
  platform tabs (build from source, Docker).
- `uv` gives vLLM's extra index priority over PyPI by default.
