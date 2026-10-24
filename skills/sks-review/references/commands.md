# Command Cheat-Sheet

Scope and read the diff:

```bash
jj diff --stat                                   # scope + size
jj diff --name-only                              # which files
jj diff                                          # full working-copy diff
jj diff --from main --to @                        # vs trunk
jj log -r '::@' -T 'commit_id ++ " " ++ description'   # commits in range
```

Security scan (added lines): see `security-scan.md`.

Tests / lint (skip silently if absent; only NEW failures block):

```bash
python -m pytest --tb=no -q 2>&1 | tail -5         # Python
npm test -- --passWithNoTests 2>&1 | tail -5       # Node
cargo test 2>&1 | tail -5                          # Rust
go test ./... 2>&1 | tail -5                       # Go
which ruff && ruff check . 2>&1 | tail -10         # Python lint
which npx && npx eslint . 2>&1 | tail -10          # Node lint
cargo clippy -- -D warnings 2>&1 | tail -10        # Rust lint
which go && go vet ./... 2>&1 | tail -10            # Go vet
```

Independent reviewer dispatch: see `review-doctrine.md`.

Post the review: see `inline-comments.md`.

```bash
gh pr view <N> && gh pr diff <N> --name-only       # PR context
gh pr checkout <N>                                  # local PR copy
gh pr review <N> --request-changes --body "..."     # post verdict
```
