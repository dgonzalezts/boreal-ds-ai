---
name: bds-table-reorder-drag-verification
description: Playwright mouse-based drag (dragTo or manual mousedown/move/up) never triggers bds-table's native HTML5 column reorder — must dispatch synthetic DragEvents instead; also isColumnReorderable() rejects pinnable columns as drop targets
metadata:
  type: project
---

`bds-table.tsx`'s column-reorder feature (`handleColumnDragStart`/`DragOver`/`Drop`/`DragEnd`) uses **native HTML5 drag-and-drop** (`th.draggable = true` set imperatively in `handleReorderMouseDown`, plus `ondragstart`/`ondragover`/`ondrop` DOM events) — not a custom pointer-based drag implementation.

**Consequence for QA automation:** neither `playwright-cli drag <ref> <ref>` (locator `.dragTo()`) nor manual `mousemove`/`mousedown`/`mousemove`/`mouseup` sequences trigger native HTML5 DnD in headless Chromium via CDP — this is a known CDP/browser limitation, not a bug in the component. Confirmed by testing both approaches against `ReorderableColumns` (EOA-16000 Task 5 QA, 2026-08-06): zero `dragstart`/`drop` events fired, column order never changed, no console errors either (the attempt just silently did nothing).

**Working verification method:** dispatch synthetic `DragEvent`s directly via `page.evaluate`/`run-code` against the frame document, reusing one `DataTransfer` object across the sequence:
```js
const dt = new DataTransfer();
src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }));
tgt.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
tgt.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
src.dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: dt }));
```
This invokes the component's real listeners (`handleColumnDragStart` etc.) synchronously and does reflect in both the `bdsColumnReorder` action payload and the live DOM column order (`th[data-col-key]` order).

**Second gotcha, easy to misdiagnose as a bug:** `isColumnReorderable(col)` returns `col.reorderable && !col.pinnable && !groupedColKeys.has(col.colKey)` — a column with **both** `pinnable` and `reorderable` set (e.g. `ReorderableColumns` story's Email column) can never be a valid drop target or drag source; `dragover`'s `preventDefault()` never fires and `drop` silently no-ops. This is correct, intentional behavior (pinning and reordering are mutually exclusive), not a wiring regression — pick a plain `reorderable`-only column (e.g. the Role column) as the drag target when verifying reorder in this story.
