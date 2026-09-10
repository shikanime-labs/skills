---
name: book-wharf
description: Use when building Nix flake OCI images with wharf.
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - wharf
      - oci
      - machines
      - ci
      - skaffold
      - ghcr
    related_skills:
      - book-llama-cpp
      - nix-flake-ci-scoping
      - sks-land
platforms:
  - linux
  - macos
---

# wharf: Nix flake OCI image builds (machines Release CI)

`shikanime-labs/wharf` (renamed from nix-containers) builds OCI images from
Nix flakes and pushes them to ghcr via the `machines` repo Release workflow.
Repo: `github:shikanime-labs/wharf`; local clone
`~/Source/Repos/github.com/shikanime-labs/wharf`; the Go module root is
`cmd/wharf`.

## Flag surface (post wharf#101, landed as ad804cc7)

- Global (persistent, valid on BOTH `wharf build` and `wharf skaffold build`):
  `--flake`, `--platforms`, `--option key=value` (repeatable), `--debug`.
- REMOVED: `--accept-flake-config` / `--no-pure-eval` flags and the
  `ACCEPT_FLAKE_CONFIG` / `NO_PURE_EVAL` env bindings. Pass nix settings
  uniformly: `--option accept-flake-config=true`. Older docs/examples with
  `skaffold build --accept-flake-config` are stale and now error.
- `--option key=value` forwards verbatim as `--option key value` to the
  underlying nix command; malformed pairs are rejected early.
- `--platforms` semantics: wharf derives the flake attribute from the IMAGE
  name's last segment (`ghcr.io/.../llama-cpp` → `packages.<sys>.llama-cpp`).
  Post-#101 it is GLOBAL, so `skaffold build --platforms ...` is valid and
  machines `skaffold.yaml` omits it entirely (skaffold/CI drives platforms).
- nixpkgs llama-cpp override surface (0.2.0, nixos-unstable): `rocmSupport`,
  `vulkanSupport ? false` (produces `libggml-vulkan.so`, evaluates on BOTH
  linux arches — the arm64 GPU fallback where ROCm is unavailable),
  `rpcSupport ? false` (adds `bin/ggml-rpc-server` + `lib/libggml-rpc.so`),
  `metalSupport` (darwin-only; user reverted darwin support), `cudaSupport`.
  Check `pkgs/by-name/ll/llama-cpp/package.nix` upstream for the current set.
- **`meta.platforms` is enforced**: a build against a host not listed fails
  with "Refusing to evaluate package ... not available on the requested
  hostPlatform". This is the gate working, not a bug — check `meta.platforms`
  first when a cross-arch build refuses. Also: an in-flight `nix build` of an
  OLD commit's attr shape fails confusingly after a force-push renames attrs —
  re-check the PR head's attr names before diagnosing.

## skaffold.yaml shape (machines repo root, post machines#1278)

```yaml
artifacts:
  - custom:
      buildCommand:
        nix run
        github:shikanime-labs/wharf/d1faf2b6
        -- skaffold build --flake . --accept-flake-config
    image: ghcr.io/shikanime-labs/machines/catbox
  - custom:
      buildCommand:
        nix run
        github:shikanime-labs/wharf/d1faf2b6
        -- skaffold build --flake . --accept-flake-config
    image: ghcr.io/shikanime-labs/machines/llama-cpp
```

BOTH artifacts use `skaffold build` with NO explicit `--platforms` — the user
directed this final shape after iterating through root-`build` + platform pins
(machines #1278); skaffold/CI drives platforms. Do not reintroduce `-- build`
or `--platforms` pins without direction.

One `llama-cpp` image per arch — the package itself switches GPU backend on
`system` (`pkgs/llama-cpp/default.nix` takes `{ pkgs, lib, system, ... }:` —
the ellipsis matters, callPackage may pass extra args):
`rocmSupport` on x86_64-linux (leader, `llama-server:8080`),
`vulkanSupport` on aarch64-linux (worker), `rpcSupport = true`
UNCONDITIONALLY (ROCm supports RPC fine — verified live on sashina, the
rocm+rpc nixpkgs build ships `bin/ggml-rpc-server` + `libggml-rpc.so`; do not
gate RPC behind arch), and Entrypoint `ggml-rpc-server` for BOTH arches.
Do NOT regress to `llama-cpp-rocm`/`llama-cpp-vulkan` name splits, per-arch
`--platforms` pins, `lib.recurseIntoAttrs` on the package attrset, or an
`llama-server` if-else — the user iterated through all of these and rejected
them (2026-09, PR #1278). ROCm does not evaluate on aarch64 (`llvm-rocm`
refuses the host platform); keep darwin out entirely (metalSupport was
added then reverted by user). Do NOT gate on
`pkgs.stdenv.hostPlatform.isLinux` inside flake-parts perSystem, and do NOT
splice a whole attrset import into `packages` (`packages = import ...` in an
`optionalAttrs` block) — both cause "infinite recursion encountered" in the
flake-parts module-arg resolution. Use explicit `system ==` checks with
`pkgs.callPackage ... { inherit system; }`, and assign individual attrs
(`packages.llama-cpp = ...`). Verified per-arch proof: `meta.description`
switches ("ROCm inference server" vs "Vulkan RPC worker") and
`packages.aarch64-darwin.llama-cpp` stays absent.

Lessons, each paid for with a failed Release run:

- `--platforms` only exists on the root `build` command. The CI action
  (`shikanime-labs/actions/skaffold/integration`) defaults
  `SKAFFOLD_PLATFORM=linux/amd64,linux/arm64`; an x86_64-only package
  (llama-cpp ROCm) MUST pin `--platforms linux/amd64` or the arm leg fails
  package resolution.
- `--flake .` (repo root), never `--flake .#pkg` — the explicit attr makes
  wharf build the invalid `llama-cpp#packages.x86_64-linux.llama-cpp`.
- Multi-platform builds re-queue themselves: an explicit rerun of an
  in-flight run 403s with "This workflow is already running" — wait for the
  auto-requeued Integration run instead of fighting it.
- Background `gh run watch` on large image builds (llama.cpp ROCm ≈ tens of
  minutes) exceeds the foreground 420s cap — run the watcher with
  `background=true, notify=true`, and re-arm it after every fresh push
  (the watch binds to the run, not the PR).
- Image names are frozen: `ghcr.io/shikanime-labs/machines/llama-cpp` and
  `.../catbox`. Never rename registry tags. TagPolicy template is `latest`.
- Anonymous ghcr tag listing returns `UNAUTHORIZED` — that is NOT evidence
  of publish failure; verify with auth.
- Release failure history: eval-cache race under concurrent per-platform
  nix builds (doubled `packages.<sys>.` attr segments, "failed to parse nix
  build output: EOF") was fixed by the nixMu mutex (d1faf2b) and then by
  the nix-fast-build batched path (wharf#100, open at session time).

## Landing gates on machines/wharf

Ruleset "Landing protections" requires code-owner review + last-push
approval; the classic branch-protection endpoint 404s (rulesets, not
classic). After a verbal lgtm: `gh pr merge --squash --admin` with
`--subject` + `--body` (never two-arg `-m`; body via file). Merge body:
rationale paragraph + `Related:` full URL + `Signed-off-by: Shikanime Deva
<william.phetsinorath@shikanime.studio>` + `Co-authored-by: Automata
<automata@shikanime.studio>`. After merge GitHub drops the remote branch —
`git push origin --delete` answering "remote ref does not exist" is
confirmation, not an error.

## aarch64 Checks: chronic environmental red (wharf)

`nix / Checks (aarch64-linux, ubuntu-24.04-arm)` fails for reasons unrelated
to the diff, identically across unrelated PRs (#100, #101):

1. Nix installer logs `Failed to open the device 'kvm': Invalid argument`.
2. golangci-lint then throws vendor typecheck false-positives ("open
   vendor/.../types.go: no such file or directory" for files that exist;
   `go mod vendor && git status --short vendor/` shows zero drift).

Trust signal: `nix / Checks (x86_64-linux)` green + local
`go build ./... && go vet ./cmd/... && go test ./cmd/...`, cross-checked
with `GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go vet ./cmd/...`. Decision
options: wait for the auto-requeued Integration run (explicit rerun 403s
"already running"), or land `--squash --admin` after lgtm documenting the
environmental red in the merge body.

## Verifying a build locally (aarch64-darwin workstation)

Local x86_64-linux builds fail "Exec format error" (no configured remote
builders for the user's nix daemon). Verify via a fleet builder:

```bash
ssh -o BatchMode=yes builder@ashira.taila659a.ts.net \
  'nix build --accept-flake-config --no-link --print-out-paths \
   "github:shikanime/machines/<sha>#packages.x86_64-linux.llama-cpp"'
```

Docker-archive sanity: ustar magic at byte offset 257; manifest says
`architecture: amd64 / os: linux`.

## Verifying a ghcr publish (post-Release)

Anonymous tag listing gives `{"name":...,"tags":["latest"]}` only with the
anonymous-bearer trick; full verification needs a scoped token:

```bash
TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:shikanime-labs/machines/llama-cpp:pull" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -sL "https://ghcr.io/v2/shikanime-labs/machines/llama-cpp/manifests/latest" \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.oci.image.manifest.v1+json"
# config blob digest → GET /blobs/<digest> shows architecture/os/Entrypoint
```

dockerTools `buildLayeredImage` manifests report `architecture: null` at the
manifest level — read `architecture`/`os` from the CONFIG blob, not the
manifest.

## Go dev notes (wharf repo)

- moq mocks live in `cmd/wharf/builder_moq_test.go` (generated) — interface
  changes ripple into the mock's Func fields; test failures after interface
  edits usually point there.
- `go build ./...` from the repo root fails ("no Go files"); use
  `go build ./cmd/...`.
- Mid-run log tails: `gh run view --log` errors "still in progress"; use
  `gh api repos/<org>/<repo>/actions/jobs/<job-id>/logs` instead.
