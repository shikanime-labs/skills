# Repo-wide structural audit — dangling files, naming, consistency (2026-09-02)

Method validated on the full manifests repo (244 kustomizations, 464 dirs)
for "review every app structure consistency, naming and dangling files".
Rebase the working branch onto latest `origin/main` FIRST (directives issued
mid-review apply to current main, not session-start HEAD).

## Dangling-file scan (no pyyaml needed — regex over kustomization fields)

For every kustomization.yaml, collect referenced basenames from:
`resources:`/`components:` list items, `path:` entries, and
`secretGenerator`/`configMapGenerator` `envs:`/`files:` values (strip
`name=file` to `file`, strip dirs). Then list every other file in the dir
and flag unreferenced ones.

False positives to re-check by hand before deleting (both bit this session):

- `path:` entries written AFTER the `target:` block in a `patches:` entry
  (reversed key order — llama-cpp) — a naive regex misses them.
- Secret files referenced via `envs: [<dir>/.enc.env]` or
  `files: [key=<dir>/<file>]` (immich `.enc.env`).
Final arbiter: `git grep <basename>` across the repo; only files with zero
matches anywhere are truly dangling.

## Classified findings (2026-09-02, @ d75a7aaa4)

1. **27 orphaned tailnet `patch-netpol.yaml`** — SMP template adding
   envoy-gateway-system + vmagent ingress; unwired since the netpol
   normalization PRs. Correct wiring patterns that DO exist in-repo:
   syncthing/llama-cpp ship a full `netpol.yaml` in overlay `resources:`;
   lldap wires `patches: [{path: patch-netpol.yaml, target: ...}]`.
   Live-cluster note: envoy data-plane pods (label
   `app.kubernetes.io/name=envoy`, ns `envoy-gateway-system`) reached app
   pods even though the app netpol had no matching ingress entry — verified
   with a curl probe pod. Netpol enforcement is partial; treat these as
   latent, not active, breakage.
2. **Hostname-split leftovers** — `gitea-mirror` + `jellyfin` tailnet
   `patch-sts.yaml` carrying `*.i.shikanime.studio` env config; unreferenced;
   confirmed absent from live STS env. Deleting enforces the split rule.
3. **Superseded singletons** — authelia tailnet `patch-httproute.yaml`
   (pre-inline leftover), `honcho/base/hpa.yaml` (HPA abandoned for VPA),
   `honcho/nishir/patch-deploy.yaml` (config.toml-era ConfigMap gone).
4. **Superseded route files** — `infrastructure/longhorn/base/httproute.yaml`
   - `overlays/nishir-tailnet/httproute.yaml`: rules moved to nishir
   `gateway.yaml`; both builds render clean without them (verified before
   deletion).

## Consistency checks worth running

- **Append-directive violation sweep** (post-#2079): grep tailnet
  kustomizations for `op: replace` IMMEDIATELY followed by
  `path: /spec/hostnames$` (member form replaces the whole list).
  As of 2026-09-02 the sole violator is authelia tailnet (not deployed).
- **Resource list ordering** per AGENTS.md ("listed sorted") is violated in
  ~50 dirs (`netpol.yaml` before `httproute.yaml`) — cosmetic, low priority.
- **Rule-reference check for probe/patch port names**: render overlay, diff
  probe `port:` names against declared `ports[].name` (see
  `references/probe-port-name-drop.md`).
- **Secret-file duplication** across nishir/nishir-tailnet: `cmp -s` each
  `<overlay>/<sub>/*.enc.*` against its nishir sibling; identical copies are
  drift candidates (none found this pass).

## Live-vs-manifest cross-checks that caught real bugs

- `kubectl get sts <name> -o jsonpath='{...containers[0].env[*].name}'`
  vs manifest render — proved patch-sts leftovers were never applied.
- `kubectl get netpol <name> -o json | jq -c '.spec'` vs render — surfaced
  the netpol enforcement gap.
- Reachability probes (curl from a pod with specific labels, PodSecurity
  `restricted` requires runAsNonRoot + dropped caps + seccomp in the pod
  spec) — used to prove/disprove netpol allow paths. `kubectl run` flags
  can't express the full securityContext; apply a JSON pod manifest instead.
