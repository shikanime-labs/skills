# Custom Commands (Nushell)

Source: `book/custom_commands.html`. `def` defines first-class commands (in `help`, parsed for type errors, usable in pipelines).

## Define / call

```nu
def greet [name] { $"Hello, ($name)!" }
greet "World"                       # => Hello, World!
```

- **Implicit return**: value of the final expression is the return value. No `return`/`echo` needed.
- `return <val>` for early return. `ignore` to suppress a trailing value (e.g. `each {...} | ignore`).
- `for`/some statements return `null` (use `each` to return a list).

## Parameters

- Positional (space/comma/linebreak separated): `def g [a b] {...}`. Required by default.
- Optional: `def g [name?: string] {...}` — body var is `null` when omitted; access WITHOUT `?`.
- Default value (also optional): `def g [name = "Nushell"] {...}`; combine with type `def c [age: int = 18] {...}`.
- Types: `any, binary, bool, cell-path, closure, datetime, duration, filesize, float, glob, int, list, nothing, range, record, string, table`. Plus shapes `number` (int|float), `path`, `directory`, `error`. Unannotated = `any`. Mismatch is a **parser** error (real-time highlight).
- Flags: `--age: int`; shorthand `--age (-a): int` (var always `$age`, not `$a`). Switch flag `--caps` => `true`/`false`. `greet X --caps=false` (NOT `--caps false` — that becomes a positional!). Dashed flags => `$all_caps` (dash→underscore). Boolean annotation on flag NOT allowed.
- Rest: `def multi-greet [...names: string] {...}` collects into `$names` list; can pair with required positional `def vip-greet [vip: string, ...names: string] {...}`.

## Naming

- Valid: `greet`, `get-size`, `my command`, `命令`, `😊`. Numbers/filesizes/caret/hash as names NOT allowed; `-a`/`{foo}`/`(bar)` not callable.
- `def` is parse-time: name cannot be a var/const. Convention: `-` to separate words.
- Subcommands via space: `def "str mycommand" [] {...}` => `str mycommand`.

## Attributes

- `@deprecated` (optional text) => warning on use. `@deprecated "Use vip-greet."`
- `@category "label"` => label in `scope commands`/`help`.

## Environment / directory persistence

- Normal `def` scopes env changes; caller unaffected.
- `def --env` / `export def --env` (modules) preserves env on caller side. Needed for `cd` persistence too (`def --env go-home [] { cd ~ }`).
- Persist: put in `config.nu`, a sourced file, or an imported module.
