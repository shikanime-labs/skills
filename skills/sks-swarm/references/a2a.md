# A2A transport (Hermes)

Harness-specific A2A setup for Hermes agents. The routing doctrine lives in
`SKILL.md`; read this when enabling or debugging A2A delivery.

## Enable

In `config.yaml`: `gateway.platforms.a2a.enabled: true` and a port via
`extra.port`; list peers under `a2a_agents`. Then `hermes tools enable a2a`
on each host.

Swarm delivery rides the Hermes `a2a` toolset / inbound JSON-RPC server.

**Outbound tools (call other agents):**

- `a2a_discover(url)` — fetch + summarize a peer's Agent Card.
- `a2a_call(agent, message, context_id?)` — send one task, get the reply;
  multi-turn via `context_id`.
- `a2a_list()` — configured peers, saved conversations, metrics.
- `a2a_history(context_id, limit?)` — recall a persisted A2A conversation.
- `a2a_orchestrate(capability, message, mode?)` — fan one task to every peer
  advertising a capability. Modes: `all` (every reply), `first` (first success),
  `best` (longest successful reply; all-error fan-out reports the failures
  instead of picking one).

**Inbound (be callable):** serves the v1.0 Agent Card at
`GET /.well-known/agent-card.json` and JSON-RPC 2.0 at `POST /` — canonical
methods `SendMessage`, `SendStreamingMessage` (SSE), `GetTask`, `ListTasks`,
`CancelTask`, `SubscribeToTask`, plus push-notification config CRUD. Tasks
inject into the live gateway session (same agent/memory/tools), keyed by
`contextId` for multi-turn.

## Security

No token ⇒ bind `127.0.0.1` only (remote needs a bearer token _and_
`A2A_HOST`); `A2A_PEER_TOKENS="name:token,…"` gives per-peer identity; inbound
text is injection-filtered and cannot reach operator slash commands;
credential-shaped replies are redacted; every exchange logs to
`~/.hermes/a2a_audit.jsonl`; per-context turn cap (`A2A_MAX_PINGPONG_TURNS`,
default 5) stops agent↔agent ping-pong. Stdlib only — no `a2a-sdk`.

## Quick test (from another agent/machine)

```bash
curl http://your-host:9900/.well-known/agent-card.json
curl -X POST http://your-host:9900/ -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"jsonrpc":"2.0","id":1,"method":"SendMessage",
       "params":{"message":{"messageId":"m1","role":"ROLE_USER",
                 "parts":[{"text":"What tools do you have?"}]}}}'
```
