---
name: tsc-relative-path-picks-workspace-root-tsconfig
description: pnpm exec tsc -p tsconfig.json from inside a package dir can silently resolve the workspace-ROOT tsconfig instead, producing thousands of bogus errors unrelated to any real change
metadata:
  type: project
---

Running `pnpm exec tsc --noEmit -p tsconfig.json` from inside `packages/boreal-web-components` (even with `workdir` correctly set to that directory) can silently resolve and use the **workspace-root** `tsconfig.json` instead of the package-local one — confirmed via `tsc -p tsconfig.json --showConfig`, which printed the root config's `module: commonjs`, no `jsx` option, and a `files` array spanning `apps/boreal-docs/**` and other unrelated packages. This produces thousands of nonsensical errors (missing `--jsx` flag, `Cannot find module '@/mixins'`, jest-global-related `TS2708`/`TS2304` in `src/utils/testing/mocks/*`) that look alarming but are **not real** and **not related to any code change** — confirmed by running the identical command against a `git stash`ed (pre-change) tree and getting the same ~4700-error count.

**Fix:** pass an **absolute path** to `-p`, e.g. `tsc --noEmit -p "$(pwd)/tsconfig.json"` (or `-p /full/path/to/package/tsconfig.json`). This reliably resolves the package-local config and reduces the (real) error count to the project's known baseline of exactly 5 pre-existing errors: 1 in `bds-dialog.behavior.spec.ts` (`MouseEvent` shape mismatch) and 4 in `bds-tooltip-events.spec.ts` (`Coords`/`centerOffset` shape mismatch) — both under `src/components/overlays/`, both unrelated to `bds-date-picker` or any other in-scope component work.

**How to apply:** whenever a plan's verification step calls for `tsc --noEmit` "confirm only the same N known pre-existing unrelated errors," always pass an absolute `-p` path. If a relative `-p tsconfig.json` from the package directory unexpectedly returns thousands of errors mentioning files far outside your `Files:` scope (e.g. `apps/boreal-docs/**`), that's this exact symptom — re-run with the absolute path before concluding anything is broken or that your change introduced new errors.

**Root cause (not fully diagnosed):** unclear why `-p tsconfig.json` (relative) doesn't resolve against the CLI's cwd in this specific pnpm/turbo workspace layout — possibly an artifact of how `pnpm exec` spawns the process or an ambient `TSC_COMPILE_ON_SAVE`/tsconfig-lookup quirk. Treat as an environment gotcha to route around (absolute path), not something to fix.
