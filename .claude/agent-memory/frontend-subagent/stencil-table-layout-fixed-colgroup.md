---
name: stencil-table-layout-fixed-colgroup
description: table-layout:fixed only consults a table's first <tr> for column widths; multi-row <thead> (e.g. bds-table-column-group) silently breaks per-th inline widths — fix with <colgroup>/<col>, which is exempt from the first-row restriction
metadata:
  type: project
---

`bds-table` (`packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`) uses `table-layout: fixed` and set each leaf column's `width` as an inline style on the leaf-row `<th>` (in `renderTh`). Per CSS 2.1 §17.5.2.1, `table-layout: fixed` only consults the table's **first `<tr>`** to determine column widths, regardless of which row a `<th>`/`<td>` with an explicit width actually lives in.

When `bds-table-column-group` causes `renderHeader()` to emit a two-row `<thead>` (group row + leaf row), the leaf `<th>`s carrying `width` move to row 2 — so the browser's fixed-layout algorithm silently ignores every leaf column's width the moment any group exists. All columns collapse to an equal share of the container width, and pinned-column sticky offsets never engage since the table stops overflowing.

**Fix**: `<col>` elements inside a `<colgroup>` are exempt from the "first row only" restriction — width applies regardless of header row structure. Added `renderColgroup()` to `bds-table.tsx`, rendered unconditionally as the first child of `<table>` (before `renderHeader()`), with one `<col>` per rendered `<th>`/`<td>` in the exact same left-to-right order: checkbox column (`selectable`) first, then expand-toggle column (`hasRowDetail && !this.loading` — note the loading guard, since that column disappears entirely during the skeleton-loading render pass), then one `<col>` per entry in `this.columns` with the same `width` as the leaf `<th>`.

**Why the order/conditions matter**: the `<colgroup>` col count and order must exactly match the actual per-row cell count for *that specific render pass* — `this.loading` changes which placeholder columns exist (the expand-toggle column vanishes when loading; the checkbox column does not). Getting this wrong causes the browser to misassign widths to the wrong columns rather than erroring.

Verified via Playwright: grouped and ungrouped tables with identical explicit widths now render pixel-identical column widths and identical `wrapper.scrollWidth`/`clientWidth` overflow behavior.

See also: [[stencil-sass-inject-global-paths-constraint]] for other `bds-table`-adjacent SCSS/rendering gotchas.
