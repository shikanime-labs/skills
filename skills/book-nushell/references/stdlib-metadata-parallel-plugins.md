# Standard Library, Metadata, Parallelism, Plugins (Nushell)

Source: `book/standard_library.html`, `book/metadata.html`, `book/parallelism.html`, `book/plugins.html`.

## Standard Library (`book/standard_library.html`)

- Loaded into memory at startup (not auto-imported). `nu --no-std-lib` disables (faster `nu -c`/`nu -n`).
- Import via `use std/...` (slash form loads ONLY that submodule — fastest). Avoid `use std *` and `use std <submodule>` in scripts (loads whole lib).
- Submodule imports:
  - `use std/assert` (assert + subcommands), `use std/bench`, `use std/dirs`, `use std/input`, `use std/help`, `use std/iters`, `use std/log` (log warning/info/...), `use std/math` (constants `$math.E`), `use std/util "path add"`.
  - `use std/dt *`, `use std/formats *` (to/from formats), `use std/math *` ($E etc.), `use std/xml *`.
- `view files | ... | where { view span ... =~ 'use\W+std[^/]' }` finds slow `use std` in startup.
- `std-rfc` = candidate staging module (PR there to propose additions).

## Metadata (`book/metadata.html`)

- Values carry metadata (currently `span` {start,end} = source location, used for error underlines).
- `metadata (open x)`; `metadata (...) | get span`.
- Custom: `"data" | metadata set { merge {custom_key: "v"} }`.
- HTTP: all http commands attach response metadata: `http get url | metadata | get http_response.status`.

## Parallelism (`book/parallelism.html`)

- `par-` prefixed companions to serial commands. `par-each` runs block per element in parallel (immutable/scoped by design).
- Example: `ls | where type==dir | par-each {|row| {name:$row.name, len:(ls $row.name|length)} }` (6ms vs 21ms each).
- Order is non-deterministic (hardware threads); sort after if order matters (`| sort-by name`).
- Scoped env lets you `cd` in parallel branches.

## Plugins (`book/plugins.html`)

- Communicate via `nu-plugin` protocol (versioned — must match Nushell version; update on Nu upgrade).
- Lifecycle: install -> `plugin add <file>` (filename must start `nu_plugin_`) -> `plugin use <name>` (without prefix/ext) or restart. Registry `$nu.plugin-path`. `plugin list`, `plugin stop <name>`, `plugin rm <name>`.
- Core plugins: `polars` (DataFrames), `formats` (EML/ICS/INI/plist/VCF), `gstat` (git status), `query` (SQL/XML/JSON/HTML), `inc` (semver increment).
- Search paths: `const NU_PLUGIN_DIRS` (immediate) / `$env.NU_PLUGIN_DIRS` (next parse). Quickstart: `const NU_PLUGIN_DIRS = [($nu.current-exe | path dirname) ...$NU_PLUGIN_DIRS]`.
- GC: auto-stops idle plugins (default 10s). Config `$env.config.plugin_gc = { default: {enabled, stop_after}, plugins: {gstat: {stop_after: 1min}} }`.
- `plugin use` is a parser keyword (evaluated first) — can't `add`+`use` in one script; use `nu --plugins '[...]'`. Dev: plugins print to stderr for debug.
