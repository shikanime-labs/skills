# Replies

Source: `docs/core-concepts/replies.mdx`.

## Reply trait

Every type returned as an actor response must implement `Reply`. Ensures the value can be sent back through the messaging system.

```rust
use kameo::Reply;

#[derive(Reply)]
pub struct MyReply {
    pub data: String,
    pub status: bool,
}
```

- `#[derive(Reply)]` macro auto-implements for custom types.
- Most std types already implement `Reply`; report gaps via issue if a std type doesn't.

## Error-as-panic rule

- `Result::Err` replies are treated distinctly from non-error replies.
- When a message is sent via **`tell`**, any error from the handler is interpreted as a **panic** → may stop the actor (tune via `on_panic`).
- With **`ask`**, a handler error is returned as `SendError::HandlerError` to the caller (not a panic).

## Workaround for non-Reply types

Wrap in `Result<T, kameo::error::Infallible>`:

```rust
// T doesn't impl Reply, but any Result does:
Result<MyType, Infallible>
```

Common when `Result` is already your natural return type.

## Handling replies (ask)

- Receive the reply; manage timeouts and `SendError::HandlerError`.
- Clear, concise error handling keeps the system resilient.

## Notes

- Reply errors are the bridge to supervision; pair with `references/requests.md` and `references/supervision.md`.
