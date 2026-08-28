---
name: cpn-constitution
description: "Use when any cloud-pi-native org skill needs environment assumptions: org identity, repo paths, toolchain, branch protection, push policy, and validation probes."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - environment
      - cloud-pi-native
      - assumptions
      - org
    related_skills:
      - cpn-constitution
      - cpn-dev-workflow
      - cpn-commit
      - cpn-pr
      - cpn-issue
      - cpn-stack
      - cpn-async
      - cpn-pr-workflow
      - cpn-issue-workflow
      - cpn-pr-review
      - cpn-pr-resolve
      - cpn-pr-triage
      - cpn-issue-triage
      - cpn-issue-refine
      - cpn-discussion
      - cpn-discussion-triage
      - cpn-swarm
      - cpn-release-patch
      - cpn-curate
      - cpn-update
platforms:
  - linux
  - macos
  - windows
---

# Cloud Pi Native Org Constitution

Single reference for the implicit organizational and environment assumptions
scattered across every `cpn-*` skill. Load this when any sibling skill needs
org identity, repo paths, toolchain, branch protection, push policy, or the
pre-work validation probes. Sibling skills MUST reference this instead of
re-stating these facts.

## When to Use

- Any `cpn-*` skill needs to assert an org, path, tool, or protection fact.
- Validating assumptions before work (identity, push rights, toolchain).
- Resolving a repo's class (console, documentation, infrastructure).

## Org Identity

- **Org:** `cloud-pi-native`.
- **Agent identity:** the `gh` account authenticated in the current session
  holds org membership; do NOT `gh auth switch`.
- **Automata co-author:** agent-assisted commits carry
  `Co-authored-by: Automata <automata@shikanime.studio>` (`cpn-commit`).
- **License:** Apache-2.0 across the catalog and org repos.

## Repo Paths

- **Source of truth:** `~/Source/Repos/github.com/cloud-pi-native` — the
  canonical git clone where PRs are opened. Operate here.
- **Operational clone:** `~/.hermes/skills/` — what `skill_view`/`skills_list`
  resolve at runtime. Editing the source-of-truth clone is invisible to the
  running agent until pushed and pulled across.
- **Dual-clone rule:** after editing a skill in `~/Source/Repos/...`, copy to
  `~/.hermes/skills/` (or push + pull) so the agent sees it. Verify which clone
  `skill_view` resolves via its `_source_path` field before patching.
- **gh remote is canonical:** trust the gh remote over the local path.

## Toolchain

- **`gh`:** authenticated, identity is a collaborator with push right.
- **`jj`:** present when `.jj/` exists. Bookmarks are NOT auto-tracked —
  `jj bookmark track <branch> --remote=origin` before any push.
- **Docker:** >= 27 (compose >= 2.35, buildx).
- **Node.js:** >= 24.
- **pnpm:** >= 10.
- **`git`:** fallback for non-jj repos; `git push origin <branch>`.

## Branch Protection

Detect via **RULES**, not classic branch protection. The classic endpoint
`gh api repos/<org>/<repo>/branches/main/protection` returns 404 on
ruleset-backed repos, which misleadingly reads as "not protected":

```bash
gh api repos/<org>/<repo>/rulesets -q '.[].name'
gh api repos/<org>/<repo>/rulesets/<id> -q '.rules[]'
```

A `pull_request` rule with `required_approving_review_count` +
`require_code_owner_review` blocks self-approval — that is what forces
`gh pr merge --squash --admin` after a verbal `lgtm`, not a classic
`required_pull_request_reviews` block.

- `main` is protected on some repos — never commit there; land via PR.
- Direct push to `main` ONLY when the user explicitly says "push to main" /
  "land it".

## Push Policy

- Push working branches to `origin` — the cloned org repo.
- Open PRs with `--head cloud-pi-native:<branch>` (the org prefix, never the
  account login / wrong fork).
- Base `main` unless the default differs
  (`gh repo view <org>/<repo> --json defaultBranchRef`).
- Never `gh pr merge` (poisoned commits); never force-push stacked branches.

## Issue-First Mandate

- A PR always resolves an issue — never open a PR without a linked issue.
- Issue body = problem statement (need, scope, API/data/security impact,
  acceptance tasklist); analysis goes in comments.
- Link via `Refs #N` (many-to-many: multiple PRs can resolve one issue, one PR
  can serve several).
- Close deliberately after N-of-N verification.

## Commit Style

- Conventional commits: `feat`, `fix`, `chore`, `docs`, `refactor`, `revert`,
  `build` (`feature` also recognized).
- French language for commit subjects and PR bodies.
- Repo-enforced hooks (commitlint, Husky) ALWAYS win — detect per repo:
  `grep -rilE "commitlint|release-please|@commitlint" . --include=package.json --include=*.cjs --include=*.json`.

## PR Conventions

- **Conventional PR title** — `feat:`/`fix:`/`docs:`/`chore:`/`refactor:`/
  `revert:`/`build:`. Release Please derives the version bump from it where
  configured.
- **French PR body** — use the repo's `PULL_REQUEST_TEMPLATE.md` sections
  verbatim when present; else the canonical French template.
- **Issue linkage** — `Issues liées: #XXXX` par défaut (suivre sans fermer).
- **Base branch** — `main` unless the repo's default differs.

## GitHub Message Conventions

- **Full URLs** over `#N` / `owner/repo#N` (broken on GitHub):
  `Related: https://github.com/<org>/<repo>/issues/N`.
- **No bare `@name` in prose** — it pings that user/team. Wrap literal `@`
  (NestJS `@Inject(x)`, decorators, config keys) in a code span or fenced
  block; only code disables mention parsing.
- Temp body files are NOT hard-wrapped — one sentence per line; GitHub joins
  consecutive non-blank lines. Never `nix fmt` / `mdformat` a temp body file.

## PR↔Commit Parity

- PR title = commit subject.
- PR body = commit message restated.
- Commit is the source of truth; PR restates, never invents rationale.

## Pre-Work Validation Probes

Probe and RECORD each; an unmet requirement is a reported blocker, never a
silent scope change:

```bash
gh api user --jq .login                                          # identity
gh api repos/<org>/<repo> --jq .viewerPermission                 # push right
ls .jj/ && jj status                                             # jj repo
gh issue view <N> --repo <org>/<repo> --json number,title        # issue exists
node --version && pnpm --version                                 # toolchain
docker --version                                                 # docker
```

Report `BLOCKED: <req> — <evidence> — <recovery>`. Independent unblocked
streams may fan out (`cpn-async`) while the blocker is surfaced.

## Done Is Proven

"`pushed` / `landed` / `merged`" are claims until verified against real
output:

- `gh pr view <N> --json state,url,headRefName` after create/merge.
- Re-measure any number (commits, PRs, files) before stating it.
- GitHub's web diff view pads context — never size a PR from it. Use
  `gh pr view <N> --json files` / `jj diff -r <branch> --git --stat`.
- A red required check / branch-protection rejection is a gate doing its job
  — surface it, never `--admin` past it unasked.

## See also

Every `cpn-*` sibling skill references this for environment facts. Update here
when org identity, paths, toolchain, or protection rules change.
