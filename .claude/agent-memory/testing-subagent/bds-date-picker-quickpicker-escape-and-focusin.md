# bds-date-picker quick-picker: Escape routing + `onFocusin` scoping (EOA-17662 Task 50)

Two non-obvious mechanics found while unit-testing the Phase 9 month/year quick-picker.

## Escape must be asserted across the grid → popover boundary

`bds-popover` attaches a **document-level** `keydown` Escape handler whenever it is visible
(`bds-popover.tsx` `attachEscapeHandler`, `document.addEventListener('keydown', …)`, gated on
`isVisible`). `bds-calendar-grid.handleGridEscape` deliberately `stopPropagation()`s when
`view !== 'days'`, so a first Escape from a picker view returns to the day grid **without**
closing the popover; from day view it returns without stopping, so the event bubbles to
`document` and the popover closes.

Test consequence: a grid-level spec can only assert "no navigation + overlay gone" — the
"popover stays open" half needs the orchestrator. Reliable pattern (mirrors
`bds-date-picker.keyboard.spec.ts`): open via `ctx.field.click()` (NOT
`popover.openPopover()`, which does not drive `popoverVisible`/`isVisible` in mock-doc),
clear `HTMLElement.prototype.hidePopover` (from `setupPopoverMocks()`), dispatch a real
`KeyboardEvent('keydown', { key: 'Escape', bubbles: true })` on the grid, assert
`hidePopover` **not** called; dispatch again from the now-day view and assert it **was**
called.

## `handleDayFocusIn` guard branches are unreachable from a header-focusin test

`onFocusin` is bound to the **day `<table>`** (`bds-calendar-grid.tsx` render), but the
header (with the label/prev/next buttons) is a **sibling** of the table's container, not
inside the table. So dispatching `focusin` on `.bds-calendar-grid__header bds-button` never
reaches `handleDayFocusIn` — the existing "does not emit bdsDayFocus when a header nav
control receives focus" test passes for the wrong structural reason and leaves the
`isoDate == null` guard (`:226`) uncovered. To cover it, dispatch `focusin` on an element
*inside* the table that is not a day cell (e.g. a `<th>`); the `!isCurrentMonth || isDisabled`
guard (`:231`) needs `focusin` on an outside-month/disabled day cell. Left uncovered in
Task 50 as out of the quick-picker scope (statement coverage already ≥ 90%).
