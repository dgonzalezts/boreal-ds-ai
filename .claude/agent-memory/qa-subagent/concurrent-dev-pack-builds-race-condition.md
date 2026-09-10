---
name: concurrent-dev-pack-builds-race-condition
description: Running dev:pack:react and dev:pack:vue in parallel corrupts the shared boreal-web-components dist/ output, producing spurious "not a module" TS build failures
metadata:
  type: project
---

Launching `pnpm run dev:pack:react` and `pnpm run dev:pack:vue` at the same time (e.g. both backgrounded in one turn) causes both to trigger `turbo run build --filter=...@telesign/boreal-web-components` concurrently. Both write to the same `dist/`, `components-build/`, and `dist/types/components.d.ts` output at once, corrupting it mid-write.

Symptom observed: `boreal-react`'s `tsc` build failed with dozens of `TS2306: File '.../components-build/bds-*.d.ts' is not a module` errors plus `TS2552: Cannot find name 'HTMLBdsTreeMenuItemElement'` — even though each individual `.d.ts` file, inspected afterward, was well-formed. Re-running `dev:pack:react` alone (with no concurrent `boreal-web-components` build in flight) succeeded immediately with the same source.

**Fix:** never run `dev:pack:react` and `dev:pack:vue` concurrently from a single dispatch — run them sequentially, or start the second only after confirming the first's `boreal-web-components:build` step has completed (grep the log for `build finished` / `postbuild:` lines).

Also relevant: a third-party's already-running `stencil build --dev --watch --serve` process (e.g. another teammate's raw web-components playground session on port 3333) rebuilds the *same* multi-target `dist/`/`www/`/`dist-custom-elements` output on every file change (confirmed via `stencil.config.ts`'s single `outputTargets` array covering all four targets in one compile). That watch process is a second source of the same race even when only one `dev:pack:*` command is run — if a QA dispatch's own build coincides with a filesystem change picked up by someone else's live watch process, expect the same corruption. There's no clean mitigation for this shared-process case other than retrying the failed build once the watcher's own rebuild has settled.
