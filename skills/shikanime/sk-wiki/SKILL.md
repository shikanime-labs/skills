---
name: sk-wiki
description:
  "Document a shikanime project on its GitHub wiki: seed the structure (internal
  ops + optional user-facing docs), edit pages through a reviewable in-repo
  source, and sync to the <repo>.wiki.git remote. Mirrors Longhorn internal-ops
  / PyTorch mirror / Kubernetes ownership patterns."
version: 0.2.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, wiki, documentation, shikanime-labs, shikanime-studio]
    related_skills: [sk-pr, sk-issue, sk-land]
---

# Shikanime Org Wiki

GitHub wiki = knowledge base, two zones:

- **Internal ops** (always): runbooks, architecture, ops, release/QA, decisions.
- **User-facing docs** (only if no docs site exists): guide, tutorials, FAQ,
  reference.

## When to Use

- "Set up the wiki for <repo>."
- "Add a runbook / architecture / ops page to the <repo> wiki."
- "Add a user guide / tutorial / FAQ / how-to-use to the <repo> wiki."
- "Sync the in-repo wiki source to the live wiki."

## Doctrine

1. **Two zones, one source.** Internal ops always in the wiki; user docs only
   when no site owns them. Both edited in-repo and synced.
2. **Edit in-repo, sync to wiki.** Source under `wiki/` (or `wiki` branch),
   reviewed via PR, then pushed to `<repo>.wiki.git`. Never edit the live wiki
   by hand when an in-repo source exists.
3. **Every page has one owner + a purpose.** Unowned pages rot.
4. **Sidebar is the index.** `_Sidebar.md` is nav; update on every add/move.
   `Home.md` is the landing page naming each section's zone.

## Procedure

### 1. Locate or seed

Repo `R` (`OWNER/REPO`) in `shikanime-labs/` or `shikanime-studio/`. Confirm
in-repo source:

```bash
# Preferred: a `wiki/` directory at repo root, or a `wiki` branch.
jj file list wiki/ 2>/dev/null
gh api repos/"$R"/branches --jq '.[].name' | grep -x wiki || true
```

Neither exists? Seed via issue → PR (`sk-issue` / `sk-pr`): create
`wiki/Home.md` + `wiki/_Sidebar.md`. Don't push to `.wiki.git` until
review-approved.

### 2. Seed structure (first time only)

Create `wiki/` with `Home.md`, `_Sidebar.md`, plus:

- **Internal:** Architecture, Development, Runbook, Troubleshooting, Releases,
  Decisions
- **User (only if no docs site owns them):** User-Guide, Tutorials, FAQ,
  Reference

Head each page:
`<!-- owner: <team-or-person> | zone: internal|user | purpose: <one line> -->`

### 3. Add or edit a page

Edit the Markdown in `wiki/`. One page = one concern. Link related pages with
`[[Other-Page]]`.

- Internal → add under the internal section of `_Sidebar.md`.
- User → add under the user section; if the content lives on a docs site, link
  from `Home.md` instead of duplicating.

### 4. Sync to the live wiki

Wiki is a separate remote `<repo>.wiki.git`. Mirror `wiki/` into it
(`_Sidebar.md`/`_Footer.md` are special).

```bash
# After the in-repo change is merged/reviewed:
WIKI="https://github.com/$R.wiki.git"
TMP="$(mktemp -d)"
# The wiki is a separate repo — clone it as its own jj workspace.
jj git clone "$WIKI" "$TMP" 2>/dev/null || git clone "$WIKI" "$TMP"
# Copy pages (flatten wiki/ -> wiki root; keep _Sidebar.md / _Footer.md names)
rsync -a --exclude='.jj' --exclude='.git' wiki/ "$TMP/"
cd "$TMP"
jj file list  # confirm the pages landed
jj describe -m "wiki: sync from repo source"
jj git push --remote origin --allow-new
cd /; rm -rf "$TMP"
```

Clone `.wiki.git` as its own jj workspace (clone → edit → `jj describe` →
`jj git push`); `git clone` is the plain-git fallback. Automate in CI on `wiki/`
changes; `actions/github-wiki-action` mirrors `wiki/`.

### 5. Verify

```bash
gh api repos/"$R"/wiki --jq '.[].title'   # list live pages
# Confirm the new/updated page appears and _Sidebar renders the link.
```

## Pitfalls

- **Editing the live wiki by hand** — bypasses review, diverges from source.
- **Duplicating a docs site** — link from the wiki; don't fork content.
- **Stale sidebar** — a page missing from `_Sidebar.md` is unreachable; update
  on every add/move.
- **Unowned pages** — add the owner/zone/purpose comment or the page rots.
- **Wiki size limit** — soft cap 5,000 files; larger docs use GitHub Pages.
- **Wrong remote** — `<repo>.wiki.git` is a separate repo, not the code repo.

## See also

- `sk-issue` / `sk-pr` — in-repo wiki source still goes through issue → PR.
- `sk-land` — land the wiki-source PR before syncing.
