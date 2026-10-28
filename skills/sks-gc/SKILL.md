---
name: sks-gc
description:
  "Use when reclaiming resources leaked by agent workflows: dangling jj
  bookmarks, skill-created workspaces, leftover working-copy dirs, and stale
  merged branches on GitHub remotes. Also fleet node disk cleanup when a
  Longhorn disk reports DiskPressure."
version: 0.4.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - gc
      - cleanup
      - workspaces
      - bookmarks
      - github
      - branches
    related_skills:
      - sks-async
      - sks-dev
      - sks-land
      - sks-github-notif-sweep
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Workspace Garbage Collection

Reclaim resources leaked by agent workflows: `jj` bookmarks with no open PR
and not on `main`, `jj` workspaces the skills created (`<repo>.<unit>`,
`<repo>.fix`), the sibling working-copy directories they leave on disk, and
stale fully-merged branches on GitHub remotes. Destructive — always dry-run
first.

## Available script

- `scripts/discover.py [REPO_DIR]` — print every GC candidate: dangling
  bookmarks (not trunk, no open PR) and skill workspaces with a clean/dirty
  guard per workspace. Dry-run only; never forgets or removes. Run it first,
  review the list, then apply manually (steps 2–4).

## When to Use

- After a finished or stalled `sks-async` fan-out or `sks-dev`
  isolation pass: workspaces and bookmarks pile up.
- "Clean up my dangling branches / orphan jj workspaces."
- "Delete the merged branches on GitHub" — the org-wide remote-branch sweep.
- Periodic hygiene on a repo worked across many parallel streams.
- A Longhorn disk reports `Schedulable=False reason=DiskPressure` — free-space
  fleet sweep (Fleet node disk cleanup, below).

## Hard rules

- **Dry-run first.** Print every candidate; never `forget`/`rm` on the same pass
  that discovers it. Require an explicit apply step after review.
- **Never drop `main` / `trunk` / `master`** or a bookmark with an OPEN PR.
- **Never forget a workspace with uncommitted changes.** Skip it and report —
  losing WIP is data loss.
- **Never delete a remote branch with an open PR, a recent push (< 7 days),
  or protected status.** Blocked candidates are listed and re-checked next
  run, never forced.
- Operate in the repo root — when operating in an org repo, read
  `references/shikanime.md` for the canonical checkout location. The
  canonical workspace (named after the repo, no unit suffix) is NEVER a
  candidate.

## Procedure

1. **Discover** — run the dry-run scanner, review its output:

   ```bash
   cd "$(jj workspace root)"   # or the repo root; see
                               # references/shikanime.md for the
                               # canonical checkout location
   <skill-dir>/scripts/discover.py   # scripts/ resolves against the
                                          # skill dir, not the target repo
   ```

   The script lists `== dangling bookmarks ==` (names only; trunk and
   open-PR bookmarks already excluded) and `== skill workspaces ==`
   (`CLEAN <name> <path>` vs `DIRTY <name> <path>`).

2. **Apply** (only after review) — forget dangling bookmarks and clean
   workspaces:

   ```bash
   jj bookmark forget <dangling...>
   jj workspace forget <name...>       # already confirmed clean
   rm -rf <path>                        # ONLY the sibling dir from step 1
   ```

3. **Prune remote-tracking bookmarks no longer on origin** (safe, built-in):

   ```bash
   jj git fetch --remote origin
   ```

   Note: jj >= 0.43 removed `--prune`; deleted remote branches auto-prune on
   plain fetch (older builds keep `--prune`).

4. **Verify.**

   ```bash
   jj workspace list && jj bookmark list
   gh pr list --state open
   ```

5. **GitHub remote-branch sweep** (when the target is merged remote branches,
   not local jj state):

   ```bash
   gh api repos/<repo>/branches --paginate
   ```

   A branch is stale when its head is an ancestor of the default branch
   (`gh api repos/<repo>/compare/<default>...<branch>` with
   `status=="identical"` or `behind`) or its PR is closed/merged. Never touch
   the default branch, protected branches, `release/*` tags, or ghstack role
   branches (`<prefix>/base|head|orig`) of OPEN ghstack stacks — only
   fully-landed ones. Delete stale branches older than 7 days:

   ```bash
   gh api -X DELETE repos/<repo>/git/refs/heads/<branch>
   # or, after a depth-1 clone:
   git push origin --delete <branch>
   ```

   Branches of closed-but-unmerged PRs are deleted only after 30 days idle.

## Fleet node disk cleanup (Longhorn DiskPressure)

The 25% DiskPressure floor (`MinimalAvailable = 25% of Storage Max` on
`nodes.longhorn.io` disks) is physical: `storageReserved` tuning cannot pass
it; only free space does. Signature: `Schedulable=False` with
`reason=DiskPressure` and `CurrentAvailable <= MinimalAvailable`.
Non-destructive per-node sweep (reclaims containerd layers, journals, nix
store only — never user data):

```bash
ssh root@<node> '
  df -BM / | tail -1
  journalctl --vacuum-size=500M
  timeout 240 nix-store --gc
  export PATH=$PATH:/var/lib/rancher/rke2/bin \
          CRI_CONFIG_FILE=/var/lib/rancher/rke2/agent/etc/crictl.yaml
  timeout 300 crictl rmi --prune
  df -BM / | tail -1'
```

- The rke2 PATH + `CRI_CONFIG_FILE` export is mandatory — bare `crictl`
  targets the wrong socket or exits 127 in scripted shells.
- `df` right after `rmi --prune` LAGS: containerd deletes blobs
  asynchronously; re-check `df` (or Longhorn `storageAvailable`) minutes
  later before judging the pass failed. Large layers report
  `DeadlineExceeded` yet still complete.
- Small MMC-boot nodes (fushi/minish/nemishi class) have little reclaimable
  overhead; the big wins live on NVMe nodes running inference images.
- Verify fleet-wide after: every `nodes.longhorn.io` disk `Schedulable=True`,
  every k8s node `DiskPressure=False`.
- Worked case: a disk blocked at 19% free crossed the floor after the sweep
  (~300 GiB reclaimed; async blob GC kept landing for minutes after the
  prune), flipping a pinned volume's `LocalReplicaSchedulingFailure` to
  `Scheduled=True` with no other action.

## What "resources from other skills" covers

- `sks-async` → one `jj workspace add ../<repo>.<unit>` per stream and a
  bookmark + PR branch per link on `origin`.
- `sks-dev` → `jj workspace add ../<repo>.fix` isolation dirs and
  `/tmp/wip*` scratch copies (the latter are manual — list, but never
  auto-`rm` without asking).
- Parallel-stream chains → branch bookmarks on `origin`; cleared by forgetting
  the bookmark plus `jj git fetch --prune` (step 3).

## Pitfalls

- `jj workspace forget` does NOT delete the on-disk directory — `rm -rf` it
  yourself after confirming it is the sibling skill dir, never the repo root.
- A dirty workspace skipped by the guard means real WIP; surface it, do not
  force.
- Remote-tracking bookmarks (`origin/...`) need `--prune` (step 3), not
  `bookmark forget`, to clear.
- The canonical workspace (bare repo name, no dot/`-fix`) is never a candidate;
  don't fold the trunk working copy into GC (paths per
  `references/shikanime.md`).
- **jj 0.43 output formats.** `jj workspace list` default lines have no path
  column, and `jj bookmark list` prints `name: changeid desc` plus indented
  `@origin` continuation lines — parsing those with `awk '{print $1}'` yields
  trailing colons and `@origin` noise. `discover.py` templates the exact fields
  (`-T 'name ++ "\t" ++ root'` for workspaces, `-T 'name ++ "\n"'` for
  bookmarks); don't revert to awk on the default output.
- **Remote-branch staleness is per-repo.** The default branch name varies
  (`main`, `master`, `trunk`); read it per repo
  (`gh repo view --json defaultBranchRef`) instead of assuming — comparing
  against a hardcoded name marks everything stale on the wrong base.
- The GitHub compare API caps at 250 commits per side; a very long-lived
  branch reports `ahead` even when fully merged — cross-check with the PR
  state (`gh pr list --head <branch> --state merged`) before deleting.

## Verification

```bash
jj workspace list && jj bookmark list
gh pr list --state open   # confirm no protected bm forgotten, canonical wc untouched
gh api repos/<repo>/branches --paginate --jq '.[].name'   # deleted branches absent
```

## Memory loop

In memory-equipped environments, close the loop around the report:
`honcho_search "stale branch cleanup"` and `honcho_context` before
reporting reuse recurring context (branches a previous run flagged blocked
and why); `honcho_conclude` after it records one line per durable lesson.
Memory-less environments skip this section.

## See also

- `sks-async` — the fan-out that creates the workspaces/bookmarks this skill
  reclaims.
- `sks-dev` — isolation workspace pattern (`../<repo>.fix`).
- `sks-land` — lands PRs (this skill only reclaims after landing, never
  merges).
- `sks-github-notif-sweep` — the companion org-wide GitHub hygiene sweep.
