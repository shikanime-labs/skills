# cpn-issue-refine — détail du fan-out `research`

Pour les items `research`, résous le travail AFK en parallèle via
`delegate_task` : un enfant par fait indépendant. Si le dépôt est touché, isole
chaque enfant sur une branche `research/<name>` via `cpn-async`. Research **lit
et rapporte uniquement** : n'édite jamais le code produit. Sépare chaque fait en
`task` distinct — n'empaquette pas plusieurs questions dans un seul `goal`.

```python
delegate_task(tasks=[
    {"goal": "Rechercher <fait> : source autoritative pour <question>. "
             "Read-only ; rapporter trouvaille + Références officielles ; "
             "n'éditer aucun code.",
     "context": "Issue <N> dans <org>/<repo> ; isole sur branche "
                "research/<name> (cpn-async) si dépôt touché.",
     "toolsets": ["web", "terminal"]},
])
```

Pour `grilling`/`prototype`, engage l'humain en série (pas de fan-out).

## Pièges

- **Code produit dans l'issue** — défaillance la plus rapportée.
- **Brouillard déguisé en ticket** — « on devrait investiguer X » sans question
  précise n'est pas une question.
- **Grilling parallèle** — deux fils posent la même question en d'autres mots.
- **Auto-sélection de prototype** — l'humain choisit ; l'agent lie les
  artifacts.
- **Éditer le corps avec les trouvailles** — le corps est l'énoncé stable.
- **Fuites du processus de pensée** — brouillards restent in-agent ; l'issue
  reçoit seulement le commentaire résolu.
- **Français uniquement** — pas d'anglais ; n'importe pas les templates sks-.
