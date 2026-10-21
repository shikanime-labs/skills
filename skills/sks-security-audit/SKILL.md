---
name: sks-security-audit
description:
  "Use when auditing an org's GitHub security surface: code-scanning,
  secret-scanning, and dependabot alerts, filing new alerts as issues,
  fastlaning small remediations."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - security
      - github
      - dependabot
      - triage
      - audit
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-redteam
      - sks-github-actions-audit
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Security Audit

Audit an org's GitHub security alerts: code scanning, secret scanning, and
dependabot across every repo, file the uncovered ones as issues, and fastlane
small remediations. The audit never closes or dismisses alerts — resolution is
an operator decision.

Org-specific scope (org names, assignee policy) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Audit the org's security alerts" / "any open code-scanning or dependabot
  alerts".
- A recurring security sweep: enumerate, dedup, file, rank.
- One alert reported by a human — same dedup and filing rules.

## Procedure

1. **Enumerate alerts per org.** `gh api /orgs/<org>/code-scanning/alerts
   --paginate` (same for `/secret-scanning/alerts` and `/dependabot/alerts`),
   repeated for each org in scope. Keep `state=="open"`. Record: alert type,
   repo, severity, CVE or rule id, html_url, created_at. Completion check:
   every org × alert-type pair enumerated.

2. **Rank before filing.** Critical and high first; secret-scanning alerts are
   always urgent regardless of severity. Dependabot alerts rank by manifest
   reachability when the repo gives evidence, otherwise by severity.

3. **Dedup against the affected repo.** `gh issue list -R <repo> --state
   open`; tracked alerts are listed, never re-filed.

4. **File each new alert.** One issue in the affected repo: title
   `<type>: <CVE or rule>`, body with severity, affected path, first-seen,
   alert link. Assign per repo policy where eligible.

5. **Fastlane small remediations.** Eligible scope: dependency bump, config
   hardening flag. Must pass the `sks-fastlane` gate in full. Ineligible or
   checks pending: leave the PR open; never wait.

6. **Note resolutions.** Alerts resolved since the last sweep are listed;
   never close or dismiss alerts from the audit.

## Pitfalls

- Org-level alert endpoints require org ownership scopes on the token; a
  404/403 on one alert class means permission, not zero alerts — verify
  before reporting clean.
- Dependabot's org endpoint is the flakiest of the three; a truncated page
  looks like a clean repo — reconcile repo counts when the run matters.
- Never file a secret-scanning alert's secret VALUE anywhere: the issue carries
  the alert link and location, never the credential.
- A dismiss-without-fix pattern (alert closed, code unchanged) is itself a
  finding — report it, never replicate it.

## Verification

```bash
gh api /orgs/<org>/code-scanning/alerts --paginate \
  --jq '[.[] | select(.state=="open")] | length'
gh api /orgs/<org>/secret-scanning/alerts --paginate \
  --jq '[.[] | select(.state=="open")] | length'
gh api /orgs/<org>/dependabot/alerts --paginate \
  --jq '[.[] | select(.state=="open")] | length'
gh issue list -R <repo> --state open --search "<CVE>"
```

Report states: alerts enumerated per class, open count per org, issues filed
(links), PRs left open, resolutions since last sweep.

## See also

- `sks-issue` — issue body shape for filed alerts.
- `sks-fastlane` — the full eligibility gate referenced by step 5.
- `sks-redteam` — the offensive counterpart; probes the perimeter, files
  there.
- `sks-github-actions-audit` — CI health, including secret-exposure signals in runs.
