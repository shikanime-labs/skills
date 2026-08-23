---
name: sk-wiki
description:
  "Document a shikanime project on its GitHub wiki: seed the structure (internal
  ops + optional user-facing docs), edit pages through a reviewable in-repo
  source, and sync to the <repo>.wiki.git remote. Mirrors Longhorn internal-ops
  / PyTorch mirror / Kubernetes ownership patterns."
version: 0.2.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [github, wiki, documentation, shikanime-labs, shikanime-studio]
    related_skills: [sk-pr, sk-issue, sk-land]
---

# Shikanime Org Wiki

Maintain a GitHub wiki as the project's knowledge base. It hosts two zones:

- **Internal ops** (always) — development runbooks, architecture intent,
  operational procedures, release/QA state, decisions, tribal knowledge.
- **User-facing docs** (when the repo has no dedicated docs site) — user guide,
  tutorials, FAQ, reference. Avoid duplicating a docs site that already exists.

Modeled on how large projects run their wikis:

- **Longhorn** — wiki carries internal operations (dev, QA, release, project
  management); user documentation lives on a dedicated site. We copy the split:
  keep user docs out of the wiki _only if_ a docs site already owns them.
- **PyTorch** — the wiki git remote is a _mirror_. Source content is edited in a
  reviewable repo (PR + CI), then synced to `<repo>.wiki.git`. We copy this so
  wiki content gets review instead of ad-hoc web edits.
- **Kubernetes** — contributor-facing docs follow a style guide, assign an
  owner, and go through review. We copy this for disciplined, owned pages.

## When to Use

- "Set up the wiki for <repo>."
- "Add a runbook / architecture / ops page to the <repo> wiki."
- "Add a user guide / tutorial / FAQ to the <repo> wiki."
- "Document how to use / run / develop <repo> on its wiki."
- "Sync the in-repo wiki source to the live wiki."

Don't use for: user-facing documentation when the repo _already_ has a docs site
or `docs/` pipeline that is the canonical source — link to it from the wiki
instead of duplicating.

## Doctrine

1. **Two zones, one source.** Internal ops are always in the wiki. User-facing
   docs join the wiki only when no docs site owns them; otherwise the wiki links
   out. Both zones are edited in-repo and synced.
2. **Edit in-repo, sync to wiki.** Maintain wiki source under `wiki/` in the
   project repo (or a `wiki` branch). Pages are Markdown reviewed via PR. A sync
   step pushes them to `<repo>.wiki.git`. Never edit the live wiki by hand when
   an in-repo source exists.
3. **Every page has one owner + a purpose.** Name the owning team/person and the
   problem the page solves. Unowned pages rot.
4. **Sidebar is the index.** `_Sidebar.md` is the navigation; update it whenever
   a page is added or moved. `Home.md` is the landing page and states which zone
   each section belongs to.

## Procedure

### 1. Locate or seed the wiki source

Target repo `R` (`OWNER/REPO`), validated under `shikanime-labs/` or
`shikanime-studio/`. Confirm the in-repo source location:

```bash
# Preferred: a `wiki/` directory at repo root, or a `wiki` branch.
git -C "$(pwd)" ls-files wiki/ 2>/dev/null | head
gh api repos/"$R"/branches --jq '.[].name' | grep -x wiki || true
```

If neither exists, propose seeding: create `wiki/Home.md` + `wiki/_Sidebar.md`
in the project repo (via issue → PR, per `sk-issue` / `sk-pr`). Do not push to
the `.wiki.git` remote until the source is review-approved.

### 2. Seed the structure (first time only)

```text
wiki/
  Home.md                # landing: project + zone map (internal vs user) + sidebar mirror
  _Sidebar.md            # nav index (auto-rendered by GitHub)
  # Internal ops zone
  Architecture.md        # intent, components, data flow, boundaries
  Development.md         # local setup, build, test loop, common workflows
  Runbook.md             # operate/deploy/observe; on-call first responder steps
  Troubleshooting.md     # known failure modes + fixes
  Releases.md            # release state, schedule, known issues (internal)
  Decisions.md           # ADRs / trade-off records
  # User-facing zone (add only if no docs site owns these)
  User-Guide.md          # how to install, configure, and use the project
  Tutorials.md           # end-to-end walkthroughs
  FAQ.md                 # recurring questions
  Reference.md           # config keys, CLI flags, API surface
```

Head each page with an owner line:

```markdown
<!-- owner: <team-or-person> | zone: internal|user | purpose: <one line> -->
```

### 3. Add or edit a page

Edit the Markdown file in `wiki/`. One page = one concern. English, plain prose,
80-col where reasonable. Link related pages with relative wiki links
(`[[Other-Page]]` renders in the wiki).

- Internal page → add under the internal section of `_Sidebar.md`.
- User page → add under the user section; if a docs site already owns that
  content, link to it from `Home.md` instead of authoring a duplicate.

### 4. Sync to the live wiki

The wiki is a separate git remote: `<repo>.wiki.git`. Mirror the `wiki/`
directory's contents into it (page names become wiki page titles; `_Sidebar.md`
and `_Footer.md` are special filenames GitHub renders).

```bash
# After the in-repo change is merged/reviewed:
WIKI="https://github.com/$R.wiki.git"
TMP="$(mktemp -d)"
git clone "$WIKI" "$TMP"
# Copy pages (flatten wiki/ -> wiki root; keep _Sidebar.md / _Footer.md names)
rsync -a --exclude='.git' wiki/ "$TMP/"
cd "$TMP"
git add -A
git commit -m "wiki: sync from repo source"
git push
cd /; rm -rf "$TMP"
```

Automate this in CI (a job that runs on changes to `wiki/`) so the wiki never
drifts from the source. The `actions/github-wiki-action` marketplace action
mirrors a `wiki/` folder to the wiki remote if you prefer no custom script.

### 5. Verify

```bash
gh api repos/"$R"/wiki --jq '.[].title'   # list live pages
# Confirm the new/updated page appears and _Sidebar renders the link.
```

## Pitfalls

- **Editing the live wiki by hand** — it bypasses review and diverges from the
  source. Always edit `wiki/` in-repo and sync.
- **Duplicating an existing docs site** — if `docs/` or a site already owns user
  docs, link from the wiki; don't fork the content.
- **Stale sidebar** — a page added but missing from `_Sidebar.md` is
  unreachable. Update the sidebar on every add/move.
- **Unowned pages** — add the owner/zone/purpose comment or the page rots.
- **Wiki size limit** — soft cap 5,000 files; for larger docs use GitHub Pages.
- **Wrong remote** — the wiki is `<repo>.wiki.git`, a different repo from the
  code. Pushing code branches there does nothing useful.

## See also

- `sk-issue` / `sk-pr` — the in-repo wiki source still goes through issue → PR.
- `sk-land` — land the wiki-source PR before syncing.
