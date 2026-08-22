---
name: sk-issue-workflow
description:
  "Single entry point for the shikanime issue side: create the issue, refine the
  problem to convergence within it, then triage immediately."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, issues, shikanime-labs, shikanime-studio, workflow]
---

# Shikanime Org Issue Workflow

One command for the full issue lifecycle: create → refine → triage. This is a
thin orchestrator over `sk-issue`, `sk-issue-refine`, and `sk-issue-triage`; it
holds no issue-creation logic of its own.

## When to Use

- "Open and set up an issue on <repo>".
- "Take this problem through to a triaged issue".
- Any shikanime issue work where creation, convergence, and triage should all
  happen before you return control to the user.

## Procedure

### 1. Create the issue

Load `sk-issue` and follow it. Body = problem statement + `- [ ]` gate ledger
(command-decidable acceptance criteria); findings go in comments, not the body.

On completion you have issue `#N` in the upstream org repo.

### 2. Refine the problem within the issue

Load `sk-issue-refine` and iterate the problem _inside the issue_ until the
acceptance criteria converge: research as comments, propose candidate solutions
as comments, update the body's tasklist only when the criteria themselves
change. Skip this step only when the problem is already converged at creation
(rare).

### 3. Triage immediately after creation

Load `sk-issue-triage` and apply metadata now — labels, assignee, milestone,
project. Apply only empty, determinable fields; never invent a label the repo
lacks.

## Gate

The issue is complete only when: the body is a stable problem statement with a
converged `- [ ]` ledger, and triage metadata is set. Verify:

```bash
gh issue view <N> --repo <org>/<repo> --json number,title,labels
```

## See also

- `sk-issue` — the create step this delegates to.
- `sk-issue-refine` — the in-issue convergence loop.
- `sk-issue-triage` — the metadata step this runs immediately after creation.
