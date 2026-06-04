# bds-text-field: Shared Utilities Refactoring + Suffix Slot

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Refactor `bds-text-field` to consume the shared form-field utilities already established by `bds-tag-field` (render helpers, SCSS mixins, `useFormField` lifecycle hook), eliminate inline duplicated logic, and expose a `<slot name="suffix">` as a **sibling to the actions div** inside the container — the structural enabler for composite components (primarily `bds-select`) to inject opt-in loading indicators and badges without modifying `bds-text-field`.

**Architecture:** Three independent layers of work run in sequence: (1) extend the shared `renderFieldParts.tsx` with two backward-compatible additions — a `readOnly` guard on `renderFieldActions` and a `counterClass` override on `renderFieldFooter`; (2) migrate the TSX component — render layer to shared render functions, form lifecycle to `useFormField`, suffix slot as a sibling to the actions div in the container, inline actions div (password toggle prevents full delegation to `renderFieldActions`) — and add the suffix slot; (3) migrate SCSS to shared mixins with documented container overrides. Password toggle and `clearOnHover` CSS remain text-field-specific throughout.

**Tech Stack:** Stencil, TypeScript, SCSS, `@stencil/core` JSX

---

## Files to create / modify

| File | Notes |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx` | Modify — add `readOnly?` to `FieldActionsProps`/`renderFieldActions`; add `counterClass?` to `FieldFooterProps`/`renderFieldFooter` |
| `packages/boreal-web-components/src/components/forms/bds-text-field/types/ITextField.ts` | Modify — extend `IFormFieldProps`; retain text-field-only props |
| `packages/boreal-web-components/src/components/forms/bds-text-field/types/enum.ts` | Modify — re-export `FIELD_VARIANTS` / `FIELD_VALIDATION_TIMING` as backward-compatible aliases |
| `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` | Modify — shared render functions, `useFormField` lifecycle, inline actions div, suffix slot first, icon `<em>` → `<i>` |
| `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.scss` | Modify — shared mixin calls + text-field-specific overrides |
| `packages/boreal-web-components/src/components/forms/bds-text-field/__test__/bds-text-field-basics.spec.ts` | Modify — add suffix slot tests |

---

## Tasks

### Task 1: Extend shared render utilities

**Files:**

- `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx` (modify)

**Context:**
`renderFieldActions` (line 132) currently computes `showClear` without checking `readOnly` — any component passing `readOnly` without knowing this gap would incorrectly show a clear button on a read-only field. `renderFieldFooter` (line 100) hardcodes `${prefix}__tag-count` as the counter CSS class, preventing other components from using their own class name without forking the function.

**Acceptance criteria:**

- `FieldActionsProps` gains `readOnly?: boolean` — when `true`, the clear button must not render regardless of `clearable` and `hasValue`
- `showClear` in `renderFieldActions` guards against `props.readOnly === true` in addition to the existing `!props.isDisabled` guard
- `FieldFooterProps` gains `counterClass?: string` — CSS class applied to the counter element; defaults to `${props.prefix}__tag-count` when omitted, preserving existing `bds-tag-field` behavior exactly
- Existing callers (`bds-tag-field`) pass no new props → zero behavioral change

**Unit tests to cover:**

No new spec file. Changes are pure type extensions + one guard condition. Coverage comes from component-level tests in Tasks 3 and 6. Validate with TypeScript compiler only.

**Manual test _(waiveable)_:**

```bash
pnpm tsc --noEmit
```

Zero new type errors. Run `bds-tag-field` spec suite as regression check:

```bash
pnpm jest -- --testPathPattern="bds-tag-field"
```

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13696 extend renderFieldActions with readOnly guard and renderFieldFooter with counterClass"
```

---

### Task 2: Align ITextField types with shared form field types

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/types/ITextField.ts` (modify)
- `packages/boreal-web-components/src/components/forms/bds-text-field/types/enum.ts` (modify)

**Context:**
`ITextField` (line 4) redeclares 16 props that are already defined in `IFormFieldProps` from `@/components/forms/common`. `enum.ts` defines `TEXT_FIELD_VARIANTS` and `TEXT_FIELD_VALIDATION_TIMING` with identical values to the shared `FIELD_VARIANTS` and `FIELD_VALIDATION_TIMING`.

**Acceptance criteria:**

- `ITextField` extends `IFormFieldProps` and removes the following duplicated prop declarations: `name`, `disabled`, `required`, `error`, `errorMessage`, `label`, `helperText`, `info`, `placeholder`, `variant`, `clearable`, `customValidators`, `validationTiming`, `customWidth`, `sublabel`, `icon`, `iconRight`
- The following text-field-specific props remain declared directly on `ITextField`: `value`, `readOnly`, `type`, `autocomplete`, `pattern`, `minLength`, `maxLength`, `clearOnHover`, `charCount`, `counter`, `selectable`
- `TEXT_FIELD_VARIANTS` in `enum.ts` becomes `export { FIELD_VARIANTS as TEXT_FIELD_VARIANTS } from '@/components/forms/common'` — not a new object; the same reference
- `TEXT_FIELD_VALIDATION_TIMING` in `enum.ts` becomes `export { FIELD_VALIDATION_TIMING as TEXT_FIELD_VALIDATION_TIMING } from '@/components/forms/common'`
- `TEXT_FIELD_TYPES` constant remains unchanged in `enum.ts` (no shared equivalent)
- `TextFieldVariant` and `TextFieldValidationTiming` type aliases in `types.ts` remain exported — they can alias `FieldVariant` and `FieldValidationTiming` if desired, but must remain importable from `./types`

**Unit tests to cover:**

No runtime behavior change. Validate with TypeScript compiler only.

**Manual test _(waiveable)_:**

```bash
pnpm tsc --noEmit
```

Zero new type errors. Any removed duplicate declarations that were also exported must not produce missing-export errors in consumers.

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-13696 align ITextField with IFormFieldProps"
```

---

### Task 3: Migrate bds-text-field render layer + add suffix slot

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` (modify)

**Context:**
`bds-text-field.tsx` (lines 457–568) computes render state inline and builds label, sublabel, footer, and actions as inline JSX. `bds-tag-field` provides the reference pattern using `deriveFieldRenderState`, `renderFieldLabel`, `renderFieldSublabel`, and `renderFieldFooter`. The actions div is **kept inline** (not delegated to `renderFieldActions`) because the password toggle requires custom ordering that would unnecessarily complicate the shared utility.

The suffix slot is positioned as a **sibling to the actions div**, placed in the container after the `<input>` and before the actions div. By being a sibling rather than a child of the actions div, the slot is always accessible in the render tree regardless of whether any system buttons are active — with no coupling between the two areas. Composite parents (e.g. `bds-select`) inject content (spinner, badge) that visually precedes the system-managed buttons, matching the Figma design.

**Acceptance criteria:**

- `render()` replaces all five inline computed variables (`effectiveError`, `helperContent`, `showFooter`, `typographyState`, `labelId`, `helperId`) with a single `deriveFieldRenderState({...})` call
- `renderFieldLabel({ id: labelId, label, required, info, htmlFor: this._id, state: typographyState })` replaces the inline `<bds-typography>` label block (lines 478–489)
- `renderFieldSublabel({ prefix: 'bds-text-field', icon: this.icon, sublabel: this.sublabel })` replaces the inline `<span class="bds-text-field__sublabel">` block (lines 491–496)
- `renderFieldFooter({ prefix: 'bds-text-field', id: helperId, helperContent, showFooter, state: typographyState, counter: this.counter && this.charCount > 0, current: this.currentCharCount, max: this.charCount, counterClass: 'bds-text-field__char-count' })` replaces the inline footer div (lines 552–565)
- `<slot name="suffix" />` is placed directly in the container JSX **after the `<input>` element and before the actions div** — always present in the render tree as an independent sibling, regardless of whether any system buttons are active
- The actions `<div>` is rendered **inline** as `<div class="bds-text-field__actions">` and contains, in this exact order:
  1. Clear button — when `(clearable || clearOnHover) && value !== '' && !isDisabled && !readOnly`
  2. Password toggle button — when `type === 'password'`
  3. Icon-right span — when `iconRight !== ''`
- The actions `<div>` renders **conditionally** — absent from the DOM when no buttons are active (existing behavior preserved; no change from pre-refactor)
- All icon elements inside the actions div and the password toggle change from `<em class={...}>` to `<i class={...} aria-hidden="true" />` to match the shared component pattern
- `<slot name="tags" />` is **removed** from the render — it is undocumented, unused by any known consumer, and is a legacy placeholder from an earlier iteration where tag chips were to be slotted into `bds-text-field` directly; that architecture was superseded by the standalone `bds-tag-field` component

**Prop default value alignment** (per `.agents/memory/stencil-prop-patterns.md` — constants as `@Prop()` defaults corrupt the Custom Elements Manifest; the CEM analyzer records the identifier, not the resolved string):
- `validationTiming` default changes from `TEXT_FIELD_VALIDATION_TIMING.BLUR` → `'blur'`
- `type` default changes from `TEXT_FIELD_TYPES.TEXT` → `'text'`
- `variant` default changes from `TEXT_FIELD_VARIANTS.OUTLINE` → `'outline'`
- Constants remain valid in all logic: `validatePropValue`, switch cases, class maps — only the `@Prop()` initializer must be a string literal

**Class JSDoc cleanup** (per `ai-docs/guidelines/jsdoc-template.md` — prohibited tags produce zero CEM output while creating maintenance divergence):
- `@summary` tag — remove; not a CEM-recognized tag
- All `@attr` entries (×8) — remove; generated from `@Prop()` decorators automatically
- All `@property` entries (×14) — remove; generated from `@Prop()` decorators automatically
- All `@fires` entries (×7) — remove; generated from `@Event()` decorators automatically
- `@cssprop` entry — remove; CSS custom properties must be documented with `/** @prop */` in the SCSS file (Task 5), not in the TSX class block
- Class JSDoc retains: one-sentence description + `@slot prefix` (verified) + `@slot suffix` (new, added above)

**Unit tests to cover** _(existing spec files — add to relevant files)_:

- `bds-text-field-basics.spec.ts`: the suffix slot placeholder is present in the DOM regardless of `clearable`, `type`, and `iconRight` values — it is a structural sibling to the actions div, not dependent on it
- `bds-text-field-basics.spec.ts`: content placed in `slot="suffix"` renders as a **sibling to** `.bds-text-field__actions`, not inside it; it precedes the actions div in document order
- `bds-text-field-a11y.spec.ts`: existing ARIA structure tests pass without modification (label, describedby, aria-invalid)

**Manual test:**

Add to `packages/boreal-web-components/src/index.html`:

- Scenario A: `<bds-text-field label="No actions">` — field with no clearable, no password, no iconRight
- Scenario B: `<bds-text-field label="With suffix + clearable" clearable value="hello">` with a `<span slot="suffix" style="font-size:12px;padding:2px 6px;background:#eee;border-radius:4px">0</span>` child

Validation checklist (`pnpm dev:components`):

- [ ] Scenario A: field renders normally; no actions div in the DOM (conditional behavior preserved — no buttons active)
- [ ] Scenario B: the "0" badge appears **to the left of** the clear (×) button — badge is in the suffix slot sibling, clear is in the actions div
- [ ] Scenario B: clearing the input hides the clear button (actions div may disappear); the badge remains visible in the suffix slot
- [ ] No console errors or Stencil slot warnings in either scenario

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-13696 migrate bds-text-field render layer to shared utilities and add suffix slot"
```

---

### Task 4: Migrate bds-text-field form lifecycle to useFormField

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` (modify)

**Context:**
`bds-text-field` (lines 319–344) implements `updateValidity()` and `invalidHandler` inline. `useFormField<T>` from `@/utils/form` provides identical implementations and is already in use by `bds-tag-field`. The hook requires the host to satisfy `IFormFieldHost<T>`, which includes a public `validators` getter — currently declared `private` on line 399.

**Acceptance criteria:**

- A `private readonly _field = useFormField<string>(this)` class property is added (matching `bds-tag-field` pattern)
- The `validators` getter (line 399) has its `private` modifier removed so the class satisfies `IFormFieldHost<string>`
- The private `updateValidity(emitEvent = false)` method is deleted; all call sites are replaced with `this._field.updateValidity(emitEvent)`
- The private `invalidHandler` arrow function (line 334) is deleted; its registration is replaced with `this._field.attachInvalidListener()` in `componentDidLoad` and `this._field.detachInvalidListener()` in `disconnectedCallback`
- `handleFocus` calls `this._field.handleFocus(e)` first, then assigns `this._valueAtFocus = this.value` after (the hook handles `focused=true` and `bdsFocus` emission; the text-field retains the `_valueAtFocus` assignment for change-timing validation)
- `formAssociatedCallback` delegates to `this._field.formAssociatedCallback(this.value)` (replaces the two-line `setFormValue + updateValidity()` body)
- `formResetCallback` resets `this.value = ''` and `this.currentCharCount = 0`, then calls `this._field.reset()` (handles `touched`, `dirty`, `validationError`, `validationMessage`), then `setFormValue(this.internals, null)`, then `this._field.updateValidity()`
- `formStateRestoreCallback` sets `this.value` then delegates to `this._field.formAssociatedCallback(this.value)`
- `checkValidity` and `reportValidity` `@Method()` implementations delegate to `this._field.checkValidity()` and `this._field.reportValidity()` respectively
- `@Watch('customValidators') onCustomValidatorsChange` calls `this._field.updateValidity()`
- `@Watch('value') onValueChange` calls `this._field.updateValidity(this.touched || this.validationError)` (logic unchanged, call target changed)
- The direct `import { runValidators }` from `@/utils` is removed if it becomes unused after this migration

**Unit tests to cover** _(existing specs — regression check, no new tests required)_:

- All tests in `bds-text-field-validation.spec.ts` pass without modification
- All tests in `bds-text-field-form.spec.ts` pass without modification
- All tests in `bds-text-field-events.spec.ts` pass without modification — specifically `bdsValidationChange` emission with correct `{ valid, validity, value, touched, dirty }` shape

**Manual test:**

Use Scenario B from Task 3 (`pnpm dev:components`):

- [ ] Type in the field, blur → validation runs and helper text shows if `required` and value is empty
- [ ] Submit a parent `<form>` → `invalid` event fires; validation error state shown
- [ ] Reset parent `<form>` → field clears, error state gone, counter resets

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-13696 migrate bds-text-field lifecycle to useFormField hook"
```

---

### Task 5: Refactor bds-text-field.scss to shared mixins

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.scss` (modify)

**Context:**
`bds-text-field.scss` currently implements its entire rule set inline using a different spacing model from `bds-tag-field` (container `padding-left: 0`, each element adds its own `padding-left`). This divergence needs to be unified: `bds-text-field` must adopt the same shared approach as `bds-tag-field` — apply `form-field-shell` and the element mixins exactly as tag-field does, letting the shell's container `padding-left: $boreal-spacing-xs` handle the left spacing for all elements. The only container difference between the two components is that text-field is fixed single-line (`height`) while tag-field is multi-line (`min-height`). See `bds-tag-field.scss` as the reference.

**Acceptance criteria:**

- File starts with `@use '../_shared/form-field-shell' as *` and `@use '../_shared/form-field-elements' as *`
- `$prefix: 'bds-text-field'` variable declared at the top
- `@include form-field-shell($prefix)` applied; immediately followed by a single `.#{$prefix}__container` override that sets only `height: $boreal-layout-l` (converts shell's `min-height` to a fixed height for the single-line input — the only structural difference from `bds-tag-field`)
- `@include form-field-sublabel($prefix, $flex-shrink: 0)` applied with no additional overrides — container padding handles left spacing
- `@include form-field-slot-prefix` applied with no additional overrides
- `@include form-field-control($prefix)` applied; followed by a `.#{$prefix}__control` override adding only:
  - `min-width: 0`
  - `width: 100%`
  (no `padding-left` — container handles it; these two are text-field-specific flex sizing)
- `@include form-field-actions($prefix)` applied with no additional overrides
- `@include form-field-action($prefix)` applied
- `@include form-field-counter('#{$prefix}__char-count')` applied (replaces inline `__char-count` block)
- `@include form-field-disabled-sublabel($prefix)` applied (the `$icon-tag` param defaults to `'i'`, matching after the `<em>→<i>` migration in Task 3)
- The following rules are retained as text-field-specific overrides **after** the mixin calls:
  - `&__action--password`: `@include bds-icon($boreal-icons-l, $boreal-typography-font-size-lg)` (not in shared — larger size than clear)
  - `&__action--icon-right`: flex-center, flex-shrink, color, bds-icon sizing
  - `&--selectable .#{$prefix}__container input`: cursor + pointer-events
  - `&--clear-on-hover .#{$prefix}__action--clear`: opacity/pointer-events show/hide logic
  - `&--readonly .#{$prefix}__control::placeholder`: placeholder color override
  - `&--disabled .#{$prefix}__control`: color override (shared mixin covers container but not control color)
- All per-element `padding-left: $boreal-spacing-xs` declarations from the old inline file are deleted — not migrated
- The `%field-inline-label` placeholder is deleted from this file — it is already defined in `_form-field-elements.scss` and available via `@use`
- No hardcoded color, spacing, or typography values remain — all replaced with `$boreal-*` token references

**`reflect: true` audit** (per `.agents/memory/stencil-prop-patterns.md` — reflect only when the SCSS has an attribute CSS selector for that prop):
- Read the full SCSS and verify which reflected props (`name`, `disabled`, `required`, `value`, `error`, `type`, `variant`) are referenced by an attribute selector (e.g. `bds-text-field[variant="plain"]` or `&[disabled]`)
- Remove `reflect: true` from any prop whose value is driven purely by a CSS class modifier (e.g. `bds-text-field--plain`) rather than an attribute selector

**CSS custom property documentation** (per `ai-docs/guidelines/jsdoc-template.md` — `@prop` belongs in SCSS, not in the TSX class JSDoc):
- Add `/** @prop --bds-text-field-width: Sets a custom width for the component. */` as a `@prop` JSDoc comment in the SCSS file's component tag-selector block (e.g. `bds-text-field { ... }`)
- This was incorrectly placed as `@cssprop` in the TSX class JSDoc; that entry was removed in Task 3

**Unit tests to cover:**

No unit test changes needed. Validate visually.

**Manual test:**

Use the full set of scenarios in `packages/boreal-web-components/src/index.html`:

- Scenario: default outline field with label, placeholder, helper text
- Scenario: field with sublabel + icon
- Scenario: field with prefix slot content
- Scenario: field with `clearable` and a non-empty value
- Scenario: field with `clearOnHover`
- Scenario: field with `type="password"`
- Scenario: field with `variant="plain"`
- Scenario: field with `disabled`
- Scenario: field with `readonly`
- Scenario: field with `selectable`
- Scenario: field with `counter` and `charCount`
- Scenario: field with `error` state

Validation checklist (`pnpm dev:components`):

- [ ] All scenarios render identically to the pre-refactor baseline (no spacing or color regressions)
- [ ] `--focused` state: correct border + focus ring
- [ ] `--error` state: danger border color
- [ ] `--disabled` state: muted background; sublabel and control are de-emphasized
- [ ] `--readonly` state: no border, transparent background
- [ ] `--plain` state: transparent border at rest, focus border on focus
- [ ] `--selectable` state: pointer cursor in the input
- [ ] `--clear-on-hover`: clear button hidden at rest, visible on hover
- [ ] Password toggle has correct larger icon size vs the smaller clear button icon
- [ ] Icon-right (chevron used by select) rotates on `aria-expanded="true"`

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-13696 migrate bds-text-field SCSS to shared form-field mixins"
```

---

### Task 6: Unit tests — suffix slot

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/__test__/bds-text-field-basics.spec.ts` (modify)

**Context:**
Task 3 adds the suffix slot and makes the actions div unconditional. These behaviors are the primary API contract enabling the `bds-select` integration and must be covered by automated tests. Existing tests that assert the actions div is absent when no built-in actions are active must be updated.

**Acceptance criteria:**

- Test: when `clearable=false`, `type="text"`, `iconRight=""`, and no suffix content — `div.bds-text-field__actions` is **absent** from the DOM (conditional behavior); the suffix slot placeholder is present as an independent sibling
- Test: when an element with `slot="suffix"` is passed — it renders as a **sibling to** `div.bds-text-field__actions`, not inside it; it precedes the actions div in document order
- Test: when `clearable=true` and `value` is non-empty — the suffix slot sibling precedes the actions div (which contains the clear button) in document order
- Test: when `type="password"` — the password toggle renders inside the actions div; the suffix slot is a sibling to that div, independent of it
- Any existing tests asserting the actions div is absent when no built-in buttons are active remain correct and need no update

**Manual test _(waiveable)_:**

Behaviors already verified manually in Task 3.

```bash
pnpm jest -- --testPathPattern="bds-text-field-basics"
```

**Commit:**

```bash
git commit -m "test(web-components): EOA-13696 add suffix slot unit tests for bds-text-field"
```

---

### Task 7: Add bds-spinner mixin to _interactions.scss and refactor bds-button

**Files:**

- `packages/boreal-web-components/src/styles/_interactions.scss` (modify)
- `packages/boreal-web-components/src/components/actions/bds-button/bds-button.scss` (modify)

**Context:**
The Figma design for the loading spinner (`/Users/dgonzalez/Downloads/spinner.svg`) is a 270° arc (3/4 circle) at 16×16px, stroke-width 2, color `$boreal-icon-default-light`. The CSS equivalent is `border: 2px solid $color; border-top-color: transparent` (only the top border transparent, producing a 270° visible arc). This is meaningfully different from `bds-button`'s current approach which makes both `border-right-color` and `border-top-color` transparent, producing only a 180° arc that doesn't match the design.

`_interactions.scss` is already the home for shared animation patterns (`bds-transition-action`, `bds-transition-surface`, `bds-focus-ring`). Adding a `bds-spinner` mixin there follows the established convention and gives any component a single source of truth for the spinner shape and animation.

`bds-button.scss` uses a verbose `::after` pseudo-element block with inline border values and its own `@keyframes rotateSpinner`. After this task, the shape and animation delegate to the shared mixin; the button retains only the positioning overrides unique to the overlay pattern.

**Acceptance criteria:**

- `_interactions.scss` gains a `bds-spinner($size, $border-width, $color)` mixin:
  - `$size` defaults to `12px`
  - `$border-width` defaults to `2px`
  - `$color` defaults to `$boreal-icon-default-light`
  - Sets: `width`, `height`, `border: $border-width solid $color`, `border-radius: 50%`, `border-top-color: transparent` (270° arc matching Figma), `animation: bds-spin 1s linear infinite`
- `@keyframes bds-spin { to { transform: rotate(360deg); } }` is added to `_interactions.scss`
- In `bds-button.scss`, the `&--is-loading::after` block is refactored:
  - `@include bds-spinner(1em, 3px, currentColor)` replaces the inline `border`, `border-radius`, `border-right-color`, `border-top-color`, and `animation` declarations
  - `currentColor` is used so the per-variant color override in `bds-button-logic` continues to work
  - Positioning-only properties remain inline: `position: absolute`, `content: ' '`, `box-sizing: inherit`, `display: block`, `left: calc(50% - 0.5em)`, `top: calc(50% - 0.5em)`
  - `rotate: 45deg` is removed (not needed with the 270° arc; the gap starts at the top by default)
- In the `bds-button-logic` mixin, the `&.bds-button--is-loading::after` block replaces `border-left-color` and `border-bottom-color` overrides with a single `color: $text-dis` — which becomes the `currentColor` consumed by the spinner border
- The inline `@keyframes rotateSpinner` block at the bottom of `bds-button.scss` is deleted (superseded by `bds-spin` in `_interactions.scss`)
- No visual regression: all button variants' loading states display a correctly sized, correctly colored spinner

**Unit tests to cover:**

No unit test changes. Validate visually.

**Manual test:**

Add to `packages/boreal-web-components/src/index.html`:

- Scenario: `<bds-button class="bds-button--is-loading bds-button--var-default bds-button--default bds-button--size-md">Loading</bds-button>` for each variant (default, primary, success, error) and style (default, outline, plain)

Validation checklist (`pnpm dev:components`):

- [ ] All button loading states show a spinner — 270° arc (3/4 circle), not a half-circle
- [ ] Spinner color matches the variant's disabled text color per variant
- [ ] Spinner animation is smooth; no visual jank vs the previous animation

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-13696 add bds-spinner mixin to _interactions.scss and standardize bds-button loading spinner"
```

---

### Task 8: JSDoc audit + Storybook story

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` (modify — JSDoc only)
- Storybook story file for `bds-text-field` (modify — add suffix slot story variant)

**Acceptance criteria:**

- All `@Prop` blocks have current, accurate descriptions (audit against final implementation)
- `@slot suffix` JSDoc entry is present per Task 3 (no `@slot tags` — that slot is removed in Task 3)
- Storybook story adds a `WithSuffix` variant rendering `<bds-text-field>` with a `<span slot="suffix">` badge element, demonstrating the integration contract to consumers
- MDX documentation updated to include a "Slots" section listing `prefix`, `tags`, and `suffix` with one-line descriptions each

**Manual test:**

```bash
pnpm dev:docs
```

- [ ] `WithSuffix` story renders the badge to the left of the clear and chevron buttons
- [ ] Storybook "Docs" tab shows all three slots in the component API table

**Commit:**

```bash
git commit -m "docs(web-components): EOA-13696 audit JSDoc and add suffix slot Storybook story for bds-text-field"
```

---

## Next Steps: bds-select Integration

> These changes are **not part of this ticket**. Document here for the engineer implementing the follow-up.

The `suffix` slot added in this plan is the structural enabler for composite parents. The integration splits into two separate follow-up efforts based on which field component is used.

### Architecture: slot-based composition

`bds-select`'s `render()` method requires **zero changes** for either follow-up. The consumer decides which field component occupies `slot="field"`:

```tsx
render() {
  return (
    <Host role="none">
      <slot name="field"></slot>   {/* consumer: bds-text-field (single) or bds-tag-field (multi) */}
      <input type="hidden" value={this.value} name={this.name} />
      <bds-popover width="full">
        <slot name="list"></slot>
      </bds-popover>
    </Host>
  );
}
```

---

### Follow-up A: Single-select loading state (immediate next ticket)

This is the direct follow-up to this plan. It wires a new `loading` prop on `bds-select` to the `suffix` slot of `bds-text-field`.

#### Behavioral matrix

| `loading` | Actions div contents (left → right inside field) |
|---|---|
| `false` | `[clear ×]` `[chevron ∨]` |
| `true` | `[spinner]` |

Loading hides both the clear button and the chevron by updating `bds-text-field` props via `updateElementProp`.

#### Step 0: bds-spinner mixin prerequisite

Task 7 of this plan adds the `bds-spinner` mixin to `packages/boreal-web-components/src/styles/_interactions.scss` and the `@keyframes bds-spin` animation. This mixin must ship before implementing the loading state.

#### New prop on bds-select

| Prop | Type | Default | Description |
|---|---|---|---|
| `loading` | `boolean` | `false` | When `true`, shows a spinner in the suffix slot and hides the clear button and chevron |

#### Integration approach

In `bds-select.tsx` `componentDidLoad`:

1. Create `<span slot="suffix" class="bds-select__suffix">` and `appendChild` it to `this.bdsField` — Stencil's light-DOM slot emulation projects it into `bds-text-field`'s `suffix` slot
2. Inside the wrapper, create `<span class="bds-select__spinner">` (hidden by default)
3. Add `@Watch('loading')`:
   - `loading=true`: show spinner, `updateElementProp(this.bdsField, 'clearable', false)`, `updateElementProp(this.bdsField, 'iconRight', '')`
   - `loading=false`: hide spinner, restore `clearable: true` and `iconRight: 'bds-icon-chevron-down'`

#### SCSS additions to bds-select.scss

```
.bds-select__suffix  — flex, align-items: center, gap: $boreal-spacing-3xs
.bds-select__spinner — @include bds-spinner() (from _interactions.scss)
```

---

### Follow-up B: Multi-select (separate ticket)

Covered in full in `ai-work/research/bds-select-multiselect-extension.md`. The consumer swaps `bds-text-field` for `bds-tag-field` in `slot="field"`. `bds-select` gains a `multiselect` prop that only affects the event contract (toggle vs replace, keep popover open); the render method stays unchanged.

The **badge** (showing a selected-items count) belongs here — not in the single-select path. A "N selected" count badge is a multi-select UX concept: in single-select, the selected value is always visible in the field itself. `bds-tag-field` will need its own `<slot name="suffix">` addition (parallel to this plan's Task 3) to receive the badge and spinner injected by `bds-select[multiselect]`.

---

### Reference

Colibri's `col-select.renderSuffix()` in `ai-docs/lib/colibri-components.tsx` is the design reference for the suffix injection pattern. For the loading state: clear button and chevron are suppressed; the spinner fills their place in the actions area.
