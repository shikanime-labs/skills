# cloud-pi-native-core — shikanime-labs Alchemy v2 extraction library

Load when working in `shikanime-labs/cloud-pi-native-core` (NOT the
cloud-pi-native/console repo — different org, different rules).

## Identity and conventions

- Checkout: `~/Source/Repos/github.com/shikanime-labs/cloud-pi-native-core`.
  Always edit in jj workspaces (`.domain`, `.topology`, `.renovate`, ...),
  never the cloned checkout (repo AGENTS.md mandates this).
- Artifact language: English. Commit envelope: plain capitalized title
  (no conventional-commit prefix), `Design:`/`Related:`/`Closes #` body
  labels, `Co-authored-by: Automata <automata@shikanime.studio>` plus
  `Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>`
  (gitlint CC1 rejects its absence).
- Resource type strings: `Cpn.<Service>.<Resource>`, globally unique.
- Reconciler convention: observe → ensure → sync; one body converges from
  any starting point. "Trust observed state, never olds" concerns
  convergence, not prop-mutation guards — rejecting a slug change on
  `olds !== undefined` is the correct pattern when child names derive
  from the prop (delete only knows the latest slug).
- Alchemy version: `2.0.0-beta.81` (Effect-based). `reconcile` receives
  `{ id, fqn, instanceId, news, olds, output, session, bindings }`;
  `olds` is `Props<Res> | undefined`.
- Branch naming ruleset requires `^(main|(feat|fix|chore|docs|refactor|test|ci|build|perf|renovate)/[a-z0-9][a-z0-9._/-]*|release-x.y.z)$`.

## Gates

- `pnpm build` (tsc), `pnpm test` (vitest), `pnpm format` = `biome check
  --write .` — **WHOLE-TREE rewrite**: `pnpm format` rewrites ~60+
  unrelated files (the css-quote-loop failure class). NEVER run it bare.
  Scope biome to touched files:
  `./node_modules/.bin/biome check src/composite/zone.ts docs/x.md`.
  If a polluted tree was already committed/bookmarked: `jj restore --from
  <clean-old-head> --to @` reverts EVERYTHING including your own fixes —
  re-apply the fixes afterward and re-run gates before re-pushing.

## Renovate

- The org-standard `postUpgradeTasks` shape (from devlib/identities):
  `allowedCommands: ["nix fmt"], commands: ["nix fmt"], executionMode:
  "branch", fileFilters: ["**/*.nix"], installTools: { "nix": {} }`.
  `postUpgradeTasks.nixFmt` is NOT a valid option — it freezes all
  Renovate PRs repo-wide (observed on 2026-10-07, fixed in PR 18).

## Board / lifecycle

- Issues carry `- [ ]` ledgers; verify each item with `gh api` evidence
  before closing (issue #3 closed with rulesets/tag/lockfiles evidence).
- Landing: `gh pr merge --squash --admin` (Landing protections ruleset
  blocks self-approval); stacks land base-first; restack children with
  `jj rebase -r <child-change-id> -d <new-parent-head>` + sideways push.
