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

Design: docs/agents/workflow.md, docs/agents/issue-tracker.md
Related: skills/workflow/{to-spec,to-tickets,implement,ask}
Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>
```
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
