---
status: in progress
---

# EOA-10099 — Form Foundation Architecture

## Context

Boreal-DS has no form-related components yet. Before implementing `bds-text-field`, `bds-select`, `bds-checkbox`, `bds-radio`, etc., a shared foundation must be established to avoid duplicating the same 15+ lines of boilerplate (form association, props, lifecycle callbacks, validation) in every component.

This plan is the result of a deep comparative analysis of four reference libraries:

- **IgniteUI** (Lit, production-grade) — mixin composition + validator array pattern
- **Colibri** (Lit, same DS as Aqua) — `validationTiming`, `touched`/`dirty` state tracking
- **Aqua DS** (Stencil, same DS as Colibri) — flat `@Component`, Stencil + SCSS, same tech stack
- **BEEQ** (Stencil, production-grade) — `@AttachInternals()`, standard HTML5 prop names

**Stack context:**

- Boreal-DS uses **Stencil.js** (not Lit)
- Existing infra: `inheritAriaAttributes` utility (`packages/boreal-web-components/src/utils/`), `alignment/size/states/stylesMap` types
- No form class, no form utilities, no form lifecycle infrastructure exists

---

## Architectural Decision: Two-Phase Approach

The foundation is split into two phases to avoid over-engineering:

- **Phase 1** (now): Types + one mixin + utility functions — the JS/TS form foundation
- **Phase 2** (after `boreal-styleguidelines` token integration): Shared SCSS partial + additional behavioral mixins (`textInputMixin`, `selectableMixin`)
- **Phase 3** (deferred): `ReactiveControllerHost` + UI behavior controllers — added when `bds-select`, `bds-modal`, or `bds-tooltip` are built and genuinely need lifecycle-managed behavior objects

### Composition Pattern Decision Rules

| What to share                                                                         | Pattern                         | Reason                                                                                                                                                                  |
| ------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Prop`, `@State`, `@Watch`                                                           | **Mixin factory**               | Stencil decorators require class membership — no function can add `@Prop()` to a component                                                                              |
| `@AttachInternals()`                                                                  | **Component class (not mixin)** | Stencil's compiler must see this decorator statically on the component class body; inside a mixin factory it is not picked up and `internals` is `undefined` at runtime |
| Stateless logic (value coercion, validator runner, slot detection)                    | **Utility function**            | No lifecycle, no state, minimal overhead                                                                                                                                |
| Encapsulated UI behavior with lifecycle (FloatingUI, IntersectionObserver, FocusTrap) | **ReactiveController**          | Lifecycle-dependent, reused across 3+ non-form components, testable in isolation                                                                                        |
| Simple debounce timer (text input only)                                               | **Inline**                      | 4 lines — controller overhead not justified                                                                                                                             |

---

## Why Mixin over Utilities for Form Props

Stencil decorators (`@Prop`, `@State`, `@Watch`, `@AttachInternals`) are class-level metadata. There is no function call that adds a reflected `@Prop()` to a component. Without a mixin, every form component (`bds-text-field`, `bds-select`, `bds-checkbox`, `bds-radio`, `bds-textarea`, `bds-switch`, `bds-number-input`, `bds-range`) would individually declare:

```typescript
// Repeated 8+ times across all form components without a mixin
@Prop({ reflect: true }) name!: string;
@Prop({ reflect: true }) disabled: boolean = false;
@Prop({ reflect: true }) required: boolean = false;
formDisabledCallback(d: boolean) { this.disabled = d; }
```

That is ~12 lines × 8+ components = 96+ lines of identical, untestable boilerplate with no single point of correction. The mixin eliminates this.

`@AttachInternals()` is the one decorator that cannot be inside the mixin — Stencil's compiler performs static analysis on the component class and does not pick it up from a mixin factory. Each component must declare `@AttachInternals() internals!: ElementInternals;` directly on its class body. This is confirmed by the Stencil docs: `@AttachInternals()` appears only on component classes, never inside mixin examples.

**Reference:** Stencil's official test suite confirms that `@Prop()`, `@State()`, `@Watch()`, and `@Method()` work inside mixin factories: `test/wdio/ts-target/extends-mixin/mixin-a.tsx`.

---

## Why ReactiveControllerHost is Deferred

`ReactiveControllerHost` is NOT a Stencil import — it is a ~40-line user-defined class you copy into your project (modeled on `test/wdio/ts-target/extends-via-host/reactive-controller-host.ts`). It uses `forceUpdate(this)` from `@stencil/core` to let controllers trigger re-renders. The value becomes clear when multiple components need the same encapsulated lifecycle behavior:

- `FloatingUIController` → `bds-select`, `bds-tooltip`, `bds-popover` (all need position management)
- `FocusTrapController` → `bds-modal`, `bds-dropdown`
- `IntersectionController` → `bds-list`, `bds-table` (virtual scroll)

For form components alone, this layer adds infrastructure without a third consumer. Deferring it until `bds-select` is built gives a real use case to validate the pattern.

---

## Phase 1 — Form Foundation (implement now)

### Files to create

| File                                                                    | Contents                                                                                                              | Status     |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------- |
| `packages/boreal-web-components/src/types/form.ts`                      | `ValidationTiming`, `IFormValidator` (uses Stencil's `MixedInCtor` from `@stencil/core` — no custom Constructor type) | ✅ done    |
| `packages/boreal-web-components/src/mixins/form-associated.mixin.ts`    | `formAssociatedMixin` factory                                                                                         | ✅ done    |
| `packages/boreal-web-components/src/utils/form/form-utils.ts`           | `setFormValue()`, `runValidators()`                                                                                   | ✅ done    |
| `packages/boreal-web-components/src/utils/dom/elements.ts`              | `hasSlotContent()`                                                                                                    | ✅ done    |
| `packages/boreal-web-components/src/styles/form/_input-field-base.scss` | Shared SCSS partial — **deferred to Phase 2** (depends on `boreal-styleguidelines` token integration)                 | 📋 Phase 2 |

---

### 1. Types (`src/types/form.ts`)

```typescript
// Components declare @Prop({ reflect: true }) error: boolean = false directly — no status enum.
// Matches Colibri and Aqua DS (same design system).

// For text-based components only (via textInputMixin, Phase 2).
// Does not include 'change' — redundant with 'blur' for text inputs.
export type ValidationTiming = "blur" | "input" | "submit";

export interface IFormValidator {
  key: keyof ValidityStateFlags;
  isValid: (el: HTMLElement) => boolean;
  message: string;
}
```

---

### 2. Mixin factory (`src/mixins/form-associated.mixin.ts`)

Declares all shared form association props and lifecycle callbacks. Eliminates ~12 lines of boilerplate per component.

Uses Stencil's official `Mixin()` utility and `MixedInCtor` type from `@stencil/core` — no custom Constructor type needed.

```typescript
import { Prop, type MixedInCtor } from "@stencil/core";

export const formAssociatedMixin = <B extends MixedInCtor>(Base: B) => {
  class FormAssociated extends Base {
    @Prop({ reflect: true }) name!: string;
    @Prop({ reflect: true, mutable: true }) disabled: boolean = false;
    @Prop({ reflect: true }) required: boolean = false;

    formDisabledCallback(disabled: boolean) {
      this.disabled = disabled;
    }
  }
  return FormAssociated;
};
```

Each form component extends the mixin and declares `@AttachInternals()` directly on its class body:

```typescript
import { AttachInternals, Component, Mixin, Prop } from "@stencil/core";

@Component({ tag: "bds-text-field", formAssociated: true })
export class BdsTextField extends Mixin(formAssociatedMixin) {
  @AttachInternals() internals!: ElementInternals; // must be on the component class, not in the mixin

  @Prop({ reflect: true }) error: boolean = false;
  @Prop({ mutable: true, reflect: true }) value: string = "";

  // Inline debounce — 4 lines, no controller needed
  private debounceTimer?: ReturnType<typeof setTimeout>;
  disconnectedCallback() {
    clearTimeout(this.debounceTimer);
  }
}
```

---

### 3. Utility functions (`src/utils/form/form-utils.ts`)

```typescript
import type { IFormValidator } from "../../types/form";

export function setFormValue(
  internals: ElementInternals,
  value: string | File | FormData | null | undefined,
): void {
  internals.setFormValue(value ?? null);
}

export function runValidators(
  internals: ElementInternals,
  validators: IFormValidator[],
  el: HTMLElement,
): boolean {
  const flags: Partial<ValidityStateFlags> = {};
  const messages: string[] = [];

  for (const { key, isValid, message } of validators) {
    if (!isValid(el)) {
      flags[key] = true;
      messages.push(message);
    }
  }

  const isValid = Object.keys(flags).length === 0;
  internals.setValidity(isValid ? {} : flags, messages[0] ?? "");
  return isValid;
}
```

---

### 4. DOM helper (`src/utils/dom/elements.ts`)

```typescript
export function hasSlotContent(el: HTMLElement, slotName?: string): boolean {
  if (slotName !== undefined) {
    return el.querySelector(`[slot="${slotName}"]`) !== null;
  }
  return Array.from(el.childNodes).some((node) => {
    if (node.nodeType === Node.ELEMENT_NODE)
      return (node as Element).slot === "";
    if (node.nodeType === Node.TEXT_NODE)
      return node.textContent?.trim() !== "";
    return false;
  });
}
```

---

### 5. Shared SCSS base partial (`src/utils/form/styles/_input-field-base.scss`)

#### Why this exists

The same duplication problem that the behavioral mixin solves for `@Prop` declarations exists for CSS. Without a shared partial, each of `bds-text-field`, `bds-select`, `bds-number-input`, `bds-combobox`, and `bds-textarea` would individually define the container border, label typography, helper text area, prefix/suffix zones, focus ring, disabled state, readonly state, and the error state — roughly 80 lines of identical SCSS per component.

**Reference:** Colibri's `InputFormComponentStyles` solves this centrally:

- `col-text-field` → `[InputFormComponentStyles]` (no overrides at all)
- `col-select` → `[InputFormComponentStyles, ColSelectStyles]` (only dropdown-specific additions)
- `col-number-field` → `[InputFormComponentStyles, ColNumberFieldStyles]` (only stepper additions)

Aqua DS has no equivalent — it duplicates error/disabled/readonly state rules in every component SCSS file, confirmed by the analysis.

#### No shadow DOM in alpha

Boreal DS alpha does not use shadow DOM (`shadow: true` is not set). `:host()` selectors are unavailable. The partial uses a SCSS mixin so each component scopes the shared styles under its own BEM root class.

#### What the partial covers

```scss
// _input-field-base.scss
// Used by: bds-text-field, bds-select, bds-number-input, bds-combobox, bds-textarea

@mixin input-field-base() {
  // 1. Container shell
  .input-container {
    /* border, radius, background, height, display, align-items */
  }

  // 2. Label zone (above the container)
  .input-label {
    /* typography tokens, color */
  }

  // 3. Input element reset (the native <input> inside the component)
  .input-control {
    /* border: none; outline: none; background: transparent; width: 100% */
  }

  // 4. Helper text / error message area (below the container)
  .input-helper-text {
    /* typography, color */
  }

  // 5. Prefix / suffix zones (inside the container)
  .input-prefix,
  .input-suffix {
    /* display, align-items, gap */
  }

  // 6. Interactive states (mapped from BEM modifier classes set by the render function)
  &--disabled .input-container {
    /* disabled appearance */
  }
  &--readonly .input-container {
    /* readonly appearance */
  }
  &:focus-within .input-container {
    /* focus ring tokens */
  }

  // 7. Error state (mapped from --error BEM modifier class)
  &--error .input-container {
    /* border-color: error token */
  }
  &--error .input-helper-text {
    /* color: error token */
  }

  // 8. Size variants (sm / md / lg via BEM modifier classes)
  &--size-sm {
    /* height: sm token */
  }
  &--size-lg {
    /* height: lg token */
  }
}
```

#### How each component uses it

```scss
// bds-text-field.scss
@use "../../utils/form/styles/input-field-base" as base;

.bds-text-field {
  @include base.input-field-base();
  // No additional rules needed for a basic text input
}

// bds-select.scss
@use "../../utils/form/styles/input-field-base" as base;

.bds-select {
  @include base.input-field-base();
  // Component-specific additions only:
  .select-chevron {
    transition: transform 0.2s;
  }
  &--open .select-chevron {
    transform: rotate(180deg);
  }
}

// bds-number-input.scss
@use "../../utils/form/styles/input-field-base" as base;

.bds-number-input {
  @include base.input-field-base();
  // Component-specific additions only:
  .stepper-buttons {
    display: flex;
    flex-direction: column;
  }
  .stepper-up,
  .stepper-down {
    height: 50%;
  }
}
```

The component's render function applies BEM modifier classes on `<Host>`:

```tsx
<Host class={{
  'bds-text-field': true,
  'bds-text-field--error': this.error,
  'bds-text-field--disabled': this.disabled,
  'bds-text-field--size-sm': this.size === 'sm',
}}>
```

#### Light DOM scoping note

Because Boreal DS alpha does not use shadow DOM, each component's styles are included in the global stylesheet via `styleUrl`. The `@mixin` approach ensures all shared styles are nested under the component's own BEM root class (e.g., `.bds-text-field { ... }`), preventing unintended style leakage to other elements.

---

## Phase 2 — Shared SCSS + Additional Behavioral Mixins (after `boreal-styleguidelines` integration)

### Shared SCSS partial (`src/styles/form/_input-field-base.scss`)

Deferred until `boreal-styleguidelines` token integration lands. Token values must come from the real system — not invented placeholders. The mixin structure (BEM elements, modifier names) is documented in the plan and in `curious-whistling-canyon.md`.

### `textInputMixin` — extract after `bds-text-field` + `bds-textarea` are both built

Equivalent to Colibri's `TextInputBase` + relevant parts of `InputFormComponent`. Adds text-entry specific props and behaviors that are NOT applicable to select, checkbox, or radio.

```typescript
// src/mixins/text-input.mixin.ts
import { Mixin, MixedInCtor } from "@stencil/core";

export const textInputMixin = <B extends MixedInCtor>(Base: B) => {
  class TextInput extends Base {
    @Prop() placeholder: string = "";
    @Prop({ reflect: true }) readonly: boolean = false;
    @Prop() pattern?: string;
    @Prop() minLength?: number;
    @Prop() maxLength?: number;
    @Prop() inputMode?:
      | "none"
      | "text"
      | "numeric"
      | "decimal"
      | "email"
      | "tel"
      | "url"
      | "search";

    @State() dirty: boolean = false;
    @State() touched: boolean = false; // set true on first blur — enables progressive error disclosure

    // initialValue: captured in componentDidLoad for dirty tracking
    // Character counting + limit enforcement
    // @Event() bdsClear — dispatched when clear action triggered
    // Enhanced blur validation (runs runValidators when validationTiming === 'blur' && touched === true)
  }
  return TextInput;
};
```

**Consumers:** `bds-text-field`, `bds-textarea`, possibly `bds-number-input` (subset of props)

---

### `selectableMixin` — extract after `bds-checkbox` + `bds-radio` are both built

Equivalent to Colibri's `SelectableFormComponent`. Handles the toggle/checked paradigm for form-associated components. Works alongside `formAssociatedMixin` — form association (`name`, `disabled`, `required`, `@AttachInternals()`) comes from the base mixin; this adds the checked state and selection behavior.

```typescript
// src/mixins/selectable.mixin.ts
import { Mixin, MixedInCtor } from "@stencil/core";

export const selectableMixin = <B extends MixedInCtor>(Base: B) => {
  class Selectable extends Base {
    @Prop({ mutable: true, reflect: true }) checked: boolean = false;
    @Prop() value: string = "on"; // HTML default for checkbox value
    @Prop() indeterminate?: boolean; // checkbox-specific, ignored by radio/switch

    // _performSelection(): toggles checked, calls internals.setFormValue(checked ? value : null)
    // @Event() bdsChange — with { checked, value, indeterminate? } detail
    // formResetCallback override: restores checked to initial default
  }
  return Selectable;
};
```

**Consumers:** `bds-checkbox`, `bds-radio`, `bds-switch`

---

### Mixin composition for selectable components

```typescript
import { Component, Mixin } from '@stencil/core';

@Component({ tag: 'bds-checkbox', formAssociated: true })
export class BdsCheckbox extends Mixin(formAssociatedMixin, selectableMixin) {
  render() { ... }
}
```

---

## Phase 3 — Controller Infrastructure (deferred, after bds-select / bds-modal)

Add these files when `bds-select`, `bds-modal`, or `bds-tooltip` are built and need lifecycle-managed behavior:

| File                                                | Purpose                                                                                                            | Trigger                                                  |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| `src/utils/controllers/reactive-controller-host.ts` | ~40-line `ReactiveControllerHost` base class + `ReactiveController` interface (modeled on Stencil's official test) | First component needing a pluggable lifecycle controller |
| `src/utils/controllers/floating-ui.controller.ts`   | FloatingUI positioning + cleanup                                                                                   | `bds-select`, `bds-tooltip`, `bds-popover`               |
| `src/utils/controllers/focus-trap.controller.ts`    | Focus containment                                                                                                  | `bds-modal`, `bds-dropdown`                              |

**Note:** When Phase 3 infrastructure exists, evaluate promoting inline debounce to a `DebounceController` if 3+ components use it.

---

## Reference Libraries Summary

| Feature                | IgniteUI (Lit)                  | Colibri (Lit)               | Aqua DS (Stencil)   | BEEQ (Stencil)          | **Boreal-DS plan**                                              |
| ---------------------- | ------------------------------- | --------------------------- | ------------------- | ----------------------- | --------------------------------------------------------------- |
| Form association       | ElementInternals ✓              | Hidden input                | Hidden input        | ElementInternals ✓      | **ElementInternals ✓**                                          |
| Property naming        | Standard                        | Standard                    | `isChecked` ✗       | Standard                | **Standard**                                                    |
| Shared abstraction     | Mixins                          | Inheritance                 | None                | Utilities               | **Mixin + Utilities**                                           |
| Shared base styling    | CSS-in-JS (centralized ✓)       | CSS-in-JS (centralized ✓)   | No shared partial ✗ | No shared partial ✗     | **SCSS partial (`_input-field-base`) ✓**                        |
| Text-entry mixin       | ✗                               | ✓ `TextInputBase`           | ✗                   | ✗                       | **Phase 2: `textInputMixin`**                                   |
| Selectable mixin       | ✓ `FormAssociatedCheckboxMixin` | ✓ `SelectableFormComponent` | ✗                   | ✗                       | **Phase 2: `selectableMixin`**                                  |
| Validation timing      | ✗                               | ✓                           | ✗                   | ✗                       | **`ValidationTiming` in `textInputMixin` (Phase 2, text only)** |
| Touched / dirty state  | ✓                               | ✓                           | ✗                   | ✗                       | **Phase 2: `textInputMixin`**                                   |
| Validation error prop  | ✗                               | ✗                           | ✗                   | `validationStatus` enum | **`error: boolean` on each component**                          |
| Validator composition  | ✓ (array)                       | Partial                     | ✗                   | ✗                       | **`runValidators()` utility**                                   |
| Radio group delegation | ✓                               | ✓                           | ✗                   | ✓                       | **Per BEEQ pattern**                                            |
| Debounce               | ✗                               | ✗                           | ✗                   | ✓ (prop)                | **Inline, per component**                                       |
| Controller pattern     | ✗ (Lit)                         | ✗                           | ✗                   | ✗                       | **Phase 2, deferred**                                           |

---

## Verification

Phase 1 verification — all steps completed ✅

1. ✅ Created `bds-text-field` using `formAssociatedMixin` + `@Component({ formAssociated: true })`
2. ✅ Rendered inside a native `<form>` in the `index.html` dev harness
3. ✅ `form.elements` includes `bds-text-field[name=username]`
4. ✅ `FormData` snapshot includes the field value under the `name` attribute
5. ✅ `form.reset()` fires `formResetCallback` and restores value to `''`
6. ✅ `formDisabledCallback` fires when a `<fieldset disabled>` ancestor is toggled — **note:** `form.disabled = true` does NOT trigger it; `HTMLFormElement` has no native `disabled` property. Use a `<fieldset>` wrapper or set `component.disabled` directly for testing.
7. ✅ `await bdsTextField.checkValidity()` returns `true` when field has a value — **note:** `bdsTextField.internals` is blocked by Stencil's element proxy; use the `@Method()` wrappers `checkValidity()` / `reportValidity()` instead.
8. ✅ `required=true` + empty value → `await bdsTextField.reportValidity()` triggers the browser's native validation tooltip; `runValidators()` sets `{ valueMissing: true }` via `internals.setValidity()`

**Styling (Phase 2 — after `boreal-styleguidelines` token integration):**

9. Render `bds-text-field` and `bds-select` side by side — verify container border, height, border-radius, and label typography are visually identical
10. Set `error` attribute on `bds-text-field` — verify border color changes to the error design token
11. Set `disabled` on `bds-text-field` — verify disabled appearance matches the disabled design token
12. Set `size="sm"` and `size="lg"` — verify height changes to the corresponding size token values
13. Inspect the light DOM of `bds-select` — verify no error/disabled/focus styles are duplicated between the base partial and component-specific overrides
