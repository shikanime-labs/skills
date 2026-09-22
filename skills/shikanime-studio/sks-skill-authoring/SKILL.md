---
name: sks-skill-authoring
description:
  "Use when creating a brand-new skill for the shikanime-labs/skills catalog:
  grounded body, evals, manifests, and ship through the dev workflow."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - skill-authoring
      - catalog
      - evals
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-curate
      - sks-update
      - sks-dev-workflow
      - sks-adversarial
      - sks-commit
      - sks-pr-workflow
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Skill Authoring

Create a NEW skill for the catalog: distill a real execution into a grounded
`SKILL.md`, give it honest evals, register it, and ship it through the shikanime
dev loop. This is the authoring counterpart to `sks-curate` (which reworks an
existing skill).

## When to Use

- "Create / add / write a new skill for shikanime-labs or shikanime-studio."
- "Turn the procedure we just ran into a reusable catalog skill."
- A gap review shows a recurring task with no catalog entry and no user-local
  skill worth promoting.

Don't use for: improving an existing skill (`sks-curate`), the whole-catalog
pass (`sks-update`), or skills outside the two org families (those stay
user-local in `~/.hermes/skills/` and never ship in this repo).

## Before You Write

Climb in order; stop at the first rung that holds:

1. **Does it exist?** Search the catalog and `~/.hermes/skills/` for an
   overlapping trigger. A near-duplicate means extend the existing skill, not
   create a narrow sibling.
2. **Does it belong here?** This repo ships exactly three families: `sks-*`
   (shikanime-studio), `cpn-*` (cloud-pi-native), and `nixpkgs`. Anything else
   is user-local, full stop.
3. **Is it grounded?** The body must be distilled from a real execution you
   ran: the steps that worked, corrections made, exact commands, the
   input/output shapes you hit. If you have not run the procedure, run it
   first — in the `sks-adversarial` sandbox when it is destructive — then
   write from the transcript, never from imagination.

## Anatomy of a Catalog Skill

The audit gate in `sks-update` enforces every item below; a skill missing one
fails before review.

- `skills/<family>/<name>/SKILL.md` — frontmatter `name` equals the directory.
- Frontmatter fields (all required): `name`, `description`, `version`
  (`0.1.0` for new skills), `author`, `license: Apache-2.0`, `platforms`,
  `metadata.hermes.tags`, `metadata.hermes.related_skills`.
- `description`: imperative `Use when …`, at most 200 characters, names the
  real triggers. Quote it when it contains a colon.
- `related_skills`: every entry resolves to a skill that exists in this repo.
- `evals/evals.json`: `{"evals": [...], "skill_name": "<name>"}`; each entry
  carries `id`, `prompt`, `expected_output`, `files`, and 3-5 objective
  `assertions` gradeable without a human.
- `.skillignore` containing `evals/` (the scanner skips fixtures).

## Procedure

1. **Run the procedure for real.** Capture commands as executed and every
   correction ("this flag was wrong", "wait for X before Y"). Those
   corrections become the Gotchas section.
2. **Isolate.** Open a fresh workspace per `sks-delegate`, pinned to
   `main@origin`; never author in a dirty checkout.
3. **Write `SKILL.md`.**
   - Section order: `## When to Use`, `## Procedure` (numbered, each step
     with a checkable completion criterion), `## Gotchas` or `## Pitfalls`,
     `## Verification`, `## See also`.
   - One default tool per decision; alternatives are an escape hatch, not a
     menu.
   - Commands exactly as run, in fenced blocks. Reference sibling skills by
     name instead of re-teaching them.
   - Push detail past ~5,000 tokens into `references/<topic>.md` with an
     explicit load condition ("read `references/x.md` when Y happens").
4. **Write `evals/evals.json`.** Three prompts: two varied phrasings of the
   trigger, one edge case (adjacent task that should route elsewhere).
   Assertions check the body, not trivia: scope routing, pinned flags, gate
   steps. Never assert the absence of a string that legitimately appears.
5. **Register the skill** in all three places:
   - `README.md` catalog table — one row.
   - `skills.json` — `{"name", "description", "path"}` entry.
   - `package.json` — `agents.skills` entry with the same three fields.
6. **Validate locally** (see Verification), then commit per `sks-commit` and
   open the PR per `sks-pr-workflow`.

## Gotchas

- **Non-imperative description never fires.** The description is a trigger;
  "Authoring tools for skills" is decorative. "Use when creating …" routes.
- **Description drift kills triggering.** After writing the body, re-read the
  description: if the body covers triggers the description omits, widen it
  (still ≤200 chars).
- **Evals rot before they run.** Assertions must survive the final body edit;
  re-run them after the last change, in the same commit.
- **MD013 / MD032 are the common CI failures.** Wrap at 80 columns; a list
  needs a blank line before it — including inside `references/` files.
- **Unregistered skill = invisible skill.** A missing `skills.json` or
  `package.json` entry ships a skill the installer never installs; grep all
  three manifests for the name before pushing.
- **`name` must equal the directory**, or `hermes skills` tooling cannot
  resolve it.

## Verification

```bash
nix develop -c nix fmt              # treefmt incl. rumdl-check (MD013)
uvx rumdl check skills/shikanime-studio/<name>/
python3 -c "import json; json.load(open('skills.json')); \
json.load(open('package.json')); print('manifests ok')"
# evals assertions pass, run programmatically (case-insensitive for prose)
grep -c '"<name>"' skills.json package.json   # both >= 1
```

Done when: frontmatter parses and matches the anatomy table, evals pass, the
skill appears in all three registration surfaces, and fmt/rumdl are clean.

## See also

- `sks-curate` — rework pass for an existing skill.
- `sks-update` — whole-catalog loop this skill plugs into.
- `sks-dev-workflow` — the shipping loop; authoring is its Phase 3 content.
- `sks-adversarial` — sandbox to ground the procedure in before writing.
