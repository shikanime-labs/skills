---
name: sks-sudo
description:
  "Use when a gh operation must run under a different org identity: lock,
  switch to the agent account, confirm the flip, restore the operator."
version: 0.3.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - gh-cli
      - identity
    related_skills:
      - sks-dev
      - sks-pr
      - sks-land
      - sks-skill-authoring
platforms:
  - linux
  - macos
  - windows
---

# Identity Switch

Run a scoped `gh` operation under a different org identity. `gh` has no
`GH_USER` selection (<https://github.com/cli/cli/issues/12145>); `gh auth
switch` is the only mechanism, and it is global — it rewrites the shared
config under every concurrent `gh` call on the machine. Never switch outside
the identity lock, never leave the flip past the restore. Account inventory
and the default identity live in `references/shikanime.md`.

## When to Use

- A push, PR post, comment, review, or API read must land under the agent
  identity while the operator identity is active — or the reverse.
- A workflow skill instructs an identity switch, e.g. `sks-land` Gate 2.

Not for git/jj commit identity — `gh auth switch` does not touch
`user.email` or signing config. Token-only reads use
`gh auth token --hostname github.com --user <identity>` without switching.

## Procedure

1. **Acquire the identity lock** — a switched section without it races every
   concurrent `gh` call:

   ```bash
   L=/tmp/gh-identity.lock
   n=0
   until mkdir "$L" 2>/dev/null; do
     n=$((n + 1))
     [ "$n" -lt 60 ] || { echo "BLOCKED: identity lock held"; exit 1; }
     sleep 0.5
   done
   cleanup() {
     gh auth switch --hostname github.com --user <default identity>
     rmdir "$L" 2>/dev/null
   }
   trap cleanup EXIT
   ```

2. **Record the active identity** — restoration is checked, not guessed:

   ```bash
   gh auth status --hostname github.com
   ```

3. **Switch explicitly, verify the flip, operate:**

   ```bash
   gh auth switch --hostname github.com --user <target identity>
   gh api user --jq .login
   # ... the scoped operation, and only that ...
   ```

4. **Restore immediately and verify** — the trap is crash insurance, not the
   excuse:

   ```bash
   gh auth switch --hostname github.com --user <default identity>
   gh auth status --hostname github.com
   ```

## Pitfalls

- **Concurrent switched sections are the incident class.** If step 1 reports
  BLOCKED, another switched section is live — wait, never bypass the lock.
- **Success lines are not proof.** Only `gh api user` proves the flip and
  `gh auth status` proves the restore.
- **`GH_ACCOUNT=` and inline `GH_TOKEN=` do not cover git.** The HTTPS
  credential helper follows the ACTIVE account; prefer a locked switch when
  git operations ride along.
- **Per-account `GH_CONFIG_DIR` dirs would drop the lock entirely**, but the
  shared keyring does not yield tokens to a copied `hosts.yml` —
  bootstrapping one needs an interactive `gh auth login` per account. Ask
  the operator before relying on it.

## Verification

```bash
gh auth status --hostname github.com   # active account is the expected one
```

## See also

- `sks-land` — Gate 2 approver posting; the canonical switch consumer.
- `sks-pr` — push identity rules; pushes go to `origin` under the agent
  identity.
- `sks-dev` — the dev loop that scopes when a switch is warranted.
