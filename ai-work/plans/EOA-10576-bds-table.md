---
status: in progress
---

# bds-table Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement the `bds-table` organism and `bds-table-column` atom for the Boreal DS data-visualization category, supporting native HTML table rendering, column sorting, row selection, column pinning, optional toolbar, and empty state.

**Ticket brief:** [`ai-work/tickets/EOA-10576-bds-table.md`](../tickets/EOA-10576-bds-table.md)

**Architecture:** Light DOM composition — implementors place `<bds-table-column>` elements inside `<bds-table>`; the table reads them via `querySelectorAll` in `componentDidLoad` and re-reads on `slotchange`. Row data is passed as a `data: RowData[]` prop. All interactive state (sort, selection) is hand-rolled with `@State` — no third-party table library. Internal rendering uses native `<table>/<thead>/<tbody>/<tr>/<th>/<td>` for semantic accessibility.

**Tech Stack:** Stencil, TypeScript (no `any`), SCSS with `var(--boreal-*)` tokens, native HTML table elements, CSS container queries for responsive toolbar.

---

## Figma Token Reference

Verified from node [55:39631](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29/-BOR--DSG-COMPONENTS-%E2%86%92-DATA-VISUALIZATION?node-id=55-39631). Use these exact Sass variables (defined in `_theme.scss`) — never invent token names.

| Role | Sass variable | CSS custom property |
|---|---|---|
| White / pinned cell bg | `$boreal-ui-inverse` | `var(--boreal-ui-inverse)` |
| Empty state bg / row hover | `$boreal-ui-default-lighter` | `var(--boreal-ui-default-lighter)` |
| Row divider / pin shadow | `$boreal-stroke-default-light` | `var(--boreal-stroke-default-light)` |
| `<th>` label text | `$boreal-text-default-light` | `var(--boreal-text-default-light)` |
| `<td>` cell text | `$boreal-text-default` | `var(--boreal-text-default)` |
| Sort icon inactive | `$boreal-icon-default-light` | `var(--boreal-icon-default-light)` |
| Sort icon active | `$boreal-icon-default-ink` | `var(--boreal-icon-default-ink)` |
| 2px spacing | `$boreal-spacing-3xs` | `var(--boreal-spacing-3xs)` |
| 4px spacing | `$boreal-spacing-2xs` | `var(--boreal-spacing-2xs)` |
| 8px spacing | `$boreal-spacing-xs` | `var(--boreal-spacing-xs)` |
| 12px spacing | `$boreal-spacing-s` | `var(--boreal-spacing-s)` |
| 16px spacing | `$boreal-spacing-m` | `var(--boreal-spacing-m)` |
| 24px spacing | `$boreal-spacing-l` | `var(--boreal-spacing-l)` |
| `<th>` font-size (12px) | `$boreal-typography-font-size-xs` | `var(--boreal-typography-font-size-xs)` |
| `<th>` line-height (16px) | `$boreal-typography-line-height-xs` | `var(--boreal-typography-line-height-xs)` |
| `<td>` font-size (14px) | `$boreal-typography-font-size-sm` | `var(--boreal-typography-font-size-sm)` |
| `<td>` line-height (20px) | `$boreal-typography-line-height-sm` | `var(--boreal-typography-line-height-sm)` |
| Semibold weight | `$boreal-typography-font-weight-semibold` | `var(--boreal-typography-font-weight-semibold)` |
| Regular weight | `$boreal-typography-font-weight-regular` | `var(--boreal-typography-font-weight-regular)` |

**Research:** `ai-work/research/2026-06-16-bds-table-column-api-spike.md`

---

## Files to create / modify

| File | Notes |
|---|---|
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/bds-table-column.tsx` | New — configuration-only Stencil component |
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/types/ITableColumn.ts` | New — column prop interface |
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/__test__/bds-table-column.basics.spec.ts` | New — unit tests |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` | New — organism component |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` | New — scoped styles with container queries |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/types/ITable.ts` | New — table prop/event/method interface |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/types/enum.ts` | New — `SORT_DIRECTION` enum |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/utils/bds-table-utils.ts` | New — sort comparator, column reader helpers |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.basics.spec.ts` | New — render and column reading tests |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.sort.spec.ts` | New — sorting behaviour tests |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.selection.spec.ts` | New — row selection tests |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.toolbar.spec.ts` | New — toolbar visibility and event tests |
| `packages/boreal-web-components/src/index.html` | Modify — add playground scenarios |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` | New — Storybook story |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` | New — MDX documentation |

---

## Utility Discovery Summary

| Feature area | Search location | Found | Reuse decision |
|---|---|---|---|
| Unique ID generation | `@/utils/helpers/common/BaseAttributes.tsx` | `createId(prefix)` | Reuse — checkbox input IDs |
| Prop validation | `@/utils/helpers/validateProps.ts` | `validatePropValue()` | Reuse — validate `sortDirection` enum |
| ARIA attribute inheritance | `@/utils/a11y` | `inheritAriaAttributes()` | Reuse — pass through `aria-label`, `aria-describedby` |
| Keyboard interaction | `@/utils/a11y/keyboard/KeyboardController.ts` | `KeyboardController` + `KEYBOARD` | Reuse — Enter/Space on sort headers |
| Class map type | `@/types/stylesMap.ts` | `StyleModifiers` | Reuse — class maps in render |
| Sort state machine | `@/utils/**` | Not found | Hand-roll — `sortKey` + `sortDirection` @State + comparator in utils |
| Row selection model | `@/utils/**` | Not found | Hand-roll — `selectedRowIds: Set<string>` @State |
| Sticky offset calculation | `@/utils/**` | Not found | Hand-roll — `componentDidRender` inline `style.left` |

---

## Task 1: Type interfaces

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table-column/types/ITableColumn.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/types/ITable.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/types/enum.ts` (create)

**Acceptance criteria:**

- `ITableColumn` interface declares: `key: string`, `label: string`, `sortable?: boolean`, `pinnable?: boolean`, `info?: string`, `formatter?: (params: { value: unknown; row: RowData }) => string | HTMLElement`
- `RowData` is a type alias `Record<string, unknown>` exported from `ITable.ts`
- `ITable` interface declares all `@Prop`, `@Event`, and `@Method` signatures for `bds-table`:
  - Props: `data: RowData[]`, `rowKey: string`, `selectable: boolean`, `subheading: string`, `tooltipText: string`, `maxHeight: string`
  - Events: `bdsSelect`, `bdsSort`, `bdsDelete`, `bdsEdit`, `bdsFilter`, `bdsTableLayout` — each typed with a detail payload
  - Methods: `getSelectedRows(): Promise<RowData[]>`, `clearSelection(): Promise<void>`
- `SORT_DIRECTION` enum in `enum.ts` with values `ASC = 'asc'`, `DESC = 'desc'`, `NONE = 'none'`
- No `any` types anywhere; all event detail payloads are explicit interfaces
- Existing `RowData`-related types in `@/types/` were checked — none found; new type is justified

**Manual test _(waiveable)_:** TypeScript compilation only — `pnpm tsc --noEmit` in `packages/boreal-web-components` passes with no errors.

**Commit:**
```
feat(web-components): EOA-10576 add type interfaces for bds-table and bds-table-column
```

---

## Task 2: `bds-table-column` scaffold

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table-column/bds-table-column.tsx` (create)

**Acceptance criteria:**

- Component tag is `bds-table-column`; class is `BdsTableColumn implements ITableColumn`
- `@Prop({ reflect: true }) readonly colKey: string` — the data accessor key; reflected as `col-key` attribute so `bds-table` can read it via `getAttribute('col-key')`. Stencil derives the kebab-case attribute name from the camelCase prop automatically.
- `@Prop({ reflect: true }) readonly label: string = ''` — column header text; reflected
- `@Prop({ reflect: true }) readonly sortable: boolean = false` — reflected
- `@Prop({ reflect: true }) readonly pinnable: boolean = false` — reflected
- `@Prop() readonly info: string = ''` — tooltip text for header info icon; not reflected (not needed for DOM reading)
- `@Prop() readonly formatter: ITableColumn['formatter']` — JS-only prop; not reflected
- `render()` returns `<Host style={{ display: 'none' }} />` — the element is hidden from layout; it serves only as a configuration carrier
- No SCSS file needed
- No slots
- JSDoc on class-level block and all `@Prop` declarations follows the pattern from `bds-tag.tsx` (existing sibling)

**Manual test _(waiveable)_:**

Playground scenarios in `packages/boreal-web-components/src/index.html`:
- Scenario 1: Place `<bds-table-column col-key="name" label="Name" sortable pinnable>` in the page and confirm it produces no visible output

Validation:
- [ ] Given a `<bds-table-column>` in the DOM, when the page loads, then no visible element is rendered. Pass: element has `display: none`.
- [ ] Given `col-key="name"` attribute, when `el.getAttribute('col-key')` is called from JS, then `"name"` is returned. Pass: reflected prop is readable as attribute.

**Commit:**
```
feat(web-components): EOA-10576 add bds-table-column configuration atom
```

---

## Task 3: `bds-table` scaffold — structure and data rendering

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/utils/bds-table-utils.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (create — minimal, expanded in later tasks)

**Acceptance criteria:**

- Component tag is `bds-table`; class is `BdsTable implements ITable`
- `@Element() el: HTMLBdsTableElement`
- `@Prop() readonly data: ITable['data'] = []` — array of row objects
- `@Prop({ attribute: 'row-key' }) readonly rowKey: string = 'id'` — the field name used as unique row identifier
- `@State() private columns: HTMLBdsTableColumnElement[] = []` — populated in `componentDidLoad`
- `componentDidLoad()` reads column children: `this.columns = Array.from(this.el.querySelectorAll('bds-table-column'))` and attaches a `slotchange` listener on the host to re-read when columns are added/removed dynamically
- `render()` produces:
  ```
  <Host>
    <div class="bds-table__wrapper">
      <table>
        <thead>
          <tr>
            [one <th scope="col"> per column, text = column.label]
          </tr>
        </thead>
        <tbody>
          [one <tr> per row in this.data]
            [one <td data-col-key={col.colKey}> per column]
              [if col.formatter exists: appendChild result; else: String(row[col.colKey] ?? '')]
        </tbody>
      </table>
    </div>
    <slot name="paginator"></slot>
  </Host>
  ```
- `bds-table-utils.ts` exports `readCellValue(row: RowData, colKey: string): unknown` — returns `row[colKey] ?? ''`
- Formatter result handling: if `formatter` returns an `HTMLElement`, use a `ref` callback on the `<td>` to `appendChild` it after render; if it returns a `string`, render it as text content
- `@Watch('data')` triggers re-render (Stencil does this automatically when a `@Prop` changes, but a `@Watch` is added to clear selection state in a later task — declare it now as a stub)
- SCSS: `:host { display: block; }`, `.bds-table__wrapper { overflow-x: auto; }`, `table { width: 100%; border-collapse: separate; border-spacing: 0; }` — all spacing via `var(--boreal-*)` tokens
- SCSS `<th>`: `font-size: $boreal-typography-font-size-xs; font-weight: $boreal-typography-font-weight-semibold; line-height: $boreal-typography-line-height-xs; color: $boreal-text-default-light` (matches Figma `supporting/label/xs`)
- SCSS `<td>`: `font-size: $boreal-typography-font-size-sm; font-weight: $boreal-typography-font-weight-regular; line-height: $boreal-typography-line-height-sm; color: $boreal-text-default` (matches Figma `body/sm`)
- SCSS `tr:hover td`: `background-color: $boreal-ui-default-lighter` — row hover highlight
- SCSS `thead`: `background-color: $boreal-ui-inverse` — header row stays white against scrolling body
- `inheritAriaAttributes` from `@/utils/a11y` is called in `componentWillLoad` to pass through host ARIA attributes to the `<table>` element

**Manual test _(waiveable)_:**

Playground scenarios in `packages/boreal-web-components/src/index.html`:
- Scenario 1: `<bds-table>` with three `<bds-table-column>` children and a `data` prop set via JS — three column headers and data rows render
- Scenario 2: Column with a `formatter` returning a `<bds-tag>` element — tag renders inside the cell
- Scenario 3: Column with a `formatter` returning a plain string — string renders as text

Validation (run `pnpm dev:components`):
- [ ] Given `data=[{id:1,name:'Alice'}]` and a `<bds-table-column col-key="name" label="Name">`, when the page loads, then one header "Name" and one data row "Alice" appear. Pass: correct text in DOM.
- [ ] Given a formatter returning `document.createElement('strong')` with text, when rendered, then a `<strong>` element is inside the `<td>`. Pass: element visible in DevTools.
- [ ] Given `data=[]`, when the page loads, then `<tbody>` is empty. Pass: no `<tr>` elements in `<tbody>`.

**Commit:**
```
feat(web-components): EOA-10576 scaffold bds-table with data and column rendering
```

---

## Task 4: Empty state

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- When `this.data.length === 0`, render a single `<tr>` inside `<tbody>` containing one `<td colspan={this.columns.length}>` that renders `<slot name="empty-state">` with a default fallback message
- The default message text is `"No data to display"` using `<bds-typography variant="body">` centred inside the cell
- When `this.data.length > 0`, the empty state `<tr>` is not rendered
- The `<td>` carrying the empty state has `class="bds-table__empty-state"` and the colspan accounts for the checkbox column when `selectable` will be added (use `this.columns.length + (this.selectable ? 1 : 0)` — `selectable` prop can be declared here as a stub `@Prop() readonly selectable: boolean = false` even though checkbox column is implemented in Task 6)
- SCSS: `.bds-table__empty-state { text-align: center; padding: $boreal-spacing-2xl; background-color: $boreal-ui-default-lighter; }` — light gray background matches Figma `ui (components)/default-lighter`

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: `<bds-table>` with `data=[]` and no `slot="empty-state"` — default message appears
- Scenario 2: Same with `<p slot="empty-state">Custom empty message</p>` — custom content appears
- Scenario 3: `<bds-table>` with data — no empty state row visible

Validation:
- [ ] Given `data=[]`, when the page loads, then "No data to display" text is centred in the table. Pass: text visible, no data rows present.
- [ ] Given `data=[]` and a filled `slot="empty-state"`, then custom slot content appears instead of the default. Pass: custom text visible.
- [ ] Given `data=[{id:1}]`, then no empty state row is rendered. Pass: `<tbody>` contains one data `<tr>`.

**Commit:**
```
feat(web-components): EOA-10576 add empty state slot with default fallback
```

---

## Task 5: Column sorting

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/utils/bds-table-utils.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- `@State() private sortKey: string = ''`
- `@State() private sortDirection: SORT_DIRECTION = SORT_DIRECTION.NONE`
- `@Event() bdsSort: EventEmitter<BdsSortEventDetail>` — emits after each sort toggle; payload shape is `{ colKey: string; direction: SORT_DIRECTION }`
- A private `sortedData` getter returns `[...this.data]` sorted by `this.sortKey` using `bds-table-utils.ts`'s `compareValues(a, b)` comparator; when `sortDirection === NONE` it returns `this.data` unchanged
- `compareValues` handles `string` (locale-aware), `number`, and `Date` values; falls back to string coercion for other types
- Sort is single-column only — changing the sort key resets direction to `ASC`; cycling on the same key goes `ASC → DESC → NONE`
- `render()` passes `sortedData` to the `<tbody>` row loop (replaces `this.data`)
- Each `<th>` for a `sortable` column renders: the label text, a sort icon (`bds-icon-sort`, `bds-icon-sort-asc`, `bds-icon-sort-desc` class depending on state), and an `onClick` handler calling `handleSort(col.colKey)`
- `handleSort(colKey)` implements the three-state cycle and emits `bdsSort`
- `KeyboardController` from `@/utils/a11y` is attached in `componentDidLoad` to handle `KEYBOARD.Enter` and `KEYBOARD.Space` on sortable `<th>` elements — calls `handleSort` on trigger
- `<th>` for sortable columns gets `role="button"` and `tabIndex={0}` to be keyboard focusable
- SCSS: sort icon classes styled with `$boreal-icon-default-light` in default/inactive state, `$boreal-icon-default-ink` when that column is the active sort column; `cursor: pointer` on sortable headers
- `disconnectedCallback()` calls `this._keyboard.detach()` — follow `bds-button.tsx` pattern

**Utility discovery note:** No shared sort state machine or comparator utility found in `@/utils/`. `compareValues` is implemented in `bds-table-utils.ts` (component-local). If a future shared comparator is added to `@/utils/helpers/`, migrate then.

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: Table with `sortable` column, unsorted data — click header once (ASC), again (DESC), again (NONE)
- Scenario 2: Click a different column while one is sorted — previous sort resets, new column sorts ASC
- Scenario 3: Focus a sortable header and press Enter — sort triggers

Validation:
- [ ] Given a sortable column, when clicked once, then rows are sorted ascending and sort icon shows ASC state. Pass: rows reordered, icon updated.
- [ ] When clicked again, then rows are sorted descending. Pass: rows reversed.
- [ ] When clicked a third time, then original data order is restored. Pass: rows in original order, icon shows neutral state.
- [ ] When sorted by column A then clicking column B, then column B sorts ASC and column A icon resets. Pass: only one column has active sort icon.
- [ ] Given focus on a sortable `<th>`, when Enter is pressed, then sort triggers identically to a click. Pass: `bdsSort` event fires in DevTools.

**Commit:**
```
feat(web-components): EOA-10576 add column sorting with keyboard support
```

---

## Task 6: Row selection

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- `@Prop() readonly selectable: boolean = false` (declared as stub in Task 4; implement logic here)
- `@State() private selectedRowIds: Set<string> = new Set()` — holds string IDs of selected rows
- `@Event() bdsSelect: EventEmitter<{ selectedIds: string[]; row: RowData }>` — emits when a single row is toggled
- `@Method() async getSelectedRows(): Promise<RowData[]>` — returns `this.data.filter(row => this.selectedRowIds.has(String(row[this.rowKey])))`
- `@Method() async clearSelection(): Promise<void>` — sets `this.selectedRowIds = new Set()`
- When `selectable === true`, render a leading `<th>` in the header containing a `<bds-checkbox>` for select-all; its `checked` state is `true` when all rows are selected, `indeterminate` when some are selected
- Each data `<tr>` gets a leading `<td>` containing a `<bds-checkbox>` bound to whether its row ID is in `selectedRowIds`
- `handleRowSelect(rowId, rowData)` toggles the row's ID in `selectedRowIds` (assign a new `Set` to trigger re-render) and emits `bdsSelect`
- `handleSelectAll()` — if all rows are selected, clears selection; otherwise selects all row IDs; does not emit `bdsSelect` per row — instead emits once with `selectedIds = allIds` and `row = undefined` (adjust event type to make `row` optional)
- `@Watch('data')` resets `selectedRowIds = new Set()` when data changes (clears stale selections)
- Selected rows get `class="bds-table__row--selected"` on their `<tr>`
- The checkbox column has a fixed width via `<col>` in a `<colgroup>` — follow `bds-tag.tsx` for SCSS column width patterns; use `var(--boreal-spacing-2xl)` as the checkbox cell width
- `createId('bds-table-checkbox')` from `@/utils/helpers` is used to generate unique IDs for each checkbox `<input>`; the pattern follows `bds-select.tsx`

**Utility discovery note:** `bds-checkbox` already exists at `packages/boreal-web-components/src/components/forms/bds-checkbox/`. Reuse it as a child component rather than a raw `<input type="checkbox">`. Its `checked` and `indeterminate` props are bindable.

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: `<bds-table selectable>` — checkbox column appears as first column
- Scenario 2: Check individual rows — selected rows are highlighted; `bdsSelect` fires
- Scenario 3: Check the header checkbox — all rows selected; check again — all deselected
- Scenario 4: Change `data` prop — selection clears

Validation:
- [ ] Given `selectable`, when the page loads, then a checkbox column is prepended. Pass: checkboxes visible in first column.
- [ ] Given an unchecked row, when its checkbox is clicked, then the row highlights and `bdsSelect` fires with the row's ID. Pass: DevTools event + visual highlight.
- [ ] When all rows are individually checked, then the header checkbox shows checked state. Pass: header checkbox checked.
- [ ] When the header checkbox is clicked from a partial selection, then all rows become selected. Pass: all rows highlighted.
- [ ] Given a selection, when `clearSelection()` is called via DevTools console, then all checkboxes uncheck. Pass: no highlighted rows.
- [ ] When `data` is updated to a new array, then all checkboxes reset to unchecked. Pass: no highlighted rows after update.

**Commit:**
```
feat(web-components): EOA-10576 add row selection with checkbox column
```

---

## Task 7: Column pinning

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- Columns whose `<bds-table-column>` has `pinnable` (the attribute is present) are rendered with `data-pinned` attribute on their `<th>` and every `<td data-col-key={col.colKey}>` in the body
- The column that is the rightmost pinned column additionally receives `data-pin-last` attribute, used by CSS for the divider shadow
- `componentDidRender()` queries `th[data-pinned]` elements in order, computes cumulative `offsetWidth`, and sets `el.style.left = "${offset}px"` on each pinned `<th>` and all matching `<td[data-col-key]>` cells in the same column — follow the pattern from the research spike (Section E, Option E2)
- SCSS for pinned cells uses `position: sticky`, `z-index: 3` on `<th>`, `z-index: 2` on `<td>`, and `background-color: $boreal-ui-inverse` — white background prevents scrolling content from showing through
- `tr:hover td[data-pinned]` must override background to `$boreal-ui-default-lighter` to maintain hover highlight on pinned cells (matches non-pinned `tr:hover td`)
- `th[data-pin-last]::after` and `td[data-pin-last]::after` pseudo-elements render a 1px right-edge divider using `$boreal-stroke-default-light` via `position: absolute`
- `thead` itself has `position: sticky; top: 0; z-index: 4` (sticky header row) to ensure pinned header cells stay above scrolling body cells
- `border-collapse: separate` is required on `<table>` (already set in Task 3) — `border-collapse: collapse` breaks `position: sticky`

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: Table with 8+ columns; first two have `pinnable`; horizontal scroll enabled
- Scenario 2: Same with `selectable` — confirm checkbox column + two pinned columns all stack correctly

Validation:
- [ ] Given two `pinnable` columns and a scrollable table, when scrolled right, then the two pinned columns remain fixed on the left. Pass: columns visible and stationary during scroll.
- [ ] Given a pinned column, when its row is hovered, then the pinned cell shows the same hover background as non-pinned cells. Pass: uniform row highlight.
- [ ] Given the last pinned column, then a vertical divider shadow is visible on its right edge. Pass: `::after` pseudo-element visible.
- [ ] Given `selectable` + two `pinnable` columns, then all three fixed columns stack with correct z-index (no overlap artefacts). Pass: no z-index bleed visible.

**Commit:**
```
feat(web-components): EOA-10576 add column pinning with sticky positioning
```

---

## Task 8: Toolbar — left zone

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- `@Prop() readonly subheading: string = ''` — when non-empty, toolbar renders
- `@Prop() readonly tooltipText: string = ''` — when non-empty, an info icon + `<bds-tooltip>` appears next to the subheading
- Private getter `hasToolbar` returns `true` when `this.subheading` is non-empty OR any of the toolbar slots (`search-bar`, `toolbar-actions`, `row-actions`) has assigned nodes; the check uses `this.el.querySelector('[slot="search-bar"]')` etc.
- When `hasToolbar` is false, the toolbar `<div>` is not rendered (conditional in JSX)
- Toolbar structure:
  ```
  <div class="bds-table__toolbar">
    <div class="bds-table__toolbar-left">
      <div class="bds-table__toolbar-left-heading">
        [if subheading] <bds-typography variant="subheading">{subheading}</bds-typography>
        [if tooltipText] <span class="bds-icon-info-circle" /> <bds-tooltip>{tooltipText}</bds-tooltip>
      </div>
      [if selectedRowIds.size > 0]
        <bds-tag>{selectedRowIds.size} items</bds-tag>
        <bds-button variant="plain" [icon-only delete icon] onClick={handleDelete} />
        <bds-button variant="plain" [icon-only edit icon] onClick={handleEdit} />
      <slot name="row-actions"></slot>
    </div>
    ...right zone in Task 9...
  </div>
  ```
- `@Event() bdsDelete: EventEmitter<{ selectedIds: string[] }>` — emits `Array.from(this.selectedRowIds)` when delete button clicked
- `@Event() bdsEdit: EventEmitter<{ selectedIds: string[] }>` — same shape, emits on edit button click
- Both buttons use `variant="plain"` and icon-only mode of `bds-button`; labels are `aria-label="Delete selected rows"` and `aria-label="Edit selected rows"`
- `bds-tag` shows the count; it is `readonly` (no close button); uses default `color` prop
- The `bds-typography` for subheading follows the pattern from `component-bds-typography-group-labels.md` memory entry
- SCSS: `.bds-table__toolbar { display: flex; justify-content: space-between; align-items: center; padding: $boreal-spacing-s 0; gap: $boreal-spacing-m; }` — all spacing tokens (`s` = 12px, `m` = 16px)

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: `<bds-table subheading="My Table">` — toolbar with title renders
- Scenario 2: Same with `tooltip-text="More info"` — info icon + tooltip next to title
- Scenario 3: `<bds-table>` with no `subheading` and no slots — no toolbar rendered
- Scenario 4: Select two rows in `selectable` table — count tag + delete/edit buttons appear
- Scenario 5: Click delete button — `bdsDelete` fires with selected IDs; click edit — `bdsEdit` fires

Validation:
- [ ] Given `subheading="My Table"`, when rendered, then "My Table" appears in subheading typography. Pass: text visible.
- [ ] Given `tooltip-text="Help"`, when the info icon is hovered, then "Help" tooltip appears. Pass: tooltip visible.
- [ ] Given no `subheading` and no toolbar slots, then no toolbar `<div>` exists in the DOM. Pass: `bds-table__toolbar` absent in DevTools.
- [ ] Given `selectable` table with 2 rows checked, then the count tag shows "2 items" and delete/edit buttons are visible. Pass: tag + buttons appear.
- [ ] When delete button is clicked, then `bdsDelete` fires with the 2 selected IDs. Pass: event detail in DevTools.

**Commit:**
```
feat(web-components): EOA-10576 add toolbar left zone with subheading and selection actions
```

---

## Task 9: Toolbar — right zone + auto-hide

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- Right zone appended inside `.bds-table__toolbar`:
  ```
  <div class="bds-table__toolbar-right">
    <slot name="search-bar"></slot>
    <bds-button variant="plain" [filter icon] aria-label="Filter" onClick={handleFilter} />
    <bds-button variant="plain" [table-layout icon] aria-label="Column visibility" onClick={handleTableLayout} />
    <slot name="toolbar-actions"></slot>
  </div>
  ```
- `@Event() bdsFilter: EventEmitter<void>` — emits on filter button click; no payload
- `@Event() bdsTableLayout: EventEmitter<void>` — emits on layout button click; no payload
- Both buttons use `variant="plain"` and icon-only mode of `bds-button`
- The filter button uses `bds-icon-filter` icon class; the layout button uses `bds-icon-table` icon class
- `hasToolbar` getter (from Task 8) must also check `slot="toolbar-actions"` and `slot="search-bar"` slots — if any of these slots has assigned nodes, the toolbar renders; this ensures the toolbar appears when only the right-side slots are used (no `subheading`)
- SCSS: `.bds-table__toolbar-right { display: flex; align-items: center; gap: $boreal-spacing-s; }` — `s` = 12px

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: `<bds-table subheading="My Table">` — filter and layout buttons appear on the right
- Scenario 2: Click filter button — `bdsFilter` event fires
- Scenario 3: Click layout button — `bdsTableLayout` event fires
- Scenario 4: `<bds-table>` with `<button slot="toolbar-actions">Export</button>` and no `subheading` — toolbar renders with just the right zone
- Scenario 5: `<bds-table>` with no subheading and no slots — toolbar absent

Validation:
- [ ] Given a table with `subheading`, when rendered, then filter and layout icon buttons appear on the right. Pass: buttons visible.
- [ ] When filter button is clicked, then `bdsFilter` fires with no payload. Pass: event in DevTools.
- [ ] When layout button is clicked, then `bdsTableLayout` fires. Pass: event in DevTools.
- [ ] Given only `slot="toolbar-actions"` filled (no `subheading`), then the toolbar renders. Pass: toolbar div present.
- [ ] Given no `subheading` and no filled slots, then toolbar `<div>` is absent. Pass: not in DOM.

**Commit:**
```
feat(web-components): EOA-10576 add toolbar right zone with filter and layout actions
```

---

## Task 10: Responsive toolbar

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- `:host` has `container-type: inline-size` — enables CSS container queries scoped to the component's own width
- At `@container (max-width: 744px)`:
  - `.bds-table__toolbar-left-heading` is hidden (`display: none`) — subheading and tooltip collapse
  - `.bds-table__toolbar-right` reduces `gap` to `$boreal-spacing-xs` — compact right-zone (8px)
- No JavaScript or `ResizeObserver` involved — this is a pure CSS change
- No hardcoded pixel sizes in token-based values; the `744px` breakpoint is the one CSS value that may remain as a literal (it is a design spec breakpoint, not a spacing token)
- Existing toolbar SCSS from Tasks 8–9 is not duplicated — only the override rules go inside the `@container` block

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: Place `<bds-table>` inside a `<div style="width: 500px">` — toolbar heading collapses

Validation:
- [ ] Given a table inside a 500px-wide container, when rendered, then the subheading is hidden and the toolbar right zone compresses. Pass: heading absent, buttons still visible.
- [ ] Given a table in a 900px-wide container, then the full toolbar is visible. Pass: heading present.

**Commit:**
```
feat(web-components): EOA-10576 add responsive toolbar with CSS container queries
```

---

## Task 11: Column header truncation + tooltip

**Executor:** @frontend-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- Each `<th>` renders the label text inside a `<span class="bds-table__col-label">` with `text-overflow: ellipsis; overflow: hidden; white-space: nowrap` applied via SCSS
- When a column has `info` set on its `<bds-table-column>`, an info icon (`bds-icon-info-circle`) and a `<bds-tooltip>` wrapping it are rendered in the header, identical to the `bds-typography` tooltip pattern (see `bds-typography.tsx:151–156`)
- When a column label overflows its cell, the same `<bds-tooltip>` approach is used: the full label text is the tooltip content (set on hover); the truncated label remains visible — follow the `bds-typography` ellipsis + tooltip pattern
- The `<th>` inner layout uses `display: flex; align-items: center; gap: var(--boreal-spacing-xs)` to align: sort icon | label span | info icon
- `maxHeight` prop: `@Prop() readonly maxHeight: string = ''` — when non-empty, sets a CSS custom property `--bds-table-max-height` on the host via inline style; the `.bds-table__wrapper` SCSS reads it as `max-height: var(--bds-table-max-height, unset); overflow-y: var(--bds-table-overflow-y, visible)` — set `overflow-y: auto` via a second custom property when `maxHeight` is set

**Manual test _(waiveable)_:**

Playground scenarios:
- Scenario 1: Column with a very long label in a narrow table — label truncates with ellipsis
- Scenario 2: Column with `info="Full description of this column"` — info icon shows; tooltip on hover
- Scenario 3: `max-height="300px"` on a table with many rows — vertical scrollbar appears; header stays sticky

Validation:
- [ ] Given a long column label, when the column is narrow, then the label is truncated with `…`. Pass: ellipsis visible.
- [ ] Given a column with `info` text, when the info icon is hovered, then the tooltip shows the full info text. Pass: tooltip appears.
- [ ] Given `max-height="200px"` with 20 data rows, then the table body scrolls vertically and the header remains fixed. Pass: sticky header during scroll.

**Commit:**
```
feat(web-components): EOA-10576 add column header truncation tooltip and maxHeight scroll
```

---

## Task 12: Unit tests — `bds-table-column`

**Executor:** @testing-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table-column/__test__/bds-table-column.basics.spec.ts` (create)

**Acceptance criteria:**

- Uses `newSpecPage` from `@stencil/core/testing`; registers `BdsTableColumn` in `components`
- Tests confirm behavior through the component's public prop API

**Unit tests to cover** _(spec file: `bds-table-column.basics.spec.ts`)_:

- Default rendering — element renders with `display: none` style; no visible child nodes
- `colKey` prop is reflected as `col-key` attribute — `el.getAttribute('col-key')` returns the set value
- `label` prop is reflected — `el.getAttribute('label')` returns the set value
- `sortable` attribute presence — when `sortable` is set, `el.hasAttribute('sortable')` is true; when absent, false
- `pinnable` attribute presence — same pattern as `sortable`
- `info` prop — readable as a JS property; not reflected to attribute
- `formatter` prop — accepts a function; readable as a JS property; does not throw when assigned

**Commit:**
```
test(web-components): EOA-10576 add unit tests for bds-table-column
```

---

## Task 13: Unit tests — `bds-table` basics, sort, selection, toolbar

**Executor:** @testing-subagent

**Files:**
- `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.basics.spec.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.sort.spec.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.selection.spec.ts` (create)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.toolbar.spec.ts` (create)

**Acceptance criteria:**

- All spec files use `newSpecPage`; register `[BdsTable, BdsTableColumn]` (and child components `BdsCheckbox`, `BdsTypography`, `BdsTag`, `BdsButton`, `BdsTooltip` as needed)
- Follow the child component prop assertion pattern from `.agents/memory/stencil-child-component-props-in-tests.md` — assert on rendered DOM output, not on JS properties of child custom elements

**Unit tests to cover — `bds-table.basics.spec.ts`:**

- Renders a `<table>` element
- Renders one `<th>` per `bds-table-column` child with correct label text
- Renders one `<tr>` in `<tbody>` per item in `data`
- Renders cell text from `data[row][column.colKey]` in the correct `<td>`
- Formatter returning a string — cell `<td>` text matches the returned string
- `row-key` attribute defaults to `'id'` when not provided
- Empty `data` — `<tbody>` contains the empty state row; no data `<tr>` elements
- `slot="empty-state"` filled — empty state slot content appears in empty state cell
- `slot="paginator"` — slot is present in the rendered output
- `@Watch('data')` change — re-renders with new rows

**Unit tests to cover — `bds-table.sort.spec.ts`:**

- Non-sortable column `<th>` — no click handler, no sort icon
- Sortable column `<th>` — clicking emits `bdsSort` with `{ colKey, direction: 'asc' }`
- Clicking the same header again — emits `bdsSort` with `direction: 'desc'`
- Clicking again — emits `bdsSort` with `direction: 'none'` and rows return to original order
- Clicking a different sortable column — resets first column to `none`, new column emits `asc`
- `sortedData` getter — ascending sort orders rows correctly for string values; descending reverses them

**Unit tests to cover — `bds-table.selection.spec.ts`:**

- Without `selectable` — no checkbox column in header or rows
- With `selectable` — first `<th>` and first `<td>` in each row contain a `bds-checkbox`
- Checking a row checkbox — `bdsSelect` event emits with the correct row ID in `selectedIds`
- `getSelectedRows()` — returns the full row objects matching selected IDs
- `clearSelection()` — resets internal selection; subsequent `getSelectedRows()` returns `[]`
- Header checkbox indeterminate state — when some but not all rows are selected
- Header checkbox checked — when all rows are selected
- `@Watch('data')` reset — selecting rows then updating `data` clears the selection

**Unit tests to cover — `bds-table.toolbar.spec.ts`:**

- No `subheading` and no toolbar slots — toolbar `<div>` is absent from the DOM
- `subheading="My Table"` — toolbar renders; subheading text is present
- `tooltip-text="Info"` — info icon and `bds-tooltip` are rendered in the toolbar
- `selectedRowIds.size === 0` — delete and edit buttons are absent
- `selectedRowIds.size > 0` — delete and edit buttons are present
- Delete button click — `bdsDelete` emits with `selectedIds` array
- Edit button click — `bdsEdit` emits with `selectedIds` array
- Filter button click — `bdsFilter` emits
- Layout button click — `bdsTableLayout` emits

**Commit:**
```
test(web-components): EOA-10576 add unit tests for bds-table rendering, sort, selection, and toolbar
```

---

## Task 14: Storybook story

**Executor:** @documentation-subagent

**Files:**
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (create)

**Acceptance criteria:**

- Story file follows the existing pattern from `apps/boreal-docs/src/stories/feedback/bds-tag/bds-tag.stories.ts`
- Category: `Data Visualization / Table`
- Stories to include:
  - `Default` — basic table with 3 columns and 5 data rows, no extras
  - `WithSorting` — two sortable columns; `bdsSort` action logged
  - `WithSelection` — `selectable` enabled; `bdsSelect`, `bdsDelete`, `bdsEdit` actions logged
  - `WithToolbar` — `subheading`, `tooltip-text`, filter + layout button events logged
  - `WithPinnedColumn` — first column has `pinnable`; table wide enough to require scroll
  - `EmptyState` — `data=[]`; default empty state message visible
  - `WithCustomEmptyState` — `data=[]`; custom `slot="empty-state"` content
  - `WithFormatter` — one column uses a `formatter` returning a `bds-tag` element
  - `WithMaxHeight` — `max-height="300px"` with 20 rows; vertical scroll visible
- JS property bindings for `data`, `formatter`, and `columns` are documented in an MDX "How to use it" note (not in the Source panel, which cannot show them)

**Commit:**
```
docs(docs): EOA-10576 add Storybook stories for bds-table
```

---

## Task 15: MDX documentation

**Executor:** @documentation-subagent

**Files:**
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (create)

**Acceptance criteria:**

- MDX file follows the structure of an existing documentation file — use `apps/boreal-docs/src/stories/feedback/bds-tag/bds-tag.mdx` as the pattern reference
- Sections to include:
  - **Overview** — what `bds-table` is, when to use it, component anatomy (toolbar / content / paginator)
  - **Component family** — explains `bds-table` + `bds-table-column` relationship; why `bds-table-column` renders nothing visible
  - **Column definition** — `<bds-table-column>` props table (`col-key`, `label`, `sortable`, `pinnable`, `info`, `formatter`); code snippet showing declarative markup
  - **Custom cell content** — how to use the `formatter` prop with a code example using `document.createElement`
  - **Row selection** — how to use `selectable`, `getSelectedRows()`, `clearSelection()`, `bdsSelect` event
  - **Column sorting** — single-column sort, `bdsSort` event, `SORT_DIRECTION` values
  - **Column pinning** — how to use `pinnable`, what happens at render time
  - **Toolbar** — slot map table (`search-bar`, `row-actions`, `toolbar-actions`); when toolbar auto-hides; events (`bdsFilter`, `bdsTableLayout`, `bdsDelete`, `bdsEdit`)
  - **Empty state** — `slot="empty-state"` and default behaviour
  - **Paginator integration** — `slot="paginator"` for future `bds-paginator`; wiring example
  - **Accessibility** — native `<table>` semantics; `th[scope="col"]`; keyboard sort interaction
  - **What's coming in v2** — column grouping, drag/drop reorder, virtualization, column visibility dropdown

**Commit:**
```
docs(docs): EOA-10576 add MDX documentation for bds-table
```
