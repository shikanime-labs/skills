---
name: cpn-commit
description: "Commit to cloud-pi-native/console with conventional format."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [conventional-commits, jj, commit, github, cloud-pi-native]
---

# CPN Org Commit

Conventional commits in `cloud-pi-native/console`, honoring the enforced
commitlint config that drives release-please and the PR-title rule (`cpn-pr`).
Does NOT push, open PRs, or run CI — those live in `cpn-pr` /
`cpn-dev-workflow`.

## Prerequisites

- Working tree in `cloud-pi-native/console`.
- Husky `commit-msg` hook runs `pnpx commitlint --edit ${1}`
  (`.husky/commit-msg`), enforcing `commitlint.config.cjs`.
- That config extends `@commitlint/config-conventional` and adds
  `'body-leading-blank': [2, 'always']` — an empty line MUST follow the subject
  even when there is no body.

## Commit shape

| Rule     | Value                                                                                     |
| -------- | ----------------------------------------------------------------------------------------- |
| Types    | `feat`, `fix`, `chore`, `docs`, `refactor`, `revert`, `build` (`feature` also recognized) |
| Scope    | optional, `type(scope):`                                                                  |
| Breaking | `type!:` / `type(scope)!:` (MAJOR bump)                                                   |
| Subject  | imperative, lowercase start, **no trailing period**                                       |
| Body     | optional, separated from subject by exactly one blank line                                |
| Footer   | optional `Closes #N`, `BREAKING CHANGE:`                                                  |

## Procedure

1. Stage: `jj add <files>`.
2. Commit through `jj commit -m` with `-m` blocks (the blank line between blocks
   satisfies `body-leading-blank`):

```bash
# short (no body) — keep the trailing blank line in the heredoc
jj commit -m "$(cat <<'EOF'
fix: prevent null group lookup in Keycloak sync

EOF
)"
# with body
jj commit -m "$(cat <<'EOF'
feat(plugins): add vault secret rotation

Supports monthly rotation via the hook post step.

Refs #123
EOF
)"
```

3. Agent attribution ALWAYS (operator instruction), as a second `-m` block:

```bash
jj describe -m "fix: prevent null group lookup in Keycloak sync" \
  -m "Co-authored-by: Automata <automata@shikanime.studio>"
```

4. Confirm: `jj log -1 --pretty=%B`.

## Pitfalls

- **Missing blank line after subject** → `commit-msg` hook rejects
  (`body-leading-blank` is error-level); applies even to bodyless commits.
- **Non-conventional type** (`update`, `wip`) → commitlint rejects.
- **Trailing period / uppercase / non-imperative subject** → `feat: Added X`
  wrong; use `feat: add X`.
- **Operator preference vs repo rule**: short bodyless messages are COMPATIBLE
  (only the blank line is hard). The
  `Co-authored-by: Automata <automata@shikanime.studio>` trailer is ALWAYS added
  even on bodyless commits; do NOT add other trailers (`Signed-off-by`, DCO)
  unless asked — console needs no DCO.
- **`main` is protected**: commit on a feature/`hotfix/*` branch, never `main`.
- **Author vs committer**:
  `jj signs new commits automatically (signing.behavior = own)`. To re-author as
  another user:
  `jj new <base> && jj restore --from <old> && jj describe -m "..."` or
  `jj commit --config 'user.name=...' --config 'user.email=...'` — but never
  falsify `Signed-off-by` to a different person. Existing `Signed-off-by` +
  `Change-Id` footers from prior history are kept, not stripped (the "no DCO
  unless asked" rule means don't ADD new ones).
- **Squash hygiene**: when folding commits, never let jj `*` / `---------`
  artifacts or duplicate trailers leak — one subject + the trailers the repo
  wants.

## Verification

```bash
jj log -1 --pretty=%B && jj status --short
```

## See also

- `cpn-pr` — open the PR (title matches conventional subject).
- `cpn-dev-workflow` — the local dev loop this feeds into.
