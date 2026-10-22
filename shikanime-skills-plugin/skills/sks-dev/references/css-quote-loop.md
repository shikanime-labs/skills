# treefmt vs antfu-eslint formatter war (websites repo, generalizable)

## Class

Any repo that runs BOTH `nix fmt` (treefmt, via devenv `enterShell`/git-hooks)
AND `@antfu/eslint-config` linting over the same files. The two tools disagree
on style, and CI enforces both in the order treefmt-then-lint.

## Verified symptom (2026-09-03, shikanime-studio/websites PR #332)

Every push flip-flopped a red gate:

| File class              | treefmt (prettier) writes      | eslint wants                     |
| ----------------------- | ------------------------------ | -------------------------------- |
| CSS (`global.css`)      | double quotes                  | `format/prettier`: single quotes |
| JSON (package/tsconfig) | preserves/reshuffles key order | `jsonc/sort-keys`: fixed order   |
| TS hex literals         | lowercases digits (`0x4d4d`)   | `unicorn/number-literal-case`: uppercase |

Local runs hide it because locally you can run `eslint --fix` LAST. CI cannot:
`javascript / Build (Workspace)` (shikanime-labs/actions `pnpm/integration`,
stages check→lint→build) enters the devenv shell FIRST — `devenv:treefmt:run`
reformats the checkout — and only then runs `pnpm -r run lint`. eslint-last is
unachievable in CI.

## Landed resolution (PR #332, commit 7f874236)

treefmt OWNS formatting; eslint yields on every contested rule. In each
`apps/*/eslint.config.ts`:

```ts
export default antfu(
  {
    astro: true,
    formatters: true,
    stylistic: false,        // kills antfu stylistic (style/quotes, style/semi,
                             // style/member-delimiter-style) everywhere
  },
  {
    files: ['**/*.css', '**/*.json', '**/*.jsonc'],
    rules: {
      'format/prettier': 'off',   // formatter plugin (CSS/JSON prettier) off
      'jsonc/sort-keys': 'off',   // treefmt preserves its own key order
    },
  },
  // fade only: hex literals (EXIF tag ids 0x829a...) — prettier lowercases,
  // unicorn wants uppercase digits → scoped off
  {
    files: ['**/*.ts', '**/*.tsx'],
    rules: {
      'unicorn/number-literal-case': 'off',
    },
  },
  ...
);
```

## Ship gate — push must be a fixed point of BOTH tools

Run the CI sequence locally until stable, twice:

```bash
nix fmt                          # treefmt pass (rewrites to its canon)
pnpm -r --no-bail run lint       # must exit 0 NOW, post-fmt
# repeat `nix fmt && pnpm -r --no-bail run lint` — exit 0 twice in a row
# means fmt no longer changes anything lint would reject
pnpm -r --no-bail run check && pnpm -r --no-bail run build
```

Only then `jj describe` + push. A single green lint after an eslint --fix run
is NOT sufficient — that state still has eslint-last ordering baked in.

## Debugging pattern for the next contested rule

1. CI log: `gh run view --job <id> --log | grep -E ': Failed| error '`
   → identify rule + file.
2. Reproduce locally in CI ORDER: `nix fmt` then `pnpm --dir <app> exec eslint
   <file>` — a local eslint-first repro proves nothing.
3. Ask: is this rule enforcing STYLE a formatter also controls? If yes → rule
   off in eslint (scoped `files:` block), never fight the formatter.
4. Whole-tree `nix fmt` churns unrelated files → restore non-task files from
   `@-` (`jj restore --from @- --to @ <paths>`) before every push; never commit
   formatter churn on files outside the change.

## Formatter DEGRADATION is a different failure class — exclude, never commit

Two contested-rule classes exist. Class 1 (above): both tools are right, they
disagree on style → eslint yields. Class 2: the formatter is WRONG for the
file — it silently destroys load-bearing structure. Never resolve class 2 by
committing the formatter's output:

- **GitHub workflow YAML**: treefmt's YAML formatter strips the deliberate
  `%YAML 1.1` directive (present so GitHub's YAML 1.2 parser reads `on:` as a
  string key, not a boolean `True:`) and reflows `${{ }}` expressions across
  lines. Verified 2026-09-04 on websites PR #333: `nix fmt` rewrote all 8
  files under `.github/workflows/` on first run — main's committed state was
  intentionally NOT treefmt-canonical.
- **Generated lockfiles** (`pnpm-lock.yaml`): prettier reflows them on every
  run; the package manager owns the format.

Fix: treefmt global excludes in `flake.nix`
(`devenv.shells.default.treefmt.settings.global.excludes`):

```nix
settings.global.excludes = [
  "*.gen.ts"
  ".github/workflows/*"
  "pnpm-lock.yaml"
  # ... keep existing entries
];
```

Diagnose class 2 before excluding: diff the formatter's rewrite and ask what
the changed lines DO. A stripped `%YAML 1.1` or reflowed `${{ }}` across a
line break is structural damage, not style. Then restore the files from `@-`
and add the exclusion — the exclusion IS the fix, the restore just undoes the
damage the run already wrote to disk.

### Upgraded ship gate: `nix fmt` idempotency

After landing the excludes, the fixed-point check simplifies to: run `nix
fmt` on a clean tree → it must report **0 changed files**. If it changes
anything you did not author, either a class-2 exclusion is missing or a
formatter update changed canon — investigate, never blind-commit.

## `astro check` parallel collision — false check failure (websites)

`pnpm -r run check` across the Astro apps (links/reiya/www) starts three
`astro check` processes simultaneously; each spins its own workerd/miniflare
and they collide on the SQLite session DB:

```text
workerd/util/sqlite.c++:852: failed: SQLite failed; database is locked:
SQLITE_BUSY (extended: SQLITE_BUSY_RECOVERY)
```

This is LOCAL-ONLY resource contention, not a code regression (CI ran the
same recursive check green). When reproducing CI locally, serialize:

```bash
pnpm -r --workspace-concurrency=1 run check
```

Triage before debugging: failure stack names workerd/miniflare → serialize
and rerun; failure is TS diagnostics → real regression, fix it.
