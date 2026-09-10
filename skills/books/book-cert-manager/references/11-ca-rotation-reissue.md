# CA Rotation Reissue Pattern

## Problem

When a self-signed CA `Certificate` (used by a CA `ClusterIssuer`/`Issuer`)
renews with a new key pair, cert-manager does NOT re-issue leaf certificates
that were signed by the old CA. The trust bundle propagates the new CA
trust anchor immediately (via trust-manager `Bundle`), but leaf certs still
serve the old CA signature → mTLS `certificate signed by unknown authority`.

**No native cert-manager setting auto-reissues on CA rotation.**

## Pattern: compare CA serial vs leaf serial, delete stale secrets

A CronJob runs `kubectl` + `jq` + `openssl` periodically, compares the CA
secret's cert serial against each leaf cert's serial, and deletes leaf TLS
secrets that don't chain to the current CA. cert-manager re-issues deleted
secrets immediately from the current CA.

```sh
NS=cert-manager-trust
ISSUER=nishir

# 1. serial of the CA currently in the issuer secret
CA_SERIAL=$(kubectl -n $NS get secret nishir-ca -o jsonpath='{.data.ca\.crt}' \
  | base64 -d | openssl x509 -noout -serial | cut -d= -f2)

# 2. delete leaf secrets whose cert was NOT signed by that serial
for res in $(kubectl get certificates -A -o json \
    | jq -r --arg iss "$ISSUER" '\
        .items[]\
        | select(.spec.issuerRef.name==$iss and .spec.issuerRef.kind!="ClusterIssuers"\
                 or .spec.issuerRef.name==$iss)\
        | "\(.metadata.namespace) \(.spec.secretName)"'); do
  ns=${res% *}; sec=${res#* }
  [ "$ns" = "$NS" ] && continue   # skip the CA itself
  crt=$(kubectl -n $ns get secret "$sec" -o jsonpath='{.data.tls\.crt}' 2>/dev/null) || continue
  serial=$(echo "$crt" | base64 -d | openssl x509 -noout -serial 2>/dev/null | cut -d= -f2)
  if [ "$serial" != "$CA_SERIAL" ]; then
    echo "stale leaf: $ns/$sec (serial $serial != CA $CA_SERIAL) — deleting for re-issue"
    kubectl -n $ns delete secret "$sec" --wait=false
  fi
done
```

### Notes

- The `bitnami/kubectl` image provides kubectl + openssl + jq + base64 in one
  small container.
- `jq` filters Certificates by `spec.issuerRef.name` to target only those
  issued by the rotated CA issuer.
- Deleting the TLS `Secret` (not the `Certificate` CRD) is the trigger —
  cert-manager sees the Secret disappear and re-issues from the current CA.
  Cert-manager docs confirm this is one of the reissue triggers: "Secret named
  on Certificate's spec does not exist / issuer annotations do not match."
- The CronJob needs `get/list/delete` on `secrets` and `get/list` on
  `certificates` across all namespaces (ClusterRole/ClusterRoleBinding).
- **Pitfall:** The `jq` filter `spec.issuerRef.kind!="ClusterIssuers"` uses the
  plural form, but the CRD kind is `ClusterIssuer` (singular). This means the
  `!="ClusterIssuers"` check never matches — it's always true, so the NOT
  condition is effectively ignored. The `or` clause then catches all certs
  regardless of kind. For the `nishir` issuer this is harmless (all are
  ClusterIssuer), but for mixed clusters you should use `!"=="` or filter
  explicitly on `kind`. See `references/12-cert-manager-issuer-topology.md`.

### Why Flux postBuild/substituteFrom can't replace this CronJob

A time-based hash via Flux `postBuild.substituteFrom` referencing a ConfigMap
updated by a CronJob would require: (1) the same CronJob to write the hash to
a ConfigMap, (2) every leaf Certificate Kustomization to adopt
`commonAnnotations` from `postBuild`, (3) the ConfigMap update to trigger
reconciliation. This is strictly more complex and less surgical than the direct
secret-deletion approach. Flux syncs Git→Cluster and does not observe
cluster-internal Secret changes — CA rotation is an in-cluster event that Flux
cannot detect natively.

### Issuer topology (shikanime example)

Two distinct issuer chains exist in the cluster:

- **CA issuer** (`nishir`): `ClusterIssuer` of `spec.ca.secretName: nishir-ca`.
  Leaf certs across `default/`, `shikaname/` namespaces use this. These are
  mTLS/ingress leaf certs that chain to the self-signed CA root.
- **ACME issuer** (`studio-shikaname`): `ClusterIssuer` pointing at
  `acme-v02.api.letsencrypt.org/directory`. Leaf certs in
  `configs/cert-manager/overlays/nishir/cert.yaml` use this for public TLS
  (Let's Encrypt). These do NOT need CA rotation healing — Let's Encrypt
  handles its own chain.

The CronJob targets only `issuerRef.name == "nishir"` (the CA chain), not the
ACME chain.

### Alternatives

- `cmctl renew --all` forces reissue of all Certificates — simpler but churns
  every leaf regardless of CA staleness.
- Setting `spec.duration: 87600h` on the CA `Certificate` prevents rotation
  entirely (lazy default for self-signed roots that don't need periodic
  rotation).
