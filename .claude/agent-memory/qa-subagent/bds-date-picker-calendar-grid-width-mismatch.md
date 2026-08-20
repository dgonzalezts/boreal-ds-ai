---
name: bds-date-picker-calendar-grid-width-mismatch
description: RESOLVED — bds-calendar-grid's table rendered 256px wide (border-spacing edge gaps) inside bds-date-picker's popover instead of 248px; fixed via negative margin on the table plus a recalculated header width; re-verified 2026-08-19
metadata:
  type: project
---

**RESOLVED as of 2026-08-19 re-check.** Fix applied to `bds-calendar-grid.scss`: `margin: 0 calc(-1 * $boreal-spatial-gap-2xs)` on `table` (cancels one `border-spacing` edge gap per side) plus `.bds-calendar-grid__header` width changed from `$grid-width` (256px) to a new `$grid-visual-width` (248px). Re-verified in `#date-picker-default` and the dedicated `#calendar-grid-states` scenario: the actual rendered day-cell span (first cell's left edge to last cell's right edge — the only visually apparent content, since `border-spacing` also leaves 4px of invisible padding inside the table's own border box before/after the first/last cell) is exactly 248px and flush with the popover-content's inner padding edges on both sides (24px/24px, confirmed via `getBoundingClientRect` on `popover-content` vs. the first/last `<td>`, not the `<table>` element itself — the `<table>`'s own border box is still 256px, extending 4px past the padding edge on each side, but that's invisible border-spacing padding, not rendered content, so it's not a visual defect). Header row width (248px) matches the cell span exactly (0px offset). 0 new console errors. No regression in cell size (32px), inter-cell gaps (4px horizontal / 2px vertical), or selected/today/outside-month states.

**Measurement gotcha for future re-checks:** don't measure `table.getBoundingClientRect()` against the padding box directly — a `border-collapse: separate` table with `border-spacing` always has invisible edge-padding baked into its own border box, so the table element's own rect will look "off" from the intended content width even when the fix is correct. Measure the first/last `<td>` (the actual visible content) instead.

Originally found during EOA-16692 `bds-date-picker` Task 19 QA (2026-08-19).

Task 19 set `bds-popover`'s `width={296}` and `--popover-content-padding: 12px 24px` on the assumption that the popover content area is `296 - 24 - 24 = 248px` wide, exactly matching `bds-calendar-grid`'s own width from a prior task. In the live `#date-picker-default` playground scenario, `bds-calendar-grid`'s actual rendered width (via `getComputedStyle`) is **256px**, not 248px — 8px wider than the math assumes.

Effect: the grid sits flush against the popover's left edge (24px gap, correct) but only 16px from the right edge (8px short of the intended 24px) — a visible asymmetric gap, not the flush-both-sides result the task's acceptance criteria described. Confirmed via `getBoundingClientRect()` comparison of `.popover-content` vs `bds-calendar-grid` (content inner box: 264–512px; grid actual box: 264–520px) and cross-checked visually via screenshot. No horizontal scrollbar appears (`.popover-content` has `overflow-x: visible`, `scrollWidth === clientWidth === 296`), so the 8px overflow silently eats into the intended right padding rather than causing a layout break.

**Why:** `bds-calendar-grid`'s width is owned by a prior task's own component CSS, not by `bds-date-picker.scss` or `bds-popover.scss` — Task 19 only set the *container* padding/width, it did not (and per scope, could not) touch `bds-calendar-grid`'s internal sizing.

**How to apply:** This is a real visual discrepancy worth a follow-up ticket/task — either shrink `bds-calendar-grid` to 248px or widen the popover/padding math to fit 256px (e.g. popover width 304px, or content padding 20px/24px asymmetric-safe values). Do not treat "296 = 24 + 248 + 24" as verified-in-practice math for this component without re-checking `bds-calendar-grid`'s actual computed width first — it drifted from the assumed value at least once already.
