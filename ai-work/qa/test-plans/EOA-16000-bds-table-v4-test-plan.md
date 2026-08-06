# Test Plan: EOA-16000 bds-table v4

**Ticket:** EOA-16000
**Components:** `bds-table`, `bds-table-column`, `bds-table-column-group`
**Scope:** Web-components surface only (`packages/boreal-web-components/src/index.html`)
**Status:** Ready — Tasks 1–13 shipped; Task 14 (docs-only) and Task 15 (mutation testing) out of scope for this plan

## Test Environment

- **Browsers:** Chrome (primary), Firefox, Safari — cross-browser mandatory for Task 5 (native DnD + sticky pinning)
- **Tool:** `pnpm dev:components` opens `index.html`
- **Theme:** `proximus`

## Out of Scope

- Task 14 (Storybook docs stories) — no `index.html` scenario
- Task 15 (consolidated mutation testing) — dropped by user decision
- React/Vue wrapper parity
- Responsive toolbar (deferred to unscheduled UX review)
- Tree-shaped row data (re-scoped to master-detail slot)
- Task 13 divider-gating fix (`hasToolbarTableActions`) — unit-tested only (48/48 in `bds-table.toolbar.spec.ts`), no `index.html` scenario

---

## Test Cases

Each test case maps to one section in `packages/boreal-web-components/src/index.html`. Follow the numbered steps already written in that section's `<ol>` — the pass criteria below summarize what must hold.

---

### TC-01: Formatter identity-guard (CellContentCache) — Task 1

**Priority:** P0 | **IDs:** `#cache-table`

Follow index.html steps 1–5.

**Pass:** Status pills render green/red, never flash or re-clone on selection toggle; console shows formatter log only on first render, never again on selection-only re-renders.

---

### TC-02: Row expand/collapse (master-detail slot) — Task 2

**Priority:** P0 | **IDs:** `#expand-no-template`, `#expand-basic`, `#expand-virtual`

Follow index.html steps 1–9.

**Pass:**
- No toggle column without `<template slot="row-detail">`
- Non-virtual: smooth animated reveal/collapse via `bds-transition-collapse`
- Virtual: instant show/hide, no stale detail under a different row
- Selection never changes from clicking the chevron
- Each toggle emits `bdsExpand` with `{ rowId, expanded, row }` (including `history`)
- Enter and Space both toggle a focused chevron via keyboard

---

### TC-03: Row-detail content shapes (non-tabular slotted content) — Task 2

**Priority:** P1 | **IDs:** `#expand-notes`, `#expand-form`, `#expand-checklist`, `#expand-timeline`

Follow index.html steps 1–5.

**Pass:** Smooth first-click animation in every case; no blank gap after collapse; interactive content inside the detail panel (form fields, checkboxes) never triggers outer-table row selection.

---

### TC-04: Custom cell content via `<template slot="cell">` — Task 3

**Priority:** P0 | **IDs:** `#template-cell-basic`, `#template-cell-precedence`, `#template-cell-virtual`

Follow index.html steps 1–4.

**Pass:**
- Basic: each badge reflects its own row's `data-*` values (`<tier> · row <id>`)
- Formatter precedence: formatter wins, exactly one console warning per column
- Virtual recycling: no stale badge content from a previous row after scrolling

---

### TC-05: Column grouping — Task 4

**Priority:** P0 | **IDs:** `#group-interspersed`, `#group-none`

Follow index.html steps 1–6.

**Pass:**
- Two-row grouped header: group bars span correct leaf columns, ungrouped columns blank in row 1
- All row-2 labels at same baseline (no centered-across-both-rows)
- Group `info` tooltip opt-in (shows for "Contact", absent for "Location")
- Dynamic column-inside-group additions picked up live
- No-groups table renders single-row header unchanged

---

### TC-06: Colgroup/width fix regression guard — Task 4

**Priority:** P0 | **IDs:** `#colgroup-fix-grouped`, `#colgroup-fix-ungrouped`

Follow index.html steps 1–3.

**Pass:** Grouped and ungrouped tables render identical explicit column widths and both overflow correctly; pin icon on Phone column sticks while scrolling.

---

### TC-07: Column drag/drop reorder — Task 5

**Priority:** P0 | **IDs:** `#reorder-basic`

Follow index.html steps 1–8.

**Pass:**
- Six-dot handles always visible (not hover-gated)
- Non-adjacent drag updates order in header/body/footer; `bdsColumnReorder` fires with full `order`
- Adjacent-neighbor drag swaps correctly (regression guard for direction-aware insert)
- Keyboard ArrowRight progresses monotonically; boundary is a no-op
- Touch emulation: handles visible/usable without hover
- Pinned column (Email) is not a valid drop target; pin offsets stay correct
- Interspersed-pinned check: unrelated reorder doesn't disturb pinned column's relative order/offset
- Grouped-leaf column (City) is never a valid drag source or drop target
- **Cross-browser:** repeat in Chrome, Firefox, Safari

---

### TC-08: Column resizing — Task 6

**Priority:** P0 | **IDs:** `#resize-basic`, `#resize-virtual`

Follow index.html steps 1–5.

**Pass:**
- Handle invisible by default; visible only on hover or Tab-focus
- Pinned offsets stay correct live during drag (not just after release)
- Keyboard: 8px step per ArrowLeft/ArrowRight from current width; Home resets to original width
- `bdsColumnResize` fires once per gesture on release with correct `{ colKey, width }`
- Virtualized scroll stays stable during resize (no jank, no scroll jump)

---

### TC-09: Right-edge column pinning — Task 7

**Priority:** P0 | **IDs:** `#pin-right-basic`

Follow index.html steps 1–6.

**Pass:**
- Left-pinned (ID) anchors left with right-edge divider; right-pinned (Actions) anchors right with left-edge divider
- Both anchor correctly simultaneously with no overlap during scroll
- Resize of Name column keeps both pinned offsets correct throughout drag
- Right-pinned divider tracks its current leftmost column (pin Role right → Actions loses divider, Role gains it)
- Pinned columns (either direction) never show reorder handles
- Unpinning a non-outermost pinned column leaves no stale offset (Role unpin → flush against Email; ID unpin → same cleanup on left side)

---

### TC-10: `selectAllPages` — Task 8

**Priority:** P0 | **IDs:** `#selectall-default`, `#selectall-crosspage`

Follow index.html steps 1–6.

**Pass:**
- Default (`selectAllPages=false`): select-all scopes to current page only (10 rows) — byte-identical to shipped v3 behavior
- `selectAllPages=true`: select-all selects all 35 rows across all pages
- Page navigation preserves selection state correctly in both modes
- `selectedRowsChange` events log correct row counts

---

### TC-11: `rowSelectable` — Task 9

**Priority:** P0 | **IDs:** `#rowselectable-table`

Follow index.html steps 1–4.

**Pass:**
- Locked rows render disabled checkboxes (visually greyed out, not clickable)
- Clicking a locked checkbox does nothing
- Select-all skips locked rows; header checkbox shows `checked: true` (not indeterminate) when all selectable rows are selected
- Console logs 2 rows selected (not 4)

---

### TC-12: Shift+range selection — Task 10

**Priority:** P0 | **IDs:** `#rangeselect-basic`, `#rangeselect-crosspage`, `#rangeselect-itemsperpage25`

Follow index.html steps 1–9.

**Pass:**
- Shift+click selects contiguous range over underlying data array; non-selectable rows inside range are skipped (4 rows selected, not 5)
- Cross-page range selection spans both pages (8 rows across pages)
- Shift+click never triggers native text-selection highlighting (`window.getSelection().toString()` is empty)
- Non-default `items-per-page="25"` is respected (page 1 shows IDs 1–25)
- Shift+Space on a focused checkbox range-selects identically to shift+click
- `selectedRowsChange` logs correct counts throughout

---

### TC-13: `persistSelection` — Task 11

**Priority:** P0 | **IDs:** `#persist-default`, `#persist-true`

Follow index.html steps 1–4.

**Pass:**
- Default (`persistSelection=false`): selection clears on `data` replacement — shipped behavior unchanged
- `persistSelection=true`: selection preserved across `data` swap when consumer re-passes `selectedRows`
- Selection survives two data swaps (page 2 fetch → page 1 restore)
- No spurious `selectedRowsChange` events when `persistSelection` is true and data changes

---

### TC-14: `rowClickSelects` — Task 12

**Priority:** P0 | **IDs:** `#rowclick-table`, `#rowclick-toggle-btn`

Follow index.html steps 1–8.

**Pass:**
- `rowClickSelects=false`: clicking a plain cell does nothing; checkbox still toggles (shipped behavior)
- `rowClickSelects=true`: clicking a plain cell toggles row selection
- Formatter-rendered button (Edit) never toggles selection in either mode; console logs "Edit clicked"
- Expand chevron never toggles selection in either mode
- Non-selectable (locked) row never toggles via row-click even with `rowClickSelects=true`

---

### TC-15: Opt-in toolbar props (`filterable`/`columnLayoutToggle`) — Task 13

**Priority:** P0 | **IDs:** `#task13-subheading-only`, `#task13-filterable-loading`, `#task13-both`

Follow index.html steps 1–6.

**Pass:**
- Subheading-only table: zero toolbar-right DOM (no hollow flex container)
- Filterable + loading: only Filter button skeleton appears (no Column-visibility skeleton)
- Toggle loading off: skeleton replaced by real clickable Filter button
- Both-true table: both buttons render in one `bds-button-group`
- Clicking Filter logs `bdsFilter`; clicking Column-visibility logs `bdsTableLayout`

---

### TC-16: Toolbar corner-rounding fix — Task 13

**Priority:** P1 | **IDs:** `#corner-interactive`, `#corner-case1`, `#corner-case2`, `#corner-case3`, `#corner-case4`

Follow index.html steps 1–4.

**Pass:** All 4 static cases plus the interactive toggle render correct corner radii — search-bar + button group merge into one seamless pill where applicable; search-alone case is fully rounded on all four corners.

---

## Summary

| # | Test | Priority | IDs |
|---|------|----------|-----|
| TC-01 | Formatter identity-guard | P0 | `#cache-table` |
| TC-02 | Row expand/collapse | P0 | `#expand-no-template`, `#expand-basic`, `#expand-virtual` |
| TC-03 | Row-detail content shapes | P1 | `#expand-notes`, `#expand-form`, `#expand-checklist`, `#expand-timeline` |
| TC-04 | Custom cell content (`<template slot="cell">`) | P0 | `#template-cell-basic`, `#template-cell-precedence`, `#template-cell-virtual` |
| TC-05 | Column grouping | P0 | `#group-interspersed`, `#group-none` |
| TC-06 | Colgroup/width fix | P0 | `#colgroup-fix-grouped`, `#colgroup-fix-ungrouped` |
| TC-07 | Column reorder | P0 | `#reorder-basic` |
| TC-08 | Column resizing | P0 | `#resize-basic`, `#resize-virtual` |
| TC-09 | Right-edge pinning | P0 | `#pin-right-basic` |
| TC-10 | selectAllPages | P0 | `#selectall-default`, `#selectall-crosspage` |
| TC-11 | rowSelectable | P0 | `#rowselectable-table` |
| TC-12 | Shift+range selection | P0 | `#rangeselect-basic`, `#rangeselect-crosspage`, `#rangeselect-itemsperpage25` |
| TC-13 | persistSelection | P0 | `#persist-default`, `#persist-true` |
| TC-14 | rowClickSelects | P0 | `#rowclick-table` |
| TC-15 | Opt-in toolbar props | P0 | `#task13-subheading-only`, `#task13-filterable-loading`, `#task13-both` |
| TC-16 | Toolbar corner-rounding | P1 | `#corner-interactive`, `#corner-case1`–`#corner-case4` |

**Total: 16 test cases** (14 P0, 2 P1) — all backed by `index.html` scenarios.
