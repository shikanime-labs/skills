# Shikanime org conventions

Curation notes specific to the shikanime org:

## Commit envelope

- `skills` repo commits: plain capitalized title + labeled body
  (`Design:`/`Related:`) + `Signed-off-by: Shikanime Deva
  <william.phetsinorath@shikanime.studio>` +
  `Co-authored-by: Automata <automata@shikanime.studio>` — landed commits
  carry both trailers.

## Mirror catalog

- Repo doctrine ships only the `sks` and `cpn` skill families; local
  mirror-only categories stay untracked (see body gotchas).
- Mirror catalog lives untracked; syncs can cull it silently. Verified
  2026-09-08: `origin/main` tracks only a subset of the operational catalog
  (~196 `SKILL.md` dirs on disk); whole categories (`apple/`, `media/`,
  `productivity/`, most `devops/` books) exist only as untracked mirror
  files. An `export from jj` sync left the mirror HEAD on a stale tree and
  the untracked layer was gone from disk. Recover from the newest mirror
  commit that still carries the catalog: list additions via
  `git diff --name-only --diff-filter=A origin/main <sha> > <list>`, then
  `git restore --source=<sha> --worktree --pathspec-from-file=<list>`.
  Keep the recovery untracked — repo doctrine ships only the org's curated
  skill families. After any mirror reset or `hermes skills update`,
  spot-check a local-only skill (e.g. a `devops/` book skill) before
  trusting the catalog.
- Local-only skill spot-check example after a mirror reset:
  `devops/envoy-byod-gateway`.
