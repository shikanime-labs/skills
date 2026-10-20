# Shikanime org conventions

Shikanime-org specifics for `sks-commit`:

- Remote split: the local clone path may read `shikanime-labs` while the gh
  remote is `shikanime-studio` (nix-containers) — trust the gh remote; push to
  `origin` only.
- Protected `main` repos (direct push rejected, land via PR):
  `shikanime-studio/actions`.
- Commit co-author trailer: owned by SKILL.md
  (`Co-authored-by: Automata <automata@shikanime.studio>`, unconditional
  default); DCO `Signed-off-by` only where a hook/ruleset requires it
  (`manifests` — gitlint CC1, plus a required body; full URLs in `Related:`).
- Gitlint-strict repo example: `manifests` enforces a required **body** (B6
  "body message is missing") and a `Signed-off-by` (CC1); a commit with both
  and a full-URL `Related:` passes.
