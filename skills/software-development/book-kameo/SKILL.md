---
name: book-kameo
description: Distilled reference for the Kameo Rust actor framework.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Rust, Actors, Async, Tokio]
---

# Kameo Actor Framework Reference

Distilled map of the Kameo framework (README + The Kameo Book + the
`examples/` directory): the async actor model built on Tokio, its
message/reply/supervision primitives, the libp2p-based distributed actor
system, and copy-paste patterns for the `kameo_actors` crate (pools, pubsub,
broker, message bus/queue, streams, forwarding). Use it to write correct Kameo
code without re-reading every page.

This skill is NOT the API reference — for exact signatures, method arity, and
trait bounds, defer to `docs.rs/kameo`. It is a structured index plus
per-topic notes distilled from the official docs.

## When to Use

- "Build / write a Kameo actor", "spawn an actor", "define a message handler"
- "How do ask vs tell work in kameo", "how do I do supervision in kameo"
- "distributed actors kameo", "register / lookup a remote actor", "bootstrap swarm"
- "kameo mailbox bounded unbounded", "kameo ctx.pipe", "kameo restart policy"
- "kameo console / metrics / observability"
- "kameo examples", "kameo_actors pool/pubsub/broker/message-bus/queue", "kameo forward/attach_stream"

## Prerequisites

- Rust >= 1.88 (`rustup`). Kameo `0.22` requires it; `cargo add kameo` or pin in `Cargo.toml`.
- Tokio runtime (`#[tokio::main]`) provides the async context for spawning and messaging.
- Optional cargo features (comma-separated in `features = [...]`):
  - `remote` — distributed actors (libp2p). Required for `RemoteActor`, `bootstrap`, `RemoteActorRef`.
  - `console` — `kameo::console::serve` collector (pull-based, zero cost when off).
  - `metrics` — counters via the `metrics` crate; pair with `metrics-exporter-prometheus`/`tcp`.
  - `hotpath` — terminal TUI via the `hotpath` crate.

## How to Run

Load a topic on demand with `skill_view(name="book-kameo", file_path="references/<file>")`.
To pull a fresh upstream page, use `web_extract` on
`https://raw.githubusercontent.com/tqwewe/kameo/main/docs/<path>.mdx`.

## Quick Reference

- Define actor: `#[derive(Actor)] struct X;` + lifecycle hooks (`on_start`/`on_stop`/`on_panic`/`on_link_died`).
- Message: `impl Message<Msg> for X { type Reply = R; async fn handle(&mut self, msg, ctx) -> R }`.
- Spawn: `X::spawn(X)` -> `ActorRef<X>`; bounded mailbox default cap 64; `spawn_with_mailbox(mailbox::bounded(n) | unbounded())`; `spawn_in_thread()`.
- Send: `ref.ask(&msg).await` (expects reply) / `ref.tell(msg).await` (fire-and-forget).
- Reply: `type Reply: Reply`; `#[derive(Reply)]` for custom types; wrap in `Result<T, Infallible>` if not auto-impl'd.
- Non-blocking work: `ctx.pipe(future)` / `ctx.pipe_with(future, |actor, ctx, res| Box::pin(async {...}))`.
- Distributed: `remote::bootstrap()` or custom `SwarmBuilder` + `remote::Behaviour`; `ref.register("name").await`; `RemoteActorRef::<X>::lookup("name").await`; messages need `#[derive(RemoteActor)]` + `#[remote_message]` handler.
- Supervision: `supervise(&sup_ref, args).restart_policy(...).restart_limit(n, dur).spawn().await`; strategies `OneForOne`/`OneForAll`/`RestForOne`; policies `Permanent`/`Transient`/`Never`; default restart limit 5 / 5s.
- Linking: `a.link(&b).await`; handle in `on_link_died` returning `ControlFlow::Continue(())` / `Break(reason)`.
- Observability: `kameo::console::serve("127.0.0.1:9999")` + `kameo-console <addr>` (`--demo`); `cargo install kameo_console`.

## Procedure

1. Inventory the task: local actor vs distributed, ask vs tell, supervised or standalone.
2. Load the matching reference file via `skill_view` (file list below).
3. Apply the verbatim API shapes from that file; cross-check signatures on `docs.rs/kameo`.
4. For distributed work, enable the `remote` feature and decide bootstrap vs custom swarm.

## Pitfalls

- Tell errors become panics; default `on_panic` may stop the actor. Use `ask` (returns `SendError::HandlerError`) when the caller must see errors.
- `tell` takes ownership (`tell(msg)`); `ask` takes a reference (`ask(&msg)`).
- Awaiting a long future inside `handle` blocks the mailbox; use `ctx.pipe` to avoid head-of-line blocking.
- Actors stop when all `ActorRef`s are dropped, `on_start` errors, or a hook returns `Break`. "Unexpected stop" is usually one of these.
- `bootstrap()` uses mDNS only (same LAN), fixed transport/security — not for production. Custom swarm needed for WebSocket / relay / no-mDNS.
- `#[remote_message]` UUID must be unique within the crate; the macro builds a `linkme` HashMap at link time for deserialization routing.
- `RemoteActorRef::lookup` returns the first match; use `lookup_all` for replicas / load-balancing.

## Verification

Run `cargo build` (with the needed features) on a minimal actor + handler to confirm the derive macros and `spawn`/`ask` compile. For distributed, a two-node `bootstrap()` + `register`/`lookup` round-trip proves the path.

## Reference Index (load on demand)

- `references/getting-started.md` — install, version floor, Hello World actor + message + spawn/tell.
- `references/actors.md` — Actor trait, lifecycle hooks, mailbox, derive attrs, spawn variants.
- `references/messages.md` — Message trait, sequential processing, `ctx.pipe`/`pipe_with`.
- `references/requests.md` — ask vs tell semantics, mailbox/reply timeouts.
- `references/replies.md` — Reply trait, `#[derive(Reply)]`, error-as-panic rule.
- `references/supervision.md` — strategies, restart policies, limits, linking, spawn options.
- `references/distributed-overview.md` — architecture, libp2p/Kademlia, two setup approaches.
- `references/distributed-swarm.md` — `bootstrap()`/`bootstrap_on()` and custom `SwarmBuilder` + `Behaviour`.
- `references/distributed-registry.md` — register/lookup, `lookup_all`, DHT, retry mechanism.
- `references/distributed-messaging.md` — remote ask/tell, `RemoteActor`, `#[remote_message]`, linkme routing.
- `references/observability.md` — metrics feature, console collector + `kameo-console`, hotpath.
- `references/faq.md` — distilled FAQ: why async/sequential, actor stops, vs Actix/Ractor/gRPC.
- `references/examples.md` — copy-paste patterns: pool, pubsub, broker, message bus/queue, streams, forward, supervision, distributed, observability examples.
- `references/glossary.md` — key Kameo terms with topic cross-refs.
