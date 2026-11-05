# Desktop and Local IPC Hunting

Use when the target is a desktop or mobile app, privileged helper,
updater, local daemon, webview host, deep-link handler, browser
native-messaging host, or local IPC client or server. The untrusted actor
may be a downloaded document, remote web content, another local app,
another OS user, a sandboxed process, or a lower-privilege account —
state that starting capability instead of treating all local users as
equivalent.

## Core Discipline

- Establish the realistic attacker — another app, another OS user, a
  sandboxed child, an untrusted document, a remote origin. Self-harm
  within the same account and authority is not a boundary violation.
- Paths, process names, bundle IDs, and claimed sender fields are not
  peer authentication. Use OS peer credentials, code identity,
  capability handles, or protected channel state.
- The native bridge or helper must authorize each operation and final
  resource after parsing. A trusted UI or broker does not make
  attacker-influenceable arguments trusted.
- OS sandbox, signing, entitlements, permissions, keychain ACLs,
  exported-component policy, and prompt behavior are real controls when
  pinned and visible.
- `confirmed` for source evidence plus bounded local or emulator tests.
  Signing, manifest merge, OS version, device policy, installer ACL, or
  packaging required but not observable is `needs_validation`.

## Deep Link and Handoff Classes

- **Custom-scheme and deep-link ambiguity**: another app or page invoking
  a route that mutates state, imports data, completes authentication, or
  selects an account without current-session and one-time callback
  binding. Review URI normalization, duplicate query fields, scheme,
  host, and path matching, exported handler policy, stale and replayed
  links.
- **App and account handoff confusion**: OAuth, SSO, magic-link,
  invite, device pairing, or payment callbacks returning to the wrong
  installed app, profile, tenant, or pending transaction. Bind state to
  the initiating app identity, current session, account, provider,
  operation, expiry.
- **File-open and intent confusion**: an associated file, share intent,
  drag-and-drop item, pasteboard record, notification action, or
  open-file event triggering a privileged operation without confirming
  content type, sender trust, current user intent, and final target.

## Webview and Bridge Classes

- **Navigation-origin to bridge confusion**: remote or
  attacker-controlled frames reaching a JavaScript or native bridge
  intended for packaged content. Validate origin at call time and after
  every navigation, redirect, subframe, popup, and error page — URL
  prefix checks and initial-load checks are insufficient.
- **Over-broad bridge capabilities**: web content selecting arbitrary
  files, commands, IPC methods, credentials, or system actions through a
  generic bridge. Check method allowlists, normalized arguments, user
  authority, confirmation requirements, return-value disclosure.
- **Webview file and universal access**: remote content reading
  app-local files, privileged custom schemes, or internal origins
  because file access, universal access, mixed content, debug
  interfaces, or custom protocol handlers join origins unexpectedly.

## IPC and Exported Component Classes

- **Peer-authentication gaps**: Unix sockets, named pipes, XPC, Binder,
  D-Bus, native messaging, shared memory, or loopback listeners
  accepting a lower-trust peer without checking OS credentials, code
  identity, sandbox token, or channel ownership. Require a meaningful
  method or disclosure behind the channel.
- **Claimed principal versus channel identity**: the authenticated
  process or channel belonging to one app or user while request fields
  select another user, tenant, profile, or capability. Bind each method
  and resource to the peer credential, not a caller-declared identifier.
- **Exported component overreach**: a mobile component or local
  automation endpoint externally invokable performing an operation
  intended for the app itself. Review final merged manifests, intent
  filters, permission and signature level, path grants, aliases.
- **Lifecycle and correlation confusion**: predictable request IDs,
  reused handles, stale channels, inherited descriptors, world-writable
  socket paths, or restart behavior letting one peer answer, cancel, or
  reuse another peer's operation. Review creation permissions and
  cleanup of socket files, locks, ports, shared mappings.

## Helper and Local File Classes

- **Privileged helper as confused deputy**: a low-privilege caller
  selecting a privileged command, file, service, user, or system setting
  without per-operation authorization. Review sudo, polkit, UAC, and XPC
  helper rules; the helper must independently validate normalized
  arguments.
- **Install and update path trust**: a privileged installer or helper
  reading manifests, scripts, packages, symlinks, working directories,
  or repair state writable by a lower-trust actor after authorization.
  Bind authorization to immutable content and safe destination paths.
- **Local file ownership and TOCTOU**: the app checking a path then
  following replacement, symlink, mount, or case-normalization changes
  during a privileged read or write. Use descriptor-relative operations
  and verify final ownership.
- **Credential-store boundary mismatch**: a keychain item, token file,
  backup, log, clipboard, notification preview, or local config
  readable by another app, profile, or user with less authority.
  Plaintext readable only by the same intended OS account is not
  automatically a vulnerability; state the lower-trust reader and the
  credential's power.

## State and Lifecycle Classes

- **Account switch and restore leakage**: cached data, background tasks,
  widgets, notifications, local databases, webview storage, or biometric
  approvals surviving logout or account change and appearing under a
  later account. Review backup, restore, and multi-profile behavior.
- **Pending-action and user-presence confusion**: a notification,
  widget, shortcut, share sheet, biometric prompt, or deferred operation
  authorizing a different action than displayed, executing after
  expiry, or using another profile's pending state. Bind confirmation
  to normalized action, resource, account, current foreground state.

## Moves and Validation

Enumerate every process, app component, local endpoint, URI scheme, file
association, webview origin, and helper; record OS identity, runtime
privilege, caller, callable operation. Read final packaging inputs —
merged manifest, entitlements, installer rules, native-messaging
registration, protocol handlers, ACL creation — source declarations are
overwritten downstream. Validate with dummy profiles and non-sensitive
local fixtures on an isolated machine or emulator; never interact with
other users' apps, credentials, or production services.

Before reporting: name the attacker starting capability, the OS or app
principal crossed, the entry channel, the accepted argument or state, and
the unauthorized operation or disclosure. Confirm which OS sandbox, peer
credential, signing, entitlement, permission, consent, and installer
controls apply; unknown packaging or runtime facts are `needs_validation`.
For webview bridges cite both the navigation control and the privileged
native sink; for IPC, peer authentication and per-resource authorization;
for helpers, the final normalized destination. Stop after proving the
boundary result.
