# Client-Side and Browser Hunting

Use when meaningful trust decisions or untrusted rendering happen in a
browser: single-page apps, extensions, embedded webviews, service
workers, offline applications, and code rendering attacker-influenceable
content into the DOM, receiving cross-window messages, or using browser
storage. These paths include sources the server never sees — URL
fragments, `window.name`, `postMessage`, previously cached content.

## Core Discipline

- A client-side candidate needs a controllable source and an executing or
  disclosing sink. Name both and show attacker-influenced data reaching
  the sink.
- Impact must reach a victim session, another origin, or shared
  persistence. Self-injection and disclosure of the attacker's own data
  are not findings.
- Framework escaping, same-origin policy, CSP, COOP and CORP,
  service-worker scope, and modern noopener defaults are real controls;
  verify them before assigning impact.
- Browser storage and caches are shared by origin and outlive login state.
  Identify who writes, who reads, and which account, tenant, or worker
  lifecycle clears each record.
- `confirmed` only for complete source evidence plus bounded local
  browser tests. Renderer behavior, extension permissions, deployed
  headers, and browser policy outside the repository are
  `needs_validation`.

## DOM and State Classes

- **DOM-based XSS**: `location` fields, `document.referrer`,
  `window.name`, message data, storage, and document state flowing into
  `innerHTML`, `document.write`, string-evaluating APIs, executable URLs,
  jQuery HTML APIs, or framework escape hatches. Framework-escaped
  interpolation is not a finding.
- **DOM clobbering**: attacker-injected `id` or `name` attributes
  shadowing a global, form property, configuration object, or
  initialization flag later trusted by code. Require both a markup path
  that preserves the attribute and a security-relevant use of the
  clobbered value.
- **Prototype pollution with gadget**: an attacker-controlled key
  reaching a recursive write — deep merge, path assignment — modifying
  prototype state, then a reachable gadget consuming the polluted
  property. `JSON.parse`, a shallow copy, or pollution without a gadget
  is not enough.

## Messaging and Network Classes

- **`postMessage` origin trust**: a handler acting on `event.data`
  without an exact origin allowlist and the expected `event.source`;
  sensitive data sent to `*` reaching an unintended embedder. Substring,
  prefix, or unanchored-regex matching is not an origin check.
- **Cross-site WebSocket hijacking**: an upgrade accepting ambient cookies
  from an untrusted origin without an Origin check or channel token,
  letting the victim session read or mutate data. Confirm both the
  upgrade behavior and a security-relevant message handler.
- **Credentialed CORS trust**: the server reflecting or weakly matching
  Origin while allowing credentials and returning sensitive responses.
  Report the actual reflected or allowed origin path and the cross-origin
  data or mutation, not a bare wildcard browsers already reject.

## Worker and Storage Classes

- **Service-worker scope takeover**: attacker-influenceable content
  becoming the registered worker script, controlling a path through an
  over-broad `Service-Worker-Allowed` scope, or altering update imports
  without integrity control. Verify the final script URL, MIME type,
  origin, scope, and who controls every imported script.
- **Worker cache identity confusion**: a worker caching personalized
  responses without account, tenant, authorization, or request mode in
  its policy, serving them after account switch or logout. Review
  fetch-event routing, cache names and keys, navigation fallbacks,
  cleanup, and error paths returning another user's response.
- **Storage disclosure and stale authorization**: tokens, private
  responses, draft data, or authorization decisions persisting in
  localStorage, sessionStorage, IndexedDB, Cache Storage, or extension
  storage and becoming readable by another account or a less-trusted
  same-origin component. Storage of a token alone is not a finding;
  require a realistic reader with less authority or continued use after
  revocation.
- **Cross-context confusion**: `storage` events, BroadcastChannel, shared
  workers, or origin-wide caches carrying identity or commands between
  tabs without binding to the current session — account switching,
  private windows, tenant changes, stale tabs overwriting newer auth
  state.

## Leak and Navigation Classes

- **XS-Leaks**: an attacker page distinguishing protected cross-origin
  state through load or error events, frame state, redirects, timing,
  cache state, or response size while the browser attaches victim
  credentials. Require a concrete secret-bearing predicate; generic
  timing variance is not a finding.
- **Window and opener disclosure**: permitted metadata or navigation
  results revealing protected state; a retained opener relationship
  letting an attacker page influence a privileged navigation. Check COOP,
  frame protections, `noopener`, exact origin.
- **Clickjacking**: a framed state-changing action lacking effective
  `frame-ancestors` or `X-Frame-Options`. Require the sensitive action to
  complete in the framed state; missing headers on read-only content stay
  hardening.
- **Navigation confusion**: a client source controlling redirect or
  navigation without scheme and destination policy, including
  `javascript:` and `data:` destinations. Reverse tabnabbing only where
  code keeps `window.opener` or supports a browser without implicit
  `noopener`.

## Moves and Validation

Start from DOM, navigation, worker, message, and storage sinks and trace
backward to browser-only and server-controlled sources, recording the
browser policy that should stop the path. Test account switch, logout,
worker update, offline fallback, and stale-tab state with a local test
origin and dummy accounts. For XS-Leaks, list only predicates proved by
source and local browser behavior, then identify the header or rendering
choice that removes the oracle.

Before reporting: cite source, sink, browser policy, affected origin or
session, and the observable mutation or disclosure. For prototype
pollution, prove the recursive write and the gadget; for clobbering, the
markup survival and the trusted use; for workers and storage, lifecycle
reachability — an attacker-controlled write must reach a different
account, tenant, or later authorization state; for messaging, CORS,
WebSocket, and XS-Leaks, show the exact origin or source validation and
confirm CSP, COOP, cookies, and SameSite do not already block the path.
