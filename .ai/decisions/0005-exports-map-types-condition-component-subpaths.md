# ADR 0005 — `boreal-web-components` exports map: add `.js` suffix and `types` condition to component subpaths

**Date:** 2026-03-16
**Status:** Accepted

---

## Context

`boreal-web-components/package.json` exposed individual custom element files via a subpath export pattern:

```json
"./components/*": {
  "import": "./components-build/*"
}
```

When `boreal-react` and `boreal-vue` import individual components using entries like:

```ts
import { BdsButton } from "@telesign/boreal-web-components/components/bds-button.js";
```

...TypeScript with `moduleResolution: bundler` **could not resolve the declaration file** for the subpath because:

1. The `*` wildcard matched `bds-button.js` but the resolution target `./components-build/bds-button.js` required the file to exist — and due to the missing extension in the glob, the TypeScript resolver did not find a `.d.ts` alongside it.
2. There was no `types` condition in the map, so `tsc` had no declaration resolution path at all.

This manifested as the build error:

```
Cannot find module '@telesign/boreal-web-components/components/bds-button.js'
```

And cascaded into `BdsButtonCustomEvent` and related types being unresolvable in the generated `components.d.ts`.

---

## Options Considered

### Option A — Use `typesVersions` mapping instead of a `types` condition

`typesVersions` is a legacy TypeScript mechanism. Rejected: `exports` map `types` conditions work natively with `moduleResolution: bundler` and are the modern approach.

### Option B — Explicit `.js` extension in the glob key + `types` condition

Change the map to:

```json
"./components/*.js": {
  "import": "./components-build/*.js",
  "types": "./components-build/*.d.ts"
}
```

This makes both the runtime and declaration resolution explicit. Accepted.

---

## Decision

Update `boreal-web-components/package.json` exports:

```json
"./components/*.js": {
  "import": "./components-build/*.js",
  "types": "./components-build/*.d.ts"
}
```

The `.js` suffix in the key is correct: consumers already import with the explicit `.js` extension (required by ESM strict mode), and the glob key must match the full specifier.

---

## Consequences

- **Fixed**: TypeScript `moduleResolution: bundler` consumers can now resolve `.d.ts` for all component subpath imports.
- **Fixed**: The cascading `BdsButtonCustomEvent` type error in generated React proxies is resolved.
- **Note**: This change requires the `components-build/` directory to emit both `.js` and `.d.ts` files (which Stencil already does via its `dist-custom-elements` output target with `generateTypeDeclarations: true`).
- **Breaking (theoretical)**: If any consumer imported without `.js` extension under the old `*` wildcard, that pattern now fails. In practice, ESM strict imports always use `.js`.
