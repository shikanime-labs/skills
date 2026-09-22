---
name: cpn-issue
description:
  "À utiliser quand vous ouvrez une issue console cloud-pi-native : énoncé du
  problème en français et critères d'acceptation décidables."
version: 0.1.2
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - github
      - issues
      - cloud-pi-native
      - french
    related_skills:
      - cpn-dev-workflow
      - cpn-issue-triage
      - cpn-pr
platforms:
  - linux
  - macos
  - windows
---

# CPN Org Issue Creation

Open `cloud-pi-native/console` issues with its French templates. Issue-first
repo norm: open the issue before any PR, then link it (see `cpn-pr`).

## When to Use

- "Open an issue on console" / "create a bug/feature ticket for console".

## Prerequisites

- `gh` authenticated (`gh auth status`); active identity must be a repo
  collaborator. Do NOT run `gh auth switch` — edit the scoped config instead.
- `cloud-pi-native/console` is the issue tracker: query/link issues against it
  directly.

## Quick Reference

| Goal          | Command                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Bug issue     | `gh issue create --repo cloud-pi-native/console --title "🐛 [BUG] - <t>" --label bug --body "$(cat <<'EOF' … EOF)"`             |
| Feature issue | `gh issue create --repo cloud-pi-native/console --title "💡 [REQUEST] - <t>" --label enhancement --body "$(cat <<'EOF' … EOF)"` |
| Verify        | `gh issue view <N> --repo cloud-pi-native/console --json number,title,labels`                                                   |

## Procedure

### 0. Vérifier les issues existantes

Recherche avant création pour éviter les doublons :

```bash
gh issue list --repo cloud-pi-native/console --state all \
  --search "<mots-clés>" --limit 10
```

Si une issue ouverte (ou récemment fermée) correspond, signale le `#N` et
demande à l'utilisateur s'il faut la réutiliser plutôt qu'en ouvrir une
nouvelle. Ne crée une nouvelle issue que s'il n'en existe aucune correspondante
(ou si l'utilisateur préfère un ticket neuf).

**GitHub issue body is free text** — never wrap lines and never insert hard
line breaks at a column width. Write natural paragraphs; a blank line
separates paragraphs, everything else renders as-is. Never run `nix fmt` /
`mdformat` over an issue body; those tools enforce an 80-column wrap that does
not apply to GitHub bodies. Encouragez un diagramme Mermaid (ex. `flowchart`)
quand une représentation visuelle aide le lecteur — GitHub rend le Mermaid dans
les corps d'issue. Le diagramme est un renfort optionnel, jamais un substitut à
la prose.

- `@nom` en prose déclenche une mention d'utilisateur/équipe — pour écrire un
  `@` littéral (decorators, clés de config, `@Inject(x)`), l'enfermer dans un
  bloc de code (inline ou fenced) ; le code est le seul contexte où l'analyse
  des mentions est désactivée.

Full French templates →
[references/issue-templates.md](references/issue-templates.md). Bug example:

```bash
gh issue create \
  --repo cloud-pi-native/console \
  --title "🐛 [BUG] - <short summary>" \
  --label "bug" \
  --body "$(cat <<'EOF'
# Full template in references/issue-templates.md
EOF
)"
```

## Triage metadata

After the body is set, delegate to `cpn-issue-triage` (#N): it sets labels
(seeded by template), assignee, project, milestone (bug → current patch,
enhancement → next release). Always against `cloud-pi-native/console`.

## Comment vs Body

- **Body** = problem statement only; edit solely to clarify the incident
  (Description, reproduction steps, affected version, _Définition du fini_).
  Must stay a stable, clean statement for triage.
- **Findings → comments:**
  `gh issue comment <N> --repo cloud-pi-native/console --body-file <file>`.
- `Définition du fini` is the work ledger (rules →
  [references/ledger.md](references/ledger.md)); closure is deliberate —
  verified N of N, then `gh issue close <N> -c "<evidence>"`:

```bash
gh issue comment <N> --repo cloud-pi-native/console --body-file /tmp/finding.md
```

## References & investigation

- Body may carry a **References** section (docs, linked issues/PRs, commits,
  specs); post extra material as comments (`gh issue comment`). Proof of the
  solution belongs in the PR (see `cpn-pr`).
- Root-cause recipe →
  [references/regression-trace.md](references/regression-trace.md): `jj log`
  pickaxe → `jj file annotate` → `jj show` → `gh pr list --search <hash>` →
  follow the PR's linked issue. Verify the linked issue actually describes the
  change — PRs are often mis-linked here; state if unrecorded.

## Pitfalls

Optional edge cases and gotchas — load `references/pitfalls.md` on demand.

## Verification

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,labels
```

Confirm title carries `🐛 [BUG]` or `💡 [REQUEST]`, label is
`bug`/`enhancement`.

## See also

- `cpn-pr` — link via `Issues liées: #N` ; PR body restates the linked commit
  (source of truth, see `cpn-dev-workflow`).
- `cpn-dev-workflow` — branch discipline, direct push, local dev loop.
- `cpn-issue-triage` — assigns metadata; run after creation.
