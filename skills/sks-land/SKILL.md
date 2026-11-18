---
name: sks-land
description:
  Use when landing a target-org PR after reconciliation (sks-pr-resolve) and
  review approval gates pass; closes the linked issue deliberately.
version: 0.4.1
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - pull-requests
      - merge
    related_skills:
      - sks-pr-resolve
      - sks-pr
      - sks-pr-ready
      - sks-sudo
      - sks-issue
      - sks-review
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# PR Landing

Land an org PR only after `sks-pr-resolve` **reconciled** it and a human
approving review is in place — protect `main`. Scope:
`references/shikanime.md`. Not for opening (`sks-pr`), review
(`sks-review`), the draft→ready flip (`sks-pr-ready`), reconciling
(`sks-pr-resolve`), or direct "push to main".
This skill only lands.

## When to Use

- "Land an org PR after DoD gates pass."
- "Close an issue deliberately after merge (verify N-of-N)."
- "Run post-merge sync (docs, downstream rebases)."

## Pre-landing gates

Five gates, each with its check command and BLOCKED verdict: triaged
issue and PR, DoD discharged from the live ledger, mandatory-approver
approval on the current head (non-bypassable), conversations
reconciled, commit/PR conventions verified — never eyeballed. The
checks live in `references/landing-gates.md`; read it before every
landing and re-verify on the current head.

## Merge

`gh pr merge --squash [--admin]`, one squash-merge per PR, base
`main` — watch and merge are two separate steps, never one chain. The
procedure (watch/merge split, `-t`/`-b` squash hygiene, stacked and
queue-enforced repos) lives in `references/landing-gates.md`.

## Post-merge

1. Verify: `gh pr view <M> --repo <org>/<repo> --json state`.
2. **Run the acceptance gate (deployment gate).** A merged PR is a claim, not a
   verified outcome — the gate runs, it is not assumed. Deploy first: resync
   for agent/skill repos, apply for infra (the repo's deploy step — org
   examples in `references/shikanime.md`). Then surface the deployed
   state and ask the user to validate it behaves as asked. Do NOT close the
   issue or report the landing complete on merge alone; only the user confirms
   the running change. If the user rejects, treat it as a reported defect: fix
   via a new PR, re-deploy, and re-request acceptance.
3. Close the issue **deliberately**: re-read the live ledger — the Gate 2
   read went stale the moment it ran —

   ```bash
   gh issue view <N> --repo <org>/<repo> --json body --jq .body
   ```

   advance met items in the issue body from verified evidence only
   (`gh issue edit <N> --repo <org>/<repo> --body-file <updated body>`),
   then close only when zero unchecked `- [ ]` items remain (impossible
   items struck with a comment per `sks-issue`, never dropped):

   ```bash
   gh issue close <N> --repo <org>/<repo> -c "Discharged by <PR URL>"
   ```

   A ledger that will not reach N/N is a reported defect, not a close.
4. Rebase downstream: if other PRs sit on top of the merged branch, rebase them
   onto the new `main` (`jj rebase -d main`).
5. **Sync the wiki (shikanime org: mandatory when the change has a wiki
   surface).** The repo wiki is the canonical home of technical docs —
   in-repo `docs/` was migrated away (machines/manifests/tailnet); never
   recreate it. If the merged PR changed anything a wiki page documents
   (architecture, ops runbooks, process, reference pages), update those
   pages in the same landing sweep: clone `<repo>.wiki.git`, edit, ONE
   commit with the org co-author trailer, push, verify local HEAD sha ==
   `git ls-remote` HEAD (guard stdin with `</dev/null`; wiki remotes
   default to `master`). Wiki pushes bypass review — accepted trade-off.
   Skip only when the change is purely internal to what the wiki does not
   cover. Full mechanics: `sks-doc`.
6. **Teardown the landing bookmark.** A merge deletes the remote branch only
   in some repo configurations — never assume it, and never read a
   "Nothing changed" push as proof: `jj bookmark delete` and `jj git push`
   remove the local bookmark and its tracking ref, and say nothing about the
   remote ref. Remove the local side, then delete the remote ref if it is
   still there:

   ```bash
   jj bookmark delete <branch>
   jj git push --remote origin
   gh api repos/<org>/<repo>/branches/<branch> >/dev/null 2>&1 \
     && gh api -X DELETE repos/<org>/<repo>/git/refs/heads/<branch>
   ```

   The first call is the check: it exits 0 only while the branch exists, so
   the deletion runs exactly when it is needed. A stale merged branch feeds
   the stale-branch audit surface.
7. **Drop the isolated workspace** if you used one. Landing is a remote
   `gh pr merge`; the local checkout that held the change is then dead weight.
   sks-land never auto-deletes a workspace — remove it deliberately:

   ```bash
   jj workspace forget <name>
   rm -rf <path>
   ```

   `forget` takes the workspace _name_ (from `jj workspace list`), not the path.

## Pitfalls

Landing pitfalls — stack async merges, deleted base branches, fetch
abandonment, queue enrollment hangs, stale approvals after a push —
live in `references/landing-gates.md`.

## Verification Checklist

- [ ] Issue tasklist N/N checked with evidence.
- [ ] Mandatory approver approval on head (non-bypassable;
      `references/shikanime.md`); `sks-review`
      approval; human review where protection requires.
- [ ] All conversations reconciled (`sks-pr-resolve`).
- [ ] PR history clean AND relevant: every commit a logical unit with an
      imperative ≤ 72-char subject, no `fixup`/`wip`/jj artifacts; restructure
      (`jj squash`/`split`/`rebase`) before landing if not (`sks-pr-resolve`
      pre-gate).
- [ ] `sks-commit` + `sks-pr` conventions verified (subject imperative, PR title
      parity).
- [ ] CI green.
- [ ] Watch and merge ran as separate steps (no `watch && merge` background
      chain); gates re-verified on the head that merged.
- [ ] Merged via
      `gh pr merge --squash [--admin if protection blocks     self-approval]`
      (lone or stacked — one squash-merge per PR, base `main`).
- [ ] Issue closed deliberately with rationale.
- [ ] Landing bookmark removed locally and reconciled on origin.
- [ ] Board card flipped to `Done` (`sks-project`) after `mergedAt`
      is confirmed live.
- [ ] User accepted the deployed change (manual acceptance gate, post-merge
      step 2) — merge alone is not the end state.
- [ ] Wiki pages synced when the change touched documented behavior
      (post-merge step 5, shikanime org).

## Verification

```bash
gh pr view "$N" --repo "$R" --json state,mergeCommit,baseRefName
gh pr checks "$N" --repo "$R"   # all green before merge; bookmark absent after
```

## Repo-specific notes

Read `references/cloud-pi-native.md` when landing in a cloud-pi-native
repo (Gate 5 flips, SonarQube gate, French post-merge rationale).

## See also

- `sks-investigate` — root-cause research before any fix.
- `sks-commit`, `sks-pr` — the conventions Gate 5 enforces before merge.
- `sks-pr-ready` — the draft→ready flip that precedes the human approval.
- `sks-tldr` — the landing report block, after user confirmation.
