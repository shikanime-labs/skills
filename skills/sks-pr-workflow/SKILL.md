---
name: sks-pr-workflow
description:
  "Use when you need the single entry point for the shikanime PR side: ensure
  the issue exists, open, and triage the PR. Land separately via sks-land."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - shikanime-labs
      - shikanime-studio
      - workflow
    related_skills:
      - sks-pr
      - sks-pr-triage
      - sks-land
      - sks-pr-resolve
      - sks-issue-workflow
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org PR Workflow

Orchestrator over `sks-issue`/`sks-pr`/`sks-pr-triage`: issue → PR → triage.

Read `references/org-conventions.md` when working in a shikanime org repo
(`shikanime-labs/*`/`shikanime-studio/*`); local checkout layout and
push/open specifics live there.

Encourage authors to embed a Mermaid diagram in the issue or PR body when a
flow or architecture helps the reader — GitHub renders Mermaid inline. The body
stays free text; the diagram is optional reinforcement, never a substitute for
the prose.

When the repo's gate includes code-quality checks (e.g. SonarQube Quality
Gate, 0 new issues), verify them via `gh pr checks <N>` before declaring the
PR complete; org-specific gate ids live in the org reference.

## When to Use

- "Run the full PR side: issue → PR → triage."
- "Ensure a PR is properly linked and triaged before work starts."

## Procedure

### 0. Pre-submit isolation & conflict gate (mandatory)

Every PR carries ONLY its own change set. Before opening (step 2), verify:

1. Isolation — change set is exactly the intended files, no foreign/dangling
   files from parallel agents or interrupted sessions.
   - jj: `jj diff -r @ --stat` and `jj file list -r @`; anything outside scope
     stays in `@` / a separate commit, never in this PR.
   - jj: `jj log -r @ --no-graph -T 'if(empty, "", "dirty\n")'` plus
     `jj diff -r 'main@origin..@' --stat` (git checkouts:
     `git status --porcelain --untracked-files=all` and
     `git diff --stat origin/main..HEAD`).
2. Conflict-free base — the branch descends from the PR base with no conflict
   markers.
   - `BASE=$(gh pr view <N> --json baseRefOid -q .baseRefOid)` (new PR:
     `origin/main`).
   - jj: `jj rebase -d main@origin -r @` — a clean rebase = gate pass; a
     conflict report = real conflict. (git checkouts:
     `git merge-base --is-ancestor "${BASE:-origin/main}" HEAD`.)
   - `CONFLICTING`/`DIRTY` = real conflict; `BLOCKED` = pending CI, not
     conflict.

Do NOT open the PR until both checks pass.

### 1. Ensure linked issue exists

If `#N` not provided/converged, load `sks-issue` (or `sks-issue-workflow`) and
create first. A PR never opens without an issue. Verify match via
`jj show <commit>` before linking.

### 2. Open the org-repo PR

Load `sks-pr`. Push to `origin` (org repo), open `--head <org>:<branch>`, base
`main`; link `Related: <full issue URL>`.

### 3. Triage immediately

Load `sks-pr-triage`; apply metadata now. Apply only empty/determinable fields;
never invent a value the repo lacks.

## Gate

Done when opened from `origin`, links issue, triage set, and the isolation gate
passed. Verify:

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

```bash
# isolation: diff vs base is exactly the intended files, no conflict markers
gh pr diff <N> --repo <org>/<repo> --name-only
git diff --stat "$(gh pr view <N> --repo <org>/<repo> --json baseRefOid -q .baseRefOid)"..HEAD
```

## Verification

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
gh pr diff <N> --repo <org>/<repo> --name-only \
  # isolation: exactly the intended files
```

## See also

- `sks-issue`/`sks-issue-workflow` — issue to solve.
- `sks-pr` — create step.
- `sks-pr-triage` — metadata step.
