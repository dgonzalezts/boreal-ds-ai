# Stencil — Form Control Interfaces and 2-Way Binding Architecture

## Interface Layering

Three interface levels govern all Boreal DS form controls:

| Interface | Location | Responsibility |
|---|---|---|
| `IFormAssociatedCallbacks` | `form-associated.mixin.ts` | Declares `formDisabledCallback`, `formResetCallback`, `formStateRestoreCallback` signatures |
| `IFormValueEmitter<T>` | `form-associated.mixin.ts` | Declares `valueChange: EventEmitter<T>` — enforces consistent event naming across all form controls |
| `IFormControl<T>` | `form-associated.mixin.ts` | Composite: `IFormAssociatedCallbacks & IFormValueEmitter<T>` — the single interface a component class implements |

Component class declaration pattern:

```typescript
export class BdsTextField extends Mixin(formAssociatedMixin) implements ITextField, IFormControl<string> {
  @AttachInternals() internals!: ElementInternals;

  @Event() valueChange!: EventEmitter<string>;
}
```

`IFormControl<T>` keeps the `implements` clause concise. Components do not implement `IFormAssociatedCallbacks` and `IFormValueEmitter<T>` separately.

## 2-Way Binding: What Belongs Where

| Concern | Location |
|---|---|
| `@Event() valueChange: EventEmitter<T>` declaration | Component class |
| `.emit()` call | Inside `@Watch('value')` on the component class |
| `IFormValueEmitter<T>` interface (enforces naming) | `form-associated.mixin.ts` |
| `componentModels` config (enables `v-model`) | `vue-output-target.ts` |

The `componentModels` config in `vue-output-target.ts` must land in the same PR as the finished component. It must never be added ahead of the component being complete — the Vue output target does NOT auto-generate v-model bindings from naming conventions. Explicit registration in `componentModels` is always required.

## `componentModels` Config Fields

`@stencil/vue-output-target`'s `componentModels` requires exactly three fields:

```typescript
componentModels: [
  {
    elements: ['bds-text-field'],
    event: 'valueChange',
    targetAttr: 'value',
  },
]
```

| Field | Purpose |
|---|---|
| `elements` | Array of custom element tag names |
| `event` | The Stencil `@Event()` name |
| `targetAttr` | The `@Prop()` name that holds the current value |

By default the output target reads the new value from `event.detail[targetAttr]`. If `valueChange` emits a flat primitive (not an object), add `eventAttr` pointing to the correct detail path to avoid `undefined` reads.

## `IFormAssociatedCallbacks` JSDoc as Canonical Reference

The JSDoc `@example` block on `IFormAssociatedCallbacks` in `form-associated.mixin.ts` shows the complete correct implementation pattern for a new form control, including:

- `IFormControl<string>` in the `implements` clause
- `@Event() valueChange` declaration
- Correct import paths

This block is the authoritative template. When building a new form component, read it before writing the class declaration.

## ADR

See `.ai/decisions/0002-iform-control-composite-interface-for-form-components.md` for full trade-off analysis of the `IFormControl<T>` composite interface decision.
