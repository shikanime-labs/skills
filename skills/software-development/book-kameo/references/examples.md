# Examples (kameo_actors + wiring patterns)

Source: `examples/*.rs` in tqwewe/kameo. Demonstrates concrete usage of the
core API plus the `kameo_actors` crate (pools, pubsub, broker, message bus,
message queue). Load this when you need a copy-paste-shaped starting point.

> Both `kameo` and `kameo_actors` are separate crates; add `kameo_actors` to
> `Cargo.toml` for the higher-level actors below.

## Basic actor (examples/basic.rs)

- `#[derive(Actor, Default)]` on the struct; `impl Message<M>` per message.
- `type Reply = i64` (value) or `Result<(), i32>` (error).
- `ask` returns the reply; `tell` is fire-and-forget.
- **Key demo**: a handler returning `Err` via `tell` panics the actor →
  subsequent `ask` returns `Err` (actor stopped). Mirrors `references/replies.md`.

## Actor pool (examples/pool.rs)

```rust
use kameo_actors::pool::{ActorPool, Broadcast, Dispatch};
let pool = ActorPool::spawn(ActorPool::new(5, || MyActor::spawn(MyActor)));
pool.tell(Dispatch(PrintActorId)).await?;     // round-robins to a worker
pool.ask(Broadcast(ForceStop)).await?;        // sends to ALL workers
```

- Factory closure spawns each worker; pool restarts killed workers (note new IDs).
- `ctx.actor_ref().kill()` + `wait_for_shutdown()` from inside a handler.

## PubSub (examples/pubsub.rs, pubsub_filter.rs)

```rust
use kameo_actors::{DeliveryStrategy, pubsub::{PubSub, Publish, Subscribe, SubscribeFilter}};
let pubsub = PubSub::spawn(PubSub::<Msg>::new(DeliveryStrategy::Guaranteed));
pubsub.ask(Subscribe(actor_a)).await?;
pubsub.ask(SubscribeFilter(actor_b, |m: &Msg| m.0.starts_with("TopicB:"))).await?;
pubsub.ask(Publish(Msg)).await?;
```

- `SubscribeFilter(actor, predicate)` — per-subscriber message predicate.
- `DeliveryStrategy::Guaranteed` vs `BestEffort`.

## Message bus (examples/message_bus.rs)

- `MessageBus::spawn(MessageBus::new(DeliveryStrategy::Guaranteed))`.
- `Register(actor_ref.recipient())` (no topics) → `Publish(Msg)` to all registered.
- Unlike PubSub: no topic routing, just a flat registry of recipients.

## Broker with topics (examples/broker.rs)

```rust
use kameo_actors::{DeliveryStrategy, broker::{Broker, Publish, Subscribe}};
let broker_ref = Broker::spawn(Broker::new(DeliveryStrategy::Guaranteed));
broker_ref.tell(Subscribe { topic: "my-topic".parse()?, recipient: a.recipient() }).await?;
broker_ref.tell(Subscribe { topic: "my-*".parse()?, recipient: b.recipient() }).await?; // wildcard
broker_ref.tell(Publish { topic: "my-topic".to_string(), message: Echo {..} }).await?;
```

- Topics support wildcards (`my-*`); use `recipient()` (not raw `ActorRef`).

## Message queue / AMQP-style (examples/message_queue.rs, message_queue_headers.rs)

```rust
use kameo_actors::DeliveryStrategy;
use kameo_actors::message_queue::{BasicConsume, BasicPublish, ExchangeDeclare, ExchangeType, MessageQueue, QueueBind, QueueDeclare};
let amqp = MessageQueue::spawn(MessageQueue::new(DeliveryStrategy::BestEffort));
amqp.tell(ExchangeDeclare { exchange: "sensors".into(), kind: ExchangeType::Topic, ..Default::default() }).await?;
amqp.tell(QueueDeclare { queue: "temperature".into(), ..Default::default() }).await?;
amqp.tell(QueueBind { queue: "temperature".into(), exchange: "sensors".into(), routing_key: "temperature.*".into(), ..Default::default() }).await?;
amqp.tell(BasicConsume { queue: "temperature".into(), recipient: display.recipient(), tags: Default::default() }).await?;
amqp.tell(BasicPublish { exchange: "sensors".into(), routing_key: "temperature.kitchen".into(), message: TemperatureUpdate(22.5), properties: Default::default() }).await?;
```

- `message_queue_headers.rs` adds `properties`/header-based routing (same shape).
- `..Default::default()` fills the remaining `MessageQueue` command fields.

## Streams (examples/stream.rs)

```rust
impl Actor for MyActor {
    async fn on_start(state, actor_ref) -> Result<Self, Self::Error> {
        let s = Box::pin(stream::repeat(1).take(5).throttle(Duration::from_secs(1)));
        actor_ref.attach_stream(s, "1st stream", "1st stream");
        Ok(state)
    }
}
impl Message<StreamMessage<i64, &'static str, &'static str>> for MyActor {
    async fn handle(&mut self, msg, ctx) -> () {
        match msg {
            StreamMessage::Next(v) => { /* process */ }
            StreamMessage::Started(s) => {}
            StreamMessage::Finished(s) => { ctx.actor_ref().stop_gracefully().await.unwrap(); }
        }
    }
}
```

- `attach_stream(stream, started_label, finished_label)` feeds a `Stream` into
  the actor as `StreamMessage::{Next,Started,Finished}` messages.
- `actor_ref.wait_for_shutdown().await` in `main` keeps the process alive.

## Supervision tree (examples/supervision.rs)

- `fn supervision_strategy() -> SupervisionStrategy { SupervisionStrategy::OneForAll }`.
- `Child::supervise(&supervisor_ref, args).restart_limit(2, Duration::from_secs(5)).spawn().await`.
- `worker.link(&brother).await;` + `on_link_died` returning `ControlFlow::Continue(())`.
- Full detail in `references/supervision.md`.

## Forwarding (examples/forward.rs, forward_with_fallback.rs)

```rust
use kameo::reply::ForwardedReply;
impl<M> Message<ForwardToPlayer<M>> for PlayersActor
where Player: Message<M>, M: Send + 'static {
    type Reply = ForwardedReply<M, <Player as Message<M>>::Reply>;
    async fn handle(&mut self, msg, ctx) -> Self::Reply {
        let player_ref = self.player_map.get(&msg.player_id).unwrap();
        ctx.forward(player_ref, msg.message).await
    }
}
```

- `ctx.forward(target_ref, message)` re-dispatches a message to another actor
  and returns a `ForwardedReply` preserving the inner reply type.
- `forward_with_fallback.rs` adds a fallback reply path on forwarding failure
  (same `ctx.forward` entry point; consult the file for the exact fallback API).

## Macro usage (examples/macro.rs)

- Shows `#[derive(Actor)]` + `#[actor(name = "...")]` and the `Message` derive
  ergonomics; refer to `references/actors.md` / `references/getting-started.md`.

## Distributed (examples/remote.rs, custom_swarm.rs, registry.rs)

- `remote.rs`: `#[derive(Actor, RemoteActor)]`, `#[remote_message]` handler,
  `remote::bootstrap()`, `register("incrementor")`, `RemoteActorRef::lookup_all`
  loop, skip local peer. See `references/distributed-messaging.md`.
- `custom_swarm.rs`: full `SwarmBuilder` + `MyBehaviour { kameo, mdns }`,
  `init_global()`, `swarm.select_next_some()` loop, `with_max_concurrent_streams`.
  See `references/distributed-swarm.md`.
- `registry.rs`: local `register`/`ActorRef::<MyActor>::lookup` (no remote
  feature) vs remote `cfg(feature = "remote")` path. See
  `references/distributed-registry.md`.

## Observability examples

- `console.rs`: `kameo::console::serve("127.0.0.1:9999")` + `kameo::console::demo::spawn()`; run `cargo run -p kameo_console`. See `references/observability.md`.
- `prometheus_metrics.rs`: `PrometheusBuilder::new().with_http_listener("0.0.0.0:9000".parse()?).install()?` with the `metrics` feature; `curl` the endpoint. See `references/observability.md`.

## Common cross-cutting APIs

- `ctx.actor_ref()` → `ActorRef` with `.id()`, `.kill()`, `.stop_gracefully()`, `.wait_for_shutdown()`, `.recipient()`.
- `DeliveryStrategy::{Guaranteed, BestEffort}` on pubsub/broker/bus/queue actors.
- `tokio::signal::ctrl_c().await?` to keep `main` alive for long-running systems.
