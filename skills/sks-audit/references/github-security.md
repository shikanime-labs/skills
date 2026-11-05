# GitHub Security Alerts

- Orgs in scope: `shikanime-labs` and `shikanime-studio`.
- Alerts file in the affected repo; assignee `yorha-operator` where eligible
  and the fix is machine-routable; human-only fixes stay unassigned.
- Secret-scanning alerts are always urgent; the issue carries the alert link
  and location, never the secret value.
- Probe fallback: a secret-scanning 404 from an identity without organization
  administrator or security-manager access means unreadable. Report it per
  org as unreadable, never as zero alerts.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s.
- Findings already proven or tracked by the perimeter redteam surface of
  `sks-audit` are cross-referenced, not re-filed.
