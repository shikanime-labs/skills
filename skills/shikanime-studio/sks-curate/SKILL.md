---
name: sks-curate
description:
  "Use when updating, improving, compressing, or token-optimizing a skill in
  the shikanime-labs/skills catalog: rework the body, tighten it, refresh
  evals, and keep it loadable."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - skill-maintenance
      - compression
      - token-efficiency
      - distillation
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-update
      - sks-skill-authoring
      - sks-dev-workflow
      - sks-pr-review
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Skill Curation

Refine an existing skill in the catalog: improve its guidance, compress it to
a lean token budget, and keep its evals honest. Curation is a rework pass, not
a rewrite from scratch — the skill already encodes proven procedure; your job
is to make that procedure sharper and cheaper to load.

## When to Use

- "Improve / tighten / compress <skill>."
- "Make <skill> more token-efficient."
- "Update <skill> after the workflow it describes changed."
- "Curate the catalog before shipping the next batch of skills."
- A review found the skill wordy, redundant, or drifting from the procedure.

Don't use for authoring a brand-new skill (`sks-skill-authoring`); curation
starts from an existing `SKILL.md`.

## How a skill earns its keep

A skill loads into a context budget; every token it costs should earn its
place. Four properties decide whether a body is worth its weight:

1. **Grounding** — the steps are distilled from a real execution (a task you
   actually ran, corrections you made, the input/output formats you hit), not
   generic advice. If a section could apply to any repo, it is not grounded.
2. **Gap-filling** — it adds exactly what the agent lacks: project
   conventions, non-obvious edge cases, exact commands. It omits what the
   agent already knows (how git works, what a PR is).
3. **Decisiveness** — one default tool/approach per decision. Alternatives are
   an escape hatch, not a menu.
4. **Self-sufficiency** — templates for fixed output formats, checklists for
   multi-step flows, validation loops (do → check → fix → repeat) for fragile
   or destructive operations.

## Curation procedure

1. **Scope.** Confirm the target skill exists and read its current
   `SKILL.md`, `evals/evals.json`, `.skillignore`, and any `references/`.
   Record a baseline: `wc -l SKILL.md`, a token estimate, and the evals
   assertion list. You cannot judge compression without a number to beat.
2. **Decide the operation.** From the baseline and the trigger, pick one:
   - **Improve** — the procedure is right but guidance is thin: add gotchas,
     exact commands, a template, a checklist. Expect the body to grow, then
     re-compress the rest to hold the budget.
   - **Compress** — the body is over budget, wordy, or padded with what the
     agent already knows: cut prose, merge duplicate phases, prefer tables and
     lists over sentences, delete content that repeats `related_skills`.
   - **Update** — the workflow it describes changed: revise commands, gates,
     and pitfalls; reconcile the `## When to Use` triggers.
3. **Apply the distillation pass.** Rework the body against the four
   properties above and the compression checklist below. Use progressive
   disclosure: keep `SKILL.md` under ~500 lines / ~5,000 tokens and push
   reference detail into `references/` with an explicit load condition ("read
   `references/api-errors.md` when the API returns a non-200"), never a generic
   "see references/".
4. **Refresh `evals/evals.json`.** The assertions must stay self-consistent
   with the new body. Re-run the assertions programmatically
   (case-insensitive for prose checks); assert scope behavior, not the absence
   of a string that legitimately appears (a skill's own name, its
   `related_skills`). Update `expected_output` for any prompt whose behavior
   you changed.
5. **Validate.** JSON-parse both manifests touched, run the evals assertions,
   and wrap markdown at 80 columns (MD013). Prefer `nix develop -c nix fmt`
   (full formatter set); a bare `nix fmt` outside the devenv skips
   rumdl-check. Confirm the frontmatter `name` still matches the directory and
   the description is still an imperative `Use when …` under 200 characters.
6. **Report the delta.** State lines and tokens before/after, what you cut or
   added, and whether the evals changed. "Compressed" is a claim — prove it
   with the numbers.

## Compression checklist

Delete or rewrite anything that matches:

- **Restating the obvious** — how git/PRs/`gh` work, generic repo hygiene.
- **Repeating a sibling skill** — content already owned by a
  `related_skills` entry (say "see `sks-commit`", don't re-teach it).
- **Two ways to do one thing** — keep the default, drop the alternatives
  (unless a fallback is genuinely load-bearing).
- **Prose that a table or list carries** — one row beats three sentences.
- **Orphan references** — `references/` files nothing loads; either add the
  explicit load condition or delete them.
- **Stale versions/gates** — commands or rules the workflow no longer uses.

Compression is bounded by clarity: a one-line answer the reader cannot act on
is not cheaper, it is broken. When a choice cuts a real corner, leave a note
naming the ceiling and the upgrade path.

## Gotchas

- **Description drift.** After a big rework the description may no longer
  match the body; keep it a 200-char imperative that names the real triggers,
  or the skill stops firing when it should.
- **Evals rot with the body.** The most common curation failure is editing the
  body and leaving assertions that now fail or assert stale behavior. Refresh
  them in the same pass, in the same commit.
- **Budget is per-load, not per-edit.** A skill can grow when improving; the
  budget is the final body. Improve-then-compress so the result lands lean.
- **Don't break the trigger by over-tightening.** Cutting the description to
  save tokens can strip the `Use when` contexts; keep at least the imperative
  and the primary context.
- **Compression ≠ deletion of safety.** Never remove the validation loops,
  input checks, or gate steps that prevent data loss or broken landings —
  those keep the skill safe, not fluffy.

## Verification

```bash
wc -l SKILL.md                # budget check
nix develop -c nix fmt        # treefmt incl. rumdl-check (MD013)
# evals assertions pass, run programmatically (case-insensitive for prose)
```

Done when the body is within budget, evals pass and match the body, the
description still triggers, and the before/after delta is stated in numbers.

## See also

- `sks-update` — orchestrates curation → dev-workflow → local resync.
- `sks-skill-authoring` — authoring a new skill (curation starts from an
  existing one).
- `sks-dev-workflow` — the loop curation changes ship through.
- `sks-pr-review` — review lens that often flags skills worth curating.
