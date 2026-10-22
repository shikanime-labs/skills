# Cloud-pi-native PR triage specifics

Load when triaging a PR in a cloud-pi-native org repo — overrides the
shikanime defaults while the generic steps in SKILL.md still apply.

- Default repo: `cloud-pi-native/console` (`gh project list --owner
  cloud-pi-native`).
- Fallback reviewer: `yorha-operator` (Automata account) — skip when it
  authored the PR (GitHub 422).
- Development link and Projects are required outputs, not best-effort: a
  triaged PR must carry its `addCloseIssueReferences` link (step 5 is
  mandatory when a driving issue exists) and a card on the `Socle` board
  (project 2). PR cards land in `To review`; the auto-added card may
  already exist — read `projectItems` first and only set the missing
  Status.
- Artifact language: **French** (labels/assignee/milestone values unchanged —
  repo-existing only).
