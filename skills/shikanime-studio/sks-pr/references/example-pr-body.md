# Example PR body (restates the commit)

```markdown
## What
- Document the exact `gh stack submit` seed mapping in sks-pr
- Align the sks-pr body template with what `gh stack` emits

## Why
The body three-section rule drifted from what `gh stack submit` actually seeds
from the commit, so stacked PRs carried divergent prose. Closing that gap keeps
PR↔commit parity without hand-editing every stacked PR.

## References
Related: https://github.com/shikanime-labs/skills/issues/123
```

Title = commit subject (no conventional prefix). `## References` carries
`Related: <full URL>`; close deliberately after final merge (verify N-of-N).
