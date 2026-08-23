# Fan-out via delegate_task — exemple de dispatch

Un task par feuille ; le `goal` porte le contrat de l'unité. Sépare les units
indépendants en tasks distincts, jamais deux feuilles dans un seul `goal`. Donne
à chaque enfant : chemin du workspace, gates de l'unit, forme du commit
(conventionnel + trailer Automata). Le parent re-vérifie chaque gate via
`terminal` dans chaque workspace avant de déclarer terminé.

```python
delegate_task(tasks=[
    {"goal": "Implémenter <repo>.<unit>: <contrat>. Workspace: "
             "../<repo>.<unit>. Gates: <N>. Commit conventionnel + "
             "trailer Automata.",
     "context": "dépôt shikanime <org>/<repo> ; racine trunk ; un workspace "
                "par unité (cpn-async).",
     "toolsets": ["terminal", "file"]},
])
```
