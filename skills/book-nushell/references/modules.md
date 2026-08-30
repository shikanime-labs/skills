# Modules: Using & Creating (Nushell)

Source: `book/modules/using_modules.html`, `book/modules/creating_modules.html`.

## Using (`use`)

```nu
use <path> <members...>
use std/log                # imports module as command w/ subcommands: log info
use std                    # import as `std log info` (record access)
use std/formats *          # import defs into current scope: to jsonl
use std/math PI           # selective: $PI
use std/assert            # virtual dir (stdlib)
```

- Module path: dir containing `mod.nu`, a `.nu` file, or virtual dir (`std/...`). Relative paths also search `$NU_LIB_DIRS` then `$env.NU_LIB_DIRS` (deprecated).
- Constants via record when importing whole module: `use std/math; $math.PI`. Or `use std/math *; $PI`.
- `hide assert` restores previous def; `hide assert main` hides just the `main` masquerade. Import patterns accepted.
- Make always-available: add `use` to startup config.

## Creating

- File form `<name>.nu` or directory form `<name>/mod.nu`. Only `export`ed defs/aliases/consts/externs/env are visible outside (others are private).
- Exports: `export def`, `export alias`, `export const`, `export extern`, `export module`, `export use`, `export-env`.
- `main` export takes module's name when imported: `export def main []: int -> int {...}` => `use inc.nu; 2024 | increment`. An export CANNOT share the module's name (error `named_as_module`) — use `main`.
- Subcommands: `export def "increment by" [...]` or just `by` (when imported as module).
- Submodules: `export module ./sub.nu` (submodule + members under it) vs `export use ./sub.nu` (members become parent's). `export use` can SELECTIVELY export: `export use ./go.nu [home, modules]`. `module` without `export` = local only.
- Document: leading comment lines => `help <module>`.
- `export-env { $env.X = ... }` runs env setup on `use`. Caveat: `export-env` only runs when the `use` is EVALUATED, not just parsed — in a parent module it won't run unless re-`use`d inside a command or inside an `export-env` block (`use my-utils []`).
- Windows: use forward-slashes for portability.
