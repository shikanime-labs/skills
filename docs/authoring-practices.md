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

## Tier costs and loading levels

Content loads in three levels with distinct token costs. Design around them,
not around topics:

| Level | Content | When loaded | Cost |
|---|---|---|---|
| 1 | name and description | Always, at startup | ~chars/4 + 25 tokens |
| 2 | SKILL.md body | When the skill triggers | Keep under ~5k tokens |
| 3 | references/, scripts/ | On demand while executing | What is read |

A skill's bundled context is effectively unbounded — the agent reads files on
demand — so level-3 size is not a constraint; level-1 and level-2 discipline
is.

## Single file versus references/

Default to a single SKILL.md. Split into `references/` only when BOTH hold:

1. **Conditional loading** — a meaningful chunk serves only a subset of
   invocations (e.g. a forms guide most PDF tasks never touch). If every
   invocation reads everything, splitting adds Read round-trips and saves
   nothing.
2. **Size pressure** — the body exceeds budget (recommended 25k chars, hard
   ceiling 50k; measure with `wc -c`, chars track tokens at ~4/char — line
   counts are not a metric).

**Distribution is a veto.** A skill that must travel as one file (CLI-embedded,
printed by a subcommand, shared by paste) stays single-file regardless of size
— condense instead. Condensing cuts redundancy while preserving every
load-bearing instruction; losing substance to hit a line count is the failure
mode, not the fix.

## Reference hygiene

- References one level deep from SKILL.md — depth is the reference CHAIN
  (a.md → b.md → c.md), not directory nesting. Partial reads miss content in
  deep chains.
- Over ~100 lines, a reference gets a table of contents at the top.
- Split large references by subtopic so each task pulls only what it needs; a
  single many-hundred-line reference defeats progressive disclosure.
- Code can be executable tool or reference documentation — state explicitly
  whether a script is run or read.

## Testing descriptions

The description is the routing surface; the body cannot help if the trigger
fails. Test with:

- 8-10 realistic should-trigger prompts (casual phrasing, typos, file paths).
- 8-10 near misses that should NOT trigger, including adjacent skills the
  description might steal from.
- Skills under-trigger more often than they over-trigger — be assertive in
  the description for true positives.

## Workflow shapes

Name the shape explicitly in the body rather than assuming the agent infers
it: sequential (numbered steps with exact commands), decision tree (route on
task type up front), feedback loop (validate → fix → re-validate, exits only
on pass), checklist (long tasks copy and tick items).

## Degrees of freedom

Match instruction rigidity to task fragility: text guidelines when several
good approaches exist; pseudocode/templates when a stable pattern holds;
exact scripts and schemas when correctness depends on exact values. Hard
MUST constraints only near real cliffs — security, irreversible writes,
schema field names, data loss.

## Anti-patterns

- Description as narrative ("this skill helps with X") instead of a routing
  rule ("use when the user asks for X").
- All content inline — reference material stuffed into SKILL.md taxes every
  invocation.
- Blurred categories — disparate domains combined in one skill.
- Anticipatory authoring — writing skills for hypothetical needs instead of
  extracting from successful runs.
- Rigidity where judgment works — locking the agent into strict rules where
  context should decide.
- README.md inside a skill folder — confuses loaders; SKILL.md is the only
  entry point.
