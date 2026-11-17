# Skills

A curated catalog of self-improved agent skills for Hermes and compatible
agents. Each skill lives in its own directory with a `SKILL.md`.

**Language:** Markdown (SKILL.md)

## Structure

- `skills/` — every catalog skill (org-neutral bodies, org specifics in
  per-skill `references/`)
- `README.md` — Installation and usage documentation

## Workflow

One doctrine — the lifecycle is **discussion → issue → issue comments → PR**.
The issue body is the problem statement with acceptance criteria as a
command-decidable tasklist (the gate ledger); the PR proves it. Skill bodies
are org-neutral; organization-specific conventions load on demand from
per-skill references (`references/shikanime.md` for shikanime,
`references/cloud-pi-native.md` for cloud-pi-native console work).

## Version Control

Use jj (Jujutsu), not git, for all local work: clone with `git clone` then
`jj git init --git-repo .`, develop on bookmarks (`jj new main@origin -m
"…"`), push with `jj git push -b <branch>`. Fall back to plain git only
where jj is refused by the server (signed annotated tags trip pre_receive
rules — `git tag -s` + `git push origin vX.Y.Z`). Fetch before starting:
`jj git fetch` (stale clones produce empty-diff PRs).

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix.
- Body is labeled, one label per line where applicable:
  - `Design:` — files or skills the change is grounded in.
  - `Related:` — companion files, issues, or PRs.
  - `Issue: #N` — the linked ticket (reference only; the PR↔issue link is
    Development metadata, `sks-pr-triage` step 5).
  - Free prose explains the atomic change: what and why. Code carries no
    matching comment — zero comments by default, extract structure
    (subfunction, named intermediate) instead; a comment only for facts
    unreachable from the repository (workaround trick, algorithm source,
    external service error quirk, non-obvious invariant), per
    `sks-edit` references/comment-policy.md.
- Footers mandated by policy:
  - `Signed-off-by:` — required; commits must be signed (see Protect `main`).
  - `Change-Id:` — keep the originating change's id when amending.
- Nix: dotted assignment (`a.b.c = v;`) for a single leaf under a shared
  parent key; a record literal once two or more keys share the parent, keys
  sorted
- Wrap Markdown lines at 80 columns and run `nix fmt` before shipping.

Example: Wire release management, milestone metadata, trunk-based jj stacking

```text
Encode four principles into the workflow substrate and skills.

Design: README.md, AGENTS.md
Related: skills/
Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>
```

## Protect `main`

- Require 1 approving review
- Require linear history (no merge commits)
- Require signed commits
- Squash+rebase merge only

## Adding a New Skill

1. Create a directory under the appropriate category
2. Write a `SKILL.md` following the
   [skill authoring](https://hermes-agent.nousresearch.com/docs) format and the
   authoring practices below; a skill shipping a `references/shikanime.md`
   carries the working doctrine bullet
3. Add the skill to the catalog table in `README.md` and both manifests
   (`skills.json`, `package.json` `agents.skills`)
4. Commit with a descriptive message

## Skill Authoring Practices

The full practices distillation — grounding in real execution, context
spend, defaults not menus, pitfalls over general advice, description
triggers, evals — lives in docs/authoring-practices.md. Read it before
authoring or materially editing any SKILL.md.

## Skill Categories

One flat catalog in `skills/`. Bodies are generic; org specifics live in
per-skill references loaded on demand.

_Each skill must include a valid `SKILL.md` with YAML frontmatter. Test against
the target agent before submitting_

## Environment

This repository ships a `.envrc` for direnv. Run `direnv allow` once after
cloning; direnv then loads the Nix flake dev shell automatically on every
directory change (`.envrc` runs
`use flake . --accept-flake-config --no-pure-eval`). Without direnv, enter
the same shell manually with `nix develop`.
