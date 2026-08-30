# Models & Quantization (docs/models.md)

Distilled structure for obtaining and preparing GGUF models.

## Getting a model

- Hugging Face hosts thousands of GGUF-compatible models
  (`hf.co/models?library=gguf&sort=trending`).
- Run directly from the Hub with the `-hf` flag (unified binary or
  `llama-cli`):

  ```bash
  llama cli -hf ggml-org/gemma-3-1b-it-GGUF
  llama cli -hf ggml-org/Qwen3.5-0.8B-GGUF:Q8_0      # with quant
  ```

- Point at a non-HF endpoint by setting `MODEL_ENDPOINT` to a HF-API-compatible
  URL.
- Local GGUF files work directly: `-m /path/to/model.gguf`.

## GGUF requirement

- llama.cpp requires the [GGUF](https://github.com/ggml-org/ggml/blob/master/docs/gguf.md)
  format. Convert other formats with the `convert_*.py` scripts in the repo.
- Quantization details: see `tools/quantize/README.md` and the
  `quantization.md` reference in this skill.

## Hugging Face online tooling

- **GGUF-my-repo** space — convert to GGUF + quantize weights to smaller sizes.
- **GGUF-my-LoRA** space — convert LoRA adapters to GGUF.
- **GGUF-editor** space (CISCai/gguf-editor) — edit GGUF metadata in-browser.
- **Inference Endpoints** — host `llama.cpp` in the cloud directly.

## Quant selection (quick)

Prefer the quant HF marks compatible for the user's hardware. Defaults:

- General chat: `Q4_K_M`.
- Code / technical: `Q5_K_M` or `Q6_K` if memory allows.
- Tight RAM: `Q3_K_M`, `IQ*` variants, or `Q2*` only if fit beats quality.
- Multimodal repos: the `mmproj-*.gguf` projector is separate from the main
  model file.
- Do not normalize repo-native labels (report `UD-Q4_K_M` as-is).
See `quantization.md` for the full tradeoff matrix.
