# Triage Field Rules

The per-field decisions and the pitfalls for `sks-triage`'s step 3.
Read when triaging; the body carries the loop (discover, apply,
verify) and the report shape.

## Decide rules

**Decide** — every field **empty on the item** and **derivable from its
context**; nothing else:

- **type** — defect/regression→`Bug`, new capability→`Feature`,
  chore/tracking→`Task`. Issues only: the API exposes no type on PRs. Skip
  when the repo has no enabled types.
- **labels** — meaning match: defect→`bug`, capability→`enhancement`,
  doc→`documentation`; area label from touched paths only when it exists. Add
  with `--add-label`, never `--label`. Every triaged item also carries exactly
  one `risk:*` label, derived from blast radius: trust boundary, auth,
  secrets, a migration, or a public API/schema change→`risk:high`; behavior
  change in shipped surface→`risk:medium`; docs, comments, typos,
  internal-only→`risk:low`. Only set a risk label when the repo offers it
  (discover step above) — never invent one. `sks-fastlane` consumes the label
  as an eligibility input; its gate is its own.
- **assignee** — if none: the org default assignee
  (`references/shikanime.md`) when present in the eligible list; else
  `$(gh api user --jq .login)`. Always assign — the role is
  participation, not machine-routability.
- **milestone** — never set here; milestone assignment is planning's
  decision and belongs to `sks-plan` (or the org release plane,
  `sks-milestone`). Leave it empty even when open milestones exist.
- **project** — skip when ambiguous, or when the token lacks project scope.
- **relationships** — parent, sub-issues, blockers: only when the body or
  links state them, never inferred.
- **issue fields (issues only)** — the org-defined set, listed per org in
  `references/shikanime.md`. Derive levels from the context
  (blocking severity→Priority, scope/risk→Effort); add dates only when the
  context signals them. Mechanics in `references/issue-fields.md` — the
  write **replaces** all values, so read, merge, write.
- **project card fields** — only on the orgs whose reference enables them
  (the org set and owner facts live in `references/shikanime.md`): when the
  item already sits on a
  Projects V2 board and a card field is empty, mirror the same
  Priority/Effort derivation onto the card via `sks-project` mechanics —
  onboarding a card is `sks-project`'s job, never here. Resolve the board,
  field, and option ids per board at runtime; ids are never portable.
- **pinned (issues only, explicit instruction only)** — a pin is a
  repo-level front-page decision; during a sweep, never pin or unpin.
  On a named issue, per instruction: GraphQL `pinIssue` / `unpinIssue`
  (REST has no endpoint) — mechanics and read-back in `sks-issue-triage`
  step 3.
- **reviewers (PR only)** — none requested → the org default reviewer
  (`references/shikanime.md`) unless they authored the PR (GitHub
  422); then another collaborator; skip if none works.

## Pitfalls

- **`repos/<R>/fields` is the retired path (404).** Org issue fields live at
  `orgs/<org>/issue-fields`; per-issue values at
  `repos/<R>/issues/<N>/issue-field-values`. Discover both.
- **The field write replaces everything.** A payload carrying only the new
  value silently drops existing ones; read current values, merge, write.
  (`POST` to the same path adds without replacing.)
- **Single-select takes the option name** (exact string); dates take ISO
  `YYYY-MM-DD`. Fetch names live — ids and options differ per org.
- **Never `--label`** — it replaces the whole label set; `--add-label` only.
- **On PRs, skip type and fields.** Type writes fail on a PR node
  (`updateIssueIssueType` cannot resolve it). Field values are issue-scoped:
  the endpoint technically accepts a PR's issue object, but org PRs stay
  empty — never set fields on a PR.
- **Enumeration needs `--paginate`** — without it, items above 100 vanish.
- **Empty TSV columns collapse under `read -r`** — trailing/adjacent empty
  fields shift columns left, so an item with all-empty fields can parse as
  complete and be silently skipped. Emit a literal `none` sentinel from jq for
  any column the gap-check treats as emptiness.
- **Sweeps are bounded.** More than CAP items → touch CAP, report the rest;
  never let an unattended run scale with the backlog.
- **Requalification without a trail comment is the defect this mode exists
  to prevent** — a changed field with no old → new comment is a silent
  metadata edit.
- **Do not diagnose, close, or reword here.** Those are `sks-investigate` /
  `sks-issue-triage` / `sks-pr-triage` jobs.
- Payloads and bodies go through files (`--body-file`, `--input`), never
  inline shell arguments.
- **`gh project item-list` truncates around 1000 rows** on large boards —
  absence in its output proves nothing. Cross-check `gh project view N --owner
  ORG --format json | .items.totalCount` and enumerate via GraphQL paging
  (`organization.projectV2.items(first:100, after:$cursor)`, Int vars with `-F`,
  cursor with `-f`).
- **The issue-field `PUT` read-back is a bare array** — the write endpoint
  returns `issue_field_values` itself, so `--jq '.issue_field_values[] | ...'`
  fails with "expected an object but got: array" and any `&&` chain after it
  silently dies. Read back with a `GET` (envelope) or jq the array root.
- **Skill scripts may ship non-executable** (`Permission denied`) — invoke as
  `bash <skill-dir>/scripts/foo.sh`.
- **`repos/<R>/releases` and `/tags` can 404 on private org repos** even with
  repo scope — derive the current minor from `git ls-remote --tags
  --sort=-v:refname` instead.
- **`gh project item-add` takes `--url`, not `--content`** (v2.102) — an
  unknown flag is a per-item fail, easy to miss in a loop; the GraphQL
  `addProjectV2ItemById(contentId:)` mutation is the node-id path.
- **`gh project field-list --format json` can emit raw hex database ids for
  single-select options** (e.g. `39d98c76`, not a node ID). Passing one as an
  `-F` GraphQL variable into `singleSelectOptionId` fails with "Type mismatch
  (ID! / String)" — inline the option id into the query string instead, or
  fetch option ids via GraphQL `projectV2.field(...)` first.
- **`updateProjectV2ItemFieldValue` input fields are `projectId`, `itemId`,
  `fieldId`** (lower d) — the CLI-era `projectV2Id`/`itemID`/`fieldID` casing
  is rejected; introspect `__type(name:"UpdateProjectV2ItemFieldValueInput")`
  when in doubt.
- **`gh` mutations can exit 0 and change nothing** — `--add-reviewer` /
  `--add-assignee` for a login that is not a collaborator is a silent no-op
  (no error, no effect); the read-back is the only truth.
- **List endpoints reflect token scopes** — `type` and
  `issue_field_values` vanish from the issues LIST and
  `orgs/<org>/issue-fields` 404s without `admin:org`, so the scan prints
  `fields=0` and under-reports gaps; scan with the highest-scope token.
  On cpn, `yorha-operator` lacks `admin:org` — export
  `GH_TOKEN=$(gh auth token --user shikanime)` for discovery/field writes
  (it carries `admin:org`), and keep it for the whole run.
  Write permission also splits per token, per repo — verify with one
  cheap mutation before a loop: on cpn, `yorha-operator` is refused on
  issue-field writes ("Must have admin rights to Repository") while the
  shikanime token succeeds, and its label/reviewer/assignee edits
  silently no-op. Run every mutation of the run as
  `GH_TOKEN=$(gh auth token --user shikanime)` — switching tokens
  mid-run to "diagnose" wastes the loop budget.
- **Check the repo's `/labels` before every `--add-label`** — label sets
  differ per repo; a name that exists in one repo may not exist in a
  sibling.
