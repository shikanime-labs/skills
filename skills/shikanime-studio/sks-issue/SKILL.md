---
name: sks-issue
description:
  "Use when opening an issue in shikanime-labs or shikanime-studio: body is the
  problem statement, acceptance criteria as a command-decidable tasklist."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-doc
      - sks-issue-refine
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Issue Creation

Open issues in `shikanime-labs/*` / `shikanime-studio/*`; English (no French).
Open the issue before the PR, link it via `sks-pr`.

Prereqs: `gh` authenticated to the canonical org repo; target it directly.
`gh auth status` clean.

## When to Use

- "Create a new shikanime issue."
- "Track and manage a shikanime GitHub issue."
- "Verify issue exists before opening a PR (issue-first policy)."

## Procedure

### 0. Check for existing issues

Search before creating to avoid duplicates:

```bash
gh issue list --repo <org>/<repo> --state all --search "<keywords>" --limit 10
```

If an open (or recently closed) issue matches, surface the `#N` and confirm with
the user whether to reuse it instead of opening a new one. Only create when no
matching issue exists (or the user explicitly wants a fresh ticket).

### 1. Repo + type

```bash
gh issue create --repo <org>/<repo> --title "<summary>" --label <type> --body "..."
```

- Bug: `--label bug`. Feature: `--label enhancement`.
- Verify repo labels first: `gh label list --repo <org>/<repo> --limit 100`.

### 2. Body = problem statement only

Temp body files are NOT hard-wrapped — semantic line breaks (one sentence per
line, no 80-col wrap); GitHub joins consecutive non-blank lines, so a
one-sentence edit churns only that line. Never `nix fmt` / `mdformat` a temp
body file.

- A bare `@name` in prose pings that user/team — wrap any literal `@` (NestJS
  `@Inject(x)`, decorators, config keys) in a code span or fenced block; only
  code disables mention parsing.

Body = clean problem statement (Description, reproduction steps, affected
version, impact). Post root-cause / investigation findings as a **comment**
(`gh issue comment <N> --repo <org>/<repo> --body-file <file>`), never in the
body — it must stay stable for triage. The issue is a clean conversation, not a
notebook: concluded findings + open questions only, never raw reasoning/status
chatter; interim comments deletable after convergence.

Acceptance criteria: a `- [ ]` tasklist, each item phrased so a command can
decide it. An item is done only once its check ran, never from memory; an
impossible criterion is struck with a comment, never dropped. Candidate
solutions belong in comments, not tasklist/body.

Observed variant (see `references/example-issue-body.md`): `## Problem` /
`## Acceptance` with no separate References block — same content, fewer
headings; either shape is acceptable. Keep the body stable; post
findings/root-cause as `gh issue comment` and cite concrete evidence (the exact
`- old` → `+ new` diff lines, or command output), not prose summaries. Interim
comments may be deleted after convergence.

Body has a **References** section: official material (docs, linked issues/PRs,
commits, changelogs, specs); more may be posted as comments to steer resolution,
but proof of the solution belongs in the PR. Close deliberately — ledger
verified N of N after final merge.

### 3. Triage metadata

Delegate to `sks-issue-triage`: sets each empty, determinable field (type,
labels, assignee, milestone, project); rules live there.

## Pitfalls

- Wrong repo — always use the org repo.
- Rewriting body with findings — findings go in a comment.
- Inventing labels the repo lacks — verify with `gh label list` first.
- English only; don't carry over cpn's French templates.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

Confirm title + label set; issue in org repo.

## See also

`sks-discussion`, `sks-pr` (links back via `Related:`), `sks-issue-refine`,
`sks-issue-triage` (run after creation), `sks-doc`.
