---
name: kustomize-overlay-authoring
description:
  "Use when editing kustomization.yaml overlays in manifests."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - kustomize
      - kubernetes
      - gitops
      - manifests
---

# Kustomize Overlay Authoring

Authoring/debugging `kustomization.yaml` overlays in the `manifests` GitOps repo (FluxCD + Kustomize, kustomize v5.8.x in `nix develop`).

## When to Use

- Editing any `apps/`, `infrastructure/`, `configs/`, or `clusters/` kustomization.
- Removing `disableNameSuffixHash` from a secretGenerator; a secret/ConfigMap reference renders with the plain name instead of the hash-suffixed generated name.
- Adding a new app (base + overlays + ks.yaml + cert wiring): worked example + template-app selection in `references/new-app-recipe.md`; Maintainerr: `references/maintainerr-integration.md`. Stateful apps use STS volumeClaimTemplates (NOT pinned PVCs) with a 512Mi floor — user directive, in the recipe.

## CI treefmt gate: run `nix fmt` after scripted YAML generation

CI runs devenv treefmt on every PR; unformatted YAML fails CI even when `kustomize build` exits 0. Local (aarch64-darwin): plain `nix fmt`, no devenv invocation (sidesteps "cannot determine current directory" assertion):

```bash
nix fmt   # formats the whole repo via the flake's treefmt; reports "formatted N files"
```

Mismatches that trip it:

- **Python `yaml.safe_dump` ≠ treefmt style**: safe_dump emits list items at parent-key indent (`rules:\n- backendRefs:`); formatter wants them indented. Both valid YAML — kustomize renders both; CI still fails on safe_dump style. After generating YAML with Python ALWAYS `nix fmt` and squash into the same commit.
- **String-append without trailing newline glues lines** (`...kind: NetworkPolicypatches:`) → `yaml: mapping values are not allowed in this context`. Always `content.rstrip() + '\n' + block + '\n'`.
- **String-appending `---` to a multi-doc file glues it to the previous line** (`sectionName: https---apiVersion:`): the appended doc is silently ABSORBED — build exits 0 but the second patch doc never applies (route loses hostname/parentRefs). Always append `'\n---\n' + doc`; after scripted multi-doc assembly verify each doc parses standalone with `yaml.safe_load_all` (count docs, check names).
- **markdownlint MD057**: when a PR DELETES a file (e.g. old `ingress.yaml`), grep root and per-app `README.md` for links to it before pushing — a dead relative link fails CI like an unformatted file.

## Pattern: replace disableNameSuffixHash with nameReference

`disableNameSuffixHash: true` defeats content-addressing; the repo-standard alternative keeps the hash AND rewrites references at render time:

1. Drop `options.disableNameSuffixHash` from the secretGenerator block.
2. Add `configurations: [namereference.yaml]` to the overlay kustomization.
3. `namereference.yaml` (mirrors `apps/jellyfin/overlays/nishir/namereference.yaml`):

```yaml
nameReference:
  - kind: Secret
    fieldSpecs:
      - kind: VirtualMachine        # target kind that references the Secret
        path: spec/template/spec/volumes/secret/secretName
```

4. Base manifests keep the plain name (e.g. `secretName: catbox-sops-key` in `apps/catbox/base/vm.yaml`) — never hardcode a hash in base. `nameReference` covers all fieldSpecs under the target kind, including array paths (list element paths like `volumes/secret/secretName` work fine).

`nameReference` covers all fieldSpecs under the target kind, including array paths (list element paths like `volumes/secret/secretName` work fine).

### nameReference for CRD secretRef fields (Envoy AI Gateway)

Built-in secret consumers (Pod/Deployment/Secret volume refs) get the hash rewrite automatically; **CRD fields do NOT**. A `MCPRoute` / `BackendSecurityPolicy` / `AIGatewayRoute` secret reference via a CRD-specific path MUST be declared in `namereference.yaml` with the target **`group`**, or the rendered `secretRef.name` stays unhashed and the workload fails to mount the secret:

```yaml
# apps/<app>/overlays/<cluster>/namereference.yaml

nameReference:
  - kind: Secret
    version: v1
    fieldSpecs:
      # BackendSecurityPolicy: aigateway.envoyproxy.io/v1beta1
      - kind: BackendSecurityPolicy
        group: aigateway.envoyproxy.io
        path: spec/apiKey/secretRef/name
      # MCPRoute: aigateway.envoyproxy.io/v1beta1 (array backendRefs)
      - kind: MCPRoute
        group: aigateway.envoyproxy.io
        path: spec/backendRefs/securityPolicy/apiKey/secretRef/name
      # SecurityPolicy OIDC clientSecret: gateway.envoyproxy.io/v1alpha1
      - kind: SecurityPolicy
        group: gateway.envoyproxy.io
        path: spec/oidc/clientSecret/name
```

Wire via `configurations:` (NOT `transformers:`):

```yaml
# apps/<app>/overlays/<cluster>/kustomization.yaml

secretGenerator:
  - name: inference-z-ai
    namespace: shikanime
    envs:
      - inference-z-ai/.enc.env      # hash on by DEFAULT; do NOT set disableNameSuffixHash
configurations:
  - namereference.yaml
```

Base/CRD manifests keep the **plain** name (`secretRef: { name: inference-z-ai }`); never hardcode a hash suffix in base (duplicate-generator collision: see below). Full recipe + verification: `references/envoy-ai-gateway-secretref.md`.

### Gotcha: cluster component dir must contain a `kustomization.yaml`

A directory referenced as a kustomize **component** (`components: [../../components/<name>]`) MUST contain a `kustomization.yaml` with `kind: Component`. Only a Flux `ks.yaml` there → build fails:

```text
Error: accumulating components: accumulateDirectory:
"couldn't make target for path '.../components/<name>': unable to find one of
'kustomization.yaml', 'kustomization.yml' or 'Kustomization' in directory
'.../components/<name>'"
```

Passes local `kustomize build apps/...` but breaks CI's `kustomize build clusters/<cluster>/overlays/tailnet` — app PR merges green, merged-main render fails. Fix:

```yaml
# clusters/<cluster>/components/<name>/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1alpha1
kind: Component
resources:
  - ks.yaml
```

Every sibling component dir (`trust-manager`, `tailscale`, ...) carries this file; a component with only `ks.yaml` is the outlier. Verify before a PR adding a component reference.

## Gotcha: `patchesJson6902` with `-` append token SEGFAULTS in kustomize 5.8.1

`path: /spec/ingress/-` inside a `patchesJson6902:` file crashes the builder:

```
panic: runtime error: invalid memory address or nil pointer dereference
sigs.k8s.io/kustomize/api/internal/builtins.(*PatchJson6902TransformerPlugin).Config
```

Fix — inline `patches:` with `target` + `patch: |-` (handles `-` correctly):

```yaml
# apps/<app>/overlays/<cluster>-tailnet/kustomization.yaml

patches:
  - target:
      kind: NetworkPolicy
      name: <np>
      namespace: <ns>
    patch: |-
      - op: add
        path: /spec/ingress/-
        value:
          from:
            - namespaceSelector:
                matchLabels:
                  kubernetes.io/metadata.name: tailscale-system
          ports:
            - port: http
      - op: add
        path: /spec/ingress/-
        value:
          from:
            - namespaceSelector:
                matchLabels:
                  kubernetes.io/metadata.name: monitoring-system
              podSelector:
                matchLabels:
                  app.kubernetes.io/name: vmagent
          ports:
            - port: metrics
```

- `patchesJson6902` is deprecated AND segfaults — do not use.
- A separate JSON6902 list FILE does work as `patches: [{path: ..., target: ...}]` WITH `target:` (repo pattern: `apps/lldap/overlays/nishir-tailnet/patch-netpol.yaml`, `apps/lldap/components/tls/patch-netpol.yaml`). "must specify a target" fires only when `path:` is given WITHOUT `target:`. **Convention (2026-09-02, PR #2081, user directive): JSON6902 goes INLINE in `patches:` entries; only strategic-merge patches stay as separate files.**
- LSP may falsely flag inline `patch` with "Missing property target" — the diagnostic is wrong; `target` IS present. Ignore.

### Gotcha: JSON6902 `target:` misses match SILENTLY — wrong group/version/name builds green

A `target:` block matching no rendered resource is a SILENT no-op: build exits 0, CI green, field never appears. Outage 2026-09-03 (issue #2109): patched `AIGatewayRoute` as `name: inference`, `group: gateway.networking.k8s.io`, `version: v1alpha2` — actual object `default` / `aigateway.envoyproxy.io` / `v1beta1`; parentRef never attached, every chat request 500'd (`upstream_cluster: null`), nothing errored.

- Read the LIVE object (`kubectl get <kind> <name> -o yaml`) or base manifest to confirm the identity triple — never infer group/version from a sibling kind. Object name may differ from app name (route is `default`, not `llama-cpp`).
- After rendering, grep for the patched field's VALUE (e.g. `parentRefs` under the route doc), not just the target name — a miss shows as absence.
- Read the LIVE object (`kubectl get <kind> <name> -o yaml`) or base manifest to confirm the identity triple — never infer group/version from a sibling kind. Object name may differ from app name (route is `default`, not `llama-cpp`).
- After rendering, grep for the patched field's VALUE (e.g. `parentRefs` under the route doc), not just the target name — a miss shows as absence.

### Gotcha: JSON6902 file MUST be a single ops-list doc; value must be scalar for append

Verified on kustomize 5.8.1 (PRs #2079–#2081):

- **Multidoc JSON6902 patch files do not exist.** A file of `{patch, target}` docs fails `unable to parse SM or JSON patch` in every entry form. One ops-list per FILE matched by `target:` — the whole contract.
- **Multidoc ops-list + one `patches:` entry per route RENDERS but is order-dependent**: swapping order made every target consume doc 1 and drop doc 2 (A/B render). Never ship that shape.
- **`add` on `/spec/hostnames/-` appends the VALUE as ONE element** — value must be the scalar hostname. `value: [host]` renders `- - host` (build exits 0; hostname garbage). Correct:

  ```yaml
  - op: add
    path: /spec/hostnames/-
    value: bazarr.taila659a.ts.net
  ```

  Two hostnames = two `add /-/` ops, never one list value.
- **RFC 6902: `add` on an EXISTING object member == replace.** Use append (`add /spec/hostnames/-`) for routes that have a `hostnames:` member; the member-creating `add /spec/hostnames` with a list value for routes that lack one (slack pair) — create-safe AND replace-equivalent.
- **Batch-render check:** a nested-list append shows as a hostname line matching `^\s*- - `. Grep rendered HTTPRoutes for it after route-patch edits.

  ```yaml
  - op: add
    path: /spec/hostnames/-
    value: bazarr.taila659a.ts.net
  ```

  Two hostnames = two `add /-/` ops, never one list value.
- **RFC 6902: `add` on an EXISTING object member == replace.** Use append (`add /spec/hostnames/-`) for routes that have a `hostnames:` member; the member-creating `add /spec/hostnames` with a list value for routes that lack one (slack pair) — create-safe AND replace-equivalent.
- **Batch-render check:** a nested-list append shows as a hostname line matching `^\s*- - `. Grep rendered HTTPRoutes for it after route-patch edits.

This is how `apps/llama-cpp/base/netpol.yaml` (Envoy-only base) gets tailscale + vmagent ingress allows ONLY in the `nishir-tailnet` overlay.

**nameReference hash rewrite vs secretGenerator `namespace:` placement** — silent no-op class (rendered Secret is `<name>-<hash>` but workload says `<name>`):

| namespace placement               | rewrite works |
| --------------------------------- | ------------- |
| intermediate layer only           | NO (silent)   |
| top overlay only                  | yes           |
| both layers (jellyfin repo style) | yes           |

Fix: set `namespace:` at the top overlay too. Bisect silent no-ops with a minimal repro OUTSIDE the repo (`/tmp/nrtest/...`): flat build → nested build → toggle suspect field.

### Gotcha: top-level `namespace:` overrides inline namespaces on EVERY resource (incl. a patch)

Kustomization `namespace:` is a **transform that runs after patches** — beats inline `metadata.namespace` AND any `patches:` entry (JSON6902 `op: replace /metadata/namespace` or strategic-merge `metadata:` block). Empirical (2026-09-01): `Ingress` with inline `namespace: envoy-gateway-system` under `namespace: shikanime` always rendered `shikanime`. Symptom: resource renders in the wrong namespace, build exits 0.

1. **Put the resource in an overlay with no top-level `namespace:`** — e.g. the flux config overlay (no `namespace:` field) renders into `flux-system`.
2. **Co-locate resource with backend by DROPPING the transform**: remove top-level `namespace:`; move it onto each generator (`configMapGenerator`/`secretGenerator` take per-entry `namespace:`). `../nishir` base overlay already applies `shikanime` to base resources. After: verify every resource's namespace (`kustomize build | grep -E 'kind:|namespace:'` pairing) — removal can silently drop a namespace from a base resource that depended on it.

Verify override behavior cheaply with a ~6-line repro in `/tmp/kustest` — don't reason about transform ordering in your head.

### Tailscale Funnel `Ingress` — serve the Envoy LB endpoint, not the app ClusterIP

Funnel uses a **Tailscale `Ingress`** (`networking.k8s.io/v1`, `ingressClassName: tailscale`, annotations `tailscale.com/funnel: "true"` + `tailscale.com/tags: tag:web`), NOT a `tailscale.com/funnel` annotation on an Envoy LoadBalancer Service. Backend must be **co-namespaced** with its Service:

- Envoy LB Service (`envoyService` → `LoadBalancer`, `loadBalancerClass: tailscale`) lands in **`envoy-gateway-system`** (HelmRelease `targetNamespace`), regardless of `EnvoyProxy` CR namespace — the Funnel Ingress must render there too.
- **Serve the Envoy LB Service, not the app ClusterIP** (user rule 2026-09-01: "ingress should serve envoy proxy endpoint"). Backend = `flux-operator-receivers:80` / `synapse-proxy:80` in `envoy-gateway-system`; pointing at app ClusterIPs (`webhook-receiver:80`, `synapse-proxy:8008`) bypasses Envoy — reverted by the user.
- Envoy LB ports: 80 (http) / 443 (https) — use 80 for the Funnel backend.
- Live check: `kubectl get svc -A -o custom-columns='NS:.metadata.namespace,NAME:.metadata.name,TYPE:.spec.type,LB:.metadata.annotations.tailscale\.com/hostname'` — NS column is authoritative.

### Gotcha: kustomize strategic merge REPLACES list entries — carry the full spec

SMP on a LIST field (e.g. `volumeClaimTemplates: [{name: data, spec: {storageClassName: ...}}]`) REPLACES the entry — a patch with only `storageClassName` drops `resources.requests.storage` and `accessModes`; rendered STS fails admission. Patch must carry the FULL entry spec (storage + accessModes + volumeMode + storageClassName), mirroring `apps/lldap/overlays/nishir/patch-pvc.yaml`. Image digest pins must be manifest-list (index) digests on mixed-arch clusters (amd64-only → `exec format error` on arm64 nodes).

Cluster policy (nishir) injects `readOnlyRootFilesystem: true`, `capabilities.drop: [ALL]`, seccomp RuntimeDefault into every container:

- chown/su-exec entrypoints fail — run as uid/gid 1000 (non-root exec branch). Apps writing next to their config at startup (authelia resolved config, healthcheck-env shims) fail unless that path is a writable volume and the shim disabled. Kubelet enforces read-only on Secret mounts regardless of `readOnly:` — mount via `subPath` INTO a writable volume dir (config-sync pattern).
- Readiness probe dialing a scheme the container doesn't serve yet never turns Ready; a Flux health check on that STS then blocks applying the FIXED spec (deadlock). Break with `kubectl scale sts <n> --replicas=0` → pod gone → `--replicas=1`. Recipe: `references/probe-port-name-drop.md`; authelia: `references/authelia-dex-migration.md`.

### Gotcha: probe port NAME dropped by multi-component `ports` merge

A component patch adding BOTH `ports: [{name: X, containerPort: N}]` and probes `httpGet: { port: X }` can render probes intact but `name: X` missing when sibling components also add `ports:` lists — kustomize's list merge drops it. Symptom: pod `1/N Ready`, kubelet repeats `Startup probe errored ... strconv.Atoi: parsing "X": invalid syntax`. Diagnose by diffing rendered probe `port:` names against declared `ports` names. Fix: probe an always-present port name (from a component ALWAYS in the overlay) or the numeric port; drop the orphan `ports` entry; remap NetworkPolicy `ports: [{port: X}]` referencing the dead name (silently matched nothing). Full recipe: `references/probe-port-name-drop.md`.

### Gotcha: component patches run AFTER the included base's `images:` transformer

A **component** (`kind: Component`) accumulates at the parent level: its `patches:` apply AFTER the included base's transformers. An `images:` entry in `base/kustomization.yaml` is a SILENT NO-OP for an image a component patch introduces (build 0, CI green, bare name). Outage 2026-09-03 (PR #2128): jellyfin LDAP initContainer bare `image: rclone` in `apps/jellyfin/components/ldap/patch-sts.yaml` pulled `docker.io/library/rclone:latest` (denied) → `Init:ImagePullBackOff`.

Fix: `images:` goes in the overlay kustomization that INCLUDES the component (`apps/jellyfin/overlays/nishir/ kustomization.yaml`). Rule: an image pin lives in the kustomization whose build tree CONTAINS the file introducing `image:`. Reproduce in ~15 lines in `/tmp/ktest/` — never reason about transformer ordering in your head. Verify: `kustomize build <overlay-with-component> | grep -c 'image: <name>$'` must be 0 (bare short name = untransformed tell).

### Gotcha: `target:` is forbidden on a multi-doc patch file

A `patches:` entry pointing at a multi-doc patch file must NOT set `target:` — kustomize 5.8.1 errors `Multiple Strategic-Merge Patches in one 'patches' entry is not allowed to set 'patches.target'`. Without `target:`, each doc matches by `metadata.name`. Repo shapes: `apps/jellyfin/overlays/nishir-tailnet/patch-httproute.yaml` (jellyfin + jellyfin-redirect), `configs/flux-operator/overlays/nishir/patch-httproute.yaml` (flux-operator-receivers + -redirect), wired as bare `patches: [{path: patch-httproute.yaml}]`. Single-doc patch files keep `target:` (e.g. `patch-sts.yaml`).

### Gotcha: CRD field that local build accepts but Flux dry-run rejects (SecurityPolicy `clientSecret.key`)

Kustomize is schema-agnostic. A CRD field the installed CRD doesn't declare passes build + CI, then fails at Flux reconcile: `dry-run failed: ... field not declared in schema` — nothing from the PR applies (2026-09-03: EG v1.9.0 SecurityPolicy `oidc.clientSecret` is a SecretObjectRef with ONLY group/kind/name/namespace; upstream `key:` invalid). Read the LIVE CRD (`kubectl get crd <kind>... -o json | jq '.spec.versions[0].schema...'`) — not upstream docs — and WATCH the Flux Kustomization after landing (dry-run failures surface there, not CI). EG reads the OIDC client secret from the Secret's `client-secret` key by convention — no key field needed.

### Gotcha: multi-doc patch files silently eat indented list items

Programmatic YAML (Python concat, heredoc, `write_file`, `patch`) with a list in a nested block: items at parent-key indent get **silently absorbed**:

```yaml
  hostnames:
    - bazarr.i.shikanime.studio
- bazarr.taila659a.ts.net    ← UNINDENTED, absorbed into previous line
    - bazarr
```

Glued result is not a valid hostname; kustomize drops it. Fix — build each hostname TYPE as a SEPARATE indented string, then join. Verified on 33 nishir-tailnet patch-httproute.yaml files (PR #2065). Same class as `sectionName: https---apiVersion:`. **Rule: never concatenate multi-line YAML scalars by string append; build each block as its own string with its own indentation, then join with newlines.**

```python
studio_lines = "\n".join(f"    - {h}.i.shikanime.studio" for h in base_hostnames)
tailscale_lines = "\n".join(f"    - {h}.taila659a.ts.net" for h in base_hostnames)
bare_lines = "\n".join(f"    - {h}" for h in base_hostnames)
all_hosts = studio_lines + "\n" + tailscale_lines + "\n" + bare_lines
```

Verified on 33 nishir-tailnet patch-httproute.yaml files (PR #2065). Same class as `sectionName: https---apiVersion:`. **Rule: never concatenate multi-line YAML scalars by string append; build each block as its own string with its own indentation, then join with newlines.**

### Labels: five-key set, version synced to the base image tag

Every tailnet overlay carries the same five-key label set; plain `nishir` overlays are label-free (labels introduced at the tailnet layer):

```yaml
# apps/<app>/overlays/nishir-tailnet/kustomization.yaml

labels:
  - includeTemplates: true
    pairs:
      app.kubernetes.io/component: <role>      # file-server, backup, communication, ...
      app.kubernetes.io/instance: <app>
      app.kubernetes.io/name: <app>
      app.kubernetes.io/part-of: <group>       # nishir-media/office/automata/platform/...
      app.kubernetes.io/version: <image-tag>   # must match base newTag
```

- **Version drift is a recurring rot class** (16/36 overlays stale, 2026-09-02 audit, PR #2089): `newTag` bumps in base while `version` lives in tailnet labels. Bump BOTH in the same PR. Non-version tags keep a sensible label: branch tags (`server-rocm`) keep the release number; commit-SHA tags (`eb547ca`) keep `0.0.0`. Don't "sync" those.
- **Fleet audit:** `kustomize build` every `apps/**/overlays/nishir-tailnet` (RECURSIVE glob — `apps/*/overlays` misses `apps/<group>/<app>/overlays/`); grep render for `app.kubernetes.io/part-of` (0 labeled resources = offender); cross-check `version:` vs base `newTag:` (strip `v` / `@sha256:` first).

### Gotcha: empty key left after scripted block removal — general case (EnvoyProxy `pod:` null)

PR #2105 deleted `nodeAffinity` from 31 `envoyproxy.yaml` files, leaving parent `pod:` childless. YAML renders `pod:` as **null**; build exits 0, but the CRD rejects null for `spec.provider.kubernetes.envoyDeployment.pod` — Flux dry-run fails on EVERY `apps-*` Kustomization (`Invalid value: "null"`), nothing reconciles. Local build green ≠ Flux will apply (PR #2111 cleanup).

- Grep for orphaned parent keys after scripted removal: `grep -rn '^ *pod:$' apps --include=envoyproxy.yaml` (adapt key). Removal regexes must consume the parent key WITH its block. Delete the key in the same edit if the block was its only content (lookahead: `re.sub(r'\n( +)pod:\n(?=\1container:)', '\n', t)`).
- Verify the RENDER for empty keys: `kustomize build <overlay> | grep -E '^[ ]*[a-zA-Z]+:$'` — empty key line directly above a sibling key is the bug. Watch Flux Kustomizations after fleet-wide scripted edits.

### Gotcha: empty `patches:` key left after removing a patch entry

Delete the now-empty `patches:` KEY too — bare `patches:` renders as null and some kustomize versions choke. Symptom after scripted sed: `patches:` dangling directly above the next top-level key. Grep `-A1 '^patches:'` before rendering.

### Splitting flux-style config out of clusters/<cluster>/base into configs/<area>/

Moving `Alert`/`Provider`/`Receiver` (any secretRef-carrying resources) into `configs/<area>/{base,overlays/<cluster>}/` (PR #2051):

- **Generators and the nameReference config MUST move with the resources** — a rewrite only applies within one `kustomize build`; leaving generators in the cluster base silently renders plain (unhashed) secretRefs. Verify: grep the new overlay render's Provider/Receiver `secretRef.name` for `-<hash>`.
- **Dependency:** a config overlay issuing cluster-CA certs (`issuerRef: studio-shikanime`) depends on `config-cert-manager`, NOT `infrastructure-cert-manager` (mirrors `external-dns`).
- **Component wiring:** `clusters/<cluster>/components/<area>/ks.yaml` gains one Kustomization per plane — `infrastructure-<area>` + `config-<area>` (tailscale exemplar); `config-*` dependsOn `infrastructure-*`.
- **Check sibling consumers before deleting from base** — moved generators may have been the only source for a secret other resources reference; grep the cluster overlay render after the move.
- **Route split (PR #2051, FINAL layout):** `infrastructure/<op>/base/httproute.yaml` keeps the generic backendRef rule; `gateway.yaml` + `patch-httproute.yaml` in plain `overlays/<cluster>/`; ONLY `gatewayclass.yaml` + `envoyproxy.yaml` (LB plane) in `overlays/<cluster>-tailnet/`. Gateway/GatewayClass/EnvoyProxy move OUT of `base/`; Flux `path:` points at the tailnet overlay (renders nishir via `resources: [../nishir]`). Redirect routes = EXTRA DOCS in the same files, not new files. Nested mautrix/servarr trees got the same treatment — audit globs must be RECURSIVE (`apps/**/overlays/nishir{,-tailnet}`).
- **Per-component route split, multi-port apps (hermes-agent):** each `apps/<app>/components/<name>/` owns its `httproute.yaml` (route + 301-redirect pair, GENERIC backendRefs only). Overlay `patch-httproute.yaml` carries ONE PATCH DOC PER ROUTE (3 components = 6 docs, each naming its `metadata.name`, NO `target:`); tailnet overlay duplicates it with ts.net hostnames. Every component kustomization must list `httproute.yaml` under `resources:`. Hostnames: `<comp>.<base>`; nishir gets ONLY `i.shikanime.studio` names, tailnet ONLY `taila659a.ts.net` (never both in one patch). Hostname renames cascade to Gateway `certificateRefs` AND `configs/cert-manager/overlays/<cluster>/cert.yaml` — replace stale certs wholesale, grep render for old tokens (0 hits). Superseding a standalone component route (a2a port 9900 from `httproutes-extra.yaml`): DELETE the extra file + kustomization entry in the same commit; move port retention to `components/<name>/patch-svc.yaml`/`patch-sts.yaml`.

### Gotcha: duplicate secretGenerator name across an overlay-include chain

Overlay `B` does `resources: [../A]`; both declare `secretGenerator` with the same `name:` → `id .../Secret/<name> exists; can not use behavior: 'unspecified'`. Declare ONCE in the shared base overlay; children inherit (verify both renders produce the identical hashed name). Bit `nishir-tailnet` when `inference-z-ai` moved into `nishir`: tailnet had to DROP its copy.

- JSON6902 wired from a plain `nishir` overlay WITHOUT `target:` fails `must specify a target for JSON patch` — SMP can match by `metadata.name`, JSON6902 lists cannot. Always give JSON6902 entries explicit `target:`.

### Gotcha: Deployment mounts a ConfigMap but no configMapGenerator exists

Deployment references `configMap: { name: my-config }` by plain name; overlay only has a `secretGenerator` (or neither) → pod gets `configmap "my-config" not found`. Example: `apps/honcho/base/deploy.yaml` mounts `configMap: name: honcho`; the tailnet overlay's `secretGenerator` produces a Secret, not a ConfigMap. Fix:

```yaml
# apps/<app>/overlays/<cluster>-tailnet/kustomization.yaml

configMapGenerator:
  - name: honcho
    files:
      - honcho/config.toml
```

Verify: `kustomize build apps/<app>/overlays/<cluster>-tailnet | grep -A2 "kind: ConfigMap" | grep "name: honcho"`. secretGenerator = encrypted secrets (`.enc.env`, Flux SOPS); configMapGenerator = plain-text config files the app reads at startup. NOT interchangeable.

## Immutable StatefulSet `volumeClaimTemplates` divergence (Flux dry-run failing)

STS `volumeClaimTemplates` change (e.g. storageClassName migration) vs live STS holding old value → Flux Kustomization `False`:

```
StatefulSet.apps "<name>" is invalid: spec: Forbidden: updates to statefulset
spec for fields other than 'replicas', 'ordinals', 'template', 'updateStrategy',
'revisionHistoryLimit', 'persistentVolumeClaimRetentionPolicy' and
'minReadySeconds' are forbidden
```

VCT is IMMUTABLE — no patch path; recreate the STS so Flux re-applies the corrected VCT. Migrated PVCs persist (data preserved):

1. Confirm migrated PVCs `Bound` on the new SC (`kubectl get pvc <data> <timeline> -n <ns>`). Snapshot first: `kubectl get sts <name> -n <ns> -o yaml > /tmp/sts-backup.yaml`.
2. `kubectl delete sts <name> -n <ns> --cascade=orphan --wait=false`
3. Reconcile Flux: `kubectl annotate kustomization <app> -n flux-system \ reconcile.fluxcd.io/requestedAt="$(date +%s)" --overwrite`
4. Verify: STS VCT matches manifest, pod Running/Ready on migrated PVC, `kustomization <app>` → `True`.

Pitfall: pre-existing pod may show `OOMKilled` restarts (no memory limit + VPA `Initial`) — check `creationTimestamp` vs STS delete time. Same class as the immich pitfall (`immich-hw-transcode-manifests` skill).

## SOPS store choice for config-file seeds: use BINARY, never ini or json+render

secretGenerator seeding an app's whole config file (qBittorrent.conf, sonarr config.xml, bazarr config.yaml): encrypt as **sops BINARY** (`--input-type binary --output-type binary`) — decrypted bytes are the EXACT file. User directive 2026-09-07: "use binary sops format, remove all rendering".

- **ini store backtick-quotes values containing `;`**: `ServerDomains = a.b; c.d` round-trips as `` ServerDomains = `"a.b; c.d"` `` — Qt QSettings reads the backticks+quotes literally; host-header validation fails (WebUI "Unauthorized").
- **json store**: flat `{"Section\\Key": value}` + render step in an initContainer — rejected complexity.
- **binary store**: one `{"data": "ENC[...]", "mac": ...}` envelope, byte-exact restore.

Re-encrypt (preserve recipients — read from old file's metadata first):

```bash
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
sops -d --input-type ini old.enc.conf > /tmp/plain.conf   # match the OLD store type
# edit plaintext (fix quoted values, update settings), then:

sops --encrypt --input-type binary --output-type binary \
  --age <recipient1> --age <recipient2> --age <recipient3> \
  /tmp/plain.conf > new.enc.conf
# verify round-trip byte-exactness:

sops -d new.enc.conf | diff - /tmp/plain.conf && echo ROUNDTRIP-EXACT
```

Secret key = the file, not the store: `secretGenerator.files: - qBittorrent.conf=qbittorrent/qBittorrent.enc.conf` makes the Secret key `qBittorrent.conf`; volume `items.key` must match. Init-container `rclone copyto` of the seed OVERWRITES the app config on every pod start — bake desired settings (e.g. `WebUI\AuthSubnetWhitelist = 0.0.0.0/0, ::/0` for an OIDC-fronted WebUI) into the seed, not runtime patches.

### Envoy SecurityPolicy OIDC naming convention (2026-09-07)

SecurityPolicy name is `<app>-oidc-client`, matching its `spec.oidc.clientSecret.name` secretGenerator (user rename qbittorrent-oidc → qbittorrent-oidc-client). Namereference entry `SecurityPolicy/gateway.envoyproxy.io → spec/oidc/clientSecret/name` rewrites the hash. A WebUI fronted this way must ALSO set its own auth bypass in the seed config or every request double-authenticates.

## Validating SOPS-encrypted overlays locally

```bash
SOPS_AGE_KEY="$HOME/.config/sops/age/keys.txt" \
  kustomize build apps/<app>/overlays/<cluster>-tailnet
```

Decrypts `.enc.*` and renders the generated `Secret` without a cluster; grep the output for the Secret name + added resource (e.g. `MCPRoute`). **Limits (2026-09-03):** kustomize has NO dotenv SOPS decryptor — `.enc.env` via `secretGenerator.envs:` renders verbatim (`client-secret: ENC[...]` + `sops_*` keys) even with `SOPS_AGE_KEY` set; `.enc.yaml` DOES decrypt. `ENC[...]` from `.enc.env` is EXPECTED (Flux decrypts at reconcile, `decryption.provider: sops`) — CodeRabbit flags it every time; false positive. `sops_*` extra keys are harmless.

## Renaming a secretGenerator / provider resource

The `<secret-name>/` directory IS the Secret name — renaming is NOT just a kustomization edit:

1. `mv apps/<app>/overlays/<cluster>-tailnet/<old>/ apps/<app>/overlays/<cluster>-tailnet/<new>/` (e.g. `inference-zai/` → `inference-z-ai/`).
2. Update BOTH the `name:` and the `envs:` path (`- <new>/.enc.env`) of that `secretGenerator` block.

### Secret folder naming convention (2026-09-03, PR 2134)

- **App-level dotenv secrets** (`envs:`/envFrom): folder `<secret>-env/`, file `.enc.env` (`lldap-env/.enc.env`, `inference-z-ai-env/.enc.env`). Secret NAME unchanged — only the folder. Infra/config-plane token secrets stay as-is in `<name>/` folders: longhorn-hetzner-backups, cloudflare-api-token, operator-oauth, hetzner, discord-webhook, receiver-token, ai-gateway-session-seed, inference-gateway-apikey, catbox-sops-key — do not migrate "for consistency" (convention scoped to app env secrets).
- **Sibling files split** (servarr pattern): a config fed to a DIFFERENT secretGenerator lives in its own folder — `sonarr/config.enc.xml` → Secret `sonarr` (startup-config mount); `sonarr-env/.enc.env` → Secret `sonarr-pkcs12-password`. One folder per secretGenerator.

Bulk rename must rewire EVERY source path in the kustomization, not just `envs:` — sibling `files:` entries (`config.yaml`, `SOUL.md`, `config.xml=<folder>/...`) fail only at `kustomize build` (`evalsymlink failure`), not edit time. Verification:

```bash
# 1. decrypt round-trip: every moved file byte-identical to HEAD original

for new in $(git status --porcelain | awk '/^R /{print $4}'); do
  old=$(echo "$new" | sed 's/-env\/\.enc\.env/\/\.enc\.env/')
  a=$(sops -d --input-type dotenv --output-type dotenv <(git show "HEAD:$old") | sort | shasum | cut -d' ' -f1)
  b=$(sops -d --input-type dotenv --output-type dotenv "$new" | sort | shasum | cut -d' ' -f1)
  [ "$a" = "$b" ] || echo "MISMATCH $new"
done
# 2. fleet sweep with a PRE-EXISTING-FAILURE baseline: build every

# kustomization on your branch AND on HEAD (temp worktree); only dirs that
# fail on the branch but NOT on HEAD are regressions. Component dirs

# (apps/*/components/*) legitimately fail standalone on both.
```

**Shared jj worktree hazard:** a sibling agent running `jj new main@origin` snapshots and REWRITES the shared working copy — uncommitted renames vanish from `git status`, surviving only as a dangling jj change. In shared worktrees: `jj describe` + commit incrementally per unit; if work disappears, check `jj log --no-graph` / `git fsck --lost-found` before redoing. Detail: `references/secret-folder-rename.md`.

Full provider rename (Backend + AIServiceBackend + BackendSecurityPolicy + secretGenerator) touches every reference file. Grep FIRST:

```bash
rg -l 'zai' --glob '!*.enc.*' apps/<app>   # find every file, then patch each
```

Then `replace_all` in each: Backend `name:`, AIServiceBackend `name:` + `backendRef.name:`, BackendSecurityPolicy `name:` + `targetRefs.name:` + `secretRef.name:`, `AIGatewayRoute` `backendRefs.name:`, the `MCPRoute`, the overlay kustomization. `api.z.ai` (dot-form public host) is NOT an internal resource name — leave it alone.

### BYOD Envoy Gateway file layout: one file per resource, multi-doc stacks forbidden

Split as `<resource-name>.yaml` — `gatewayclass.yaml`, `envoyproxy.yaml`, `gateway.yaml` (Gateway docs only), `httproute.yaml` — NEVER a multi-doc `gateway.yaml` stack (user reverted a merge, directed per-resource splits). `envoyDeployment.replicas: 1` is the EnvoyProxy CRD default — omit it.

CRITICAL: two gateways can share one overlay (llama-cpp: `inference` mTLS/API-key + `llama-cpp` chat). Before rewriting `envoyproxy.yaml` / `gatewayclass.yaml`, check `git show origin/main:<path>` FIRST — the file may hold the OTHER gateway's docs (chat docs once overwrote the inference GatewayClass/EnvoyProxy, leaving the inference Gateway on a non-existent class; caught only after rebase + render inspection).

`envoyService.name` == app Service name is the fleet convention, NOT a collision bug (jellyfin: `envoyService.name: jellyfin`; Envoy Gateway adopts the existing Service). CodeRabbit once suggested `lldap-envoy` — rejected; inconsistent with all ~29 tailnet gateways. Don't "fix" it.

### Base keeps only transport-agnostic rules; app-gateway rules go to the tailnet overlay

Base `netpol.yaml` admits only transport-agnostic flows (lldap: `ldap` port; deny-all `ingress: []` when no intra-app callers). Exposure-path rules (Envoy `envoy-gateway-system` allow, vmagent scrapes) are inline JSON6902 appends in the overlay OWNING the path — PR #2294: plain `overlays/<cluster>/` carries envoy + vmagent appends; `-tailnet` inherits via `resources: [../nishir]` (a standalone tailnet `netpol.yaml` collides with the base policy — same-id resources cannot coexist in one build). Cluster-wide `default` netpol's envoy admission goes directly into `clusters/<cluster>/base/netpol.yaml`. No same-app self-ingress rule unless the workload genuinely calls itself.

**Cheap render verification (macOS, no devenv):** `K=$(nix build nixpkgs#kustomize --print-out-paths)/kustomize` (5.8.1); `nix fmt` after a plain `nix build` dirties the `result` symlink and sops `.enc.*` files — `jj restore result <enc files>` before describing; parse renders with `uv run --with pyyaml python` (system python lacks yaml) asserting rule tuples (namespace, pod, ports) per policy + a `patch-netpol` stale-token grep — build exit 0 does not prove the rules.

PITFALL: moving a rule out of base — NEVER rewrite the base file from scratch (one rewrite dropped `podSelector` + `policyTypes`, which would have selected every pod in the namespace). Shrink with a targeted `patch`, preserving `podSelector`/`policyTypes`.

## Escaping a corrupted rebase: cherry-pick hotfix

When an interactive rebase corrupts `.git/rebase-merge/git-rebase-todo` (all `drop` edits merge into one line, `pick` lines orphaned, resolution impossible), cherry-pick onto a clean branch instead of rebase-reset + re-attempt (happened on `realign-tailscale-hostnames`: 18 commits, 18 conflicts):

1. `git rebase --abort` (stash uncommitted work first).
2. `git checkout main && git checkout -B <branch> origin/main`
3. `git cherry-pick <sha>` one at a time; resolve as they arise (`sed`/`patch` + `git add`); `git stash push --include-untracked` as last resort.
4. Note skipped shas; `git diff origin/main` shows what actually changed — missing-commit outputs are the dropped ones.
5. `git push --force-with-lease origin <branch>` (never bare `--force`; it can clobber collaborators).

Advantages over rebase: one conflict at a time; `git status` shows only the current conflict; picks keep original messages/shas. Full procedure: `references/cherry-pick-rebase-hotfix.md`.

Advantages: one conflict at a time; `git status` shows only the current conflict; picks keep original messages/shas in `git log`. Full procedure: `references/cherry-pick-rebase-hotfix.md`.

- **Conflict markers in YAML with heredoc delimiter `$`:** `sed` inside Python fails on `<<<<<<<` in heredoc content (e.g. `--caddyfile` field) — use pure Python `re` (`execute_code`) for conflict resolution on YAML.
- **`git cherry-pick --continue` cannot skip:** on conflicts it always fails (no `--skip` equivalent). Resolve, `git add`, then `git commit --amend` to rewrite the current commit without aborting the chain; or `--abort` and re-apply.

## Verification (before claiming done)

```bash
kustomize build apps/<app>/overlays/<cluster>-tailnet | grep -E "name: <secret>|secretName"
# generated name and every reference must carry the SAME hash suffix

kustomize build clusters/nishir/overlays/tailnet   # app wired via ks.yaml; must render clean
# if the secret is referenced by a CRD field (MCPRoute/BackendSecurityPolicy), the rendered

# secretRef.name must carry the SAME hash suffix as the Secret:
kustomize build apps/<app>/overlays/<cluster> | rg -n 'name: <secret>-[a-z0-9]+'
kustomize build apps/<app>/overlays/<cluster> | rg -n 'kind: (MCPRoute|BackendSecurityPolicy)' -A14 | rg -n 'secretRef|name: <secret>'
# both must show <secret>-<hash>; a plain <secret> in the CRD means nameReference is missing

```

Build exit 0 is NOT content verification — a multi-doc file can carry a stale value that still builds. After renaming a value (hostname, cert, port name), grep the RENDER for BOTH old and new tokens:

```bash
kustomize build <overlay> | grep -nE 'old-value|new-value'   # old must be 0 hits
```

Verified miss (PR #2047): llama-cpp UI hostname renamed, build exited 0, but the redirect HTTPRoute inside multi-doc `ui-gateway.yaml` still carried the old hostname. Grep-for-stragglers catches what exit codes don't.

- **Leading `---` markers are treefmt-normalized**: treefmt ADDS a leading `---` to the first doc and removes doubled separators. Don't hand-fight; `nix fmt` then scoped-stage (never `git add -A` after whole-tree fmt).
- Check `git diff` after edits — misapplied patches look truncated in custom diff formats; `git show HEAD:path | diff - path` is the reliable read.

### LWS (LeaderWorkerSet) + router mode — 2-node capacity

llama.cpp `router` mode (no `-hf`; models loaded via `POST /models/load`): overlay shared by `nishir/` + `nishir-tailnet/`; Flux `ks.yaml` targets the tailnet overlay. `models-preset.ini` as ConfigMap or secretGenerator Secret (subfolder convention below). Flux patch adds `--models-preset`, `--models-dir` env + overlay patches (ingress, netpol). One router pod replaces N model StatefulSets.

With LWS `replicas: 2`, both replicas are **identical** (same `leaderWorkerTemplate`, mounts, args) and load ALL models simultaneously — the full set must fit in ONE node's RAM:

```
Capacity math per node (128GB RAM, ~115GB usable after GPU reservation):
  GLM-5.3-Flash  ~93 GB  ✅ fits alone
  DeepSeek-V4-Flash ~87 GB  ✅ fits alone
  Qwen3-8B        ~80 GB  ✅ fits alone
  Qwen3.8-27B     ~55 GB  ✅ fits alone
  Qwen3-Embedding-8B ~6 GB ✅ fits alone
  Total (all 5)   ~321 GB ❌ exceeds 128 GB
```

Options: (1) single model (~87-93GB) × 2 replicas; (2) per-node overlays (`nishir-kushira/`, `nishir-sashina/`) with different ConfigMaps + LWS affinity; (3) compatible pairs — DeepSeek+Embedding (93GB) or GLM-5.3-Flash+Embedding (99GB), loses models.

`--models-dir` is local per pod (independent copies in `/models`). Default volume = ConfigMap; a Longhorn PVC at the same path (`apps/llama-cpp/inference-router/base/pvc.yaml`) shares disk I/O, loading idempotent — preferred when both nodes share a GPU machine with storage. LWS `size: 1` = leader pods only; `replicas: 2` = 2 leaders on 2 nodes.

### LWS headless Service has no ports and its name is controller-owned

LWS `networkConfig` exposes ONLY `subdomainPolicy: Shared|UniquePerReplica` (verified against `api/leaderworkerset/v1/leaderworkerset_types.go` + live CRD) — no disable, no name override, no ports. The headless Service renders `ports: null`, name == LWS name, `ownerReferences.controller: true`:

- HTTPRoute `backendRefs: [{name: <lws-name>, port: N}]` fails `ResolvedRefs=False: PortNotFound`. You cannot create a plain Service named like the LWS (headless owns the name).

Fix (PR #2110): RENAME the LWS with a suffix (`llama-cpp-cluster`), add plain `svc.yaml` claiming the app name with real ports, keep HTTPRoute/Envoy `Backend` fqdn on the app name. Cascade: worker DNS (`<lws>-0-1.<lws>.<ns>.svc.cluster.local` — update RPC peer env vars); VPA `targetRef.name`; Flux `ks.yaml` healthCheck `LeaderWorkerSet/<old-name>`. Pod labels untouched (netpol/vmservicescrape/anti-affinity selectors need no edits). Old LWS pruned automatically via `prune: true` (repo default) — verify `kubectl get kustomization <app> -n flux-system -o jsonpath='{.spec.prune}'`, don't hand-delete.

**Selector must be leader-only:** plain Service on pod labels matches leaders AND workers; workers (`ggml-rpc-server`) expose only `rpc: 50052`, so `targetPort: http` can't resolve on their endpoints. Pin with `leaderworkerset.sigs.k8s.io/worker-index: "0"` (leaders 0, workers 1+, verified on live pods).

### LWS volume migration: PVC → EmptyDir + Secret

Swap BOTH `containers[].volumeMounts` and `volumes[]` (leader + worker): **PVC volume** → `emptyDir: {}`; **ConfigMap volume** → `secret: { secretName: <secret-name> }`. Secret name = the `secretGenerator` name, used directly (no hash suffix — LWS volume names are not name-reference targets). Base switches `configMapGenerator` → `secretGenerator`, drops the PVC from resources; `models-preset.ini` moves to `<secret-name>/models-preset.ini`. Verify with `nix run nixpkgs#kustomize`.

### AIGatewayRoute routing patterns

Two AIGatewayRoutes bind the same Gateway via `spec.parentRefs` — listener shared, routes selected on `x-ai-eg-model` header matches; higher priority first (non-zai `glm/glm-5.3-flash` wins over zai; zai fires only when the primary chain is absent/exhausted). AIGatewayRoutes live in `apps/llama-cpp/base/route.yaml` with Backends + AIServiceBackends; all Backends in `apps/llama-cpp/base/backend.yaml`. `backendRefs` use `priority:` integers: 0 = local floor (first local hit wins), ascending for remote chains. `modelNameOverride` is required and must match the `x-ai-eg-model` header value.

Generic model names for `x-ai-eg-model` (used consistently in `modelNameOverride` and match headers, regardless of provider ID):

| Header value             | Provider model ID                 | Notes                           |
| ------------------------ | --------------------------------- | ------------------------------- |
| `qwen/qwen-flash`        | `qwen/qwen3.8-flash` (remote)     | Short alias for local cache key |
| `qwen/qwen-27b`          | `qwen/qwen3.8-27b` (remote)       |                                 |
| `deepseek/deepseek-flash`| `deepseek/deepseek-v4-flash-0731` | Actual GGUF: DeepSeek-V4-Flash  |
| `z-ai/glm-flash`         | `z-ai/glm-5.3-flash` (remote)     |                                 |

Local key in `models-preset.ini` may differ (e.g. `[qwen/qwen3.8-flash]` section); the route header uses the generic name. Dedicated fallback chains: `default` (inference→nous→openrouter) vs `zai` (inference→zai→nous→openrouter) on one Gateway, split by `x-ai-eg-model: glm/glm-5.3-flash`.

### MCPRoute — separate CRD for MCP servers

Provider MCP tools (Z.ai `web_search_prime`/`zread`, etc.) through the same gateway use the `MCPRoute` CRD (`aigateway.envoyproxy.io/v1beta1`), DISTINCT from `AIGatewayRoute`; reuses an existing `Backend` + provider secret via inline `securityPolicy`:

```yaml
apiVersion: aigateway.envoyproxy.io/v1beta1
kind: MCPRoute
metadata:
  name: z-ai
  namespace: shikanime
spec:
  parentRefs:
    - name: inference
      kind: Gateway
      group: gateway.networking.k8s.io
  path: /mcp/z-ai
  backendRefs:
    - group: gateway.envoyproxy.io
      kind: Backend
      name: z-ai
      path: /api/mcp/z-ai            # upstream MCP base path on the provider host
      securityPolicy:
        apiKey:
          secretRef:
            name: inference-z-ai     # plain name; nameReference rewrites to hash
            namespace: shikanime
```

Upstream path is provider-specific — confirm against provider MCP docs (wrong path 404s at the gateway). Place in `base` so every overlay including it (esp. non-tailnet `nishir`) renders it; ensure each such overlay generates the referenced secret.

### llama-cpp/ model deployments: per-app kustomize trees

`apps/llama-cpp/<model>/`: `base/`, `overlays/nishir/`, `overlays/nishir-tailnet/`. Consolidating into one router-mode StatefulSet (`apps/llama-cpp/inference/`) replaces per-model Flux entries with one `apps-llama-cpp-inference`. Splitting a pool: each sub-app needs its own `base/` (LWS or STS, models-preset.ini, netpol); `overlays/nishir/` (namespace-only ref); `overlays/nishir-tailnet/` (ingress, netpol patches); Flux `ks.yaml` path update.

### Secret subfolder convention for models-preset.ini

With `secretGenerator`, `models-preset.ini` MUST live at `<secret-name>/models-preset.ini`, referenced as `secretGenerator.files: - models-preset.ini=<secret-name>/models-preset.ini` (user directive; AGENTS.md convention). ConfigMapGenerator is hash-free — subfolder relaxed, file sits beside kustomization.yaml:

```yaml
# apps/llama-cpp/inference/base/kustomization.yaml

configMapGenerator:
  - name: models-preset
    namespace: shikanime
    files:
      - models-preset.ini
```

```yaml
# apps/llama-cpp/embedding/base/kustomization.yaml

secretGenerator:
  - name: qwen-embedding
    files:
      - models-preset.ini=qwen-embedding/models-preset.ini
# File lives at apps/llama-cpp/embedding/base/qwen-embedding/models-preset.ini

```

### --models-max and LRU eviction

Router mode loads on demand, unloads under memory pressure. Without a cap each node loads all preset models (can exceed RAM). `--models-max N` caps simultaneously loaded models per node (LRU); applies per-pod even with shared storage. Reference: `apps/llama-cpp/inference-router/base/lws.yaml` env args.

### Deleting a configs/<area>/ tree (Flux wiring)

`configs/<area>/` is wired as a Flux `Kustomization` in some `clusters/<cluster>/components/<area>/ks.yaml` (e.g. `config-node-feature-discovery` → `path: ./configs/<area>`). Deleting the dir without removing the wiring dangles the path and breaks the Flux build:

1. `rm -rf configs/<area>`
2. Delete the `<area>` Kustomization doc block from the component `ks.yaml` (keep the operator-infra doc if the operator still deploys).

No empty placeholders (`resources: []`) "for future rules" — user rejected. Verify: `kustomize build clusters/<cluster>/overlays/tailnet` renders; `grep -r "<area>" clusters/` has no dangling reference.

### Cluster-scoped infrastructure operators via Flux HelmRelease

Operators (CRDs + controller: LWS, cert-manager, gatekeeper...) differ from per-app workloads: operator namespace declared, HelmRelease targets it (`targetNamespace`), Flux `Kustomization` in `ks.yaml` drives reconciliation:

```
infrastructure/<operator>/base/
  helmrepo.yaml    — Flux HelmRepository (public OCI or HTTP)
  hr.yaml          — Flux HelmRelease (chart version, values: {})
  kustomization.yaml — references the two above
```

```yaml
# clusters/<cluster>/overlays/<overlay>/ks.yaml

apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure-lws
  namespace: flux-system
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-age
  dependsOn:
    - name: infrastructure-tailscale   # infra operators depend on networking
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: leaderworkerset-controller-manager
      namespace: leaderworkerset-system
  interval: 10m
  path: ./infrastructure/lws/base
  prune: true
  sourceRef:
    name: flux-system
    kind: GitRepository
```

Differences from per-app: `path` → `infrastructure/<operator>/base`; `healthChecks` target the controller namespace; no generators in base (config in `HelmRelease.values` or chart defaults); operator CRDs (e.g. `leaderworkerset.x-k8s.io`) installed by the chart's CRD bundle.

### Gateway API migration reference

`references/gateway-api-migration.md` — route-parity rules, EnvoyPatchPolicy static-response patterns, Flux dependency wiring, PR-branch validation.

### Splitting a multi-kind file into per-kind files

A file with multiple kinds (CronJob + ServiceAccount + ClusterRole + ClusterRoleBinding) violates one-kind-per-file. Split to files named by the lowercase kind, list each in `resources:` — a missing entry silently omits the object (no kustomize error); verify the full render after splitting: `ca-rotation-heal.yaml → cronjob.yaml + sa.yaml + clusterrole.yaml + clusterrolebinding.yaml`. If the file existed in history but not the working tree, validate against `git show <sha>:<path>`.

### repo conventions

- Existing `nameReference` users: `apps/jellyfin/overlays/nishir/`, `apps/prowlarr/overlays/nishir/`, `apps/servarr/{lidarr,radarr,sonarr,whisparr}/overlays/nishir/`, `clusters/*/base/` (Provider/Receiver `secretRef`). Per-app encrypted secrets live in a subfolder named after the secret (`sops-key/.enc.env`); Flux decrypts `.enc.*` at reconcile.
- Namespace gotcha debug bisect evidence: `references/namespace-gotcha-bisect.md`. NFD PCI/AMD GPU labels (no custom NodeFeatureRules): `references/nfd-label-convention.md`. HTTPRoute hostname injection + verification: `references/httproute-hostname-injection.md`.
- Patch layout (JSON6902 inline vs SMP files, append-scalar, multidoc): `references/tailnet-patch-layout.md`. Structural audit method: `references/structural-audit.md`. Envoy AI Gateway hashed-secret nameReference (`configurations:` vs `transformers:`, no `hash:` field, duplicate-generator collision): `references/envoy-ai-gateway-secretref.md`.
- Tailnet UI gateway smoke test (Flux revision, Gateway Accepted/LB IP, curl `--resolve` vs MagicDNS flakiness, failure-mode table): `references/tailnet-smoke-test.md`. dex → authelia migration (Authelia 4.39 config, silent startup-check fatals, Flux health-check deadlock, PVC debug residue): `references/authelia-dex-migration.md`.
- Inference app: `apps/llama-cpp/` defines OpenAI-schema AIServiceBackends, Backends, AIGatewayRoutes (local floors `priority: 0`); workload/LWS is `llama-cpp` (Service `llama-cpp.shikanime.svc.cluster.local:8080`) but Gateway/Route/Backend-API names stay `inference` (only the workload was renamed from `router`). Flux entry `apps-llama-cpp` in `clusters/nishir/overlays/tailnet/ks.yaml`, healthCheck `LeaderWorkerSet/llama-cpp`. Label `app.kubernetes.io/component: inference` (was `llm-inference`).
- `apps/honcho/`: ConfigMap mount needs a `configMapGenerator` — a `secretGenerator` alone does NOT produce a ConfigMap.
- Corrupted-rebase cherry-pick escape hatch — full procedure: `references/cherry-pick-rebase-hotfix.md`.
