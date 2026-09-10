# Accounts & Volumes (copyparty)

A **volume** maps a filesystem path (`src`) to a URL path (`dst`) with
per-user/per-group permissions. Prefer a config file over args for anything
complex; it can be hot-reloaded.

## Argument syntax

- Account: `-a usr:pwd`
- Volume: `-v src:dst:perm:perm` where perm = `permString,acctList`
  - `-v .::r` → current folder as webroot, readable by anyone
- `-v /mnt/music:music:r,u1,u2:rw,u3` → `/music` read-only for u1/u2, rw for u3
  - grant same perm to many: `-v .::r,usr1,usr2:rw,usr3,usr4`
- The config file always wins on conflict.

## Permission matrix

- `r` read: browse, download, zip/tar, see filekeys/dirkeys
- `w` write: upload, move/copy INTO this folder
- `m` move: move files/folders FROM this folder
- `d` delete: delete files/folders
- `.` dots: may request dotfiles be shown in listings
- `g` get: download files only, cannot see folder contents or zip/tar
- `G` upget: like `g` but uploaders see their own filekeys (needs `fk` volflag)
- `h` html: like `g` but folders return index.html (no filekey needed)
- `a` admin: see upload time, uploader IPs, config-reload
- `A` all: shorthand for `rwmda.`

## Groups

- Define in `[groups]`: `g1: u1, u2`
- Reference as `@g1`. Special groups: `@acct` = all logged-in users,
  `*` = everyone (incl. anonymous), `*,@acct` = logged-in only,
  `*,@acct` minus: `*,@acct` / `*,-@acct` (not logged in), `@admins,-james`.

## Config-file shape

```yaml
[accounts]
  u1: p1
[groups]
  g1: u1, u2
[/music]
  /mnt/music
  accs:
    r: u1, u2
    r: @g1
    r: @acct
    rw: u3
[/inc]
  /mnt/incoming
  accs:
    w: u1      # upload but cannot see/download
    rm: u2     # browse + move files out
[/i]
  /mnt/ss
  accs:
    rw: u1
    g: *       # everyone can fetch if they know the URL
  flags:
    fk: 4      # 4-char filekey per file URL
```

Comments need 2 spaces before `#`. Reload with `kill -s USR1` or `[reload cfg]`
button (needs `a` on a volume). Changes to `[global]` need a restart.

## Common volflags (per-volume, see `--help-flags`)

- `fk=N` filekey length N (enables `G` upget); `wg` lets anon upload + get own
  link
- `e2d` uploads database (enables unpost); `e2t` tag indexing; `d2t` disable
  parsers
- `dthumb` disable all thumbnails; `dvthumb`/`dathumb`/`dithumb`
  video/audio/image
- `grid` default grid view; `gsel` desktop multiselect; `dots`/`dotsrch`
  dotfiles
- `lifetime` max upload lifetime (self-destruct); `nodupe` reject duplicate
  uploads
- `no-thumb`/`no-vthumb` global thumbnail toggles

## Shadowing (hide subfolders)

Mount another volume on top; omit `accs:` to block. Use `//NULL` to fully unmap:

```yaml
[/drives]
  /mnt
  accs:
    r: *
[/drives/foo/bar]
  //NULL        # /mnt/foo/bar never accessible
```

Works for single files too (files can be volumes).

## Dotfiles

Unix hidden files (leading `.`) are accessible if the name is known but hidden
from listings unless `-ed` global, volflag `dots`, or user has `.` permission.
Appear in search only with `dots`+`dotsrch`. Ignored for `[shares]`.

## IdP / dynamic volumes

- URL may contain `${u}`/`${g}` → a volume per user/group, revived on first
  request after restart (inherits parent perms until then — place inside a sane
  parent volume).
- `idp-store`: 1=log only (default), 2=remember usernames, 3=usernames+groups.
