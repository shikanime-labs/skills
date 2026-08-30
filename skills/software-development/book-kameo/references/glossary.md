# Glossary

Key Kameo terms with cross-references to skill reference files.

- **Actor** — unit encapsulating state + behavior, runs in its own async task, processes messages sequentially. See `references/actors.md`.
- **ActorRef<T>** — reference to a spawned actor; used to `ask`/`tell`. See `references/actors.md`, `references/requests.md`.
- **Message** — any static type handled via `impl Message<T>`; processed one-at-a-time with `&mut self`. See `references/messages.md`.
- **Message trait** — `Message<T>: Actor { type Reply: Reply; async fn handle(&mut self, msg, ctx) -> Reply }`. See `references/messages.md`.
- **Reply / Reply trait** — type sent back to caller; `#[derive(Reply)]` for custom. Errors via `tell` become panics. See `references/replies.md`.
- **ask** — send + await reply (`ask(&msg)`). Errors surface as `SendError::HandlerError`. See `references/requests.md`.
- **tell** — fire-and-forget (`tell(msg)`, by value). Handler errors become panics. See `references/requests.md`.
- **ctx.pipe / ctx.pipe_with** — run a future off-thread, deliver result back as a self-message; keeps mailbox unblocked. See `references/messages.md`.
- **Mailbox** — per-actor queue; bounded (default cap 64) or unbounded; bounded enables backpressure. See `references/actors.md`.
- **mailbox_timeout / reply_timeout** — bounded-queue wait / reply wait limits for ask/tell. See `references/requests.md`.
- **Supervision tree** — parent-child restart management (Erlang/OTP style). See `references/supervision.md`.
- **SupervisionStrategy** — `OneForOne` (default) / `OneForAll` / `RestForOne`. See `references/supervision.md`.
- **RestartPolicy** — `Permanent` (default) / `Transient` / `Never`. See `references/supervision.md`.
- **Restart limit** — default 5 restarts / 5s; `.restart_limit(n, dur)`. See `references/supervision.md`.
- **Actor linking** — peer-to-peer monitoring via `link`/`link_remote`; handle in `on_link_died` with `ControlFlow`. See `references/supervision.md`.
- **RemoteActor** — `#[derive(RemoteActor)]`; required for an actor to be messaged across nodes. See `references/distributed-messaging.md`.
- **RemoteActorRef** — reference to an actor on a (possibly remote) node; same ask/tell API. See `references/distributed-registry.md`, `references/distributed-messaging.md`.
- **#[remote_message]** — annotates a handler; assigns a crate-unique ID for linkme-based routing. See `references/distributed-messaging.md`.
- **bootstrap() / bootstrap_on()** — one-line swarm setup (mDNS, dev only). See `references/distributed-swarm.md`.
- **remote::Behaviour** — libp2p `NetworkBehaviour` for composing Kameo into a custom swarm. See `references/distributed-swarm.md`.
- **Kademlia DHT** — decentralized registry for actor name → reference lookup. See `references/distributed-registry.md`.
- **ActorStopReason** — why an actor stopped; includes `PeerDisconnected` for remote link death. See `references/supervision.md`.
- **console / metrics / hotpath** — observability features (cargo features). See `references/observability.md`.
- **linkme** — crate Kameo uses at link time to build the remote-message dispatch HashMap. See `references/distributed-messaging.md`.
