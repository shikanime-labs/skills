# cpn-dev-workflow — Pitfalls

Lazily loaded from `SKILL.md`.

- **jj / git snapshot desync is the #1 time-sink.** After any raw `git` write
  (`git apply`, `git checkout main -- <file>`) the working tree changes but jj's
  snapshot lags; `jj squash` lies ("Nothing changed") and `jj diff` shows
  nothing until you `touch` the file. Verify every jj edit with
  `jj diff -r <rev>` (grep a known token), never the squash message, and push
  with `jj git push --bookmark <name> --remote origin`. Full recovery:
  `references/jj-snapshot-pitfalls.md`.
- `apps/server` is frozen: contributions touching it are rejected, including bug
  fixes.
- **Unsalted SHA-256 token hash REQUIRED**:
  `apps/server-nestjs/src/utils/crypto.ts` (or `crypto.utils.ts`) hashes
  admin/PAT tokens with `createHash('sha256')` — no salt, no KDF. The Fastify
  `apps/server` stores/verifies the identical unsalted `sha256`
  (`apps/server/src/resources/admin-token/business.ts`,
  `apps/server/src/resources/user/tokens/business.ts`). A CodeQL
  `js/insufficient-password-hash` alert here is EXPECTED — do NOT "fix" with
  bcrypt/argon2/scrypt (invalidates every shared token). Leave the alert unless
  the user explicitly requests a coordinated two-server migration.
- **GitHub bot comments stale vs HEAD**: CodeQL / `github-code-quality[bot]`
  anchor to the commit they ran on. Re-read the file at HEAD before acting; the
  flagged import/function may already be gone.
- Dependency changes need explicit Socle approval, even for bug fixes.
- Console commits in English; doc-only changes still follow scope/review rules.
- ArgoCD redeploy needs an image tag change; manifest-only changes may not
  rollout.
- **jj `split` launches `hx`** (hardcoded `ui.editor="hx"`; ignores `JJEDITOR`).
  Bypass: `jj split --config ui.editor=cat <paths>`. Inspect:
  `jj config list --include-defaults | grep editor`. For precise file-splitting,
  prefer the `jj new main` + `git apply` + `touch` + `squash` sequence below.
- **Move a PR bookmark**: `jj bookmark move <name> -t <rev>` (e.g.
  `jj bookmark move pr/2407 -t @`). Push: `jj git push --bookmark <name>`
  (repeat `--bookmark` per bookmark; NO `--allow-new` flag — it errors).
- **Clean PR line off a polluted WC**: `jj new <bookmark>` builds a fresh empty
  WC atop that bookmark, isolating your change from unrelated edits (e.g.
  doc-only changes in `@`).
- **"Push a patch on a branch" → split unrelated edits FIRST, prove minimal
  before pushing.** The jj-backed tree often holds multiple unrelated in-flight
  changes; rebuilding a fix via `git apply` of a saved patch can pollute the
  commit with unrelated WIP (a 2-file fix shipped as 7 files to PR #2526). Safe
  sequence (rebuild from clean `main`, verify file set):
  `references/push-patch-procedure.md`.
- **Push 403 = wrong gh account**: git's HTTPS helper resolves the ACTIVE gh
  account, not `GH_ACCOUNT` (that var only affects the gh CLI). If `jj git push`
  is denied as e.g. `yorha-automata` but the repo is `shikanime`, run
  `gh auth switch --user shikanime` first. `GH_ACCOUNT=shikanime jj git push`
  STILL uses the active token — don't bother.
- **Content vs tracking conflict differ.** A 2-sided `<<<<<<<` in a tracked file
  is a _content_ conflict — resolve in the WC (`jj status` clears it). A
  _push/remote bookmark_ conflict (`jj bookmark list` shows
  `<name> (conflicted)`, `@git`/`@origin` behind N commits) is a **tracking
  conflict on another branch** — do NOT `jj bookmark set` it. Confirm the
  conflicted bookmark's commit is in `@` ancestry
  (`jj log -r "::@" | grep <bookmark>`) before touching; if not, surface and ask
  (rebase onto origin, or force).
- **`jj git push --deleted` sweeps ALL locally-deleted bookmarks.** A single
  `--deleted` push deletes every locally-deleted bookmark, not just the intended
  one. To drop ONE remote bookmark: `jj bookmark delete <name>` then
  `jj git push --bookmark <name> --remote origin`, unless matching remote↔local
  is the explicit intent.
- **GitLab 409 "Username has already been taken" is NORMAL — don't build a
  handler.** GitLab auto-provisions via OIDC/SSO (Keycloak); same local-part
  distinct emails collide, but the console must NOT create a second account. Fix
  the root (dedupe by external identity / resolve existing user); leave 409
  propagation unchanged. If the user says "X is normal, ignore it," drop the
  handling commit entirely (close PR, abandon commit, delete remote bookmark)
  rather than ship a no-op guard.
