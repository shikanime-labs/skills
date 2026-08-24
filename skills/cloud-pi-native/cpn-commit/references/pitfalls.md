# cpn-commit — Pitfalls

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
