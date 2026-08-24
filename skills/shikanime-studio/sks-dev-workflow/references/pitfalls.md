# sks-dev-workflow — Pitfalls

- Not recording steering discoveries in AGENTS.md — next agent repeats them.
- `jj` push without `jj bookmark track <branch> --remote=origin` — rejected.
- Direct-pushing `main` on protected repos — rejected; use PR.
- Assuming conventional commits — shikanime code repos use plain English.
- Skipping build-verify on NixOS repos — invalid config ships.
- `jj describe`/`commit` snapshots every dirty WC file, not just `jj add` —
  isolate via `jj workspace add ../<repo>-fix -r main` (see above).
- GitHub pings any `@name` in prose as a user/team mention. To write a literal
  `@` without notifying anyone — NestJS `` `@Inject(x)` ``, decorators, config
  keys — wrap it in a code span or fenced block; code is the only context where
  mention parsing is disabled.
