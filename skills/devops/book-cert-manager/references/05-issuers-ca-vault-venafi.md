# CA, SelfSigned, Vault & Venafi Issuers

## CA Issuer

A CA whose cert + key live in a Kubernetes `Secret`. Certs issued are NOT
publicly trusted. Intended for advanced PKI operators; needs rotation / trust
distribution / DR planning. Prefer trust-manager for distributing the CA cert.

```yaml
apiVersion: v1
kind: Secret
metadata: { name: ca-key-pair, namespace: sandbox }
type: kubernetes.io/tls
data:
  tls.crt: <base64 PEM>   # full chain issuer->intermediate(s)->root
  tls.key: <base64 PEM>
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata: { name: ca-issuer, namespace: sandbox }
spec:
  ca:
    secretName: ca-key-pair
    # optional:
    crlDistributionPoints: ["http://example.com/my.crl"]
    ocspServers: ["http://ocsp.example.com"]
```

- Secret must be in the Issuer's namespace, or the Cluster Resource Namespace
  for a ClusterIssuer.
- No automatic CA rotation. Track CA + leaf expiry; `cmctl renew` re-issues
  leaves if the CA was rotated.
- Updating the CA Secret does NOT auto re-issue leaves.
- CA basic constraints (`isCA=true`) and `certificate sign` usage required;
  other constraints (name constraints, max path length) are NOT validated.

## SelfSigned Issuer

Signs certs with their own private key. Mainly for bootstrapping a root CA for
a private PKI, or quick ad-hoc test certs. Not for direct production trust.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: selfsigned-issuer }
spec: { selfSigned: {} }
```

- CertificateRequest referencing a self-signed cert needs the
  `cert-manager.io/private-key-secret-name` annotation (added automatically by
  the Certificate controller).
- Optional `crlDistributionPoints`.
- **Caveat — validity**: self-signed certs have identical Subject DN and Issuer
  DN; RFC 5280 requires non-empty Issuer DN. Set `spec.subject` on the
  Certificate (cert-manager emits a `BadConfig` warning event if empty).
- **Caveat — trust**: consumers can't trust without pre-distribution; use
  trust-manager.

### Bootstrapping a CA issuer

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: selfsigned-issuer }
spec: { selfSigned: {} }
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: my-selfsigned-ca, namespace: sandbox }
spec:
  isCA: true
  commonName: my-selfsigned-ca
  secretName: root-secret
  privateKey: { algorithm: ECDSA, size: 256 }
  issuerRef: { name: selfsigned-issuer, kind: ClusterIssuer, group: cert-manager.io }
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata: { name: my-ca-issuer, namespace: sandbox }
spec: { ca: { secretName: root-secret } }
```

For a ClusterIssuer signing cluster-wide, put `root-secret` in the
`cert-manager` namespace and reference it from a ClusterIssuer `ca` stanza.

## Vault Issuer

Uses HashiCorp Vault PKI as CA. Common fields: `server`, `path` (must use the
`sign` endpoint, e.g. `pki_int/sign/example-dot-com`), `caBundle` (usually
required for `https`).

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata: { name: vault-issuer, namespace: sandbox }
spec:
  vault:
    path: pki_int/sign/example-dot-com
    server: https://vault.local
    caBundle: <base64 PEM>
    auth: { ... }
```

### Auth methods

| Method | Config |
| --- | --- |
| AppRole | `auth.appRole`: `path`, `roleId`, `secretRef` (Secret w/ `secretId`) |
| Token | `auth.tokenSecretRef`: Secret w/ `token`. cert-manager does NOT refresh tokens |
| Kubernetes / JWT-OIDC | `auth.kubernetes`: `role`, `mountPath`, `serviceAccountRef` (>= v1.12) |

- K8s auth: create a Role allowing `create` on `serviceaccounts/token` for the
  SA, bind cert-manager SA. Recommended: one Vault role per Issuer/ClusterIssuer.
  `audience` syntax: `"vault://<namespace>/<issuer-name>"` (Issuer) or
  `"vault://<cluster-issuer-name>"` (ClusterIssuer).
- Verify: `kubectl get issuers vault-issuer -n sandbox -o wide` → `Vault verified`.
  Vault is checked via `v1/sys/health` (unsealed + initialized).
- mTLS to Vault: `caBundleSecretRef`, `clientCertSecretRef`, `clientKeySecretRef`.

## CyberArk Certificate Manager (formerly Venafi)

One `Issuer` = one CyberArk **zone**. Supports SaaS, Self-Hosted (TPP), and
Palo Alto NGTS.

- **SaaS**: `venafi.zone: "<Application>\\<CIT>"`, `venafi.cloud.apiTokenSecretRef`.
- **Self-Hosted (TPP)**: `venafi.zone: "\\VED\\Policy\\..."`,
  `venafi.tpp: { url, caBundle/caBundleSecretRef, credentialsRef }`. Must allow
  "User Provided CSRs" in policy; locked "Service Generated CSR" fails.
- **NGTS**: `venafi.zone: "<CIT>"`, `venafi.ngts: { tsgID, credentialsRef,
  tokenEndpoint?, url? }`.
- Credentials Secret for a ClusterIssuer goes in the Cluster Resource Namespace
  (default `cert-manager`).
- Issuer-level custom fields: `venafi.cert-manager.io/custom-fields` annotation
  (>= v1.20) on Issuer/ClusterIssuer; Certificate-level annotation merges.
- CyberArk/Venafi may disallow private-key reuse → set `rotationPolicy: Always`.
