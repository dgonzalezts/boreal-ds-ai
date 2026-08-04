---
name: stencil-table-column-resize-pattern
description: bds-table column resizing (EOA-16000 Task 6) — colgroup as resize target, imperative-write-before-throttled-state pattern, single-key dispatch branching
metadata:
  type: project
---

Column resizing (`bds-table-column.resizable`, `bdsColumnResize`) resizes the `<colgroup>`'s `<col>` element, not the `<th>`. Per [[stencil-table-layout-fixed-colgroup]], `table-layout: fixed` only reads per-`<th>` inline widths from the table's first `<tr>` — with a `<colgroup>` present, the `<col>` is authoritative. `renderColgroup` now stamps `data-col-key` on each `<col>` so `resizeColEl(colKey)` can look it up.

Resize writes width to both `<col>` and `<th>` inline styles **imperatively** (`applyColumnWidth`), synchronously on every `pointermove` — no throttling on the DOM write itself, only on the state commit. `scheduleResizeRecompute` mirrors `scheduleVirtualRerender`'s microtask-flag shape exactly and, inside the throttled callback, updates `@State() columnWidths` and calls `updatePinnedColumnOffsets(true)`. Because the DOM write already happened synchronously before the microtask fires, `offsetWidth` reads inside the offset recompute are correct regardless of whether Stencil's own render cycle has caught up to the state change yet — sidesteps a render-timing race that would otherwise read stale widths.

`KeyboardController.set(key, handler)` only holds one handler per key (Map, not a list). Column reorder already owned global `ArrowLeft`/`ArrowRight` bindings. Adding a second bound-to-the-same-key feature required a branching dispatcher (`handleColumnArrowKey`) that checks `e.target.closest('.bds-table__resize-handle')` first and falls back to the reorder handler — not two `.set()` calls, which would silently drop one.

Reset-to-auto width (`Home` key) is `columnWidths[colKey] = col.width` (often `''`), read back via `columnWidths[col.colKey] ?? col.width` — nullish coalescing, not `||`, so an explicit `''` override is distinct from "never resized" and correctly falls through to auto-sizing.
