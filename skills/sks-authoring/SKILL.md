---
name: sks-authoring
description:
  "Use when authoring or revising code, manifests, secrets, skills, or GitHub
  or technical English in an org repo: routes to the per-domain reference with
  its full conventions."
version: 0.1.0
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - authoring
      - conventions
      - style
    related_skills:
      - sks-dev
      - sks-commit
      - sks-pr-review
      - sks-curate
platforms:
  - linux
  - macos
  - windows
---

# Authoring

Single entry point for authoring and revision conventions in org repos. Each
domain's full rule set lives in one reference — read the one that matches the
surface you are about to edit, never all of them:

| You are writing or reviewing…      | Read                                 |
| ---------------------------------- | ------------------------------------ |
| TypeScript                         | `references/ts.md`                   |
| Nix                                | `references/nix.md`                  |
| Kubernetes manifests / kustomize   | `references/kubernetes-manifests.md` |
| sops-encrypted `.enc.*` secrets    | `references/sops-secrets.md`         |
| GitHub text (commits, issues, PRs, | `references/github-text.md`          |
| discussions, comments)             |                                      |
| Technical English (docs, runbooks) | `references/technical-english.md`    |
| A new catalog skill or profile     | `references/skill.md`                |

Cross-domain rules: format only the files you touched (`nix fmt` is
whole-tree by default and corrupts `.enc.*`); generated YAML is never
hand-edited — fix the generator and re-render; ship through `sks-dev`
(`sks-delegate` isolation, `sks-commit` envelope, `sks-pr`).

Org-specific repo names, paths, and shapes live in the per-domain
`*-shikanime.md` references when operating in a shikanime org.

## When to Use

- Writing or changing code, manifests, secrets, skills, or GitHub/technical
  text in an org repo — before the first edit.
- Reviewing a diff against the org's conventions (`sks-pr-review` applies
  these as findings).
- Deciding whether a new option, wrapper, or helper is worth adding.

## Verification

Confirm the domain reference was read before editing: the change cites the
conventions it followed (formatter scoped, no generated-file edits, YAGNI on
new options).

## See also

- `sks-dev` — the loop authored changes ship through.
- `sks-commit` / `sks-pr` — commit envelope and PR side.
- `sks-pr-review` — review lens that enforces these conventions.
- `sks-curate` — revising an existing catalog skill's own body.
