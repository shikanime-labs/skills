# Tailscale BYOD proxy recovery & verification recipes

Session-derived, reusable. Not environment-specific (except the macOS openssl
note, called out inline).

## 1. Wedged proxy on a stale/orphaned tailnet device

Symptom: `Gateway` Programmed, listeners up, app manifests correct — but the
data-plane `Service` `status.addresses[].value` still shows the OLD hostname
(e.g. `…-gw.taila659a.ts.net`) and MagicDNS returns NXDOMAIN for both old and
new names.

Confirm wedged (not collision):
```sh
kubectl -n tailscale-system logs ts-<app>-<hash>-0 -c tailscale --tail=20 \
  | grep -iE "login|auth|waiting"
# expect: "Auth key missing or invalid (NeedsLogin state)" / "Waiting for operator to provide new auth key"
kubectl -n tailscale-system get secret ts-<app>-<hash>-0 \
  -o jsonpath='{.data.device_fqdn}' | base64 -d; echo
# expect OLD name; .reissue_authkey empty
tailscale status --json | python3 -c "import sys,json;d=json.load(sys.stdin);print([p['DNSName'] for p in d['Peer'].values() if '<app>' in p['DNSName']])"
# expect []  (device gone from control, session stuck)
```

Recover (live-state only — do NOT touch app manifests):
```sh
kubectl -n tailscale-system delete statefulset ts-<app>-<hash> --ignore-not-found
kubectl -n tailscale-system delete secret       ts-<app>-<hash>-0 --ignore-not-found
sleep 20
kubectl -n tailscale-system get pods -l tailscale.com/parent-resource=<app>
# pod logs: "Startup complete, waiting for shutdown signal"; wgengine Reconfig with peers
kubectl -n tailscale-system get secret ts-<app>-<hash>-0 \
  -o jsonpath='{.data.device_fqdn}' | base64 -d; echo
# expect <app>.taila659a.ts.net
```

## 2. TCP listener verification (syncthing 22000 etc.)

NEVER `curl https://<host>:22000/` — raw-TLS protocol hangs even when healthy.
```sh
# external (may be blocked by tailnet egress — not authoritative)
nc -z -w 10 <app>.taila659a.ts.net 22000 && echo "TCP 22000 OPEN" || echo "FAIL (verify in-cluster)"

# authoritative: in-cluster through the gateway LB Service
kubectl -n <app-ns> run tcptest --rm -i --tty --image=busybox:1.36 \
  --restart=Never --command -- sh -c \
  'nc -zv -w 8 <app>.envoy-system.svc.cluster.local 22000 2>&1; echo EXIT=$?'
# expect: "<app>.envoy-system.svc.cluster.local (10.x.y.z:22000) open"  EXIT=0
```
UDP open check (less definitive — nc udp "succeeds" even if filtered):
`nc -z -u -w 6 <app>.taila659a.ts.net 22000 && echo "UDP 22000 OPEN"`.

## 3. Status-query one-liners

```sh
# BackendTLSPolicy nests under .status.ancestors[] (top-level jsonpath is empty)
kubectl -n <ns> get backendtlspolicy <app> -o jsonpath='{.status.ancestors[0].conditions[?(@.type=="Accepted")].status}'

# Cert SAN (macOS openssl has no -ext)
kubectl -n <ns> get secret <tls> -o jsonpath='{.data.tls\.crt}' | base64 -d \
  | openssl x509 -noout -text | grep -A1 'Subject Alternative Name' | tr ',' '\n'

# Gateway Programmed + address
kubectl -n <ns> get gateway <app> -o jsonpath='{.status.conditions[?(@.type=="Programmed")].status} {.status.addresses[0].value}'
```

## 4. Flux reconcile quirk

When source is already fetched, `flux reconcile kustomization <app> --with-source`
can hit a context-deadline inside the CLI. Use plain `flux reconcile kustomization
<app>` (no `--with-source`). A transient READY=False `dependency … is not ready`
blip clears on a second plain reconcile — confirm the dependency Kustomization
itself is READY first.
