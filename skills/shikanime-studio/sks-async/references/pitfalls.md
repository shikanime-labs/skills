# sks-async — Pitfalls

- Pseudo-independent units (overlapping file sets) → merge conflicts at join; fix the decomposition, not the conflict.
- Workspaces share the repo — bookmarks and the commit graph are GLOBAL: one bookmark per unit, never two streams on one bookmark.
- Fan-out before contracts → spawning children without fixed gates reproduces the prose-enforcement failure the gates exist to prevent.
- `gh stack` is GitHub public preview; fine for internal shikanime use (see `sks-dev-workflow`).
- Forgetting `jj workspace update-stale` on a workspace left idle while the trunk advanced — it does not auto-advance.
