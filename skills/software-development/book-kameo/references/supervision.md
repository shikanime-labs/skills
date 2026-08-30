# Supervision

Source: `docs/core-concepts/supervision.mdx`. Erlang/OTP-style supervision trees + actor linking.

## Two mechanisms

1. **Supervision trees** — parent-child, automatic restart on failure.
2. **Actor linking** — peer-to-peer monitoring (with or without restart).

## Supervision strategies

Override `supervision_strategy()` on the supervisor:

```rust
fn supervision_strategy() -> SupervisionStrategy {
    SupervisionStrategy::OneForOne // default
}
```

| Strategy | Behavior | Use when |
|----------|----------|----------|
| `OneForOne` (default) | Restart only the failed child | Workers independent |
| `OneForAll` | Restart all children | Children tightly coupled |
| `RestForOne` | Restart failed child + younger siblings | Later stages depend on earlier |

## Creating supervised children

```rust
use kameo::actor::{Actor, ActorRef, Spawn};
use kameo::error::Infallible;
use kameo::supervision::{RestartPolicy, RestartStrategy}; // RestartStrategy per docs
use std::time::Duration;

// Clone args:
let worker = Worker::supervise(&supervisor_ref, Worker { count: 0 })
    .restart_policy(RestartPolicy::Permanent)
    .restart_limit(5, Duration::from_secs(10))
    .spawn().await;

// Factory for non-Clone args:
let task = Task::supervise_with(&supervisor_ref, || Task::new())
    .restart_policy(RestartPolicy::Transient)
    .spawn().await;
```

> Note: docs show `RestartStrategy` import in the strategy table context; verify the exact path on `docs.rs/kameo::supervision`.

## Restart policies

| Policy | Panics | Errors | Normal exits | Use for |
|--------|--------|--------|--------------|---------|
| `Permanent` (default) | ✅ restart | ✅ restart | ✅ restart | Critical services |
| `Transient` | ✅ restart | ✅ restart | ❌ no restart | Tasks that can complete |
| `Never` | ❌ no restart | ❌ no restart | ❌ no restart | One-shot / externally managed |

## Restart limits

- Prevent restart storms; **default: 5 restarts within 5 seconds**.
- `.restart_limit(n, duration)` — beyond the limit, supervisor stops restarting that child.
- Tune: relaxed (10/60s) for flaky deps; strict (2/5s) for fast-failing actors.

## Spawn options (supervised)

```rust
.spawn().await                                          // default bounded(64)
.spawn_with_mailbox(mailbox::bounded(1000)).await
.spawn_in_thread().await                               // dedicated thread (blocking ops)
.spawn_in_thread_with_mailbox(mailbox::bounded(500)).await
```

## Actor linking (peer monitoring)

```rust
use std::ops::ControlFlow;
use kameo::actor::{ActorId, WeakActorRef};
use kameo::error::ActorStopReason;

let worker_a = WorkerA::supervise(&sup, WorkerA).spawn().await;
let worker_b = WorkerB::supervise(&sup, WorkerB).spawn().await;
worker_a.link(&worker_b).await;

// handle link death:
async fn on_link_died(
    &mut self,
    _actor_ref: WeakActorRef<Self>,
    id: ActorId,
    reason: ActorStopReason,
) -> Result<ControlFlow<ActorStopReason>, Self::Error> {
    tracing::warn!("linked actor {id} died: {reason:?}");
    Ok(ControlFlow::Continue(())) // keep running; Break(reason) to stop
}
```

- **Default**: actors stop when a link dies (except normal shutdown). Return `Continue(())` to survive.
- Remote linking: `a.link_remote(&remote_actor_ref).await`; unlink: `a.unlink(&b)` / `a.unlink_remote(...)`.
- Remote node disconnect → `ActorStopReason::PeerDisconnected`.

## Best practices

- **Supervision** for automatic restart/lifecycle; **linking** for peer notification or cross-node monitoring; combine when supervised children coordinate.
- Trees: shallow (2–3 levels), group related actors, critical services higher, `OneForOne` for independent workers / `OneForOne`→`OneForAll` for coupled.
- See `examples/supervision.rs` in the repo for a full example.
