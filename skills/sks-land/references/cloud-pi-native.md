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
- The `main` ruleset also carries `required_signatures`: a head rewritten
  via `git commit-tree` (plumbing ignores `commit.gpgsign`) lands unsigned
  and the queue hangs CLEAN-armed with no entry. Sign manually:
  `git cat-file commit <sha> > f; ssh-keygen -Y sign -f ~/.ssh/id_ed25519
  -n git f`, splice the sig in as a `gpgsig` last header,
  `git hash-object -t commit -w`, force-with-lease push. Verify via
  GraphQL `object(...) { ... on Commit { signature { isValid } } }` — REST
  `verification` is null org-wide, even for known-good commits.
- Queue merges are rebase: the landed commit IS the branch commit (message
  verbatim) — `-t`/`-b` are cosmetic no-ops; put trailers in the branch
  commit before enrolling.
- Post-merge issue close uses the French rationale, after ledger N/N +
  user acceptance:
  `gh issue close <N> -R <org>/<repo> -c "Réglée par <PR URL>"`.
  Several PRs may resolve one issue together (`Issues liées` / `Refs`); the
  ledger stays one per issue.

## Console merge mechanics

- The repo is queue-only: ruleset `main` rejects `direct_merge` (merge
  queue required + commit signatures; no bypass actors exist, so
  `bypass_rules` is a no-op). Non-stacked PRs: `gh pr merge --auto
  --rebase`. Stacked PRs: `--auto` refuses ("part of a stack"); enqueue
  with `PUT /repos/{o}/{r}/pulls/<n>/merge-async`, body
  `{"merge_action": "merge_queue", "sha": <head>}` — passing
  `merge_method`/`commit_message` alongside is a 422. Then watch the
  `merge_group` run; the queue applies the merge ~30 s after it goes
  green (`mergedAt` lags the green run).
- The queue merge auto-deletes the head branch and auto-retargets a
  stacked child's base to `main`, but the child still descends from the
  pre-rebase SHA: rebase it onto the new `main` (`jj rebase -r <commit>
  -d main`, `jj bookmark set <branch> -r <rebased>`, push) and expect
  its CI to restart from zero.
- The yorha-operator approval must be posted under the operator identity
  itself: switching through yorha-automata hits "Review can not approve
  your own pull request" (author-identity refusal). After any batch that
  switches identities, re-run `gh auth status` before project/admin
  writes — a failed batch leaves the switched identity active, and the
  operator token lacks the `project` scope.
- Socle board card flip: mutation is `updateProjectV2ItemFieldValue`
  (not `updateProjectV2FieldValue`); Status field id
  `PVTSSF_lADOB87hP84BOL8pzg89lR4`, Done option `98236657`; cards can be
  re-homed by deleting the misplaced item (`deleteProjectV2Item` with
  `projectId`+`itemId`) and re-adding against the Socle project id.
- Trailer precedent: agent-authored console PRs may land without
  `Co-authored-by: Automata` when the work is the operator's own (many
  recent precedents); the queue merge method is REBASE, so the landed
  message is the authored commit message — adding trailers late rewrites
  the head and dismisses human approvals (dismiss-on-push is on).
