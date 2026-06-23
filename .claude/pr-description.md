# Introduce `bds-table` data visualization component

## Type of Change
- [X] New feature (non-breaking change which adds functionality)

## Description of the Feature

Adds `bds-table` and `bds-table-column` to the Boreal DS data-visualization component category. The table renders structured row and column data using native HTML `<table>` / `<thead>` / `<tbody>` elements, preserving full semantic accessibility while supporting an opt-in feature set: column sorting, row selection with bulk actions, column pinning, an auto-hiding toolbar, custom cell formatters, empty state handling, column header / cell truncation, vertical scrolling via `maxHeight`, and a `slot="paginator"` mount point for `bds-pagination`.

`bds-table-column` is a configuration-only atom (`display: none`) that carries column metadata as reflected props. `bds-table` reads its children via `querySelectorAll` and re-reads via a `MutationObserver` when columns are added or removed dynamically.

## Implementation Details

**Component architecture**

- Light DOM composition — `<bds-table-column>` elements are placed as direct children of `<bds-table>`; no Shadow DOM, no slot diffing.
- All interactive state (`sortKey`, `sortDirection`, `selectedRowIds`, `pinnedColKeys`) is managed with Stencil `@State`; no third-party table library.
- `data: RowData[]` prop carries the current page slice. `bds-table` never filters or paginates internally — consumers own that logic and replace `data` on each change.
- `inheritAttributes(el, ['aria-label', 'aria-describedby'])` strips ARIA attributes from the host and forwards them onto the native `<table>` element, preserving screen-reader semantics without attribute duplication.

**Sorting**

Three-state cycle per column (`ASC → DESC → NONE`). Switching to a different column resets the previous one. A `compareValues` utility in `bds-table-utils.ts` handles strings (locale-aware), numbers, and Dates. `KeyboardController` adds Enter/Space activation on sortable headers.

**Row selection**

`selectedRowIds: Set<string>` tracks selections by the `rowKey` field. A `@Watch('data')` watcher clears the set whenever `data` is replaced, avoiding stale selections after page changes. `getSelectedRows()` and `clearSelection()` are exposed as `@Method()` APIs. The bulk-action toolbar zone (delete, edit, custom `slot="row-actions"`) appears only when `selectedRowIds.size > 0`, controlled via a host class and CSS rule.

**Column pinning**

`pinnedColKeys: Set<string>` lives on `bds-table`, not on `bds-table-column`, keeping all interactive state co-located. `componentDidRender` queries `th[data-pinned]` in DOM order, computes cumulative `offsetWidth`, and stamps `style.left` on each pinned `<th>` and its body `<td>` cells. `border-collapse: separate` is required for `position: sticky` to work and is set from Task 3.

**Toolbar**

Auto-hides when `subheading` is empty and no toolbar slots (`search-bar`, `toolbar-actions`, `row-actions`) have assigned nodes. The right zone holds a `slot="search-bar"` passive mount point (consumer-owned filter wiring), plus filter (`bdsFilter`) and column-visibility (`bdsTableLayout`) buttons. Both events emit with no payload; the consumer is responsible for opening the relevant panel and updating `data`.

**Truncation and scroll**

`table-layout: fixed` activates `text-overflow: ellipsis` on both `<th>` labels and `<td>` cells. `maxHeight` stamps `--bds-table-max-height` as a CSS custom property on `<Host>`; `.bds-table__wrapper` reads it via `max-height: var(--bds-table-max-height)`. The sticky `<thead>` (always on, `z-index: 4`) remains fixed during vertical scroll.

**Pagination integration**

No new props on `bds-table`. `slot="paginator"` is the mount point. The `bdsPageChange` handler on `bds-pagination` slices the source array and assigns to `table.data`; `@Watch('data')` clears any stale selection automatically.

**Loading state stub**

`loading: boolean` and `loadingRows: number` props are declared with a `@Watch` stub. Visual implementation (skeleton rows) is deferred pending UX/UI design specs.

## Impact of the Feature

- Two new components registered in the Stencil component registry (`bds-table`, `bds-table-column`).
- No changes to existing components or shared utilities; `KeyboardController`, `inheritAttributes`, `StyleModifiers`, and `createId` are reused without modification.
- `border-collapse: separate` on `<table>` is a deliberate deviation from the more common `collapse`; it is required for `position: sticky` on pinned columns and is scoped entirely within `bds-table.scss`.
- The `slot="search-bar"` is intentionally passive — `bds-table` does not listen to `bdsSearch` internally. This is a documented design decision (V2-3 in the research file) pending `bds-search-bar` shipping.
- `bds-table-column` elements have `display: none`; they produce no layout impact when placed in the DOM.

## Testing Conducted

All playground scenarios in `packages/boreal-web-components/src/index.html` cover tasks 3–11:

- **Basic rendering** — three columns, three rows, formatter returning `HTMLElement`, formatter returning string, `aria-label` transfer to `<table>`, dynamic column addition via `MutationObserver`.
- **Empty state** — default `emptyMessage`, custom `slot="empty-state"`, non-empty data (no empty row).
- **Sorting** — single-column sort cycle (ASC → DESC → NONE), switching active sort column, keyboard activation.
- **Row selection** — checkbox column, select-all (including indeterminate state), data-change clears selection.
- **Column pinning** — 8-column wide table with horizontal scroll; pinned columns + selectable checkbox.
- **Toolbar** — subheading only; subheading + icon + tooltip; selectable + bulk actions with in-page event log; no subheading + no slots (toolbar absent); filter/layout event log; `slot="toolbar-actions"` alone triggers toolbar; `slot="search-bar"` with external JS filter.
- **Truncation** — long column header in a 400px table, cell truncation, `maxHeight="200px"` with 20 rows (sticky header verified).
- **Pagination** — 100-row client-side slice, page navigation, items-per-page change, selectable + selection reset on page change.

Unit tests (tasks 12–13) cover `bds-table-column` prop reflection and `bds-table` rendering, sort cycle, selection state machine, and toolbar visibility / event emission.

## Screenshots/Videos (if applicable)

N/A — the playground at `packages/boreal-web-components/src/index.html` covers all scenarios and can be run with `pnpm dev:components` from the monorepo root.

## Additional Remarks

- **Overflow tooltip deferred (V2-3):** showing the full text in a `bds-tooltip` when a header or cell is truncated requires imperative `show()`/`hide()`/`anchorTo()` APIs on `bds-tooltip` that do not exist yet.
- **Responsive toolbar deferred (V2-8):** behavior below the 800px minimum supported width has not been UX/UI specced.
- **`searchable` convenience prop deferred:** blocked on `bds-search-bar` shipping; `slot="search-bar"` is the escape hatch in the interim.
- **Loading skeleton deferred:** `loading` / `loadingRows` props are API-complete but render nothing pending design specs.
- The playground file (`src/index.html`) is intentionally not committed — it is dev-only scratch content.
