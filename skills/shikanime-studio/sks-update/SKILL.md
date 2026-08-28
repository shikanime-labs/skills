---
name: sks-update
description:
  "Use when updating a skill in the shikanime-labs/skills catalog: curate it,
  land the improvement through the dev workflow, and resync it to local Hermes
  agents."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - skill-update
      - curation
      - resync
      - shikanime-labs
      - shikanime-studio
      - workflow
    related_skills:
      - sks-curate
      - sks-dev-workflow
      - sks-stack
      - sks-commit
      - sks-pr-workflow
      - sks-land
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Skill Update

End-to-end update of a skill in the catalog: curate it (`sks-curate`), ship
the improvement through the shikanime dev loop, and resync the landed skill to
local Hermes agents. This is the orchestration shell — curation and shipping
each delegate to their owning skill.

## When to Use

- "Update / improve / resync <skill>."
- "Ship a skill improvement and pull it into my local agents."
- "Run the skill maintenance loop after a batch of corrections."
- "Sync the catalog back into the local Hermes skills."

## Procedure

1. **Curate** — Load `sks-curate`; apply the improvement/compression/update to
   the target `SKILL.md` and refresh `evals/evals.json`. Record the baseline
   and the before/after delta. Do not ship un-curated edits; the curation pass
   is what keeps the catalog lean.
2. **Ship through the dev workflow** — Follow `sks-dev-workflow` for the
   branch/commit/PR/land path:
   - Isolate in a fresh workspace at `main@origin` (`sks-stack`) so foreign
     WIP is never folded in.
   - Commit per `sks-commit` (plain-English title, Automata trailer,
     `Signed-off-by:`; AGENTS.md repos add labeled `Design:`/`Related:` body).
   - Push to origin, open the PR per `sks-pr-workflow` (`--head <org>:<branch>`,
     base `main`, `Related:` full issue URL).
   - Run `sks-pr-review` before requesting merge, then land per `sks-land`
     (or `sks-dev-workflow` landing rules). Verify the merge:
     `gh pr view <N> --json state,url`.
3. **Resync to local Hermes agents** — After the change lands on `main`, pull
   the updated skill into local agents so future sessions load the new body:

   - Default (tap): ensure the repo is tapped, then update the skill:

     ```bash
     hermes skills tap add shikanime-labs/skills 2>/dev/null || true
     hermes skills update shikanime-labs/skills/shikanime-studio/<skill>
     ```

     `hermes skills update` refreshes installed hub/tap skills; `--help`
     lists the flags.

   - Fallback (manual copy from a local checkout):

     ```bash
     cp -r skills/shikanime-studio/<skill> ~/.hermes/skills/shikanime-studio/
     ```

     Resolve the real home from `$HERMES_HOME` when a profile is active
     (`~/.hermes/profiles/<name>/skills/...`), never hardcode `~/.hermes`.

   - Verify the resync: `hermes skills list` shows the skill and
     `hermes skills diff <skill>` (or reading the file) shows the new body.

## Resync gotchas

- **Bundled vs hub-installed skills.** If a skill is bundled with Hermes, a
  manual `cp` marks it `user-modified`, which blocks future `hermes update`
  refreshes; `hermes skills reset` clears that and lets updates flow again.
  Prefer the tap/update path for bundled skills.
- **Profile-aware paths.** Local agents may run under a profile; resolve
  `$HERMES_HOME` instead of assuming `~/.hermes`.
- **Resync is only meaningful after landing.** Copying a branch's skill into
  `~/.hermes/skills` before the PR merges loads un-reviewed content. Land
  first, resync second.

## Gate

Complete when the skill is curated (delta reported), merged to `main`
(`gh pr view <N> --json state` = `MERGED`), and the local agent loads the new
body (`hermes skills list` + content check). Any unmet step is a blocker —
say `BLOCKED:` with evidence and recovery, never silently skip.

## See also

- `sks-curate` — the curation pass (step 1).
- `sks-dev-workflow` — the shipping loop (step 2).
- `sks-stack`, `sks-commit`, `sks-pr-workflow`, `sks-land` — the pieces of
  step 2.
- `hermes-agent` — local agent configuration and skills management.
