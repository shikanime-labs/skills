---
name: sks-wiki
description:
  Use when documenting a project's technical knowledge in its GitHub wiki:
  enabling the wiki, seeding or syncing pages after a behavior-changing PR,
  and backfilling per-repo technical documentation.
version: 0.4.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - documentation
      - wiki
    related_skills:
      - sks-pr
      - sks-land
      - sks-repo
      - sks-async
platforms:
  - linux
  - macos
  - windows
---

# Project Wiki

Maintain a project's technical documentation in its GitHub wiki — per-repo
pages rendered by GitHub, searchable, and pushed over the normal
`<repo>.wiki.git` remote. Two zones:

- **Technical documentation** (always) — architecture, delegation and
  fan-out mechanics, runbooks, procedure detail too heavy for a skill body.
- **User-facing pages** (when the repo has no dedicated docs site) — user
  guide, FAQ, reference. If a docs site already owns them, link from
  `Home` instead of duplicating.

## When to Use

- "Set up / enable the wiki for <repo>."
- "Add a page to <repo>'s wiki."
- "Backfill <repo>'s technical documentation into its wiki."
- "Document how to use / run / develop <repo> in the wiki."

Don't use for: user-facing documentation when the repo already has a docs
site or `docs/` pipeline that is the canonical source — link to it instead
of duplicating.

## Doctrine

1. **Wiki is the per-repo knowledge base.** Technical documentation lives in
   the target repo's wiki, not in a central skill or a third repo. Per-repo
   detail stays with the repo it describes.
2. **One UI-only gate.** The wiki flag is API-settable (`gh repo edit
   --enable-wiki`), but the FIRST page can only be created in the web UI — no
   REST or GraphQL endpoint covers page creation, and the `.wiki.git` remote
   does not exist until a page exists. Do it once by hand, record it as a
   manual step (same pattern as `sks-repo`'s auto-close toggle; CDP recipe:
   `references/wiki-home-cdp.md`), then every later change is a plain push.
3. **No PR review on wiki content.** Wiki pushes bypass branch protection
   entirely — that is the accepted trade-off for rendered, searchable,
   per-repo pages. Org-sensitive content follows the repo's visibility; when
   in doubt keep it in-repo under `docs/`.
4. **`Home` is the index.** Update it on every page add, move, or rename —
   an unlisted page is unreachable.
5. **One owner per page.** Head each page with the owner comment; unowned
   pages rot.

## Procedure

### 1. Enable the wiki (API)

Repo scoping rule: read `references/shikanime.md` when scoping the
target repo — it names the orgs and the validation rule. Validate repo `R`
(`OWNER/REPO`) there, then:

```bash
gh api repos/OWNER/REPO --jq .has_wiki          # probe
gh repo edit OWNER/REPO --enable-wiki           # flip if false
gh api repos/OWNER/REPO --jq .has_wiki          # verify: true
```

### 2. Create the first page (UI-only, once)

Open `https://github.com/OWNER/REPO/wiki` in a browser and create `Home`
with a one-line index. This is the only manual step; record it as such
("manual: Home created in UI"). Skip if the wiki already renders.

### 3. Seed or sync pages (normal git from here)

```bash
git clone git@github.com:OWNER/REPO.wiki.git && cd REPO.wiki.git
# pages are *.md files at the repo root; Home.md is the index
$EDITOR Home.md Page.md
git add . && git commit -m "Add <page>" && git push
```

Seeding a full docset (backfill): write all pages locally first, then land
them in ONE commit — `Home.md` index plus one page per concern. Link pages
with relative Markdown links. Head each page:

```markdown
<!-- owner: <team-or-person> | zone: technical|user | purpose: <one line> -->
```

### 4. Verify

```bash
git -C REPO.wiki.git log --oneline -1        # push landed
git ls-remote git@github.com:OWNER/REPO.wiki.git HEAD
# open https://github.com/OWNER/REPO/wiki — Home renders and lists pages
```

## Pitfalls

- **Page-creation API does not exist.** REST `repos/.../wiki/pages` 404s and
  GraphQL has no wiki mutations or types (introspected). The `.wiki.git`
  remote 404s until the first UI page exists — do not retry the clone before
  then.
- **Wiki pushes bypass review.** No ruleset, no branch protection, no PR.
  Deliberate trade-off — do not use the wiki for content that needs review.
- **Duplicating in-repo `docs/`** — if the repo already keeps `docs/`
  (in-repo, PR-reviewed), either keep that canonical and link it from
  `Home`, or migrate deliberately and delete the source. Never fork both.
- **Stale `Home` index** — a page added but missing from `Home.md` is
  unreachable. Update the index on every add/move.
- **Unowned pages** — add the owner/zone/purpose comment or the page rots.
- **Fresh clone before first page** — the remote only materializes after
  step 2; script around it, do not hand-wave the 404.

## Verification

```bash
gh api repos/OWNER/REPO --jq .has_wiki   # true (flag: gh repo edit --enable-wiki)
git ls-remote git@github.com:OWNER/REPO.wiki.git HEAD
# Home renders in the UI and lists every page
```

## See also

- `sks-repo` — new-repo bootstrap; flips the wiki flag and records the
  Home-in-UI step.
- `sks-issue` / `sks-pr` — code changes still go through issue → PR; the
  wiki documents the result.
- `sks-async` — fan-out mechanics; its per-repo technical detail belongs in
  each repo's wiki under this skill.
