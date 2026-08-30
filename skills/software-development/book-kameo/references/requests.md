# Requests (ask vs tell)

Source: `docs/core-concepts/requests.mdx`.

## Two patterns

- **ask**: sender waits for a reply (`actor_ref.ask(&msg).await`).
- **tell**: fire-and-forget, no reply (`actor_ref.tell(msg).await`).

## Ask requests

- Sender pauses (awaits) until reply → synchronous-in-async.
- Error handling falls to the caller: handler errors return as `SendError::HandlerError`.
- **Timeouts**:
  - `mailbox_timeout` (bounded mailboxes only): max time the request waits in the queue before processing. If mailbox full past this, request dropped/error.
  - `reply_timeout`: max time sender waits for a response (avoids indefinite blocking).

## Tell requests

- No reply; sender continues immediately (truly async).
- Errors encountered while processing a `tell` are treated as **panics** → by default may stop the actor (customizable via `on_panic` for recovery/logging).
- `mailbox_timeout` also available for bounded mailboxes (backpressure management).

## Ownership nuances

- `tell(msg)` takes the message by value (ownership).
- `ask(&msg)` takes a reference.

## Choosing

- Use `ask` for critical ops needing data/confirmation or where the caller must observe errors.
- Use `tell` for notifications/commands whose outcome doesn't affect the sender.

## Notes

- For tell errors as panics caveat, see `references/replies.md` (error/panic rule) and `references/faq.md` (unexpected stops).
