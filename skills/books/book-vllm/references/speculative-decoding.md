# Speculative Decoding (vLLM)

Source: <https://docs.vllm.ai/en/latest/features/speculative_decoding/>

Reduces inter-token latency under medium-to-low QPS / memory-bound workloads by
drafting several tokens then verifying in one pass.

## Configure

JSON only — `--speculative-config` on CLI or `LLM(...,
speculative_config={...})` in Python:

```bash
vllm serve <target> --speculative-config '{
  "method": "draft_model",
  "model": "<draft-model>",
  "num_speculative_tokens": 5
}'
```

## Methods

Model-based (best latency gain): EAGLE/EAGLE3, MTP (multi-token prediction),
Draft Model, PARD (parallel draft), MLP speculator, DFlash, Medusa. Lightweight:
N-gram, Suffix decoding (dynamic depth, no extra model), extract_hidden_states.
Experimental/custom: custom_class (your own proposer; `method="custom_class"`,
`model="module.YourProposer"` implementing `propose` over a `VllmConfig`),
dynamic SD, adaptive verification (DSpark), per-request acceptance metrics.

`--spec-method` accepts a long list (auto-detected from `model` when possible):
`draft_model|ngram|suffix|mtp|eagle|eagle3|dflash|mlp_speculator|medusa|deepseek_mtp|...|None`.
N-gram needs `prompt_lookup_max` / `prompt_lookup_min`.

## Selection at a glance

| Method | Low QPS | High QPS | Notes |
| --- | --- | --- | --- |
| EAGLE | High | Med–High | Strong general-purpose |
| MTP | High | Med–High | Best if target has native MTP |
| Draft model | High | Med | Needs separate draft model |
| PARD | High | Med–High | Low draft latency |
| MLP | Med–High | Med | If MLP speculators exist |
| N-gram | Low–Med | Med | Lightweight, easy |
| Suffix | Low–Med | Med | No extra model |
| Dynamic SD | High | > base | Fluctuating QPS / RL |
| Adaptive Verif. | High | > base | DSpark only |

## Common config keys (--speculative-config)

- `method` (string), `model` (draft/eagle/weights name),
  `num_speculative_tokens` (int; defaults to draft config).
- method-specific: `prompt_lookup_max/min` (ngram), `draft_model_runner_kwargs`,
  etc. See `vllm.config.SpeculativeConfig` and engine-args reference for the
  full set.

## Verification

- `--per-request-spec-decode-metrics summary|detailed` adds
  `metrics.speculative_decoding` (acceptance length, draft acceptance rate) —
  single-sequence (`n==1`) only.
- Aggregate Prometheus: `vllm:spec_decode_*` metrics.

## Notes

- `--speculative-model` (old) is removed; use `--speculative-config`.
- Gains are workload/model/hardware/sampling dependent — measure with
  `examples/features/speculative_decoding/spec_decode_offline.py` or the
  benchmark CLI.
