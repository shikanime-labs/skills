# Inference gateway probe (nishir)

## Triage ladder: "Connection error" vs HTTP 000 vs 5xx

Three distinct failure layers — diagnose in this order:

1. **Connection error / 000 with TCP timeout** = DNS or reachability, NOT the
   gateway. Compare public DNS vs the live LB:

   ```bash
   dig +short inference.i.shikanime.studio @1.1.1.1
   kubectl -n envoy-gateway-system get svc inference \
     -o jsonpath='{.status.loadBalancer.ingress}'
   ```

   A mismatch (e.g. DNS says `100.103.240.115`, LB says `100.110.197.5`) is a
   stale/orphaned Cloudflare record — see the external-dns orphaned-record
   recipe in `book-external-dns` `references/orphaned-record-drift.md`.
   Verified 2026-09-03: `inference.i.shikanime.studio` served a dead VIP for
   days while the gateway itself was healthy.
2. **000 with TLS CertificateRequest abort** = mTLS required (below). The 000
   is the signal to present a client cert, not to retry.
3. **5xx** = read the Envoy access log (section below).

## The gateway enforces mTLS — bare probes return 000 by design

`inference` Gateway (ns `shikanime`) is fronted by `ClientTrafficPolicy inference`
which requires client-cert validation against `nishir-ca-certificates.crt`. A
probe that presents no client cert gets a **CertificateRequest** in the TLS
handshake and aborts → `curl` reports `000` with no body. This is NOT tailnet
flakiness and NOT a service outage — the envoy pod serves 200s to mTLS clients.

## Get the test client cert

A ready-made client identity lives in `Secret/inference-test-client-tls`
(ns `shikanime`, type `kubernetes.io/tls`):

```bash
kubectl --context nishir-k8s-operator.taila659a.ts.net -n shikanime \
  get secret inference-test-client-tls -o jsonpath='{.data.tls\.crt}' \
  | base64 -d > /tmp/inf-client.crt
kubectl --context nishir-k8s-operator.taila659a.ts.net -n shikanime \
  get secret inference-test-client-tls -o jsonpath='{.data.tls\.key}' \
  | base64 -d > /tmp/inf-client.key
```

## Probe recipe (Mac → localhost via port-forward)

The Tailscale LoadBalancer VIP (`svc/inference` in ns `envoy-gateway-system`;
live shape 2026-09-03: `100.110.197.5` / `inference-proxy.taila659a.ts.net`)
drops plain HTTP/2 probes from the Mac; use `kubectl port-forward` and force
HTTP/1.1. The envoy pod is distroless (no `sh`/`curl`) so `exec` probes are
impossible — port-forward from the Mac. NOTE: the namespace is
`envoy-gateway-system` on this cluster (older notes saying `envoy-system` are
wrong).

```bash
# background port-forward (envoy-gateway-system svc/inference 443 -> 9443)
kubectl --context nishir-k8s-operator.taila659a.ts.net -n envoy-gateway-system \
  port-forward svc/inference 9443:443 &
CERT="--cert /tmp/inf-client.crt --key /tmp/inf-client.key --cacert /tmp/inf-client.crt"
GW=https://localhost:9443
curl -sk --http1.1 -m20 $CERT "$GW/v1/models" -w '\nHTTP %{http_code}\n'
# MCP initialize example:
curl -sk --http1.1 -m20 $CERT -X POST "$GW/mcp/z-ai" \
  -H 'Content-Type: application/json' -w '\nHTTP %{http_code}\n' \
  --data @- <<'JSON'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
  "protocolVersion":"2024-11-05","capabilities":{},
  "clientInfo":{"name":"t","version":"1"}}}
JSON
```

- `--cacert` points at the client cert itself (same CA chain); the server's
  private CA is what the client must trust to complete the handshake.
- Use `--http1.1`: the gateway's HTTP/2 frontend is finicky from the Mac TLS
  stack even with a valid cert; HTTP/1.1 is reliable.

## Localizing a 500 on /mcp/<route> or /v1/*

Read the Envoy access log (`kubectl logs <envoy-pod> -n envoy-gateway-system
-c envoy --tail=N`; find the pod with
`-l gateway.envoyproxy.io/owning-gateway-name=<gw>`):

- `response_code_details: direct_response` + `upstream_cluster: null` → route
  matched but no upstream selected (backend/policy/secret not wired, route not
  attached to the Gateway, wrong path). Application layer never reached.
- `response_code_details: via_upstream` + `upstream_cluster: httproute/...` +
  `upstream_host: 127.0.0.1:9856` → request reached ai-gateway's MCP proxy; the
  500 originates inside ai-gateway (session creation / backend session).
- ai-gateway controller pod logs are often empty on success and failure; the
  Envoy access log is the primary signal.
- Also check `HTTPRoute .status.parents[].conditions` for
  `ResolvedRefs=False` — e.g. `PortNotFound: TCP 8080 not found on Service` when
  an LWS-created headless Service carries no `ports` (LWS only auto-creates the
  Service object, not its ports).

## Known defects (do not "fix" in manifests)

- **AIGatewayRoute parentRefs patch silently misses** (found 2026-09-03): the
  nishir kustomization JSON6902 patch that binds the `/v1` route to
  `Gateway/inference` targets `name: inference, kind: AIGatewayRoute`, but the
  actual AIGatewayRoute (from `apps/llama-cpp/base/aigatewayroute.yaml`) is
  named **`default`**. Kustomize silently skips a JSON6902 target that matches
  nothing — the AIGatewayRoute ships with no parentRefs, `/v1` is unrouted on
  the inference Gateway, and every `/v1/*` request 500s with
  `direct_response`/`upstream_cluster: null`. Fix: patch target
  `name: default`. Lesson: after any kustomize target rename, grep the RENDERED
  output (`kustomize build`) for the patched field — a missed target is silent,
  not an error.
- **`/mcp/z-ai` returns 500** (`failed to create MCP session to any backend`):
  ai-gateway **v1.1.0** MCP client omits the `Accept: application/json,
  text/event-stream` header that Z.ai's Spring WebFlux Streamable-HTTP servers
  require → Z.ai 400 → session create fails. Backend sub-routes
  (`ai-eg-mcp-br-z-ai-*`) DO reach `api.z.ai` with 200; only the main
  session-create route 500s. Tracked in `shikanime-labs/manifests#1894` (and
  issues #1874/#1884). Do NOT close those until `POST /mcp/z-ai` returns
  non-500. No manifest-level fix exists — the `Backend` CRD has no
  header-injection field.
- **OpenRouter key not injected (HTTP 404)**: `BackendSecurityPolicy/
  openrouter-key` targeted a non-existent `AIServiceBackend
  inference-openrouter` (renamed to `openrouter`). Fixed in PR
  `shikanime-labs/manifests#1898`. Sibling BSPs (`z-ai-key`, `mistral-key`,
  `nous-key`) target bare ASB names — match that convention.
- **llama-cpp pods Pending** (nodeSelector `minisforum-ms-s1` matches 0 nodes,
  kushira/sashina absent): `/v1` 500s via `direct_response` are expected while
  the backend floor is down — remote-provider tiers still work if routed.
- **Anthropic-schema backends unreachable via `/v1/*`** (verified 2026-09-05,
  source-level): ai-gateway v1.1.0 ships Anthropic→OpenAI translation
  (`anthropic_openai.go`) but NOT OpenAI→Anthropic (no `openai_anthropic.go`);
  `/v1/chat/completions` for a `schema: Anthropic` backend (z-ai) returns 500
  `unsupported API schema: backend={Anthropic api/anthropic/v1}{via_upstream}`.
  Reach such backends ONLY via `/anthropic/v1/messages`. No fixed release yet
  (v1.1.0 is latest); also api.z.ai OpenAI-compatible endpoint had zero
  balance (429 code 1113), so rerouting z-ai to `api/paas/v4` was not viable.
- **Client auth = gateway-issued `sk-infer` keys only** (verified 2026-09-05):
  keys from `Secret/inference-gateway-apikey` authenticate on BOTH `/v1` and
  `/anthropic` paths (x-api-key and Bearer both accepted); upstream provider
  keys (nous/z-ai/openrouter) 401 as client creds. Cloudflare in front of
  upstreams blocks bare python-urllib User-Agents (403 code 1010) — probe with
  curl or the native SDK. Free-pool models (laguna) intermittently 503 under
  saturation; instant retry usually clears.

## Quick health checks

```bash
kubectl -n shikanime get gateway inference -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status}'
kubectl -n envoy-gateway-system get pods -l app.kubernetes.io/name=ai-gateway
```
