---
name: sks-bulk
description:
  "Use when auditing or bulk-changing many shikanime-labs / shikanime-studio
  repos at once: enumerate targets, drive the batch from a plan file, and
  verify every result."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - bulk-ops
      - audit
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-commit
      - sks-delegate
      - sks-dev-workflow
      - sks-issue-workflow
      - sks-pr-workflow
platforms:
  - linux
  - macos
  - windows
---

# Bulk Repo Ops

Audit or change many repos at once. This is the N-repo shape: one repo is
`sks-dev-workflow`, and one repo that must not fold in foreign WIP is
`sks-delegate`.

For org specifics — target orgs, canonical checkout paths, branch and PR
policy, commit envelope, and the ruleset-approval resolution — read
`references/org-conventions.md` when operating in a shikanime repo.

## When to Use

- "Which of our repos miss X?" — an org-wide audit.
- "Add X to every repo" / "backport Y across the org" — a batch mutation.
- "This same fix has to land in N repos."
- One PR per repo derived from a single census.

Not for: a single repo (`sks-dev-workflow`), or parallel units inside one repo
(`sks-async`).

## Procedure

1. **Filter in the query, not afterwards.** Empty repos carry no default
   branch, so every later branch or commit step fails on them:

   ```bash
   gh repo list <org> --limit 200 --json name,isArchived,defaultBranchRef
   ```

   Done when the target list drops archived and empty repos; record its size
   as N.

2. **Detect gaps from the Contents API tree**, never from the community
   profile endpoint — that endpoint serves a stale cache, reporting files that
   exist as missing and health percentages that contradict the tree:

   ```bash
   gh api repos/<org>/<repo>/contents --jq '.[].name'
   ```

   Done when the probe agrees with one real clone.

3. **Source canonical content from a repo that already has it** rather than
   inventing boilerplate per repo:

   ```bash
   gh api repos/<org>/<repo>/contents/<file> --jq .content | base64 -d
   ```

4. **Drive the loop from a tab-separated plan file**, one row per repo, read
   with `while IFS=$'\t' read` — `xargs` splits on whitespace, so a multiword
   argument list (file names per repo) flattens into garbage invocations that
   no-op silently. Keep the script re-entrant — `[ -d "$d/.git" ] || git
   clone …` with fresh unique clone dirs, never an `rm -rf` preamble, which
   trips an approval prompt and stalls an unattended batch on a non-essential
   step.

5. **Mutate in a throwaway clone per repo.** Never push to the default branch:

   ```bash
   git init "$d" && cd "$d"
   git fetch origin "$branch"
   git checkout -B "$branch" "$head_sha"
   # add files, commit per sks-commit, then push the branch:
   git push origin "HEAD:refs/heads/$branch"
   ```

   Branches await user review; open a PR per repo (`sks-pr-workflow`) only on
   explicit go-ahead, from `--head <org>:<branch>`. Done when the plan file
   records a branch per repo.

6. **Verify after the batch**: re-query the branch or file for every target and
   report N/M success plus the named failures — an empty repo, a denied push,
   and a bad default branch name have different remediations, so track the
   reason per repo. A push command's own success line proves nothing.

## Gotchas

- **The probe's output format must match the query.** Emit plain paths
  (`--jq '.tree[].path'`), never the JSON-array form (`'[.tree[].path]'`):
  grepping quoted names against plain patterns (or the reverse) yields
  silently inverted yes/no columns. Verify the probe against one real clone
  before driving any mutation off it.
- **Check per-repo applicability inside the batch loop**, not only in the
  probe: grep the target file for the topic first (skip already-documented
  repos) and confirm the feature the section describes actually exists (no
  `.envrc` means no direnv section). A uniform census column is not proof —
  one false-positive cell ships a false PR to every repo that shares it.
- **`gh pr merge` reports failures that look like successes** (near-empty
  output). Verify every merge by re-querying `gh pr view <n> --json
  state,mergedAt`, and treat a ruleset rejection as a gate doing its job: read
  the ruleset JSON to a file and check for `require_last_push_approval` before
  guessing. Unasked-for bypass attempts stay forbidden — surface the gate,
  execute only on explicit go-ahead. Resolution recipe:
  `references/org-conventions.md`.
- **Run bulk mutation scripts through `terminal`**, not a code-kernel loop
  over `gh api` — per-repo subprocess batches blow the kernel timeout and lose
  all progress state, while a shell script resumable from the plan file
  survives.
- **The Contents API serves a stale cached blob for minutes after a merge.**
  Diff the clone against the fetched blob before pushing, and treat "no-op
  after transform" as a staleness signal rather than a success.
- **Re-running a partially completed bulk push:** fetch the existing branch,
  not the default branch, or the push rejects non-fast-forward ("fetch first")
  even though the first run's work is already fine on the remote.
- **Backporting a workflow-parse fix revives dead workflows:** CI then runs for
  the first time in weeks and fails on pre-existing drift (stale nixpkgs
  against flake-checker's 30-day limit, broken composite inputs). Before
  landing, classify branch-run reds against the default branch's run history —
  pre-existing red is not introduced by the backport, but merging with red
  needs an explicit operator call and a follow-up fix wave.
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

Done when every plan row reports its expected state and each failure is named
with its reason.

## See also

- `sks-dev-workflow` — the one-repo loop this scales out.
- `sks-delegate` — isolation workspace for the change itself.
- `sks-commit` — commit envelope the batch commits must carry.
- `sks-pr-workflow`, `sks-issue-workflow` — per-repo PR and issue sides.
- Org specifics (orgs, checkout paths, commit envelope, ruleset gate):
  `references/org-conventions.md`.
