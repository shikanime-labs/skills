# Tailnet UI gateway smoke test (post-deploy)

Recipe proven 2026-09-01 after landing PR #2047 (lldap + llama-cpp chat UIs).
Extended 2026-09-02 with the fleet-wide app-validation matrix used after the
route-patch PR chain (#2079–#2082).

## 0. Fleet-wide validation matrix (route-patch PRs)

For PRs that touch MANY apps' routes at once, validate per-app on four axes
instead of spot-checking; build the matrix programmatically, never by eye:

1. **Render**: `kustomize build` every `apps/**/overlays/nishir-tailnet`
   (note the RECURSIVE glob — `apps/*/*/overlays` for mautrix/servarr).
2. **Hostname validity**: in each rendered HTTPRoute, every `hostnames:` list
   item must be a clean FQDN (`[a-z0-9.-]+\.[a-z]+`); a nested-list append
   bug shows as an item starting with `- `.
3. **Flux**: `kubectl get kustomization -n flux-system -o json | jq` →
   per-app Ready + lastAppliedRevision must equal the merged main SHA.
   A kustomization caught MID-RECONCILE reports False with
   "Reconciliation in progress" — re-check after a minute before judging;
   also reconcile manually (`flux reconcile kustomization <app>
   --with-source`) when its revision lags main after a batch merge.
4. **Live routes**: `kubectl get httproutes -A -o json` and match hostnames
   per app. Match by NAME TOKEN too, not only hostname prefix — hermes-agent
   routes carry `automata.*` hostnames (no "hermes" token) and synapse carries
   `matrix.*`; a naive app-name-in-hostname matcher reports 0 routes and a
   false negative.

Aggregate count assertions (e.g. "66 HTTPRoutes across 36 overlays") are the
cheap global tripwire: if the total drops between runs, a route got deleted
or an overlay stopped rendering.

## 1. Flux reconciled?

```bash
kubectl get kustomization -n flux-system | grep -iE '<app>'
# "Applied revision: refs/heads/main@sha1:<merged-sha>" = new state live
```

## 2. Gateway resources Accepted + pods

```bash
kubectl get gatewayclass,gateway,httproute -n shikanime | grep -iE '<app>'
# Gateway must show True (Accepted) and a tailscale LB IP
kubectl get pods -n shikanime | grep -iE '<app>|envoy'
```

## 3. HTTP/HTTPS — bypass flaky local MagicDNS with `--resolve`

macOS curl intermittently throws `curl: (6) Could not resolve host` for
`*.i.shikanime.studio` while `dig @100.100.100.100` resolves instantly
(client resolver-cache quirk, NOT a service fault). Don't chase DNS; fetch
the LB IP and pin it:

```bash
IP=$(dig +short <host>.i.shikanime.studio @100.100.100.100 | head -1)
# http must 301 -> https:
curl -sS -o /dev/null -w '%{http_code} -> %{redirect_url}\n' \
  --resolve <host>.i.shikanime.studio:80:$IP http://<host>.i.shikanime.studio/
# https must 200 (or app-expected code):
curl -sSk -o /dev/null -w '%{http_code}\n' \
  --resolve <host>.i.shikanime.studio:443:$IP https://<host>.i.shikanime.studio/
```

## Interpreting failures

- **301 on :80, 200 on :443** — gateway path fully working; done.
- **301 on :80, 500 on :443** — gateway + TLS fine; the BACKEND is down.
  Check workload pods before blaming the gateway (e.g. llama-cpp LWS
  Pending = MS-S1 nodes kushira/sashina down — known pre-existing, not a
  manifests regression).
- **Gateway not Accepted / no LB IP** — check GatewayClass parametersRef
  chain and envoy-gateway-system controller logs.

## Public DNS smoke test (external-dns-managed hostnames)

external-dns on nishir runs with `--source=gateway-httproute --source=ingress
--source=service --policy=sync --registry=txt` against Cloudflare. Consequences
verified 2026-09-03 (inference outage):

- A hostname is synced ONLY if an HTTPRoute/Ingress/Service declares it. A
  hostname that exists only on a Certificate's `dnsNames` (e.g.
  `inference.i.shikanime.studio` — AIGatewayRoutes carry it nowhere else) is
  NEVER synced; its A record is manual or absent.
- An A record with no ownership TXT is ORPHANED: `--policy=sync` ignores it
  (won't update or delete), so a stale record pointing at a dead tailnet IP
  survives forever and causes TCP-timeout "Connection error" on clients.
- Diagnose: `dig +short A <host> @1.1.1.1`; then read the record via the
  Cloudflare API (token: Secret `external-dns-system/cloudflare-api-token`,
  key `cloudflare_api_token`, `base64 -d`; zone id live in the secret's
  usage history) and check for a matching TXT
  (` heritage=external-dns,external-dns/owner=nishir-external-dns`).
- Fix an orphaned/stale record by deleting it via the API and recreating the
  A record at the live Gateway LB IP (`kubectl get svc -n
  envoy-gateway-system <gw>` — the `100.x` External-IP), then verify with dig.
