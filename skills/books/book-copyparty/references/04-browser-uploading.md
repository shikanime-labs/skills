# Browser UI & Uploading (copyparty)

## Main tabs (UI)

- `[🔎]` search by size/date/path/name/mp3-tags
- `[🧯]` unpost (undo/delete own uploads)
- `[🚀]` / `[🎈]` uploaders (up2k / bup)
- `[📂]` mkdir · `[📝]` new textfile · `[📟]` send message
- `[🎺]` audio player config · `[⚙️]` client config

## Key hotkeys (always qwerty)

- `?` help · `B` breadcrumbs/navpane · `I/K` prev/next folder · `M` parent
- `G` list/grid · `T` thumbnails/icons · `ESC` close
- `ctrl-K` delete · `ctrl-X` cut · `ctrl-C` copy · `ctrl-V` paste · `Y` download
- `F2` rename
- Audio: `J/L` prev/next, `U/O` ±10s, `0-9` 0-90%, `P` play/pause
- Viewer: `J/L` prev/next, `F` fullscreen, `R` rotate, `C` continue-next, `V`
  loop

## up2k (resumable uploader — default drag-drop)

Advantages:

- Recursive folder drop; chunks checksummed; autoresume on network loss or
  browser/PC reboot (re-drop same files). Corruption → client reuploads chunk.
- Client skips chunks already on server; no filesize limit (even behind
  Cloudflare).
- Parallel connections → high speed on some links.
- Preserves file mtime.
- Safe to restart/upgrade copyparty mid-upload; clients resume.

UI controls: parallel-upload count, `[🏃]` analyze-while-upload, `[🥔]` simple UI,
`[🛡️]` overwrite policy (never / if older / if different), `[🎲]` randomize
names, `[🔎]` upload/search toggle. Tabs: `[ok]` done, `[ng]` failed/rejected,
`[done]`, `[busy]`, `[que]`. Enable `turbo` to skip re-hashing finished files.

Server knobs: `--u2sz` stay under proxy request-size limit; `--u2ow 2` default
overwrite-if-different (needs delete perm).

## file-search

Drop files → client hashes, server reports if each exists → `[ok]` with link or
`[ng]`. Search a wark directly with `w = <wark>` in the `raw` field.

## unpost

Undo accidental uploads via `[🧯]`. Allowed only for files uploaded within
`--unpost` seconds (default 12h) and only if server runs `-e2d`.

```yaml
[global]
  e2d
  unpost: 43200
```

## self-destruct

Per-volume `lifetime` upload rule sets max stay; client may pick a shorter
expiry in the up2k UI (also shrinks the unpost window).

## race the beam

Download a file while it is still uploading (up2k only).

## file manager

Cut/paste, rename (`F2`/batch-rename), delete if permitted. Batch rename under
`[⚙️]`. RSS/OPDS feeds, recent uploads, media player (m3u8 playlists, OS media
controls, opus/mp3 transcode, android playback fix), textfile/markdown viewers
(with live-growing-file streaming) all built in.
