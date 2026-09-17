# mTLS vs DNS diagnosis — inference gateway

## Symptom
Hostname resolves and routes correctly (externalDNS published the right A
record; `dig` returns the tailnet LB IP), but every ordinary client fails at
the TLS layer. NOT a DNS problem.

## Root cause
`ClientTrafficPolicy/inference` (ns `shikanime`) enforces
`tls.clientValidation` against the nishir CA. Only clients presenting a
CA-signed client cert get through; everyone else gets a TLS handshake reset
(`reason(1116)` in the Envoy access log).

## Two-curl discriminator (localizes in seconds)

```bash
CTX=nishir-k8s-operator.taila659a.ts.net
H=inference.shikanime.studio
# WITH client cert → 200 (proves routing + app are fine)
curl -sk --http1.1 -m12 --cert /tmp/inf-client.crt --key /tmp/inf-client.key \
  --cacert /tmp/inf-ca.crt -o /dev/null -w "clientcert HTTP %{http_code}\n" \
  "https://$H/v1/models"
# WITHOUT client cert → 000 (handshake abort) ⇒ mTLS gate, not DNS
curl -sk --http1.1 -m12 -o /dev/null -w "no-cert HTTP %{http_code}\n" \
  "https://$H/v1/models"
```

- both `200` ⇒ open.
- clientcert `200` + no-cert `000` ⇒ `ClientTrafficPolicy` mTLS. Remove
  `clientValidation` (see below).
- both `000` ⇒ real TLS/listener fault (bad cert Secret, Envoy not Ready) —
  check `kubectl get gateway inference` Programmed and the cert Secret.

## Fix (must survive Flux reconcile)

The `https` listener `clientValidation` is set by the base
`apps/llama-cpp/components/tls/clienttrafficpolicy.yaml`. Remove it at the
overlay via a JSON6902 patch so the rendered output is `tls: {}`:

```yaml
# apps/llama-cpp/overlays/nishir-tailnet/patch-clienttrafficpolicy.yaml
- op: remove
  path: /spec/tls/clientValidation
```

Verify the render strips it:

```bash
kustomize build apps/llama-cpp/overlays/nishir-tailnet | grep -c clientValidation
# → 0
```

### Live relief (temporary — reverts on next reconcile)
```bash
kubectl --context $CTX -n shikanime patch clienttrafficpolicy inference \
  --type=json -p='[{"op":"remove","path":"/spec/tls/clientValidation"}]'
```

WARNING: `flux reconcile kustomization apps-llama-cpp` re-applies `main`
(which lacks the patch) and re-enables mTLS → endpoint returns `000`. The live
patch is ONLY durable once the overlay change is committed to the PR branch and
Flux applies that branch.

## After mTLS is off — the remaining `-k` caveat
The listener still serves the internal `inference-tls` cert (nishir CA, SANs:
`inference`, `inference.taila659a.ts.net`, but NOT `inference.shikanime.studio`).
So:
- `inference.taila659a.ts.net` → trusted by Tailscale-aware clients, no `-k`.
- `inference.shikanime.studio` → still needs `-k` until a Let's Encrypt cert
  with the `.studio` SAN is issued and the listener's `certificateRefs` points
  at it.

## Trusted LE cert follow-up (gated on valid Cloudflare token)
A `ClusterIssuer` with `server: https://acme-v02.api.letsencrypt.org/directory`
+ Cloudflare DNS-01 will not issue if the token is invalid. Verify FIRST:

```bash
TOK=$(kubectl --context $CTX -n cert-manager-trust get secret cloudflare-api-token \
  -o jsonpath='{.data.apiToken}' | base64 -d)
curl -s -H "Authorization: Bearer $TOK" \
  https://api.cloudflare.com/client/v4/user/tokens/verify
# Invalid API Token ⇒ cert stays pending ⇒ do NOT point the listener at it
```

If the token is invalid, keep `inference-tls` (with `-k`) and treat the LE cert
as a separate PR once a valid token exists.
