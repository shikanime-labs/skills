# Creating the first wiki page via CDP

The full procedure for the one UI-only wiki step from `sks-edit`
references/wiki/guide.md — creating `Home` on
`https://github.com/<org>/<repo>/wiki` from the shell. No REST, GraphQL, or CLI
endpoint covers page creation (REST `repos/.../wiki/pages` 404s; GraphQL
introspection yields only `hasWikiEnabled`); and the `<repo>.wiki.git` remote
does not exist until a first page is saved. Works for one repo at bootstrap or a
backfill sweep over many.

## Prerequisites

- A dedicated automation Chrome profile runs with
  `--remote-debugging-port=9222` and holds an authenticated GitHub session
  (any tab on `github.com`). Never the operator's daily browser — see
  Pitfalls.
- `websocket-client` importable (`python3 -c "import websocket"`); stdlib
  `urllib.request` does the REST half (the `--enable-wiki` flag flip).

## Procedure

1. **Find a GitHub tab** — the debug port lists targets; reuse a logged-in tab
   rather than opening a new one:

   ```bash
   curl -s http://localhost:9222/json/list
   # pick the entry with "type": "page" whose "url" starts with https://github.com/
   # note its "webSocketDebuggerUrl"
   ```

2. **Connect with Origin suppressed.** Chrome 155+ rejects WebSocket
   handshakes carrying an `Origin` header (403 "Rejected an incoming WebSocket
   connection"); `websocket-client` sends one by default.
   `suppress_origin=True` is mandatory:

   ```python
   import websocket

   ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
   ```

3. **Navigate to the new-page editor** over the same connection —
   `Page.enable`, `Page.navigate` to
   `https://github.com/<org>/<repo>/wiki/_new`, then wait ~4s for render. If
   the wiki flag is still off this URL 404s — flip
   `gh repo edit <org>/<repo> --enable-wiki` first and re-navigate.

4. **Fill title and body** by id — the editor ids are stable even when
   surrounding DOM shifts:

   ```js
   (() => {
     const title = document.querySelector('#gollum-editor-page-title');
     const body = document.querySelector('#gollum-editor-body');
     if (!title || !body) return {found: false};
     title.value = 'Home';
     body.value = 'Index of this repo\'s technical documentation.';
     return {found: true, title: title.value};
   })()
   ```

5. **Scroll, then click Save.** The commit-summary field and the Save button
   sit below the fold; `scrollIntoView({block: 'center'})` the button, wait
   ~0.5s, re-read its rect, then dispatch both halves of the click at the
   same viewport coords. The button's label is `Save page` (verified
   2026-10-20 live run) — match on it explicitly, not on `'Save'`:

   ```python
   ws: Input.dispatchMouseEvent type=mousePressed  x, y, button=left, clickCount=1
   ws: Input.dispatchMouseEvent type=mouseReleased x, y, button=left, clickCount=1
   ```

6. **Verify by remote materialization, not DOM.** The wiki remote only
   exists once a page is saved — its appearance IS the proof:

   ```bash
   git ls-remote git@github.com:<org>/<repo>.wiki.git HEAD
   # a HEAD sha = the page exists; 404/exit 128 = retry step 4
   ```

## Backfill sweep shape

Loop over the repo list: flip the flag (`gh repo edit --enable-wiki`) →
navigate to `/wiki/_new` → fill → save → `git ls-remote` verify → record
before/after per repo to a JSONL as you go. At the auto-close sweep's scale
(#301, 23 repos) the whole pass is minutes.

## Pitfalls

- **Never drive the user's live browser.** Synthetic input into the daily
  browser (Zen/Chrome with personal sessions) is forbidden without explicit
  per-task authorization: mid-run, the target `window_id` rebinds to another
  window of the same process — one capture showed a personal checkout page
  where the wiki form had been. Hard stop the moment a capture shows a page
  you did not open. Re-check `window_title` matches the wiki editor before
  EVERY input action, not just the first.
- **Dedicated profile or nothing.** The safe shape is a separate automation
  browser profile holding only the GitHub session; the user's daily browser
  is off-limits even though it is the authenticated one.
- **osascript/System Events need assistive access** — `AXPress` of the Save
  button fails with error -1719 unless the host terminal has been granted
  Accessibility; grant or skip, do not retry.
- **Background input refused on same-pid ambiguity** — Chrome-family
  processes own several windows; process-scoped keystrokes cannot be proven
  to reach the target. `delivery_mode: "foreground"` works but fronts the
  window and races the user's focus (a Hermes dashboard stole one Tab
  mid-walk). Expect focus walks (click textarea → Tab to Edit message →
  Tab to Save → Enter) to be the last resort, never the plan.
- **403 on WS connect** — Origin header present; fix is `suppress_origin=True`
  (do NOT restart Chrome with `--remote-allow-origins=*`; that flag widens the
  debug port to any local process for the browser's lifetime).
- **Click misses** — element below the fold; `scrollIntoView` before reading
  coordinates, and re-read the rect AFTER the scroll.
- **Editor id drift** — if `#gollum-editor-*` is gone, re-locate by label
  text ("Page title", the markdown textarea) the way the auto-close recipe
  finds its checkbox; never trust a hardcoded CSS path twice.
- **Sweep races** — drive ONE tab per run; navigating a shared tab from two
  loops races page loads.
- **`curl` cannot create pages** — same class as the auto-close checkbox:
  server-rendered per session, no parseable API surface.
