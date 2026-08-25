---
name: sks-pr-workflow
description:
  "Use when you need the single entry point for the shikanime PR side: ensure
  the issue exists, open, triage, and land the PR."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - shikanime-labs
      - shikanime-studio
      - workflow
    related_skills:
      - sks-pr
      - sks-pr-triage
      - sks-land
      - sks-pr-resolve
      - sks-issue-workflow
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org PR Workflow

Orchestrator over `sks-issue`/`sks-pr`/`sks-pr-triage`: issue → PR → triage.

## When to Use

- "Run the full PR side: issue → PR → triage."
- "Ensure a PR is properly linked and triaged before work starts."

## Procedure

### 1. Ensure linked issue exists

If `#N` not provided/converged, load `sks-issue` (or `sks-issue-workflow`) and
create first. A PR never opens without an issue. Verify match via
`jj show <commit>` before linking.

### 2. Open the org-repo PR

Load `sks-pr`. Push to `origin` (org repo), open `--head <org>:<branch>`, base
`main`; link `Related: <full issue URL>`.

### 3. Triage immediately

Load `sks-pr-triage`; apply metadata now. Apply only empty/determinable fields;
never invent a value the repo lacks.

## Gate

Done when opened from `origin`, links issue, triage set. Verify:

```bash
gh pr view <N> --repo <org>/<repo> --json title,baseRefName,body
```

## See also

- `sks-issue`/`sks-issue-workflow` — issue to solve.
- `sks-pr` — create step.
- `sks-pr-triage` — metadata step.
