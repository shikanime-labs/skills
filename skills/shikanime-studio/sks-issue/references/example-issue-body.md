# Example issue body

Two accepted shapes. Both keep the body a stable problem statement; findings
move to comments, never into the tasklist.

## Canonical (sections + `- [ ]` ledger)

```markdown
## Problem

`gh pr create` seeds the PR title/body from the top commit, but the skill's
documented `## What`/`## Why`/`## References` sections are not produced by the
command, so agents write divergent prose.

## References

- gh-stack docs: <https://cli.github.com/extensibility/gh-extension>
- sks-pr: body three-section rule

## Acceptance

- [ ] sks-pr documents the exact PR seed mapping
- [ ] sks-pr body template matches what the PR renders
```

## Variant (`## Problem` / `## Acceptance`, no separate References)

```markdown
## Problem

Same drift as above: the sks-pr body rule is not what the PR seeds.

## Acceptance

- [ ] sks-pr documents the exact PR seed mapping
- [ ] sks-pr body template matches what the PR renders
```

Either shape is acceptable — pick one per issue. An acceptance item is done only
once its check ran, never from memory.
