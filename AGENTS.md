# Skills

A curated catalog of self-improved agent skills for Hermes and compatible
agents. Each skill lives in its own directory with a `SKILL.md`.

**Language:** Markdown (SKILL.md)

## Structure

- `skills/shikanime/` — the shikanime `sk-*` workflow family
- `skills/devops/`, `skills/github/`, `skills/vcs/` — the cloud-pi-native
  `cpn-*` workflow family
- `README.md` — Installation and usage documentation

## Workflow

Two orgs, one doctrine — the lifecycle is **discussion → issue → issue comments
→ PR** for both families. The issue body is the problem statement with
acceptance criteria as a command-decidable tasklist (the gate ledger); the PR
proves it. shikanime skills are written in English with plain-English commits +
Automata co-author trailer; cloud-pi-native skills operate in French with
conventional commits. Skills: `sk-dev-workflow`, `sk-async`, `sk-commit`,
`sk-discussion`, `sk-issue`, `sk-pr`, `cpn-dev-workflow`, `cpn-commit`,
`cpn-discussion`, `cpn-issue`, `cpn-pr`.

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix.
- Body is labeled, one label per line where applicable:
  - `Design:` — files or skills the change is grounded in.
  - `Related:` — companion files, issues, or PRs.
  - `Closes #N` — the linked ticket (required for atomic delivery).
- Footers mandated by policy:
  - `Signed-off-by:` — required; commits must be signed (see Protect `main`).
  - `Change-Id:` — keep the originating change's id when amending.
- Wrap Markdown lines at 80 columns and run `nix fmt` before shipping.

Example: Wire release management, milestone metadata, trunk-based jj stacking

```text
Encode four principles into the workflow substrate and skills.

Design: README.md, AGENTS.md
Related: skills/shikanime/, skills/devops/, skills/github/, skills/vcs/
Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>
```

## Stack (atomic delivery)

- One ticket → one branch → one PR; PRs stack on the previous ticket's branch.
- Each PR is atomic: one objective, linked issue (`Closes #N`), small enough for
  a human to review in one sitting.
- Agent runs a review as pre-flight; **a human approving review is the gate**
  before landing (protect `main`).
- Never `gh pr merge` (poisoned commits). Never force-push stacked branches.

## Protect `main`

- Require 1 approving review
- Require linear history (no merge commits)
- Require signed commits
- Squash+rebase merge only

## Adding a New Skill

1. Create a directory under the appropriate category
2. Write a `SKILL.md` following the
   [skill authoring](https://hermes-agent.nousresearch.com/docs) format
3. Add the skill to the catalog table in `README.md` and both manifests
   (`skills.json`, `package.json` `agents.skills`)
4. Commit with a descriptive message

## Skill Categories

- `shikanime` — the shikanime org workflow family (`sk-*`)
- `devops` — Infrastructure, Nix, Kubernetes, CI/CD (`cpn-*`)
- `github` — GitHub workflows, issues, PRs (`cpn-*`)
- `vcs` — Commit conventions (`cpn-*`)

_Each skill must include a valid `SKILL.md` with YAML frontmatter. Test against
the target agent before submitting_
