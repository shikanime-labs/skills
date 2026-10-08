# Example PR body (restates the commit)

```markdown
# Why

The body three-section rule drifted from what actually gets seeded from the
commit, so stacked PRs carried divergent prose. Closing that gap keeps PR↔commit
parity without hand-editing every stacked PR.

## What

- Document the exact PR seed mapping in sks-pr
- Align the sks-pr body template with what GitHub renders

## References

- Commits: abc1234 (body seed mapping), def5678 (template alignment)
```

Title = commit subject (no conventional prefix). `## References` carries
proof refs only — the issue link is Development metadata created by
`addCloseIssueReferences` (`sks-pr-triage` step 5), never a body keyword.
Close deliberately after final merge (verify N-of-N).
