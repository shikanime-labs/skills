# Shikanime org conventions

Load when editing sops-encrypted files in a shikanime repo: concrete repos,
paths, and recipient specifics.

- Fleet-config repo: `shikanime-labs/machines` — per-host
  `secrets/<host>.enc.yaml`, per-host age key, consumed by `sops-nix`;
  no repo `.sops.yaml`. Per-host files carry `sops_age__*-*` entries for
  that host's key; `nix develop` carries `sops`.
- Render repo: `shikanime-labs/manifests` — fleet `*.enc.env` /
  `*.enc.conf`, THREE fleet age recipients (telsha / nixtar / nishir),
  consumed by Flux `sops` decrypt; no repo `.sops.yaml`.
- Org co-author trailer on commits (see `sks-commit`):
  `Co-authored-by: Automata <automata@shikanime.studio>`.
