---
status: in progress
---

# bds-table Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement the `bds-table` organism and `bds-table-column` atom for the Boreal DS data-visualization category, supporting native HTML table rendering, column sorting, row selection, column pinning, optional toolbar, and empty state.

**Ticket brief:** [`ai-work/tickets/EOA-10576-bds-table.md`](../tickets/EOA-10576-bds-table.md)

**Architecture:** Light DOM composition — implementors place `<bds-table-column>` elements inside `<bds-table>`; the table reads them via `querySelectorAll` in `componentDidLoad` and re-reads via a `MutationObserver({ childList: true })` when columns are added/removed dynamically (`slotchange` does not fire for direct DOM children in light DOM). Row data is passed as a `data: RowData[]` prop. All interactive state (sort, selection) is hand-rolled with `@State` — no third-party table library. Internal rendering uses native `<table>/<thead>/<tbody>/<tr>/<th>/<td>` for semantic accessibility.

**Tech Stack:** Stencil, TypeScript (no `any`), SCSS with `var(--boreal-*)` tokens, native HTML table elements, CSS container queries for responsive toolbar.

---

## Figma Token Reference

Verified from node [55:39631](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29/-BOR--DSG-COMPONENTS-%E2%86%92-DATA-VISUALIZATION?node-id=55-39631). Use these exact Sass variables (defined in `_theme.scss`) — never invent token names.

| Role                       | Sass variable                             | CSS custom property                             |
| -------------------------- | ----------------------------------------- | ----------------------------------------------- |
| White / pinned cell bg     | `$boreal-ui-inverse`                      | `var(--boreal-ui-inverse)`                      |
| Empty state bg / row hover | `$boreal-ui-default-lighter`              | `var(--boreal-ui-default-lighter)`              |
| Row divider / pin shadow   | `$boreal-stroke-default-light`            | `var(--boreal-stroke-default-light)`            |
| `<th>` label text          | `$boreal-text-default-light`              | `var(--boreal-text-default-light)`              |
| `<td>` cell text           | `$boreal-text-default`                    | `var(--boreal-text-default)`                    |
| Sort icon inactive         | `$boreal-icon-default-light`              | `var(--boreal-icon-default-light)`              |
| Sort icon active           | `$boreal-icon-default-ink`                | `var(--boreal-icon-default-ink)`                |
| 2px spacing                | `$boreal-spacing-3xs`                     | `var(--boreal-spacing-3xs)`                     |
| 4px spacing                | `$boreal-spacing-2xs`                     | `var(--boreal-spacing-2xs)`                     |
| 8px spacing                | `$boreal-spacing-xs`                      | `var(--boreal-spacing-xs)`                      |
| 12px spacing               | `$boreal-spacing-s`                       | `var(--boreal-spacing-s)`                       |
| 16px spacing               | `$boreal-spacing-m`                       | `var(--boreal-spacing-m)`                       |
| 24px spacing               | `$boreal-spacing-l`                       | `var(--boreal-spacing-l)`                       |
| `<th>` font-size (12px)    | `$boreal-typography-font-size-xs`         | `var(--boreal-typography-font-size-xs)`         |
| `<th>` line-height (16px)  | `$boreal-typography-line-height-xs`       | `var(--boreal-typography-line-height-xs)`       |
| `<td>` font-size (14px)    | `$boreal-typography-font-size-sm`         | `var(--boreal-typography-font-size-sm)`         |
| `<td>` line-height (20px)  | `$boreal-typography-line-height-sm`       | `var(--boreal-typography-line-height-sm)`       |
| Semibold weight            | `$boreal-typography-font-weight-semibold` | `var(--boreal-typography-font-weight-semibold)` |
| Regular weight             | `$boreal-typography-font-weight-regular`  | `var(--boreal-typography-font-weight-regular)`  |
| Container radius (4px)     | `$boreal-radius-xs`                       | `var(--boreal-radius-xs)`                       |

**Research:** `ai-work/research/2026-06-16-bds-table-column-api-spike.md`

---

## Files to create / modify

| File                                                                                                                         | Notes                                        |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/bds-table-column.tsx`                     | New — configuration-only Stencil component   |
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/types/ITableColumn.ts`                    | New — column prop interface                  |
| `packages/boreal-web-components/src/components/data-visualization/bds-table-column/__test__/bds-table-column.basics.spec.ts` | New — unit tests                             |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx`                                   | New — organism component                     |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.scss`                                  | New — scoped styles with container queries   |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/types/ITable.ts`                                 | New — table prop/event/method interface      |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/types/enum.ts`                                   | New — `SORT_DIRECTION` enum                  |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/utils/bds-table-utils.ts`                        | New — sort comparator, column reader helpers |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.basics.spec.ts`               | New — render and column reading tests        |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.sort.spec.ts`                 | New — sorting behaviour tests                |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.selection.spec.ts`            | New — row selection tests                    |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/__test__/bds-table.toolbar.spec.ts`              | New — toolbar visibility and event tests     |
| `packages/boreal-web-components/src/index.html`                                                                              | Modify — add playground scenarios            |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`                                             | New — Storybook story                        |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx`                                                    | New — MDX documentation                      |

---

## Utility Discovery Summary

| Feature area               | Search location                               | Found                             | Reuse decision                                                       |
| -------------------------- | --------------------------------------------- | --------------------------------- | -------------------------------------------------------------------- |
| Unique ID generation       | `@/utils/helpers/common/BaseAttributes.tsx`   | `createId(prefix)`                | Reuse — checkbox input IDs                                           |
| Prop validation            | `@/utils/helpers/validateProps.ts`            | `validatePropValue()`             | Reuse — validate `sortDirection` enum                                |
| ARIA attribute inheritance | `@/utils/a11y`                                | `inheritAriaAttributes()`         | Reuse — pass through `aria-label`, `aria-describedby`                |
| Keyboard interaction       | `@/utils/a11y/keyboard/KeyboardController.ts` | `KeyboardController` + `KEYBOARD` | Reuse — Enter/Space on sort headers                                  |
| Class map type             | `@/types/stylesMap.ts`                        | `StyleModifiers`                  | Reuse — class maps in render                                         |
| Sort state machine         | `@/utils/**`                                  | Not found                         | Hand-roll — `sortKey` + `sortDirection` @State + comparator in utils |
| Row selection model        | `@/utils/**`                                  | Not found                         | Hand-roll — `selectedRowIds: Set<string>` @State                     |
| Sticky offset calculation  | `@/utils/**`                                  | Not found                         | Hand-roll — `componentDidRender` inline `style.left`                 |

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
- `componentDidLoad()` reads column children: `this.columns = Array.from(this.el.querySelectorAll('bds-table-column'))` and attaches a `MutationObserver({ childList: true })` on the host to re-read when `bds-table-column` children are added/removed dynamically; observer is disconnected in `disconnectedCallback()`
- `render()` produces:
  ```
  <Host>
    <div class="bds-table__wrapper">
      <table>
        <thead>
          <tr>
            [one <th scope="col"> per column]
              <span class="bds-table__th-content">   ← flex: space-between (right side for Task 5 sort / Task 7 pin)
                <span class="bds-table__th-label">   ← flex: center, gap 2xs
                  [if col.icon: <i class={col.icon} aria-hidden="true" />]
                  <bds-typography variant="label" tooltipText={col.info || undefined}>
                    {col.label}
                  </bds-typography>
                </span>
              </span>
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
- SCSS: `bds-table { display: flex; flex-direction: column; gap: $boreal-spacing-xs; padding: $boreal-spacing-m $boreal-spacing-l; border: 1px solid $boreal-stroke-default-light; border-radius: $boreal-radius-xs; overflow: clip; background-color: $boreal-ui-inverse; }` — outer chrome on the host element; `overflow: clip` clips to the radius without creating a scroll container (preserves `position: sticky` for Task 7 pinning); `flex-direction: column` + `gap` makes toolbar (Task 8) and paginator slot natural flex siblings of `.bds-table__wrapper`
- SCSS: `.bds-table__wrapper { overflow-x: auto; }`, `table { width: 100%; border-collapse: separate; border-spacing: 0; }` — all spacing via `var(--boreal-*)` tokens
- **`bds-table-column` gets an `icon: string = ''` prop** — CSS icon class (e.g. `bds-icon-emoji-circle`) rendered as `<i class={col.icon} aria-hidden="true" />` to the left of the label; not reflected to the DOM attribute
- **Column header uses `bds-typography variant="label"`** — replaces the bare `{col.label}` text; `tooltipText={col.info || undefined}` wires the existing `info` prop into the built-in info icon; color overridden via `th .bds-typography--label { color: $boreal-text-default-light }` in SCSS (default variant color is `$boreal-text-default-darker`)
- **`__th-content`** flex container inside each `<th>`: `display: flex; align-items: center; justify-content: space-between` — left group holds icon + typography; right group is empty now (Task 5 adds sort icon, Task 7 adds pin icon)
- **`__th-label`** inner flex group: `display: flex; align-items: center; gap: $boreal-spacing-2xs` — icon + bds-typography side-by-side
- SCSS `<th>`: `height: var(--bds-table-header-height, 44px)` — exposed as a CSS custom property (same pattern as `--bds-table-empty-state-height`); 44px matches col-table and Figma spec; `text-align: left`; padding preserved from manual adjustments; font tokens kept as fallback
- SCSS `thead`: `position: sticky; top: 0; z-index: 4; background-color: $boreal-ui-base-lighter` — always-on sticky (no prop, per col-table pattern); `base-lighter` background prevents scrolling body rows from showing through
- SCSS `__th-label`: `gap: $boreal-spacing-3xs` (corrected from `2xs` per Figma Content gap spec); `@include bds-icon($boreal-icons-s, $boreal-typography-font-size-xs)` constrains icon to 12×12px via the standard mixin
- SCSS `<td>`: `font-size: $boreal-typography-font-size-sm; font-weight: $boreal-typography-font-weight-regular; line-height: $boreal-typography-line-height-sm; color: $boreal-text-default` (matches Figma `body/sm`)
- SCSS row dividers: `tbody tr td { border-bottom: 1px solid $boreal-stroke-default-light; }` — visible separator between every data row; applies to all rows including the last (matches Figma design)
- SCSS header bottom border: `thead th { border-bottom: 1px solid $boreal-stroke-default-light; }` — separates the header row from the first data row
- SCSS `tr:hover td`: `background-color: $boreal-ui-default-lighter` — row hover highlight
- SCSS `thead`: `background-color: $boreal-ui-inverse` — header row stays white against scrolling body
- `inheritAttributes(this.el, ['aria-label', 'aria-describedby'])` from `@/utils/a11y/attributes` is called in `componentWillLoad`; result stored in `private inheritedAttributes: Attributes` and spread onto `<table {...this.inheritedAttributes}>` in `render()` — strips those ARIA attrs from the host and places them on the semantic `<table>` element

**Manual test _(waiveable)_:**

Playground scenarios in `packages/boreal-web-components/src/index.html`:

- Scenario 1: `<bds-table>` with three `<bds-table-column>` children and a `data` prop set via JS — three column headers and data rows render
- Scenario 2: Column with a `formatter` returning a `<bds-tag>` element — tag renders inside the cell
- Scenario 3: Column with a `formatter` returning a plain string — string renders as text
- Scenario (header): Column with `icon="bds-icon-emoji-circle"` and `info="The product category"` — icon appears left of label; ⓘ icon appears right of label with tooltip on hover

Validation (run `pnpm dev:components`):

- [ ] Given `data=[{id:1,name:'Alice'}]` and a `<bds-table-column col-key="name" label="Name">`, when the page loads, then one header "Name" and one data row "Alice" appear. Pass: correct text in DOM.
- [ ] Given a formatter returning `document.createElement('strong')` with text, when rendered, then a `<strong>` element is inside the `<td>`. Pass: element visible in DevTools.
- [ ] Given `data=[]`, when the page loads, then `<tbody>` is empty. Pass: no `<tr>` elements in `<tbody>`.
- [ ] Given `<bds-table aria-label="Users table">`, when rendered, then `<table aria-label="Users table">` appears in DevTools and the host element has no `aria-label` attribute. Pass: attribute on `<table>`, absent on host.
- [ ] Given a table with one column and `data` set, when a second `<bds-table-column>` is appended via JS, then the new column header and its cell data appear immediately. Pass: new column visible without page reload.
- [ ] Given `icon="bds-icon-emoji-circle"` on a column, when the page loads, then an `<i class="bds-icon-emoji-circle">` appears to the left of the label inside `__th-label`. Pass: icon visible in DevTools.
- [ ] Given `info="The product category"` on a column, when the page loads, then hovering the ⓘ icon shows the tooltip text. Pass: tooltip visible on hover.

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

- `@Prop() readonly emptyMessage: string = 'No data to display'` — overridable default text; added to `ITable` interface
- When `this.data.length === 0`, render a single `<tr>` inside `<tbody>` containing one `<td class="bds-table__empty-state" colSpan={colSpan}>` where `colSpan = this.columns.length + (this.selectable ? 1 : 0)`
- Empty state content priority: slot wins over prop — check `this.el.querySelector('[slot="empty-state"]') !== null` at render time; if truthy render `<slot name="empty-state" />`; otherwise render `<span class="bds-table__empty-text">{this.emptyMessage}</span>`
- Do NOT use `<bds-typography>` for the default text — it overrides component token styles; use a plain `<span>` styled with `$boreal-*` tokens directly
- Do NOT use Stencil slot fallback children (`<slot>...<FallbackContent/></slot>`) — this creates `<slot-fb>` DOM noise; use the imperative `querySelector` check instead (see `feedback_prop_or_slot_pattern.md` memory entry)
- When `this.data.length > 0` the empty state `<tr>` is not rendered
- `classMap` getter with `StyleModifiers` drives the wrapper div classes: `bds-table__wrapper` always present, `bds-table__wrapper--empty` when `data.length === 0`
- Use `const PREFIX = 'bds-table' as const` for all BEM class names in the file (see `feedback_prefix_constant.md` memory entry)
- SCSS uses BEM nesting (`&__empty-state`, `&__empty-text`) inside the `bds-table { }` block — no flat selectors (see `feedback_scss_bem_nesting.md` memory entry)
- SCSS: `&__empty-state { text-align: center; padding: $boreal-spacing-2xl; background-color: $boreal-ui-default-lighter; }` — `$boreal-spacing-2xl` confirmed to exist
- SCSS: `&__empty-text { font-size: $boreal-typography-font-size-xs; font-weight: $boreal-typography-font-weight-regular; line-height: $boreal-typography-line-height-sm; }`

**Manual test _(waiveable)_:**

Playground scenarios (all three added to `packages/boreal-web-components/src/index.html`):

- Scenario 1: `<bds-table>` with `data=[]` and no `slot="empty-state"` — default "No data to display" appears as a `<span>`
- Scenario 2: Same with `<p slot="empty-state">No results found. Try adjusting your filters.</p>` — custom content replaces default; no `empty-message=""` needed
- Scenario 3: `<bds-table>` with data — no empty state row visible

Validation:

- [ ] Given `data=[]`, when the page loads, then "No data to display" text is centred in the table. Pass: text visible as `<span class="bds-table__empty-text">`, no data rows present.
- [ ] Given `data=[]` and a filled `slot="empty-state"`, then custom slot content appears instead of the default. Pass: custom text visible, no `<span>` in DOM.
- [ ] Given `data=[{id:1}]`, then no empty state row is rendered. Pass: `<tbody>` contains one data `<tr>`.
- [ ] Given `emptyMessage="No hay resultados"`, then the custom string appears in the span. Pass: localised text visible.

**Commit:**

```
feat(web-components): EOA-10576 add empty state with emptyMessage prop and slot override
```

---

## Task 4b: Loading state — prop stub ⏳ pending design specs

**Executor:** @frontend-subagent

**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table.tsx` (modify)

**Context:** The UX/UI team is preparing the visual design for the loading state. This task locks in the prop API so consumers can bind `loading` without a future breaking rename. No rendering logic, skeleton markup, or SCSS is added here — those land once specs are delivered.

**Acceptance criteria:**

- Add to `ITable` interface:
  - `loading: boolean` — when `true` the table is in a loading state
  - `loadingRows: number` — number of skeleton rows to pre-allocate (default `5`)
- Add to `BdsTable`:
  - `@Prop() readonly loading: boolean = false`
  - `@Prop() readonly loadingRows: number = 5`
  - `@Watch('loading') onLoadingChange(): void {}` — stub; will trigger skeleton re-render in the full implementation
- No render branching, no SCSS, no playground scenarios — implementation deferred to follow-up task once design specs land
- No `any` types; JSDoc on both new props

**Manual test _(waiveable — no visual output)_:** `rtk pnpm tsc --noEmit` in `packages/boreal-web-components` passes with no new errors.

**Commit:**

```
feat(web-components): EOA-10576 add loading prop stub — visual implementation pending design specs
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
- Each `<th>` for a `sortable` column renders: the label text, a sort icon in the right group of `__th-content` using one of three icon classes depending on state — `bds-icon-chevron-up-down` (NONE), `bds-icon-chevron-up` (ASC), `bds-icon-chevron-down` (DESC) — and an `onClick` handler calling `handleSort(col.colKey)`
- `handleSort(colKey)` implements the three-state cycle and emits `bdsSort`
- `KeyboardController` from `@/utils/a11y` is attached in `componentDidLoad` to handle `KEYBOARD.Enter` and `KEYBOARD.Space` on sortable `<th>` elements — calls `handleSort` on trigger
- `<th>` for sortable columns gets `role="button"` and `tabIndex={0}` to be keyboard focusable
- SCSS: sort icon (`bds-icon-chevron-up-down`, `bds-icon-chevron-up`, `bds-icon-chevron-down`) styled with `$boreal-icon-default-light` when the column is not the active sort column, `$boreal-icon-default-ink` when it is; `cursor: pointer` on sortable headers; icon size `$boreal-icons-s` (12px) via `@include bds-icon($boreal-icons-s, $boreal-typography-font-size-xs)` on the right group span
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

**Keyboard behavior:**

- **Tab** — moves focus sequentially through all checkboxes (header → row 1 → row 2 …)
- **Space** — toggles the focused checkbox (native `<input type="checkbox">` behavior via `bds-checkbox`)
- **Enter** — not applicable; Enter is standard for `role="button"` only. Checkboxes (`role="checkbox"`) respond to Space exclusively per WAI-ARIA Checkbox Pattern.

**Future enhancement (not in scope):** Shift+Click / Shift+Space range selection — selects all rows between last-clicked and current. Common in data tables but deferred pending UX spec.

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

- Pinnable `<th>` cells render a pin icon (12×12px) in the right group of `__th-content`, alongside the sort icon — two states: `bds-icon-pin` when the column is not yet pinned (inactive), `bds-icon-pin-fill` when the column is pinned (active); clicking toggles the pinned state
- **Architecture note:** pinned state is stored in `@State() private pinnedColKeys: Set<string>` on `bds-table` (same pattern as `sortKey`/`sortDirection`) — do NOT reflect it back onto `bds-table-column`; table-level state keeps all interactive state co-located and avoids DOM mutation side-effects
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
- `@Prop() readonly subheadingIcon: string = ''` — CSS icon class (e.g. `bds-icon-user-manager`) rendered as `<i class={subheadingIcon} aria-hidden="true" />` to the left of the subheading typography element
- `@Prop() readonly selectionLabel: string = 'items'` — noun label appended to the selection count in the tag (e.g. `"users"` renders "3 users"); defaults to `"items"`
- `@Prop() readonly tooltipText: string = ''` — when non-empty, passed into `<bds-typography tooltipText={...}>` — the typography component renders the ⓘ icon and tooltip internally; do NOT add a separate `<bds-tooltip>` in the toolbar
- Private getter `hasToolbar` returns `true` when `this.subheading` is non-empty OR any of the toolbar slots (`search-bar`, `toolbar-actions`, `row-actions`) has assigned nodes
- When `hasToolbar` is false, the toolbar `<div>` is not rendered (conditional in JSX)
- `<Host>` receives class `bds-table--has-selection` when `selectedRowIds.size > 0`; SCSS rule `bds-table:not(.bds-table--has-selection) [slot="row-actions"] { display: none }` hides slotted row-action content in Stencil scoped (non-shadow) mode when no rows are selected
- Toolbar structure:
  ```
  <div class="bds-table__toolbar">
    <div class="bds-table__toolbar-left">
      [if subheading]
        <div class="bds-table__toolbar-left-heading">
          [if subheadingIcon] <i class={subheadingIcon} aria-hidden="true" />
          <bds-typography variant="subheading" tooltipText={tooltipText || undefined}>
            {subheading}
          </bds-typography>
        </div>
      [if selectedRowIds.size > 0]
        <div class="bds-table__toolbar-row-actions">
          <bds-tag onBdsClose={() => { clearSelection(); bdsSelect.emit({ selectedIds: [] }); }}>
            {selectedRowIds.size} {selectionLabel}
          </bds-tag>
          <bds-button-group variant="default" color="default" size="md" label="Bulk row actions">
            <bds-button variant="plain" aria-label="Delete selected rows" onBdsClick={handleDelete}>
              <i slot="icon" class="bds-icon-trash" aria-hidden="true" />
            </bds-button>
            <bds-button variant="plain" aria-label="Edit selected rows" onBdsClick={handleEdit}>
              <i slot="icon" class="bds-icon-edit" aria-hidden="true" />
            </bds-button>
          </bds-button-group>
          <bds-divider orientation="vertical" />
          <slot name="row-actions"></slot>
        </div>
    </div>
    ...right zone in Task 9...
  </div>
  ```
- `@Event() bdsDelete: EventEmitter<{ selectedIds: string[] }>` — emits `Array.from(this.selectedRowIds)` when delete button clicked; payload is IDs only (full row objects intentionally excluded — see "Getting rich row data" in Task 16 MDX and V2-7 design decision)
- `@Event() bdsEdit: EventEmitter<{ selectedIds: string[] }>` — same shape, emits on edit button click
- `bds-tag` close button (`onBdsClose`) calls `clearSelection()` AND emits `bdsSelect` with `{ selectedIds: [] }` — user-initiated clear must notify listeners the same way checkbox deselection does; `clearSelection()` `@Method` does NOT emit (programmatic resets are silent)
- Delete and edit buttons are wrapped in `<bds-button-group variant="default" color="default" size="md" label="Bulk row actions">`; icon is provided via `slot="icon"` named slot on `<bds-button>` (not an `icon` prop)
- `<bds-divider orientation="vertical" />` separates the built-in button group from `slot="row-actions"` content
- `slot="row-actions"` is always present in the DOM but hidden via the host class CSS rule when `selectedRowIds.size === 0`
- SCSS: `.bds-table__toolbar { display: flex; justify-content: space-between; align-items: center; height: $boreal-spacing-xl; gap: $boreal-spacing-s; }`

**Manual test _(waiveable)_:**

Playground scenarios:

- Scenario 1: `<bds-table subheading="Users">` — toolbar with subheading renders
- Scenario 2: Same with `subheading-icon="bds-icon-user-manager"` — icon appears to the left of the subheading
- Scenario 3: Same with `tooltip-text="More info"` — ⓘ icon appears inside the typography element (right of text) with tooltip on hover
- Scenario 4: `<bds-table>` with no `subheading` and no slots — no toolbar rendered
- Scenario 5: `selectable` table with `selection-label="users"` and a `<bds-button slot="row-actions">` — select rows; tag shows "N users", delete/edit group, divider, and custom button all appear; tag × clears selection and emits `bdsSelect { selectedIds: [] }`; all four events (`bdsSelect`, `bdsDelete`, `bdsEdit`, custom button `bdsClick`) visible in the in-page event log

Validation:

- [ ] Given `subheading="Users"`, when rendered, then "Users" appears in `<bds-typography variant="subheading">`. Pass: text visible.
- [ ] Given `subheading-icon="bds-icon-user-manager"`, then `<i class="bds-icon-user-manager">` appears to the left of the typography. Pass: icon visible in DevTools.
- [ ] Given `tooltip-text="Help"`, when the ⓘ icon is hovered, then "Help" tooltip appears. Pass: tooltip visible without a separate `<bds-tooltip>` in the toolbar DOM.
- [ ] Given no `subheading` and no toolbar slots, then no toolbar `<div>` exists in the DOM. Pass: `bds-table__toolbar` absent in DevTools.
- [ ] Given `selectable` table with `selection-label="users"` and 2 rows checked, then the tag shows "2 users" and delete/edit button group is visible. Pass: tag text and buttons present.
- [ ] When delete button is clicked, then `bdsDelete` fires with `{ selectedIds: ["1","2"] }`. Pass: event in log.
- [ ] When tag × is clicked, then selection clears AND `bdsSelect` fires with `{ selectedIds: [] }`. Pass: toolbar row-actions zone disappears + event in log.
- [ ] Given a `<bds-button slot="row-actions">` child, then it is hidden on load and visible only after row selection. Pass: button absent/present conditionally.

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

- Extract `private renderToolbarRight(): JSX.Element` method from the inline right-zone JSX in `renderToolbar()` — symmetry with `renderToolbarLeft()`, and provides a clean home for the search bar rendering that will be added once `bds-search-bar` ships
- Right zone rendered by `renderToolbarRight()` inside `.bds-table__toolbar`:
  ```
  <div class="bds-table__toolbar-right">
    <slot name="search-bar"></slot>
    <bds-button variant="plain" [filter icon] aria-label="Filter" onClick={handleFilter} />
    <bds-button variant="plain" [table-layout icon] aria-label="Column visibility" onClick={handleTableLayout} />
    <slot name="toolbar-actions"></slot>
  </div>
  ```
- `@Event() bdsFilter: EventEmitter<void>` — emits on filter button click; no payload; the consumer is responsible for opening a filter drawer/panel, collecting filter criteria, and setting `table.data` with the filtered result; `bds-table` has no internal filter state
- `@Event() bdsTableLayout: EventEmitter<void>` — emits on layout button click; no payload
- Both buttons use `variant="plain"` and icon-only mode of `bds-button`
- The filter button uses `bds-icon-filter` icon class; the layout button uses `bds-icon-table` icon class
- `hasToolbar` getter (from Task 8) must also check `slot="toolbar-actions"` and `slot="search-bar"` slots — if any of these slots has assigned nodes, the toolbar renders; this ensures the toolbar appears when only the right-side slots are used (no `subheading`)
- SCSS: `.bds-table__toolbar-right { display: flex; align-items: center; gap: $boreal-spacing-s; }` — `s` = 12px
- **`bds-table` does NOT handle `bdsSearch` internally.** The `slot="search-bar"` is a passive mount point. The consumer listens to `bdsSearch` from the slotted element and updates `bds-table`'s `data` prop externally. This is intentional: the table holds only the current page slice and cannot filter the full dataset on its own. The wiring pattern is identical to `bdsFilter` — event bubbles up, consumer acts on it.

**Design decision — `searchable` prop (deferred):**

A future `searchable: boolean` prop will render `<bds-search-bar mode="filter">` internally inside `renderToolbarRight()`, removing the need for consumers to slot in their own element for the common case. This is blocked on `bds-search-bar` shipping. When it lands:

- `slot="search-bar"` is preserved as the escape hatch for custom implementations
- The `searchable` prop is the convenience API for the default case
- No equivalent `paginated` prop will be added — `bds-pagination` has `totalItems`, `itemsPerPage`, and `currentPage` that would require full prop-forwarding on `bds-table`, making the slot the correct long-term API for pagination

**Manual test _(waiveable)_:**

Playground scenarios:

- Scenario 1: `<bds-table subheading="My Table">` — filter and layout buttons appear on the right
- Scenario 2: Click filter button — `bdsFilter` event fires
- Scenario 3: Click layout button — `bdsTableLayout` event fires
- Scenario 4: `<bds-table>` with `<button slot="toolbar-actions">Export</button>` and no `subheading` — toolbar renders with just the right zone
- Scenario 5: `<bds-table>` with no subheading and no slots — toolbar absent
- Scenario 6: `<bds-table>` with a plain `<input slot="search-bar">` wired externally to filter `data` — typing in the input updates the visible rows; clearing the input restores all rows. Demonstrates the consumer-owned wiring pattern that `bds-search-bar` will replace. Implementation:
  ```js
  const table = document.querySelector("bds-table");
  const allRows = table.data;
  document.querySelector("#search-input").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    table.data = q
      ? allRows.filter((r) =>
          Object.values(r).some((v) => String(v).toLowerCase().includes(q)),
        )
      : allRows;
  });
  ```

Validation:

- [ ] Given a table with `subheading`, when rendered, then filter and layout icon buttons appear on the right. Pass: buttons visible.
- [ ] When filter button is clicked, then `bdsFilter` fires with no payload. Pass: event in DevTools.
- [ ] When layout button is clicked, then `bdsTableLayout` fires. Pass: event in DevTools.
- [ ] Given only `slot="toolbar-actions"` filled (no `subheading`), then the toolbar renders. Pass: toolbar div present.
- [ ] Given no `subheading` and no filled slots, then toolbar `<div>` is absent. Pass: not in DOM.
- [ ] Given `slot="search-bar"` filled with a plain `<input>` and a JS filter handler, when typing "Alice", then only rows containing "Alice" render in `<tbody>`. Pass: row count reduces correctly.
- [ ] Given the same scenario, when the input is cleared, then all rows restore. Pass: full row count returns.

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

## Task 12: `bds-pagination` integration

**Executor:** @frontend-subagent

**Files:**

- `packages/boreal-web-components/src/index.html` (modify — add integration playground scenario)

**Context:** `bds-pagination` exists as a sibling component (branch `EOA-10580_pagination`, close to merge). The `slot="paginator"` added in Task 3 is the mount point. No new props on `bds-table` are needed — the integration is wiring at the consumer level. `bds-table` always receives only the current page's rows; it never sees the full dataset.

**Acceptance criteria:**

- A playground scenario in `src/index.html` demonstrates the full client-side wiring:
  1. A JS array of 50 rows (generated inline) is the source dataset
  2. `<bds-table>` receives the current page slice — `rows.slice((page - 1) * pageSize, page * pageSize)` — updated on each `bdsPageChange`
  3. `<bds-pagination total-items="50" items-per-page="10" current-page="1">` sits inside `<bds-table>` with `slot="paginator"`
  4. A `bdsPageChange` listener on `bds-pagination` reads `event.detail.currentPage` and `event.detail.itemsPerPage`, recomputes the slice, and assigns to `table.data`
  5. Changing items-per-page in the dropdown re-slices correctly and the table updates
- Verify that when `bds-table` is `selectable` and the user has checked rows on page 2, navigating to page 3 resets the selection — this exercises `@Watch('data')` from Task 6
- No loading state is needed for client-side — data is synchronous

**Manual test:**

Playground scenario (`pnpm dev:components`):

- [ ] Given 50 rows and `items-per-page="10"`, when the page loads, then rows 1–10 appear in the table and `bds-pagination` shows page 1 of 5. Pass: correct rows visible, correct pagination state.
- [ ] When clicking "Next page", then rows 11–20 appear. Pass: new page slice visible.
- [ ] When changing items-per-page to 25, then rows 1–25 appear and `bds-pagination` recalculates to page 1 of 2. Pass: slice and page count update correctly.
- [ ] Given `selectable` table on page 2 with two rows checked, when navigating to page 3, then all checkboxes are unchecked. Pass: selection cleared on data change.

**Commit:**

```
feat(web-components): EOA-10576 add bds-pagination client-side integration playground
```

---

## Task 13: Unit tests — `bds-table-column` (renumbered from 12)

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

## Task 14: Unit tests — `bds-table` basics, sort, selection, toolbar (renumbered from 13)

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
- `slot="search-bar"` filled, no `subheading` — toolbar renders (slot presence alone is sufficient)
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

## Task 15: Storybook story (renumbered from 14)

**Executor:** @documentation-subagent

**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (create)

**Acceptance criteria:**

- Story file follows the existing pattern from `apps/boreal-docs/src/stories/feedback/bds-tag/bds-tag.stories.ts`
- Category: `Data Visualization / Table`
- Stories to include:
  - `Default` — basic table with 3 columns and 5 data rows, no extras
  - `WithSorting` — two sortable columns; `bdsSort` action logged
  - `WithSelection` — `selectable` enabled; `bdsSelect` action logged
  - `WithToolbar` — `subheading`, `subheading-icon`, `tooltip-text` props; filter + layout button events logged
  - `WithPinnedColumn` — first column has `pinnable`; table wide enough to require scroll
  - `EmptyState` — `data=[]`; default empty state message visible
  - `WithCustomEmptyState` — `data=[]`; custom `slot="empty-state"` content
  - `WithFormatter` — one column uses a `formatter` returning a `bds-tag` element
  - `WithMaxHeight` — `max-height="300px"` with 20 rows; vertical scroll visible
  - `WithPagination` — 50-row dataset sliced client-side; `bds-pagination` in `slot="paginator"`; `bdsPageChange` handler updates `data` slice; shows page 1 of 5 on load
  - `WithSearch` — 20-row dataset; plain `<input slot="search-bar">` wired via `input` event to filter `data`; demonstrates the consumer-owned wiring pattern and serves as a visual placeholder until `bds-search-bar` is built
  - **Bulk row-actions group** (actions that operate on the selected row subset — appear only when `selectedRowIds.size > 0`):
    - `BulkDelete` — `selectable` table; selecting rows reveals the trash button; `bdsDelete` fires and the consumer filters those IDs out of `data`; no blocking confirmation in the story (pattern note in MDX)
    - `BulkDeleteWithUndo` — same as above but the consumer shows an inline "Deleted N rows · Undo" banner below the table; clicking Undo restores the rows; demonstrates the recoverable-delete pattern without a modal
    - `BulkEdit` — selecting rows triggers `bdsEdit`; consumer renders a compact inline form below the table with a single shared field (e.g. "Department"); Confirm button in the form updates all selected rows at once; Cancel closes the form
    - `BulkCustomAction` — `slot="row-actions"` holds a `<bds-button>Approve</bds-button>`; clicking it updates a `status` field on selected rows to `"approved"` and the cell renders a `bds-tag` via formatter; demonstrates non-destructive bulk state change
  - **Toolbar-actions group** (table-wide controls — always visible, no selection dependency):
    - `WithAddRow` — `<bds-button slot="toolbar-actions" icon="bds-icon-plus">New</bds-button>` opens an inline form row prepended to the table; saving appends the new object to `data`
    - `WithImportExport` — `<bds-button slot="toolbar-actions">Import CSV</bds-button>` triggers a file-input picker and parses rows into `data`; `<bds-button slot="toolbar-actions">Export All</bds-button>` downloads all rows as a `.csv` file
    - `WithRefresh` — `<bds-button slot="toolbar-actions" icon="bds-icon-refresh">` simulates a 1-second async fetch and replaces `data` when it resolves; demonstrates the server-side data-refresh wiring pattern
- JS property bindings for `data`, `formatter`, and `columns` are documented in an MDX "How to use it" note (not in the Source panel, which cannot show them)

**Commit:**

```
docs(docs): EOA-10576 add Storybook stories for bds-table
```

---

## Task 16: MDX documentation (renumbered from 15)

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
  - **Toolbar** — slot map table with scope column (`search-bar` / `toolbar-actions` = table-wide, always visible; `row-actions` = row subset, conditional on selection); when toolbar auto-hides; built-in events (`bdsFilter`, `bdsTableLayout`, `bdsDelete`, `bdsEdit`); note that `bds-table` does NOT handle `bdsSearch` internally — the slot is a passive mount point and the consumer owns the filter logic
  - **Bulk row actions** — documents the three consumer patterns using `bdsDelete` / `bdsEdit` / `slot="row-actions"`: (1) delete with no confirmation + undo banner, (2) bulk field edit with inline form + Confirm/Cancel, (3) non-destructive state change (Approve); clarifies that confirmation dialogs belong in the consumer, not the table; `@Watch('data')` auto-clears selection when `data` is replaced so no manual reset is needed after a confirmed delete; includes a "Getting rich row data" subsection explaining that `bdsDelete`/`bdsEdit` intentionally emit `{ selectedIds }` only (IDs are the correct currency for server-side operations and remain accurate when v2 server-side mode ships), and that consumers needing full row objects for UI purposes (e.g. a confirmation dialog listing names) should call `await table.getSelectedRows()` inside their event handler — includes a code example showing this pattern
  - **Toolbar actions** — documents the three patterns using `slot="toolbar-actions"`: (1) Add new row (inline form), (2) Import/Export All, (3) Refresh from server; distinguishes `toolbar-actions` (table-wide, no selection needed) from `row-actions` (selection-scoped)
  - **Search bar integration** — explains the consumer-owned wiring pattern: consumer listens to `bdsSearch` (or `input`) from the slotted element, filters or re-slices the source data, and sets `table.data`; `bdsClear` restores the full dataset; full wiring code example; note that `bds-table` holds only the current page slice so internal filtering is intentionally absent; `bds-search-bar` (future component, `mode="filter"`) will replace the plain `<input>` placeholder without changing the wiring contract
  - **Empty state** — `slot="empty-state"` and default behaviour
  - **Paginator integration** — `slot="paginator"` wired to `bds-pagination`; full client-side code example showing: `bds-pagination` placed inside `bds-table` with `slot="paginator"`, `bdsPageChange` listener that slices the source array and assigns to `table.data`, `totalItems` set to the full dataset length; note that `bds-table` only ever holds the current page's rows — the parent owns the slice logic
  - **Accessibility** — native `<table>` semantics; `th[scope="col"]`; keyboard sort interaction
  - **What's coming in v2** — column grouping, drag/drop reorder, virtualization, column visibility dropdown

**Commit:**

```
docs(docs): EOA-10576 add MDX documentation for bds-table
```
