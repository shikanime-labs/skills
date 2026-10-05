# Cloud-pi-native triage conventions

Load when triaging an issue in the cloud-pi-native/console repository — the
generic procedure in SKILL.md is unchanged; these are the org overrides.

- Default repo: `R=cloud-pi-native/console`. Transfer targets are other
  `cloud-pi-native/*` repos (and, where fitting, `shikanime-labs/*`).
- Artifact language is **French**, close comments included.
- Issue titles carry the template shape: `🐛 [BUG]` → label `bug`,
  `💡 [REQUEST]` → `enhancement`; never set a label outside
  `gh label list`.
- Org projects: `gh project list --owner cloud-pi-native` (Projects v2).
  The main board is `Socle` (project 2); its Status has no `Ready` option —
  the ready equivalent is `To do`. Custom single-selects worth setting:
  Priority (low/medium/high) and Epic (e.g. `Migration NestJS`); mirror the
  Epic of the closest benchmark card. New console issues may auto-land on a
  PI-exploit board in `Backlog` — that card is not the triage target; check
  `gh issue view --json projectItems`, it shows every card.
- Fallback assignee is the same `yorha-operator` account (see the generic
  `shikanime.md`), still only when it appears in the repo's assignee
  list.
