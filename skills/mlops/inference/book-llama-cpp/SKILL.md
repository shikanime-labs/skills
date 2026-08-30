---
name: book-llama-cpp
description: Local llama.cpp GGUF inference, serving, and Hub discovery.
version: 2.2.0
author: Hermes
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llama.cpp, GGUF, Quantization, Hugging Face Hub, Build, Backends, Docker, Multi-GPU, Speculative Decoding, Serving, Apple Silicon, NVIDIA, AMD GPUs]
---

# llama.cpp — Local GGUF Inference & Build Reference

Use this skill for local GGUF inference, model discovery on the Hugging Face
Hub, building llama.cpp with the right compute backend, running the
OpenAI-compatible server, multi-GPU deployment, and speculative decoding. It
does NOT cover training or weight conversion from non-GGUF checkpoints beyond
pointers to the repo's `convert_*.py` scripts. Dependency stance: the
llama.cpp CLI/binaries (or `llama-cpp-python` bindings) plus Hugging Face Hub
for `-hf` model pulls.

## When to Use

- Run a local LLM/VLM on CPU, Apple Silicon, CUDA, ROCm, SYCL, Vulkan, etc.
- Find the right GGUF and quant for a Hugging Face repo
- Build llama.cpp from source for a specific backend (Metal, CUDA, HIP, ...)
- Launch `llama-server` or `llama-cli` from the Hub
- Decide between Q4/Q5/Q6/IQ quant variants for the user's RAM/VRAM
- Run across multiple GPUs or enable speculative decoding
- Deploy via the official Docker images

## Prerequisites

- Binaries: `brew install llama.cpp` (macOS/Linux) or `winget install llama.cpp` (Windows); or build from source (see references/build-backends.md).
- Python bindings: `pip install llama-cpp-python` (CUDA: `CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir`; Metal: `-DGGML_METAL=on`).
- Hub pulls (`-hf`) need network access; set `MODEL_ENDPOINT` to any HF-API-compatible URL to use a mirror.

## How to Run

Invoke commands through the `terminal` tool. Discover models and reconstruct
commands with `web_extract` against the Hugging Face URLs in Quick Reference.
Load a reference file on demand with `skill_view` (file_path="references/<file>").

## Quick Reference

```bash
# Run a model straight from the Hub (unified launcher or standalone binary)
llama cli -hf ggml-org/Qwen3.5-0.8B-GGUF
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf --hf-file Phi-3-mini-4k-instruct-q4.gguf -c 4096

# Build from source (CPU)
cmake -B build && cmake --build build --config Release

# Multi-GPU
llama-cli -m model.gguf -sm tensor -ctk f16 -ctv f16          # experimental tensor parallel
llama-cli -m model.gguf -ts 3,1                                # custom split ratio
llama-cli --list-devices                                       # show device names

# Speculative decoding
llama-server -m model.gguf -md draft.gguf --spec-type draft-eagle3
llama-server [...] --spec-type ngram-mod,ngram-map-k4v --spec-draft-n-max 64

# Docker
docker run -v /models:/models -p 8080:8080 ghcr.io/ggml-org/llama.cpp:server \
  -m /models/m.gguf --port 8080 --host 0.0.0.0
```

Hugging Face URL shapes (use via `web_extract`):

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

## Python Bindings (llama-cpp-python)

```python
from llama_cpp import Llama
llm = Llama(model_path="./m-q4_k_m.gguf", n_ctx=4096, n_gpu_layers=35, chat_format="llama-3")
print(llm.create_chat_completion(messages=[{"role":"user","content":"Hi"}])["choices"][0]["message"]["content"])
# From Hub: Llama.from_pretrained(repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF", filename="*Q4_K_M.gguf", n_gpu_layers=35)
```

## Procedure

1. Discover: open `https://huggingface.co/models?apps=llama.cpp&sort=trending`,
   add `search=<term>` and `num_parameters=min:0,max:24B` as needed.
2. Resolve the exact GGUF: load `<repo>?local-app=llama.cpp` for the recommended
   quant and command, then confirm filenames/sizes via the tree API
   (`/api/models/<repo>/tree/main?recursive=true`); separate `mmproj-*.gguf`
   projectors from main checkpoints.
3. Choose a quant (see references/quantization.md): `Q4_K_M` general,
   `Q5_K_M`/`Q6_K` for code, IQ/Q3 for tight RAM. Keep repo-native labels
   (e.g. `UD-Q4_K_M`) as-is.
4. Run: `llama serve -hf <repo>:<QUANT>` or the exact-file form; for Docker use
   the matching `:server` / `:server-cuda` tag.
5. Optimize: set `--n-gpu-layers`/`--device`, tune threads
   (references/optimization.md), scale with multi-GPU
   (references/multi-gpu.md) or speculative decoding
   (references/speculative-decoding.md) when throughput demands it.

## Pitfalls

- GPU Docker images are built but not CI-tested beyond the build; rebuild
  locally (`.devops/*.Dockerfile`) for non-default CUDA/ROCm/MUSA versions.
- `--split-mode tensor` is experimental, needs `-fa on` and non-quantized KV
  (`-ctk f16 -ctv f16`), has no `--fit`, and is unsupported for many MoE/
  state-space architectures (falls back to `layer`).
- `-ngl 0` still offloads *some* compute; use `--device none` to fully disable GPU.
- ngram-mod shares one hash pool across all server slots.
- The unified `llama cli`/`llama serve` launcher and the standalone
  `llama-cli`/`llama-server` binaries are equivalent.

## Verification

Confirm a server is live and the model loaded:

```bash
curl http://localhost:8080/v1/models
```

Or confirm backend/device visibility before launching:

```bash
llama-cli --list-devices
```

## Reference Library

Load any of these on demand with `skill_view` (file_path="references/<name>"):

- **hub-discovery.md** — URL-only HF workflows, search patterns, GGUF extraction, command reconstruction
- **quantization.md** — quant quality tradeoffs, Q4/Q5/Q6/IQ guidance, imatrix
- **build-backends.md** — CMake build, backend flags (CUDA/Metal/HIP/SYCL/Vulkan/...), runtime env vars
- **docker.md** — official image tags and run/build recipes (CUDA/ROCm/MUSA/SYCL)
- **multi-gpu.md** — split modes, device flags, tensor-mode constraints, troubleshooting
- **speculative-decoding.md** — draft types, CLI options, n-gram tuning, statistics
- **server.md** — direct-from-Hub launch, OpenAI endpoints, Docker deploy, load balancing, monitoring
- **optimization.md** — CPU threading, BLAS, GPU offload heuristics, batch tuning, benchmarks
- **advanced-usage.md** — batched inference, grammar-constrained generation, LoRA, custom builds
- **troubleshooting.md** — install/convert/quantize/inference/server issues, Apple Silicon, debugging

## Resources

- GitHub: <https://github.com/ggml-org/llama.cpp>
- Docs index: <https://github.com/ggml-org/llama.cpp/tree/master/docs>
- HF GGUF + llama.cpp: <https://huggingface.co/docs/hub/gguf-llamacpp>
- License: MIT
