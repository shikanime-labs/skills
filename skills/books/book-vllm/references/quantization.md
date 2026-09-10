# Quantization (vLLM)

Source: <https://docs.vllm.ai/en/latest/features/quantization/>

Quantization trades precision for memory/throughput so larger models fit. Set
via `--quantization <fmt>` (+ optional `--kv-cache-dtype` for KV cache). For
creating quantized checkpoints, [LLM
Compressor](https://docs.vllm.ai/en/latest/features/quantization/llm_compressor/)
supports FP8/INT8/INT4.

## Supported formats

- AWQ (`auto_awq`), GPTQModel (`gptqmodel`), Marlin (GPTQ/AWQ/FP8/FP4 kernel),
  BitsAndBytes (`bnb`), GGUF.
- LLM Compressor: FP8 W8A8, INT8 W8A8, INT4 W4A16, INT8 W4A8.
- NVIDIA ModelOpt, AMD Quark, Intel Neural Compressor (INC), TorchAO, Online
  Quantization, Quantized KV Cache, FP8 ViT Encoder Attention.

## Hardware compatibility matrix

| Implementation | Volta | Turing | Ampere | Ada | Hopper | AMD | Intel GPU | x86 CPU | Arm CPU |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AWQ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| GPTQ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Marlin | ❌ | ✅* | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| llm-comp FP8 W8A8 | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| llm-comp INT8 W8A8 | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| llm-comp INT8 W4A8 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| bitsandbytes | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| GGUF | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

(SM: Volta 7.0, Turing 7.5, Ampere 8.0/8.6, Ada 8.9, Hopper 9.0. *Turing lacks
Marlin MXFP4.)

## When to pick

- FP8 (W8A8) — fastest on Hopper/Blackwell and recent Ada; HLMs fit with least
  accuracy loss. KV cache: `--kv-cache-dtype fp8`.
- AWQ / GPTQ — broad HW support, good accuracy; `--dtype half` recommended for
  AWQ.
- INT4/INT8 (llm-compressor) — CPU/edge or memory-tight GPUs.
- Marlin — kernel acceleration for GPTQ/AWQ/FP8/FP4 when HW supports it.

## Custom / out-of-tree

Register a method via `@register_quantization_config("my_quant")` on a class
subclassing `QuantizationConfig` (implement `get_name`,
`get_supported_act_dtypes`, `get_min_capability`, `get_config_filenames`,
`from_config`, `get_quant_method`). No vLLM source change required.

## Notes

- `--allow-deprecated-quantization` gates removed methods.
- KV-cache quantization is independent of weight quantization: `--kv-cache-dtype
  fp8` etc.
- DeepSeekV3.2 defaults KV to fp8; set `bfloat16` to override.
- Gaudi (Intel) quantization moved to
  [vLLM-Gaudi](https://github.com/vllm-project/vllm-gaudi).
