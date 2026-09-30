# Orphaned DNS records: why external-dns --policy=sync leaves them forever

## The failure mode

external-dns only touches records it can prove it owns (via the TXT registry:
an ownership TXT next to each managed record). A record with **no ownership
TXT** is invisible to the reconciliation loop regardless of policy:

- `--policy=sync` will not update it (not ours)
- `--policy=sync` will not delete it (not ours)
- Log still ends with `All records are already up to date`

The record drifts forever while external-dns reports healthy. Verified
2026-09-03 on nishir: `inference.i.shikanime.studio` served a dead Tailscale
VIP (`100.103.240.115`, no matching peer, TCP connect timeout) for days. The
live LB was `100.110.197.5`. Sibling records (authelia, forgejo) also lacked
TXTs but happened to hold correct values — they were equally orphaned, just
not yet wrong. Likely cause: the ownership TXTs were lost when the
external-dns Deployment was recreated with a rotated Cloudflare token (token
secret is 3d old; records are 4d old). Deploy args for reference:
`--source=gateway-httproute --source=ingress --source=service --policy=sync
--registry=txt --txt-owner-id=nishir-external-dns --domain-filter=shikanime.studio
--provider=cloudflare`.

## Detection recipe

```bash
# 1. What does DNS say vs what does the cluster say?
dig +short <host> @1.1.1.1
kubectl -n envoy-gateway-system get svc <name> \
  -o jsonpath='{.status.loadBalancer.ingress}'

# 2. Does the record have an ownership TXT? (registry=txt)
# Secret key on nishir is `cloudflare_api_token` (NOT `api-token`).
TOKEN=$(kubectl --context nishir-k8s-operator.taila659a.ts.net \
  -n external-dns-system get secret cloudflare-api-token \
  -o jsonpath='{.data.cloudflare_api_token}' | base64 -d | tr -d '\n\r ')
ZONE=<zone-id>   # from GET /zones?name=<domain>
curl -s \
  "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records?name=<host>" \
  -H "Authorization: Bearer $TOKEN"
URL="https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records"
URL="$URL?name=<host>&type=TXT"
curl -s "$URL" \
  -H "Authorization: Bearer ***"    # count 0 = orphaned
```

Distinguishing signals:

- **TCP connect timeout** (curl exit before HTTP; nc refused/timed out; or
  `tailscale ping <ip>` → `no matching peer` for a stale tailnet IP) is a
  DNS-level fault — contrast with HTTP `000` after successful connect, which
  is the inference gateway's mTLS CertificateRequest, not DNS.
- Only SOME hosts broken, others fine: per-record drift, not controller
  outage. external-dns logs may still show benign `conflicting record type
  candidates; discarding CNAME record` warnings on every reconcile — harmless
  when an A record also exists, but they confirm the provider path is active.

## Remediation

1. Delete the stale record via the provider API (or dashboard):

   ```bash
    REC="https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records/<record-id>"
    curl -s -X DELETE "$REC" \
      -H "Authorization: Bearer ***"
   ```

2. Wait one reconcile interval (`--interval=1m` here) — external-dns
   recreates it fresh with an ownership TXT pointing at the current target.
3. Verify: `dig +short <host> @1.1.1.1` equals the live LB IP, and a TXT query
   now returns the ownership record.

Do NOT hand-edit the A record's content to the correct IP: that patches the
symptom but leaves the record orphaned — it drifts again on the next LB
address change. Delete-and-recreate is the fix.

## Prevention

- When rotating provider tokens or recreating external-dns, keep
  `--txt-owner-id` and `--txt-prefix` IDENTICAL — changing either orphans
  every existing record (same effect as changing `--txt-prefix`, per the
  upstream pitfall in the `book-external-dns` skill).
- Periodic sweep: for each `*.i.shikanime.studio` host, assert
  `dig +short` matches the owning Service's LB ingress. Any mismatch is either
  an orphaned record or a just-moved VIP — check which before acting.
