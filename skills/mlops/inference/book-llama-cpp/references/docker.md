# Docker (docs/docker.md)

Distilled structure for the official llama.cpp container images.

## Image tags (ghcr.io/ggml-org/llama.cpp)

Base variants (platforms: linux/amd64, linux/arm64, linux/s390x):

- `:full` — `llama-cli` + `llama-completion` + conversion tools
- `:light` — `llama-cli` + `llama-completion` only
- `:server` — `llama-server` only

GPU-accelerated variants (same contents, compiled with the backend):

- CUDA 12: `:full-cuda`, `:light-cuda`, `:server-cuda`
- CUDA 13: `:full-cuda13`, `:light-cuda13`, `:server-cuda13`
- ROCm: `:full-rocm`, `:light-rocm`, `:server-rocm` (linux/amd64)
- MUSA: `:full-musa`, `:light-musa`, `:server-musa`
- SYCL/Intel: `:full-intel`, `:light-intel`, `:server-intel`
- Vulkan: `:full-vulkan`, `:light-vulkan`, `:server-vulkan`
- OpenVINO: `:full-openvino`, `:light-openvino`, `:server-openvino`
- s390x aliases: `:full-s390x`, `:light-s390x`, `:server-s390x`

GPU images are built but not CI-tested beyond build; rebuild locally for
different CUDA/ROCm/MUSA versions.

## Basic usage

```bash
# all-in-one: download + convert + quantize
docker run -v /path/to/models:/models ghcr.io/ggml-org/llama.cpp:full \
  --all-in-one "/models/" 7B

# run
docker run -v /path/to/models:/models ghcr.io/ggml-org/llama.cpp:full \
  --run -m /models/7B/ggml-model-q4_0.gguf

# server
docker run -v /path/to/models:/models -p 8080:8080 \
  ghcr.io/ggml-org/llama.cpp:server \
  -m /models/7B/ggml-model-q4_0.gguf --port 8080 --host 0.0.0.0 -n 512
```

`--entrypoint /app/llama-cli` is the default and can be omitted.

## CUDA container

Requires `nvidia-container-toolkit` on Linux / GPU cloud.

```bash
docker run --gpus all -v /path/to/models:/models local/llama.cpp:full-cuda \
  --run -m /models/7B/ggml-model-q4_0.gguf -p "..." -n 512 --n-gpu-layers 1
```

Local build: `docker build -t local/llama.cpp:full-cuda --target full -f .devops/cuda.Dockerfile .`
Defaults: `CUDA_VERSION=12.8.1`, `CUDA_DOCKER_ARCH` = all supported.

## MUSA / SYCL containers

- MUSA: set `mthreads` as default runtime via the mt-container-toolkit, then
  run with `--n-gpu-layers`.
- SYCL: pass `--device /dev/dri/renderD128:/dev/dri/renderD128 --device /dev/dri/card0:/dev/dri/card0` and `--n-gpu-layers 99`. Intel GPU driver must be installed on the **host**.
