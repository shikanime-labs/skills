---
name: sks-delegate
description:
  "Use when handing an entire shikanime unit to the Automata account:
  authoring, commits, pushes, and gh interactions run as yorha-operator,
  never the personal shikanime identity."
version: 0.1.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - identity
      - jj
      - shikanime-labs
      - shikanime-studio
      - workflow
    related_skills:
      - sks-stack
      - sks-commit
      - sks-dev-workflow
      - sks-pr-workflow
      - sks-skill-authoring
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Delegate to Automata

Hand an ENTIRE unit of work to the Automata account: the authoring, every
commit, every push, and every `gh` interaction run as `yorha-operator` —
never the personal `shikanime` identity. Delegation is end-to-end, not a
trailer: switching only the `Co-authored-by:` while pushing under the
personal token ships the unit under the wrong account.

## When to Use

- "Delegate this to automata" / "do this unit as automata" — the unit's
  delivery is owned by the Automata account end to end.
- Delegated authoring (skills, docs, fixes) that must not carry the human
  identity on any commit, push, or gh call.

## Requirement: sks-stack comes first

Delegation rides on `sks-stack` — the unit runs in a fresh jj workspace
pinned to `main@origin`, never in the cloned checkout. Isolation first,
identity second: open the workspace, then apply the Automata overrides
inside it.

## Identity model (verified 2026-09-10)

| Plane      | gh keyring name | GitHub login    | Role                     |
| ---------- | --------------- | --------------- | ------------------------ |
| Delegation | `yorha-automata`| `yorha-operator`| commits, pushes, gh calls|
| Personal   | `shikanime`     | `shikanime`     | stays out of the unit    |

- The keyring name (`yorha-automata`) and the login (`yorha-operator`)
  DIFFER. `gh auth switch --user` takes the KEYRING name; `gh api user`
  returns the login. Verify with `gh api user` after every switch.
- The commit AUTHOR email must be the account noreply
  `243783539+yorha-operator@users.noreply.github.com` — GitHub rejects
  pushes whose commits carry a private email (GH007, verified); the
  account's `email` field is null/private. `automata@shikanime.studio`
  exists ONLY in the `Co-authored-by:` trailer (precedent #214).

## Procedure

1. **Isolate** — `sks-stack`: `jj workspace add ../<repo>.<unit> -r
   'main@origin'`; copy in ONLY this unit's files.

2. **Switch the gh account** — once per unit, before any gh call or push:

   ```bash
   gh auth switch --user yorha-automata   # keyring name
   gh api user --jq .login                # must print yorha-operator
   ```

3. **Commit as Automata** — AUTHOR email is the account noreply
   `243783539+yorha-operator@users.noreply.github.com` (GH007 rejects the
   private `automata@` on push). `jj describe` sets the message only —
   jj 0.44.0 has no `--reset-author`. Re-stamp an existing workspace
   commit with the verified recipe, then describe:

   ```bash
   JJ_USER="Automata" \
     JJ_EMAIL="243783539+yorha-operator@users.noreply.github.com" jj new
   jj squash --from @- --into @        # content moves into the env child
   jj abandon @-
   JJ_USER="Automata" \
     JJ_EMAIL="243783539+yorha-operator@users.noreply.github.com" \
     jj describe -m "<subject>" \
     -m "Co-authored-by: Automata <automata@shikanime.studio>" \
     -m "Signed-off-by: Shikanime Deva <william.phetsinorath@shikanime.studio>"
   jj log -r @ --no-graph -T 'author.email() ++ "\n"'
   # 243783539+yorha-operator@users.noreply.github.com
   ```

   Never build the restamp with `jj restore --from @- --to @` + abandon —
   that variant dropped the tree twice in a row on this machine. New
   commits (`jj new`) inherit the env automatically; the env prefix is
   per-invocation for every `jj` call.

4. **Push + gh as Automata** — the switch in step 2 covers `jj git
   push` (credential helper) and all `gh` calls. jj workspaces have no
   `.git`, so pass the repo explicitly: `gh pr create -R <org>/<repo>
   --head <org>:<branch>` — the head org is the repo OWNER (same-repo
   branch), never the gh login; the Automata credential is what
   authenticates, not the head prefix.

5. **Switch back** when the unit lands:

   ```bash
   gh auth switch --user shikanime && gh api user --jq .login
   ```

## Pitfalls

- Skipping `gh auth switch` leaves the personal `shikanime` token active —
  pushes and gh calls ship under the WRONG account while the commit author
  says Automata.
- `--user` takes the keyring name (`yorha-automata`); the login is
  `yorha-operator`. `gh auth status` lists both; `gh api user` shows which
  is active.
- `git log` / plain `git` inside the isolation workspace fails ("not a git
  repository") — use jj commands and `-R <org>/<repo>` on gh.
- A delegated PR lands into the same `main` as personal work; landing
  follows `sks-land` regardless of authoring identity.

## Verification

```bash
gh api user --jq .login                    # yorha-operator while delegating
jj log -r @ --no-graph -T 'author.email() ++ "\n"'
gh pr view <N> -R <org>/<repo> --json author,headRefName,headRefOid
```

## See also

- `sks-stack` — required isolation this skill runs on top of.
- `sks-commit` — commit envelope; here with Automata author overrides.
- `sks-dev-workflow` — the loop this delegates.
- `sks-pr-workflow` — PR side under the Automata credential.
