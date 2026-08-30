# pnpm install / add / run

Verbatim-accurate notes from pnpm.io/cli/{install,add,run} (v11 & 12).

## pnpm install (alias `i`)

Installs all dependencies. In a workspace, installs every project; set
`recursive-install: false` to disable. In CI, fails if the lockfile needs an
update.

TL;DR:

| Command | Meaning |
| --- | --- |
| `pnpm i --offline` | Install from store only |
| `pnpm i --frozen-lockfile` | `pnpm-lock.yaml` not updated |
| `pnpm i --lockfile-only` | Only `pnpm-lock.yaml` updated |
| `pnpm i --dry-run` | Preview changes, write nothing |

Filtering options:

- `--prod`, `-P` — skip `devDependencies`.
- `--dev`, `-D` — install only `devDependencies`.
- `--no-optional` — skip `optionalDependencies`.
- `--no-runtime` (v11.1.0) — skip runtime entries (e.g. Node via
  `devEngines.runtime`); lockfile untouched so frozen installs still validate.
- `--no-lockfile` — don't read/generate `pnpm-lock.yaml`.
- `--lockfile-only` — update lockfile + manifest, nothing to `node_modules`.
- `--dry-run` (v11.8.0) — full resolution, report only; exits 0 even when a
  real install would update the lockfile. Cannot be used with a pnpr server.
- `--fix-lockfile` — auto-fix broken lockfile entries.
- `--update-checksums` (v11.4.0) — refresh locked tarball integrity from the
  registry. By default since v11.4.0 an integrity mismatch is a HARD failure
  (`ERR_PNPM_TARBALL_INTEGRITY`); `--force`/`pnpm update` do NOT bypass it.
- `--frozen-lockfile` — default `true` in CI; fails if lockfile out of sync or
  absent.
- `--force` — refetch store, recreate lockfile/modules, install all optional deps.
- `--offline` / `--prefer-offline` — store-only / skip staleness checks.
- `--shamefully-hoist`, `--ignore-scripts`, `--filter <selector>`,
  `--cpu=<name>`, `--os=<name>`, `--libc=<name>` (v10.14.0, native module overrides).
- `--reporter=<default|append-only|ndjson|silent>`.
- `--resolution-only` — pnpm 11 ONLY (removed in 12; use `pnpm peers check`).

## pnpm add <pkg>

By default installs as a production dependency.

TL;DR:

| Command | Meaning |
| --- | --- |
| `pnpm add sax` | `dependencies` |
| `pnpm add -D sax` | `devDependencies` |
| `pnpm add -O sax` | `optionalDependencies` |
| `pnpm add -g sax` | global |
| `pnpm add sax@next` | from `next` tag |
| `pnpm add sax@3.0.0` | exact version `3.0.0` |

Options:

- `--save-prod/-P`, `--save-dev/-D`, `--save-optional/-O`,
  `--save-exact/-E` (exact version, not semver range),
  `--save-peer` (adds to `peerDependencies` + dev install),
  `--save-catalog` / `--save-catalog-name <name>` (v10.12.1, catalogs),
  `--config` (v10.8.0, configDependencies).
- `--ignore-workspace-root-check` / `-w` — required to add a dep to the root
  workspace package (otherwise fails).
- `--global/-g` — each package isolated; comma-list shares one install.
- `--workspace` — add only if found in the workspace.
- `--allow-build=<pkgs>` (v10.4.0) — allowlisted postinstall scripts; also
  writes them to `allowBuilds` in `pnpm-workspace.yaml`.
- `--filter <selector>`.

Adding a package manager / runtime (v12.0.0-rc.6+):

- `pnpm add yarn@4` writes `"packageManager": "yarn@4.18.0"` (records the PM,
  not an npm package).
- `pnpm add node@22` installs that Node release globally.
- `pnpm add bun@runtime:1.3.0` records the runtime; bare `pnpm add bun` sets it
  as the package manager.

## pnpm run <script> (alias `run-script`)

Runs a `package.json` script. Every script is also aliased as a pnpm command
(`pnpm watch`). `node_modules/.bin` and the workspace-root `node_modules/.bin`
are on `PATH`.

Multiple scripts via regex (quoted, slash-wrapped):

```text
pnpm run "/^watch:.*/"      # all scripts starting with watch:
pnpm run "/build:.*/"       # also matches prebuild:web (not anchored)
```

- Matching is not anchored; use `^`/`$` for exact prefix.
- Matched scripts run in lexicographical order (deterministic).
- `--sequential` / `-s` (v11.14.0) runs them one by one (`-s` here ==
  `--sequential`; everywhere ELSE `-s` == `--reporter=silent`).
- Regex flags unsupported: `/^build:.*/i` fails with
  `ERR_PNPM_UNSUPPORTED_SCRIPT_COMMAND_FORMAT`.

Options:

- `--recursive/-r` — run from each package's scripts; dependency-aware task
  graph by default (see `tasks` setting).
- `--if-present` — don't fail if script undefined.
- `--no-bail` — continue after a failure (still non-zero exit if any failed).
- `--parallel` — no sorting/concurrency, prefixed streaming output.
- `--stream`, `--aggregate-output` (CI logs), `--resume-from <pkg>`,
  `--dry-run` (recursive only; topological order), `--json` (with --dry-run),
  `--report-summary` (writes `pnpm-exec-summary.json`).

Lifecycle: `pre<name>` / `post<name>` auto-run (`pnpm prefoo && pnpm foo &&
pnpm postfoo`); controlled by `enablePrePostScripts` setting.
