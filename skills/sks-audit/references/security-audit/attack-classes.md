# Attack Classes

Core classes for every audit. Select from reconnaissance findings, not from
language or dependency names; add application-specific classes and split
large codebases per subsystem. Load the domain companion named in the
skill's domain table once reconnaissance finds that boundary.

`confirmed` requires source evidence plus bounded validation establishing
the full boundary and a meaningful result. `needs_validation` when a
specific deployment, provider, platform, or runtime fact is unavailable:
state the missing fact and the safe check that resolves it.

## Injection

Trace untrusted input from entry point to dangerous sink; what counts as
dangerous depends on the application. Web: SQL, HTML output, shell
commands, template engines, file paths, redirects, deserialization.
Libraries: any function processing caller data without validation — buffer
operations, parsers, format strings. CLI: command construction, path
handling, environment interpolation. Services: query construction,
message serialization, log injection.

Look past direct paths: data stored safely then used dangerously by
different code; injection through field names, keys, headers, and
metadata, not just values; injection into secondary systems — logs,
caches, search indexes, analytics.

## Access Control

Verify a caller cannot act outside its authority — not whether checks
exist, but whether the right permission is checked for the right resource
through the right mechanism:

- A path to the same state change that checks a weaker permission.
- Request-body fields overriding what the permission system meant to
  restrict.
- Endpoints that gate on authentication but forget authorization.
- One resource with several access paths and inconsistent checks.
- Bulk, batch, export, and import operations skipping per-item
  permissions.

Split complex models into separate auth-bypass and authorization-logic
reviews.

## Resource and File Handling

Path traversal through symlinks, encoded sequences, and null bytes; SSRF
through redirects, DNS rebinding, and URL parser differentials; unsafe
deserialization and archive extraction (zip slip); temp-file handling;
TOCTOU races between check and use on file operations.

## Cryptography and Secrets

Weak randomness for tokens, keys, and nonces; hardcoded secrets and
secrets reaching logs, error messages, URLs, or client-visible responses;
broken key derivation and missing HMAC verification; nonce reuse; timing
side channels in secret comparison; misused primitives — ECB,
unauthenticated encryption, static IVs; error paths that fall back to
no-crypto.

## Business Logic

Logic errors scanners cannot find, hunted by hand per workflow:

- State machine violations: skipped or reversed steps, replayed completed
  flows, partial failure without rollback.
- Races with business impact: check-then-act on concurrent operations —
  double-approve, double-spend, lost updates.
- Numeric manipulation: negative and zero values, overflow, precision
  loss, string-to-number coercion.
- Boundary violations against the business rule, not merely a missing
  check: input to one operation bypassing a restriction another operation
  enforces for the same effect.
- Implicit trust: stored, configured, or plugin data assumed safe because
  it was validated on the way in — what if another code path wrote it?
- Time logic: expiry boundaries, replay windows, clock skew, timezone
  differences between components.
- Default and fallback posture: missing config, disabled feature flag,
  unavailable dependency, mid-migration state.

## Feature Abuse and Data Leakage

Legitimate features used for unintended purposes:

- Export and backup as exfiltration: a low-privilege user triggering an
  export that includes data above their access level, other users' data,
  deleted, draft, or supposedly pruned content.
- Import and restore as injection: overwriting existing records,
  bypassing validation, injecting into collections the user cannot write.
- Search, filter, and sort as oracle: existence probes for inaccessible
  content; hidden field values revealed through result ordering.
- Enumeration through side effects: differing errors for "missing" versus
  "denied", differing timing and response size, reset and invite flows.
- Preview and draft leakage: preview tokens scoped beyond one item;
  drafts discoverable through search, feeds, or listing endpoints; CDN
  caching private content.
- Notification and webhook URLs as SSRF: server-fetched callbacks without
  internal-network validation, including after redirects.

## Chained Vulnerabilities

Individually contained behavior becomes a vulnerability when a later step
relies on a stronger guarantee:

- Multi-step boundary failures: connect only concrete outputs of a
  low-privilege principal to later trust decisions; confirm each
  prerequisite, never assume the downstream effect.
- Cross-component trust gaps: the guarantee component A produces versus
  what component B assumes — truncation, type coercion, normalization,
  tenant scope, plugin access.
- Second-order use: a stored field name becomes a JSON path, a slug a
  file path, escaped text enters raw rendering, a stored string becomes a
  URL, regex, or template.
- Scope growth: token, API-key, plugin, OAuth, or agent capabilities
  widening after delegation, refresh, caching, role change, or
  composition.
- Timing and ordering: setup, migration, soft-delete, revoke and cache
  expiry, check-versus-use windows; confirm stale state is accepted
  before reporting.
- Rollback and recovery: undelete, restore, revision rollback, and
  cancellation re-applying current ownership, validation, and
  authorization.

## Wildcard

No assigned category: find vulnerabilities outside the standard classes.
Read the code that looks boring or disconnected from security; follow
incomplete, experimental, compatibility, and fallback features. Starting
points: the strangest code and why it exists; half-finished features that
got the least review; API calls possible but never made by the client;
undocumented endpoints, parameters, headers, and features in route
registrations and middleware; mixing features not designed together —
localization with preview and caching, import with plugins and webhooks;
git history — reverted security fixes, commented-out auth, removed
secrets; valid-account actions affecting other users, shared integrity,
or operator cost; irreversible operations and whether approval binds the
final principal, action, and resource; environment assumptions — local
database, accurate clock, trustworthy DNS, case-sensitive filesystem;
what the tests do not cover versus what they do.

Pursue anomalies until the invariant is settled: if a comment explains why
code is safe, verify the explanation; if a variable is named `temp`,
`hack`, or `legacy`, read it closely.

## Obvious Things

The basic exposures everyone assumes someone else checked. Be thorough and
literal; check every item:

- Hardcoded passwords, API keys, tokens, secrets — grep `password`,
  `secret`, `apikey`, `token`, `Bearer`, `-----BEGIN`, default
  passwords.
- TODO, FIXME, HACK, XXX comments referencing security — "add auth",
  "validate input", "skip permission check".
- Debug or dev mode reachable in production through an environment
  variable, query parameter, or header.
- Test, example, or seed credentials that work in production.
- Unprotected `/debug`, `/admin`, `/test`, `/status`, `/metrics`,
  `/env`, `/config` endpoints.
- `.env`, `.env.local`, `credentials.json`, `*.pem`, `*.key` committed;
  a `.gitignore` that actually covers secrets, uploads, local config.
- Unpinned dependencies; known CVEs in the lockfile.
- `eval()`, `exec()`, `child_process`, `Function()`, `vm` escapes,
  dynamic `import()` with untrusted input.
- CORS `*` or reflected origins with credentials; cookies missing
  `HttpOnly`, `Secure`, `SameSite`.
- Open redirects through `redirect`, `return`, `next`, `url`, `goto`,
  `continue` parameters; HTTP-only endpoints; stack traces, internal
  paths, or SQL errors in production responses.

A flag is not a finding — trace the impact. A cookie missing `HttpOnly`
matters only if it holds security-sensitive data no script reads by
design; an error field matters only if it is ever populated with
sensitive data.
