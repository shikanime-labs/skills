# ExternalDNS Annotations

Distilled from docs/annotations/annotations/. Annotations override CLI flags and defaults
for the resource they're on (except on `DNSEndpoint`, where they're ignored). Filter flags
(`--source`, `--service-type-filter`, `--*-filter`) define scope, not per-resource overrides.

## Source support matrix

| Source | controller | hostname | internal-hostname | target | ttl | provider-specific |
| --- | --- | --- | --- | --- | --- | --- |
| Ambassador | | | | Yes | Yes | Yes |
| Contour | Yes | Yes¹ | | Yes | Yes | Yes |
| CRD | | | | | | |
| F5 | | | | Yes | Yes | |
| Gateway | Yes | Yes¹ | | Yes⁴ | Yes | Yes |
| Gloo | | | | Yes | Yes⁵ | Yes⁵ |
| Ingress | Yes | Yes¹ | | Yes | Yes | Yes |
| Istio | Yes | Yes¹ | | Yes | Yes | Yes |
| Kong | | Yes¹ | | Yes | Yes | Yes |
| Node | Yes | | | Yes | Yes | |
| OpenShift | Yes | Yes¹ | | Yes | Yes | Yes |
| Pod | | Yes | Yes | Yes | | |
| Service | Yes | Yes¹ | Yes¹² | Yes³ | Yes | Yes |
| Skipper | Yes | Yes¹ | | Yes | Yes | Yes |
| Traefik | | Yes¹ | | Yes⁶ | Yes | Yes |

¹ Unless `--ignore-hostname-annotation`. ² Only differs from `hostname` for `ClusterIP`/`LoadBalancer`.
³ Also on Pods referenced from headless Service Endpoints. ⁴ Gateway API annotation placement varies by type.
⁵ Must be on the listener's `VirtualService`. ⁶ Traefik CRDs need explicit `target`; no LB IP in status.

## Annotation semantics

### `external-dns.kubernetes.io/hostname`

Additional/override domains for the resource's records. Comma-separated for multiple
(`svc.a.com,svc.b.com`). For Pods uses PodIP (or NodeExternalIP/NodeInternalIP if
`hostNetwork: true`). Must match `--domain-filter`. Alpha — subject to change.

### `external-dns.kubernetes.io/internal-hostname`

Internal network domain. For `LoadBalancer` Services → Service `ClusterIP`; for Pods →
`Status.PodIP`. Needs `--publish-internal-services` if the Service isn't ClusterIP/LoadBalancer.

### `external-dns.kubernetes.io/target`

Force the record target (IP or hostname). A hostname target creates a CNAME. Supported on
Services, Ingresses, Pods (headless), Gateways. Use when ExternalDNS can't auto-discover the
ingress controller endpoint.

### `external-dns.kubernetes.io/ttl`

Record TTL in seconds (string) or Go duration (`1m`, `1h2m11s`). Positive integer. Default 0.
Overrides `--min-ttl` only when annotation is set and `>0`. Requires `hostname` set and
provider/source support (see advanced-features TTL table).

### `external-dns.kubernetes.io/access`

For `NodePort` Services: `public` → Node `ExternalIP` (+IPv6 `InternalIP`); `private` →
Node `InternalIP`. Absent + any `ExternalIP` present → public; else private.

### `external-dns.kubernetes.io/controller`

If present and not `dns-controller`, the source ignores the resource.

### `external-dns.kubernetes.io/endpoints-type`

For headless Services: `NodeExternalIP` (needs `--service-type-filter=ClusterIP` and
`Node`, or no filter) uses Pod Node's `ExternalIP` (+IPv6 `InternalIP`); `HostIP` uses
Pod `Status.HostIP`. Otherwise uses Service Endpoints addresses.

### `external-dns.kubernetes.io/ingress-hostname-source`

For Ingress only: `defined-hosts-only` (use spec only), `annotation-only` (use annotations
only), or unset (both, union). Use `annotation-only` + remove annotation, or `defined-hosts-only`,
to stop an Ingress claiming a hostname during migration.

### `external-dns.kubernetes.io/ingress`

For Istio/GlooEdge Gateways without a public IP: names an Ingress resource whose LoadBalancer
IP becomes the target (the Gateway's own ClusterIP is ignored).

### Provider-specific (use the instance's `--annotation-prefix`)

- `cloudflare-proxied: "true"` — per-record Cloudflare proxy override.
- `cloudflare-region-key` — per-record regional services region (`eu`,`us`,`ap`,`fedramp`,`in`,`ca`,`jp`,`kr`,`br`,`za`,`ae`).
- `cloudflare-custom-hostname` — comma-separated custom hostnames.
- `cloudflare-tags` — comma-separated `key:value` tags.
- `aws-alias: "true"` — force AWS ALIAS.
- `set-identifier` — set identifier for same domain+type with routing policy (alpha).

## Two sources, same hostname

When two sources emit the same DNS name with different targets, ExternalDNS keeps the record on
whichever acquired it first and ignores the competitor (prevents flapping). To migrate a
hostname, make the OLD source stop emitting it entirely (remove from `spec.rules[].host` and/or
the hostname annotation) — the record hands to the remaining source on next reconcile, no manual
deletion needed.
