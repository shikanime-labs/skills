---
name: sk-code-review
description:
  "Use when reviewing shikanime repos: YAGNI, root-cause, repo conventions,
  security scan, severity-tagged findings."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags:
      [
        "code-review",
        "yagni",
        "conventions",
        "security",
        "github",
        "pull-requests",
        "shikanime-labs",
        "shikanime-studio",
      ]
    related_skills: ["sk-pr", "sk-land", "sk-dev-workflow"]
---

# Code Review (sk-code-review)

Review local diffs and GitHub PRs through the Ponytail/YAGNI lens, enforcing
shikanime review practice and repo conventions. Reports only — never
auto-commit/merge/fix. Uses `jj`, `gh`, and standard Hermes tools.

## When to Use

- "review this diff", "check before pushing", "review PR #N", "look at this PR"
- After a task touching 2+ files
- Before opening/merging a PR in shikanime/* or cloud-pi-native/*

## Prerequisites

- Inside a jj repo (colocated or jj-native)
- `gh` authenticated for PR-level interaction
- Optional `ruff`/`eslint`/`tsc`/`go vet`/`pytest` — skipped silently if absent

## How to Run

Run via `terminal`; read context with `read_file` / `search_files`. For an
independent verdict, dispatch a reviewer per `references/dispatch.md` (diff
only, fail-closed on non-JSON). Standard: `references/review-doctrine.md`.

## Quick Reference

Command cheat-sheet: `references/commands.md`.

## Procedure

**1 — Scope.** Diff + stat. Empty → tell user. >15k chars → split by file. **2 —
High-level (Ponytail).** Per change: (1) needed? speculative → flag deletion;
(2) already in codebase? reuse before reviewing re-implementation; (3) root
cause not symptom — fix where all callers route through; (4) test strategy
present? **3 — Line-by-line.** Correctness (edge/error paths), security,
maintainability (naming/DRY/no premature abstraction), conventions. **4 —
Summary.** Tag findings with severity, post inline at line. Standard
`references/review-doctrine.md`: approve if it improves health even if
imperfect; request changes only on `blocking`. Never block on polish.

## Posting (PRs)

ONE review, inline comments per line (`references/inline-comments.md`), not a
block: each at its `path`/`line`, severity-prefixed; body = 2-3 sentence verdict

- praise. If commits violate conventions, suggest a corrected message in the
  body (author amends — reviewer never pushes).

## Severity Labels

`references/severity-labels.md` (blocking / important / nit / suggestion /
learning / praise).

## Security Scan

Added-line scan (any match = `blocking`): `references/security-scan.md`. Also
check hardcoded secrets, SQL/Shell injection, path traversal, XSS
(`innerHTML = userInput`), missing input validation at trust boundaries.

## Repo Conventions (enforced)

Full rule set: `references/conventions.md` (no AI-marker comments,
commit/license/Nix/Go style, PR routing with `--head`, secrets, agent identity).

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

Done when: all findings posted inline (severity-prefixed) in one review, body =
verdict + praise (2-3 sentences), corrected commit message suggested. Mapping:
any `blocking` → `REQUEST_CHANGES`; else `APPROVE` if confident, `COMMENT`
otherwise (`gh pr review <N> --request-changes|--approve|--comment`).

Related: `requesting-code-review`, `github-code-review`.
