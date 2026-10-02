---
name: sks-fleet
description:
  "Use when maintaining many open stacked PRs on one org repo: git stack
  restacks, fleet-wide review sweeps, history rewrites, and CI polling
  across dozens of branches."
version: 0.1.0
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - stacked-prs
      - fleet
    related_skills:
      - sks-restack
      - sks-land
      - sks-pr-resolve
platforms:
  - linux
  - macos
---

# Fleet maintenance

Dozens of open PRs on one repo, stacked base-to-child, maintained by one
agent. Single-PR workflows live in `sks-pr`; jj-based restacking in
`sks-restack`. This skill is the git-side fleet tier.

## Roster

Keep a roster file (branch, PR number, base branch, stack root). Stacks
branch child-from-base; verify claimed topology with
`git merge-base --is-ancestor` before trusting it — a child may branch from
the root, not the tip.

## Restack a stack

```bash
git fetch origin
git checkout -B <child> origin/<child>
GIT_EDITOR=true git \
  -c user.name='<author>' -c user.email='<author-email>' \
  -c core.hooksPath=/dev/null \
  -c rebase.committerDateIsAuthorDate=true \
  rebase origin/<base>
git merge-base --is-ancestor origin/<base> HEAD && echo ancestor-ok
git push origin HEAD:<child> --force-with-lease=<child>:<known-sha>
```

- `rebase.committerDateIsAuthorDate=true` is a config flag; the
  `--committer-date=is-author-date` CLI spelling errors out.
- Pin the lease to the fetched SHA: a concurrent session force-pushing the
  same branch must fail your push, not silently lose its commit. On lease
  rejection: fetch, diff, cherry-pick your commit onto the new head.
- Conflict rule: keep the side with the newer semantic content — the
  child's updated spec beats the parent's stale copy of the same file.
  After resolving, run the module's targeted tests before pushing.

## Fleet review sweep

Enumerate every open PR by author, then per PR: `reviewDecision`, open
review threads, CI state. Mechanics in `references/github-fleet-api.md`.

- Resolve fixed threads via GraphQL `resolveReviewThread`; a reply
  precedes resolution. Target zero unresolved fleet-wide.
- The PR author cannot submit REQUEST_CHANGES; post `event=COMMENT` with
  the blocking tag instead.
- Approvals are head-bound. After every force-push, re-request review;
  an approval on an old head does not count.

## History rewrite across all branches

Rewriting trailers or identities fleet-wide: `git filter-branch` with a
msg-filter (case-match existing trailers — a case-insensitive match eats
stdin) and env-filter. Before pushing:

1. Commit count per branch preserved.
2. No duplicated or dropped commits (range-diff against the pre-rewrite
   tip).
3. Every branch force-pushed with a pinned lease.

Disclose the rewrite to maintainers with local checkouts — they must
hard-reset.

## CI

- Aggregate: `gh pr checks <N> --repo <R> | awk -F'\t' 'NR>1{c[$2]++}
  END{for(k in c) printf "%s=%d ",k,c[k]; print ""}'`.
- CI is authoritative over local runs when worktrees cannot run the full
  suite (broken pnpm symlinks, missing codegen).
- paths-filter workflows stay silent on filtered pushes: dispatch manually
  `gh workflow run <ci>.yml --ref <branch>`.
- Known flake, already triaged: `gh run rerun <id> --failed`, do not
  "fix" it.

## Boundaries

Opening a single PR: `sks-pr`. Landing: `sks-land` (mandatory approver
gate). jj restacking: `sks-restack`. Never mix a rewrite with content
changes — separate rounds, separate verification.
