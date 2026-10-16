# Shikanime org conventions

## Boards

Two owner planes; resolve the owner before any `--owner` flag:

- Per-team boards, org-owned — one per org team, the default landing for a
  unit whose family has no user-level board:
  - `shikanime-labs` team `Core`: clone target ownerId `O_kgDOEX1U4A`
    (org node; team node `T_kwDOEX1U4M4BI6uj`)
  - `shikanime-studio` team `Core`: clone target ownerId `O_kgDOBluxIQ`
    (org node; team node `T_kwDOBluxIc4BJ7ti`)
  Both provision on first use (no org-owned board exists yet;
  `shikanime-studio` already owns Reiya/Darkroom/Roadmap for other scopes —
  never reuse those for team `Core`).
- User-level family boards, owner `shikanime` — a family match wins over the
  team default: this catalog → Skills (9); `sks-*` ops (machines,
  manifests) → Shikanime Studio (6); `cpn-*` / cloud-pi-native console →
  Cloud Pi Native (7); upstream OSS (nixpkgs PRs and allies) → Open Source
  Contributions (3).

cloud-pi-native console work always resolves to the org-owned "Socle" board
(project 2, owner `cloud-pi-native`) — that org owns its own boards.

## Provisioning

Template board: project 6, "Shikanime Studio". Clone it with `copyProjectV2`,
template project id resolved at runtime by number (`gh project list --owner
shikanime --format json --jq '.projects[] | select(.number==6) | .id'`) and
`ownerId` = the destination owner's
node id — the org node for a per-team board, the `shikanime` user id
otherwise. The copy inherits its five views with real kanban grouping (the
API cannot set `verticalGroupByFields` on a fresh project), the
Priority/Size fields, and the lifecycle Status vocabulary.
