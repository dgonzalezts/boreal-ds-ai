# EOA-10576 — bds-table

**Ticket:** EOA-10576
**Goal:** Implement a `bds-table` component family (organism + column definition atom) that renders a native HTML data table with toolbar, sort, row selection, column pinning, and empty state for the Boreal DS data-visualization category.

---

## Scope

**In:**
- `bds-table-column` — configuration-only atom; carries column definition props; renders nothing visible
- `bds-table` — organism; reads `bds-table-column` children; renders native `<table>/<thead>/<tbody>/<tr>/<th>/<td>`; manages sort, row selection, and optional toolbar
- Toolbar (optional, auto-hides): subheading, info tooltip, selected-count `bds-tag`, delete/edit `bds-button` (auto-show on selection), `slot="row-actions"`, `slot="search-bar"`, filter button, column-layout button, `slot="toolbar-actions"`
- Column sorting — single-column, three-state cycle (`none → asc → desc → none`), client-side only
- Row selection — internal `Set<string>` state, checkbox column, select-all, `getSelectedRows()` method, `clearSelection()` method
- Column pinning — `position: sticky` + inline `style.left` computed in `componentDidRender`
- Empty state — `slot="empty-state"` + default centred message
- Custom cell content — `formatter?: ({ value, row }) => string | HTMLElement` on `bds-table-column`
- `slot="paginator"` — wired for future `bds-paginator` integration
- Responsive toolbar — CSS container queries, collapses at ≤744px container width
- Storybook story + MDX documentation
- Unit tests for both components

**Out:**
- `bds-paginator` and `bds-search-bar` components (built by other teammates; integration via slots only)
- Column grouping (`bds-table-column-group`) — v2
- Column drag/drop reorder — v2
- Column resizing — v2
- Row expand/collapse — v2
- Virtualization (`@tanstack/virtual-core`) — v2
- Column visibility dropdown implementation (button renders and emits `bdsTableLayout`; dropdown logic is v2 — blocked on `bds-dropdown` which does not exist yet)
- Server-side sort/filter mode — v2
- `@tanstack/table-core` — not adopted (see research spike `ai-work/research/2026-06-16-bds-table-column-api-spike.md`)

---

## Acceptance Criteria

- [ ] `<bds-table-column key="x" label="X" sortable pinnable info="Tooltip text">` renders nothing on its own but provides readable props to `bds-table`
- [ ] `<bds-table .data=${rows} row-key="id">` renders a native `<table>` with one `<th>` per column and one `<tr>` per row
- [ ] Clicking a sortable column header cycles sort direction; `bdsSort` event fires with `{ key, direction }`
- [ ] `selectable` prop adds a checkbox `<th>`/`<td>` column; checking a row adds its ID to internal state; `bdsSelect` fires
- [ ] Header checkbox selects/deselects all rows
- [ ] `getSelectedRows()` method returns the full row objects for currently selected IDs
- [ ] `clearSelection()` method empties the selection
- [ ] Pinned columns remain fixed during horizontal scroll; sticky offsets are computed per column
- [ ] Empty `data=[]` shows `slot="empty-state"` content; a default message appears when the slot is not filled
- [ ] Toolbar renders only when `subheading` is set or any toolbar slot has assigned nodes
- [ ] Delete and edit buttons auto-appear in toolbar when `selectedRowIds.size > 0`; `bdsDelete`/`bdsEdit` events fire on click
- [ ] Filter and layout buttons emit `bdsFilter` and `bdsTableLayout` respectively
- [ ] At container width ≤744px the toolbar heading and secondary actions collapse via container query
- [ ] `formatter` function on a column is called per cell; returned `string` or `HTMLElement` is rendered in the `<td>`
- [ ] `slot="paginator"` renders below the table content

**Unit tests:**
- [ ] `bds-table-column` — prop reflection, `display: none` render, `formatter` assignable
- [ ] `bds-table` basics — column headers from children, data rows, cell values, `slot="empty-state"`, `slot="paginator"` present
- [ ] `bds-table` sort — `bdsSort` event shape, three-state cycle, multi-column reset, `sortedData` correctness
- [ ] `bds-table` selection — checkbox column presence, `bdsSelect` event, `getSelectedRows()`, `clearSelection()`, select-all, data-change reset
- [ ] `bds-table` toolbar — auto-hide logic, delete/edit button visibility, `bdsDelete`, `bdsEdit`, `bdsFilter`, `bdsTableLayout` events
- [ ] All spec files pass `pnpm test` in `packages/boreal-web-components` with ≥90% line coverage

**Documentation:**
- [ ] Storybook: 9 stories covering Default, WithSorting, WithSelection, WithToolbar, WithPinnedColumn, EmptyState, WithCustomEmptyState, WithFormatter, WithMaxHeight — all render without console errors
- [ ] MDX: Component anatomy, `bds-table-column` prop table, custom cell content example, row selection guide, column sorting guide, toolbar slot map, accessibility notes, v2 roadmap section
- [ ] JS property bindings (`data`, `formatter`) documented in MDX "How to use it" (not in Storybook Source panel)

---

## Dependencies

- `bds-tooltip` (already exists) — column header truncation tooltip
- `bds-typography` (already exists) — toolbar subheading `variant="subheading"`
- `bds-tag` (already exists) — selected row count in toolbar
- `bds-button` (already exists) — toolbar action buttons
- `bds-checkbox` (already exists) — row selection checkboxes
- `bds-paginator` — built by other teammates; no blocking dependency for v1 (slot only)
- `bds-search-bar` — built by other teammates; no blocking dependency for v1 (slot only)
- `bds-dropdown` — **does not exist yet**; blocking dependency for V2-4 (column visibility toggle); must be scoped as a separate ticket before v2 table sprint begins

---

## Open Questions

- None. All architecture decisions finalised in research spike `ai-work/research/2026-06-16-bds-table-column-api-spike.md`.
