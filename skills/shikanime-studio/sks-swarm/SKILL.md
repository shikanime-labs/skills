---
name: sks-swarm
description:
  Use when distributing a task across a cluster of agents over A2A — route by
  capability need, machine resource, and runner pressure, optionally in a
  disposable sks-adversarial sandbox.
version: 0.1.1
author: Hermes Agent
license: Apache-2.0
metadata:
  hermes:
    tags:
      - swarm
      - a2a
      - multi-agent
      - fan-out
      - delegation
      - resource-aware
      - shikanime-labs
      - shikanime-studio
    related_skills:
      - sks-adversarial
      - sks-async
      - sks-investigate
      - sks-gc
platforms:
  - linux
  - macos
  - windows
---

# Shikanime Org Agent Swarm

Distribute one task across a cluster of agents over the Hermes A2A protocol
(<https://hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a>). Route
each unit by the capability it needs, the machine it should run on, and the live
resource pressure on the runner — then optionally run the whole swarm inside a
disposable `sks-adversarial` sandbox so a misroute costs nothing.

This skill is a router, not a transport. It decides _what goes where_; A2A and
`delegate_task` do the delivery. It does NOT replace them.

## When to Use

- One task fragments into units that need different capabilities (model, tool,
  permission) or different machines (GPU vs CPU, isolated vs shared).
- The runner is under resource pressure and units must be spread, not stacked.
- A fan-out result is uncertain → wrap the swarm in `sks-adversarial` first.

## When NOT to Use

- A few sibling PRs in one repo → `sks-async` (jj workspaces, no cluster).
- One unit, one machine → `sks-isolate`; do not spin up a swarm.
- Root cause only → `sks-investigate`; this skill executes, not analyzes.

## Procedure

1. **Enable A2A on every host that will run a unit.** In `config.yaml`:
   `gateway.platforms.a2a.enabled: true` and a port via `extra.port`; list peers
   under `a2a_agents`. Then `hermes tools enable a2a` on each host. Inbound
   serves the Agent Card at `GET /.well-known/agent-card.json` and JSON-RPC 2.0
   at `POST /` (`SendMessage`, `SendStreamingMessage` over SSE, `GetTask`,
   `ListTasks`, `CancelTask`, `SubscribeToTask`, plus push-notification config
   CRUD). Tasks inject into the live gateway session (same agent/memory/ tools),
   keyed by `contextId` for multi-turn.

2. **Enumerate units** with their requirements — capability tag (model/tool/
   permission), target machine, and a rough resource weight (cpu/mem/io). Record
   the list in the linked issue before dispatching.

3. **Probe runner pressure** before assigning. Read live load on candidate
   machines; a unit whose weight exceeds a host's headroom must move or wait.
   Never co-locate two heavy units on a pressured runner. Re-probe before each
   (re)dispatch, not once at the start — pressure re-checks are cheap, a
   misroute onto a loaded runner is not.

4. **Route each unit** by capability match → resource fit → least-loaded
   eligible host. The target host must be A2A-callable (verify its card with
   `a2a_discover(url)`). Override the default host only with an explicit reason
   (`# ponytail: manual placement — <reason>`).

5. **Dispatch over A2A.** Fan one task to every peer advertising a capability
   with `a2a_orchestrate(capability, message, mode?)` — modes `all` (every
   reply), `first` (first success), `best` (longest successful reply; an
   all-error fan-out reports the failures instead of picking one). For a single
   targeted unit use `a2a_call(agent, message, context_id?)` (multi-turn via
   `context_id`); `a2a_history(context_id, limit?)` recalls a prior exchange.
   Parent re-verifies every child's gate via `terminal` before trusting the
   aggregate — child reports are not proof. If sandboxed, pass the unit its
   promote/discard contract from `sks-adversarial`.

6. **Reconcile.** Collect results, surface a blocked child as a `BLOCKED:`
   report with evidence, and merge only units that passed. Reclaim idle agents /
   workspaces with `sks-gc`.

## Pitfalls

- Routing purely by capability and ignoring live pressure stacks heavy units on
  a hot runner — measure headroom, then place.
- Treating a child's "done" self-report as verified — re-run its gate in the
  parent before promoting.
- Spinning a swarm for one unit — `sks-isolate` is the smaller, correct tool.
- A sandboxed swarm that merges un-reviewed skips the `sks-adversarial` promote
  gate; the sandbox is a trial, not an approved change.
- Unauthenticated A2A binds `127.0.0.1` only. Remote needs a bearer token _and_
  `A2A_HOST`. `A2A_PEER_TOKENS="name:token,…"` sets per-peer identity. Inbound
  text is injection-filtered and cannot reach operator slash commands;
  credential-shaped replies are redacted; every exchange logs to
  `~/.hermes/a2a_audit.jsonl`. Per-context turn cap (`A2A_MAX_PINGPONG_TURNS`,
  default 5) stops agent↔agent ping-pong. Stdlib only — no `a2a-sdk`.

## Verification

```bash
# after dispatch: every unit has a host + capability tag recorded
# pressure: re-probe candidate hosts before each (re)dispatch
# reconcile: gh issue view <N> --repo <org>/<repo>  # units + gates listed
# sks-gc reclaims idle agents/workspaces once reconciled
# host reachable: a2a_discover(url) returns a parsed Agent Card
curl http://<host>:9900/.well-known/agent-card.json
```

## See also

- `sks-adversarial` — wrap an uncertain swarm in a disposable sandbox.
- `sks-async` — in-repo parallel streams when no agent cluster is needed.
- `sks-investigate` — root-cause discipline before executing a swarm.
- `sks-gc` — reclaim idle agents / workspaces after reconcile.
