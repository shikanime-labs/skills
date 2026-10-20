---
name: sks-github-issues-sweep
description:
  "Use when sweeping GitHub issues across an org's repos: enumerate open
  issues, dedup against prior coverage, surface stale or silent ones, and
  file summary issues for systemic patterns."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - triage
      - sweep
    related_skills:
      - sks-triage
      - sks-issue
      - sks-github-notif-sweep
      - sks-github-actions-audit
platforms:
  - linux
  - macos
  - windows
---

# Issues Sweep

An org-wide enumeration pass over open GitHub issues: every repo in scope,
every open issue recorded, staleness and silence detected, systemic patterns
filed as summary issues. Field assignment belongs to `sks-triage`; closing
belongs to no sweep.

Org-specific scope (org names, assignee policy) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Sweep issues across the org" / "what's piling up untriaged".
- A recurring issues pass: enumerate, dedup, detect, file summaries.
- A backlog review after time away — same rules, bigger batch.

## Procedure

1. **Enumerate per repo.** `gh repo list <org> --limit 100 --json
   nameWithOwner` per org, then `gh issue list -R <repo> --state open --json
   number,title,labels,assignees,createdAt,updatedAt` (PRs are a different
   surface — this sweep reads issues only). Completion check: every repo
   scanned, every open issue recorded.

2. **Dedup against prior coverage.** An issue already labeled, assigned, or
   covered by a previous run is listed, not re-processed. Cross-check
   `updatedAt` against the last run's coverage (cron output dir or run memory
   when the harness has it).

3. **Detect the actionable classes.** Unlabeled or unassigned issues older
   than 48h; issues awaiting a first reply for 7+ days; duplicate clusters
   (same root cause filed multiple times). Record per item: repo, number,
   class, age.

4. **File systemic findings as summary issues.** A pattern spanning issues
   or repos (repeat failure, cross-repo drift) becomes ONE summary issue in
   the repo where it belongs, linking its members — never one issue per
   member re-filed.

5. **Hand off, never close.** Field assignment (type/area labels, assignee,
   milestone) routes to `sks-triage`; answerable question comments route to
   `sks-github-notif-sweep` rules. The sweep closes nothing and notes items
   resolved since the last pass.

## Pitfalls

- `gh issue list` omits PRs by design, but `gh issue list --search` can
  re-include them via matched text — filter `is:pr` out of any search-based
  pass or the report mixes surfaces.
- Duplicate detection on title similarity alone files false summaries;
  cluster on the underlying error or object reference, spot-check each
  cluster before filing.
- Repo enumeration with `--limit 100` silently truncates bigger orgs; page
  with `--paginate` or reconcile against a known repo count.
- An issue old but actively discussed is not stale — age gates apply to the
  LAST activity (`updatedAt`), never to `createdAt` alone.

## Verification

```bash
gh repo list <org> --limit 100 --json nameWithOwner --jq 'length'
gh issue list -R <repo> --state open --json number --jq 'length'
```

Report states: repos scanned, issues open per repo, actionable classes with
ages, summary issues filed (links), handoffs to triage, resolved since last
sweep.

## See also

- `sks-triage` — the field-assignment pass the sweep hands off to.
- `sks-issue` — issue body shape for filed summaries.
- `sks-github-notif-sweep` — the notification-driven counterpart.
- `sks-github-actions-audit` — the CI-failure sweep that files per repo+workflow.
