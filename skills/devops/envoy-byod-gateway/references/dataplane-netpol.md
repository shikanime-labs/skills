# Envoy dataplane namespace + NetworkPolicy verification

The single most common silent failure when wiring a BYOD Envoy Gateway is a
wrong `namespaceSelector` in the app's `NetworkPolicy`. Because
`clusters/nishir/base/netpol.yaml` is `podSelector: {}` + **Ingress default-deny**,
any netpol that selects the app pod turns into a deny-all for unlisted sources —
with no error. A wrong namespace means "gateway cannot reach app" = protocol
timeouts, not a clear signal.

## Verify the dataplane namespace before trusting any netpol

Do NOT assume the dataplane lands in the Gateway's namespace. In this repo the
Gateway + EnvoyProxy are in `shikanime`, but EG deploys the proxy pods into the
**EG controller's `targetNamespace`** (`envoy-system`, set by
`infrastructure/envoy/base/hr.yaml`). The `Gateway.metadata.namespace` ≠ dataplane
namespace.

```sh
ctx=nishir-k8s-operator.taila659a.ts.net
# Every envoy dataplane pod: ns + owning-gateway (decisive)
kubectl --context "$ctx" get pods -A -l 'app.kubernetes.io/name=envoy' \
  -o custom-columns='NS:.metadata.namespace,POD:.metadata.name,OWNER:.metadata.labels.gateway\.envoyproxy\.io/owning-gateway-name' --no-headers
# Drill down to the gateway you care about
kubectl --context "$ctx" get pods -A -l 'app.kubernetes.io/name=envoy' -o json \
  | python3 -c "import sys,json; d=json.load(sys.stdin); \
[print(p['metadata']['namespace'],'|',p['metadata']['name']) for p in d['items'] \
 if p['metadata']['labels'].get('gateway.envoyproxy.io/owning-gateway-name')=='<gateway>']"
```

The correct netpol ingress rule (verified live for syncthing):

```yaml
ingress:
  - from:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: envoy-system   # EG controller ns, NOT shikanime
        podSelector:
          matchLabels:
            app.kubernetes.io/name: envoy                 # EG dataplane label
    ports: [{ port: http }, { port: sync }, { port: sync-udp }]
  - from:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: monitoring-system
        podSelector:
          matchLabels:
            app.kubernetes.io/name: vmagent
    ports: [{ port: metrics }]
```

## Do NOT add tailscale-system to the netpol

Tailscale (`tailscale-system`) only *programs* the Envoy `LoadBalancer` Service
(BYOD LB class). It never sources pod-to-pod traffic. A
`tailscale-system → app-pod` ingress allow permits a hop that does not occur —
inert dead weight. The real ingress path is:

```
tailscale LB (tailscale-system programs it)
  → envoy svc (shikanime, loadBalancerClass: tailscale)
  → envoy pod (envoy-system, label app.kubernetes.io/name: envoy)   ← covered by rule above
  → app pod (shikanime, ports http/sync/sync-udp)
```

## Multi-install / namespace smell

This cluster runs **two** EG installs:
- `envoy-system` — Flux-managed (`infrastructure/envoy` HelmRelease), holds the
  control plane AND the **syncthing** dataplane.
- `envoy-gateway-system` — **out-of-band**, unsupervised by Flux, holds the
  **inference** dataplane (the `inference` GatewayClass has no `parametersRef`,
  so it falls to that install's default namespace). The inference dataplane even
  forks across both namespaces.

If you ever touch the inference gateway's netpol, confirm which namespace its
dataplane is actually in (it may be `envoy-gateway-system`, unlike syncthing's
`envoy-system`). Recommendation: pin the `inference` GatewayClass to an
EnvoyProxy with `infra.namespace: envoy-system`, or remove the stray
`envoy-gateway-system` install — don't let inference depend on an unsupervized
namespace.
