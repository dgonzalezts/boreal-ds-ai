# ADR 0006 — Stencil interface files must use named exports, not default exports

**Date:** 2026-03-16
**Status:** Accepted

---

## Context

`bds-button/types/IButton.ts` defined the component's prop interface as a **default export**:

```ts
// Before
export default interface IButton { ... }
```

The component imported it as:

```ts
import IButton from "./types/IButton";
```

This compiled without errors in the component itself. However, Stencil's declaration generator (`dist-custom-elements` output target) processes component prop types to build the global `Components` namespace in `components.d.ts`. When it encountered `IButton` in the props, it attempted to import it from the source file — but **Stencil's codegen only tracks named exports** when building the import list for `components.d.ts`.

The generated file referenced `IButton` without importing it, producing:

```
Cannot find name 'IButton'
```

This caused the entire `Components.BdsButton` interface to fail to parse, eliminating `BdsButtonCustomEvent` from scope — a cascading type failure affecting every consumer of the React and Vue wrappers.

---

## Options Considered

### Option A — Re-export the default as a named export in a separate barrel

```ts
export { default as IButton } from "./types/IButton";
```

Rejected: adds a layer of indirection for no benefit, and the root issue remains.

### Option B — Convert to a named export throughout

```ts
// IButton.ts
export interface IButton { ... }

// bds-button.tsx
import { IButton } from './types/IButton';
```

Accepted: consistent with TypeScript and Stencil best practices, removes the ambiguity.

---

## Decision

**All interface and type files within Stencil components must use named exports.** Default exports are prohibited for interface definition files used as component prop types.

Applied to `IButton`:

```ts
// types/IButton.ts
export interface IButton { ... }

// bds-button.tsx
import { IButton } from './types/IButton';
```

---

## Consequences

- **Fixed**: Stencil's declaration generator correctly includes the named import in `components.d.ts`.
- **Generalised rule**: Every `types/I*.ts` file in `boreal-web-components/src/components/` must be audited for default exports if similar type failures appear on other components.
- **Easier to grep**: Named exports are statically analysable; default exports are not.
- **ESLint enforcement added**: A `no-restricted-syntax` override targeting `src/**/types/*.ts` is active in `eslint.config.ts`. Any `ExportDefaultDeclaration` in a component type file is now a lint error with a message referencing this ADR.
