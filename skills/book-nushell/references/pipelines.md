# Pipelines (Nushell)

Source: `book/pipelines.html`. Three roles: input/source, filter, output/sink.

```nu
open Cargo.toml | update workspace.dependencies.base64 0.24.2 | save Cargo_new.toml
```

- Input: produces data (`open`, `ls`). Filter: transforms (`update`, `where`, `each`). Output: finalizes (`save`, `table`, `print`).
- Multiline pipelines wrap in parentheses `( ... )`.
- **Semicolon `;` discards preceding output** — no value piped; `$in` does NOT capture a `;`-separated statement. Use a continued pipeline, not `;`.
- Most Nu commands *return* data, they do not print. `do { ls; ls }` returns only the last value; use `print`/`| table` to force early display.

## The `$in` variable — the core composability primitive

`$in` holds current pipeline input. Rules (verbatim from book):

- **Rule 1:** In the *first position* of a pipeline inside a closure/block, `$in` = that closure's/block's pipeline (or filter) input. Holds through the whole scope, even later lines.
- **Rule 1.5:** Same `$in` on every line in that scope's first-position use.
- **Rule 2:** Anywhere *else* in a pipeline, `$in` = previous expression's result. Inside a closure/block this creates a new sub-expression scope (Rule 2.5), so Rule 1 and Rule 2 coexist.
- **Rule 3:** No input => `$in` is `null`.
- **Rule 4:** Across `;`-separated statements, `$in` cannot capture the prior statement (same as no-input).

Filter closures may rebind `$in` to a convenient value:

```nu
1..10 | each { $in * 2 }            # $in = current item (same as {|v| $v*2})
ls | update name { str upcase }     # update: $in = the column being updated
```

Best practice: assign `$in` to a named var on the first line for readability/debug.

## Collectability

`$in` on a stream forces collection (not guaranteed future behavior). Use `collect` to guarantee a single collected value. Avoid `$in` when normal pipeline input suffices — it converts `PipelineData` -> `Value` (possible perf/mem cost).

## Display output hook

```nu
$env.config.hooks.display_output = { table -e }   # expanded table
$env.config.hooks.display_output = { table }      # collapsed
$env.config.hooks.display_output = {||}           # simple
$env.config.hooks.display_output = null           # revert to default
```

## External commands interop

- `internal | external`: internal output -> string -> external stdin.
- `external | internal`: bytes -> UTF-8 text stream (or binary if conversion fails); `lines` helps.
- `external1 | external2`: connected like Bash (stdout->stdin).
- `^` prefix forces external: `^ls -la $in`. Without `^`, a builtin with the same name shadows.
- `help <cmd>` shows Input/output types. `ls` ignores piped input (defaults to cwd); pass as param: `echo .. | ls $in`. `sleep` errors on piped input (matches Bash).
