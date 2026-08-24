# Example reconcile comment (concrete evidence)

When resolving a pertinent review thread with a fix, cite the diff or command
output — not a prose summary.

```markdown
Resolved. The body now documents the seed mapping; the org is derived from the
gh remote. Before:

-   gh pr create --head "$ORG:<branch>"

After:

-   gh pr create --head "$(gh repo view --json owner,name -q '...'):<branch>"

`gh pr view <N> --json mergeable` returns MERGEABLE after the rebase.
```

The `- old` → `+ new` snippet is the proof; the mergeable query is the gate
check that actually ran.
