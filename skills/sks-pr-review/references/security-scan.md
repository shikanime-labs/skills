# Security Scan (added lines only)

Run against the staged/working diff. Any match is `blocking` — reported, not
fixed (reviewer never patches). Reuse the patterns from `requesting-code-review`
(they already encode the shikanime trust-boundary lessons: Keycloak/JWKS
timeouts, client-binding on `aud`/`azp`, Prisma vs contract types).

```bash
# scope the added lines
jj diff --stat
jj diff --name-only
DIFF=$(jj diff)   # or: jj diff --from main --to @

# hard-coded secrets
echo "$DIFF" | grep "^[+]" | grep -iE '(api_key|secret|password|token|passwd)\s*=\s*['"'"'"]<[^'"'"'"]{6,}>['"'"'"]'

# shell / command injection
echo "$DIFF" | grep "^[+]" | grep -E 'os\.system\(|subprocess.*shell=True'
# also: string-built shell args -> subprocess.run([...], shell=False)

# dangerous eval/exec
echo "$DIFF" | grep "^[+]" | grep -E '\beval\(|\bexec\('

# unsafe deserialization
echo "$DIFF" | grep "^[+]" | grep -E 'pickle\.loads?\('

# SQL injection (f-string / .format in queries)
echo "$DIFF" | grep "^[+]" | grep -E 'execute\(f"|\.format\(.*SELECT|\.format\(.*INSERT'
```

## Auth / trust-boundary (blocking if missing)

- Keycloak/JWT/OIDC: token bound to backend `aud`/`azp`/client-id, not
  realm-only; JWKS fetch has a timeout + safe cache/refresh (no
  hang-on-network). Both cache-hit and cache-miss `kid` paths verified.
- NestJS+Prisma: raw Prisma model fixtures use generated client types
  (`bigint`/`Date`); shared contract serializes to strings — don't conflate.
- Web/HTML: `element.textContent` not `innerHTML = userInput` (XSS).
- File paths validated (no traversal); external calls wrapped in error handling.

## Output

List every match as a `blocking` finding anchored at file:line. If clean, state
"security scan: clean" in the summary.
