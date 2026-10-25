---
name: sks-land
description:
  Use when landing a target-org PR after reconciliation (sks-pr-resolve) and
  review approval gates pass; closes the linked issue deliberately.
version: 0.4.0
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

## Pre-landing gates (must already hold)

**Gate 1 — issue and PR triaged.** Both sides carry complete triage
metadata (`sks-issue-triage` / `sks-pr-triage`): labels, assignee,
milestone, board card. Normally delivered by the `sks-pr-ready` train;
an untriaged side routes back to its triage skill before any merge.

**Gate 2 — DoD discharged.** Issue criteria (`- [ ]`, `sks-issue`) all checked;
re-read the ledger (unchecked box blocks merge):

```bash
gh issue view <N> --repo <org>/<repo> --json body --jq .body
```

**Gate 3 — mandatory approver approval (non-bypassable).** The org designates
one approver account (`references/shikanime.md`); before any other
review consideration, the merge is blocked until that account has an APPROVED
review on the current head commit — a stale approval after a new push does not
count, and `--admin` may bypass branch protection but never this gate. CI
green: `gh pr checks <M> --repo <org>/<repo>`. Verify the approval against the
head SHA (REST reviews carry `commit_id`):

```bash
R=<org>/<repo>; M=<PR>; APPROVER=<approver login>  # references/shikanime.md
HEAD=$(gh pr view "$M" -R "$R" --json headRefOid -q .headRefOid)
gh api "repos/$R/pulls/$M/reviews" --paginate \
  --jq 'map(select(.user.login == "'"$APPROVER"'" and .state == "APPROVED"
                 and .commit_id == "'"$HEAD"'")) | length > 0'
```

The approval post runs under the approver account — locked identity switch
via `sks-sudo` — then re-run this gate's verification against the head SHA.

`False` → `BLOCKED: <approver> approval required` — request it
(`gh pr edit <M> -R "$R" --add-reviewer "$APPROVER"`) or obtain it verbally,
then re-verify on the new head. In addition, `sks-review`
approval applies as before: approved on current head; re-review if new
commits landed.

```bash
gh pr view <M> --repo <org>/<repo> --json reviews,headRefOid \
  --jq '.reviews | map(select(.state == "APPROVED")) | length > 0'
```

Agent review is pre-flight; **a human approving review is the gate.** Where
branch protection blocks self-approval (repos listed in
`references/shikanime.md`), a verbal `lgtm` from the operator (the human
who owns the approver account) satisfies Gate 3 — land via
`gh pr merge --squash --admin` (see Merge procedure). `--admin` is what
bypasses the protection; no separate human review is then required.

**Gate 4 — Conversations reconciled.** Every inline thread resolved
(`sks-pr-resolve`'s output). If not run, do so now; if it already reported all
reconciled, skip.

**Gate 5 — `sks-commit` + `sks-pr` conventions (verified, never eyeballed).**
Commit subject is plain-English imperative (no `fix:`/`feat:`/`chore:`
conventional prefix), capitalized, no trailing period. PR title equals the
commit subject unless the repo's own conventions say otherwise (template,
semantic-release / PR-title linting — the repo wins, see `sks-pr`); PR body
follows the repo's PR template when one exists (see `sks-pr`), else restates
the rationale. ALWAYS run the shape check
before merging — on every landing, not only when a violation is suspected; a
`BLOCKED` line is the gate working, not a tooling failure. When the repo's
conventions legitimately diverge the title (semantic-release, template), the
title-parity `BLOCKED` is waivable — document why in the landing notes. A
doc-repo commit
may carry a `doc:` prefix — that is the `sks-commit` override for doc repos,
and the check accepts it.

```bash
R=<org>/<repo>; M=<PR>
gh pr view "$M" -R "$R" --json commits,title,body -q '
  .commits[0].messageHeadline as $s
  # The commits payload truncates messageHeadline (~70 chars + "…") for long
  # subjects; accept a truncated headline when it prefixes the PR title.
  | ($s == .title
     or (($s | endswith("…"))
         and (.title | startswith(($s | sub(" ?…$"; "")))))) as $parity
  | if ($s | test("^(fix|feat|chore|docs|refactor|test|build|ci|perf|"
                  + "renovate)(\\([^)]*\\))?!?: "))
    then error("BLOCKED: conventional prefix: " + $s)
    elif ($s | test("^[a-z]") and ($s | startswith("doc: ") | not))
    then error("BLOCKED: lowercase subject: " + $s)
    elif ($s | endswith(".")) then error("BLOCKED: trailing period: " + $s)
    elif ($parity | not)
    then error("BLOCKED: PR title differs from commit subject")
    else "OK: commit conventions pass" end'
```

Non-zero exit with `BLOCKED: <reason>` on violation; `OK: commit conventions
pass` is the only merge-ready signal. If the commit subject violates
`sks-commit` (conventional prefix, lowercase start, trailing period) or the
PR title diverges from it, fix before merging:

```bash
jj describe -m "<plain-English subject>" \
  -m "<required trailer lines — see references/shikanime.md>"
```

then force-push and re-run the check. Required trailers (e.g. a bot co-author
line) are org-specific — see `references/shikanime.md`. The recurring
failure mode is skipping the check: a landing merged without the required
trailer because Gate 5 dumped the commit message for eyeball review instead of
deciding.

## Merge procedure

Land with plain `gh pr merge`. A `gh stack` extension, where installed, may
create and maintain stacks; landing itself stays plain `gh pr merge` (org
tooling state in `references/shikanime.md`). For a lone PR use
`gh pr merge --squash [--admin]`; never `gh pr merge` on a stacked PR — but
stacked PRs are landed the same way now (one squash-merge per PR, base `main`).
Never force-push. **Watch and merge are two separate steps — never one
background chain.** A merge that fires unattended from a watcher is a
recurring incident class: by the time it lands, gates may have moved (new
commits, stale approval, red check). Keep the observe step separable from
the act step:

Step 1 — watch (observe-only; may run in a background terminal):

```bash
gh run watch --exit-status --repo <org>/<repo> \
  $(gh run list --repo <org>/<repo> --branch <branch> --limit 1 \
    --json databaseId -q '.[0].databaseId')
```

Re-run after each fresh push. A failing run exits non-zero — red never
merges. When it returns, STOP and re-verify the merge gates on the current
head (`gh pr view <M> --json reviews,headRefOid,mergeable`) before merging;
Step 2 binds the merge to that head with `--match-head-commit`.

Step 2 — merge (act; foreground, deliberate, never auto-chained to the
watch):

```bash
HEAD=$(gh pr view <M> --repo <org>/<repo> --json headRefOid -q .headRefOid)
gh pr merge <M> --repo <org>/<repo> --squash --match-head-commit "$HEAD" \
  -t "<PR title> (#<PR number>)" \
  -b "$(cat <<'EOF'
<body: one coherent change, no jj * bullets / --------- separators; trailers
only: Related: [url], Signed-off-by: [user], required co-author trailer (see
references/shikanime.md)>

<required trailer lines — see references/shikanime.md>
EOF
)"
```

> Gotcha: `gh run watch <run-id>` exits 0 even on FAIL — always pass
> `--exit-status`. It takes a `<run-id>` (no `--branch`); resolve via
> `gh run list`.
> Gotcha: never join the two with a shell conjunction — one `&&` between
> watch and merge IS the background-merge bug. The watch reports; a separate
> decision merges.

- **Squash hygiene**: pass `-t "<PR title> (#<PR number>)"` and `-b` (see
  `sks-commit`) — gh passes a `-t` subject verbatim and uses the bare PR
  title when `-t` is omitted, and neither carries the `(#N)` suffix GitHub
  appends to default squash subjects; without an explicit `-t` the landed
  commit loses its PR back-reference (#542, #544). Never auto-concatenate
  branch commits (leaks jj's `*` / `---------` artifacts). One subject +
  required trailers (`references/shikanime.md`).
- Lone, self-approval blocked (after verbal lgtm): use `--squash --admin`.
- `--admin` may be REFUSED outright when a Landing protections ruleset sets
  `bypass_actors: []` (shikanime-labs/.github ruleset 25477751 since
  2026-10-21): "Waiting on code owner review" even with `--admin`. The only
  path is a real code-owner approval from a non-author account — Gate 3
  `sks-sudo` switch, `gh pr review --approve`, restore — then merge with
  `--match-head-commit` (plain `--squash` suffices once approval exists).
- Stacked (multiple PRs off `main`): land each with
  `gh pr merge <PR_NUMBER> --squash --admin` in dependency order (base first).
- Branch protection may require linear history + signed commits (org example
  in `references/shikanime.md`); squash-merge satisfies both.

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
3. Close the issue **deliberately**: confirm tasklist N/N and user acceptance
   (step 2), then `gh issue close <N> --repo <org>/<repo> -c "Discharged by
   <PR URL>"`.
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
   cover. Full mechanics: `sks-wiki`.
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

- `--match-head-commit` takes the FULL 40-char oid — a short sha fails GraphQL
  coercion (`Could not coerce value "abc1234" to GitObjectID`) and the merge
  silently no-ops while the command exits 0-looking. Fetch it with
  `gh pr view <M> --json headRefOid -q .headRefOid`, never hand-truncate.

- Stacked PRs (GitHub stack feature, Oct 2026+): legacy `gh pr merge`, the
  GraphQL mutation, and `--auto` all refuse with "part of a stack and must be
  merged using the asynchronous merge REST API". Use
  `PUT /repos/{o}/{r}/pulls/<n>/merge-async` body
  `{merge_method, merge_action:"direct_merge", commit_message, sha,
  bypass_rules}` then poll `GET .../merge-async/<uuid>` until status !=
  `pending`. `bypass_rules` is the async API's `--admin`.
- Mid-stack async merges can land the squash onto the stack-LINK base branch
  instead of `main` (empirical: merged status, commit on the child base).
  After every stacked merge, verify `main` actually advanced
  (`ls-remote` + commit log); if not, abandon re-merging children and open
  ONE stack-free PR (base `main`) with the remaining delta — watch its real
  CI, merge legacy.
- Repos whose cleanup workflow deletes PR head branches on close: a stacked
  child's BASE is the PR below's head branch, so every merge deletes the next
  PR's base → DIRTY / "Base branch no longer exists". Preempt: re-push the
  exact base SHA (raw git from the colocated checkout; jj no-ops on stale
  tracking), re-check `mergeStateStatus`, then merge.
- A `jj git fetch` after remote branch deletion abandons the local commits +
  bookmark ("no longer reachable"); `jj undo` restores them. Never fetch
  between a merge and the next push of the stack.
- Unchecked criterion — discharge or escalate, don't merge.
- Merging a dependent stacked PR before its base lands — go in dependency order,
  base first.
- Merge after new commits without re-review — approval binds to a head commit.
- Joining the CI watch and the merge with a shell conjunction in one
  background terminal — the merge fires unattended while gates move. Watch
  reports; merge is a separate deliberate step on a re-verified head.
- The Development link is metadata (`addCloseIssueReferences`), not a body
  keyword; with repo auto-close off (#301) merging leaves the issue open —
  close deliberately after N-of-N. Where auto-close is still on, discharge
  the ledger before merging.
- Closing the issue before the user accepts the deployed change — merge is a
  claim; wait for manual acceptance of the running/deployed state before
  discharging the ledger.
- Open threads — reconcile first via `sks-pr-resolve`.

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
