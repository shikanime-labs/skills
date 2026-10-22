---
name: sks-security-audit
description:
  "Use when auditing an org's GitHub security surface: code-scanning,
  secret-scanning, and dependabot alerts, adversarial path exploration, and
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
      - sks-adversarial
      - sks-async
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
dependabot across every repo, explore the paths those feeds do not model,
file the uncovered ones as issues, and fastlane small remediations. The audit
never closes or dismisses alerts — resolution is an operator decision.

Org-specific scope (org names, assignee policy) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Audit the org's security alerts" / "any open code-scanning or dependabot
  alerts".
- A recurring security sweep: enumerate, dedup, file, rank.
- One alert reported by a human — same dedup and filing rules.
- Paths to explore that alert feeds do not model: an exposed internal
  endpoint a scanner never reaches, a repo reachable from a dependency with
  no advisory, a trust path between two repos.

## Procedure

1. **Enumerate alerts per org.** `gh api /orgs/<org>/code-scanning/alerts
   --paginate` (same for `/secret-scanning/alerts` and `/dependabot/alerts`),
   repeated for each org in scope. Keep `state=="open"`. Record: alert type,
   repo, severity, CVE or rule id, html_url, created_at. Completion check:
   every org × alert-type pair enumerated.

2. **Rank before filing.** Critical and high first; secret-scanning alerts are
   always urgent regardless of severity. Dependabot alerts rank by manifest
   reachability when the repo gives evidence, otherwise by severity.

3. **Explore paths the feeds do not model.** Alert surfaces cover only what
   scanners see: a published CVE, a pattern a rule matches, a manifest a bot
   parses. Paths outside that model — an internal endpoint exposed through a
   side route, a vulnerable dependency pattern with no advisory, a trust
   path from a low-value repo into a high-value one, an over-privileged CI
   token — are uncertain results, so explore them as disposable trials:
   shape each trial per `sks-adversarial`, run independent paths as parallel
   `sks-async` workspaces (one per trial, dot-qualified names
   `<repo>.<trial>`), and record the repro command with each result. A trial
   that survives is filed exactly like an alert (step 6). Read-only and
   no-secret rules hold inside the sandbox.

4. **Audit the sweep's own path.** Before filing, self-audit what this sweep
   actually covered: which org × alert-type pairs failed to enumerate, which
   repos were skipped, which feed-unmodeled paths were assumed safe without
   a trial. An audit that stops at CVE and GitHub alert absence is
   blind, not clean: those feeds do not model your paths, and silence from
   them is not evidence of safety. Close the gap: re-run the failed
   enumeration, open the trial for the assumed-safe path. Log the audited
   coverage list with the sweep report.

5. **Dedup against the affected repo.** `gh issue list -R <repo> --state
   open`; tracked alerts are listed, never re-filed.

6. **File each new alert** via `sks-issue`: free-text title, bug label, plus
   `security` only when the repo has it. Assign per repo policy where
   eligible.

7. **Fastlane small remediations.** Eligible scope: a dependency bump, or a
   config hardening flag. Must pass the `sks-fastlane` gate in full.
   Ineligible or checks pending: leave the PR open; never wait.

8. **Note resolutions.** Alerts resolved since the last sweep are listed;
   never close or dismiss alerts from the audit.

9. **Memory loop.** Before reporting, honcho_search "security audit" and
   honcho_context for recurring context (alert types that recur,
   remediations already in flight); honcho_conclude one line per durable
   lesson.

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
- `sks-fastlane` — the full eligibility gate referenced by step 7.
- `sks-adversarial` — sandbox shape for feed-unmodeled path trials (step 3).
- `sks-async` — per-trial fan-out used by step 3.
- `sks-redteam` — the offensive counterpart; probes the perimeter, files
  there.
- `sks-github-actions-audit` — CI health, including secret-exposure signals
  in runs.
