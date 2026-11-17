---
name: sks-edit
description: "Use when a write-phase change needs authoring conventions: identify the matching family (TypeScript, Nix, skill authoring, sops secrets, Kubernetes manifests, plain English) and apply its fused rules in this skill."
version: 0.2.1
author: Automata
license: Apache-2.0
metadata:
  hermes:
    tags:
      - editing
      - authoring
      - conventions
      - identification
    related_skills:
      - sks-dev
      - sks-commit
      - sks-pr
platforms:
  - linux
  - macos
  - windows
---

# Fused Authoring

`sks-edit` owns all authoring conventions for target-org repos: identification
(match table below), family rule sets (each routed by the table below to its
`references/<family>/guide.md`),
and the shared write conventions. During the write phase of any target-org repo
(see `sks-dev`), match the files being edited to the table, then apply the
matched family. If several rows match, prefer the most specific.

## Identify the authoring family (match table)

| File / trigger | Family | Detail reference |
| --- | --- | --- |
| `.ts` / `.tsx` under `apps/` or a shared package | TypeScript | `references/typescript/guide.md` |
| `.nix` in a flake / module / devshell | Nix | `references/nix/guide.md` |
| New skill / profile under `skills/` | Skill authoring | `references/skill-authoring/guide.md` |
| `secrets/*.enc.*`, `*.enc.env`, `*.enc.conf` | sops secrets | `references/sops-secrets/guide.md` |
| Kubernetes manifests, `kustomization.yaml`, overlays, `Deployment` / `STS` | Kubernetes manifests | `references/kubernetes-manifests/guide.md` |
| Docs, runbooks, commit / PR / issue body (STE prose), error messages | Plain English | `references/text/guide.md` |
| GitHub issue / PR / comment body, review threads | GitHub text | `references/github-text/guide.md` |

Do not double-apply: if a `.nix` module emits YAML (`sopsFile`,
`secretGenerator`), it is Nix-only — the generated YAML is the
Kubernetes-manifests family's surface, not a second edit. If a secret file is
consumed by a Nix `sopsFile`, the Nix side uses the Nix family and the secret
edit uses the sops-secrets family — two distinct files, two distinct families.

## Apply the matched family

1. Load the family guide from the table above; it and its sibling files under
   the same `references/<family>/` directory are the detail source of truth.
2. Org-convention entry points for concrete repo names and paths:
   - `references/shikanime.md` — the shikanime org map (applies to all
     families when operating in a shikanime repo).
   - `references/typescript/cloud-pi-native-console.md` — the
     cloud-pi-native/console TypeScript surface.
3. Keep `sks-dev` gates (branch protection, jj bookmark tracking,
   push-to-origin, PR draft→ready) in force for every authored change.

## Write conventions (all families)

- Plain English across the family; `#N` for standalone refs; commit↔PR parity.
- Zero code comments by default. Before writing one, move the intent into
  structure — a subfunction or a named intermediate carries what the comment
  would have said. A comment passes only if it names a fact unreachable from
  the repository: a workaround trick, an algorithm's source, an external
  service's error quirk, a non-obvious invariant. If a competent dev could
  recover the fact from the code in about a minute, the comment fails —
  refactor instead. The commit body, not a comment, explains an atomic
  change. Full policy: `references/comment-policy.md`.
- Ponytail-based edits obey the hard prose caps in
  `references/comment-policy.md` (comment 1 line, commit body 10, PR/issue
  body 30, reply 5, review finding 3, per-unit summary 10) — exceeding a
  cap moves the content to a linked artifact, never inline.
- For prose (docs, runbooks, commit / PR / issue bodies) the plain-English
  family (ASD-STE100) owns sentence content; `references/github-text/guide.md` owns
  prose mechanics (wrapping, `@` escaping, body transport).
- Do NOT pass bodies inline via `--body "..."` — shell expansion mangles
  backticks and `$`. Write the body to a file and pass `--body-file`.

## See also

`sks-dev` (dev loop write phase), `references/github-text/guide.md` (prose
mechanics), `sks-commit`, `sks-pr`, `sks-context` (org conventions).

## Verification

No standalone command: each family guide carries its own verification block;
this skill only routes to it.

## evals routing

`evals/evals.json` carries three prompts grading identification routing (two
trigger phrasings + one no-double-apply edge case). Run with the repository's
eval harness; assertions check scope routing, not trivia.
