# Console review procedure detail (Phases 2 & 3)

Cloud-pi-native console checkpoints. Load when reviewing a console PR; see
`references/cloud-pi-native.md` for the full org rules.

## Phase 2 — High-level architecture checklist

Run against `references/console-architecture.md`:

- resource 3-file pattern
- hook lifecycle
- plugin module augmentation
- Prisma multi-file schema
- env override chain
- NestJS conditional enablement

Flag any deviation from these patterns.

## Phase 3 — Line-by-line checklist

- Strict TS
- vue-dsfr usage
- BigInt permission bitmasks
- `@ts-rest` contract changes (stay in `packages/shared`, keep client/server in
  sync)
- secret hygiene (`.env` gitignored)
- no AI-marker comments
- conventional commit prefixes: `feat|fix|chore|docs|refactor|revert|build`

Per-area pitfalls: see `references/console-architecture.md` and
`references/pitfalls.md`.
