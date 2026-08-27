---
name: cpn-commit
description:
  "À utiliser quand vous committez dans cloud-pi-native/console : commits
  conventionnels en français via jj."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - conventional-commits
      - jj
      - commit
      - github
      - cloud-pi-native
    related_skills:
      - cpn-dev-workflow
      - cpn-pr
platforms:
  - linux
  - macos
  - windows
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
| Footer   | optional `BREAKING CHANGE:` (no `Closes #N` — close deliberately)                         |

> Reference safety: `#N` in a commit body resolves to a console issue/PR and
> `Closes` / `Fixes` / `Resolves` auto-close it on merge. Bare `#N` is only safe
> for a console ticket; cross-repo refs use a full URL or `owner/repo#N`.

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

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

```bash
jj log -1 --pretty=%B && jj status --short
```

## See also

- `cpn-pr` — open the PR (title matches conventional subject).
- `cpn-dev-workflow` — the local dev loop this feeds into.
