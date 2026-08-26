---
name: issue
description:
  "Use when opening a GitHub issue in shikanime-labs or cloud-pi-native:
  org-aware language/repo/convention via references/<org>.md, body as a stable
  problem statement with a command-decidable acceptance ledger."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - shikanime-labs
      - cloud-pi-native
      - workflow
    related_skills:
      - issue-refine
      - issue-triage
      - pr
    references:
      - references/shikanime.md
      - references/cloud-pi-native.md
platforms:
  - linux
  - macos
  - windows
---

# Issue Creation (composable)

Open issues in a shikanime-family repo. One base skill serves both orgs; the
only variation is org policy, loaded from `references/<org>.md` (the standard
skills reference folder). The 14 lifecycle capabilities duplicated as
`sks-*`/`cpn-*` pairs collapse to one base skill each; each references its
org files instead of copying the body.

## Reference selection

Resolve the org from the target repo, then load the matching reference:

- `shikanime-labs/*` or `shikanime-studio/*` → `references/shikanime.md`
- `cloud-pi-native/console` → `references/cloud-pi-native.md`

The reference supplies every org-specific value (language, target repo, commit
convention, title prefix, co-author trailer, label defaults). This skill holds
only the shared procedure below.

## When to Use

- "Open an issue on <repo>."
- "Track a problem as a shikanime-family GitHub issue."

## Procedure

### 0. Check for existing issues

```bash
gh issue list --repo <target_repo> --state all --search "<keywords>" --limit 10
```

If a match exists, surface `#N` and confirm reuse before creating.

### 1. Create

```bash
gh issue create --repo <target_repo> --title "<title>" --label <type> --body "..."
```

Apply the org's title prefix (cloud-pi-native only; see its reference) and
default label. Bug → `bug`; feature → `enhancement`. Verify repo labels
first: `gh label list --repo <target_repo> --limit 100`.

### 2. Body = problem statement only

Write in the org's language (from the reference). Body = clean problem
statement (Description, reproduction, affected version, impact). Keep it
stable for triage — post root-cause / investigation findings as a **comment**
(`gh issue comment <N> --repo <target_repo> --body-file <file>`), never in the
body. Acceptance criteria are a `- [ ]` tasklist; each item must be decidable
by a command, done only once its check ran.

### 3. Triage metadata

Delegate to `issue-triage` (#N): sets type, labels, assignee, milestone,
project — only empty + derivable fields, never inventing a repo-lacking value.

## Pitfalls

- Wrong repo — always target the org repo from the reference.
- Rewriting body with findings — findings belong in a comment.
- Inventing labels the repo lacks — verify with `gh label list`.

## Verification

```bash
gh issue view <N> --repo <target_repo> --json number,title,labels
```

Confirm the title carries the org's prefix (cloud-pi-native) and the label is set.

## See also

- `issue-refine` — iterate the problem to convergence in-issue.
- `issue-triage` — metadata step.
- `pr` — derive the PR once the issue converges.
