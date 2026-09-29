---
name: roving-tabindex-demotes-only-provided-items
description: "applyRovingTabindex only demotes cells present in the array it is given; grids that filter disabled cells to null can leave a stale tabindex=0 on a now-disabled cell (two roving stops). Demote from the rendered DOM instead."
---

**`applyRovingTabindex(items, activeIndex)` only demotes items that are in `items`.** In `packages/boreal-web-components/src/utils/a11y/keyboard/focus/roving-tabindex.ts` it locates the current stop with `items.findIndex(item => item.getAttribute('tabindex') === '0')` and, when `prevIndex !== -1`, demotes `items[prevIndex]`. Any element that currently holds `tabindex="0"` but is **not** in the passed array is never touched. `KeyboardController.rovingTabindex()` → `applyRovingTabindex()` is the same code path used by `bds-calendar-grid` (`this._keyboard.rovingTabindex(flatItems, index)`).

**Failure mode.** A grid that builds its items array by filtering disabled cells out (mapping them to `null`) can leave a stale `tabindex="0"` on a cell that has since become disabled. When the array no longer contains that cell, `findIndex` returns `-1` (or finds a different item), the stale stop survives, and the grid ends up with **two roving-tabindex stops**. `bds-calendar-grid`'s `getMonthPickerGridItems()` / `getYearPickerGridItems()` map disabled cells to `null` (`bds-calendar-grid.tsx:745`, `:815`), so a month/year picker cell that disables while it holds the stop produced exactly this.

**The invariant to protect:** a roving-tabindex grid must expose **exactly one tabbable stop (`tabindex="0"`), and never on a disabled cell**. Specs encode it, e.g. `bds-calendar-grid.keyboard.spec.ts` → "keeps exactly one roving-tabindex stop on the focused cell after arrow traversal", and `bds-calendar-grid.quickpicker.spec.ts` → "traverses month cells with the arrow keys keeping exactly one roving-tabindex stop".

**Recommended fix shape: demote from the rendered DOM, not from the filtered items list.** Before applying the new stop, clear the tabindex of every rendered cell via a DOM query, then set the single new stop. `bds-calendar-grid.focusPickerCellByKey()` does this (`bds-calendar-grid.tsx:651`):

```
for (const cellEl of this.el.querySelectorAll<HTMLTableCellElement>('td.bds-calendar-grid__picker-cell')) {
  cellEl.setAttribute('tabindex', '-1');
}
this._keyboard.rovingTabindex(flatItems, index);
```

The day-grid path avoids the bug for the same reason — it demotes from the DOM via `markTabbableCell()`, which iterates every `_cellRefs` value rather than a filtered array.

**General takeaway:** whenever a roving-tabindex items array is filtered (disabled, unmounted, or out-of-range cells removed), the demote step must not rely on that same filtered array. Demote against the rendered DOM, or the removed element keeps its stale stop.

**Related:** the linear-navigation fallback has the mirror-image hazard — when `initial === -1` it falls back to index `0`, which can assign `tabindex="0"` to a disabled first item (`ai-work/reviews/2026-06-04-commit-0b538776-feature-eoa-13735-update-components-keyboard-navigation-review.md`). Same invariant, different code path.
