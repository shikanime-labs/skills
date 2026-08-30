# Overview, Architecture & Installation

## What Flux is

- CNCF Graduated GitOps toolkit for Kubernetes: continuously reconciles declared
  state from Sources into the cluster. Pull (not push) model — least privilege,
  auditable via Git history, no need to run `kubectl` by hand.
- Built on `controller-runtime`. Composable APIs: Sources, Appliers (Kustomize/Helm),
  Notification, Image automation. All CRDs registered under Flux resource
  categories for `kubectl get fluxcd -A`.

## Controllers / components

- `source-controller` — mirrors Git/OCI/Bucket/Helm into immutable `.tar.gz` Artifacts.
- `kustomize-controller` — builds + applies Kustomize overlays or plain YAML; decrypts SOPS.
- `helm-controller` — installs/upgrades/tests/rollbacks Helm releases; drift detection.
- `notification-controller` — dispatches events to Providers; receives webhooks (Receivers).
- `image-reflector-controller` — scans registries, stores tags (`ImageRepository`/`ImagePolicy`).
- `image-automation-controller` — commits+pushes image bumps back to Git (`ImageUpdateAutomation`).
- Default bootstrap installs source/kustomize/helm/notification. Image controllers are
  OPT-IN via `--components-extra=image-reflector-controller,image-automation-controller`.

## Install & bootstrap

- Prereqs: cluster admin; Kubernetes >= 1.33 (>=1.33.0 / >=1.34.1 / >=1.35.0). EOL unsupported.
- CLI install: `brew install fluxcd/tap/flux` | `nix-env -i fluxcd` | `choco install flux` |
  `curl -s https://fluxcd.io/install.sh | sudo bash` (custom dir: `bash -s ~/.local/bin`).
- Pre-flight: `flux check --pre`.
- Bootstrap (GitHub, idempotent, pushes manifests to Git + configures self-update):

  ```sh
  flux bootstrap github --owner=$GITHUB_USER --repository=fleet-infra \
    --branch=main --path=./clusters/my-cluster --personal
  ```

  - Other providers: `flux bootstrap git|gitea|gitlab|bitbucket|azure-devops|generic-git-server`.
  - Image automation: append `--components-extra=image-reflector-controller,image-automation-controller --read-write-key`.
  - `bootstrap` is safe to re-run (upgrades in place). Delete `flux-system` secret first to rotate deploy key.
- Dev install (no Git storage): `flux install` | `kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml`
  | `helm install -n flux-system --create-namespace flux oci://ghcr.io/fluxcd-community/charts/flux2`.

## Flux Operator (declarative lifecycle mgmt)

- Alt to CLI bootstrap. Installs controllers + sync via a `FluxInstance` CR
  (`fluxcd.controlplane.io/v1`, name `flux`, ns `flux-system`).
- Install: `helm install flux-operator oci://ghcr.io/controlplaneio-fluxcd/charts/flux-operator --namespace flux-system --create-namespace`.
- Example `FluxInstance.spec`: `distribution.{version,registry,artifact}`,
  `components: [source-controller, kustomize-controller, helm-controller, ...]`,
  `cluster: {type, size, multitenant, networkPolicy, domain}`, `sync: {kind: OCIRepository|GitRepository, url, ref, path}`.
- Auto-upgrade: pin `distribution.version` (e.g. `2.7.x`) to cap; fixed version disables upgrades.

## Upgrade & uninstall

- Upgrade controllers: re-run bootstrap, or `flux install` after editing pinned version in Git.
- Uninstall: `flux uninstall` (removes CRDs + controllers).
- Pin CLI: `FLUX_VERSION=2.7.0 curl -s https://fluxcd.io/install.sh | bash -s ~/.local/bin`.

## GitHub Action

- `uses: fluxcd/flux2/action@main` with `version: 'latest'`, then `flux version --client`
  (e.g. for `flux build`/`diff` in CI).

## Auth integration posture

- Cloud auth (AWS IRSA / Azure Workload Identity / GCP Workload Identity) is configured by
  patching the controller ServiceAccount in `flux-system/kustomization.yaml`, not in the CR.
- Multi-tenancy: `--no-cross-namespace-refs=true` on controllers blocks cross-ns source/alert refs.
