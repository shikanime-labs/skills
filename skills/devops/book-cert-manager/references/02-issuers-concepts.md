# Issuers & Concepts

## Issuer vs ClusterIssuer

- `Issuer` — **namespaced**. Can only issue `Certificate`s in the same namespace.
  You need one per namespace that requests certs.
- `ClusterIssuer` — **cluster-scoped** (non-namespaced). Issues across all
  namespaces. Use when one CA serves the whole cluster.

All cert-manager certificates require a referenced issuer in `Ready` condition.

## Cluster Resource Namespace

The single most common "getting started" gotcha for `ClusterIssuer`.

- `ClusterIssuer` is cluster-scoped, but secrets it references (e.g. `ca`
  `secretName`, ACME `privateKeySecretRef`, Vault credentials) are looked up in
  the **Cluster Resource Namespace**.
- Default: `cert-manager`.
- Older docs / the `--cluster-resource-namespace` flag default to `kube-system`
  — verify what your install uses.
- Change via the controller flag `--cluster-resource-namespace=my-namespace`.

Rule of thumb: for a `ClusterIssuer`, put referenced Secrets in the Cluster
Resource Namespace (default `cert-manager`).

## Built-in vs external issuers

- **Built-in** (in `cert-manager.io` group): CA, SelfSigned, ACME, Vault, Venafi.
- **External / out-of-tree** (e.g. `AWSPCAIssuer`): configured similarly;
  reference them via `issuerRef.group` (and `issuerRef.kind`). The
  `cert-manager.io/issuer` ingress annotation defaults the group to
  `cert-manager.io`; for external issuers set group/kind explicitly.

## Issuer status check

```bash
kubectl get issuers -n <ns> -o wide
kubectl get clusterissuers -o wide
# CA issuer:   STATUS "Signing CA verified"
# Vault:       STATUS "Vault verified"
```

## Component overview (for context)

- `controller` — reconciles resources, drives issuance.
- `webhook` — validating/mutating admission.
- `cainjector` — injects CA data into webhooks/apiservices.
- `acmesolver` — ephemeral pod for HTTP01 challenges.

## Key resources chain

`Certificate` → `CertificateRequest` → (ACME only) `Order` → `Challenge`.
Each is created by its predecessor; inspect down the chain when debugging.
