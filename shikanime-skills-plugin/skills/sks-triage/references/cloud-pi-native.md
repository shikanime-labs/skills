# Cloud-pi-native specifics

Load when triaging a PR, issue, repo, or org item in a cloud-pi-native org
repo — overrides the shikanime defaults while the generic steps in SKILL.md
still apply.

- Default repo: `cloud-pi-native/console`.
- Artifact language: **French** for user-facing text (sweep reports,
  comments); repo values (labels, milestones, field options) stay as stored.
- Default reviewer: `yorha-operator` — skip when it authored the PR (GitHub
  422) or is not a collaborator of the target repo.
- Projects: never add draft PRs or PRs closed as "not planned" to any org
  project — abandoned work does not belong on boards.
- In this org the Development link and the Projects section are REQUIRED
  triage outputs, never skips: a PR ships with its `addCloseIssueReferences`
  link to the issue and a card on the `Socle` board (project 2); an issue
  ships with a Socle card. The generic "skip when ambiguous / token lacks
  scope" exemptions do not apply here — Socle is the unambiguous default
  board and the token has project scope.
- Issue fields: the org defines Priority, Effort, Start date, Target date —
  same mechanics as `references/issue-fields.md`; fetch ids per org.
