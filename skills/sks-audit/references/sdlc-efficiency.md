# SDLC efficiency surface — details

Metrics pass over the orgs' issues and PRs. Facts first, conclusions after;
the audit mutates nothing it measures.

## Sources

- Census — `gh api
  "search/issues?q=org:<org>+is:open+type:issue&per_page=1" --jq
  .total_count` (repeat with `type:pr`); drop archived and empty repos
  before any per-repo depth.
- Untriaged — run `sks-triage`'s `scripts/scan-untriaged.sh` per repo
  instead of re-deriving the gap classes; it computes missing metadata
  against what the repo actually supports.
- Latency — merged PRs in the window (default 30): time to first review and
  time to merge; bot-authored PRs (renovate, dependabot, org bot
  identities) stay in their own row or they bury the human signal.
- Residue — issues still open whose linked PR already merged: read each
  merged PR's Development links or timeline for the issue number.
- Stalls — open PRs with `reviewDecision` CHANGES_REQUESTED or
  REVIEW_REQUIRED, or `mergeStateStatus` BLOCKED or BEHIND, older than 7
  days; read per repo, since org ruleset endpoints 403 on free-plan orgs.
- Stale branches — heads fully merged or behind the default branch, older
  than 7 days, excluding protected and stack-role branches.

## Gaps

A gap is a metric worse than its recorded baseline or above an absolute
threshold: untriaged above 0, residue above 0, median human review latency
above 7 days, stale branches above 0. Rank by leverage over effort; a
worsening metric outranks a bad absolute number that is improving. Sample
the last 10 merged PRs against the repo's PR template when conformance is a
standing question. A gap already tracked by an open issue is listed, never
re-filed — host cron records carry no continuity ledger, so the tracker's
open issues are the dedup surface.

## Report shape

Table: metric, previous, current, verdict per row; findings marked new or
tracked. A clean audit is a valid outcome — flat numbers and zero filed
issues.

## Pitfalls

- `search/issues` mixes PRs into every result: without `type:issue` or
  `type:pr` in the query, both counts are wrong.
- `closingIssuesReferences` misses issues linked through Development
  metadata without closing keywords — the residue count is a floor; say so.
- The search API rate-limits at 30 requests per minute authenticated: batch
  org-level searches before per-repo work.
- p90 over a small population is one outlier; report the median beside it
  or the number lies.
- Mutating during an audit contaminates the next baseline: label fixes
  belong to `sks-triage`, rewording to `sks-pr-triage`.
