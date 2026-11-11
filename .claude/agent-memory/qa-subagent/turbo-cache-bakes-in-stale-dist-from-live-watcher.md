---
name: turbo-cache-bakes-in-stale-dist-from-live-watcher
description: A pack/validate run can ship pre-fix component code while exiting 0 — a third-party live `stencil --watch` build (whose in-memory program predates the fix) can write stale bytes into `packages/boreal-web-components/dist`, and Turbo then caches those bytes under the current-source hash, so later `validate:pack`/`dev:pack` runs replay them from cache
metadata:
  type: project
---

Hit during EOA-19597 Task 43 re-verification (2026-10-26, Chrome). `pnpm run dev:pack:react` finished with
no error, the browser loaded the testapp, and `bds-search-bar.applyQuery` behaved like the **unfixed**
code. The installed pack really did contain pre-fix output:

```
node_modules/.pnpm/@pxglobal+boreal-react@file+…/node_modules/@pxglobal/boreal-web-components/
  dist/collection/components/forms/bds-search-bar/bds-search-bar.js   →  this.value = value;   (no emit)
```

while the worktree source had the equality guard. `node_modules/.vite/deps/@pxglobal_boreal-react.js`
(the bundle the browser actually executes) matched the stale pack, so the run was silently a pre-fix run.

Confirmed mechanism, in order:

1. A third-party `stencil build --dev --watch --serve` process had been running for hours, started
   **before** the fix landed. On a rebuild it re-emits its (older) in-memory program into the shared
   `dist/`, `components-build/` and `www/` targets. See [[concurrent-dev-pack-builds-race-condition]] —
   this is the "third-party live watcher" branch of it, and it poisons **output content**, not just causing
   TS corruption.
2. `turbo run build --filter=…boreal-web-components` then cached that stale `dist/**` under the hash of the
   **current** source (`--dry=json` showed `cache HIT` for hash `eccf4706303098ae` both before and after the
   fix was present). Turbo hashes inputs but trusts outputs, so the corruption is now sticky: every later
   `dev:pack:*` / `validate:pack:*` restores pre-fix bytes with a green exit code, and `validate:pack`
   "passing" proves nothing about the changed component.

Detection / correct protocol:

- Before any browser assertion about a changed component, grep the artifact that will actually run for a
  fix-specific marker: `node_modules/.vite/deps/@pxglobal_boreal-<fw>.js` (what the browser executes), or
  the installed pack's `dist/collection/.../<component>.js`. Do **not** trust `packages/*/dist` — a
  watcher can rewrite it seconds later (mtime check + re-grep).
- After `validate:pack`, grep the app's built bundle (`examples/*/dist/assets/index-*.js`) for the marker;
  that is the only proof the validated artifact contains the fix.
- Recovery: bust the cache — `pnpm exec turbo run build --filter=@pxglobal/boreal-web-components --force`
  (or a direct `pnpm --filter … build`, which bypasses Turbo), re-grep `dist`, then re-run
  `validate:pack:*`. Do not kill another session's watcher.
- A v-model harness can also mask the whole thing: with the fix present Vue emits a 4th (commit)
  `valueChange`, with the fix absent it emits 3 — so a "React 3 / Vue 3" event-count match is a smoking gun
  that the served bundle predates the fix.
