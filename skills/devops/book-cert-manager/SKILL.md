---
name: book-cert-manager
description: cert-manager install, issuers, and certs reference.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes.tags:
    - Kubernetes
    - TLS
    - cert-manager
    - PKI
  hermes.related_skills:
    - kustomize-overlay-authoring
    - sks-tls
    - book-envoy-gateway
---

# cert-manager Reference

A distilled knowledge base of the cert-manager documentation: how to install
cert-manager, configure `Issuer`/`ClusterIssuer` types (ACME, CA, SelfSigned,
Vault, Venafi/CyberArk), request `Certificate`s, use ingress-shim, trust
private CAs, troubleshoot issues, and drive the `cmctl` CLI and controller
flags. This skill does NOT cover every API field verbatim — for an exhaustive
list, point the agent at the `cert-manager.io` API reference; load the relevant
chapter below instead.

## When to Use

- "Install cert-manager" / "deploy cert-manager with Helm/OCI"
- "Configure a Let's Encrypt / ACME issuer" (HTTP01, DNS01, solvers, EAB)
- "Set up a CA / SelfSigned / Vault / Venafi issuer"
- "Request a TLS certificate with a Certificate resource"
- "Add cert-manager annotations to my Ingress"
- "Why is my Certificate not ready?" / "troubleshoot ACME challenge"
- "How do I trust my private CA across namespaces?"
- "What does cmctl renew / status / x install do?"

## Prerequisites

- A Kubernetes or OpenShift cluster (supported version per
  `cert-manager.io/docs/releases/`).
- `kubectl` configured against the cluster.
- For Helm installs: Helm v3+ (`helm version`).
- For `cmctl`: `brew install cmctl` or download the binary from
  `github.com/cert-manager/cmctl/releases`.

## How to Run

Load chapters on demand with `skill_view` (file_path="references/<file>").
When changing manifests, edit with `patch`/`write_file`, then verify with
`terminal` (`kubectl get` / `kubectl describe` / `cmctl status certificate`).
Install commands run through the `terminal` tool.

## Quick Reference

- Install (static): `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml`
- Install (Helm OCI): `helm install cert-manager oci://quay.io/jetstack/charts/cert-manager --version v1.21.1 --namespace cert-manager --create-namespace --set crds.enabled=true`
- Check issuer: `kubectl get clusterissuers -o wide`
- Certificate status: `cmctl status certificate <name> -n <ns>`
- Force renewal: `cmctl renew <cert-name>` (or `--all`, `-l app=x`)
- Uninstall: `cmctl x uninstall` (safe, keeps CRDs >= v1.15.0 / cmctl v2)

## Procedure

1. Install cert-manager once (Helm OCI preferred; never embed as a subchart of
   unrelated charts — see `references/01-installation.md`).
2. Create an `Issuer` (namespaced) or `ClusterIssuer` (cluster-wide) — see
   `references/02-issuers-concepts.md` and `references/03-acme.md` /
   `references/05-issuers-ca-vault-venafi.md`.
3. Request certificates via a `Certificate` resource or ingress-shim
   annotations (`references/06-certificate.md`, `references/07-ingress-shim.md`).
4. Mount the resulting `Secret` in your app / Ingress; distribute private CA
   trust with trust-manager (`references/10-trust.md`).
5. Troubleshoot by walking the resource chain
   `Certificate → CertificateRequest → Order/Challenge` (`references/08-troubleshooting.md`).

## Pitfalls

- `duration`/`renewBefore` use Go `time.Duration` — `h`/`m`/`s` only, never `d`.
- `renewBefore` close to `duration` causes a renewal loop; prefer
  `renewBeforePercentage`.
- `ClusterIssuer` secrets live in the **Cluster Resource Namespace** (default
  `cert-manager`, older docs/`--cluster-resource-namespace` default
  `kube-system` — check your install).
- Never mount the server's `Secret` (it holds the private key) to share `ca.crt`
  with clients; use a separate trust bundle / trust-manager.
- Ingress-nginx is EOL March 2026 — plan Gateway API migration.

## Verification

A Certificate is healthy when `kubectl get certificate <name> -o wide` shows
`READY True` and `cmctl status certificate <name>` reports a valid Secret with
matching key usages.

## Reference Index (load on demand)

- `references/01-installation.md` — install methods, uninstall, Flux/GitOps.
- `references/02-issuers-concepts.md` — Issuer vs ClusterIssuer, namespaces,
  Cluster Resource Namespace, built-in vs external issuers.
- `references/03-acme.md` — ACME issuer config: HTTP01/DNS01, solvers,
  selectors, EAB, profiles, `waitInsteadOfSelfCheck`, alt chains.
- `references/04-acme-orders-challenges.md` — Order/Challenge CRDs, lifecycle,
  scheduling, `--max-concurrent-challenges`.
- `references/05-issuers-ca-vault-venafi.md` — CA, SelfSigned bootstrap,
  Vault auth, CyberArk/NGTS Venafi.
- `references/06-certificate.md` — Certificate spec, Secret contents, renewal,
  `rotationPolicy`, usages, output formats, name constraints.
- `references/07-ingress-shim.md` — ingress-shim annotations and subject/key
  overrides; troubleshooting.
- `references/08-troubleshooting.md` — resource-chain debugging flow.
- `references/09-cli-cmctl-controller.md` — `cmctl` commands and key
  controller flags / feature gates.
- `references/10-trust.md` — trusting private CAs, trust-manager, not mounting
  the server Secret.
