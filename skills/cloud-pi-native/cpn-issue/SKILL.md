---
name: cpn-issue
description: "Open CPN console issues with French templates."
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags: [GitHub, Issues, cloud-pi-native, French]
---

# CPN Org Issue Creation

Create GitHub issues for `cloud-pi-native/console` using the repo's French issue
templates and label conventions. Issue-first is the repo norm: create the issue
before any PR, then link the PR to it (see `cpn-pr`).

## When to Use

- "Open an issue on console" / "create a bug/feature ticket for console".
- Any creation task in `cloud-pi-native/console` requiring a French issue body.

## Prerequisites

- `gh` authenticated (`gh auth status`); the active identity must be a repo
  collaborator. Do NOT run `gh auth switch` — edit the scoped config instead.
- The `shikanime/cloud-pi-native-console` fork has **Issues disabled**: query
  and link issues against upstream `cloud-pi-native/console`.

## How to Run

All mutations go through the `terminal` tool with `gh`.

## Quick Reference

| Goal          | Command                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Bug issue     | `gh issue create --repo cloud-pi-native/console --title "🐛 [BUG] - <t>" --label bug --body "$(cat <<'EOF' … EOF)"`             |
| Feature issue | `gh issue create --repo cloud-pi-native/console --title "💡 [REQUEST] - <t>" --label enhancement --body "$(cat <<'EOF' … EOF)"` |
| Verify        | `gh issue view <N> --repo cloud-pi-native/console --json number,title,labels`                                                   |

## Procedure

### 1. Bug issue

Title `🐛 [BUG] - <short summary>`, label `bug`:

```bash
gh issue create \
  --repo cloud-pi-native/console \
  --title "🐛 [BUG] - <short summary>" \
  --label "bug" \
  --body "$(cat <<'EOF'
## Description

<explicit description of the incident>

## Etapes de reproduction

1. Aller à '...'
2. Cliquer sur '....'
3. Voir l'erreur

## Captures d'écran

## Logs

## Navigateurs

## OS

## Version de la console impactée

## Définition du fini

- [ ] Le correctif est terminé
- [ ] Les tests liés à ce correctif ont été ajoutés
EOF
)"
```

### 2. Feature issue

Title `💡 [REQUEST] - <short summary>`, label `enhancement`:

```bash
gh issue create \
  --repo cloud-pi-native/console \
  --title "💡 [REQUEST] - <short summary>" \
  --label "enhancement" \
  --body "$(cat <<'EOF'
## Description

<brief feature explanation>

## PRs liées

## Issues liées

## Exemples simples

## Spécifications techniques

## Définition du fini

- [ ] La fonctionnalité est terminée
- [ ] Les tests liés à cette fonctionnalité ont été ajoutés
- [ ] La documentation liée a été ajoutée
EOF
)"
```

## Triage metadata

After the issue body is set, delegate to `cpn-triage-issue` (#N): it enumerates
the repo's available metadata and sets each empty, determinable field — labels
(already seeded by the template), assignee, project, and milestone (bug →
current patch, enhancement → next release). The rules live in
`cpn-triage-issue`; do not re-derive them here. This is always against upstream
`cloud-pi-native/console` (the fork has Issues disabled).

## Comment vs Body convention

- **Body** = the problem statement only. Edit it solely to clarify or correct
  the reported incident (Description, reproduction steps, affected version,
  _Définition du fini_). Never embed investigation results there.
- **Findings go in comments.** Any root-cause analysis, code references,
  regression commits, or proposed fixes are posted with
  `gh issue comment <N> --repo cloud-pi-native/console --body-file <file>`.
- Rationale: the body must stay a stable, clean problem statement for triage;
  findings evolve and should not rewrite it.

### Définition du fini = the gate ledger

The body's `Définition du fini` tasklist is the work item's ledger (unlazy
method): each `- [ ]` item phrased so a command can decide it, mirrored as
`todo` items in-session (todo is the working copy, the issue is the record). An
item is done only once its check ran — not from memory. The PR (cpn-pr) proves
the ledger: N of N, numbers re-measured at writing time. A genuinely impossible
criterion is struck with a comment, never silently dropped. Several PRs may
jointly solve one issue — linkage stays `Issues liées` / `Refs` (auto-close
avoided; see cpn-pr); the ledger stays one per issue, and closure is deliberate:
verified N of N after the final merge, then
`gh issue close <N> -c "<evidence>"`.

```bash
gh issue comment <N> --repo cloud-pi-native/console --body-file /tmp/finding.md
```

## References and evidence

The issue body carries a **References** section: official material (upstream
documentation, linked issues/PRs, commits, changelogs, specs) attesting a
potential solution or adding context about the problem statement. The agent may
post additional material as comments (`gh issue comment`) to help steer
resolution toward a solution. Proof of the solution itself belongs in the PR
(see `cpn-pr`), not the issue.

## Investigation — tracing a change's rationale

When the issue needs a root cause (not just a symptom report), trace the code
change instead of guessing. The recipe and a worked example live in
[references/regression-trace.md](references/regression-trace.md): `jj log`
revset pickaxe → `jj file annotate` → `jj show` → `gh pr list --search <hash>` →
follow the PR's linked issue. Always **verify the linked issue actually
describes the change** — in this repo PRs are often linked to an unrelated
issue, so the real rationale may be unrecorded (state that explicitly rather
than assuming).

## Pitfalls

- Pushing to the wrong repo: on the `shikanime` fork, Issues are disabled —
  create/link against `cloud-pi-native/console` upstream.
- Missing `bug`/`enhancement` label — both templates set it; keep it.
- English bodies break repo convention; the templates are French.
- Do NOT rewrite the body with investigation results — those belong in a comment
  (see above).

## Verification

```bash
gh issue view <N> --repo cloud-pi-native/console --json number,title,labels
```

Confirm: title carries `🐛 [BUG]` or `💡 [REQUEST]`, and label is
`bug`/`enhancement`.

## See also

- `cpn-pr` — the PR that solves this issue must link it via `Issues liées: #N`
  (auto-close avoided unless explicitly one-to-one); the PR title is
  conventional and its body restates the linked commit (commit is the source of
  truth, see `cpn-dev-workflow`).
- `cpn-dev-workflow` — branch discipline, upstream-only push, and the full local
  dev loop this issue feeds into.
- `cpn-triage-issue` — assigns issue metadata (labels, assignee, milestone,
  project); run it after creation.
