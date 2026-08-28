# GitHub Actions merge-queue triggers (shikanime repos)

Reference for authoring `.github/workflows/*.yaml` in shikanime repos. Loaded on
demand from `sks-dev-workflow`; not part of the dev loop.

GitHub Actions workflows that interact with merge queue or branch protection need
`pull_request_target` triggers alongside or instead of `pull_request`.

## merge_group / pull_request_target gotcha

GitHub's native merge queue emits the `merge_group` event, but workflows that
need to inspect PR state (check runs, labels, reviews) in the merge queue context
MUST use `pull_request_target` instead of (or alongside) `pull_request`.

Why: `pull_request_target` runs in the context of the base branch, which is the
only context where the merge queue's accumulated check state is visible. With
`pull_request` triggers, the workflow runs in the PR's head context and cannot see
checks from other PRs in the queue.

```yaml
# Correct: pull_request_target for check access in merge queue
"on":
  pull_request_target:
    types: [check_suite, check_run]
    branches: [main]
  merge_group:
    types: [checks_requested]
```

`pull_request` triggers work fine for plain PR events (opened, synchronize,
ready_for_review) where you don't need the merge-queue context. The two trigger
types are complementary — `pull_request_target` for queue-aware workflows,
`pull_request` for PR lifecycle workflows.

## Pitfall: unnecessary pull_request_target triggers

When adding `merge_group` support, the temptation is to also add
`pull_request_target` to the workflow so it can access check state in the merge
queue. **Do not do this unless the workflow actually needs to inspect PR state**
(e.g., read labels, reviews, or commit messages). A workflow that only *runs*
checks (via `workflow_call`) and reports status does not need `pull_request_target`.
The integration workflow (devenv modules) is a common pattern — it delegates
entirely to `nix.yaml`'s reusable workflow and never reads PR state.

## YAML generation pattern for workflow triggers

Nix-generated workflow YAML maps directly to GitHub's `on:` block structure. Each
top-level event key (`pull_request`, `merge_group`, `push`) is a sibling at the
same level as `jobs:` — not a child. In Nix:

```nix
{
  github.settings.workflows.myWorkflow = {
    # CORRECT — merge_group at the top level, alongside pull_request
    on.pull_request = { ... };
    on.merge_group.types = [ "checks_requested" ];
    # WRONG — nested object creates wrong YAML structure
    # on.merge_group = { types = [ "checks_requested" ]; };
  };
}
```

This trips up every session that generates merge queue workflows — the Nix
attrset structure must mirror the YAML indentation exactly.
