# Test Plan: EOA-14935 bds-table v2 (Condensed)

**Ticket:** EOA-14935 | **Components:** `bds-table`, `bds-pagination`, `bds-tooltip` | **Status:** Done (2026-07-09)

---

## Scope (12 Shipped Tasks)

| Task | Component      | Feature                                               |
| ---- | -------------- | ----------------------------------------------------- |
| 1    | bds-pagination | Fix `totalItems` watcher snap-back                    |
| 2    | bds-pagination | Fix empty-state literal "1"                           |
| 3    | bds-pagination | Add `loading` prop                                    |
| 4    | bds-pagination | Tests + docs consolidation                            |
| 5    | bds-tooltip    | Manual mode + `show`/`hide`/`anchorTo`                |
| 6    | bds-tooltip    | Manual mode docs                                      |
| 7    | bds-table      | Controlled `selectedRows` prop + `selectedRowsChange` |
| 8    | bds-table      | Vue `v-model:selectedRows` wiring                     |
| 12   | bds-table      | `searchable` prop + `bds-search-bar` fixes            |
| 13   | bds-table      | Pinnable-only column hover darkening                  |
| 14   | bds-table      | Overflow tooltip on truncated text                    |
| 15   | bds-table      | Docs for 7,8,12,13,14                                 |

---

## Test Strategy

| Type          | Coverage           | Tool                                      |
| ------------- | ------------------ | ----------------------------------------- |
| Unit          | ≥90% per component | Jest (CI)                                 |
| Mutation      | ≥90% per component | Stryker (batched in v3)                   |
| Manual/Visual | All UI behaviors   | `pnpm dev:components` and `pnpm dev:docs` |
| Regression    | P0: 100%, P1: ≥90% | Full suite/PR                             |

**Env:** Chrome/FF/Safari latest, Desktop/Tablet/Mobile, themes: proximus/connect/engage/protect

---

## Exit Criteria

- [ ] All manual tests pass
- [ ] No P0/P1 bugs open
- [ ] Regression: 100% P0, ≥90% P1 pass

---

## Test Cases by Task

### Task 1: Pagination `totalItems` Watcher Snap-Back Fix

| ID   | Scenario                                  | Expected                                                             |
| ---- | ----------------------------------------- | -------------------------------------------------------------------- |
| T1-1 | On page 3 (50 items), set `totalItems=30` | Stays page 3 (30/10=3 pages), no snap-back                           |
| T1-2 | On page 5 (50 items), set `totalItems=25` | Clamps to page 3 (max valid)                                         |
| T1-3 | Unit: watcher uses `internalCurrentPage`  | `normalizePage(this.internalCurrentPage)` called, JSDoc explains why |

### Task 2: Pagination Empty State

| ID   | Scenario                 | Expected                                    |
| ---- | ------------------------ | ------------------------------------------- |
| T2-1 | Render `total-items="0"` | No literal "1" in DOM; nav buttons disabled |
| T2-2 | Click disabled buttons   | No `bdsPageChange` emitted                  |
| T2-3 | Unit: `totalItems={0}`   | No text "1"; buttons have `disabled=true`   |

### Task 3: Pagination `loading` Prop

| ID   | Scenario               | Expected                                                                 |
| ---- | ---------------------- | ------------------------------------------------------------------------ |
| T3-1 | Set `loading=true`     | All nav buttons + items-per-page select disabled; clicks no-op           |
| T3-2 | Visual: `loading=true` | Disabled styling (opacity, cursor not-allowed)                           |
| T3-3 | Unit: `loading` prop   | `true` forces disabled regardless of page/total; `false` preserves logic |

### Task 4: Pagination Tests + Docs

| ID   | Scenario           | Expected                                                      |
| ---- | ------------------ | ------------------------------------------------------------- |
| T4-1 | Coverage report    | ≥90% lines/functions/branches/statements                      |
| T4-2 | Storybook Controls | `loading` appears (boolean, default false), toggle works live |

### Task 5: Tooltip Manual Mode

| ID   | Scenario                               | Expected                                                                                                                                                        |
| ---- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T5-1 | `manual=true`, `anchorTo(A)`, `show()` | Tooltip on A without hover                                                                                                                                      |
| T5-2 | `anchorTo(B)` then hover A             | No tooltip on A (no listener leak)                                                                                                                              |
| T5-3 | `hide()`                               | Tooltip dismissed, can re-show                                                                                                                                  |
| T5-4 | Default (non-manual) mode              | Hover/focus behavior unchanged                                                                                                                                  |
| T5-5 | Unit: manual methods                   | `manual=true` skips auto-discovery; `anchorTo`/`showTooltip`/`hideTooltip` work; `disconnectedCallback` cleans up; repeated `anchorTo` replaces not accumulates |

### Task 6: Tooltip Manual Mode Docs

| ID   | Scenario                                 | Expected                                 |
| ---- | ---------------------------------------- | ---------------------------------------- |
| T6-1 | Storybook "Programmatic control" section | Renders with working example matching T5 |

### Task 7: Table Controlled `selectedRows`

| ID   | Scenario                             | Expected                                                                                                                        |
| ---- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| T7-1 | `selectedRows = ['1','3']`           | Rows 1,3 checked; header indeterminate                                                                                          |
| T7-2 | `selectedRows = []`                  | All unchecked; header unchecked                                                                                                 |
| T7-3 | Click row checkbox                   | `selectedRowsChange` fires with new array; prop updates                                                                         |
| T7-4 | Header select all/deselect           | `selectedRowsChange` fires with all ids / `[]`                                                                                  |
| T7-5 | External change triggers `bdsSelect` | `bdsSelect` fires with `{selectedIds, row}`                                                                                     |
| T7-6 | Unit: controlled selection           | Setter updates state; getter returns current; external change re-renders; both events emitted; persists across sort/filter/page |

### Task 8: Vue `v-model:selectedRows`

| ID   | Scenario                                     | Expected                                                            |
| ---- | -------------------------------------------- | ------------------------------------------------------------------- |
| T8-1 | Vue `<bds-table v-model:selectedRows="sel">` | User click → `sel` updates; `sel.value=['2']` → UI updates          |
| T8-2 | Unit: `selectedRowsChange` payload           | Detail is `string[]` (not object); matches `valueChange` convention |

### Task 12: Table `searchable` + `bds-search-bar` Fixes

| ID    | Scenario                           | Expected                                                                                                        |
| ----- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| T12-1 | `searchable=true`                  | Search icon in toolbar right zone (collapsed)                                                                   |
| T12-2 | Click search icon                  | Expands **leftward** (icon moves left, input right); no overlap with Filter/Column icons                        |
| T12-3 | Type + Enter                       | `bdsSearch` fires; consumer filters; table updates                                                              |
| T12-4 | Clear input / `bdsClear`           | `bdsClear` fires; consumer restores full data                                                                   |
| T12-5 | `searchable=false` (default)       | No search element; no residual DOM                                                                              |
| T12-6 | Unit: `searchable` prop/events     | Renders search bar; `hasToolbar` true; events bubble                                                            |
| T12-7 | Unit: `bds-search-bar` mode=search | Collapsed at minimized; click expands; `clearable=true` shows ×; `clearable=false` hides; `mode=list` unchanged |

### Task 13: Pinnable-Only Hover State

| ID    | Scenario                   | Expected                                                                                                                         |
| ----- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| T13-1 | Hover pinnable-only header | Pin icon darkens to `$boreal-icon-default-ink` (like sortable icon); no pointer cursor                                           |
| T13-2 | Sortable-only header       | Sort icon darkens; no `data-pinnable` attr                                                                                       |
| T13-3 | Unit: attributes + SCSS    | `pinnable` → `data-pinnable`; `sortable` → `data-sortable` only; SCSS `th[data-pinnable]:hover .bds-table__th-actions i` matches |

### Task 14: Overflow Tooltip

| ID    | Scenario                            | Expected                                                                                                                                                                                                                                |
| ----- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T14-1 | Hover truncated header              | Tooltip shows full text; anchors to text (not cell); mouse away hides                                                                                                                                                                   |
| T14-2 | Hover truncated cell                | Same as header                                                                                                                                                                                                                          |
| T14-3 | Hover non-truncated                 | No overflow tooltip; `info` tooltip works                                                                                                                                                                                               |
| T14-4 | Column has both truncation + `info` | Both tooltips work independently (overflow = manual singleton; info = default auto)                                                                                                                                                     |
| T14-5 | Unit: delegation                    | Singleton `bds-tooltip manual` in render; capture `mouseenter`/`leave` on wrapper; `scrollWidth>clientWidth` → `anchorTo`+`show`; non-truncated → nothing; `leave` → `hide`; cleanup in `disconnectedCallback`; `info` tooltip separate |

### Task 15: Documentation

| ID    | Scenario                                    | Expected                                                                                                           |
| ----- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| T15-1 | Limitations table                           | Rows 1,3,12 (overflow tooltip, controlled selection, built-in search) removed; renumbered; row 2 (dataset) remains |
| T15-2 | ArgTypes                                    | `selected-rows`, `selectedRowsChange`, `searchable` present with correct types                                     |
| T15-3 | `WithSearch` story                          | Uses `searchable` prop (not `slot="search-bar"`); filter/clear works via `bdsInputDebounced`/`bdsClear`            |
| T15-4 | `WithLongHeaderLabel`/`WithLongCellContent` | "(To be implemented in v2)" removed; describes tight anchoring + independence from `info` tooltip                  |
| T15-5 | `WithPinnedColumn` story                    | Doc mentions pinnable-only hover darkening; includes pinnable-only column                                          |
| T15-6 | `WithControlledSelection` story             | Exists; demonstrates `selectedRows`/`selectedRowsChange` (Tasks 7/8)                                               |

---

## Test Data

| Area            | Data                                                                 |
| --------------- | -------------------------------------------------------------------- |
| Pagination      | `totalItems: 0,30,50,100`; `itemsPerPage: 10`; various `currentPage` |
| Tooltip         | 2 anchor buttons; tooltip content string                             |
| Table selection | 3-5 rows with unique `id`; `selectable=true`                         |
| Table search    | Names: Alice, Bob, Charlie                                           |
| Table pinnable  | 2 cols: 1 `sortable`, 1 `pinnable` only                              |
| Table overflow  | `max-width: 260px`; long header + long cell; column with `info`      |

---

## Manual Test Quick Reference (from index.html)

| Task | Steps                                                        | Pass Criteria                                         |
| ---- | ------------------------------------------------------------ | ----------------------------------------------------- |
| 1    | Go page 3 (50 items) → Set totalItems=30                     | Stays page 3, no snap-back                            |
| 2    | Render `total-items="0"`                                     | No "1", buttons disabled                              |
| 3    | Toggle loading                                               | Controls disabled/enabled; clicks no-op while loading |
| 5    | Anchor A → Show → Anchor B → Hover A (nothing) → Show → Hide | Tooltip on A, no leak on A, on B, dismisses           |
| 7    | Set selectedRows=['1','3'] → Set [] → Check console          | Rows 1,3 checked → all unchecked; events fire         |
| 12   | Click search icon → Type+Enter → Clear                       | Expands leftward no overlap; filters; restores        |
| 13   | Hover pinnable-only header                                   | Pin icon darkens like sortable; no pointer cursor     |
| 14   | Hover truncated header/cell → Hover info icon                | Full text tooltip; hides on leave; info tooltip works |
