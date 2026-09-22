# Cloud-pi-native triage conventions

Load when triaging an issue in the cloud-pi-native/console repository — the
generic procedure in SKILL.md is unchanged; these are the org overrides.

- Default repo: `R=cloud-pi-native/console`. Transfer targets are other
  `cloud-pi-native/*` repos (and, where fitting, `shikanime-labs/*`).
- Artifact language is **French**, close comments included.
- Issue titles carry the template shape: `🐛 [BUG]` → label `bug`,
  `💡 [REQUEST]` → `enhancement`; never set a label outside
  `gh label list`.
- Org projects: `gh project list --owner cloud-pi-native` (Projects v2).
- Fallback assignee is the same `yorha-operator` account (see the generic
  `org-conventions.md`), still only when it appears in the repo's assignee
  list.
