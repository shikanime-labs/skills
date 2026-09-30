---
name: sks-commit
description:
  "Use when committing in a target-org repo: plain-English imperative titles
  and repo-enforced hooks (gitlint, DCO) win."
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - jj
      - commit
    related_skills:
      - sks-pr-review
      - sks-dev
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Commit

Commit in the target org's repos. Repo-enforced hooks
(gitlint, commitlint, DCO) ALWAYS win over the defaults below — detect them per
repo, never assume.

## When to Use

- Any commit in a target-org repo. For shikanime-org conventions (the remote
  split between local path and gh remote, protected-main repos, the co-author
  trailer value), read `references/shikanime.md` when operating in a
  shikanime org. For cloud-pi-native commitlint rules (French org,
  conventional English commits with `body-leading-blank`), read
  `references/cloud-pi-native.md` when committing in that org.

## Prerequisites

- Working tree in target repo; `gh` authenticated.
- Branches push to `origin` (the cloned org repo). Where the local path and
  the gh remote disagree, trust the gh remote (the org remote split — see
  `references/shikanime.md`).
- jj repos: `jj bookmark track <branch> --remote=origin` before any push.

## Commit style (when no hook enforces otherwise)

Prose mechanics for the message (free-text body, full URLs in `Related:`,
one clean trailer block, no formatter runs) are owned by
`sks-github-text-authoring`. This skill owns the commit-specific shape:

- **Code repos**: plain English, imperative, capitalized title, **no prefix, no
  body**. One trailer ALWAYS: the org co-author trailer (value in
  `references/shikanime.md`). One logical fix per
  commit.
  - Good: `Force NFS v4.0 on RWX StorageClasses` + trailer.
  - Bad: `fix: force nfs v4.0` (conventional prefix not used here).
- **Doc repos**: `doc:` prefix, else same shape. No `(...)` in titles/labels.

## Squash / multi-commit hygiene

`jj squash` / `gh pr merge --squash` emit INTERNAL artifacts — strip before
commit/merge:

- `*` bullet lines separating former descriptions.
- `---------` separators where descriptions overlapped. Final message = exactly
  one plain-English subject + the correct trailers:
- Exactly ONE org co-author trailer when agent-assisted. Never a self
  `Co-authored-by:` or repeated `Signed-off-by:`.
- `Signed-off-by: <user>` only where a hook/ruleset requires DCO.
- Never rely on GitHub's auto-concatenation of branch commits — pass it clean:

```bash
gh pr merge <M> --repo <org>/<repo> --squash \
  -m "<plain-English subject>" \
  -m "$(cat <<'EOF'
<coherent body; no * bullets, no --------->

Co-authored-by: <the org co-author trailer>
EOF
)"
```

## Repo-enforced overrides

```bash
ls .gitlint .commitlintrc* commitlint.config.* 2>/dev/null
grep -rl "Signed-off-by" .github/ 2>/dev/null
```

- A gitlint-enforced repo enforces a **body** (B6 "body message is missing")
  and a `Signed-off-by` (CC1). A commit with both + no `Related:` passes. See
  `references/example-commit.md` for a filled example.
- PR↔commit parity: the PR title equals the commit subject and the PR body
  restates the commit message; author the commit to carry full rationale.
- Any repo with `commitlint`: follow its config.

## Procedure

1. Stage only the intended files.
2. Commit; two `-m` blocks = subject + trailer paragraph:

```bash
jj describe -m "<subject>" -m "<the org co-author trailer>"
```

3. Confirm the hook accepted it: `jj log -1`.

## Push / landing

- Push to `origin`; open PRs from `--head <org>:<branch>` (`sks-pr`).
- NEVER push to `main` unless the user explicitly authorizes ("push to main" /
  "land it") — then push directly, no PR.
- Protected `main` repos → PR; direct push rejected (org examples in
  `references/shikanime.md`).

## Pitfalls

- Ignoring a repo hook → local commit rejected; detect first.
- Pushing a branch to the wrong remote — `origin` is the single push target.
- Forgetting `jj bookmark track <branch> --remote=origin` → push fails.
- Trailing period / lowercase start in subject — imperative, capitalized.
- Leaving jj `*` / `---------` artifacts or a self `Co-authored-by:` in a
  squashed message.

## Verification

```bash
jj log -1 --no-graph -T 'description' && jj status
```

## See also

- `sks-github-text-authoring` — prose mechanics this skill delegates.
- `sks-pr` — PR title/body derived from this commit (source of truth).
- `sks-dev` — branch discipline this feeds into.
- cloud-pi-native commitlint rules (English conventional commits,
  `body-leading-blank`, no DCO): `references/cloud-pi-native.md`.
