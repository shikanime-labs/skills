---
name: sks-constitution
description: "Use when any shikanime org skill needs environment assumptions: org identity, repo paths, toolchain, branch protection, push policy, and validation probes."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - environment
      - shikanime-labs
      - shikanime-studio
      - assumptions
      - org
    related_skills:
      - sks-constitution
      - sks-commit
      - sks-pr
      - sks-issue
      - sks-stack
      - sks-async
      - sks-pr-workflow
      - sks-issue-workflow
      - sks-land
      - sks-pr-review
      - sks-pr-resolve
      - sks-pr-triage
      - sks-issue-triage
      - sks-issue-refine
      - sks-discussion
      - sks-discussion-triage
      - sks-doc
      - sks-investigate
      - sks-adversarial
      - sks-gc
      - sks-restack
      - sks-converge
      - sks-swarm
      - sks-curate
      - sks-update
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Constitution

Single reference for the implicit organizational and environment assumptions
scattered across every `sks-*` skill. Load this when any sibling skill needs
org identity, repo paths, toolchain, branch protection, push policy, or the
pre-work validation probes. Sibling skills MUST reference this instead of
re-stating these facts.

## When to Use

- Any `sks-*` skill needs to assert an org, path, tool, or protection fact.
- Validating assumptions before work (identity, push rights, toolchain).
- Resolving a repo's class (NixOS, docs, AGENTS.md, jj, protected main).

## Org Identity

- **Orgs:** `shikanime-labs`, `shikanime-studio`.
- **Agent identity:** the `gh` account authenticated in the current session
  holds org membership; do NOT `gh auth switch`.
- **Automata co-author:** agent-assisted commits carry
  `Co-authored-by: Automata <automata@shikanime.studio>` (`sks-commit`).
- **License:** Apache-2.0 across the catalog and org repos.

## Repo Paths

- **Source of truth:** `~/Source/Repos/github.com/<org>/<repo>` — the canonical
  git clone where PRs are opened. Operate here.
- **Operational clone:** `~/.hermes/skills/` — what `skill_view`/`skills_list`
  resolve at runtime. Editing the source-of-truth clone is invisible to the
  running agent until pushed and pulled across.
- **Dual-clone rule:** after editing a skill in `~/Source/Repos/...`, copy to
  `~/.hermes/skills/` (or push + pull) so the agent sees it. Verify which clone
  `skill_view` resolves via its `_source_path` field before patching.
- **gh remote is canonical:** local path may read `shikanime-labs` while the
  remote is `shikanime-studio` (e.g. `nix-containers`) — trust the gh remote.

## Toolchain

- **`gh`:** authenticated, identity is a collaborator with push right.
- **`jj`:** present when `.jj/` exists. Bookmarks are NOT auto-tracked —
  `jj bookmark track <branch> --remote=origin` before any push.
- **`nix`:** required for NixOS/infra repos (`machines`, `nix-containers`).
  `nix fmt` before shipping Nix files.
- **`git`:** fallback for non-jj repos; `git push origin <branch>`.

## Branch Protection

Detect via **RULES**, not classic branch protection. The classic endpoint
`gh api repos/<org>/<repo>/branches/main/protection` returns 404 on
ruleset-backed repos (e.g. `manifests`), which misleadingly reads as
"not protected":

```bash
gh api repos/<org>/<repo>/rulesets -q '.[].name'
gh api repos/<org>/<repo>/rulesets/<id> -r '.rules[]'
```

A `pull_request` rule with `required_approving_review_count` +
`require_code_owner_review` blocks self-approval — that is what forces
`gh pr merge --squash --admin` after a verbal `lgtm`, not a classic
`required_pull_request_reviews` block.

- `main` is protected on some repos (e.g. `shikanime-studio/actions`,
  `shikanime-labs/skills`) — never commit there; land via PR.
- Direct push to `main` ONLY when the user explicitly says "push to main" /
  "land it".

## Push Policy

- Push working branches to `origin` — the cloned org repo.
- Open PRs with `--head <org>:<branch>` (the org prefix, never the account
  login / wrong fork).
- Base `main` unless the default differs
  (`gh repo view <org>/<repo> --json defaultBranchRef`).
- Never `gh pr merge` (poisoned commits); never force-push stacked branches.

## GitHub Message Conventions

- **Full URLs** over `#N` / `owner/repo#N` (broken on GitHub):
  `Related: https://github.com/<org>/<repo>/issues/N`.
- **No bare `@name` in prose** — it pings that user/team. Wrap literal `@`
  (NestJS `@Inject(x)`, decorators, config keys) in a code span or fenced
  block; only code disables mention parsing.
- **English word "as" PROHIBITED** in issue/PR/comment bodies. Before
  `gh pr create` / `gh issue create` / comment: `grep -w -i 'as'` on body;
  zero tolerance.
- Temp body files are NOT hard-wrapped — one sentence per line; GitHub joins
  consecutive non-blank lines. Never `nix fmt` / `mdformat` a temp body file.

## PR↔Commit Parity

- PR title = commit subject.
- PR body = commit message restated (`## What` / `## Why` / `## References`).
- Commit is the source of truth; PR restates, never invents rationale.

## Pre-Work Validation Probes

Probe and RECORD each; an unmet requirement is a reported blocker, never a
silent scope change:

```bash
gh api user --jq .login                                          # identity
gh api repos/<org>/<repo> --jq .viewerPermission                 # push right
ls .jj/ && jj status                                             # jj repo
gh issue view <N> --repo <org>/<repo> --json number,title        # issue exists
which nix                                                        # NixOS repo
```

Report `BLOCKED: <req> — <evidence> — <recovery>`. Independent unblocked
streams may fan out (`sks-async`) while the blocker is surfaced.

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

Every `sks-*` sibling skill references this for environment facts. Update here
when org identity, paths, toolchain, or protection rules change.
