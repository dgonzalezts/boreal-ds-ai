---
name: component-code-organization-bds-table
description: Non-obvious ordering and lifecycle rules when applying the member ordering standard to Stencil components
metadata:
  type: project
---

## `@Element()` must precede `@State()`

The member ordering standard places the element reference before internal reactive state. A common mistake is declaring `@State()` fields above `@Element()`.

**Why:** Every Stencil component reads state scoped to `this.el`, so the element reference is contextually prior even if there is no compile-time dependency ordering.

**How to apply:** When reorganising any component file, always place `@Element()` above the first `@State()` field, regardless of how the original author ordered them.

---

## Lifecycle methods follow execution order, not alphabetical order

Lifecycle methods must appear in the order Stencil actually fires them:

```
componentWillLoad → componentDidRender → componentDidLoad → disconnectedCallback
```

A frequent mistake is placing `componentDidLoad` above `componentDidRender`. On first mount, `componentDidRender` fires first (after every render pass, including the initial one), then `componentDidLoad` fires once.

**Why:** Lifecycle ordering is the single exception to the "alphabetical within group" rule. Alphabetical ordering puts `componentDidLoad` before `componentDidRender`, which is wrong and misleads the reader about the actual execution sequence.

**How to apply:** For any component with both `componentDidLoad` and `componentDidRender`, always place `componentDidRender` first in the file.

---

## Alphabetical ordering applies within every group except lifecycle methods

All other groups (`@State()`, `@Prop()`, `@Watch()`, `@Event()`, `handle*` methods, `@Method()`, internal methods, `render*` helpers) sort members alphabetically.

**Why:** Predictable ordering lets reviewers find members by name without scrolling. The alphabetical constraint is easy to overlook because it is stated separately from the group definitions.

**How to apply:** After placing a member in the correct group, sort all members in that group A–Z by identifier name. `@Watch()` sorts by watched prop name, not by method name.

---

## Section comments should not be added without asking

The guidelines describe section divider comments as "optional but encouraged for large components (more than ~150 lines)". The team preference in this repo is to omit them and rely on the ordering convention itself.

**Why:** Section comments were added then removed at team request — the guideline says "encouraged" but the team prefers a clean file over visual dividers.

**How to apply:** Ask the assignee before adding section comments to any component, even when the file exceeds the size threshold.

---

## `@State()` JSDoc is a readability choice, not a tooling requirement

The CEM analyzer and Stencil compiler require JSDoc only on `@Prop()`, `@Event()`, and `@Method()`. Placing JSDoc on `@State()` fields produces no output in `custom-elements.json` and triggers no lint rule.

**Why:** Internal reactive state is an implementation detail, not part of the public API contract.

**How to apply:** Omit JSDoc from `@State()` fields unless the field name alone is genuinely ambiguous. Do not add JSDoc to `@State()` fields just because adjacent `@Prop()` fields have it.
