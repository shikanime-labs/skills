# sks-edit — Shikanime org conventions

Org map for the fused `sks-edit` skill when operating in a shikanime org repo.
Shared environment facts live in `sks-context`: org identity, checkout paths,
commit trailers, remote split, toolchain. Do not restate them here.

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

Load this file when a write-phase change touches a shikanime org repo and you
need the concrete repo names or the family-to-reference routing. Load
`sks-context` for the ecosystem map.

- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
