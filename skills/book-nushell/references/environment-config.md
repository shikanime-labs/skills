# Environment & Configuration (Nushell)

Source: `book/environment.html`, `book/configuration.html`.

## Environment (`book/environment.html`)

- `$env` is a record of all env vars; any type allowed. Case-INSENSITIVE: `$env.PATH`/`Path`/`path` all equal (use `$env | get --sensitive` for case-sensitive).
- Set: `$env.FOO = 'BAR'`; `load-env { BOB: "FOO", JAY: "BAR" }`; one-shot `FOO=BAR $env.FOO`; `with-env { FOO: BAR } { ... }`.
- Read: `$env.FOO`; unset-safe `$env.FOO?` (=> null) then `| default "BAR"`; or `"FOO" in $env`.
- Scoped: set only in current block + children. `cd` = setting `$env.PWD` (same scoping).
- `def --env` / `export def --env` to persist changes to caller.
- Remove: `hide-env FOO` (scoped).
- `ENV_CONVERSIONS`: record mapping var -> `{from_string: <closure>, to_string: <closure>}`. Converts string<->value on startup (from_string) and before running externals (to_string). `PATH` auto-converted to list. Merge, don't overwrite: `$env.ENV_CONVERSIONS = $env.ENV_CONVERSIONS | merge {...}`.

## Configuration (`book/configuration.html`)

- Files loaded in order: `env.nu` -> `config.nu` -> `$nu.vendor-autoload-dirs/*.nu` -> `$nu.user-autoload-dirs/*.nu` -> `login.nu` (login shell only). Stored in `$nu.default-config-dir` (macOS `~/Library/Application Support/nushell`, Linux `~/.config/nushell`, Win `AppData/Roaming/nushell`).
- `config nu` opens config.nu; `config env` opens env.nu (needs `$env.config.buffer_editor` or `$EDITOR`/`$VISUAL`).
- Settings live in `$env.config` record. Assign KEYS, not whole record (overwriting resets others): `$env.config.show_banner = false`. Nested records: set all values when overwriting.
- PATH: `$env.path ++= ["~/.local/bin"]`. Stdlib helper: `use std/util "path add"; path add "~/.local/bin"` (prepends). Use `path join` for safety.
- Prompts: `$env.PROMPT_COMMAND`, `PROMPT_COMMAND_RIGHT`, `PROMPT_INDICATOR`, `PROMPT_INDICATOR_VI_NORMAL/INSERT`, `PROMPT_MULTILINE_INDICATOR` (string | closure | null). Transient variants `TRANSIENT_PROMPT_*`.
- `ENV_CONVERSIONS` documented as `$env.config` sibling; merge for new conversions (e.g. XDG_DATA_DIRS).
- `$nu` constant (parse-time): `$nu.default-config-dir`, `$nu.data-dir`. `source`/`use` need parse-time args => use `$nu.*` constants, not runtime vars. `NU_LIB_DIRS` constant usable in config.nu.
- Launch flags: `nu -c "..."` (no config files/repl), `nu -l` (login), `nu -n` (no config), `nu --no-std-lib`, `nu --config <f>`, `nu --env-config <f>`, `nu <script>`.
- XDG dirs (`XDG_CONFIG_HOME`/`XDG_DATA_HOME`/`XDG_DATA_DIRS`) set BEFORE launch; point at the dir ABOVE the `nushell` subdir.
