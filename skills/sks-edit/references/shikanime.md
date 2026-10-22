# sks-edit — Shikanime org conventions

Org map for the fused `sks-edit` skill when operating in a shikanime org repo.
Concrete repos live at `~/Source/Repos/github.com/shikanime-labs/<repo>` (see
`sks-context` for the ecosystem map).

## Commit conventions

Commits carry the org co-author trailer
`Co-authored-by: Automata <automata@shikanime.studio>` (`sks-commit`).

## Paths

- Fleet-config repo: `shikanime-labs/machines`
- Render repo: `shikanime-labs/manifests`
- All org checkouts: `~/Source/Repos/github.com/shikanime-labs/<repo>`

## Family entry points inside this skill

| Family | Guide | Org notes |
| --- | --- | --- |
| TypeScript | `typescript/guide.md` | console TS surface: `typescript/cloud-pi-native-console.md` |
| Nix | `nix/guide.md` | fleet shapes: `nix/repo-shapes.md` |
| Skill creation | `skill-authoring/guide.md` | — |
| sops secrets | `sops-secrets/guide.md` | Flux manifests: `sops-secrets/sops-manifests.md` |
| Kubernetes manifests | `kubernetes-manifests/guide.md` | live cross-check: `kubernetes-manifests/live-cross-check.md` |
| Plain English | `text/guide.md` | — |
| GitHub wiki | `wiki/guide.md` | Home seeding: `wiki/wiki-home-cdp.md` |

Load this file when a write-phase change touches a shikanime org repo and you
need the concrete repo names, paths, or the family-to-reference routing.
