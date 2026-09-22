# Infrastructure ingress → Envoy Gateway migration (manifests repo)

Recipe for replacing a `kind: Ingress` resource with the fleet Gateway plane,
verified on `nishir-flux-webhook` / `telsha-webhook` (PR #2048).

## Per-cluster plane files (mirror the app Gateway pattern, e.g. bazarr)

- `clusters/<c>/base/gateway.yaml` — Gateway (HTTPS Terminate), per-cluster Service
- `clusters/<c>/base/httproute.yaml` — HTTPRoute → receiver Service:80
- `clusters/<c>/overlays/<c>-tailnet/gatewayclass.yaml`
- `clusters/<c>/overlays/<c>-tailnet/envoyproxy.yaml` — Tailscale LoadBalancer;
  annotations `tailscale.com/hostname: <original-name>` + `tag: web` — KEEP the
  original hostname so webhook consumers don't change
- `clusters/<c>/overlays/<c>-tailnet/patch-gateway.yaml` —
gatewayClassName/hostname patch
- Delete `base/ingress.yaml` + `overlays/<c>-tailnet/patch-ingress.yaml` and drop
  both from kustomization resources

## Envoy-gateway component prerequisite

A GatewayClass is adopted only when the EG controller is installed. nishir had
`clusters/nishir/components/envoy-gateway`; telsha did NOT — a cluster without
the component must gain all three:

- `infrastructure/envoy-gateway/overlays/<c>/kustomization.yaml` →
  `resources: [../../base]`
- `clusters/<c>/components/envoy-gateway/kustomization.yaml` (Component
wrapping ks.yaml)
- `clusters/<c>/components/envoy-gateway/ks.yaml` — Flux Kustomization: path →
  infra overlay, `decryption: sops` + `secretRef: sops-age`, healthCheck on
  HelmRelease/envoy (copy nishir's ks.yaml and change only the path)
- wire `../../components/envoy-gateway` into the cluster overlay components
  list (nishir's list is the canonical alphabetical order)

## TLS: bare MagicDNS names → cluster CA, NOT ACME

Webhook hostnames are bare MagicDNS names (`nishir-flux-webhook`) with no
public DNS record — ACME DNS01 cannot validate them. Issue from the cluster's
internal CA ClusterIssuer (`nishir` / `telsha`) instead, appended to
`configs/cert-manager/overlays/<c>/cert.yaml` (Certificate ns `flux-system`,
same ns as the EnvoyProxy TLS secret). GitHub still validates the funnel's
public LE cert; the cluster CA serves only the internal hop — the proven app
pattern.

## Verification

- `kustomize build` on BOTH cluster overlays + BOTH cert overlays → exit 0
- `grep -rln 'kind: Ingress'` — remaining hits are HelmRelease CRD targets
  (vminsert/vlogs/longhorn ingress enablement), NOT manifests to migrate
- scope check in the isolation workspace: `jj diff --git --stat` must list only
  intended files; a shared file (e.g. cert.yaml) carrying a parallel agent's
  edits → `jj restore --from 'main@origin' --to @ <file>` then re-append only
  your block (see "Staging only your hunks" for the git analogue)
