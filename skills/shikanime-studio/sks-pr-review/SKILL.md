---
name: sks-pr-review
description:
  "Use when reviewing shikanime code: enforce YAGNI, root-cause fixes, and
  project conventions before approval."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - code-review
      - yagni
      - conventions
      - security
      - github
      - pull-requests
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr-resolve
      - sks-land
      - sks-pr
      - requesting-code-review
      - cpn-pr-review
platforms:
  - linux
  - macos
  - windows
---

# PR Review (sks-pr-review)

Review local diffs and GitHub PRs through the Ponytail/YAGNI lens, enforcing
shikanime review practice and repo conventions. Reports only — never
auto-commit/merge/fix. Uses `jj`, `gh`, and standard Hermes tools.

The mechanics below (added-line security scan, independent fail-closed
reviewer) are distilled from `requesting-code-review` and adapted to the
shikanime human-gated flow: the agent posts findings and a verdict, a human
approves.

## When to Use

- "review this diff", "check before pushing", "review PR #N", "look at this PR"
- After a task touching 2+ files
- Before opening/merging a PR in shikanime/* or cloud-pi-native/*

## Prerequisites

- Inside a jj repo (colocated or jj-native)
- `gh` authenticated for PR-level interaction
- Optional `ruff`/`eslint`/`tsc`/`go vet`/`pytest` — skipped silently if absent

## Procedure

**1 — Scope.** Diff + stat. Empty diff → tell user. >15k chars → split by file.
Command cheat-sheet: `references/commands.md`.

**2 — High-level (Ponytail).** Per change:

- (1) needed? speculative need → flag deletion, not review polish;
- (2) already in codebase? reuse before reviewing a re-implementation;
- (3) root cause not symptom — fix where all callers route through, not in the
  one path the ticket named;
- (4) test strategy present and owned by the right unit?

**3 — Security scan (added lines).** Run `references/security-scan.md`. Any match
= `blocking`. Covers hard-coded secrets, shell/SQL injection, `eval`/`exec`,
unsafe deserialization, path traversal, XSS; plus auth trust-boundary checks
(Keycloak/JWKS timeout + client binding, NestJS/Prisma type boundary).

**4 — Independent verdict.** Self-review checklist + a `delegate_task` reviewer
with only the diff (no shared context, fail-closed on non-JSON):
`references/review-doctrine.md`. `passed` false on any security/logic finding.

**5 — Line-by-line.** Correctness (edge/error paths), maintainability
(naming/DRY/no premature abstraction), conventions.

**6 — Summary.** Severity-tag findings; post each inline at its line
(`references/inline-comments.md`), not one block; body = 2-3 sentence verdict +
praise. Standard doctrine: approve if it improves health even if imperfect;
request changes only on `blocking`. Never block on polish.

## Severity Labels

`blocking` / `important` / `nit` / `suggestion` / `learning` / `praise`.
Inline-anchoring syntax and `gh api` template: `references/inline-comments.md`.

## Posting (PRs)

ONE review on the PR, inline comments per line (`references/inline-comments.md`),
not a block: each at its `path`/`line`, severity-prefixed; body = 2-3 sentence
verdict + one specific praise. Use a top-level review comment (`gh pr review <N>
--comment`) only when a finding has no line anchor. No local-only summary — every
finding lands on the PR. If commits violate conventions, suggest a corrected
plain-English message in the body (author amends — reviewer never pushes).

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

Done when: all findings posted inline (severity-prefixed) in one review, body =
verdict + praise (2-3 sentences), corrected commit message suggested. Mapping:
any `blocking` → `REQUEST_CHANGES`; else `APPROVE` if confident, `COMMENT`
otherwise (`gh pr review <N> --request-changes|--approve|--comment`).

Related: `requesting-code-review`, `github-code-review`, `cpn-pr-review`.

## See also

- `sks-investigate` — root-cause research before any fix.
