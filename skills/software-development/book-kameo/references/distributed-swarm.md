# Distributed Actors — Swarm Setup

Source: `docs/distributed-actors/bootstrapping-actor-swarm.mdx`, `custom-swarm-configuration.mdx`.

## Requires the `remote` feature

```toml
kameo = { version = "0.22", features = ["remote"] }
```

## Bootstrap (quick start)

```rust
use kameo::remote;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let peer_id = remote::bootstrap()?;
    println!("Node started with peer ID: {}", peer_id);
    Ok(())
}
```

- Auto-configures: TCP + QUIC transports, mDNS local discovery, listens on `0.0.0.0:0` (OS-assigned), global actor registry, returns `PeerId`.

### Listen on specific address

```rust
let peer_id = remote::bootstrap_on("/ip4/0.0.0.0/tcp/8020")?;
```

- Multiaddr formats: `/ip4/0.0.0.0/tcp/8020`, `/ip4/127.0.0.1/tcp/8020`, `/ip4/0.0.0.0/udp/8020/quic-v1`.

### Bootstrap includes

Transports TCP+QUIC; Noise (encryption); Yamux (multiplexing); mDNS discovery; 60s idle connection timeout; full Kameo remote capability.

### Bootstrap limitations

mDNS only (same LAN), fixed transport/security, **cannot be combined with other libp2p behaviors**, not for production.

## Custom swarm (production)

Minimal setup:

```rust
use kameo::{prelude::*, remote};
use libp2p::{noise, tcp, yamux, swarm::NetworkBehaviour};

#[derive(NetworkBehaviour)]
struct MyBehaviour { kameo: remote::Behaviour }

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut swarm = libp2p::SwarmBuilder::with_new_identity()
        .with_tokio()
        .with_tcp(tcp::Config::default(), noise::Config::new, yamux::Config::default())?
        .with_behaviour(|key| {
            let kameo = remote::Behaviour::new(
                key.public().to_peer_id(),
                remote::messaging::Config::default(),
            );
            Ok(MyBehaviour { kameo })
        })?
        .build();

    swarm.behaviour().kameo.init_global();          // init Kameo global registry
    swarm.listen_on("/ip4/0.0.0.0/tcp/0".parse()?)?;
    // ... event loop (see below)
    Ok(())
}
```

### Compose with other behaviors

Add `gossipsub`, `mdns`, `kademlia` to `MyBehaviour`; build each in `with_behaviour` closure. Kameo registration/lookup APIs stay identical after migration.

### Messaging config

```rust
let cfg = remote::messaging::Config::default()
    .with_request_timeout(Duration::from_secs(30))
    .with_max_concurrent_requests(1000)
    .with_max_request_size(1024 * 1024)        // 1MB
    .with_max_response_size(10 * 1024 * 1024); // 10MB
let kameo = remote::Behaviour::new(peer_id, cfg);
```

### Transports

TCP (`with_tcp`, `port_reuse`, `nodelay`), QUIC (`with_quic`), WebSocket (`with_websocket` for browsers), relay (`with_relay_client` for NAT traversal).

### Event loop

```rust
use libp2p::swarm::SwarmEvent;
use futures::StreamExt;
tokio::spawn(async move {
    loop {
        match swarm.select_next_some().await {
            SwarmEvent::Behaviour(MyBehaviourEvent::Kameo(remote::Event::Registry(ev))) => { /* registry events */ }
            SwarmEvent::Behaviour(MyBehaviourEvent::Mdns(mdns::Event::Discovered(peers))) => {
                for (pid, ma) in peers { swarm.add_peer_address(pid, ma); }
            }
            SwarmEvent::ConnectionEstablished { peer_id, .. } => { /* ... */ }
            SwarmEvent::NewListenAddr { address, .. } => { /* ... */ }
            _ => {}
        }
    }
});
```

### Production example highlights

- `.with_swarm_config(|c| c.with_idle_connection_timeout(Duration::from_secs(300)).with_max_negotiating_inbound_streams(1024))`
- Listen on multiple addrs (TCP + QUIC) for redundancy.
- Dial known bootstrap peers: `swarm.dial(addr)?;`

## Migration

bootstrap → custom: replace `bootstrap()` with `SwarmBuilder`, add protocols, configure transports/addressing. **Actor registration & messaging APIs unchanged.**
