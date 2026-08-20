---
name: sk-issue
description: "Open issues in shikanime-labs and shikanime-studio."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Issues, shikanime-labs, shikanime-studio]
---

# Shikanime Org Issue Creation

Create GitHub issues in `shikanime-labs/*` and `shikanime-studio/*` repos.
English bodies (no French). Issue-first is encouraged: create the issue before
the PR, then link the PR to it (see `sk-pr`).

## When to Use

- "Open an issue on <repo>" / "create a bug/feature ticket".
- Any issue creation in a shikanime-owned repo.

## Prerequisites

- `gh` authenticated against the canonical org remote (shikanime-labs or
  shikanime-studio). Personal forks may have Issues disabled — always target the
  upstream org repo.
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

Keep the body a clean problem statement (Description, reproduction steps,
affected version, impact). Post root-cause / investigation findings as a
**comment** (`gh issue comment <N> --repo <org>/<repo> --body-file <file>`), not
in the body — the body must stay stable for triage.

Include acceptance criteria as a `- [ ]` tasklist, each item phrased so a
command can decide it — this is the work item's gate ledger (unlazy method):
`todo` mirrors it in-session (working copy), the issue is the record. An item is
done only once its check ran, never from memory; a genuinely impossible
criterion is struck with a comment, never silently dropped. Candidate solutions
do NOT go in the tasklist or body — they are comments. The issue closes
deliberately — ledger verified N of N after the final merge — never by a
merge-time auto-close keyword unless the PR is explicitly one-to-one with the
issue.

### 3. Triage metadata

- **Assignee**: default to active `gh` identity:

  ```bash
  ASSIGNEE=$(gh api user --jq .login)
  gh issue edit <N> --repo <org>/<repo> --add-assignee "$ASSIGNEE"
  ```

- **Labels**: set by `--label` above; add domain labels only if the repo uses
  them.
- **Project / Milestone**: only if the repo boards issues (Org Projects v2 use a
  number). Skip otherwise.

## Pitfalls

- Targeting a personal fork where Issues are disabled — use the upstream org
  repo.
- Rewriting the body with findings — findings belong in a comment.
- Inventing labels the repo doesn't have — verify with `gh label list` first.
- English only; don't carry over cpn's French templates.

## Verification

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

Confirm title + label are set and the issue lives in the upstream org repo.

## See also

- `sk-discussion` — the pre-issue stage when the problem is not yet converged.
- `sk-pr` — the solver; links back via `Related:` without auto-close.
- `cpn-issue` — French twin with cloud-pi-native issue templates.
