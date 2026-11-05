# AI and LLM Hunting

Use when a language model participates in a trust-sensitive decision:
chatbots, RAG pipelines, persistent agent memory, tool-calling loops, MCP
servers and clients, prompts assembled from untrusted input, or model
output that reaches a sink. The flow under review is untrusted content
into a model, memory, or tool layer, then into capability, authority, or
a sink. Transport, access control, and filesystem use stay with the core
classes; this file covers the delegation layer.

## Core Discipline

- Prompt injection alone is not a finding. Require a code-level boundary
  failure: content reaching another principal's context, invoking
  authority the requester lacks, disclosing data they cannot read, or
  driving a sink they cannot reach directly.
- Model output, memory, tool descriptions, and MCP responses are untrusted
  inputs. Point to the code that grants authority, trusts output, writes
  durable state, or feeds a sink.
- A guardrail prompt is not a security boundary. Count only deterministic
  checks, resource-scoped authorization, isolation, binding, and
  constrained credentials.
- State attacker, affected principal, effective execution identity,
  resource, exact action, authority used, and observable impact. A direct
  request exercising the requester's own authority is not a delegation
  defect merely because a model executes it.
- Authorization and action binding are separate controls. Attacker
  content causing an action under a principal's valid authority is an
  action-binding failure when that principal did not intentionally
  request or approve the exact action.

## Context and Memory Classes

- **Indirect injection through retrieved content**: attacker-written
  documents, indexed pages, files, issues, tool responses, or metadata
  entering another principal's model context. Trace who writes each
  source, how retrieval scopes it, whose session consumes it, and what
  capability is enabled there.
- **Cross-session or cross-tenant bleed**: conversation history,
  embeddings, retrieval results, or prompt caches keyed too broadly.
  Verify tenant and ACL filters in the query itself and every cache key;
  a tenant field on an object is not enforcement if an alternate path
  omits it.
- **Persistent memory poisoning**: attacker-controlled content or model
  summaries written into memory that later shapes another task, user, or
  privileged session. Review who may create, update, and delete memory,
  its provenance and tenant scope, and whether low-trust observations
  become durable instructions.
- **Role and provenance confusion**: prompt assembly letting untrusted
  text impersonate a system message, prior turn, tool result, policy, or
  memory record — string concatenation, untyped history, caller-controlled
  role fields. Confirm the forged provenance changes a deterministic trust
  decision.

## Tool and Action Classes

- **Tool-argument injection into sinks**: model-produced arguments
  reaching SQL, shell, file, URL-fetch, or privileged APIs without
  handler-side validation. Treat the tool schema as input parsing; a
  schema narrows shape, not authorization, safe paths, or query
  semantics.
- **Excessive agency and confused deputy**: the agent runs under a service
  identity while the handler skips the requesting principal's permission
  on the named resource. Prove the caller could not perform that exact
  operation through the normal product interface.
- **Action-confirmation binding**: approving one described action while
  execution uses changed arguments, a different resource or principal, or
  a later model turn. Bind approval to the normalized tool name, complete
  argument object, requester, target, expiry, and batch membership; an
  approval must not authorize a mutated or duplicate side effect on retry
  or resume.
- **Schema and dispatcher disagreement**: the schema accepting aliases,
  extra fields, duplicate keys, coercions, or out-of-range values the
  dispatcher interprets differently; compare the validated object with
  the handler's object where values become resource selectors.
- **Unbounded delegated loops**: a bounded request enqueuing repeated
  spend, send, or mutation without per-request budget, per-action
  authorization, cancellation, or idempotency.

## MCP and Sub-agent Classes

- **Trust inheritance**: a delegated task receiving the full session,
  credentials, memory, or capabilities instead of least authority. Check
  the principal and tenant carried into each call, credential audience,
  and whether delegated results are treated as untrusted on return.
- **Server and tool identity confusion**: routing by attacker-influenceable
  server names, tool names, request IDs, resource URIs, or model-selected
  aliases rather than the authenticated connection and outstanding
  request; whether two servers can claim one tool identity and a response
  from one can satisfy another's pending call.
- **Metadata as policy**: tool descriptions, resource metadata, prompts,
  or schemas from an MCP peer trusted as authorization. They can guide
  the model but never grant capability; find the deterministic allowlist
  and handler authorization that stay authoritative.

## Output Classes

- **Insecure output rendering**: model output reaching an executing HTML,
  Markdown, template, URL, or command sink without the sink's required
  encoding and policy. Renderer behavior outside the repository makes the
  candidate `needs_validation`.
- **Sensitive context extraction**: credentials, another user's data,
  private source, or access-granting policy values assembled into context
  and exposed through user-influenced output. Disclosure of generic
  instructions crosses no data boundary.

## Moves and Validation

Draw four maps first — execution identities, capabilities, writable
context and memory sources, output destinations — then connect the
principal at the start to the authority at the end. Start at
side-effecting tools and work backward through dispatcher, schema,
confirmation, model context, and retrieval; start at durable memory reads
and trace every writer. Compare direct, queued, retry, resume, batch, and
delegated paths for the same action: the strongest gate must apply after
arguments are final and before every side effect.

Before reporting: name the crossed boundary and observable result. For
confused-deputy claims, prove the tool lacks requester-and-resource
authorization and the attacker cannot act normally; for action-binding
claims, prove attacker content caused an action the principal did not
approve. For memory and retrieval claims, cite both the attacker-controlled
write and the later cross-principal read or privileged decision. For MCP
identity claims, verify the authenticated connection, request correlation,
tool namespace, and effective credential — external server identity or
deployment routing is `needs_validation`.
