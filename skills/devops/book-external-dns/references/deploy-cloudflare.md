# ExternalDNS on Cloudflare

Distilled from docs/tutorials/cloudflare/. Use ExternalDNS ≥ 0.4.2 for this provider.

## Credentials

- API Token preferred if `CF_API_TOKEN` is set; else `CF_API_KEY` + `CF_API_EMAIL`.
- Token via file: `CF_API_TOKEN="file:/path/to/token"` (whitespace trimmed).
- Token grants: Zone `Read`, DNS `Edit`, access `All zones`.
- When scoping token to specific zones, also pass `--zone-id-filter` so API only hits those zones.
- Create secret (no trailing newline):
  `printf '%s' "$CF_API_TOKEN" | kubectl create secret generic cloudflare-api-key --from-file=apiKey=/dev/stdin`

## Deploy via Helm

Chart repo: `https://kubernetes-sigs.github.io/external-dns/`.

```yaml
# values.yaml
provider:
  name: cloudflare
env:
  - name: CF_API_TOKEN
    valueFrom:
      secretKeyRef:
        name: cloudflare-api-key
        key: apiKey
```

```bash
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm repo update
helm upgrade --install external-dns external-dns/external-dns --values values.yaml
```

## Deploy via manifest (RBAC-enabled)

RBAC needs: `services`,`pods` (get/watch/list); `discovery.k8s.io/endpointslices`
(get/watch/list); `extensions`,`networking.k8s.io/ingresses` (get/watch/list); `nodes`
(list,watch). ServiceAccount + ClusterRole + ClusterRoleBinding + Deployment.

Deployment args (Cloudflare subset):

```text
--source=service            # ingress also possible
--policy=upsert-only        # NOTE: never deletes; use --policy=sync to delete
--domain-filter=example.com # limit to zone; change to match yours
--zone-id-filter=023e105f...# optional, specific zone
--provider=cloudflare
--cloudflare-proxied        # optional: enable Cloudflare proxy (DDOS/CDN)
--cloudflare-dns-records-per-page=5000  # optional
--cloudflare-regional-services           # optional
--cloudflare-region-key="eu"            # optional
--cloudflare-record-comment="provisioned by external-dns"  # <=100 free / <=500 paid
```

Image: `registry.k8s.io/external-dns/external-dns:v0.22.0` (pin a version).

## Per-ingress overrides (annotations)

- `external-dns.kubernetes.io/cloudflare-proxied: "true"` — override global `--cloudflare-proxied`.
- `external-dns.kubernetes.io/cloudflare-region-key` — region for that record (`eu`,`us`,`ap`,`fedramp`,`in`,`ca`,`jp`,`kr`,`br`,`za`,`ae`); empty = no regional hostname. Needs SuperAdmin/Admin.
- `external-dns.kubernetes.io/cloudflare-custom-hostname: <h1>,<h2>` — Cloudflare for SaaS custom
  hostnames (needs `--cloudflare-custom-hostnames`; HTTP validation requires the custom hostname to
  resolve to the external-dns record; TXT method unsupported).
- `external-dns.kubernetes.io/cloudflare-tags: "owner:frontend-team, env:dev"` — comma `key:value` tags.

## Throttling & batch

- Cloudflare global rate limit: 1,200 requests / 5 min. Many fast-polling instances hit it.
- Mitigation: high `--cloudflare-dns-records-per-page` (max 5000); tune `--batch-change-size`
  (default 200) and `--batch-change-interval` (default 1s).
- Batch API is transactional per chunk; on chunk failure Cloudflare rolls back and ExternalDNS
  retries each record individually. CAA and similar unsupported-by-batch types always submitted
  individually. SRV records use Cloudflare's structured SRV fields.

## Service example

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  annotations:
    external-dns.kubernetes.io/hostname: example.com   # or www.example.com
    external-dns.kubernetes.io/ttl: "120"              # optional; >=120 valid
spec:
  type: LoadBalancer
  ports: [{protocol: TCP, port: 80, targetPort: 80}]
```

For Cloudflare proxied entries set TTL to `1` (automatic) or omit it. Removing the hostname
annotation makes ExternalDNS delete the record.

## SRV via CRD

Cloudflare needs structured SRV (`priority weight port target`). DNSEndpoint accepts standard
`<priority> <weight> <port> <target>` and converts. Example in upstream tutorial.

## Verify & cleanup

- Dashboard: Cloudflare DNS zone shows the Service external IP as the A record.
- `dig +short example.com` returns the LB IP.
- Cleanup: `kubectl delete -f nginx.yaml` and the external-dns manifest.
