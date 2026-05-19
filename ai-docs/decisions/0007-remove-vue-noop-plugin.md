# ADR 0007 — Remove no-op `plugin.ts` from `boreal-vue`

**Date:** 2026-03-16
**Status:** Accepted

---

## Context

`boreal-vue/lib/plugin.ts` exported a `ComponentLibrary` Vue plugin intended to support the `app.use(ComponentLibrary)` global registration pattern:

```ts
export const ComponentLibrary: Plugin = {
  install() {},
};
```

The `install()` method was empty. The intent was presumably to register all custom elements globally so consumers could write `<BdsButton>` without explicit imports.

However, the vue output target was configured with:

```ts
vuOutputTarget({
  includeImportCustomElements: true,
  includePolyfills: false,
  includeDefineCustomElements: false,
});
```

With `includeImportCustomElements: true`, the generated proxy files already call `defineCustomElement` per-component at import time (via the `@telesign/boreal-web-components/components/` subpaths). Each component self-registers its custom element when imported. There is no global registration step that a plugin could perform.

The plugin was never implemented, was not tested, was misleading to consumers, and was re-exported from `lib/index.ts` as part of the public API.

---

## Options Considered

### Option A — Implement the plugin with `defineCustomElement` calls for all components

Would require the plugin to enumerate every component — a brittle maintenance burden as new components are added. Also contradicts the tree-shaking model: registering all components globally defeats the purpose of `includeImportCustomElements: true`. Rejected.

### Option B — Remove the plugin entirely

No registration logic is needed; each proxy component handles its own element registration. Accepted.

---

## Decision

Delete `boreal-vue/lib/plugin.ts` and remove its re-export from `boreal-vue/lib/index.ts`.

**Before:**

```ts
// lib/index.ts
export * from "./components";
export * from "./plugin";
```

**After:**

```ts
// lib/index.ts
export * from "./components";
```

---

## Consequences

- **Removed false affordance**: Consumers can no longer do `app.use(ComponentLibrary)` — but it never worked anyway.
- **Cleaner API surface**: The public API is solely the named component exports from `./components`.
- **Breaking change (theoretical)**: Any consumer importing `ComponentLibrary` from `@telesign/boreal-vue` will get a build error. Given the plugin was a no-op, such consumers gained nothing from it and their removal is safe.
- **Future global registration**: If a genuine global registration pattern is needed in future, it should be implemented by iterating the full component list and calling `defineCustomElement` on each. That belongs in a separate ADR.
