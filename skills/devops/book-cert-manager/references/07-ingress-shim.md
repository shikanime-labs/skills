# Ingress Shim

ingress-shim (part of cert-manager) watches `Ingress` resources. If an Ingress
has the right annotations, it auto-creates/updates a `Certificate` named after
`spec.tls[].secretName` in the Ingress's namespace.

## Trigger annotations

- `cert-manager.io/cluster-issuer: <name>` — use a `ClusterIssuer` (namespace
  agnostic). Not for external cluster-scoped issuers.
- `cert-manager.io/issuer: <name>` — use an `Issuer` (namespaced; must be in
  the same namespace as the Ingress; works for external issuers too via
  `issuer-kind`/`issuer-group`).
- `cert-manager.io/issuer-kind` / `cert-manager.io/issuer-group` — for
  out-of-tree issuers (e.g. `AWSPCAIssuer`, `awspca.cert-manager.io`).
- `kubernetes.io/tls-acme: "true"` — legacy kube-lego behavior; requires a
  default Issuer configured on the ingress-shim. Per-ingress annotations
  override the default.

## HTTP01 challenge routing annotations

- `acme.cert-manager.io/http01-ingress-class` — sets `kubernetes.io/ingress.class`.
- `acme.cert-manager.io/http01-ingress-ingressclassname` — sets
  `spec.ingressClassName` for the solver.
- `acme.cert-manager.io/http01-edit-in-place: "true"` — modify the existing
  ingress in place (adds `cert-manager.io/issue-temporary-certificate: "true"`
  so a temporary cert is set until the real one returns; useful for ingress-gce).

## Certificate field overrides (ingress annotations)

Map onto `Certificate.spec`. Comma-separated multi-values supported:

- `cert-manager.io/common-name`
- `cert-manager.io/email-sans`, `cert-manager.io/subject-organizations`,
  `subject-organizationalunits`, `subject-countries`, `subject-provinces`,
  `subject-localities`, `subject-postalcodes`, `subject-streetaddresses`,
  `subject-serialnumber`
- `cert-manager.io/duration`, `cert-manager.io/renew-before`
- `cert-manager.io/usages` (e.g. `"key agreement,digital signature,server auth"`)
- `cert-manager.io/revision-history-limit` (min 1)
- `cert-manager.io/private-key-algorithm` (RSA/ECDSA/Ed25519; default RSA),
  `-encoding` (PKCS1/PKCS8; default PKCS1), `-size`
  (RSA 2048/4096/8192, ECDSA 256/384/521, Ed25519 ignores size),
  `-rotation-policy` (Never/Always; default Always >= v1.18)

## Copying custom annotations to the Certificate (>= v1.18)

Redeploy controller with `--extra-certificate-annotations=...` (Helm:
`config.ingressShimConfig.extraCertificateAnnotations`). Then the annotation on
the Ingress is copied onto the generated Certificate.

## Default Issuer for `tls-acme: "true"`

Helm:

```bash
--set ingressShim.defaultIssuerName=letsencrypt-prod \
   --set ingressShim.defaultIssuerKind=ClusterIssuer \
   --set ingressShim.defaultIssuerGroup=cert-manager.io
```

Or controller args: `--default-issuer-name/-kind/-group`.

## Troubleshooting

No `Certificate` created? Ensure at least `cert-manager.io/issuer` or
`cert-manager.io/cluster-issuer` is set. With `tls-acme: "true"`, ensure the
default issuer is configured. Check cert-manager pod logs if still silent.
Each ingress needs a unique `tls.secretName`.
