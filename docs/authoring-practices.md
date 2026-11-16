# Skill authoring practices

The agentskills.io best-practices distillation for catalog skills.
Read this before authoring or materially editing any SKILL.md.

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
  When a skill needs delegation, spawning, or multi-agent coordination, point
  at the `hermes-agent` skill (its spawning-additional-hermes-instances
  section) instead of restating `delegate_task` call shapes or spawn commands.
  See
  <https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent#spawning-additional-hermes-instances>.
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
- **Pitfalls > general advice.** A `## Pitfalls` section of concrete
  corrections that defy assumptions is the highest-value content. When an
  agent makes a mistake you correct, add the correction there. The heading is
  always `## Pitfalls`; `## Gotchas` is never used.
- **Templates + checklists.** Give output templates for fixed formats; use
  checklists for multi-step workflows; add validation loops
  (do → check → fix →
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
