# Code Review — bds-badge

| Field         | Value                                      |
| ------------- | ------------------------------------------ |
| **Date**      | 2026-04-22                                 |
| **Commit**    | `ab59ed2`                                  |
| **Branch**    | `feature/EOA-12033-bds-badge-Test-and-Doc` |
| **Package**   | `packages/boreal-web-components`           |
| **Component** | `bds-badge`                                |

---

## Static Analysis Summary

Tool: `code_quality_checker.py` on `packages/boreal-web-components/src/components/feedback/bds-badge/`

```
bds-badge.tsx:4  ⚠ [import-order] Import order violation
bds-badge.tsx:5  ⚠ [import-order] Import order violation
bds-badge.tsx:52 ⚠ [getter-get-prefix] Redundant `get` prefix on getter accessor

Summary: 0 error(s), 3 warning(s)
```

---

## Review Checklist

### 0. Pre-Review Setup

- [x] **Scope clarity**: Branch name encodes ticket (`EOA-12033`) and scope (`bds-badge-Test-and-Doc`).
- [x] **Branch hygiene**: Feature branch from `release/current`.
- [x] **Compatibility intent**: Additive change (new component with tests and docs).

---

### 1. Universal

#### Code Quality and Architecture

- [x] **Single responsibility**: Component is focused — status badge with variant and disabled state only.
- [x] **Type safety**: No `any` usage. All props explicitly typed via `IBadge` interface. `BadgeVariant` union type derived from `BADGE_VARIANT` const object.
- [x] **Edge cases**: Invalid `variant` values handled via `validatePropValue`; falls back to `'default'` with a `console.warn`.
- [x] **Security**: No user-supplied content is rendered as HTML; only slot projection.
- [x] **Performance**: No re-renders, no heavy work. Getter is evaluated at render time only.

#### Testing and Verification

- [x] **Test coverage**: Four spec files — basics, variants, a11y, slots. All public API surface covered.
- [x] **Regression protection**: Tests are focused and independent; no existing component affected.
- [x] **Async correctness**: All tests use `newSpecPage` with `html:` initialisation (sync path). No post-render prop mutations that would require `waitForChanges()`.

#### Documentation and Developer Experience

- [x] **Storybook stories**: Complete five-section structure; `satisfies BorealStoryMeta`; all five variants + disabled + icon story present.
- [ ] **MDX examples**: Only vanilla JS example provided. **React and Vue usage examples are absent.** Required sections per docs guidelines.
- [x] **Consistent naming**: Props, events, slots follow Boreal DS conventions.

#### Build and Release

- [x] **Export integrity**: No new export map changes required. Component is under the existing `feedback/` namespace.

---

### 2. Package-Specific — `boreal-web-components`

#### Import Order and Barrel Hygiene

- [ ] **Import order** ❌ `bds-badge.tsx` lines 2–3 are local/relative imports (`./types/IBadge`, `./types/enum`) placed **before** the internal alias imports on lines 4–5 (`@/utils`, `@/types`). Correct order: `@stencil/core` → `@/utils` → `@/types` → local.
  - **Standard**: Framework → `@/services` → `@/mixins` → `@/utils` → local/relative.
  - **Antipattern**: Wrong import order hides coupling and violates the layer abstraction rule.
  - **Fix**:
    ```ts
    import { Component, Host, h, Prop, Element, Watch } from "@stencil/core";
    import { validatePropValue } from "@/utils";
    import { StyleModifiers } from "@/types";
    import type { IBadge } from "./types/IBadge";
    import { BADGE_VARIANT } from "./types/enum";
    ```

- [x] **Named barrel re-exports**: No barrel files introduced.
- [x] **No cross-component barrel imports**: Only `@/utils` and `@/types` used.

#### Component and Prop Discipline

- [x] **Props are readonly + documented**: Both `@Prop()` declarations have `readonly` and adjacent JSDoc blocks.
- [x] **Prop validation pattern**: `validatePropValue` + `componentWillLoad()` + `@Watch('variant')` is correctly applied. Single `@Watch` is appropriate here since only `variant` is an enum-like prop.
- [x] **Mutable props**: `disabled` is `readonly`. Correct — badge is not FACE so no `formDisabledCallback` concern.
- [x] **No class-level `@internal`**: Class JSDoc is clean.
- [x] **Interface file naming**: `IBadge.ts` — ✅ No `Bds` prefix.
- [ ] **Getter accessor naming** ❌ `get getBadgeClasses()` carries a redundant `get` prefix. The `get` keyword already communicates accessor semantics. Rename to `get badgeClasses()`.
  - **Standard**: Getter accessors must not carry a `get` prefix.
  - **Antipattern**: `get getPlacement()` — redundant verb; name should describe the returned value.
  - **Fix**: `private get badgeClasses(): StyleModifiers { ... }` and update the `render()` reference.

- [ ] **JSDoc on private methods** ⚠️ (minor) `checkPropValues()`, `componentWillLoad()`, and `getBadgeClasses` all carry JSDoc blocks. The Boreal DS convention is: "Do not add JSDoc to internal helpers, private methods, or test utilities." These blocks are harmless but violate the convention.

#### DOM and Accessibility

- [x] **ARIA attribute casing**: ARIA attributes set via JSX attributes (`role`, `aria-live`, `aria-label`, `aria-disabled`) — no `setAttribute` calls, no casing issue.
- [x] **`aria-label` coverage**: `aria-label={`status ${this.variant}`}` provides variant-based accessible name for all states. Tested in `bds-badge.a11y.spec.tsx`.

#### Events

- [x] **No events declared**: Badge is a display-only component. No events are expected.

#### FACE

- N/A — not a form-associated component.

#### Rendering and Testing

- [x] **Async render assertions**: No post-mutation DOM reads; all tests initialise via `html:` attribute. No `waitForChanges()` gaps detected.
- [x] **Light DOM assumption**: No shadow DOM used. Slots rendered via light DOM.

#### SCSS

- [x] **Token usage**: All values use `$boreal-*` SCSS variables. No hard-coded colours, spacing, or radii.
- [ ] **Redundant CSS on `display: contents`** ⚠️ In the `badge-variant` mixin, the `[slot='icon']` selector applies `align-items: center` and `justify-content: center` alongside `display: contents`. These flex properties have **no effect** on an element with `display: contents` — the element's box is removed from the formatting context, so it cannot be a flex or grid container for alignment purposes. Remove the two redundant declarations.
  ```scss
  > [slot="icon"] {
    display: contents;
    /* remove: align-items: center; */
    /* remove: justify-content: center; */
    color: $accent;
  }
  ```

---

## Memory-Guided Review

### Enum-like prop validation pattern (`feedback_prop_validation_pattern.md`)

`variant` is validated with `validatePropValue + componentWillLoad() + @Watch('variant')`. Single watch is correct; stacking is only needed when multiple enum props require validation (e.g. button with `variant` and `size`). **No issues found.**

### FACE / `@AttachInternals()` (`stencil-face-attach-internals.md`)

`bds-badge` is not a form-associated component — no `formAssociated: true`, no `@AttachInternals()`. **Not applicable.**

### Stencil prop patterns — `disabled` mirror (`stencil-prop-patterns.md`)

`disabled` is a `readonly @Prop()` driving a CSS class. No `mutable: true` and no FACE lifecycle involved. The `@State()` mirror is only required for FACE components; this is correct as-is. **No issues found.**

### Shadow DOM (`project_no_shadow_dom.md`)

No `shadow: true` in the `@Component` decorator. Component uses light DOM. **No issues found.**

### Event naming (`feedback_event_naming.md`)

No `@Event()` declarations. **Not applicable.**

### Accessor naming conventions (`component-accessor-naming-conventions.md`)

`get getBadgeClasses()` violates the "no `get` prefix on getter accessors" rule. Already flagged above as a ❌ finding.

### Interface file naming (`component-interface-file-naming.md`)

`IBadge.ts` — correct. No `Bds` prefix on the interface file. **No issues found.**

### Memory topic files consulted

- `feedback_prop_validation_pattern.md`
- `stencil-face-attach-internals.md`
- `stencil-prop-patterns.md`
- `feedback_event_naming.md`
- `component-accessor-naming-conventions.md`
- `component-interface-file-naming.md`

---

## Summary of Findings

| #   | Severity   | File                 | Finding                                                                                                  |
| --- | ---------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | ❌ Warning | `bds-badge.tsx` L2–5 | Import order: local imports before internal aliases                                                      |
| 2   | ❌ Warning | `bds-badge.tsx` L52  | Getter `getBadgeClasses` has redundant `get` prefix → rename to `badgeClasses`                           |
| 3   | ❌ Missing | `bds-badge.mdx`      | React and Vue usage examples absent                                                                      |
| 4   | ⚠️ Minor   | `bds-badge.tsx`      | JSDoc on private methods (`checkPropValues`, `componentWillLoad`, `getBadgeClasses`) violates convention |
| 5   | ⚠️ Minor   | `bds-badge.scss`     | `align-items` and `justify-content` on `display: contents` element are no-ops; remove them               |

**Blockers for merge**: Findings 1, 2, and 3 should be resolved before merge. Findings 4 and 5 are non-blocking but recommended.
