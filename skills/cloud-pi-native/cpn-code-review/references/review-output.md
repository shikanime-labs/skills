# Modèles de revue (commentaires inline — français)

Langue des artifacts cpn : français. Pas de `(...)` dans les titres. Chaque
constat est posté en commentaire inline sur SA ligne (revue unique via l'API),
pas en un seul gros commentaire. Voir
`sk-code-review/references/inline-comments.md` pour les commandes `gh api`.

## Corps de la revue (2-3 phrases max + éloge)

```markdown
**Verdict :** Changements demandés | Approuvé | Commentaire

<2-3 phrases : synthèse du changement, son effet sur la santé du code, et un
point positif précis (pourquoi c'est bien).>
```

## Commentaire inline (un par constat, sur sa ligne)

```markdown
[🔴 Bloquant] <problème>. Suggestion : <correctif>. [🟠 Important] <problème>.
[🟡 Nit] <préférence de style>. [⚪ Suggestion] <amélioration optionnelle>. [✨
Éloge] <bonne pratique — pourquoi.>
```

## Message de commit suggéré (si commitlint rejette)

```markdown
Message de commit suggéré :

    fix(<scope>): <description impérative, minuscule, <= 72 car>

    <corps optionnel : pourquoi, pas quoi>
```

L'auteur amende sa branche (`jj describe` / rebase) ; le réviseur ne pousse
jamais.

<!-- Legacy block-comment template (local review summary only):

## Revue de code — <titre court>

**Verdict :** Changements demandés | Approuvé | Commentaire

### 🔴 Bloquant (à corriger avant fusion)
- **<chemin:fichié:ligne>** — <problème>. Suggestion : <correctif>.
-->

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
