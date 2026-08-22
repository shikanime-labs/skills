---
name: sk-pr-workflow
description:
  "Single entry point for the shikanime PR side: ensure the issue exists, open
  the org-repo PR derived from the commit, then triage immediately."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, pull-requests, shikanime-labs, shikanime-studio, workflow]
---

# Shikanime Org PR Workflow

One command for the full PR lifecycle: ensure the linked issue exists → open the
org-repo PR derived from the commit → triage immediately. This is a thin
orchestrator over `sk-issue`, `sk-pr`, and `sk-pr-triage`; it holds no
PR-creation logic of its own.

## When to Use

- "Open and set up a PR for this branch on <repo>".
- "Take this fix through to a triaged, linked PR".
- Any shikanime PR work where issue-existence, creation, and triage should all
  happen before you return control to the user.

## Procedure

### 1. Ensure the linked issue exists

If a linked issue `#N` is not already provided and converged, load `sk-issue`
(or `sk-issue-workflow` for the full create+refine+triage path) and create it
first. A PR always solves an issue — never opened alone. Verify the issue
actually matches the branch's change (`jj show <commit>`) before linking.

### 2. Open the org-repo PR

Load `sk-pr` and follow it. Push to `origin` (the org repo), open
`--head <org>:<branch>`, base `main`; derive title/body from the commit and link
with `Related: <full issue URL>` (no auto-close keyword unless explicitly
one-to-one).

On completion you have PR `#N` against the org repo.

### 3. Triage immediately after creation

Load `sk-pr-triage` and apply metadata now — labels, assignee, milestone,
project, reviewers. Apply only empty, determinable fields; never invent a value
the repo lacks.

## Gate

The PR is complete only when: it opens from `origin`, links the correct issue,
and triage metadata is set. Verify:

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

## See also

- `sk-issue` / `sk-issue-workflow` — the issue this PR must solve.
- `sk-pr` — the create step this delegates to.
- `sk-pr-triage` — the metadata step this runs immediately after creation.
