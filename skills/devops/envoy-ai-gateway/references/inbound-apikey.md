# Inbound API-key auth on top of mTLS (Envoy Gateway)

Verified recipe applied to the `inference` Gateway (ns `shikanime`,
`apps/llama-cpp/overlays/nishir-tailnet`) in PR #1909. Reusable for any Envoy
Gateway that already enforces client-cert mTLS and needs an application-layer
credential on top.

## What it adds

A `SecurityPolicy` (gateway.envoyproxy.io/v1alpha1) with `apiKeyAuth` that
targets the Gateway. The gateway then requires BOTH a CA-signed client cert
(the existing `ClientTrafficPolicy inference`, mTLS) AND a valid key in the
`x-api-key` header. `sanitize: true` strips the key before it reaches the
ai-gateway ext-proc or upstream providers.

## SecurityPolicy shape

```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: SecurityPolicy
metadata:
  name: inference-apikey
  namespace: shikanime
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: Gateway
      name: inference
  apiKeyAuth:
    credentialRefs:
      - group: ""
        kind: Secret
        name: inference-gateway-apikey
    extractFrom:
      - headers:
          - Authorization
          - X-Api-Key
    sanitize: true
    forwardClientIDHeader: x-inference-client-id
```

- `credentialRefs` points at an Opaque Secret (one data key per client id; the
  key name is the client id). EG treats each Secret data key as a valid key.
- `extractFrom.headers` is where the key comes from (EG also supports
  `cookies` / `params`). List BOTH `Authorization` and `X-Api-Key`: OpenAI-SDK
  clients send Bearer-in-Authorization, Anthropic-SDK clients send `x-api-key`.
- **CRITICAL: store the credential as the RAW key, NEVER `Bearer <key>`.**
  EG's `apiKeyAuth` compares the header value with the scheme ALREADY
  STRIPPED — a Secret holding `Bearer <key>` never matches and every request
  401s with "Client authentication failed". (An earlier revision of this file
  wrongly claimed the prefix was required; live-verified 2026-08-31 on
  nishir that the raw key matches on both headers.) Anthropic clients hit
  `/anthropic/v1/messages` (served via the controller's `--endpointPrefixes`)
  with `x-api-key`, so both extractFrom headers matter there.
- `sanitize` removes the header before forwarding — important so the key never
  reaches paid upstreams or the ext-proc.
- `forwardClientIDHeader` adds `x-inference-client-id: <client-id>` to the
  upstream request for audit.

## Secret generation (kustomize + SOPS)

The key lives in a SOPS-encrypted `.enc.env`, generated into an Opaque Secret
via `secretGenerator`:

```yaml
# kustomization.yaml (overlay)
secretGenerator:
  - name: inference-gateway-apikey
    namespace: shikanime
    envs:
      - inference-gateway-apikey/.enc.env
```

Encrypt the `.enc.env` to the THREE fleet age recipients (telsha / nixtar /
nishir) with the unwrapped sops binary — see `sks-dev-workflow` SOPS section.
A single `.enc.env` line: `inference-gateway=<random-key>`.

## namereference wiring (hashed secret name)

kustomize hashes the generated Secret name (`inference-gateway-apikey-<hash>`).
The `SecurityPolicy.spec.apiKeyAuth.credentialRefs[].name` must follow that
hash, so extend the overlay `namereference.yaml`:

```yaml
nameReference:
  - version: v1
    kind: Secret
    fieldSpecs:
      - kind: SecurityPolicy
        path: spec/apiKeyAuth/credentialRefs/name
        group: gateway.envoyproxy.io
```

(Keep the existing `BackendSecurityPolicy` / `MCPRoute` entries; just add the
`SecurityPolicy` one.)

## Verification

```bash
SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt" \
  kustomize build apps/llama-cpp/overlays/nishir-tailnet
# → SecurityPolicy inference-apikey present, credentialRefs.name = inference-gateway-apikey-<hash>
```

- Scope check: the `SecurityPolicy` must appear ONLY in the overlay that owns
  the Gateway (here `nishir-tailnet`). Build a sibling overlay (e.g. `nishir`)
  and confirm zero `SecurityPolicy` — the gate is intentionally Gateway-scoped.
- The generated Secret renders as `type: Opaque` (correct for EG `apiKeyAuth`).

## Envoy access-log triage of apiKeyAuth (fast discriminators)

Access-log `response_code_details` on the Envoy data plane (`-c envoy`) tells
you which side of the gate failed:
- `missing_api_key` — no `Authorization`/`X-Api-Key` header reached the gate
  (client didn't send one, or it was stripped upstream of Envoy).
- `unkonwn_api_key` (sic — EG's typo) — a key was sent but matches NO Secret
  data value (wrong key, or stored WITH `Bearer ` prefix).
- 404 `via_upstream` with an upstream host = auth PASSED; the route/model
  match or the provider failed. Auth and routing are independent layers —
  always read `response_code_details` before blaming the key.

JSON-log parse loop for triage (path, code, details, upstream):

```bash
kubectl -n envoy-gateway-system logs <envoy-pod> -c envoy --since=5m | python3 -c "
import sys, json
for line in sys.stdin:
    try: d = json.loads(line)
    except: continue
    print(d.get('start_time','')[11:19], d.get('user-agent','')[:24],
          d.get('method'), d.get('x-envoy-origin-path'), '->',
          d.get('response_code'), d.get('response_code_details','')[:60],
          'up:', d.get('upstream_host'))
"
```

Gotcha: the Anthropic SDK's User-Agent (`Anthropic/Python x.y`) appears on
ANY client session — check `x-envoy-origin-path` (e.g. `/anthropic/v1/messages`
= the real primary request; `/v1/chat/completions` = an OpenAI-schema fallback
chain riding the same gateway), not the UA, to attribute requests.

## Live-patching the route before PR merge (suspend-first pattern)

When the cluster must serve traffic before the manifests PR lands (Flux
`apps-llama-cpp` Kustomization re-applies `main` every ~10 min and reverts
live edits):

1. `flux suspend kustomization apps-llama-cpp` FIRST — an unsuspended Flux
   will silently revert your `kubectl apply` within minutes.
2. Export live object → edit locally (`uv run --with pyyaml` — the system
   python has no PyYAML) → `kubectl apply` (expect the "missing
   last-applied-configuration" warning; it patches fine).
3. After merge: `flux resume kustomization apps-llama-cpp`, then re-verify
   the reconciled objects (rule list, Secret data, extractFrom headers).

Live interim changes are HANDOFF state, not durable — list them explicitly
when pausing a session so the next one resumes Flux.

## Full end-to-end debugging chain (2026-08-31 session: Hermes → gateway 401 → 404)

Four stacked causes masked each other; each fix revealed the next. When an
inference client fails, fix and re-test ONE layer at a time — the error class
changes as each layer heals:

1. **401 "Client authentication failed"** — Secret stored `Bearer <key>` (see
   raw-key rule above). Envoy log: `unkonwn_api_key`.
2. **401 for Anthropic-SDK clients only** — `extractFrom.headers` lacked
   `X-Api-Key` (Anthropic SDK sends `x-api-key`, not Bearer).
3. **Client sends key but Hermes ignores the configured env var** — Hermes
   bare `provider: custom` + explicit `base_url` ignores
   `custom_providers[].key_env`; it host-derives `<VENDOR>_API_KEY` from the
   registrable host label (`inference.i.shikanime.studio` →
   `SHIKANIME_API_KEY`). Two working shapes: (a) named provider
   `custom:<name>` with an explicit `custom_providers` entry honoring
   `key_env`; (b) bare `custom` + env named for the host label. Simulate
   resolution in the hermes-agent venv with
   `resolve_runtime_provider(requested=...)` before blaming the gateway.
4. **Auth passes, model 404s via catch-all** (`via_upstream` to openrouter
   IPs) — Hermes requests the BARE model id (`glm-5.3-flash`) while the
   AIGatewayRoute only matches the prefixed `z-ai/glm-5.3-flash` Exact rule;
   the bare id falls into `.*` → nous/openrouter → 404. Fix on the CLIENT
   side: configure the prefixed id (`z-ai/glm-5.3-flash`) in the provider
   entry. (A bare-id route rule was prototyped live and REJECTED by the
   user — do not add one to the repo.)

Debug tip: `hermes chat -q --verbose` prints the full Anthropic SDK request
options (`url`, headers, model) — one command shows which base_url, key
source, and model id the client actually used. The client-side E2E probe is
`hermes chat -q "Reply with exactly: GATEWAY-OK"`; fallback warnings in
stderr name which chain entry took over.
