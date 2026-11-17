# Disabling auto-close via CDP

The full procedure for toggling **Auto-close issues with merged linked pull
requests** (Settings → General → Issues) from the shell. No REST, GraphQL, or
CLI field exists — Repository introspection yields only `has_issues`; the
checkbox (input id `issues_auto_close`) is the sole read/write path. Works for
one repo at bootstrap or a backfill sweep over many.

## Prerequisites

- The operator's Chrome runs with `--remote-debugging-port=9222` and holds an
  authenticated GitHub session (any tab on `github.com`).
- `websocket-client` importable (`python3 -c "import websocket"`); stdlib
  `urllib.request` does the REST half.

## Procedure

1. **Attach** per `sks-dev` `references/cdp-attach.md`: find the
   logged-in GitHub tab on the debug port, connect with
   `suppress_origin=True`.

2. **Navigate to the settings page** over the same connection —
   `Page.enable`, `Page.navigate` to `https://github.com/<org>/<repo>/settings`,
   then wait ~4s for render (GitHub settings pages are server-delivered but
   slow to settle).

3. **Locate the checkbox** by label text, not CSS path — the settings DOM is
   unstable, the label is not. Evaluate in the page:

   ```js
   (() => {
     const wanted = /auto-close issues with merged linked pull requests/i;
     for (const lab of document.querySelectorAll('label')) {
       if (!wanted.test((lab.textContent || '').trim())) continue;
       const input = lab.querySelector('input[type=checkbox]') ||
         document.getElementById(lab.getAttribute('for') || '');
       if (input) return {found: true, checked: input.checked, id: input.id};
     }
     return {found: false};
   })()
   ```

4. **Scroll, then click.** The checkbox sits far down the page; coordinates
   from `getBoundingClientRect()` are viewport-relative and wrong until the
   element is scrolled in. `input.scrollIntoView({block: 'center'})`, then
   the shared scroll-then-click dispatch (`sks-dev`
   `references/cdp-attach.md`) — the click is what saves the setting (no
   submit button).

5. **Verify on a fresh navigation.** Never trust the post-click DOM —
   re-navigate the tab to the settings page and re-run step 4; `checked` must
   read `false`. For a sweep, run this verify pass as a second full loop over
   the repo list, asserting every repo, and fail loudly on any miss.

## Backfill sweep shape

Loop over the repo list: per repo, navigate → locate → scroll+click if
`checked` is true (skip if already off) → sleep ~2.5s → re-read. Record
before/after per repo to a JSONL as you go, then the fresh-nav verify loop.
At #301's scale (23 repos) the whole pass is minutes.

## Pitfalls

- **Verified from a stale DOM** — the post-click DOM can lag the saved state;
  only a fresh navigation proves the toggle stuck.
- **`curl` cannot read the state** — the checkbox renders server-side per
  session; without a browser context there is nothing to parse.

The connect-and-click machinery — finding the GitHub tab on the
debug port, connecting with `suppress_origin=True`, the
scroll-then-click dispatch, and the shared pitfalls — lives in
`sks-dev` `references/cdp-attach.md`; this recipe covers only
its surface-specific steps.
