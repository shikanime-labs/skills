# Public hostname migration: `<app>.i.shikanime.studio`

Verified fleet pattern (2026-08-30, proven on `inference`, `syncthing`, piloted
on `jellyfin`, then batch-rolled to ALL 27 tailscale-Ingress apps — the old
Ingress pattern is fully retired in `apps/*/overlays/nishir-tailnet/`). Publishes
each app at a real public DNS name that resolves to the tailnet CGNAT IP, with a
trusted Let's Encrypt cert. Off-tailnet clients time out (CGNAT is not
internet-routable) — but the name resolves everywhere, TLS is trusted, and
tailnet clients get a clean hostname without Split DNS or an internal resolver.

This REPLACES the CoreDNS-internal-resolver recipe for new work: external-dns
publishes the CGNAT `A` into the dedicated Cloudflare zone `i.shikanime.studio`.
The old `references/custom-domain-tailnet.md` path is only for arbitrary
non-`i.` domains.

## Prerequisites (already in repo, do not re-create)

- `infrastructure/external-dns/base/hr.yaml`: sources include
  `gateway-httproute`; `domainFilters` include `shikanime.studio` AND
  `i.shikanime.studio`; `policy: sync`, `proxied: false`,
  `txtOwnerId: nishir-external-dns`.
- `configs/cert-manager/overlays/nishir/clusterissuer.yaml`: ClusterIssuer
  `studio-shikanime` (LE prod, Cloudflare DNS-01, zone `shikanime.studio`).
- Per-app Envoy Gateway dataplane in `envoy-gateway-system` (see SKILL.md
  structural pattern).

## Per-app migration recipe (5 touch points)

For app `X` in `apps/X/overlays/nishir-tailnet/`:

1. **Delete `ingress.yaml`** (the old `ingressClassName: tailscale` Ingress).
2. **Create four files** (substitute `X`):
   - `gatewayclass.yaml` — GatewayClass `X`, `parametersRef` → EnvoyProxy `X`
     (group `gateway.envoyproxy.io`, ns `shikanime`).
   - `envoyproxy.yaml` — EnvoyProxy `X`, tailscale LoadBalancer,
     `tailscale.com/hostname: X` (unique tailnet device), stable
     `envoyService.name: X`.
   - `gateway.yaml` — Gateway `X`, single `https` 443 HTTPS-Terminate listener,
     `certificateRefs: [{name: X-i-shikanime-studio-tls, kind: Secret}]`.
     Raw TCP/UDP listeners ONLY if the app needs them (syncthing 22000).
   - `httproute.yaml` lives in **`base/`** (NOT the overlay): HTTPRoute `X`
     with `rules`/`backendRefs` ONLY — no hostnames, no parentRefs.
     backendRef → svc `X` port NAME (every app in this fleet names its web
     port `http`; grep the base `svc.yaml` to confirm). Add it to the base
     `kustomization.yaml` resources. The tailnet overlay then adds
     `patch-httproute.yaml` (HTTPRoute `X` with `hostnames:
     [X.i.shikanime.studio]` + `parentRefs: [{name: X, sectionName: https}]`)
     wired via a `patches:` entry targeting the base HTTPRoute — the syncthing
     model (base = what to route, overlay = where to attach). USER CORRECTION
     (2026-08-30): overlay-resident routes with inline parentRefs were rejected;
     keep base/overlay separation exactly like `apps/syncthing`.
3. **`kustomization.yaml`** — drop `ingress.yaml`, add the four new files.
4. **Public Certificate** — append to the CENTRALIZED
   `configs/cert-manager/overlays/nishir/cert.yaml` (not a per-app overlay):
   name/secretName `X-i-shikanime-studio-tls`, ns `shikanime`,
   dnsNames `[X.i.shikanime.studio]`, issuerRef `studio-shikanime`.
5. **Netpol** — the old `tailscale-system` ingress rule is dead weight
   (Tailscale programs the LB, it never sources pod traffic). Replace with one
   `envoy-gateway-system` + `app.kubernetes.io/name: envoy` rule on the web
   port. Keep the `monitoring-system`/vmagent rule. See SKILL.md pitfall #2.

Known-good example: `apps/jellyfin/overlays/nishir-tailnet/` (post-pilot) and
`apps/syncthing/overlays/nishir-tailnet/`.

## Non-template apps (judge per app, don't force the recipe)

- **Multi-hostname apps** (`hermes-agent`: old Ingress had 4 hosts
  `automata`, `automata-a2a`, `automata-dashboard`, `nishir`): keep ONE
  Gateway with one `https` listener, one cert covering... no — one cert per
  hostname (4 centralized Certificate blocks), and ONE HTTPRoute listing all
  4 `hostnames` with per-hostname `rules[].hostname` overrides routing to
  different service ports (`api-server`/`a2a`/`dashboard`). Gateway-API rule:
  rule-level `hostname` narrows which hostnames that rule applies to.
- **Funnel endpoints** (`tailscale.com/funnel: "true"` on the old Ingress):
  the Envoy pattern has NO funnel equivalent — dropping the annotation drops
  public-internet reachability. Flag to the user before dropping; a funnel
  endpoint needs a separate tailscale-proxied Service, not the Gateway.
- **Service with `ports: []`** (`hermes-agent`): real port names come from
  component `patch-svc.yaml` files, not the base svc — grep
  `apps/<app>/components/*/patch-svc.yaml` for the actual port names.
- **Base-netpol apps** (dex/immich/metatube had no overlay netpol patch, but
  the BASE netpol admits `tailscale-system` inline): create
  `patch-netpol.yaml` in the overlay (JSON6902 add of the envoy-gateway rule)
  and wire a `patches:` entry targeting the app's NetworkPolicy. Base
  default-deny + no envoy rule = silently blocked gateway→pod traffic.

## Port-scope rule

Default: migrate only the web UI (http port); raw protocol ports stay
Service-exposed. BUT when the app already had its raw ports on a tailscale LB
Service (forgejo `git`, qbittorrent tracker, copyparty `ftp`), the user's
standing directive is to MERGE those into the app's Gateway (TCPRoute/UDPRoute
+ listeners, delete the LB Service — see the merge section below) rather than
keep two tailscale devices. Ask only when the port count is extreme (copyparty
103 — user approved full merge anyway). syncthing 22000 is the original
precedent — and remember the ai-gateway listener-hook constraint: see the
envoy-ai-gateway skill before adding TCP/UDP listeners to any Gateway while
the extensionManager hook is enabled.

## Batch-migration workflow (proven)

1. Pilot ONE app end-to-end (jellyfin), `kustomize build` the app overlay AND
   `clusters/<cluster>/overlays/tailnet` before touching anything else.
2. Follow the repo route-placement convention FROM THE START: HTTPRoute in
   `base/` (rules + backendRefs only), overlay `patch-httproute.yaml` supplies
   hostnames + parentRefs (syncthing model). A mid-campaign review round
   forced restructuring 27 PRs; baking it into the pilot avoids that.
   Same for tags: audit each app's OLD tailscale tags up front and stamp them
   into the EnvoyProxy in the first pass — a uniform tag pass (tag:syncthing
   everywhere) got rejected in review and cost a full rework campaign.
2. Batch the rest via parallel subagents, partitioning apps into disjoint
   groups — OR do the mechanical template substitution in-shell
   (`sed "s/jellyfin/$app/g"` over the four template files + scripted
   kustomization/cert edits): subagents burn their 600s budget on per-file
   tool calls and can achieve nothing (one of three did zero apps). Either
   way, verify file state on disk afterward — never trust agent self-reports.
   `configs/cert-manager/overlays/nishir/cert.yaml` is a shared file — if
   agents are used, instruct ONE atomic read-append-write of all its cert
   blocks at the END of each agent's run, re-reading on conflict (this worked:
   zero dupes across 3 agents). Give any special-case app (multi-hostname,
   funnel, non-template ports) to the parent, not a subagent.
   If the user then wants per-app PRs, do NOT hand-rebuild commits; split the
   mega commit per `references/pr-campaign-split.md`.
3. Verify: no `ingressClassName: tailscale` remains under `apps/`; cert.yaml
   has exactly one block per app (dedupe check for race artifacts); every
   overlay builds; full cluster render passes.
4. Post-merge: Flux reconciles → certs issue (LE DNS-01) → Gateways Programmed →
   external-dns publishes `X.i.shikanime.studio → <tailnet IP>` in Cloudflare.
   Verify with `dig +short X.i.shikanime.studio @1.1.1.1` and a TLS'd curl.

## Gotchas

- Old Ingress `tls.hosts` entries are NOT hostnames to preserve — the old
  pattern used bare short names (`jellyfin`); the new hostname is always
  `X.i.shikanime.studio`.
- kustomization resources referencing a file that only exists in `base/` (e.g.
  a tailnet-overlay `netpol.yaml` line when netpol lives in base) fails the
  build with `evalsymlink failure` — check where the file actually lives
  before listing it.
- The Certificate block is centralized on purpose: one file, one Flux
  Kustomization (`config-cert-manager`), one place to audit public SANs.
- **Subagent batch pitfalls (2026-08-30, all three observed):** one of three
  batch agents timed out at 600s having done NOTHING (check actual file state
  on disk before re-dispatching — its whole list may be untouched); one left
  its app's old `ingress.yaml` on disk while rewiring the kustomization
  (orphaned file, no build error — the final sweep
  `grep -rl "ingressClassName: tailscale" apps --include="*.yaml"` catches
  it); cert.yaml race handling worked as instructed (atomic append-at-end,
  zero dupes across 3 agents). Verify with file-state checks, never trust
  agent self-reports alone. Cert dedupe:
  `grep "  name: .*-i-shikanime-studio-tls$" configs/cert-manager/overlays/nishir/cert.yaml | sort | uniq -d`
  (empty = clean).

## Tailscale tags: per-purpose, never one uniform tag (USER CORRECTION)

Do NOT stamp every app's EnvoyProxy with a uniform `tag:syncthing` (the
reference impl's tag). Preserve each app's per-purpose tags from its old
tailscale Service/Ingress — Tailscale ACLs key on tags, so a uniform tag
silently changes device reachability:

| Old Service/Ingress tag | Apps |
|---|---|
| `tag:web` (Ingress default) | jellyfin, bazarr, dex, gitea-mirror, hermes-agent, honcho, immich, metatube, prowlarr, seerr, synapse-proxy, vaultwarden, mautrix/*, servarr/* |
| `tag:web,tag:git` | forgejo (web Ingress + `git` Service) |
| `tag:web,tag:bittorrent` | qbittorrent (web Ingress + tracker Service) |
| `tag:web,tag:ftp` | copyparty (web Ingress + `ftp` Service) |
| `tag:syncthing` | syncthing only |

Audit an app's old tags BEFORE choosing: `jj file show -r main@origin
apps/<app>/overlays/nishir-tailnet/ingress.yaml` + the app's `patch-svc.yaml`
/ component `svc.yaml` (grep `tailscale.com/tags`). Multi-tag format:
`tailscale.com/tags: "tag:web,tag:git"` (one annotation, comma-separated).

## Merging an old tailscale Service + Ingress into ONE Gateway (user-directed pattern)

Apps that had BOTH a tailscale-Ingress web UI AND a separate tailscale LB
Service for raw ports (copyparty ftp, forgejo git/ssh, qbittorrent tracker)
merge everything onto the one per-app Gateway device — the syncthing model:

1. Add TCP/UDP listeners to `gateway.yaml` (one per port). **Listener names
   must be MEANINGFUL — the old Service's port names, NOT `tcp-<port>`
   (USER CORRECTION 2026-08-30):** copyparty 21=`ftp-control`, 990=`ftps`,
   22=`sftp`, 12000–12099=`ftp-data-<port>`; forgejo 22=`ssh`; qbittorrent
   6881=`bittorrent` (TCP) + `bittorrent-udp` (UDP). Generic `tcp-<port>` names
   were rejected in review. Renaming a listener REQUIRES renaming every route's
   `parentRefs[].sectionName` to match — render-verify both sides
   (kustomize build does NOT validate sectionName↔listener pairing; grep the
   rendered output for the section names).
2. One TCPRoute or UDPRoute per backend Service PORT (a TCPRoute has exactly
   one `backendRefs[].port`), `parentRefs` → Gateway + matching
   `sectionName`. Bulk example: copyparty = 103 listeners + 103 TCPRoutes
   in one generated `tcproutes.yaml`.
3. Delete the old tailscale LB Service (`patch-svc.yaml`) and drop it from
   `kustomization.yaml`. The Gateway's EnvoyProxy LB is now the only
   tailscale device.
4. The EnvoyProxy `tailscale.com/tags` must carry the union (e.g. copyparty
   `tag:web,tag:ftp`) so ACL rules for BOTH purposes still match.
5. Netpol must allow `envoy-gateway-system` on ALL migrated ports (copyparty's
   patch-netpol lists every ftp port).
6. Scale warning: each listener = a bootstrap entry and an open port on the
   tailnet device. 82–103 ports renders fine but bloats the Envoy config and
   widens exposure — confirm the user really wants full merge vs leaving the
   raw-port Service as-is. (User chose full merge for copyparty.)

## jj PR-campaign session traps (2026-08-30, repeated across two sessions)

- **`jj new main` (or any `jj new <target>`) with a dirty working copy is the
  #1 self-inflicted wound**: an edit made to files, followed by `jj new <x>`,
  either silently discards the diff or auto-commits it into an anonymous commit
  on top of the OLD parent — then later `jj new` calls abandon it. The
  deterministic loop that worked repeatedly:
  `jj new <remote-branch>@origin` → edit files → `jj describe -m "<title>"` →
  `jj bookmark set <branch> -r @ --allow-backwards` → `jj git push --bookmark
  <branch>` → verify via `git fetch && git show origin/<branch>:<path>`.
- **`jj bookmark set -r @-` after `jj new` points the bookmark at the REMOTE
  commit, not your edit** (`@-` is the parent; your edit lives in `@`).
- **Verify on origin, never on local refs**: divergent bookmarks, stale
  remote-tracking refs, and abandoned-sibling chaos make `jj file show -r
  <branch>` unreliable mid-campaign. Ground truth is
  `git fetch && git show origin/<branch>:<path>` and
  `git cat-file -e origin/<branch>:<path>` (exit 128 = absent).
- **`gh pr edit --base` can fail with a generic GraphQL error**; the REST
  equivalent works: `gh api repos/<org>/<repo>/pulls/<N> -X PATCH -f base=main`.
- **Verify remote actual state after push** (`git ls-remote origin <branch>`);
  a `push` rc=0 with no "bookmark:" output line may mean nothing moved.
- **Divergent bookmarks**: resolve with `jj log -r <change-id>` listing
  `/<0>` `/<1>` versions, `jj bookmark set ... -r <good-version>
  --allow-backwards`, then `jj abandon <stale-version>`.

## Post-migration app-config sweep + live edits that stick

Manifests going green is not "done" — app configs on PVCs keep serving old
hostnames/flags. Sweep running pods before declaring done
(`kubectl exec <pod> -- grep -rl taila659a /config /data 2>/dev/null | grep
-vE 'logs|\.db|\.sqlite'`) and patch what you find live AND codify in repo:

| App | File | What breaks |
|---|---|---|
| jellyfin | `config/network.xml` | `PublishedServerUriBySubnet` (client redirect target), `EnableHttps/RequireHttps`, `PublicHttp/HttpsPort` |
| qbittorrent | `qBittorrent.conf` | `WebUI\ServerDomains` + `HostHeaderValidation=true` reject unknown Host headers — ADD the new domain (keep old during transition), restart pod |
| vaultwarden | `config.json` | `domain` + `sso_callback_path`; also the `DOMAIN` env (encrypted) — disk file must be patched too, env only wins at runtime |
| copyparty | exports/config | historical hostnames (low impact) |

Live-edit techniques that worked:
- Edit config INSIDE the running pod when the container has a shell
  (`kubectl exec <pod> -- sed -i ...`) — fastest path; restart the pod after
  so the app re-reads.
- RWOP PVC (ReadWriteOncePod) blocks helper pods while the app runs:
  `kubectl scale sts <app> --replicas=0`, wait for pod delete, run a busybox
  helper with the PVC mounted, `scale --replicas=1`. **Suspend the Flux
  kustomization first** (`flux suspend kustomization apps-<app>`) — Flux's
  10-min interval re-reconciles and undoes manual scale-downs mid-surgery.
  `flux resume` + reconcile after.
- `subPath` volume mounts (e.g. jellyfin's `homeserver.yaml`) do NOT update
  when the backing Secret changes — delete the pod after the secret updates
  or the app keeps reading the old content.
- Some apps hard-refuse config migrations (synapse: server_name change on a
  DB with existing users → `Exception: Found users in database not native
  to <new>`). Check for this BEFORE planning a rename; if refused, keep the
  identity and only move routing (well-known/listener) — see PRs #2028/#2033.

## Gateway listener patterns per app (post-migration refinements)

Most apps: single `https:443` Terminate listener, route → plaintext backend.
Exceptions, all deliberate:
- **Dual-listener (jellyfin)**: `http:80` (HTTP) + `https:443` (Terminate);
  two HTTPRoutes (`jellyfin`→8096 parent http, `jellyfin-https`→8920 parent
  https via BackendTLSPolicy). Jellyfin keeps its own TLS + RequireHttps.
  Rules apply to all attached listeners — never split backends across rules
  of one route.
- **Raw-protocol listeners**: forgejo `ssh:22`, syncthing `22000`, copyparty
  ftp range — one TCPRoute/UDPRoute per backend Service port.
- New listener port ⇒ new tailscale ACL grant (see tailnet-acl skill) and a
  ts proxy pod delete to reprogram the proxy.
