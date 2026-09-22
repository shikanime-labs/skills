# sks-env — shikanime org environment facts

Environment facts for running the dev loop in shikanime repos (loaded by
`sks-dev-workflow` when operating in shikanime repos):

- Org identity: `shikanime-labs` and `shikanime-studio` GitHub orgs.
- Repo paths: `~/Source/Repos/github.com/<org>/<repo>`; dual-clone
  discipline with the `.hermes/skills` mirror.
- Remote split: local path may say `shikanime-labs` while the gh remote is
  `shikanime-studio` (nix-containers) — the gh remote is canonical.
- Protected-main repos (land via PR only): `shikanime-studio/actions`.
  Rulesets-backed repos (e.g. `manifests`) read as unprotected via the
  classic endpoint — detect via rulesets (body, Branch discipline).
- Commit trailers: `Co-authored-by: Automata
  <automata@shikanime.studio>` (all agent-assisted commits) plus
  repo-mandated `Signed-off-by` (gitlint CC1 on `manifests` and `skills`).
- Push policy: working branches to `origin`; direct push to `main` only on
  explicit user authorization; landing is `gh pr merge --squash` in
  dependency order (see `sks-land`).
- Toolchain: jj + `gh` (no bare git remote inside jj isolation workspaces —
  pass `-R <org>/<repo>`); `nix` for NixOS-class repos.
