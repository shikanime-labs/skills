# ExternalDNS Overview, Providers & Sources

Distilled from kubernetes-sigs.github.io/external-dns (README + sources/ + FAQ).

## What it does

ExternalDNS is a Kubernetes controller that synchronizes exposed Services, Ingresses, and
Gateway API routes into DNS provider records. It is NOT a DNS server — it only configures
provider APIs (Route 53, Cloudflare, Google Cloud DNS, etc.).

- Pulls desired records by watching K8s resources via the API (like KubeDNS, but outbound).
- By default aware of records it manages (ownership registry) → safe on non-empty zones.
- Runs in-cluster as a control loop, or locally for validation (`--once --dry-run`).

## Providers

Two tiers. No new **in-tree** providers are accepted — new ones MUST use the webhook system.

### In-tree (built-in, some seeking maintainers)

Alibaba Cloud, AWS Cloud Map, AWS Route 53, AzureDNS, Azure Private DNS, Civo, Cloudflare,
CoreDNS, DNSimple, Exoscale, Gandi, GoDaddy, Google Cloud DNS, Linode, NS1, OCI DNS,
OVHcloud, Pi-hole, PowerDNS, RFC2136, Scaleway. (IBM Cloud, TencentCloud, UltraDNS moved
out-of-tree as of v0.20.0.)

### Webhook (out-of-tree, community-maintained, unvetted by maintainers)

Examples: Hetzner, IONOS, Infoblox, Netcup, Porkbun, STACKIT, Tencent Cloud, Vultr, Yandex,
deSEC, Gcore, GleSYS, Namecheap, Unifi. Use at your own risk. A webhook provider is a separate
container/pod ExternalDNS calls over HTTP (`provider.webhook.*` in the Helm chart).

## Sources (K8s objects ExternalDNS watches)

| Source | Notes |
| --- | --- |
| service | `type=LoadBalancer`, `ExternalName`, `NodePort`, headless hostPort |
| ingress | `networking.k8s.io` Ingresses |
| gateway-httproute / gateway-*route | Gateway API routes (annotation placement per type) |
| crd | `DNSEndpoint` CRD for declarative records |
| pod, node | Pod/Node addresses |
| istio-gateway, istio-virtualservice | Istio |
| traefik-proxy | Traefik IngressRoute |
| contour-httpproxy, gloo-proxy, kong-tcpingress, skipper-routegroup | ingress controllers |
| ambassador-host, openshift-route, f5-virtualserver, f5-transportserver | others |
| unstructured | custom CRDs |
| fake | testing |

Configure with one or more `--source=` flags. Only enable sources whose CRDs/RBAC are
present on the target cluster (see operational-best-practices).

## DNS record types managed

Default: `A`, `AAAA`, `CNAME`. Enable others via `--managed-record-types` (e.g. `SRV`,
`NS`, `TXT`, `DNAME`). Not all providers support every type (e.g. `DNAME` only on Gandi,
NS1, OCI, PowerDNS, Scaleway, RFC2136 backends; rejected by Route 53/Azure/Google/Cloudflare).

## Compatibility

### Kubernetes version

- ExternalDNS ≥ 0.18.x: supports K8s ≥ 1.21 and ≥ 1.22–1.32.
- ExternalDNS ≥ 0.18.x: K8s ≥ 1.33 supported; ≤ 0.9.x dropped.
- v0.18.0 moved to `discovery.k8s.io/endpointslices` (RBAC on `endpointslices` required).
- v0.19.0: no longer exposes internal IPv6 by default; legacy `traefik.containo.us` listeners disabled.

### Architecture

- Official images: `registry.k8s.io/external-dns/external-dns:<version>` (no `latest` tag).
- Supported: `amd64`, `arm32v7`, `arm64v8` (from v0.7.5).
- OS: GNU/Linux only; no Windows support.

## Registries (who owns a record)

`--registry=txt` (default, TXT ownership records), `aws-sd`, `dynamodb`, `noop`. Use `txt`
for safe co-existence with other actors in a zone. Set `--txt-owner-id` unique per cluster.
