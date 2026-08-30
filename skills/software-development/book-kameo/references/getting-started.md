# Getting Started

Source: `docs/getting-started.mdx`, README installation + Basic Example.

## Install

- Rust **1.88** minimum (via rustup). Kameo `0.22`.
- `Cargo.toml`: `kameo = "0.22"` or `cargo add kameo`.
- Distributed features need `features = ["remote"]`; observability needs `console`/`metrics`/`hotpath`.

## Minimal Hello World actor

```rust
use kameo::prelude::*;

#[derive(Actor)]
pub struct HelloWorldActor;

pub struct Greet(String);

impl Message<Greet> for HelloWorldActor {
    type Reply = (); // no reply
    async fn handle(
        &mut self,
        Greet(greeting): Greet,
        _: &mut Context<Self, Self::Reply>,
    ) -> Self::Reply {
        println!("{greeting}");
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let actor_ref = HelloWorldActor::spawn(HelloWorldActor); // unbounded by default in README example
    actor_ref.tell(Greet("Hello, world!".to_string())).await?;
    Ok(())
}
```

## Key APIs (verbatim shapes)

- `#[derive(Actor)]` — derive macro; reduces boilerplate, sensible defaults.
- `#[actor(name = "MyAmazingActor")]` — custom name for logging (default: struct ident).
- `X::spawn(state)` -> `ActorRef<X>` — spawn and get a reference.
- `actor_ref.tell(msg).await?` — fire-and-forget send (takes ownership of msg).
- `actor_ref.ask(&msg).await?` — request expecting a reply (takes a reference).
- `#[tokio::main]` — required async runtime entry point.

## Notes

- `handle` takes `&mut self` (exclusive state access), the message, and a `Context`.
- README's first example uses `use kameo::actor::Spawn;` to bring `spawn` into scope; `prelude::*` covers the same.
- Distilled structure, not the source. For full signatures use `docs.rs/kameo`.
