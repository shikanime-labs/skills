# Messages

Source: `docs/core-concepts/messages.mdx`.

## Message trait

Any static type can be a message by implementing `Message<T>` for an actor.

```rust
pub trait Message<T>: Actor {
    type Reply: Reply;             // reply sent back to caller
    async fn handle(
        &mut self,
        msg: T,
        ctx: &mut Context<Self, Self::Reply>,
    ) -> Self::Reply;
}
```

- Generic over `T` (the message type) → type-safe, per-message handlers.
- `type Reply: Reply` — must implement the `Reply` trait (see `references/replies.md`).
- `handle(&mut self, msg, ctx)` returns a future resolving to `Reply`.

## Sequential processing

- Messages processed **one at a time**, exclusive `&mut self` access.
- No explicit locks/sync needed inside an actor.
- Preserves order received → consistency/correctness for state.
- Concurrent across actors (many actors on one Tokio thread).

## Async & non-blocking work

`handle` is async; you can `.await` I/O, other actors, etc. But **awaiting a long future inside `handle` blocks the mailbox** (head-of-line). To keep responsive, use `ctx.pipe`:

### ctx.pipe — "pipe to self"

Runs a future on a separate task; delivers its output back as a message.

```rust
struct Fetched(Data);
impl Message<Fetched> for MyActor {
    type Reply = ();
    async fn handle(&mut self, Fetched(data): Fetched, _: &mut Context<Self, Self::Reply>) {
        self.last_result = data;
    }
}
// inside another handler:
ctx.pipe(async { Fetched(fetch_from_network().await) });
```

### ctx.pipe_with — inline continuation

Same mechanism, applies result via closure with `&mut self` (no new message type).

```rust
ctx.pipe_with(
    async { fetch_from_network().await },
    |actor, _ctx, result| {
        Box::pin(async move { actor.last_result = result; })
    },
);
```

- Actor kept alive until the future resolves; if already stopped, the message/continuation is skipped.

## Notes

- Prefer `ask`/`tell` for normal sends; `pipe` only when you must start async work without blocking the mailbox.
- Distilled from docs; exact `Context` methods on `docs.rs/kameo`.
