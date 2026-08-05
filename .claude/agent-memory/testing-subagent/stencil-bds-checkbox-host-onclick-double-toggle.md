---
name: stencil-bds-checkbox-host-onclick-double-toggle
description: bds-checkbox attaches its own click handler to <Host>, so dispatching a real 'click' plus a manual 'bdsChange' CustomEvent on the same checkbox in a test double-toggles selection state
metadata:
  type: project
---

`bds-checkbox.tsx` renders `<Host onClick={this.handleClick}>`, and `handleClick` calls `toggle()` which flips `checked` and emits a real `bdsChange` itself. This means dispatching a raw `MouseEvent('click', { bubbles: true })` directly on a `bds-checkbox` element in a spec file already produces a genuine `bdsChange` emission as a side effect — no manual event needed.

**Why this matters:** while testing `bds-table`'s `rowClickSelects` prop (EOA-16000 Task 12), a test helper that dispatched both a synthetic `click` (to simulate a real user click bubbling to the row's `onClick` handler) AND a manual `CustomEvent('bdsChange')` (to simulate the checkbox's own change notification) caused the row's checkbox toggle to fire `handleRowSelect` twice — once from the real click's own `bdsChange` emission, once from the manual dispatch — which cancelled the toggle back to unselected. The test failed with an empty `selectedRows` array where `['1']` was expected, with no exception thrown, which made the root cause non-obvious.

**How to apply:** in `bds-table` (or any component consuming `bds-checkbox` as a child in `newSpecPage`), simulating "a user clicks the checkbox" only requires `.click()` (or `dispatchEvent(new MouseEvent('click', { bubbles: true }))`) on the checkbox element — do not also manually dispatch `bdsChange` afterward, that double-fires the parent's `onBdsChange` handler. The pre-existing `clickCheckbox()` helper in `bds-table.selection.spec.ts` (which dispatches only `bdsChange`, no `click`) is a different, narrower simulation — appropriate when a test wants to bypass `bds-checkbox`'s own click plumbing entirely and jump straight to the change notification. Do not blend the two dispatch styles on the same checkbox in one interaction.

Likely generalizes beyond `bds-table`: any `bds-checkbox`-consuming component test that dispatches both event types on the same interaction is at risk of the same silent double-toggle. Candidate for promotion to `.agents/memory/` if another component's spec suite hits the same pattern.
