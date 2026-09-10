# Install & Quickstart (copyparty)

## Install methods

- **Self-extracting (sfx)** — no Python needed: download `copyparty-sfx.py`
  from releases/latest. Unpacks embedded tar.gz into `$TEMP` then runs.
  `python3 copyparty-sfx.py` (or double-click on Windows).
- **PyPI**: `python3 -m pip install --user -U copyparty` → run `copyparty` or
  `python -m copyparty`.
- **uv**: `uv tool run copyparty`.
- **zipapp (pyz)** — alternative if sfx scares you; slightly worse perf.
- **Docker**: `docker run --rm -it copyparty/ac --help`; images
  `ac`/`im`/`iv`/`dj` include SFTP deps.
- **OS packages**: Arch (AUR), Homebrew, NixOS module, Synology DSM
  (`docs/synology-dsm.md`), Termux (Android), a-Shell (iOS).
- **Isolation launchers**: `bin/prisonparty.sh` (chroot) or `bin/bubbleparty.sh`
  (bubblewrap) — recommended if you don't fully trust the binary.

## Mirrors (non-GitHub)

- `https://copyparty.eu/py` (= sfx), `/pyz` (zipapp), `/en` (english-only sfx),
  `/enz` (enterprise pyz), `/cli` (online helptext).

## Optional dependencies (media features)

- **Alpine**: `apk add py3-pillow ffmpeg`
- **Debian**: `apt install --no-install-recommends python3-pil ffmpeg`
- **Fedora**: `dnf install python3-pillow ffmpeg --allowerasing`
- **FreeBSD**: `pkg install py311-sqlite3 py311-pillow ffmpeg`
- **macOS**: `brew install pillow ffmpeg` (or `port install py-Pillow ffmpeg`)
- **Windows**: `python -m pip install --user -U Pillow` + manual ffmpeg (do NOT
  use winget/Microsoft Store — breaks PATH). copyparty.exe ships Pillow.
- SFTP needs `paramiko`; SMB needs `impacket==0.13.0`; audio tags need
  `mutagen` or `ffprobe`.

## Quickstart

- No args → everyone gets read/write to the **current folder** on port 3923.
  Use accounts/volumes before exposing it.
- Recommended options:
  - `-e2dsa` enable general file indexing
  - `-e2ts` enable audio metadata indexing (needs ffprobe or mutagen)
  - `-v /mnt/music:/music:r:rw,foo -a foo:bar` → share `/mnt/music` as `/music`,
    readable by anyone, read-write for user `foo` (pwd `bar`).

## Expose over the internet

- Cloudflare quick tunnel: `cloudflared tunnel --url http://127.0.0.1:3923`
  (shows a shareable URL). Run copyparty with `--xff-hdr cf-connecting-ip`.
- Permanent tunnel / domain: see README "permanent cloudflare tunnel".

## Service scripts (servers)

- `contrib/systemd/copyparty.service` (type=notify; reads `NOTIFY_SOCKET`)
- `contrib/systemd/prisonparty.service` (chroot)
- `contrib/podman-systemd/` (Podman + systemd)
- `contrib/openrc/copyparty`, `contrib/rc/copyparty` (FreeBSD)
- `contrib/nginx/copyparty.conf` (reverse proxy)
- NixOS module available.

## Firewall ports to open

```text
69:tftp  1900:ssdp  3921:ftp  3922:sftp  3923:http/https
3945:smb  3969:tftp  3990:ftps  5353:mdns  12000-12099:passive-ftp
```
