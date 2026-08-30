# Speculative Decoding (docs/speculative.md)

Distilled structure. Speculative decoding drafts several tokens, then verifies
them in one batch with the target model — faster when drafts are often correct.
Supported in `llama-server` (and `llama-cli`); a draft implementation can be
mixed with a draftless one (draftless wins).

## Implementations (`--spec-type`)

| Type | Draft source | Notes |
|---|---|---|
| `none` | - | default |
| `draft-simple` | small draft model | most common approach |
| `draft-eagle3` | EAGLE-3 1-layer transformer reading target hidden states | higher acceptance; shares target tokenizer; reduced draft vocab via `d2t` |
| `draft-dflash` | block-diffusion draft, whole block per step | small, GPU-friendly |
| `draft-dspark` | DFlash + semi-autoregressive Markov head | Qwen3 backbone only (others planned) |
| `draft-mtp` | MTP heads from the main model | |
| `ngram-cache` | n-gram statistics | external stats loadable |
| `ngram-simple` | last matching n-gram in history | no extra model; minimal overhead |
| `ngram-map-k` | n-gram key → m-gram, min hits | hash-map of n-grams in window |
| `ngram-map-k4v` | key → up to 4 m-gram values (experimental) | |
| `ngram-mod` | LCG n-gram hasher, shared pool (~16 MB) | variable draft length; cross-slot sharing |

`--spec-default` enables `ngram-mod`. Comma-separate multiple types, e.g.
`--spec-type ngram-mod,ngram-map-k4v`.

## Draft-model workflow (EAGLE-3 example)

```bash
python convert_hf_to_gguf.py AngelSlim/Qwen3-4B_eagle3 \
    --target-model-dir Qwen/Qwen3-4B --outtype bf16 --outfile Qwen3-4B-eagle3.gguf
llama-server -m Qwen3-4B.gguf -md Qwen3-4B-eagle3.gguf --spec-type draft-eagle3
```

DFlash / DSpark convert the same way with `--target-model-dir`; launch with
`--spec-type draft-dflash|draft-dspark --spec-draft-n-max N -fa on --jinja`.
`--spec-draft-n-max` is clamped to the draft's trained block size. DSpark
`--spec-draft-conf-min P` truncates a block at first position below confidence P.

## Core CLI options

```text
--spec-type TYPE                 none|draft-simple|draft-eagle3|draft-dflash|
                                draft-dspark|draft-mtp|ngram-cache|ngram-simple|
                                ngram-map-k|ngram-map-k4v|ngram-mod  (env LLAMA_ARG_SPEC_TYPE)
--spec-default                   enable ngram-mod
--spec-draft-model, -md          draft model path
--spec-draft-hf, -hfd            HuggingFace repo for draft (env LLAMA_ARG_SPEC_DRAFT_HF_REPO)
--spec-draft-n-max               max draft tokens (default 3)
--spec-draft-n-min               min draft tokens (default 0)
--spec-draft-p-split             split probability (default 0.10)
--spec-draft-p-min               min greedy probability (default 0.00)
--spec-draft-ngl, -ngld          draft model GPU layers (auto|all|N)
--spec-draft-device, -devd       devices for draft offload
```

Full CPU-scheduling and KV-override flags exist (`--spec-draft-threads`,
`--spec-draft-type-k/-v`, etc.) — see docs/speculative.md.

## n-gram tuning

- `ngram-simple`: `--spec-ngram-simple-size-n` (lookup, def 12),
  `--spec-ngram-simple-size-m` (draft, def 48), `--spec-ngram-simple-min-hits` (def 1).
- `ngram-map-k`: `--spec-ngram-map-k-size-n` (12), `-size-m` (48), `-min-hits` (1).
- `ngram-map-k4v`: same shape, `-min-hits` default 1.
- `ngram-mod`: `--spec-ngram-mod-n-match`, `--spec-ngram-mod-n-min`,
  `--spec-ngram-mod-n-max`. Small `n` not recommended; MoEs need long drafts.

## Sampling & benchmarking

- `--backend-sampling` runs target samplers on the backend; draft uses it by
  default and can be toggled with `--spec-draft-backend-sampling` /
  `--no-spec-draft-backend-sampling`. Tensor split mode doesn't support backend
  sampling. Greedy sampling for exact-output matching.
- Synthetic acceptance for benchmarks (output is NOT valid model output):
  `--spec-synth-rates P0,P1,...` or `--spec-synth-len L`.
- SPEED-Bench client (`tools/server/bench/speed-bench`) compares baseline vs
  speculative runs against a live server.

## Statistics

Per-implementation lines report `#calls(b,g,a)`, `#gen drafts`, `#acc drafts`,
`#gen tokens`, `#acc tokens`, and `dur(b,g,a)`. `draft acceptance rate` =
accepted / generated.
