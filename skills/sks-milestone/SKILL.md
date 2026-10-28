---
name: sks-milestone
description:
  "Use when provisioning nixpkgs-release-aligned milestones across the org's
  Nix repos: discover the flake roster, create per-release milestones, assign
  issues and PRs, audit drift."
version: 0.3.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - milestones
      - nix
      - release-management
    related_skills:
      - sks-triage
      - sks-issue-triage
      - sks-pr-triage
      - sks-project
      - sks-plan
      - sks-bulk
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Release Milestones

Milestone plane for the target orgs' Nix repos: one milestone per nixpkgs
release, titled after the release (`26.11`), due on its ship date, present on
every Nix repo the orgs ship. Items that move a repo's nixpkgs baseline
(flake.lock bumps, module fixes for the new release) land on the current
release milestone; drift is auditable per repo.

Org facts — the target orgs, the Nix repo roster snapshot, and placement
rules — live in `references/shikanime.md`; the release calendar in
`references/nixpkgs-calendar.md`. cloud-pi-native repos follow a different
convention — load `references/cloud-pi-native.md` when the target repo is
cloud-pi-native.

## When to Use

- "Create the 26.11 milestones across our Nix repos" — provision the plane.
- An issue or PR bumps nixpkgs or targets the release — assign the milestone
  (also reached from `sks-triage` sweeps).
- "Which repos still lack the current release milestone?" — audit.
- A release just shipped — close its milestone, provision the next.

## Milestone shape

| Field    | Value                                                       |
| -------- | ----------------------------------------------------------- |
| title    | nixpkgs release, `YY.MM` (`26.11`)                          |
| due_on   | release date from `references/nixpkgs-calendar.md`, ISO UTC |
| state    | open until the release ships, then closed                   |
| description | `<release> (<code name>)` — e.g. `26.11 (Zokor)`          |

One milestone per release per repo — no patch granulation; the nixpkgs
cadence is the only cadence. Provisioning the next release closes the
previous release's milestone on every roster repo.

## Title convention

Milestone titles follow the same title standard as every other org surface
(`sks-commit` subject, `sks-pr` title, `sks-issue` title): plain-English
capitalized text, version identifiers verbatim, no conventional prefixes, no
kebab slugs — the milestone is not the surface to decorate or slugify them.

| Milestone class | Title shape                        | Example                     |
| --------------- | ---------------------------------- | --------------------------- |
| Release         | `YY.MM` verbatim                   | `26.11`                     |
| Semver train    | `X.Y.Z` verbatim                   | `9.28.0`                    |
| Product train   | `vX.Y — <Qualifier>`               | `v1.2 — Open World & Progression` |
| Goal            | plain English, capitalized, ≤ 72 chars | `Hetzner inference support` |

- Never retitle a version identifier into prose: a `YY.MM`, `X.Y.Z`, or
  `vX.Y — <Qualifier>` title already conforms — adding a `Release` prefix,
  a code name, or any other decoration breaks the addressing contract
  (`gh issue edit --milestone` and `gh pr edit --milestone` take the title
  verbatim).
- A goal title is capitalized text, not a slug: `Hetzner inference support`,
  never `hetzner-inference-support` or `Add the Hetzner inference support
  milestone`. No conventional prefix (`feat:`) — the family bans prefixes on
  every surface.

### Backfill rename

Fixing a drifted title is a PATCH on the milestone — the number is stable,
items and audit history follow the title:

```bash
gh api repos/<org>/<repo>/milestones/<number> -X PATCH \
  -F title="<conforming title>"        # -F: no expansion; the title is literal
gh api repos/<org>/<repo>/milestones  --jq '.[].title'   # read back
```

Batch shape: every rename lands behind the gated sks-bulk table — repo,
milestone number, old title, new title — approved before the first PATCH.

## Procedure

### 1. Discover the Nix repo roster

Live enumeration, never the snapshot alone — the roster shifts with renames,
archives, and new repos:

```bash
# ORGS — the target orgs (org fact, references/shikanime.md)
for org in $ORGS; do
  gh repo list "$org" --limit 200 --json name,isArchived \
    --jq '.[] | select(.isArch | not) | .name' \
    | while read -r r; do
        gh api "repos/$org/$r/contents/flake.nix" --jq .name >/dev/null 2>&1 \
          && echo "$org/$r"
      done
done
```

A repo ships Nix iff it roots a `flake.nix`; archived repos drop out at the
list step. When the live count disagrees with `references/shikanime.md`,
the live scan wins — update the snapshot in the same unit.

### 2. Provision (or verify) the release milestone

Idempotent per repo — create only when the title is absent:

```bash
gh api repos/<org>/<repo>/milestones --input payload.json
# payload.json: {"title": "26.11", "state": "open",
#                "description": "26.11 (Zokor)",
#                "due_on": "2026-11-23T12:00:00Z"}   # midday UTC — midnight
#                anchors a day early in western timezones (date-only storage)
gh api repos/<org>/<repo>/milestones --jq '.[].title'   # read back
```

A full-roster roll is a gated batch (`sks-bulk` shape): present the table —
repo, action (create / exists / skip), title, due — and wait for approval.
Creation is additive only; never delete or edit an existing milestone here.

### 3. Assign items

```bash
gh issue edit "$N" --repo "$R" --milestone "26.11"   # by TITLE, not number
gh pr edit "$N" --repo "$R" --milestone "26.11"
```

Assignable: the item's diff moves `flake.lock`, touches nixpkgs-derived
packages or modules, or explicitly targets the release. Unrelated work stays
milestone-less — an empty milestone is honest, a wrong one is noise.

### 4. Audit

```bash
gh api repos/<org>/<repo>/milestones \
  --jq '.[] | "\(.title) open=\(.open_issues) closed=\(.closed_issues)"'
```

Offenders: a roster repo missing the current title; a shipped release whose
milestone is still open; items whose diff bumps nixpkgs but sit milestone-less
(`sks-triage` finds those in its scan).

## Pitfalls

- **Milestones are addressed by title.** `--milestone 12` fails with
  "'12' not found"; the number is not an identifier.
- **`due_on` needs a full ISO timestamp with timezone**
  (`2026-11-23T00:00:00Z`), not a bare date; a bare date 422s.
- **The roster is live, not memorized.** Re-run discovery every cycle; the
  snapshot in `references/shikanime.md` dates fast.
- **Closing a milestone does not close its items.** GitHub leaves orphan
  items open with the milestone greyed; sweep them before closing.
- **cloud-pi-native repos never take release milestones** — a different
  convention applies (`references/cloud-pi-native.md`), even where the repo
  roots a `flake.nix`.
- **A due date is a commitment.** It comes from the calendar reference only;
  never invent one to fill the field.
- **Version identifiers are titles — never retitle them into prose.** A
  `YY.MM`, `X.Y.Z`, or `vX.Y — <Qualifier>` title already conforms;
  decorating it (`Release 26.03`) breaks the by-title addressing contract
  (Title convention).
- **A rename is a PATCH, never delete-and-recreate.** The PATCH keeps the
  number, and items keep their milestone through a title change; recreating
  drops assignments and the audit trail (Backfill rename).

## Verification

```bash
gh api repos/<org>/<repo>/milestones --jq '.[].title'   # plane present
gh api repos/<org>/<repo>/issues/<N> --jq .milestone.title   # assignment landed
```

Conformance audit — every title across both orgs against the Title
convention table:

```bash
for org in shikanime-labs shikanime-studio; do
  for r in $(gh repo list "$org" --limit 300 --json name,isArchived \
      --jq '.[] | select(.isArchived==false) | .name'); do
    gh api "repos/$org/$r/milestones?state=all" \
      --jq '.[] | .title
      | select(test("^[a-z]|^Release") and (test("^v[0-9]") | not))' \
      | sed "s|^|$org/$r: |"
  done
done
```

An empty audit output means every title conforms.

## See also

- `sks-triage` / `sks-issue-triage` / `sks-pr-triage` — per-item assignment
  during sweeps; this skill is the provisioning plane behind them.
- `sks-commit` / `sks-pr` / `sks-issue` — the family title standard this
  skill's Title convention extends to milestones.
- `sks-project` — the board plane (cards and Status); milestones track
  releases, boards track work.
- `sks-plan` — fills a work milestone with planned units; provisioning the
  release plane stays here.
- `sks-bulk` — the gated batch shape for a full-roster roll.
