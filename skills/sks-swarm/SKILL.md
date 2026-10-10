---
name: sks-swarm
description:
  Use when distributing a task across a cluster of agents over A2A — route by
  capability need, machine resource, and runner pressure, optionally in a
  disposable sks-adversarial sandbox.
version: 0.2.0
author: Automata
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

# Agent Swarm

Distribute one task across a cluster of agents over the Hermes A2A protocol
(<https://hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a>). Route
each unit by the capability it needs, the machine it should run on, and the live
resource pressure on the runner — then optionally run the whole swarm inside a
disposable `sks-adversarial` sandbox so a misroute costs nothing.

Read `references/shikanime.md` when working in a shikanime org repo;
linked-issue conventions live there. Read `references/cloud-pi-native.md`
when working in the cloud-pi-native/console repository (reconciliation repo,
French issue language, no-swarm-for-siblings rule).

This skill is a router, not a transport. It decides _what goes where_; A2A and
the harness delegation primitive (mapping:
`sks-async/references/harness-delegation.md`) do the delivery. It does NOT
replace them.

## When to Use

- One task fragments into units that need different capabilities (model, tool,
  permission) or different machines (GPU vs CPU, isolated vs shared).
- The runner is under resource pressure and units must be spread, not stacked.
- A fan-out result is uncertain → wrap the swarm in `sks-adversarial` first.

## When NOT to Use

- A few sibling PRs in one repo → `sks-async` (jj workspaces, no cluster).
- One unit, one machine → `sks-delegate`; do not spin up a swarm.
- Root cause only → `sks-investigate`; this skill executes, not analyzes.

## Procedure

1. **Enable A2A on every host that will run a unit.** Publish the inbound
   Agent Card and register peers (config keys and enablement command per
   harness: `references/a2a.md`). Inbound serves the Agent Card at
   `GET /.well-known/agent-card.json` and JSON-RPC 2.0 at `POST /`; tasks
   inject into the live session, keyed by `contextId` for multi-turn.

2. **Enumerate units** with their requirements — capability tag (model/tool/
   permission), target machine, and a rough resource weight (cpu/mem/io). Record
   the list in the linked issue before dispatching.

3. **Probe runner pressure** before assigning. Read live load on candidate
   machines; a unit whose weight exceeds a host's headroom must move or wait.
   Never co-locate two heavy units on a pressured runner. Re-probe before each
   (re)dispatch, not once at the start — pressure re-checks are cheap, a
   misroute onto a loaded runner is not.

4. **Route each unit** by capability match → resource fit → least-loaded
   eligible host. The target host must be A2A-callable (verify its Agent Card
   over A2A discovery). Override the default host only with an explicit reason
   (`# ponytail: manual placement — <reason>`).

5. **Dispatch over A2A.** Fan one task to every peer advertising a
   capability —
   modes `all` (every reply), `first` (first success), `best` (longest
   successful reply; an all-error fan-out reports the failures instead of
   picking one); for a single targeted unit, send one task (multi-turn via
   context id). Tool names and signatures: `references/a2a.md`. Parent
   re-verifies every child's gate via `terminal` before trusting the
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
- Spinning a swarm for one unit — `sks-delegate` is the smaller, correct tool.
- A sandboxed swarm that merges un-reviewed skips the `sks-adversarial` promote
  gate; the sandbox is a trial, not an approved change.
- Unauthenticated A2A binds `127.0.0.1` only; remote needs a bearer token.
  Full security model (tokens, injection filtering, audit log, turn caps):
  `references/a2a.md`.

## Verification

```bash
# after dispatch: every unit has a host + capability tag recorded
# pressure: re-probe candidate hosts before each (re)dispatch
# reconcile: gh issue view <N> --repo <org>/<repo>  # units + gates listed
# sks-gc reclaims idle agents/workspaces once reconciled
# host reachable: a2a_discover(url) returns a parsed Agent Card
curl --fail --silent --show-error http://<host>:9900/.well-known/agent-card.json
```

Validate the Agent Card with the harness A2A discovery tool; plain curl works
when A2A tooling is unavailable.

## A2A API

Transport setup, the Hermes toolset (`a2a_discover`, `a2a_call`, …), security
model, and a quick test live in `references/a2a.md` — read it when enabling or
debugging A2A delivery.

## See also

- `sks-adversarial` — wrap an uncertain swarm in a disposable sandbox.
- `sks-async` — in-repo parallel streams when no agent cluster is needed.
- `sks-investigate` — root-cause discipline before executing a swarm.
- `sks-gc` — reclaim idle agents / workspaces after reconcile.
