---
ticket: EOA-10057
component: bds-text-field
status: in progress
---

# bds-text-field — Full Implementation Plan

## Context

The form-association infrastructure (Phase 1 of EOA-10099) is complete and verified. `bds-text-field` is the first full form control built on top of it. The component logic skeleton is complete at `packages/boreal-web-components/src/components/forms/bds-text-field/` — all props, events, watches, and FACE lifecycle callbacks are in place. The remaining work covers styling (Tasks 3–5), unit tests (Task 6), and Storybook documentation (Task 7).

---

## Reference Analysis — Colibri vs Aqua

### Architecture Comparison

| Concern                   | col-text-field (Lit/Colibri)                                                 | aq-text-field (Stencil/Aqua)                   | Boreal Approach                                                                                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Framework                 | Lit with deep inheritance                                                    | Stencil flat component                         | Stencil + mixin composition, `scoped: true` (no shadow DOM)                                                                                                        |
| Form association          | `InputFormComponent` base                                                    | Manual `@Element` + prop                       | `formAssociatedMixin` + `@AttachInternals()` ✅ done. `name`/`disabled`/`required` declared on component class (not from mixin)                                    |
| Validation control        | `validationTiming` prop (blur/input/change/submit)                           | `isError` prop only (external)                 | `ValidationTiming` type already exists in `src/types/form.ts`                                                                                                      |
| Validation state tracking | `valid`, `touched`, `dirty`, `focused` states                                | `isError`, `hasFocus` states                   | Must add `touched`, `dirty`, `focused`, `valid` as `@State` on component                                                                                           |
| Built-in validators       | `validate()` abstract method + browser checkValidity                         | External only                                  | `IFormValidator[]` pattern (`customValidators` prop already exists); add `required` + `minLength` built-ins                                                        |
| Password toggle           | `inputType: 'text' \| 'password'` + subclass                                 | `type` prop + `localType` state + toggle icon  | `type` prop + `showPassword` state on component                                                                                                                    |
| Clear button              | `TextInputBase._supportsClearing`, `_handleClear()`                          | `hasClear` + `showClearOnHover` props          | `clearable` + `clearOnHover` props — no `has`/`show` prefix                                                                                                        |
| Disclosure                | Not in col-text-field                                                        | `hasDisclosure` + `clickDisclosure` event      | `disclosure` prop + `bdsDisclosure` event                                                                                                                          |
| Sublabel/icon             | Separate `<slot name="sub-label">`                                           | `sublabel` + `icon` props inside container     | `sublabel` prop (inside container, like aqua)                                                                                                                      |
| Label                     | Slot                                                                         | `label` prop via `aq-label` component          | `label` prop; rendered via `bds-typography` with optional `info` tooltip                                                                                           |
| Helper text               | `<slot name="helper-text">`                                                  | `helperText` prop + `aq-helper-text` component | `helperText` prop                                                                                                                                                  |
| Prefix/suffix             | `<slot name="prefix">` / `<slot name="suffix">`                              | `left-content` slot / icon-based right         | `<slot name="prefix">` / `<slot name="suffix">` (colibri model, more flexible)                                                                                     |
| Error message             | `errorMessage` prop                                                          | External (just `isError` flag)                 | `errorMessage` prop (replaces helper text when `error=true`)                                                                                                       |
| Custom width              | `customWidth` prop → `--input-width` CSS var                                 | `width: 100%` always                           | `customWidth` prop → `--bds-text-field-width` CSS custom property                                                                                                  |
| Character counter         | `charCount` in `InputFormComponent`                                          | `charCounter` + `maxLength` props              | `charCount: number` (max chars), `counter: boolean` (toggle display) — verified via Figma MCP                                                                      |
| Textarea                  | Not in col-text-field                                                        | `isTextarea` prop                              | **Explicitly out of scope**                                                                                                                                        |
| Tooltip/info              | Not present                                                                  | `info` + `tooltipWidth` props                  | `info: string` prop — rendered via `bds-typography`'s `tooltipText` prop on the label. Gated on that feature being merged; include prop now, render conditionally. |
| Variant                   | colibri `InputFormComponent` has `variant`                                   | `isPlain` boolean                              | `variant: 'outline' \| 'plain'` — string enum, consistent with `bds-button` API                                                                                    |
| Autocomplete              | Not present                                                                  | `autocomplete` prop                            | Include as `autocomplete` prop                                                                                                                                     |
| Max length                | Not present                                                                  | `maxLength` prop                               | Include as `maxLength` prop (browser native, no counter UI)                                                                                                        |
| Events — value            | `input`, `change` native re-emitted                                          | `input`, `change` via `emitEvent` helper       | `bdsInput` (`{ value, event }`), `bdsChange` (`{ value, event }`)                                                                                                  |
| Events — focus            | `focus`, `blur` native                                                       | `focus`, `blur` via `emitEvent`                | `bdsFocus`, `bdsBlur`                                                                                                                                              |
| Events — keyboard         | `keydown`, `keyup` custom with modifiers                                     | Not present                                    | **Deferred** (not needed for form functionality)                                                                                                                   |
| Events — paste            | `paste` custom with clipboardData                                            | Not present                                    | **Deferred**                                                                                                                                                       |
| Events — clear            | `input-cleared`                                                              | `clear` EventEmitter                           | `bdsClear`                                                                                                                                                         |
| Events — validation       | `validation-change` with full validity detail                                | Not present                                    | `bdsValidationChange` (`{ valid, validity, value, touched, dirty }`)                                                                                               |
| Events — disclosure       | Not present                                                                  | `clickDisclosure` EventEmitter                 | `bdsDisclosure`                                                                                                                                                    |
| ARIA                      | Full: `aria-labelledby`, `aria-describedby`, `aria-invalid`, `aria-required` | Basic via `aq-label`                           | Full ARIA pattern (colibri model)                                                                                                                                  |

### DOM Structure Decision

**No shadow DOM** — component uses `scoped: true` (Stencil attribute-based CSS scoping, light DOM). This means `bds-typography` can safely be composed inside the label row without cross-shadow styling issues, and `<slot>` elements work in scoped mode.

`<Host>` is the outer wrapper (IS the `<bds-text-field>` element — no extra node). The inner container uses CSS Grid (`auto auto 1fr auto`) to prevent text overflow under action buttons. No `_updateInputPadding` JS method is needed; `min-width: 0` on the input cell enforces truncation at the layout level.

```javascript
  <Host>                               ← .bds-text-field (IS the element, no extra node)
    <div label-row>                    ← .bds-text-field__label-row
      <bds-typography variant="label"  ← renders label text + optional tooltip icon
        tooltipText={info}>            ← info prop wired here; renders when bds-typography tooltipText merges
      </bds-typography>
    </div>
    <div container>                    ← .bds-text-field__container  [CSS Grid: auto auto 1fr auto]
      <span sublabel>                  ← .bds-text-field__sublabel   [if sublabel prop set]
      <div prefix>                     ← .bds-text-field__prefix     [slot="prefix"]
      <input>                          ← .bds-text-field__control    [min-width: 0 — critical]
      <div right-actions>              ← .bds-text-field__actions
        [clear button — if clearable or clearOnHover]
        [password toggle — if type="password"]
        [disclosure icon — if disclosure]
        <slot name="suffix">
      </div>
    </div>
    <div footer>                       ← .bds-text-field__footer
      <span helper-or-error>           ← .bds-text-field__helper or .bds-text-field__error
                                        [error replaces helper when error=true; helperText returns on clear]
      <span char-count>                ← .bds-text-field__char-count  [if counter=true: "45/120", always visible]
    </div>
```

### Props Surface for bds-text-field

**Must be declared directly on the component class** (mixin no longer provides these — Stencil's static analysis requires `@Prop`/`@State` on the class body):

- `@Prop({ reflect: true }) readonly name: string`
- `@Prop({ reflect: true }) readonly disabled: boolean = false`
- `@Prop({ reflect: true }) readonly required: boolean = false`
- `@State() private isDisabled: boolean = false`
- `@Watch('disabled') onDisabledChange(next: boolean): void { this.isDisabled = next; }`

**From existing skeleton (keep as-is):**

- `value: string` — mutable, reflected
- `error: boolean` — reflected
- `customValidators: IFormValidator[]`

**New props to add:**

- `type: TextFieldType` — `'text' | 'password'` (default: `'text'`)
- `placeholder: string` (default: `''`)
- `readOnly: boolean` (default: `false`)
- `pattern: string` (optional)
- `minLength: number` (optional)
- `maxLength: number` (optional)
- `autocomplete: string` (default: `'off'`)
- `label: string` (default: `''`)
- `sublabel: string` (default: `''`)
- `helperText: string` (default: `''`)
- `errorMessage: string` (default: `''`)
- `clearable: boolean` (default: `false`) — shows clear button when value is present
- `clearOnHover: boolean` (default: `false`) — clear button visible only on hover (implies clearable)
- `disclosure: boolean` (default: `false`) — shows disclosure icon in right actions
- `validationTiming: ValidationTiming` (default: `'blur'`) — from `src/types/form.ts`
- `variant: TextFieldVariant` — `'outline' | 'plain'` (default: `'outline'`) — plain hides idle border
- `info: string` (default: `''`) — tooltip content; wired to `bds-typography` `tooltipText` prop on the label row
- `customWidth: string` (optional) — reflects as `--bds-text-field-width` CSS custom property
- `charCount: number` (optional) — max character count (e.g. `120` → shows `45/120` in footer)
- `counter: boolean` (default: `false`) — enables char counter display (requires `charCount` to be set)

**Internal states to add:**

- `@State() private isDisabled: boolean = false` — mirrors `disabled` prop; also set by `formDisabledCallback` via mixin
- `@State() private showPassword: boolean` — toggles password visibility
- `@State() private isFocused: boolean` — drives focus-within container styling
- `@State() private touched: boolean` — set true on first blur
- `@State() private dirty: boolean` — true when value differs from initial
- `@State() private currentCharCount: number` — current input length (updated on input)

---

## Implementation Tasks (ordered)

### Task 1 — ✅ Expand types: ITextField, enums, types.ts

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-text-field/types/ITextField.ts`
- `packages/boreal-web-components/src/components/forms/bds-text-field/types/enum.ts`
- `packages/boreal-web-components/src/components/forms/bds-text-field/types/types.ts`

Defined:

- `TEXT_FIELD_TYPES` → `TextFieldType`: `'text' | 'password'`
- `TEXT_FIELD_VARIANTS` → `TextFieldVariant`: `'outline' | 'plain'`
- `TEXT_FIELD_VALIDATION_TIMING` → `TextFieldValidationTiming`: `'blur' | 'change' | 'input' | 'submit'` (component-local; `'change'` added to match Colibri — fires only when value changed on blur, unlike `'blur'` which fires on every focus loss)
- `ITextField` expanded with all props

Note: `ValidationTiming` was removed from `@/types/form.ts`; validation timing is now owned by each form component via its own enum.

### Task 2a — ✅ Prop/State/Event surface + scoped: true

**File:** `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`

Completed:

- `scoped: true` added to `@Component`
- Form props declared on class body: `name`, `disabled`, `required`; `@State() isDisabled`; `@Watch('disabled') onDisabledChange`
- All 20 `@Prop()` declarations with JSDoc
- `@State() focused` (drives `--focused` CSS modifier; `showPassword`, `touched`, `dirty`, `currentCharCount` deferred to 2b)
- 8 `@Event()` declarations with JSDoc
- `checkPropValues()` with stacked `@Watch('type')`, `@Watch('variant')`, `@Watch('validationTiming')` — validates all three enum props
- `componentWillLoad()` calls `checkPropValues()` to guard invalid initial attributes
- `getClassMap()` private method returns `StyleModifiers` (expanded in 2c)
- `getHostStyle()` private method returns `--bds-text-field-width` CSS custom property or `undefined`
- Class JSDoc updated with `@summary`, `@slot`, `@attr`, `@property`, `@fires`, `@cssprop`

### Task 2b — Business logic: events, validation, password, clear, disclosure

**File:** `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`

- Add `@State()`: `showPassword`, `touched`, `dirty`, `currentCharCount`
- Add `createId()` call inside the existing `componentWillLoad()` (use `getBaseAttributes(this)` pattern from `bds-banner`)
- `handleInput`: update value, emit `bdsInput`, set `dirty=true`, update `currentCharCount`, run validation if `validationTiming === 'input'`
- `handleChange`: emit `bdsChange`; run validation if `validationTiming === 'change'` — fires only when value actually changed on blur
- `handleFocus`: set `focused=true`, emit `bdsFocus`
- `handleBlur`: set `focused=false`, `touched=true`, emit `bdsBlur`, run validation if `validationTiming === 'blur'`
- Password toggle: `handleShowPassword()` flips `showPassword`; effective input type switches between `'password'` and `'text'`
- Clear: `handleClear()` resets value to `''`, emits `bdsClear`; clear button visible when `(clearable || clearOnHover) && value !== ''`
- Disclosure: `handleDisclosure()` emits `bdsDisclosure`
- Expand built-in validators: `valueMissing` (required) + `tooShort` (minLength > 0)
- Emit `bdsValidationChange` from `updateValidity()` with `{ valid, validity, value, touched, dirty }`
- `formResetCallback`: also reset `touched=false`, `dirty=false`, `currentCharCount=0`, `showPassword=false`

### Task 2c — Render: full DOM structure, slots, ARIA

**File:** `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`

All class modifiers must go into `getClassMap()` — do not inline in render():

- `getClassMap()` additions: `--readonly`, `--plain` (variant === 'plain'), `--password` (type === 'password'), `--clearable-on-hover`, `--show-password`
- Label row (`.bds-text-field__label-row`): `bds-typography` with `tooltipText={info}`; renders only when `label` is set
- Sublabel (`.bds-text-field__sublabel`): inside container; renders only when `sublabel` is set
- Container (`.bds-text-field__container`): CSS Grid wrapper
- Prefix slot (`.bds-text-field__prefix`): `<slot name="prefix">`
- Input (`.bds-text-field__control`): all native attrs wired — `id={idComponent}`, effective `type` via `showPassword`, `disabled`, `readOnly`, `placeholder`, `autocomplete`, `minLength`/`maxLength` (omit when 0), `pattern`, `aria-labelledby`, `aria-describedby`, `aria-invalid`, `aria-required`
- Right-actions (`.bds-text-field__actions`): clear button, password toggle, disclosure icon, `<slot name="suffix">`
- Footer (`.bds-text-field__footer`): helper/error toggle + char counter (`counter && charCount > 0` shows `currentCharCount/charCount`)

### Task 3 — ✅ Create shared interactions SCSS partial

**File:** `packages/boreal-web-components/src/styles/_interactions.scss`

Created and wired via `injectGlobalPaths` in `stencil.config.ts` (injected after the token file so all `$boreal-*` variables are in scope at call-site compilation):

- `bds-focus-ring-value($outer-color, $inner-color)` — SCSS function; returns the two-layer focus ring shadow value. Parameters are explicit (no `$boreal-*` defaults) because Stencil compiles the file standalone during build/watch and any `$boreal-*` reference in the file body would fail.
- `bds-focus-ring($outer-color, $inner-color)` — mixin wrapping the above
- `bds-transition-surface` — `background-color`, `border-color`, `box-shadow` at `0.3s ease`
- `bds-transition-action` — `color`, `opacity` at `0.3s ease`
- `bds-icon($size, $font-size)` — styles `em[class^='bds-icon-']` / `em[class*=' bds-icon-']` children

Applied to:
- `bds-button.scss` — `@include bds-focus-ring(...)`, `bds-focus-ring-value(...)`, `@include bds-transition-surface`
- `bds-text-field.scss` — container and action transitions + focus ring via shared mixins; local `@mixin bds-icon` removed

Note: `_form-control.scss` (Phase 2 of EOA-10099) is deferred; `_interactions.scss` covers the cross-component interaction patterns needed for this ticket.

### Task 4 — ✅ Figma token audit for SCSS (completed inline with Task 5)

All token values verified via Figma MCP during the SCSS authoring session and mapped to `$boreal-*` variables.

### Task 5 — ✅ Write bds-text-field.scss

**File:** `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.scss`

BEM token-based styles complete. Key decisions:

- `display: flex` on container (not CSS Grid) — sufficient since `min-width: 0` on `__control` handles overflow truncation
- `%flex-center` and `%field-inline-label` SCSS placeholders for zero-duplication layout and typography reuse
- `[slot='prefix']` selector targets slotted content directly (no `::slotted()` — not available without shadow DOM)
- Container transition via `@include bds-transition-surface`; action transition via `@include bds-transition-action`; focus ring via `@include bds-focus-ring($boreal-stroke-focus, $boreal-ui-inverse)`
- All states covered: `--focused`, `--error`, `--disabled`, `--readonly`, `--plain`, `--clear-on-hover`

### Task 6 — Write unit tests

**Files (create under `__test__/`):**

- `bds-text-field-basics.spec.tsx` — renders, default props, label/helper/sublabel/counter rendering
- `bds-text-field-form.spec.tsx` — form association, FormData, reset, required
- `bds-text-field-validation.spec.tsx` — all 4 `validationTiming` values (`blur`, `change`, `input`, `submit`), touched/dirty tracking, built-in validators (`valueMissing`, `tooShort`), `customValidators`, `bdsValidationChange` payload
- `bds-text-field-events.spec.tsx` — `bdsInput`, `bdsChange`, `bdsFocus`, `bdsBlur`, `bdsClear`, `bdsDisclosure`
- `bds-text-field-a11y.spec.tsx` — `aria-invalid`, `aria-required`, `aria-labelledby`, `aria-describedby`

Target: ≥ 90% coverage. Use `newSpecPage` pattern from `bds-button` tests as reference.

### Task 7 — Storybook stories + MDX docs

**Files (create):**

- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.stories.ts`
- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.mdx`

Five-section story structure:

1. Overview — default story
2. Variants — `variant` (outline/plain), `type` (text/password), `clearable`, `disclosure`
3. States — error, disabled, readonly, focused
4. With slots — prefix, suffix
5. Form integration — inside `<form>` with reset/submit

MDX: component summary, props table, accessibility notes, slot documentation.

---

## Critical Files

| File                                                                          | Action                                                  |
| ----------------------------------------------------------------------------- | ------------------------------------------------------- |
| `src/styles/_interactions.scss`                                               | ✅ Done (shared focus ring, transitions, icon mixin)    |
| `src/components/forms/bds-text-field/bds-text-field.tsx`                      | ✅ Done (full props/events/logic)                       |
| `src/components/forms/bds-text-field/bds-text-field.scss`                     | ✅ Done (full token-based BEM styles)                   |
| `src/components/forms/bds-text-field/types/ITextField.ts`                     | ✅ Done                                                 |
| `src/components/forms/bds-text-field/types/enum.ts`                           | ✅ Done                                                 |
| `src/components/forms/bds-text-field/types/types.ts`                          | ✅ Done                                                 |
| `src/components/forms/bds-text-field/test/bds-text-field-basics.spec.tsx`     | Create                                                  |
| `src/components/forms/bds-text-field/test/bds-text-field-form.spec.tsx`       | Create                                                  |
| `src/components/forms/bds-text-field/test/bds-text-field-validation.spec.tsx` | Create                                                  |
| `src/components/forms/bds-text-field/test/bds-text-field-events.spec.tsx`     | Create                                                  |
| `src/components/forms/bds-text-field/test/bds-text-field-a11y.spec.tsx`       | Create                                                  |
| `src/stories/forms/bds-text-field/bds-text-field.stories.ts`                  | Create                                                  |
| `src/stories/forms/bds-text-field/bds-text-field.mdx`                         | Create                                                  |

## Utilities to Reuse

| Utility                 | Path                                          | Usage                                 |
| ----------------------- | --------------------------------------------- | ------------------------------------- |
| `formAssociatedMixin`   | `src/mixins/form-associated.mixin.ts`         | Already extended in skeleton          |
| `runValidators`         | `src/utils/form/internals.ts`                 | Run `IFormValidator[]` + set validity |
| `setFormValue`          | `src/utils/form/internals.ts`                 | Sync value with ElementInternals      |
| `IFormValidator`        | `src/types/form.ts`                           | Validator shape                       |
| `ValidationTiming`      | `src/types/form.ts`                           | `'blur' \| 'input' \| 'submit'` type  |
| `createId`              | `src/utils/helpers/common/BaseAttributes.tsx` | Auto-generate component ID            |
| `validatePropValue`     | `src/utils/helpers/validateProps.ts`          | Guard `type` and `variant` props      |
| `inheritAriaAttributes` | `src/utils/a11y/attributes.ts`                | Pass through aria-\* from host        |

## Out of Scope (next sprints)

- `textarea` mode
- `bds-typography` `tooltipText` feature (not yet merged) — `info` prop is declared and wired; tooltip UI activates once merged
- Keyboard/paste events (`bdsKeydown`, `bdsKeyup`, `bdsPaste`)
- Strict char count enforcement (counter display is in scope; hard input truncation is not)
- `bds-form-group` layout wrapper
- **Extract common input-form SCSS** — `bds-text-field.scss` contains patterns (container layout, sublabel, prefix slot, actions, footer, state modifiers) that will repeat in other form controls (`bds-select`, `bds-textarea`, etc.). A future task should extract these into a shared SCSS partial (originally planned as `src/styles/form/_form-control.scss`, Phase 2 of EOA-10099). Prerequisite: at least one more form control implemented so shared patterns can be identified with confidence.

## Verification

After Task 7 is complete, the following should pass:

1. `pnpm --filter boreal-web-components test` — all spec files green, ≥ 90% coverage
2. `pnpm --filter boreal-web-components build` — no TypeScript errors
3. Open Storybook (`pnpm dev` in `apps/boreal-docs`), verify all 5 story sections render correctly
4. Form Integration story: fill field + submit → value in FormData; reset → field clears
5. Set `required` + submit empty → `checkValidity()` false, error state visible
6. Set `type="password"` → toggle icon appears; click → toggles visibility
7. Set `clearable` + type value → clear button appears; click → clears value, emits `bdsClear`
8. Tab to field → focus ring visible using `$boreal-stroke-focus` token value
9. Set `counter` + `charCount=120` + type → footer shows `n/120`
