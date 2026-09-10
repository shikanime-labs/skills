# Reverse Proxy & IdP (copyparty)

## Reverse proxy basics

- Give copyparty its own domain/subdomain (recommended) OR location-based
  proxying with `--rp-loc=/stuff` (slight perf cost, more bugs).
- If copyparty errors `incorrect --rp-loc or webserver config`, the proxy is
  stripping the location prefix (see `ProxyPass` in the apache example).

## Real-IP (critical — features depend on client IP)

- Best: proxy sets a header with ONLY the real client IP; run copyparty with
  `--xff-hdr <hdr> --rproxy 1`.
- Or let copyparty parse: `--xff-hdr x-forwarded-for --xff-src <proxyCIDR>
  --rproxy <n>`, where `1` = header has one (correct) IP, negative = trust
  Nth-from-right (`-1` rightmost/nearest proxy, `-2` next hop…).
- Cloudflare: `--xff-hdr cf-connecting-ip` AND ensure nginx only accepts
  Cloudflare IPs (allowlist). `--xff-src lan` accepts private IPs.
- Without correct real-IP, everyone shares one IP → banned (`thank you for
  playing`).
- Config form:

  ```yaml
  [global]
    xff-src: lan
    xff-hdr: cf-connecting-ip
  ```

- Quick-and-insecure bypass (disables bot-detectors + unpost safety):
  `ban-404: no  ban-403: no  ban-422: no  ban-url: no  ban-pw: no`.

## Proxy configs shipped in `contrib/`

- `contrib/nginx/copyparty.conf` (recommended) · `contrib/apache/` ·
  `contrib/haproxy/` · `contrib/lighttpd/` (subdomain + subpath) ·
  `contrib/traefik/copyparty.yaml` (use v3.6.7+, CVE-2025-66490).
- Caddy UDS: `caddy reverse-proxy --from :8080 --to unix///dev/shm/party.sock`
- Caddy TCP: `caddy reverse-proxy --from :8081 --to http://127.0.0.1:3923`
- Perf boost + security: listen on unix socket
  `-i unix:770:www:/dev/shm/party.sock` (group `www` only).

## Reverse-proxy performance (uds vs tcp)

- no-proxy: 28.9k req/s, 6.9k MiB/s up, 7.4k down
- haproxy (uds): 18.75k / 3.5k / 2.37k
- caddy (uds): 9.9k / 3.75k / 2.2k
- nginx (uds): 18.7k / 2.2k / 1.57k
- apache (uds): 9.7k / 1.75k / 1.83k
- HTTP/1.1 often 5x faster than HTTP/2; nginx-QUIC/HTTP/3 experimental (slower
  uploads).

## Identity Providers (IdP)

Place copyparty behind a reverse-proxy whose middleware injects user headers.

- `[global]`: `idp-h-usr: X-Auth-User` (required), `idp-h-grp: X-Auth-Groups`
  (opt), `idp-h-key: secret` (secret header the proxy must send to prove headers
  are legit), plus `--xff-src` for the proxy subnet.
- `idp-store: 3` persists IdP users+groups across restarts (default 1 =
  log-only).
- `idp-hm-usr ^Header^remoteValue^localUser` maps a header VALUE to a local user
(repeatable; separator can be any char). Accounts must match the header identity
or be mapped this way.
- Header trust: copyparty does NOT validate JWTs. When the proxy is Envoy
  Gateway, use SecurityPolicy `forwardIDToken` + a `jwt` provider with
  `claimToHeaders` so EG validates the token (JWKS) and emits scalar claims as
  headers — EG's oauth2 filter order (9) runs before jwt_authn (10), so the
  forwarded token validates. Array claims (authelia `groups`) are NOT supported
  by claimToHeaders; drive volume access from copyparty `[groups]` config
  instead.
- Dynamic volumes with `${u}`/`${g}` in the URL are forgotten on restart,
  revived on first request (inherit parent perms until then). `idp-store`: 1
  log-only (default), 2 remember usernames, 3 usernames+groups.
- WebDAV over IdP: set Authelia rule `policy: one_factor`, and in rclone add
  `headers = Proxy-Authorization,basic <base64(user:pass)>`.
- Docker example: `docs/examples/docker/idp-authelia-traefik`.
