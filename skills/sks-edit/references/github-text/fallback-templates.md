# Fallback body shapes (no template found)

Use ONLY when both template probes are empty — the repo `.github/` and the
org `.github` repo (see guide.md "Templates: query, then conform"). A
template found at either level always wins over these shapes; never merge a
template with them.

## PR body

````markdown
# Why

<Why now: the drift/risk/pain this closes — one short paragraph.>

## What

<One-line summary, then bullet the delivered scope.>

## Verification

<The exact proving command or check and its outcome. `none` only when
nothing runs (docs, comments).>

## References

Related: <commits/specs/changelogs proving the solution>
````

The issue link is Development metadata (`addCloseIssueReferences`,
`sks-pr-triage` step 5), never a body line.

## Issue body

````markdown
# Problem

<Problem statement: what is wrong, reproduction steps, affected version,
impact.>

## Acceptance

- [ ] <each item phrased so a command can decide it>

## References

<Docs, linked issues/PRs, commits, changelogs, specs.>
````

Keep the body a stable problem statement; findings and candidate solutions
go in comments. The PR body never borrows the issue shape and vice versa.
Prose rules: guide.md in this directory.
