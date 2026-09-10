# Clients: rclone, curl, u2c (copyparty)

## rclone mount (full filesystem)

- Server `/?hc` (connect page) auto-generates rclone config for your server.
- Manual config (`~/.config/rclone/rclone.conf`):

  ```ini
  [cpp-rw]
  type = webdav
  vendor = owncloud
  url = http://127.0.0.1:3923/
  headers = Cookie,cppwd=hunter2
  pacer_min_sleep = 0.01ms

  [cpp-ro]
  type = http
  url = http://127.0.0.1:3923/
  headers = Cookie,cppwd=hunter2
  pacer_min_sleep = 0.01ms
  ```

(Windows: same, drop into `%userprofile%\.config\rclone\rclone.conf`; needs
WinFsp.)

- Mount: `rclone mount --vfs-cache-mode writes --vfs-cache-max-age 5s
  --attr-timeout 5s --dir-cache-time 5s cpp-rw: W:` (`cpp-ro:` is ~2x faster,
  read-only).
- `vendor=owncloud` enables `x-oc-mtime` (retain mtime), streaming, OCM5/SHA1.
  If it breaks, try `vendor=fastmail`.

## rclone sync

`rclone sync /usr/share/icons/ cpp-rw:fds/` — bidirectional, ubiquitous. For
faster/safer uploads prefer the up2k client `u2c.py` (on the connect page).

## curl uploads

- Plain PUT/POST works (curl-friendly). WebDAV: `curl -T file http://.../`.
- FTP: `curl ftp://127.0.0.1:3921/` ; FTPS: `curl --ssl-reqd
  ftp://127.0.0.1:3990/`.
- TFTP: `curl --tftp-blksize 1428 -T firmware.bin tftp://127.0.0.1:3969/`.

## Speed reference (same win10 host)

- rclone↔rclone: 1070 MiB/s · rclone-client + `copyparty -ed -j16`: 570 ·
`copyparty -ed`: 220 · partyfuse.py client: 100 (1gbit LAN: 75 partyfuse / 92
rclone / 103 cp -ed -j16).

## FUSE client

`bin/partyfuse.py` (read-only mount). Up2k command-line uploader: `bin/u2c.py`.
Both linked from the server connect page (`/?hc`).
