# Org conventions

Shikanime-org specifics for `sks-commit`:

- Remote split: the local clone path may read `shikanime-labs` while the gh
  remote is `shikanime-studio` (nix-containers) — trust the gh remote; push to
  `origin` only.
- Protected `main` repos (direct push rejected, land via PR):
  `shikanime-studio/actions`.
- Commit trailer (always, code repos):
  `Co-authored-by: Automata <automata@shikanime.studio>`; DCO
  `Signed-off-by` only where a hook/ruleset requires it (`manifests` —
  gitlint CC1, plus a required body; full URLs in `Related:`).
