# cpn-discussion — Pitfalls

Lazily loaded from `SKILL.md`.

- **`gh api graphql -F variables=@file.json` FAILS**: `-F` sends the file as a
  raw string, not a JSON map. Always use `--input file.json` with
  `{ "query": "...", "variables": {...} }`.
- **Discussions ≠ Issues.** No `gh discussion edit`; edits go through the
  `updateDiscussion` GraphQL mutation. Do not use `gh issue edit`.
- **French + #NNNN links** per house style.
