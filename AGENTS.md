# Skills

A curated catalog of self-improved agent skills for Hermes and compatible
agents. Each skill lives in its own directory with a `SKILL.md`.

**Language:** Markdown (SKILL.md)

## Structure

- `skills/workflow/` — The strict development workflow skills, each a directory
  with a `SKILL.md`
- `docs/agents/` — Durable substrate (`issue-tracker.md`, `domain.md`,
  `workflow.md`) the workflow reads
- `README.md` — Installation and usage documentation

## Workflow

One narrative, not a toolbox. The pipeline validates every feature as a GitHub
issue before code; the minimalism discipline is the always-on minimalism guard
woven through every coding step (defined in `docs/agents/workflow.md`, not a
separate skill); features ship behind feature-driven tests and property-based
stability tests. Full flow in `docs/agents/workflow.md`. Skills: `bootstrap`,
`to-spec`, `to-tickets`, `triage`, `implement`, `code-review`, `ask`.

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix
- Body with labels: `Design:`, `Related:`, `Closes #`
- Keep Markdown lines wrapped at 80 columns and run `nix fmt` before shipping

## Stack (atomic delivery)

- One ticket → one branch → one PR; PRs stack on the previous ticket's branch.
- Each PR is atomic: one objective, linked issue (`Closes #N`), small enough for
  a human to review in one sitting.
- 1 commit == 1 PR via ghstack, or manual per-ticket branches with
  `gh pr create`.
- Agent runs `code-review` as pre-flight; **a human approving review is the
  gate** before landing (protect `main`).
- Amend + `ghstack` to resubmit; `ghstack land` on the head PR to land the
  stack.
- Never `gh pr merge` (poisoned commits). Never force-push stacked branches.
- ghstack needs a HEAD commit chain, not a detached HEAD.
- Prefer `jj`; ghstack is git-only, so under jj replicate the stack manually
  (one bookmark per ticket + `gh pr create`).

## Protect `main`

- Require 1 approving review
- Require linear history (no merge commits)
- Require signed commits
- Squash+rebase merge only

## Adding a New Skill

1. Create a directory under the appropriate category
2. Write a `SKILL.md` following the
   [skill authoring](https://hermes-agent.nousresearch.com/docs) format
3. Add the skill to the catalog table in `README.md`
4. Commit with a descriptive message

## Skill Categories

- `autonomous-ai` — Agent orchestration and delegation
- `devops` — Infrastructure, Nix, Kubernetes, CI/CD
- `github` — GitHub workflows, issues, PRs
- `productivity` — Communication, documents, automation
- `reconnaissance` — Domain intelligence, OSINT
- `software-dev` — Development workflows, debugging, testing

_Each skill must include a valid `SKILL.md` with YAML frontmatter. Test against
the target agent before submitting_
