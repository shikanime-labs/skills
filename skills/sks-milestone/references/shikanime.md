# Shikanime org conventions

## Roster snapshot

Nix repos (root a `flake.nix`, non-archived; verified by live
scan — GitHub repo list ∩ `flake.nix` probe):

- `shikanime-labs`: .github, actions, algorithm, colemak, cpin-operator,
  curriculum-vitae, dashboards, devlib, dotfiles, enhancements, identities,
  knix, machines, manifests, minishells, skills, tailnet, wharf, xqbit
- `shikanime-studio`: .github, hakurei, tailscale-gateway, websites
- `shikanime-x`: curriculum-vitae, enhancements

Re-verify with the discovery step before any batch; when the live scan
disagrees, the scan wins and this snapshot is updated in the same unit.

## Placement rules

- Milestones live on each repo (per-repo GitHub milestones), never on a
  board; the board plane (`sks-project`) tracks cards, this plane tracks
  releases.
- All three orgs take the same release milestones — shikanime-labs,
  shikanime-studio and shikanime-x Nix repos align to the one nixpkgs
  calendar (`references/nixpkgs-calendar.md`).
- Org `.github` repos count when they carry Renovate configs, even where
  they do not root a flake.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
