# Hermes resync (sks-update companion)

Harness-specific resync paths for Hermes agents. The neutral flow lives in
`SKILL.md` step 5; read this when the target agents run Hermes.

## Tap (default)

```bash
hermes skills tap add <catalog-tap> 2>/dev/null || true
hermes skills update <catalog-tap>
```

`hermes skills update` refreshes installed hub/tap skills; `--help` lists the
flags. Update the tap as a whole for a full pass, or name the skill path to
update one.

## Manual copy (fallback)

```bash
cp -r skills/<skill> ~/.hermes/skills/
```

Repeat per updated skill. Resolve the real home from `$HERMES_HOME` when a
profile is active (`~/.hermes/profiles/<name>/skills/...`), never hardcode
`~/.hermes`.

## Profiles

Profiles resync the same way: install the distribution with
`hermes profile install --name <name> --force profiles/<name>`.

## Verify

`hermes skills list` shows each updated skill and `hermes skills diff <skill>`
(or reading the file) shows the new body.

## Pitfalls

- **Bundled vs hub-installed skills.** If a skill is bundled with Hermes, a
  manual `cp` marks it `user-modified`, which blocks future `hermes update`
  refreshes; `hermes skills reset` clears that and lets updates flow again.
  Prefer the tap/update path for bundled skills.
- **Profile-aware paths.** Local agents may run under a profile; resolve
  `$HERMES_HOME` instead of assuming `~/.hermes`.
