# Tailnet endpoints for the inference gateway

Verified during a live troubleshooting session (2026-08-29).

## FQDNs

- `ai.taila659a.ts.net` — gateway's tailnet FQDN. Wired in
  `configs/tailscale/overlays/nishir/svc.yaml`:
  `tailscale.com/tailnet-fqdn: ai.taila659a.ts.net`,
  `externalName: ai.taila659a.ts.net`, proxy-group `nishir-ai-egress`.
  Fronted by the `ts-llm-proxy` / aperture layer before the Envoy gateway.
- `inference.taila659a.ts.net` — DEAD END for the gateway. It is only a TLS SAN
  on the llama-cpp Ingress (`apps/llama-cpp/overlays/nishir-tailnet/
  patch-cert.yaml`); the Ingress TLS host is the label `inference` (RFC1123),
  not a tailnet FQDN. The name resolves to the raw Strix-Halo node
  (100.75.85.39) which has NO listener.

## Verified probe results

- `tailscale status`: `inference` = 100.75.85.39, active, `relay "par"`;
  `ai` = 100.105.75.83, active, direct IPv6.
- `curl https://ai.taila659a.ts.net/v1/models` → 200, full catalog, no auth.
- `curl https://inference.taila659a.ts.net/...` (80/443/8080/8443) →
  connection timeout / 000 on every port; ICMP pong only.
- `POST /v1/chat/completions` on `ai` requires aperture `tags` array + a user
  tag. `tags:["chat"]` clears `missing tags`; the user-tag grammar is unknown
  (`user:`, `user/`, `u:`, bare name, `x-user`, `user` body field all rejected
  with `missing user tag`). The working client is `custom:aperture-openai` in
  `~/.hermes/config.yaml` (Bearer `sk-lm-<id>:<secret>`). Do not guess the tag
  format — capture a request from the Hermes client or read the ts-llm-proxy
  config.

## Caveat

An early `deepseek/deepseek-v4-flash-0731` chat returned 200, but later calls
to the same and other models hit the `missing tags` / `missing user tag` wall.
Treat chat-via-raw-curl auth as UNSOLVED; use the Hermes client path.
