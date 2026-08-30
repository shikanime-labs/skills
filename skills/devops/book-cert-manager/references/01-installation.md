# Installation

## Install methods

cert-manager provides Helm charts as the first-class method. Two sources:

- **OCI registry (source of truth):** `oci://quay.io/jetstack/charts/cert-manager:v1.21.1`. Published immediately on release.
- **Legacy HTTP repo:** `https://charts.jetstack.io` — updated a few hours after OCI; avoid for latest. Very old versions (< v1.12) only here.

Never embed cert-manager as a subchart of unrelated charts — it manages
non-namespaced resources and must be installed exactly once. (Subchart override
of namespace is supported but discouraged.)

## Helm OCI (recommended)

```bash
helm install \
  cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --version v1.21.1 \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

Verify the chart signature (optional): download the GPG keyring, add `--verify
--keyring ./cert-manager-keyring-<hash>.gpg`.

## Static manifests (kubectl apply)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.21.1/cert-manager.yaml
```

## Common install flags (Helm values)

Full list on ArtifactHub. Examples:

- `--set crds.enabled=true` (install CRDs)
- `--set prometheus.enabled=false`
- `--set webhook.timeoutSeconds=4`
- `--set ingressShim.defaultIssuerName/Kind/Group`
- `--set maxConcurrentChallenges=60`

## Output YAML (for GitOps)

```bash
helm template cert-manager oci://quay.io/jetstack/charts/cert-manager:v1.21.1 \
  --namespace cert-manager --set crds.enabled=true > cert-manager.custom.yaml
```

`helm template` does NOT emit a Namespace resource and ignores
`--create-namespace`; ensure the target namespace exists.

Also possible: `cmctl x install` / `cmctl x install --dry-run >
cert-manager.custom.yaml`.

## Continuous deployment / GitOps

Drive the chart with Flux Helm Controller or Argo CD; or pipe `helm template`
output into any deployment tool. See
`cert-manager.io/docs/installation/continuous-deployment-and-gitops/`.

## Uninstalling

1. Delete all user-created resources first:
   `kubectl get Issuers,ClusterIssuers,Certificates,CertificateRequests,Orders,Challenges --all-namespaces`
2. Reverse the install: `helm uninstall cert-manager -n cert-manager`.
   - Helm keeps the CRDs on uninstall (>= v1.15.0) to avoid data loss.
   - Pre-v1.15.0 removes CRDs/objects — back up first or upgrade first.
   - `cmctl x uninstall` (cmctl v2) is safe and keeps CRDs.
   - To delete CRDs explicitly (destroys all instances):
     `kubectl delete crd issuers.cert-manager.io clusterissuers.cert-manager.io certificates.cert-manager.io certificaterequests.cert-manager.io orders.acme.cert-manager.io challenges.acme.cert-manager.io`
3. If a namespace is stuck `Terminating` after uninstall:
   `kubectl delete apiservice v1beta1.webhook.cert-manager.io`

## Compatibility

- Supported Kubernetes/OpenShift versions: `cert-manager.io/docs/releases/`.
- Cloud-provider caveats: `cert-manager.io/docs/installation/compatibility/`.
