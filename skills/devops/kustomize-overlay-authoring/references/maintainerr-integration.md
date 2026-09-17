# Maintainerr app + integration notes (manifests, 2026-09-02/03)

Session detail for the maintainerr deployment (PRs #2090 → #2093 → #2096)
and its pending service integration. Class-level rules live in SKILL.md and
`references/new-app-recipe.md`; this file holds the app-specific facts.

## Upstream facts (verified from source, not docs)

- Image: `ghcr.io/maintainerr/maintainerr`, tags on Docker Hub
  `maintainerr/maintainerr` (`3.26.0@sha256:0ff47e24...680ea`).
- Port `6246` (`ENV UI_PORT` / `EXPOSE` in Dockerfile) — NOT the 8085 quoted
  in many third-party guides.
- Data at `/opt/data` (README + `start.sh` `DATA_DIR`), UID 1000.
- Native probes from `apps/server/src/app/health.controller.ts`:
  `GET /api/health/live` (no DB) and `GET /api/health/ready` (DB ping, 503
  when down). Docker healthcheck.sh uses `/ready`.

## Integration API (upstream contracts, verified 2026-09-03)

Settings controller: `apps/server/src/modules/settings/settings.controller.ts`.

- Radarr/Sonarr: `POST /settings/test/radarr` then `POST /settings/radarr`
  with `{serverName, url, apiKey}` (zod schema
  `packages/contracts/src/settings/servarr/radarrSetting.ts`; same shape for
  sonarr). Update via `PUT /settings/radarr/:id`.
- Jellyfin: `{jellyfin_url, jellyfin_api_key, jellyfin_user_id?}`
  (`packages/contracts/src/media-server/jellyfin/jellyfinSetting.ts`).
- API key for *arr apps: `kubectl exec <pod> -- grep ApiKey /config/config.xml`
  (lidarr/radarr/sonarr/whisparr all carry it in config.xml).
- Jellyfin API key is NOT in any config file — it lives in the ApiKeys table
  of the live SQLite DB (`/config/data/jellyfin.db`), created via Dashboard →
  API Keys. Copying the DB out of a running pod yields a torn/malformed image;
  clean copy requires stopping jellyfin first, or ask the user to paste the
  key. Prefer asking.
- In-cluster reachability: maintainerr's deny-all netpol is its INGRESS; the
  blocker for calling other apps is the TARGETS' netpols (radarr/sonarr/
  whisparr allow only bazarr/jellyfin/seerr/prowlarr). Add
  `app.kubernetes.io/name: maintainerr` podSelector entries to each target
  app's `base/netpol.yaml` (servarr apps listen on port name `https`).
- Tailnet reachability caveat: `*.taila659a.ts.net` names do NOT resolve from
  inside cluster pods (MagicDNS is tailnet-side). Probe routes from inside a
  pod via the `i.shikanime.studio` hostname, or `curl --resolve <host>:443:<LB-IP>`
  from the tailnet.

## Deployment recovery ledger (2026-09-03)

- #2090 shipped the seerr pinned-PVC shape → pod Pending (pinned PV never
  existed). #2093 converted to VCT (lldap/authelia pattern). #2096 sized the
  VCT to 512Mi.
- Each VCT change required: `kubectl delete sts --cascade=orphan --wait=false`,
  force-delete the stuck pod (`--force --grace-period=0` — RWOP detach can
  hang termination for 10+ min), then annotate the Flux Kustomization to
  re-reconcile.
- Pod stuck `ContainerCreating` with "node fushi is not ready" attach errors:
  root cause was `longhorn-manager` on fushi degraded (ManagerPodDown, 1/2).
  Deleting the manager pod (force) restored node Ready and the engine image
  deployed; attach then succeeded. Check `kubectl get nodes.longhorn.io
  <node> -n longhorn-system` conditions when attach errors mention node
  readiness.
- Sandbox-name-reserved errors after force-deletes: one more force-delete of
  the same pod clears the stale reservation; the next pod comes up clean.
- A Kustomization can read `Ready=False` (stale health-check timeout) while
  the workload is actually healthy — after fixing the workload, annotate for
  a fresh reconcile; one cycle later it reads True/True.
