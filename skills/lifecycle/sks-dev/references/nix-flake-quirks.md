# Nix flake quirks in shikanime repos (machines, nix-containers, manifests)

Verified against `shikanime-labs/machines` (flake-parts + devenv + sops-nix)
and `shikanime-labs/manifests` (devenv flake module, no NixOS system build).

## devenv `env` template escaping — the 1-backslash rule

`devenv.shells.default.env.X = "\${{ secrets.Y }}";` must contain EXACTLY ONE
backslash byte before `${{`. Two backslash bytes is a Nix syntax error:

```text
error: syntax error, unexpected '}', expecting '.' or '='
       at modules/flake/devenv.nix:24:59:
           24|         env.SOPS_AGE_KEY = "\\${{ secrets.CATBOX_SOPS_KEY }}";
```

- 1 byte `\` + `${{` → valid; interpolates the devenv secret into the string.
- 2 bytes `\\` + `${{` → Nix sees `\\` as an escaped backslash, then `{{`
  outside an interpolation → syntax error. This breaks EVERY flake eval, not
  just the one host.
- Verify byte count, not eyeballs — editor/terminal renders can lie:

  ```bash
  sed -n '24p' modules/flake/devenv.nix | od -c   # expect \  $  {  {  (one 0x5c)
  nix-instantiate --eval -E '"\${{ secrets.X }}"'   # OK
  nix-instantiate --eval -E '"\\${{ secrets.X }}"'  # syntax error
  ```

- Pattern-match against sibling lines: `CACHIX_AUTH_TOKEN` / `GH_TOKEN`
  entries in the same file are the known-good shape.

## Flake eval verification

- The whole flake must eval before any per-host work: a single syntax error
  anywhere (devenv included) fails every attribute. `nix flake show` trips on
  devShells first — use `--all-systems` to skip darwin-only errors, or eval
  the target attr directly.
- Target a specific output, e.g. catbox containerdisk:

  ```bash
  nix eval .#packages.x86_64-linux.catbox.name   # -> "docker-image-catbox.tar.gz"
  # full 253-derivation eval; exit 0 = clean
  nix build .#packages.x86_64-linux.catbox --dry-run
  ```

- `nixosConfigurations` does NOT include every host — catbox is exposed only
  under `packages.<system>.catbox` (`modules/flake/nixos.nix`). Eval'ing
  `.nixosConfigurations.catbox` fails with "attribute 'catbox' missing";
  don't chase that path.
- SOPS-protected flakes need the age key in env before eval:

  ```bash
  export SOPS_AGE_KEY=$(grep AGE-SECRET-KEY /tmp/catbox-age-key)
  ```

  Without it, sops-nix configs error during eval.

## Building / verifying a devenv shell (no NixOS build)

When the task is ONLY to confirm a package lands in the devenv shell
(`shells.default.packages`), you do not build the whole system — you build the
devShell output and prove the binary is wired in.

- Build the shell derivation (already-cached closure → fast):

  ```bash
  nix build ".#devShells.<system>.default" --no-link --impure
  ```

- **`--impure` is MANDATORY on macOS / outside a devenv shell.** The devenv
  flake module asserts `config.devenv.root != ""`, which it reads from
  `builtins.getEnv "PWD"`. The Nix sandbox strips `PWD` under a pure build, so
  the assertion fails with `devenv was not able to determine the current
  directory` even though the flake is correct. `--impure` lets the env reach
  eval and the build succeeds. Setting `export PWD=...` / `export
  DEVENV_ROOT=...` alone does NOT fix it — the sandbox still drops them;
  `--impure` is the actual switch.
- The built `devenv-shell` output is a single ~32K activation script (NOT a
  directory, and `$OUT/bin/flux` will report "Not a directory" — that is
  expected, not a missing binary). To prove a package is present, grep the
  activation script for the derivation's store path and exec the real binary:

  ```bash
  OUT=$(nix build ".#devShells.aarch64-darwin.default" --print-out-paths \
    --impure 2>/dev/null | tail -1)
  P=$(grep -oE "/nix/store/[a-z0-9]+-fluxcd-[0-9.]+" "$OUT" | sort -u | head -1)
  "$P/bin/flux" version   # -> flux: v2.9.4
  ```

- **Do NOT `nix eval` a devenv devShell.** `nix eval` trips on devenv's
  `optionalValue`/assertion plumbing and returns a misleading error; build
  instead. This matches the dev-workflow rule: devenv packages are verified by
  `nix build`, not `nix eval`.
- **YAGNI check first:** before editing `flake.nix` to "add" a package, grep the
  existing `shells.default.packages` list — the requested tool is often already
  there (e.g. `pkgs.fluxcd` was already present at `flake.nix:187`); a second
  line is a duplicate, not a fix.

## Verifying a shared-module change against real host configs (no full build)

When you edit a shared NixOS module (e.g. `modules/nixos/profiles/ai.nix`)
and must prove the rendered config is correct per host, eval the host's
`config` attr instead of building the whole system:

```bash
SYS=x86_64-linux
nix eval --system $SYS .#nixosConfigurations.<host>.config.<attr>
```

- **Pin `--system` explicitly.** On a darwin host the flake resolves to
  `aarch64-darwin` and `nixosConfigurations` errors with "does not provide
  attribute 'packages.aarch64-darwin.nixosConfigurations.<host>...'". Force
  the Linux system even when only inspecting a NixOS config.
- **`nix eval --apply` has ONLY `builtins` in scope** — `lib` is not
  available, so `lib.strings.splitString` raises "unknown variable 'lib'".
  Extract sub-values by grepping the raw output instead, or pre-compute in the
  attr itself. Verified pattern for a newline-separated sops template line
  (the attr's `\n` is a literal two-char escape in the Nix string):

  ```bash
  nix eval --system $SYS \
    '.#nixosConfigurations.<host>.config' \
    --apply 'c: c.sops.templates."hermes-agent-a2a-env".content' \
    | grep 'A2A_TRUSTED_PEERS'
  ```

- Attrset keys from a rendered set (peer list in the A2A agent config):

  ```bash
  nix eval --system $SYS \
    '.#nixosConfigurations.<host>.config.services.hermes-agent.settings' \
    --apply 's: s.a2a_agents' \
    | grep -oE '[a-z]+ = \{ auth = \{ token' | sed -E 's/ =.*//' | tr '\n' ' '
  ```

### Worked example: directional (unidirectional) A2A boundary

To prove a one-way agent mesh, eval a CLUSTER host and a WORKSTATION host and
compare (verified on `machines`: `ashira` = cluster, `nixtar` = workstation):

- outbound `a2a_agents` names must be identical (cluster-only) for both classes.
- `A2A_TRUSTED_PEERS` must be non-empty for the cluster host, empty for the
  workstation.
- Pitfall caught in-session: if a cluster host still lists a workstation in
  `a2a_agents`, the boundary is open at the OUTBOUND layer even when the
  inbound allow-list is correct. A directional mesh must close BOTH layers —
  outbound peer list AND inbound allow-list must be asymmetric, or the reverse
  path stays reachable.

## `nix fmt` check mode

`nix fmt` wraps treefmt. `nix fmt -- --check` is rejected ("unknown flag:
--check"). Use `nix fmt -- --ci` (fail-on-change, no-cache) as the check, or
`nix fmt <path>` to format a single file. Scope the format to the edited
module before a full-tree run.

## Flattening module directory structure — relative path adjustment

When collapsing `modules/<type>/<name>/{default,nixos,home}.nix` into a single
flat `modules/<type>/<name>.nix`, every relative import path inside the file
must be adjusted: one fewer `../` since the file moved up one directory level.

**Path adjustment rules by module type:**

- NixOS profile modules (`modules/profiles/<name>.nix`): `../../` → `../`
  (e.g. `../../../secrets` → `../../secrets`, `../../../pkgs` → `../pkgs`)
- Home-manager modules (`modules/profiles/<name>-home.nix`): same as profiles
  above — `../../../` → `../../`
- NixOS user modules (`modules/users/<name>.nix`): `../../profiles/` → `../profiles/`
  and `../../apps/` → `../apps/` (one level up to `modules/`)
- Darwin user modules (`modules/darwin/users/<name>.nix`): `../../` → `../../`
  (stays at 2 levels — darwin/users is nested one deeper than nixos/users)

**Verification shortcut:** `nix-instantiate --parse` on every file catches syntax
errors fast without full evaluation. Parse-check ALL module files after a
flattening refactor — a single un-fixed path produces a cryptic "path does not
exist" error that's hard to trace back.

**Pre-existing sops assertion:** `nix eval` on host configs may fail at
`sops.templates` with `assertion = !(cfg.owner != null && cfg.uid != 0)` /
`cannot coerce null to a string` — this is a pre-existing sops-nix version
mismatch, NOT caused by flattening. Confirmed by stashing and testing on clean
main. The assertion index may shift (e.g. 101 → 117) as more modules load
successfully, but the error itself is unrelated to module restructuring.

## devenv tasks: cache invalidation + workspace compatibility

- **Stale task graph after lockfile bumps.** devenv persists the resolved task
  graph in `.devenv/state/tasks.db`. After a `nix flake lock` bump removes or
  renames tasks (e.g. devlib dropping the ghstack hook task), `devenv test`
  keeps RE-RUNNING the deleted task from the stale cache and fails on it even
  though the flake no longer defines it. Invalidate first:

  ```bash
  rm -f .devenv/state/tasks.db .devenv/state/tasks.db-shm .devenv/state/tasks.db-wal
  ```

  Verified 2026-09-04 (websites #335): `devlib:ghstack:hooks:install` kept
  failing post-bump until the cache was cleared; then 6/6 tasks green.
- **Run devenv/nix from the MAIN checkout, never a jj workspace.** A
  `jj workspace add` sibling has no `.git`, and devenv's nix evaluation
  requires one: `nix flake lock`/`nix flake check` fail with `opening Git
  repository ... could not find repository (libgit2 error code = 6)`, and
  treefmt inside the workspace degrades to minutes-long runs (verified: 574s
  vs 2s from the main checkout). The isolation workspace is for jj
  bookkeeping; all devenv-native verification (`devenv test`, `nix build`,
  `nix fmt`) runs from the original checkout. Transfer the change first:
  push the branch from the workspace (`jj git push -b <branch>`), then in
  the main checkout `jj git fetch && jj new <branch>@origin` so verification
  runs against the change; return with `jj new main@origin` afterwards.
- **flake.lock rebase conflicts:** after `jj rebase -d main@origin -r @` marks
  flake.lock conflicted, do NOT hand-resolve conflict markers. Instead:
  `jj restore --from main@origin --to @ flake.lock` (take main's version),
  then re-run `nix flake lock --update-input <input>` — nix recomputes the
  correct lock content cleanly. Hand-editing the 3-way markers is slower and
  error-prone.

## Containerdisk module notes (machines)

- `modules/nixos/virtualisation/containerdisk.nix` wraps
  `${modulesPath}/virtualisation/disk-image.nix`, which already provides
  `boot.growPartition = true` — do not re-add a hand-rolled growfs service.
- Module options are the extension surface (`containerdisk.kernelModules`,
  `extraKernelModules`, `extraPackages`, `usb.enable`); keep per-host VM
  config in the module, not in `hosts/<name>/configuration.nix`.
- `nixos-rebuild` / `nix eval` on the module: `nix-instantiate --parse` +
  `treefmt --stdin` on the module file, then the dry-run above.
