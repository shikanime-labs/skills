# sk-async companion reference

Lazy-loaded detail for `SKILL.md` (not loaded at default skill load). Documents
the DAG model, pitfalls, and the exact `delegate_task` payload shape for
parallel fan-out.

## Model: work is a DAG, jj executes it

- **Fan-out** — N children of one trunk commit = parallel independent units.
- **Depth** — child of a child = dependent unit; each root-to-leaf chain is a
  STACK (`gh stack`), each link its own PR.
- **Join** — `jj new <a> <b>` (multiple parents) = depends on several units;
  lands after them.
- **Isolation** — each stream in its OWN jj workspace (separate working copy +
  working-copy commit, same repo/graph). No contention by construction.
- **Independence test**: a unit is independent iff its file set is disjoint from
  its siblings' and it imports none of their NEW code. Otherwise it is a
  dependent unit (depth) or a join (merge).

## Fan-out via delegate_task — payload

Give each child agent: its workspace path, its unit's gates, the commit shape
(plain English + Automata co-author trailer). The parent re-verifies every gate
via `terminal` inside each workspace before reporting done.

Dispatch with `delegate_task(tasks=[...])`; one task per leaf, the `goal`
carrying the unit's contract (workspace path, gates, commit shape). Split
independent units into separate tasks — never bundle two leaves into one `goal`,
that defeats isolation:

```python
delegate_task(tasks=[
    {"goal": "Implement <repo>.<unit>: <contract>. Workspace: "
             "../<repo>.<unit>. Gates: <N>. Commit plain-English + "
             "'Co-authored-by: Automata <automata@shikanime.studio>' trailer.",
     "context": "shikanime repo <org>/<repo>; rooted at trunk; one workspace "
                "per unit per sk-async.",
     "toolsets": ["terminal", "file"]},
])
```

## Pitfalls

- **Pseudo-independent units** (overlapping file sets) → merge conflicts at
  join; fix the decomposition, not the conflict.
- **Workspaces share the repo** — bookmarks and the commit graph are GLOBAL: one
  bookmark per unit, never two streams on one bookmark.
- **Fan-out before contracts** — spawning children without fixed gates
  reproduces the prose-enforcement failure the gates exist to prevent.
- `gh stack` = GitHub public-preview; fine for internal shikanime use (see
  `sk-dev-workflow`).
- Forgetting `jj workspace update-stale` on a workspace left idle while the
  trunk advanced — it does not auto-advance.
