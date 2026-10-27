# CI Failures

- Orgs: `shikanime-labs` and `shikanime-studio`.
- Failures file in the repo where they failed; assignee `yorha-operator`
  where eligible and the fix is machine-routable; human-only fixes stay
  unassigned.
- Console quirk (`cloud-pi-native/console`): push branches touching only
  `apps/server` run no CI — re-arm with
  `gh workflow run workflow-continuous-integration.yml --ref <branch>`.
- Draft-PR CI skips are normal on machines (`nix`/`skaffold` jobs skip draft
  PRs; `gh pr ready <n>` arms them) — not failures.
- Renovate PR checks belong to `sks-maintenance` (`references/renovate.md`);
  drop them here.
- Fastlane merge mechanics and receipt comment are `sks-fastlane`'s.
