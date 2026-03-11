# ADR-0002 — Use `IFormControl<T>` as the Composite Interface for All Form Controls

**Status:** Accepted

---

## Context

During the PR review for the form foundation work (EOA-10099 / EOA-10230), the question arose of how to enforce consistent 2-way binding contracts across all Boreal DS form controls (`bds-text-field`, `bds-select`, `bds-checkbox`, `bds-radio`, `bds-textarea`, `bds-switch`, `bds-number-input`, `bds-range`).

Each form control needs to:

1. Implement the FACE lifecycle callbacks (`formDisabledCallback`, `formResetCallback`, `formStateRestoreCallback`).
2. Emit a consistently named event for 2-way binding (`valueChange`) with a typed payload.
3. Keep its `implements` clause readable as the number of interfaces grows.

The mixin (`formAssociatedMixin`) already eliminates `@Prop()` boilerplate. The remaining question was whether the interface layer above the mixin should be flat (many interfaces listed in `implements`) or composite (one interface grouping related contracts).

---

## Options Considered

### Option A — Components implement individual interfaces separately (rejected)

Each component class explicitly lists every interface it satisfies:

```typescript
export class BdsTextField extends Mixin(formAssociatedMixin)
  implements ITextField, IFormAssociatedCallbacks, IFormValueEmitter<string> {
```

**Pros:**
- Maximum explicitness — every contract is visible in the class declaration.
- No indirection to follow to understand what a component does.

**Cons:**
- As the number of shared interfaces grows, `implements` clauses become long and repetitive across every form component.
- `IFormAssociatedCallbacks` and `IFormValueEmitter<T>` always appear together for form controls — listing them separately adds noise without adding information.
- A contributor building a new form control must know to include both interfaces; there is no single type to reach for.
- Inconsistency risk: a new form control might omit `IFormValueEmitter<T>`, silently breaking the v-model contract.

### Option B — `IFormControl<T>` composite interface (accepted)

Define `IFormControl<T>` as:

```typescript
export type IFormControl<T> = IFormAssociatedCallbacks & IFormValueEmitter<T>;
```

Components use:

```typescript
export class BdsTextField extends Mixin(formAssociatedMixin)
  implements ITextField, IFormControl<string> {
```

**Pros:**
- Single type to implement for the complete form control contract.
- Enforces that `IFormAssociatedCallbacks` and `IFormValueEmitter<T>` always travel together — no risk of a component satisfying one but not the other.
- Concise `implements` clause that scales as more form components are added.
- TypeScript still enforces every member declared by both constituent interfaces; nothing is hidden from the compiler.
- Easy to extend: adding a new shared obligation to all form controls means adding it to `IFormControl<T>` once, not updating every component.

**Cons:**
- One level of indirection: reading a component class does not immediately show `IFormAssociatedCallbacks` and `IFormValueEmitter<T>` by name. A contributor must look up `IFormControl<T>`.
- Mitigated by: the JSDoc `@example` on `IFormAssociatedCallbacks` in `form-associated.mixin.ts` serves as the canonical implementation template, and `IFormControl<T>` is defined in the same file.

### Option C — No shared interface; rely solely on the mixin (rejected)

Skip the interface layer and rely on the mixin alone for consistency.

**Pros:**
- Zero interface overhead.

**Cons:**
- No compile-time contract for the event shape — a component could emit `onChange` instead of `valueChange` and TypeScript would not catch it.
- The Vue output target's `componentModels` config requires a known, consistent event name. Drift in naming causes silent v-model failures.
- The mixin provides props; the interface provides the event contract. Both layers are needed.

---

## Decision

`IFormControl<T>` is defined as a composite type alias (`IFormAssociatedCallbacks & IFormValueEmitter<T>`) in `form-associated.mixin.ts`. Every Boreal DS form control implements it alongside its component-specific interface.

The split of responsibilities is:

| What | Where |
|---|---|
| `@Prop() name`, `disabled`, `required`, `formDisabledCallback` | `formAssociatedMixin` (runtime, eliminates boilerplate) |
| `IFormAssociatedCallbacks`, `IFormValueEmitter<T>` | `form-associated.mixin.ts` (compile-time contracts, individual interfaces) |
| `IFormControl<T>` | `form-associated.mixin.ts` (composite alias for the two above) |
| Component-specific interface (e.g. `ITextField`) | Component file or `types/` |
| `@Event() valueChange` declaration | Component class body |
| `valueChange.emit()` call | `@Watch('value')` on the component class |
| `componentModels` config | `vue-output-target.ts` (added in the same PR as the component) |

---

## Consequences

**Easier:**
- New form components have a single type to implement (`IFormControl<T>`) that guarantees the full FACE + event contract.
- Compiler enforcement prevents naming drift on the `valueChange` event.
- `componentModels` in the Vue output target has a stable, predictable event name to register against.
- The `IFormAssociatedCallbacks` JSDoc `@example` provides the complete correct implementation template in one place, reducing the learning curve for contributors.

**Harder:**
- A contributor reading a component class must follow `IFormControl<T>` to understand its constituent interfaces. The JSDoc on the composite type and on `IFormAssociatedCallbacks` mitigates this.

**Follow-up actions:**
- When `bds-select`, `bds-checkbox`, `bds-radio`, and `bds-textarea` are built, each must implement `IFormControl<T>` — add this to the form component Definition of Done checklist.
- `componentModels` entry must be added to `vue-output-target.ts` in the same PR that delivers the finished component. This is a hard requirement — the Vue output target does not auto-generate v-model from naming conventions.
- If `valueChange` emits a flat primitive rather than an object, the `componentModels` entry must set `eventAttr` to prevent `undefined` reads from `event.detail[targetAttr]`.
