---
name: bds-table-resize-throttle-spy-target
description: bds-table's componentDidRender calls updatePinnedColumnOffsets() unforced on every render, so spying on raw call count over-counts a throttle assertion — spy on the th[data-pinned] querySelectorAll instead
metadata:
  type: project
---

`bds-table.tsx`'s `componentDidRender()` calls `this.updatePinnedColumnOffsets()` (unforced, `force=false`) after every single render, in addition to the forced (`force=true`) calls made from `scheduleResizeRecompute()`'s throttled microtask callback and the `ResizeObserver` callback. `jest.spyOn(instance, 'updatePinnedColumnOffsets')` therefore over-counts when asserting "at most once per throttled frame" for the Task 6 resize drag — a `columnWidths` state change triggers a re-render, whose `componentDidRender` adds an extra unforced call that has nothing to do with the throttle being tested.

The unforced call is cheap: its internal guard (`force || pinnedColKeysChanged || columnsChanged || columnOrderChanged`) skips the `querySelectorAll('th[data-pinned]')` walk entirely when nothing relevant changed, so it never queries. This is exactly the mechanism the existing "phase 1 guard skips the expensive recompute on a virtualizer-only re-render" test in `bds-table.pin-offsets.spec.ts` already exploits.

**How to apply:** when asserting a throttled-recompute call count for `bds-table` resize/pin/reorder work, spy on `root.querySelectorAll` and filter `calls.filter(([selector]) => selector === 'th[data-pinned]').length` instead of spying on `updatePinnedColumnOffsets` directly — the query-count reflects only the forced (real work) calls. Verified in `bds-table.resize.spec.ts`'s pointer-drag throttle test during EOA-16000 Task 6.
