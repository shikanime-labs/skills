---
name: sk-issue
description: "Open issues in shikanime-labs and shikanime-studio."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, issues, shikanime-labs, shikanime-studio]
---

# Shikanime Org Issue Creation

Create GitHub issues in `shikanime-labs/*` and `shikanime-studio/*` repos.
English bodies (no French). Issue-first is encouraged: create the issue before
the PR, then link the PR to it (see `sk-pr`).

## When to Use

- "Open an issue on <repo>" / "create a bug/feature ticket".
- Any issue creation in a shikanime-owned repo.

## Prerequisites

- `gh` authenticated against the canonical org repo (`shikanime-labs` or
  `shikanime-studio`). Target the org repo directly — issues live there.
- `gh auth status` clean.

## Procedure

### 1. Pick the repo + type

```bash
gh issue create --repo <org>/<repo> --title "<summary>" --label <type> --body "..."
```

- Bug: `--label bug`, title `<short summary>` (no emoji prefix required).
- Feature/enhancement: `--label enhancement`.
- Verify a repo uses these labels first:
  `gh label list --repo <org>/<repo> --limit 100`.

### 2. Body = problem statement only

**Temp body files are NOT hard-wrapped.** Author the `--body-file` / heredoc in
semantic line breaks (one sentence per line, no 80-col wrap). GitHub joins
consecutive non-blank lines into one flowing paragraph, so it reads naturally —
and a one-sentence edit only churns that one line in the diff instead of
reflowing the whole block. Never run `nix fmt` / `mdformat` over a temp body
file.

Keep the body a clean problem statement (Description, reproduction steps,
affected version, impact). Post root-cause / investigation findings as a
**comment** (`gh issue comment <N> --repo <org>/<repo> --body-file <file>`), not
in the body — the body must stay stable for triage. An issue is a clean
conversation for any reader — human or another agent — not the agent's notebook:
post only concluded findings and the questions that need an answer, never raw
reasoning or status chatter. Interim comments may be deleted once the thread
converges.

Include acceptance criteria as a `- [ ]` tasklist, each item phrased so a
command can decide it — this is the work item's gate ledger (unlazy method):
`todo` mirrors it in-session (working copy), the issue is the record. An item is
done only once its check ran, never from memory; a genuinely impossible
criterion is struck with a comment, never silently dropped. Candidate solutions
do NOT go in the tasklist or body — they are comments. The body carries a
**References** section: official material (official documentation, linked
issues/PRs, commits, changelogs, specs) attesting a potential solution or adding
context about the problem statement. The agent may post additional material as
comments (`gh issue comment`) to help steer resolution toward a solution. Proof
of the solution itself belongs in the PR, not the issue. The issue closes
deliberately — ledger verified N of N after the final merge — never by a
merge-time auto-close keyword unless the PR is explicitly one-to-one with the
issue.

### 3. Apply triage metadata

Delegate to `sk-issue-triage` (#N): it enumerates the repo's available metadata
and sets each empty, determinable field — labels, assignee, milestone, project.
The rules (natural-language label inference, additive `--add-label`,
milestone-by-type) live in `sk-issue-triage`; do not re-derive them here.

## Pitfalls

- Targeting the wrong repo for issues — always use the org repo.
- Rewriting the body with findings — findings belong in a comment.
- Inventing labels the repo doesn't have — verify with `gh label list` first.
- English only; don't carry over cpn's French templates.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

Confirm title + label are set and the issue lives in the org repo.

## See also

- `sk-discussion` — the pre-issue stage when the problem is not yet converged.
- `sk-pr` — the solver; links back via `Related:` without auto-close.
- `sk-issue-refine` — the iteration loop extracted from this skill; after the
  issue exists, use it to resolve open questions within the issue via comments
  (research + candidate solutions) until the acceptance criteria converge.
- `cpn-issue` — French twin with cloud-pi-native issue templates.
- `sk-issue-triage` — assigns issue metadata (labels, assignee, milestone,
  project); run it after creation.
