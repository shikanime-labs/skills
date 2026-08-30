---
name: book-fluxcd
description: "Flux Toolkit controllers, CRDs, and CLI reference."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Flux, GitOps, Kubernetes, CD, Helm]
---

# Flux GitOps Toolkit Reference

Distilled reference for the Flux GitOps Toolkit (fluxcd.io). It covers the
controllers, their custom resources (CRDs), authentication/secret shapes, and
the `flux` CLI. It does NOT replace the live docs for every edge flag — load a
`references/` file when you need exact field semantics for a specific component.

Key mental model: Flux is a set of Kubernetes controllers that continuously
reconcile declared state from Sources (Git/OCI/Bucket/Helm) into the cluster via
Appliers (Kustomize/Helm). Each Source produces an immutable `.tar.gz` Artifact
addressed by a revision (git sha, OCI digest, helm index sha). The artifact
revision is the unit of drift detection and garbage collection.

## When to Use

- "Create a GitRepository / Kustomization / HelmRelease / OCIRepository manifest"
- "Bootstrap Flux onto a cluster" or "set up Flux sync from Git"
- "Why is my Kustomization not reconciling / HelmRelease not ready"
- "Configure Flux notifications / webhook receivers / image automation"
- "Encrypt secrets with SOPS for Flux" or "write a flux CLI command"

## Prerequisites

- `flux` CLI installed: `brew install fluxcd/tap/flux` (or `nix-env -i fluxcd`,
  `choco install flux`, `curl -s https://fluxcd.io/install.sh | sudo bash`).
- Cluster admin on the target cluster; Kubernetes >= 1.33
  (>= 1.33.0 / >= 1.34.1 / >= 1.35.0). EOL versions unsupported.
- `kubectl` configured against the target cluster; `flux check --pre` passes.

## How to Run

- Author CRDs with `write_file`; validate with `flux build kustomization --path=...`
  or `flux diff kustomization`.
- Reconcile on demand via the `terminal` tool:
  `flux reconcile kustomization <name> --with-source`.
- Inspect with `flux get kustomizations -A`, `flux trace -n <ns> deployment <name>`,
  `flux logs --all-namespaces --level=error`.
- Load a chapter on demand:
  `skill_view(name="book-fluxcd", file_path="references/03-kustomize-controller.md")`.

## Quick Reference

- Bootstrap: `flux bootstrap github --owner=$G --repository=fleet-infra --branch=main --path=./clusters/my-cluster --personal`
- Install (dev): `flux install` | `kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml`
- Reconcile: `flux reconcile source git <name>` | `flux reconcile kustomization <name>` | `flux reconcile helmrelease <name>`
- Trigger webhook: `flux trigger receiver <name>`
- Suspend/resume: `flux suspend kustomization <name>` / `flux resume kustomization <name>`
- Generate manifests: `flux create source git <name> --url=... --branch=... --interval=1m --export > file.yaml`
- Secrets: `flux create secret git <name> --url=ssh://... --private-key-file=./identity`
- List all: `kubectl get fluxcd -A` (category); `flux get all -A --status-selector ready=false`
- Image automation components are NOT installed by default: bootstrap with
  `--components-extra=image-reflector-controller,image-automation-controller`

## Procedure (bootstrap + first app)

1. `flux check --pre`
2. `flux bootstrap github --owner=$GITHUB_USER --repository=fleet-infra --branch=main --path=./clusters/my-cluster --personal`
3. `git clone https://github.com/$GITHUB_USER/fleet-infra && cd fleet-infra`
4. `flux create source git podinfo --url=https://github.com/stefanprodan/podinfo --branch=master --interval=1m --export > clusters/my-cluster/podinfo-source.yaml`
5. `flux create kustomization podinfo --target-namespace=default --source=podinfo --path=./kustomize --prune=true --wait=true --interval=30m --export > clusters/my-cluster/podinfo-kustomization.yaml`
6. `git add -A && git commit -m "Add podinfo" && git push` — Flux syncs automatically.
7. Watch: `flux get kustomizations --watch`.

## Pitfalls

- SOPS: encrypt only `data`/`stringData` of Secrets; kustomize-controller cannot
  decrypt encrypted `metadata`/`kind`/`apiVersion`. Prefer age over OpenPGP.
- Helm `oci` HelmRepository type is in maintenance mode — use `OCIRepository` for OCI charts.
- `HelmRelease`: exactly one of `.spec.chart` or `.spec.chartRef` must be set (not both).
  Changing chart name triggers uninstall+reinstall unless `upgrade.chartNameChangeStrategy: InPlaceUpdate`.
- SSH Git URLs must be `ssh://user@host:22/repo.git` — scp syntax `user@host:repo.git` is NOT supported.
- `spec.interval` minimum 60s on Kustomizations; generation/ref changes reconcile instantly out of band.
- `prune` is required on Kustomization; targetNamespace must already exist.
- Image automation is opt-in (extra components) and needs a `--read-write-key` for push.
- Generic `Receiver` / `generic` Provider do no auth; use `-hmac` / `-oidc` variants for verification.

## Verification

- `flux check` returns controllers Ready; `flux get kustomizations -A` shows
  `READY=True` for the app; `kubectl -n default get deploy,pods` shows expected
  objects from the source revision.

## Reference Index (load on demand)

- `references/01-overview-install.md` — architecture, components, bootstrap, upgrade, install methods, Flux Operator.
- `references/02-source-controller.md` — GitRepository, OCIRepository, HelmRepository, HelmChart, Bucket: spec fields, auth/secret shapes, providers.
- `references/03-kustomize-controller.md` — Kustomization spec, prune/deletionPolicy, patches, health checks, SOPS decryption, inventory.
- `references/04-helm-controller.md` — HelmRelease spec, chart template vs chartRef, remediation, drift detection, post-renderers, values.
- `references/05-notification-controller.md` — Provider types, Alert filtering, Receiver webhooks, event metadata precedence.
- `references/06-image-automation.md` — ImageRepository, ImagePolicy (semver/alphabetical/numerical), ImageUpdateAutomation, marker syntax, digest policies.
- `references/07-operations-cli-troubleshooting.md` — CLI command map, get/reconcile/trace/trigger/suspend/resume, CRD categories, health-check CEL, troubleshooting recipes.
