# Distributed Actors — Overview

Source: `docs/distributed-actors.mdx`.

## What it is

Kameo's distributed actor system lets actors communicate across nodes in a decentralized network. Built on **libp2p** (request-response protocol) and integrates as a composable `NetworkBehaviour`.

## Key components

- `kameo::remote::Behaviour` — a libp2p `NetworkBehaviour` providing distributed actor capability; compose with mDNS, Gossipsub, custom protocols.
- `RemoteActorRef` — reference to an actor on a remote node; abstracts networking, uses the familiar `ask`/`tell` API.
- **Registry** — built on **Kademlia DHT**; stores actor name→reference mappings, distributed across the network for discoverability.
- **Messaging** — reliable request-response over libp2p, both ask/tell with configurable timeouts.

## Two setup approaches

1. **Bootstrap (quick start)** — one line, dev/testing/simple:

   ```rust
   let peer_id = kameo::remote::bootstrap()?;
   ```

2. **Custom swarm (production)** — full control over transports, protocols, behavior composition:

   ```rust
   #[derive(NetworkBehaviour)]
   struct MyBehaviour {
       kameo: kameo::remote::Behaviour,
       mdns: mdns::tokio::Behaviour,
       // other protocols...
   }
   ```

## How it works

1. **Network setup** — `bootstrap()` or custom swarm with `remote::Behaviour`.
2. **Actor registration** — register under unique names; propagated via Kademlia DHT, discoverable network-wide.
3. **Discovery & messaging** — look up and message remote actors via `RemoteActorRef`; serialization/routing/delivery transparent.

## Why use it

Real-time systems (chat, games, monitoring), microservices, IoT, edge computing. Horizontal scale, fault tolerance (nodes fail/add without disruption), decentralized discovery (no single point of failure), protocol agnostic (TCP/QUIC/WebSockets + mDNS/DHT).

## Next

- Quick start → `references/distributed-swarm.md` (bootstrap).
- Production → `references/distributed-swarm.md` (custom swarm).
- Discovery → `references/distributed-registry.md`.
- Wire messages → `references/distributed-messaging.md`.
