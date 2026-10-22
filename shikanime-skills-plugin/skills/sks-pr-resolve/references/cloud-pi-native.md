# Cloud-pi-native PR resolution specifics

Load when reconciling review threads on a cloud-pi-native org PR — these
override the shikanime org defaults while the generic gates in SKILL.md still
apply.

- Repos: `cloud-pi-native/*`; the strictest repo (`console`) blocks
  self-approval via branch protection → a verbal `lgtm` suffices (merge
  itself stays in the dev-workflow / `gh pr merge`).
- Heavyweight e2e at land time (high-impact PRs): schema, auth/Keycloak,
  syncs, critical product paths — run the manual merge queue as a pre-check
  (SKILL.md, "Pre-check" section); console workflow id `243523481`:
  `gh workflow run 243523481 --repo cloud-pi-native/console -f PR_NUMBER=<N>`.
- Artifact language: **French**.
