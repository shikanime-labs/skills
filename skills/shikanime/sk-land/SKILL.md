---
name: sk-land
description:
  "Merge a shikanime org PR after reconciliation (sk-pr-resolve) and review
  approval gates pass; close the linked issue deliberately."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, pull-requests, merge, shikanime-labs, shikanime-studio]
    related_skills: [sk-pr-resolve, sk-pr, sk-issue, sk-code-review, sk-async, sk-wiki]
---

# Shikanime Org PR Landing

Merge a pull request against `shikanime-labs/*` and `shikanime-studio/*` after
two gates pass: the PR is **reconciled** and review approval is in place. A
human approving review is the gate before landing (protect `main`).

Reconciliation (review threads, DoD ledger, approval/CI state) lives in
`sk-pr-resolve` — run it first and hand back a readiness verdict. This skill
only lands; it does not re-do resolution.

## When to Use

- "Land / merge PR #N" in a shikanime-owned repo.
- PR already reconciled via `sk-pr-resolve`, now ready to merge.

Don't use for: opening the PR (`sk-pr`), the review itself (`sk-code-review`),
reconciling threads (`sk-pr-resolve`), or direct "push to main" landings (that
bypasses this skill's gates by explicit user override).

## Pre-landing gates (must already be satisfied)

### Gate 1 — Definition of done discharged

The linked issue's acceptance criteria (`- [ ]` tasklist, see `sk-issue`) are
all checked or verifiably satisfied. Verify is owned by `sk-pr-resolve`; this
skill trusts its verdict but re-reads the ledger for a final check:

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body
```

An unchecked box blocks merge — discharge it (or escalate) before continuing.

### Gate 2 — `sk-code-review` approval

`sk-code-review` approved the current head commit; re-review if new commits
landed after. CI green: `gh pr checks <M> --repo <org>/<repo>`.

```bash
gh pr view <M> --repo <org>/<repo> --json reviews,headRefOid \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

- Agent review is pre-flight; **a human approving review is the gate** before
  landing. If only the agent reviewed and protection demands a human, request
  one and stop.
- Where branch protection blocks self-approval (e.g. `shikanime-labs/skills`,
  `nix-containers`), a verbal `lgtm` from the user satisfies Gate 2 — land via
  `gh pr merge --squash --admin` (see Merge procedure). `--admin` is what
  bypasses the protection; no separate human review is then required.

### Gate 3 — Conversations reconciled

Every inline review thread resolved. This is `sk-pr-resolve`'s core output; if
you have not run it, do so now and return. Skip only if `sk-pr-resolve` already
reported all threads reconciled.

## Merge procedure

Stacked branches land via `gh stack` (never `gh pr merge` on a stacked PR —
poisoned commits); lone branches may use `gh pr merge`. Never force-push stacked
branches.

Land via a background watcher — the whole skill is fire-and-forget; never
block inline on CI. The gates (1 to 3) must already be satisfied: land only a
PR whose ledger, review approval, and threads are closed. Launch a background
watcher that waits for CI then merges.

```bash
gh run watch --exit-status --repo <org>/<repo> \
  $(gh run list --repo <org>/<repo> --branch <branch> --limit 1 \
    --json databaseId -q '.[0].databaseId') \
  && gh pr merge <M> --repo <org>/<repo> --squash --rebase
```

Run it as a background terminal with notify_on_complete so you are alerted on
land. Re-run the command after a fresh push to pick up the new run id. A
failing run exits non-zero and skips the merge (red never lands).

> Gotcha (caught in PR #96/#98): `gh run watch <run-id>` returns exit 0 even
> when the watched run FAILS — always pass `--exit-status` or the PR merges on
> red. Also, `gh run watch` takes a `<run-id>`, there is no `--branch` flag;
> resolve it via `gh run list --repo <org>/<repo> --branch <branch> --limit 1
> --json databaseId -q '.[0].databaseId'`.

- Lone branch, self-approval blocked (after a verbal lgtm): swap --rebase for
  --admin (protection rejects a non-admin merge):
  `gh run watch --exit-status --repo <org>/<repo> $(gh run list --repo <org>/<repo> --branch <branch> --limit 1 --json databaseId -q '.[0].databaseId') && gh pr merge <M> --repo <org>/<repo> --squash --admin`
- Stacked (see sk-async / sk-pr): run `gh stack merge <PR_NUMBER> --yes --squash`
  in a background terminal with notify_on_complete; it blocks until the stack
  merges.
- Branch protection requires linear history + signed commits; squash merge only.

## Post-merge

1. Verify the merge landed: `gh pr view <M> --repo <org>/<repo> --json state`.
2. Close the linked issue **deliberately** (the PR avoids auto-close keywords
   per `sk-pr`): confirm tasklist N of N, then
   `gh issue close <N> --repo <org>/<repo> -c "Discharged by <PR URL>"`.
3. Rebase downstream stacked branches (`gh stack rebase`) if any sit on top.
4. **Sync the wiki if the change alters ops/architecture/runbooks** — a merged
   change makes the live `Home`/`Architecture`/`Runbook`/`Troubleshooting` pages
   stale the moment it ships. Edit the in-repo `wiki/` source and sync to
   `<repo>.wiki.git` per `sk-wiki`. Skip when the change is purely internal and
   already covered by the closed issue.

## Pitfalls

- Merging with an unchecked acceptance criterion — the ledger is the contract;
  discharge or escalate, don't merge.
- `gh pr merge` on a stacked PR — use `gh stack merge`.
- Merging after new commits without re-review — the approval is bound to a head
  commit.
- Auto-closing via `Closes #N` at merge time — close the issue deliberately
  after verifying the ledger.
- Merging with open review threads — reconcile first via `sk-pr-resolve`.

## Verification Checklist

- [ ] Linked issue tasklist: every criterion checked with evidence.
- [ ] `sk-code-review` approval on the current head commit; human review where
      protection requires it.
- [ ] Every review conversation reconciled (via `sk-pr-resolve`).
- [ ] CI checks green.
- [ ] Merged via `gh stack merge` (stacked) or
      `gh pr merge --squash     [--admin if protection blocks self-approval]`
      (lone), per repo override.
- [ ] Issue closed deliberately with a rationale comment.
