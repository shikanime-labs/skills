# External Commands, Streams, Hooks, Background Jobs (Nushell)

Source: `book/running_externals.html`, `book/stdout_stderr_exit_codes.html`, `book/hooks.html`, `book/background_jobs.html`.

## Running externals (`book/running_externals.html`)

- `^` sigil forces the external (found in PATH): `^ls`, `^git`. Without `^`, a builtin with the same name shadows.
- Args separated by Nushell syntax, not spaces-in-quotes: `git commit -m "msg"` (one arg).
- Lists are NOT auto-spread; use `...`: `git add ...$paths`. (See operators spread rules.)
- `^$program status` runs from a variable. `extern` declaration adds type-check/completions.
- Windows: `^ls` finds nothing (PowerShell alias); some CMD.EXE internals forwarded to cmd.

## Stdout/stderr/exit (`book/stdout_stderr_exit_codes.html`)

- External stdout -> pipeline by default in a pipeline; else prints to screen.
- stderr NOT redirected by default (prints to screen). Pipe it: `e>|` (or `err>|`); to file `e> file`; capture with `do -i { cmd } | complete`.
- Exit code: `$env.LAST_EXIT_CODE` or `complete` (returns record `{stdout, stderr, exit_code}`).
- `echo` returns args (pipe-oriented); `print` prints plain text, returns `nothing`. std lib `use std/log` for levels (`log info`, etc.); level via `$env.NU_LOG_LEVEL`.
- File redirects: `out> file` / `err> file` (short `o>`/`e>`); both `out+err> file` (`o+e>`). Expression paths allowed: `cat x o+e> (std null-device)`.
- Pipe redirects: `|` (stdout), `e>|` (stderr), `o+e>|` (both) — only the LAST command in an expression is affected.
- Raw streams: bytes; Nu tries UTF-8 decode to text; on failure rest stays bytes. `decode <enc>` for control (e.g. `0x[8a 4c] | decode shift-jis`).

## Hooks (`book/hooks.html`)

REPL-only (no effect with `nu script.nu` / `nu -c`). Types: `pre_prompt`, `pre_execution`, `env_change`, `display_output`, `command_not_found`. Cycle: pre_prompt -> env_change -> prompt -> pre_execution -> parse -> command_not_found/display_output -> loop.

- Define in `$env.config.hooks` as blocks or lists of blocks. Append: `$env.config.hooks.pre_execution = $env.config.hooks.pre_execution | append {...}`.
- Hooks PRESERVE env (like `def --env`).
- `pre_execution` can read `commandline`.
- `env_change`: `{ PWD: [{|before, after| ...}] }`. Conditional hook = record `{condition: {|b,a| ...}, code: {...}}`; missing condition => always run. `code` may be a STRING (evaluated as if typed at REPL) to define commands/aliases.
- `display_output` block receives the value; controls rendering (`table`, `to html`). External output NOT filtered through it.
- `command_not_found`: `{|cmd_name| ...}` returns a string to show.

## Background jobs (`book/background_jobs.html`)

- Experimental, thread-based (NOT separate processes). `job spawn { ... }` returns id; killed when shell exits (no `disown`).
- `job list`, `job kill <id>`. Unix: `Ctrl+Z` freezes a running external into a "frozen" job; `job unfreeze [id]` (alias `fg = job unfreeze`) resumes.
- Communicate: `job send <id> <data>` / `job recv` (main thread id = 0).
