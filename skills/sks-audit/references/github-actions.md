
# CI Failure Audit

Sweep an org's GitHub repositories for failed workflow runs in the trailing
window, file the uncovered failures as issues, and fastlane trivial CI fixes.
Ignorable classes stay ignored; nothing is retried or re-triggered from the
audit without a repo-specific rule that says so.

Org-specific scope (org names, per-repo CI quirks, re-arm paths) live in
`references/github-actions-shikanime.md`; read it when operating in a
shikanime org.

## When to Use

- "Check CI failures across the org" / "what failed in the last 24 hours".
- A recurring CI sweep: enumerate repos, dedup against open issues, file new
  failures.
- One failed run reported by a human — same dedup and filing rules.

## Procedure

1. **Enumerate repos and failed runs.** `gh repo list <org> --limit 100 --json
   nameWithOwner` per org, then per repo
   `gh run list -R <repo> --status failure --created ">$(date -d '-24 hours'
   '+%Y-%m-%d')"`. Completion check: every repo scanned, every failure in the
   window recorded.

2. **Drop the ignorable classes.** Renovate PR checks (covered by the renovate
   sweep), draft-PR CI skips, and flakes that passed on rerun. Record what was
   dropped and why; an unexplained drop is a finding, not a shortcut.

3. **Dedup against the filing repo.** `gh issue list -R <repo> --state open`;
   one issue per repo+workflow pair, tracked failures are listed, never
   re-filed.

4. **File each new failure.** One issue per repo+workflow in the repo where it
   failed: run URL, failing job, first error lines
   (`gh run view <run> --log-failed`), head sha. Assign per repo policy where
   eligible.

5. **Fastlane trivial fixes.** Eligible scope: CI yaml fix, action pin, typo.
   Must pass the `sks-fastlane` gate in full. Ineligible or checks pending:
   leave the PR open; never wait.

6. **Apply repo-specific quirks only when referenced.** Re-arm rules or
   known-broken paths are repo facts, not audit defaults; read them from the
   org reference. Never re-run a workflow from the audit without a declared
   quirk rule.

## Pitfalls

- `gh run list --created` filters on run creation, not conclusion time — a
  long-running failure that started 25h ago vanishes from the window; sweep on
  the union of creation-time and `updatedAt` when precision matters.
- `--log-failed` returns empty while sibling jobs in the same run are still in
  progress; fall back to `gh api repos/<repo>/actions/jobs/<id>/logs`.
- Repo enumeration with `--limit 100` silently truncates bigger orgs; page
  with `--paginate` or reconcile against a known repo count.
- A workflow failing on schedule with zero code changes is an infra finding
  (runner quota, token expiry), not a code bug — file it as such.

## Verification

```bash
gh run list -R <repo> --status failure --created ">$(date -d '-24 hours' '+%Y-%m-%d')"
gh issue list -R <repo> --state open --search "CI:"
```

Report states: repos scanned, failures found, drops with reasons, issues filed
(links), PRs left open.

## See also

- `sks-issue` — issue body shape for filed failures.
- `sks-fastlane` — the full eligibility gate referenced by step 5.
- `sks-renovate-sweep` — owns renovate PR checks; this skill ignores them.
- `sks-triage` — repo-wide issue/PR triage beyond CI failures.
