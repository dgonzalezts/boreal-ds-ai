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
