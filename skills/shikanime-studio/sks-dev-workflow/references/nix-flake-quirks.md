# Nix / treefmt formatting + devenv escaping (machines-class repos)

Reference for formatting and flake-eval gotchas in shikanime `machines`-class
repos. Loaded on demand from `sks-dev-workflow`; not part of the dev loop.

## nix fmt / treefmt

`nix fmt` runs `treefmt` which applies Nix-specific formatters and a markdown
linter (`rumdl-check`). It fails on any Nix files that are not formatted AND on
markdown files with lines exceeding 80 characters.

- Markdown-only fixes: wrap long lines to ≤ 80 columns, re-run `nix fmt`.
- Mixed (Nix + docs): apply `nix fmt` first, fix remaining markdown errors,
  re-run `nix fmt` until both clean.
- **Do NOT skip `--skip` on markdown** — treefmt runs rumdl-check on all `.md`
  files by default; omitting them needs a treefmt config change (out of scope).

## Nix / devenv escaping gotchas

- **1-backslash `\\${{ }}` rule** — when generating GitHub Actions YAML from Nix,
  escape expressions with a single backslash so the rendered YAML keeps the
  `${{ }}` for the runner, not Nix interpolation.
- **SOPS_AGE_KEY eval env** — flake eval that reads SOPS secrets needs
  `SOPS_AGE_KEY` in the environment; export it before `nix eval`/`nix build`.
- **catbox under `packages`, not `nixosConfigurations`** — container/image builds
  belong in `packages`, not `nixosConfigurations`.
