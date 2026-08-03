# `pnpm dev:components`: A Long-Running Watch Process Can Serve a Stale, Orphaned Lazy Chunk

## The Symptom

`pnpm dev:components` runs `stencil build --dev --watch --serve` directly against `packages/boreal-web-components/src/index.html` (no Storybook layer). After many successive incremental rebuilds over a long-running session (dozens of edits across several hours), the dev server can start serving a **stale, content-hashed lazy-loaded chunk** (e.g. `p-cdabecdf.entry.js`) for a component, even though:

- The component's **friendly-named** build artifact (e.g. `bds-button.entry.js`) is correctly rebuilt and up to date on every edit.
- `curl`/`fetch` checks against that friendly-named file show the fix is present.
- The dev server process is alive, `--watch` is running, and the server's HTTP response headers correctly say `cache-control: no-cache, no-store, must-revalidate, max-age=0` (so it is not a browser HTTP-caching problem either).
- Restarting the dev server process (plain `kill` + `pnpm dev:components` again) does **not** fix it — the stale hashed chunk persists across restarts, because it survives in whatever `www/build/` output or `.stencil/` build cache the restarted process picks back up.

The browser's `<script type="module">` entry actually resolves to the stale hashed filename, not the friendly-named one — so checking the friendly-named file (an easy thing to reach for, since it is stable and easy to `curl`) gives false confidence that the fix is live. Confirm what the browser is *actually* loading via `playwright-cli -s=<name> requests` (the Playwright MCP server is disabled; drive the browser via the `playwright-cli` Bash CLI, or the Network tab) before trusting any content check against a differently-named file.

## Repro Signature

- A code fix is verified correct via `grep`/`cat` against the on-disk source and the "obvious" build output file, and the full unit test suite passes.
- The live browser (including a freshly-navigated Playwright page, not just a stale tab) still exhibits the pre-fix behavior, repeatedly, across multiple reload attempts.
- `playwright-cli -s=<name> requests` (filtered to the component name) shows the actual `<script>`/dynamic-import request resolves to a **different filename** than the one being checked (a `p-[hash].entry.js` chunk, not the component's own `.entry.js`).

## Fix

A plain server restart is not sufficient once this happens. Clear both Stencil caches and do a full rebuild:

```bash
rm -rf packages/boreal-web-components/.stencil packages/boreal-web-components/www
pnpm dev:components
```

After a clean rebuild, lazy chunks are regenerated (in this codebase's config, without the `p-[hash]` prefix at all — directly as `<component-name>.entry.js`), and the browser correctly loads the current code on the next navigation.

## How This Differs From the Existing `dev:docs` Staleness Note

`feedback_dev_server_restart.md` (personal memory, not this file) documents that the **Storybook** dev server (`pnpm dev:docs`) does not hot-reload Stencil component changes and needs a manual restart — but a plain restart *is* sufficient there. This is a different server (`dev:components`, no Storybook/Vite layer), a different root cause (an internal Stencil watch-build chunk-naming staleness, not a "no hot-reload" gap), and a different, stronger fix (clear `.stencil/`/`www/`, not just restart). Do not assume the `dev:docs` guidance ("just restart") is sufficient here if a `dev:components` fix appears not to be taking effect after a normal restart — escalate to the full cache-clear before concluding the code itself is still broken.

## When To Reach For This

Only after ruling out the simpler explanations first, in order: (1) confirm the source file actually has the fix, (2) confirm the *actually-loaded* network resource (not a same-purpose but differently-named file) contains the fix, (3) try a plain dev-server restart. Only escalate to a full `.stencil`/`www` clear if the server has been running `--watch` for a long session with many prior rebuilds and a plain restart didn't resolve it — this is what happened in the originating session (dozens of rebuilds across several hours before the stale chunk appeared).

Source: bds-table formatter-cache flash-bug session, 2026-07-27. Cost several rounds of "the fix still doesn't work" investigation before being correctly diagnosed and ruled out as the cause of a real, separate code bug (see `stencil-non-shadow-slot-relocation-timing.md`).
