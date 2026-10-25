---
name: sks-cichecks
description: "Use when a PR's CI is red: trace root cause, verify landing."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - ci
      - pull-request
      - landing
      - root-cause
      - verification
    related_skills:
      - sks-dev
      - sks-pr
      - sks-pr-review
      - sks-land
      - sks-investigate
platforms:
  - linux
  - macos
  - windows
---
# sks-cichecks

CI green-gate verification and root-cause tracing for PR landing.

Class-level procedures:
- Verify PR landability with real command output, never the summary line.
- Trace a red gate to root cause; distinguish code-caused from infra/pre-existing failures.
- Do not change PR code for a pre-existing infra failure.

## Ordering
1. Verify push right + identity:
   - `gh api repos/<org>/<repo> --jq .permissions.push` (needs `true`).
   - `gh api user --jq .login`.
2. Detect branch protection via RULESETS (the classic `branches/main/protection` endpoint returns 404 on ruleset-backed repos):
   - `gh api repos/<org>/<repo>/rulesets` → id + name.
   - `gh api repos/<org>/<repo>/rulesets/<id>` → `.rules[]`.
   - Look for: `pull_request.required_approving_review_count`, `required_status_checks`, `required_signatures`, `required_linear_history`, `allowed_merge_methods`, `merge_queue`.
3. On red CI: `gh api repos/<org>/<repo>/actions/runs/<run>/jobs` → conclusion per job. `failure` (not `skipped`) is the blocker.
4. Fetch the failing job's log: `gh api repos/<org>/<repo>/actions/jobs/<id>/logs` (pass `--allow-escape-sequences` for ANSI noise) or `gh run view <run> --job <id> --log`. Read the first failing step.
5. Trace dependencies: if a `needs` job is red and the failing job is downstream of it, the root cause is the dependency that actually failed — not the downstream job.
6. Classify: a pure-refactor/perf PR whose build/lint/tests/Sonar/CodeQL are all green, but which has an infra error (non-200, 403, "not a git repository", action-syntax, authorization) → pre-existing infra failure. Do not change the PR's code.
7. Verify landing, not the push:
   - `gh pr view <n> --json state,url,headRefOid` after merge.
   - `gh pr view <n> --json files` to report size.
   - `gh pr checks <n>` per-job.
   - The push command's success lines prove nothing.

## Standing gates
- Branch protection (ruleset-based) → PR mandatory.
- `pull_request.required_approving_review_count: 1` → one approving review from a non-author collaborator; self-approval blocked.
- `required_signatures` → commit `verification.verified: true`.
- `allowed_merge_methods: ["rebase"]` → `gh pr merge --rebase` (squash rejected). Direct push to main never.
- Required status checks (e.g. "Check jobs status") must be green before merge.

## Pitfalls
- "Check jobs status" red is often a *symptom*: its `needs` (e.g. `build`) failed, and `build` failed because a preview deploy returned 403. Trace to the real failing job, not the downstream one.
- GitHub rejects self-approval of your own PR; a reviewer must be a non-author collaborator.
