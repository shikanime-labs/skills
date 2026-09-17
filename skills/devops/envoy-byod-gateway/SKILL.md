---
name: envoy-byod-gateway
description: "Use when giving a K8s app its own Tailscale Envoy Gateway."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - kubernetes
      - envoy-gateway
      - tailscale
      - byod
      - gateway-api
      - shikanime-labs
    related_skills:
      - kustomize-overlay-authoring
      - envoy-ai-gateway
      - tailnet-acl
      - verify-k8s-crds
platforms:
  - linux
  - macos
---

# Envoy BYOD Gateway (Tailscale)

Give an app its own L4 data plane: Envoy Gateway operator fronted by the Tailscale Kubernetes operator (BYOD = "bring your own data plane"). Replaces routing through the shared Traefik `nishir` Gateway; proven by `apps/inference` in the shikanime `manifests` repo. For apps needing UI TLS + raw TCP/UDP (sync, game, p2p) on one tailnet device, or data-plane isolation.

## When to use

- "Give <app> its own gateway / envoy / tailscale device."
- Migrating an app off the shared Traefik Gateway to a dedicated Envoy Gateway.
- App needs mTLS client-cert validation end-to-end: an L7 ingress terminates and cannot forward it; L4 tailscale passthrough does.

## Structural pattern (per app)

Create in the app `base/`:

1. **`gatewayclass.yaml`** — `GatewayClass`, `controllerName: gateway.envoyproxy.io/gatewayclass-controller`, `parametersRef` → the `EnvoyProxy` (same namespace; GEP-3262 pins `parametersRef` to same namespace).
2. **`envoyproxy.yaml`** — `EnvoyProxy` with `provider.type: Kubernetes`, `envoyService.type: LoadBalancer`, `loadBalancerClass: tailscale`, annotation `tailscale.com/hostname: <unique-name>`. Stable `envoyService.name` keeps the tailnet hostname independent of EG's generated names.
3. **`gateway.yaml`** — `Gateway` with `gatewayClassName` → the class and `infrastructure.parametersRef` → the `EnvoyProxy`. Listeners: `https` (443, HTTPS Terminate, `certificateRefs` → a `Certificate`) plus `TCP`/`UDP` listeners on the app's ports (e.g. 22000).
4. **`cert.yaml`** (overlay) — `Certificate` from the cluster `ClusterIssuer` (e.g. `nishir`); SAN includes the tailnet hostname.
5. Reparent `HTTPRoute`/`TCPRoute`/`UDPRoute` to the new Gateway's `name` + `sectionName`; drop the shared gateway parentRefs.

In the overlay: drop the old in-pod TLS component (`components/tls`) and the `BackendTLSPolicy` (TLS now terminates at the Gateway).

**Caddy reverse-proxy migration** (path routing, header rewrites, static responses → native Gateway API: HTTPRoute + RequestHeaderModifier, BackendTLSPolicy, EnvoyPatchPolicy, cleanup checklist): `references/caddy-to-gateway-api.md`. Proven on `apps/synapse-proxy` (PR #2057).

References (with load conditions):
- Known-good manifests: `references/envoyproxy.yaml`, `references/gateway.yaml`.
- Wedged-proxy recycle, TCP `nc` probe, status jsonpath traps, Flux reconcile quirk: `references/tailscale-proxy-recovery.md`.
- Live dataplane-namespace verification, netpol `tailscale-system` trap, multi-install smell: `references/dataplane-netpol.md`.
- Public-endpoint verification when external curl fails (in-cluster TLS-handshake proof; "TCP-open/TLS-reset = tailscale proxy not gateway" signature; EG-namespace PodSecurity trap): `references/public-endpoint-verify.md`.
- Custom-domain tailnet-only resolution + dead-public-A trap: `references/custom-domain-tailnet.md`.
- **Standard public hostnames** — `<app>.i.shikanime.studio` via external-dns publishing the tailnet CGNAT A to Cloudflare + centralized LE cert: the DEFAULT exposure pattern for all apps. Per-app recipe, cert/netpol touch points, batch-migration workflow: `references/public-hostname-migration.md`. (Internal-resolver recipe below is only for arbitrary non-`i.` domains.) Batch migration as per-app stacked PRs (user-preferred over mega PRs): `references/pr-campaign-split.md`.

External-DNS auto-publishes A/AAAA from a Gateway/HTTPRoute: `infrastructure/external-dns/base/hr.yaml` sets `sources: [gateway-httproute, ingress, service]`, `domainFilters: [shikanime.studio, i.shikanime.studio]`. Once an HTTPRoute carries `hostnames: [<app>.i.shikanime.studio]` and the zone is in `domainFilters`, the record appears with no manual DNS edit — but the cert must already be `Ready` (see `sks-tls`). **The route must actually carry `spec.hostnames`**: external-dns reads HTTPRoute hostnames, not Gateway listeners; a hostless route publishes NOTHING, silently (Gateway Programmed, cert Ready, DNS empty). Verified live: one `hostnames:` entry → A record in ~30s.

### 0. Identity-header injection happens at the L7 Funnel Ingress, not the BYOD LB

**CORRECTED 2026-09-02 (copyparty, PRs #2068/#2073):** an earlier revision claimed `tailscale.com/auth: "true"` on `EnvoyProxy` annotations makes the operator inject `Tailscale-User-Login` on the BYOD LB path — live-verified WRONG. A `loadBalancerClass: tailscale` LB Service is L4-only; its `ts-<app>-*` proxy StatefulSet forwards TCP and CANNOT inject headers. Injection happens only at the **L7 Tailscale Ingress** (`ingressClassName: tailscale` + `tailscale.com/funnel: "true"`), whose proxy dials the Envoy LB Service on **443**. An app consuming `Tailscale-User-Login` (e.g. copyparty `idp-h-usr`) behind a BYOD LB gets NO identity header — route it through a funnel Ingress (see `shikanime-gateway-routing` "Funnel Ingress placement") or use another auth mechanism. Do not add `tailscale.com/auth` to EnvoyProxy annotations.

Security boundary: the funnel terminates TLS at Tailscale, but any tailnet member can forge a `Tailscale-User-Login` header — header-auth apps are fail-open inside the tailnet and MUST NOT also be exposed on a public hostname without an Envoy-side header-scrub guard (issue #2067).

## Custom domains within the tailnet

A BYOD Gateway is a `*ts.net` device — tailnet-only, never public. To answer a custom domain (e.g. `app.example.com`) from tailnet devices, follow the official Tailscale "custom domains with Gateway API" recipe: resolves inside the tailnet only — NOT public exposure. Chain (each link required):

1. Envoy Gateway on the tailnet LB (structural pattern above): stable `*.ts.net` hostname (e.g. `inference.taila659a.ts.net`) + stable tailnet IP (e.g. `100.103.240.115`, 100.64.0.0/10 CGNAT). **Read the IP from `tailscale status --json` (`Peer[].TailscaleIPs`) or the `ts-<app>-*` proxy Secret — `kubectl get svc … -o jsonpath='{.status.loadBalancer.ingress[0]}'` returns the hostname, not the IP.**
2. **Internal DNS resolver** in-cluster, on its own tailnet LB (small CoreDNS or Pi-hole); authoritative for the custom zone only.
3. **Tailscale Split DNS** (manual, in Tailscale control — NOT a k8s manifest): DNS → Add nameserver → Custom → resolver's tailnet IP → *Restrict to search domain* → `example.com`. The one by-hand step; the cluster cannot set it.
4. **ExternalDNS writes the `A` into the internal resolver**, not the public zone. For a **single** name skip external-dns: a static CoreDNS `file` zone is the minimum (below); use external-dns + coreDNS `rfc2136` only for many domains.
5. **LE DNS-01 keeps Cloudflare — ONLY for the `TXT` challenge.** Let's Encrypt validates from the public internet and does not care that the `A` is internal. Keep the Cloudflare issuer; stop publishing the public `A`.

### Minimum resolver for one name (Ponytail)

```yaml
# ConfigMap coredns (ns internal-dns)
data:
  Corefile: |
    .:53 { errors health ready file /etc/coredns/zones example.com }
  zones: |
    example.com. IN SOA internal-dns.example.com. admin.example.com. 1 7200 3600 1209600 3600
    example.com. IN NS internal-dns.example.com.
    app.example.com. IN A 100.103.240.115
    app.example.com. IN AAAA fd7a:115c:a1e0::ca2b:f074
```
CoreDNS Deployment + `LoadBalancer`/`tailscale` Service (`tailscale.com/hostname: internal-dns`, `tailscale.com/expose: "true"`), 2 replicas. A `file` zone is authoritative for `example.com` ONLY; add `forward . /etc/resolv.conf` to recurse. Full recipe + verification: `references/custom-domain-tailnet.md`.

## Pitfalls

### 1. Tailnet device-name collision → cert SAN mismatch

If `tailscale.com/hostname` is already reserved (real peer or stale proxy), the operator auto-suffixes (`syncthing` → `syncthing-1`) but the `Certificate` SAN and `HTTPRoute` `hostnames` keep the un-suffixed name → **UI TLS breaks** (SAN mismatch).
- **Detect:** `tailscale status --json` shows a `Peer` with `HostName` equal to your chosen name, not a cluster object you own → taken.
- **Fix:** pick a distinct gateway hostname (e.g. `<app>-gw`). SAN, `tailscale.com/hostname`, `HTTPRoute` `hostnames` must all match the *final* device name. A real peer's device is not deletable from the cluster; deleting an orphan `ts-<app>-*` proxy SVC does NOT free a name held by a separate tailnet device — the reservation lives in the tailnet.

### 2. NetworkPolicy blocks gateway ingress (TCP/UDP time out)

Envoy data-plane pods run in the EG controller's `targetNamespace` — **`envoy-gateway-system`** here (post-split; old `envoy-system` orphaned), NOT the Gateway's namespace (`shikanime`). If the app `NetworkPolicy` only admits `kube-system` (e.g. metrics scrape), the gateway can't reach the pod: TCP 22000 connects from outside but times out; L7 (443) may still answer (listener is on the data plane, not the pod).
- **Fix:** ONE `namespaceSelector` ingress rule for `envoy-gateway-system` (label `kubernetes.io/metadata.name`) on the app's ports; podSelector `app.kubernetes.io/name: envoy` — EG's real dataplane label. **Do NOT use `shikanime/envoy`**: that's the Gateway's namespace. (Verified live: syncthing dataplane = `envoy-gateway-system/envoy-shikanime-syncthing-…`, label `app.kubernetes.io/name: envoy`, `owning-gateway-name: syncthing`. Do not netpol against orphaned `envoy-system`.)
- **Do NOT add `tailscale-system` to the netpol.** Tailscale only *programs* the Envoy `LoadBalancer` Service (BYOD); it never sources pod-to-pod traffic — that rule permits a nonexistent hop. Real path: `tailscale LB → envoy svc (shikanime) → envoy pod (envoy-gateway-system) → app pod`, already covered above.
- **Silent under default-deny:** `clusters/nishir/base/netpol.yaml` is `podSelector: {}` + Ingress default-deny; once ANY netpol selects the pod, a wrong namespace selector blocks ALL traffic with no error. **Verify the live dataplane namespace before merge** — `references/dataplane-netpol.md`.
- Worked example: `apps/syncthing/overlays/nishir-tailnet/netpol.yaml` — `envoy-gateway-system`/`app.kubernetes.io/name: envoy` on `http,sync,sync-udp` + `monitoring-system`/`vmagent` on `metrics`. (Old `apps/syncthing/base/netpol.yaml` deleted; netpol lives only in the tailnet overlay.)

### 3. Envoy data-plane container is distroless

`kubectl exec -c envoy -- sh` fails (`executable file not found`): no shell. Don't `ss`/`netstat` inside it — verify from a separate debug pod (below).

### 4. External `nc` may time out spuriously

Local `nc <app>-gw.taila659a.ts.net 22000` can time out on tailnet **egress** from the operator machine while the cluster path is healthy. Always confirm with an in-cluster probe before declaring the gateway broken.

### 5. Proxy wedged on a stale/orphaned tailnet device (NeedsLogin)

After a gateway hostname rename (e.g. `syncthing-gw` → `syncthing`) or freeing a reserved name, the `ts-<app>-*` StatefulSet in `tailscale-system` can bind the **old device**, get logged out, never re-register. Unlike #1 (collision → suffix), the operator silently keeps the dead device.
- **Detect:** proxy pod logs `Auth key missing or invalid (NeedsLogin state)` / `Waiting for operator to provide new auth key`; proxy Secret (`ts-<app>-<hash>-0`) `device_fqdn` still OLD name, `reissue_authkey` empty; `tailscale status --json` shows **neither** name as peer.
- **Symptom:** `Gateway` `Programmed=True`, listeners up, but the data-plane `Service` `status.addresses[].value` still advertises the stale `…-gw.taila659a.ts.net`; MagicDNS NXDOMAIN for both names. Manifests are correct — only the live proxy is wedged.
- **Fix (live recovery, not a manifest change):** delete the wedged proxy StatefulSet + credential Secret so the operator recreates a fresh proxy under the current `tailscale.com/hostname`:

  ```sh
  kubectl -n tailscale-system delete statefulset ts-<app>-<hash> --ignore-not-found
  kubectl -n tailscale-system delete secret       ts-<app>-<hash>-0 --ignore-not-found
  # operator recreates ts-<app>-<hash> within ~20s; pod logs show "Startup complete"
  # confirm: secret device_fqdn == <app>.taila659a.ts.net
  ```

Verify the new proxy logs in (no `NeedsLogin`), re-test MagicDNS + UI. Do NOT edit app manifests — the annotation is already correct.

### 6. Custom domain via *public* external-dns writes a dead `A` record

(**Superseded for standard hostnames** — fleet publishes `<app>.i.shikanime.studio` into a dedicated Cloudflare zone, see `references/public-hostname-migration.md`; still applies to arbitrary non-`i.` domains.) Writing the tailnet IP (`100.103.240.115`, CGNAT) into the public Cloudflare zone gives a name that:
- **off-tailnet:** times out — `100.64.0.0/10` is not internet-routable (curl `HTTP_CODE=000`), regardless of `proxied:false`.
- **inside the tailnet:** does NOT resolve — no Split DNS, no internal resolver for `example.com`.

Data plane stays fine (`<app>.ts.net` serves 200); only the mapping breaks (hit on `inference.shikanime.studio`). **Fix:** publish the `A` into the internal resolver (chain step 4) + Split DNS; Cloudflare for LE DNS-01 `TXT` only. If `bitnamicharts/external-dns` OCI pull 401s (Bitnami gates OCI), prefer the static CoreDNS zone — external-dns is YAGNI for one name.

### 7. `EnvoyProxy` Service status shows hostname, not IP

`kubectl -n envoy-gateway-system get svc <app> -o jsonpath='{.status.loadBalancer.ingress[0]}'` returns `{"hostname":"<app>.taila659a.ts.net"}`. For a static DNS `A`, get the stable tailnet IP from `tailscale status --json` (`Peer[].TailscaleIPs`, first = IPv4) or the `ts-<app>-*` proxy Secret in `tailscale-system`; stable across proxy restarts.

### 8. FTP passive data: `ftp-nat` is a literal IP, not a hostname

Migrating an FTP app (e.g. copyparty) off a direct Tailscale `LoadBalancer`: `ftp-nat` (pyftpdlib `masquerade_address`) is stamped **verbatim** into the PASV reply as a dotted-quad — does NOT resolve a hostname; a hostname corrupts passive mode. Set a **static tailnet IP** (pin via `tailscale.com/tailnet-ip` on the `EnvoyProxy` `envoyService`, reusing a released IP from the deleted LB). Gateway caps at **64 listeners**: a 100-port passive range (`12000-12099`) can't be 100 listeners — shrink `ftp-pr` to match (we used `12000-12009`), one `TCPRoute` per `ftp-data-<port>` listener. Full recipe + `nix fmt` whole-tree pollution workaround: `references/ftp-via-gateway.md`.

### 9. Gateway ingress netpol in the overlay (`patch-netpol`); base is deny-by-default

The `envoy-gateway-system`/`app.kubernetes.io/name: envoy` ingress source is tailnet-specific. On "move envoy/tailscale related to overlay using patch-netpol": strip `base/netpol.yaml` to deny-by-default skeleton (`ingress: []` + `podSelector` + `policyTypes`); carry the envoy `from:` block (all ports, incl. `ftp-data-N`) in `overlays/nishir-tailnet/patch-netpol.yaml` (already wired in that overlay's `kustomization.yaml`). Verify the rendered overlay has exactly ONE envoy `from:` block and `grep -c tailscale-system` on rendered output is 0 — the old rule is dead weight (#2). Caveat: deny-by-default base means a plain-`nishir` overlay ships NO ingress until it adds its own patch; only do this for `nishir-tailnet`-only apps. Full pattern: `references/ftp-via-gateway.md` "Netpol belongs in the overlay".

### 10. Inherited session summaries about migration progress go stale

Do NOT trust a session-start summary's claim of apps migrated / doc state — the Gateway-API rollout is in active flux; summaries lag the repo by days (one claimed "5 apps migrated" + "mermaid not started" while ~19 apps were on Gateway API and the doc committed). Before asserting state, run read-only `search_files` for `kind: Gateway` / `gatewayClassName:` / `kind: HTTPRoute` and read the actual overlays. Ground every architecture/migration claim in a fresh grep, not memory.

### 11. Backend TLS mode must match the Gateway (two symmetric failure modes)

Post-migration the Gateway terminates TLS and speaks **plain HTTP** to the backend. Two breakages when the app's TLS config is inconsistent:
- **App serves TLS, Gateway sends HTTP** → every request 400s with `"Client sent an HTTP request to an HTTPS server"` (`via_upstream` in EG access logs). Fix: `BackendTLSPolicy` on the Service (`sectionName: <tls port name>`), `validation.hostname` = the **pod cert's SAN** (e.g. `dex.shikanime.svc.cluster.local`), `caCertificateRefs` → trust-manager bundle ConfigMap (`nishir-ca-certificates.crt`). Proven on dex.
- **App redirects HTTP→its own HTTPS port** (Jellyfin `EnableHttps`/`RequireHttps=true` → `307 https://<host>:8920/...`, a port nothing serves behind the gateway) → browser dead-ends. Fix: disable in-container HTTPS. Jellyfin docker images honor `JELLYFIN_<ConfigKey>` env overrides (`JELLYFIN_EnableHttps=false`, `JELLYFIN_RequireHttps=false`) seeding `network.xml` on the PVC; also patch the live PVC file + delete the pod to re-read. If the app had `components/tls` (HTTPS probes, keystore mount, Certificate + pkcs12 secret), REMOVE it — with in-pod HTTPS off its HTTPS probes fail, pod flips 0/1 → gateway 503.

Adding/changing a `BackendTLSPolicy`: delete the stale `CertificateRequest` if stuck `RequestChanged` — cert-manager won't replace it on its own.

**`components/tls` split pattern (forgejo variant):** apps whose tls component makes the POD serve TLS (cert mount, HTTPS probes, svc port renamed `https`) must point the HTTPRoute backendRef at that **https service port** + a BackendTLSPolicy — else plaintext hits a TLS-only backend, every request 400s (`via_upstream`). Forgejo broke this way: route → svc port 80 while the component published https:443. Audit after any tls-component change: `kubectl get httproute <app> -o jsonpath='{.spec.rules[0].backendRefs[0].port}'` vs the component's `patch-svc.yaml` https port. Apps whose svc `https` port has `targetPort: http` (copyparty, syncthing) are the plaintext-proxy pattern — route matching the same port is correct, no policy needed. Apps that only *prefer* TLS but answer plaintext (prowlarr, caddy-based synapse-proxy on 8008/8448) work either way — verify before "fixing".

### 12. Jellyfin end-state: app owns TLS, gateway re-encrypts (per-user directive)

Jellyfin keeps `EnableHttps/RequireHttps=true` with its keystore cert, serving **both** protocols: TWO listeners — `http:80` and `https:443` (HTTPS Terminate) — each with its own HTTPRoute (`jellyfin` → backend svc port 8096 parent http; `jellyfin-https` → backend svc port 8920 parent https) plus a BackendTLSPolicy on svc port 443 (`targetPort: https` → pod 8920). Do NOT collapse to one route with two rules (#14). Key facts:
- `JELLYFIN_*` env overrides apply only at config **generation** (first boot); the PVC `network.xml` is authoritative after — patch it live AND restart the pod when changing flags.
- PublicHttpPort/PublicHttpsPort advertise 80/443 so RequireHttps redirects land on standard ports.
- `components/tls` owns the https side (keystore mount, HTTPS probes, second `httproute.yaml`, BackendTLSPolicy).
- Quirk: plain-http `/web/` paths may 307 to internal https :8920 unless Jellyfin's known-proxies/X-Forwarded-Proto handling is set.

### 13. New gateway listener ports need a tailscale ACL grant

The ts operator proxy drops traffic to ports not permitted by the tailnet ACL — ts proxy logs `Drop: TCP{... :80} no rules matched`, curl times out though Envoy + routes are correct. New listener (e.g. `http:80`) needs an ACL grant (`shikanime-labs/tailnet` `policy.hujson`, grants: member → `tag:web` now allows `["80","443"]`). After changing listeners, delete the `ts-<app>-*` proxy pod so the operator reprograms it (doesn't always pick up new ports while running).

### 14. One HTTPRoute per listener, not one route with many rules

Gateway API `spec.rules` apply to ALL parent listeners — one route attached to http+https with two backend rules doesn't bind rule→listener; https traffic can hit the plaintext backend. Pattern: one HTTPRoute per listener (`<app>` parent http, `<app>-https` parent https), single rule each. A component adding a NEW route (not patching one) must list the file under the component kustomization's `resources:` — a new-resource file under `patches:` fails the build with "no matches for Id".

### 15. Rewrite the upstream Host with `URLRewrite`, never `RequestHeaderModifier`

To rewrite the Host header Envoy sends a backend (e.g. Synapse `server_name` `matrix.taila659a.ts.net`), **do NOT use `filters: [{type: RequestHeaderModifier, requestHeaderModifier: {set: [{name: Host, value: ...}]}}]`** — EG v1.9 rejects it (Host is a reserved header the filter may not set). The rule drops as `PartiallyInvalid: Dropped Rule(s) [N]` and returns **HTTP 500**. EG log signature: `RequestHeaderModifier Filter did not provide valid configuration to add/set/remove any headers`. Use:
```yaml
backendRefs:
  - name: synapse
    port: 8448
filters:
  - type: URLRewrite
    urlRewrite:
      hostname: matrix.taila659a.ts.net
```
(`backendRefs[].hostRewrite` is spec-preferred when the installed HTTPRoute CRD exposes it; shikanime CRD v1.6.1 does not — use `URLRewrite`.) Confirm `ResolvedRefs=True`, no `PartiallyInvalid`. Bit post-merge on `apps/synapse` Sept 2026: the `RequestHeaderModifier.set Host` pattern survived review across several PRs, live EG v1.9 dropped both `matrix` and `matrix-discord-media` fallback rules; fixed by a follow-up URLRewrite PR after live validation.

### 16. Migrate in-app config files, not just manifests

PVC-hosted configs keep legacy hostnames after a hostname migration while manifests render green. Sweep before declaring done: `kubectl exec <pod> -- grep -rl taila659a /config /data 2>/dev/null | grep -vE 'logs|\.db|\.sqlite'`
- **jellyfin** `config/network.xml` — `PublishedServerUriBySubnet` (client redirect target) + HTTPS flags.
- **qbittorrent** `qBittorrent.conf` — `WebUI\ServerDomains` + `HostHeaderValidation=true` reject Hosts not listed; add the new domain (keep old during transition), restart pod.
- **vaultwarden** `config.json` — `domain` + `sso_callback_path`; also the `DOMAIN` env (encrypted). Patch the disk file too — env only wins at runtime.
- **synapse/mautrix/dex** — identity domains; see server_name note in memory.
- **LEGITIMATE stays:** remote peer addresses (syncthing `<device>.taila659a…` device entries), tailnet-internal service URLs consumed over the tailnet (honho → `ai.`, hermes-agent platform peers, victoria-logs ingest).

### 17. Orphan patch file = silent no-op

A `patch-*.yaml` in an overlay dir does NOTHING unless the overlay `kustomization.yaml` lists it under `patches:` (with a `target`). The jellyfin tailnet `patch-sts.yaml` was orphaned for the whole gateway migration — env edits rendered fine in isolation, live STS never changed. Before trusting a patch edit: `grep -n "patch-sts\|patches:" <overlay>/kustomization.yaml` and render the overlay — the patched field must appear in `kustomize build` output.

### 18. Stale healthCheck in cluster overlay after deleting a workload

Migration deleting a workload (e.g. Caddy pod → Gateway API routes) can leave a `healthChecks` entry for the deleted StatefulSet/Deployment in the cluster overlay `ks.yaml` → Flux hangs on a gone pod, or `HealthCheckFailed`. **Detect:** `grep -n "name: <old-workload-name>" clusters/<cluster>/overlays/<overlay>/ks.yaml` **Fix:** remove the `healthChecks:` block (or entry):
```yaml
# BEFORE (stale):
spec:
  healthChecks:
    - apiVersion: apps/v1
      kind: StatefulSet
      name: synapse-proxy    # <-- deleted
      namespace: shikanime
  interval: 10m

# AFTER:
spec:
  interval: 10m
```
The Kustomization `path:` stays correct; only the healthCheck references a resource that no longer exists.

### 19. Folding a standalone proxy/gateway app into the app it fronts

Merging a reverse-proxy app into the backend app's tree (`apps/synapse-proxy/` → `apps/synapse/`) tracks files as `R`enames; the block becomes the last `apps-<app>` Flux Kustomization.
- **`envoyService.name == app name` does NOT collide.** Renaming gateway/GatewayClass/EnvoyProxy/tailscale-hostname from `<proxy>` to the backend name (`synapse`) looks like a collision with backend `shikanime/synapse` ClusterIP — it is not: the LB Service lives in **`envoy-gateway-system`** (EG's `targetNamespace`) → `envoy-gateway-system/synapse`. Only check tailnet-device-name availability (#1): `tailscale status --json | grep <name>` — safe if only the old `<proxy>` device exists. Verify live before merge: `kubectl get svc <proxy> -n envoy-gateway-system`.
- **Drop stale same-namespace proxy podSelectors.** The old proxy was a pod in `shikanime`, so the backend base netpol (and bridge netpols like `mautrix/discord`) carried `app.kubernetes.io/name: <proxy>` podSelectors; post-merge they match nothing (data plane now in `envoy-gateway-system`). Remove every `<proxy>` podSelector or traffic silently breaks under default-deny.

Full file-by-file recipe: `references/merge-proxy-into-backend.md`.

### 20. Chart-generated Tailscale ingresses are a BLOCKED migration class

HelmRelease chart ingresses (victoria-metrics `telemetry`, victoria-logs `logs.taila659a.ts.net`, longhorn UI `nishir-longhorn`) CANNOT move to Envoy TLS-Terminate: Tailscale provisions their ts.net LE certs via its own zone DNS-01, which cert-manager cannot do, and fleet hosts remoteWrite both ingestion URLs with strict OS trust — cluster-CA certs break ingestion fleet-wide, silently. They live in `postRenderers` patches, not repo manifests. Full evidence + ts.net-alias-SAN-death follow-up (comin fleet pulls broke on `forgejo.taila659a.ts.net` after its app migrated): `references/infrastructure-ingress-migration.md`.

### 21. Cluster-base webhook Gateway requires the EG controller in THAT cluster

A per-cluster Gateway plane (e.g. flux webhook) is inert without the `envoy-gateway` component in that cluster's `components/` — telsha needed `clusters/telsha/components/envoy-gateway/` + `infrastructure/envoy-gateway/overlays/telsha/` added alongside the plane. Bare MagicDNS webhook hostnames take the cluster CA issuer (no public DNS for ACME); file-by-file pattern: `references/infrastructure-ingress-migration.md`.

### 22. Hostname-bearing chart UIs live in manifests, not chart values

Chart-managed UI (flux-operator via knix, longhorn via postRenderers) getting `<name>.i.shikanime.studio`: HTTPRoute+Certificate ship from manifests (`infrastructure/<operator>/` with only the exposure plane + a cluster components/ KS); the old ingress block is removed in a DEPENDENCY-ORDERED second PR in the owning repo (machines `extraConfig` block, or the chart-values patch). Two HTTPS listeners on one Gateway MUST carry per-listener `hostname:` (port/protocol/hostname uniqueness) — also pins host→listener routing. Verify the plane live (kubectl apply of the rendered route + `curl --resolve`) BEFORE the PR; the Flux Kustomization stays ArtifactFailed ("path not found") until merge — expected. Full campaign shape: `references/infrastructure-ingress-migration.md`.

## SOPS in this repo — practical loop

- `.sops.yaml` is NOT committed; devenv generates it from `flake.nix` creation rules. Outside devenv (plain worktree) it is missing → `sops -e` writes zero bytes or whole-file encryption. Regenerate rules from `flake.nix` (per-app `encrypted_regex` + key_groups with workstation + cluster age keys) or copy from a sibling worktree.
- **Always** `sops -e --input-type yaml --output-type yaml --filename-override <real-path-in-repo> <tmpfile> > <real-path>` — without `--filename-override`, sops matches `path_regex` against the temp-file path, finds no creation rules (zero-byte or JSON output). On decrypt a non-`.yaml` extension (e.g. `.new`) breaks type detection — move to the final path before verifying.
- Round-trip verify after every edit: `ENC\[` count equals the original's, `sops -d` succeeds, expected plaintext fields changed. sops re-normalizes indentation on re-encrypt (2-space YAML default) — run the repo formatter only if CI's treefmt demands it (plain `nix fmt` outside devenv disagrees with devenv treefmt on sops files; trust CI).
- Pre-existing MAC mismatch (edited out-of-band historically): `sops -d --ignore-mac` is normal for reading; always re-encrypt so the new MAC is computed.
- Vaultwarden's `DOMAIN` is encrypted via the generic catch-all rule, not an app-specific `encrypted_regex` — if flake rules change, re-check it still lands encrypted.

## Verification

Live-cluster shortcuts:
- Dataplane config changes may not reach long-running dataplane pods: `rollout restart deploy envoy-shikanime-<app>` in `envoy-gateway-system` (or delete pods) after gateway/listener changes if traffic still hits the old shape.
- Quick plaintext-vs-TLS check of a pod port: `kubectl exec <pod> -- curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://localhost:<port>/<path>`.

### In-cluster reachability probe (authoritative)

Cluster `PodSecurity` is `restricted` — a debug pod needs a full securityContext; plain `kubectl run alpine` is rejected. Use the compliant pod in `references/probe-pod.yaml`, then `kubectl -n envoy-system logs synctest`. It probes TCP from inside `envoy-system` to both the pod IP and the `envoy-system` Service — if those open, NetworkPolicy + routing are correct; any external timeout is tailnet egress, not a cluster fault.

Checklist (live):
- `Gateway` `status.conditions`: `Accepted=True`, `Programmed=True`.
- `HTTPRoute`/`TCPRoute`/`UDPRoute` `status.parents[].conditions`: `Accepted=True`, `ResolvedRefs=True`.
- `Certificate` `Ready=True`, SAN includes the tailnet hostname.
- Data-plane `Service` in `envoy-system` has `EXTERNAL-IP`/hostname = your `tailscale.com/hostname`.
- In-cluster TCP probe opens; UI over TLS returns 200 with SAN-matched cert.

### Status-query traps

- **BackendTLSPolicy nests under `.status.ancestors[]`.** Top-level `jsonpath='{.status.conditions[?(@.type=="Accepted")].status}'` returns *empty* — the policy is actually `Accepted=True`. Read: `kubectl -n <ns> get backendtlspolicy <app> -o jsonpath='{.status.ancestors[0].conditions[?(@.type=="Accepted")].status}'`. TCP/UDP routes lack the `Accepted` condition HTTP has; `ResolvedRefs` under their ancestor is the signal that matters.
- **Probe TCP 22000 with `nc`, never `curl`.** Syncthing's 22000 speaks raw TLS — `curl https://<host>:22000/` hangs until timeout even when healthy. Use `nc -z -w 10 <host> 22000` (expect `open` / exit 0). Authoritative: in-cluster through the gateway LB Service: `nc -zv -w 8 <app>.envoy-system.svc.cluster.local 22000` from a debug pod returns `open` when data plane + route are correct.
- **SAN read on macOS** (`openssl` has no `-ext`; parse cert text): `kubectl -n <ns> get secret <tls> -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | grep -A1 'Subject Alternative Name' | tr ',' '\n'`.
- **Flux `reconcile --with-source` can hit a context-deadline inside the command though the source is already fetched.** If the gitrepo artifact is already at the target revision, run plain `flux reconcile kustomization <app>` — applies immediately. `--with-source` can also time out waiting on health while the apply still lands; confirm via `kubectl -n flux-system get kustomization apps-<app> -o jsonpath='{.status.lastAppliedRevision}'` against main. After a reconcile the Kustomization may briefly show READY=False `dependency … is not ready` (stale dependency-eval blip); a plain re-reconcile clears it — confirm the dependency Kustomization is READY before concluding.

## Live-test hygiene
- `flux suspend kustomization <app> -n flux-system` before manual `kubectl apply`, so Flux doesn't revert test objects mid-test; resume (`flux resume …`) or reconcile from Git after.
- Rollback: re-apply the committed overlay and delete the BYOD orphans (`gateway`/`envoyproxy`/`gatewayclass` in the app ns) — Flux only prunes objects it manages, orphans go by hand; the operator then GCs its data plane and frees the tailnet node.

## See also
- `kustomize-overlay-authoring` — editing the overlay kustomizations.
- `envoy-ai-gateway` — AI-gateway variant (different CRDs: AIGatewayRoute); its `references/inbound-apikey.md` is an inbound API-key `SecurityPolicy` recipe (apiKeyAuth on top of mTLS), reusable for any BYOD Gateway that already enforces client-cert mTLS.
- `tailnet-acl` — Tailscale ACL GitOps.
- `verify-k8s-crds` — authoring/reviewing the Gateway/EnvoyProxy CRs.

