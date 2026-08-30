# Image Automation — Repository / Policy / Update

Controllers (`image-reflector-controller`, `image-automation-controller`) are OPT-IN
(`--components-extra=...`). Flow: scan registry → select tag by policy → patch manifest →
commit+push to Git → Git-to-cluster reconcile rolls it out.

## ImageRepository (`image.toolkit.fluxcd.io/v1`)

- `.spec.image` — repo without scheme, e.g. `ghcr.io/stefanprodan/podinfo` (canonical form in `.status.canonicalImageName`).
- `.spec.interval` — scan interval. `.spec.timeout` (default = interval).
- `.spec.provider` — generic (no auth if public) | aws | azure | gcp.
- `.spec.secretRef` — `kubernetes.io/dockerconfigjson` (`kubectl create secret docker-registry`).
- `.spec.serviceAccountName` — generic => imagePullSecrets on SA; aws/azure/gcp => Workload Identity (needs `ObjectLevelWorkloadIdentity` gate).
- `.spec.certSecretRef` — mTLS (`tls.crt`+`tls.key`+`ca.crt`) or CA-only (`ca.crt`).
- Storage: BadgerDB at `--storage-path` (`/data`); `FluxStorage` gate => per-object `tags.txt[.gz]` keyed by `<ns>/<name>`.
- Status: `.status.lastScanResult.{latestTags, tagCount, scanTime}`.

## ImagePolicy (`v1`)

- `.spec.imageRepositoryRef` — `{name, namespace?}` (required).
- `.spec.policy` (required) — choose latest:
  - `semver: {range: '>=1.0.0 <2.0.0'}` (Masterminds/semver constraints; `1.0.x` patch only; pre-release `^1.x-0`).
  - `alphabetical: {order: asc|desc}` (default asc) — last when sorted.
  - `numerical: {order: asc|desc}`.
- `.spec.filterTags: {pattern: <regex>, extract?: <tmpl>}` — pre-filter tags before policy.
- `.spec.digestReflectionPolicy` — `IfNotPresent` (digest only updates with new tag) | `Always` (poll digest for fixed tag; needs `interval`, filter single tag).
- Status: `.status.latestRef.{image, tag, digest}`.

## ImageUpdateAutomation (`v1`)

- `.spec.sourceRef` — `{kind: GitRepository (default), name, namespace?}` (required). Timeouts/proxy derive from the GitRepository.
- `.spec.git.commit.author.{name,email}` + `.spec.git.push.branch` — commit+push target.
- `.spec.update.path` — dir to scan for markers (default `./`).
- `.spec.interval` — automation run interval.
- Status: `.status.lastPushCommit`, `.status.lastPushTime`, `.status.observedPolicies[]`.
- Git auth: source must carry checkout creds; for cloud provider (Azure) bind Workload Identity to
  image-automation-controller SA. Needs `--read-write-key` (or write deploy key) at bootstrap for push.

## Marker syntax (in manifest YAML)

- Image: `image: ghcr.io/x/app:5.0.0 # {"$imagepolicy": "flux-system:podinfo"}`
- HelmRelease values (separate fields):

  ```yaml
  image:
    repository: ghcr.io/x/app # {"$imagepolicy": "flux-system:podinfo:name"}
    tag: 5.0.0               # {"$imagepolicy": "flux-system:podinfo:tag"}
    digest: sha256:...        # {"$imagepolicy": "flux-system:podinfo:digest"}
  ```

- Format: `{"$imagepolicy": "<namespace>:<policyName>[:name|tag|digest]"}`.

## Commands

- `flux create image repository <n> --image=ghcr.io/x/app --interval=5m --export`
- `flux create image policy <n> --image-ref=<repo> --select-semver=5.0.x --export`
- `flux create image update <n> --git-repo=<src> --branch=main --export`
- `flux get image repository|policy|update -A` | `flux reconcile image <kind> <name>`

## Pitfalls

- Image automation NOT installed by default; `--read-write-key` required for push.
- `latest` tag is mutable — use `digestReflectionPolicy: Always` to track its digest, or pin semver.
- `IfNotPresent` + interval not allowed (digest only moves with a new elected tag).
