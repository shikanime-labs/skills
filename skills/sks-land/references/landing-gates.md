# Landing Gates

The full pre-landing gate checks, the merge procedure, and the
landing pitfalls for `sks-land`. Read before every landing; the
body carries the routing and the post-merge sequence.

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

Land a lone PR with `gh pr merge --squash [--admin]`. For a stacked PR, land
the TOP-most unmerged PR: `gh stack merge <top-pr> --yes --squash`. GitHub
merges that PR and every unmerged layer below it in ONE all-or-nothing stack
merge, bottom-up internally — never merge links one at a time from the base.
On a merge-queue base the command enqueues the PRs instead; the queue chooses
the merge method and `--squash` is ignored. Link base-chained PRs into a
native stack before calling it — base chaining alone is not a stack.
Org tooling state: `references/shikanime.md`.
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
- Stacked (multiple PRs off `main`): Step 2's `gh pr merge` is for a lone PR.
  For a stack, link the PRs, run Gates 2–5 for every PR the merge will land,
  then merge the TOP PR with `gh stack merge <top-pr> --yes --squash`. The
  waterfall lands that PR and all unmerged parents below in one action —
  never base first. Stack merges cannot bypass merge requirements; no
  `--admin`.
- Branch protection may require linear history + signed commits (org example
  in `references/shikanime.md`); squash-merge satisfies both.

## Pitfalls

- Stacked PRs (GitHub stack feature, Oct 2026+): legacy `gh pr merge`, the
  GraphQL mutation, and `--auto` all refuse with "part of a stack and must be
  merged using the asynchronous merge REST API". Prefer
  `gh stack merge <top-pr> --yes --squash`, which asks GitHub to waterfall the
  whole stack. API fallback: `PUT /repos/{o}/{r}/pulls/<top-pr>/merge-async`
  body `{merge_method, merge_action:"direct_merge", commit_message, sha,
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
- Landing stacked links one by one from the base — old procedure. Merge the
  top PR with `gh stack merge` so GitHub waterfalls every parent in one action.
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
- Queue-enforced repos: auto-merge enrollment can hang (PR sits CLEAN +
  armed with no queue entry for minutes/hours). Disable then re-enable
  auto-merge to re-kick enrollment; verify pickup via `mergeQueueEntry`
  (GraphQL) — `autoMergeRequest` reads null once enrolled and that is
  normal. The queue build adds its own minutes: poll
  `mergeQueueEntry.state`.

## Landing gates under dual-agent identities

`require_last_push_approval` turns cyclic when the mandatory approver is
also the PR author and the only other human identity pushed the commits:
neither identity can legally approve. Do not burn cycles rekeying
authors/committers or swapping approvers — GitHub counts identity either
way. Go straight to the documented bypass grant flow: admin-view GET
ruleset → PUT with `bypass_actors=[{actor_id:5,RepositoryRole,always}]` →
`gh pr merge --squash --admin --match-head-commit` → PUT bypass_actors=[]
immediately → read-back must show `b: null`. The ruleset PUT 404s under
the automation identity (not admin on the repo) — run the whole
grant/restore from the owner identity.

`gh pr view --json headRefOid` can lag a force-push by seconds — resolve
the merge HEAD from `gh api repos/<R>/pulls/<M> --jq .head.sha` instead,
or the merge dies on "Head branch was modified".
