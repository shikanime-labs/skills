---
name: sks-edit
description: "Use when a write-phase change needs an authoring skill: identify which authoring convention applies to the files being edited, then apply the matched family skill for detail."
version: 0.1.0
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
      - sks-ts-authoring
      - sks-nix-authoring
      - sks-skill-authoring
      - sks-sops-secrets-authoring
      - sks-kubernetes-manifests-authoring
      - sks-text-authoring
      - sks-wiki
platforms:
  - linux
  - macos
  - windows
---

# sks-edit — Authoring-skill identification

`sks-edit` is the fused umbrella for the individual authoring skills. During the
write phase of any target-org repo (see `sks-dev`), match the files being edited
to the row below; the matching row tells you which family skill to load for the
detail. If several rows match, prefer the most specific. If a file is a TypeScript
file on the NestJS server it is TypeScript-only — do not additionally apply Nix.

## Identify the authoring skill (match table)

| File / trigger | Matches | Apply (detail) |
| --- | --- | --- |
| `.ts` / `.tsx` under `apps/` or a shared package | TypeScript authoring | `sks-ts-authoring` |
| `.nix` in a flake / module / devshell | Nix authoring | `sks-nix-authoring` |
| New skill / profile under `skills/` | Skill authoring | `sks-skill-authoring` |
| `secrets/*.enc.*`, `*.enc.env`, `*.enc.conf` | sops secrets authoring | `sks-sops-secrets-authoring` |
| Kubernetes manifests, `kustomization.yaml`, overlays, `Deployment` / `STS` | manifests authoring | `sks-kubernetes-manifests-authoring` |
| Docs, runbooks, commit / PR / issue body (STE prose), error messages | plain English authoring | `sks-text-authoring` |
| GitHub wiki pages (`Home.md`, `*.md` under `.wiki`) | wiki authoring | `sks-wiki` |

Do not double-apply: if a `.nix` module emits YAML (`sopsFile`, `secretGenerator`),
it is Nix-only — the generated YAML is the manifests skill's surface, not a second
edit. If a secret file is consumed by a Nix `sopsFile`, the Nix side is
`sks-nix-authoring` and the secret edit is `sks-sops-secrets-authoring` — two
distinct files, two distinct skills.

## Apply the matched skill

1. Load the matched family skill (`sks-ts-authoring`, `sks-nix-authoring`,
   `sks-skill-authoring`, `sks-sops-secrets-authoring`, `sks-kubernetes-manifests-authoring`,
   `sks-text-authoring`, or `sks-wiki`). That skill's body and `references/` are the
   detail source of truth.
2. For `sks-ts-authoring`, `sks-nix-authoring`, `sks-sops-secrets-authoring`, and
   `sks-kubernetes-manifests-authoring`, their `references/shikanime.md` is the org
   convention entry point for concrete repo names and paths.
3. Keep `sks-dev` gates (branch protection, jj bookmark tracking, push-to-origin,
   PR draft→ready) in force for every authored change.

## Write conventions

- Plain English across the family; `#N` for standalone refs; commit↔PR parity.
- For prose (docs, runbooks, commit / PR / issue bodies) apply `sks-text-authoring`
  (ASD-STE100) — it owns sentence content; `sks-github-text-authoring` owns prose
  mechanics (wrapping, `@` escaping, body transport).
- Do NOT pass bodies inline via `--body "..."` — shell expansion mangles backticks
  and `$`. Write the body to a file and pass `--body-file`.

## See also

`ske-dev` (dev loop write phase), `sks-skill-authoring` (creating a new skill),
`sks-github-text-authoring` (prose mechanics), `sks-commit`, `sks-pr`, `sks-context`
(org conventions).

## Verification

```bash
# Routing smoke test: confirm sks-edit loads and the family skill resolves.
# Each family skill owns its own verification block; sks-edit only routes.
sks-edit (identification) — no standalone command; the matched family skill
carries the check.
```

## evals routing

The file `evals/evals.json` carries three prompts that grade the identification
routing (two trigger phrasings + one edge case that must route elsewhere).
Run with the repository's eval harness; the assertions check scope routing, not
trivia.
