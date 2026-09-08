# pnpm / TypeScript monorepo pitfalls (websites, fade, accounts lineage)

## devenv is unusable from a `git worktree`

No `.devenv` in the worktree — run installs from the main checkout with:

```bash
pnpm -C <worktree> install --ignore-scripts
```

`--ignore-scripts` is required when `better-sqlite3` (reyia) gyp-builds
against system node and dies; nothing at runtime needs postinstall scripts.

## tsc resolution through pnpm workspaces

`tsc --noEmit` from the app dir may take 30s+ resolving types through pnpm's
symlinked node_modules. Run it from the PACKAGE dir (e.g. `packages/darkroom/`)
— resolves in ~1s. Use per-package compilation for fast feedback when
extracting modules.

## Extracting a module to a standalone package (fade → packages/darkroom)

- `pnpm-workspace.yaml` must list the new package dir (`packages/*`).
- The package needs a unique `name` (e.g. `@shikanime-studio/darkroom`) and
  must be listed as a dependency of the consuming app.
- Subpath imports (`./demosaic`) require an `exports` map in the package's
  `package.json`; otherwise consumers deep-import and the boundary breaks.

## Bulk import rewriting across many files

`patch(mode='replace_all')` fails on import paths that do not end with `/`
and on mixed trailing segments (`../image-processing` vs
`../image-processing/parsers/exif`). Prefer sed (one pass):

```bash
find apps/fade/src \( -name "*.ts" -o -name "*.tsx" \) \
  -exec sed -i '' 's|\.\./image-processing/|@shikanime-studio/darkroom/|g' {} +
sed -i '' 's|from "\.\./image-processing"|from "@shikanime-studio/darkroom"|g' <files>
grep -r "image-processing" apps/fade/src/   # must be 0
```

## eslint vs treefmt in this repo family

CI = `pnpm/integration` (check→lint→build) PLUS a treefmt gate that runs
BEFORE them; treefmt's eslint formatter enforces dprint style (double quotes

- semicolons). Do NOT `eslint --fix` new files to antfu defaults — `nix fmt`
flips them back and CI fails. Author in dprint style, then scoped `nix fmt`.
Full reconciliation doctrine (stylistic:false config shape, formatter
degradation, fixed-point ship gate, astro check SQLITE_BUSY):
`references/css-quote-loop.md`.

## accounts IdP stack is ghstack-shaped but broken

PRs #306–#327 use `gh/shikanime/N/{base,head,orig}` refs, but `orig` does
not exist on the remote → `ghstack submit`/`checkout` fail ("poisoned
commit"). Stack new work as a plain PR with
`--base gh/shikanime/<tip#>/base`; GitHub retargets to main as lower PRs
land. Landing into a stack base with `gh pr merge --squash --admin` works.

## Old eslint-config bases fail lint on dprint-formatted code (verified #338)

Older stack bases branched before `stylistic: false` existed → `eslint .`
reports hundreds of style errors on dprint-formatted code. Fix: adopt the

## 336 config shape (see `references/css-quote-loop.md`); never reformat

source to antfu style. Note `pnpm install --no-frozen-lockfile` in an
old-base worktree can downgrade patch versions (eslint 9.39.4 vs 9.39.5)
with rule-behavior differences — diff the lockfile against the CI-passing
lineage before assuming the source is wrong.

### devenv task cache after lock bumps

`rm .devenv/state/tasks.db*` after lockfile changes — the cache is keyed on
the lockfile hash and a stale cache makes `pnpm install` skip needed deps.
