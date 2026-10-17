# Hermes resync (sks-selfupdate companion)

Harness-specific resync paths for Hermes agents. The neutral flow lives in
`SKILL.md` step 5; read this when the target agents run Hermes.

## Tap (default)

```bash
hermes skills tap add <org>/<repo> 2>/dev/null || true
hermes skills update            # every outdated skill
hermes skills update <skill>    # one skill by name
```

`hermes skills update` takes an installed skill name — all outdated skills
when omitted — never the tap name; `--force` overwrites local edits.
Re-adding the tap (it may already exist) points it at the current repo.

## Manual copy (fallback)

```bash
cp -r skills/<skill> ~/.hermes/skills/
```

Repeat per updated skill. Resolve the real home from `$HERMES_HOME` when a
profile is active (`~/.hermes/profiles/<name>/skills/...`), never hardcode
`~/.hermes`.

## Profiles

Profiles resync in place — do not reinstall: `hermes profile update <name>`
re-pulls the distribution and refreshes the skills it ships while preserving
user data (memories, sessions, auth; config unless `--force-config`).

## Verify

`hermes skills list` shows each updated skill. `hermes skills diff` only
compares a local copy against the bundled stock copy, so for tap-installed
skills verify by reading the installed body under `$HERMES_HOME/skills/`
and confirming the new content landed.

## Pitfalls

- **Bundled vs hub-installed skills.** If a skill is bundled with Hermes, a
  manual `cp` marks it `user-modified`, which blocks future `hermes update`
  refreshes; `hermes skills reset` clears that and lets updates flow again.
  Prefer the tap/update path for bundled skills.
- **Profile-aware paths.** Local agents may run under a profile; resolve
  `$HERMES_HOME` instead of assuming `~/.hermes`.
