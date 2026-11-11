# Real-browser verification without Playwright: Chrome `--dump-dom`

When Playwright is unavailable (not installed in this repo) and `qa-subagent` is not in play, a
self-driving page plus headless Chrome gives real-engine evidence for DOM/focus/selection claims.

## Recipe

1. Serve the built bundle: symlink `www/build` and `www/css` into a temp dir and run
   `python3 -m http.server <port>` there. `file://` cannot load the ESM loader (CORS).
2. Load the loader the build generated — read the current hash out of `www/build/../index.html`
   (`<script type="module" src="/build/p-XXXX.js" data-stencil data-resources-url="/build/"
   data-stencil-namespace="boreal-web-components">`). Do not hard-code a hash across builds; the
   `stencil-dev-server-stale-lazy-chunk` hazard applies.
3. The page drives the interaction itself and appends `key: JSON` lines into a `<pre id="out">`.
4. Run `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --headless=new --disable-gpu
   --no-sandbox --virtual-time-budget=40000 --dump-dom <url>` and regex the `<pre>` out of the dump.
5. Grep the built artifact for a marker from your edit before trusting the run (staleness guard).

## Gotchas (measured)

- **`requestAnimationFrame` is heavily throttled in headless** (`CVDisplayLinkCreateWithCGDisplay
  failed`, ~5 frames in a 60 s budget). A `waitFor`/`settle` helper must `Promise.race` rAF against a
  short `setTimeout`, otherwise the harness hangs after the first `await`.
- Consequence: **synchronous assertions are reliable; render-dependent ones need a poll**. A render
  can be proven to have happened by polling a child prop (e.g. `bds-text-field.value`) rather than by
  counting frames.
- `document.execCommand('insertText', false, 'z')` is a faithful "user typed a key" proxy — it
  respects the input's current selection, so it distinguishes *replaced* from *appended* from *lost*.
- `item.click()`, a synthetic `PointerEvent('pointerdown')` on the item, `input.blur()` and a
  keyboard `keydown` on the item reproduce the component pick flows end to end (the item's own click
  handler is what emits the selection event).
- `--dump-dom` prints the DOM at budget expiry, so log progressively; there is no console capture
  unless `--enable-logging=stderr` is added (`INFO:CONSOLE` lines).
