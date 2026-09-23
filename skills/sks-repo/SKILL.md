---
name: sks-repo
description:
  "Use when creating a new shikanime org repo: apply the 5-ruleset protection
  template, bootstrap the devlib devenv scaffold, and tag v0.1.0."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - repo-bootstrap
      - rulesets
      - devlib
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-dev-workflow
      - github-workflow-generation
platforms:
  - linux
  - macos
---

# Repo Bootstrap

Create a new shikanime org repo end to end: GitHub repo with the standard
5-ruleset protection template, devlib-based devenv scaffold, generated CI, and
an initial semver tag. Distilled from the live bootstrap of
`shikanime-labs/dashboards` (empty repo to merged PR).

## When to Use

- "Create a repo in the org" / "bootstrap a new repo with rulesets."
- An org repo exists but is empty and needs the standard scaffold.

## Prerequisites (probe first, report blockers)

- `gh api user --jq .login` — org-member account.
- `gh api repos/<org>/<repo> --jq .permissions.admin` — must be `true`
  (ruleset create/delete and ref writes need it).
- jj signing configured (`jj config get signing.backend` → `ssh`); the Main
  protections ruleset enforces `required_signatures`.
- The repo may already exist (possibly empty). Check
  `gh api repos/<org>/<repo> --jq .size` — `0` means empty.

## Procedure

1. **Apply the 5-ruleset template.** The canonical payloads live on any
   already-protected repo (e.g. `shikanime-labs/skills`). Fetch each ruleset
   by id (the list endpoint OMITS `rules` — always fetch
   `repos/<org>/<repo>/rulesets/<id>`), strip server fields (`id`, `node_id`,
   `source`, `source_type`, timestamps, `_links`,
   `current_user_can_bypass`), and POST to the target. The five, in creation
   order:

   - `Main branch protections` (branch, `refs/heads/main`):
     `required_linear_history` + `required_signatures`.
   - `Landing protections` (branch, `refs/heads/main`): `pull_request` with
     `require_code_owner_review`, `require_last_push_approval`,
     `require_extra_approval_for_unattributed_changes`, thread resolution,
     squash/rebase only, 0 required approvals.
   - `Enforce branch naming` (branch, `~ALL` minus main/master/release-*):
     `^(main|(feat|fix|chore|docs|refactor|test|ci|build|perf|renovate)/[a-z0-9][a-z0-9._/-]*|release-[0-9]+\.[0-9]+)$`.
     The regex is long; fetch the exact pattern from the template repo
     rather than retyping it.
   - `Enforce tag naming` (tag, `~ALL`): `^v[0-9]+\.[0-9]+\.[0-9]+$`.
   - `Copilot review for default branch` (branch, `~DEFAULT_BRANCH`):
     `deletion` + `non_fast_forward` + `copilot_code_review`.

   Verify by re-fetching each id and byte-comparing
   `enforcement`/`conditions`/`rules`/`bypass_actors` against the template.

2. **Scaffold the repo content.** Copy from the most minimal devlib consumer
   (e.g. `shikanime-labs/colemak`): `flake.nix` (devlib inputs, flake-parts,
   `devenv.shells.default` importing `devlib.devenvModules.git`, `.nix`,
   `.shell`, `.shikanime-studio`), `.envrc` (`use flake .`), plus org-standard
   `SECURITY.md` and `CODE_OF_CONDUCT.md` (hand-authored, NOT generated).

3. **Add the devenv.root fix.** devlib's flake module sets
   `devenv.modules = [ ... ]`, which REPLACES devenv's default module list and
   drops the module that reads the `devenv-root` input. Compensate in-shell:

   ```nix
   devenv.shells.default = {
     devenv.root = builtins.getEnv "PWD";
     imports = [ ... ];
   };
   ```

   `toString ./.` is wrong — it resolves to the read-only /nix store copy and
   devenv then fails writing `.devenv/`. `getEnv "PWD"` requires impure flake
   evaluation; keep the colemak-style `.envrc` (`use flake .
   --accept-flake-config --no-pure-eval`) so `PWD` reaches the evaluator
   under direnv.

4. **Stage the scaffold, then activate direnv and generate.** Track all
   scaffold files BEFORE `direnv allow` — direnv evaluates the flake on
   activation and nix evaluates the git tree, so an untracked `flake.nix` is
   invisible (error: "not tracked by Git"). In a jj colocated repo
   `jj file track <paths>` is the staging equivalent; in a plain git clone use
   `git add`. The user directive: use direnv like other repos, not bare
   `nix develop`:

   ```bash
   # or in a plain git clone: git add -A
   jj file track flake.nix .envrc SECURITY.md CODE_OF_CONDUCT.md
   direnv allow
   eval "$(direnv export bash 2>/dev/null)"
   devenv tasks run devlib:license:install
   devenv tasks run devlib:gitignore:install
   devenv tasks run devlib:renovate:install
   devenv tasks run devlib:github:workflows:install
   ```

5. **Land via PR (never direct to main).** Branch `feat/<slug>` (branch-naming
   ruleset), commit with `Co-authored-by: Automata
   <automata@shikanime.studio>` + `Signed-off-by`, push, open PR with
   `--head <org>:<branch>`. Track files only AFTER `.gitignore` exists — the
   devenv run drops `.direnv/` and `.devenv/` caches plus a
   `.pre-commit-config.yaml` symlink that must not enter the commit
   (gitignore covers them only if it landed first).

6. **Merge — expect the review gate.** CI green is necessary but the Landing
   protections require an approval from someone other than the last pusher;
   `gh pr merge --squash --admin` fails with "New changes require approval
   from someone other than the last pusher" even as admin. Surface the gate to
   the user for a human approval. Only if the user explicitly authorizes an
   exception, temporarily delete + recreate the Landing ruleset with review
   requirements off (PATCH on rulesets 404s for classic PATs — use
   DELETE+POST), merge, then restore the exact template ruleset and
   byte-verify.

7. **Tag.** On merged main:

   ```bash
   jj git fetch                           # latest main@origin
   jj tag set v0.1.0 -r main@origin
   jj git push --remote origin --tag v0.1.0
   ```

   The tag-naming ruleset rejects anything but `^v[0-9]+\.[0-9]+\.[0-9]+$`.

## Gotchas

- **Empty repo default-branch deadlock.** An empty repo has no `main`; the
  first pushed branch becomes the default branch and immediately falls under
  the default-branch rulesets (non-fast-forward, deletion) — it can then be
  neither rewritten nor deleted. Push the signed "Initial commit" to
  `feat/bootstrap`, create `refs/heads/main` at that sha via the refs API
  (`gh api -X POST repos/<org>/<repo>/git/refs -f ref=refs/heads/main -f
  sha=<sha>`), flip the default branch with `gh api -X PATCH
  repos/<org>/<repo> -f default_branch=main`, delete the stale branch, then
  re-push the feature branch on top of the Initial commit.
- **Ruleset PATCH 404s with a classic PAT** even with `admin:org` —
  update-via-PATCH is denied while POST/DELETE work. Route all ruleset
  changes through delete + recreate.
- **The ruleset LIST endpoint omits `rules`** — fetching the list and
  comparing shows false MISMATCH for everything. Fetch each ruleset by id for
  verification.
- **`nix develop` directly fails** in flake-mode devenv ("was not able to
  determine the current directory") unless `devenv.root` is set; and even set,
  direct `nix develop -c devenv tasks run` re-resolves the store path. Always
  go through direnv (`use flake .` in `.envrc`), which exports
  `DEVENV_ROOT` correctly.
- **Deleting a branch that has an open PR auto-closes the PR** — reopen by
  creating a new PR; the old one stays CLOSED.

## Verification

```bash
# rulesets: 5, all active, byte-equal to template
gh api repos/<org>/<repo>/rulesets -q '.[] | "\(.id) \(.name) \(.enforcement)"'
# per-id fetch and compare enforcement/conditions/rules/bypass_actors
# CI green on the bootstrap PR
gh pr checks <n> -R <org>/<repo>
# PR merged, tag exists
gh pr view <n> -R <org>/<repo> --json state,mergedAt
gh api repos/<org>/<repo>/tags -q '.[].name'
```

## See also

- `sks-dev-workflow` — the loop this bootstrap feeds into (workspace, commit,
  PR, land).
- `github-workflow-generation` — the generated workflows land as rendered
  YAML; behavior changes go to the devlib generator, not the repo.
