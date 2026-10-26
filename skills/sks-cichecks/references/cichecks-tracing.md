# Tracing a red CI gate to root cause

1. `gh api repos/<org>/<repo>/actions/runs/<run>/jobs` → conclusion per job.
2. Non-success, non-skipped conclusions are blockers. Their `needs` chain shows the tree.
3. Fetch the failing job's log: `gh api .../actions/jobs/<id>/logs --allow-escape-sequences` or `gh run view <run> --job <id> --log`. Read the first failing step.
4. A downstream red (e.g. "Check jobs status") proves nothing about itself — examine its `needs` (e.g. `build`).
5. Classify by the diff + the failing job's nature:
   - Refactor/perf diff + green build/lint/tests/Sonar/CodeQL + infra error → pre-existing infra; do not edit the PR's code.
   - Diff shows the failing path + other checks green → code fix likely needed.
6. Example: pure performance work with green build/lint/tests/Sonar/CodeQL and a preview-deploy HTTP 403 → pre-existing infra failure.
