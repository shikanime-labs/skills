# Cloud-pi-native PR workflow specifics

Load when running the issue → PR → triage flow in a cloud-pi-native org repo —
overrides the shikanime defaults while the orchestration in SKILL.md still
applies.

- Repos: `cloud-pi-native/*`; default target `cloud-pi-native/console`.
- Artifact language: **French**; PR titles conventional (`feat:`/`fix:`/…),
  bodies per the repo's `PULL_REQUEST_TEMPLATE.md`.
- Gate includes SonarQube Quality Gate (0 new issues) via `gh pr checks <N>`;
  Husky `pre-push` runs `vitest` before push.
- PR opened from `origin` with `--head cloud-pi-native:<branch>`; merge queue
  trigger when `BLOCKED`: `gh workflow run 243523481 --repo
  cloud-pi-native/console -f PR_NUMBER=<N>`.
