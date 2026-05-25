# Stencil — Form Control Interfaces and 2-Way Binding Architecture

## Interface Layering

Three interface levels govern all Boreal DS form controls:

| Interface                  | Location                   | Responsibility                                                                                                   |
| -------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `IFormAssociatedCallbacks` | `form-associated.mixin.ts` | Declares `formDisabledCallback`, `formResetCallback`, `formStateRestoreCallback` signatures                      |
| `IFormValueEmitter<T>`     | `form-associated.mixin.ts` | Declares `valueChange: EventEmitter<T>` — enforces consistent event naming across all form controls              |
| `IFormControl<T>`          | `form-associated.mixin.ts` | Composite: `IFormAssociatedCallbacks & IFormValueEmitter<T>` — the single interface a component class implements |

Component class declaration pattern:

```typescript
export class BdsTextField
  extends Mixin(formAssociatedMixin)
  implements ITextField, IFormControl<string>
{
  @AttachInternals() internals!: ElementInternals;

  @Event() valueChange!: EventEmitter<string>;
}
```

`IFormControl<T>` keeps the `implements` clause concise. Components do not implement `IFormAssociatedCallbacks` and `IFormValueEmitter<T>` separately.

## 2-Way Binding: What Belongs Where

| Concern                                             | Location                                                                                                                                                                                                                                    |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Event() valueChange: EventEmitter<T>` declaration | Component class                                                                                                                                                                                                                             |
| `.emit()` call                                      | In event/interaction handlers that change the value (e.g. `handleRadioChange`, `navigateTo`). For simpler controls a `@Watch('value')` also works; either pattern is valid as long as every code path that mutates `value` calls `.emit()`. |
| `IFormValueEmitter<T>` interface (enforces naming)  | `form-associated.mixin.ts`                                                                                                                                                                                                                  |
| `componentModels` config (enables `v-model`)        | `vue-output-target.ts`                                                                                                                                                                                                                      |

The `componentModels` config in `vue-output-target.ts` must land in the same PR as the finished component. It must never be added ahead of the component being complete — the Vue output target does NOT auto-generate v-model bindings from naming conventions. Explicit registration in `componentModels` is always required.

## `componentModels` Config Fields

`@stencil/vue-output-target`'s `componentModels` requires exactly three fields per entry. Components that share the same `event` and `targetAttr` can be grouped in a single entry:

```typescript
componentModels: [
  {
    elements: ["bds-text-field", "bds-radio-group"],
    event: "valueChange",
    targetAttr: "value",
  },
];
```

| Field        | Purpose                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------- |
| `elements`   | Array of custom element tag names. Group elements that share the same event + targetAttr. |
| `event`      | The Stencil `@Event()` name                                                               |
| `targetAttr` | The `@Prop()` name that holds the current value                                           |

**Flat primitive payloads work without `eventAttr`.**
When `valueChange` emits a flat primitive (e.g. `string`), the generated proxy reads `$event.detail` directly — Vue's `v-model` receives the correct value. `eventAttr` is not needed and should not be added. Verified with `bds-radio-group` which emits `valueChange` as a plain `string`.

## `IFormAssociatedCallbacks` JSDoc as Canonical Reference

The JSDoc `@example` block on `IFormAssociatedCallbacks` in `form-associated.mixin.ts` shows the complete correct implementation pattern for a new form control, including:

- `IFormControl<string>` in the `implements` clause
- `@Event() valueChange` declaration
- Correct import paths

This block is the authoritative template. When building a new form component, read it before writing the class declaration.

## The `formAssociatedMixin` Provides Zero Compile-Time Enforcement

**Critical fact:** The `formAssociatedMixin` mixin factory does NOT enforce any API contract at compile time. Its `name` declaration and all FACE callback signatures exist only as JSDoc.

```typescript
// From form-associated.mixin.ts
export const formAssociatedMixin = <T extends Constructor<HTMLElement>>(
  base: T,
) => {
  class FormAssociatedBase extends base implements ElementInternals {
    /** @type {string} Form control name (for submission) */
    name?: string; // ❌ JSDoc-only — TypeScript will NOT error if a component forgets to declare @Prop() name

    formDisabledCallback(disabled: boolean): void {}
    formResetCallback(): void {}
    formStateRestoreCallback(
      state: string | FormData | File | null,
      mode: "restore" | "autocomplete",
    ): void {}
  }
  return FormAssociatedBase as Constructor<IFormAssociatedCallbacks> & T;
};
```

**Why this matters:**

- A component that `extends Mixin(formAssociatedMixin)` but forgets to declare `@Prop() name` will **compile successfully** — no TypeScript error
- The forgotten `name` prop only manifests as a runtime failure: `internals.setFormValue(value, value)` submits the value with no key, and most server-side parsers silently discard it

**Required pattern to enforce `name` at compile time:**
Every FACE component must declare `name: string` in its own interface (`ICheckboxButton`, `IRadioButton`, `ITextField`, etc.), and the component class must `implements` that interface. TypeScript will then error if the `@Prop() name` declaration is missing.

## The `name` Prop Pattern for FACE Components

**All Form-Associated Custom Elements (FACE) must declare the `name` prop in both the component interface and the component class.**

### Why `name` Matters

`ElementInternals.setFormValue(value, value)` submits the form field keyed by the element's `name` attribute. Without `name`, the browser submits an **unnamed field** that most server-side parsers silently discard.

**Exception:** Components used exclusively inside a group (`bds-checkbox-group`, `bds-radio-group`) do not need a functional `name` prop — the **group** owns `name` and handles submission. Child components still declare `@Prop() name` for API consistency, but its value is irrelevant at runtime.

**Standalone usage:** Components used outside a group (e.g. standalone `<bds-checkbox>`, `<bds-text-field>`) **require** a `name` prop to participate in form submission.

### Required Declaration Pattern

```typescript
// 1. Add `name` to the component's interface
export interface ICheckboxButton {
  value: string;
  checked: boolean;
  disabled: boolean;
  name: string; // ✅ Enforces compile-time presence
}

// 2. Implement the interface in the component class
export class BdsCheckboxButton
  extends Mixin(formAssociatedMixin)
  implements ICheckboxButton, IFormControl<string>
{
  @Prop() name!: string; // ✅ TypeScript errors if this line is missing
  @Prop() value: string = "";
  // ...
}
```

### Components Updated

The following FACE components now enforce `name` via their interface:

- `bds-checkbox-button` (`ICheckboxButton`)
- `bds-radio-button` (`IRadioButton`)
- `bds-checkbox` (`ICheckbox`)
- `bds-checkbox-card` (`ICheckboxCard`) — already had `name` before this pattern was established

### Test Pattern for Hidden Inputs

When a FACE component contains a hidden `<input>` (for progressive enhancement or legacy form compatibility), that `<input>` must **not** have a `name` attribute — `ElementInternals` handles submission, and duplicating `name` on the inner input would submit the value twice.

**Test assertion:**

```typescript
it("hidden input does not have a name attribute", async () => {
  const page = await newSpecPage({
    components: [BdsCheckboxButton],
    html: `<bds-checkbox-button name="group" value="option-a"></bds-checkbox-button>`,
  });
  const input = page.root?.querySelector('input[type="checkbox"]');
  expect(input?.getAttribute("name")).toBeNull();
});
```

## ADR

See `.ai/decisions/0002-iform-control-composite-interface-for-form-components.md` for full trade-off analysis of the `IFormControl<T>` composite interface decision.
