# Kustomize Controller — Kustomization

`Kustomization` (`kustomize.toolkit.fluxcd.io/v1`) = pipeline: fetch → decrypt →
build → validate → apply (server-side). Counterpart of `kustomization.yaml`.

## Required / key spec fields

- `.spec.sourceRef` — `{kind: GitRepository|OCIRepository|Bucket|ExternalArtifact, name, namespace?}`.
  Cross-ns allowed unless `--no-cross-namespace-refs=true`.
- `.spec.path` — dir containing `kustomization.yaml` or plain YAMLs (default: root).
- `.spec.prune` — REQUIRED bool. GC for objects missing from new revision; also on Kustomization delete.
  Disable per-object: label/annotate `kustomize.toolkit.fluxcd.io/prune: disabled`.
- `.spec.interval` — REQUIRED, min 60s. Gen/ref change reconciles instantly out of band.
- `.spec.targetNamespace` — overrides/forces ns for all objects. MUST already exist; not auto-created.
- `.spec.timeout` — apply/health timeout (Go duration; e.g. `3m0s`).
- `.spec.retryInterval` — retry-only interval; defaults to `.spec.interval`.
- `.spec.wait` — wait for readiness before marking Ready.
- `.spec.decryption` — `{provider: sops, secretRef: {name: sops-gpg|sops-age|sops-hcvault}}`.

## deletionPolicy (on Kustomization delete)

- `MirrorPrune` (default): delete if prune=true, orphan if false.
- `Delete` | `WaitForTermination` (blocks until k8s GC removes; bounded by timeout) | `Orphan`.

## Patches (inline, no repo control)

- `.spec.patches[].patch` (YAML), `.spec.patches[].target` (`{kind, name, group?, version?, labelSelector?}`),
  `.spec.patches[].path` (file in source).
- `.spec.postBuild` — Kustomize components/transformers from a `postBuild` source.

## Health checks

- `.spec.healthChecks[]` — `{apiVersion, kind, name, namespace}` objects to wait on.
- `.spec.healthCheckExprs[]` — CEL expressions (see `07` CEL cheatsheet):
  `failed:`, `current:`, optional `apiVersion`/`kind`. Input = the CR object itself.
  Use `has(status.x)` to guard missing fields. Empty `kind` = applies to whole API group.

## SOPS decryption (Flux + Mozilla SOPS)

- Encrypt ONLY `data`/`stringData` of Secrets. `metadata`/`kind`/`apiVersion` must stay plaintext
  (kustomize-controller cannot decrypt them).
- Workflow: `sops --encrypt --in-place secret.yaml` (OpenPGP) or
  `sops --age=<pubkey> --encrypt --encrypted-regex '^(data|stringData)$' --in-place secret.yaml`.
- Store key in cluster: `kubectl create secret generic sops-gpg --from-file=sops.asc=/dev/stdin`
  (or `sops-age` with `age.agekey`, or `sops-hcvault` with `sops.vault-token`).
- Kustomization decrypt: `--decryption-provider=sops --decryption-secret=sops-age`.
- `.sops.yaml` `creation_rules` with `encrypted_regex: ^(data|stringData)$` + `pgp: <fp>`.
- Cloud KMS (AWS/GCP/Azure): bind IAM/Workload Identity to kustomize-controller SA; skip `--decryption-secret`.
- Pitfall: if patches add fields matching `encrypted_regex`, SOPS fails on decrypt — move secrets into patches
  (decrypted before apply).

## Inventory & status

- `.status.inventory.entries[]` — `<ns>_<name>_<group>_<kind>_<version>`; drives drift/GC.
- `.status.lastAppliedRevision` / `.lastAppliedOriginRevision` (OCI: `org.opencontainers.image.revision`) /
  `.lastAttemptedRevision`.
- Suspend edits: `flux suspend kustomization <name>` / `flux resume kustomization <name>`.

## Commands

- `flux create kustomization <name> --source=<src> --path=./x --prune=true --wait=true --interval=30m --export`
- `flux build kustomization --path=./clusters/c` (local render) | `flux diff kustomization`
- `flux reconcile kustomization <name> --with-source`
