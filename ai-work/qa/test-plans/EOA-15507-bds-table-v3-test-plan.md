# Test Plan: EOA-15507 bds-table v3 — Dataset Mode, Column Footer, Server-Side/Loading, Virtualization, Guardrail

## Executive Summary

**Feature:** bds-table v3 — Dataset Mode, Column Footer, Server-Side/Loading, Virtualization, Large-Dataset Guardrail
**Ticket:** EOA-15507
**Components Under Test:** `bds-table`, `bds-pagination`, `bds-table-column`
**Testing Scope:** Functional, UI/Visual, Integration, Regression, Performance (DOM node bounding)
**Plan Status:** Ready (v3 plan completed 2026-07-23, all 11 tasks shipped; Task 12 mutation testing deferred to `EOA-16000`)

This test plan covers the 11 shipped tasks from the v3 implementation plan (`ai-work/plans/EOA-15507-bds-table-v3.md`). The work spans:

- `rows` prop with internal pagination and cross-page selection (Task 1)
- Slot-based column footer row, including pinned-column offset sync (Tasks 2–4)
- Server-side mode with a full inline skeleton loading visual (Tasks 5, 5b–5e)
- Opt-in row virtualization via `@tanstack/virtual-core`, sticky header, variable-height rows (Task 7)
- Pin-offset throttling during virtualized scroll, including resize correctness (Task 8)
- `maxClientRows` large-dataset guardrail with auto-enabled virtualization (Task 10)
- Documentation for dataset mode, footer, server-side/loading, virtualization, and the guardrail (Tasks 1b, 6, 9, 11)

Every functional test case below reproduces the manual-test scenarios already built and verified in `packages/boreal-web-components/src/index.html` during implementation — this plan formalizes them into a repeatable QA artifact.

---

## Test Scope

### In Scope

| Task | Component                | Feature                                                                 |
| ---- | ------------------------- | ------------------------------------------------------------------------ |
| 1    | bds-table, bds-pagination | `rows` prop, internal pagination, cross-page selection                  |
| 1b   | bds-table (docs)          | Documentation for `rows` prop / dataset mode                            |
| 2–4  | bds-table                 | Slot-based column footer row, pinned-footer offset sync                 |
| 5    | bds-table                 | Server-side mode + inline skeleton loading visual                       |
| 5b   | bds-table, bds-pagination | Paginator skeleton during loading                                       |
| 5c   | bds-table                 | Toolbar-right skeleton completeness                                     |
| 5d   | bds-table                 | Loading-visual refinements (row-count sync, footer skeleton)            |
| 5e   | bds-table, bds-pagination | Stale pagination prop fix, remainder-aware skeleton rows, conflict warning |
| 6    | bds-table (docs)          | Documentation for server-side mode and loading state                    |
| 7    | bds-table                 | Opt-in row virtualization (`virtual` prop)                              |
| 8    | bds-table                 | Pin-offset throttling during virtualized scroll                         |
| 9    | bds-table (docs)          | Documentation for row virtualization                                    |
| 10   | bds-table                 | `maxClientRows` large-dataset guardrail, auto-enabled virtualization    |
| 11   | bds-table (docs)          | Documentation for the guardrail                                         |

### Out of Scope

- Column grouping, drag/drop column reorder, column resizing, row expand/collapse (moved to v4, `EOA-16000`)
- Declarative `<template>`-based custom cell content (moved to v4, `EOA-16000`)
- `checkboxSelectionVisibleOnly`, `isRowSelectable`, shift+range selection, `keepNonExistentRowsSelected`, `disableRowSelectionOnClick` (moved to v4, `EOA-16000`)
- Opt-in filter/column-visibility toolbar buttons (moved to v4, `EOA-16000`)
- Responsive toolbar below 744px (moved to v4, `EOA-16000`; blocked on UX/UI review)
- Mutation testing gate (deferred to `EOA-16000`, final task — not manually testable, out of this plan's scope by nature)
- Everything already covered by the `EOA-14935` v2 test plan (externally controlled selection, built-in search, pinnable hover state, overflow tooltip) — regression-only in this plan, not re-detailed

---

## Test Strategy

### Test Environment

- **OS:** macOS (dev), Ubuntu (CI)
- **Browsers:** Chrome latest (primary — all manual verification during implementation used Chrome via Playwright), Firefox latest, Safari latest
- **Viewport:** Desktop (1920×1080), Tablet (768×1024) — mobile/narrow-width behavior is explicitly out of scope (see V2-9/V2-10 deferral in the v3 research spike)
- **Theme:** `proximus` (primary), `connect`, `engage`, `protect`
- **Tools:** `pnpm dev:components` (playground, `packages/boreal-web-components/src/index.html`) and `pnpm dev:docs` (Storybook/MDX) for manual QA
- **Datasets:** Large-scale test cases (virtualization, guardrail) use seeded, deterministic generators (5,000 rows for virtualization/pin-offset scenarios, 1,500 rows for guardrail scenarios) already present in `index.html` — reuse them rather than regenerating ad hoc data, to keep row heights and content reproducible across runs

---

## Entry Criteria

- [x] v3 plan implementation complete (all 11 tasks shipped; Task 12 formally deferred to `EOA-16000`)
- [x] Unit tests passing (233/233, coverage 98.1% statements / 90.69% branches / 100% functions / 99.47% lines)
- [x] `tsc --noEmit` and `eslint` clean on all touched files
- [x] Storybook stories updated and rendering (`WithRowsPagination`, `WithServerSideMode`, `WithLoadingState`, `WithVirtualization`)
- [x] Documentation (MDX) updated per Tasks 1b, 6, 9, 11; "Current limitations" table reflects only what remains unshipped

### Exit Criteria

- [ ] All manual test cases in this plan pass
- [ ] No P0/P1 bugs open
- [ ] Regression suite passes (100% P0, ≥90% P1) — re-run the `EOA-14935` v2 test plan's own test cases separately; this plan does not duplicate them
- [ ] Visual regression: no unexpected changes in Chromatic

---

## Risk Assessment

| Risk                                                                 | Probability | Impact | Mitigation                                                                                                          |
| --------------------------------------------------------------------- | ------------ | ------ | ---------------------------------------------------------------------------------------------------------------------- |
| Virtualized `<tbody>` renders the full dataset on first paint (crash) | Low          | High   | Task 7 fixed a real crash bug (found via manual testing with 5,000 rows); T7-006 below is a direct regression guard for it |
| Sticky `<thead>` detaches from wrapper top during virtualized scroll  | Low          | High   | Validated via two Playwright spikes before implementation; T7-003/T7-004 verify header stays pinned through normal and rapid-jump scrolling |
| Pin-offset values go stale after a container resize during virtualized scroll | Medium       | Medium | Task 8 explicitly added a `ResizeObserver`; T8-003/T8-004 verify recompute on resize, not just on scroll             |
| `maxClientRows` auto-enable silently no-ops under an explicit `virtual={false}` | Medium       | High   | Task 10 deliberately overrides explicit `false`; T10-002 is a direct regression guard                                |
| `serverSide` + `rows` set simultaneously produces silently wrong behavior | Low          | Medium | Task 5e added a dedicated conflict warning; T5e-003 verifies it fires                                                |
| Skeleton row count mismatches real page size on a partial last page   | Medium       | Low    | Task 5e made `effectiveLoadingRows` remainder-aware; T5e-001/T5e-002 verify both the mid-range and last-page cases    |
| Stale `bds-pagination` props after internal (v3) page navigation      | Medium       | Medium | Task 5e's `itemsPerPage`/`currentPage` write-back fix; T5e-004 verifies props reflect internal navigation state       |

---

## Test Cases by Task

### Task 1: bds-table — `rows` Prop, Internal Pagination, Cross-Page Selection

#### TC-EOA-15507-T1-001: Selection survives page navigation

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-table selectable row-key="id"` with `rows` set to 50 generated rows, slotted `bds-pagination items-per-page="10" show-total-items`

**Test Steps:**

1. Select a row on page 1
2. Navigate to page 2 using the paginator
3. Navigate back to page 1

**Expected Result:**

- The originally selected row remains checked after the round trip
- No console warnings or errors

**Test Data:** Matches `index.html` "bds-table rows prop with internal pagination" example (50 rows, `items-per-page="10"`)

---

#### TC-EOA-15507-T1-002: Paginator shows correct page count with no consumer-side slicing

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T1-001

**Test Steps:**

1. Render the table with 50 `rows` and `items-per-page="10"`
2. Observe the paginator

**Expected Result:**

- Paginator shows 5 pages (50/10) with no consumer-side data slicing required

---

#### TC-EOA-15507-T1-003: `getSelectedRows()` resolves across all pages, not just the current slice

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Table from T1-001 with a row selected on page 1

**Test Steps:**

1. Navigate to page 3
2. Call `table.getSelectedRows()` via console/script

**Expected Result:**

- Returned array includes the row selected on page 1, even though it is not currently rendered

---

### Tasks 2–4: bds-table — Slot-Based Column Footer

#### TC-EOA-15507-T2-001: Footer row renders and aligns to its column

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id"` with columns `id` (pinnable, `slot="footer"` = "Total"), `item` (pinnable), `amount` (`slot="footer"` = "$1,234.00")

**Test Steps:**

1. Render the table with 2 data rows
2. Inspect the rendered DOM for a `<tfoot>` row below the body

**Expected Result:**

- `<tfoot>` renders with the slotted footer content aligned under its own column

**Test Data:** Matches `index.html` "bds-table column footer (slot=\"footer\")" example

---

#### TC-EOA-15507-T2-002: Pinned footer cell keeps the same offset as header/body cells

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same table as T2-001

**Test Steps:**

1. Hover the "ID" header to reveal its pin icon, click it
2. Hover the "Item" header, click its pin icon
3. Inspect the computed/inline `left` offset on the pinned `<th>`, `<td>`, and footer `<td>` for each pinned column

**Expected Result:**

- Each pinned footer cell's `left` offset matches its corresponding header and body cell exactly

---

#### TC-EOA-15507-T2-003: Footer stays aligned under a pinned column while paginating

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id" selectable searchable` with `action` column pinned (footer = "Total: 20"), `campaign`/`status`/`fileName` pinnable, slotted `bds-pagination items-per-page="5"`, 20 rows

**Test Steps:**

1. Pin the "Action" column (already pinned by default in this scenario per the playground setup) and navigate through all 4 pages via the paginator

**Expected Result:**

- The "Total" footer cell stays aligned under the pinned "Action" column on every page

**Test Data:** Matches `index.html` "column footer + toolbar + pagination" example

---

#### TC-EOA-15507-T2-004: Toggling pin state keeps footer/body/header cells in sync

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T2-003

**Test Steps:**

1. Toggle the pin icon on "Campaign", "Status", and "File Name" headers in various combinations

**Expected Result:**

- Each toggle keeps that column's footer, body, and header cells synchronized in offset

---

#### TC-EOA-15507-T2-005: Footer count live-updates on selection change (consumer-driven)

**Priority:** P1 | **Type:** Integration | **Status:** Not Run

**Preconditions:**

- Same table as T2-003, with a `selectedRowsChange` listener wired to update the footer text (per the "Column footers" slot-based design — the footer is static slotted markup, so the consumer owns keeping it live)

**Test Steps:**

1. Select/deselect several rows

**Expected Result:**

- Footer count text updates to reflect the current selection count, reverting to the full row count when nothing is selected

---

#### TC-EOA-15507-T2-006: Footer renders correctly across a wide, mostly-unpinnable column set

**Priority:** P1 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id"` with 8 columns (`id`, `name` pinnable; `role`, `dept`, `location`, `email`, `start`, `salary` not pinnable), `id` footer = "Total", `salary` footer computed as a running total

**Test Steps:**

1. Pin "ID" and/or "Name"
2. Scroll the table horizontally

**Expected Result:**

- Pinned columns stay fixed at the left edge while unpinned columns scroll underneath
- Footer row renders correctly across all 8 columns, with the computed "Total salary" cell correct under "Salary"

**Test Data:** Matches `index.html` "Column pinning — pinned columns stay fixed on the left" example (3 rows, computed salary total)

---

### Tasks 5, 5b–5e: bds-table — Server-Side Mode and Skeleton Loading

#### TC-EOA-15507-T5-001: Full skeleton visual renders on `loading=true`

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id" selectable searchable subheading="Users" server-side` with `rows` (5 rows), slotted `bds-pagination items-per-page="2"`, `slot="toolbar-actions"` Export button

**Test Steps:**

1. Navigate the paginator to page 2
2. Click "Toggle loading"

**Expected Result:**

- Toolbar title, column header labels, checkbox column (header + every row), body rows (2 skeleton rows matching `items-per-page="2"`, not a flat 5), the filter/column-visibility/search icon buttons (3 skeleton squares), the footer (skeleton bar), and the paginator (title bar + 6 square placeholders) all render as pulsing skeleton placeholders
- The toolbar-actions "Export" button disappears entirely (hidden, not skeletonized)

**Test Data:** Matches `index.html` "serverSide mode + full skeleton loading visual" example

---

#### TC-EOA-15507-T5b-001: Paginator state preserved across loading toggle, no row-count jump

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, currently on page 2 with loading toggled on

**Test Steps:**

1. Toggle loading off

**Expected Result:**

- Paginator returns still showing page 2 (state preserved)
- No visible row-count jump during the transition

---

#### TC-EOA-15507-T5-002: Server-side sort disables local reordering

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, loading off

**Test Steps:**

1. Click the "Name" column header (sortable)
2. Check the `bdsSort` event logged below the table

**Expected Result:**

- The sort icon updates but row order does NOT change (`serverSide=true`)
- `bdsSort` event fires with the expected column/direction detail

---

#### TC-EOA-15507-T5-003: Skeleton respects `prefers-reduced-motion`

**Priority:** P1 | **Type:** Accessibility | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, loading on

**Test Steps:**

1. Open devtools' Rendering panel, force-emulate `prefers-reduced-motion: reduce`

**Expected Result:**

- Skeleton bars stop pulsing

---

#### TC-EOA-15507-T5e-001: `bds-pagination` `itemsPerPage` reflects internal navigation, not stale initial attribute

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, `items-per-page="2"` initial attribute

**Test Steps:**

1. Change the items-per-page dropdown to "10"
2. Read `document.querySelector('#skeleton-table bds-pagination').itemsPerPage` in the console

**Expected Result:**

- Reflects `10`, not the original `items-per-page="2"` attribute (regression guard for the previously-stale prop)

---

#### TC-EOA-15507-T5e-002: Skeleton row count is remainder-aware on a mid-range page

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, items-per-page changed to "10" (5-row dataset)

**Test Steps:**

1. With items-per-page still "10", click "Toggle loading"

**Expected Result:**

- Skeleton renders 5 rows (the dataset's full remaining count), not 10 and not the original 2

---

#### TC-EOA-15507-T5e-003: Skeleton row count is remainder-aware on the last page

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same table as T5-001, items-per-page reset to "2", navigated to page 3 (last page, 1 remaining row)

**Test Steps:**

1. Click "Toggle loading"

**Expected Result:**

- Skeleton renders exactly 1 row, not 2

---

#### TC-EOA-15507-T5e-004: `serverSide` + `rows` conflict warning fires

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T5-001 (deliberately combines `server-side` and `rows` to also exercise the sort-disable behavior in T5-002)

**Test Steps:**

1. Open the devtools console on page load

**Expected Result:**

- A warning is logged noting `serverSide` is enabled while `rows` is set

---

### Task 7: bds-table — Opt-In Row Virtualization

#### TC-EOA-15507-T7-001: Rendered `<tr>` count stays bounded regardless of scroll position

**Priority:** P0 | **Type:** Performance | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id" selectable searchable max-height="500px" virtual` with a 5,000-row seeded dataset (variable-height "Notes" formatter column)

**Test Steps:**

1. Click "Refresh row-count readout" at the top of the scroll range
2. Scroll the table down through the 5,000 rows
3. Click "Refresh row-count readout" again at a few more positions

**Expected Result:**

- "Rendered data `<tr>` count" stays small/bounded at every scroll position — never approaches 5,000

**Test Data:** Matches `index.html` "bds-table row virtualization (virtual)" example

---

#### TC-EOA-15507-T7-002: Checked rows survive a sort while virtualized

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T7-001

**Test Steps:**

1. Check a few checkboxes
2. Click the "Name" column header to sort

**Expected Result:**

- The same rows remain checked after the sort (row-identity preserved via `key={rowId}`)

---

#### TC-EOA-15507-T7-003: Sticky header stays pinned through normal scroll

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same table as T7-001

**Test Steps:**

1. Click "Jump to distant row (~4980)"
2. Click "Refresh row-count readout" immediately after

**Expected Result:**

- Header stayed pinned (delta between `thead` top and wrapper top stays under 1.5px)

---

#### TC-EOA-15507-T7-004: Sticky header stays pinned through rapid-jump scrolling

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same table as T7-001

**Test Steps:**

1. Click "Stress: rapid jumps (2% → 80% → 1%)"
2. Click "Refresh row-count readout" immediately after
3. Click "Scroll to top" to reset

**Expected Result:**

- Header never detaches from the wrapper's top edge, even through rapid successive jumps

---

#### TC-EOA-15507-T7-005: Warning fires for `virtual` without `max-height`

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Second table in the same playground section: `bds-table row-key="id" virtual` with no `max-height`

**Test Steps:**

1. Open the devtools console on page load

**Expected Result:**

- A `bds-table` warning fires for the table with no `max-height` set

---

#### TC-EOA-15507-T7-006: First paint does not crash on a large dataset (regression guard)

**Priority:** P0 | **Type:** Regression | **Status:** Not Run

**Preconditions:**

- Same 5,000-row table as T7-001, hard page reload (not a warm navigation)

**Test Steps:**

1. Load the page fresh and observe the very first paint of the virtualized table

**Expected Result:**

- Table renders without crashing the browser tab — a single bounded placeholder spacer row appears before the real `Virtualizer` instance mounts, not the full unbounded dataset (regression guard for the crash bug found during Task 7's own manual testing)

---

### Task 8: bds-table — Pin-Offset Throttling During Virtualized Scroll

#### TC-EOA-15507-T8-001: Pinned offsets stay correctly aligned while scrolling

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table row-key="id" selectable max-height="500px" virtual` (5,000-row seeded dataset) with `id`, `name`, `email` columns `pinnable`

**Test Steps:**

1. Pin "ID", "Name", and/or "Email" (hover header, click pin icon)
2. Scroll vertically through the 5,000 rows

**Expected Result:**

- Pinned column offsets stay correctly aligned to the unpinned columns' real left edge as new rows scroll into view — no lag or misalignment from the throttled recompute

**Test Data:** Matches `index.html` "pin-offset throttling during virtualized scroll" example

---

#### TC-EOA-15507-T8-002: Readout shows currently-applied offsets

**Priority:** P2 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T8-001, at least one column pinned

**Test Steps:**

1. Click "Refresh pin-offset readout"

**Expected Result:**

- Readout shows the currently-applied `left` offset for each pinned column's `<th>` and `<td>`

---

#### TC-EOA-15507-T8-003: Offsets recompute on container resize (not stale)

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T8-001, one or more columns pinned

**Test Steps:**

1. Click "Narrow container (550px)" to simulate a responsive resize without touching which columns are pinned
2. Click "Refresh pin-offset readout" again

**Expected Result:**

- Offsets changed to match the narrower column widths — not stale from before the resize

---

#### TC-EOA-15507-T8-004: Offsets recompute again after restoring container width

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same table as T8-001, narrowed per T8-003

**Test Steps:**

1. Click "Restore container (800px)"
2. Click "Refresh pin-offset readout"

**Expected Result:**

- Offsets recompute again to match the restored width

---

### Task 10: bds-table — `maxClientRows` Guardrail

#### TC-EOA-15507-T10-001: Auto-enable triggers and both warnings log

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- "Table A": `bds-table row-key="id" max-height="400px"` (no `virtual`, no `server-side`) with 1,500 rows

**Test Steps:**

1. Open devtools console before the section loads
2. Observe warnings on load
3. Click "Refresh readouts" and check the "Table A" line

**Expected Result:**

- Two `bds-table` warnings log: one noting virtualization was automatically enabled because the row count exceeds `maxClientRows`, one noting sort/selection/memory cost still scales with dataset size
- Rendered `<tr>` count is small/bounded (well under 1,500), not one real row per data row

**Test Data:** Matches `index.html` "`maxClientRows` guardrail (auto-enabled virtualization)" example

---

#### TC-EOA-15507-T10-002: Auto-enable overrides an explicit `virtual="false"`

**Priority:** P0 | **Type:** Regression | **Status:** Not Run

**Preconditions:**

- "Table B": identical to Table A (1,500 rows, no `server-side`) but explicitly sets `virtual="false"`

**Test Steps:**

1. Observe warnings on load
2. Click "Refresh readouts" and check the "Table B" line

**Expected Result:**

- Still auto-enables: bounded `<tr>` count, and its own pair of warnings logged on load despite the explicit `virtual="false"` attribute

---

#### TC-EOA-15507-T10-003: `serverSide` mode is exempt from auto-enable

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- "Table C": `server-side` set, same 1,500-row dataset, no `virtual`

**Test Steps:**

1. Observe warnings on load
2. Click "Refresh readouts" and check the "Table C" line

**Expected Result:**

- No `bds-table` warnings log for Table C
- Full 1,500 real `<tr>` rendered (not bounded) — `serverSide` mode is exempt from auto-enable

---

### Task 1b, 6, 9, 11: Documentation (Storybook / MDX)

#### TC-EOA-15507-TDOC-001: "Dataset mode (`rows` prop)" section renders with cross-page selection guidance

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `pnpm dev:docs` running, `bds-table` MDX open

**Test Steps:**

1. Locate the dataset-mode section
2. Verify the `rows`+`bds-pagination` wiring example and the `data`+`rows` conflict warning callout

**Expected Result:**

- Section present, wiring example accurate, warning callout documented

---

#### TC-EOA-15507-TDOC-002: `WithServerSideMode` and `WithLoadingState` stories render and function

**Priority:** P0 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- Storybook running, `bds-table` stories list

**Test Steps:**

1. Open `WithServerSideMode` — verify it demonstrates server-side sort-disable behavior
2. Open `WithLoadingState` — verify skeleton toggles correctly

**Expected Result:**

- Both stories render without console errors and demonstrate the documented behavior

---

#### TC-EOA-15507-TDOC-003: "Row virtualization" section documents sticky-header-works-normally as a positive feature

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `bds-table` MDX open to the "Virtualization" section

**Test Steps:**

1. Verify the sticky-header callout is framed as a positive feature, not a caveat
2. Verify the `loadingRows`+`virtual` warning callout and the `virtual`-vs-`serverSide` alternative-strategies note are present
3. Open the `WithVirtualization` story and confirm the header stays sticky while scrolling a ~5,000-row dataset

**Expected Result:**

- All three documentation elements present and accurate; story functions as described

---

#### TC-EOA-15507-TDOC-004: "Automatic virtualization for large datasets" subsection and Layout constraints cross-link resolve

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `bds-table` MDX open

**Test Steps:**

1. Locate "Layout constraints" → "Row count ceiling" bullet
2. Click its link to the "Automatic virtualization for large datasets" subsection

**Expected Result:**

- Link navigates to the correct heading (not just visually present — must actually resolve)
- Subsection covers `serverSide` scoping, stickiness, override-of-explicit-`false`, and the sort/selection cost caveat

---

#### TC-EOA-15507-TDOC-005: `max-client-rows` and `virtual` props appear correctly in the Properties/ArgTypes table

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `bds-table` story Controls panel open

**Test Steps:**

1. Verify `virtual` and `max-client-rows` appear with correct type/default/description

**Expected Result:**

- Both props render correctly in the ArgTypes table
</content>
