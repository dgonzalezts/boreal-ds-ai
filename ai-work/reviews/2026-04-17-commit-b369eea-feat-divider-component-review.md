# Boreal DS — Code Review Report

**Generated:** 2026-04-17T14:22:58  
**Base ref:** `main`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-react (React wrapper)** — checklist section(s): B
- **boreal-vue (Vue wrapper)** — checklist section(s): B
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[class-jsdoc-invalid-tags]** Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-banner/bds-banner.tsx:5`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:5`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-spinner/bds-spinner.tsx:53`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx:70`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx:89`
- 🟡 **[face-reset-no-validity]** `formResetCallback` is defined but `updateValidity()` or `setValidity()` is not called — validity state may be stale after reset. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.tsx`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:63`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:71`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-flag/bds-flag.tsx:78`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/constants/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-flag/types/index.ts:2`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:98`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:188`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:6`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/overlays/bds-dialog/types/index.ts:3`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:55`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:3`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:6`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:7`
- 🔴 **[aria-camel-set-attr]** `setAttribute` called with a camelCase ARIA attribute name. Use kebab-case: `setAttribute('aria-describedby', ...)` not `setAttribute('ariaDescribedBy', ...)`. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:249`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx:300`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:5`
- 🔴 **[aria-camel-set-attr]** `setAttribute` called with a camelCase ARIA attribute name. Use kebab-case: `setAttribute('aria-describedby', ...)` not `setAttribute('ariaDescribedBy', ...)`. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:173`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:100`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/mixins/backdrop.mixin.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/mixins/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/services/floating/interfaces/index.ts:5`

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ✅ Storybook/MDX/README updated when behavior or APIs change
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
  - **Standard:** Every `@Prop()` must be `readonly` and have a JSDoc block directly above it. Missing JSDoc means missing descriptions in `custom-elements.json`, breaking Storybook argTypes auto-generation.
  - **Antipattern:** `Missing JSDoc on @Prop()` — violates `stencil/required-jsdoc` (an ESLint error). Affected: `bds-flag.tsx:63,71,78`, `bds-popover.tsx:55`.
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - **Standard:** Do not use `mutable: true` on `disabled`, `checked`, or `value`. Use `@Prop({ reflect: true }) readonly checked` + `@State() private isChecked` and write to state in `@Watch` and `formDisabledCallback`.
  - **Antipattern:** `mutable: true` on `disabled`/`checked` causes a Stencil compiler warning and creates two writers on the same reflected attribute (the component and the browser via FACE lifecycle). Affected: `bds-checkbox.tsx:70`, `bds-text-field.tsx:98`.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - **Standard:** Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). Exception: `valueChange` is reserved for Vue `v-model` integration — see Memory-Guided Review below.
  - **Antipattern:** Event names not matching `bds{Action}` break generated framework bindings (`onBdsClose` in React, `@bds-close` in Vue). Affected: `bds-checkbox.tsx:89`, `bds-text-field.tsx:188` — see note in Memory-Guided Review.
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ❌ Only ElementInternals.setValidity() manages validity
  - **Standard:** The custom element owns validity via `ElementInternals.setValidity()`; inner `<input>` elements must not carry native constraint attributes (`required`, `minlength`, etc.). Without this, the browser fires two validation events and attempts to focus the inner `<input>` rather than the host element on submit failure.
  - **Antipattern:** `Using native constraint attrs on inner <input>` — causes doubled validation events and "invalid form control is not focusable" errors on submit. Affected: `bds-text-field.tsx` (`required` on inner `<input>`).
- ❌ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
  - **Standard:** Both callbacks must call `updateValidity()` after restoring the value. Skipping this leaves the validity state reflecting the pre-reset value — the control may appear valid when it should not.
  - **Antipattern:** `Skipping updateValidity() after reset/restore` — leaves validity state stale. Affected: `bds-checkbox.tsx` `formResetCallback` (does not call `updateValidity()`).
- ❌ JSDoc changes preserve custom-elements.json generation accuracy
  - **Standard:** Do not place `@element` or `@method` in a component class JSDoc block. The CEM analyzer reads these and discards them silently — decorators are the sole source of truth. Writing them creates a false sense of documentation completeness.
  - **Antipattern:** `Using @element or @method in class JSDoc` — ignored by the CEM analyzer, produces no output in `custom-elements.json`. Affected: `bds-banner.tsx`.
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ❌ ARIA attribute names passed to `setAttribute` are kebab-case
  - **Standard:** `setAttribute` requires the HTML attribute name in kebab-case. The DOM property uses camelCase (`element.ariaDescribedBy`) but `setAttribute` operates on the attribute name, which is always kebab-case for ARIA.
  - **Antipattern:** `setAttribute with camelCase ARIA names` — writes a non-standard, unrecognised attribute to the DOM. Screen readers do not recognise the camelCase variant — this is an accessibility regression with no visible runtime error. Affected: `bds-popover.tsx:249`, `bds-tooltip.tsx:173`.
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ❌ Getter accessors carry no redundant `get` prefix
  - **Standard:** Getter accessors must not carry a `get` prefix. The `get` keyword already communicates accessor semantics — callers read it as `this.getPlacement` which is doubly redundant. Name getters after the value they return.
  - **Antipattern:** `get prefix on getter accessors` — `get getPlacement()` should be `get placement()`. Affected: `bds-spinner.tsx:53`, `bds-popover.tsx:300`, `bds-tooltip.tsx:100`.

### B — React/Vue Wrappers

- ✅ Generated outputs/types rebuilt when web components change
- ✅ @telesign/boreal-web-components stays in `dependencies`
- ✅ Uses `publishPackageManager: pnpm` with `publishArgs`

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

> _This section is completed by the agent after reading `.claude/memory/MEMORY.md` and the relevant topic files. The script leaves this placeholder intentionally._

<!-- MEMORY_REVIEW_PLACEHOLDER -->

---

**Result: 22 passed · 8 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_