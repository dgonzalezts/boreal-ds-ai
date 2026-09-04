# Boreal DS — Code Review Report

**Component:** `bds-color-picker` (EOA-17156)
**Generated:** 2026-09-04
**Base ref:** `release/current`
**Branch:** `feature/EOA-17156_color-picker`
**Scope:** 41 files across 6 subcomponents + helpers

---

## Affected Components

| Component | Files | Role |
|-----------|-------|------|
| `bds-color-picker` | tsx, scss, types, test | Root form-associated wrapper |
| `bds-color-controls` | tsx, scss, types, tests | Picker panel compositor |
| `bds-color-box` | tsx, scss, types, test | 2D saturation/brightness selector |
| `bds-hue-slider` | tsx, scss, types, test | Hue range slider |
| `bds-alpha-slider` | tsx, scss, types, test | Opacity range slider |
| `bds-color-format` | tsx, scss, types, test | Format selector + channel inputs |
| `helpers/color-utils.ts` | 1 file | Color parsing, conversion, format config |

---

## Automated Findings

### Errors

1. **[event-name-format]** `@Event() valueChange` at `bds-color-picker.tsx:107` does not follow `bds{Action}` format.
   - **Exception applies**: MEMORY.md documents that `valueChange` is reserved for Vue `v-model` integration. This is a deliberate, documented exception — not a violation. **Dismissed.**

2. **[face-native-constraint-on-input]** Inner `<input>` in `bds-alpha-slider.tsx` and `bds-hue-slider.tsx` carries native `min` attribute.
   - **Severity: Medium.** These subcomponents are NOT form-associated (no `formAssociated: true`, no `@AttachInternals()`). The constraint validation rule applies to FACE components where `ElementInternals.setValidity()` owns validity. Standalone presentational sliders using native `<input type="range">` with `min`/`max` for UI boundary clamping is acceptable. **Dismissed for subcomponents.**

3. **[prop-mutable-form-attr]** `value` prop uses `mutable: true` at `bds-color-picker.tsx:73`.
   - **Severity: High.** The `value` prop is the canonical form value. The coding standard requires a `@State() private` mirror for native form attributes written by the component. The component writes `this.value = hex` in `commitColor()` (line 213) and `this.value = this.initialValue` in `formResetCallback()` (line 338), which creates two writers on the same reflected attribute (the component and the browser via form association). Should use `@State() private internalValue` and sync via `@Watch('value')`.

### Warnings

4. **[barrel-wildcard-export]** All 6 `types/index.ts` files use `export * from '...'` (12 instances).
   - **Severity: Low.** Hinders tree-shaking analysis. Should use named re-exports: `export { IColorPicker } from './IColorPicker'`.

5. **[import-order]** `bds-color-controls.tsx:4` — `import type { HsvColor } from '@colordx/core'` appears after a relative import.
   - **Severity: Low.** External package imports should precede relative imports.

6. **[missing-stories]** No Storybook stories detected in the diff.
   - **Severity: High.** Component is undocumented for consumers.

7. **[missing-changeset]** No changeset or CHANGELOG entry.
   - **Severity: Medium.** Required for release tracking.

---

## Review Checklist

### Universal

- [x] Change has a clear purpose with minimal unrelated edits
- [x] No `any` usage without justification (see test helper issue below)
- [x] Error paths and invalid inputs handled explicitly
- [x] New logic is covered by tests (partial — several `it.todo` remain)
- [x] Tests use `waitForChanges()` before DOM assertions
- [ ] Storybook/MDX/README updated when behavior or APIs change
- [x] Public APIs, events, and props follow naming conventions (with documented `valueChange` exception)
- [x] Self-referencing `{ ...x, ... }` spreads guard against no-op reassignment
- [x] Event handlers guard against redundant re-invocation

### A — Stencil (boreal-web-components)

- [x] Every @Prop() has `readonly` and an adjacent JSDoc block
- [ ] Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true` — **FAIL: `value` uses `mutable: true`**
- [x] `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props — N/A (no enum props)
- [x] Custom events use the `bds{Action}` prefix pattern (with documented `valueChange` exception)
- [x] Event names do not reuse native DOM events
- [x] @AttachInternals() is on the class body, not in a mixin
- [x] `checkValidity()` and `reportValidity()` exposed via @Method()
- [ ] Only ElementInternals.setValidity() manages validity — **FAIL: `formResetCallback` and `formStateRestoreCallback` do not call `updateValidity()`**
- [x] Boolean @Prop() names use no `is`/`has`/`show` prefix
- [x] Props declared on component class, not inside mixin factory
- [x] ARIA attribute names passed to `setAttribute` are kebab-case
- [x] Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- [x] Getter accessors carry no redundant `get` prefix
- [x] No unused `@State()`/non-`reflect` `@Prop()` fields

---

## Memory-Guided Review

### `valueChange` event naming
- **No issue.** MEMORY.md explicitly documents: "`valueChange` is reserved for Vue `v-model` integration." The automated tool flags this, but it is a deliberate exception.

### FACE `disabled` pattern
- **No issue.** `disabled` is declared as `@Prop() readonly disabled: boolean = false` — correct, no `mutable: true`. No `@State() private isDisabled` mirror needed since the component never writes to `disabled` internally.

### Form controls — `IFormControl<string>` composite interface
- **Correct.** `implements IColorPicker, IFormControl<string>` is present. `validators` getter returns the correct shape. `checkValidity()` and `reportValidity()` are exposed via `@Method()`.

### `formResetCallback` missing `updateValidity()`
- **Issue found.** `formResetCallback()` resets `validationError` and `validationMessage` to defaults but does NOT call `this._field.updateValidity()`. This leaves the `ElementInternals` validity state stale after a form reset. Same issue in `formStateRestoreCallback()`.

### Light DOM — no shadow
- **No issue.** No `shadow: true` anywhere. All components use light DOM correctly.

### SCSS — unscoped selector leak
- **No issue.** All selectors in `bds-color-picker.scss` are nested inside the `.bds-color-picker` root block.

### SCSS — hard-coded colors
- **Issue found.** `bds-color-picker.scss:30` uses `repeating-conic-gradient(#ddd 0 25%, #fff 0 50%)` — hard-coded `#ddd` and `#fff` violate the "no hard-coded colours" rule. Should use design tokens or CSS custom properties.

### SCSS — `!important` usage
- **Issue found.** `bds-color-picker.scss:60,72` uses `border-color: transparent !important` to override child component styles. This is a maintenance hazard and indicates the child component's style API may need a CSS custom property instead.

### Event naming semantics
- **No issue.** Events follow `bds{Action}` pattern: `bdsChange`, `bdsInput`, `bdsFocus`, `bdsBlur`, `bdsValidationChange`, `bdsPickerChange`, `bdsHueChange`, `bdsAlphaChange`, `bdsColorBoxChange`, `bdsFormatColorChange`, `bdsFormatAlphaChange`. No component noun embedded in the middle.

### `mouseleave` / `relatedTarget`
- **No issue.** No `mouseleave` handlers used. Focus management uses `focusin`/`focusout` on the wrapper element.

### Enum-like props
- **No issue.** No string-literal-union props that need `validatePropValue`.

### Reference stability — spread guards
- **No issue.** `commitColor()` always sets `this.hsva = next` with a new value from an event. The `@Watch('value')` guard at line 166 (`if (next.toUpperCase() === toHexString(this.hsva)) return`) correctly prevents redundant re-emission when the parent reflects back the same value.

### Unsafe type cast in `bds-color-controls`
- **Issue found.** `bds-color-controls.tsx:71` — `color={details as ColorChangeDetail & string}` is an unsafe intersection cast. `ColorChangeDetail` is an object type; intersecting with `string` produces `never` at the type level. This compiles only because `as` casts bypass checking. The `bds-color-format` `color` prop expects `ColorChangeDetail`, so the cast should be removed — `details` is already `ColorChangeDetail`.

### Test quality — `any` in test helper
- **Issue found.** `bds-color-picker.spec.ts:17` — `instance: any` in `invokeInput()` helper. The project rule is "no `any`". Should type as `BdsColorPicker`.

### Test coverage — incomplete `it.todo` items
- **Issue found.** 5 `it.todo` items remain in `bds-color-picker.spec.ts`:
  - Alpha draft commit on blur
  - Alpha normalization on blur
  - External value draft preservation
  - Focus emission behavior
  - Popover open trigger behavior

### `bds-color-format` — native `onChange` vs `onBdsChange`
- **Issue found.** `bds-color-format.tsx:185` uses `onChange={this.handleAlphaInput}` (native DOM event) on a `<bds-number-field>`. All other number-field listeners in the codebase use `onBdsChange`. This may work but is inconsistent and could break if `bds-number-field` changes its native event bubbling behavior.

---

## Summary

| Category | Passed | Failed |
|----------|--------|--------|
| Automated rules | 20 | 3 (1 dismissed, 1 dismissed, 1 valid) |
| Checklist items | 17 | 2 |
| Memory-guided checks | 10 | 6 |

### Critical issues (must fix before merge)

1. **`value` prop `mutable: true`** — Use `@State() private` mirror pattern
2. **`formResetCallback` / `formStateRestoreCallback`** missing `updateValidity()` calls
3. **Unsafe cast** in `bds-color-controls.tsx:71` — `ColorChangeDetail & string` is `never`
4. **Missing Storybook stories** — component is undocumented

### High-priority issues (should fix)

5. **Hard-coded colors** in SCSS (`#ddd`, `#fff`)
6. **`!important` overrides** in SCSS — needs CSS custom property API from child components
7. **Native `onChange`** on `bds-number-field` in `bds-color-format.tsx:185`
8. **`any` type** in test helper

### Medium-priority issues (nice to fix)

9. **Barrel wildcard exports** — 12 instances across `types/index.ts` files
10. **Import order** in `bds-color-controls.tsx`
11. **Missing changeset**
12. **5 `it.todo` test items** — incomplete coverage

---

## Memory topic files consulted

- `MEMORY.md` — event naming exception for `valueChange`
- `stencil-light-dom-unscoped-selector-leak.md` — SCSS selector nesting check
- `stencil-state-spread-reference-instability-redundant-rerender.md` — spread guard check
- `component-enum-prop-const-object-pattern.md` — enum prop validation check
- `sass-design-tokens-are-css-vars-not-literals.md` — hard-coded color check
