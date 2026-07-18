# Skills

A single, strict development workflow skill for
[Hermes](https://hermes-agent.nousresearch.com/docs) and compatible agents.

This repo ships **one** skill — `dev-workflow` — that encodes the entire
pipeline (spec-as-issue → tickets → triage → implement → review) with the
always-on Ponytail laziness ladder. See `README.md` and
`skills/dev-workflow/SKILL.md`.

## Structure

- `skills/dev-workflow/` — the one skill (`SKILL.md`)
- `docs/agents/` — durable substrate (`issue-tracker.md`, `domain.md`,
  `workflow.md`)
- `README.md` — install + overview

## Repo governance

### Commit style

- Plain-text capitalized title, no conventional-commit prefix
- Body with labels: `Design:`, `Related:`, `Closes #`
- Keep Markdown lines wrapped at 80 columns and run `nix fmt` before shipping

### Stack

- 1 commit == 1 PR via ghstack
- Amend + `ghstack` to resubmit
- `ghstack land` on head PR to land the entire stack
- Never `gh pr merge` (creates poisoned commits)
- Never force-push ghstack branches
- ghstack only works on HEAD commit chains, not detached HEADs

### Protect `main`

- Require 1 approving review
- Require linear history (no merge commits)
- Require signed commits
- Squash+rebase merge only

## Working in this repo

Changes to the workflow itself are made through the `dev-workflow` skill's own
pipeline: draft an issue, decompose, implement, review. The `docs/agents/`
substrate is the source of truth for vocabulary and decisions.
