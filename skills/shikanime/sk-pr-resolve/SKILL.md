---
name: sk-pr-resolve
description:
  "Resolve a shikanime PR's review conversations, check the DoD ledger, and
  surface approval/CI state WITHOUT merging it — pre-flight reconciliation
  extracted from sk-land."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      [
        github,
        pull-requests,
        review-threads,
        reconcile,
        shikanime-labs,
        shikanime-studio,
      ]
    related_skills: [sk-land, sk-pr, sk-issue, sk-code-review, sk-async, sk-wiki]
---

# Shikanime Org PR Resolution (no merge)

Reconcile a pull request against `shikanime-labs/*` and `shikanime-studio/*`:
enumerate review conversations, check the linked issue's definition-of-done
ledger, and report approval/CI state. **This skill never lands the PR** — for
that, see `sk-land`. Use it to clear review threads, close out the ledger, and
hand back a readiness verdict the user can act on.

## When to Use

- "Resolve the suggestions on PR #M", "clear the review threads on #M".
- "Is PR #M ready to land?" — reconcile and report, without merging.
- Pre-landing cleanup: drive every thread to a resolved state and the ledger to
  N-of-N before handing off to `sk-land`.

Don't use for: opening the PR (`sk-pr`), the review itself (`sk-code-review`),
or merging (`sk-land`). This skill stops at reconciliation.

## Gates reconciled (extracted from sk-land)

### Gate 1 — Definition of done ledger

The linked issue's acceptance criteria are the `- [ ]` tasklist in the issue
body (see `sk-issue`). Verify each item against the actual diff/CI.

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body   # read the tasklist
gh pr view <M> --repo <org>/<repo> --json body,state --jq .body
```

- An unchecked box is open work — report it, do not silently mark done.
- If the criterion is genuinely met, check the box (`gh issue edit` or the API)
  with evidence in a comment first.
- If the PR has no linked issue, stop and ask: link one (`sk-issue`) or get
  explicit user confirmation this is ledger-free.
- **No merge here.** This gate only reports ledger status; `sk-land` acts on it.

### Gate 2 — Review approval + CI (report only)

`sk-code-review` must have run on the final head commit and returned an
approving verdict. Re-review is required if new commits landed after the last
review.

```bash
gh pr view <M> --repo <org>/<repo> --json reviews,headRefOid \
  --jq '{head: .headRefOid,
         reviews: [.reviews[] | {state: .state, submittedAt}]}' \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

- Where branch protection blocks self-approval (e.g. `shikanime-labs/skills`,
  `nix-containers`), a verbal `lgtm` from the user satisfies this gate — but the
  merge itself stays in `sk-land` (`gh pr merge --squash --admin`).
- CI checks: `gh pr checks <M> --repo <org>/<repo>`.

### Gate 3 — Conversations reconciled (the core of this skill)

Every review conversation (inline thread) on the PR must be reconciled — an open
thread is unfinished review. Enumerate them:

```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$num:Int!) {
    repository(owner:$owner,name:$repo){
      pullRequest(number:$num){
        reviewThreads(first:100){
          nodes{
            id
            isResolved
            isOutdated
            comments(first:1){
              nodes{ body author{login} path line diffHunk }
            }
          }
        }
      }
    }
  }' -f owner=<org> -f repo=<repo> -F num=<M>
```

For each **unresolved** thread, judge the suggestion and act:

- **Pertinent + already in the ledger** — verify the diff/CI addresses it; if so
  resolve the thread, if not flag it (open criterion, blocks merge in
  `sk-land`).
- **Pertinent + not yet in the ledger** — add the item to the linked issue's
  acceptance-criteria tasklist (Gate 1), note it must be addressed in the diff,
  then resolve the thread if the diff already covers it.
- **Not pertinent** — discard: post one comment stating the rationale (out of
  scope / handled elsewhere / not applicable), then resolve. Never resolve
  silently; a discarded suggestion still owes a one-line why.

Outdated threads (`isOutdated`) that are otherwise uncontested may be resolved
without a code change; note the supersession in the resolution comment.

```bash
# Resolve a reconciled thread:
gh api graphql -f query='
  mutation($id:ID!){
    resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
  }' -f id=<threadId>
```

Issue-level discussion and PR comments are **out of scope** here — only inline
review threads gate via `isResolved`.

## Output (hand back to the user)

A readiness verdict covering:

- Ledger: N of N criteria satisfied, listing any open items.
- Approval: `sk-code-review` approval present on the current head commit (or
  human/verbal `lgtm` pending the `sk-land` merge).
- Conversations: every thread resolved with one-line rationale, or a list of
  threads still requiring the author's decision.
- CI: green / pending / failing.
- Wiki: flag any ops/architecture change surfaced during reconciliation for a
  post-land `sk-wiki` update (runbook / troubleshooting / architecture page).

Then stop. Merging is `sk-land`'s job.

## Pitfalls

- Resolving a thread silently — discarded suggestions owe a one-line why.
- Trusting a checkbox without evidence — verify each criterion against the diff.
- Reconciling after new commits without re-review — the approval is bound to a
  head commit.
- Treating issue/PR comments as gate threads — only inline review threads gate.
- Merging from this skill — it only reconciles; defer landing to `sk-land`.

## Verification Checklist

- [ ] Linked issue tasklist checked: every criterion verified against diff/CI.
- [ ] `sk-code-review` approval on the current head commit; human review where
      protection requires it (or verbal `lgtm` recorded for `sk-land`).
- [ ] Every review conversation reconciled: pertinent addressed/added to ledger,
      non-pertinent discarded with rationale, all threads resolved.
- [ ] CI checks reported.
- [ ] PR NOT merged — landing deferred to `sk-land`.
