# Operations, CLI & Troubleshooting

## CLI command map (all under `flux`)

- bootstrap (github|git|gitlab|gitea|bitbucket|...), install, uninstall, upgrade, check, version, completion.
- create — source (git|oci|helm|bucket|chart), kustomization, helmrelease, image (repository|policy|update),
  alert, alert-provider, receiver, secret (git|githubapp|helm|oci|proxy|receiver|tls|notation), tenant.
- get — all, sources (all|git|oci|helm|bucket|chart), kustomizations, helmreleases, images, alerts, receivers.
- reconcile — source, kustomization, helmrelease, image, receiver (+ `--with-source`).
- suspend / resume — kustomization, helmrelease, source, image, alert, receiver.
- delete — (same kinds). trace, tree (kustomization|artifact), trigger receiver, events, logs, stats,
  build (kustomization|artifact), diff (kustomization|artifact), export, debug (kustomization|helmrelease), envsubst, tag.
- Global flags: `-n/--namespace` (default `flux-system`), `--kubeconfig`, `--context`, `--timeout` (5m),
  `--verbose` (print generated objects), `--ns-follows-kube-context` (or `FLUX_NS_FOLLOWS_KUBE_CONTEXT`).

## list / discover

- `kubectl get fluxcd -A` — ALL Flux CRs (category). `kubectl get fluxcd-sources -A` | `fluxcd-appliers -A`.
- `flux get all -A --status-selector ready=false` — non-ready only.
- `flux get sources all -A` / `flux get kustomizations -A` / `flux get helmreleases -A`.
- `kubectl get gitrepositories.source.toolkit.fluxcd.io -A` (fully-qualified, avoids CRD clashes).

## diagnose

- `flux check` — controller readiness + versions.
- `flux logs --all-namespaces --level=error` — controller error logs.
- `kubectl get events -n flux-system --field-selector type=Warning`.
- `flux trace -n <ns> deployment <name>` (PREVIEW) — shows source → revision → reconcile status of an object.
  Multi: `flux trace -n redis pod/redis-master-0 cm/redis`; can pass `--kind`/`--api-version`.
- `flux debug kustomization <n>` / `flux debug helmrelease <n>` — dump built objects.
- `flux build kustomization --path=./clusters/c` (render locally) | `flux diff kustomization <n>`.

## Changes not applied — checklist

1. Source Ready + Suspend=false? `flux get sources all -A`.
2. Kustomization/HelmRelease Ready + Suspend=false? `flux get kustomizations -A`.
3. Force: `flux reconcile kustomization <n> --with-source`.

## Kustomize issues

- `admission webhook does not support dry run` — set `sideEffects: None`/`NoneOnDryRun` on the
  Validating/MutatingWebhookConfiguration.
- `configured` event spam — remove empty/null fields (`field: null`, `{}`, `[]`, empty string) from manifests
  (server-side apply dry-run sees them as drift).
- SOPS decrypt fail after patch — see `03` (move secrets into patches).

## Helm issues

- `HelmChart 'x' is not ready` — check `flux get sources chart` / `flux get sources helm` for source/version typo or 404.
- `install retries exhausted` — a resource not ready in 5m; `kubectl describe helmrelease` for events, or set `install.disableWait: true` then inspect.
- `Request entity too large: limit is 3145728` — chart > Secret size limit; trim `.helmignore`/`.sourceignore`.

## CEL health-check recipes (`.spec.healthCheckExprs`)

- Input = the CR object. `failed:` and `current:` are CEL exprs returning bool.
- Ready-condition pattern: `status.conditions.filter(e, e.type=='Ready').all(e, e.status=='True' && e.observedGeneration==metadata.generation)`.
- Failed pattern: `status.conditions.exists(e, e.type=='Stalled' && e.status=='True' && e.observedGeneration==metadata.generation)`.
- Guard missing fields with `has(status.x) && status.x.ready`.
- Empty `kind` matches whole API group (version ignored). Group-only entry overridden by specific kind.
- Examples: `ceph.rook.io/v1 CephCluster` (`status.ceph.health == 'HEALTH_OK'`/`'HEALTH_ERR'`),
  `cert-manager.io/v1 ClusterIssuer`, `cluster.x-k8s.io/v1beta1 Cluster`, `external-secrets.io/v1beta1 ClusterSecretStore`,
  `keda.sh/v1alpha1 ScaledObject`. Test at CEL Playground (playcel.undistro.io).

## Misc

- Raspberry Pi / low-mem: image-reflector BadgerDB OOM → increase swap (>=1GB).
- `flux uninstall` removes CRDs + controllers; re-bootstrap to restore.
