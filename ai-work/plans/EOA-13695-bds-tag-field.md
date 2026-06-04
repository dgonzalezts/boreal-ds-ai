---
status: done
---

# `bds-tag-field` Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement `bds-tag-field`, a form-associated Stencil component that lets users enter and remove multiple discrete string values as tag chips inside a fixed-height single-row container, visually consistent with `bds-text-field`.

**Architecture:** Standalone new component — not an extension of `bds-text-field`. Shared form-field logic is extracted into a new `useFormField<T>()` factory in `utils/form/field-form-association.ts` (following the `useFormCheckbox` precedent); shared JSX render helpers go into `components/forms/common/`; shared SCSS container rules go into `components/forms/_shared/_form-field-shell.scss`. `bds-text-field` is **not modified in this PR** — the shared utilities are built for `bds-tag-field` first and will be adopted by `bds-text-field` in a follow-up ticket.

**Tech Stack:** Stencil v4, TypeScript, SCSS with `$boreal-*` design tokens, `KeyboardController` (`utils/a11y/keyboard`), `formAssociatedMixin` (`mixins/`), `runValidators` + `setFormValue` (`utils/form/internals`), `bds-tag` (existing feedback component), `bds-typography` (existing component).

---

## Files to create / modify

| File                                                                                                          | Notes                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `packages/boreal-web-components/src/utils/form/field-form-association.ts`                                     | New — `useFormField<T>()` factory, `IFormFieldHost<T>` interface                                                                                                                                                                                       |
| `packages/boreal-web-components/src/utils/form/index.ts`                                                      | Modify — add `export * from './field-form-association'`                                                                                                                                                                                                |
| `packages/boreal-web-components/src/components/forms/_shared/_form-field-shell.scss`                          | New — shared SCSS partial: container shell, focus ring, error/disabled/plain/outline states                                                                                                                                                            |
| `packages/boreal-web-components/src/components/forms/_shared/_form-field-elements.scss`                       | New (Task 9) — opt-in element mixins: `form-field-sublabel`, `form-field-slot-prefix`, `form-field-control`, `form-field-actions`, `form-field-action`, `form-field-counter`, `form-field-disabled-sublabel`; shared `%field-inline-label` placeholder |
| `packages/boreal-web-components/src/components/forms/common/form-field-types.ts`                              | New — `FIELD_VARIANTS`, `FIELD_VALIDATION_TIMING` enums, `FieldVariant`, `FieldValidationTiming` types, `IFormFieldProps` interface; modified in Task 7b to add `sublabel?`, `icon?`, `iconRight?`                                                     |
| `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx`                             | New — `renderFieldLabel`, `renderFieldFooter`, `deriveFieldRenderState`; modified in Task 7b to add `renderFieldSublabel`, `renderFieldActions`                                                                                                        |
| `packages/boreal-web-components/src/components/forms/common/index.ts`                                         | New — barrel export for `common/`                                                                                                                                                                                                                      |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/ITagField.ts`                        | New — extends `IFormFieldProps`, declares only 6 tag-specific props                                                                                                                                                                                    |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/enum.ts`                             | New — re-exports `FIELD_VARIANTS as TAG_FIELD_VARIANTS`, `FIELD_VALIDATION_TIMING as TAG_FIELD_VALIDATION_TIMING` from `common/`                                                                                                                       |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/types.ts`                            | New — type aliases `TagFieldVariant = FieldVariant`, `TagFieldValidationTiming = FieldValidationTiming`                                                                                                                                                |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/index.ts`                            | New — types barrel                                                                                                                                                                                                                                     |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx`                         | New — component implementation                                                                                                                                                                                                                         |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.scss`                        | New — component styles                                                                                                                                                                                                                                 |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-basics.spec.ts`     | New — rendering and tag management tests                                                                                                                                                                                                               |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-events.spec.ts`     | New — event emission tests                                                                                                                                                                                                                             |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-keyboard.spec.ts`   | New — keyboard interaction tests                                                                                                                                                                                                                       |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-validation.spec.ts` | New — built-in and custom validator tests                                                                                                                                                                                                              |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-form.spec.ts`       | New — FACE lifecycle tests                                                                                                                                                                                                                             |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-a11y.spec.ts`       | New — accessibility attribute tests                                                                                                                                                                                                                    |
| `packages/boreal-web-components/targets/vue-output-target.ts`                                                 | Modify — add `bds-tag-field` to `componentModels`                                                                                                                                                                                                      |
| `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.stories.ts`                                   | New — Storybook stories                                                                                                                                                                                                                                |
| `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.mdx`                                          | New — MDX documentation page                                                                                                                                                                                                                           |

---

## Task 1: Shared form-field logic utility

**Files:**

- `packages/boreal-web-components/src/utils/form/field-form-association.ts` (create)
- `packages/boreal-web-components/src/utils/form/index.ts` (modify)

**Utility discovery — Form association and validation:**

- Feature area: shared form-field state management, validation lifecycle, focus/blur handling, FACE `invalid` event integration.
- Search performed: `utils/form/`, `mixins/`, `components/forms/bds-checkbox/utils/`.
- Candidates found: `formAssociatedMixin` (handles `formDisabledCallback` only), `runValidators` + `setFormValue` in `utils/form/internals.ts` (handles the validation call), `useFormCheckbox` in `bds-checkbox/utils/checkbox-form-association.ts` (handles checkbox-specific FACE callbacks).
- Fit assessment: `formAssociatedMixin` — partial fit (only one callback); `runValidators`/`setFormValue` — full fit (used internally); `useFormCheckbox` — partial fit (checkbox-specific, not generic).
- Reuse decision: create a new `useFormField<T>()` factory in `utils/form/field-form-association.ts` that wraps `runValidators` and `setFormValue`. This is the generic equivalent of `useFormCheckbox` for any field component with a typed value.
- Gap handling: `useFormCheckbox` cannot be extended — it is tightly coupled to `ICheckbox` (checked, indeterminate). A new generic factory is required.
- Anti-duplication: `bds-tag-field` must not implement `invalidHandler`, `updateValidity`, `attachInvalidListener`, or `handleFocus` directly — these must come exclusively from `useFormField<T>()`.

**Acceptance criteria:**

- Define and export `IFormFieldHost<T>` interface requiring: `el: HTMLElement`, `internals: ElementInternals`, `focused: boolean`, `touched: boolean`, `dirty: boolean`, `validationError: boolean`, `validationMessage: string`, `value: T`, `validators: IFormValidator[]`, `customValidators: IFormValidator[]`, `bdsFocus: EventEmitter<{ event: FocusEvent }>`, `bdsBlur: EventEmitter<{ event: FocusEvent }>`, `bdsValidationChange: EventEmitter<ValidationChangePayload<T>>`.
- Define and export `ValidationChangePayload<T>` type: `{ valid: boolean; validity: ValidityState; value: T; touched: boolean; dirty: boolean }`.
- `useFormField<T>(host: IFormFieldHost<T>)` returns an object with the following members:
  - `updateValidity(emitEvent?: boolean)` — calls `runValidators`, updates `host.validationError` and `host.validationMessage`, emits `bdsValidationChange` when `emitEvent` is `true`.
  - `checkValidity()` — delegates to `host.internals.checkValidity()`.
  - `reportValidity()` — delegates to `host.internals.reportValidity()`.
  - `attachInvalidListener()` — adds the internal `invalidHandler` to `host.el` as an `'invalid'` event listener.
  - `detachInvalidListener()` — removes the same `invalidHandler` reference.
  - `handleFocus(e: FocusEvent)` — sets `host.focused = true`, emits `host.bdsFocus`.
  - `formAssociatedCallback(formValue: FormDataEntryValue | null)` — calls `setFormValue(host.internals, formValue)` then `updateValidity()`.
  - `reset()` — sets `host.validationError = false`, `host.validationMessage = ''`, `host.touched = false`, `host.dirty = false`.
  - `clearValidation()` — sets `host.validationError = false`, `host.validationMessage = ''` only.
- The internal `invalidHandler` calls `e.preventDefault()`, sets `host.validationError = true`, `host.validationMessage = host.internals.validationMessage`, and emits `bdsValidationChange` with `valid: false`.
- `utils/form/index.ts` exports everything from `field-form-association.ts`.
- No JSX, no Stencil decorators, no component-specific imports anywhere in this file.

**Unit tests to cover** _(no spec file — this utility is tested via integration through `bds-tag-field` specs)_:

- Covered indirectly by `bds-tag-field-validation.spec.ts` and `bds-tag-field-form.spec.ts` in Tasks 10–11.

**Manual test _(waiveable — pure TypeScript utility with no visual output)_:**

Run: TypeScript compiler check only.

- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes with no new errors.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add useFormField generic form-field utility"
```

---

## Task 2: Shared SCSS partial — form field shell

**Files:**

- `packages/boreal-web-components/src/components/forms/_shared/_form-field-shell.scss` (create)

**Utility discovery — Styling:**

- Feature area: container border, focus ring, error/disabled states, plain/outline variant, footer layout — shared between `bds-text-field` and `bds-tag-field`.
- Search performed: `components/forms/_shared/`, `components/forms/bds-text-field/bds-text-field.scss`.
- Candidates found: `_selectable-button.scss`, `_selectable-group.scss` — not relevant (button/group layout). `bds-text-field.scss` — full source of truth for the rules to extract.
- Reuse decision: Extract a new `_form-field-shell.scss` partial. `bds-text-field.scss` is **not modified** in this PR; the extraction serves `bds-tag-field.scss` only. The migration of `bds-text-field` to use this partial is a follow-up.

**Acceptance criteria:**

- Partial provides a `bds-field-shell` mixin (or block of placeholders) covering: container border (`1px solid $boreal-stroke-default-light`), border-radius (`$boreal-radius-xs`), background (`$boreal-ui-inverse`), `@include bds-transition-surface`, and flex alignment.
- Provides modifier rules for: `--focused` (focus ring color + border color), `--error` (danger border + focus ring), `--disabled` (disabled background + pointer-events none), `--plain` (transparent border at rest, visible on focus), `--readonly` (transparent background, no border).
- Provides footer layout rules: flex row, gap between helper text and counter.
- Uses only `$boreal-*` tokens — zero hardcoded color, size, or spacing values.
- File starts directly with `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *;` and `@use '../../../styles/_interactions' as *;` — no leading comment block. SCSS partials accessed via `@use` from component SCSS exist in their own Sass module scope; they do NOT inherit `injectGlobalPaths` globals and must declare their own imports. Component SCSS files (like `bds-tag-field.scss`) must NOT add an additional `@use` of the token package — see `.agents/memory/stencil-sass-inject-global-paths-constraint.md`.

**Unit tests to cover** _(no spec file — visual regression caught by manual test and Chromatic)_:

- N/A for SCSS partials.

**Manual test _(waiveable until Task 9 when bds-tag-field.scss uses it)_:**

- [ ] Visual regression deferred to Task 9 manual test.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add shared form-field shell SCSS partial"
```

---

## Task 3: Shared component-layer types and render helpers

**Files:**

- `packages/boreal-web-components/src/components/forms/common/form-field-types.ts` (create)
- `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx` (create)
- `packages/boreal-web-components/src/components/forms/common/index.ts` (create)

**Utility discovery — Shared types:**

- Feature area: `variant` enum (`outline | plain`) and `validationTiming` enum (`blur | change | input | submit`) — values are identical between `bds-text-field` and `bds-tag-field`.
- Search performed: `bds-text-field/types/enum.ts` (source), `@/types/form.ts` (existing `IFormProps`), `components/forms/common/` (does not yet exist).
- Candidates found: `TEXT_FIELD_VARIANTS` / `TEXT_FIELD_VALIDATION_TIMING` in `bds-text-field/types/enum.ts` — identical values needed by tag-field. `IFormProps` in `@/types/form.ts` — partial fit (5 optional props; 1 consumer: `bds-toggle`). `ITextField` — not extendable (bds-text-field is out of scope for this PR).
- Reuse decision: create `IFormFieldProps` in `components/forms/common/form-field-types.ts` that extends `IFormProps` (narrowing its optional members to required) and adds the full shared field surface. `bds-tag-field/types/ITagField.ts` extends `IFormFieldProps` and declares only its 6 tag-specific props. `IFormProps` itself is **not modified** — `bds-toggle` is not affected.
- Known temporary duplication: `FIELD_VARIANTS` / `FIELD_VALIDATION_TIMING` in `common/` will have the same values as `TEXT_FIELD_VARIANTS` / `TEXT_FIELD_VALIDATION_TIMING` in `bds-text-field/types/`. This is intentional. The follow-up `bds-text-field` migration ticket will replace the text-field copies with imports from `common/`.

**Utility discovery — JSX rendering:**

- Feature area: label rendering via `bds-typography[variant="label"]` and footer rendering via `bds-typography[variant="helper"]` — identical JSX between `bds-text-field` and `bds-tag-field`.
- Search performed: `components/forms/bds-text-field/bds-text-field.tsx` render method; `components/forms/common/` (does not yet exist).
- Candidates found: none — no shared JSX helpers exist today.
- Reuse decision: create new helpers. These are JSX-returning functions so they must live in `components/forms/common/` (not `utils/`), preserving the one-way dependency rule: `utils/` must not import from `components/`.

**Acceptance criteria — `form-field-types.ts`:**

- Export `FIELD_VARIANTS = { OUTLINE: 'outline', PLAIN: 'plain' } as const`.
- Export `FIELD_VALIDATION_TIMING = { BLUR: 'blur', CHANGE: 'change', INPUT: 'input', SUBMIT: 'submit' } as const`.
- Export `FieldVariant` and `FieldValidationTiming` derived types.
- Export `IFormFieldProps` that extends `IFormProps` (from `@/types`) and declares the full shared field prop surface with **required** (non-optional) members: `error`, `errorMessage`, `label`, `helperText`, `info` (narrowed from optional in `IFormProps`), plus `name`, `disabled`, `required`, `placeholder`, `variant: FieldVariant`, `clearable`, `customValidators: IFormValidator[]`, `validationTiming: FieldValidationTiming`, `customWidth`.
- No Stencil decorators or JSX in this file — pure TypeScript types and constants only.

**Acceptance criteria — `renderFieldParts.tsx`:**

- Export `deriveFieldRenderState(host)` — accepts an object with `{ _id, label, required, info, helperText, error, errorMessage, validationError, validationMessage, isDisabled, counter?, charCount?, values? }` and returns `{ labelId, helperId, helperContent, showFooter, typographyState, effectiveError }`. `helperContent` follows the cascade: `error + errorMessage` → `validationError + validationMessage` → `helperText`.
- Export `renderFieldLabel(props: FieldLabelProps): JSX.Element | null` — returns `<bds-typography variant="label" ...>` when `props.label !== ''`, `null` otherwise. Props: `id`, `label`, `required`, `info` (forwarded as `tooltipText`), `htmlFor`, `state`.
- Export `renderFieldFooter(props: FieldFooterProps): JSX.Element | null` — returns the footer `<div>` with `<bds-typography variant="helper">` and an optional counter `<span>`. Returns `null` when `showFooter` is `false`. Props: `id`, `helperContent`, `showFooter`, `state`, `counter` (boolean), `current` (number), `max` (number).
- `FieldLabelProps` and `FieldFooterProps` are exported types from this file.
- No logic other than JSX derivation — no event handling, no state mutation.

**Acceptance criteria — `common/index.ts`:**

- Re-exports everything from `form-field-types.ts` and `renderFieldParts.tsx`.

**Unit tests to cover** _(no dedicated spec — covered via bds-tag-field render tests in Task 10)_:

- Indirectly tested: label renders when `label !== ''`, absent when `label === ''`; footer renders helper text, validation message takes precedence over helperText, error message takes precedence over both; counter renders `{current}/{max}` when enabled.

**Manual test _(waiveable — no standalone visual output)_:**

- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add shared form field render helpers"
```

---

## Task 4: Type files

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/types/ITagField.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/types/enum.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/types/types.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/types/index.ts` (create)

**Acceptance criteria:**

- `enum.ts` re-exports shared constants from `common/` under tag-field-scoped aliases — declares no new constant objects:
  - `export { FIELD_VARIANTS as TAG_FIELD_VARIANTS, FIELD_VALIDATION_TIMING as TAG_FIELD_VALIDATION_TIMING } from '../../common'`
- `types.ts` declares type aliases pointing to shared types — declares no new union literals:
  - `export type TagFieldVariant = FieldVariant`
  - `export type TagFieldValidationTiming = FieldValidationTiming`
- `ITagField.ts` exports `ITagField` that **extends `IFormFieldProps`** (imported from `../../common`) and declares **only the 6 tag-field-specific props**. Follow the naming convention from `ITextField.ts` (`ITagField`, not `IBdsTagField`):

  | Prop              | Type       | Default  | Reflect |
  | ----------------- | ---------- | -------- | ------- |
  | `values`          | `string[]` | `[]`     | no      |
  | `allowDuplicates` | `boolean`  | `false`  | no      |
  | `maxTags`         | `number`   | `0`      | no      |
  | `maxVisibleTags`  | `number`   | `0`      | no      |
  | `maxTagLength`    | `number`   | `0`      | no      |
  | `tagColor`        | `TagColor` | `'gray'` | no      |

  The 15 shared props (`name`, `disabled`, `required`, `error`, `errorMessage`, `label`, `helperText`, `info`, `placeholder`, `variant`, `clearable`, `customValidators`, `validationTiming`, `customWidth`) are **inherited from `IFormFieldProps`** — do not redeclare them.

- `types/index.ts` re-exports everything from all three files.

**Unit tests to cover** _(no spec — type-only, verified by TypeScript compiler)_:

- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes.

**Manual test _(waiveable)_:**

- [ ] TypeScript compiler reports no errors.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add bds-tag-field type definitions"
```

---

## Task 5: Scaffold — props, events, stub render

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (create)

**Acceptance criteria:**

- Component class `BdsTagField` extends `Mixin(formAssociatedMixin)` and implements `ITagField` and `IFormControl<string[]>`.
- `@Component` decorator: `tag: 'bds-tag-field'`, `styleUrl: 'bds-tag-field.scss'`, `formAssociated: true`.
- All `@Prop()`, `@State()`, `@Event()`, and `@AttachInternals()` declarations match the interface in Task 4 exactly.
- Shared state block declares: `isDisabled`, `focused`, `touched`, `dirty`, `validationError`, `validationMessage` — matching the `IFormFieldHost<T>` contract so `useFormField<string[]>(this)` can be instantiated.
- Private field `private readonly _field = useFormField<string[]>(this)` instantiated at class level.
- Private field `private readonly _keyboard = new KeyboardController({ preventDefault: false })` instantiated at class level.
- `@Method() async checkValidity()` delegates to `this._field.checkValidity()`.
- `@Method() async reportValidity()` delegates to `this._field.reportValidity()`.
- `render()` returns a minimal `<Host />` stub — no content yet.
- All lifecycle methods (`componentWillLoad`, `componentDidLoad`, `disconnectedCallback`) and FACE callbacks (`formAssociatedCallback`, `formResetCallback`, `formStateRestoreCallback`) exist as empty stubs.
- Component compiles with no TypeScript errors.

**Unit tests to cover** _(no spec yet — scaffold only)_:

- N/A.

**Manual test:**

Playground scenarios to implement in `packages/boreal-web-components/src/index.html`:

- Scenario 1: A bare `bds-tag-field` with no props, to verify registration.

Run: `pnpm dev:components` and validate each scenario:

- [ ] Given `bds-tag-field` added to the playground, when the page loads, then the element registers without console errors. Pass: no errors in the browser console and the custom element is defined.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 scaffold bds-tag-field with props, events, stub render"
```

---

## Task 6: Lifecycle, FACE callbacks, and interaction handlers

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify)

**Utility discovery — Keyboard:**

- Feature area: keyboard bindings for Backspace (remove last tag) and Escape (clear input), and Enter/comma (commit tag from native keydown on the `<input>`).
- Search performed: `utils/a11y/keyboard/KeyboardController.ts`, existing usages in `bds-button-group`, `bds-checkbox`.
- Candidates found: `KeyboardController` — full fit for Backspace and Escape bindings on the host element. `setLinearNavigation` — partial fit for future arrow navigation between tags (not in this PR scope).
- Reuse decision: use `KeyboardController.set()` for Backspace and Escape. Enter and comma are handled via native `onKeyDown` on the `<input>` element directly (they must only fire when the input has focus, not anywhere on the host).
- Anti-duplication: do not add `document.addEventListener('keydown', ...)` or manual `removeEventListener` calls — `KeyboardController` handles cleanup via `AbortController` on `detach()`.

**Utility discovery — Focus/blur:**

- Feature area: focus state tracking, `bdsFocus` emission, `bdsBlur` emission, validation-on-blur.
- Candidates found: `useFormField<T>().handleFocus` — full fit for focus-in. Blur is handled per-component because the tag-field must check `relatedTarget` (focus moving to a `bds-tag` button inside the field must not trigger blur validation).
- Reuse decision: delegate `handleFocus` to `this._field.handleFocus(e)`. Implement `handleBlur` directly on the component with a `relatedTarget` guard.

**Acceptance criteria:**

- `componentWillLoad`: calls `this.checkPropValues()`, sets `this.isDisabled = this.disabled`.
- `componentDidLoad`: calls `this._field.attachInvalidListener()`, then chains `this._keyboard.attach(this.el).set(KEYBOARD.Backspace, () => this.handleBackspace()).set(KEYBOARD.Escape, () => this.clearInput())`.
- `disconnectedCallback`: calls `this._field.detachInvalidListener()` and `this._keyboard.detach()`.
- `@Watch('disabled') onDisabledChange(next)`: sets `this.isDisabled = next`.
- `@Watch('customValidators') onCustomValidatorsChange()`: calls `this._field.updateValidity()`.
- `@Watch('variant') @Watch('validationTiming') checkPropValues()`: calls `validatePropValue` for each watched prop using the corresponding enum values and defaults.
- `@Watch('values') onValuesChange(next)`: calls `setFormValue(this.internals, JSON.stringify(next))`, `this._field.updateValidity(this.touched || this.validationError)`, and emits `valueChange`.
- `formAssociatedCallback`: delegates to `this._field.formAssociatedCallback(JSON.stringify(this.values))`.
- `formResetCallback`: sets `this.values = []`, `this.dirty = false`, calls `this._field.reset()`, calls `setFormValue(this.internals, null)`, then `this._field.updateValidity()`.
- `formStateRestoreCallback(state)`: parses state via `JSON.parse` in a try/catch (defaults to `[]` on error), sets `this.values`, calls `setFormValue` and `this._field.updateValidity()`.
- `handleCommit(raw: string)`: trims input; ignores empty string; ignores input exceeding `maxTagLength` when `maxTagLength > 0`; ignores duplicate when `allowDuplicates === false` and value already in `values`; ignores when `maxTags > 0` and `values.length >= maxTags`; otherwise appends to `values`, sets `dirty = true`, emits `bdsTagAdd`, clears the input element value.
- `handleBackspace()`: when the inner `<input>` value is empty and `values.length > 0`, removes the last entry from `values`, emits `bdsTagRemove`.
- `clearInput()`: sets the inner `<input>` element value to `''`.
- `handleTagClose(value: string)`: removes the first occurrence of `value` from `values`, emits `bdsTagRemove`.
- `handleOverflowClose()`: sets `values = values.slice(0, effectiveMaxVisible)`, emits `bdsTagRemove` for each removed value.
- `handleClearAll()`: sets `values = []`, sets `dirty = true`, calls `this._field.clearValidation()`, emits `bdsClear`.
- `handleFocus(e: FocusEvent)`: delegates to `this._field.handleFocus(e)`.
- `handleBlur(e: FocusEvent)`: checks `relatedTarget` — if focus moved to a descendant of `this.el`, returns early (prevents false blur when clicking a tag's close button). Otherwise sets `focused = false`, `touched = true`, emits `bdsBlur`, and calls `this._field.updateValidity(true)` when `validationTiming === 'blur'`.
- `handleKeyDown(e: KeyboardEvent)` (on the `<input>`): if `e.key === 'Enter'` or `e.key === ','`, calls `e.preventDefault()` then `this.handleCommit(inputEl.value)`.
- Private getter `validators: IFormValidator[]` returns: `valueMissing` (fails when `required && values.length === 0`, message: `'At least one tag is required.'`), `rangeOverflow` (fails when `maxTags > 0 && values.length > maxTags`, message: `'Maximum of {maxTags} tags allowed.'`).
- Private getter `effectiveMaxVisible: number` returns: `maxVisibleTags > 0 ? maxVisibleTags : maxTags > 0 ? maxTags - 1 : values.length`.
- Private getter `classMap` returns BEM modifier map: `bds-tag-field`, `bds-tag-field--error`, `bds-tag-field--disabled`, `bds-tag-field--focused`, `bds-tag-field--plain`, `bds-tag-field--clear-on-hover` (not applicable — omit).
- Private getter `hostStyle` returns `{ '--bds-tag-field-width': customWidth }` when `customWidth !== ''`, else `undefined`.
- Private getter `inputEl` returns `this.el.querySelector<HTMLInputElement>('input')`.

**Unit tests to cover** _(deferred to Task 10)_:

- N/A.

**Manual test:**

Playground scenarios to implement in `packages/boreal-web-components/src/index.html`:

- Scenario 1: A `bds-tag-field` with `required=true` and no tags, to verify validation-on-blur.
- Scenario 2: A focused tag field with text in the input, to verify tag commit on Enter.
- Scenario 3: A tag field with one tag and an empty input, to verify Backspace removal.

Run: `pnpm dev:components` and validate each scenario:

- [ ] Given a tag field with `required=true` and no tags, when focus leaves the field, then the error state is applied. Pass: `--error` modifier present, validation message displayed in the footer.
- [ ] Given a tag field with a focused input containing text, when Enter is pressed, then a tag is added and the input clears. Pass: `bdsTagAdd` emitted, input value empty.
- [ ] Given a tag field with one tag and an empty input, when Backspace is pressed, then the last tag is removed. Pass: `bdsTagRemove` emitted, `values` length decremented by one.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 implement bds-tag-field lifecycle, FACE callbacks, and interaction handlers"
```

---

## Task 7: Full render tree

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify)

**Acceptance criteria:**

- `render()` calls `deriveFieldRenderState(this)` (imported from `../common`) and destructures `{ labelId, helperId, helperContent, showFooter, typographyState, effectiveError }`.
- `<Host>` receives: `class={this.classMap}`, `style={this.hostStyle}`, `tabIndex={-1}`, `onFocus` handler that forwards focus to the inner `<input>` when the field is not disabled.
- Label: calls `renderFieldLabel({ id: labelId, label, required, info, htmlFor: this._id, state: typographyState })` — renders above the container.
- Container `<div class="bds-tag-field__container">`:
  - For each value in `values.slice(0, this.effectiveMaxVisible)`: renders `<bds-tag color={tagColor} closeButtonLabel={`Remove ${v}`} disabled={isDisabled} onBdsClose={() => this.handleTagClose(v)}>{v}</bds-tag>`.
  - When `overflowCount > 0`: renders `<bds-tag color="gray" closeButtonLabel={`Remove ${overflowCount} hidden tags`} onBdsClose={() => this.handleOverflowClose()}>+{overflowCount}</bds-tag>`.
  - `<input>` element: `id={this._id}`, `class="bds-tag-field__control"`, `aria-labelledby={label !== '' ? labelId : undefined}`, `aria-describedby={showFooter && helperContent !== '' ? helperId : undefined}`, `aria-invalid={effectiveError ? 'true' : undefined}`, `aria-required={required ? 'true' : undefined}`, `placeholder={values.length === 0 ? placeholder : ''}`, `disabled={isDisabled}`, `onKeyDown={e => this.handleKeyDown(e)}`, `onFocus={e => this.handleFocus(e)}`, `onBlur={e => this.handleBlur(e)}`. Hidden (via CSS `display: none`) when `maxTags > 0 && values.length >= maxTags`.
  - Actions `<div class="bds-tag-field__actions">`: renders the clear-all `<button>` when `clearable && values.length > 0 && !isDisabled` — `aria-label={ARIA_LABELS.Clear}`, `type="button"`, `onClick={() => this.handleClearAll()}`.
- Footer: calls `renderFieldFooter({ id: helperId, helperContent, showFooter, state: typographyState, counter: maxTags > 0, current: values.length, max: maxTags })`.

**Unit tests to cover** _(deferred to Task 10)_:

- N/A.

**Manual test:**

Playground scenarios to implement in `packages/boreal-web-components/src/index.html`:

- Scenario 1: An empty field with `label` and `placeholder` set.
- Scenario 2: A field with an interactive input to add tags via keyboard.
- Scenario 3: A field with `maxTags=4`, `maxVisibleTags=3`, and 4 values pre-set to show overflow.
- Scenario 4: A field with `clearable=true` and pre-set values to verify the clear button.
- Scenario 5: A field with a slotted element in `slot="prefix"` to verify position 6 renders after icon/sublabel and before input.

Run: `pnpm dev:components` and validate each scenario:

- [ ] Given an empty field with `label` and `placeholder` set, when rendered, then the label appears above and placeholder text is visible inside the container. Pass: label and placeholder both present in the DOM.
- [ ] Given a focused input, when the user types a value and presses Enter, then a tag chip appears and the input clears. Pass: new `bds-tag` rendered, input value empty.
- [ ] Given `maxTags=4`, `maxVisibleTags=3`, and 4 values pre-set, when rendered, then 3 chips and a `+1` overflow chip are visible. Pass: overflow badge with correct count present.
- [ ] Given `clearable=true` with at least one tag, when the clear button is clicked, then all tags are removed. Pass: values array empty, clear button no longer rendered.
- [ ] Given a `<span slot="prefix">` child, when rendered, then the slotted element appears after the sublabel area and before the input. Pass: slotted content visible at position 6 in the container DOM order.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 implement bds-tag-field full render tree"
```

---

## Task 7b: Shared container helpers — prefix area and actions

**Files:**

- `packages/boreal-web-components/src/components/forms/common/form-field-types.ts` (modify)
- `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx` (modify)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify)

**Context:**

The Figma spec shows all three form field components (text field, select, tag field) sharing the same container structure: an optional prefix area (`[icon][sublabel]`) on the left and an optional actions area (clear button, `iconRight`) on the right. Future components such as `textarea` will not use either. Both areas should be opt-in helpers in `renderFieldParts.tsx` — components include only the helpers they need; absent props return `null` with no DOM output.

**Utility discovery:**

- `renderFieldLabel` and `renderFieldFooter` already follow the `prefix`-parameterised CSS class pattern — new helpers follow the same convention.
- `bds-text-field` renders both areas inline; the clear-button logic (`clearable && value.length > 0 && !isDisabled`) is identical to `bds-tag-field`. Extracting it avoids duplication when `bds-text-field` migrates.
- Password toggle is text-field-only and must never be extracted.

**Acceptance criteria — `form-field-types.ts`:**

- Add three optional props to `IFormFieldProps`:
  - `sublabel?: string` — text rendered inside the container to the left of the input.
  - `icon?: string` — icon font class rendered beside the sublabel (e.g. `bds-icon-settings`).
  - `iconRight?: string` — icon font class rendered on the right side of the actions area.
- `ITagField` gains all three automatically through inheritance — no change required in `ITagField.ts`.

**Acceptance criteria — `renderFieldParts.tsx`:**

- Export `FieldSublabelProps` type: `{ prefix: string; icon?: string; sublabel?: string }`.
- Export `renderFieldSublabel(props: FieldSublabelProps): JSX.Element | null` — returns a `<span class="{prefix}__sublabel">` containing an `<em class={icon}>` when `icon` is non-empty and the sublabel text when `sublabel` is non-empty. Returns `null` when both are absent.
- Export `FieldActionsProps` type: `{ prefix: string; clearable: boolean; hasValue: boolean; isDisabled: boolean; iconRight?: string; onClear: () => void }`.
- Export `renderFieldActions(props: FieldActionsProps): JSX.Element | null` — returns a `<div class="{prefix}__actions">` containing:
  - A `<button class="{prefix}__action {prefix}__action--clear" type="button" aria-label={ARIA_LABELS.Clear}>` with an `<i class="bds-icon-close" aria-hidden="true" />` child, when `clearable && hasValue && !isDisabled`.
  - A `<span class="{prefix}__action--icon-right" aria-hidden="true"><i class={iconRight} /></span>` when `iconRight` is non-empty. Non-interactive — the parent container handles the click for dropdown-style components; the chevron is a visual affordance only.
  - Returns `null` when neither condition is met.
- `ARIA_LABELS` is imported from `@/utils` (already available in this file's scope via the existing `h` import block).

**Acceptance criteria — `bds-tag-field.tsx`:**

- Add three new `@Prop()` declarations (each with a single-line JSDoc, `readonly`, default `''`):
  - `/** Sublabel rendered inside the container to the left of the input. */` `@Prop() readonly sublabel: string = '';`
  - `/** Icon font class rendered beside the sublabel inside the container (e.g. `bds-icon-settings`). */` `@Prop() readonly icon: string = '';`
  - `/** Icon font class rendered on the right side of the actions area. Visual affordance only — the parent container handles click for dropdown behaviour. */` `@Prop() readonly iconRight: string = '';`
- In `render()`, replace the inline `{this.clearable && ... && <div class="bds-tag-field__actions">...</div>}` with a call to `renderFieldActions({ prefix: 'bds-tag-field', clearable: this.clearable, hasValue: this.values.length > 0, isDisabled: this.isDisabled, iconRight: this.iconRight, onClear: () => this.handleClearAll() })`.
- After the tag chips and before the `<input>`, call `renderFieldSublabel({ prefix: 'bds-tag-field', icon: this.icon, sublabel: this.sublabel })`.
- Import `renderFieldSublabel` and `renderFieldActions` from `@/components/forms/common`.
- Import `ARIA_LABELS` is already present — no duplicate import needed.

**Unit tests to cover** _(deferred to Task 10)_:

- N/A — covered indirectly by `bds-tag-field-basics.spec.ts`.

**Manual test:**

Update `packages/boreal-web-components/src/index.html` to add a scenario with `icon` and `sublabel` set:

- [ ] Given a tag field with `icon="bds-icon-search"` and `sublabel="Optional"`, when rendered, the icon and sublabel text appear inside the container to the left of the tags. Pass: `bds-tag-field__sublabel` element present in the DOM with the correct content.
- [ ] Given `clearable=true` with pre-set values, the clear button still renders correctly after the refactor to `renderFieldActions`. Pass: button with `aria-label="Clear"` present.
- [ ] Given `iconRight="bds-icon-chevron-down"`, the icon renders on the right side of the container. Pass: `bds-tag-field__action--icon-right` span present.
- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes with no new errors.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add shared prefix and actions container helpers"
```

---

## Task 8: JSDoc audit

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify)

**Acceptance criteria:**

- Class-level JSDoc block:
  - **Component description**: The first paragraph describes the component's purpose and behavior, concise and clear.
  - **@slot prefix**: Document the `prefix` slot — inline content rendered after the icon/sublabel area (position 6 in Figma anatomy) and before the input. Phrasing: `"Inline content rendered after the icon and sublabel, before the input (e.g. status indicator). Intended for single-line elements only; multi-line content will be clipped."`.
  - **No** `@attr`, `@property`, `@fires`, `@summary`, `@cssprop`, or `@method` tags at the class level (per Boreal JSDoc template).
- Every `@Prop()` has a single-line JSDoc (`/** ... */`) directly above the decorator, describing the prop's purpose. This is required for all props, including reflected and non-reflected.
- Every `@Event()` has a single-line JSDoc describing when it fires, placed directly above the decorator.
- Every `@Method()` has a JSDoc describing what it does, what it returns, and any side effects, placed directly above the method.
- JSDoc for the `values` prop must note that the form value is serialized as `JSON.stringify(values)` because `ElementInternals.setFormValue()` only accepts `string | FormData | null`.
- No inline `//` comments anywhere in the file.

**Manual test _(waiveable)_:**

- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes with no new errors.

**Commit:**

```bash
git commit -m "docs(web-components): EOA-13695 complete bds-tag-field JSDoc"
```

---

## Task 9: SCSS

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.scss` (create)

**Acceptance criteria:**

- `bds-tag-field.scss` uses two shared partials: `@use '../_shared/form-field-shell' as *` (container/state) and `@use '../_shared/form-field-elements' as *` (element mixins). No `@use` of the token package directly — tokens come via `injectGlobalPaths`.
- `_form-field-elements.scss` (new shared partial) exports `%field-inline-label` placeholder and seven opt-in mixins: `form-field-sublabel`, `form-field-slot-prefix`, `form-field-control`, `form-field-actions`, `form-field-action`, `form-field-counter`, `form-field-disabled-sublabel`. Each mixin is independently callable so future components (e.g. textarea) include only what they need.
- `bds-tag-field.scss` component-specific rules (not in shared partial): `__container { gap: $boreal-spacing-xs }`, `__control { min-width: var(--bds-tag-field-input-min-width, 80px); flex: 1 }`, `__action--icon-right` non-interactive indicator styles.
- CSS custom property `--bds-tag-field-input-min-width` documented via `@prop` comment above the `.bds-tag-field` selector.
- `__action` button (via `form-field-action` mixin): `&:hover`, `&:focus-visible` (`@include bds-focus-ring`), clear `&--clear` icon sizing. Note: hover/focus states are not specified in Figma designs — defaults use existing tokens and should be reviewed by design before final release.
- `__action--icon-right`: non-interactive — no cursor, hover, or focus styles. Visual affordance only; the parent container owns the click.
- Zero hardcoded pixel values, colors, or font sizes — all values reference `$boreal-*` tokens.
- `pnpm --filter boreal-web-components build` passes with no SCSS errors.

**Manual test:**

Playground scenarios to implement in `packages/boreal-web-components/src/index.html`:

- Scenario 1: `variant="outline"` field at rest, focused, and with `error=true`.
- Scenario 2: `variant="plain"` field at rest and focused.
- Scenario 3: A field with pre-set values exceeding `effectiveMaxVisible` to verify single-row layout.
- Scenario 4: A field with `icon` and `sublabel` set to verify prefix area layout.
- Scenario 5: A field with `clearable`, pre-set values, and `iconRight` to verify action buttons layout and hover states.

Run: `pnpm dev:components` and validate each scenario:

- [ ] Given `variant="outline"` at rest, when the inner input receives focus, then a focus ring and updated border color appear. Pass: visual focus indicator matches the focused token.
- [ ] Given `error=true`, when rendered, then a danger border is applied. Pass: border color matches the error/danger token.
- [ ] Given `variant="plain"`, when rendered at rest, then no border is visible; when focused, a border appears. Pass: border absent at rest, present on focus.
- [ ] Given multiple pre-set values exceeding `effectiveMaxVisible`, then all tags and the input remain on a single row. Pass: container does not grow vertically; no overflow or height increase.
- [ ] Given `icon` and `sublabel` set, when rendered, then the icon and text appear left-aligned inside the container with correct spacing. Pass: `bds-tag-field__sublabel` visible, no overflow.
- [ ] Given `clearable` with values and `iconRight` set, when hovering each action button, then icon color changes to the primary text token. Pass: hover state visible on both buttons.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 add bds-tag-field SCSS styles"
```

---

## Task 10: Unit tests

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-basics.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-events.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-keyboard.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-validation.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-form.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-a11y.spec.ts` (create)

**Test setup note:** Use `newSpecPage` from `@stencil/core/testing`. Register `BdsTagField` in the `components` array. Child custom elements (`bds-tag`, `bds-typography`) are not registered and will render as unknown elements — assert on the tag-field's own output and emitted events, not on the inner DOM of child components. See `.agents/memory/stencil-child-component-props-in-tests.md`.

**Utility discovery — Testing:**

- Feature area: test helpers and spec page setup.
- Candidates found: `utils/testing/` barrel — check for shared spec helpers before adding local utilities.
- Reuse decision: use existing `newSpecPage` and any available event-spy helpers from `@stencil/core/testing`.

**Acceptance criteria per spec file:**

**`bds-tag-field-basics.spec.ts`:**

- Renders with no tags when `values` is empty.
- Renders one `bds-tag` per entry when `values` is pre-populated.
- Renders an overflow `bds-tag` with label `+{N}` when `values.length > effectiveMaxVisible`.
- Input element is absent from the DOM when `maxTags > 0 && values.length >= maxTags`.
- Input `placeholder` is present when `values` is empty, absent when at least one tag exists.
- Adding a value equal to an existing entry is ignored when `allowDuplicates === false`.
- Adding a value equal to an existing entry succeeds when `allowDuplicates === true`.
- Adding a value whose trimmed length exceeds `maxTagLength` is ignored.
- Adding a whitespace-only value is ignored.
- `variant` prop applies the correct BEM modifier class to the host.
- `customWidth` applies `--bds-tag-field-width` to the host style.
- `tagIcon` non-empty: each visible `bds-tag` child contains `<span slot="icon"><i class="{tagIcon}"></i></span>`.
- `tagIcon` empty (default): no `<span slot="icon">` is rendered inside any visible chip.
- Overflow chip never contains `<span slot="icon">` regardless of `tagIcon`.
- `__container` has a direct child div with class `__body`; the `__actions` div is a sibling of `__body` (not nested inside it).

**`bds-tag-field-events.spec.ts`:**

> **Test setup note:** `handleFocusOut` uses `requestAnimationFrame`. Mock it synchronously in `beforeEach` with `global.requestAnimationFrame = (cb: FrameRequestCallback) => { cb(0); return 0; }` and restore in `afterEach`. This ensures RAF callbacks run inline during `focusout` dispatch in JSDOM.

- `bdsTagAdd` fires with `{ value }` when a tag is committed via Enter.
- `bdsTagAdd` fires with `{ value }` when a tag is committed via comma.
- `bdsTagRemove` fires with `{ value }` when a tag's close handler is called.
- `bdsTagRemove` fires for each removed value when the overflow close handler is called.
- `bdsClear` fires with no payload when `handleClearAll` is called.
- `valueChange` fires with the updated `string[]` on every values mutation.
- `bdsFocus` fires with `{ event }` when the input receives focus.
- `bdsBlur` fires with `{ event }` when a `focusout` event is dispatched on the host with `relatedTarget` set to an element outside the component — verify via host `focusout`, not input `blur`.
- `bdsBlur` does NOT fire when `focusout` fires on the host with `relatedTarget` pointing to a descendant of the host (e.g. a mock element appended to the component's DOM).
- `touched` becomes `true` after `focusout` leaves the component entirely.
- `bdsValidationChange` fires after `updateValidity(true)` with correct `{ valid, validity, value, touched, dirty }`.

**`bds-tag-field-keyboard.spec.ts`:**

- Backspace on an empty input removes the last tag from `values`.
- Backspace on a non-empty input does not remove any tag.
- Backspace when `values` is empty does nothing.
- Escape clears the input element value without committing a tag.
- Enter with whitespace-only input does not add a tag and does not emit `bdsTagAdd`.
- Comma key commits the current input text as a new tag.
- Enter key commits the current input text as a new tag.

**`bds-tag-field-validation.spec.ts`:**

- `valueMissing` validator fails when `required === true` and `values` is empty.
- `valueMissing` passes when `required === true` and `values` has at least one entry.
- `rangeOverflow` validator fails when `maxTags > 0` and `values.length > maxTags`.
- `rangeOverflow` passes when `values.length <= maxTags`.
- Custom validator added via `customValidators` is merged with built-in validators and runs on `updateValidity`.
- `validationTiming = 'blur'` triggers `updateValidity(true)` on blur.
- `validationTiming = 'input'` triggers `updateValidity(true)` on each tag commit.
- `validationError` state sets the `--error` BEM modifier class on the host.
- `validationMessage` is displayed in the footer when `validationError` is `true`.
- Explicit `error` prop sets the `--error` class independently of validation state.

**`bds-tag-field-form.spec.ts`:**

- `formResetCallback` sets `values` to `[]`, clears `touched`, `dirty`, `validationError`, `validationMessage`.
- `formStateRestoreCallback` with a valid JSON string restores `values` correctly.
- `formStateRestoreCallback` with invalid JSON defaults `values` to `[]` without throwing.
- `setFormValue` is called with `JSON.stringify(values)` on every `values` mutation.
- `setFormValue` is called with `null` on `formResetCallback`.
- `formDisabledCallback(true)` sets `isDisabled` to `true` (via `formAssociatedMixin`).
- `isDisabled = true` propagates the `disabled` prop to every rendered `bds-tag`.

**`bds-tag-field-a11y.spec.ts`:**

- `aria-invalid="true"` is set on the inner `<input>` when `error === true` or `validationError === true`.
- `aria-invalid` is absent when neither `error` nor `validationError` is true.
- `aria-required="true"` is set on the inner `<input>` when `required === true`.
- `aria-required` is absent when `required === false`.
- Each rendered `bds-tag` receives `closeButtonLabel` equal to `"Remove {value}"`.
- The overflow `bds-tag` receives `closeButtonLabel` equal to `"Remove {N} hidden tags"`.
- `aria-labelledby` on the `<input>` points to the label element `id` when `label !== ''`.
- `aria-describedby` on the `<input>` points to the helper element `id` when footer content is present.

**Manual test:**

Run: `pnpm --filter boreal-web-components test --testPathPattern="bds-tag-field"`.

- [ ] All 6 spec files pass with zero failures.
- [ ] No regressions in `bds-text-field` specs: `pnpm --filter boreal-web-components test --testPathPattern="bds-text-field"`.

**Commit:**

```bash
git commit -m "test(web-components): EOA-13695 add bds-tag-field unit tests"
```

---

## Task 11: Vue output target registration

**Files:**

- `packages/boreal-web-components/targets/vue-output-target.ts` (modify)

**Acceptance criteria:**

- Add `'bds-tag-field'` to the existing `componentModels` group that uses `event: 'valueChange'` and `targetAttr: 'value'` — the same group that contains `'bds-text-field'`, `'bds-toggle'`, `'bds-radio-group'`, `'bds-checkbox-group'`, `'bds-select'`.
- No other changes to `vue-output-target.ts`.
- The `valueChange` event emitted by `bds-tag-field` carries `string[]` — document this in the component JSDoc (already covered in Task 8); the Vue wrapper handles the type transparently.

**Manual test:**

- [ ] `pnpm --filter boreal-web-components build` completes without errors.
- [ ] Generated Vue wrapper file for `bds-tag-field` exists in the output and contains the `modelValue` / `onUpdate:modelValue` binding.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 register bds-tag-field in Vue output target componentModels"
```

---

## Task 12: Storybook story and MDX documentation

**Files:**

- `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.stories.ts` (create)
- `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.mdx` (create)

**Acceptance criteria — stories:**

- Follow the pattern of `bds-text-field.stories.ts` for structure, arg types, and render helpers.
- All stories render with explicit `values` to make them statically reviewable in Chromatic.

Required stories (16 total):

| Story                    | Props/slots demonstrated                                                                   | Playground origin |
| ------------------------ | ------------------------------------------------------------------------------------------ | ----------------- |
| `Default`                | Empty field, no tags                                                                       | Scenario 1        |
| `WithLabel`              | `label`, `helperText`, `placeholder`                                                       | Scenario 1        |
| `WithHelperText`         | `helperText` footer in isolation                                                           | Scenario 1        |
| `WithSublabel`           | `sublabel` inline inside the body                                                          | Scenarios 5, 6, 8 |
| `Plain`                  | `variant="plain"`                                                                          | —                 |
| `WithIcon`               | `icon` (left field icon, e.g. `bds-icon-search`)                                           | Scenarios 5, 6    |
| `WithPrefixSlot`         | `slot="prefix"` with slotted content (e.g. `bds-status`)                                   | Scenarios 5, 8    |
| `WithTagIcon`            | `tagIcon` + `tagColor` with pre-set values                                                 | Scenario 8        |
| `WithTagColor`           | `tagColor` alone (no `tagIcon`) with pre-set values                                        | Scenario 8        |
| `WithMaxTags`            | `maxTags=4`, `maxVisibleTags=3`, tag counter in footer                                     | Scenario 1        |
| `WithOverflow`           | 5 pre-set values, `maxVisibleTags=3` → `+2` badge visible on load                          | Scenario 3        |
| `Clearable`              | `clearable=true` with pre-set values                                                       | Scenario 4        |
| `Required`               | `required=true`, blur triggers validation                                                  | Scenario 2        |
| `Error`                  | `error=true` with `errorMessage`                                                           | —                 |
| `Disabled`               | `disabled=true` with pre-set values                                                        | —                 |
| `InteractiveFormExample` | Native `<form>` with submit + reset; code snippet shows `JSON.parse(formData.get('name'))` | —                 |

Notes:

- `WithIconRight` is **not** included as a standalone story — `iconRight` only makes semantic sense when `bds-tag-field` is embedded inside a `bds-select` multiselect (the chevron signals a dropdown). That integration is out of scope (separate ticket). Document the prop in the MDX table but do not publish a story that shows a chevron with no action.
- `WithPrefixSlot` requires a custom render function (slot content is not expressible as a control arg); use a `slotPrefix` boolean arg like `bds-text-field` does for its `WithIcon` story.
- `WithTagIcon` and `WithTagColor` stay as separate stories so Chromatic captures each prop independently.
- `WithOverflow` must have `values` pre-set to 5 entries with `maxVisibleTags=3` so the `+2` overflow chip is immediately visible without interaction.
- `WithMaxTags` story includes the tag counter in the footer (`maxTags > 0`).
- `InteractiveFormExample`: the JSON serialization of `values` is non-obvious to consumers (`FormData.get('tags')` returns `'["React","Vue"]'`). The story must show `JSON.parse(formData.get('name'))` in the code snippet panel and demonstrate that form reset clears all chips via `formResetCallback`. Follow the `<form-demo>` wrapper pattern from `bds-text-field.stories.ts`.

**Acceptance criteria — MDX:**

- Follows the two-type documentation pattern used for other form components.
- Documents: component purpose, all props (table), all events (table), keyboard interactions, form integration note (JSON serialisation), Vue `v-model` usage.
- Includes a "How to use" section showing how to set `maxTags`, `maxVisibleTags`, and `maxTagLength` together.
- Documents the `tagIcon` and `tagColor` props added post-plan, including the note that per-tag icon/color (rich value type) is deferred to v2.

**Manual test:**

Run: `pnpm dev:docs`.

- [ ] Given the docs app loaded, when navigating to the `bds-tag-field` stories page, then all 16 stories render without console errors. Pass: no errors in the browser console.
- [ ] Given the `WithOverflow` story, when the page loads, then 3 visible tags and a `+2` overflow tag are immediately visible without interaction. Pass: overflow badge present on initial render.
- [ ] Given the `WithTagIcon` story, then each visible chip contains the icon element. Pass: icon visible inside every chip.
- [ ] Given the `WithPrefixSlot` story, then the slotted prefix content renders inside the body before the chips. Pass: prefix content visible.
- [ ] Given the `InteractiveFormExample` story, when Submit is clicked, then the output panel shows the parsed `values` array (not the raw JSON string). Pass: array logged correctly. When Reset is clicked, all chips are removed. Pass: field is empty after reset.
- [ ] Given the MDX documentation page, when loaded, then all props and events tables are populated. Pass: no empty or missing rows in the tables.

**Commit:**

```bash
git commit -m "docs(docs): EOA-13695 add bds-tag-field Storybook stories and MDX documentation"
```

---

## Out of scope (follow-up tickets)

- **`bds-text-field` migration:** adopt `useFormField<T>()`, `renderFieldParts`, `IFormFieldProps`, `FIELD_VARIANTS`, and `FIELD_VALIDATION_TIMING` from `components/forms/common/`. Until then, `TEXT_FIELD_VARIANTS` / `TEXT_FIELD_VALIDATION_TIMING` in `bds-text-field/types/enum.ts` are known intentional duplicates of the values declared in `common/form-field-types.ts`.
- Extend `bds-select` to multiselect using `bds-tag-field` — separate ticket. The `iconRight` prop (e.g. `bds-icon-chevron-down`) is designed for this integration: when `bds-tag-field` is embedded inside `bds-select`, the chevron signals the dropdown trigger. A standalone `WithIconRight` Storybook story is intentionally omitted until this integration exists; the prop is documented in the MDX props table only.
- Arrow-key navigation between rendered `bds-tag` chips via `KeyboardController.setLinearNavigation`.
- Per-tag color and icon via a rich value type (`TagFieldValue[]` replacing `string[]`) — would be a breaking API change; deferred to v2 since the library is in alpha with no consumers yet. For now, uniform color is covered by `tagColor` and uniform icon by `tagIcon`.
- Autocomplete / suggestions dropdown.
- Async tag resolution.
- `ResizeObserver`-based auto-detection of visible tags (replaces the `maxVisibleTags` prop in a future enhancement).

---

## Addendum: Suffix slot (prerequisite for bds-select multiselect)

> This work was not in the original plan. It emerged from the architecture discussion in `ai-work/research/bds-select-multiselect-extension.md` and is a direct parallel to Task 3 of `ai-work/plans/EOA-13696-bds-text-field-refactor.md`.

The `bds-select[multiselect]` integration (separate ticket) requires injecting badge and spinner elements into `bds-tag-field`'s right side. The structural enabler is a `<slot name="suffix">` placed as a **sibling to the actions div** in the container — the same pattern added to `bds-text-field` in EOA-13696.

Badge and spinner are independent, not mutually exclusive: a user can have 3 items selected (badge = "3") while options are still loading (spinner visible). `bds-select[multiselect]` manages both via a single wrapper injected into the slot.

### Files

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify — insert `<slot name="suffix" />` in render tree; update class-level JSDoc)
- `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-basics.spec.ts` (modify — add 4 suffix slot tests)
- `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.mdx` (modify — add suffix slot to slots table/section)

### What changes in `bds-tag-field.tsx`

Add `<slot name="suffix" />` as a sibling of `__body` and `{renderFieldActions(...)}` in the container render tree — no changes to the `renderFieldActions` call itself:

```tsx
<div class="bds-tag-field__container">
  <div class="bds-tag-field__body">
    {renderFieldSublabel(...)}
    <slot name="prefix" />
    {/* visible chips */}
    {/* overflow chip */}
    <input class="bds-tag-field__control" ... />
  </div>
  <slot name="suffix" />               {/* ← new; sibling to __body AND __actions */}
  {renderFieldActions(...)}            {/* unchanged; remains conditional */}
</div>
```

Update the class-level JSDoc:

```typescript
/**
 * @slot prefix  - Inline content rendered after the icon/sublabel area, before the input.
 * @slot suffix  - Inline content rendered between the input and the built-in action buttons
 *                 (clear, icon-right). Always present in the render tree as an independent
 *                 sibling to the actions area. Intended for single-line elements such as
 *                 badges or loading indicators injected by composite parent components
 *                 (e.g. bds-select[multiselect]).
 */
```

### SCSS

N/A — the suffix slot is a pass-through projection point. No selector is needed inside `bds-tag-field.scss`; the injecting parent (`bds-select`) owns the visual treatment of its injected content.

### MDX update

In `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.mdx`, add a row to the slots reference table:

| Slot     | Description                                                                                                                                                                                                                                                             |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `suffix` | Inline content rendered between the input and the built-in action buttons. Always present in the DOM as an independent sibling to the actions area. Intended for badges or loading indicators injected by composite parent components (e.g. `bds-select[multiselect]`). |

No new Storybook story is needed — the slot is injection-only (same rationale as the `WithIconRight` story omission in Task 12: it only makes semantic sense inside a composite parent).

### Manual test

Playground scenarios in `packages/boreal-web-components/src/index.html`:

- **Scenario 1:** A tag field with `clearable=false`, no `iconRight`, and an empty `values` array (so the actions div is absent). Verify the suffix slot placeholder is still present in the DOM.
  - Pass: `.bds-tag-field__container` has a direct `slot[name="suffix"]` child even though `.bds-tag-field__actions` is not rendered.

- **Scenario 2:** A tag field with `clearable=true` and pre-set values, plus `<span slot="suffix">3</span>` injected as a child. Verify the badge renders to the left of the clear button.
  - Pass: "3" is visible and precedes the clear button in DOM order.

### Unit tests to add (`bds-tag-field-basics.spec.ts`)

- `<slot name="suffix">` is present in `.bds-tag-field__container` regardless of `clearable`, `values`, and `iconRight` combinations — including when no `.bds-tag-field__actions` div is rendered.
- A `<span slot="suffix">` child renders as a sibling of `.bds-tag-field__body` (not nested inside it) and as a sibling of `.bds-tag-field__actions`.
- In DOM order, the suffix slot node appears before `.bds-tag-field__actions` when both are present.
- Existing tests that assert `.bds-tag-field__actions` is absent when `clearable=false`, `values=[]`, and `iconRight=''` remain valid and require no changes.

### Commit

```bash
git commit -m "feat(web-components): EOA-13695 add suffix slot to bds-tag-field for multiselect integration"
```

---

## Addendum: FormData multiple-entries form submission

> This improvement emerged from the `bds-select[multiselect]` form integration session. The form output for a standalone `bds-tag-field` currently produces `{ "tags": "[\"react\",\"vue\"]" }` — a JSON-serialised string that requires explicit parsing on the consumer side.

**Goal:** Align `bds-tag-field` with native `<select multiple>` semantics so each selected value submits as a separate `FormData` entry. `formData.getAll('tags')` then returns `['react', 'vue']` natively — no parsing required.

**This is a breaking change.** Consumers currently doing `JSON.parse(formData.get('tags'))` will receive `JSON.parse('react')` (first entry only) which throws a `SyntaxError`. A minor version bump and changelog entry are required when shipping this change.

---

### Files to change

| File                                                                                  | Change                                                                |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `packages/boreal-web-components/src/utils/form/internals.ts`                          | Widen `setFormValue` parameter type                                   |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` | `onValueChange`, `formAssociatedCallback`, `formStateRestoreCallback` |
| `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.stories.ts`           | `InteractiveFormExample` code snippet, `value` argType description    |

---

### 1. Widen `setFormValue` utility (`utils/form/internals.ts`)

The current signature only accepts `FormDataEntryValue | null` (`string | File | null`). The native `ElementInternals.setFormValue()` spec accepts `File | string | FormData | null`. Widen to match:

```typescript
// before
export function setFormValue(internals: ElementInternals, value: FormDataEntryValue | null): void {

// after
export function setFormValue(internals: ElementInternals, value: File | string | FormData | null): void {
```

No logic change — the implementation `internals.setFormValue?.(value)` already works for all four types.

---

### 2. Update `bds-tag-field.tsx`

**`onValueChange`** — build a `FormData` instead of `JSON.stringify`:

```typescript
@Watch('value')
onValueChange(next: string[]): void {
  const fd = new FormData();
  next.forEach(v => fd.append(this.name, v));
  setFormValue(this.internals, next.length > 0 ? fd : null);
  this._field.updateValidity(this.touched || this.validationError);
  this.valueChange.emit(next);
}
```

Empty array passes `null` (field absent from `FormData`) — matches native `<select multiple>` with nothing selected.

**`formAssociatedCallback`**:

```typescript
formAssociatedCallback(): void {
  const fd = new FormData();
  this.value.forEach(v => fd.append(this.name, v));
  this._field.formAssociatedCallback(this.value.length > 0 ? fd : null);
}
```

**`formStateRestoreCallback`** — add an `instanceof FormData` guard for browser session restore (old JSON state vs. new FormData state):

```typescript
formStateRestoreCallback(state: unknown, _mode: string): void {
  if (state instanceof FormData) {
    this.value = [...state.getAll(this.name)] as string[];
  } else {
    try {
      this.value = JSON.parse(state as string) as string[];
    } catch {
      this.value = [];
    }
  }
  const fd = new FormData();
  this.value.forEach(v => fd.append(this.name, v));
  setFormValue(this.internals, this.value.length > 0 ? fd : null);
  this._field.updateValidity();
}
```

The `JSON.parse` fallback handles any previously browser-cached state from before this change.

Also update the JSDoc on the `value` prop — remove the `JSON.stringify` note and replace it with the `getAll()` pattern:

```typescript
/**
 * The current list of tag values. Each entry is submitted as a separate `FormData` entry
 * under the component's `name` — use `formData.getAll(name)` to recover the full array.
 * An empty array contributes no entry (field absent from `FormData`).
 */
```

---

### 3. Update `bds-tag-field.stories.ts`

**`value` argType description** — remove the `JSON.stringify` sentence:

```typescript
description: 'The current list of tag values.',
```

**`InteractiveFormExample` code snippet** — replace `JSON.parse(formData.get(...))` with `formData.getAll(...)`:

````javascript
// Read tags from FormData after submit
form.addEventListener('submit', (event) => {
  if (event.defaultPrevented) return;
  event.preventDefault();

  const formData = new FormData(form);

  // Each tag submits as a separate entry — use getAll(), not get()
  const tags = formData.getAll('tags'); // → ['React', 'Vue', 'Stencil']

  console.log('Submitted tags:', tags);
});
```j

Also update the story JSDoc comment above `InteractiveFormExample`:

```typescript
/**
 * Interactive form demonstrating `bds-tag-field` inside a native HTML form.
 * Each tag value is submitted as a separate `FormData` entry — use
 * `formData.getAll(name)` to recover the full array.
 * Resetting the form clears all chips via `formResetCallback`.
 */
````

---

### Unit tests to update (`bds-tag-field-form.spec.ts`)

These assertions must change:

- `setFormValue` is called with a `FormData` containing each value on `values` mutation (not `JSON.stringify`).
- `setFormValue` is called with `null` (not `JSON.stringify([])`) when `values` is empty.
- `setFormValue` is called with `null` on `formResetCallback`.
- `formStateRestoreCallback` with a `FormData` instance restores `values` correctly.
- `formStateRestoreCallback` with a legacy JSON string still restores `values` correctly (backward-compat guard).

---

### Commit

```bash
git commit -m "feat(web-components): EOA-13695 use FormData multiple-entries for bds-tag-field form submission"
```
