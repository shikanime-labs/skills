# Vitest CLI

Verbatim-accurate notes from vitest.dev/guide/cli (current major).

## Commands

- `vitest` — start in cwd; WATCH mode in dev, RUN mode in CI / non-TTY
  automatically.
- `vitest run` — single run, no watch.
- `vitest watch` — watch for changes (alias `vitest dev`).
- `vitest related <files...>` — run only tests covering given source files
  (static imports only; relative to root). Pair with `--run` for lint-staged:
  `'*.{js,ts}': 'vitest related --run'`.
- `vitest bench` — run benchmark tests only.
- `vitest init <name>` — setup config; currently `vitest init browser`.
- `vitest list` — print matching tests (ignores `reporters`); `--json`,
  `--filesOnly`, `--static-parse` (Vitest 4.1+) to parse without running.
- Filter arg: `vitest foobar` runs files whose path contains `foobar`
  (substring only, no regex/glob unless the shell pre-expands).
- Filename + line: `vitest basic/foo.test.ts:10` (full filename required;
  ranges like `:10-25` NOT supported; multiple `:10, :25` OK).

## Option conventions

- CamelCase and kebab-case both work (`--passWithNoTests` ==
  `--pass-with-no-tests`). `--reporter dot` == `--reporter=dot`.
- Array options: pass repeatedly (`--reporter=dot --reporter=default`).
- Boolean negation: `--no-api` == `--api=false`.

## Key CLI options

- `-r, --root <path>` — root path.
- `-c, --config <path>` — config file.
- `-u, --update [type]` — update snapshot (boolean|"new"|"all"|"none").
- `-w, --watch` — watch mode.
- `-t, --testNamePattern <pattern>` — run tests whose full name matches regexp.
- `--dir <path>` — base dir to scan for tests.
- `--ui` / `--open` — enable / auto-open the UI.
- `--api.port [port]` (default `51204`), `--api.host`, `--api.strictPort`,
  `--api.allowExec`.
- `--shard=<index>/<count>` — split suite into `count` parts, run `index` part
  (e.g. `--shard=1/3`). Cannot combine with `--watch`.
- `--changed [ref]` — run only tests for changed files. No value → uncommitted
  changes; `--changed HEAD~1`, a commit hash, or a branch name also work.
  Pairs with `forceRerunTriggers` to rerun the whole suite on certain changes.
- `--merge-reports [dir]` — merge blob reports in `.vitest-reports` (or given
  dir); use any reporter except `blob`.
- `--reporter=<name>` (e.g. `dot`, `default`, `blob`, `junit`).
- `--coverage` — enable coverage (provider configured in `test.coverage`).
- `--no-color`, `--inspect-brk` are the exceptions that don't support kebab.

## Shell autocompletions

- `source <(vitest complete zsh)` (add to `~/.zshrc`); package-manager
  completions (`pnpm vitest <Tab>`) via @bomb.sh/tab.
