# Listener-hook vs TCPRoute/UDPRoute conflict — investigation record

Session 2026-08-30, nishir cluster. Resolved by manifests PR #1946, issue #1945.
This is the deep-dive transcript behind the "Listener-hook + TCP/UDP gateways:
SOLVED" section of SKILL.md. Read for line-level source evidence before
re-deriving anything about ai-gateway's extension server and listener IR.

## Timeline of conclusions (note the reversal)

1. EG v1.8.3 era: syncthing Gateway Programmed=False — "unable to find
   HTTPConnectionManager in FilterChain: tcproute/.../syncthing" in EG's own
   translator. Fixed by the v1.9.0 bump (#1941).
2. Still broken on v1.9.0 → blamed ai-gateway's extension server receiving
   listener IR. #1942 set `listener.includeAll: false`. Syncthing healed;
   inference broke (every chat completion 500).
3. Working theory for weeks: "ai-gateway v1.1.0 structurally cannot serve an
   HTTP-extension Gateway and a TCP/UDP Gateway under one control plane —
   either/or." This was FALSIFIED by the adversarial pass.

## The falsified "either/or" mechanism

Claimed: with `listener.includeAll: true`, ai-gateway's `findHCM`
(`internal/extensionserver/inferencepool.go:426-440`) hard-errors on syncthing's
TCP/UDP filter chains → whole translation NACKs → syncthing crash-loops.

Reality: there are FOUR listener walks in `PostTranslateModify`, with three
different error behaviors:

| Walk | Gate | Behavior on non-HCM chain |
|---|---|---|
| `insertRouterLevelAIGatewayExtProc` | `enabled` — only listeners whose route configs contain an AIGateway-generated route (`isRouteGeneratedByAIGateway` checks the `ai-gateway-generated` annotation in route metadata) | never runs for syncthing |
| `insertRequestHeaderToMetadataFilters` | `len(logRequestHeaderAttributes) > 0` | **fatal `return err`** ← the actual killer |
| `maybeInjectQuotaRateLimiting` walk | quota config | `continue` |
| `patchListenerWithInferencePoolFilters` | InferencePool present | log + `continue` |

`logRequestHeaderAttributes` defaults to `agent-session-id:session.id` via
`requestheaderattrs.ResolveLog` (`internal/requestheaderattrs/resolve.go` —
"Defaults to DefaultSessionIDHeaderMapping when unset. Set to empty to
disable"). The controller flag `--logRequestHeaderAttributes=` (explicit empty)
clears the default BY DESIGN; the Helm chart value
`controller.logRequestHeaderAttributes: ""` renders exactly that flag
(verified with `helm template ... --set controller.logRequestHeaderAttributes=""`).

## Why listener IR is mandatory (the inference side)

`PostTranslateModify` → `maybeModifyListenerAndRoutes`
(`post_translate_modify.go:542`):
- `enableRouterLevelAIGatewayExtProcOnRoute` (:733) stamps per-route
  `TypedPerFilterConfig` enablement on AIGateway-generated routes.
- `insertRouterLevelAIGatewayExtProc` (:768) inserts the router-level
  `envoy.filters.http.ext_proc/aigateway` filter (Disabled:true globally,
  enabled per-route), only when `req.Listeners` is non-empty.
- That router filter is the source of `x-envoy-aigateway-internal-req-id`
  (`internal/extproc/server.go:184-187`): the upstream-level ext_proc requires
  it and returns gRPC 13 `missing internal request ID header from router
  filter` without it → 500 on every completion.
- With `listener.includeAll: false`, the CLUSTER hook still runs, so the
  upstream (cluster-level) filter installs — asymmetric config: route table +
  clusters wired, router leg absent, upstream leg failing.

Live discriminator (Envoy admin `config_dump`, port-forward 19000 on the
dataplane pod): the `shikanime/inference/https` HCM chain showed
`[credential_injector ×3, router]` (broken) vs `[ext_proc/aigateway, router]`
(healthy).

## Escape-hatch sources checked during falsification

- `helm show values oci://docker.io/envoyproxy/ai-gateway-helm --version 1.1.0`
  → `logRequestHeaderAttributes: null` with "Set to \"\" to disable the
  default" (line ~119).
- `cmd/controller/main.go` flag help: same wording.
- Upstream search for existing issue: none covers findHCM-on-TCP (issue #1708
  is the cross-namespace injection bug, #2003 is MCP EndpointSlice — both
  unrelated).

## Falsification heuristic (generalized)

When a concluded "incompatible / no solution" rests on a hard error, ask: which
walk emitted it, what gates that walk, and does the gate have a documented off
switch? Check `helm show values`, controller `--help`, and the source's own
defaulting helpers (`resolve.go`-style "defaults to X when unset, empty
disables"). Only after all three come up empty is the upstream issue justified.

## Live verification (post-fix, 2026-08-30, merge commit 295a9801f)

- Both HelmReleases Ready from Git; inference dataplane rolled fresh.
- Gateways `inference` + `syncthing`: Accepted=True, Programmed=True.
- config_dump: `inference/https` chain `['ext_proc/aigateway', 'router']`.
- `POST /v1/chat/completions` (qwen/qwen3.8-flash via openrouter): HTTP 200,
  real completion body.
- syncthing TCP 22000 on the Gateway LB: OPEN (raw `/dev/tcp` probe; the one
  TLS-error access-log line was the probe's own `UF,URX` cert-verify, not
  syncthing traffic).
- Cost: `agent-session-id` no longer lands in access-log attributes (cosmetic).

## Open follow-ups (not blocking)

- Upstream hardening PR: `insertRequestHeaderToMetadataFilters` /
  `insertRouterLevelAIGatewayExtProc` should skip non-HCM chains (`continue`)
  instead of erroring. Unchanged on ai-gateway main as of v1.1.0+.
- Separate defect: `z-ai` AIServiceBackend with `schema: Anthropic
  (api/anthropic/v1)` → extproc 500 `unsupported API schema: backend={Anthropic
  api/anthropic/v1}` — request-side Anthropic only; backend-side unsupported.
