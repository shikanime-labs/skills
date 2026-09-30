---
name: sks-kubernetes-manifests-authoring
description:
  "Use when authoring or editing Kubernetes manifests or kustomize overlays in
  a shikanime manifests repo: placement, patches, generators, labels, probes,
  and live-cluster cross-checks."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - kubernetes
      - kustomize
      - flux
      - gitops
      - shikanime-labs
    related_skills:
      - sks-delegate
      - sks-commit
      - sks-dev-workflow
      - sks-nix-authoring
      - sks-sops-secrets-authoring
      - sks-pr-review
platforms:
  - linux
  - macos
  - windows
---

# Kubernetes Manifests Authoring

Author YAML manifests and kustomize overlays in a shikanime manifests-class
repo (Flux + Kustomize GitOps) the way the fleet already reads them: one
kube resource per file named after it, sorted lists, each concern owned by
the layer that needs it, and every change proven by rendering before it
ships. The repo's own `AGENTS.md` is the per-repo source of truth for the
directory layout — read it first. This skill carries the org-wide authoring
discipline and the corrections that came from real incidents.

## When to Use

- Adding or editing workloads, Services, Ingresses, PVCs, netpols, probes,
  VPA objects, or Flux `Kustomization`/`HelmRelease` resources in a
  manifests-class repo.
- Deciding where a change belongs: base vs overlay, which patch type, which
  layer owns a generator.
- Verifying a manifests change against the live cluster before opening the
  PR (read `references/live-cross-check.md` for the sizing and drift
  recipes).

Don't use for: the Nix side of a render flake — that is
`sks-nix-authoring`. sops-encrypted `.enc.*` files — that is
`sks-sops-secrets-authoring`. Workspace, commit, and PR mechanics —
`sks-delegate` / `sks-commit` / `sks-pr-workflow`. Deep recipes for Gateway
route audits, image digest pinning, and infrastructure migrations live in
`sks-dev-workflow`'s `references/` behind explicit load conditions.

## Procedure

1. **Read the repo's `AGENTS.md`.** It defines the domain split
   (`apps/`, `infrastructure/`, `configs/`, `clusters/`, `modules/`,
   `bootstraps/`), the file-naming convention, and per-cluster composition.
   Completion check: you can name the directory your change belongs in and
   the files it touches.

2. **Name and shape files by the repo convention.** One kube kind per file,
   named `<short-kube-resource-name>.yaml` (`sts.yaml`, `svc.yaml`,
   `hr.yaml`, `netpol.yaml`, `pvc.yaml`), every list in a
   `kustomization.yaml` sorted, and no dangling files — every file on disk
   is referenced by a `path:`, `files:`, `envs:`, or inline entry.
   Completion check: `kustomize build` of the target overlay resolves every
   file it lists.

3. **Place the change in the layer that owns the concern.** Base carries
   what every cluster/flavor shares; overlays carry cluster- or
   flavor-specific deltas. Storage classes stay in base — overlays never
   patch the class. Hostnames never duplicate across flavors:
   `overlays/<cluster>/` owns `*.i.shikanime.studio`,
   `overlays/<cluster>-tailnet/` owns `*.taila659a.ts.net`. A transform
   needed by every flavor of a cluster goes in `overlays/<cluster>/`
   (flavors build on it via `resources:`); a transform for one flavor goes
   in that flavor's overlay. Completion check: reverting the base change
   leaves every other cluster rendering unchanged.

4. **Patch with the default type for the target.** Core kube resources
   (StatefulSet, Deployment, Service, Ingress) get a strategic-merge file
   `patch-<resource>.yaml` listed under `patches:`. JSON6902 is for CRDs
   and for what strategic merge cannot express — list appends like
   `env/-`, or keyed lists without merge keys (tailnet hostnames append
   with `op: add` on `path: /spec/hostnames/-` and a scalar `value:`).
   Kustomize rewrites core-resource references to generated
   Secrets/ConfigMaps itself; `namereference.yaml` entries are only for
   CRDs. Completion check: each patch file appears exactly once under
   `patches:` and the render shows the intended result.

5. **Generate config and secrets in the overlay that consumes them.**
   Generators in a parent overlay are invisible to a child overlay — the
   rendered names carry a hash suffix a child cannot guess. Secret sources
   are `*.enc.*` files (field-level sops encryption, decrypted by Flux at
   reconcile time) feeding `secretGenerator`, with the source file in a
   subfolder named after the secret. Never commit decrypted output.
   Completion check: the reference in the workload and the generator entry
   sit in the same overlay the Flux `Kustomization` reconciles.

6. **Size from live usage, never from estimates.** PVC/PV sizes grow to the
   next power of two above measured live usage — verify with `df`/`du`
   in-cluster before writing the number. No speculative multiples.
   Completion check: the PR names the measurement the new size came from.

7. **Ship monitoring and probes with the workload.** Probes target the
   pod's own port (`tcpSocket.port` on a named container port), never a
   secondary-CNI address. Every app exposing a signal gets
   `components/monitoring/` with `vmservicescrape.yaml` and a `vmrule.yaml`
   keyed on a signal the app actually reports, each alert carrying
   `labels.severity` and `annotations.summary`. Monitoring is part of the
   app, not a follow-up. Completion check: the VMRule queries a series the
   app's scrape emits.

8. **Render, then ship.** `kustomize build` every directory you touched;
   for a wide change, sweep every directory holding a
   `kustomization.yaml`. Tailnet overlays carry the five-key
   `app.kubernetes.io` label set with `includeTemplates: true`, and
   `version` stays synced to the base image tag — bump it in the same PR
   as any `newTag` change. Then commit per `sks-commit`.
   Completion check: renders succeed and `jj diff -r @ --stat` shows only
   the intended files.

## Pitfalls

- **Kustomize replaces, not merges, VCT list entries.** An overlay patch to
  `volumeClaimTemplates` must restate every field of the entry; a
  partial patch silently drops the rest. Changing `storageClassName` in an
  existing STS also does nothing to live PVCs — the flip recipe is in
  `references/live-cross-check.md`.
- **Generator not in the active overlay → `MountVolume.SetUp failed ...
  configmap not found`.** Diagnose which path Flux reconciles
  (`ks.yaml` → `path:`), find the reference in the render, and generate in
  that overlay — or rewrite the reference via patch.
- **Two `patches:` map keys in one kustomization is a YAML duplicate-key
  error.** One `patches:` list; routing and netpol patches are separate
  entries in it.
- **Kustomize v5 JSON6902 traps.** A patch file is a single ops-list doc
  (a multidoc `{patch,target}` file fails to parse); `add` on an existing
  member acts as replace (RFC 6902); a component referencing a named probe
  port must declare that `containerPort` in the same patch tree. A scalar
  `value:` appends one hostname — a list value appends a nested list.
- **Probes against a secondary-CNI address restart-loop healthy pods.**
  Kubelet dials probes from the node network namespace, so a macvlan/br1
  address times out forever and liveness kills a working pod.
- **A suspended `Kustomization` freezes its last-applied revision** —
  dependents block until it unsuspends. Suspend only as deliberate interim
  relief, never as a landing state.
- **The fix is the commit.** Flux reverts a live `kubectl patch` at the
  next reconcile. A running object with no manifest in the repo is drift —
  delete it, never build on it.
- **Do not hand-edit Nix-generated YAML** (e.g. sorting a rendered
  kustomization): fix the generating Nix and re-render (`sks-nix-authoring`).
- **Never run a bare whole-tree `nix fmt` here.** It rewrites every treefmt-
  owned file and can corrupt `.enc.*`; scope it to Nix trees you touched.
- **`kubectl port-forward` bypasses netpols.** Proving connectivity through
  a port-forward proves nothing about the policy path.

## Verification

```bash
# every touched overlay renders
kustomize build apps/<app>/overlays/<cluster> > /dev/null && echo render-ok

# no dangling files: each path/ files/ entry resolves
kustomize cfg cat apps/<app>/overlays/<cluster> > /dev/null 2>&1 || true

# diff is exactly the intended files (isolation workspace, per sks-delegate)
jj diff -r @ --stat
```

Done when renders succeed, the diff is scoped, and — for changes that
interact with live state — the live cross-check passed
(`references/live-cross-check.md`).

## See also

- `sks-nix-authoring` — the Nix side of a render flake; the generated-YAML
  surface is this skill.
- `sks-sops-secrets-authoring` — decrypt-editing the `.enc.*` sources.
- `sks-dev-workflow` — branch/push/land loop; carries the route-audit,
  image-pinning, and migration references.
- `sks-commit` / `sks-pr-workflow` — commit shape and PR envelope.
- `sks-pr-review` — reviewer lens before merge.
