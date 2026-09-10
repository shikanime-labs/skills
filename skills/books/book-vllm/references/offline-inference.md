# Offline Inference (vLLM `LLM` class)

Source: <https://docs.vllm.ai/en/latest/serving/offline_inference/>

## Basic

```python
from vllm import LLM, SamplingParams
llm = LLM(model="meta-llm/Llama-3-8B-Instruct",
          tensor_parallel_size=2, gpu_memory_utilization=0.92,
          max_model_len=8192, dtype="auto")
sampling = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=256,
                          stop=["</s>","\n\n"])
outputs = llm.generate(["Hello, my name is"], sampling)
print(outputs[0].outputs[0].text)
```

- `LLM` kwargs == engine args (see references/engine-args.md). Eager path
  serializes multimodal preprocessing; `--renderer-num-workers` (default 1) only
  speeds the async server path.
- Default sampling params come from the model's HF `generation_config.json`;
  pass `generation_config="vllm"` to use vLLM defaults.

## Model types

- Generative (LLaMA, Qwen, DeepSeek): `llm.generate()`, `llm.chat()`.
- Pooling (bge-m3, Qwen3-Reranker): `llm.embed()`, `llm.classify()`,
  `llm.score()`, `llm.encode()`.

## API surface

Generative:

- `LLM.generate(prompts, sampling)` — completions.
- `LLM.chat(messages, sampling)` — chat responses.

Async queue (don't block):

- `LLM.enqueue`, `LLM.enqueue_chat`, `LLM.wait_for_completion`.

Pooling:

- `LLM.embed`, `LLM.classify`, `LLM.score`, `LLM.encode`.

Profiling (RL/dev):

- `LLM.start_profile(prefix?)`, `LLM.stop_profile`.

Sleep mode (CUDA/HIP):

- `LLM.sleep`, `LLM.wake_up` — sleep mode auto-enables cumem allocator.

Cache management:

- `LLM.reset_mm_cache`, `LLM.reset_prefix_cache`.

Metrics:

- `LLM.get_metrics()` — Prometheus snapshot.

Weight transfer (RL training):

- `LLM.init_weight_transfer_engine`, `LLM.start_weight_update`,
  `LLM.update_weights`, `LLM.finish_weight_update`, `LLM.update_weight_version`,
  `LLM.get_weight_version`.

Misc:

- `LLM.collective_rpc(callable)` — run on all workers.
- `LLM.apply_model(fn)` — apply fn to model in each worker (e.g. inspect
  `type(model)` to detect Transformers backend).

## Ray Data LLM API (large-scale)

`ray>=2.44.1` + `ray.data.llm`:

```python
from ray.data.llm import vLLMEngineProcessorConfig, build_llm_processor
config = vLLMEngineProcessorConfig(model_source="unsloth/Llama-3.2-1B-Instruct")
processor = build_llm_processor(config,
    preprocess=lambda row: {"messages":[...], "sampling_params":{...}},
    postprocess=lambda row: {"answer": row["generated_text"]})
ds = ray.data.from_items([...]); ds = processor(ds); ds.write_parquet("local:///tmp/")
```

Adds streaming, autoscaling, fault tolerance, TP/PP transparency across a Ray
cluster.

## Notes

- `SamplingParams`: `temperature`, `top_p`, `top_k`, `max_tokens`, `stop`,
  `logprobs`, `n`, `best_of`, `seed`, `min_tokens`, `repetition_penalty`.
- Output shape: `outputs[i].outputs[j].text` / `.token_ids`;
  `outputs[i].prompt`.
