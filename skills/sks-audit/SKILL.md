---
name: sks-audit
description:
  "Use when auditing fleet or org health — Flux, CI runs, alerting, cluster
  events, security alerts: read state, dedup against issues, file findings,
  fastlane small fixes."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - audit
      - sweep
      - health
    related_skills:
      - sks-issue
      - sks-fastlane
      - sks-redteam
platforms:
  - linux
  - macos
  - windows
---

# Audit

Single entry point for recurring health sweeps over a fleet or org: read
live state, dedup against open issues, file each new finding, fastlane small
fixes. One domain per reference — read the one that matches the audit
surface:

| Audit surface                | Read                          |
| ---------------------------- | ----------------------------- |
| Flux / GitOps reconciliation | `references/flux.md`          |
| GitHub Actions failed runs   | `references/github-actions.md`|
| Alertmanager firing alerts   | `references/grafana.md`       |
| Kubernetes warning events    | `references/k8s.md`           |
| GitHub security alerts       | `references/security.md`      |

## Shared sweep procedure (every domain)

1. **Read state** with the domain's enumeration command (reference step 1);
   record every finding with its evidence.
2. **Dedup** against open issues in the filing repo
   (`gh issue list -R <repo> --state open`); tracked findings are listed,
   never re-filed.
3. **File each new finding** per `sks-issue` — one issue per object/alert,
   body with evidence and first-seen.
4. **Fastlane small fixes** per `sks-fastlane` — full gate; ineligible or
   checks pending: leave the PR open, never wait.
5. **Report** — findings read, issues filed (links), PRs left open,
   resolutions since the last sweep.

Hard rules: the audit never closes, dismisses, or auto-fixes beyond the
fastlane gate; resolutions since the last sweep are listed only.
Org-specific targets (clusters, orgs, filing repos) live in the per-domain
`*-shikanime.md` references.

## When to Use

- "Check Flux health" / "what is failing to reconcile".
- "Check CI failures across the org" / "what failed in the last 24 hours".
- "Triage the firing alerts" / "what is alerting right now".
- "Triage the cluster's warning events" / "what is unhealthy in the fleet".
- "Audit the org's security alerts".
- One failure reported by a human — same dedup and filing rules.

## Verification

```bash
gh issue list -R <repo> --state open   # filed findings deduped, none re-filed
```

Report states: findings enumerated, open count, issues filed (links), PRs
left open, resolutions since the last sweep.

## See also

- `sks-issue` — issue body shape for filed findings.
- `sks-fastlane` — the full eligibility gate referenced by the sweep.
- `sks-redteam` — offensive perimeter probes (security counterpart).
- `sks-bulk` — N-repo mutation batches beyond filing.
