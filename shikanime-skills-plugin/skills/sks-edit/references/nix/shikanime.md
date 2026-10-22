# Shikanime org conventions

Load when editing Nix in a shikanime repo: the class names below map to
these concrete repos.

- Orgs: `shikanime-labs` and `shikanime-studio`; checkouts at
  `~/Source/Repos/github.com/<org>/<repo>`.
- machines-class fleet-config repo: `shikanime-labs/machines` — NixOS /
  nix-darwin / Home Manager flake (flake-parts + devlib), carries sops-nix
  with per-host `secrets/<host>.enc.yaml` and shared modules `modules/`.
  Convention from this repo: "no explanatory comments in `.nix` files".
- manifests-class render repo: `shikanime-labs/manifests` — kustomize /
  Flux render; Nix generates kustomization YAML (`apps/<app>` trees carry
  `.enc.*` files a whole-tree `nix fmt` can corrupt).
- Commits carry the org co-author trailer
  `Co-authored-by: Automata <automata@shikanime.studio>` (see `sks-commit`).
