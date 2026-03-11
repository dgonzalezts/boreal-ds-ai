# ADR-0001 — Declare `@AttachInternals()` on the Component Class, Not Inside a Mixin Factory

**Status:** Accepted

---

## Context

Boreal DS uses a mixin-based composition pattern to share common form-association boilerplate (`name`, `disabled`, `required`, `formDisabledCallback`) across all form-associated custom elements. The initial design question was whether `@AttachInternals()` could also be declared inside `formAssociatedMixin`, alongside the other shared props, to fully encapsulate the FACE setup in one place.

During the implementation of `bds-text-field`, placing `@AttachInternals()` inside the mixin factory caused `this.internals` to be `undefined` at runtime inside `formAssociatedCallback`. The error thrown was:

```
TypeError: Cannot read properties of undefined (reading 'setFormValue')
```

This surfaced that Stencil's compiler treats `@AttachInternals()` differently from other decorators — it requires static visibility on the component class body and does not pick it up when the decorator is applied inside a factory function at runtime.

---

## Options Considered

### Option A — Declare `@AttachInternals()` inside `formAssociatedMixin` (rejected)

**Pros:**
- Single location for all FACE setup; consumers write zero internals-related code

**Cons:**
- Stencil's compiler performs static analysis on the component class body. Decorators placed inside mixin factory functions are not visible to this analysis for `@AttachInternals()` specifically.
- `this.internals` is `undefined` at runtime in every FACE lifecycle callback — the component cannot call `internals.setFormValue()`, `internals.setValidity()`, or `internals.checkValidity()`.
- Confirmed by Stencil's own docs: `@AttachInternals()` appears exclusively on component classes, never inside mixin examples.
- Silent failure — the TypeScript type is correct, the runtime value is not, so TypeScript provides no protection.

### Option B — Declare `@AttachInternals()` directly on each consuming component class (accepted)

**Pros:**
- Stencil's compiler sees the decorator statically on the class body and wires up `ElementInternals` correctly.
- `this.internals` is defined and fully functional in all FACE lifecycle callbacks.
- Consistent with every Stencil FACE example in the official docs and test suite.
- The mixin still eliminates the real boilerplate (three `@Prop` declarations and `formDisabledCallback`).

**Cons:**
- Each form component must write one extra line: `@AttachInternals() internals!: ElementInternals;`
- The setup is not fully encapsulated in the mixin — consumers must know about this requirement.

---

## Decision

`@AttachInternals()` is declared directly on each component class, not inside `formAssociatedMixin`. `formAssociatedMixin` documents this requirement explicitly in its JSDoc with a working `@example`.

The split is:

| What | Where |
|---|---|
| `@Prop() name`, `@Prop() disabled`, `@Prop() required`, `formDisabledCallback` | `formAssociatedMixin` |
| `@AttachInternals() internals!: ElementInternals` | Component class body (each component) |

**Note:** This constraint applies only to `@AttachInternals()`. Other Stencil decorators — `@Prop()`, `@State()`, `@Watch()`, `@Method()` — work correctly inside mixin factories. This is confirmed by Stencil's official test suite at `test/wdio/ts-target/extends-mixin/mixin-a.tsx`.

---

## Consequences

**Easier:**
- `this.internals` is always defined and functional in FACE callbacks across all form components.
- Future form components (`bds-select`, `bds-checkbox`, `bds-radio`, `bds-textarea`) can safely call `internals.setFormValue()` and `internals.setValidity()` without debugging undefined access errors.
- The mixin JSDoc contains a complete, compilable `@example` that shows the required `@AttachInternals()` line, making the constraint discoverable at point of use.

**Harder:**
- Contributors building a new form component must remember to add `@AttachInternals() internals!: ElementInternals;` to the class body. The mixin's JSDoc `@example` mitigates this by serving as the authoritative template.

**Follow-up actions:**
- Add a checklist item to the form component Definition of Done: "Component class declares `@AttachInternals() internals!: ElementInternals` directly on the class body (not inherited from mixin)."
- When `bds-select`, `bds-checkbox`, and `bds-radio` are built, verify each one declares the decorator directly before the PR is merged.
