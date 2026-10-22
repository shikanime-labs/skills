# LWS (LeaderWorkerSet) + llama.cpp Router Mode

Verified reference for the shikanime inference refactor on nishir. The two
Strix Halo MS-S1 machines are `kushira` and `sashina`, labeled
`node.kubernetes.io/instance-type: minisforum-ms-s1` (set in
`machines/hosts/{kushira,sashina}/configuration.nix`).

## Architecture

```text
User → Envoy AI Gateway (apps/inference/) → AIGatewayRoute
       ↓
  Backend (inference / embedding) → Service → LeaderWorkerSet
    apps/llama-cpp/inference  (LLM router,  replicas: 2)
    apps/llama-cpp/embedding  (embedding router, replicas: 2)
       ↓
    leaderWorkerTemplate → 1 pod per Halo node (kushira + sashina)
    init container pulls GGUFs into emptyDir /models
    ConfigMap models-preset.ini mounted at /etc/llama-cpp
```

Router workloads live in `apps/llama-cpp/{inference,embedding}`. The gateway
plane (Gateway, EnvoyProxy, GatewayClass, AIGatewayRoute, Backend,
AIServiceBackend) stays in `apps/inference/base`. Do NOT merge the router
StatefulSets/LWS into `apps/inference/` — that was an explicit user
correction.

## Verified LWS spec (apps/llama-cpp/inference/base/lws.yaml)

- `replicas: 2`, default `size: 1` → two leader pods, NO `workerTemplate`.
- `nodeSelector: node.kubernetes.io/instance-type: minisforum-ms-s1`
  targets the two Halo nodes specifically. (Do NOT use
  `feature.node.kubernetes.io/amd-gpu: "true"` — that also matches the rpi5
  GPU nodes and would scatter replicas off the Halos.)
- `podAntiAffinity` (preferred, weight 100) on `kubernetes.io/hostname`
  spreads the two replicas one-per-node.
- Models: init container `python:3.12-slim` runs
  `pip install -q "huggingface_hub[cli]" && hf download <repo> --local-dir
  /models --include "*<QUANT>*"` for each model, into an `emptyDir` at `/models`
  (user chose emptyDir for raw IOPS over a shared PVC).
- Container args: `--host 0.0.0.0 --port 8080 --models-preset
/etc/llama-cpp/models-preset.ini --models-dir /models --models-max 2
--no-models-autoload -c 32768 --flash-attn on --cache-type-k q8_0
--cache-type-v q8_0 --gpu-layers 99 --no-mmap`. Embedding router adds
`--embeddings` and `--models-max 1`.
- VPA targetRef is the `LeaderWorkerSet` (apiVersion
  `leaderworkerset.x-k8s.io/v1`), not a StatefulSet.
- Flux healthCheck is `kind: LeaderWorkerSet` (not `StatefulSet`).

## LWS install (infrastructure/lws/)

```yaml
# infrastructure/lws/base/helmrepo.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: leaderworkerset
  namespace: flux-system
spec:
  url: oci://registry.k8s.io/lws/charts
  type: oci
  interval: 1h
```

```yaml
# infrastructure/lws/base/hr.yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: leaderworkerset
  namespace: flux-system
spec:
  chart:
    spec:
      chart: lws
      version: "0.10.0"
      sourceRef:
        kind: HelmRepository
        name: leaderworkerset
        namespace: flux-system
      interval: 1h
  interval: 10m
  releaseName: leaderworkerset
  targetNamespace: lws-system
```

Wire it as a cluster component `infrastructure-lws`
(`clusters/nishir/components/lws/{kustomization.yaml,ks.yaml}`) and add
`../../components/lws` to the nishir overlay `kustomization.yaml`
`components:` list. Router app Flux docs (`apps-inference`, `apps-embedding`)
`dependsOn: [infrastructure-lws, infrastructure-envoy, ...]`.

## Capacity table (AMD Strix Halo, 128GB RAM, best-fit unsloth quant)

| Model | GGUF | Quant | Size | Fits 128GB? | Local floor |
|-------|------|-------|------|-------------|-------------|
| DeepSeek-V4-Flash-0731 | unsloth/DeepSeek-V4-Flash-0731-GGUF | UD-Q3_K_M | ~116 GB | Yes | inference (p0) |
| GLM-5.3-Flash | unsloth/GLM-5.3-Flash-GGUF | UD-IQ3_XXS | ~98 GB | Yes | inference (zai→local→nous→openrouter) |
| Qwen3.8-Flash-Next | unsloth/Qwen3.8-Flash-Next-GGUF | UD-Q4_K_XL | ~79 GB | Yes | inference (p0) |
| Qwen3.8-27B | unsloth/Qwen3.8-27B-GGUF | UD-Q4_K_XL | ~18 GB | Yes | inference (p0) |
| Qwen3-Embedding-8B | unsloth/Qwen3-Embedding-8B-GGUF | UD-Q5_K_XL | ~5.4 GB | Yes | embedding (p0) |

All four LLMs share ONE node (sum ≈ 311 GB) — that is why the LLM router is
two replicas (one full set per Halo node), not a single pod with all models.
GLM-5.3-Flash previously had no local GGUF (llama.cpp glm5next PR #27754);
the user reversed that and now runs it locally via `UD-IQ3_XXS`. DeepSeek
`UD-Q3_K_M` (~116 GB) is the tightest fit — keep `--models-max 2` so KV
cache pressure stays bounded.

## models-preset.ini shape

```ini
[deepseek/deepseek-v4-flash-0731]
model = /models/DeepSeek-V4-Flash-0731-UD-Q3_K_M.gguf

[glm-5.3-flash]
model = /models/GLM-5.3-Flash-UD-IQ3_XXS.gguf

[qwen/qwen3.8-27b]
model = /models/Qwen3.8-27B-UD-Q4_K_XL.gguf

[qwen/qwen-flash]
model = /models/Qwen3.8-Flash-Next-UD-Q4_K_XL.gguf
```

Section names are the `modelNameOverride` values the gateway sends, so the
router resolves each request to the right local GGUF with no id rewrites.
