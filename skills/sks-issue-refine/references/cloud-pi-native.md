# Cloud-pi-native refinement conventions

Load when refining an issue in the cloud-pi-native/console repository — the
generic loop in SKILL.md is unchanged; these are the org overrides.

- Artifact language is **French only** — comments and convergence summaries;
  never import the shikanime (sks-) templates or headings into a console
  thread.
- Run every `gh` command against `--repo cloud-pi-native/console`.
- `research` fan-out: one `delegate_task` child per independent fact — never
  bundle several questions into a single `goal`. Isolate each child on a
  `research/<name>` branch (via `sks-async`) when the repo is touched;
  read-only, post only the conclusion as a comment, never edit product code.
- Suggested fan-out shape (French):

```python
delegate_task(tasks=[
    {"goal": "Rechercher <fait> : source autoritative pour <question>. "
             "Read-only ; poster la conclusion en commentaire (pas de "
             "trouvaille ni de liste de Références) ; n'éditer aucun code.",
     "context": "Issue <N> dans cloud-pi-native/console ; isole sur branche "
                "research/<name> si dépôt touché.",
     "toolsets": ["web", "terminal"]},
])
```

- Routing: open with `sks-issue`, RFC surface `sks-discussion` (before the
  problem is statable), solver `sks-pr` (links back via `Refs:`), metadata
  via `sks-issue-triage` once converged.
