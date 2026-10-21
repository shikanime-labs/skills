# Shikanime org conventions

## Language

- English everywhere in the shikanime family, including commit titles.
- French artifacts belong to the cpn (cloud-pi-native) family only — the
  console repo is the French twin, out of family scope.

## Commit envelope

- Agent-assisted commits and squash merges carry exactly ONE co-author
  trailer: `Co-authored-by: Automata <automata@shikanime.studio>`.
- DCO: gitlint CC1 enforces `Signed-off-by` on the `manifests` and `skills`
  repos; hooks always win over the defaults.
