# Test Plan: EOA-14935 bds-table v2 High-Priority Limitations

## Executive Summary

**Feature:** bds-table v2 — High-Priority Limitations Implementation
**Ticket:** EOA-14935
**Components Under Test:** `bds-table`, `bds-pagination`, `bds-tooltip`
**Testing Scope:** Functional, UI/Visual, Integration, Regression
**Plan Status:** Done (v2 plan completed 2026-07-09)

This test plan covers the 12 shipped tasks from the v2 implementation plan (Tasks 1–8, 12–15, with 9–11 removed). The work spans:

- `bds-pagination`: 3 bug fixes + 1 new prop (Tasks 1–4)
- `bds-tooltip`: Manual/imperative API (Tasks 5–6)
- `bds-table`: Controlled selection, Vue v-model wiring, built-in search, pinnable hover state, overflow tooltip, docs (Tasks 7, 8, 12, 13, 14, 15)

---

## Test Scope

### In Scope

| Task | Component      | Feature                                                   |
| ---- | -------------- | --------------------------------------------------------- |
| 1    | bds-pagination | Fix `totalItems` watcher snap-back bug                    |
| 2    | bds-pagination | Fix empty-state literal "1"                               |
| 3    | bds-pagination | Add `loading` prop                                        |
| 4    | bds-pagination | Tests consolidation + docs                                |
| 5    | bds-tooltip    | Manual mode + `showTooltip`/`hideTooltip`/`anchorTo`      |
| 6    | bds-tooltip    | Docs for manual mode                                      |
| 7    | bds-table      | Externally controlled `selectedRows`                      |
| 8    | bds-table      | Vue `v-model:selectedRows` wiring                         |
| 12   | bds-table      | Built-in `searchable` prop + `bds-search-bar` integration |
| 13   | bds-table      | Pinnable-only column hover state                          |
| 14   | bds-table      | Overflow tooltip on truncated text                        |
| 15   | bds-table      | Documentation for Tasks 7, 8, 12, 13, 14                  |

### Out of Scope

- Row virtualization (moved to v3, Task 7)
- Dataset/internal pagination (moved to v3, Task 1)
- Column footer slot (moved to v3, Task 3)
- Server-side mode + skeleton loading (moved to v3, Task 5)
- Large-dataset guardrail `maxClientRows` (moved to v3, Task 10)
- Mutation testing gate (consolidated in v3 Task 12)

---

## Test Strategy

### Test Environment

- **OS:** macOS (dev), Ubuntu (CI)
- **Browsers:** Chrome latest, Firefox latest, Safari latest
- **Viewport:** Desktop (1920×1080), Tablet (768×1024), Mobile (375×667)
- **Theme:** `proximus` (primary), `connect`, `engage`, `protect`
- **Tools:** `pnpm dev:components` and `pnpm dev:docs` for manual QA

---

## Entry Criteria

- [x] v2 plan implementation complete (all 12 tasks merged)
- [x] Unit tests passing (≥90% coverage)
- [x] Storybook stories updated and rendering
- [x] Documentation (MDX) updated per Task 15
- [x] Vue wrapper `componentModels` updated for `selectedRows`

### Exit Criteria

- [ ] All manual test cases in this plan pass
- [ ] No P0/P1 bugs open
- [ ] Regression suite passes (100% P0, ≥90% P1)
- [ ] Visual regression: no unexpected changes in Chromatic

---

## Risk Assessment

| Risk                                                  | Probability | Impact | Mitigation                                                                                  |
| ----------------------------------------------------- | ----------- | ------ | ------------------------------------------------------------------------------------------- |
| `bds-tooltip` manual mode leaks listeners             | Medium      | High   | Task 5 manual test validates no leak; unit test covers cleanup in `disconnectedCallback`    |
| `selectedRows` Vue v-model desync                     | Medium      | High   | Task 8 unit test validates `selectedRowsChange` event payload matches `v-model` expectation |
| `searchable` toolbar layout shift on collapse/expand  | Medium      | Medium | Task 12 manual test validates leftward expansion without overlap                            |
| Overflow tooltip conflicts with column `info` tooltip | Medium      | Medium | Task 14 unit test validates independence; manual test validates both coexist                |
| Pagination `totalItems` watcher regression            | Low         | High   | Task 1 unit test covers snap-back fix; regression test added                                |

---

## Test Cases by Task

### Task 1: bds-pagination — Fix `totalItems` Watcher Snap-Back

#### TC-EOA-14935-T1-001: Preserve current page when totalItems shrinks but current page still valid

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-pagination` rendered with `total-items="50"`, `items-per-page="10"`
- User navigated to page 3

**Test Steps:**

1. Verify pagination shows page 3 (50 items / 10 per page = 5 pages)
2. Set `totalItems = 30` via script (30 items / 10 per page = 3 pages, page 3 still valid)
3. Observe displayed page number

**Expected Result:**

- Pagination stays on page 3
- No snap-back to page 1
- Page indicator shows "3 of 3"

**Test Data:** `totalItems: 50 → 30`, `currentPage: 3`, `itemsPerPage: 10`

---

#### TC-EOA-14935-T1-002: Clamp current page down when totalItems shrinks below current page

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-pagination` rendered with `total-items="50"`, `items-per-page="10"`
- User navigated to page 5

**Test Steps:**

1. Verify pagination shows page 5
2. Set `totalItems = 25` via script (25 items / 10 per page = 3 pages)
3. Observe displayed page number

**Expected Result:**

- Pagination clamps to page 3 (max valid page)
- No snap-back to page 1
- Page indicator shows "3 of 3"

**Test Data:** `totalItems: 50 → 25`, `currentPage: 5`, `itemsPerPage: 10`

---

### Task 2: bds-pagination — Fix Empty-State Literal "1"

#### TC-EOA-14935-T2-001: No stray "1" rendered when totalItems=0

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-pagination` rendered with `total-items="0"`, `items-per-page="10"`

**Test Steps:**

1. Render component
2. Inspect rendered DOM for any text node containing "1"
3. Verify navigation buttons exist but are disabled

**Expected Result:**

- No literal "1" text anywhere in pagination controls
- Previous/Next buttons rendered with `disabled` attribute
- Page indicator shows "0 of 0" or equivalent empty state

**Test Data:** `totalItems: 0`, `itemsPerPage: 10`

---

#### TC-EOA-14935-T2-002: Navigation buttons disabled in empty state

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T2-001

**Test Steps:**

1. Attempt to click Previous button
2. Attempt to click Next button
3. Verify no page change events fire

**Expected Result:**

- Both buttons have `disabled` attribute
- Click handlers do not execute
- `bdsPageChange` event not emitted

---

### Task 3: bds-pagination — Add `loading` Prop

#### TC-EOA-14935-T3-001: loading=true disables all navigation controls

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-pagination` rendered with `total-items="100"`, `items-per-page="10"`, `current-page="3"`

**Test Steps:**

1. Set `loading = true` via script
2. Attempt to click Previous, Next, First, Last buttons
3. Attempt to change items-per-page select
4. Set `loading = false`
5. Verify controls re-enable

**Expected Result:**

- All nav buttons (`bds-button`) have `disabled` attribute while loading
- Items-per-page `bds-select` has `disabled` attribute while loading
- Clicking/typing has no effect while loading
- Controls re-enable immediately when `loading=false`

**Test Data:** `loading: false → true → false`

---

#### TC-EOA-14935-T3-002: loading=true visual state shows disabled styling

**Priority:** P1 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T3-001

**Test Steps:**

1. Set `loading = true`
2. Visually inspect buttons and select
3. Compare against non-loading state

**Expected Result:**

- Buttons show disabled visual state (opacity, cursor not-allowed)
- Select shows disabled visual state
- Loading indicator/spinner may appear (if implemented)

---

### Task 4: bds-pagination — Tests Consolidation & Docs

#### TC-EOA-14935-T4-002: Storybook docs render loading prop in ArgTypes

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `pnpm dev:docs` running
- Navigate to bds-pagination story

**Test Steps:**

1. Open Controls panel
2. Verify `loading` prop appears with type `boolean`, default `false`
3. Toggle `loading` in Controls
4. Verify component updates in Canvas

**Expected Result:**

- `loading` appears in ArgTypes table
- Toggle works in real-time

---

### Task 5: bds-tooltip — Manual Mode + showTooltip/hideTooltip/anchorTo

#### TC-EOA-14935-T5-001: Manual mode — anchorTo + showTooltip displays tooltip

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-tooltip manual="true"` rendered
- Two buttons: "Button A", "Button B"

**Test Steps:**

1. Click "Anchor to Button A"
2. Click "Show"
3. Observe tooltip position and content

**Expected Result:**

- Tooltip appears anchored to Button A
- Content shows "Manual tooltip content"
- No hover/focus required on Button A

**Test Data:** Matches `index.html` Task 5 example

---

#### TC-EOA-14935-T5-002: Manual mode — anchorTo switches target without leak

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T5-001

**Test Steps:**

1. Click "Anchor to Button A", then "Show" → tooltip on A
2. Click "Anchor to Button B"
3. Hover Button A (should NOT show tooltip)
4. Click "Show" → tooltip on B
5. Click "Hide"

**Expected Result:**

- Step 3: No tooltip appears on hover of A (no listener leak)
- Step 4: Tooltip appears on B
- Step 5: Tooltip dismisses

---

#### TC-EOA-14935-T5-003: Manual mode — hideTooltip dismisses tooltip

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Tooltip showing (via TC-EOA-14935-T5-001)

**Test Steps:**

1. Click "Hide"
2. Observe tooltip

**Expected Result:**

- Tooltip immediately hidden
- Can be shown again with "Show"

---

#### TC-EOA-14935-T5-004: Non-manual mode unchanged (regression)

**Priority:** P1 | **Type:** Regression | **Status:** Not Run

**Preconditions:**

- `bds-tooltip` without `manual` prop (default behavior)
- Tooltip has trigger element

**Test Steps:**

1. Hover trigger element
2. Verify tooltip appears
3. Move mouse away
4. Verify tooltip hides

**Expected Result:**

- Default hover/focus behavior works exactly as before
- No regression in auto-discovery or positioning

---

### Task 6: bds-tooltip — Docs for Manual Mode

#### TC-EOA-14935-T6-001: Storybook "Programmatic control" section renders

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `pnpm dev:docs` running
- Navigate to bds-tooltip story

**Test Steps:**

1. Find "Programmatic control" section in MDX
2. Verify code example matches Task 5 manual test
3. Interact with Canvas example if present

**Expected Result:**

- Section exists with working example
- `manual`, `anchorTo`, `showTooltip`, `hideTooltip` documented

---

### Task 7: bds-table — Externally Controlled selectedRows

#### TC-EOA-14935-T7-001: Set selectedRows externally — checkboxes update

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- `bds-table selectable="true"` with 3 rows (ids: '1', '2', '3')
- Table rendered with data

**Test Steps:**

1. Click "Set selectedRows = ['1', '3']" button
2. Observe row checkboxes

**Expected Result:**

- Rows with id '1' and '3' show checked checkboxes
- Row '2' remains unchecked
- Header checkbox shows indeterminate state (if partial selection)

**Test Data:** Matches `index.html` Task 7 example

---

#### TC-EOA-14935-T7-002: Clear selectedRows externally — all unchecked

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T7-001, with rows '1' and '3' selected

**Test Steps:**

1. Click "Set selectedRows = []" button
2. Observe row checkboxes

**Expected Result:**

- All row checkboxes unchecked
- Header checkbox unchecked (not indeterminate)

---

#### TC-EOA-14935-T7-003: User interaction updates selectedRows prop (two-way)

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Table with `selectedRows` initially empty
- `selectedRowsChange` event listener attached (logs to console)

**Test Steps:**

1. Click row '2' checkbox
2. Check console for `selectedRowsChange` event
3. Verify `selectedRows` prop updated

**Expected Result:**

- `selectedRowsChange` fires with `detail: ['2']`
- `selectedRows` prop reflects `['2']`
- Checkbox stays checked

---

#### TC-EOA-14935-T7-004: Select all / deselect all updates selectedRows

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Table with 5 rows, `selectedRows = []`

**Test Steps:**

1. Click header checkbox (select all)
2. Verify `selectedRowsChange` fires with all 5 ids
3. Click header checkbox again (deselect all)
4. Verify `selectedRowsChange` fires with `[]`

**Expected Result:**

- Select all: `selectedRowsChange` detail = all row ids
- Deselect all: `selectedRowsChange` detail = `[]`

---

#### TC-EOA-14935-T7-005: selectedRows prop sync with bdsSelect event

**Priority:** P1 | **Type:** Integration | **Status:** Not Run

**Preconditions:**

- Table with `bdsSelect` listener attached

**Test Steps:**

1. Set `selectedRows = ['1', '3']` externally
2. Verify `bdsSelect` fires with `{ selectedIds: ['1', '3'], row: [...] }`

**Expected Result:**

- `bdsSelect` event fires on programmatic change
- Payload matches expected format

---

### Task 8: bds-table — Vue v-model:selectedRows Wiring

#### TC-EOA-14935-T8-001: Vue v-model:selectedRows binds bidirectionally

**Priority:** P0 | **Type:** Integration (Vue) | **Status:** Not Run

**Preconditions:**

- Vue app with `<bds-table selectable v-model:selectedRows="selected">`
- `selected` ref initialized to `[]`

**Test Steps:**

1. User clicks row checkbox in browser
2. Verify `selected` ref updates
3. Programmatically set `selected.value = ['2']`
4. Verify checkbox updates

**Expected Result:**

- User action → `selected` updates
- Programmatic change → UI updates

---

### Task 12: bds-table — Built-in searchable Prop

#### TC-EOA-14935-T12-001: searchable=true renders search bar in toolbar

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table searchable="true"` with columns
- `pnpm dev:components` running

**Test Steps:**

1. Render table
2. Inspect toolbar right zone

**Expected Result:**

- Search icon/button visible in toolbar right zone
- No search input visible initially (collapsed state)

---

#### TC-EOA-14935-T12-002: Click search icon expands leftward without overlap

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T12-001
- Filter and Column-visibility icons present in toolbar

**Test Steps:**

1. Click search icon
2. Observe expansion animation and final position

**Expected Result:**

- Search bar expands LEFTWARD (icon moves left, input appears to its right)
- No overlap with Filter/Column-visibility icons
- Input focused and ready for typing

**Visual Reference:** `index.html` Task 12 manual test steps

---

#### TC-EOA-14935-T12-003: Type query + Enter filters table via bdsSearch

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Table with `searchable="true"` and sample data (Alice, Bob, Charlie)
- Consumer handles `bdsInputDebounced` to filter data

**Test Steps:**

1. Expand search bar
2. Type "Ali"
3. Press Enter
4. Observe table rows

**Expected Result:**

- `bdsSearch` event fires with value "Ali"
- Consumer filters data to matching rows (Alice only)
- Table updates to show filtered results

---

#### TC-EOA-14935-T12-004: Clear input restores full dataset

**Priority:** P0 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Filtered state from TC-EOA-14935-T12-003 (showing Alice only)

**Test Steps:**

1. Click clear (×) affordance in search input
2. Or fire `bdsClear` event
3. Observe table rows

**Expected Result:**

- `bdsClear` event fires
- Consumer restores full dataset
- Table shows all 3 rows

---

#### TC-EOA-14935-T12-005: searchable=false (default) renders no search element

**Priority:** P1 | **Type:** Regression | **Status:** Not Run

**Preconditions:**

- `bds-table` without `searchable` prop (default)

**Test Steps:**

1. Render table
2. Inspect toolbar right zone

**Expected Result:**

- No search icon/button in toolbar
- No residual DOM from removed slot
- Filter/Column-visibility icons in normal positions

---

### Task 13: bds-table — Pinnable-Only Column Hover State

#### TC-EOA-14935-T13-001: Pinnable-only column header shows pin icon hover darkening

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table` with two columns:
  - Column 1: `col-key="name"`, `label="Name"`, `sortable="true"`
  - Column 2: `col-key="email"`, `label="Email"`, `pinnable="true"` (NOT sortable)

**Test Steps:**

1. Hover "Name" header (sortable) → sort icon darkens
2. Hover "Email" header (pinnable only) → pin icon darkens

**Expected Result:**

- Both icons darken on hover to same color (`$boreal-icon-default-ink`)
- "Email" header does NOT show pointer cursor (not sortable)
- "Name" header shows pointer cursor (sortable)

**Visual Reference:** `index.html` Task 13 example

---

#### TC-EOA-14935-T13-002: Sortable-only column unaffected

**Priority:** P1 | **Type:** Regression | **Status:** Not Run

**Preconditions:**

- Column with `sortable="true"`, `pinnable="false"`

**Test Steps:**

1. Hover header
2. Verify sort icon darkens
3. Verify no `data-pinnable` attribute on `<th>`

**Expected Result:**

- Existing sortable hover behavior unchanged
- No `data-pinnable` attribute added

---

### Task 14: bds-table — Overflow Tooltip on Truncated Text

#### TC-EOA-14935-T14-001: Truncated header shows tooltip on hover

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- `bds-table` with `style="max-width: 260px"`
- Column: `col-key="name"`, `label="A very long column name that gets truncated"`, `info="Also has an info tooltip"`
- Table rendered in dev server

**Test Steps:**

1. Hover truncated header text
2. Observe tooltip
3. Move mouse away

**Expected Result:**

- Tooltip appears with full untruncated label text
- Tooltip anchors tightly to truncated text (not padded cell)
- Mouse away → tooltip hides
- Column's `info` tooltip (on info icon) works independently

**Visual Reference:** `index.html` Task 14 example

---

#### TC-EOA-14935-T14-002: Truncated cell value shows tooltip on hover

**Priority:** P0 | **Type:** UI/Visual | **Status:** Not Run

**Preconditions:**

- Same as TC-EOA-14935-T14-001
- Row data: `name: "A very long value that should overflow and truncate in this narrow column"`

**Test Steps:**

1. Hover truncated cell value
2. Observe tooltip
3. Move mouse away

**Expected Result:**

- Tooltip appears with full untruncated cell value
- Same anchoring behavior as header
- Independent of column `info` tooltip

---

#### TC-EOA-14935-T14-003: Non-truncated text shows no tooltip

**Priority:** P1 | **Type:** Functional | **Status:** Not Run

**Preconditions:**

- Column wide enough to show full text without truncation

**Test Steps:**

1. Hover non-truncated header/cell
2. Wait 500ms

**Expected Result:**

- No overflow tooltip appears
- `info` tooltip still works on icon hover

---

#### TC-EOA-14935-T14-004: info tooltip unaffected by overflow tooltip

**Priority:** P0 | **Type:** Integration | **Status:** Not Run

**Preconditions:**

- Column has both long label (truncates) AND `info` prop

**Test Steps:**

1. Hover truncated label → overflow tooltip shows
2. Hover info icon → info tooltip shows
3. Verify both work independently

**Expected Result:**

- Both tooltips function
- No interference (different `bds-tooltip` instances)
- Overflow tooltip uses `manual` singleton; info tooltip uses default auto mode

---

### Task 15: bds-table — Documentation for Tasks 7, 8, 12, 13, 14

#### TC-EOA-14935-T15-001: Limitations table updated

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- `pnpm dev:docs` running
- Navigate to bds-table MDX

**Test Steps:**

1. Find "Limitations" table
2. Verify rows 1, 3, 12 removed (overflow tooltip, controlled selection, built-in search)
3. Verify remaining rows renumbered correctly
4. Verify row 2 (dataset pagination) still present

**Expected Result:**

- Three limitation rows removed
- Table renumbered sequentially
- Row 2 (now row 1) still shows dataset limitation

---

#### TC-EOA-14935-T15-002: ArgTypes includes new props

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- bds-table story Controls panel open

**Test Steps:**

1. Verify `selected-rows` prop in ArgTypes
2. Verify `selectedRowsChange` event in ArgTypes
3. Verify `searchable` prop in ArgTypes

**Expected Result:**

- All three appear in ArgTypes table with correct types

---

#### TC-EOA-14935-T15-003: WithSearch story works correctly

**Priority:** P0 | **Type:** Functional/Documentation | **Status:** Not Run

**Preconditions:**

- `pnpm dev:docs` running
- Navigate to bds-table → WithSearch story

**Test Steps:**

1. Verify story uses `searchable` prop (not old `slot="search-bar"`)
2. Type in search bar, press Enter
3. Verify table filters
4. Clear search
5. Verify full dataset restored

**Expected Result:**

- Story renders with `searchable` + `bds-search-bar`
- Filter/clear works via `bdsInputDebounced`/`bdsClear` wiring
- No reference to removed `slot="search-bar"`

---

#### TC-EOA-14935-T15-004: WithLongHeaderLabel / WithLongCellContent docs updated

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- bds-table MDX open to "Long header labels" / "Long cell content" sections

**Test Steps:**

1. Verify "(To be implemented in v2)" qualifier removed
2. Verify description: "tooltip anchors tightly to truncated text itself (not the padded cell/header)"
3. Verify note: "fully independent of the per-column `info` tooltip (both can exist on the same column without interfering)"

**Expected Result:**

- Docs reflect implemented behavior
- No "TODO" or "v2" references

---

#### TC-EOA-14935-T15-005: WithPinnedColumn story documents pinnable-hover

**Priority:** P1 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- WithPinnedColumn story open

**Test Steps:**

1. Verify doc comment mentions pinnable-only hover darkening (Task 13)
2. Story includes pinnable-only column (`id`, `pinnable` without `sortable`)

**Expected Result:**

- Doc comment updated
- Story demonstrates the hover behavior

---

#### TC-EOA-14935-T15-006: WithControlledSelection story exists

**Priority:** P0 | **Type:** Documentation | **Status:** Not Run

**Preconditions:**

- bds-table stories list

**Test Steps:**

1. Find `WithControlledSelection` story
2. Verify it demonstrates `selectedRows`/`selectedRowsChange`
3. Verify Vue `v-model:selectedRows` example if applicable

**Expected Result:**

- New story present
- Demonstrates controlled selection (Tasks 7/8)
