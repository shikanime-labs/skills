# Skk-edit references — Shikanime org conventions

Routing for the fused `sks-edit` skill. This directory holds the org-convention
entry point every authoring family points at; the family skills own their own
deep `references/`.

## `sks-edit` consumers

- `sks-ts-authoring` (TypeScript) → `references/shikanime.md`
- `sks-nix-authoring` (Nix) → `references/shikanime.md`
- `sks-sops-secrets-authoring` (sops secrets) → `references/shikanime.md`
- `sks-kubernetes-manifests-authoring` (Kubernetes manifests) → `references/shikanime.md`
- `sks-wiki` (GitHub wiki) → `references/shikanime.md`

## Shikanime org conventions

This repo (`shikanime-labs/skills`) ships the authoring families below. Concrete
org repos live at `~/Source/Repos/github.com/shikanime-labs/<repo>` (see
`sks-context` for the ecosystem map).

### Authoring families shipped here

| Family | Skill | Trigger |
| --- | --- | --- |
| TypeScript | `sks-ts-authoring` | `.ts` / `.tsx` under `apps/` or shared packages |
| Nix | `sks-nix-authoring` | `.nix` in a flake / module |
| Skill creation | `sks-skill-authoring` | new skill / profile under `skills/` |
| SOPS secrets | `sks-sops-secrets-authoring` | `*.enc.*` files |
| Kubernetes manifests | `sks-kubernetes-manifests-authoring` | manifests / `kustomization.yaml` |
| Plain English | `sks-text-authoring` | docs / runbooks / commit / PR / issue body |
| GitHub wiki | `sks-wiki` | `*.md` under a `.wiki` remote |

### Commit conventions

Commits carry the org co-author trailer
`Co-authored-by: Automata <automata@shikanime.studio>` (`sks-commit`).

### Paths

- Fleet-config repo: `shikanime-labs/machines`
- Render repo: `shikanime-labs/manifests`
- All org checkouts: `~/Source/Repos/github.com/shikanime-labs/<repo>`

Load this file when a write-phase change touches a shikanime org repo and you
need the concrete repo names, paths, or recipients.
