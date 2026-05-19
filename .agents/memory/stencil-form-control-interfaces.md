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

## ADR

See `.ai/decisions/0002-iform-control-composite-interface-for-form-components.md` for full trade-off analysis of the `IFormControl<T>` composite interface decision.
