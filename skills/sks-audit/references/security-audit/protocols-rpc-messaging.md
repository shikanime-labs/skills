# Protocols and Messaging Hunting

Use when the target uses gRPC, GraphQL transports, Protobuf, Cap'n Proto,
Thrift, custom binary protocols, streaming RPC, webhooks, brokers,
queues, pub/sub, or event buses — peer identity, message interpretation,
routing, replay, ordering, and delivery semantics. Parser memory safety
belongs to the memory-safety companion; HTTP framing to the web
companion.

## Core Discipline

- "Internal" is not authentication. Name the peer identity at every hop
  and show how it becomes the application principal used for
  authorization.
- Schema validation proves message shape, not provenance, resource
  authority, ordering, or safe values. Follow decoded fields to policy
  and side effects.
- Broker guarantees and application guarantees differ. Write down retry,
  ordering, acknowledgement, deduplication, and transaction behavior
  before evaluating state changes.
- Parser disagreement requires two concrete consumers, schema versions,
  or wire representations and one security-relevant divergent value.
- `confirmed` for source-complete paths plus bounded local
  producer-consumer tests. Broker ACL, service-mesh identity, topic
  attachment, or compatibility behavior outside the repository is
  `needs_validation`.

## Framing and Interpretation Classes

- **Boundary and canonicalization disagreement**: components disagreeing
  on length, compression, duplicate fields, unknown fields, encoding,
  numeric width, normalization, or envelope-versus-body precedence.
  Compare generated and custom parsers, gateways, language bindings,
  version converters; confirm which principal, resource, or operation
  differs after decoding.
- **Union, enum, and default confusion**: unknown variants, missing
  discriminators, zero values, default privileges, or compatibility
  mappings reaching code that assumes a validated case. Review exhaustive
  dispatch, default branches, and how old consumers interpret newly added
  fields.
- **Envelope and payload identity mismatch**: authorization trusting
  routing or envelope metadata while the handler acts on a conflicting
  tenant, account, subject, or sender in the body. Identify the
  authoritative source and ensure clients cannot override it.

## Identity and Authorization Classes

- **Interceptor and path inconsistency**: an auth interceptor applying to
  unary methods but not streams, reflection, health, gateway-transcoded,
  or compatibility services. Compare every registration and route to the
  same operation.
- **Peer identity to principal confusion**: mTLS, workload identity,
  bearer metadata, or broker credentials authenticating a channel while a
  caller-controlled field selects the user or tenant. Channel identity
  and claimed principal must be bound by deterministic policy.
- **Per-item and streaming gaps**: a stream, subscription, or batch
  authorized once, then later items naming different resources or
  continuing after role, membership, or token revocation. Re-check where
  scope can change; bind subscriptions to their original principal.
- **Callback and reply confusion**: predictable, reused, or cross-tenant
  correlation IDs letting a response, webhook, cancellation, or
  acknowledgment satisfy another caller's pending operation. Bind each
  outstanding request to authenticated peer, tenant, operation,
  lifecycle.

## Broker and Queue Classes

- **Topic and subscription scope gaps**: a publisher or subscriber
  selecting another tenant's topic, wildcard, consumer group, partition,
  reply queue, or dead-letter route. Check broker-enforced ACLs where
  visible and application-side namespace construction; tenant text
  inside a payload is not isolation.
- **Dead-letter and diagnostic disclosure**: messages routed to dead-letter
  queues, error topics, tracing, or operator views containing secrets or
  cross-tenant payloads accessible to a lower-trust consumer. Review
  redaction at the failure path, not just normal delivery.
- **Untrusted producer as control plane**: a message body declaring
  itself an admin event, provider callback, replication record, or
  migration instruction without an independently authenticated producer
  and event type. Verify signatures and source, account, and audience
  binding before privileged handling.

## Replay and Transaction Classes

- **Duplicate delivery and idempotency gaps**: retries or redelivery
  repeating a side effect because deduplication is absent, occurs after
  mutation, or uses a key that collides across tenants or operations.
- **Out-of-order and stale acceptance**: older state, revoked membership,
  canceled work, or pre-step-up authorization arriving after newer state
  and overwriting it. Review sequence and version checks, tombstones,
  partition changes, restore and replay workflows.
- **Acknowledgment ordering defects**: acknowledgment before durable
  commit losing security-relevant work; commit before an unreliable
  acknowledgment duplicating a mutation. Evaluate outbox and inbox
  behavior and failure recovery.
- **Partial multi-consumer transitions**: several consumers jointly
  implementing one authorization or business transition, with retries and
  partial failure leaving a subset committed. Identify invariants that
  must become durable atomically or compensate with current
  authorization.

## Moves and Validation

Draw producer, broker or transport, gateway, consumer, storage for each
message family; at each hop record the authenticated peer, authoritative
tenant and resource fields, validation, and side effect. Feed the same
small fixture to every in-repo schema version or language binding; test
duplicate, missing, unknown, boundary, replayed, and reordered messages
without producing load. Compare normal, retry, dead-letter, replay,
migration, reflection, stream, and transcoded routes — security policy
must survive transport changes.

Before reporting: name the realistic producer or peer, accepted message,
authenticated channel identity, affected principal or resource, and the
unauthorized mutation or disclosure. For disagreement claims, cite both
parsers or consumers and the divergent decoded value — safe rejection by
either side prevents confirmation. For replay and ordering claims,
establish actual delivery guarantees and reproduce the invariant failure
with a bounded in-memory transport. For authorization and isolation,
verify every interceptor, broker ACL, gateway, and consumer layer visible
in source; external attachments make the candidate `needs_validation`.
