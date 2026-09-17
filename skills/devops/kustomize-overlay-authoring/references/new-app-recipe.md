# Adding a new app to manifests — worked example (maintainerr, PR #2090)

Verified 2026-09-02 end-to-end: `kustomize build` both overlays + full cluster
render exit 0, PR head == local commit, MERGEABLE.

## 1. Pick the template app and placement

- Survey a same-class app FIRST (`find apps/<template> -type f`, read every
  file) — the new app inherits its shape.
- Template classes:
  - UI app behind a tailnet gateway, no SOPS secrets → `apps/seerr/`
  - Servarr worker (TLS sidecar component, rclone config seed, pkcs12) →
    `apps/servarr/<member>/`
- Placement is by service name, NOT by family resemblance: maintainerr is
  media-adjacent but went to `apps/maintainerr/`, not `apps/servarr/`. Servarr
  membership = speaks the *arr API, queries prowlarr.
- Media-adjacent UI apps get `app.kubernetes.io/component: library-manager`,
  `part-of: nishir-media` labels in the tailnet overlay.

## 2. Verify upstream facts — never from README lore

- Image digest (GHCR):
  ```bash
  TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:<org>/<img>:pull" | jq -r .token)
  curl -s -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.oci.image.index.v1+json" \
    "https://ghcr.io/v2/<org>/<img>/manifests/<tag>" -D -   # docker-content-digest header
  ```
- Docker Hub tags: `https://hub.docker.com/v2/repositories/<repo>/tags?page_size=15`
  (`registry.hub.docker.com` mirror 404s; hub.docker.com works).
- Port + data dir: read the upstream Dockerfile (`EXPOSE`, `ENV`, `WORKDIR`,
  volume path) and start.sh — e.g. maintainerr exposes 6246, data at
  `/opt/data`, NOT the 8085 often quoted in third-party guides.
- Probe paths: read the app's health controller/route source on GitHub, not
  guesses. Maintainerr: `/api/health/live` (no DB) and `/api/health/ready`
  (DB ping) — split liveness from readiness when upstream offers both.

## 3. Author the tree (base + nishir + nishir-tailnet)

One resource per file, `<short-name>.yaml`, listed sorted in kustomization.

Base `netpol.yaml` classes:
- No in-namespace consumer → deny-all (`policyTypes: [Ingress]`,
  `ingress: []`, copyparty/maintainerr pattern). The gateway plane is
  cross-namespace and not admitted by podSelector anyway.
- Named in-namespace consumer → podSelector allow (metatube→jellyfin).
- Gateway-plane allows (tailscale-system, vmagent) belong in tailnet overlay
  patches only when the app needs them (see SKILL.md base-netpol rule).

Env: `TZ: Europe/Paris`, `fsGroup: 1000` securityContext, `replicas: 1`
(omit per layout convention), VPA `updateMode: Initial` (seerr uses
InPlaceOrRecreate — acceptable variance).

## Storage: volumeClaimTemplate, NOT a pinned PVC (user directive 2026-09-03)

"Newly stateful should be using volumetemplate." The seerr template's
shape (standalone `base/pvc.yaml` + `patch-pvc.yaml` pinning
`volumeName: <pvc>` + `storageClassName`) requires an OUT-OF-BAND
Longhorn volume + static PV that no manifest creates — the pod went
`Pending` (unbound immediate PVC) and #2090 shipped broken. New
stateful apps follow the lldap/authelia shape:

- `base/sts.yaml` declares `volumeClaimTemplates` (e.g. 512Mi,
  ReadWriteOncePod); the container mounts the VCT name directly, no
  `volumes:` entry.
- `overlays/nishir/patch-pvc.yaml` is an SMP restating the whole VCT
  (resources included — a partial patch drops the storage spec, #2091)
  with `storageClassName: nishir-standard`. Delete `base/pvc.yaml`
  entirely.
- **Storage floor: 512Mi** (user: "always start from 512mi unless 1gb
  is reasonable"). Maintainerr's 1Gi start was right-sized to 512Mi in
  #2096.
- VCT is immutable → ship the FINAL size/SC before first deploy; each
  later VCT change needs the orphan-cascade STS recreation (SKILL.md
  "Immutable StatefulSet volumeClaimTemplates").

Deny-all base netpol (this recipe's default) also blocks in-cluster
integrations: any pod that must REACH another app's API gets that
consumer added to the TARGET app's netpol allow-list (podSelector on
`app.kubernetes.io/name: <consumer>`), and vice versa when the new app
exposes an API other pods call.

## 4. Cert classes (easy to get wrong)

- Gateway apps reference ONLY the shared studio cert in
  `configs/cert-manager/overlays/nishir/cert.yaml`
  (`studio-shikanime-i-<app>`, issuer `studio-shikanime`, dnsNames just the
  one `i.shikanime.studio` hostname). No app-level Certificate needed unless
  workloads verify in-cluster TLS.
- TLS-component apps (servarr) additionally carry
  `apps/<app>/overlays/nishir/cert.yaml` with `nishir` ClusterIssuer,
  in-cluster dnsNames (`<app>`, `<app>.shikanime`,
  `<app>.shikanime.svc.cluster.local`), pkcs12 keystore + password secret +
  `namereference.yaml`. Only copy this when adding the tls component.

## 5. Wire and verify

- `clusters/nishir/overlays/tailnet/ks.yaml`: `apps-<name>` Kustomization
  (copy `apps-seerr` block; dependsOn autoscaler/cert-manager/tailscale,
  healthCheck `StatefulSet/<name>` ns `shikanime`, path the tailnet overlay).
- Verify: `kustomize build` the nishir overlay AND nishir-tailnet AND
  `clusters/nishir/overlays/tailnet` (greps: hostname split clean — one
  `.i.shikanime.studio` in nishir layer, ts.net appended only in tailnet,
  0 `taila659a` hits in the nishir overlay render).
- `nix fmt` scoped to the new dir, then `git add` explicit paths only
  (whole-tree fmt pollutes — see SKILL.md).
- Commit with both trailers (gitlint CC1); PR body `## What/## Why/
  ## References` per sks-pr.
