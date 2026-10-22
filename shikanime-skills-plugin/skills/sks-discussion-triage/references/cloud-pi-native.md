# cloud-pi-native discussion-triage specifics

Load when working in the cloud-pi-native/console repository.

## Org identity

- Default repo: `R=cloud-pi-native/console` — Issues disabled, Discussions
  active; GraphQL examples use `repository(owner: "cloud-pi-native",
  name: "console")`.
- Artifact language: **français** (comments, close rationales).
- Category routing (cloud-pi-native): RFC/design → `Ideas` ;
  décision/discussion → `General` ; question → `Q&A`.

## Procedure deltas vs the generic flow

- A "discussion issue" request routes here as a _discussion_, never a GitHub
  Issue — derive the issue (`sks-issue`) only once converged.
- Triage has no labels/assignees: category + lifecycle routing only, GraphQL
  only, mutations via `--input` (never `-F variables=@file`), no
  `gh issue edit`, no REST.
- Probe first: `gh api repos/"$R" --jq .has_discussions` — 404 when
  Discussions are disabled.
- Body trim keeps contexte + questions ouvertes; a converged discussion is
  commented then routed to the issue flow, not resolved in-thread; closure is
  never silent (motif comment before
  `closeDiscussion(... RESOLVED|DUPLICATE|OUTDATED)`).
