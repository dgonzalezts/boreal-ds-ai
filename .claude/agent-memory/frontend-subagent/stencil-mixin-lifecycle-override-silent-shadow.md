---
name: stencil-mixin-lifecycle-override-silent-shadow
description: Adding a plain (non-override) lifecycle method to a Mixin-composed Stencil class silently shadows the mixin's own same-named lifecycle method
metadata:
  type: project
---

Adding `componentWillLoad()` (or any other Stencil lifecycle method: `componentDidLoad`, `disconnectedCallback`, etc.) directly to a class that extends `Mixin(someMixin)` — without `override` and a `super.methodName()` call — silently shadows the mixin's own implementation of that same lifecycle method. TypeScript does not error on this (no `override` keyword required by the project's tsconfig), and Stencil calls whichever one wins the prototype chain with no warning.

**Concrete incident:** `bds-popover.tsx` extends `Mixin(anchoredMixin)`. `anchoredMixin` already defines `componentWillLoad()` to construct `this.positionEngine = new PositioningEngine()` and bind `show`/`hide`/`toggle`. Adding a bare `componentWillLoad() { this.hasContentBand = hasSlotContent(...); }` on `BdsPopover` shadowed it — `positionEngine` stayed `undefined`, and every `openPopover()`/click-to-open call across the entire test suite threw `Cannot read properties of undefined (reading 'computePosition')` at `anchored.mixin.ts:199`. 10 of 16 suites failed. Only caught by diffing against a clean `git stash` baseline run (54/54 passing) — the failure mode (positioning engine crash) looked completely unrelated to the actual change (a new slot/state field), which is what makes this dangerous: the stack trace points at mixin internals, not at the lifecycle method you just added.

**Fix:** `override componentWillLoad(): void { super.componentWillLoad(); /* own logic */ }`.

**How to apply:** Before adding ANY lifecycle method (`componentWillLoad`, `componentDidLoad`, `connectedCallback`, `disconnectedCallback`, `componentWillRender`, etc.) to a component class, grep the mixin(s) it composes (`extends Mixin(xMixin, yMixin)`) for that same method name first. If found, use `override` + `super.methodName()`. Applies to any Boreal DS component built on `anchoredMixin`, `floatingMixin`, or `formAssociatedMixin` — all of which define lifecycle hooks (`bds-popover`, `bds-tooltip`, `bds-select`, `bds-dropdown`, `bds-date-picker`, and any FACE form control). See also [[stencil-nested-component-same-name-event-collision]] for a related "composition hides a collision" class of bug.
