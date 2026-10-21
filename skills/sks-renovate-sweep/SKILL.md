---
name: sks-renovate-sweep
description:
  "Use when landing or triaging open renovate PRs across an org's repos:
  check green on the exact head, land eligible ones, report the rest."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - renovate
      - github
      - landing
      - triage
    related_skills:
      - sks-land
      - sks-issue
      - sks-audit
platforms:
  - linux
  - macos
  - windows
---

# Renovate Sweep

A landing pass over open renovate PRs across the org's repos: every PR with
green checks on its exact head lands; everything else gets one reported line
with its blocking reason. Red-for-days PRs become summary issues. Landing
runs only under standing operator authorization or an explicit go-ahead.

Org-specific scope (org names, landing mechanics, repo quirks) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Land the renovate PRs" / "sweep renovate across the org".
- A recurring dependency-PR pass: enumerate, triage, land, report.
- One stuck renovate PR a human asks about — same triage per PR.

## Procedure

1. **Enumerate.** `gh repo list <org> --limit 100 --json nameWithOwner` per
   org, then `gh pr list -R <repo> --author app/renovate --state open --json
   number,title,headRefName,updatedAt,statusCheckRollup`. Completion check:
   every repo scanned, every open renovate PR recorded.

2. **Triage per PR.** Green checks on the exact head → eligible. Red checks →
   read `gh pr checks <n>` and the failing job's first error lines
   (`gh run view <run> --log-failed`). Stalled (no check runs, CI not
   triggered) → note the re-arm path per repo quirk. Branch behind main with
   a merge conflict → drop from this pass; renovate rebases those itself.

3. **Land eligible PRs.** Under standing operator authorization or explicit
   go-ahead: land each eligible PR per repo landing mechanics. Never merge
   past a red required check or a stale head (head sha moved after the checks
   ran → re-check, do not merge).

4. **Report the rest.** One line per PR: repo, number, update, check state,
   blocking reason when red.

5. **Escalate chronic reds.** A PR red for 3+ consecutive days with the same
   error: one summary issue in its repo with the error pattern; assign per
   repo policy where eligible.

## Pitfalls

- Checks must be green on the PR's CURRENT head sha — a green run on an older
  sha is stale; re-check after any renovate rebase before landing.
- A red required check is a gate doing its job: surface it, never force-past
  it. `--admin` bypass belongs to the repo's landing skill and only after the
  gate verdict is green or explicitly waived.
- Renovate rebase conflicts resolve themselves on the next renovate run —
  manually rebasing renovate branches invites tug-of-war; drop and report.
- Landing without the human gate is the classic failure: the sweep inherits
  authorization from the operator's standing policy or explicit go-ahead;
  neither present, it reports only.

## Verification

```bash
gh pr list -R <repo> --author app/renovate --state open
# landed PRs verify here:
gh pr view <n> -R <repo> --json state,mergedAt,headRefOid
```

Report states: PRs enumerated, landed (links), reported with reasons, summary
issues filed.

## See also

- `sks-land` — landing mechanics and approval gates.
- `sks-issue` — issue body shape for chronic-red summaries.
- `sks-audit` — the CI-failure sweep that ignores renovate PRs.
