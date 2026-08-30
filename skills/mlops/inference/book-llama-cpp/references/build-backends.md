# Build & Backends (docs/build.md)

Distilled structure for compiling llama.cpp and selecting a compute backend.
The product is the `llama` library (`include/llama.h`) plus example binaries
(`llama-cli`, `llama-server`, `llama-server`, etc.).

## Binary naming

- Recent builds ship a unified launcher: `llama cli`, `llama serve`.
- Standalone binaries `llama-cli` / `llama-server` remain valid and are used
  throughout the docs. Treat the two forms as equivalent unless noted.

## Generic CMake build

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build
cmake --build build --config Release        # add -j 8 for parallel
```

- Debug (single-config): `cmake -B build -DCMAKE_BUILD_TYPE=Debug`
- Debug (multi-config, e.g. Xcode): `cmake --build build --config Debug`
- Static: `-DBUILD_SHARED_LIBS=OFF`
- ccache speeds rebuilds. HTTPS/TLS needs OpenSSL dev libs; builds run without
  it if absent.
- Windows: use a VS2022 Developer prompt; WoA uses `cmake --preset arm64-windows-llvm-release -DGGML_OPENMP_FETCH=ON`.

## Backend selection (compile-time flags)

Backend is chosen by a `GGML_*` CMake option; most can be combined
(e.g. `-DGGML_CUDA=ON -DGGML_VULKAN=ON`). At runtime pick devices with
`--device`; list them with `--list-devices`.

| Backend | Flag | Target | Notes |
|---|---|---|---|
| CPU | (default) | all | baseline; disable higher-priority backends with `-DGGML_METAL=OFF` or `--device none` |
| BLAS | `-DGGML_BLAS=ON` | all | helps prompt processing at batch > 32; no gen-speed effect |
| Accelerate | default on macOS | Apple Silicon/Intel Mac | enabled automatically |
| OpenBLAS | `-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS` | CPU | |
| BLIS / oneMKL | `GGML_BLAS_VENDOR` | CPU / Intel | oneMKL via `icx`/`icpx`; no Intel **GPU** |
| Metal | default on macOS; off with `-DGGML_METAL=OFF` | Apple Silicon | GPU compute; disable at runtime with `--n-gpu-layers 0` |
| CUDA | `-DGGML_CUDA=ON` | NVIDIA | needs CUDA toolkit |
| HIP | `-DGGML_HIP=ON` | AMD GPU | ROCm; ggml CUDA code translated via HIP |
| SYCL | (see backend/SYCL.md) | Intel GPU | Arc/Flex/Max/iGPU |
| Vulkan | `-DGGML_VULKAN=ON` | GPU | cross-vendor |
| CANN | `-DGGML_CANN=ON` | Ascend NPU | |
| MUSA | `-DGGML_MUSA=ON` | Moore Threads GPU | |
| ZenDNN | `-DGGML_ZENDNN=ON` | AMD CPU | |
| OpenCL | `-DGGML_OPENCL=ON` | Adreno (Android) | headers + ICD loader required |
| WebGPU | `-DGGML_WEBGPU=ON` | browser/WASM | needs Dawn |
| IBM Z | (see build-s390x.md) | IBM Z & LinuxONE | |
| RPC | (tools/rpc) | all | remote backend |

## CUDA specifics

- Non-native for all GPUs: `-DGGML_CUDA=ON -DGGML_NATIVE=OFF`.
- Override compute capability when `nvcc` can't detect:
  `-DCMAKE_CUDA_ARCHITECTURES="86;89"` (lookup at developer.nvidia.com/cuda-gpus).
- Pin a CUDA install: pass `-DCMAKE_CUDA_COMPILER=/opt/cuda-11.7/bin/nvcc` and
  RPATH flags.
- Old CUDA + new glibc `cospi`/`sinpi` errors: patch `math_functions.h` to add
  `noexcept (true)` (see build.md for exact lines).

### CUDA runtime env vars

- `CUDA_VISIBLE_DEVICES="0,1"` / `"-0"` (hide first) — hides GPUs from llama.cpp.
- `CUDA_SCALE_LAUNCH_QUEUES=4x` — larger command buffer; helps multi-GPU
  pipeline-parallel prefill.
- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` — swap to RAM when VRAM exhausted
  (Linux; Windows = System Memory Fallback).
- `GGML_CUDA_P2P=1` — peer-to-peer GPU transfers; opt-in, may crash on some
  motherboards/BIOS (IOMMU).
- `GGML_CUDA_CUBLAS_COMPUTE_TYPE` — `auto|f16|fp16|bf16|f32|fp32`.
- `GGML_CUDA_FORCE_MMQ` — force custom MMQ kernels (lower VRAM, slower batches).

## GPU backend notes

- `-ngl 0` (`--n-gpu-layers 0`) still offloads *some* compute to GPU; fully
  disable with `--device none`.
- Build backends as dynamic libs with `GGML_BACKEND_DL=ON` to use one binary
  across machines with different GPUs.
