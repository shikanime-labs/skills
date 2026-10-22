---
name: sks-sdlc-efficiency
description:
  "Use when measuring a GitHub org's SDLC delivery process with facts and
  metrics: counts of open and untriaged issues and PRs, review and merge
  latency, and gap conclusions filed as proposals."
version: 0.1.0
author: Automata
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, process, metrics, audit]
    related_skills:
      - sks-triage
      - sks-issue
      - sks-issue-triage
      - sks-pr-review
      - sks-land
      - sks-github-issues-sweep
---

# SDLC Efficiency Audit

Measure an org's delivery pipeline with counts and latencies, then file the
gaps as proposal issues. The audit reads; it never mutates the items it
measures. Org scope, tracker, and bot identities live in
`references/shikanime.md` — load it before running against a target org.

## When to Use

- "Measure how our issues and PRs process is doing" — a monthly or ad-hoc
  delivery-SDLC efficiency audit over an org.
- "Where is the process broken" — turn pipeline facts into ranked gap
  proposals.

Not for: assigning missing metadata (`sks-triage`), rewording or closing
items (`sks-pr-triage`, `sks-issue-triage`), or landing stalled PRs
(`sks-land`).

## Procedure

### 1. Scope the orgs

Enumerate repos per target org, dropping archived and empty repos; record
the repo count. A census over archived repos inflates every downstream
number.

### 2. Measure — numbers only

Collect all facts in one pass and write the metrics table before drawing
any conclusion. Re-measure in this session: numbers from a previous run
are the baseline, never the current value.

- Census: open issues and open PRs per repo.
- Untriaged: open items missing derivable metadata, computed against what
  each repo supports — run `sks-triage`'s `scripts/scan-untriaged.sh` per
  repo instead of re-deriving the gap classes.
- Age: median and p90 age in days of open issues and open PRs.
- Latency: over merged PRs in the window (default 30), time to first
  review and time to merge. Keep bot-authored PRs (renovate, dependabot,
  org bot identities) in a separate row — merged with human rows they
  bury the signal.
- Residue: issues still open whose linked PR already merged. Read each
  merged PR's Development links or timeline for the issue number; a
  repo-wide text search misses cross-repo links.
- Stalls: open PRs with `reviewDecision` CHANGES_REQUESTED or
  REVIEW_REQUIRED older than 7 days, and PRs with `mergeStateStatus`
  BLOCKED or BEHIND older than 7 days.
- Stale branches: branch heads fully merged or behind the default branch,
  older than 7 days, excluding protected and stack-role branches.

### 3. Identify gaps — deltas against baseline

Read the previous run's table (its issue ledger or report). A gap is a
metric worse than its recorded baseline or above an absolute threshold:
untriaged above 0, residue above 0, median human review latency above 7
days, stale branches above 0. Sample the last 10 merged PRs against the
repo's PR template when conformance is a standing question. A gap already
tracked by an open issue is listed, never re-filed.

### 4. File proposals — issues only

One proposal issue per actionable gap, at most 3 per run, in the org's
designated tracker (`references/shikanime.md`). Follow `sks-issue`:
create, then triage. The `- [ ]` acceptance ledger states each threshold
as a command-decidable check with the measured baseline as the starting
value. The audit opens no PRs, closes nothing, and edits nothing it
measured — fixing what an audit found is separate triage or dev work.

### 5. Report the delta

Table: metric, previous, current, verdict per row; findings marked new or
tracked. A clean audit is a valid outcome: the table with flat numbers
and zero new issues.

## Pitfalls

- A search-API query cannot compute the residue class: linked issues live
  in Development metadata and timelines, so the check is per-PR reads,
  never a repo-wide text search.
- Org-level rulesets return 403 on free-plan orgs; probe landing-gate
  stalls per repo (`mergeStateStatus`), not through org ruleset
  endpoints.
- Bot PRs are not human latency: an unsplit median can read healthy while
  human review rots, or the reverse.
- Mutating during the audit contaminates the next baseline: label fixes
  belong to `sks-triage`, rewording to `sks-pr-triage`.
- p90 over a small population is one outlier; report the median beside it
  or the number lies.

## Verification

```bash
gh api "search/issues?q=org:<org>+state:open+type:issue" --jq .total_count
```

Every number in the reported table is re-derivable by the command recorded
beside it in the working notes. Done when: the metrics table is complete,
each gap is either tracked by issue number or filed as a proposal issue
with its baseline threshold in the ledger, and no item under audit was
mutated.

## See also

- `sks-triage` — assign the missing metadata an audit surfaces.
- `sks-issue` / `sks-issue-triage` — proposal filing and triage.
- `sks-land` — unstick PRs the stall metrics flag.
- `sks-github-issues-sweep` — stale-issue sweep over content, not process.
