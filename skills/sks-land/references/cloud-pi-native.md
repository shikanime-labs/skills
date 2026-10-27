# Cloud-pi-native landing conventions

Load when landing a PR in a `cloud-pi-native/<repo>` repository (default:
console; base `main`).

- **Gate 5 flips vs the shikanime default**: in cloud-pi-native repos the
  commit IS conventional (`fix:` / `feat:` / `chore:` … prefix required) and
  the PR title/body are **French**, with `Refs: <#N>` present. Correct a
  deviation before merge (amend `jj describe` + push) or in a follow-up —
  never merge with a missing prefix or a divergent title.
- Quality Gate CI: SonarQube must show 0 new issues / Quality Gate passed,
  visible via `gh pr checks`.
- **Landing lane (console)**: the `main` ruleset enforces the merge queue
  and squash is disabled repo-wide — rebase is the only merge method, and
  `gh pr merge --squash` (including `--admin`) is rejected. Enter the queue
  with `gh pr merge --auto --rebase -R cloud-pi-native/console`; the
  "merge method set by queue" warning is expected — it registers a REBASE
  merge that lands when the queue batch is green. `--admin` does not bypass
  the queue: it is the only lane, not a fast lane.
- A push after approval dismisses the approval
  (`dismiss_stale_reviews_on_push`): approve after the final push, and
  re-verify the head before any merge command.
- On queue ejection (conflict with another batched PR): never push the
  queue's merge commit — restack the branch onto the updated `main`, push,
  and re-arm `--auto --rebase`.
- Gate 3 approver is the same `yorha-operator` account (see
  `shikanime.md`); GitHub refuses auto-approval when the active
  identity is the author — the approval must come from the `yorha-operator`
  account itself.
- Post-merge issue close uses the French rationale, after ledger N/N +
  user acceptance:
  `gh issue close <N> -R <org>/<repo> -c "Réglée par <PR URL>"`.
  Several PRs may resolve one issue together (`Issues liées` / `Refs`); the
  ledger stays one per issue.
