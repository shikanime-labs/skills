---
name: sk-pr-workflow
description:
  "Single entry point for the shikanime PR side: ensure the issue exists, open
  the org-repo PR derived from the commit, then triage immediately."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, pull-requests, shikanime-labs, shikanime-studio, workflow]
---

# Shikanime Org PR Workflow

Orchestrator over `sk-issue`/`sk-pr`/`sk-pr-triage`: issue → PR → triage.

## Procedure

### 1. Ensure linked issue exists

If `#N` not provided/converged, load `sk-issue` (or `sk-issue-workflow`) and
create first. A PR never opens without an issue. Verify match via
`jj show <commit>` before linking.

### 2. Open the org-repo PR

Load `sk-pr`. Push to `origin` (org repo), open `--head <org>:<branch>`, base
`main`; link `Related: <full issue URL>` (no auto-close keyword unless
explicitly one-to-one).

### 3. Triage immediately

Load `sk-pr-triage`; apply metadata now. Apply only empty/determinable fields;
never invent a value the repo lacks.

## Gate

Done when opened from `origin`, links issue, triage set. Verify:

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

## See also

- `sk-issue`/`sk-issue-workflow` — issue to solve.
- `sk-pr` — create step.
- `sk-pr-triage` — metadata step.
