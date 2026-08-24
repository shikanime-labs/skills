---
name: sks-land
description:
  Use when landing a shikanime org PR after reconciliation (sks-pr-resolve) and
  review approval gates pass; closes the linked issue deliberately.
version: 0.2.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - merge
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr-resolve
      - sks-pr
      - sks-issue
      - sks-pr-review
      - sks-doc
platforms:
  - linux
  - macos
---

# Shikanime Org PR Landing

Land a `shikanime-labs/*` / `shikanime-studio/*` PR only after `sks-pr-resolve`
**reconciled** it and a human approving review is in place — protect `main`. Not
for opening (`sks-pr`), review (`sks-pr-review`), reconciling
(`sks-pr-resolve`), or direct "push to main". This skill only lands.

## When to Use

- "Land a shikanime PR after DoD gates pass."
- "Close an issue deliberately after merge (verify N-of-N)."
- "Run post-merge sync (docs, downstream rebases)."

## Pre-landing gates (must already hold)

**Gate 1 — DoD discharged.** Issue criteria (`- [ ]`, `sks-issue`) all checked;
re-read the ledger (unchecked box blocks merge):

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body
```

**Gate 2 — `sks-pr-review` approval.** Approved on current head; re-review if
new commits landed. CI green: `gh pr checks <M> --repo <org>/<repo>`.

```bash
gh pr view <M> --repo <org>/<repo> --json reviews,headRefOid \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

Agent review is pre-flight; **a human approving review is the gate.** Where
branch protection blocks self-approval (e.g. `shikanime-labs/skills`,
`nix-containers`), a verbal `lgtm` from the user satisfies Gate 2 — land via
`gh pr merge --squash --admin` (see Merge procedure). `--admin` is what bypasses
the protection; no separate human review is then required.

**Gate 3 — Conversations reconciled.** Every inline thread resolved
(`sks-pr-resolve`'s output). If not run, do so now; if it already reported all
reconciled, skip.

## Merge procedure

Stacked via `gh stack` (never `gh pr merge` on a stacked PR — poisoned commits);
lone may use `gh pr merge`. Never force-push stacked. Background watcher waits
for CI then merges:

```bash
gh run watch --exit-status --repo <org>/<repo> \
  $(gh run list --repo <org>/<repo> --branch <branch> --limit 1 \
    --json databaseId -q '.[0].databaseId') \
  && gh pr merge <M> --repo <org>/<repo> --squash --rebase \
       -b "$(cat <<'EOF'
<body: one coherent change, no jj * bullets / --------- separators; trailers
only: Related: [url], Signed-off-by: [user], Co-authored-by: Automata
<automata@shikanime.studio>

Co-authored-by: Automata <automata@shikanime.studio>
EOF
)"
```

Run in a background terminal with notify_on_complete; re-run after each fresh
push. A failing run exits non-zero and skips merge (red never lands).

> Gotcha: `gh run watch <run-id>` exits 0 even on FAIL — always pass
> `--exit-status`. It takes a `<run-id>` (no `--branch`); resolve via
> `gh run list`.

- **Squash hygiene**: pass `-b` (see `sks-commit`); `gh pr merge --squash` has
  **no `-m`** — the PR title is the subject. Never auto-concatenate branch
  commits (leaks jj's `*` / `---------` artifacts). One subject + correct
  trailers.
- Lone, self-approval blocked (after verbal lgtm): use `--squash --admin`.
- Stacked (`sks-async`/`sks-pr`): `gh stack merge <PR_NUMBER> --yes --squash`
  (background, notify_on_complete).
- Branch protection needs linear history + signed commits; squash only.

## Post-merge

1. Verify: `gh pr view <M> --repo <org>/<repo> --json state`.
2. Close the issue **deliberately** (`sks-pr` avoids auto-close): confirm
   tasklist N/N, then
   `gh issue close <N> --repo <org>/<repo> -c "Discharged by <PR URL>"`.
3. Rebase downstream: `gh stack rebase` if any sit on top.
4. **Sync docs** if ops/arch/runbooks changed — edit `docs/` per `sks-doc`; skip
   if purely internal.

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification Checklist

- [ ] Issue tasklist N/N checked with evidence.
- [ ] `sks-pr-review` approval on head; human review where protection
      requires.
- [ ] All conversations reconciled (`sks-pr-resolve`).
- [ ] CI green.
- [ ] Merged via `gh stack merge` (stacked) or
      `gh pr merge --squash [--admin if protection blocks self-approval]`
      (lone).
- [ ] Issue closed deliberately with rationale.
