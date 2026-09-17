# HTTPRoute hostname injection

Programmatic hostname list generation for `patch-httproute.yaml` overlays.
Proved by PR #2065 rebase on `main` (2026-09-01).

## The failure mode

Two separate corruption classes came from the same script: using a global
regex replacement over all `patch-httproute.yaml` files.

1. **Duplicate / misplaced tailnet hostnames** — the regex matched the first
   `- <host>` line in a file, even when that file already contained multiple
   hosts from a previous patch. Result: duplicate `*.taila659a.ts.net` entries
   and tailnet hosts appearing before their i.shikanime.studio counterparts.

2. **Broken YAML indentation** — the substitution reused the matched line's
   indentation instead of emitting `    - <host>` under `hostnames:`. Result:
   `mapping values are not allowed in this context` from `nix fmt` / oxfmt.

3. **Repo-wide second-pass corruption** — after manually fixing a conflict
   file (`configs/flux-operator/overlays/nishir-tailnet/patch-httproute.yaml`),
   rerunning the global script rewrote the fixed file back into a broken state.

## Correct approach

- **Generate from `origin/main:<path>`**, not from the already-patched tree.
  The base hostname list is the source of truth; everything else derives.
- **Track `spec` / `hostnames` state explicitly** instead of using a global
  regex. The first `hostnames:` block after `spec:` is the target; ignore
  later blocks (e.g. `matrix-discord-media` in `synapse`).
- **Emit every hostname with explicit indentation**:
  `\n`.join(f"    - {h}" for h in hostnames)
- **Run `nix fmt` immediately after generation** — it catches indentation bugs
  before they enter the index.
- **Never rerun a bulk injection script on a tree that is already mid-conflict**.
  Conflict files must be resolved in place; a second script pass clobbers manual fixes.

## Verification

```bash
# After generation, confirm every patch-httproute has expected hosts
rg "\.taila659a\.ts\.net" apps/*/overlays/nishir/patch-httproute.yaml infrastructure/*/overlays/nishir/patch-httproute.yaml
# Each file should list exactly one tailnet host per i.shikanime.studio host
```

## Related skill guidance

- Multi-doc patch files without `target:`:
  see `kustomize-overlay-authoring` skill, "Gotcha: `target:` is forbidden on a multi-doc patch file".
- `nix fmt` after programmatic YAML generation: same skill, "CI treefmt gate".
