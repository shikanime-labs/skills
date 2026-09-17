# Verify a Tailscale-Envoy public endpoint (in-cluster, when external curl fails)

## When this applies
You published an app at a public DNS name (e.g. `inference.shikanime.studio`) via a
Tailscale `loadBalancerClass` Envoy Gateway, but `curl` from off-cluster returns
`000` / timeout / connection-reset while the Gateway shows `Programmed=True`. The
failure is usually **routing** (the Service external IP is a private tailnet VIP), not a
listener/cert defect. Prove the gateway itself is sound before touching manifests.

## Step 1 — locate the data-plane ClusterIP
The Envoy Service is named after the Gateway, in the EG data-plane namespace
(`envoy-gateway-system` post-split; old `envoy-system` is orphaned).
```sh
CTX=nishir-k8s-operator.taila659a.ts.net
kubectl config use-context $CTX
kubectl -n envoy-gateway-system get svc inference -o wide   # ClusterIP + EXTERNAL-IP
kubectl -n envoy-gateway-system get svc inference -o jsonpath='{.status.loadBalancer}'
```
`status.loadBalancer.ingress[]`: `hostname` = MagicDNS, `ip` (ipMode VIP) = the tailnet
device IP. Both are private (`100.64.0.0/10`) — **NOT internet-routable**.

## Step 2 — prove listener + cert in-cluster (authoritative)
Run a `nicolaka/netshoot` pod in the **Gateway's own namespace** (`shikanime`) — it is
NOT under PodSecurity "restricted", so a root image runs (the EG namespace IS
restricted and rejects it). TLS-handshake to the ClusterIP with the public SNI:
```sh
kubectl -n shikanime run curltest --rm -i --restart=Never --image=nicolaka/netshoot -- \
  sh -c 'echo | openssl s_client -connect 10.111.44.220:443 -servername inference.shikanime.studio'
```
Success = `CONNECTION ESTABLISHED` + `Peer certificate: CN=inference.shikanime.studio`.
That proves the listener, route host match, and LE cert are correct — independent of
external reachability and of pod-egress NetworkPolicy (which otherwise makes an HTTP
`curl` from a probe pod return `000`).

## Step 3 — characterise the external failure
From a tailnet host (the Mac is on tailnet):
```sh
nc -z -w5 -G5 100.103.240.115 443 && echo OPEN          # TCP usually opens
curl -sv -m30 https://100.103.240.115/v1/models \
  --resolve inference.shikanime.studio:443:100.103.240.115
```
- TCP **open** but `curl` = `Recv failure: Connection reset by peer` (TLS reset) → the
  Tailscale proxy VIP isn't delivering TLS to Envoy. The gateway is fine; fix the proxy
  wiring or bridge via a Cloudflare Tunnel (`cloudflared`) to the `https-public` listener.
- `dig inference.shikanime.studio` → the tailnet VIP → Cloudflare cannot proxy a private
  IP, so `proxied:false` (DNS-only) is mandatory, and the public name is only reachable
  where the tailnet VIP routes (other tailnet nodes, not the open internet).

## Gotchas
- Don't conclude "gateway broken" from a `000` probe pod — pod-egress NetworkPolicy to
  the Gateway Service blocks HTTP, but the listener is healthy (Step 2 proves it).
- Don't run debug pods in `envoy-gateway-system`: PodSecurity "restricted" rejects
  `nicolaka/netshoot` (root) and `curlimages/curl` (named user `curl_user` fails
  `runAsNonRoot`). Probe from the Gateway namespace, or set a full restricted
  securityContext on a numeric-UID image:
  `runAsUser`/`runAsGroup` numeric, `runAsNonRoot: true`,
  `seccompProfile: {type: RuntimeDefault}`, `allowPrivilegeEscalation: false`,
  `capabilities.drop: [ALL]`.
- Envoy container is distroless (no `sh`/`ss`) — verify via the Service ClusterIP or
  Envoy admin port-forward, never `kubectl exec -c envoy -- sh`.

## 404 from the gateway is often CORRECT — read Envoy access logs first

A bare `curl https://<app>.taila659a.ts.net/` returning 404 with
`content-length: 0` does NOT mean routing broke. The decisive check is Envoy's
own access log — it names the verdict:

```sh
kubectl -n envoy-gateway-system logs deploy/envoy-<ns>-<gateway>-<hash> -c envoy \
  | jq -r 'select(.x_envoy_origin_path=="/") | .response_code_details'
# "route_not_found" + route_name=null → the route only matches other paths. Expected.
# "via_upstream" + route_name=httproute/... → traffic IS routing. 404 is from the app.
```

Two live-proven cases (Sept 2026):
- **matrix/synapse**: the HTTPRoute matches only `/_matrix/*` paths, so `/`
  returns `route_not_found` 404 by design while all real Matrix traffic
  (`/_matrix/client/v3/sync` etc.) shows `via_upstream` 200 in the same log.
- **funnel ingress dialing :80**: when a Tailscale funnel Ingress's
  `defaultBackend.service.port.number` is `80` and the fleet's
  `<app>-redirect` HTTPRoute (301) also claims the tailnet hostname on the
  http listener, every funnel request lands on the redirect → infinite 301
  loop. Fix: point the ingress backend at `443` (the https listener where the
  content route matches). Applied fleet-wide in `infrastructure/envoy-gateway/
  overlays/nishir-tailnet/ingress.yaml` (PRs #2073/#2074); any NEW funnel
  ingress must dial 443 from day one.

Corollary: verify probes against a path the route actually matches
(`/.well-known/matrix/client`, `/hook`, the app's UI path), not `/`.
