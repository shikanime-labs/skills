# skctl

Wrap the mechanical operations the `sks-*` / `cpn-*` skills used to carry as
bare shell scripts behind one tested CLI. Agents run it from anywhere:

```bash
nix run github:shikanime-labs/skills#skctl -- <command> [args]
```

## Commands

| Command | Script it replaces | Purpose |
| --- | --- | --- |
| `next-milestone BASE_TAG` | `cpn-release-patch/scripts/next-milestone.sh` | `v9.24.4` → `9.24.5` |
| `milestone-number REPO TITLE` | `cpn-release-patch/scripts/milestone-number.sh` | milestone number, or exit 1 |
| `fetch-backport-set REPO MILE_NUM [OUTFILE]` | `cpn-release-patch/scripts/fetch-backport-set.sh` | ordered merge-commit SHAs of a milestone's merged PRs |
| `verify-backport BASE_TAG TIP EXPECTED` | `cpn-release-patch/scripts/verify-backport.sh` | count / conflict / tree-parity check |
| `gc-discover [REPO_DIR]` | `sks-gc/scripts/discover.sh` | GC candidates: dangling bookmarks + skill workspaces (dry-run) |
| `discover-metadata REPO` | `sks-issue-triage/scripts/discover-metadata.sh` | every triage-relevant value a repo offers |

Output parity with the replaced scripts is preserved; pure logic (version
derivation, line filtering) carries unit tests.

## Develop

```bash
cargo test
cargo clippy --all-targets
```
