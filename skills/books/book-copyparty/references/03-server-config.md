# Server Config (copyparty)

Config is args and/or a config file (`-c some.conf`); everything in `--help`
works in the `[global]` section, everything in `--help-flags` works as a
volflag. `kill -s USR1` / `[reload cfg]` reloads accounts+volumes (not
`[global]`).

## Indexing

- `-e2dsa` general file indexing (names, sizes, dates)
- `-e2ts` audio metadata indexing (needs `ffprobe` or `mutagen`)
- `-e2d` uploads database (enables unpost/up2k registry)

## Logging

- Log goes to stdout by default (terminal/journalctl/docker collector).
- `-q` disables stdout logging (small perf gain).
- `-lo logfolder/cpp-%Y-%m-%d.txt` logs to a dated file (new file each day).
- `--rlo` controls behavior when the log filename is taken.
- `--flo 2` disables colors in the logfile; `--no-ansi` disables everywhere.
- `log-date: %Y-%m-%d` adds dates to stdout too.

## Version-checker (CVE monitoring)

- `--vc-url https://api.copyparty.eu/advisories` (everything noteworthy) or
  `.../advisories-panic` (only critical) or `.../advisories-all` (everything).
- `--vc-age 3` check interval in hours (default 3).
- `--vc-exit` panic-exit if the running version is vulnerable (else warns
  admins).
- `--vc-sev medium` (github feed only) min severity.
- Test with `--vc-url https://api.copyparty.eu/advisories-test`.

## Zeroconf / mdns

- `-z` enables zeroconf; `-qr` shows a QR code for quick mobile access.
- mdns/ssdp announce on `5353`/`1900`.

## Thumbnails

- `g` / `田` toggles grid view; `t` toggles icons/thumbnails.
- `--grid` / volflag `grid` default grid; `--no-thumb` / `--no-vthumb` disable.
- Image thumbs: Pillow (3x faster/safer than FFmpeg) / pyvips / FFmpeg.
  Video: FFmpeg. Audio: spectrograms via FFmpeg (`--no-athumb`).
- Folder cover names: `folder.png folder.jpg cover.png cover.jpg` (ordered;
`--th-covers no` disables). HEIF needs libvips (absent in docker for legal
reasons).
- Per-volume: `dthumb` (all), `dvthumb`/`dathumb`/`dithumb` (video/audio/image).
- `--ext-th=exe=/icons/exe.png` maps a thumbnail per extension.
- Cache eviction is max-age based.

## Zip / tar downloads

Select archive type in `[⚙️]` config tab or via URL suffix:

- `?tar` gnutar · `?tar=pax` pax · `?tar=gz` tgz · `?tar=xz` txz · `?tar=bz2`
- `?zip` zip · `?zip=dos` cp437 (fix win7 glitchy names) · `?zip=crc`
  cp437+crc32
- Compression levels: `?tar=gz:9` (default 3), `?tar=xz:9` (default 1),
  `?tar=bz2:9` (default 2). Dotfiles excluded unless the account may list them.

## Misc global options

- `--ipu 192.168.123.0/24=spartacus` autologin by CIDR (IP auth).
- `--ban-pw` bruteforce ban (default: 24h ban after 9 fails/hour).
- `-i unix:770:www:/dev/shm/party.sock` listen on a unix socket (770 = group
  `www`).
