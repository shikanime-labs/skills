# Shikanime org conventions

Load when operating in a shikanime org (shikanime-labs / shikanime-studio):
template repo, scaffold donors, and commit trailer values.

## Bootstrap references

- Distilled from the live bootstrap of `shikanime-labs/dashboards` (empty
  repo to merged PR).
- Canonical 5-ruleset template payloads live on `shikanime-labs/skills`
  (any already-protected repo works).
- Minimal devlib scaffold donor: `shikanime-labs/colemak` (flake.nix,
  devenv.shells.default with org modules incl. `.shikanime-studio`).

## Commit trailers

Bootstrap commit trailer: `Co-authored-by: Automata
<automata@shikanime.studio>` plus `Signed-off-by`.

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
