# Source Controller — Git/OCI/Bucket/Helm

All sources produce an immutable Artifact; revision is the drift key.
Common spec: `apiVersion: source.toolkit.fluxcd.io/v1`, `interval` (Go duration,
min 60s), `provider` (generic|aws|azure|gcp|github; default generic).

## GitRepository (`gitrepositories`)

- `.spec.url` — HTTP/S or SSH. SSH MUST be `ssh://user@host:22/repo.git`
  (scp `user@host:repo.git` NOT supported).
- `.spec.ref` — `branch` / `tag` / `semver` / `commit`.
- `.spec.secretRef.name` — Secret in same ns for auth.
  - Basic: `username` + `password` (base64). Bearer: `bearerToken`.
  - HTTPS CA: `ca.crt` (or `caFile`; `ca.crt` wins). mTLS: `tls.crt`+`tls.key`+`ca.crt`.
  - SSH: `identity` + `known_hosts` (stringData). Password-protected key: add `password`.
  - CLI: `flux create secret git <name> --url=ssh://git@github.com/org/repo --private-key-file=./identity`.
- `.spec.provider`: `generic` (default) | `aws` (CodeCommit, URL must be
  `https://git-codecommit.<region>.amazonaws.com/v1/repos/<repo>`, needs IRSA/EKS Pod Identity,
  IAM `codecommit:GitPull`) | `azure` | `github`.
- Status: `.status.artifact.revision` = `master@sha1:<40hex>`; `.status.artifact.url`
  is the internal controller URL.

## OCIRepository (`ocirepositories`)

- `.spec.url` — `oci://<host>[:port]/<org>/<repo>` (NO tag/digest in url).
- `.spec.ref` — `tag` | `digest` | `semver` | `branch`(for OCI artifacts with tags).
- `.spec.provider` — generic|aws|azure|gcp. AWS: EKS node IRSA or IRSA patch on
  source-controller SA (`eks.amazonaws.com/role-arn`). Azure: Workload Identity patch. GCP: `iam.gke.io/gcp-service-account`.
- `.spec.secretRef` — docker-registry style (`kubectl create secret docker-registry`).
- `.spec.serviceAccountName` — for workload identity (generic => uses attached imagePullSecrets).
- Revision = `latest@sha256:<64hex>`.

## HelmRepository (`helmrepositories`)

- `.spec.type` — `default` (HTTP/S index.yaml → Artifact) | `oci` (data container, no Artifact;
  `oci` type is MAINTENANCE MODE — prefer `OCIRepository`).
- `.spec.url` — index URL (default) or `oci://...` (oci).
- `.spec.provider` — only for `oci` type: generic|aws|azure|gcp.
- `.spec.interval` — used for `default`, ignored for `oci`.

## HelmChart (`helmcharts`)

- Usually created by helm-controller from `HelmRelease.spec.chart`; name
  `<ns>-<hr-name>`, same ns as sourceRef.
- `.spec.chart` (chart name), `.spec.version`, `.spec.sourceRef` (HelmRepository |
  OCIRepository | GitRepository), `.spec.interval`.

## Bucket (`buckets`)

- S3-compatible object storage (Minio, AWS S3, GCS, Alibaba OSS).
- `.spec.endpoint` (e.g. `minio.svc:9000`), `.spec.bucketName`, `.spec.insecure`,
  `.spec.region`, `.spec.provider` (generic|aws|azure|gcp).
- `.spec.secretRef` — `accesskey` + `secretkey` (generic required; aws can use EC2
  node identity / IRSA / workload identity).
- Revision = SHA256 of sorted etag list.

## Failure/Stalled semantics (all sources)

- Failing: `Ready=False` + `FetchFailed`/`StorageOperationFailed`/`AuthenticationFailed`,
  exponential backoff retry.
- Stalled: `Stalled=True` (e.g. `URLInvalid`) — controller STOPS requeueing until spec changes.
- `.status.lastHandledReconcileAt` tracks `reconcile.fluxcd.io/requestedAt` annotation.

## Reconcile on demand

- `flux reconcile source git <name>` | `source oci` | `source helm` | `source bucket <name>`.
- Or annotate: `reconcile.fluxcd.io/requestedAt: <token>`.
