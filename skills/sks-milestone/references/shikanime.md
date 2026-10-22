# Shikanime org conventions

## Roster snapshot

Nix repos (root a `flake.nix`, non-archived; verified 2026-10-15 by live
scan — GitHub repo list ∩ `flake.nix` probe):

- `shikanime-labs`: .github, actions, algorithm, colemak, cpin-operator,
  curriculum-vitae, dashboards, devlib, dotfiles, enhancements, identities,
  knix, machines, manifests, minishells, skills, tailnet, wharf, xqbit
- `shikanime-studio`: .github, hakurei, tailscale-gateway, websites

22 repos total. Re-verify with the discovery step before any batch; when the
live scan disagrees, the scan wins and this snapshot is updated in the same
unit.

## Placement rules

- Milestones live on each repo (per-repo GitHub milestones), never on a
  board; the board plane (`sks-project`) tracks cards, this plane tracks
  releases.
- Both orgs take the same release milestones — shikanime-labs and
  shikanime-studio Nix repos align to the one nixpkgs calendar
  (`references/nixpkgs-calendar.md`).
- Org `.github` repos count: they root flakes and carry Renovate configs
  that ride the same cadence.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
