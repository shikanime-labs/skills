# Skills

A curated catalog of self-improved agent skills for Hermes and compatible
agents. Each skill lives in its own directory with a `SKILL.md`.

**Language:** Markdown (SKILL.md)

## Structure

- `skills/shikanime-studio/` — the shikanime `sks-*` workflow family
- `skills/cloud-pi-native/` — the cloud-pi-native `cpn-*` workflow family
- `README.md` — Installation and usage documentation

## Workflow

Two orgs, one doctrine — the lifecycle is **discussion → issue → issue comments
→ PR** for both families. The issue body is the problem statement with
acceptance criteria as a command-decidable tasklist (the gate ledger); the PR
proves it. shikanime skills are written in English with plain-English commits +
Automata co-author trailer; cloud-pi-native skills operate in French with
conventional commits. Skills: `sks-dev-workflow`, `sks-async`, `sks-commit`,
`sks-discussion`, `sks-issue`, `sks-pr`, `cpn-dev-workflow`, `cpn-commit`,
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
Related: skills/shikanime, skills/cloud-pi-native
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
   [skill authoring](https://hermes-agent.nousresearch.com/docs) format and the
   authoring practices below
3. Add the skill to the catalog table in `README.md` and both manifests
   (`skills.json`, `package.json` `agents.skills`)
4. Commit with a descriptive message

## Skill Authoring Practices

Source: agentskills.io best practices (`skill-creation/best-practices`,
`optimizing-descriptions`, `evaluating-skills`) and the `skill-creator` skill.

- **Ground in real execution.** Extract the skill from a hands-on task, not a
  template: the steps that worked, the corrections made, the input/output
  formats, the context the agent lacked. Synthesize from project artifacts
  (runbooks, review comments, patches) — never from generic references.
- **Spend context wisely.** Add what the agent lacks (project conventions,
  non-obvious edge cases, exact APIs); omit what it already knows. Aim for
  moderate detail — concise stepwise guidance beats exhaustive coverage.
- **Defaults, not menus.** Pick one default tool/approach per decision; mention
  alternatives only as an escape hatch.
- **Procedures over declarations.** Teach how to approach a class of problems,
  not the answer to one instance. Output-format templates, constraints, and tool
  specifics are still fine.
- **Progressive disclosure.** Keep `SKILL.md` under 500 lines / ~5,000 tokens.
  Push detailed reference into `references/` with an explicit load condition
  ("read `references/api-errors.md` when the API returns a non-200"), never a
  generic "see references/".
- **Calibrate control.** Prescribe exact sequences for fragile or
  consistency-critical operations; explain _why_ and leave freedom where
  multiple approaches are valid.
- **Gotchas > general advice.** A `## Gotchas` section of concrete corrections
  that defy assumptions is the highest-value content. When an agent makes a
  mistake you correct, add the correction there.
- **Templates + checklists.** Give output templates for fixed formats; use
  checklists for multi-step workflows; add validation loops (do → check → fix →
  repeat) and plan-validate-execute for batch or destructive operations.
- **Descriptions drive triggering.** Imperative, intent-focused, "pushy": list
  contexts where the skill applies, even when the user doesn't name the domain.
  Keep the `Use when` / `À utiliser quand` trigger and the 200-char cap (the
  spec allows 1024).
- **Evaluate, then iterate.** Ship `evals/evals.json` with 2-3 realistic prompts
  (varied phrasing, one edge case) and objective assertions graded with evidence
  — not "output is good", not exact-phrase brittleness. Run with-skill vs
  baseline, review with a human, fix, rerun. Stop when feedback is empty or
  improvement plateaus. `skill-creator` automates the loop (run → grade →
  benchmark → eval-viewer).

## Skill Categories

- `shikanime` — the shikanime org workflow family (`sks-*`)
- `cloud-pi-native` — the cloud-pi-native org workflow family (`cpn-*`): console
  dev loop, GitHub lifecycle, and commit conventions

_Each skill must include a valid `SKILL.md` with YAML frontmatter. Test against
the target agent before submitting_
