# Distributed Serving (vLLM)

Source: <https://docs.vllm.ai/en/latest/configuration/engine_args/>
(ParallelConfig) + serving docs.

## Parallelism axes

- **Tensor Parallel (TP)** `-tp`/`--tensor-parallel-size`: shard each layer
  across GPUs. Powers of two (or = GPU count) for best results. Use `mp` backend
  when `tp*pp <= num_gpus`.
- **Pipeline Parallel (PP)** `-pp`/`--pipeline-parallel-size`: split layers into
  stages.
- **Data Parallel (DP)** `-dp`/`--data-parallel-size`: replicate model; MoE
  layers sharded by `tp*pcp*dp`. Non-MoE: launch independent vLLM instances
  instead.
- **Expert Parallel (EP)** `-ep`/`--enable-expert-parallel`: replace TP for MoE
  experts. `--enable-eplb` balances experts; `--expert-placement-strategy
  linear|round_robin`.
- **Context Parallel**: `--prefill-context-parallel-size`/`-pcp` (shards prefill
  compute, grows world size), `--decode-context-parallel-size`/`-dcp` (shards
  decode KV, reuses TP ranks).

## Backends & multi-node

- `--distributed-executor-backend` (`mp|ray|uni|external_launcher`). `mp` auto
  when `tp*pp <= gpus`; Ray required for TPU and multi-node.
- Multi-node (mp): `--nnodes`/`-n`, `--node-rank`/`-r`, `--master-addr`
  (127.0.0.1), `--master-port` (29501).
- `--device-ids "2,3,5,7"` selects physical GPUs without CUDA_VISIBLE_DEVICES
  (preserves topology for NIC affinity / DeepGEMM). No effect under Ray (use
  placement groups).
- `--distributed-timeout-seconds` raise for slow multi-node downloads (NCCL
  default 600s).

## Data-parallel load balancing (online serving)

- Default (internal LB): single instance spans DP ranks.
- `--data-parallel-hybrid-lb`/`-dph`: per-node AsyncLLM + API server, external
  LB across nodes.
- `--data-parallel-external-lb`/`-dpe`: one-pod-per-rank wide-EP (K8s); set
  implicitly by `--data-parallel-rank`. MoE only.
- `--data-parallel-multi-port-external-lb`/`-dpm`: node-local supervisor, one
  API server per local DP rank.

## MoE specifics

- `--all2all-backend`:
  `deepep_high_throughput|deepep_low_latency|flashinfer_nvlink_*|nixl_ep|mori_*|naive|...`
  (default `allgather_reducescatter`).
- `--enable-ep-weight-filter`: each rank reads only its expert shard (cuts I/O
  for DeepSeek/Mixtral/Kimi). No effect on 3D fused (GPT-OSS) or non-MoE.
- `--enable-elastic-ep`: stateless NCCL groups for DP/EP.

## Memory offload (fit bigger models)

- `--cpu-offload-gb` (per GPU): UVA zero-copy; treat as virtual GPU expansion
  (e.g. 24GB GPU + 10 → ~34GB). Needs fast CPU↔GPU link.
- `--offload-group-size`/`--offload-num-in-group`/`--offload-prefetch-step`:
  async grouped layer offload.
- `--kv-offloading-size` + `--kv-offloading-backend native|lmcache`: KV to CPU.

## Fault tolerance

- `--enable-fault-tolerance` + `--fault-tolerance-config`
  (`FaultToleranceConfig(engine_recovery_timeout_sec=120)`) — e.g. scale down
  faulted DP cores.

## Notes

- `gpu_memory_utilization` is per-instance; multiple instances on one GPU each
  apply their own fraction.
- For disaggregated prefill/decode/encode, see KV transfer
  (`--kv-transfer-config`) and encoder cache (`--ec-transfer-config`) in engine
  args.
