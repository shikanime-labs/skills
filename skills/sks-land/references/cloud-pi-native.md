# Cloud-pi-native landing conventions

Load when landing a PR in a `cloud-pi-native/<repo>` repository (default:
console; base `main`).

- **Gate 4 flips vs the shikanime default**: in cloud-pi-native repos the
  commit IS conventional (`fix:` / `feat:` / `chore:` … prefix required) and
  the PR title/body are **French**, with `Refs: <#N>` present. Correct a
  deviation before merge (amend `jj describe` + push) or in a follow-up —
  never merge with a missing prefix or a divergent title.
- Quality Gate CI: SonarQube must show 0 new issues / Quality Gate passed,
  visible via `gh pr checks`.
- Gate 2 approver is the same `yorha-operator` account (see
  `org-conventions.md`); GitHub refuses auto-approval when the active
  identity is the author — the approval must come from the `yorha-operator`
  account itself.
- Post-merge issue close uses the French rationale, after ledger N/N +
  user acceptance:
  `gh issue close <N> -R <org>/<repo> -c "Réglée par <PR URL>"`.
  Several PRs may resolve one issue together (`Issues liées` / `Refs`); the
  ledger stays one per issue.
