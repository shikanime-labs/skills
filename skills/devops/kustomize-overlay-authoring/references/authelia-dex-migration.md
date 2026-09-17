# dex → authelia migration (PRs #2083, #2087–#2104, #2107, #2108)

Session-proven facts for deploying Authelia (4.39.20) on the hardened nishir
cluster. Class-level pod/Flux lessons live in the SKILL.md; this file holds
the app-specific detail.

## Authelia hardening baseline (PRs #2107 + #2108, live-verified)

The deployed config carries the upstream security recommendations:

- LDAP: `tls.server_name: lldap.shikanime.svc.cluster.local` (matches cert SAN)
  instead of `skip_verify: true` — the trust-manager CA bundle is already
  mounted at `/etc/ssl/certs` by cluster policy, so verification just works.
- `regulation`: max_retries 3 / find_time 2m / ban_time 15m.
- Session: `inactivity: 15m`, `expiration: 12h`, `remember_me: 1w`
  (NOT `remember_me_duration` — deprecated 4.38, auto-mapped but warns).
- `password_policy.zxcvbn: {enabled: true, min_score: 3}`.
- `server.buffers: {read: 4096, write: 4096}`.
- **`server.endpoints.ratelimit.enable` is NOT a valid 4.39 runtime key** —
  `validate-config` ACCEPTS it but runtime config load rejects it
  (`configuration key not expected` → fatal crash loop). Always boot the real
  server once (even in docker) after config changes; validate-config alone
  misses runtime-only key rejections.
- Verification recipe that catches everything: in-cluster
  `kubectl run curlchk --rm -i --image=curlimages/curl -- curl -sk
  https://authelia.<ns>.svc.cluster.local:9091/api/health`, plus an authorize
  endpoint hit with a real client_id (expect 303 with OAuth2 error params when
  state is missing — proves client/redirect validation and issuer binding).

## Authelia config facts (validated against 4.39.20 source + validate-config)

- Env prefix for config overrides is `AUTHELIA_` (`AUTHELIA_SERVER_TLS_KEY`).
  `X_AUTHELIA_` is ONLY the template config-filter namespace — `X_AUTHELIA_SERVER_TLS_KEY`
  is silently ignored and the server stays plain HTTP.
- `X_AUTHELIA_CONFIG_FILE` is ignored without an explicit `--config <path>`
  arg. Pass the config via container args.
- `server.disable_healthcheck: true` is REQUIRED on readOnlyRootFilesystem
  clusters (see SKILL.md hardened-cluster section).
- `session.secret` (not `encryption_key`) in 4.39; `storage.encryption_key`
  binds to the SQLite db — changing it after db creation fails startup with
  "encryption key does not appear to be valid for this database". Wipe the
  db (fresh deploy) or use `authelia storage encryption change-key`.
- OIDC client secrets are PBKDF2 digests (`authelia crypto hash generate
  pbkdf2`); `public: true` + PKCE S256 for public clients. Client migration
  from dex is 1:1 on redirect URIs.
- Issuer URL kept at the old dex hostname (`accounts.i.shikanime.studio`) —
  clients need no reconfiguration if issuer is preserved. Live check that the
  OIDC pipeline is intact: `/.well-known/openid-configuration` serves the
  issuer, `/jwks.json` serves `kid=<key-id>`, and the authorize endpoint
  returns 303 (not 404) with OAuth2 error params on a missing state.
- Validate locally: decrypt with wrapped sops, then
  `docker run --rm --user 1000:1000 --entrypoint sh -v /private/tmp/x.yaml:/cs/configuration.enc.yaml:ro -e X_AUTHELIA_CONFIG_FILTER=template authelia/authelia:4.39.20 -c 'authelia validate-config --config /cs/configuration.enc.yaml'`
  (docker mounts of `/tmp/...` fail — use `/private/tmp/...`).

## Silent startup-check fatal: read the app source, not the logs

Symptom: `fatal msg="Errors occurred performing startup checks"` with ZERO
per-provider detail even at `--log.level trace`. Cause: the server code path
runs `StartupChecks(ctx, log=false)` — errors are collected in a map and only
counted, never logged; and the healthcheck-env write happens BEFORE any
provider check, failing into the generic `Fatal("Errors occurred performing
startup checks")` branch (no `ErrProviderStartupCheck`, so no provider list).

Method that cracked it: fetch the tagged source
(`raw.githubusercontent.com/authelia/authelia/v4.39.20/internal/middlewares/startup.go`),
read `doStartupCheck` + the `log` flag semantics, then bisect with minimal
configs in a debug pod until the failing step isolated. Source-reading beats
log-spelunking when errors are collected but not logged.

## Flux health-check deadlock on a never-ready probe

If a readiness probe dials a scheme the container isn't serving yet (HTTPS
probe vs plain HTTP listener after an env-var fix that Flux hasn't applied),
the pod never goes Ready → Flux `Kustomization` health check stalls BEFORE
applying the new STS spec → the fix never lands. Chicken-and-egg.

Break: `kubectl scale sts <name> --replicas=0`, wait for pod deletion (the
scale IS applied — replicas is mutable), then `--replicas=1`. The STS spec
with the fix must already be rendered by Flux (`lastAttemptedRevision` shows
the new SHA; check `.spec.template.spec.containers[0].env` on the STS, not
the old pod).

Also: after any app change, verify the LIVE pod env/mounts, not the STS —
a 15-minute-old pod keeps running the pre-fix spec while the STS sits at
generation N+1 unapplied. A newly-created pod can ALSO render a stale
template if the secretGenerator hash changed and the new Secret landed after
the pod was scheduled (`MountVolume.SetUp failed: secret "<old-hash>" not
found`) — delete the pod once more; STS recreation then picks the current
template.

Force the full path when Flux lags: annotate the GitRepository
(`reconcile.fluxcd.io/requestedAt`) AND the Kustomization; confirm
`status.lastAttemptedRevision` shows the new commit SHA before debugging the
workload. A merged PR is NOT applied until that SHA appears.

## PVC residue from debug sessions

Debug pods writing to the app's PVC leave stale artifacts that break later
starts: an old `db.sqlite3` (wrong encryption key), a 0-byte config file at
the subPath mount target (blocks the secret mount!), leftover test files.
Wipe via a busybox pod with the PVC mounted BEFORE scaling back up; RWOP
locks mean the wipe pod needs the app pod gone first. `kubectl exec` into a
CrashLooping container fails ("container not found") — use `kubectl debug`
with the PVC volume, or the wipe pod.

## Tailscale MagicDNS NXDOMAIN is fleet-level, not app-level

When a `<svc>.taila659a.ts.net` name stops resolving, check a SIBLING name
(e.g. grafana) before blaming the app: if all operator-registered names go
NXDOMAIN from every node (workstation + `getent hosts` on minish/ashira),
it is a Tailscale control-plane DNS registration issue — the k8s operator
pods and headless services (`ts-<app>-xxxxx`, endpoints populated) are
healthy and no manifest change is at fault. Verify the app itself in-cluster
(`kubectl run curlchk --image=curlimages/curl -- curl -sk
https://<svc>.<ns>.svc.cluster.local:9091/api/health`) and move on; do not
debug the app's Gateway/route.

## SOPS edit loop on an encrypted config (wrapped sops)

The wrapped sops (`/nix/store/...-sops-wrapped/bin/sops`) enforces flake
creation_rules: `sops -e <plaintext>` FAILS ("no matching creation rules")
unless the INPUT PATH matches the flake regex. Working loop: overwrite the
`.enc.yaml` with the plaintext, `sops -i -e apps/authelia/overlays/nishir/authelia/configuration.enc.yaml`,
then decrypt-verify (`grep -c ENC`, key presence) and `validate-config` in
docker. Piping decrypt output through Python/heredoc is fine; the flag check
only gates the ENCRYPT direction.

Also: resolving a sops-ciphertext jj/git conflict — `jj restore --from
main@origin <file>`, decrypt, apply the plaintext change, re-encrypt fresh.
Never merge ciphertext hunks by hand.
