# ADR 0004 — `boreal-react` dist structure: flat declarations, no raw sources in files

**Date:** 2026-03-16
**Status:** Accepted

---

## Context

`boreal-react` is the React wrapper around the Stencil web components. Its `lib/` directory holds the TypeScript source input for `tsc` — including auto-generated Stencil proxy files that are written to `lib/components/` during `stencil build`. These files are gitignored; they are not hand-authored artefacts.

After comparing `boreal-react` against `boreal-vue` (the reference), three structural inconsistencies were found:

1. **`"files": ["dist", "./lib/*"]`** — the `lib/` wildcard caused raw TypeScript sources to be included in the published npm tarball. This is wrong: consumers receive `.ts` files that their bundlers are not configured to compile.

2. **`"declarationDir": "./dist/types"`** in `tsconfig.json** — emitting `.d.ts`files into a separate`dist/types/`subdirectory, inconsistent with`boreal-vue`which co-locates declarations alongside`.js`files. The`types`and`exports.types`paths in`package.json` pointed to this non-standard location.

3. **Stale `types` and `exports.types` paths** in `package.json` pointed to `dist/types/index.d.ts` instead of `dist/index.d.ts`.

---

## Options Considered

### Option A — Keep `dist/types/` structure, update docs

Retain the split output; document the non-standard layout. Rejected: adds cognitive overhead, diverges from the Vue package, and provides no benefit.

### Option B — Align with `boreal-vue` flat structure

Remove `declarationDir`, co-locate `.d.ts` files with `.js` files, update `types` paths to match. Accepted.

---

## Decision

Apply the following three changes to `boreal-react`:

1. **`package.json` — `files`**: `["dist", "./lib/*"]` → `["dist"]`
2. **`tsconfig.json`** — remove `"declarationDir": "./dist/types"`
3. **`package.json` — `types` and `exports["."].types`**: `dist/types/index.d.ts` → `dist/index.d.ts`

The resulting `dist/` output mirrors `boreal-vue`:

```
dist/
  components/
    components.js
    components.d.ts
  index.js
  index.d.ts
  css/
  scss/
```

---

## Consequences

- **Easier**: Both wrapper packages have an identical, predictable dist shape.
- **Safer**: The npm tarball no longer ships raw TypeScript sources to consumers.
- **Simpler**: One fewer tsconfig option to maintain.
- **Follow-up**: Any consumer who was importing from `@telesign/boreal-react/dist/types/...` must update their import paths (unlikely, as that path was never documented as public API).
