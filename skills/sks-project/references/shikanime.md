# Shikanime org conventions

## Boards

- All Projects V2 boards belong to user `shikanime`; the orgs themselves own
  no boards — pass `--owner shikanime` everywhere.
- Board resolution table: this catalog → Skills (9); `sks-*` ops (machines,
  manifests) → Shikanime Studio (6); `cpn-*` / cloud-pi-native console →
  Cloud Pi Native (7); upstream OSS (nixpkgs PRs and allies) → Open Source
  Contributions (3).
- Template board for provisioning: project 6, "Shikanime Studio"
  (`copyProjectV2` id `PVT_kwHOAVFzJM4BNT_b`). The copy inherits its five
  views with real kanban grouping (the API cannot set
  `verticalGroupByFields` on a fresh project), the Priority/Size fields, and
  the lifecycle Status vocabulary.
