# Merge method is ruleset-governed

`pull_request.allowed_merge_methods` restricts what `gh pr merge` accepts:
- `["rebase"]` → `gh pr merge --rebase` (squash rejected).
- `["squash"]` → `--squash`.
- `["merge"]` → `--merge`.
A red required check / protection rejection = a gate doing its job — surface it; never push a disallowed flag unasked.
