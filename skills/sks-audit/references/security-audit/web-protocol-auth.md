# HTTP and Identity Hunting

Use when the target speaks HTTP at a parsing, caching, browser
authentication, or identity boundary: web apps, APIs, reverse proxies,
gateways, custom HTTP servers, and services implementing sessions, JWT,
OAuth/OIDC, SAML, MFA, passkeys, API keys, or mTLS. The core classes ask
whether a principal may perform an operation; this file asks whether the
HTTP or identity layer can confuse which principal, request, assurance
level, or token the operation belongs to.

## Core Discipline

- Framing and cache findings require two interpretations of the same
  request, response, or key. Name both components and the divergent
  normalized value on each side.
- For every credential, find the verification and every binding its role
  requires: issuer, audience, origin, relying party, client, session,
  principal, resource, assurance, expiry, one-time state.
- Host, Forwarded, X-Forwarded-*, Origin, Referer, redirect targets,
  callback state, and request-derived URLs are trust decisions; trace
  each to the affected identity or response.
- A missing header, cookie attribute, MFA prompt, or rate limit alone is
  not a finding. Require an accepted invalid request, cross-principal
  impact, assurance downgrade, or credential disclosure.
- `confirmed` only from complete source evidence plus bounded local
  request or token tests. Proxy, IdP, browser, certificate, or deployed
  configuration behavior that is not visible is `needs_validation`.

## Framing and Cache Classes

- **Request desynchronization**: front end and back end disagree on
  request length or header normalization — multiple Content-Length
  values, Transfer-Encoding, HTTP/2 or HTTP/3 downgrade, header-name
  normalization, forbidden connection headers, CR/LF conversion. Confirm
  which bytes each component assigns to the next request.
- **Cache poisoning through unkeyed input**: a request value changes
  cached content or security headers but is absent from the cache key.
  Compare key construction with every response variant — forwarded
  host and scheme, selected cookies, query normalization, language
  headers, authorization state.
- **Cache deception**: cache routing treating a private dynamic path as a
  public static asset. Compare edge cacheability with application route
  parsing and suffix or path-parameter normalization.
- **Host and forwarded-header trust**: untrusted host or proxy metadata
  selecting absolute URLs, tenant routing, callbacks, reset links, cache
  keys, or the client address authorization uses. Confirm who can supply
  the header and whether trusted ingress strips client copies.
- **Response-header injection**: untrusted data reaching Location,
  Set-Cookie, or CSP with unsafe control characters. Verify framework
  rejection and a security-relevant response change before reporting.

## Session Classes

- **CSRF**: a cookie-authenticated state-changing endpoint accepting a
  cross-site request without an effective anti-CSRF token, same-site
  binding, or strict Origin or Referer validation. Inventory every
  cookie-authenticated mutation — forms, JSON, multipart,
  method-override, legacy routes.
- **Fixation and invalidation**: session identifiers not rotated on
  login, account switch, MFA completion, or impersonation; sessions
  remaining valid after logout, password change, revocation, or account
  disable. Check server sessions, refresh tokens, signed cookies,
  websocket state, cache copies, fallback endpoints.
- **Cookie scope and transport**: over-broad Domain or Path, insecure
  transport crossing, sibling-cookie selection conflicts. Bare missing
  flags stay hardening unless a realistic less-trusted origin or network
  position gains the credential.

## Federated Identity Classes

Establish role first: authorization-server controls do not belong to a
relying-party client; verification and binding defects belong to the
component consuming the artifact.

- **JWT verification and claim binding**: signature verification,
  server-pinned algorithm and key source, exp, nbf, aud, iss; kid, jku,
  and x5u as untrusted key selectors; duplicate and header normalization;
  decode-without-verify paths. A valid token for another service is
  invalid here even when signed by a trusted issuer.
- **OAuth/OIDC request and callback binding**: exact redirect_uri
  ownership where the target is the authorization server;
  session-bound state; PKCE and code binding where applicable; ID-token
  issuer, audience, signature, nonce; selected-IdP binding in
  multi-provider flows. Compare initial callback, retry, deep-link, and
  account-link routes.
- **SAML signed-object binding**: the element whose signature is validated
  is the element used as identity. Review unsigned fallback paths, XML
  parser configuration, canonicalization differences, validity windows,
  audience, recipient, request correlation, replay state.

## Assurance and Recovery Classes

- **MFA enrollment and downgrade**: enrollment, replacement, disable,
  recovery-code generation, trusted-device creation, and fallback login
  requiring the intended prior assurance; stale or disabled factors still
  authorizing sessions.
- **Step-up binding and bypass**: a challenge upgrading the wrong session,
  account, tenant, or action; alternate routes omitting the assurance
  check. Bind challenge to principal, session, assurance target,
  operation, expiry, one-time completion.
- **WebAuthn and passkey verification**: registration binding challenge,
  RP ID, expected origin, credential, user, algorithm, and user-verification
  policy to the initiating session; authentication verifying each;
  account-discovery flows checking userHandle or credential-to-account
  confusion.
- **Account linking and identity collision**: adding an IdP, passkey,
  email, or device requiring a current authenticated session, verified
  ownership of the new identity, and callback state bound to the
  initiator; unlink and invite paths checked for verified-identifier
  collisions.
- **Password reset and recovery**: often the weakest path. Token
  randomness, user and action binding, expiry, one-time state, rate
  controls, delivery URL trust, invalidation of prior tokens and
  sessions.

## API Key and mTLS Classes

- **Key scope and resource binding**: a key acting on broader tenants,
  resources, actions, or environments than its server-side record grants;
  request parameters overriding bindings; publishable versus secret key
  confusion; rotation and revocation caches; bulk endpoints.
- **Key exposure**: keys in client bundles, URLs, redirects, logs, error
  paths, build artifacts. Confirm key type and the authority disclosure
  actually gains.
- **Peer and application-identity confusion**: trusting client-certificate
  identity headers from any network peer; mapping attacker-influenceable
  subject text to accounts; wrong trust domain, extended usage, or
  validity policy. Where a proxy terminates mTLS, only that proxy may
  connect, it must strip incoming identity headers, and the backend binds
  the sanitized identity.
- **Certificate lifecycle fallback**: expiry, revocation, or renewal
  failure silently degrading to bearer-only or anonymous operation;
  long-lived pooled connections retaining authorization after revocation.
  An in-repo fail-open branch is source-confirmable; deployed revocation
  data is `needs_validation`.

## Moves and Validation

Walk issue, store, transmit, consume, refresh, revoke for every credential
and challenge; compare normal, error, retry, migration, legacy, and
account-switch paths. Enumerate every route to the same identity and every
door to the same sensitive operation — the effective policy is the weakest
parallel path, not the polished UI. Diff parser, proxy, router, cache, and
application normalization side by side, feeding identical bounded fixtures
into each component rather than sending live traffic. For recovery and
linking, draw the account before-and-after graph; each edge names
principal, proof of the new identity, required assurance, callback
binding, and revocation effect.

Before reporting: name both components and the divergent parse or key for
framing and cache claims; cite the verification line and the missing
principal, session, resource, origin, audience, or assurance binding for
token, MFA, passkey, linking, recovery, key, and mTLS claims, proving the
server accepts the invalid transition. For CSRF, name the ambient
credential, the mutating route, the accepted cross-site request shape, and
the missing effective check — read-only actions and non-ambient bearer
routes do not qualify. Unknown framework or library defaults at unknown
versions are `needs_validation`; never convert an unverified critical
claim into a lower-severity confirmed one.
