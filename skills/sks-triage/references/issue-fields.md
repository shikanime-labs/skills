# Issue fields

Org-level structured metadata on issues: **Priority** and **Effort**
(single-select) plus **Start date** and **Target date** (dates) on both
shikanime orgs. Load when the target org defines issue fields and an item has
empty or incomplete values.

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

## Derive

- **Priority** — blocking severity: blocks other work or red on trunk →
  `High`; drop-everything → `Urgent`; routine queue → `Medium`; cosmetically
  deferred → `Low`.
- **Effort** — scope and risk: multi-file or risky → `High`; moderate →
  `Medium`; bounded and cosmetic → `Low`.
- **Start date** — only when the context signals work begins (actively picked
  up → today).
- **Target date** — only for a stated deadline or commitment; never invented.

## Read, merge, write

The `PUT` write replaces **all** field values, so never send only the new
one. The endpoint demands a literal field-id numeral in `field_id` and the option
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

Issue shikanime-labs/skills#292 — a requested catalog addition, no blocker,
work picked up the same day: Priority `Medium`, Effort `Medium`, Start date
`2026-09-29`, Target date `2026-09-30`. The `PUT` echoed all four values back
with their `single_select_option` names.

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
