# sk-doc — Pitfalls

Lazily loaded from `SKILL.md`.

- **Editing a published docs site by hand** — it bypasses review and diverges
  from the source. Always edit `docs/` in-repo and review via PR.
- **Duplicating an existing docs site** — if `docs/` or a site already owns user
  docs, link from `docs/`; don't fork the content.
- **Stale index** — a page added but missing from `docs/README.md` is
  unreachable. Update the index on every add/move.
- **Unowned pages** — add the owner/zone/purpose comment or the page rots.
- **Wiki-size reflex** — a separate `.wiki.git` remote is no longer used; docs
  live in the repo and follow the repo's size norms.
