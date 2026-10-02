---
name: sks-issue
description:
  "Use when opening an issue in an org repo: body is the
  problem statement, acceptance criteria as a command-decidable tasklist."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
    related_skills:
      - sks-doc
      - sks-issue-refine
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Issue Creation

Open issues in the org repos; language and repo scoping rules live in
`references/shikanime.md` (load it when working in an org repo). Open
the issue before the PR, link it via `sks-pr`.

Prereqs: `gh` authenticated to the target repo; target it directly.
`gh auth status` clean.

## When to Use

- "Create a new org issue."
- "Track and manage a GitHub issue."
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

Prose rules (free text, no wrapping, no formatter runs, `@` escaping,
evidence style, comment etiquette) come from `sks-github-text-authoring` —
load it for any body or comment writing; they are not restated here.

- A bare `@name` in prose pings that user/team — wrap any literal `@` in a
  code span (rule owned by `sks-github-text-authoring`).

Body = clean problem statement (Description, reproduction steps, affected
version, impact). Post root-cause / investigation findings as a **comment**
(`gh issue comment <N> --repo <org>/<repo> --body-file <file>`), never in the
body — it must stay stable for triage. The issue is a clean conversation, not a
notebook: concluded findings + open questions only, never raw reasoning/status
chatter; interim comments deletable after convergence.

Encourage a Mermaid diagram (e.g. `flowchart TD`) in the body when a visual
aids the reader — rendered inline by GitHub (rule owned by
`sks-github-text-authoring`); the diagram is optional reinforcement, never a
substitute for the prose.

Acceptance criteria: a `- [ ]` tasklist, each item phrased so a command can
decide it. An item is done only once its check ran, never from memory; an
impossible criterion is struck with a comment, never dropped. Candidate
solutions belong in comments, not tasklist/body.

Comments follow the prose rules in `sks-github-text-authoring`: lead with the
conclusion, cite evidence, stop. One subject per comment — split unrelated
findings into separate comments.

Observed variant (see `references/example-issue-body.md`): `# Problem` /
`## Acceptance` with no separate References block — same content, fewer
headings; either shape is acceptable. Keep the body stable; post
findings/root-cause as `gh issue comment` and cite concrete evidence (the exact
`- old` → `+ new` diff lines, or command output), not prose summaries. Interim
comments may be deleted after convergence.

The issue template (`# Problem` / `## Acceptance`) is issue-only. The PR body
must not reuse it — the PR side uses the `# Why` / `## What` / `## References`
shape from `sks-pr`.

**Templates: detect, then conform.** Probe for repo issue templates before
writing the body — candidate paths: `.github/ISSUE_TEMPLATE.md`,
`.github/ISSUE_TEMPLATE/`, `.github/issue_template.md`. When one exists,
fill its sections and keep its headings verbatim; the acceptance-criteria
tasklist rides in whichever section fits. Cross-check the form's `labels:`
against `gh label list` before flagging or passing a label. No template →
the default shapes above.

A body without a template has a **References** section: official material
(docs, linked issues/PRs, commits, changelogs, specs); with a template, place
references in a suitable template-defined section instead of adding headings
it lacks. More may be posted as comments to steer resolution, but proof of the
solution belongs in the PR. Close deliberately — ledger verified N of N after
final merge.

### 3. Triage metadata

Delegate to `sks-issue-triage`: sets each empty, determinable field (type,
labels, assignee, milestone, project); rules live there.

## Pitfalls

- Wrong repo — always use the org repo.
- Rewriting body with findings — findings go in a comment.
- Inventing labels the repo lacks — verify with `gh label list` first.
- Language and template rules live in `references/shikanime.md`; follow
  them.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

Confirm title + label set; issue in org repo.

## See also

`sks-github-text-authoring` (prose rules), `sks-discussion`, `sks-pr` (links
back via `Related:`), `sks-issue-refine`, `sks-issue-triage` (run after
creation), `sks-gist` (verified snippets too long for a comment), `sks-doc`.
