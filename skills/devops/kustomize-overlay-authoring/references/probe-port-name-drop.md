# Probe port name dropped by multi-component `ports` merge

Verified on `apps/hermes-agent` (nishir): `components/api/patch-sts.yaml` added
`ports: [{name: http, containerPort: 8642}]` plus liveness/readiness/startup
probes `httpGet: { path: /health, port: http }`. Sibling components
(`a2a`, `webhook`, `dashboard`) each also added their own `ports:` lists to the
same `hermes-agent` container. The rendered StatefulSet kept all three probes
with `port: http` but the `name: http` entry was GONE from `ports` (the other
four port names survived). Root cause: kustomize list-merge on the `ports`
field across multiple strategic-merge patches collapsed the `http` entry.

## Second occurrence, different mechanism (PR #2082, 2026-09-02)

#2065 split hermes-agent routes per component and DELETED the
`api-server` containerPort entry from the a2a component's patch-sts while the
new `components/api-server/patch-sts.yaml` declared probes
(`httpGet: { port: api-server }`) and env (`API_SERVER_ENABLED`) but NEVER a
`ports: [{name: api-server, containerPort: 8642}]` entry. Same symptom
(`strconv.Atoi: parsing "api-server"`, pod 1/2), but the cause was not list
merge — the owning component simply never rendered the port. Rule: **a
component that references a named port in probes/SVC targetPort/NetPol must
itself declare that containerPort in the SAME patch**; moving a port between
components in a route split requires the destination component to re-add the
`ports:` entry in the same PR. Grep the render, not the components dir —
`kustomize build <overlay> | grep containerPort` vs probe port names.

Also verified live (2026-09-02): the `hermes serve` CLI (v2026.8.27) binds the
API on the gateway itself; a probe `connection refused` on 8642 AFTER the port
renders correctly means the app never listens there — check the CLI subcommand
exists (`hermes api-server` printed usage error; the real server subcommand is
`hermes serve`) before concluding the manifest is at fault. Healing after the
port fix required BOTH a Flux reconcile to a revision containing it AND
`kubectl delete pod hermes-agent-0` — a pod already stuck in CrashLoop does not
pick up the new STS spec on its own, and the STS rollout shows
`updateRevision != currentRevision` while the old pod lingers.

## Symptom

- Pod `1/N Ready`, the broken container `Ready: False`, 0 restarts.
- Kubelet event repeats for hours:
  `Startup probe errored and resulted in unknown state: strconv.Atoi: parsing "http": invalid syntax`
  (readiness/liveness variants use the same wording).
- The string is the port NAME, not a number — kubelet tries to `Atoi` the port
  field and fails because no declared port matches that name.

## Diagnose (deterministic, no cluster needed)

1. Render the offending overlay:
   `kubectl kustomize apps/<app>/overlays/<cluster>-tailnet > /tmp/rendered.yaml`
   (or `kustomize build` from `nix develop` — same result).
2. Extract the container and compare probe port names to declared port names:
   ```bash
   python3 - <<'PY'
   import sys, re
   doc = open('/tmp/rendered.yaml').read()
   sts = doc[doc.find('kind: StatefulSet'):]
   sts = sts[:sts.find('\n---')] if '\n---' in sts else sts
   print('probe ports:', sorted(set(re.findall(r'httpGet:\s+path: \S+\s+port: (\S+)', sts))))
   print('declared   :', sorted(set(re.findall(r'^\s+- containerPort: \d+\s+name: (\S+)', sts, re.M))))
   PY
   ```
   Any name in `probe ports` absent from `declared` is the bug.
3. Confirm which patch owns the orphan name: grep the components dir for
   `port: <name>` and the matching `name: <name>` port entry.

## Fix

- Point the probes at a port name that is ALWAYS present — a port declared by a
  component guaranteed in every overlay that uses these probes (here
  `api-server` = 8642, declared by the `a2a` component which is always in the
  overlay). Or use the numeric port directly.
- Delete the orphan `ports: [{name: http, ...}]` entry from the patch.
- Grep the app tree for NetworkPolicy `ports: [{port: <name>}]` referencing the
  dead name and remap those to the real name — a named port in a NetworkPolicy
  that no pod exposes matches NOTHING, so the rule was silently dead.

## Live-heal gotcha

Patching the StatefulSet with `kubectl replace` updates `spec.template` but k8s
does NOT recreate the running pod for probe-only changes — `kubectl get pod`
still shows the old pod (stale `port: http` in its cached spec) and it stays
NotReady. Force recreate: `kubectl delete pod <sts>-0`. The new pod picks up the
corrected spec; probes then pass once the process binds the port (allow the
startup-probe grace window — here 180x5s = 15 min — before assuming failure).
Verify in-pod: `kubectl exec <pod> -c <c> -- curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8642/health` -> 200, then `kubectl get pod` shows `N/N Ready`.

## The same bad NAME spreads to Service port + Ingress backend

The orphan `http` port on hermes-agent did NOT only break probes. The same
component (`api`) also defined a **Service port** named `http` with
`targetPort: http`, and the `automata` Ingress selected `port: { name: http }`.
Neither resolved to a real container port, so:

- **Service:** the `hermes-agent` Service exposed port 8642 as `name: http`,
  but its `targetPort: http` referenced a container port name that did not exist
  → the Service's Endpoints for that port were invalid (k8s could not map to a
  pod port). A reviewer flagged this; it was the live, not outdated, finding.
- **Ingress:** the `automata` Ingress `defaultBackend.service.port.name: http`
  pointed at a Service port that (after the probe fix dropped the orphan
  `ports` entry) no longer existed → the Ingress backend selected nothing.

**Full-consistency fix (do all four in one change):**

1. Probes → `api-server` (real container port 8642).
2. NetworkPolicy `ports: [{port: <name>}]` → `api-server` (silent no-op otherwise).
3. **Service `patch-svc.yaml`:** rename the port AND `targetPort` to the real
   container port name:
   ```yaml
   # before (broken — no container port "http")
   ports:
     - name: http
       port: 8642
       targetPort: http
   # after (consistent)
   ports:
     - name: api-server
       port: 8642
       targetPort: api-server
   ```
4. **Ingress backend** selecting that Service port → `api-server`:
   ```yaml
   # before
   defaultBackend:
     service:
       name: hermes-agent
       port:
         name: http
   # after
       port:
         name: api-server
   ```

**Verify zero stale port-name references after the fix** (grep the rendered
overlay — must return nothing):

```bash
kubectl kustomize apps/<app>/overlays/<cluster>-tailnet 2>&1 \
  | grep -nE 'name: http|port: http|targetPort: http' || echo "NONE — clean"
```

Also confirm the Service block carries `targetPort: api-server` (the real
container port name), and that every Ingress backend `port.name` matches a
Service port name that matches a container `name:`. A port name is only valid if
it exists at ALL three layers: container `ports[].name` → Service `ports[].name`
(+ `targetPort`) → Ingress/NetworkPolicy backend `port.name`. Drop any name that
is missing at any layer; the probe/NetPol-only fix leaves Service/Ingress dangling.
