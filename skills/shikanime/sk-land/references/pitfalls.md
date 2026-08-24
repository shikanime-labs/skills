# sk-land — Pitfalls

Lazily loaded from `SKILL.md`.

- Unchecked criterion — discharge or escalate, don't merge.
- `gh pr merge` on a stacked PR — use `gh stack merge`.
- Merge after new commits without re-review — approval binds to a head commit.
- Auto-close via `Closes #N` at merge — close deliberately after verifying
  ledger.
- Open threads — reconcile first via `sk-pr-resolve`.
