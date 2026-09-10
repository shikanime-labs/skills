# Versus: Alternatives to copyparty

From `docs/versus.md` (compared against awesome-selfhosted). Symbol legend:
`█`=yes, `╱`=partial, `•`=maybe, ` `=no. Review marks: ✅ advantage over
copyparty, 💾 what copyparty offers instead, 🔵 similar, ⚠️ copyparty does better,
🔥 hazard.

## Recommendations (when to pick something else)

- **kodbox** — fantastic alternative if you don't mind Chinese software; but
  shared files must live inside its filesystem.
- **Seafile** / **Nextcloud** — heavier; AGPL license is thorny; copyparty is
  much better at uploads (resumable, accelerated); both require moving files
  into their filesystem.
- **Filebrowser** / **dufs** — simpler copyparties with a settings GUI;
  portable, work with existing folders, but copyparty wins on uploads + extras.

## Where copyparty leads

- Uploads: resumable (up2k), chunk-checksummed, no filesize limit even behind
  Cloudflare, parallel connections, mtime preserved, safe to restart mid-upload.
- Protocols: HTTP + WebDAV + FTP/S + SFTP + TFTP + SMB from one binary.
- Per-folder per-user permissions, write-only folders, filekeys, unpost,
self-destruct, folder sync, FUSE client, media indexing/transcoding, thumbnails.

## Where others lead

- Nextcloud/Seafile: full two-way sync, calendar/contacts, richer app
  ecosystems.
- kodbox: polished UI, Chinese-ecosystem integrations.

## Notes

- copyparty is intentionally "bloated" feature-wise but dependency-light and
  single-binary; the README itself admits undocumented features exist — run
  `--help` for the full option surface.
- Full matrix covers: hfs2/hfs3, nextcloud, seafile, rclone, dufs, chibisafe,
  kodbox, filebrowser, filegator, sftpgo, arozos, updog, goshs, gimme-that, ass,
  linx, h5ai, autoindex, miniserve, pingvin-share.
