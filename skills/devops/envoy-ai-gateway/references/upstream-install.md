# Upstream Install & First Request (Envoy AI Gateway)

Source: aigateway.envoyproxy.io/docs — getting-started/{prerequisites,installation,
basic-usage,connect-providers/openai}. Verbatim commands from upstream.

## Prerequisites
- `kubectl`, `helm`, `curl`.
- Kubernetes **>= 1.32** (server version must show 1.32+).
- Envoy Gateway **>= 1.8.1** (AI Gateway is built on it). Use a clean EG
  deployment; existing EG with custom config may conflict.

## Step 0: Install Envoy Gateway (with AI Gateway values)
```shell
helm upgrade -i eg oci://docker.io/envoyproxy/gateway-helm \
  --version v1.8.1 \
  --namespace envoy-gateway-system --create-namespace \
  -f https://raw.githubusercontent.com/envoyproxy/ai-gateway/main/manifests/envoy-gateway-values.yaml
kubectl wait --timeout=2m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available
```
Addon values (pass alongside the base `-f`) for extra features:
- Rate limiting: `-f .../examples/token_ratelimit/envoy-gateway-values-addon.yaml`
- InferencePool: `-f .../examples/inference-pool/envoy-gateway-values-addon.yaml`

## Step 1: Install AI Gateway CRDs
```shell
helm upgrade -i aieg-crd oci://docker.io/envoyproxy/ai-gateway-crds-helm \
  --version v1.1.0 --namespace envoy-ai-gateway-system --create-namespace
```

## Step 2: Install AI Gateway controller
```shell
helm upgrade -i aieg oci://docker.io/envoyproxy/ai-gateway-helm \
  --version v1.1.0 --namespace envoy-ai-gateway-system --create-namespace
kubectl wait --timeout=2m -n envoy-ai-gateway-system deployment/ai-gateway-controller --for=condition=Available
```
Upgrade note: if previously installed with only `ai-gateway-helm`, install the
CRD chart with `--take-ownership` first, then upgrade the main chart.

## Basic usage (mock backend)
```shell
kubectl apply -f https://raw.githubusercontent.com/envoyproxy/ai-gateway/main/examples/basic/basic.yaml
kubectl wait pods --timeout=2m -l gateway.envoyproxy.io/owning-gateway-name=envoy-ai-gateway-basic -n envoy-gateway-system --for=condition=Ready
export GATEWAY_URL=$(kubectl get gateway/envoy-ai-gateway-basic -o jsonpath='{.status.addresses[0].value}')
# or port-forward: kubectl port-forward -n envoy-gateway-system svc/$ENVOY_SERVICE 8080:80
```
Test endpoints (OpenAI-compatible): `/v1/chat/completions`, `/v1/completions`,
`/v1/embeddings`, `/cohere/v2/rerank`. `model: some-cool-self-hosted-model`
returns a mock response until a real backend is wired.

### Buffer / HTTP/2 gotcha (verbatim from upstream)
EG defaults `bufferLimit` to 32KB — too small for AI responses. The example
sets **50Mi** via `ClientTrafficPolicy`. Over HTTP/2 also raise
`initialStreamWindowSize: 16Mi` and `initialConnectionWindowSize: 24Mi`, or you
get `413 request_payload_too_large` even after the buffer limit is raised.

## Connect a real provider (OpenAI example)
```shell
curl -O https://raw.githubusercontent.com/envoyproxy/ai-gateway/main/examples/basic/openai.yaml
# edit openai.yaml: replace OPENAI_API_KEY placeholder
kubectl apply -f openai.yaml
kubectl wait pods --timeout=2m -l gateway.envoyproxy.io/owning-gateway-name=envoy-ai-gateway-basic -n envoy-gateway-system --for=condition=Ready
# test
curl -H "Content-Type: application/json" -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hi."}]}' $GATEWAY_URL/v1/chat/completions
```
Add more models by adding `AIGatewayRouteRule`s with `x-ai-eg-model` header
`value` matches. Credential updates are picked up automatically in a few seconds.

## When to load this file
- First-time install, or reproducing the upstream quickstart verbatim.
- Debugging 413 / buffer-limit / HTTP/2 window issues.
