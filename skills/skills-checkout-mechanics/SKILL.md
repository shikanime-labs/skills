---
name: skills-checkout-mechanics
version: 1.2.0
author: hermes-curator
license: MIT
description: "Use when landing skill edits in the skills catalog checkout."
metadata:
  hermes:
    tags: [skills, jj, checkout, landing]
    related_skills: [sks-pr, sks-dev]
---

# Skills checkout mechanics

Mechanics of the `shikanime-labs/skills` checkout and of landing a skill
edit. The WHAT-to-write lives in each skill's own domain; this covers the
plumbing that silently costs a session when done wrong.

## When to Use

- Committing, carving out, or landing a change to any file under the
  skills catalog checkout.
- A `skill_manage` write fails with a PermissionError naming a `.tmp`
  file.
- A commit on the skills checkout turned out to include a parallel
  session's dirty working-copy files.

## Two locations, different ownership

- `~/.hermes/skills/<name>/` — the live Hermes install AND the jj checkout
  root (colocated). Root-level entries are git-excluded (`.git/info/exclude`
  ignores `/*`, un-ignores only the catalog scaffolding); the tracked
  catalog tree is `skills/` (e.g. `~/.hermes/skills/skills/sks-audit/`).
- Bundled and hub skills (`autonomous-ai-agents/hermes-agent/...`) and
  agent-created skills (`devops/...`) are HOST-LOCAL — they are outside the
  catalog tree. Editing them changes only this machine; landing the change
  needs a PR to the upstream repo that owns them (hermes-agent repo, or the
  local author). Never point the user's PR at a path the catalog does not
  track.

## skill_manage permission trap

`chmod u+w` on the TARGET FILE is not enough. The error is
`PermissionError: .../.tmp_*.tmp` — skill_manage writes via a TEMP FILE IN
THE PARENT DIRECTORY, so the directory must be writable too:

```bash
chmod u+w <skill_dir> <skill_dir>/references  # dir first, then the files
```

Catalog skills (`skills/sks-*/...`) are world-readable 0444 by design
(tap layout); every edit needs this first. Also chmod the sibling dir when
patching a linked file under `references/` — the file lives in a different
subtree than the SKILL.md.

After ANY skill_manage batch — success or failure — verify the edit landed
with search_files on disk: failed batches leave partial writes behind, and
a successful result message is not proof.

Before editing a catalog skill, grep the whole skill directory for the rule
being changed — `evals/` assertions and `scripts/` carry their own copies of
a behavior; a deferral that leaves them asserting the old behavior re-teaches
it on the next run.

## Shared dirty checkout: carve out, never commit @

The checkout's working copy (@) is shared: a parallel session's unsnapped
drafts sit in it as tracked modifications. Rules:

1. **Never `jj new`/describe on @ with foreign dirt** — the new change
   inherits every modified file. The isolation gate catches it only after
   the fact.
2. **Carve your change out of the dirty @** — when you own whole files,
   `jj split -r @ <your-file> -m "..."` lifts exactly your paths into @-
   and leaves the rest in @; then `jj describe` / `jj new -m "empty"` /
   bookmark `-r @-` on the carved change, and `jj diff -r @- --git` to
   prove the change set. When a parallel session's dirt shares YOUR file,
   path-level split silently evicts their hunks from the working copy:
   snapshot the mixed files to scratch, `jj restore <the shared files>`,
   re-apply only your hunks, split them out, then verify the @ delta on
   those files is the foreign hunks alone — and restore them byte-for-byte.
3. **Abandoning a wrong commit on a shared checkout DESTROYS the dirt** —
   abandon removes the commit AND its content from the working copy; the
   parallel session's unsnapped drafts vanish. If it happens, restore
   first: `jj restore --from <hidden-rev>` resurrects the full content,
   then `jj split` out your file cleanly. Verify restoration with a diff
   against the hidden revision — byte-identical, no drift.
4. `jj rebase -d main@origin` (never `trunk()` in shell — parens break
   bash eval; use the explicit `main@origin` form) and re-verify the diff
   after every rebase; a rebase rewrites the change and can surprise.
5. **A parallel session can migrate into its own jj workspace mid-flight**
   (`jj workspace list` lists them). Dirt it later committed belongs to its
   workspace, not the shared @: before restoring a lost shared-file hunk,
   confirm its workspace checkout does not already carry the change, and
   never write into the foreign workspace.

## Landing a catalog skill edit

Behavior change → bump the skill's frontmatter `version` and update its
`evals/evals.json` in the same change (an assertion naming a removed
capability ships its removal). Then: describe (plain-English, sign-off +
Co-authored-by trailers) → carve out → rebase onto main → push bookmark
(`jj git push --bookmark <name>`) → PR (query the repo for a template; fill
its shape) → merge on explicit lgtm only. Sign-on-push routes through the
SSH agent: when the agent refuses a headless sign, the push BLOCKS — park
it with the unblock step (operator approves/unlocks the key) rather than
retrying, and never strip signing to force it through.

## Verify-before-claim

- Live skill content: search_files the path on disk after every write
  (skill_view reads a cache that can lag a raw file edit).
- Catalog vs install drift: `jj diff -r @- --stat` IS the delivered diff;
  anything not in it did not land regardless of what the live file shows.
