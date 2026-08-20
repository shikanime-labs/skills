---
name: cpn-commit
description: "Commit to cloud-pi-native/console with conventional format."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [conventional-commits, git, commit]
---

# CPN Console Commit

Create commits in `cloud-pi-native/console` honoring the repo's enforced
commitlint config. Covers the conventional-commit contract that drives
Release Please and the PR-title rule (see `cpn-pr`). It does NOT push, open
PRs, or run CI — those live in `cpn-pr` / `cpn-dev-workflow`.

## When to Use

- "Commit this in console" / "make a conventional commit".
- Any commit in `cloud-pi-native/console` that must pass the `commit-msg` hook.

## Prerequisites

- Working tree in `cloud-pi-native/console`.
- Husky `commit-msg` hook runs `pnpx commitlint --edit ${1}`
  (`.husky/commit-msg`), enforcing `commitlint.config.cjs`.
- `commitlint.config.cjs` extends `@commitlint/config-conventional` and adds the
  rule `'body-leading-blank': [2, 'always']` — so an empty line MUST follow the
  subject line even when there is no body.
- `gh` (if linking a PR later) — see `cpn-pr`.

## How to Run

Stage files and commit through the `terminal` tool with `jj commit -m`. Do
NOT hand-type a long message into an editor; pass `-m` blocks so the
body-leading-blank rule is satisfied.

## Quick Reference

| Rule | Value |
|---|---|
| Types | `feat`, `fix`, `chore`, `docs`, `refactor`, `revert`, `build` (also `feature` recognized by release-please) |
| Scope | optional, `type(scope):` |
| Breaking | `type!:`, or `type(scope)!:` (triggers MAJOR bump per release-please) |
| Subject | imperative, lowercase start, no trailing period |
| Body | optional, but MUST be separated from subject by exactly one blank line |
| Footer | optional `Closes #N`, `BREAKING CHANGE:`, etc. |

## Procedure

### 1. Stage the intended files

```bash
jj add <files>
```

### 2. Commit with the enforced shape

Short commit (no body) — note the empty line between subject and the trailing
closing quote; that blank line satisfies `body-leading-blank`:

```bash
jj commit -m "$(cat <<'EOF'
fix: prevent null group lookup in Keycloak sync

EOF
)"
```

With a body:

```bash
jj commit -m "$(cat <<'EOF'
feat(plugins): add vault secret rotation

Supports monthly rotation via the hook post step.

Refs #123
EOF
)"
```

Agent attribution (ALWAYS, per operator): add the co-author trailer as a
second `-m` block — two `-m` = subject paragraph + trailer paragraph, blank
line auto-inserted (satisfies `body-leading-blank`):
```bash
jj describe -m "fix: prevent null group lookup in Keycloak sync" \
  -m "Co-authored-by: Automata <automata@shikanime.studio>"
```

### 3. Confirm the hook accepted it

```bash
jj log -1 --pretty=%B
```

## Pitfalls

- **Missing blank line after subject** → `commit-msg` hook rejects
  (`body-leading-blank` is error-level). This applies even for bodyless commits;
  keep the trailing blank line in the heredoc.
- **Non-conventional type** (e.g. `update`, `wip`) → commitlint rejects. Use one
  of the seven listed types.
- **Trailing period in subject** → violates conventional style; while
  commitlint's default `subject-full-stop` rule is warning-level here, keep
  subjects period-free.
- **Uppercase / non-imperative subject** → `feat: Added X` is wrong; use `feat:
  add X`.
- **User preference vs repo rule**: the operator prefers short, bodyless
  messages — COMPATIBLE with the repo (the only hard constraint is the blank
  line after the subject). The one standing exception: the `Co-authored-by:
  Automata <automata@shikanime.studio>` trailer is ALWAYS added (explicit
  operator instruction) even on bodyless commits — it lands via the second `-m`
  block. Do not add OTHER trailers (`Signed-off-by`, DCO) unless the operator
  explicitly asks; console does not require DCO.
- **`main` is protected**: commit locally on a feature/`hotfix/*` branch; do not
  commit directly to `main`.
- **Author vs committer vs trailers**: when a commit already carries a
  `Signed-off-by` and `Change-Id` trailer for a specific identity, the author
  AND committer should match that identity — not the bare `git config user.*`.
  If they diverge (e.g. author = `shikanime`, committer = `William Phetsinorath`
  with a William `Signed-off-by`), align them. To set both author and committer
  on a fresh commit, recreate it: `jj new <base> && jj restore --from <old> &&
  jj describe -m "..." && jj commit --config 'user.name=...' --config
  'user.email=...' -m "..."`. jj signs new commits automatically
  (`signing.behavior = own`). Do NOT hand-edit the `Signed-off-by` line to a
  different person than who actually authored it.
- **Existing `Signed-off-by` trailers are kept, not stripped**: this operator's
  commits legitimately carry `Signed-off-by` + `Change-Id` footers (from prior
  jj workflow). The "no DCO unless asked" rule means *don't add new* trailers to
  a bodyless commit the operator just wrote; it does NOT mean delete trailers
  that are already part of the commit history being squashed/extended.

## Verification

```bash
jj log -1 --pretty=%B && jj status --short
```

Confirm the last commit message is conventional and a blank line separates
subject from body (if any), and the working tree reflects only the intended
change.

## See also

- `cpn-pr` — open the PR once committed (title must match the conventional
  subject, body kept in parity).
- `cpn-dev-workflow` — branch discipline, pre-push unit tests, and the full
  local dev loop this commit feeds into.
