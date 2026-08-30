# Distributed Actors — Registry (Register & Lookup)

Source: `docs/distributed-actors/registering-looking-up-actors.mdx`.

## Register an actor

```rust
let actor_ref = MyActor::spawn(MyActor::default());
actor_ref.register("my_actor").await?;
```

- Name propagated across the network via **Kademlia DHT** (name → reference on registering node).
- Other nodes can then look it up and message it.

## Lookup a single actor

```rust
let remote_actor_ref = RemoteActorRef::<MyActor>::lookup("my_actor").await?;
if let Some(actor) = remote_actor_ref {
    let result = actor.ask(&Inc { amount: 10 }).await?;
    println!("Incremented count: {result}");
} else {
    println!("Actor not found");
}
```

- Returns `Option<RemoteActorRef>`; `None` if not found.
- A `RemoteActorRef` may reference an actor on the **current** node too.
- `lookup` == first item of `lookup_all`.

## Lookup all (replicas)

```rust
let mut actors = RemoteActorRef::<MyActor>::lookup_all("my_actor");
while let Some(actor) = actors.try_next().await? {
    let result = actor.ask(&Inc { amount: 5 }).await?;
    println!("Actor on {:?} returned: {result}", actor.id().peer_id());
}
```

- Returns a stream yielding `RemoteActorRef` as discovered.
- Use for: load balancing across instances, redundancy, monitoring all replicas.

## Kademlia DHT

- Decentralized registry; each node stores a portion.
- Registration: name stored as DHT key → reference value.
- Lookup: DHT retrieves location, returns reference.
- No central server / single point of failure.

## Retry mechanism

DHT propagation can lag (just-registered actor, syncing network). Retry loop:

```rust
use std::time::Duration;
use tokio::time::sleep;
async fn retry_lookup() -> Result<Option<RemoteActorRef<MyActor>>, RegistryError> {
    for _ in 0..5 {
        if let Some(actor) = RemoteActorRef::<MyActor>::lookup("my_actor").await? {
            return Ok(Some(actor));
        }
        sleep(Duration::from_secs(2)).await;
    }
    println!("Actor not found after retries");
    Ok(None)
}
```

- Cleaner: use the `backon` crate for retry policies.

## Two-node round trip

Node 1: `bootstrap()` → spawn → `register("my_actor")`.
Node 2: `bootstrap()` → `lookup("my_actor")` → `ask(&Inc{..})`.
