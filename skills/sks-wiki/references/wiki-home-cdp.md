# Creating the first wiki page via CDP

## Contents

- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
- [Backfill sweep shape](#backfill-sweep-shape)
- [Pitfalls](#pitfalls)
The full procedure for the one UI-only wiki step from `sks-wiki` — creating
`Home` on `https://github.com/<org>/<repo>/wiki` from the shell. No REST,
GraphQL, or CLI endpoint covers page creation (REST `repos/.../wiki/pages`
404s; GraphQL introspection yields only `hasWikiEnabled`); and the
`<repo>.wiki.git` remote does not exist until a first page is saved. Works
for one repo at bootstrap or a backfill sweep over many.

## Prerequisites

- A dedicated automation Chrome profile runs with
  `--remote-debugging-port=9222` and holds an authenticated GitHub session
  (any tab on `github.com`). Never the operator's daily browser — see
  Pitfalls.
- `websocket-client` importable (`python3 -c "import websocket"`); stdlib
  `urllib.request` does the REST half (the `--enable-wiki` flag flip).

## Procedure

1. **Attach** per `sks-dev` `references/cdp-attach.md`: find the
   logged-in GitHub tab on the debug port, connect with
   `suppress_origin=True`.

2. **Navigate to the new-page editor** over the same connection —
   `Page.enable`, `Page.navigate` to
   `https://github.com/<org>/<repo>/wiki/_new`, then wait ~4s for render. If
   the wiki flag is still off this URL 404s — flip
   `gh repo edit <org>/<repo> --enable-wiki` first and re-navigate.

3. **Fill title and body** by id — the editor ids are stable even when
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

4. **Scroll, then click Save.** The commit-summary field and the Save button
   sit below the fold. The button's label is `Save page` (verified in a
   live run) — match on it explicitly, not on `'Save'`; then the
   shared scroll-then-click dispatch (`sks-dev`
   `references/cdp-attach.md`).

5. **Verify by remote materialization, not DOM.** The wiki remote only
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
- **Editor id drift** — if `#gollum-editor-*` is gone, re-locate by label
  text ("Page title", the markdown textarea) the way the auto-close recipe
  finds its checkbox; never trust a hardcoded CSS path twice.
- **`curl` cannot create pages** — same class as the auto-close checkbox:
  server-rendered per session, no parseable API surface.

The connect-and-click machinery — finding the GitHub tab on the
debug port, connecting with `suppress_origin=True`, the
scroll-then-click dispatch, and the shared pitfalls — lives in
`sks-dev` `references/cdp-attach.md`; this recipe covers only
its surface-specific steps.
