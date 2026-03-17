# ADR 0008 — Wrapper packages must declare `"sideEffects": false`

**Date:** 2026-03-16
**Status:** Accepted

---

## Context

`boreal-react` and `boreal-vue` are ESM packages built with `"type": "module"` and `"module": "ESNext"`. Their output consists of named component exports — each a pure wrapper that passes `defineCustomElement` as a callback to the runtime factory (`createComponent` / `defineContainer`). No module-level side effects are present.

Neither package declared `"sideEffects"` in `package.json`. Without this field:

- **webpack 5** treats every module as potentially side-effectful and will not tree-shake unused component exports from the bundle.
- The Rollup/Vite bundlers (which power the consuming apps) perform ESM static analysis and tree-shake regardless, but `"sideEffects": false` is the authoritative, bundler-agnostic signal.

---

## Options Considered

### Option A — Rely on Rollup/Vite ESM analysis only

Works for Vite-based consumers, fails for webpack-based consumers. Rejected: the design system must support both.

### Option B — `"sideEffects": ["dist/css/**", "dist/scss/**"]`

Excludes CSS files from tree shaking (needed if consumers import CSS as bare side-effect imports). In practice, CSS is imported via explicit `./css/*` / `./scss/*` subpaths and is never imported as a bare module-level side effect in our patterns. Premature to add the exemption. Rejected.

### Option C — `"sideEffects": false` on both wrapper packages

Accurate for the current output shape. If CSS files are ever imported as side-effect imports in a consuming app, the field can be updated to exemption form. Accepted.

---

## Decision

Add `"sideEffects": false` to `boreal-react/package.json` and `boreal-vue/package.json`.

---

## Consequences

- **Enables webpack 5 tree shaking**: Consumers on Create React App, Next.js (webpack mode), or other webpack-based toolchains will now only bundle the components they import.
- **Correct for the current output**: All component proxy modules are pure factories with no module-level side effects.
- **`'use client'` directive**: The React output emits `'use client'` at the top of `components.js`. This is a string literal used by RSC-aware bundlers (Next.js App Router). Modern webpack 5 and Rollup do not treat it as a side effect — no exemption needed.
- **Future `sideEffects` updates**: If a future consumer does `import '@telesign/boreal-react/dist/css/index.css'` directly (instead of via the `./css/*` subpath export), the `sideEffects` field would need to be updated to `["dist/css/**", "dist/scss/**"]`. Track as a follow-up if CSS-as-side-effect import patterns emerge.
