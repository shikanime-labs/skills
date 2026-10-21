---
name: sks-grafana-audit
description:
  "Use when auditing fleet alerting health: firing alertmanager alerts, filing
  new alerts as issues, and fastlaning small monitoring-config fixes."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - monitoring
      - alertmanager
      - triage
      - audit
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-k8s-audit
      - sks-flux-audit
      - sks-context
platforms:
  - linux
  - macos
  - windows
---

# Alert Audit

Audit the firing alerts of a monitoring stack, file the uncovered ones as
issues, and fastlane small monitoring-config fixes. The alert source is the
alertmanager HTTP API; dedup and filing happen in the target repo. Never close
or silence anything from an audit run.

Org-specific targets (cluster names, alertmanager URL, filing repo) live in
`references/shikanime.md`; read it when operating in a shikanime org.

## When to Use

- "Triage the firing alerts" / "what is alerting right now" for a fleet.
- A recurring monitoring sweep: read alerts, dedup against open issues, file
  new ones.
- Filing or fixing one alert found by an external report — same dedup and
  gate rules.

## Procedure

1. **Read the alert source.** `curl -s <alertmanager>/api/v2/alerts` and parse
   with python3. Record per alert: alertname, labels, annotations, startsAt.
   Completion check: every active alert has a recorded line.

2. **Dedup against the filing repo.** `gh issue list -R <repo> --state open`;
   skip alerts already covered by an open issue (match alertname and affected
   object). Covered alerts are listed in the run report, never re-filed.

3. **File each new alert.** One issue per alert: title
   `<alertname>: <summary>`, body with labels, annotations, affected object,
   startsAt. Assign per repo policy where eligible.

4. **Fastlane small fixes.** A fix is fastlane-eligible only as a small
   monitoring-config patch (values bump, threshold, image pin) and must pass
   the `sks-fastlane` gate in full. Ineligible or checks pending: leave the
   PR open; never wait.

5. **Note resolutions.** Alerts resolved since the last sweep are listed; the
   audit closes nothing automatically — resolution is an operator decision.

## Pitfalls

- The alertmanager API returns active AND recently-resolved alerts; filter on
  `status.state == "active"` before filing or you file ghosts.
- A flapping alert re-files every sweep if dedup matches only exact titles —
  match alertname plus affected object, and let honcho/memory hold known
  flappers between runs when the harness has it.
- Grafana's HTTP API is a different surface than alertmanager's; if the
  platform's Grafana is OIDC-only with no API-key path, read the vm*/alertmanager
  APIs instead — never scrape dashboards.
- Never ack, silence, or resolve from the audit. The read-only posture is what
  keeps a bad dedup from hiding a real incident.

## Verification

```bash
curl -s <alertmanager>/api/v2/alerts | python3 -c \
  "import json,sys; print(len(json.load(sys.stdin)))"
gh issue list -R <repo> --state open --search "<alertname>"
```

Report states: alerts read, issues filed (links), PRs left open, alerts
resolved since last sweep.

## See also

- `sks-issue` — issue body shape for filed alerts.
- `sks-fastlane` — the full eligibility gate referenced by step 4.
- `sks-flux-audit` — the companion GitOps-health audit.
- `sks-k8s-audit` — the companion warning-events audit.
