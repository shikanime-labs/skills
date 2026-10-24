# Shikanime org conventions

Org review-stack specifics (used when the repo under review runs the
shikanime org stack):

- Org stack: Keycloak / NestJS / Prisma; auth trust-boundary checks for
  that stack live in `references/conventions.md` (keyed to the org's
  Keycloak/NestJS/Prisma boundaries).
- Orgs in scope: `shikanime-labs/*` and `shikanime-studio/*`.
- Working doctrine: long-term solutions over short-term fixes — fix the root
  cause, never land a tactical patch that accrues debt. No hard SLA
  constraints: correctness and durability outrank turnaround time; take the
  time to do it properly.
