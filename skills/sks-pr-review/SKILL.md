---
name: sks-pr-review
description:
  "Use when reviewing shikanime code: cross-check related issues, enforce
  YAGNI, root-cause fixes, and project conventions before approval."
version: 0.4.0
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
      - caveman-review
      - ponytail-review
platforms:
  - linux
  - macos
  - windows
---

# PR Review

Review local diffs and GitHub PRs through the `ponytail`/YAGNI lens
(`ponytail` plugin skills; `ponytail-review` is the over-engineering-only
pass), enforcing review practice and repo conventions. Reports
only — never auto-commit/merge/fix. Uses `jj`, `gh`, and standard Hermes
tools.

Read `references/conventions.md` when the repo under review uses the org's
standard stack (auth trust boundaries). Read `references/cloud-pi-native.md`
when reviewing a cloud-pi-native console PR (console architecture
checkpoints, French output templates, toolchain). When operating in a
shikanime org, read `references/shikanime.md` for the org stack
mapping.

The mechanics below (added-line security scan, independent fail-closed reviewer)
are distilled from `requesting-code-review` and adapted to the
human-gated flow: the agent posts findings and a verdict, a human approves.

## When to Use

- "review this diff", "check before pushing", "review PR #N", "look at this PR"
- After a task touching 2+ files
- Before opening/merging a PR

## Prerequisites

- Inside a jj repo (colocated or jj-native)
- `gh` authenticated for PR-level interaction
- Optional `ruff`/`eslint`/`tsc`/`go vet`/`pytest` — skipped silently if absent

## Procedure

**1 — Scope.** Diff + stat. Empty diff → tell user. >15k chars → split by file.
Command cheat-sheet: `references/commands.md`. Review the diff that would
merge, not the branch tip: `main@origin..@` locally; a PR's merge-base diff
against `main`.

**1b — Issue cross-check.** Before the verdict, search the repo's issues
and PRs related to the diff. Search by changed file paths, symbols, and the
subject keyphrase (`gh issue list -R <org>/<repo> --state all --search
"<symbol or path>" --limit 10`). Verify a recurring bug's fix against the
issue's root cause, not the symptom it names. Do not re-flag a tradeoff a
closed issue already accepted. Cite an open issue that covers the same
change. If the search finds nothing and the diff touches a
domain-specific area (infra, auth, storage), consult memory
(`honcho_search`) for known pitfalls first. Never skip the search on the
assumption memory already covers the area.

**2 — High-level (Ponytail ladder).** Per change:

- (1) needed? speculative need → flag deletion, not review polish;
- (2) already in codebase? reuse before reviewing a re-implementation;
- (3) root cause not symptom — fix where all callers route through, not in the
  one path the ticket named;
- (4) test strategy present and owned by the right unit?

Full ladder: the `ponytail` skill. Deliberate corner-cuts found here should
carry a `ponytail:` comment (ceiling + upgrade path) — `ponytail-debt`
harvests them.

**3 — Security scan (added lines).** Run `references/security-scan.md`. Any
match = `blocking`. Covers hard-coded secrets, shell/SQL injection,
`eval`/`exec`, unsafe deserialization, path traversal, XSS; plus auth
trust-boundary checks for the repo's stack (org-stack specifics:
`references/conventions.md`).

**4 — Independent verdict.** Self-review checklist + a `delegate_task` reviewer
with only the diff (no shared context, fail-closed on non-JSON):
`references/review-doctrine.md`. `passed` false on any security/logic finding.

**5 — Line-by-line.** Correctness (edge/error paths), maintainability
(naming/DRY/no premature abstraction), conventions.

**6 — Summary.** Severity-tag findings; post each inline at its line
(`references/inline-comments.md`), not one block; body = 2-3 sentence verdict +
praise. Standard doctrine: approve if it improves health even if imperfect;
request changes only on `blocking`. Never block on polish.

## Flag test

A `blocking` or `important` finding qualifies only when ALL hold: it
meaningfully affects correctness, security, performance, or maintainability;
it is discrete and actionable; it was introduced by the reviewed change
(never pre-existing or an intentional behavior change); a demonstrable call
path exists in the code; the author would likely fix it. The test does not
gate `nit`, `suggestion`, `learning`, or `praise` — those stay reportable
under Severity Labels and never gate the verdict. It also does not gate
security-scan matches (step 3): any added-line match is `blocking`
regardless of call path. Confirm each qualifying finding against the tests
and call sites before posting, and keep traversing
the whole diff after the first one. Nothing qualifies at any tier → say
`No findings.` — never invent one to fill the report.

## Severity Labels

`blocking` / `important` / `nit` / `suggestion` / `learning` / `praise`.
Inline-anchoring syntax and `gh api` template: `references/inline-comments.md`.

## Finding format

One line per finding: `<file>:L<line>: <severity>: <problem>. <fix>.` Keep the
exact line and exact symbol name in backticks, and a concrete fix, not
"consider refactoring". Drop restating what the line does, hedging ("perhaps"),
and throat-clearing. If the fix is not obvious from the problem, add the why.
Cite the full URL of a related issue when it confirms or contradicts the
finding. Full paragraphs only for security/architecture findings; resume the
one-line format after.

## Posting (PRs)

ONE review on the PR, inline comments per line
(`references/inline-comments.md`), not a block: each at its `path`/`line`,
severity-prefixed; body = 2-3 sentence verdict + one specific praise. Use a
top-level review comment (`gh pr review <N> --comment`) only when a finding has
no line anchor. No local-only summary — every finding lands on the PR. If
commits violate conventions, suggest a corrected plain-English message in the
body (author amends — reviewer never pushes).

## Pitfalls

- Empty diff → check `jj status`, tell user nothing to verify.
- Large diff (>15k chars) → split by file, review each.
- `delegate_task` non-JSON → treat as FAIL (fail-closed).
- False positives → note intentional patterns, don't block.
- Lint/test tools absent → skip that check silently; verdict still runs.
- In jj workspaces `gh` can fail to resolve the repo; always pass `-R
  <org>/<repo>` to issue and PR queries. Report a failed or empty search;
  it never blocks the review.

## Verification

Done when: all findings posted inline (severity-prefixed) in one review, body =
verdict + praise (2-3 sentences), corrected commit message suggested. Mapping:
any `blocking` → `REQUEST_CHANGES`; else `APPROVE` if confident, `COMMENT`
otherwise (`gh pr review <N> --request-changes|--approve|--comment`).

Related: `requesting-code-review`, `github-code-review`.

## See also

- `sks-investigate` — root-cause research before any fix.
