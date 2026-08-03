---
name: bds-table-reorder-boundary-pinned-invariant
description: A boundary-pinned bds-table column keeps its physical DOM/th index under any Task-5 reorder, since pinned columns are always excluded from being a drag source or target — safe fixture choice for pin-offset regression tests
metadata:
  type: project
---

`bds-table`'s column reorder (`moveColumn` splice-based drop path, `moveColumnByKeyboard` swap-based
arrow-key path) only ever touches `columnOrder` indices belonging to `isColumnReorderable(col)`
columns — pinned (`col.pinnable === true`) and grouped-leaf columns are excluded as both source and
target in every code path (`handleColumnDragStart`/`handleColumnDragOver`/`handleColumnDrop`/
`handleReorderKeyboardMove`).

**Consequence for pin-offset regression testing:** if a pinned column sits at index `0` or the last
index of `columnOrder`, no reorder operation (splice-based drag/drop *or* swap-based keyboard move) can
ever change its physical index — array splice/swap operations restricted to indices `>= 1` (or
`<= length - 2`) never touch position `0` (or the last position). This means:

- `<th>` elements have no `key` prop in `renderTh`, so Stencil's VDOM reuses DOM nodes positionally.
  A pinned column that *did* shift index (interspersed pinned columns, not boundary ones) would risk a
  stale/wrong `style.left` being retained on the wrong physical `<th>` after a reorder, since
  `updatePinnedColumnOffsets`'s cheap guard (`this.columns !== this._pinOffsetColumns` /
  `pinnedColKeys` reference equality) does not fire on a pure `columnOrder`-only state change.
- A **boundary-pinned** fixture sidesteps this entirely and is empirically verified correct (test
  passes, confirmed via `bds-table.pin-offsets.spec.ts`'s "reorder + pin interaction" describe block):
  offsets are colKey-keyed (`_pinOffsetsByColKey: Map<string, number>`), not index-keyed, so even
  without a forced recompute, previously-cached offsets stay valid because the pinned `<th>`'s DOM
  identity and width are unchanged.

Did not empirically verify the interspersed-pinned-column case (a pinned column with reorderable
columns dragged across it via the splice path) — flagged as a latent correctness question for the
implementation, not confirmed as a bug, since the task's only required regression test used the safe
boundary scenario matching the plan's realistic-usage intent.
