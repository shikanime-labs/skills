---
name: envoy-ai-gateway
description:
  "Use when deploying or troubleshooting Envoy AI Gateway."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - envoy
      - ai-gateway
      - gateway-api
      - flux
      - kustomize
      - shikanime-labs
    related_skills:
      - verify-k8s-crds
      - sks-investigate
      - sks-dev-workflow
      - book-llama-cpp-inference
platforms:
  - linux
  - macos
---

## Preferences encoded from session history

- **Single-file Backends.** Backends and AIServiceBackends live in
  `backend.yaml` only. Do not split them into `backend-<provider>.yaml`
  files. This is the user's preference; splitting one CRD per file adds
  diff noise for no operational gain. The kustomization stays
  `[aiservicebackend, backend, backendsecuritypolicy, envoyproxy, gateway,
  gatewayclass, route]`. A dedicated `route-<name>.yaml` is OPTIONAL — add one
  only when a model needs an isolated, auditable failover path (e.g. a paid
  subscription that must be the p0 floor); it must then also be listed in the
  kustomization `resources:`. In this repo the GLM subscription route was
  prototyped as `route-zai.yaml` then MERGED BACK into `route.yaml` (single
  `AIGatewayRoute` convention won), so `route.yaml` currently carries the
  `z-ai/glm-5.3-flash` rule and no `route-zai.yaml` exists.
- **Inline-merge addon values.** When adding Envoy AI Gateway "Additional
  Features" (InferencePool, Rate Limiting) to the `envoy` gateway-helm
  HelmRelease, merge the keys inline into `spec.values.config.envoyGateway` —
  do NOT create a separate `envoy-gateway-values-addon.yaml` nor a `valuesFrom`
  ConfigMap. The user rejected the indirection twice this session ("merge
  configs", "don't add separate file"). The upstream extra `-f
  envoy-gateway-values-addon.yaml` is faithfully reproduced by inlining the
  same keys; a `valuesFrom` ConfigMap would also need a `nameReference` rewrite
  in every overlay that deploys the HelmRelease or the hashed name won't
  resolve.

# Envoy AI Gateway ops

Fleet knowledge for the inference gateway: `apps/llama-cpp/` (AIGatewayRoute,
Backend, AIServiceBackend, BackendSecurityPolicy) + `infrastructure/envoy/`
(gateway-helm + ai-gateway-helm HelmReleases). All facts below were verified
live on nishir; trust them over upstream docs when they conflict.

## Tailnet endpoint topology (verified live)

- **Gateway entrypoint is `inference.taila659a.ts.net` (canonical).** The
  `inference` Gateway (ns `shikanime`) is Programmed with addresses
  `100.75.85.39` AND `inference.taila659a.ts.net`, serving HTTP:80 and
  HTTPS:443 (mTLS). The Envoy data-plane Service is named `inference` in ns
  `envoy-system` (ports `http-80`→10080, `https-443`→10443). Probe from a
  workstation: `kubectl port-forward -n envoy-system svc/inference 8080:80`
  then `curl -X POST http://localhost:8080/v1/chat/completions -H
  "x-ai-eg-model: <model>" -d '{"model":"<model>","messages":[...]}'`.
  (`ai.taila659a.ts.net` is a SEPARATE aperture egress layer, not the gateway —
  see the bullets below.)
- Triage of the universal empty-body 500 (extension-unwired vs in-processor
  routing 500) is in `references/extproc-500-triage.md`.
- `GET https://ai.taila659a.ts.net/v1/models` works unauthenticated (full catalog).
- `POST /v1/chat/completions` on `ai` requires an aperture `tags` array + user
  tag that raw curl could not satisfy (`missing tags` → `missing user tag`). The
  working client is the `custom:aperture-openai` provider in `~/.hermes/config.yaml`
  (Bearer `sk-lm-<id>:<secret>`). Do NOT hand-guess the tag grammar — reuse the
  Hermes client or read the proxy config.
- Model selection to the Envoy gateway is via the **`x-ai-eg-model` header**
  (`AIGatewayRoute` matches on it), failover local → nous → openrouter.
  Reproduction + port-scan detail in `references/tailnet-endpoints.md`.

## mTLS blocks non-client-cert clients (the inference 502)

The `inference` Gateway `https/443` listener is **mTLS**, not plain TLS terminate:

```yaml
spec:
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls:
        mode: Terminate
        certificateRefs: [{ name: inference-tls }]
        options: { "gateway.envoyproxy.io/mtls": "true" }   # <-- client-cert REQUIRED
```

`inference-tls` carries `ca.crt` (client CA). Clients WITHOUT a CA-signed
client cert get a **TLS handshake reject → Envoy returns HTTP 502** (no access-log
upstream, the failure is pre-route). This is the root cause of Open WebUI
provider-test errors like `tencent/hy3:free via OpenAI Chat → HTTP 502 Bad
Gateway` — NOT a backend/route defect.

Verify the mTLS hypothesis in two curls from a workstation that has the certs:
- WITH client cert → `HTTP 200` (`--cert /tmp/inf-client.crt --key /tmp/inf-client.key --cacert /tmp/inf-ca.crt`).
- WITHOUT → `HTTP 000`/`502`. That 000 = handshake abort, the gateway's 502 to Open WebUI.

#### externalDNS worked — mTLS was the gate (the "DNS set the right IP but it didn't work" case)

When a hostname resolves and routes correctly but every ordinary client fails
at the TLS layer, the cause is NOT DNS. externalDNS can publish
`inference.shikanime.studio → 100.103.240.115` correctly while the
`ClientTrafficPolicy/inference` still enforces `tls.clientValidation` — only
clients presenting a CA-signed client cert get through; everyone else gets a
handshake reset. Verified this session: with a client cert → `200`; without →
`000`; after removing `clientValidation` live → `200` from both
`inference.shikanime.studio` and `inference.taila659a.ts.net`.

The two-curl discriminator localizes it in seconds:
- `curl -k --cert /tmp/inf-client.crt --key /tmp/inf-client.key --cacert /tmp/inf-ca.crt https://<host>/v1/models` → `200`
- `curl -k https://<host>/v1/models` → `000` (handshake abort) ⇒ mTLS gate, not DNS.

Caveat after removing `clientValidation`: the listener still serves the
internal `inference-tls` cert (nishir CA, SANs include `inference.taila659a.ts.net`
but NOT `inference.shikanime.studio`), so strict clients still need `-k`
until a trusted LE cert with the `.studio` SAN is in place.

#### Live `kubectl patch` is REVERTED on the next `flux reconcile` (proven this session)

Flux re-applies the **tracked revision (`main`)**, not your working tree. A
live `kubectl patch clienttrafficpolicy inference --type=json -p='[{"op":"remove","path":"/spec/tls/clientValidation"}]'`
returns `200` immediately, but the moment someone runs
`flux reconcile kustomization apps-llama-cpp` (or any reconcile that applies
`main`, which lacked the patch), mTLS returns and the endpoint goes `000`
again. This bit the session: fix applied → verified 200 → reconcile → 000.

RULE: never treat a live `kubectl` change in this repo as durable. To make a
fix survive reconcile:
1. Edit the source overlay so `kustomize build <overlay>` renders the field
   **absent** (verify: `kustomize build apps/llama-cpp/overlays/nishir-tailnet | grep -c clientValidation` → `0`).
2. Commit to a PR branch and push (`jj commit <files> -m ...` then
   `jj git push -b <branch>`). Flux must apply YOUR branch, not `main`, for the
   change to stick.
3. Then (and only then) can you apply the same `kubectl patch` live for instant
   relief — it will persist until the branch merges and Flux applies it.

#### Before promising a trusted LE cert: verify the Cloudflare DNS-01 token

A `Certificate` pointing at a Let's Encrypt issuer stays `Ready=False /
pending` forever if the DNS-01 solver can't authenticate. Verify the token
BEFORE wiring a cert that the listener depends on — otherwise pointing the
`https` listener's `certificateRefs` at a never-created Secret breaks the
endpoint (`000`):

```bash
TOK=$(kubectl --context <ctx> -n cert-manager-trust get secret cloudflare-api-token \
  -o jsonpath='{.data.apiToken}' | base64 -d)
curl -s -H "Authorization: Bearer $TOK" \
  -H "Content-Type: application/json" \
  https://api.cloudflare.com/client/v4/user/tokens/verify
# → {"success":true,...}  OR  {"success":false,"errors":[{"code":1000,"message":"Invalid API Token"}]}
```

If that returns `Invalid API Token`, the LE cert will not issue — keep the
existing internal-CA cert (with `-k`) and treat the trusted cert as a separate
follow-up gated on a valid token. Do NOT merge a PR that points the listener at
an LE cert that cannot issue.

Full discriminator + reconciliation recipe: `references/mtls-vs-dns-diagnosis.md`.

### Open WebUI / Tailscale aperture topology (verified live)

- `ai.taila659a.ts.net` is **Open WebUI** (302→`/chat`, CSP, admin at
  `/admin/settings/providers`). It is NOT the gateway.
- It is backed by `shikanime/ai` `ExternalName` →
  `ts-ai-8c9g5.tailscale-system.svc.cluster.local:443` (a Tailscale `ts-`
  Service). The `nishir-ai-egress` ProxyGroup forwards only the `ai` mapping
  (`tailnetTarget.fqdn: ai.taila659a.ts.net`, matchPort 10405→targetPort 443).
  **There is NO `inference` egress mapping** — Open WebUI has no route to
  `inference.*` at all, and even if it did, mTLS would 502 it.
- Open WebUI cannot present a client cert → its provider calls to
  `https://inference.taila659a.ts.net/v1/...` fail at TLS → 502.

Fix options (present to user; all need a durable PR against `manifests`):
- **A — client cert into Open WebUI.** Issue a cert from the `inference-tls`
  client CA; mount it in the Open WebUI deployment as its TLS client identity.
  No gateway change. Depends on Open WebUI supporting mTLS client certs.
- **B — second non-mTLS listener/host on the `inference` Gateway** (plain
  HTTPS Terminate, no `mtls: "true"`), gated so only the `ai` tailnet node
  reaches it. Cleanest if Open WebUI can't do client certs.
- **C — forwarder shim.** A small Deployment that does mTLS→gateway and is
  published via the ProxyGroup (`inference-openwebui.taila659a.ts.net:10407→443`,
  no client cert). More moving parts than A/B.

### Provider wiring gap: Tencent (and unknown models via catch-all)

`tencent/hy3:free` was NOT un-wired — the default catch-all `.*` rule already
routes unknown models to `nous` → `openrouter`, so a model like `tencent/hy3`
reaches OpenRouter through the existing `openrouter` AIServiceBackend. The
catch-all's REAL defect (found + fixed this session, PR #1917): it carried
`modelNameOverride: ${header.x-ai-eg-model}` and **ai-gateway v1.1.0 does not
evaluate that header variable** — it ships the literal string
`${header.x-ai-eg-model}` upstream, so OpenRouter 404s with "Model
'${header.x-ai-eg-model}' not found". Drop the override so the request body
`model` is forwarded unchanged (see the PITFALL under Route structure below).

A separate, upstream-side fact: **`tencent/hy3:free` is RETIRED on
OpenRouter** (returns `404 "This model is unavailable for free"`); the paid
`tencent/hy3` works and routes fine through the gateway once the override bug
is fixed. If you need a free model through this gateway, use
`qwen/qwen3.8-flash` (runs on the local floor) or another free OpenRouter slug.

## Version pairing (verified)

- ai-gateway-helm **1.1.0** pairs with gateway-helm **v1.8.3+** (compatibility
  matrix: ai-gateway v1.1.x needs EG v1.8.1+).
- gateway-helm version floor: cluster Gateway API CRDs are bundle v1.5.0 and
  the `safe-upgrades.gateway.networking.k8s.io` ValidatingAdmissionPolicy
  denies charts shipping an older bundle. v1.6.x/v1.7.x ship v1.4.1 →
  uninstallable under Flux; **v1.8.3 is the floor** (bundles v1.5.1).
- `HelmRepository` with `oci://` URL REQUIRES `type: oci` — Flux otherwise
  fails "URLInvalid: 'oci' URL scheme cannot be used with 'default'".
- Multi-doc `hr.yaml`: every doc after the first needs its own
  `apiVersion: helm.toolkit.fluxcd.io/v2` — kustomize renders it fine,
  kubectl rejects missing apiVersion.

## Backend API is opt-in (the #1 gotcha)

EG v1.8 disables the `Backend` (gateway.envoyproxy.io) API by default. Without
`extensionApis.enableBackend: true`, EG logs
`setting 500 direct response in routes: Backend is disabled in Envoy Gateway
configuration` and EVERY route 500s with `upstream_cluster: null`.

```yaml
# gateway-helm values in infrastructure/envoy/base/hr.yaml
values:
  config:
    envoyGateway:
      extensionApis:
        enableBackend: true
```

## Gateway-helm addon values (Envoy AI Gateway Additional Features)

Upstream's prerequisites page lists "Additional Features" addon value files:
- Rate Limiting: `examples/token_ratelimit/envoy-gateway-values-addon.yaml`
- InferencePool: `examples/inference-pool/envoy-gateway-values-addon.yaml`

These are extra `-f` values files at Helm install time. In Flux, reproduce them by
**merging the keys inline** into the `envoy` HelmRelease
(`infrastructure/envoy-gateway/base/hr.yaml` in this fleet) under
`spec.values.config.envoyGateway` — NOT a separate file and NOT a `valuesFrom`
ConfigMap (see the preference above).

```yaml
# infrastructure/envoy-gateway/base/hr.yaml — spec.values.config.envoyGateway
extensionManager:
  backendResources:
    - group: inference.networking.k8s.io
      kind: InferencePool
      version: v1
provider:
  kubernetes:
    rateLimitDeployment:
      patch:
        type: StrategicMerge
        value:
          spec:
            template:
              spec:
                containers:
                  - imagePullPolicy: IfNotPresent
                    name: envoy-ratelimit
                    image: docker.io/envoyproxy/ratelimit:60d8e81b
rateLimit:
  backend:
    type: Redis
    redis:
      url: redis.redis-system.svc.cluster.local:6379
```

Notes:
- **InferencePool** alone needs no new dependency — just `backendResources`.
- **Rate Limiting** is INERT until (a) a `RateLimitPolicy` selects it and (b) a
  Redis backend exists at the configured `url`. This fleet does NOT deploy Redis
  under `redis-system` — wiring it is a separate unit. Flag the prerequisite; do
  not silently ship a dead config.
- The `envoy-ratelimit` image pin (`docker.io/envoyproxy/ratelimit:60d8e81b`) is
  the upstream example tag; confirm it tracks the ai-gateway release you pair.

## AIServiceBackend constraints

- `backendRef` MUST be a gateway.envoyproxy.io `Backend` resource. Kubernetes
  Service refs are CEL-blocked: "BackendRef must be a Backend resource of
  Envoy Gateway" (ai-gateway #902, #1328). Do not try Service refs.
- `schema.prefix` is the upstream API path: OpenAI chat = `${prefix}/chat/completions`.
  OpenRouter needs `api/v1`; the default `v1` hits its web root → HTML 404.
  z.ai: the CODING-PLAN key works on `api/v1` (base `https://api.z.ai/api/v1`).
  `api/coding/paas/v4` and `api/paas/v4` both REJECT the coding key with
  401 "token expired or incorrect" — and z.ai may return HTTP 200 with a
  JSON body `{"code":401,"msg":"token expired or incorrect"}` instead of a
  real 401, so check the body not just the status. A valid coding key
  returns `model_access_denied` (code 1214, "modelCode does not exist" / not
  granted on plan) for `glm-5.3-flash` when the model is NOT entitled on the
  plan — that is an ENTITLEMENT blocker, NOT a manifest-wiring defect (the
  manifest cannot fix it; grant the model on the Z.ai plan or drop the route).
- `BackendSecurityPolicy` `targetRefs` point at the **AIServiceBackend name**
  (e.g. `openrouter`), NOT the Secret name. Mismatch → controller logs
  "Targeted AIServiceBackend not found"; the API key is never attached and
  routes still proxy (upstream 401/500).
- Secret data key must be literally `apiKey` (no key selector exists in the BSP).
- **kustomize secretGenerator hashing + BSP secretRef**: in this repo the
  overlay `namereference.yaml` DOES rewrite `BackendSecurityPolicy.spec.apiKey.
  secretRef` to the hashed `inference-nous-<hash>` name (verified live: the
  `nous-key` BSP `secretRef` was `inference-nous-fk6chd6ddt`). So a hashed
  secret name is the INTENDED state, not a drift bug. If a BSP points at a
  missing/stale hashed secret, reconcile the `apps-llama-cpp` Kustomization —
  do NOT assume `disableNameSuffixHash` is needed. (Caveat: after a key
  rotation, ai-gateway v1.1.0 can leave the projected credential Secret
  `inference-shikanime-<hash>` stale so one backend's ext-proc injects the
  pre-rotation (revoked) key while an identical BSP→secret pattern works for
  another backend — root cause and triage in `references/credential-401-triage.md`.)

## TLS upstreams

- Cloudflare rejects SNI-less ClientHellos (`SSLV3_ALERT_HANDSHAKE_FAILURE`).
  EG does NOT populate SNI from the Backend fqdn — set `tls.sni` explicitly:
  ```yaml
  spec:
    endpoints: [{ fqdn: { hostname: openrouter.ai, port: 443 } }]
    tls:
      wellKnownCACertificates: System
      sni: openrouter.ai
  ```
- Verify the SNI theory: `curl -k https://<ip>/` (no SNI) reproduces the exact
  envoy alert; `curl --resolve host:443:<ip> https://host/` succeeds.

### Models list (live, verified on nishir)

All target models run on ONE **unified** local floor: a single LeaderWorkerSet
`router` in `apps/llama-cpp/` (see the `book-llama-cpp-inference` skill). The
router holds all models in one llama.cpp process under a 120 Gi ceiling
(`--models-max 5` + `--embeddings`), so llama.cpp LRU-evicts across LLM + embed
instead of holding two fixed-budget pods. (The old split — `inference` LWS 120
Gi + `embedding` LWS 24 Gi = 144 Gi/node — could NOT co-schedule on a 128 Gi
Halo node.) Best-fit unsloth quants per 128 GB Halo node:

- `qwen/qwen-flash` — Qwen3.8-Flash-Next-GGUF (`UD-Q4_K_XL`, ~79 GB, local first via LWS)
- `qwen/qwen3.8-27b` — Qwen3.8-27B-GGUF (`UD-Q4_K_XL`, ~18 GB, local first via LWS)
- `deepseek/deepseek-v4-flash-0731` — DeepSeek-V4-Flash-0731-GGUF (`UD-Q3_K_M`, ~116 GB, local first via LWS)
- `glm-5.3-flash` → logical id `z-ai/glm-5.3-flash` — GLM-5.3-Flash-GGUF (`UD-IQ3_XXS`, ~98 GB, local first via LWS; previously remote-only, now local)
- `embeddings/qwen-embed` — Qwen3-Embedding-8B-GGUF (`UD-Q5_K_XL`, ~5.4 GB, local first via the unified `router`)
- `z-ai/glm-4.7` — removed from all routes; not registered.

DeepSeek `UD-Q3_K_M` (~116 GB) replaced the earlier "155 GB exceeds VRAM,
local floor removed" assessment — it fits a 128 GB Halo node at the tight end.
GLM-5.3-Flash `UD-IQ3_XXS` replaced the earlier "no local GGUF (PR #27754
unmerged)" assessment — the user chose to run it locally. GLM's route key is
`z-ai/glm-5.3-flash` (NOT `glm-5.3-flash`) — z.ai must receive the
`z-ai/` namespaced id; the local `router` floor also keys on it.

### Adding new local-floor models

Prefer unsloth dynamic quants when available — they match or beat the
original GGUF at smaller sizes. LWS sharding: one `router` LWS
`replicas: 2`, each replica a full model set on its own Halo node
(kushira/sashina) via nodeSelector + podAntiAffinity (emptyDir models,
init-container pull); no RWX needed.

### Route structure

The gateway uses `AIGatewayRoute` resources (`apps/llama-cpp/base/route.yaml`
+ optional `route-<name>.yaml`) with match rules on the `x-ai-eg-model` header.
Failover is explicit by-priority: highest priority (first in the list) is tried
first; next priority is elevated if the upstream returns non-200.

#### Multiple AIGatewayRoutes on one Gateway

Envoy AI Gateway MERGES all `AIGatewayRoute` resources that share a
`parentRefs` Gateway — "split rules across multiple AIGatewayRoute resources"
is the documented pattern. A second route does NOT require a second Gateway.
Use a dedicated route object when a model needs an isolated, auditable
failover path (e.g. a paid provider subscription that must be the p0 floor).
Concrete example: a standalone `AIGatewayRoute` named `zai`, parented to the
same `inference` Gateway, carrying only the `z-ai/glm-5.3-flash` rule with
`zai (p0) → router (p1) → nous (p2) → openrouter (p3)`. (This repo's GLM rule
was prototyped this way as `route-zai.yaml`, then merged back into `route.yaml`
— the pattern is identical; only the file location differs.)

PITFALL: do NOT copy a header match into both routes — two `AIGatewayRoute`s
on the same Gateway must not match the same `x-ai-eg-model` value, or the
merge is ambiguous. MOVE the rule out of `route.yaml` into the dedicated
route (delete it from the default), as done for GLM.

### Adding a new AIGatewayRoute: parentRef patch pattern

To add a new AIGatewayRoute that binds to the inference Gateway, create the
route in the app base and add a JSON6902 `parentRefs` patch in each overlay's
`kustomization.yaml` `patches:` block (inline, with a `target:` matching the
new route's name + group/version/kind):

```yaml
# apps/llama-cpp/overlays/nishir/kustomization.yaml
patches:
  - patch: |-
      - op: add
        path: /spec/parentRefs
        value:
          - name: inference
            kind: Gateway
            group: gateway.networking.k8s.io
    target:
      name: shikanime-forge        # AIGatewayRoute metadata.name
      version: v1beta1
      group: aigateway.envoyproxy.io
      kind: AIGatewayRoute
```

The `target:` MUST match the exact identity triple (name, group, version,
kind) — a mismatch is a silent no-op (the patch builds green but never
applies; see "target misses match SILENTLY" in the kustomize skill). Verify
the rendered route has `parentRefs` pointing at the `inference` Gateway.

Local floor = ONE `router` Backend (`router.shikanime.svc.cluster.local:8080`,
the unified llama.cpp LWS in `apps/llama-cpp/` serving LLM + embeddings). Remote =
`nous`, `openrouter`, `zai` (each with optional `AIServiceBackend` for
API-key auth). Each provider gets its own `AIServiceBackend` so API keys are
isolated per-provider.

Verified route table (priority order, lower number = tried first):

| x-ai-eg-model header | Backend path |
|---|---|
| `qwen/qwen-flash` | router (p0) → nous (p1) → openrouter (p2) |
| `qwen/qwen3.8-27b` | router (p0) → nous (p1) → openrouter (p2) |
| `deepseek/deepseek-v4-flash-0731` | router (p0) → nous (p1) → openrouter (p2) |
| `z-ai/glm-5.3-flash` | zai (p0) → router (p1) → nous (p2) → openrouter (p3) — in `route.yaml` (was prototyped as a dedicated `AIGatewayRoute/zai`, then merged in) |
| `embeddings/qwen-embed` | router (p0) → nous (p1) → openrouter (p2) |
| `shikanime/atlas` | nous (p0, `text-embedding-3-small`) → llama-cpp (p1, `qwen/qwen3-embedding-8b`) → openrouter (p2, `text-embedding-3-small`) |
| `shikanime/forge` | z-ai (p0) → llama-cpp (p1) → nous (p2) → openrouter (p3) — all `modelNameOverride: z-ai/glm-5.3-flash` |
| `shikanime/scribe` | llama-cpp (p0, `poolside/laguna-s-free`) → llama-cpp (p1, `poolside/laguna-xs-free`) → openrouter (p2, `stepfun/step-3.7-flash:free`) |
| `.*` (default catch-all, RegularExpression) | nous (p0) → openrouter (p1) |

The **default catch-all** (`type: RegularExpression`, `value: ".*"`) routes
generic models that have no local floor straight to the remote pool
(`nous` → `openrouter`) **without** a `modelNameOverride` — the body `model`
passes through unchanged. Routing `tencent/hy3` this way proved the path works
end-to-end after the override was removed. GLM-5.3-Flash uses `zai` first
(coding-plan key) then falls back to the local floor — that ordering lets GLM
stay on-cluster when zai is at quota.

PITFALL — `modelNameOverride` does NOT expand substitution vars in ai-gateway v1.1.0:
`${header.x-ai-eg-model}` AND `${request.body.model}` are both passed **verbatim**
to the upstream (verified: OpenRouter returns 404 "Model '${header.x-ai-eg-model}'
not found" / "...${request.body.model}..."). To forward the client's requested
model on the catch-all, OMIT `modelNameOverride` entirely — ai-gateway then
sends the original request body (model included) to the backend. This was the
root cause of every "unknown model" 404 on the catch-all; fixed in PR #1917
(route.yaml catch-all has no override). Verified: after the fix, `tencent/hy3`
(paid) returns a real reply through openrouter.

### Inference backends: unified router-mode llama.cpp (single LWS, not two)

- Local floor = ONE `Backend` named `router` → `router.shikanime.svc.cluster.local:8080`.
  The old split into `inference` + `embedding` Backends was unified. Do NOT
  reintroduce separate per-model/per-type Backends — the LWS auto-generates a
  single `router` Service; a hand-written `svc.yaml` or an `inference`/`embedding`
  Backend points at a Service that no longer exists.
- `apps/llama-cpp/` — one `LeaderWorkerSet` named `router` (replicas: 2)
  with `--models-preset /etc/llama-cpp/preset/models-preset.ini` + `--models-dir
  /models`, `--models-max 5`, `--embeddings`, `--no-models-autoload`, `-c 32768`.
  One llama.cpp process serves LLM + embed from a single 120 Gi pool (replaces
  the 120 Gi LLM + 24 Gi embed split that couldn't co-schedule on a 128 Gi Halo).
- `apps/llama-cpp/base/preset/models-preset.ini` (generated by a
  `configMapGenerator` into ConfigMap `router-models-preset`) defines every
  model with `model = /models/<name>.gguf`.
- No `--rpc` flag, no RPC port.
- `modelNameOverride` is the **logical model name** (the `[section]` key in
  the preset) — the router resolves names via the preset file, no GGUF id
  rewrites needed.
- For the LWS install and full spec, see the `sks-dev-workflow` skill
  `references/lws-router-mode.md` (nodeSelector `minisforum-ms-s1`,
  emptyDir+init-container model pull, Flux `infrastructure-lws` wiring).

#### llama.cpp router mode flags

- `--models-preset /path` — starts server without a model, loads dynamically
  via `POST /models/load`. Models defined in the INI file under `[section]`
  keys with `model = /models/name.gguf`.
- `--models-dir /path` — directory containing GGUF files referenced by the
  preset.
- `--models-max N` — cap concurrent loaded models (optional; 0 = unlimited).
- `--models-ttl SECS` — unload idle models after timeout (optional).
- `--no-models-autoload` — disable startup model loading (always load on
  demand).
- `-c N` — shared context window for all loaded models.
- No `-hf` flag — server starts without a HuggingFace model reference.
- `--embeddings` auto-enabled when a model has an embedding layer.

#### GGUF file naming convention

Use lowercase, no-space filenames with the quantization name as the suffix:
`qwen3-8b-q5_K_M.gguf`, `deepseek-v4-flash-q4_K_XL.gguf`. These names are
used in `model =` entries in the preset INI and must match the actual GGUF
files in `/models/`.

#### LWS LeaderWorkerSet as inference router (router-mode llama.cpp)

Full verified spec (nodeSelector `minisforum-ms-s1`, podAntiAffinity,
emptyDir + init-container GGUF pull, Flux `infrastructure-lws` wiring,
capacity/quant table): `sks-dev-workflow` skill `references/lws-router-mode.md`.

- **No shared PVC.** Each replica pulls its own GGUFs (init container →
  `emptyDir` at `/models`); both replicas are identical and serve all models,
  so RWX is unnecessary (supersedes the RWX/`inference-models` PVC design).
- `--models-max 2` bounds loaded models per node (LRU eviction, KV-cache/OOM
  risk on 128 GB Halo nodes). Note the live `router` LWS runs
  `--models-max 5`.
- Flux `apiVersion: leaderworkerset.x-k8s.io/v1` `kind: LeaderWorkerSet` —
  not `apps/v1 StatefulSet`.

### Provider quirks (live, verified)

| Provider | Endpoint | Notes |
|----------|----------|-------|
| Nous | `inference-api.nousresearch.com` (NOT `api.nousresearch.com` — NXDOMAIN) | Same catalog as OpenRouter; pass-through logical model names; `/embeddings` serves `qwen/qwen3-embedding-8b` |
| OpenRouter | `openrouter.ai` | `tls.sni: openrouter.ai` required (Cloudflare SNI check); `/embeddings` serves `qwen/qwen3-embedding-8b` though `/models` omits it; **`tencent/hy3:free` is RETIRED (404 "unavailable for free") — use paid `tencent/hy3`** |
| z.ai | `api.z.ai` | Coding-plan key entitlement is PER-SURFACE (verified 2026-09-09): `api/coding/paas/v4` → 200 for `glm-5.3-flash`; `api/paas/v4` (pay-as-you-go) → `1113 "Insufficient balance or no resource package"`; `api/v1/chat/completions` → `model_access_denied` for glm-5.3-flash. A gateway client sees the upstream error WRAPPED (Anthropic-prefix → `429 {"error":{"message":"Insufficient balance...","type":""}}`), which reads as an exhausted account — probe the provider DIRECTLY per surface before believing it. Key `inference-z-ai` (SOPS `inference-z-ai/.enc.env`) |
| OpenRouter/Nous embeddings | `/embeddings` | `/models` catalog does NOT list embedding models, but `/embeddings` DOES serve `qwen/qwen3-embedding-8b` (verified live). Never infer "no embeddings" from `/models` — probe `/embeddings` directly |

### Z.ai GLM protocol + ai-gateway translation limit (verified)

Z.ai GLM is **NOT OpenAI chat/completions-compatible**. Direct probes proved:
- `POST /api/v1/chat/completions` → **403** `model_access_denied` (wrong protocol).
- `POST /api/v1/responses` (x-api-key or Bearer) → **200** (GLM is Responses-API-only).
- `POST /api/anthropic/v1/messages` (x-api-key or Bearer, `anthropic-version: 2023-06-01`) → **200** (Anthropic Messages-compatible).

ai-gateway v1.1.0 translation matrix is **one-directional**: it translates
*Anthropic `/messages` → OpenAI `/chat/completions`* (and Bedrock), never the
reverse. Setting `AIServiceBackend z-ai` to `schema.name: Anthropic,
schema.prefix: api/anthropic/v1` does NOT fix an OpenAI-client request — the
route schema stays OpenAI, the upstream path stays `/api/v1/chat/completions`
(confirmed in the Envoy access log: `x-envoy-origin-path: /api/v1/chat/completions`),
and Z.ai 403s. The `Anthropic` backend DOES inject `x-api-key` (verified in
`internal/backendauth/credential_override.go`, `applyAnthropicCredential`) — but
auth was never the blocker; the path/protocol is.

**Conclusion:** ai-gateway v1.1.0 cannot bridge OpenAI chat/completions → Z.ai
GLM. The only ways to serve `z-ai/glm-5.3` through the gateway:
- **Translator shim** (one Deployment + Service, no second gateway): receives
  OpenAI `/chat/completions`, emits Z.ai `/api/anthropic/v1/messages`,
  translating the body. `AIServiceBackend z-ai` points at the shim (Backend
  endpoint → shim Service). ai-gateway still injects `x-api-key`; the shim
  forwards it to Z.ai.
- **Drop GLM from the gateway**; call Z.ai's Anthropic `/messages` endpoint
  directly from the client.

`AIGatewayRoute` v1beta1 has **no `failover` field** — a 4xx (403) is terminal,
so the `z-ai → nous → openrouter` chain never reaches the next backend. Only
5xx/transport errors trigger priority failover.

### SOPS-encrypting a new `.enc.env` (no `.sops.yaml` in repo)

The repo has NO sops config file — the flake's creation rules live in the NixOS module.
Plain `sops -e` / `--in-place` fails with "config file not found, or has no creation
rules". Encrypt with explicit recipients (telsha, nixtar, nishir — extract from an
existing `.enc.env` or use the three below) and dotenv types:

```bash
RECIPS="age17q5ljstyzkvqtejwfnyf5jvqduars2yauw7vtgu5fcf54tm2jf0sspvt3c,age1x9v4ps90txy9mk4392uya93tyzx40te4dvns4chg5s6q8mfy03ns74jpay,age1f4yuh4j3gqafjduusfpxz3na9xtwth9s6gznq043mfex0zglp5jqkkdm64"
nix shell nixpkgs#sops -c sh -c "sops --encrypt --age '$RECIPS' apps/.../.enc.env > /tmp/out.env"
# verify: sops --decrypt /tmp/out.env → original value
# copy /tmp/out.env over the placeholder file
```

The file format is `apiKey=ENC[AES256_GCM,data:...,type:str]` plus
`sops_age__list_N__map_enc`/`recipient` lines — NOT a whole-file age ciphertext.
Pitfall: `sops -e` alone prints the version to stdout; `--in-place` needs a config file
that doesn't exist. `--encrypt --age` to stdout is the working form.

### Inbound API-key auth on top of mTLS (verified recipe)

Layer an Envoy Gateway `SecurityPolicy` (apiKeyAuth) on the `inference` Gateway
so a client needs BOTH a CA-signed client cert (the existing mTLS
`ClientTrafficPolicy inference`) AND a valid key in the `Authorization` (Bearer)
or `X-Api-Key` header — defense in depth, not a replacement. Full
`SecurityPolicy` shape, `secretGenerator` + `namereference` wiring, raw-key
semantics (store WITHOUT `Bearer `), access-log discriminators
(`missing_api_key` vs `unkonwn_api_key` vs `via_upstream`), the
suspend-before-live-patch pattern, and the four-layer Hermes↔gateway
debugging chain (401 raw-key → 401 X-Api-Key → Hermes key-env resolution →
bare-vs-prefixed model id):
`references/inbound-apikey.md`.

## Streaming routes need timeouts.request: 0s (the 15s cut, verified 2026-09-11)

EG applies a **15s default per-route request timeout** when the HTTPRoute rule
has no `timeouts`. Long LLM streams die mid-generation at exactly 15.0s
(client sees 200 + partial SSE then `HTTP/2 INTERNAL_ERROR` reset; Envoy logs
`flags: UT`, `response_code_details: response_timeout`, `duration: 15001`).
Fix: `timeouts: {request: 0s}` on every route carrying chat completions
(llama-cpp `base/httproute.yaml` does this for both `llama-cpp` UI and
`llama-cpp-api` /v1 routes). Verified: same probe ran 150s post-fix.

Access-log trap: in THIS fleet's EG JSON access log `:path`/`:authority` are
often **null** — path/authority filters silently match nothing. Filter by
`response_code` / `duration` / `response_flags` instead. `grep 402` also
false-positives on `http2.too_many_headers` (string contains "402").

### AIGatewayRoute synthesizes a 60s route timeout on `default` (verified 2026-09-14, PR #2352)

`AIGatewayRoute` (v1beta1) has no timeout field, but the controller
synthesizes an HTTPRoute named `default` carrying `timeouts.request: 60s` on
EVERY rule — so the `inference` Gateway path has a **60s cap**, NOT the 15s
seen on hand-written routes. Long llama.cpp generations (14k-35k tokens at
~10-16 t/s = minutes) die at exactly ~60.0s: the inference Envoy access log
shows `response_flags: UT`, `response_code_details: response_timeout`,
`upstream_host: <llama-cpp-pod>:9931`, `duration: ~60100`, on
`route_name: httproute/shikanime/default/rule/<N>`. The router then logs
`http client error: Connection handling canceled` → `stop: cancel task` →
`slot release ... n_tokens = <big>` — those are the AFTERMATH of Envoy's
reset, NOT a router fault (the llama.cpp router is healthy; it is reporting
the reset).

- A `BackendTrafficPolicy` targeting the synthesized `default` route does NOT
  help — the HTTPRoute rule's OWN `60s` wins (route timeout > BTP timeout in
  EG precedence).
- The correct fix is on the AIGatewayRoute rule: the CRD rules schema supports
  `timeouts.request` (and `backendRequest`). Set `timeouts: {request: 0s}` on
  every rule that carries chat completions — it renders `request: 0s` into the
  generated HTTPRoute. The dedupe anchor is the `modelsOwnedBy: Shikanime
  Studio` line that precedes every rule's `backendRefs`.
- Verify via the generated route, not the AIGatewayRoute:
  `kubectl get httproute default -n shikanime -o jsonpath='{.spec.rules[*].timeouts}'`
  → each rule should show `{"request":"0s"}`.

## Out-of-band `kubectl apply` of rendered policies breaks hashed secretRefs

`kustomize build` regenerates secretGenerator hashes from YOUR working tree;
Flux's live hashes come from main. Applying rendered SecurityPolicies /
HTTPRouteFilters rewrites `credentialRefs`/`secretRef`/`valueRef` to YOUR
hashes → dangling refs → EG 500 `direct_response` (instant, empty body) on
every request. Verified 2026-09-11: apply of 2 SecurityPolicies + 2
HTTPRouteFilters + 5 HTTPRoutes dangled 3 refs
(`llama-cpp-key-5486d4tckh` vs live `llama-cpp-key-26hmg66k56`, etc.).
If it happens: `kubectl patch` each ref back to the LIVE hash (list secrets,
match by prefix), never re-apply the render. Restrict out-of-band applies to
the exact resource kind you intend (grep the extracted docs), and prefer
`kubectl patch` for single-field changes.

## Embedding responses 500 with response_payload_too_large (verified 2026-08-30)

`/v1/embeddings` on large models (qwen3-embedding-8b) returns empty-body 500 with
`response_code_details: response_payload_too_large` **on every failover target**
— failover itself works (envoy log shows the request reaching nous/openrouter).
Cause: ai-gateway ext_proc runs `response_body_mode: BUFFERED` and Envoy's
default connection buffer (32KiB) is smaller than an 8B embedding vector.
The `x-envoy-ext-proc-overrides: {"response_body_mode":"STREAMED"}` header did
NOT take (v1.1.0). Fix is ClientTrafficPolicy on the inference Gateway
(`apps/llama-cpp/overlays/nishir/clienttrafficpolicy.yaml`), per upstream
ai-gateway docs:

```yaml
spec:
  connection:
    bufferLimit: 50Mi          # was 8Mi — still too small
  http2:
    initialStreamWindowSize: 16Mi
    initialConnectionWindowSize: 24Mi
```

Shipped as manifests PR #1950. Verify after merge with a real
`/v1/embeddings` call, not just Gateway conditions.

## Upstream documentation (distilled from aigateway.envoyproxy.io, v1.1)

Forking + filing a PR against envoyproxy/ai-gateway: `references/upstream-fork-pr.md`
(sequence, semantic-title + DCO gates, body conventions).

The reference files below distill the **upstream Envoy AI Gateway docs** (the
official site, not the fleet wiring). Load them on demand via `skill_view` when
authoring against upstream shapes or explaining AI Gateway behavior to a reader
who has not read the source. They are complementary to the fleet-ops notes
above — when fleet facts and upstream docs conflict, the fleet notes win.

- `references/upstream-overview.md` — what AI Gateway is, two-plane architecture, ext-proc router/upstream phases, why failover lives in ext-proc.
- `references/upstream-install.md` — prerequisites (k8s ≥1.32, EG ≥1.8.1), Helm install of EG + ai-gateway CRDs/controller, basic-usage mock backend, connect-provider, buffer/HTTP2 gotcha.
- `references/upstream-resources.md` — AIGatewayRoute / AIServiceBackend / BackendSecurityPolicy shapes, priority vs failover, modelNameOverride, header/body mutation, route merging, v1beta1 4xx-is-terminal.
- `references/upstream-security.md` — client-auth (EG SecurityPolicy) vs upstream-auth (BackendSecurityPolicy): API key vs AWS/Entra/GCP short-lived federation.
- `references/upstream-traffic.md` — usage-based rate limiting (llmRequestCosts + Global BackendTrafficPolicy) vs QuotaPolicy; token timing, streaming over-limit, per-tenant metadata limits, cost expressions.

## Listener-hook + TCP/UDP gateways: SOLVED (verified live 2026-08-30)

ai-gateway v1.1.0 needs **listener IR** (`xdsTranslator.translation.listener.includeAll: true`)
to insert the router-level `envoy.filters.http.ext_proc/aigateway` filter
(`PostTranslateModify` → `insertRouterLevelAIGatewayExtProc`). The router leg is what sets
`x-envoy-aigateway-internal-req-id`; without it every chat completion 500s with
`ext_proc_error_gRPC_error_13{missing_internal_request_ID_header_from_router_filter}`.
Earlier conclusion ("either/or: listener IR breaks syncthing TCP/UDP") was FALSIFIED — the
two hard-error sources on non-HTTP filter chains are separately gated:

1. **`insertRouterLevelAIGatewayExtProc` only runs on listeners whose route configs contain
   an AIGateway-generated route** (`enabled` flag). Syncthing's TCP listener never qualifies.
   The unrelated `patchListenerWithInferencePoolFilters` and quota-ratelimit walks already
   `continue` on non-HCM chains.
2. **`insertRequestHeaderToMetadataFilters` was the real syncthing killer**: it defaults ON
   (`logRequestHeaderAttributes` defaults to `agent-session-id:session.id`) and `findHCM`
   hard-errors on TCP/UDP chains. `controller.logRequestHeaderAttributes: ""` disables the
   default by design (chart value renders `--logRequestHeaderAttributes=`).

**Working config (both applied together, verified end-to-end):**
- `infrastructure/envoy-gateway/base/hr.yaml`: `listener.includeAll: true`.
- `infrastructure/envoy-ai-gateway/base/hr.yaml`: `controller.logRequestHeaderAttributes: ""`.

Verified: inference dataplane HCM = `[ext_proc/aigateway, router]`, chat completion → 200
through openrouter; syncthing Gateway Programmed=True, TCP 22000 forwarding. Cost: the
agent-session-id header no longer lands in access-log attributes (cosmetic).

Side note (open, separate defect): a `z-ai` AIServiceBackend with
`schema: Anthropic (api/anthropic/v1)` 500s under v1.1.0 ext-proc —
`cannot set backend: failed to create translator ... unsupported API schema: Anthropic`.
The translation matrix handles Anthropic on the REQUEST side only; Anthropic-schema
BACKENDS are unsupported. Route z.ai through OpenAI schema or a translator shim.
E2E re-verified 2026-08-30 on `inference.i.shikanime.studio` (public LE endpoint,
post-#1946). **CORRECTION (same day, live-verified): the gateway DOES expose
Anthropic-format serving under the `--endpointPrefixes` prefix** — the
controller runs with `--endpointPrefixes=openai:,cohere:/cohere,anthropic:/anthropic`,
so GLM works via `POST https://inference.i.shikanime.studio/anthropic/v1/messages`
(`x-ai-eg-model: z-ai/glm-5.3[-flash]`, `anthropic-version: 2023-06-01`) → **200**
with a real reply. `/v1/messages` without the prefix 404s (`unsupported path`);
`/v1/chat/completions` still 500s with `unsupported API schema: Anthropic`.
Client-side rule: **use the `/anthropic` prefix for GLM — it is not broken,
it is served on a different path.**

Upstream hardening FILED + fix drafted: envoyproxy/ai-gateway#2600 (2026-08-30) —
skip-don't-error on non-HCM chains in `insertRequestHeaderToMetadataFilter`
(header_to_metadata.go:41) and `insertRouterLevelAIGatewayExtProc`
(post_translate_modify.go:777). Fix lives in draft PR
envoyproxy/ai-gateway#2601 (`fix: skip non-HCM filter chains instead of failing
translation`, head `shikanime:fix/skip-non-hcm-chains`), developed in a fork
clone at `~/Source/Repos/github.com/envoyproxy/ai-gateway` (remote `upstream` =
envoyproxy/ai-gateway). Local verification before push: full
`go test ./internal/extensionserver/` (with a `skip-non-hcm-chain` regression
case in header_to_metadata_test.go), `go vet`, `gofmt -l`.

Upstream contribution gates (learned 2026-08-30, cost three force-pushes):
1. PR title MUST match their semantic-pull-request allowlist — plain types only
   (`fix:`, `feat:`, `docs:`, …). An `extensionserver:` scope prefix FAILS the
   Title check ("Unknown release type"). Check `.github/PULL_REQUEST_TEMPLATE.md`
   and existing landed PR titles before the first push.
2. DCO is enforced: every commit needs `Signed-off-by:` whose email matches the
   commit AUTHOR email — the fleet git config is
   `william.phetsinorath@shikanime.studio`, not a `shikanime.dev`-style address.
3. Amend + `git push --force-with-lease` re-runs Title/Description/DCO (~60s);
   the Go test workflows only trigger on mark-ready. Poll
   `gh pr view --json statusCheckRollup`, not the checks panel lag.
4. PR body follows `.github/PULL_REQUEST_TEMPLATE.md`:
   `**Description**` / `**Related Issues/PRs**` (`Fixes #N`) /
   `**Special notes for reviewers**`.

Left in DRAFT pending user review (mark-ready triggers full CI).
Internal trackers: manifests#1947
(z-ai Anthropic-schema backend 500; matches upstream envoyproxy/ai-gateway#1936
"OpenAI→Anthropic schema translator"), manifests#1948 (tracks #2600 upstream fix + dropping
the `logRequestHeaderAttributes: ""` workaround after it lands). manifests#1940 (original
syncthing outage) closed as superseded by #1941/#1942/#1946.

### Deep-dive record of the listener-hook investigation

Full session detail (source line numbers for `post_translate_modify.go` /
`inferencepool.go` / `requestheaderattrs/resolve.go` at v1.1.0, the falsified
"either/or" reasoning, the falsification pass, and the live probe sequence) is
in `references/listener-hook-tcproute-conflict.md`. Read it before re-deriving
anything about listener IR, `findHCM`, or the internal-req-id contract.

## ext-proc not injected: cross-namespace Gateway/Envoy trap (verified root cause)

Symptom: every `/v1/chat/completions` returns empty-body **HTTP 500** with
`response_code_details: ext_proc_error_gRPC_error_14 ... No such file or
directory ... /etc/ai-gateway-extproc-uds/run.sock` in the Envoy access log
— the ext-proc **UDS socket is missing**, so ext-proc never starts. The
extproc filter IS in the listener (controller logs `inserting AI Gateway
extproc filter`), so this is NOT the wiring failure in `extproc-500-triage.md`
Cause #1.

Root cause (ai-gateway v1.1.0): the ai-gateway controller finds the Envoy
data-plane Deployment by **namespace-scoping its search to the Gateway's
namespace**. In this fleet the `inference` Gateway lives in `shikanime` but
envoy-gateway deploys the Envoy data plane to `envoy-system` (the
`envoy` HelmRelease `targetNamespace: envoy-system`, hr.yaml line 23). ai-gateway
logs `No pods, deployments or daemonsets found for the Gateway
{namespace: shikanime, name: inference}` every 5s and **never injects the
ext-proc init container** into the Envoy pod. No ext-proc Deployment ever gets
created. This is independent of `--envoyGatewayNamespace` (that flag points at
the envoy-gateway CR namespace; default `envoy-gateway-system`, which is empty
here — set it to `envoy-system` where envoy-gateway actually runs, but that
alone does NOT fix the injection; the blocker is the Gateway-vs-Envoy
deployment namespace mismatch).

THE DELETE TRAP that triggers it: deleting `inference-shikanime` (the
controller render-source Opaque Secret, ns `envoy-system`) or the projected
bundle `inference-shikanime-<hash>` breaks the *initial* sync; ai-gateway
will not re-render on any reconcile/restart/object-recreate. Once broken, the
only durable fix is a topology change (co-locate Gateway + Envoy in one
namespace) so the initial sync fires cleanly.

Fix options (present to user before mutating topology):
- **A — co-locate in `envoy-system` (durable).** Move the `inference` Gateway
  + `AIGatewayRoute` into `envoy-system` (where ai-gateway runs and the Envoy
  deployment already lives); add the `ReferenceGrant` + set
  `AIGatewayRoute.spec.parentRefs[].namespace` for the cross-namespace route.
  Matches ai-gateway v1.1.0's single-namespace assumption; initial sync
  re-injects ext-proc. Persist via Flux in `manifests`.
- **B — manual ext-proc injection (quick unblock, drift).** Hand-patch the
  live Envoy deployment to add the `ai-gateway-extproc:v1.1.0` init container
  mounting `inference-shikanime-<hash>`; reversible via `rollout undo` but not
  Flux-managed.

Do NOT `kubectl delete` any `inference-shikanime*` Secret to "force a
re-render" — it is unrecoverable without a topology change (see Credential
injection architecture above).

## Credential injection architecture (verified, ai-gateway v1.1.0)

- The ext-proc that injects the `Authorization` header (`ai-gateway-extproc`,
  image `ai-gateway-extproc:v1.1.0`) runs as an **init container in the Envoy
  data-plane pod** (`envoy-shikanime-inference-*`), which also holds `envoy`
  + `shutdown-manager`. It is NOT in the `ai-gateway-controller` Deployment and
  NOT a standalone ext-proc pod. The controller renders credentials into a
  **projected Secret `inference-shikanime-<hash>`** (ns `envoy-system`) that
  the ext-proc init container mounts as its config bundle at startup.
- Consequence: bouncing the Envoy data-plane pod does NOT reload credentials
  (the same stale projected Secret re-mounts), and a controller bounce does NOT
  reliably regenerate that Secret either. **AI-GATEWAY DOES NOT RE-RENDER THE
  PROJECTED SECRET WHEN THE SOURCE SECRET'S DATA ROTATES** — it watches
  name/ref, not content. So a key rotation can leave the ext-proc injecting the
  pre-rotation (revoked) key indefinitely → 401, while the raw key in the
  cluster is valid and direct curl works. This is an ai-gateway v1.1.0
  operational limitation, not a manifest defect.
- **Do NOT `kubectl delete` the projected Secret** to force regeneration.
  VERIFIED this session: a deleted `inference-shikanime-<hash>` did NOT
  regenerate via `rollout restart ai-gateway-controller`, BSP annotation, or
  Flux HelmRelease reconcile — it stayed `NotFound`. ai-gateway creates it only
  on the *initial* Gateway/EnvoyProxy sync, so a delete leaves the running pod
  alive (cached bundle) but guarantees a crashloop on the next pod restart.
  The same applies to the controller's render-source Opaque Secret
  `inference-shikanime` (key `filter-config.yaml`): deleting it also breaks
  the initial sync and ai-gateway will not recreate it. Leave ALL
  `inference-shikanime*` resources untouched. DEBUG
  logging also does not expose the injected credential (deliberately not
  logged) and the ext-proc image is distroless (no exec/cp).
- **Flux owns reconciliation.** User directive ("flux is there's for this"):
  manual kubectl pokes at generated ai-gateway objects (delete Secret, roll
  pod, patch Deployment) create drift + crashloop hazards and do NOT force a
  re-render. Let Flux reconcile; if a forced re-render is truly needed, ask the
  user to run `flux reconcile` from a host with the binary (it is NOT on every
  command PATH — the `flux` CLI was absent this session).
- First-line diagnostic (run before the 5-step recipe): the **400-vs-401
  differential** — a headerless direct provider call returns 400 "Unknown
  model" while the gateway returns 401, proving the ext-proc injects a *stale*
  key (localizes to the projected Secret without logs/exec). Full recipe
  (decode secret → direct curl → BSP check → trailing-newline → same-backend
  discriminator → stale-projected-Secret check → delete-trap warning):
  `references/credential-401-triage.md`.
- mTLS-vs-DNS diagnosis (externalDNS-correct-but-000, live-patch-reverted-on-reconcile,
  LE-token precheck): `references/mtls-vs-dns-diagnosis.md`.

### Live-testing on the cluster

- Client-side end-to-end probe (auth via `SKS_API_KEY`, namespaced model-id
  rule, the empty-body OpenAI-vs-working-Anthropic trap, `pong` smoke proof):
  `references/client-probe-from-tailnet.md`.
- **The EG `values.config` renders into ConfigMap `envoy-gateway-config` (key
  `envoy-gateway.yaml`), NOT a standalone EnvoyGatewayConfig CRD.** Manual
  probes on it follow these rules (all proven 2026-08-30, the hard way):
  - A manual `kubectl replace` of that ConfigMap **sticks** — Flux's Helm
    upgrade does NOT re-render it while the chart version is unchanged. The
    "reconcile will fix it" assumption is false; your probe becomes prod.
  - `flux reconcile hr` / suspend+resume / HR delete+recreate do NOT restore a
    diverged or deleted ConfigMap. Re-render only happens on a chart/version
    change. Treat every manual ConfigMap write as something you must revert
    by hand or by landing the real values in Git.
  - **Helm upgrade does not roll the EG pod** — it loads config at startup
    only. After changing values (live or via Git), a rollout of the control
    plane is REQUIRED for the new extension config to take effect.
  - `kubectl rollout restart` can report success WITHOUT rotating the pod
    (check `.metadata.creationTimestamp`). If the pod didn't rotate, force it:
    `kubectl delete pod <eg-pod>`. Verify the new timestamp before testing.
  - Debug-pod reachability checks (`kubectl run curlimages/curl`) fail under
    PodSecurity `restricted` unless the pod sets `runAsNonRoot: true`,
    `seccompProfile: RuntimeDefault`, `allowPrivilegeEscalation: false`,
    `capabilities.drop: [ALL]` — and `exec sh` fails on distroless images
    (envoy-gateway, ai-gateway-extproc: no shell). Test connectivity from a
    separate curl pod, never from the dataplane pod itself.
- **Never probe by toggling the global extensionManager hook on/off.** The
  2026-08-30 outage (inference 500 for ~80 min) came from repeated manual
  ConfigMap edits removing/restoring `extensionManager`. The sequence
  remove → test → restore does not return to a working state: EG stops
  calling the ai-gateway extension and a restore + restart does not reliably
  re-establish it. Use the listener-hook config above
  (`listener.includeAll: true` + `logRequestHeaderAttributes: ""`) which keeps
  both inference and syncthing healthy — no live mutation needed.

- **Trial config on a Flux-managed HelmRelease: suspend → patch → verify →
  promote in repo.** A bare `kubectl patch helmrelease <name> -p '{"spec":{"values":...}}'`
  is REVERTED by Flux's own HelmRelease reconcile (~minutes, from Git state) —
  it reverts even without a branch merge. To hold a candidate config long
  enough to verify: `kubectl patch ... -p '{"spec":{"suspend":true}}'` first,
  THEN patch `spec.values`, annotate `reconcile.fluxcd.io/requestedAt`, verify
  (Gateway conditions, config_dump, live request), then promote the exact
  values into the repo hr.yaml. Never leave `suspend: true` behind.
  (Proven 2026-08-30: the unsuspended patch reverted within one reconcile
  cycle mid-verification; only the suspend-first sequence held.)
- **Port-forwards die with the dataplane pod.** Rolling the Envoy data plane
  (HelmRelease upgrade, config change) orphans `kubectl port-forward
  pod/<name>` with confusing `connection refused`/empty-output failures, and
  pod names churn. Re-resolve the pod name (`kubectl get pods | grep
  envoy-shikanime-<gw>`) and re-establish the forward after every rollout
  before concluding the probe failed. Also: a stale port-forward holding
  19000 makes the next one fail with `bind: address already in use` — kill
  the old process (`lsof -ti :19000 | xargs kill`) before re-forwarding.

- CI: `gh workflow run Integration --ref <branch>` (does not always auto-trigger).
  The PR checks panel lags — read
  `gh api repos/<org>/<repo>/commits/<sha>/check-runs`.
- Out-of-band apply: `kustomize build <overlay>` → strip placeholder Secrets
  from the render (real keys live server-side) → `kubectl apply`. The infra
  overlay does NOT carry its namespace (it comes from the cluster base) —
  apply `kubectl create namespace <ns>` first or every object fails
  "namespaces ... not found".
- Re-running `kubectl apply` on a multi-doc `hr.yaml` only upserts matching
  docs; a doc that was rejected on first apply (missing ns, invalid) stays
  absent — verify `kubectl get helmrelease` for all three after apply.
- SOPS trap: the render's Secret data is the **ciphertext**
  (`apiKey=ENC[AES256_GCM,data:...`) — Flux decrypts `.enc.*` at reconcile,
  but out-of-band `kubectl apply` writes ciphertext verbatim. The value looks
  real by length, and upstream 401s. Fix:
  `sops -d apps/.../*.enc.env` → `kubectl create secret generic <name>
  --from-literal=apiKey="$(grep '^apiKey=' file | cut -d= -f2-)"`.
- Upstream 401 with a real-looking key? Isolate key vs wiring with a throwaway
  curl pod: curlimages/curl, `runAsUser: 100`, nodeSelector rpi5, and the key
  mounted via `secretKeyRef` env, then `curl` the provider's
  `/v1/chat/completions` directly. 401 from the provider = bad/expired key
  (nous: "invalid, blocked or out of funds"; zai: "token expired or
  incorrect"); success = gateway wiring is the problem.
- Flux reconcile annotations on HelmRepository are unreliable — delete +
  recreate the object to force source-controller.
- Envoy admin (port-forward 19000): `config_dump?resource=dynamic_active_clusters`
  shows endpoints + SNI; `dynamic_route_configs` shows `direct_response` vs
  proxy and `route-not-found` rules. `x-envoy-origin-path` is the ORIGINAL
  path, pre-rewrite.
- Dataplane is distroless (no shell/exec). Use the admin API, or a
  `curlimages/curl` pod with `runAsUser: 100` + nodeSelector for outbound tests.

## Dead endpoints / DNS

- `api.nousresearch.com` is NXDOMAIN everywhere (no A records; served via
  `portal.nousresearch.com` OAuth). Never route to it.
- The REAL OpenAI-compatible Nous endpoint is
  `inference-api.nousresearch.com` (Cloudflare, resolves 104.26.x). It serves
  `/v1/chat/completions` with an `Authorization: Bearer` key; HTTPS direct curl
  from in-cluster with the stored key returns 401 "invalid, blocked or out of
  funds" when the key is a placeholder — that is a credentials issue, not a
  manifests defect. Backend needs `tls.sni: inference-api.nousresearch.com`.
- Before concluding "cluster DNS broken", test control domains (github.com,
  openrouter.ai) from the same path — one NXDOMAIN is domain-specific, not
  infra-wide.

## rpi4 memory: root-cause fix, not node pinning

- The 3 GiB rpi4 nodes (instance-type rpi4-model-b) kill envoy's tcmalloc
  (`CHECK in Alloc: FATAL ERROR: Out of memory`, exit 133 SIGTRAP) under
  memory pressure. Root cause is the kernel's heuristic overcommit policy
  (*vm.overcommit_memory=0* default) REFUSING tcmalloc's large mmap — the
  SIGTRAP on small nodes is a failed allocation, not a real OOM.
- FIX AT THE SOURCE (fleet convention, reviewed): the shared NixOS machine
  profile (`machines/modules/nixos/profiles/machine.nix`) sets
  `boot.kernel.sysctl."vm.overcommit_memory" = 1`. Always-overcommit lets the
  mmap succeed and defers genuine pressure to the kernel OOM-killer + zram +
  systemd-oomd (all already enabled fleet-wide). Applies to every host that
  imports `machine.nix` (fushi, minish, nemishi, ...) — no per-host pin.
- DO NOT pin the data plane off small nodes with `nodeSelector` / node
  affinity as a workaround. A scheduling constraint that exists only to dodge
  a crash is a symptom-fix. Once the overcommit sysctl lands, envoy runs fine
  on rpi4 — remove the pin entirely and let the scheduler place it. (This was
  reversed in review: the original `nodeSelector: rpi5` and a later
  rpi4+rpi5 affinity were both dropped.)
- The CONTROL-PLANE `deployment.nodeSelector` (gateway-helm values) was
  REMOVED in review — the control plane schedules fine on beelink nodes
  without a pin; do not re-add it.

## MCPRoute (Model Context Protocol)

`MCPRoute` (`aigateway.envoyproxy.io/v1beta1`) is a SEPARATE CRD from
`AIGatewayRoute` — it proxies MCP servers, not LLM chat. Add one to expose a
provider's MCP tools through the same Gateway the `AIGatewayRoute` uses.

Pattern (verified to render; live MCP serving NOT yet confirmed this session):

- Reuse an EXISTING `Backend` (e.g. the `z-ai` Backend already pointing at the
  provider fqdn) — do NOT create a new Backend just for MCP.
- Inline the auth under the MCPRoute `backendRefs` instead of a standalone
  `SecurityPolicy`: `securityPolicy.apiKey.secretRef: { name: inference-<p>,
  namespace: shikanime }` (the same `inference-*` SOPS secret the LLM route
  uses). No new `BackendSecurityPolicy` resource needed.
- `spec.parentRefs` → the same Gateway the `AIGatewayRoute` uses (`inference`,
  `kind: Gateway`).
- `spec.path` is the gateway route prefix (e.g. `/mcp/z-ai`); the Backend
  `path` under `backendRefs` is the provider's MCP endpoint path (e.g.
  `/api/mcp/z-ai`). These are independent.
- Place the `MCPRoute` in `base/` so it inherits the overlay's generated
  `inference-*` Secret (only the overlay's `secretGenerator` creates it).

```yaml
apiVersion: aigateway.envoyproxy.io/v1beta1
kind: MCPRoute
metadata: { name: z-ai, namespace: shikanime }
spec:
  parentRefs: [{ name: inference, kind: Gateway, group: gateway.networking.k8s.io }]
  path: /mcp/z-ai
  backendRefs:
    - name: z-ai
      kind: Backend
      group: gateway.envoyproxy.io
      path: /api/mcp/z-ai
      securityPolicy:
        apiKey:
          secretRef: { name: inference-z-ai, namespace: shikanime }
```

UNVERIFIED (do not assert as fact — confirm before relying):
- EG may require an MCP feature flag analogous to `enableBackend: true` (the
  Backend API is opt-in). Check `infrastructure/envoy/base/hr.yaml` and test
  live before depending on MCP serving.
- The upstream MCP path was an inference (`/api/mcp/z-ai`); Z.ai's docs describe
  per-server paths (`https://api.z.ai/api/mcp/<server>/mcp`, e.g.
  `web_search_prime`, `zread`). Confirm the correct base path with the provider.
- Validate render without a cluster: `kustomize build apps/llama-cpp/base`
  (MCPRoute must appear) and `SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt"
  kustomize build apps/llama-cpp/overlays/nishir-tailnet` (generated `Secret
  inference-z-ai` + `MCPRoute` must both render).
