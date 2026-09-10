---
name: book-copyparty
description: Configure and operate the copyparty file-sharing server.
version: 0.1.0
license: Apache-2.0
author: Hermes Agent
metadata:
  hermes:
    tags:
      - File Sharing
      - Self-Hosted
      - WebDAV
      - SMB
      - FTP
---

# Copyparty

Distilled operational knowledge for copyparty — a single-binary,
dependency-light file server (HTTP, WebDAV, FTP/S, SFTP, TFTP, SMB) with
resumable uploads, per-folder accounts/volumes, media indexing, and a web
UI. This skill does NOT cover internals/contrib plugins beyond what the docs
state; load a `references/` file when a specific area is in question.

Source: `9001/copyparty` README.md + `docs/` (example.conf, idp.md, rclone.md,
versus.md, up2k.txt, xff.md, design.txt). Default HTTP/HTTPS port is **3923**.

## When to Use

- Install copyparty (pip / uv / sfx / docker) and enable thumbnails/transcoding.
- Author `-v`/`-a` arguments or a `copyparty.conf` for accounts and volumes.
- Set per-folder permissions (read/write/move/delete, write-only, get-only).
- Enable resumable up2k uploads, unpost, self-destructing uploads.
- Run the FTP/SFTP/WebDAV/TFTP/SMB servers or mount a server with rclone.
- Put copyparty behind nginx/caddy/traefik or an IdP (Authelia/Authelia-style).
- Wire event hooks (upload/rename/delete) or ZeroMQ notifications.

## Prerequisites

- Python 3 (any platform). Install options:
  - `python3 -m pip install --user -U copyparty` (PyPI)
  - `uv tool run copyparty` (if `uv` is installed)
  - Self-extracting `copyparty-sfx.py` from releases (no install needed)
- Optional deps for media: `Pillow` + `ffmpeg` (Debian: `apt install
  --no-install-recommends python3-pil ffmpeg`).
- Optional: `paramiko` (SFTP), `impacket==0.13.0` (SMB), `mutagen` or `ffprobe`
  (audio tags).
- Full CLI help: `python copyparty-sfx.py --help` (or `--help-accounts`,
  `--help-flags`, `--help-hooks`).

## How to Run

Invoke through the `terminal` tool. Start the server, then manage via the
browser UI (control-panel) and config reload.

```bash
# quickstart: read/write to cwd for everyone, port 3923
python3 copyparty-sfx.py

# with indexing + an account + a shared volume
python3 copyparty-sfx.py -e2dsa -e2ts -a foo:bar -v /mnt/music:music:r:rw,foo

# config-file mode (recommended for anything non-trivial)
python3 copyparty-sfx.py -c /etc/copyparty/party.conf
PRTY_CONFIG=/etc/copyparty/party.conf python3 copyparty-sfx.py   # env override (docker)
```

## Quick Reference

- Default port: `3923` (HTTP/HTTPS). Other ports: `3921` ftp, `3922` sftp,
  `3945` smb, `3969` tftp, `3990` ftps, `69` tftp, `5353` mdns, `1900` ssdp,
  `12000-12099` passive-ftp.
- Indexing: `-e2dsa` (files), `-e2ts` (audio tags via ffprobe/mutagen).
- Volume arg: `-v src:dst:perm:perm` (local path, URL path, perms).
- Account arg: `-a usr:pwd`.
- Reload accounts/volumes at runtime: `kill -s USR1 $(pidof copyparty)` or the
  `[reload cfg]` button (needs `a` admin on a volume). `[global]` needs restart.
- Permissions: `r w m d . g G h a A`
  (read/write/move/delete/dots/get/upget/html/admin/all).
- Reverse-proxy real-IP: `--xff-hdr <hdr> --xff-src <cidr|lan> --rproxy
  <1|-1..>`.
- Version-checker: `--vc-url https://api.copyparty.eu/advisories`.
- ZeroMQ hooks: `--xau zmq:pub:tcp://*:5556`.

## Procedure

1. Pick an install path (see `references/01-install-quickstart.md`).
2. Define accounts/volumes via args or a config file
   (`references/02-accounts-volumes.md`).
3. Enable servers/protocols and real-IP handling
   (`references/05-protocols-servers.md`, `references/06-reverse-proxy-idp.md`).
4. Tune indexing, logging, thumbnails (`references/03-server-config.md`).
5. Mount from clients / wire hooks (`references/07-clients-rclone-curl.md`,
   `references/08-event-hooks.md`).
6. Verify (`references/10-verification.md` style check below).

## Pitfalls

- Running with NO arguments gives everyone read/write to the current folder.
- `[global]` config changes require a restart; only
  `[vol]`/`[accounts]`/`[groups]` hot-reload.
- FTP uploads are NOT resumable (up2k/HTTP is). SMB is slow, possibly not truly
  read-only — sandbox it.
- Behind a proxy/WAF without correct `--xff-*`, all clients share one IP and get
  banned (`thank you for playing`).
- Windows built-in WebDAV has many bugs; prefer rclone. See
  `references/06-reverse-proxy-idp.md`.

## Verification

A running instance answers on 3923 and lists volumes per permissions:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3923/
# expect 200 for readable webroot; 401/403 for restricted volumes without creds
```

## Reference Files (load on demand via `skill_view` file_path="references/<file>")

- `references/01-install-quickstart.md` — install methods, deps, quickstart,
  mirrors, systemd/docker.
- `references/02-accounts-volumes.md` — `-a`/`-v` syntax, permission matrix,
  groups, volflags, shadowing, dotfiles, IdP volumes.
- `references/03-server-config.md` — global options: indexing, logging,
  version-checker, zeroconf, thumbnails, zip/tar downloads.
- `references/04-browser-uploading.md` — UI tabs, hotkeys, up2k resume, unpost,
  self-destruct, file-search, file manager.
- `references/05-protocols-servers.md` — FTP/S, SFTP, WebDAV, TFTP, SMB: flags,
  ports, client quirks.
- `references/06-reverse-proxy-idp.md` — nginx/caddy/traefik, real-IP,
  unix-socket, IdP headers, webdav-over-IdP.
- `references/07-clients-rclone-curl.md` — rclone mount/sync, curl upload
  examples, u2c.py, connect page.
- `references/08-event-hooks.md` — `--xau` hooks, ZeroMQ pub/push/req, mtag
  upload events.
- `references/09-versus-alternatives.md` — how copyparty compares to
  Nextcloud/Seafile/dufs/Filebrowser/rclone.
