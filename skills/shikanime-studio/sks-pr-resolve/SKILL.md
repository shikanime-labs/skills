---
name: sks-pr-resolve
description:
  Use when resolving a shikanime PR's review conversations, checking the DoD
  ledger, and reconciling before merge (no merge itself).
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - review-threads
      - reconcile
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr-review
      - sks-pr
      - sks-land
      - sks-doc
      - sks-issue
platforms:
  - linux
  - macos
---

# Shikanime Org PR Resolution (no merge)

Reconcile a PR in `shikanime-labs/*`/`shikanime-studio/*`: enumerate review
conversations, check the linked issue DoD ledger, report approval/CI. **Never
lands the PR** — that is `sks-land`.

## When to Use

- "Resolve the suggestions on PR #M", "clear the review threads on #M".
- "Is PR #M ready to land?" — reconcile and report, no merge.
- Pre-landing cleanup before handing off to `sks-land`.

Not for opening (`sks-pr`), reviewing (`sks-pr-review`), merging (`sks-land`).

## Gates

### Gate 1 — DoD ledger

Criteria = the `- [ ]` tasklist in the linked issue body (see `sks-issue`);
verify each against diff/CI.

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body   # read the tasklist
gh pr view <M> --repo <org>/<repo> --json body,state --jq .body
```

- Unchecked box ≠ done — report it, never silently mark done.
- If met, check the box (`gh issue edit` or API) with evidence in a comment
  first.
- No linked issue → stop: link one (`sks-issue`) or get explicit ledger-free
  confirmation.
- **No merge here** — this gate only reports; `sks-land` acts.

### Gate 2 — Approval + CI (report only)

`sks-pr-review` must have run on the final head commit and approved. Re-review
if new commits landed after the last review. Check approval via the query in
`references/resolve.md`.

- Where branch protection blocks self-approval (e.g. `shikanime-labs/skills`,
  `nix-containers`), a verbal `lgtm` from the user satisfies this gate — merge
  stays in `sks-land` (`gh pr merge --squash --admin`).
- CI: `gh pr checks <M> --repo <org>/<repo>`.

### Gate 3 — Conversations reconciled (core)

Every inline review thread must be reconciled. Enumerate threads and resolve
them with the GraphQL in `references/resolve.md`.

For each **unresolved** thread:

- **Pertinent + in ledger** — verify diff/CI addresses it; resolve, else flag
  (blocks `sks-land`).
- **Pertinent + not in ledger** — add to issue tasklist (Gate 1), resolve if
  diff already covers it.
- **Not pertinent** — post one comment with the rationale, then resolve. Never
  resolve silently.

Outdated (`isOutdated`) uncontested threads may be resolved without code change;
note supersession in the comment.

Issue-level discussion and PR comments are **out of scope** — only inline review
threads gate via `isResolved`.

## Output (hand back)

Readiness verdict:

- Ledger: N of N satisfied, listing open items.
- Approval: `sks-pr-review` approval on current head (or verbal `lgtm` for
  `sks-land`).
- Conversations: every thread resolved with one-line rationale, or list needing
  author decision.
- CI: green / pending / failing.
- Docs: flag ops/architecture changes for post-land `sks-doc` update.

Then stop — merging is `sks-land`'s job.

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.
