# Custom domain within the tailnet (Envoy BYOD Gateway)

Proven recipe for exposing `<app>.example.com` to **tailnet devices only** via
a Tailscale BYOD Envoy Gateway. Source: Tailscale docs "Use custom domains with
Kubernetes Gateway API and Tailscale" + `inference.shikanime.studio` incident
(2026-08-30).

## What the name actually is

- BYOD Gateway device = `*.ts.net` hostname (MagicDNS, tailnet-only).
- Custom domain = a *second* name that resolves inside the tailnet via Split
  DNS → internal resolver. It is NOT public internet.

## Manifests (minimum, one domain — no external-dns)

**Component `internal-dns`** (Flux Kustomization `infrastructure-internal-dns`,
path `./infrastructure/internal-dns/overlays/nishir`, `prune: true`):

```yaml
# infrastructure/internal-dns/base/coredns.yaml
apiVersion: v1
kind: Namespace
metadata: { name: internal-dns }
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: coredns, namespace: internal-dns, labels: { app.kubernetes.io/name: coredns } }
spec:
  replicas: 2
  selector: { matchLabels: { app.kubernetes.io/name: coredns } }
  template:
    metadata: { labels: { app.kubernetes.io/name: coredns } }
    spec:
      containers:
        - name: coredns
          image: cgr.dev/chainguard/coredns:latest
          args: [ "-conf", "/etc/coredns/Corefile" ]
          ports:
            - { containerPort: 53, name: dns, protocol: UDP }
            - { containerPort: 53, name: dns-tcp, protocol: TCP }
          volumeMounts: [ { name: config, mountPath: /etc/coredns } ]
      volumes: [ { name: config, configMap: { name: coredns, items:
          [ { key: Corefile, path: Corefile }, { key: zones, path: zones } ] } } ]
---
apiVersion: v1
kind: Service
metadata:
  name: coredns
  namespace: internal-dns
  annotations: { tailscale.com/hostname: internal-dns, tailscale.com/expose: "true" }
spec:
  type: LoadBalancer
  loadBalancerClass: tailscale
  selector: { app.kubernetes.io/name: coredns }
  ports:
    - { name: dns, port: 53, targetPort: 53, protocol: UDP }
    - { name: dns-tcp, port: 53, targetPort: 53, protocol: TCP }
```

```yaml
# infrastructure/internal-dns/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: coredns, namespace: internal-dns }
data:
  Corefile: |
    .:53 { errors health ready file /etc/coredns/zones example.com }
  zones: |
    example.com. IN SOA internal-dns.example.com. admin.example.com. 1 7200 3600 1209600 3600
    example.com. IN NS internal-dns.example.com.
    app.example.com. IN A 100.103.240.115
    app.example.com. IN AAAA fd7a:115c:a1e0::ca2b:f074
```
`kustomization.yaml` in base + overlay: `apiVersion:
kustomize.config.k8s.io/v1beta1` (v1alpha1 is REJECTED for plain kustomizations).

## Wire the Gateway listener + cert (unchanged from base pattern)

`apps/<app>/overlays/nishir-tailnet/gateway.yaml`: listener `name: https`,
`protocol: HTTPS`, `port: 443`, `hostname: app.example.com`,
`tls.certificateRefs[0].name: app-example-com-tls`.
`cert.yaml`: `Certificate` from the cluster `ClusterIssuer` (LE staging/prod via
Cloudflare DNS-01), `dnsNames: [app.example.com]`, `secretName:
app-example-com-tls`.

## The one manual step (cluster cannot do it)

Tailscale Split DNS — console: DNS → Add nameserver → Custom →
`<internal-dns tailnet IP>` → Restrict to search domain → `example.com`.
The IP is the resolver's tailnet address (from `tailscale status --json` after
deploy). Without this, tailnet devices query public DNS for `example.com` and
NXDOMAIN.

## Verification (tailnet device)

```sh
RESOLVER_IP=$(tailscale status --json | python3 -c "import sys,json;print([p['TailscaleIPs'][0] for p in json.load(sys.stdin)['Peer'].values() if p['HostName']=='internal-dns'][0])")
dig +short @$RESOLVER_IP app.example.com        # → 100.103.240.115
curl -sv https://app.example.com/v1/models      # → 200, SAN-matched LE cert
```
Off-tailnet: `curl` times out by design (CGNAT). That is correct for
tailnet-only exposure.

## Gotchas

- `kubectl get svc … -o jsonpath='{.status.loadBalancer.ingress[0]}'` returns
  `{"hostname": …}` not the IP. Get the IP from `tailscale status --json`
  (`Peer[].TailscaleIPs[0]`) or the `ts-<app>-*` proxy Secret. It is stable.
- `file` zone is authoritative for `example.com` ONLY. Add `forward .
  /etc/resolv.conf` to the Corefile if the resolver must also recurse.
- Cloudflare token secret: generate it in the cert-manager nishir overlay as
  `cloudflare-api-token` (ns `cert-manager`) so the ClusterIssuer reads it
  same-namespace — avoids the cross-namespace `apiTokenSecretRef` footgun.
- `bitnamicharts/external-dns` OCI pull now 401s (Bitnami gates OCI). For one
  domain, the static CoreDNS zone replaces it entirely — do not fight auth.
