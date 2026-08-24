# sks-land — Pitfalls

- Unchecked criterion — discharge or escalate, don't merge.
- `gh pr merge` on a stacked PR — use `gh stack merge`.
- Merge after new commits without re-review — approval binds to a head commit.
- Auto-close via `Closes #N`/`Fixes #N` at merge — fires before the ledger is
  verified; close deliberately after N-of-N.
- Open threads — reconcile first via `sks-pr-resolve`.
