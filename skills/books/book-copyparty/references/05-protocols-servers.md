# Protocol Servers (copyparty)

All protocols share the same accounts/volumes/permissions. Default HTTP port
3923.

## FTP / FTPS (`--ftp 3921`, `--ftps` for explicit TLS)

- Based on pyftpdlib. Needs a dedicated port (not shared with HTTP API).
- Uploads are NOT resumable (delete + restart). Runs active mode by default →
  set `--ftp-pr 12000-13000` (range split in half if both ftp+ftps enabled).
- Login: any username + your password, OR put password in the username field
  (unless `--usernames` is set).
- Clients: `lftp -u k,wark -p 3921 127.0.0.1 -e ls`;
  `curl ftp://127.0.0.1:3921/`; `curl --ssl-reqd ftp://127.0.0.1:3990/`.

## SFTP (`--sftp 3922`)

- NOT ftps — ssh-based, prefers ssh keys. Needs `paramiko` (docker:
  `ac`/`im`/`iv`/`dj`).
- `~700 MiB/s` (slower than webdav/ftp).
- `--sftp-key 'david ssh-ed25519 AAAA...'` bind a key to a user.
- `--sftp-pw` enable password login (default keys-only).
- `--sftp-anon foo` anonymous login (same access as unauthenticated web).

## WebDAV (read-write)

- Great for mounting in OS file explorer. Control-panel `[connect]` (`/?hc`)
  gives per-OS instructions.
- Login: any username + password, or password-in-username (unless
  `--usernames`).
- macOS Finder: Go → Connect to Server → `http://192.168.123.1:3923/`.
- Editing existing files needs the Delete permission + often the `daw` volflag
  (or `x-oc-mtime` header). Without `daw`, clients create copies like
`notes.txt-1771978661...txt`. WARNING: `daw` makes PUT overwrite existing files.
- `dav-port` option as alternative. IdP auth can break some WebDAV clients.

## TFTP (`--tftp 3969`)

- For 90s hardware (e.g. RTX DECT base flashing). Based on partftpy.
- No accounts: read from world-readable, write to world-writable, overwrite in
  world-deletable. Dedicated UDP port; port 69 needs root → NAT 69→3969.
- Only octet mode; no RFC 7440 (slow over WAN). `curl --tftp-blksize 1428`.

## SMB / CIFS (`--smb` ro, `--smbw` rw)

- UNSAFE, SLOW, not WAN-recommended. Deps: `impacket==0.13.0`.
- Big warnings: read-only may not be truly read-only; not fully VFS-integrated
  (possible path traversal) → use `prisonparty`/`bubbleparty` + `--smb-port`.
- Only first ~400 files visible in big folders (impacket#1433 workaround;
`--smb-nwa-1` disables but kills perf). Not compatible with
pw-hashing/`--usernames`.
- Listens on first IPv4 `-i` only. Port 445 privileged → NAT 445→3945.
- Auth: username `$user`/pwd `$pw`, OR username `$pw`/pwd `k`.

## WOPI

- Edit Office docs in web UI; only Collabora Online supported (OnlyOffice
  pending).
