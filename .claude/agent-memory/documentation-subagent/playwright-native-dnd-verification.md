---
name: playwright-native-dnd-verification
description: How to manually verify bds-table's native HTML5 drag/drop reorder in a live Storybook instance via Playwright.
metadata:
  type: project
---

**Playwright's mouse-based drag (`playwright-cli drag`, `dragTo`) does not reliably trigger native HTML5 drag-and-drop** on `bds-table`'s reorder handles — the handle only arms `draggable` on `mousedown`, and the subsequent native `dragstart`/`dragover`/`drop` sequence isn't produced by a synthetic mouse drag. To verify native DnD reorder live, use `playwright-cli -s=<name> eval` (the Playwright MCP server is disabled — drive the browser via the `playwright-cli` Bash CLI instead) to manually dispatch the event sequence inside the Storybook iframe's `contentDocument`:

```js
const md = new MouseEvent('mousedown', { bubbles: true });
icon.dispatchEvent(md); // arms th.draggable = true
const dt = new DataTransfer();
th.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }));
targetTh.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
targetTh.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
th.dispatchEvent(new DragEvent('dragend', { bubbles: true, cancelable: true, dataTransfer: dt }));
```

Read the resulting order on a **separate** `playwright-cli eval` call, not inline in the same script — Stencil re-renders in a microtask, so DOM read back synchronously in the same evaluate still shows the pre-drop order even though the `bdsColumnReorder` event already fired with the correct new order.

Note: an earlier version of `bds-table.tsx`'s `moveColumn` had a real bug where dropping a column onto its immediate right neighbor was a silent no-op (insert-before-target semantics landed the source back in its original slot). This was fixed (direction-aware insert: before target when moving left, after target when moving right) and covered by a regression test in `bds-table.reorder.spec.ts` — dropping onto any neighbor, in either direction, now produces a visible reorder.
