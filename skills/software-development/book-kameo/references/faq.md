# FAQ (distilled)

Source: `docs/faq.mdx`.

## Networking

- Uses **libp2p**; **Kademlia DHT** under the hood for registration/lookup. No predefined schema; messages routed via multiaddresses (TCP/IP, QUIC, etc.).

## Query actor state

- `ask` a query message (no state mutation):

  ```rust
  let result = actor_ref.ask(QueryState).await?;
  ```

- Prefer a **push model**: actors notify each other of state changes → less constant querying, more decoupled.

## Kameo vs gRPC

- gRPC needs predefined schemas + codegen/boilerplate. Kameo: dynamic cross-node communication via `RemoteActorRef`, messages passed like local actors; no schema management.

## Why async?

- Multiple actors run on one thread via Tokio (efficient for IO-bound). async keeps non-blocking tasks (network) from stalling others even when some are CPU-bound.

## Parallel / multi-core

- Yes: Tokio `rt-multi-thread` spreads actors across cores for parallel workloads.

## Production-ready?

- Relatively new, active development, API has iterated. Tested in real projects but not yet widely adopted in production; maturing fast.

## Why sequential message processing?

- Maintains consistency/correctness; state changes in well-defined order — critical where order matters.

## Why does my actor stop unexpectedly?

One of:

- All `ActorRef<MyActor>` dropped.
- Explicitly stopped (`.stop_gracefully()` / `.kill()`).
- `on_start` returns an error.
- `on_panic` returns `Ok(ControlFlow::Break(reason))` or an error.
- `on_link_died` returns `Break` or an error.
- `Actor::next` returns `None`.
- → Double-check each when debugging a stop.

## vs Actix / Ractor

- **Actix**: Kameo simpler API, less boilerplate (esp. async); Actix runtime changed over time, Kameo built directly on Tokio.
- **Ractor**: Kameo messages are separate structs with own `Message` trait; Ractor uses one enum. Kameo: actor IS the state; Ractor separates state and actor.
