# pnpm CLI Basics

Verbatim-accurate notes from pnpm.io/pnpm-cli (pnpm v11 & 12).

## Short aliases (v11+)

- `pn` is a short alias for `pnpm`.
- `pnx` is a short alias for `pnpm dlx` (was `pnpx`).

```text
pn install
pn add express
pn build
pn test
pnx create-vue my-app
```

## Differences vs npm

- pnpm **validates all options**. `pnpm install --target_arch x64` FAILS
  (`--target_arch` is not a valid `install` option).
- Workarounds when a dependency reads `npm_config_*`:
  1. `npm_config_target_arch=x64 pnpm install`
  2. `pnpm install --config.target_arch=x64`

## Global options (all commands)

- `-C <path>`, `--dir <path>` — run as if pnpm started in `<path>`.
- `-w`, `--workspace-root` — run as if started in the workspace root.

## Command resolution

- Unknown command → pnpm searches `package.json` scripts:
  `pnpm run lint` == `pnpm lint`.
- If no script matches, runs it as a shell command:
  `pnpm eslint` (see `pnpm exec`).
- `pnx <pkg>` == `pnpm dlx <pkg>`.

## npm → pnpm equivalents

| npm | pnpm |
| --- | --- |
| `npm install` | `pnpm install` |
| `npm i <pkg>` | `pnpm add <pkg>` |
| `npm run <cmd>` | `pnpm <cmd>` |
| `npx <pkg>` | `pnx <pkg>` |

## Environment variables

- `CI` (and common build vars) makes `--frozen-lockfile` default `true`.
- `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`
  change the global store/config/data/state directories pnpm uses.
