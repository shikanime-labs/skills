# Notification Controller — Provider / Alert / Receiver

## Provider (`notification.toolkit.fluxcd.io/v1beta3`)

- `.spec.type` (required) — where/how to send. Alerting: `slack`, `discord`, `msteams`,
  `telegram`, `pagerduty`, `opsgenie`, `grafana`, `datadog`, `rocketchat`, `sentry`, `generic`,
  `generic-hmac`, `alertmanager`, `matrix`, `lark`, `googlechat`, `webex`, `nats`, `zulip`, `otel`,
  `azureeventhub`, `googlepubsub`, `githubdispatch`, ...
- Git commit status: `github`, `gitlab`, `gitea`, `bitbucket`, `bitbucketserver`, `azuredevops`.
- PR/MR comments: `githubpullrequestcomment`, `giteapullrequestcomment`, `gitlabmergerequestcomment`
  (need `event.toolkit.fluxcd.io/change_request` annotation on the Flux object).
- `.spec.secretRef.name` — token/secret in same ns. `generic-hmac` adds `X-Signature: <hashfn>=<hex>`
  (sha256 default) computed from secret `token`.
- Generic webhook body = JSON `Event` (involvedObject, metadata, severity, reason, message, ...);
  includes `Gotk-Component` header.

## Alert (`v1beta3`)

- `.spec.providerRef.name` (required) — Provider in same ns.
- `.spec.eventSources[]` (required) — `{kind, name|'*', namespace?, matchLabels?}`. `*` = all of kind in ns.
- `.spec.eventSeverity` — `info` (default: all) | `error` (errors only).
- `.spec.eventMetadata` — extra key/values (e.g. `cluster`, `env`, `region`, `summary`).
- `.spec.exclusionList` / `.spec.inclusionList` — Go-regex on message; exclusion wins over inclusion.
- `.spec.summary` — DEPRECATED (<=v1beta3); use `.spec.eventMetadata.summary`. Max 255 chars.
- `.spec.suspend` — stop processing.

### Event metadata precedence (low → high)

1. object annotations `event.toolkit.fluxcd.io/<key>`
2. Alert `.spec.eventMetadata`
3. Alert `.spec.summary` (deprecated)
4. controller metadata `<group>.toolkit.fluxcd.io/<key>`

## Receiver (`notification.toolkit.fluxcd.io/v1`)

- Incoming webhook that triggers reconciliation of listed resources.
- `.spec.type` — `github`, `gitlab`, `gitea`, `bitbucket`, `harbor`, `dockerhub`, `quay`, `generic`,
  `generic-hmac`, `generic-oidc`, `acr`, `gcr`, `nexus`, `cdevents`, ...
- `.spec.events[]` — event types to filter (e.g. `push`, `ping`); only some types support filtering.
- `.spec.secretRef.name` — `token` for HMAC/path generation. `generic-oidc` has no secret (OIDC auth, path = `/hook/sha256(name+ns)`).
- `.spec.resources[]` — `{apiVersion, kind, name, namespace?}` to reconcile.
- `.status.webhookPath` — `/hook/sha256(token+name+namespace)`; point Git webhook Payload URL at
  `<ingress-host><webhookPath>`, Secret = token.
- HMAC send: `X-Signature: sha256=<hmac>`; verify with openssl: `printf '<body>' | openssl dgst -sha256 -r -hmac "<token>"`.

## Commands

- `flux create alert <name> --provider=<p> --event-source=Kustomization/* --event-severity=error --export`
- `flux create receiver <name> --type=github --secret-ref=<s> --resource=GitRepository/<r> --export`
- `flux trigger receiver <name>` (invoke webhook from outside cluster)
- `flux reconcile receiver <name>` | `flux suspend/resume receiver <name>`
