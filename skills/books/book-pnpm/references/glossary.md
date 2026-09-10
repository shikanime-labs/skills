# pnpm Glossary & Constraints

Shared terms and version/compat constraints for pnpm.

## Version constraints

- **Node.js**: pnpm v11/12 → 20.19+/22.12+.
- **pnpm v11+**: settings moved from `package.json`'s `pnpm` field into
  `pnpm-workspace.yaml`.
- **pnpm v12**: drops `--resolution-only` (use `pnpm peers check`);
  `--no-runtime` added (v11.1.0); `devEngines.runtime` pin applies to bare
  `node` from inside the project (v12.0.0-rc.2+).

## Key terms

- **frozen-lockfile**: `--frozen-lockfile` is TRUE by default in CI for pnpm
  (any `CI`/build env var). A mismatch with the manifest fails the install.
  `--lockfile-only` updates ONLY the lockfile; `--no-lockfile` skips it.
- **workspace: protocol**: pnpm-only dependency specifier binding a dep to a
  local workspace package; rewritten to a real version range on publish.
- **pnpm run -s**: within `pnpm run`, `-s` == `--sequential` (run scripts one
  by one); in ALL other pnpm commands `-s` == `--reporter=silent`.

## Naming collisions to avoid

- `pnpm <script>` vs `pnpm <command>`: same name as a built-in pnpm command
  shadows the script alias.
