---
name: sk-land
description:
  "Merge a PR in shikanime-labs and shikanime-studio after verifying the
  definition of done and review approval."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, pull-requests, merge, shikanime-labs, shikanime-studio]
    related_skills: [sk-pr, sk-issue, sk-code-review, sk-async]
---

# Shikanime Org PR Landing

Merge a pull request against `shikanime-labs/*` and `shikanime-studio/*` only
after two gates pass: the linked issue's definition of done (acceptance criteria
tasklist) is fully discharged, and `sk-code-review` has produced an approving
review. A human approving review is the gate before landing (protect `main`).

## When to Use

- "Land / merge PR #N" in a shikanime-owned repo.
- Any PR merge where the issue's acceptance criteria must be verified first.

Don't use for: opening the PR (`sk-pr`), the review itself (`sk-code-review`),
or direct "push to main" landings (that bypasses this skill's gates by explicit
user override).

## Gates (all mandatory, in order)

### Gate 1 — Definition of done discharged

The linked issue's acceptance criteria are the `- [ ]` tasklist in the issue
body (see `sk-issue`). Every item must be checked — or verifiably satisfied —
before merge.

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body   # read the tasklist
gh pr view <M> --repo <org>/<repo> --json body,state --jq .body
```

- Verify each criterion against the actual diff/CI, not the checkbox text.
- An unchecked box blocks merge. If the criterion is genuinely met, check the
  box (`gh issue edit` or the API) with evidence in a comment first — never
  merge against an open ledger.
- If the PR has no linked issue, stop and ask: either link one (`sk-issue`) or
  get explicit user confirmation this is ledger-free.

### Gate 2 — sk-code-review approval

`sk-code-review` must have run on the final head commit and returned an
approving verdict (inline per-line comments + suggested commit message, per its
doctrine). Re-review is required if new commits landed after the last review.

```bash
gh pr view <M> --repo <org>/<repo> --json reviews,headRefOid \
  --jq '{head: .headRefOid,
         reviews: [.reviews[] | {state: .state, submittedAt}]}' \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

- Agent review is pre-flight; **a human approving review is the gate** before
  landing. If only the agent reviewed and branch protection demands a human,
  request one and stop.
- CI checks green: `gh pr checks <M> --repo <org>/<repo>`.

## Merge procedure

Stacked branches land via `gh stack` (never `gh pr merge` on a stacked PR —
poisoned commits); lone branches may use `gh pr merge`. Never force-push stacked
branches.

```bash
# Stacked (see sk-async / sk-pr):
gh stack merge <PR_NUMBER> --yes --squash

# Lone branch:
gh pr merge <M> --repo <org>/<repo> --squash --rebase   # squash+rebase only
```

- Repo-specific overrides win: e.g. `nix-containers` requires
  `gh pr merge --squash --admin`.
- Branch protection requires linear history + signed commits; squash+rebase
  merge only.

## Post-merge

1. Verify the merge landed: `gh pr view <M> --repo <org>/<repo> --json state`.
2. Close the linked issue **deliberately** (the PR avoids auto-close keywords
   per `sk-pr`): confirm tasklist N of N, then
   `gh issue close <N> --repo <org>/<repo> -c "Discharged by <PR URL>"`.
3. Rebase downstream stacked branches (`gh stack rebase`) if any sit on top.

## Pitfalls

- Merging with an unchecked acceptance criterion — the ledger is the contract;
  discharge or escalate, don't merge.
- Trusting a checkbox without evidence — verify each criterion against the
  diff/CI.
- `gh pr merge` on a stacked PR — use `gh stack merge`.
- Merging after new commits without re-review — the approval is bound to a head
  commit.
- Auto-closing via `Closes #N` at merge time — close the issue deliberately
  after verifying the ledger.

## Verification Checklist

- [ ] Linked issue tasklist: every criterion checked with evidence.
- [ ] `sk-code-review` approval on the current head commit; human review where
      protection requires it.
- [ ] CI checks green.
- [ ] Merged via `gh stack merge` (stacked) or `gh pr merge --squash` (lone),
      per repo override.
- [ ] Issue closed deliberately with a rationale comment.
