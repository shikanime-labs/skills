# Availability and Exhaustion Hunting

Use when untrusted requests, messages, files, tenant state, or agent work
can consume CPU, memory, disk, connections, worker slots, paid APIs, or
queue capacity, or can deadlock or crash a shared service. This companion
separates a source-reviewable availability vulnerability from a general
performance issue. Never validate by stressing a shared or live service.

## Core Discipline

- Require an input-to-cost path, a missing effective bound, and impact on
  another user, shared service, safety function, or operator-owned spend.
  Self-limiting work in the requester's own process is not a service
  vulnerability.
- A missing rate limit is not enough. Check body, message, and file caps,
  concurrency, queues, deadlines, database constraints, upstream
  gateways, and per-tenant quotas before calling a path unbounded.
- Do not run stress, saturation, or production tests. Use asymptotic
  analysis, small boundary fixtures, mocked paid calls, strict local
  resource limits, deterministic cancellation tests.
- State attacker cost, service work, persistence, scope, and recovery.
  One bounded input with superlinear or persistent shared effect differs
  materially from sustained volume.
- `confirmed` for source-visible bounds failures demonstrated safely.
  Upstream caps, deployed topology, autoscaling, paid quota, or recovery
  behavior outside the repository is `needs_validation`.

## Amplification Classes

- **Superlinear parsing, matching, evaluation**: small accepted input
  driving catastrophic regex backtracking, nested parsing, recursive
  validation, symbolic evaluation, graph traversal, template expansion,
  adversarial sort or hash behavior. Derive accepted depth and
  cardinality, then demonstrate a bounded growth curve locally.
- **Decompression and representation amplification**: compressed, sparse,
  nested, aliased, or encoded input expanding far beyond the checked
  transfer or file size. Verify limits after every expansion stage —
  archives, images, fonts, structured documents, protocol compression
  tables.
- **Database and downstream query amplification**: a small request
  creating broad scans, pathological joins, fan-out, unbounded sort or
  aggregation, or many downstream calls because depth, filter
  cardinality, pagination, or expansion fields are unbounded. Confirm
  authorization does not intentionally permit the same resource scope.

## Accumulation Classes

- **Unbounded buffering and cardinality**: bodies, out-of-order streams,
  uploads, sessions, unique cache keys, metrics labels, subscriptions, or
  pending jobs accumulating without per-item and aggregate limits. Find
  cleanup and expiration on disconnect, timeout, cancellation, partial
  parse.
- **Descriptor and handle leaks**: malformed or canceled work missing
  cleanup and retaining sockets, files, cursors, timers, subprocesses,
  temporary files, object references. Confirm the leak repeats through
  bounded local iterations and affects a shared pool.
- **Detached work after cancellation**: client timeout, disconnect,
  canceled job, or failed authorization returning control while database,
  model, network, or worker work keeps running. Trace cancellation and
  deadline propagation through every layer.

## Quota and Scheduling Classes

- **Pre-authentication work imbalance**: expensive parsing, key lookup,
  cryptography, decompression, or external requests happening before
  authentication and the earliest size or rate gate. Compare minimal
  requester effort to shared service cost.
- **Quota accounting and reset gaps**: accounting keyed on
  attacker-influenceable IP, route, tenant, key prefix, or task ID,
  letting one principal escape its budget or consume another's
  allocation. Review integer overflow, distributed races, retries,
  reconnects, account switching.
- **Worker and priority starvation**: low-priority or attacker-controlled
  jobs holding shared locks, workers, database pools, event-loop turns,
  or scheduler priority needed by unrelated users. Require a path that
  bypasses queue or concurrency fairness or retains a slot past its
  deadline.

## Failure and Recovery Classes

- **Reachable fatal error or deadlock**: untrusted input reaching a
  panic, abort, fatal assertion, unhandled exception, process exit, lock
  cycle, or infinite loop in a shared process. Confirm supervisor scope —
  one worker or the whole service; a restarted isolated worker reduces
  impact but does not erase the defect.
- **Retry storm and fail-open amplification**: timeouts, dependency
  errors, partially processed messages, or health-check failures
  triggering synchronized or unbounded retries without jitter, ceilings,
  circuit breaking, deduplication. Verify one bounded failure source can
  create persistent aggregate work.
- **Poison record and head-of-line blocking**: one malformed record
  repeatedly failing at the front of a shared queue, partition, startup
  scan, migration, or recovery loop. Review skip and quarantine policy,
  offsets, and whether other tenants share the blocked unit.
- **Unsafe recovery and rollback**: restart, restore, fallback, or
  cleanup rebuilding unbounded state, ignoring current quotas, or
  restoring the input that immediately repeats the failure.

## Moves and Validation

Build an input-to-resource table: earliest accepted size and cardinality,
work before auth, downstream fan-out, persistence, shared pool, limit and
cleanup owner, recovery. Compare aggregate with per-object limits — ten
thousand valid one-byte items can evade a per-message cap while
exhausting process-wide state. Validate only in an isolated fixture with
strict CPU, memory, and time limits at small growth points; mock external
and paid calls; stop once the missing bound or cancellation is
observable.

Before reporting: name the untrusted input, requester work, service
amplification or retained resource, shared blast radius, and recovery —
missing limits without concrete shared impact are hardening. Confirm no
source-visible upstream, parser, queue, tenant, or framework bound
prevents the path; unknown deployed controls are `needs_validation`. For
superlinear behavior, establish the accepted complexity and bounded local
growth; for leaks, repeatable retention after cleanup should occur; for
fatal paths, identify process and supervisor isolation. Prioritize by low
requester cost, unauthenticated reachability, cross-tenant scope,
persistence, and poor recovery.
