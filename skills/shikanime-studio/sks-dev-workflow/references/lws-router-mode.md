# Llama.cpp router mode + LWS inference deployment

Reference for the shikanime inference stack. Loaded on demand from
`sks-dev-workflow` only when deploying or debugging the inference gateway on a
`machines`-class repo. Not part of the dev loop.

## Router mode

llama.cpp server supports **router mode** (no `-hf`/`-m` flag) for dynamic
multi-model loading from a directory. Each GGUF becomes a loadable model via the
`/models` REST API. Context window (`-c`) is shared across all loaded models.

```bash
# Single-model mode (current pattern)
llama-server -hf unsloth/Qwen3.8-Flash-Next-GGUF:UD-Q4_K_XL ...

# Router mode (multi-model, no model in args)
llama-server --models-dir /path/to/models --models-max 2 --models-ttl 300 -c 32000
```

Use router mode over separate StatefulSets when: few models, shared GPU, dynamic
load/unload; each model < ~80 GB so they fit together in VRAM; avoids N pods each
pinning a full model copy.

Router mode replaces per-model llama-cpp deployments but NOT the inference
AIGatewayRoute — the gateway still routes to the router's single Service IP.

## inference-models-preset.yaml ConfigMap

Kubernetes ConfigMap (`apiVersion: v1`) named `inference-models-preset` in the
`shikanime` namespace. Data key `models-preset.ini` (INI parsed by llama.cpp):

```ini
[section-name]
model = /models/model-file.gguf
```

Sections define loadable model names (used by `POST /models/load`). Mounted at
`/etc/llama-cpp/models-preset.ini`, referenced via
`--models-preset /etc/llama-cpp/models-preset.ini`.

## backend.yaml — remote providers + local floor

For the inference gateway, `apps/inference/base/backend.yaml` defines:

1. **Remote Backends** (one per provider): `kind: Backend`
   `gateway.envoyproxy.io/v1alpha1`
   - `spec.endpoints[].fqdn.hostname` — provider domain
   - `spec.tls.wellKnownCACertificates: System` — system CA bundle
   - `spec.tls.sni` — explicit SNI when Cloudflare rejects SNI-less handshakes
   - Must NOT reference a Kubernetes Service (CEL-blocked by ai-gateway)
2. **AIServiceBackend** (per provider, API-key auth): `kind: AIServiceBackend`
   `aigateway.envoyproxy.io/v1beta1`
   - `spec.type: APIKey`
   - `spec.targetRefs[]` — points back at the Backend name
   - `spec.apiKey.secretRef` — Secret containing `apiKey = ENC[...]`
   - `secretGenerator` must NOT hash the secret name (BSP lacks nameReference
     rewrites), OR set `disableNameSuffixHash: true`
3. **Local floor Backend**: `kind: Backend` at the router pod's headless Service
   - `spec.endpoints[].fqdn.hostname`: `<service>.shikanime.svc.cluster.local`
   - `spec.endpoints[].port`: llama.cpp HTTP port (8080)

Route rules reference `backendRefs` by Backend name, NOT AIServiceBackend name.
Priority 0 = local floor (never 429'd); priority 1+ = remote tiers (nous,
openrouter, zai).

## LWS + router mode — 2-node capacity

With LWS (`replicas: 2`) both replicas are **identical** — same
`leaderWorkerTemplate`, same ConfigMap mount, same `--models-preset` /
`--models-dir`. Both pods load ALL models simultaneously → capacity constraint:
total model set must fit in one node's RAM.

```text
Capacity math per node (128GB RAM, ~115GB usable after GPU reservation):
  GLM-5.3-Flash  ~93 GB  fits alone
  DeepSeek-V4-Flash ~87 GB  fits alone
  Qwen3-8B        ~80 GB  fits alone
  Qwen3.8-27B     ~55 GB  fits alone
  Qwen3-Embedding-8B ~6 GB fits alone
  Total (all 5)   ~321 GB exceeds 128 GB
```

Options for both nodes' capacity:

1. **Single model** — trim preset to one model that fits (~87-93GB), 2 LWS
   replicas for redundancy/throughput.
2. **Per-node preset differentiation** — node-specific kustomize overlays with
   different ConfigMaps; LWS affinity places each replica on its target node.
3. **Reduce preset to compatible pairs** — DeepSeek+Embedding (93GB) or
   GLM-5.3-Flash+Embedding (99GB) fits in 128GB, but loses models.

`--models-dir` is a local path (not shared storage); each pod copies models from
the ConfigMap/volume into its own local `/models`.

## Inference router layout (verified on nishir)

Router workloads live under `apps/llama-cpp/{inference,embedding}` (LLM router +
embedding router), NOT under `apps/inference/` (gateway-plane objects only:
Gateway, EnvoyProxy, GatewayClass, AIGatewayRoute, Backend, AIServiceBackend).
User corrected this naming; do not merge router StatefulSets/LWS into
`apps/inference/`.

Verified LWS shape:

- `replicas: 2` with default `size: 1` → two leader pods, no worker template.
- `nodeSelector: node.kubernetes.io/instance-type: minisforum-ms-s1` pins both
  pods to the two Strix Halo MS-S1 nodes (kushira/sashina);
  `podAntiAffinity` on `kubernetes.io/hostname` spreads one-per-node.
- Models pulled once by an **init container** (`python:3.12-slim` running
  `pip install huggingface_hub[cli] && hf download ...`) into an **emptyDir** at
  `/models` — emptyDir chosen for raw IOPS over a shared PVC. Each pod re-pulls
  on restart; both replicas identical, no RWX needed.
- LWS installed via `infrastructure/lws/` (OCI
  `oci://registry.k8s.io/lws/charts/lws` v0.10.0), reconciled as cluster
  component `infrastructure-lws`; router app Flux docs depend on it.

## aiservicebackend.yaml — pre-existing remote providers

`zai` and `openrouter` AIServiceBackends (free-tier remote access) were previously
in `apps/inference/base/aiservicebackend.yaml` and moved into `backend.yaml`
during the GLM-5.3-Flash migration. When adding a new remote provider, check
whether it already exists there to avoid duplicate definitions.
