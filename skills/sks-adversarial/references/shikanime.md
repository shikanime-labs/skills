# Shikanime org conventions

Generic probing procedure; shikanime-org specifics:

- Sandbox commit shape (Automata co-author trailer) and protected-main
  push policy: see `sks-commit` and the org remote split
  (`git@github.com:shikanime-labs/<repo>.git` vs the https gh remote).
- Promotion gates and landing rules for org repos: `sks-dev`.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
- Sandbox image hygiene: a `:ci` tag found staged may be stale from an
  earlier session — before running a probe against `dso-console/*:ci`, verify
  `docker image inspect` RepoDigests against `docker buildx imagetools inspect
  <remote>` for each image; a digest mismatch voids all evidence the probe
  produces. Kill the run, `docker compose down -v`, re-pull, re-tag, re-run.
