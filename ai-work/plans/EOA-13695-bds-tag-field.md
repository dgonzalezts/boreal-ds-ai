# `bds-tag-field` Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement `bds-tag-field`, a form-associated Stencil component that lets users enter and remove multiple discrete string values as tag chips inside a fixed-height single-row container, visually consistent with `bds-text-field`.

**Architecture:** Standalone new component — not an extension of `bds-text-field`. Shared form-field logic is extracted into a new `useFormField<T>()` factory in `utils/form/field-form-association.ts` (following the `useFormCheckbox` precedent); shared JSX render helpers go into `components/forms/common/`; shared SCSS container rules go into `components/forms/_shared/_form-field-shell.scss`. `bds-text-field` is **not modified in this PR** — the shared utilities are built for `bds-tag-field` first and will be adopted by `bds-text-field` in a follow-up ticket.

**Tech Stack:** Stencil v4, TypeScript, SCSS with `$boreal-*` design tokens, `KeyboardController` (`utils/a11y/keyboard`), `formAssociatedMixin` (`mixins/`), `runValidators` + `setFormValue` (`utils/form/internals`), `bds-tag` (existing feedback component), `bds-typography` (existing component).

---

## Files to create / modify

| File                                                                                                          | Notes                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/utils/form/field-form-association.ts`                                     | New — `useFormField<T>()` factory, `IFormFieldHost<T>` interface                                                                    |
| `packages/boreal-web-components/src/utils/form/index.ts`                                                      | Modify — add `export * from './field-form-association'`                                                                             |
| `packages/boreal-web-components/src/components/forms/_shared/_form-field-shell.scss`                          | New — shared SCSS partial: container shell, focus ring, error/disabled/plain/outline states                                         |
| `packages/boreal-web-components/src/components/forms/common/form-field-types.ts`                              | New — `FIELD_VARIANTS`, `FIELD_VALIDATION_TIMING` enums, `FieldVariant`, `FieldValidationTiming` types, `IFormFieldProps` interface |
| `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx`                             | New — `renderFieldLabel`, `renderFieldFooter`, `deriveFieldRenderState`                                                             |
| `packages/boreal-web-components/src/components/forms/common/index.ts`                                         | New — barrel export for `common/`                                                                                                   |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/ITagField.ts`                        | New — extends `IFormFieldProps`, declares only 6 tag-specific props                                                                 |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/enum.ts`                             | New — re-exports `FIELD_VARIANTS as TAG_FIELD_VARIANTS`, `FIELD_VALIDATION_TIMING as TAG_FIELD_VALIDATION_TIMING` from `common/`    |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/types.ts`                            | New — type aliases `TagFieldVariant = FieldVariant`, `TagFieldValidationTiming = FieldValidationTiming`                             |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/types/index.ts`                            | New — types barrel                                                                                                                  |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx`                         | New — component implementation                                                                                                      |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.scss`                        | New — component styles                                                                                                              |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-basics.spec.ts`     | New — rendering and tag management tests                                                                                            |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-events.spec.ts`     | New — event emission tests                                                                                                          |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-keyboard.spec.ts`   | New — keyboard interaction tests                                                                                                    |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-validation.spec.ts` | New — built-in and custom validator tests                                                                                           |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-form.spec.ts`       | New — FACE lifecycle tests                                                                                                          |
| `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-a11y.spec.ts`       | New — accessibility attribute tests                                                                                                 |
| `packages/boreal-web-components/targets/vue-output-target.ts`                                                 | Modify — add `bds-tag-field` to `componentModels`                                                                                   |
| `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.stories.ts`                                   | New — Storybook stories                                                                                                             |
| `apps/boreal-docs/src/stories/forms/bds-tag-field/bds-tag-field.mdx`                                          | New — MDX documentation page                                                                                                        |

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

Run: `pnpm dev:components` from monorepo root, then use `packages/boreal-web-components/src/index.html` as the playground (restart required — Stencil does not hot-reload).

- [ ] Add `<bds-tag-field></bds-tag-field>` inside the `<body>` of `packages/boreal-web-components/src/index.html`.
- [ ] Open the playground page and verify `bds-tag-field` is registered and renders without console errors.
- [ ] No TypeScript compilation errors in the terminal.

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

Run: `pnpm dev:components` and validate in `packages/boreal-web-components/src/index.html`.

- [ ] Update the playground markup to include one `<bds-tag-field>` instance and interact with it in the browser.
- [ ] No new console errors after this change.
- [ ] `pnpm --filter boreal-web-components tsc --noEmit` passes.

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

Run: `pnpm dev:components` and validate in `packages/boreal-web-components/src/index.html`.

- [ ] In the playground, set complex props via script or browser console when needed (for example: `values`, `maxTags`, `maxVisibleTags`) to validate overflow and counter scenarios.

- [ ] Empty field renders with label, empty container, placeholder text.
- [ ] Typing a value and pressing Enter adds a tag chip; input clears.
- [ ] Tag chip shows close button; clicking it removes the tag.
- [ ] With `maxTags=4` and 4 values, `effectiveMaxVisible=3` renders 3 chips + `+1` overflow chip with close button.
- [ ] Clicking `+1` close button removes the overflow tag only.
- [ ] `clearable=true` shows clear-all button when tags present; clicking empties all tags.
- [ ] `maxTags=3` counter shows `{n}/3` in footer.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-13695 implement bds-tag-field full render tree"
```

---

## Task 8: JSDoc audit

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (modify)

**Acceptance criteria:**

- Class-level JSDoc block:
  - **Component description**: The first paragraph describes the component's purpose and behavior, concise and clear.
  - **@slot tags**: Only if the component exposes slots (none for this component, so omit).
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

- File starts with `@use '../_shared/form-field-shell' as *;` then `@include form-field-shell('bds-tag-field');`. No `@use` of the token package directly — tokens come via injectGlobalPaths. No leading comment block.
- The `@use` of the shared partial pulls in the container, focus ring, error/disabled/plain/outline variant rules. Do not duplicate those rules locally.
- Container (`.bds-tag-field__container`): `display: flex`, `flex-wrap: nowrap`, `overflow: hidden`, `align-items: center`, `gap: $boreal-spacing-2xs`, `padding: $boreal-spacing-1xs`, `min-height: $boreal-layout-l` (not fixed height — min-height allows the container to match text-field height when empty while staying single-row).
- Input (`.bds-tag-field__control`): `min-width: 80px`, `flex: 1`, `border: none`, `outline: none`, `background: transparent`, `font-size: $boreal-typography-font-size-sm`, `font-weight: $boreal-typography-font-weight-regular`, `line-height: $boreal-typography-line-height-sm`.
- Actions (`.bds-tag-field__actions`): `display: flex`, `align-items: center`, `gap: $boreal-spacing-3xs`, `margin-left: auto`, `flex-shrink: 0`.
- Tag count (`.bds-tag-field__tag-count`): `font-size: $boreal-typography-font-size-xs`, `color: $boreal-text-secondary`, `white-space: nowrap`.
- Host custom property: `--bds-tag-field-width` with fallback `100%`.
- Zero hardcoded pixel values, colors, or font sizes — all values reference `$boreal-*` tokens.

**Manual test:**

Run: `pnpm dev:components` and validate in `packages/boreal-web-components/src/index.html`.

- [ ] `outline` variant: border visible at rest, blue focus ring on focus, red border in error state, dimmed background when disabled.
- [ ] `plain` variant: no border at rest, border and focus ring on focus.
- [ ] Tags and input sit on a single row; container does not grow vertically when overflow tags are present.
- [ ] Side-by-side playground check confirms `bds-text-field` remains visually unchanged (regression check — the SCSS partial is new, text-field is untouched).

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

**`bds-tag-field-events.spec.ts`:**

- `bdsTagAdd` fires with `{ value }` when a tag is committed via Enter.
- `bdsTagAdd` fires with `{ value }` when a tag is committed via comma.
- `bdsTagRemove` fires with `{ value }` when a tag's close handler is called.
- `bdsTagRemove` fires for each removed value when the overflow close handler is called.
- `bdsClear` fires with no payload when `handleClearAll` is called.
- `valueChange` fires with the updated `string[]` on every values mutation.
- `bdsFocus` fires with `{ event }` when the input receives focus.
- `bdsBlur` fires with `{ event }` when focus leaves the component entirely.
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
- Required stories: `Default`, `WithLabel`, `Plain` (variant), `WithMaxTags` (`maxTags=4`, `maxVisibleTags=3`), `WithOverflow` (pre-populated to show `+N` badge), `Disabled`, `Error`, `Required`, `Clearable`.
- `WithMaxTags` story includes the tag counter in the footer (`maxTags > 0`).
- `WithOverflow` story has `values` pre-set to 5 entries with `maxVisibleTags=3` so the `+2` overflow tag is immediately visible without interaction.
- All stories render with explicit `values` to make them statically reviewable in Chromatic.

**Acceptance criteria — MDX:**

- Follows the two-type documentation pattern used for other form components.
- Documents: component purpose, all props (table), all events (table), keyboard interactions, form integration note (JSON serialisation), Vue `v-model` usage.
- Includes a "How to use" section showing how to set `maxTags`, `maxVisibleTags`, and `maxTagLength` together.

**Manual test:**

Run: `pnpm dev:docs`.

- [ ] All stories render in Storybook without console errors.
- [ ] `WithOverflow` story shows 3 visible tags + `+2` overflow tag immediately on load.
- [ ] MDX page loads and all props/events tables are correctly populated.
- [ ] Restart the dev server if stories do not appear — Stencil does not hot-reload.

**Commit:**

```bash
git commit -m "docs(docs): EOA-13695 add bds-tag-field Storybook stories and MDX documentation"
```

---

## Out of scope (follow-up tickets)

- **`bds-text-field` migration:** adopt `useFormField<T>()`, `renderFieldParts`, `IFormFieldProps`, `FIELD_VARIANTS`, and `FIELD_VALIDATION_TIMING` from `components/forms/common/`. Until then, `TEXT_FIELD_VARIANTS` / `TEXT_FIELD_VALIDATION_TIMING` in `bds-text-field/types/enum.ts` are known intentional duplicates of the values declared in `common/form-field-types.ts`.
- Extend `bds-select` to multiselect using `bds-tag-field` — separate ticket.
- Arrow-key navigation between rendered `bds-tag` chips via `KeyboardController.setLinearNavigation`.
- Per-tag color via a `tagColors: Record<string, TagColor>` prop.
- Autocomplete / suggestions dropdown.
- Async tag resolution.
- `ResizeObserver`-based auto-detection of visible tags (replaces the `maxVisibleTags` prop in a future enhancement).
