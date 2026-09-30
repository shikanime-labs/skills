# Shikanime org conventions

Load when operating in a shikanime org (shikanime-labs / shikanime-studio):
concrete repos, paths, and recipient specifics.

## sops repos and recipients

- Fleet-config repo: `shikanime-labs/machines` — per-host
  `secrets/<host>.enc.yaml`, per-host age key, consumed by `sops-nix`;
  no repo `.sops.yaml`. Per-host files carry `sops_age__*-*` entries for
  that host's key; `nix develop` carries `sops`.
- Render repo: `shikanime-labs/manifests` — fleet `*.enc.env` /
  `*.enc.conf`, THREE fleet age recipients (telsha / nixtar / nishir),
  consumed by Flux `sops` decrypt at reconcile time; no repo
  `.sops.yaml`.

## Commit trailers

Org co-author trailer on commits (see `sks-commit`):
`Co-authored-by: Automata <automata@shikanime.studio>`.
