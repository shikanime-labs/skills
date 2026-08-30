---
name: book-nushell
description: "Nushell book distilled: types, pipelines, commands, modules."
version: 0.1.0
author: Hermes
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [Nushell, Shell, Data-Processing, Reference]
---

# Nushell Docs

Distilled knowledge base of the official Nushell book (nushell.sh/book). Nushell is a shell + programming language where commands pass **typed structured data** (not just text) through pipelines. This skill covers the language, the shell features, and the standard library/plugins — not a re-paste of the book, but structured mental models and verbatim command forms.

What it does NOT do: replace `help <command>` (run it for live signatures/Input-Output types), or cover every command — use the command reference. It assumes `nu` is installed.

Load a reference on demand with `skill_view` (file_path="references/<file>"). SKILL.md is always loaded; references cost nothing until needed.

## When to Use

- "How do I do X in Nushell?" (filter a table, parse a file, write a custom command)
- Translating a Bash/PowerShell/Python snippet to Nushell (`coming-from-bash`, `maps-and-thinking`)
- "Why does this Nushell error happen?" (type mismatch, `source` not found, env not set) — see `maps-and-thinking`, `environment-config`
- Authoring `.nu` scripts, modules, overlays, or config (`config.nu`/`env.nu`)
- Running external commands, capturing exit codes, parallelizing with `par-each`

## Prerequisites

- `nu` installed (any recent 0.9x+). Check: `nu --version`.
- For plugins: `nu-plugin` protocol version must match the `nu` version.
- For stdlib: loaded at startup by default; `use std/<submodule>` to import.

## How to Run

- Explore commands via `terminal`: `nu -c 'help <cmd>'` or `nu -c 'help <cmd> | columns'`.
- Run a snippet: `nu -c 'ls | where type == dir | each {|r| $r.name}'`.
- Read a reference here with `skill_view` (file_path="references/<name>.md").
- Official command index: `https://www.nushell.sh/commands/docs/` (use `web_extract` if needed).

## Quick Reference

- Pipeline: `input | filter | output`; multiline wrap `( ... )`; `;` discards output.
- Types: `int float string bool datetime duration filesize range binary list record table closure cell-path block nothing any`.
- Data: `open` (auto-format), `from <fmt>`, `to <fmt>`, `http get`, `describe`, `get`/`select`, `where`, `each`, `reduce`, `par-each`.
- Def: `def name [p: type --flag (-f): int ...rest: t] { ... }` (implicit return).
- Env: `$env.FOO = ..`; scoped; `def --env` to persist; `with-env {..} {..}`; `hide-env`.
- Modules: `use std/assert`; `export def`; `overlay use spam`.
- Shell: `^ls` forces external; `out> file`; `e>|` stderr pipe; `complete` captures streams+exit.

## Procedure

1. Identify the task; if it maps from another shell, load `references/coming-from-bash.md` or `references/maps-and-thinking.md`.
2. For data shaping, load the matching reference (`types-and-data`, `navigating-data`, `working-with-strings/lists/tables`, `pipelines`, `loading-data`).
3. For authoring, load `custom-commands`, `scripts-modules-overlays-testing`, `modules`, `environment-config`.
4. For shell interop, load `shell-runtime` (externals, streams, hooks, jobs); for stdlib/parallel/plugins load `stdlib-metadata-parallel-plugins`.
5. Verify the exact command form with `nu -c 'help <cmd>'` before relying on it.

## Pitfalls

- `>` is the comparison operator, NOT redirection (use `| save` / `out>`).
- `echo` returns a value, not prints — use `print` for side-output; only the LAST expression value is returned.
- Static parsing: `source`/`use`/`plugin use` resolve at parse time — targets must exist (use `const` paths, full paths; never `cd` then `source` in one expression).
- `get` returns the VALUE; `select` returns the STRUCTURE (table/list/record).
- Tables are lists of records; `get 0` on a table => a record.
- Semicolon discards output — `$in` can't capture a `;`-separated statement.
- Env changes are scoped (die at block end) unless `def --env` / `export def --env`.
- Floats are approximate: `10.2 * 5.1` => `52.0199...`.

## Verification

Run `nu -c 'open --raw <somefile> | from json | describe'` to confirm Nu parses/prints structured data; or `nu -c 'help' | lines | length` to confirm the command index loads.

## Reference Index (load on demand)

- `references/types-and-data.md` — type table, literals, cell-paths, optionals. Load when: typing/coercing values or debugging a type mismatch.
- `references/loading-data.md` — `open`/`from`/`to` formats, NUON, URLs, raw mode. Load when: reading files/SQLite/APIs into structured data.
- `references/pipelines.md` — input/filter/output, the `$in` variable rules, externals interop. Load when: building or debugging a pipeline.
- `references/navigating-data.md` — cell-path syntax, `get` vs `select`, missing-data `?`/`default`. Load when: accessing nested fields.
- `references/working-with-strings.md` — string formats, interpolation, `str` subcommands, comparison ops. Load when: parsing/transforming text.
- `references/working-with-lists.md` — create/update/iterate/filter/convert lists. Load when: operating on lists.
- `references/working-with-tables.md` — sort/select/merge/insert/update/rename, `#` index column, `table` render. Load when: shaping tables.
- `references/custom-commands.md` — `def`, params/flags/rest, attributes, env persistence. Load when: writing functions/commands.
- `references/aliases-operators-variables.md` — aliases, operator table+precedence, `let`/`mut`/`const`. Load when: using operators or variables.
- `references/scripts-modules-overlays-testing.md` — script `main`, modules, overlays, `std assert`. Load when: organizing/running code.
- `references/modules.md` — `use` patterns, `export`, submodules, `export-env` caveat. Load when: building a module.
- `references/environment-config.md` — `$env` scoping, `ENV_CONVERSIONS`, config files, prompts. Load when: configuring Nushell or env.
- `references/shell-runtime.md` — `^` externals, stdout/stderr/exit, hooks, background jobs. Load when: interop with external programs.
- `references/stdlib-metadata-parallel-plugins.md` — stdlib imports, metadata, `par-each`, plugins. Load when: using stdlib/parallel/plugins.
- `references/coming-from-bash.md` — Bash→Nu command table. Load when: migrating a Bash snippet.
- `references/maps-and-thinking.md` — cross-language command/operator maps + the "Thinking in Nu" mental models. Load when: understanding Nu's design or a confusing error.
