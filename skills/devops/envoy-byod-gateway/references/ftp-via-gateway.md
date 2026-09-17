# FTP / passive-data through a BYOD Gateway

Reusable lesson from migrating `apps/copyparty` off a direct Tailscale
`LoadBalancer` onto a Gateway-API Envoy Gateway. The pitfall that bit us:
**`ftp-nat` (PASV masquerade address) must be a literal IPv4, not a hostname.**

## Why a hostname breaks passive mode

copyparty's FTP server is pyftpdlib. In `copyparty/ftpd.py`:

```python
if self.args.ftp_nat:
    h2.masquerade_address = self.args.ftp_nat   # ftp-nat config value
...
if self.args.ftp_pr:
    p1, p2 = [int(x) for x in self.args.ftp_pr.split("-")]
    h2.passive_ports = list(range(p1, p2 + 1))   # ftp-pr config value
```

`masquerade_address` is stamped **verbatim** into the `227 Entering Passive
Mode (h1,h2,h3,h4,p1,p2)` reply as a dotted-quad. pyftpdlib does NOT resolve
it. A hostname like `copyparty.taila659a.ts.net` produces a malformed PASV
reply → clients fail passive transfers entirely.

**Fix:** `ftp-nat` is a static tailnet IP, e.g. `100.68.52.27`.

## Pinning a static tailnet IP for the masquerade address

The BYOD Gateway's EnvoyProxy is a `*ts.net` device. Its IP is normally
dynamic (MagicDNS name stable, IP may rotate). To give `ftp-nat` a stable
literal, pin the IP on the `EnvoyProxy`'s `envoyService` annotations:

```yaml
# apps/<app>/overlays/nishir-tailnet/envoyproxy.yaml
spec:
  provider:
    type: Kubernetes
    kubernetes:
      envoyService:
        type: LoadBalancer
        loadBalancerClass: tailscale
        annotations:
          tailscale.com/hostname: <app>
          tailscale.com/tags: "tag:web,tag:ftp"
          tailscale.com/tailnet-ip: 100.68.52.27   # pin → stable masquerade addr
```

Tailscale operator 1.98.x supports `tailscale.com/tailnet-ip`. Reuse a
**released** IP from the old direct-LB Service you deleted (it was already in
`100.64.0.0/10` and tied to this hostname) — lowest collision risk. Verify
post-deploy: `kubectl -n shikanime get svc <app> -o jsonpath='{.metadata.annotations}'`
shows the pinned IP, and `tailscale status --json` lists it as a `Peer[].TailscaleIPs`.

If the annotation is silently ignored (wrong spelling for your operator
version), the device still gets MagicDNS and may re-acquire the same IP — but
`ftp-nat` would be stale. Confirm the pin landed before trusting passive mode.

## Passive port range vs Gateway listener cap

Gateway API caps a Gateway at **64 listeners** total. A classic FTP passive
range (`12000-12099` = 100 ports) cannot become 100 listeners. Options:

- **Reduced representative range:** expose N ports as Gateway TCP listeners
  (N ≤ 64 minus your other listeners) and set `ftp-pr` to match exactly. We
  used `12000-12009` (10 listeners) for copyparty. The rest of the range is
  unreachable through the Gateway — fine for a personal file server (10
  concurrent passive transfers).
- **Keep passive on the ClusterIP Service + netpol** if you need the full
  range: the `ftp` Service becomes `type: ClusterIP`, `patch-sts` opens the
  container ports, `netpol` admits the `ftp-data-N` ports, and the Gateway
  only carries the control/ftps/sftp listeners. Direct LB dropped, but
  passive still needs the listener count under 64.

Each `ftp-data-<port>` listener needs its own `TCPRoute` (Gateway API: one
route per listener/sectionName) — you cannot collapse a port range into one
TCPRoute.

## Verification

```sh
kustomize build apps/<app>/overlays/nishir-tailnet > /tmp/out.yaml
grep -E "ftp-nat|tailnet-ip" /tmp/out.yaml   # expect literal IP in both
# cluster build:
bash verify.sh 2>&1 | tail -3                 # expect "docs: 85", no stale refs
```

## Netpol belongs in the overlay, not base

The Gateway ingress source (`envoy-gateway-system` + `app.kubernetes.io/name: envoy`)
is **tailnet-specific**. Keep `base/netpol.yaml` a deny-by-default skeleton
(`ingress: []`, only `podSelector` + `policyTypes`) and add the envoy `from:`
block as a `patch-netpol.yaml` in the `nishir-tailnet` overlay (already wired
in that overlay's `kustomization.yaml` `patches:`). Pattern (copyparty, verified):

- `base/netpol.yaml`: `{ podSelector, policyTypes: [Ingress], ingress: [] }`.
- `overlays/nishir-tailnet/patch-netpol.yaml`:
  ```yaml
  - op: add
    path: /spec/ingress/-
    value:
      from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: envoy-gateway-system
          podSelector:
            matchLabels:
              app.kubernetes.io/name: envoy
      ports:
        - port: http
        - port: ftp-control
        - port: ftp-data-12000
        # ... ftp-data-12001..12009
        - port: ftps
        - port: sftp
  ```
- **Do NOT put `tailscale-system` in netpol.** Tailscale only programs the
  Envoy `LoadBalancer` Service; it never sources pod-to-pod traffic. A
  `tailscale-system → app-pod` rule is dead weight (see pitfall #2).
- Verify the rendered overlay netpol has exactly ONE envoy `from:` block (no
  base+patch duplication) and `grep -c tailscale-system` on the rendered output
  is 0.
- Caveat: a deny-by-default base means a non-tailnet overlay (e.g. plain
  `nishir`) deploys the pod with NO ingress until that overlay adds its own
  `patch-netpol`. copyparty only ships via `nishir-tailnet`, so this is fine
  here; if you later add a non-tailnet deployment, give it its own patch.

## Repo ops: `nix fmt` is non-idempotent on origin/main

`nix fmt` (treefmt) in this repo reformats ~64 unrelated WIP files on EVERY
whole-tree run — it does not equal origin/main's formatting, so a whole-tree
run pollutes your PR with unrelated diffs.

**Fix (two ways):**
1. Format only your target dirs: `nix fmt apps/<app>` (fast, scoped). Note: a
   scoped `nix fmt apps/copyparty` can hang on flake evaluation — if it
   times out, fall back to whole-tree + restore.
2. Whole-tree then restore unrelated: `timeout 300 nix fmt`; then
   `git diff --name-only | grep -vE '^apps/(forgejo|copyparty|qbittorrent)/'`
   → loop `git checkout origin/main -- "$f"` for each. Leaves only your
   intended files formatted.

Always `git diff --name-only` after fmt and before commit to confirm the
changed set is exactly your intended scope.
