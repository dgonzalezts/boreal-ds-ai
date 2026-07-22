---
name: stencil-dev-server-hashed-chunk-stale-cache
description: pnpm dev:components (stencil build --dev --watch --serve) can serve a stale content-hashed lazy chunk after incremental rebuilds; verifying via www/build/<tag>.entry.js on disk is misleading — restart the dev server and check the actual hashed p-*.js the browser fetched
metadata:
  type: project
---

When manually verifying a `bds-table.tsx` (or any component) change against a running `pnpm dev:components` dev server via Playwright, a stale bundle can keep being served even after the on-disk source and the readable-named `www/build/<tag>.entry.js` file both reflect the new code, and even across full-page `page.goto()` navigations (not just SPA hash changes).

**Why:** Stencil's dev server lazy-loads components via content-hashed chunk filenames (e.g. `p-BqJlOB6b.js`, regenerated per rebuild) — NOT the stable `www/build/bds-table.entry.js` name. That stable-named file is also written to disk but is not necessarily what the browser's `<script type="module">` loader actually dynamic-`import()`s. During one incremental watch rebuild, the merged/hashed chunk containing the changed component's code did not get regenerated, so the browser (even after full navigation) kept fetching an old-content hash chunk. Grepping the stable-named file for new code and finding a match is not proof the browser is running that code.

**How to apply:** When a manual browser verification shows behavior inconsistent with the source (e.g. a change appears to have no effect, or a `console.log`/`console.warn` you added never fires), don't trust `grep` against `www/build/<tag>.entry.js`. Instead:
1. Use `mcp__playwright__browser_network_requests` (`static: true`) to see the actual hashed `.js` URLs the browser fetched, and `fetch(url, {cache:'no-store'})` + `.text()` from `browser_evaluate` to confirm that specific served file's content.
2. If it's stale, kill the `stencil build --dev --watch --serve` process and restart `pnpm dev:components` fresh (may bind a new port if the old one didn't release immediately) — a clean rebuild reliably regenerates all hashed chunks in sync with source.

Also: same-hash-URL navigations (`page.goto()` to the same origin+path differing only by `#hash`) do not force a real document reload in Chromium — always navigate to a neutral URL (e.g. `about:blank`) or vary the path/query before returning, or state (including monkey-patched `console.warn`, pinned columns, etc.) silently persists across "navigations" and produces confusing results.

Related: [[stencil-worktree-missing-dist-dependency]] (a different dev-server/build environment gotcha in this same codebase).
