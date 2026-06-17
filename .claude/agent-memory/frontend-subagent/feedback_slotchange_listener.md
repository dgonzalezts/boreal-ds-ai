---
name: feedback_slotchange_listener
description: Two patterns for observing child changes — choose based on whether children are slotted content or unslotted direct DOM children
metadata:
  type: feedback
---

There are two patterns for re-reading children when they change dynamically. Choose based on how the children are placed.

**Pattern A — `<slot onSlotchange={handler}>` (JSX, idiomatic Stencil)**

Use when the component renders a `<slot>` in its template and the children being observed are assigned to that slot by the consumer.

```tsx
<slot onSlotchange={this.handleSlotUpdate} />
```

No `addEventListener` or teardown needed — Stencil wires and cleans up the listener with the VDOM.

**Pattern B — `this.el.addEventListener('slotchange', handler)` (imperative)**

Use when children are unslotted direct DOM children read via `querySelectorAll`, not assigned to any rendered `<slot>`. The `slotchange` event still fires on the host element when its light DOM children change.

```ts
componentDidLoad() {
  this.columns = Array.from(this.el.querySelectorAll('bds-table-column'));
  this.el.addEventListener('slotchange', () => {
    this.columns = Array.from(this.el.querySelectorAll('bds-table-column'));
  });
}
```

**Why the distinction matters:** `onSlotchange` on a `<slot>` only fires for nodes assigned to that specific slot. If the component does not render a default `<slot>` in its template (e.g. `bds-table` only renders `<slot name="paginator">`), there is no slot to attach `onSlotchange` to for the column children — Pattern B is required.

**How to apply:** Default to Pattern A whenever the component renders a `<slot>`. Fall back to Pattern B only when children are unslotted configuration carriers queried imperatively.
