# bds-calendar-grid: prop-only re-render leaves two `tabindex="0"` cells

Task 40 wired `@Watch('grid') handleGridChange` + `componentDidUpdate` into
`bds-calendar-grid.tsx` to re-establish the roving-tabindex stop after a full month
re-render (every `<td>` remounts with `tabindex="-1"`, killing Tab reachability).

The `componentDidUpdate` else-branch (`targetDay == null`) calls
`markTabbableCell(getPriorityFocusCell())`, which only **sets** `tabindex="0"` on the target
and never demotes the previously-tabbable cell.

- On a `grid`-prop change the cells remount (fresh `tabindex="-1"`), so the invariant holds.
- On a **prop-only** re-render (e.g. `selectedDate` changing after a day click, or a hover
  preview change) the cells are keyed by `isoDate` and reused; Stencil's vdom skips the
  unchanged `tabIndex={-1}` write (`oldValue === newValue`), so the old stop keeps
  `tabindex="0"` and a second one is added.

Observed during EOA-17662 Task 43: render Feb 2026 with no selection (stop = Feb 1), then
`element.selectedDate = '2026-02-15'` + `waitForChanges()` → tabbable cells are `['1','15']`.

Testing implication: the initial-render invariant (`basics.spec.ts` "exactly one roving stop")
does **not** cover this path. A regression test must change a non-`grid` prop and then assert
`querySelectorAll('td[role="gridcell"][tabindex="0"]')` still has length 1. Deferred as a
`frontend-subagent` fix (failure-mode row FM-86) — do not add the failing test until the fix
lands, per the FM-03 precedent.

## Same leak, month quick-picker paging path (2026-09-28)

The month-view paging focus fix (`focusMonthViewCell` + `getNearestEnabledMonthCell`) moves DOM
focus correctly, but leaves the same two-stop leak behind when the previously roving month becomes
**disabled** in the new year. `focusPickerCellByKey` builds its `flatItems` from
`getMonthPickerGridItems`, which maps disabled cells to `null`, so `applyRovingTabindex`
(`KeyboardController.ts:479-484` → `roving-tabindex.ts:18-25`) cannot find the old `tabindex="0"`
cell to demote it. Month cells are keyed by `cell.month`, so the old `<td>` persists across the
year change and keeps its imperatively-set `tabindex="0"` while the newly focused enabled cell
gets a second one.

- Fixture that reveals it: `min=2026-06-01` / `max=2027-03-31`, month view, `Jun` focused,
  `PageDown` → `document.activeElement` is correctly `Mar` (the focus contract is met) but the
  `tabindex="0"` month cells are `['Mar','Jun']`, with `Jun` carrying `aria-disabled="true"`.
- Logged as `ai-work/testing/failure-modes/bds-calendar-grid.md` FM-CG-21 (`pending-decision`,
  option A = demote all prior picker stops / option B = out of scope). Do not add the failing
  assertion to `bds-calendar-grid.quickpicker.spec.ts` until the user rules and the fix lands
  (FM-03/FM-86 precedent).

## Resolution (2026-09-28 — FM-CG-21 ruled "fix it", fix landed)

`focusPickerCellByKey` now demotes every rendered picker cell before delegating to
`rovingTabindex`:

```ts
for (const cellEl of this.el.querySelectorAll<HTMLTableCellElement>('td.bds-calendar-grid__picker-cell')) {
  cellEl.setAttribute('tabindex', '-1');
}
this._keyboard.rovingTabindex(flatItems, index);
```

The regression guard is the pair of assertions `expect(tabbablePickerCells(element)).toEqual([target])`
plus `expect(disabledTabbablePickerCells(element)).toHaveLength(0)` (a new helper querying
`td.bds-calendar-grid__picker-cell[tabindex="0"][aria-disabled="true"]`). Assert both after a picker
page — the `toEqual([target])` alone catches the leak, but the explicit disabled query is the
FM-CG-21 guard the row names. Tests now cover bounded PageDown (Jun 2026 + `PageDown`) / bounded
PageUp (Mar 2027 + `PageUp`) / unbounded PageUp (new test) plus the two year-window focus tests.
Pre-fix, the bounded tests fail (two stops `['Mar','Jun']`); do not chase the year-view equivalent —
a year cell's `isDisabled` derives only from `min`/`max`, which never change during paging, so the
year-picker path cannot transition an enabled stop into a disabled one (its assertions are a
one-stop sanity guard only).

## `generateMonthPickerGrid` enabled months are always contiguous

`isDisabled` is `cellEnd < min || cellStart > max`, with `cellStart`/`cellEnd` increasing across
months 0-11 — so the enabled set is always a single contiguous run (or empty). Consequence: a
nearest-enabled tie-break (`getNearestEnabledMonthCell`'s `(cell.month - preferredMonth) *
direction > 0`) can **never** be reached through a real `min`/`max` range. Exercise it by calling
the private helper directly via `page.rootInstance` with a hand-built `MonthPickerCell[]` (e.g.
only months 3 and 7 enabled around preferred 5), not by constructing a range.
