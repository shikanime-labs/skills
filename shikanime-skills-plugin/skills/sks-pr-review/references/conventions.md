# Org stack conventions (shikanime)

Auth trust-boundary checks to add on top of `security-scan.md` when the
repo under review uses the org stack:

- Keycloak/JWKS: the JWKS fetch must have a timeout, and the token audience
  and client must be bound (no `verify_aud=false`, no unvalidated issuer).
- NestJS/Prisma: validated DTO types are the only trust boundary into the
  service layer — no raw `any` request bodies passed to Prisma queries.
