# Infrastructure ingress → Gateway migration (cluster base level)

Verified 2026-09 on PR #2048 (`manifests`): migrating the last repo-level
`kind: Ingress` resources (flux webhooks) to per-cluster Envoy Gateway planes,
plus the investigation that mapped the remaining chart-generated ingresses and
why they are BLOCKED, not migratable.

## Pattern: cluster-base Ingress → Gateway planes

For each cluster (`nishir`, `telsha`), the webhook Ingress
(`clusters/<c>/base/ingress.yaml` + overlay `patch-ingress.yaml`) became:

- `clusters/<c>/base/gateway.yaml` — Gateway named after the original ingress
  hostname (e.g. `nishir-flux-webhook`), HTTPS Terminate listener,
  `certificateRefs` → the webhook TLS Secret.
- `clusters/<c>/base/httproute.yaml` — HTTPRoute → `webhook-receiver:80`.
- `clusters/<c>/overlays/tailnet/gatewayclass.yaml` — GatewayClass with
  `parametersRef` → the EnvoyProxy.
- `clusters/<c>/overlays/tailnet/envoyproxy.yaml` — `envoyService.type:
  LoadBalancer`, `loadBalancerClass: tailscale`, annotations
  `tailscale.com/hostname: <orig-name>` + `tailscale.com/tags: tag:web`.
  Original names/annotations preserved so the tailnet device name is stable.
- `clusters/<c>/overlays/tailnet/patch-gateway.yaml` — adds `parentRefs` to
  the HTTPRoute (base routes have backendRefs only; orphaned without this).

**Nishir public-name variant (post-review):** the nishir webhook was
republished as `webhooks.flux.i.shikanime.studio` — studio-shikanime LE
issuer + HTTPRoute `spec.hostnames` (external-dns publishes it), replacing
the bare MagicDNS name and cluster-CA cert. Telsha keeps the internal-only
name + cluster CA (no public DNS record → ACME impossible). Cert/Gateway/
route names follow the reverse-dns-kebab convention
(`studio-shikanime-i-webhooks-flux`); all three hostname touch points
(hostnames / cert SAN / certRef secret) rename together. GitHub validates
the funnel's public LE cert; the cluster CA only serves the internal hop.

Webhook TLS issues from the **cluster CA issuer** (`telsha`), NOT
studio-shikanime: the bare MagicDNS hostnames have no public DNS record, so
ACME DNS-01 cannot validate. GitHub validates the funnel's public LE cert; the
cluster CA only serves the internal hop (same as the app pattern).

## Per-cluster EG controller prerequisite

A GatewayClass is inert until the Envoy Gateway controller is installed **in
that cluster**. Telsha lacked it: adding the plane required
`clusters/telsha/components/envoy-gateway/` (Component + ks.yaml) +
`infrastructure/envoy-gateway/overlays/telsha/` (mirrors the nishir overlay).
Check a cluster's `components/` for `envoy-gateway` before assuming its
GatewayClass will be adopted.

## BLOCKED class: chart-generated Tailscale ingresses — do NOT migrate

Three HelmRelease chart ingresses remain on `ingressClassName: tailscale` and
must stay there:

- victoria-metrics `telemetry` (`infrastructure/victoria-metrics/overlays/nishir/patch-hr.yaml`)
- victoria-logs `logs.taila659a.ts.net` (`infrastructure/victoria-logs/overlays/nishir-tailnet/patch-hr.yaml`)
- longhorn UI `nishir-longhorn` (`infrastructure/longhorn/overlays/nishir-tailnet/patch-hr.yaml`)

They are helm-values objects (touched via `postRenderers` JSON6902 patches),
not repo manifests — `grep 'kind: Ingress'` on the repo finds only the patch
targets, not resources. Why migration is impossible today:

1. `logs.taila659a.ts.net` / `telemetry.taila659a.ts.net` serve **Let's
   Encrypt certs issued via Tailscale's own DNS-01 on the ts.net zone**
   (verified: `openssl s_client` → issuer Let's Encrypt, verify ok). Tailscale
   controls the zone; cert-manager via the Cloudflare issuer cannot obtain
   certs for `*.taila659a.ts.net` or short names like `telemetry`.
2. Every fleet host remoteWrites to those exact URLs with **strict OS trust**
   (`machines/modules/{nixos,darwin}/profiles/base.nix`:
   vmagent → `https://telemetry.taila659a.ts.net/insert/0/prometheus`,
   vlagent → `https://logs.taila659a.ts.net/insert/0/logs`). No cluster-CA
   distribution exists in the machines repo, so cluster-CA termination breaks
   ingestion fleet-wide and silently.

**Longhorn UI: migrated 2026-09 (PR #2048), superseding item 3.** The browser-only
objection was wrong as stated — the UI is exposed at
`longhorn.i.shikanime.studio` (public name → studio-shikanime LE DNS-01, not a
ts.net alias), external-dns publishes the record, UI returns 200 with SAN match.
Three moving parts beyond the standard BYOD pattern:

- Suspend `infrastructure-longhorn` before live smoke, RESUME after — the
  HelmRelease otherwise reverts the chart ingress out from under the test.
- Chart `longhorn-ui-frontend` NetworkPolicy admits only its own ingress —
  envoy-gateway-system dataplane pods time out (`upstream connect error`,
  reset reason: connection timeout) until a postRenderer patch admits
  `envoy-gateway-system`.
- The chart keeps its own ingress serving the ts.net name during the test —
  404/old-name behavior is the chart ingress, not the new gateway.

Recovery path if ever needed: full cross-repo campaign (in-cluster DNS
resolver + Tailscale Split DNS + machines-repo CA distribution) BEFORE
touching the ingresses.

## Chart-managed UI via knix extraConfig (machines side)

The flux-operator UI (NixOS leader, RKE2) is a fourth case: its tailscale
Ingress is not in manifests at all — it is chart values stamped by the
`machines` repo via `services.knix.addons.flux.operator.extraConfig.web.ingress`
(knix `recursiveUpdate`s extraConfig into chart values; the chart renders the
Ingress). knix CANNOT render Gateway API objects — the route must ship from
manifests while the ingress removal ships from machines (two PRs, dependency
ordered: gateway live first, then remove the old ingress).

Multi-repo campaign shape (verified live, PRs #2051 manifests + #1253
machines, 2026-09):

1. **manifests**: `infrastructure/<operator>/` holds ONLY the exposure plane —
   base kustomization + `httproute.yaml` (no helmrepo/hr/ns: the chart itself
   is owned by knix/RKE2 on the host). Overlay per cluster with app labels.
   A `clusters/<c>/components/<operator>/` Component (ks.yaml only, pointing
   at the overlay) wired into the cluster overlay's components list creates
   the Flux Kustomization that applies the route.
2. **machines**: delete the `extraConfig.web.ingress` block. Chart netpol
   check: `flux-operator-web` admits `namespaceSelector: {}` on 9080, so
   envoy-gateway-system is already admitted (unlike longhorn's
   allow-own-namespace netpol, which needed a postRenderer patch).
3. **Same-Gateway multi-service layout**: an existing BYOD Gateway serving
   webhook traffic gains a second listener. Two HTTPS listeners on :443 MUST
   set per-listener `hostname:` (api-server rejects "Combination of port,
   protocol and hostname must be unique for each listener") — which also makes
   host→listener routing explicit. Each listener gets its own cert Secret
   (reverse-dns-kebab: `studio-shikanime-i-webhooks-flux` /
   `studio-shikanime-i-flux`); one route per listener parentRef
   (`sectionName: https-ui`).

Live-verify BEFORE PR (Flux applies from main, so pre-merge smoke means
kubectl-apply of rendered docs): Gateway Programmed, new cert Ready, route
Accepted, `curl --resolve <host>:443:<lb-ip>` → 200/SAN-match. The
prerelease Kustomization shows `ArtifactFailed: kustomization path not found`
until the PR merges — expected, not a bug.

## ts.net aliases are SAN-dead after an app migrates

A Gateway serves only the SAN on its cert (e.g. `forgejo.i.shikanime.studio`).
The `<app>.taila659a.ts.net` alias still resolves to the same device but
**fails strict TLS verify** — verified: `git ls-remote
https://forgejo.taila659a.ts.net/...` → `SSL: no alternative certificate
subject name matches target hostname`. The public name verifies cleanly.

Rule: after migrating any app, sweep TLS-client consumers of its ts.net alias
and switch them to the `i.shikanime.studio` name. Found live: machines-repo
`comin` still pointed at `forgejo.taila659a.ts.net` → fleet pulls failing TLS
verify. Check `machines/modules/*/profiles/base.nix` and SOPS configs.

## Scope note for "migrate infrastructure ingress" asks

`grep -rn 'kind: Ingress' infrastructure/` returning patch-target hits does
NOT mean unmigrated ingress surface remains. Classify each hit: repo manifest
(migrate) vs HelmRelease `postRenderers` target (chart object — blocked class
above) vs netpol `ingress:` keys / external-dns `sources:` (not resources).
External-dns keeps `sources: [ingress]` — inert once no Ingress objects exist.
