# Supported Models (vLLM)

Source: <https://docs.vllm.ai/en/latest/models/supported_models/>

vLLM supports 200+ HF architectures across generative and pooling tasks. Full
list: <https://docs.vllm.ai/en/latest/models/supported_models/>.

## Categories

- Decoder-only LLMs: Llama, Qwen, Gemma.
- MoE LLMs: Mixtral, DeepSeek-V3, Qwen-MoE, GPT-OSS.
- Hybrid attention / SSM: Mamba, Qwen3.5.
- Multimodal: LLaVA, Qwen-VL, Pixtral.
- Embedding/retrieval: E5-Mistral, GTE, ColBERT.
- Reward/classification: Qwen-Math.

## Implementation paths

1. **Native vLLM** — `vllm/model_executor/models`. Listed under supported
   text/multimodal models. Best performance.
2. **Transformers backend** — `model_impl="transformers"` (`--model-impl
   transformers`). Works for encoder-only, decoder-only, MoE; full + sliding
   attention; embedding/VL/audio-language. Performance ≈ native. Check via
   `llm.apply_model(lambda m: print(type(m)))` — `Transformers...` prefix means
   Transformers backend.
3. **Custom HF model** — if neither native nor Transformers, a
   Transformers-compatible custom model (has `auto_map.AutoModel` in
   `config.json`) works via the Transformers backend. Set
   `trust_remote_code=True` (offline) / `--trust-remote-code` (serve). Local
   dir: pass path to `model=`.

## Writing a custom model (Transformers backend compatible)

In `modeling_my_model.py`, inherit `PreTrainedModel` and:

- thread `kwargs` from `MyModel` → `MyAttention`; encoder-only sets
  `is_causal=False`; MoE `experts` is `nn.ModuleList` or packed 3D params,
  forward accepts `(hidden_states, top_k_index, top_k_weights)`.
- `MyAttention` uses
  `ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]`.
- `MyModel` sets `_supports_attention_backend = True`.
For TP/PP compatibility add `base_model_tp_plan` / `base_model_pp_plan` to the
config (e.g. `{"layers.*.self_attn.k_proj":"colwise", ...}`).

## Generation config

- By default vLLM applies the model's HF `generation_config.json` sampling
  params.
- `LLM(..., generation_config="vllm")` / `--generation-config vllm` → vLLM
  defaults only.
- `--override-generation-config '{"temperature":0.5}'` merges/overrides.

## Notes

- `model_impl="auto"` tries native vLLM first, falls back to Transformers.
- VL models (Transformers backend) accept image inputs only; video inputs
  planned.
