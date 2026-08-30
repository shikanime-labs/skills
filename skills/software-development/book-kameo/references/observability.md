# Observability

Source: `docs/observability.mdx`, README console section.

## Metrics (feature flag)

```toml
kameo = { version = "*", features = ["metrics"] }
```

- Tracks counts of messages/signals sent & received across actors.
- Install any global recorder compatible with the `metrics` crate.
- Common exporters:
  - `metrics-exporter-prometheus` — Prometheus scrape endpoint.
  - `metrics-exporter-tcp` — outputs metrics to clients over TCP.

## Console (real-time TUI)

Kameo ships a terminal UI for monitoring a running actor system: live supervision tree, throughput, mailbox backpressure, restarts, deadlocks.

```toml
kameo = { version = "*", features = ["console"] }
```

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let console = kameo::console::serve("127.0.0.1:9999").await?; // start once, keep handle alive
    // spawn & run actors...
    tokio::signal::ctrl_c().await?;
    Ok(())
}
```

- Instrumentation is behind the `console` feature; **zero cost when off**.
- Polling is pull-based and on-demand → idle app does no extra work.
- Install binary: `cargo install kameo_console`.
- Connect: `kameo-console 127.0.0.1:9999`; try without an app via `kameo-console --demo`.
- Full feature list/keybindings: console README (`github.com/tqwewe/kameo/tree/main/console`).

## Hotpath (terminal TUI)

```toml
kameo = { version = "*", features = ["hotpath"] }
```

- Install TUI: `cargo install hotpath --features tui`.
- Run your kameo app, then `hotpath` in another terminal for live usage metrics.

## Notes

- Console/hotpath are dev/ops tools; they do not change actor logic.
- For distributed traces, combine with the `metrics` feature + an exporter.
