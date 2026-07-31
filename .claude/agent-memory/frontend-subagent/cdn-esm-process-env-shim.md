---
name: cdn-esm-process-env-shim
description: Loading an npm ESM package raw via CDN (unpkg/esm.sh) in a bundler-free HTML page throws ReferenceError if the package's dist references process.env.NODE_ENV
metadata:
  type: project
---

`@tanstack/virtual-core`'s published ESM dist (`dist/esm/index.js`) contains a bare
`process.env.NODE_ENV !== "production"` reference inside the `Virtualizer` constructor
(used as a debug-key guard for `memo()`). This is a bundler artifact — Vite/webpack/etc.
normally replace `process.env.NODE_ENV` with a string literal at build time. When the
same file is imported directly via `<script type="module">` + a CDN URL (no bundler in
the loop, e.g. Stencil's static `www` dev server), `process` is `undefined` in the
browser and the constructor throws `ReferenceError: process is not defined`.

**Why:** discovered 2026-07-22 while building a temporary validation spike in
`packages/boreal-web-components/src/index.html` to test sticky `<thead>` +
virtualized `<tbody>` behavior for Task 7 of `ai-work/plans/EOA-15507-bds-table-v3.md`.
The spike needed the real `@tanstack/virtual-core@3.17.1` package (already a pinned
dependency) wired in vanilla JS outside the Stencil/Vite module graph, so it imported
from `https://unpkg.com/@tanstack/virtual-core@3.17.1/dist/esm/index.js` directly.

**How to apply:** whenever importing any npm ESM package raw via CDN into a page with
no bundler, add a classic (non-module) `<script>` before the `<script type="module">`
that shims `window.process = window.process || { env: { NODE_ENV: 'production' } };`.
Classic scripts execute synchronously in document order; module scripts are deferred
by default and always run after — so the shim is guaranteed to exist before the
imported module's top-level/constructor code runs. This is specific to
bundler-free static pages (like this repo's Stencil dev playground
`src/index.html`); it does not apply to `bds-table.tsx` itself, which goes through
Stencil's real build pipeline and never sees `process` undefined.
