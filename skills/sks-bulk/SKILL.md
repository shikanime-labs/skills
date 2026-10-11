---
name: sks-bulk
description:
  "Use when applying one instruction to many targets — repos, issues, PRs,
  orgs, or any enumerable agentic batch: enumerate targets, drive the batch
  from a plan file, and verify every result."
version: 0.2.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - bulk-ops
      - fan-out
      - audit
      - github
    related_skills:
      - sks-commit
      - sks-delegate
      - sks-dev
      - sks-issue
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Bulk Ops

Apply one instruction to N targets. A target is whatever the instruction
names: every repo in an org, every open issue matching a filter, every PR
touching a path, or any other enumerable agentic target. This is the
N-target shape: one target is `sks-dev`, and one unit that must not
fold in foreign WIP is `sks-delegate`.

For org specifics — target orgs, canonical checkout paths, branch and PR
policy, commit envelope, and the ruleset-approval resolution — read
`references/shikanime.md` when operating in a shikanime org.

## When to Use

- "Which targets miss X?" — an audit across the set.
- "Add X to every target" / "backport Y across the org" — a batch mutation.
- "This same fix has to land in N repos."
- "Label / close / reassign every issue matching Q."
- One PR per repo derived from a single census.
- Any other single instruction with an enumerable target set.

Not for: a single target (`sks-dev`), or parallel units inside one
repo (`sks-async`).

## Procedure

1. **Enumerate and filter targets in the query, not afterwards.** Empty
   repos carry no default branch, so every later branch or commit step fails
   on them:

   ```bash
   # repos in an org
   gh repo list <org> --limit 200 --json name,isArchived,defaultBranchRef
   # issues matching a filter
   gh issue list -R <org>/<repo> --search "<query>" --json number,title
   # PRs matching a filter
   gh pr list -R <org>/<repo> --json number,headRefName
   # any other target kind: emit one row per target into the plan file
   ```

   Done when the target list drops archived and empty repos; record its size
   as N.

2. **Detect gaps from ground truth per target**, never from a cached summary
   endpoint — the community-profile endpoint serves a stale cache, reporting
   files that exist as missing and health percentages that contradict the
   tree:

   ```bash
   gh api repos/<org>/<repo>/contents --jq '.[].name'
   ```

   Done when the probe agrees with one real clone.

3. **Source canonical content from a target that already has it** rather
   than inventing boilerplate per target:

   ```bash
   gh api repos/<org>/<repo>/contents/<file> --jq .content | base64 -d
   ```

4. **Drive the loop from a tab-separated plan file**, one row per target,
   read with `while IFS=$'\t' read` — `xargs` splits on whitespace, so a
   multiword argument list (file names per target) flattens into garbage
   invocations that no-op silently. Keep the script re-entrant —
   `[ -d "$d/.git" ] || git clone …` with fresh unique clone dirs, never an
   `rm -rf` preamble, which trips an approval prompt and stalls an
   unattended batch on a non-essential step.

   Full-command plan lines beat argument-list columns: `$args` word-splitting
   shatters quoted multiword values (`--add-label "technical debt"` arrives as
   two garbage args), and `gh issue/pr edit --milestone` takes the milestone
   TITLE, not its number — a numeric column fails "'37' not found" minutes
   into a batch.

5. **Mutate per target kind; never push to the default branch.** Repo
   targets mutate in a throwaway clone:

   ```bash
   git init "$d" && cd "$d"
   git fetch origin "$branch"
   git checkout -B "$branch" "$head_sha"
   # add files, commit per sks-commit, then push the branch:
   git push origin "HEAD:refs/heads/$branch"
   ```

   Issue and PR targets bypass the clone: apply the mutation via `gh api`
   inside the same plan-file loop, then read each one back to confirm the
   write. Branches await user review; open a PR per repo
   (`sks-pr`) only on explicit go-ahead, from
   `--head <org>:<branch>`. Done when the plan file records the applied
   state per row.

6. **Verify after the batch**: re-query every target for the expected state
   and report N/M success plus the named failures — an empty target, a
   denied push, and a bad default branch name have different remediations,
   so track the reason per row. A push command's own success line proves
   nothing.

## Pitfalls

- **The probe's output format must match the query.** Emit plain paths
  (`--jq '.tree[].path'`), never the JSON-array form (`'[.tree[].path]'`):
  grepping quoted names against plain patterns (or the reverse) yields
  silently inverted yes/no columns. Verify the probe against one real clone
  before driving any mutation off it.
- **Check per-target applicability inside the batch loop**, not only in the
  probe: grep the target file for the topic first (skip already-converged
  targets) and confirm the feature the change describes actually exists (no
  `.envrc` means no direnv section). A uniform census column is not proof —
  one false-positive cell ships a false PR to every target that shares it.
- **`gh pr merge` reports failures that look like successes** (near-empty
  output). Verify every merge by re-querying `gh pr view <n> --json
  state,mergedAt`, and treat a ruleset rejection as a gate doing its job:
  read the ruleset JSON to a file and check for `require_last_push_approval`
  before guessing. Unasked-for bypass attempts stay forbidden — surface the
  gate, execute only on explicit go-ahead. Resolution recipe:
  `references/shikanime.md`.
- **Run bulk mutation scripts through `terminal`**, not a code-kernel loop
  over `gh api` — per-target subprocess batches blow the kernel timeout and
  lose all progress state, while a shell script resumable from the plan file
  survives.
- **The Contents API serves a stale cached blob for minutes after a merge.**
  Diff the clone against the fetched blob before pushing, and treat "no-op
  after transform" as a staleness signal rather than a success.
- **Re-running a partially completed bulk push:** fetch the existing branch,
  not the default branch, or the push rejects non-fast-forward ("fetch
  first") even though the first run's work is already fine on the remote.
- **`gh api --jq .name` on a missing path prints the 404 error JSON to
  stdout**, not stderr: a `[ -z "$low" ]` emptiness check inverts and reports
  every row as failed. Capture the expected exact name and compare
  (`[ "$low" = "expected" ]`), or pipe through `grep -qx <name>`.
- **Backporting a workflow-parse fix revives dead workflows:** CI then runs
  for the first time in weeks and fails on pre-existing drift (stale
  nixpkgs against flake-checker's 30-day limit, broken composite inputs).
  Before landing, classify branch-run reds against the default branch's run
  history — pre-existing red is not introduced by the backport, but merging
  with red needs an explicit operator call and a follow-up fix wave.
- **Dependabot warnings on push** (vulnerability alerts) are noted in the
  report, not treated as push failures and not auto-fixed.

## Verification

```bash
# census agrees with a real clone
gh api "repos/$org/$repo/git/trees/$ref" --jq '.tree[].path'

# N/M success per row of the batch plan
while IFS=$'\t' read -r org repo branch; do
  printf '%s/%s %s\n' "$org" "$repo" \
    "$(gh api "repos/$org/$repo/branches/$branch" --jq .name 2>/dev/null)"
done < plan.tsv

# every merge, from GitHub — never from the merge command's output
gh pr view <n> -R <org>/<repo> --json state,mergedAt --jq '.state, .mergedAt'
```

Done when every plan row reports its expected state and each failure is
named with its reason.

## See also

- `sks-dev` — the one-repo loop this scales out.
- `sks-delegate` — isolation workspace for the change itself.
- `sks-commit` — commit envelope the batch commits must carry.
- `sks-pr`, `sks-issue` — per-repo PR and issue sides.
- `sks-gist` — host a shared helper script at a stable URL when the batch
  spans repos or sessions.
- Org specifics (orgs, checkout paths, commit envelope, ruleset gate):
  `references/shikanime.md`.
