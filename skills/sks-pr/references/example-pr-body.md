# Example PR body (restates the commit)

```markdown
# Why

The documented body sections drifted from what actually gets seeded from the
commit, so stacked PRs carried divergent prose. Closing that gap keeps PR↔commit
parity without hand-editing every stacked PR.

## What

- Document the exact PR seed mapping in sks-pr
- Align the sks-pr body template with what GitHub renders

## Verification

None — docs and skill text only.

## References

- Commits: abc1234 (body seed mapping), def5678 (template alignment)
```

Title = commit subject (no conventional prefix). Body sections: `# Why` /
`## What` / `## Verification` (exact proving command + outcome; `none` only
when nothing runs) / `## References`. `## References` carries
proof refs only — the issue link is Development metadata created by
`addCloseIssueReferences` (`sks-pr-triage` step 5), never a body keyword.
Close deliberately after final merge (verify N-of-N).
