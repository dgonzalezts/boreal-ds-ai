# Native drag-and-drop child elements cause dragenter/dragleave churn (Windows cursor flicker)

Native HTML5 drag-and-drop events (`dragenter`, `dragleave`, `dragover`) follow the same hit-testing rules as ordinary pointer events. When a drag source or drop target element contains nested interactive children (icons, labels, a resize handle, a six-dot drag handle), the pointer moving over those children **during an active drag-hover** causes the browser to fire `dragleave` on the parent (as the pointer "leaves" it to enter the child) immediately followed by `dragenter` again — repeatedly, for every child boundary crossed.

Each of these transitions is a fresh opportunity for the negotiated `dropEffect` to momentarily revert to its default before being re-set by a `dragenter`/`dragover` handler, which can manifest as the cursor visibly flickering between the "not-allowed" and "valid drop target" icons during an otherwise-valid drag. This is most visible on **Windows** (distinct cursor glyphs for the two states) and effectively invisible on macOS (both states render as a plain arrow), so a report of "cursor flickers during drag, only on Windows" should be treated as this class of bug rather than dismissed as unreproducible.

Found on `bds-table`'s column reorder six-dot-handle `<th>` elements, which contain a resize handle, label text, sort/pin icons, and the drag handle itself as children.

**Fix**:

1. Apply `pointer-events: none` to **all descendants** of the draggable/drop-target element while a drag is actively in progress (e.g. `&--reorder-dragging th * { pointer-events: none; user-select: none; }`), toggled via a state class. Since native drag-event hit-testing follows pointer-events rules, this makes the parent element itself the *sole* possible target for all drag events for the duration of the drag, eliminating the child-hover churn entirely rather than patching around it.
2. As defense-in-depth, guard `dragleave` handlers with a `relatedTarget`-containment check (`if (th.contains(e.relatedTarget as Node)) return;`) so a leave-to-a-still-contained-child never clears a highlight state it shouldn't.

**Critical constraint on where to toggle the dragging-state class**: it must be added on the native `dragstart` event and removed on the native `dragend` event — never on `mousedown`/`pointerdown`. `dragstart`/`dragend` are a browser-guaranteed pair (the browser always fires `dragend` after `dragstart`, regardless of how the drag concludes: successful drop, drop on an invalid target, or an Escape-cancelled drag). `mousedown` does **not** guarantee a native drag actually starts — a simple click, or movement below the browser's drag-initiation threshold, never fires `dragstart` and therefore never fires `dragend` either, which would leave the dragging-state class (and its `pointer-events: none`) permanently stuck on every other interactive element in the table until an unrelated successful drag happens to trigger cleanup.

**Testing note**: the shared mock-doc drag/drop helper (`src/utils/testing/mocks/dragDrop.ts`'s `createDragEvent()`) needed extending with an optional third `relatedTarget` parameter to test the `dragleave` guard above — added as backward-compatible (existing 2-argument call sites unaffected).

**Source**: EOA-16000 `bds-table` v4 column reorder cursor-flicker fix (Windows-reported bug).
