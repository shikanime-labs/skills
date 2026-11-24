# Cloud-pi-native specifics

Load when triaging a PR, issue, repo, or org item in a cloud-pi-native org
repo — overrides the shikanime defaults while the generic steps in SKILL.md
still apply.

- Default repo: `cloud-pi-native/console`.
- Artifact language: **French** for user-facing text (sweep reports,
  comments); repo values (labels, milestones, field options) stay as stored.
- Reviewer: fill-empty only — request `yorha-operator` when a PR carries
  no review request; skip when it authored the PR (GitHub 422), or when
  it is not a collaborator of the target repo — on `console` it is NOT
  one, so every reviewer request there exits 0 with an empty
  `reviewRequests` read-back. Prove collaborator status with
  `gh api repos/<R>/collaborators/<login>` before requesting; record
  the skip instead of retrying.
- Architecture decisions governing an issue live in the
  `documentation-interne-socle` repo,
  `architectural-decision-record/NNN-slug.md` (Nygard template; status
  `Proposed` still governs). On a realign request, read the latest ADR
  first: its prerequisites become `addBlockedBy` relations with a trail
  comment citing the ADR section, before any new issue is minted.
- Projects: never add draft PRs or PRs closed as "not planned" to any org
  project — abandoned work does not belong on boards.
- In this org the Development link and the Projects section are REQUIRED
  triage outputs, never skips: a PR ships with its `addCloseIssueReferences`
  link to the issue and a card on the `Socle` board (project 2); an issue
  ships with a Socle card. The generic "skip when ambiguous / token lacks
  scope" exemptions do not apply here — Socle is the unambiguous default
  board and the token has project scope.
- Issue fields: the org defines Priority, Effort, Start date, Target date —
  same mechanics as `references/issue-fields.md`; fetch ids per org (current
  numerals: Priority 25078554, Effort 25078557, Start date 25078555,
  Target date 25078556).
- Assignee default: `yorha-operator` is a READ-ONLY collaborator on
  `console` — every `--add-assignee` for it there is a silent no-op (exit
  0, no effect; verify with the `assignees` read-back, never the exit
  code). Fall back to the operator account (`shikanime`) per the
  current-user rule, and prove eligibility with
  `gh api repos/<R>/collaborators/<login>/permission --jq .permission`.
- The repo defines NO `task` label — refactor/internal work is tracked via
  the existing `refactor` + `technical debt` + `internal` labels; never
  invent the missing label (discover-first holds).
