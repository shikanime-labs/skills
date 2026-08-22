---
name: sk-code-review
description: "Code review discipline: YAGNI, root-cause, conventions."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      [
        code-review,
        yagni,
        conventions,
        security,
        github,
        pull-requests,
        shikanime-labs,
        shikanime-studio,
      ]
---

# Code Review (sk-code-review)

Structured review of local diffs and GitHub PRs through the Ponytail/YAGNI lens,
enforcing the accumulated shikanime review practice and repo conventions. Does
NOT auto-commit, auto-merge, or auto-fix: it reports, you act. Relies only on
`jj`, `gh`, and standard Hermes tools — no extra dependencies.

## When to Use

- "review this diff", "check before pushing", "review PR #N", "look at this PR"
- After a task touching 2+ files in a repo
- Before opening or merging a PR in a shikanime/* or cloud-pi-native/* repo

## Prerequisites

- Inside a jj repository (colocated or jj-native)
- `gh` authenticated for any PR-level interaction
- Optional language tooling (`ruff`, `eslint`, `tsc`, `go vet`, `pytest`) —
  skill skips silently if absent

## How to Run

Frame execution through the `terminal` tool; read context with `read_file` /
`search_files`. For an independent verdict, dispatch a `delegate_task` reviewer
with ONLY the diff (no shared context — no agent verifies its own work). Load
`references/review-doctrine.md` for the shared review standard.

## Quick Reference

```bash
jj diff -r @                           # working-copy change
jj diff --from main --to @ --stat      # PR scope
jj diff --from main --to @ --name-only # changed files
jj log --no-graph -r 'main..@' -T 'description ++ "\n"'  # intent
gh pr view <N> && gh pr diff <N>       # PR context
gh pr checkout <N>                     # full local review
```

## Procedure

**Phase 1 — Scope.** Get the diff and stat. If empty, tell the user (nothing to
verify). If >15k chars, split by file.

**Phase 2 — High-level (Ponytail lens).** For each change, in order:

1. Does this need to exist? Speculative code = flag for deletion.
2. Already in the codebase? Reuse the existing helper/util/type before reviewing
   a re-implementation.
3. Root cause, not symptom — if a function is fixed, check every caller; the fix
   belongs where all callers route through.
4. Test strategy present? New logic paths need a test.

**Phase 3 — Line-by-line.** Check correctness (edge cases, error paths),
security (below), maintainability (naming, DRY, no premature abstraction), and
convention compliance (below).

**Phase 4 — Summary.** Tag every finding with a severity and post each one
inline at its line. Judge by the approving standard
(`references/review-doctrine.md`): approve when the change definitely improves
code health, even if imperfect; request changes only on `blocking` findings.
Never block on polish.

## Posting (PRs)

Post findings as ONE review with inline comments anchored per line
(`references/inline-comments.md`), NOT one big block comment: each finding at
its `path`/`line`, severity-prefixed; the review body is a 2-3 sentence
verdict + praise. If commit messages violate the repo conventions, suggest a
corrected commit message in the body (author amends — the reviewer does not
push).

## Severity Labels

| Label        | Meaning                                |
| ------------ | -------------------------------------- |
| `blocking`   | Must be fixed before merge             |
| `important`  | Should be fixed; may block on context  |
| `nit`        | Minor style or preference issue        |
| `suggestion` | Optional improvement worth considering |
| `learning`   | Educational note for the author        |
| `praise`     | Explicitly highlight great work        |

## Security Scan (added lines only)

```bash
jj diff -r @ | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"
jj diff -r @ | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True|\beval\(|\bexec\("
jj diff -r @ | grep "^+" | grep -E "pickle\.loads?\("
jj diff -r @ | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT"
```

Any match = `blocking`. Also check hardcoded secrets, SQL/Shell injection, path
traversal, XSS (`innerHTML = userInput`), and missing input validation at trust
boundaries.

## Repo Conventions (enforced in review)

- **No AI-marker comments** — `ponytail:`, `claude:`, `gpt-4:` etc. Replace with
  a real _why_ comment. Reject on sight.
- **Commits** — code repos: short imperative, no prefix, no body, no trailers,
  one commit per logical fix. Doc repos: `doc:` prefix.
- **License** — prefer Apache 2.0 for new repos.
- **Nix style** — single-key attrset inline (`a.b = v`); multi-key block
  (`a = { b = 1; c = 2; }`); never mix on one line.
- **Go (xqbit/shikanime-labs)** — `jj` + ghstack flow; `gofmt` clean; PRs opened
  as drafts.
- **PR routing** — `shikanime/sk-*` : push to `origin` (the org repo), open
  `--head <org>:<branch>`. `cloud-pi-native/*` : push to `origin`, open
  `--head cloud-pi-native:<branch>`. Never mix.
- **Secrets** — never read/print/commit `.env` or credential files.
- **Agent identity** — commits co-authored by
  `Automata <automata@shikanime.studio>`; gh agent id `yorha-automata`. Do not
  switch `gh` auth.

## Pitfalls

- Empty diff → check `jj status`, tell user nothing to verify.
- Large diff (>15k chars) → split by file, review each.
- `delegate_task` returns non-JSON → treat as FAIL (fail-closed).
- False positives → note intentional patterns in the report, don't block.
- Lint/test tools absent → skip that check silently, reviewer verdict still
  runs.

## Verification

A review is complete when: every finding is posted inline at its line
(severity-prefixed) via a single review, the review body states the verdict +
praise in 2-3 sentences, and a corrected commit message is suggested when the
history violates conventions. Verdict mapping: any `blocking` →
`REQUEST_CHANGES`; else `APPROVE` when confident, `COMMENT` otherwise
(`gh pr review <N> --request-changes|--approve|--comment`).

Related: `requesting-code-review`, `github-code-review`.
