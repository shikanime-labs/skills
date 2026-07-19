---
name: github-issue-workflow
description: "GitHub issue lifecycle: create, edit, label, assign, and comment via gh CLI in cloud-pi-native/console."
---

# GitHub Issue Workflow

Use this skill for issue operations in `cloud-pi-native/console`.

## Create

Use French-markdown issue bodies when the repo expects it.
Use `--body-file` with a temp `.md` (write via `write_file`, then `gh issue create --body-file <file>`, then `rm`) for clean multiline bodies — avoids heredoc quoting/escaping pitfalls in shells. Keep the body to relevant content only; set labels, assignee, project, type, priority, and parent/child relationship as structured fields per `github-issue-metadata`.

### Title + label + section conventions (from `.github/ISSUE_TEMPLATE/`)
- **Feature request:** title `💡 [REQUEST] - <short title>`, label `enhancement`.
  - Body sections (mirror `FEATURE-REQUEST.yml`) use **`###` (h3) headings**, NOT `##`:
    `### Description`, `### PRs liées`, `### Issues liées`, `### Exemples simples`, `### Spécifications techniques`, `### Définition du fini` (a DoD checkbox list).
  - **Empty optional sections** must contain the literal `_No response_` (this is what the rendered template produces and what existing issues like #2307/#2250 show). Do not delete them or leave them blank.
- **Bug:** title `🐛 [BUG] - <short summary>`, label `bug`.
  - Body sections (mirror `BUG-REPORT.yml`): `Description`, `Etapes de reproduction`, `Captures d'écran`, `Logs`, `Navigateurs`, `OS`, `Version de la console impactée`, `Définition du fini`.
- When in doubt, read the template files in the local checkout — they are authoritative and already available offline. Repo convention is French-ish section headings; **English body content is acceptable** (PR bodies here are English), but when the user explicitly asks for French ("in French" / "en français" / "update in french"), translate the whole body and keep the French section headings verbatim.
- **Match existing issues, not just the template.** Before drafting structure, run `gh issue view <similar> --json body` on 1–2 recent issues of the same type to copy their exact heading style, empty-section marker (`_No response_`), and DoD list. The template YAML is the spec; the rendered issues are the ground truth.

### Verify PR scope against actual code before drafting
When an issue is "based on PR #N", **do not trust the PR description's stated scope**. The PR author's summary can understate reach (e.g. #2298 description said "ArgoCD and GitLab" but the code added `autoSync`/`suspended` to all 7 plugins: argocd, gitlab, vault, keycloak, nexus, sonarqube, harbor). Before writing the issue, grep the repo for the relevant symbols to confirm which modules/files are actually touched:
- `search_files` for the PR's new constants/flags (e.g. `AUTO_SYNC_PLUGIN_KEY`, `PLUGIN_NAME = '`) to enumerate affected plugins.
- Open one representative `*datastore.service.ts` / `*.service.ts` to confirm the recurring pattern (e.g. `getAutoSyncProjects()` + `@Cron(EVERY_HOUR)` + `syncProject()`).
Then state the verified scope in the issue so it is accurate, and flag any gap between PR description and code if material.

### Deriving structure when the API is blocked
If `mcp__aperture__GitHub_*` issue/search endpoints return `Resource not accessible by integration` (403), do NOT retry the same path. Instead:
1. Read `.github/ISSUE_TEMPLATE/*.yml` and `.github/PULL_REQUEST_TEMPLATE.md` from the local checkout to study structure/style.
2. Create the issue with the authenticated `gh` CLI (your token carries `repo`/`maintain` on this repo).

### Synthetic / non-template issues (decisions, descope, process)

No issue template matches every content type. For a decision / descope / process
issue (e.g. "reduce 9.20.1 scope"), there is no DECISION template in this repo —
reuse the **nearest** template's structure (here `FEATURE-REQUEST.yml` → `💡 [REQUEST]`
prefix). This is acceptable even when the content is a decision, not a feature.

Rules the user enforced on this class of issue:
- **Unused / non-applicable sections → literal `N/A`, not deletion, not `_No response_`.**
  The user explicitly said "set to N/A" for `Exemples simples` and `Spécifications techniques`
  that didn't apply. Keep the `###` heading so the body still mirrors the template.
  (Reserve `_No response_` for *optional* sections of a real template-driven issue; for a
  synthetic issue where a section is conceptually irrelevant, `N/A` reads cleaner.)
- **Strip PII.** No `@handles`, no real names, no emails in the issue body. The repo
  habitually @-mentions people; the user asked to remove them. Cross-link issues/PRs by
  number only (#2323, #2328), never by tagging a person.
- **Review-before-create.** For this user, draft the full title + body and STOP. Do not call
  `gh issue create` until they say "create issue" (or equivalent). They iterate on the draft
  several times (structure, PII, N/A, references). Show the draft as markdown in chat, then
  create on explicit go-ahead.
- **Labels / milestone.** A synthetic decision issue defaults to `enhancement,tech`; confirm
  the milestone (e.g. `9.20.1`) — it may not exist yet, so leave unset if unsure and let the
  user create it.

### GitHub MCP scope fallback
`mcp__aperture__GitHub_issue_write` may be denied the `issues` write scope (403 `Resource not accessible by integration`) even though PR reads via `mcp__aperture__GitHub_pull_request_read` succeed. When issue create/update is blocked on the MCP side, fall back to `gh issue create` / `gh issue edit` from the CLI — same outcome, different transport.

## Edit

When asked to "edit the ticket" about content, update the body, not just add a comment.
Confirm current state with `gh issue view <number>` first if needed.
Prefer a single focused rewrite over layered conflicting edits. If the user changes scope, re-read the latest request before replacing prior intent.

## Architectural / code-quality bugs vs UI bugs (BUG-REPORT template)

The BUG-REPORT.yml template lists UI-facing fields (`Navigateurs`, `OS`,
`Version de la console impactée`) alongside `Captures d'écran` and `Logs`.
For an **architectural / code-quality / duplication** bug (no UI, no user-facing
error), keep the template's required section structure but set the UI-only
fields to `N/A` so the body still mirrors the template and renders cleanly:

- `Captures d'écran` → `N/A (problème de conception, non visuel)`
- `Logs` → `N/A`
- `Navigateurs` / `OS` / `Version de la console impactée` → omit when the body
  is already long (they are meaningless for a server-side design defect); keep
  `Description` / `Etapes de reproduction` / `Définition du fini`, which always
  apply. Keep the French section headings verbatim.
- Applied to #2327 (`makeDisabledPluginResult` duplication in server-nestjs):
  reworded body kept `Description`, `Etapes de reproduction`, `Captures d'écran`
  (N/A), `Logs` (N/A), `Définition du fini`.

## Pin tech-debt / duplication issues to the introducing release + commit

When the issue documents duplication or a design defect, find the commit that
introduced it and cite it — this turns a vague "there's duplication" into an
actionable root cause. Recipe (run from repo root):

```bash
git describe --tags --abbrev=0          # latest release tag (HEAD may BE the release)
git log --oneline <tag>..HEAD           # often empty if HEAD == release
git show --stat <sha>                   # what the introducing commit touched
git grep -n "getAutoSyncProjects" -- 'apps/server-nestjs/src'   # enumerate dup sites
```

For #2327 the chain was: `git describe --tags --abbrev=0` → `v9.20.0`
(HEAD == release); `git show --stat 4142e0147d` revealed the autosync commit
that fanned the same `getAutoSyncProjects()` query into all 7 plugin datastores.
State the verified module/file scope in the issue and add a
**`Racine commune — release vX`** section so implementers know the fix must
centralize the duplicated code (one shared helper), not patch a single caller.
Full recipe + condensed notes: `references/issue-root-cause-recipe.md`.

## "Remark" vs body edit

- User says "update the issue with a remark" / "add a remark" → `gh issue comment <n>`
  (append a comment; leaves the structured body intact).
- User says "update the body" / "reword the body" / "follow the template" →
  `gh issue edit <n> --body "$(cat <<'EOF' ... EOF)"` (full rewrite).
Confirm the current body with `gh issue view <n> --json body` before a rewrite.

## Reframe, translate, and restructure an issue

Users iterate on issue bodies in this repo. Follow this progression when asked to
"update in french", "plain language", "expression of need", or "follow other issues' structure":

1. **Match existing issues, not just the template.** `gh issue view <n> --json body` on a
   same-type issue (e.g. #2250 for a feature request) to copy the exact `###` heading style,
   the `_No response_` empty-section marker, and the DoD checklist. The repo uses French
   section headings but English body content is acceptable unless French is explicitly asked.
2. **French translation.** When the user says "in french" / "update in french", translate the
   whole body and keep the French section headings verbatim. Keep real code identifiers
   (`autoSync`, `syncProject()`, `getAutoSyncProjects()`, `@Cron(...)`, file paths) so
   implementers can still locate the hooks.
3. **Plain-language rewrite.** Replace jargon with everyday French while preserving identifiers:
   `drapeau` → "option", `cron` → "tâche planifiée", `datastore` → "accès aux données",
   `réconciliation`/`dérive` → "synchronisation"/"écart".
4. **Expression of need (user story).** Reframe the Description as
   "En tant que <rôle>, je souhaite <capabilité> afin que <bénéfice>." (mirror #2250).
   Rewrite "Exemples simples" as operator wants ("En tant qu'opérateur, je veux…") and reduce
   "Spécifications techniques" to need-level constraints, not an implementation spec.
5. **Cross-link and restructure PRs too.** When the user wants a PR description updated to the
   repo's PR template and linked to the issue: rewrite the PR body to follow
   `.github/PULL_REQUEST_TEMPLATE.md` (French `##` sections: `Issues liées`,
   `Quel est le comportement actuel ?`, `Quel est le nouveau comportement ?`,
   `Cette PR introduit-elle un breaking change ?`, `Autres informations`), correct any
   outdated scope claims against the actual code, and link the issue number.

Verify the asserted scope against code first (see "Verify PR scope against actual code
before drafting" above) — e.g. a PR description claiming "ArgoCD and GitLab" actually touched
all 7 plugins; the issue must state the verified scope.

## Scope Change (draft PR workflow example)

A common correction is replacing a misread scope (e.g., "disable build on PR noise") with the intended one (e.g., "run build and test on draft PRs").
When this happens, preserve other requirements such as language/locale and labels, and overwrite the smallest stale section possible.

## Migration tracking

For migration issues (e.g., Fastify -> NestJS), use the French status labels from #1889 to keep consistency:

- `Migré (Code-Ready)`
- `Fait (Hors-Trafic)`
- `Fait (Trafic Actif)`

Reference the global tracking issue explicitly, e.g.:
`Issue de suivi globale : #1889 — [NestJS] Modularisation de server`.

## Scope checklist for admin-role / related migration issues

Confirm scope from the tracking issue body before creating. Typical scope:
- `POST /api/v1/auth` (Sync session)
- `GET /api/v1/admin/roles`

For auth-related migrations, preserve the repo’s structure constraint:
- `user/` and `project/` files must keep symmetric patterns (same class anatomy, method names, naming conventions).
- Add this note verbatim to the new issue to avoid implementation drift.

Linking isn’t automatic — include the tracking issue number in the new issue body.

## Triage

- Assignee: add with `gh issue edit <number> --add-assignee <login>`
- Labels: add with `gh issue edit <number> --add-label "<name>"`
- Common labels in this repo: `bug`, `tech`, `to refine`
- If the project uses GitHub issues default French phrasing, keep body headings minimal and obvious: `Contexte`, `Comportement observé`, `Impact`, `Étapes de reproduction`, `Informations complémentaires`.

Board/project association:
- Requires `project` token scope.
- Use `gh issue edit <number> --add-project "<title>"`.
- Preferred board for this repo is `Socle` (`projects/2`).
- Parent linkage is not automatic; include the parent issue number in the new issue body.

Constraints:
- Run commands from the repo root.
- After `gh issue create`, provide the issue URL and stop unless further edits were requested explicitly.