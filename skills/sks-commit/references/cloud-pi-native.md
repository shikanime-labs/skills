# cloud-pi-native commit rules (conventional + commitlint)

Load when committing in the cloud-pi-native/console repository.

## Org identity

- Commits in **English** (even doc-only changes); scope and review rules
  unchanged. Issues/discussions/PR bodies are French.
- Attribution trailer ALWAYS (operator instruction), as a second `-m` block:
  `Co-authored-by: Automata <automata@shikanime.studio>` — even on bodyless
  commits. Do NOT add other trailers (`Signed-off-by`, DCO) unless asked —
  console needs no DCO. Existing `Signed-off-by` + `Change-Id` footers from
  prior history are kept, not stripped.
- The repo is jj-backed: never `git commit`; use `jj describe` / `jj new`.
  `jj` signs new commits automatically (`signing.behavior = own`). To
  re-author as another user: `jj new <base> && jj restore --from <old> &&
  jj describe -m "..."` or `jj commit --config user.name=... --config
  user.email=...` — never falsify `Signed-off-by` to a different person.

## Enforced commitlint config (when the repo enforces it)

- Husky `commit-msg` hook runs `pnpx commitlint --edit ${1}` (`.husky/commit-msg`),
  enforcing `commitlint.config.cjs`, which extends
  `@commitlint/config-conventional` and adds
  `'body-leading-blank': [2, 'always']` — an empty line MUST follow the
  subject even when there is no body.

| Rule     | Value                                                                                     |
| -------- | ----------------------------------------------------------------------------------------- |
| Types    | `feat`, `fix`, `chore`, `docs`, `refactor`, `revert`, `build` (`feature` also recognized) |
| Scope    | optional, `type(scope):`                                                                  |
| Breaking | `type!:` / `type(scope)!:` (MAJOR bump)                                                   |
| Subject  | imperative, lowercase start, **no trailing period**                                       |
| Body     | optional, separated from subject by exactly one blank line                                |
| Footer   | optional `BREAKING CHANGE:` (no `Closes #N` — close deliberately)                         |

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

- Reference safety: `#N` in a commit body resolves to an issue/PR of that
  repo; `Closes`/`Fixes`/`Resolves` auto-close on merge — close deliberately
  after N-of-N instead. Bare `#N` only for same-repo tickets; cross-repo refs
  use a full URL or `owner/repo#N`.

## Pitfalls

- Missing blank line after subject → hook rejects (`body-leading-blank` is
  error-level), applies to bodyless commits too.
- Non-conventional type (`update`, `wip`) → commitlint rejects.
- Trailing period / uppercase / non-imperative subject → `feat: Added X`
  wrong; use `feat: add X`.
- Squash hygiene: never let jj `*` / `---------` artifacts or duplicate
  trailers leak — one subject + the trailers the repo wants.
- `main` is protected: commit on a feature/`hotfix/*` branch, never `main`.
