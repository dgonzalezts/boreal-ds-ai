---
name: stencil-build-stale-stencil-cache-false-tsc-error
description: pnpm --filter <pkg> build (stencil build) can report a false "Property does not exist" TS error for a field that is genuinely present on disk, caused by a stale packages/boreal-web-components/.stencil/.build cache — distinct from tsc -p directly, which is unaffected.
metadata:
  type: project
---

`stencil build` (via `pnpm --filter @telesign/boreal-web-components build`) reported:

```
TypeScript: .../bds-calendar-grid.tsx:93:10
Property '_pickerCellRefs' does not exist on type 'BdsCalendarGrid'.
```

at a line that referenced a private field declared two lines earlier in the same class. `tsc -p tsconfig.build.json --noEmit` run independently against the exact same file passed with zero errors, and `awk`/`grep` confirmed the field was present on disk at the reported line. The cause was a stale `packages/boreal-web-components/.stencil/.build` cache directory (observed non-empty, ~2000 entries, before the failing build). Deleting `.stencil`, `www`, and `dist` and rerunning `stencil build` fixed it immediately with no code change.

**Why:** `stencil build`'s internal TypeScript program appears to reuse a cached transpile/type-check artifact keyed loosely enough that it can miss a very recent edit to a class's own field list, even though a fresh top-level `tsc -p` invocation against the same files is always correct. This is a different failure mode from [[stencil-dev-server-hashed-chunk-stale-cache]] (dev server serving old JS) and [[stencil-turbo-build-cache-hit-false-positive]] (Turbo replaying an old log) — this one is Stencil's own build cache producing a spurious compiler diagnostic, not stale runtime output.

**How to apply:** If `pnpm --filter <pkg> build` (or `stencil build`) reports a TS error referencing a symbol that a direct `tsc -p tsconfig.build.json --noEmit` run does NOT report for the same file, do not trust the `stencil build` error — `rm -rf packages/boreal-web-components/{.stencil,www,dist}` and rerun before concluding there's a real type error. Treat a standalone `tsc -p` pass as the source of truth over `stencil build`'s own diagnostics when the two disagree.
