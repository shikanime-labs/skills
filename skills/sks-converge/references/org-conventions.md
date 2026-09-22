# Org conventions

Generic conflict/divergence convergence; shikanime-org specifics:

- The org remote split (ssh `git@github.com:shikanime-labs/<repo>.git` vs the
  https gh remote) and protected-main landing rules: `sks-dev-workflow`.
- Push signing behavior used on this host: `--config signing.behavior=drop
  --config git.sign-on-push=false` (GitHub squash-merge re-signs
  server-side).
