# Projects V2 Card Mechanics for Triage

Depth for `sks-triage` step 3 when the gap lives on a Projects V2 board
card: detection, onboarding, and the GraphQL shapes that are safe to trust.
Complements `triage-field-rules.md` (field decisions) and
`cloud-pi-native.md` (org board requirements).

## Detect a missing card

An open issue with zero cards is a fill-empty gap wherever the org's
reference makes a card a required output (on cpn, every issue carries a
Socle card):

```graphql
query{repository(owner:"$ORG",name:"$REPO"){issue(number:$N){
  projectItems{totalCount}}}}
```

`totalCount == 0` → onboard; `totalCount > 0` → per-field gap check on the
existing card only. Onboarding during triage overrides the generic
"onboarding is `sks-project`'s job" rule exactly when the org reference
marks the card a required triage output — it already does for cpn.

## Onboard and set fields

1. Resolve the board once: `organization(login:$ORG){projectV2(number:$N)
  {id fields(first:20){nodes{... on ProjectV2SingleSelectField{id name
  options{id name}}}}}}`.
2. Add the card: `addProjectV2ItemById(input:{projectId, contentId:
  <issue node id>})` → keep the returned item id.
3. Set each single-select through `updateProjectV2ItemFieldValue` with
  `projectId` / `itemId` / `fieldId` (lowercase d) and
  `value:{singleSelectOptionId}`.
4. Read back and assert on the option `.name` values.

Derive card values from item context, never invent: Priority mirrors the
org issue field; Epic/category from the domain sibling cards already carry;
Status from the item's event trail and open-fix-PR state.

## GraphQL shape rules

- Introspect on the first `undefinedField`, never iterate guesses — the
  Projects V2 schema differs per type, so every guessed field costs a round
  trip; one `{__type(name:"…"){fields{name}}}` settles the whole shape.
  Guessing twice without introspecting is the failure mode.
- `ProjectV2` exposes `title`, not `name`.
- The single-select option text is `ProjectV2ItemFieldSingleSelectValue.name`
  — there is no `.value` and no `.title` on that type.
- On read-back the owning `field.name` can resolve to null through the
  `ProjectV2FieldConfiguration` union (selections cannot be made directly on
  a union) even when the value landed; assert on the option `.name`, which is
  the reliable evidence.
