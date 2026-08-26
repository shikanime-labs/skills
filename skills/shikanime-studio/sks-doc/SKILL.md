---
name: sks-doc
description:
  Use when documenting a shikanime project in the repo's docs/ directory after a
  behavior-changing PR.
version: 0.3.0
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - documentation
      - docs
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-pr
      - sks-land
      - sks-issue
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Docs

Maintain a project's knowledge base as plain Markdown under `docs/` in the repo
— reviewed via PR, no separate wiki remote to sync. Two zones:

- **Internal ops** (always) — development runbooks, architecture intent,
  operational procedures, release/QA state, decisions, tribal knowledge.
- **User-facing docs** (when the repo has no dedicated docs site) — user guide,
  tutorials, FAQ, reference. If a docs site already owns them, link out instead
  of duplicating.

Modeled on how large projects run contributor docs:

- **Longhorn** — internal operations (dev, QA, release, project management) live
  alongside the code; user documentation lives on a dedicated site. We copy the
  split: keep user docs out of `docs/` only if a site already owns them.
- **Kubernetes** — docs follow a style guide, assign an owner, and go through
  review. We copy this for disciplined, owned pages.
- **PyTorch** — content is edited in a reviewable repo (PR + CI), never via
  ad-hoc web edits. We copy this so docs get review like any other change.

## When to Use

- "Set up docs for <repo>."
- "Add a runbook / architecture / ops page to <repo> docs."
- "Add a user guide / tutorial / FAQ to <repo> docs."
- "Document how to use / run / develop <repo>."

Don't use for: user-facing documentation when the repo already has a docs site
or `docs/` pipeline that is the canonical source — link to it instead of
duplicating.

## Doctrine

1. **Two zones, one location.** Internal ops are always in `docs/`. User-facing
   docs join `docs/` only when no docs site owns them; otherwise `docs/` links
   out. All pages are Markdown reviewed via PR.
2. **Edit in-repo, review via PR.** Maintain pages under `docs/` in the project
   repo. No separate remote, no sync step — the PR that changes a page is the
   change. Never hand-edit a published docs site when an in-repo source exists.
3. **Every page has one owner + a purpose.** Name the owning team/person and the
   problem the page solves. Unowned pages rot.
4. **Index is the nav.** `docs/README.md` is the landing page and index; update
   it whenever a page is added or moved.

## Procedure

### 1. Locate or seed the docs source

Target repo `R` (`OWNER/REPO`), validated under `shikanime-labs/` or
`shikanime-studio/`. Confirm the in-repo source:

```bash
jj file list docs/ 2>/dev/null
```

If absent, propose seeding via issue → PR (`sks-issue` / `sks-pr`): create
`docs/README.md` listing the zones. Do not publish a separate docs site until
the in-repo source is review-approved.

### 2. Seed the structure (first time only)

```text
docs/
  README.md              # landing: project + zone map + index
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

Head each page with an owner comment:

```markdown
<!-- owner: <team-or-person> | zone: internal|user | purpose: <one line> -->
```

### 3. Add or edit a page

Edit the Markdown file in `docs/`. One page = one concern. English, plain prose,
80-col where reasonable. Link related pages with relative Markdown links
(`[Architecture](./Architecture.md)`).

- Internal page → add to the internal section of `docs/README.md`.
- User page → add to the user section; if a docs site already owns that content,
  link to it from `docs/README.md` instead of authoring a duplicate.

### 4. Verify

```bash
jj file list docs/   # confirm the page landed and README lists it
# Open the rendered page / run the repo's docs build if one exists.
```

## Pitfalls

- Editing a published docs site by hand — it bypasses review and diverges from
  the source. Always edit `docs/` in-repo and review via PR.
- Duplicating an existing docs site — if `docs/` or a site already owns user
  docs, link from `docs/`; don't fork the content.
- Stale index — a page added but missing from `docs/README.md` is unreachable.
  Update the index on every add/move.
- Unowned pages — add the owner/zone/purpose comment or the page rots.
- Wiki-size reflex — a separate `.wiki.git` remote is no longer used; docs live
  in the repo and follow the repo's size norms.

## Verification

```bash
jj file list docs/   # page landed and README lists it
# run the repo's docs build if one exists; open the rendered page
```

## See also

- `sks-issue` / `sks-pr` — docs changes go through issue → PR like any other.
- `sks-land` — land the docs PR; no separate wiki sync step remains.
