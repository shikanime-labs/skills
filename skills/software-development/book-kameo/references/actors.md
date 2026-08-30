# Actors

Source: `docs/core-concepts/actors.mdx`, `core-concepts.mdx` (Actors section).

## Actor trait overview

Actors encapsulate state + behavior, run in their own async task, communicate via messages. Define via `impl Actor` (manual) or `#[derive(Actor)]`.

### Key components

- **Lifecycle hooks**: `on_start`, `on_stop`, `on_panic`, `on_link_died`.
- **Mailbox** (`type Mailbox`): bounded or unbounded; queue for incoming messages. Bounded enables backpressure.
- **Messaging**: spawn returns `ActorRef<T>`; messages sent async, processed sequentially.
- **Supervision**: actors supervise children; `on_panic`/`on_link_died` react to failures.

## Lifecycle

- `on_start(state, actor_ref)` -> `Result<Self, Error>` — init before processing messages.
- `on_stop` — cleanup (called on stop).
- `on_panic` — invoked on panic/error while processing; decides stop vs continue.
- `on_link_died` — called when a linked actor dies.
- **Stopping**: explicitly, or when all `ActorRef`s dropped.
- **Args/Error**: `type Args = Self; type Error = Infallible;` (or `Box<dyn Error + Send + Sync>`).

## Mailbox

- Default spawn: **bounded, capacity 64**.
- Configure via `_with_mailbox` spawn methods.
- Import: `use kameo::mailbox;` then `mailbox::bounded(n)` / `mailbox::unbounded()`.

## Spawn variants

```rust
let actor_ref = MyActor::spawn(MyActor);                       // default bounded(64)
let actor_ref = MyActor::spawn_with_mailbox(mailbox::unbounded());
let actor_ref = MyActor::spawn_with_mailbox(mailbox::bounded(1000));
let actor_ref = MyActor::spawn_in_thread().await;              // dedicated OS thread (blocking ops)
let actor_ref = MyActor::spawn_in_thread_with_mailbox(mailbox::bounded(500)).await;
```

## Derive attributes

- `#[derive(Actor)]` — basic derive.
- `#[actor(name = "...")]` — custom name (logging).

## Manual impl skeleton

```rust
impl Actor for MyActor {
    type Args = Self;
    type Error = Infallible;
    async fn on_start(state: Self::Args, actor_ref: ActorRef<Self>) -> Result<Self, Self::Error> {
        println!("Actor started");
        Ok(MyActor)
    }
}
```

## Notes

- One actor = one sequential message processor; no locks needed for internal state.
- See `references/supervision.md` for `supervise()` and `spawn_in_thread` lifecycle nuances.
