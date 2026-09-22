# Example discussion body (pre-issue RFC)

```markdown
## Context

Several skills hard-code `gh` calls that differ by org (`shikanime-labs` vs
`shikanime-studio`), and the local path sometimes disagrees with the gh remote.

## Open question

Should the org be derived from the gh remote (canonical) rather than the local
path, and where should that rule live?

## Affected repos

- shikanime-labs/skills
- shikanime-labs/nix-containers
```

No acceptance criteria, no `- [ ]` tasklist — that belongs in the derived issue.
The discussion converges on the problem; the issue carries the gate. English
bodies only (no French).
