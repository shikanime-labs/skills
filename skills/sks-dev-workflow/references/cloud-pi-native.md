# cloud-pi-native console — repo facts, French rules, deep recipes

Load when working in the cloud-pi-native/console repository.

## Org identity

- Default repo: `cloud-pi-native/console`. Artifact language (issues,
  discussions, PRs) is **French**; commits in English.
- Push to `origin` only; PRs with `--head cloud-pi-native:<branch>`
  (origin-only; the legacy fork-head guidance is retired).
- Commit author identity:
  `William Phetsinorath <william.phetsinorath-open@interieur.gouv.fr>`,
  SSH-signed; attribution trailer
  `Co-authored-by: Automata <automata@shikanime.studio>` always (see
  `sks-commit` → `references/cloud-pi-native.md`).
- Husky `pre-push` runs `vitest`: unit tests must pass before `jj git push`.
- PR↔issue linkage: `Refs #N` by default; never open a PR without an issue
  behind it. Linkage is many-to-many; after the final PR's merge, verify task
  N on N and close deliberately (`gh issue close <N> -c "<evidence>"`).
- Lifecycle: discussion → issue (French problem statement + `Définition du
  fini` ledger) → issue comments → PR. Discussion RFC first when the problem
  is unconverged.

## Checkout et layout

- Checkout local : `~/Source/Repos/github.com/cloud-pi-native` ; dépôt
  `console` ; commandes lancées depuis `console/`.
- `console/README.md` — overview, architecture, ports, run modes.
- `console/CONTRIBUTING.md` — scope, backend target, quality gates.
- `console/package.json` — workspace scripts : lint, test, build, docker.
- `console/.github/PULL_REQUEST_TEMPLATE.md` — sections de PR requises.
- `console/apps/server-nestjs` — backend cible actuel ; `console/apps/server`
  — historique, **ne pas modifier** (frozen ; contributions rejetées, y
  compris bug fixes).
- `console/misc/plugins.md` — cycle de vie des plugins ;
  `console/playwright/README.md` — e2e Playwright.

## Toolchain et commandes

- Docker >= 27 (compose >= 2.35, buildx), Node.js >= 24, pnpm >= 10.
- Install/build/generate : `pnpm install`, `pnpm build`,
  `pnpm --filter @cpn-console/server-nestjs run db:generate`.
- Lancer : local+remote → `pnpm run dev` puis
  `pnpm --filter @cpn-console/server-nestjs run dev` +
  `pnpm --filter @cpn-console/client run dev` ; full containerisé →
  `pnpm run docker:dev` ; intégration → `pnpm run docker:integ` ou
  `pnpm run integ`.
- Checks avant soumission : `pnpm lint`, `pnpm test`, `pnpm playwright:test`
  si un parcours est touché.

## Deep recipes (load on demand, cloud-pi-native/console only)

- **Gates / module consistency / vitest+e2e+Playwright rules** — the issue is
  the gates file, CI is the runnable check, required checks + draft PRs are
  the wall, PR body restates N-of-N from live measurements; 3-file module
  split, all Prisma calls through `<module>-queries.utils.ts`, namespaced
  config injection, `@cpn-console/hooks` flags `'enabled'`/`'disabled'`,
  `mockDeep` + faker test factories, no describe-scope calls, e2e-spec for
  systemic reconciler changes (`describe.runIf(process.env.E2E)`),
  Playwright for user-facing+systemic (socle cahier fallback at
  `../documentation-interne-socle/Tests Fonctionnels/`).
- **Migration parity (apps/server → apps/server-nestjs)** — before approving
  cutover, grep emitted `eventEmitter.emitAsync('<entity>.<verb>')` vs
  `@OnEvent` consumers vs legacy `hook.<entity>` calls: an event with no
  `@OnEvent` → `capturePluginResult` bridge silently drops Keycloak/GitLab
  sync at cutover → REQUEST CHANGES. Also: event-in-transaction ordering is
  parity-preserving; dead imports added to `main.module.ts` are scaffolding;
  a live-vs-at-cutover severity must be stated.
- **jj/git snapshot desync** — raw git writes leave jj's snapshot stale:
  `touch` changed files to force re-snapshot; never trust `jj squash`'s
  "Nothing changed."; verify with `jj diff -r @`; recovery sequence +
  two-fixes-one-tree splitting in the full recipe (`git apply` → `touch` →
  `jj squash --into @ --config ui.editor=cat`).
- **Push a patch on a branch** — split unrelated edits FIRST and prove the
  split minimal before pushing: save WIP (`jj diff > /tmp/wip.patch`),
  `jj restore --from main --to @`, rebuild the fix by hand on `jj new main`,
  verify `jj diff -r <commit> --stat` is exactly the intended files, re-point
  the bookmark (`--allow-backwards` if ancestor), push origin, restore WIP.
  A 2-file fix once shipped as 7 files when the saved patch was applied
  blindly.

## Pitfalls (console-specific, load on demand)

- `apps/server` is frozen: contributions rejected, including bug fixes.
- **Unsalted SHA-256 token hash is REQUIRED**
  (`apps/server-nestjs/src/utils/crypto.ts` mirrors legacy `apps/server`) —
  a CodeQL `js/insufficient-password-hash` alert here is EXPECTED; do NOT
  migrate to bcrypt/argon2/scrypt (invalidates every shared token) without a
  coordinated two-server migration.
- GitHub bot comments (CodeQL / `github-code-quality[bot]`) anchor to the
  commit they ran on — re-read the file at HEAD before acting.
- `Closes #N`/`Fixes #N` auto-close fires before the `Définition du fini` is
  verified — close deliberately after N-sur-N.
- ArgoCD redeploy needs an image tag change; manifest-only changes may not
  rollout.
- `jj split` launches `hx` (hardcoded `ui.editor="hx"`); bypass:
  `jj split --config ui.editor=cat <paths>`.
- Move a PR bookmark: `jj bookmark move <name> -t <rev>`; push with
  `jj git push --bookmark <name>` (repeat `--bookmark` per bookmark; no
  `--allow-new` flag — it errors).
- Clean PR line off a polluted WC: `jj new <bookmark>` isolates your change.
- Content vs tracking conflict: a 2-sided `<<<<<<<` resolves in the WC; a
  `<name> (conflicted)` bookmark is a remote-tracking conflict on another
  branch — do NOT `jj bookmark set` it; confirm ancestry first
  (`jj log -r "::@" | grep <bookmark>`).
- `jj git push --deleted` sweeps ALL locally-deleted bookmarks; drop one via
  `jj bookmark delete <name>` + targeted push.
- GitLab 409 "Username has already been taken" is NORMAL (OIDC auto-provision
  collision) — don't build a handler; if the user says "X is normal, ignore
  it", drop the handling commit entirely rather than ship a no-op guard.
- Force-push to an EXISTING PR branch: `jj git push` lies when `@origin`
  tracking is stale; from the `console` workspace run
  `git push --force https://github.com/cloud-pi-native/console <SHA>:refs/heads/<branch>`
  (retry once on send-pack disconnect; other workspaces lack the loose
  object).
- `jj log -T 'commit_id'` returns graph glyphs — strip:
  `SHA=$(jj log -r <rev> -T commit_id | tr -d '○│~ ' | head -1)`; never pass
  `@` (empty WC) as the ref.
- No `as` TypeScript cast in NEW nestjs code (hard constraint):
  `as never`/`as any`/`as X` prohibited; prefer typing or
  `mockResolvedValueOnce` sequencing. Parameter annotations are not casts.
- Shared-file collision across a migration wave: defer, don't edit blindly —
  flag "shared with #X/#Y — coordinate at merge" in the PR body; only fix
  files unique to your PR.
- Trust jj/gh ground truth, not subagent self-reports — verify with
  `jj bookmark list` / `gh pr view <N> --json headRefOid` / `jj diff -r <rev>`
  before reporting done.
- Push 403 = wrong gh account: git's HTTPS helper uses the ACTIVE gh account
  (`gh auth switch --user <user>` first); `GH_ACCOUNT=` does not affect it.
