# Stencil FACE — `@AttachInternals()` Placement Constraint

## Rule

`@AttachInternals()` must be declared directly on the component class body. It cannot be placed inside a mixin factory function.

## Why

Stencil's compiler performs static analysis on the component class. Decorators inside factory functions are not visible to this analysis for `@AttachInternals()`. The result is `this.internals === undefined` at runtime — every FACE lifecycle callback that calls `this.internals.setFormValue()` or `this.internals.setValidity()` throws a `TypeError`.

The failure is silent from TypeScript's perspective: the type is correct, the runtime value is not.

## What Works in Mixins

Other Stencil decorators do work inside mixin factories:

- `@Prop()` — confirmed
- `@State()` — confirmed
- `@Watch()` — confirmed
- `@Method()` — confirmed

Source: Stencil's official test suite at `test/wdio/ts-target/extends-mixin/mixin-a.tsx`.

## Required Pattern for Every FACE Component

```typescript
import { AttachInternals, Component, Mixin } from '@stencil/core';
import { formAssociatedMixin } from '@/mixins/form-associated.mixin';

@Component({ tag: 'bds-my-field', formAssociated: true })
export class BdsMyField extends Mixin(formAssociatedMixin) {
  @AttachInternals() internals!: ElementInternals;
}
```

The `@AttachInternals()` line must be on the class body — not in the mixin. `formAssociatedMixin`'s JSDoc contains a full working `@example` that shows this.

## ADR

See `.ai/decisions/0001-attach-internals-must-be-on-component-class-not-in-mixin.md` for full trade-off analysis.
