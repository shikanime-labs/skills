# CDP Attach

The shared attach procedure for driving a GitHub page through Chrome's
debug port — used by the UI-only GitHub recipes (auto-close checkbox in
`sks-repo`, wiki bootstrap in `sks-wiki`). Each recipe owns its
surface-specific steps (what to fill, what proves success); this file
owns the connect-and-click machinery they all repeat.

## Find a GitHub tab

The debug port lists targets; reuse a logged-in tab rather than opening
a new one:

```bash
curl -s http://localhost:9222/json/list
# pick the entry with "type": "page" whose "url" starts with https://github.com/
# note its "webSocketDebuggerUrl"
```

## Connect with Origin suppressed

Chrome 155+ rejects WebSocket handshakes carrying an `Origin` header
(403 "Rejected an incoming WebSocket connection"); `websocket-client`
sends one by default. `suppress_origin=True` is mandatory:

```python
import websocket

ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
```

## Scroll, then click

The target element usually sits below the fold; coordinates from
`getBoundingClientRect()` are viewport-relative and wrong until the
element is scrolled in. `scrollIntoView({block: 'center'})`, wait
~0.5s, re-read the rect, then dispatch both halves of the click at the
same viewport coords:

```python
ws: Input.dispatchMouseEvent type=mousePressed  x, y, button=left, clickCount=1
ws: Input.dispatchMouseEvent type=mouseReleased x, y, button=left, clickCount=1
```

## Pitfalls

- **403 on WS connect** — Origin header present; fix is
  `suppress_origin=True` (do NOT restart Chrome with
  `--remote-allow-origins=*`; that flag widens the debug port to any
  local process for the browser's lifetime).
- **Click misses** — element below the fold; `scrollIntoView` before
  reading coordinates, and re-read the rect AFTER the scroll.
- **Never drive the user's live browser** — synthetic input into the
  daily browser is forbidden without explicit per-task authorization;
  use a dedicated automation profile holding only the GitHub session.
- **One tab per run** — navigating a shared tab from two loops races
  page loads.
- **A page you did not open appears** — hard stop immediately.
