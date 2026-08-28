---
name: sks-land
description:
  Use when landing a shikanime org PR after reconciliation (sks-pr-resolve) and
  review approval gates pass; closes the linked issue deliberately.
version: 0.2.3
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
  - windows
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

**Gate 4 — `sks-commit` + `sks-pr` conventions.** Commit subject is
plain-English imperative (no `fix:`/`feat:`/`chore:` conventional prefix),
capitalized, no trailing period. PR title equals the commit subject; PR body
restates the rationale. Verify:

```bash
gh pr view <M> --repo <org>/<repo> --json commits,title,body \
  --jq '.commits[0].messageHeadline, .title, .body'
```

If the commit subject violates `sks-commit` (conventional prefix, lowercase
start, trailing period) or the PR title diverges from it, fix before merging:

```bash
jj describe -m "<plain-English subject>" \
  -m "Co-authored-by: Automata <automata@shikanime.studio>"
```

then force-push and re-verify. A doc-repo commit may carry a `doc:` prefix —
that is the `sks-commit` override for doc repos, not a violation.

## Merge procedure

Land with plain `gh pr merge` (the org removed `gh stack`). For a lone PR use
`gh pr merge --squash [--admin]`; never `gh pr merge` on a stacked PR — but
stacked PRs are landed the same way now (one squash-merge per PR, base `main`).
Never force-push. Background watcher waits for CI then merges:

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
- Stacked (multiple PRs off `main`): land each with
  `gh pr merge <PR_NUMBER> --squash --admin` in dependency order (base first).
- Branch protection needs linear history + signed commits; squash only.

## Post-merge

1. Verify: `gh pr view <M> --repo <org>/<repo> --json state`.
2. Close the issue **deliberately**: confirm tasklist N/N, then
   `gh issue close <N> --repo <org>/<repo> -c "Discharged by <PR URL>"`.
3. Rebase downstream: if other PRs sit on top of the merged branch, rebase them
   onto the new `main` (`jj rebase -d main`).
4. **Sync docs** if ops/arch/runbooks changed — edit `docs/` per `sks-doc`; skip
   if purely internal.
5. **Teardown the landing bookmark.** GitHub drops the remote branch on merge,
   but the local `jj` bookmark and its `origin` tracking ref linger and clutter
   the workspace. Remove both:

   ```bash
   jj bookmark delete <branch>
   jj git push --remote origin
   ```

   `delete` propagates to tracked remotes on the next push (no `--remote` flag).
   If `push` reports nothing changed, GitHub already removed it.
6. **Drop the isolated workspace** if you used one. Landing is a remote
   `gh pr merge`; the local checkout that held the change is then dead weight.
   sks-land never auto-deletes a workspace — remove it deliberately:

   ```bash
   jj workspace forget <name>
   rm -rf <path>
   ```

   `forget` takes the workspace _name_ (from `jj workspace list`), not the path.

## Pitfalls

- Unchecked criterion — discharge or escalate, don't merge.
- Merging a dependent stacked PR before its base lands — go in dependency order,
  base first.
- Merge after new commits without re-review — approval binds to a head commit.
- Auto-close via `Closes #N`/`Fixes #N` at merge — fires before the ledger is
  verified; close deliberately after N-of-N.
- Open threads — reconcile first via `sks-pr-resolve`.

## Verification Checklist

- [ ] Issue tasklist N/N checked with evidence.
- [ ] `sks-pr-review` approval on head; human review where protection requires.
- [ ] All conversations reconciled (`sks-pr-resolve`).
- [ ] `sks-commit` + `sks-pr` conventions verified (subject imperative, PR title
      parity).
- [ ] CI green.
- [ ] Merged via
      `gh pr merge --squash [--admin if protection blocks     self-approval]`
      (lone or stacked — one squash-merge per PR, base `main`).
- [ ] Issue closed deliberately with rationale.
- [ ] Landing bookmark removed locally and reconciled on origin.

## Verification

```bash
gh pr view "$N" --repo "$R" --json state,mergeCommit,baseRefName
gh pr checks "$N" --repo "$R"   # all green before merge; bookmark absent after
```

## See also

- `sks-investigate` — root-cause research before any fix.
- `sks-commit`, `sks-pr` — the conventions Gate 4 enforces before merge.
