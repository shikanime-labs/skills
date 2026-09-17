# ext-proc 500 triage (Envoy AI Gateway)

Symptom: every `/v1/chat/completions` returns **empty-body HTTP 500**; Envoy
access log shows `response_code_details: direct_response`, `upstream_cluster: null`.

## Two distinct root causes

### 1. Extension not wired (filter-config-bundle never emitted)
ai-gateway `extensionManager` missing on the EnvoyGateway HelmRelease, and/or
no `GatewayConfig` + `aigateway.envoyproxy.io/gateway-config` annotation on the
Gateway → the ext-proc filter-config-bundle is never emitted → empty route
table → ext_proc cannot route → 500.
Signature: controller log lacks `found GatewayConfig for Gateway` /
`inserting AI Gateway extproc filter into listener`; ext_proc stats show
`streams_failed > 0` or UDS cluster `ai-gateway-extproc-uds` is unhealthy
(`cx_connect_fail > 0`). Fix: wire `extensionManager` (ai-gateway-controller:1063,
xdsTranslator hooks) + `GatewayConfig` (`extProc: {}`) + annotation. (PR #1875.)

### 2. In-processor routing decision 500 (residual)
Wiring healthy, but ai-gateway returns an ImmediateResponse 500 — the
per-route `direct_response: 500` placeholder fires because the processor's
route/backend selection failed for that model.
Signature: ext_proc stats `streams_started == streams_closed`,
`streams_failed == 0`; UDS cluster `health_flags::healthy`,
`cx_connect_fail: 0`. All `AIServiceBackend`/`BackendSecurityPolicy` may be
`Accepted=True`. Means the model's priority-0 backend target is unreachable,
the API key is unresolved, or the model is absent from the bundle.

### 3. ext-proc workload never deployed (cross-namespace Gateway/Envoy trap)
Symptom is a **gRPC error 14**, NOT `direct_response`: Envoy access log shows
`response_code_details: ext_proc_error_gRPC_error_14 ... No such file or
directory ... /etc/ai-gateway-extproc-uds/run.sock` — the ext-proc **UDS
socket is absent**, so ext-proc never starts. The extproc filter IS in the
listener (`inserting AI Gateway extproc filter` in controller logs), so the
*emission* wiring (Cause #1) is fine; the *workload* is missing.
Root cause: ai-gateway v1.1.0 finds the Envoy data-plane Deployment by
**namespace-scoping its search to the Gateway's namespace**. With the Gateway
in `shikanime` but the Envoy data plane in `envoy-system`
(`envoy` HelmRelease `targetNamespace: envoy-system`), the controller loops on
`No pods, deployments or daemonsets found for the Gateway {namespace: shikanime,
name: inference}` and never injects the ext-proc init container. Trigger:
deleting `inference-shikanime` (render-source Opaque Secret) or the projected
bundle `inference-shikanime-<hash>` — ai-gateway won't re-render on any
reconcile (initial-sync only). Fix: co-locate Gateway + Envoy in one namespace
(`envoy-system`) so the initial sync re-injects ext-proc; see SKILL.md
"ext-proc not injected: cross-namespace Gateway/Envoy trap".

## Diagnostic commands (data-plane is distroless — use admin API)

```bash
# probe HTTP listener (data-plane svc is `inference` in envoy-system)
kubectl port-forward -n envoy-system svc/inference 8080:80
curl -s -o /dev/null -w 'HTTP=%{http_code}\n' -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" -H "x-ai-eg-model: z-ai/glm-5.3-flash" \
  -d '{"model":"z-ai/glm-5.3-flash","messages":[{"role":"user","content":"hi"}]}'
# HTTP 404 on GET / = listener OK; 500 on chat = ext-proc decision.

# port-forward envoy admin
kubectl port-forward -n envoy-system pod/<envoy-shikanime-inference-*> 19000:19000

# ext_proc stream health (listener http.http-10080 / https.https-10443)
curl -s localhost:19000/stats | grep 'ext_proc'   # streams_started/closed/failed
# UDS cluster health
curl -s localhost:19000/clusters | grep ai-gateway-extproc-uds  # cx_connect_fail, health_flags

# the per-route 500 placeholder (normal when ext_proc fails to inject upstream)
curl -s localhost:19000/config_dump   # route httproute/shikanime/default/rule/0 has direct_response:500

# bundle is a SECRET (not ConfigMap), in envoy-system (and envoy-gateway-system)
kubectl get secret -n envoy-system inference-shikanime-<hash>[-part-000] \
  -o jsonpath='{.data.chunk}' | base64 -d   # backends + modelNameOverride list
```

## Notes
- ext-proc container admin (`:1064`) returns 404 on `/v1/config` — not useful;
  use Envoy `:19000` admin instead.
- `x-ai-eg-model` MUST match a real route. `tencent/hy3:free` has no local floor
  (catch-all → nous remote; nous returns x402 for free models). `z-ai/glm-5.3-flash`
  is the correctly-keyed rule. A model with no matching rule also yields the 500.
- Healthy WASM + empty 500 ⇒ decode the bundle, check the priority-0 backend
  target + BSP secret key (`apiKey` data key, literal), not the wiring.

### 4. Router-level ext_proc filter missing (gRPC error 13 — listener hook off)
Symptom is a **gRPC error 13**, mid-request: Envoy access log shows
`response_code_details: ext_proc_error_gRPC_error_13{missing_internal_request_ID_header_from_router_filter{via_upstream}}`
with a REAL `upstream_cluster` (traffic reaches the provider IP, e.g. openrouter
104.26.x) — so wiring (Cause #1) and workload (Cause #3) are fine; it dies inside
ext-proc. Reproduce on demand: any `POST /v1/chat/completions` → 500, duration 1–12ms.
Root cause (verified 2026-08, ai-gateway v1.1.0 + EG v1.9.0): the router-level
`envoy.filters.http.ext_proc/aigateway` filter is inserted by ai-gateway's
`PostTranslateModify` → `insertRouterLevelAIGatewayExtProc`, which only runs when
EG sends listener IR (`xdsTranslator.translation.listener.includeAll: true`).
With `includeAll: false` (manifests #1942, chosen to protect syncthing's TCP/UDP
listeners — see SKILL.md "Listener-hook toggle"), the filter is absent from the
443 HCM chain while the CLUSTER-level filter still exists; the upstream leg then
demands the `x-envoy-aigateway-internal-req-id` header that only the router leg
mints (`internal/extproc/server.go:184`) and fails gRPC 13.
Discriminate in seconds via Envoy admin config_dump: the 443 HCM `http_filters`
must contain `envoy.filters.http.ext_proc/aigateway` (anywhere before `router`);
Cause #4 = it is missing while cluster-level `http_filters` still show it.
Fix: restore `listener.includeAll: true` (requires the upstream findHCM
skip-non-HTTP-chains fix, or no TCP/UDP Gateways on the shared EG) — the toggle
is either/or between syncthing and inference on one control plane.

```bash
# HCM filter-chain check (the Cause #4 discriminator)
kubectl -n envoy-gateway-system port-forward pod/<envoy-shikanime-inference-*> 19100:19000
curl -s localhost:19100/config_dump | python3 -c "
import json,sys
for cfg in json.load(sys.stdin)['configs']:
    if 'ListenersConfigDump' in cfg.get('@type',''):
        for dl in cfg.get('dynamic_listeners',[]):
            st=dl.get('active_state') or {}
            l=st.get('listener',{})
            port=l.get('address',{}).get('socket_address',{}).get('port_value')
            for fcm in l.get('filter_chains',[]):
                for f in fcm.get('filters',[]):
                    h=f.get('typed_config',{})
                    if 'HttpConnectionManager' in str(h.get('@type','')):
                        print(port,[x.get('name') for x in h.get('http_filters',[])])
"
# healthy: [... 'envoy.filters.http.ext_proc/aigateway' ... 'envoy.filters.http.router']
# Cause #4: [... credential_injector×N, 'envoy.filters.http.router'] with no ext_proc
```
