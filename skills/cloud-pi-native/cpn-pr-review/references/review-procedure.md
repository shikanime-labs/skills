# cpn-pr-review — Procedure detail (Phases 2 & 3)

Loaded lazily from `SKILL.md` (Phase 2 High-level / Phase 3 Line-by-line).

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
