# Issue fields

Org-level structured metadata on issues: **Priority**, **Effort**,
**Reproduce** (single-select) plus **Start date** and **Target date** (dates)
in every shikanime org. Blast radius is a `risk:*` label family, not a field.
Load when the target org defines issue fields and an
item has empty or incomplete values.

Every applicable field is filled when an issue is created or triaged. An empty
applicable field is drift, not a placeholder for later. Fields outside the
item's issue type stay unset by decision.

Scope: issues only. The write endpoint technically accepts a PR's issue
object, but org PRs stay empty — never set field values on a PR.

## Discover

```bash
gh api orgs/<org>/issue-fields \
  --jq '.[] | "\(.id)\t\(.name)\t\(.data_type)\t\([.options[]?.name] | join(","))"'
```

Never hardcode field ids — they differ per org. Single-select values are set
by exact option name. **Fetch field ids live at runtime**: the write payload
keys are `field_id` + `value`, resolved from this listing — never from memory
or stale examples, ids are org-scoped numerals.

## Applicability

Field visibility is pinned per issue type in org Settings → Planning →
Issue fields → Field visibility: choose which issue types show the field
when viewing and creating issues. Current pins are `Reproduce` → `Bug`,
`Start date` and `Target date` → `Feature`, and `Priority` and `Effort` →
all three types. This layout is consistent across every shikanime org.
Read the live configuration with GraphQL `IssueType.pinnedFields`; GitHub
exposes no public REST or GraphQL mutation for changing it.

A field not pinned to the item's type stays unset.

## Derive

- **Priority** — blocking severity: blocks other work or red on trunk → `High`;
drop-everything → `Urgent`; routine queue → `Medium`; cosmetically deferred →
`Low`. Default when evidence is silent: `Medium`.
- **Effort** — scope and risk: multi-file or risky → `High`; moderate →
`Medium`; bounded and cosmetic → `Low`. Default: `Medium`.
- **Reproduce** — `Bug` only: `Always`, `Often`, `Rare`, or `None` when
reproduction fails. Default for a bug with no evidence: `None`.
- **Start date** — when work begins: today when picked up. Default for a new
issue with no schedule: today.
- **Target date** — stated deadline or commitment when one exists. Default when
none is stated: seven days after Start date, a planning horizon to revise when a
real commitment appears.

## Read, merge, write

The `PUT` write replaces **all** field values, so never send only the new
one. The endpoint demands a literal field-id numeral in `field_id` and the
option
**name** as a string in `value` — an id in `value` or an option id in a
`single_select_option_id` key is a 422:

```bash
# 0. resolve field ids by name (single source of truth)
FIELDS=$(gh api "orgs/$ORG/issue-fields" \
  --jq '[.[] | {id, name}] | from_entries? // {}')  # jq map name→id

# 1. read current values as {field_id, value} pairs
gh api "repos/$R/issues/$N" \
  --jq '.issue_field_values[] | {field_id: .issue_field_id,
    value: (.single_select_option.name // .value)}'

# 2. write the merged payload from a file (current values + new ones)
gh api -X PUT "repos/$R/issues/$N/issue-field-values" --input payload.json
# payload.json: {"issue_field_values": [
#   {"field_id": <id from step 0>, "value": "High"}]}

# adding without replacing: POST to the same path, with the new values only
# (same payload shape — a bare array or {"values": ...} is also a 422)
```

Dates take ISO `YYYY-MM-DD`; single-select takes the option name.

## Worked example

Issue shikanime-labs/skills#292 — a requested catalog addition typed `Feature`,
no blocker, work picked up the same day: Priority `Medium`, Effort `Medium`,
Reproduce unset because the type is not `Bug`, Start date `2026-09-29`, Target
date `2026-10-06`. The `PUT` echoed all four set values back with their
`single_select_option` names.

## Runtime id resolution

Org field ids and option ids are opaque org-scoped numerals — never paste one
read earlier into a payload or a doc. Resolve at runtime, by name:

```bash
# field id by name
gh api orgs/$ORG/issue-fields --jq '.[] | select(.name=="Priority") | .id'
# option validity check (names, not ids, go in the payload)
gh api orgs/$ORG/issue-fields \
  --jq '.[] | select(.name=="Priority") | [.options[].name]'
```

The read-back (`issue-field-values`) names the field and option — verify
against names, never numerals.
