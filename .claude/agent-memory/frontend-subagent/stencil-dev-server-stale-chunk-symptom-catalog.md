---
name: stencil-dev-server-stale-chunk-symptom-catalog
description: Symptom catalog for a stale/long-running `stencil build --dev --watch --serve` process serving outdated lazy-loaded component chunks despite fresh source and confirmed-fresh disk builds — extends stencil-dev-server-hashed-chunk-stale-cache.md
metadata:
  type: project
---

Extends [[stencil-dev-server-hashed-chunk-stale-cache]] with concrete symptoms observed after a dev server had been running (via `--watch`) for over an hour across many incremental edits (EOA-17138 Task 19o).

**Symptoms that indicate a stale served chunk despite a correct rebuilt file on disk:**
- `grep` against `www/build/<component>.entry.js` shows your latest edits present, but browser-observed behavior matches an *older* version of the same method (e.g. only the first few lines of a multi-step function appear to execute).
- Debug instrumentation added inside a method (writes to `window.__foo`, sets a DOM attribute, appends a `<style>` tag) never appears in the live page — even though a `fetch('/build/<file>.js', {cache:'no-store'})` from within the SAME page confirms the served response text contains the debug tokens.
- `customElements.get('tag-name').toString()` — the ACTUAL executing class source — does not match the file on disk when diffed carefully; this is the definitive proof, more reliable than fetch (fetch can still hit a route that ends up serving something else than what got hot-loaded into the running JS realm).
- Behavior is inconsistent/flaky across repeated identical test runs in ways that don't correspond to any real race condition in the source.

**Why fetch can lie but customElements.get(...).toString() doesn't:** a `fetch()` call goes through the SAME dev-server HTTP layer that may already be confused about which chunk is current; the live `customElements` registry reflects whatever module actually got evaluated into the page's JS realm, which is the one thing that must match observed runtime behavior.

**Fix:** kill the stencil dev server process (`pkill -f "stencil build --dev --watch --serve"` and any `server-worker-thread.js`/`worker.js` children), `rm -rf www/build`, and restart fresh (`stencil build --dev --watch --serve --port <N>` via `with-node.sh`). A page navigation (even a hard one) is NOT sufficient to fix this — the staleness lives in the dev server process itself, not the browser.

**Cost incurred:** this exact failure mode cost roughly 45 minutes of debugging on Task 19o before being identified — several rounds of "fix should work, still fails identically" were actually testing against a stale chunk the whole time. When a fix that is verified-correct via a from-scratch manual DOM diagnostic (bypassing the component entirely) still fails identically when wired into the real component, and especially when debug instrumentation placed at the TOP of a method never shows any effect at all, suspect a stale dev-server chunk FIRST, before re-deriving new theories about the actual bug.
