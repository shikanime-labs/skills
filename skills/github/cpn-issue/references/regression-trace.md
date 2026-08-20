# Regression rationale trace (cloud-pi-native/console)

When an issue requires explaining *why* the code behaves a certain way (root
cause for a bug report), trace the change rather than guessing. Console commits
frequently ship behavior changes with only a `Signed-off-by` + `Change-Id` and
no prose "why", so the git history + PR/issue chain is the only source of truth.

## Recipe

1. **Pickaxe** the suspicious value/symbol across history:
   `git log --oneline -S "<string>" -- <path>`
(e.g. `-S "project.owner.email" --
     apps/server-nestjs/src/modules/sonarqube/sonarqube.service.ts`)
2. **Blame** the exact line: `git blame -L <line>,<line> <file>` → commit hash +
  author + date.
3. **Show** the commit: `git show <hash>` for the diff + message. Note that the
   message often omits the rationale.
4. **Find the PR**: `gh pr list --repo cloud-pi-native/console --search "<hash>"
  --state all`
   (or `gh search prs --repo cloud-pi-native/console "<title fragment>"`).
5. **Follow the linked issue**: `gh pr view <N> --json body` → parse
   `Issues liées: #XXXX`, then `gh issue view XXXX --json body,comments`.
6. **Verify the link is real.** PRs in this repo are frequently linked to an
   issue that describes a *different* change. If the linked issue doesn't
   describe your change, the rationale is **unrecorded** — say so explicitly
   rather than assuming the linked issue explains it.

## Worked example — SonarQube SSO collision (condensed)

- Symptom: SonarQube SSO login → "already associated with another authentication
  method".
- `git log -S "project.owner.email" --
  apps/server-nestjs/src/modules/sonarqube/sonarqube.service.ts` → `44d6d2700a`.
- `git blame` line 209 → same commit (W. Phetsinorath, 2026-08-04).
- The change replaced the legacy fake email `${slug}@${slug}` with
  `project.owner.email`
  on a `local: true` robot account → the owner's real email became bound to a
  `local` SonarQube identity, colliding with their SSO login.
- PR #2403 ("use project owner email") → linked issue #2400, which is a *Vault
  GITLAB secret-path bug* — **unrelated and mis-associated**. No prose rationale
  for the email change exists anywhere in code, spec, or docs.
- Fix direction: revert the robot email to a unique per-project fake
(`${slug}@${slug}`), matching the legacy plugin `plugins/sonarqube/src/user.ts`.
