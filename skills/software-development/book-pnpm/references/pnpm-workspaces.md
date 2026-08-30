# pnpm Workspaces

Verbatim-accurate notes from pnpm.io/workspaces and /package_json (v11 & 12).

## Workspace setup

- A workspace requires a `pnpm-workspace.yaml` at the repo root.
- Since v11, settings moved OUT of the `pnpm` field in `package.json` into
  `pnpm-workspace.yaml` (the `pnpm` field is no longer read).

## workspace: protocol

- `workspace:*` / `workspace:~` / `workspace:^` / `workspace:<range>` pins a
  dependency to a LOCAL workspace package; pnpm refuses to resolve elsewhere.
- A bare `workspace:` is treated as `workspace:*`.
- Before publish, `workspace:` specs are converted to real version ranges
  (e.g. `workspace:*` → `1.5.0`), so published packages work for consumers.
- Aliases: `"bar": "workspace:foo@*"` → published as `"bar": "npm:foo@1.0.0"`.
- Relative path: `"foo": "workspace:../foo"`.

## Workspace config keys (pnpm-workspace.yaml)

- `linkWorkspacePackages` — auto-link matching local packages.
- `injectWorkspacePackages`, `dedupeInjectedDeps`, `preferWorkspacePackages`,
  `sharedWorkspaceLockfile`, `saveWorkspaceProtocol`.
- `includeWorkspaceRoot` — also run recursive commands on the root project.
- `ignoreWorkspaceCycles` — downgrade cycle error to a warning.
- `disallowWorkspaceCycles` — fail install on cycles.
- `failIfNoMatch` — non-zero exit when `--filter` matches nothing.

## Release workflow

- No built-in versioning. Use [changesets](https://github.com/changesets/changesets)
  or [Rush](https://rushjs.io/).

## Troubleshooting

- Cyclic workspace dependencies produce a warning; topological script order is
  NOT guaranteed with cycles. Inspect `dependencies`/`optionalDependencies`/
  `devDependencies`.

## package.json fields relevant to workspaces

- `engines`: `{ "node": ">=10", "pnpm": ">=3" }` — advisory unless
  `engineStrict`; errors during local dev if pnpm version mismatches.
- `engines.runtime` (v10.21.0): `{"name":"node","version":"^24.11.0","onFail":"download"}`
  — pnpm auto-installs the runtime for CLI apps / postinstall.
- `devEngines.runtime` (v10.14): node/deno/bun with `onFail: download`; pinned
  in lockfile; scripts use the local runtime. Bare `node` from inside the
  project follows the pin since v12.0.0-rc.2 (off: `globalShims` setting or
  `PNPM_SHIM_BYPASS=1`).
- `devEngines.packageManager` (v11): supports version ranges, recorded under
  `packageManagerDependencies` in `pnpm-lock.yaml`.
- `dependenciesMeta.<dep>.injected: true` — install a workspace dep as a hard
  linked copy in the virtual store instead of a symlink; lets different
  consumers resolve different peer deps (e.g. `react@16` vs `react@17`).
- `publishConfig`: `directory` (publish a subdir), `linkDirectory` (default
  `true`), `executableFiles` (extra +x files in archive).
