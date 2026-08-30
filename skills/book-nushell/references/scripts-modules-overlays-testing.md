# Scripts, Modules, Overlays, Testing (Nushell)

Source: `book/scripts.html`, `book/modules.html`, `book/overlays.html`, `book/testing.html`.

## Scripts (`book/scripts.html`)

- Run in new instance: `nu myscript.nu`. Run in current instance: `source myscript.nu`.
- Definitions run first, then top-to-bottom command groups (order doesn't require defs-before-use).
- `main` command runs last; enables CLI args/flags: `nu myscript.nu 100` -> `def main [x: int] { $x + 10 }`.
- Untyped script args parsed by apparent type (`nu x.nu +1` => int). Typed args enforced.
- Subcommands: `def "main run" [] {...}`, `def "main build" [] {...}`; called `nu x.nu build`. Must define `main` (even empty) for subcommands to expose.
- Shebang: `#!/usr/bin/env nu`. For stdin: `#!/usr/bin/env -S nu --stdin` and `def main [] { echo $"stdin: ($in)" }`.

## Modules (`book/modules.html`)

- Containers of custom commands, aliases, constants, externs, env vars, submodules.
- Three forms: inline `module spam { ... }`, file `spam.nu`, directory.
- `use spam.nu` / `use spam.nu *` (exported only). `export def`/`export alias`/`export-env` to expose.
- `export-env { load-env { BAZ: "baz" } }` runs env setup on `use`.
- (Sub-pages `modules/using_modules.html`, `modules/creating_modules.html` for detail.)

## Overlays (`book/overlays.html`)

- Swappable "layers" of definitions (like Python venvs). Default overlay `zero`. `overlay list`.
- Create from a module: `overlay use spam` (brings defs/aliases/env into scope, runs `export-env`).
- `overlay hide spam` removes; `overlay hide` (no arg) removes last. Scoped: removed at end of block.
- Definitions recorded into last active overlay; remembered after hide (re-add to restore).
- `overlay new scratchpad` creates empty overlay just for recording changes.
- `overlay use --prefix spam` => defs as subcommands (`spam foo`); env vars NOT prefixed.
- `overlay use spam as eggs` renames. `overlay hide --keep-custom spam` keeps added defs; `--keep-env [FOO]` keeps listed env vars.
- Stack: last-active overlay wins on name clash; `overlay use zero` again reorders to top.

## Testing (`book/testing.html`)

- `use std/assert`. `assert (<cond>)` errors if false; add message: `assert ($a==19) $"wrong: ($a)"`.
- Typed asserts for better errors: `assert equal`, `assert str contains $b $a`, etc.
- Custom assert via `error make` label:
  `def "assert even" [n:int] { assert ($n mod 2 == 0) --error-label {text: $"($n) not even", span: (metadata $n).span} }`
- Nupm package: `tests/` dir + `mod.nu`; `export def` = a test; `nupm test`.
- Standalone: write `tests.nu` using `use ...` + `use std/assert`, run `nu tests.nu`.
- Basic framework: discover via `scope commands | where name starts-with "test "` and run in a second `nu` instance.
