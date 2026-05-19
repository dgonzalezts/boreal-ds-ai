# Boreal DS — Code Review Report

**Generated:** 2026-05-06T11:45:52
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/actions/bds-button-group/bds-button-group.tsx:4`
  - **Standard:** Imports must follow the order: (1) framework/node_modules, (2) internal aliases `@/` ordered by abstraction layer, (3) local/relative `./` or `../`.
  - **Antipattern:** Lines 2–3 (`./types/IButtonGroup`, `./types/enum`) are local imports placed before the `@/types` and `@/utils` alias imports on lines 4–6. The corrected order:
    ```ts
    import { Component, Host, Prop, h, Element, Watch } from "@stencil/core";
    import { ORIENTATIONS } from "@/types";
    import { CORE_COLORS } from "@/types/coreColors";
    import { validatePropValue } from "@/utils/helpers/validateProps";
    import { BUTTON_GROUP_SIZES } from "./types/enum";
    import { IButtonGroup } from "./types/IButtonGroup";
    import { BUTTON_VARIANTS } from "../bds-button/types/enum";
    ```
- 🟡 **[barrel-wildcard-export]** `export * from '...'` in `packages/boreal-web-components/src/types/index.ts` — **pre-existing, not introduced by this PR.** Out of scope for this review.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  - **Standard:** Every PR that touches a publishable package (`boreal-web-components`, `boreal-docs`) must include a changeset entry or verified CHANGELOG update.
  - **Action required:** This PR introduces a new component (`bds-button-group`) — that is a `minor` bump. A changeset file must be added before merge.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - Stories and MDX are present, but the MDX only has a vanilla HTML usage example. React and Vue snippets are missing.
  - **Standard:** Every MDX file must include usage examples for all three integration paths: vanilla JS, React, and Vue (see documentation.instructions.md §MDX sections).
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ✅ Every @Prop() has `readonly` and an adjacent JSDoc block
- ✅ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ✅ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ✅ JSDoc changes preserve custom-elements.json generation accuracy
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/\*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### 1. Prop validation pattern (`feedback_prop_validation_pattern.md`)

✅ No issues. The component correctly combines:

- `validatePropValue` for all four enum-like props (`size`, `orientation`, `color`, `variant`).
- Stacked `@Watch()` decorators on `validateProps()`.
- `componentWillLoad()` calling `validateProps()` to catch invalid initial attribute values.

### 2. Getter accessor naming (`component-accessor-naming-conventions.md`)

✅ No issues. The single getter `classMapButtonGroup` correctly names the value it returns with no redundant `get` prefix.

### 3. Light DOM / no Shadow DOM (`project_no_shadow_dom.md`)

✅ No issues. SCSS uses direct tag selectors (`bds-button { ... }`) and class selectors (`.bds-button-group`). No `:host` pseudo-class appears anywhere in the stylesheet.

### 4. Event naming semantics (`feedback_event_naming.md`)

✅ Not applicable. This component dispatches no custom events.

### 5. TODO comment in committed code

❌ **Violation of commit standards.**
`bds-button-group.tsx` line 75 contains:

```ts
// TODO: Remove sizeMap once bds-button adopts the same size nomenclature (sm, md, lg)
```

Per project conventions, `TODO` annotations must not appear in committed code. Track this as a task in the issue tracker instead.

### 6. Cross-component type import

⚠️ **Informational / low risk.**
`BUTTON_VARIANTS` is imported directly from `../bds-button/types/enum`. This creates a coupling between `bds-button-group` and `bds-button`'s internal enum file. For a group component that exists solely to wrap and propagate button props, this is intentional and reasonable — but it means any rename of `BUTTON_VARIANTS` in `bds-button` will break this import. The coupling is acceptable but should be noted in the ticket.

### 7. SCSS outer margin on host element

⚠️ **Design question.**
`.bds-button-group` applies `margin: $boreal-spacing-2xs $boreal-spacing-3xs` to itself. Components should generally not impose outer margin, leaving layout control to the consumer. If this margin is required by the Figma spec, it is acceptable. If not, it should be removed.

### 8. Unit tests

**Run result:** ✅ 37 tests, 4 suites — all pass (`pnpm test -- src/components/actions/bds-button-group`).

**Suite breakdown:**

| File                                | Tests | Status |
| ----------------------------------- | ----- | ------ |
| `bds-button-group.a11y.spec.ts`     | 6     | ✅     |
| `bds-button-group.basics.spec.ts`   | 7     | ✅     |
| `bds-button-group.slots.spec.ts`    | 3     | ✅     |
| `bds-button-group.variants.spec.ts` | 21    | ✅     |

**Coverage assessment:** Good. The suite covers all four enum-like props across initial render, `@Watch`-triggered updates, and invalid-value fallbacks. Accessibility attributes (`role`, `tabindex`, `aria-orientation`, `aria-label`) and slot rendering are fully covered.

**Issues found:**

❌ **Typo in test assertion message** — `bds-button-group.variants.spec.ts`, size table iteration:

```ts
assertExists(button, "Child button shouldt");
// should be:
assertExists(button, "Child button should exist");
```

❌ **TODO comment in committed test file** — `bds-button-group.variants.spec.ts`, line above `sizeConfigurations`:

```ts
// TODO: Update expected values when bds-button adopts the same size nomenclature (sm, md, lg)
```

Same violation as in the component file. Remove and track as a task.

⚠️ **`BdsButton` not registered in `components` array** — All test pages query `bds-button` children after `propagatePropsToButtons()` calls native `setAttribute` on them. Because `setAttribute` is a native DOM call (not a Stencil prop binding), `getAttribute` correctly reflects the set value even without `BdsButton` in `components`. The pattern works as written, but registering `BdsButton` would make intent explicit and protect against future refactors that switch from `setAttribute` to JSX prop binding. Low risk, informational.

⚠️ **No test for `label` prop update** — The `label` prop drives `aria-label` via the render method. There is no test asserting that updating `label` after initial render causes `aria-label` to re-reflect. Coverage gap is minor since the `aria-label` default and custom-at-init cases are covered.

⚠️ **No test for `orientation` class update on prop change** — `@Watch('orientation')` only calls `validateProps`, not `propagatePropsToButtons` (correct by design). There is no test asserting that mutating `orientation` after load updates the CSS class from `--horizontal` to `--vertical`. Consider adding to `basics.spec.ts`.

---

### Memory topic files consulted

- `feedback_prop_validation_pattern.md`
- `component-accessor-naming-conventions.md`
- `project_no_shadow_dom.md`
- `feedback_event_naming.md`
- `stencil-child-component-props-in-tests.md`

---

**Result: 26 passed · 1 failed** — unit test review complete

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
