---
name: sks-update
description:
  "Use when updating skills in the shikanime-labs/skills catalog: curate every
  skill by default (or named ones only), land through the dev workflow, and
  resync to local Hermes agents."
version: 0.2.0
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

End-to-end update of the catalog: curate each skill (`sks-curate`), ship the
improvements through the shikanime dev loop, and resync the landed skills to
local Hermes agents. This is the orchestration shell — curation and shipping
delegate to their owning skills.

**Default scope: every skill in the catalog.** Only narrow to a named subset
when the user explicitly lists skills ("update sks-commit only"). "Update the
catalog / all skills / sync everything" all mean the full pass. Never silently
curate one skill when the user asked for all, and never silently expand to all
when the user named one.

## When to Use

- "Update / improve / resync the catalog" or "all skills" — full pass.
- "Update / improve / resync <skill>" — that skill only (or a named subset).
- "Ship skill improvements and pull them into my local agents."
- "Run the skill maintenance loop after a batch of corrections."

## Procedure

1. **Scope.** Decide the target set:
   - Full pass (default): enumerate the catalog from `README.md` (or the
     `skills/` tree) — every `sks-*` and `cpn-*` `SKILL.md`.
   - Explicit subset: only the skills the user named.
   Record the set. Do not skip skills silently; a skipped one is a reported
   reason, not an omission.
2. **Audit every skill in scope.** For each, run an automated check and record
   the defects (these are the evidence the curation acts on):
   - `SKILL.md` YAML frontmatter parses; `name` equals the directory.
   - Description is an imperative trigger (`Use when …` / `À utiliser quand`)
     under 200 characters.
   - `evals/evals.json` exists, parses, `skill_name` matches, and assertions
     are self-consistent with the body.
   - `.skillignore` present (so the scanner skips `evals/`).
   - No lines over 80 columns (MD013); run `rumdl check` / `nix fmt` to catch
     it.
   - Body within budget (~500 lines / ~5,000 tokens).
3. **Curate per skill.** Load `sks-curate`; apply improvement/compression/
   update to each audited defect, and refresh its `evals/evals.json`. Record
   the baseline and before/after delta for each. Do not ship un-curated edits;
   the curation pass is what keeps the catalog lean.
4. **Ship through the dev workflow** — Follow `sks-dev-workflow` for the
   branch/commit/PR/land path:
   - Isolate in a fresh workspace at `main@origin` (`sks-stack`) so foreign
     WIP is never folded in.
   - Commit per `sks-commit` (plain-English title, Automata trailer,
     `Signed-off-by:`; AGENTS.md repos add labeled `Design:`/`Related:` body).
   - Push to origin, open the PR per `sks-pr-workflow` (`--head <org>:<branch>`,
     base `main`, `Related:` full issue URL). A full pass is one atomic PR
     carrying the whole curated set (one objective, reviewed in one sitting);
     split into stacked PRs only when the change set grows past a comfortable
     review size.
   - Run `sks-pr-review` before requesting merge, then land per `sks-land`
     (or `sks-dev-workflow` landing rules). Verify the merge:
     `gh pr view <N> --json state,url`.
5. **Resync to local Hermes agents** — After the change lands on `main`, pull
   every updated skill into local agents so future sessions load the new body:

   - Default (tap): ensure the repo is tapped, then update:

     ```bash
     hermes skills tap add shikanime-labs/skills 2>/dev/null || true
     hermes skills update shikanime-labs/skills
     ```

     `hermes skills update` refreshes installed hub/tap skills; `--help`
     lists the flags. Update the tap as a whole for a full pass, or name the
     skill path to update one.

   - Fallback (manual copy from a local checkout):

     ```bash
     cp -r skills/shikanime-studio/<skill> ~/.hermes/skills/shikanime-studio/
     ```

     Repeat per updated skill. Resolve the real home from `$HERMES_HOME` when a
     profile is active (`~/.hermes/profiles/<name>/skills/...`), never hardcode
     `~/.hermes`.

   - Verify the resync: `hermes skills list` shows each updated skill and
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
- **Audit drives the pass, not taste.** Curate what the audit flags; leave
  healthy skills untouched so the full pass stays a small, reviewable diff
  rather than a rewrite of everything.

## Gate

Complete when every in-scope skill is curated (delta reported per skill),
merged to `main` (`gh pr view <N> --json state` = `MERGED`), and local agents
load the new bodies (`hermes skills list` + content check). Any unmet step is
a blocker — say `BLOCKED:` with evidence and recovery, never silently skip.

## See also

- `sks-curate` — the per-skill curation pass (step 3).
- `sks-dev-workflow` — the shipping loop (step 4).
- `sks-stack`, `sks-commit`, `sks-pr-workflow`, `sks-land` — the pieces of
  step 4.
- `hermes-agent` — local agent configuration and skills management.
