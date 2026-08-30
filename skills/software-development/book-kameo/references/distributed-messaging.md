# Distributed Actors — Messaging

Source: `docs/distributed-actors/messaging-remote-actors.mdx`.

## Send to a remote actor

Use the same `ask`/`tell` API on `RemoteActorRef`:

```rust
let remote_actor_ref = RemoteActorRef::<MyActor>::lookup("my_actor").await?;
if let Some(actor) = remote_actor_ref {
    let result = actor.ask(&Inc { amount: 10 }).await?;   // expects reply
    println!("Incremented count: {result}");
}
```

- `ask` → replies; `tell` → fire-and-forget:

  ```rust
  actor.tell(&LogMessage { text: "Logging event".to_string() }).await?;
  ```

- Serialization, routing, and delivery are transparent.

## Requirements for remote messaging

1. **Actor must implement `RemoteActor`**:

   ```rust
   #[derive(RemoteActor)]
   pub struct MyActor;
   ```

2. **Messages need `#[remote_message]`** + `Serialize`/`Deserialize`:

   ```rust
   #[remote_message]
   impl Message<Inc> for MyActor {
       type Reply = i64;
       async fn handle(&mut self, msg: Inc, _ctx: &mut Context<Self, Self::Reply>) -> Self::Reply {
           self.count += msg.amount as i64;
           self.count
       }
   }
   ```

   - `#[remote_message]` assigns a unique ID to the actor+message handler combo.
   - The UUID string **must be unique within the crate** to avoid routing conflicts.

## Why `#[remote_message]` is needed

Kameo lets actors handle many message types without a central enum. At deserialization time the exact type is unknown, so Kameo uses the **`linkme`** crate to build, at link time, a HashMap:

```text
HashMap<RemoteMessageRegistrationID, RemoteMessagesFns>
```

- `RemoteMessageRegistrationID` = actor ID + message ID (from `RemoteActor` + `#[remote_message]`).
- `RemoteMessagesFns` = function pointers for the `ask`/`tell` handlers of that actor+message.
- On receipt, Kameo looks up the entry by ID to deserialize + dispatch.

## Handling replies

`ask` returns the reply type declared in the handler; await it:

```rust
let result = actor.ask(&Inc { amount: 10 }).await?;
println!("Received reply: {}", result);
```

## Notes

- Same `ask`/`tell` semantics as local (see `references/requests.md`); `tell` errors are still panics remotely.
- Distributed overview: `references/distributed-overview.md`; swarm: `references/distributed-swarm.md`; registry: `references/distributed-registry.md`.
