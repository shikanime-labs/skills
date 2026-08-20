# Modèle de retour de revue (PR comment — français)

Collez ce modèle en commentaire de PR via
`gh pr comment <N> --body "$(cat ...)"`. Langue des artifacts cpn : français.
Pas de `(...)` dans les titres.

```markdown
## Revue de code — <titre court>

**Verdict :** Changements demandés | Approuvé | Commentaire

### 🔴 Bloquant (à corriger avant fusion)

- **<chemin:fichié:ligne>** — <problème>. Suggestion : <correctif>.

### 🟠 Important

- **<chemin:fichié:ligne>** — <problème>.

### 🟡 Nit (style)

- **<chemin:fichié:ligne>** — <préférence de style>.

### ⚪ Suggestion

- **<chemin:fichié:ligne>** — <amélioration optionnelle>.

### 📚 Note pédagogique

- <point de connaissances pour l'auteur>.

### ✨ Points positifs

- <ce qui est bien fait>.

### Vérifications effectuées

- [ ] Branche depuis `upstream` (pas de fork)
- [ ] Auteur : William Phetsinorath
      <william.phetsinorath-open@interieur.gouv.fr>
- [ ] `pnpm test` (vitest) vert
- [ ] Conventions : commits conventionnels, pas de commentaire marqueur IA
- [ ] Contrats `@ts-rest` synchronisés client/serveur
- [ ] Schéma Prisma + migration cohérents
- [ ] Pas de secret dans le diff (`.env` ignoré)
```

## Règles de ton

- Questions plutôt que commandes ; suggestions plutôt que mandates.
- Séparer ce que les linters/CI attrapent de ce que la revue humaine doit voir.
- En cas de doute (PR draft) : `--comment` plutôt que `--request-changes`.

## Publication du verdict

```bash
# Changements demandés
gh pr review <N> --request-changes --body "Voir commentaire ci-dessus."
# Approuvé
gh pr review <N> --approve --body "Revue OK, pas de point bloquant."
# Commentaire simple
gh pr review <N> --comment --body "Quelques suggestions non bloquantes."
```
