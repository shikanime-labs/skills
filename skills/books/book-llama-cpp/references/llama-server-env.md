# llama-server flag -> LLAMA_ARG_* env mapping

Every `llama-server` flag has a `LLAMA_ARG_<UPPER>_<UNDERSCORE>` env
equivalent (auto-generated from the same `--help` source the binary is built
with). Passing flags as env vars lets a container keep `command: [llama-server]`
with NO `args:` — cleaner, and avoids `/bin/sh -c` wrapping (which is dead
weight and breaks signal handling).

| CLI flag | Env var | Example value |
|----------|---------|---------------|
| `--host` | `LLAMA_ARG_HOST` | `0.0.0.0` |
| `--port` | `LLAMA_ARG_PORT` | `8080` |
| `--models-dir` | `LLAMA_ARG_MODELS_DIR` | `/models` |
| `--models-max` | `LLAMA_ARG_MODELS_MAX` | `5` |
| `--embeddings` | `LLAMA_ARG_EMBEDDINGS` | empty string (`value: ""`) |
| `-c` | `LLAMA_ARG_CTX_SIZE` | `32768` |
| `--flash-attn` | `LLAMA_ARG_FLASH_ATTN` | `on` |
| `--gpu-layers` | `LLAMA_ARG_N_GPU_LAYERS` | `999` |
| `--no-mmap` | `LLAMA_ARG_MMAP` | `0` (inverted: `--no-*` flag -> falsy value) |

Bool-ish flags map to empty string (`--embeddings` -> `""`) or the inverted
value (`--no-mmap` -> `0`). Full mapping: upstream `tools/server/README.md`
(auto-generated `--help` dump, stable across builds).

## Critical: `--no-models-autoload` is a trap behind API gateways

`--no-models-autoload` is a `--no-*` switch (default ON). With it set, the
server will NOT auto-load a model on a chat request — it waits for an explicit
`POST /models/load`, which API-gateway clients never send, so inference fails
on the first request. Lazy "download/load on first use" IS the default
autoload behavior. OMIT the flag.
