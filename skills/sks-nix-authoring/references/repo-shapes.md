# Repo shape differences: machines vs manifests Nix

Loaded by `sks-nix-authoring` when the repo could be either class and the
edit touches sops wiring or rendered YAML. The style rules are identical;
only the surface differs.

- **machines-class flakes** (NixOS / nix-darwin / Home Manager,
  flake-parts + the shared lib): the flake carries sops-nix, per-host
  `secrets/<host>.enc.yaml`, and the shared modules under `modules/`. When
  you touch sops-nix wiring, the sops side (recipients, templates,
  `sopsFile`) is a secret edit — involve `sks-sops-secrets-authoring`
  for the `.enc.*` part. The Nix part is this skill.
- **manifests-class flakes** (kustomize / Flux render, kustomization YAML as
  Nix output): the Nix here generates YAML. Sorting and formatting still
  apply to the Nix; the generated YAML sorting and structure are the
  manifests skill's territory. Do not hand-edit the generated YAML to
  "fix" sorting — fix the Nix that produces it, then re-render.
