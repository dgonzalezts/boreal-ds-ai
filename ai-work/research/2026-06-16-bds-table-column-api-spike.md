# Research Spike: bds-table Column API & Virtualization

**Date:** 2026-06-16
**Status:** Draft

---

## Goal

Determine the best column API approach (light DOM composition vs. JSON props) and virtualization strategy for `bds-table`, considering alignment with existing Boreal DS component patterns, implementation complexity for column grouping, and available virtualization libraries.

---

## Options Evaluated

- **Column API A** — Light DOM composition (`<bds-table-column>` elements in markup)
- **Column API B** — JSON props (`columns: ColumnDef[]` + `@tanstack/table-core`)
- **Virtualization** — `@tanstack/virtual-core`, `content-visibility: auto`, `virtua`, `@lit-labs/virtualizer`

---

## Findings

### 1. Alignment with existing Boreal DS patterns

Every composite component in the repo reads children via **`querySelectorAll` on `this.el`** after mount. No component uses a JSON prop to define its children.

| Component          | Pattern                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| `bds-breadcrumb`   | `querySelectorAll('bds-breadcrumb-item')` + `onSlotchange`                                 |
| `bds-radio-group`  | `querySelectorAll('bds-radio, bds-radio-button, bds-radio-card')` + `@Listen('bdsChange')` |
| `bds-button-group` | `querySelectorAll('bds-button')` + `@Watch`                                                |
| `bds-select`       | `querySelectorAll('bds-list-menu-item')` in `componentDidLoad`                             |
| `bds-list-menu`    | `querySelectorAll('bds-list-menu-item')` + `@Listen('bdsSelectItem')`                      |

No component uses `MutationObserver`. Slot changes are handled via `onSlotchange` or child event bubbling. **Option A (light DOM) is the dominant pattern. Option B (JSON) is a sharp departure from every composite component in the codebase.**

---

### 2. Column grouping — implementation depth

**Option A (light DOM) — Medium complexity**

Requires a `bds-table-column-group` wrapper element. `bds-table` must:

1. Walk `this.el.children` to distinguish groups from leaf columns.
2. Compute `colspan` (number of leaf children per group) and `rowspan` manually (`2` for leaf-only columns, `1` for group headers).
3. Handle two-level slot change detection: top-level `slotchange` is blind to mutations inside a group. Requires either a custom event dispatched from `bds-table-column-group` up to `bds-table`, **or** a `MutationObserver` with `subtree: true` (the only justified use in Boreal DS).

```html
<!-- Proposed light DOM grouping API -->
<bds-table>
  <bds-table-column-group label="Personal Info">
    <bds-table-column key="name" label="Name" sortable></bds-table-column>
    <bds-table-column key="age" label="Age"></bds-table-column>
  </bds-table-column-group>
  <bds-table-column key="email" label="Email"></bds-table-column>
</bds-table>
```

**Option B (JSON props + TanStack) — Low complexity for grouping**

`@tanstack/table-core` v8 supports grouped columns natively via nested `ColumnDef`:

```typescript
const columns: ColumnDef<RowData>[] = [
  {
    id: "personalInfo",
    header: "Personal Info",
    columns: [
      { accessorKey: "name", header: "Name" },
      { accessorKey: "age", header: "Age" },
    ],
  },
  { accessorKey: "email", header: "Email" },
];
```

`table.getHeaderGroups()` returns one `HeaderGroup` per depth level. Each `Header` carries `.colSpan` and `.rowSpan` auto-computed. No manual math needed.

**Hidden cost of Option B:** All of Aqua DS's table rendering is imperative DOM manipulation (`document.createElement`, `appendChild`) — not Stencil JSX. This introduces a two-class rendering architecture within the Boreal DS repo and departs from every other component's render pattern.

|                      | Option A       | Option B                    |
| -------------------- | -------------- | --------------------------- |
| Grouping complexity  | Medium         | Low                         |
| Colspan/rowspan calc | Manual         | Automatic (TanStack)        |
| Codebase alignment   | High           | Low                         |
| Custom cell content  | Natural (slot) | Requires formatter callback |
| Rendering model      | Stencil JSX    | Imperative DOM              |

---

### 3. Virtualization options

| Library                    | ~bundle (min+gz) | Variable-height rows   | Known height required | Stencil compatible  | Notes                                                              |
| -------------------------- | ---------------- | ---------------------- | --------------------- | ------------------- | ------------------------------------------------------------------ |
| `@tanstack/virtual-core`   | ~4 kB            | Yes (`measureElement`) | No                    | Full                | Proven in Aqua DS; framework-agnostic; independent of `table-core` |
| `content-visibility: auto` | 0 kB             | Yes (browser)          | No                    | Full                | Paint optimization only — does NOT reduce DOM node count           |
| `virtua`                   | ~3–5 kB          | Yes                    | No                    | Partial (bare core) | No Stencil/Aqua precedent; pre-1.0 API stability                   |
| `@lit-labs/virtualizer`    | ~15–20 kB        | Yes                    | No                    | Lit-coupled         | Public API is a `LitElement`; internal core is undocumented        |

**Aqua DS Stencil integration pattern for `@tanstack/virtual-core`:**

- `@State() virtualizer: Virtualizer<Element, Element>` — state change triggers Stencil re-render
- `observeElementOffset` + `observeElementRect` callbacks wired to the scroll container
- `virtualizer.getVirtualItems()` drives the render window; `virtualizer.getTotalSize()` sets the container height

The virtualizer is **fully independent of `@tanstack/table-core`** — it only requires a scroll container, item count, and size estimate.

---

## Recommendation

### Column API: Option A (light DOM) for v1

Every composite Boreal DS component follows the `querySelectorAll` + slot pattern. Authors already know it. HTML-attribute booleans (`sortable`, `pinnable`) follow the project's `@Prop` naming conventions. Custom cell content via a named slot on `bds-table-column` is the natural extension of the existing pattern.

### Do not adopt `@tanstack/table-core` for v1

The auto-`colspan`/`rowspan` value is real but only materialises for column grouping, which is a v2 feature. The cost — imperative DOM rendering that diverges from the JSX model used by every other Boreal DS component — outweighs the benefit at v1 scope.

**Exception:** If column grouping is confirmed as a v1 requirement, reconsider. In that case Option B + TanStack becomes significantly more attractive because the colspan/rowspan calculation alone justifies the dependency.

### Virtualization: skip v1, adopt `@tanstack/virtual-core` for v2

V1 should rely on server-side pagination to bound row count. When virtualization is needed, `@tanstack/virtual-core` is the only justified choice:

- Framework-agnostic, works with Stencil's `forceUpdate()` pattern
- Aqua DS has a proven Stencil integration (same design system family)
- Handles variable-height rows via `measureElement`
- Independent of the column API decision — can be adopted in v2 without changing the column architecture

---

## Extended Findings

### A. What "hand-rolled state" means

"Hand-rolled state" means `bds-table` owns and manages all interactive state itself using Stencil `@State()` decorators, without delegating logic to an external library. For v1 scope (sort + row selection + empty state), the following `@State` properties are needed:

```typescript
@State() sortKey: string = '';
@State() sortDirection: 'asc' | 'desc' | 'none' = 'none';
@State() selectedRowIds: Set<string> = new Set();
@State() isEmpty: boolean = false;
```

**What the component owns:** sort direction toggling, row ID tracking, empty-state detection, and re-rendering when any of these change. The component must also implement the comparison function for sort, the toggle logic for selection, and the derived "is empty" check.

**What `@tanstack/table-core` would own instead:** sort state machine (multi-column, controlled/uncontrolled), row selection model (single/multi/range), derived row models, and column visibility. TanStack holds a `state` object and exposes getter methods (`getHeaderGroups()`, `getRowModel()`); the component only calls these methods in `render()`. The component itself owns none of the business logic — it is purely a rendering adapter.

For v1 the distinction matters: hand-rolled state is ~80–120 lines. The TanStack adapter is ~250–400 lines but covers more features automatically.

---

### B. Option A + TanStack table-core: complexity assessment

#### 1. The adapter layer: DOM → ColumnDef[]

`bds-table` must read `<bds-table-column>` elements and convert their attributes into `ColumnDef[]` objects that TanStack consumes. The conversion runs in `componentDidLoad` and whenever columns change:

```typescript
private buildColumnDefs(): ColumnDef<RowData, unknown>[] {
  const cols = Array.from(
    this.el.querySelectorAll<HTMLBdsTableColumnElement>('bds-table-column'),
  );

  return cols.map(col => ({
    accessorKey: col.getAttribute('key') ?? col.key,
    header: col.getAttribute('label') ?? col.label ?? '',
    meta: {
      sortable: col.hasAttribute('sortable'),
      pinnable: col.hasAttribute('pinnable'),
    },
  }));
}
```

This is straightforward. The complication is that `<bds-table-column>` is a custom element whose properties may not be reflected as attributes (Stencil props are not reflected by default). Reading `.key` and `.label` as JS properties works after `componentDidLoad`, but only if `bds-table-column` has already upgraded. This requires `await customElements.whenDefined('bds-table-column')` before calling `buildColumnDefs()` — a race condition that light DOM composition avoids entirely.

#### 2. Responding to dynamic column changes

`slotchange` does not fire for attribute mutations on existing slotted elements; it fires only when slotted nodes are added or removed. Two options:

- **`slotchange` on a default slot** — covers add/remove of `<bds-table-column>` nodes. Sufficient if implementors only ever add or remove columns, not change attributes at runtime. This is the pattern all existing Boreal DS components use.
- **`MutationObserver` with `subtree: true, attributes: true`** — covers runtime attribute changes (e.g., toggling `sortable` dynamically). No existing Boreal DS component uses this; the spike's finding (section 1) notes it is the only justified use case for column grouping.

For most real-world usage, `slotchange` is sufficient. Dynamic attribute mutation of column definitions at runtime is not a common pattern.

#### 3. Bridge: TanStack state → Stencil re-render

TanStack table-core has no reactive system of its own. When state changes (sort click, row selection), the component must manually call Stencil's `forceUpdate()`:

```typescript
private table: Table<RowData>;

componentDidLoad() {
  this.table = createTable({
    columns: this.buildColumnDefs(),
    data: this.data,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onStateChange: () => {
      this.table.setOptions(prev => ({ ...prev, state: this.table.getState() }));
      forceUpdate(this);
    },
    state: {},
    renderFallbackValue: '',
  });
}
```

`forceUpdate(this)` is imported from `@stencil/core` and triggers a synchronous re-render. Aqua DS uses `@State() instance: Table<RowData>` — assigning to a `@State()` property is equivalent because Stencil detects the assignment and schedules a re-render. The Aqua DS pattern is slightly cleaner because it avoids the explicit `forceUpdate` import.

#### 4. Effort rating and line count

**Rating: Medium–High.**

The adapter itself (DOM → ColumnDef conversion + MutationObserver/slotchange wiring + onStateChange bridge) is approximately **150–200 lines**. This does not count: the render method (which becomes a thin TanStack-driven loop), the TanStack sort/selection wiring, or event emission. The full integration ballpark is 350–500 lines in `aq-table-core.tsx` from Aqua DS — and that is with imperative DOM rendering. A JSX-based Stencil component would be comparable.

The hidden cost remains what was identified in the original spike: all column and cell rendering in Aqua DS is **imperative DOM manipulation** (`document.createElement`, `appendChild`). This is a deliberate Aqua DS architectural choice driven by TanStack's functional cell renderers returning `HTMLElement | string`. In Stencil JSX, the adapter must either: (a) accept that cell renderers return `HTMLElement` and `appendChild` them into JSX-rendered containers, or (b) abandon the formatter callback pattern and use only primitive values in JSX.

#### 5. Industry precedent

No major web component library (Vaadin Grid, Carbon Web Components, Spectrum Web Components, FAST Data Grid) uses a headless table library internally while exposing a light DOM column API externally. Each library that exposes light DOM columns (`<vaadin-grid-column>`, `<igc-column>`) implements its own state management. Libraries that adopt TanStack (Tanstack Table for Angular, React Table) are framework-component libraries that expose a JS config API — not light DOM custom elements. The combination (light DOM API + TanStack internals) has no established precedent and is effectively a novel architecture requiring a custom adapter.

---

### C. Custom cell content approaches

#### Approach C1 — Named slot per column (light DOM)

**How cell slot content gets row data**

A `<template slot="cell">` by itself has no access to row data — HTML templates are inert. The practical patterns are:

1. **`bds-table-cell` wrapper prop injection**: `bds-table` renders a `<bds-table-cell>` component per cell, passing `row-data` as a JSON attribute or reflected prop. The implementor's slot content is rendered inside `<bds-table-cell>`, which exposes the row data via a scoped context attribute on its host element. The implementor's markup can then read it via `closest('bds-table-cell').rowData`. This is fragile and requires JavaScript.

2. **Template cloning with dataset injection**: The most viable pattern for native `<table>` + Stencil scoped CSS. `bds-table` reads the `<template>` inside `<bds-table-column>`, clones it per row, and stamps row data onto the clone's root element as `data-*` attributes:

```typescript
private renderCellContent(col: HTMLBdsTableColumnElement, rowData: RowData): Node {
  const tpl = col.querySelector<HTMLTemplateElement>('template[slot="cell"]');
  if (!tpl) return document.createTextNode(String(rowData[col.key] ?? ''));

  const clone = tpl.content.cloneNode(true) as DocumentFragment;
  const root = clone.firstElementChild as HTMLElement | null;
  if (root) {
    Object.entries(rowData).forEach(([k, v]) => {
      root.dataset[k] = String(v);
    });
  }
  return clone;
}
```

The implementor accesses row data via `this.dataset.fieldName` in an event handler — a workable but non-declarative DX.

3. **Render callback** (see C2 below) — cleaner DX but not declarative HTML.

**Can a `<template>` slot be cloned per row in Stencil?**

Yes, but only via imperative DOM manipulation inside `componentDidRender` or a dedicated helper, because JSX cannot reference a cloned `DocumentFragment` directly. The component must maintain a reference to each `<td>` element via `ref` callbacks, then imperatively `appendChild(clone)` after render. This mixes JSX and imperative DOM in the same component — the same anti-pattern that makes the TanStack adapter undesirable.

**Accessibility**

When using native `<table>/<tr>/<td>` elements, `role="cell"` is implicit on `<td>`. Custom content inside the `<td>` does not need additional roles unless it itself is interactive (buttons, links). The key requirement is that `<th>` elements carry `scope="col"` or `scope="row"` so screen readers can associate header text with data cells.

**Industry patterns**

- **Vaadin Grid**: uses `<vaadin-grid-column>` with a `renderer` property (a function) for custom cell content. Their light DOM API does not use `<template slot="cell">` — it uses the renderer callback pattern.
- **Carbon Web Components** (`<cds-table>`): uses a `<cds-table-cell>` child element with a default slot for custom content. The implementor writes a `<cds-table-cell>` per row in the markup — the table does not render rows from data, the implementor does. This is a fundamentally different model (declarative row markup, not data-driven rendering).

Neither Vaadin nor Carbon supports the `<template slot="cell">` pattern for data-driven tables. Both converge on either (a) an explicit render/formatter callback or (b) fully declarative row markup.

#### Approach C2 — Formatter function callback

**Aqua DS implementation**

Aqua DS defines the formatter on the column's `meta` property (from TanStack's `ColumnDef`):

```typescript
export interface AqColumnProp {
  formatter?: (value: {
    value: unknown;
    data: RowData;
  }) => string | HTMLElement;
}
```

Usage in Aqua DS:

```typescript
columns = [
  {
    accessorKey: "status",
    header: "Status",
    meta: {
      formatter: ({ value, data }) => {
        const tag = document.createElement("aq-tag");
        tag.setAttribute("label", String(value));
        return tag;
      },
    },
  },
];
```

Cell rendering in `aq-table-core.tsx` (line ~13986):

```typescript
if (columnDef.meta?.formatter) {
  const original = cell.getContext().row.original;
  content = columnDef.meta.formatter({
    value: cell.getValue(),
    data: original,
  });
}
if (content instanceof HTMLElement) {
  td.appendChild(content);
}
```

**Downsides of C2**

- **No declarative HTML**: the formatter is a JS function, not markup. It cannot be expressed in an HTML template, Angular template, or Vue SFC `<template>` block without a wrapper.
- **Framework wrapper friction**: React and Vue wrappers for Boreal DS (`@telesign/boreal-react`, `@telesign/boreal-vue`) expose `@Prop` bindings. A formatter function prop is bindable in React (`columns={myColumns}`) but requires careful serialization considerations in Vue. The function reference must be stable across renders or the table will re-render unnecessarily.
- **No SSR**: `document.createElement` inside a formatter cannot run in a Node/SSR context without a DOM polyfill.
- **DX cost vs C1**: The formatter pattern requires implementors to write imperative DOM creation code. For a simple text transformation this is fine; for a composite component (tag + tooltip + icon) it becomes verbose compared to writing declarative HTML.

#### Recommendation

**Use C2 (formatter callback) for v1; defer C1 to v2.**

Rationale:

- The `<template slot="cell">` cloning approach requires imperative DOM manipulation mixed into a JSX render — the same anti-pattern that makes TanStack integration undesirable.
- C2 is simpler to implement (no template cloning, no `ref` wiring), consistent with how Aqua DS works, and covers all real use cases.
- C1 can be added in v2 as an enhancement without changing the column API, since `<bds-table-column>` already uses the light DOM pattern.
- Both can coexist: if the column has a formatter, use it; if it has a `<template slot="cell">`, clone it. V1 implements only C2.

The formatter signature for `bds-table` should accept both a primitive return value and an `HTMLElement`, matching Aqua DS:

```typescript
formatter?: (params: { value: unknown; row: RowData }) => string | HTMLElement;
```

---

### D. Row selection model

#### Which model do existing Boreal DS components use?

`bds-checkbox` uses **mutable reflected props** with events: `@Prop({ mutable: true, reflect: true }) checked: boolean`. The component owns its checked state internally (mutates the prop) and emits `bdsChange` when the user interacts. Implementors can set `checked` externally to control it. This is a hybrid of D1 and D2 — the component owns state but the prop is also settable externally.

There is no example of a `Set<string>` selection model (D1 pure internal) in the codebase. There is also no example of a fully external controlled prop for multi-item selection.

#### Which model fits `bds-table`?

**Model D1 (internal `@State` tracking) is recommended for v1.**

Rationale:

- Tables embedded in data management pages are the primary use case. In these contexts, the page component calls `table.getSelectedRows()` when the user clicks "Delete selected" or "Export". The selection state does not need to be externally controlled — it needs to be readable on demand.
- An external `selectedRows: string[]` prop (D2) creates a prop → state → event loop that requires the implementor to wire up `bdsSelect` → update `selectedRows` → pass back to the table. This is the React controlled-component pattern and is natural in React but unnatural in HTML-first web component usage.
- Aqua DS uses internal selection state (`@State() selectionsData`) with `getSelectedRows()` method exposure plus `selectionChangeTable` event emission — exactly Model D1.
- D2 can be added later as a `selectedRows` prop with a `@Watch` that syncs the internal `Set`, without breaking D1 consumers.

**Recommended API surface for v1:**

```typescript
@State() private selectedRowIds: Set<string> = new Set();

@Event() bdsSelect!: EventEmitter<{ selectedIds: string[]; row: RowData }>;

@Method()
async getSelectedRows(): Promise<RowData[]> {
  return this.data.filter(row => this.selectedRowIds.has(String(row[this.rowKey])));
}

@Method()
async clearSelection(): Promise<void> {
  this.selectedRowIds = new Set();
}
```

---

### E. Column pinning CSS strategy

Column pinning with native `<table>/<th>/<td>` elements uses `position: sticky` on individual cells. Each pinned cell must specify `left: Npx` where `N` is the sum of widths of all columns pinned to its left.

#### 1. The sticky offset problem

Column widths are not fixed in `bds-table` (no explicit `width` prop planned for v1). Three approaches:

**Option E1 — ResizeObserver on header cells**

After render, observe each pinned `<th>` cell with a `ResizeObserver`. When a header cell's width changes, recompute the cumulative offsets for all pinned columns to its right and update their inline `style.left`:

```typescript
private pinOffsets: number[] = [];
private ro = new ResizeObserver(() => this.recalculatePinOffsets());

private recalculatePinOffsets(): void {
  const pinnedHeaders = Array.from(
    this.el.querySelectorAll<HTMLTableCellElement>('th[data-pinned]'),
  );
  let offset = 0;
  pinnedHeaders.forEach((th, i) => {
    this.pinOffsets[i] = offset;
    th.style.setProperty('--pin-offset', `${offset}px`);
    offset += th.offsetWidth;
  });
  this.el.querySelectorAll<HTMLTableCellElement>('td[data-pinned-col]').forEach(td => {
    const colIndex = Number(td.dataset.pinnedCol);
    td.style.setProperty('--pin-offset', `${this.pinOffsets[colIndex] ?? 0}px`);
  });
}
```

This is the most accurate approach and handles dynamic column resizing. It requires cleanup in `disconnectedCallback`.

**Option E2 — CSS custom property via inline style (simpler, v1-appropriate)**

Set `--pin-offset` as an inline style on each pinned `<th>` and `<td>` when the component renders. Offsets are calculated once in `componentDidRender` using `offsetWidth` of already-rendered header cells. No ResizeObserver needed if column widths do not change after initial render (true for v1 without column resizing):

```typescript
componentDidRender() {
  this.applyPinOffsets();
}

private applyPinOffsets(): void {
  const pinnedHeaders = Array.from(
    this.el.querySelectorAll<HTMLTableCellElement>('th[data-pinned]'),
  );
  let offset = 0;
  pinnedHeaders.forEach((th, i) => {
    th.style.left = `${offset}px`;
    const colKey = th.dataset.colKey ?? '';
    this.el.querySelectorAll<HTMLTableCellElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
      td.style.left = `${offset}px`;
    });
    offset += th.offsetWidth;
  });
}
```

**Recommendation for v1:** Option E2 (inline style in `componentDidRender`). No ResizeObserver complexity, sufficient for fixed-width columns. Add ResizeObserver in v2 when column resizing is introduced.

#### 2. Shadow DOM vs. scoped CSS: does it affect `position: sticky`?

Stencil's `styleUrl` uses **scoped CSS** by default (not shadow DOM). Scoped CSS adds a data attribute selector to every rule (e.g., `th[data-stencil-sc-123]`) but does not create a shadow root. `position: sticky` works entirely at the browser layout level and is unaffected by CSS scoping mechanisms. There are no known issues with Stencil's scoped CSS and sticky positioning.

The one genuine constraint is that the scroll container — the element that has `overflow-x: auto` and establishes the scroll context — must be an ancestor of the `<table>` but must not have `overflow: hidden` on its cross-axis, or sticky positioning breaks. Since `bds-table` controls its own DOM, this is easily managed.

#### 3. Z-index stacking strategy

```
Pinned header cells (th[data-pinned]):  z-index: 3
Pinned body cells   (td[data-pinned]):  z-index: 2
Non-pinned cells (th, td):              z-index: 1 (default, no explicit z-index needed)
```

The header row (`<thead>`) itself needs `position: sticky; top: 0; z-index: 4` if the table also supports vertical scrolling with a frozen header row. If only horizontal scroll + column pinning (no frozen header), header cells need `z-index: 3` and body cells `z-index: 2`.

#### 4. Background fill with Boreal DS tokens

Sticky cells become transparent over scrolling content unless they have an explicit `background-color`. The token to use depends on the surface context:

```scss
th[data-pinned],
td[data-pinned] {
  background-color: var(--boreal-color-surface-default);
}

tr:hover td[data-pinned] {
  background-color: var(--boreal-color-surface-hover);
}
```

These must be declared in the component's SCSS file. Because Stencil uses scoped CSS, the selector will be scoped to the component automatically.

#### 5. Complete CSS snippet for a pinned column

```scss
// bds-table.scss

.bds-table__wrapper {
  overflow-x: auto;
  position: relative;
}

table {
  border-collapse: separate;
  border-spacing: 0;
}

// Pinned header cell
th[data-pinned] {
  position: sticky;
  left: 0; // overridden by inline style.left per column
  z-index: 3;
  background-color: var(--boreal-color-surface-default);

  // Divider on the right edge of the last pinned header
  &[data-pin-last]::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background-color: var(--boreal-color-border-subtle);
  }
}

// Pinned body cell
td[data-pinned] {
  position: sticky;
  left: 0; // overridden by inline style.left per column
  z-index: 2;
  background-color: var(--boreal-color-surface-default);

  &[data-pin-last]::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background-color: var(--boreal-color-border-subtle);
  }
}

tr:hover td[data-pinned] {
  background-color: var(--boreal-color-surface-hover);
}
```

The `left` value is set via `componentDidRender` (see Option E2 above), not in SCSS. The `data-pinned` and `data-pin-last` attributes are stamped onto cells during render based on the `pinnable` attribute on `<bds-table-column>`.

---

### F. `bds-pagination` integration — client-side and server-side assessment

`bds-pagination` (branch `EOA-10580_pagination`, close to merge) is the concrete component that fills `slot="paginator"`. This section documents the integration contract, confirmed behaviors, and known gaps for both usage modes.

#### Client-side integration (v1)

The two components are fully decoupled siblings — `bds-table` never directly talks to `bds-pagination`. The parent page owns the wiring:

```html
<bds-table id="my-table" row-key="id">
  <bds-table-column col-key="name" label="Name" sortable></bds-table-column>
  <bds-pagination
    slot="paginator"
    total-items="50"
    items-per-page="10"
    current-page="1"
  ></bds-pagination>
</bds-table>

<script>
  const allRows = Array.from({ length: 50 }, (_, i) => ({
    id: i + 1,
    name: `Row ${i + 1}`,
  }));
  const table = document.querySelector("#my-table");
  const pagination = table.querySelector("bds-pagination");

  function renderPage(page, pageSize) {
    table.data = allRows.slice((page - 1) * pageSize, page * pageSize);
  }

  renderPage(1, 10);

  pagination.addEventListener("bdsPageChange", (e) => {
    const { currentPage, itemsPerPage } = e.detail;
    renderPage(currentPage, itemsPerPage);
  });
</script>
```

`bds-table`'s `@Watch('data')` (Task 6) resets row selection whenever `data` is replaced — this means page navigation automatically clears checked rows without any extra wiring.

#### Known issues in `bds-pagination` to flag before v2 server-side work

**Bug — `@Watch('totalItems')` resets to prop value, not internal state (line 143 in `bds-pagination.tsx`):**

```typescript
@Watch('totalItems')
onTotalItemsChange(newValue: number) {
  this.internalTotalItems = this.normalizeTotalItems(newValue);
  this.internalItemsPerPage = this.normalizeItemsPerPage(this.itemsPerPage);
  this.internalCurrentPage = this.normalizePage(this.currentPage); // ← uses prop, not internalCurrentPage
}
```

If `totalItems` is updated (e.g., after server-side filtering returns a new count) while `internalCurrentPage` has already advanced beyond `currentPage` prop, the displayed page snaps back. Fix: `this.normalizePage(this.internalCurrentPage)`. This must be resolved before V2-9 can be implemented.

**Bug — empty state renders literal "1" (line 486):**

```tsx
{
  isEmpty ? (
    <bds-typography variant="helper">1</bds-typography>
  ) : (
    this.getPaginationControls()
  );
}
```

When `totalPages === 0` (i.e., `totalItems = 0`), a naked `1` renders in helper typography. Should render nothing or a disabled control set.

**Gap — no `loading` prop:** Navigation buttons stay active during an in-flight server request. Server-side usage requires a `loading: boolean` prop that disables `<bds-button>` elements.

**Gap — no error rollback:** The component optimistically updates `internalCurrentPage` immediately on navigation (before the server responds). If the fetch fails and the parent does not reset `current-page` prop, the display stays on the failed page with no way to retry the same page click (the `handlePage` guard `if (pageNumber === this.internalCurrentPage) return` prevents it).

#### Server-side integration (v2 — see V2-11)

Server-side tables differ fundamentally: `bds-table` receives only the current page's rows; `totalItems` comes from the server's count query; sort and filter events emit to the parent for re-fetching rather than operating in-browser. The component API gaps above must be resolved before this mode is usable. See V2-11.

---

## Resolved Decisions

| Question                          | Decision                                                          | Rationale                                                                           |
| --------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Column grouping a v1 requirement? | **No — v2**                                                       | Deferred; hand-roll with `bds-table-column-group` when needed                       |
| `rowKey` prop name                | **`row-key`** (attr) / `rowKey` (TS)                              | Consistent with Boreal DS kebab-case attribute convention                           |
| Native elements vs. div + ARIA    | **Native `<table>/<thead>/<tbody>/<tr>/<th>/<td>`**               | Free a11y semantics; `th[scope="col"]` works out of the box                         |
| Column API                        | **Option A — light DOM composition**                              | Matches all existing Boreal DS composite components                                 |
| TanStack table-core               | **Not adopted in v1**                                             | No benefit at v1 scope; imperative DOM rendering conflicts with Stencil JSX pattern |
| Virtualization                    | **Deferred to v2 — `@tanstack/virtual-core`**                     | V1 relies on pagination; proven Stencil integration in Aqua DS                      |
| Custom cell content               | **Formatter callback (C2) for v1**                                | Simpler than template cloning; C1 (slot) addable in v2 without breaking API         |
| Row selection model               | **Internal `@State() selectedRowIds: Set<string>` + method (D1)** | Matches Aqua DS; external controlled prop addable later via `@Watch`                |
| Column pinning CSS                | **Inline `style.left` in `componentDidRender` (Option E2)**       | No ResizeObserver needed in v1; sufficient without column resizing                  |

---

## v2 Backlog

Features deferred from v1, with enough implementation context to plan the next sprint without re-doing this research.

Ordered by sprint-readiness: no-dependency items first, single Boreal DS component dependency next, architectural and multi-prerequisite items last.

### V2-1 — External controlled row selection (Model D2)

**Approach:** Additive `@Prop` layered on top of the v1 internal model.

**Implementation notes:**

- Add `@Prop() readonly selectedRows: string[] = []` — external controlled prop
- `@Watch('selectedRows')` syncs: `this.selectedRowIds = new Set(this.selectedRows)`
- No breaking change to D1 consumers — the internal `@State` is still the source of truth; the prop is an initialiser/controller

**Unlocks Vue v-model:**

V2-1 is the prerequisite for adding `bds-table` to the `componentModels` array in `vue-output-target.ts`. Once `selectedRows` exists as a writable prop, the Vue output target can wire v-model as:

```ts
{
  elements: ['bds-table'],
  event: 'bdsSelect',
  targetAttr: 'selectedRows',
}
```

This gives Vue consumers:

```vue
<BdsTable v-model:selectedRows="mySelection" :data="rows" />
```

Until V2-1 ships, `bds-table` must not be added to `componentModels` — there is no prop to bind against, and `bdsSelect` is a notification event, not a value-update signal.

**Complexity:** Low (~20 lines)

---

### V2-2 — Custom cell content via slot (C1)

**Approach:** `<template slot="cell">` on `<bds-table-column>`, cloned per row with dataset injection.

**Implementation notes:**

- See Extended Findings Section C for the full implementation pattern
- Can coexist with `formatter` (C2): if `formatter` is present it takes precedence; if a `<template slot="cell">` is present and no `formatter`, the template is cloned and row data is injected via `data-*` attributes on the root element of the clone
- Requires imperative `DocumentFragment` cloning inside `componentDidRender` — mixed JSX/imperative pattern accepted at this stage since it is additive

**Complexity:** Medium (~80 lines)

---

### V2-3 — Overflow tooltip on truncated header and cell text

**Context:** `bds-table` v1 ships with `text-overflow: ellipsis` truncation on both column headers and cell content (`table-layout: fixed`). No tooltip is shown on hover — the truncation is visual only. This entry tracks adding the on-hover overflow tooltip for both surfaces.

**Two independent behaviors that must NOT be conflated:**

1. **`info` prop tooltip** — already shipped in v1. An explicit `ⓘ` icon + `<bds-tooltip>` rendered when `<bds-table-column info="...">` is set. Shows a column description, unrelated to overflow.
2. **Overflow tooltip** — shows the full text on hover, only when `scrollWidth > clientWidth`. No icon. Applies to both `__th-label-text` (header) and `td` cell content.

**Blocker — `bds-tooltip` lacks imperative `@Method()` APIs:**

For headers (≤15 nodes), always rendering `<bds-tooltip>` per header is acceptable. For cells (potentially hundreds of rows × columns), a **singleton floating tooltip** is required for performance. This requires three new `@Method()` decorators on `bds-tooltip`:

- `show(): Promise<void>` — delegates to the existing internal `this.show()` from `anchoredMixin`
- `hide(): Promise<void>` — delegates to `this.hide()`
- `anchorTo(element: HTMLElement): Promise<void>` — detaches listeners from the current trigger, calls the internal `subscribe(element)` to wire up hover events on a new element, and triggers a positioning update via `anchoredMixin`

**Required changes before V2-3 can ship:**

| File | Change |
|------|--------|
| `bds-tooltip.tsx` | Add `@Method() show()`, `@Method() hide()`, `@Method() anchorTo(el)` |
| `types/ITooltip.ts` | Add the three method signatures |
| `bds-tooltip.spec.tsx` | Unit tests: `show()` sets `isVisible=true`; `hide()` sets it false; `anchorTo(el)` rewires trigger; `show()` while `disabled=true` stays hidden |
| `bds-tooltip.mdx` | New "Programmatic control" section; singleton usage example for list/table contexts |
| `bds-table.tsx` | One `<bds-tooltip>` singleton in `render()`; `mouseenter` event delegation in `componentDidLoad()` on `__wrapper`; overflow check → `anchorTo(span)` + `show()`; `mouseleave` → `hide()` |

**Note:** This work is complementary to, but independent of, the `imperative-migration.md` research (Steps 1–9). The slot-based trigger refactor (Steps 8–9) changes how `bds-tooltip` detects triggers declaratively — the imperative `@Method()` additions here are a separate capability. If Steps 8–9 land first, the `anchorTo()` implementation will need to be aligned with the new slot-based internal trigger management.

**Complexity:** Medium (~60 lines in `bds-table` + prerequisite `bds-tooltip` changes)

---

### V2-4 — Built-in search bar (`searchable` prop)

**Approach:** A `searchable: boolean` prop that renders `<bds-search-bar mode="filter">` internally inside `renderToolbarRight()`, removing the need for consumers to slot in their own element for the common case. The `slot="search-bar"` (introduced in v1 Task 9) is preserved as the escape hatch for custom implementations.

**⚠️ Blocking dependency:** `bds-search-bar` does not exist in Boreal DS yet. It must be designed and implemented before V2-3 can begin.

**Implementation notes:**

- When `searchable=true`, `renderToolbarRight()` renders `<bds-search-bar mode="filter">` before the filter/layout buttons; `slot="search-bar"` serves custom cases; both must not be active simultaneously
- `bds-table` does not filter internally — it listens to `bdsSearch` from `bds-search-bar` and the consumer updates `data` externally (same contract as the consumer-wired slot pattern established in v1 Task 9)
- `hasToolbar` must include `this.searchable` in its truth check
- No equivalent `paginated` prop will be added — `bds-pagination` has `totalItems`, `itemsPerPage`, `currentPage` that would require full prop-forwarding on `bds-table`; the slot is the correct long-term API for pagination

**Prerequisites:**

- `bds-search-bar` component (does not exist — must be built first)
- `renderToolbarRight()` method (implemented in v1 Task 9)

**Complexity:** Low (~15 lines) once `bds-search-bar` ships

---

### V2-5 — Row expand/collapse

**Approach:** Tree-shaped `RowData` with a `children?: RowData[]` field.

**Implementation notes:**

- Add `@State() private expandedRowIds: Set<string> = new Set()`
- Rows with `children` render an expand/collapse toggle `<button>` as their first cell content
- When expanded, child rows render immediately after the parent `<tr>` with an indent class
- Emits `bdsExpand: EventEmitter<{ rowId: string; expanded: boolean }>`
- `getSelectedRows()` must decide whether to include child rows — default: only top-level rows unless children are also checked

**Complexity:** Medium (~120 lines)

---

### V2-6 — Column grouping (`bds-table-column-group`)

**Approach:** New configuration-only Stencil element `bds-table-column-group`. No TanStack needed.

**Implementation notes:**

- `bds-table-column-group` carries a single `label: string` prop and renders `<Host style={{ display: 'none' }} />`
- `bds-table` switches from `querySelectorAll('bds-table-column')` (flat) to walking direct children: `Array.from(this.el.children)` to detect both `bds-table-column` and `bds-table-column-group`
- Replaces `slotchange` listener with `MutationObserver({ childList: true, subtree: true })` — needed because `slotchange` is blind to mutations inside `bds-table-column-group` children
- `colspan` per group = recursive count of leaf `bds-table-column` descendants
- Leaf column `rowspan` in a two-level header = `(maxDepth − columnDepth)`; group header `rowspan = 1`
- `<thead>` renders one `<tr>` per depth level; `table.getHeaderGroups()` equivalent must be hand-rolled (~150 lines)
- Public API:
  ```html
  <bds-table-column-group label="Personal Info">
    <bds-table-column key="name" label="Name" sortable></bds-table-column>
    <bds-table-column key="age" label="Age"></bds-table-column>
  </bds-table-column-group>
  ```

**Complexity:** Medium (~200 lines for column tree traversal + header group renderer)

---

### V2-7 — Column drag/drop reorder

**Approach:** Native HTML5 Drag and Drop API. No library needed.

**Implementation notes:**

- Add `@State() private columnOrder: string[]` — initialized from `this.columns.map(c => c.key)` in `componentDidLoad`
- `<th>` elements for reorderable columns get `draggable="true"`, `onDragStart`, `onDragOver`, `onDrop` handlers
- `onDrop` swaps positions in `columnOrder`; re-render picks up the new order
- `this.columns` getter returns columns sorted by `columnOrder` rather than DOM order
- Non-reorderable columns (e.g. the injected checkbox column) are excluded from drag targets
- Emits `bdsColumnReorder: EventEmitter<{ order: string[] }>` after each successful drop
- A drag handle icon (`bds-icon-drag-handle`) in the `<th>` signals draggability

**Complexity:** Low–Medium (~100 lines)

---

### V2-8 — Column resizing

**Approach:** Drag-resize handle on `<th>` right edge. Switches pin offset calculation from `componentDidRender` (static) to `ResizeObserver` (dynamic).

**Implementation notes:**

- Add `@State() private columnWidths: Record<string, number> = {}` — stores explicit widths per column key
- A `<div class="bds-table__resize-handle">` is appended inside each resizable `<th>`; `onPointerDown` starts a resize drag via `pointermove`/`pointerup`
- On drag end, updates `columnWidths[col.key]` and sets `th.style.width`
- `componentDidRender` pin offset calculation replaced with a `ResizeObserver` that fires whenever a pinned `<th>` width changes
- `disconnectedCallback` must disconnect the `ResizeObserver`

**Complexity:** Medium (~130 lines)

---

### V2-9 — Responsive toolbar

**⚠️ UX/UI validation required before scoping.** The Figma spec defines two size variants (small: min-width 744px, large: min-width 800px) and shows the full toolbar — subheading, selection zone, and right-zone icons — visible at both minimum widths. No collapsed state has been designed. `bds-table` v1 therefore treats 744px as a hard minimum width constraint; behavior below that threshold is out of scope and undocumented.

**Open questions that must be answered by UX/UI before implementation can begin:**

- What collapses first below 744px — subheading, right-zone icons, or both?
- When selection is active and the toolbar is at its densest (tag + bulk actions + slot + right-zone icons), what is the priority order for collapsing elements?
- Is there a second breakpoint (e.g. 480px) at which the toolbar switches to a stacked or overflow-menu layout?
- Should the right-zone icons (filter, columns) collapse into a single overflow `bds-dropdown` button at narrow widths?

**Proposed approach (pending UX/UI sign-off):**

- `container-type: inline-size` on the `bds-table` host element — enables CSS container queries scoped to the component's own width
- `@container (width < 744px)` override block: hide `.bds-table__toolbar-left-heading` (subheading) first since it is informational, not interactive; the selection tag and bulk actions are higher priority
- Further breakpoints and overflow-menu patterns to be specced by design

**Complexity:** Low (CSS-only if subheading-only collapse) to Medium (if overflow menu pattern is required)

---

### V2-10 — `bds-pagination` responsive text wrapping fix

**Context:** At narrow container widths, the typography text inside `.bds-pagination__items-per-page` wraps to a second line, collapsing the pagination row height and disrupting the toolbar layout. This is noticeable in any table configured with `bds-pagination` inside `slot="paginator"` when the viewport or table container is below ~744 px.

**Root cause:** `<bds-typography>` is a block-level or inline-block element inside a flex row. Without an explicit width constraint, the flex algorithm allows it to wrap when the container runs out of space. The instinctive fix — adding `white-space: nowrap` to the typography element — forces the text onto one line but introduces two new problems:

1. **Flickering:** `white-space: nowrap` makes the element's intrinsic width equal to its full unwrapped content width. If `bds-pagination` also runs a `ResizeObserver` or container query that reacts to its own width, the layout can oscillate between the nowrap and wrap states across multiple frames, causing visible flicker.
2. **Overflow:** `nowrap` does not clip — it simply prevents wrapping, so the text bleeds outside the pagination container if no `overflow: hidden` or `min-width: 0` is applied to ancestor flex items.

**Proposed approach (needs validation in `bds-pagination`):**

- Apply `white-space: nowrap` only to the typography element **and simultaneously** add `min-width: 0` on the enclosing flex item (`.bds-pagination__items-per-page`). `min-width: 0` overrides the default `min-width: auto` on flex children, which is what allows intrinsic-width blowout.
- Alternatively, wrap the label text in a container with `overflow: hidden; text-overflow: ellipsis` and a capped max-width, accepting truncation at very narrow widths.
- If `bds-pagination` uses a `ResizeObserver`, confirm it does not re-observe on every render cycle — this is the most likely source of flicker if the observer callback triggers a state update that causes re-render, which changes the observed element's size, which triggers the observer again.

**Prerequisite for V2-9 (responsive toolbar):** This fix must land in `bds-pagination` before the container-query breakpoints introduced by V2-9 are testable, since the pagination component is part of every narrow-width layout scenario. Without it, the responsive toolbar tests will produce false negatives (layout looks broken due to the wrapping text, not the toolbar logic).

**Complexity:** Low (CSS-only change in `bds-pagination`) — but requires reproducing the flicker in a minimal test case to confirm the root cause before applying a fix.

---

### V2-11 — Virtualization (`@tanstack/virtual-core`)

**Approach:** Add `@tanstack/virtual-core` (~4 kB gz). Independent of column API — no architecture change required.

**Implementation notes:**

- Add `@State() private virtualizer: Virtualizer<Element, Element>` — assignment triggers Stencil re-render
- `componentDidLoad` initialises the virtualizer with:
  - `count: this.data.length`
  - `getScrollElement: () => this.scrollContainerRef`
  - `estimateSize: () => 48` (default row height estimate)
  - `measureElement` callback for variable-height rows
  - `observeElementOffset` + `observeElementRect` wired to the scroll container (follow Aqua DS pattern in `ai-docs/lib/aqua-ds.txt`)
- `<tbody>` renders only `virtualizer.getVirtualItems()` rows; total container height set via `virtualizer.getTotalSize()` on a spacer element
- `maxHeight` prop becomes required when virtualization is enabled; without a bounded scroll container, the virtualizer has no reference height
- Decision: virtualization is opt-in via a `virtual` boolean prop — when `false`, all rows render as today

**Prerequisite:** `maxHeight` prop (implemented in v1 Task 11).

**Complexity:** Medium (~120 lines of virtualizer wiring + render update)

---

### V2-12 — Server-side mode

**Approach:** A `server-side` boolean prop that switches `bds-table` from client-owned state to an event-driven model where the parent owns all data operations.

**What changes in `bds-table` when `server-side=true`:**

- Internal sort state (`@State() sortKey / sortDirection`) is disabled — clicking a sortable header emits `bdsSort` but does NOT reorder `this.data`
- `@Watch('data')` clears selection as normal — the parent sets a new page slice, triggering a clean render
- A `loading: boolean` prop (new) shows a skeleton overlay or disables interaction while the parent fetches; implementation: `pointer-events: none` + skeleton rows or an overlay `<div>` with reduced opacity

**What changes in `bds-pagination` before V2-11 can ship (prerequisite fixes):**

- Fix `@Watch('totalItems')` to use `this.internalCurrentPage` instead of `this.currentPage` prop (Extended Finding F, Bug 1) — required for server-side filtering where `totalItems` changes per filter result
- Fix empty state branch (Finding F, Bug 2) — renders "1" when `totalItems = 0`
- Add `loading: boolean` prop — disables navigation buttons during in-flight requests

**Integration contract for server-side:**

```typescript
// Parent listens to both bds-pagination and bds-table sort/filter events
pagination.addEventListener("bdsPageChange", async ({ detail }) => {
  table.loading = true;
  const { rows, total } = await fetchPage({
    page: detail.currentPage,
    pageSize: detail.itemsPerPage,
    sort: currentSort,
    filter: currentFilter,
  });
  table.data = rows;
  pagination.totalItems = total;
  table.loading = false;
});

table.addEventListener("bdsSort", async ({ detail }) => {
  currentSort = detail;
  // re-fetch page 1 with new sort
});
```

**The async pipeline (async loading → server sorting → server filtering → virtual scroll):**

- Async loading + server sorting: covered by V2-11
- Server filtering: `bdsFilter` event (already in v1 toolbar) becomes meaningful — parent opens a filter panel, user confirms, parent re-fetches and updates `totalItems`; this works with V2-11 without additional `bds-table` changes
- Virtual scroll + server-side = infinite scroll: architecturally different from V2-11 (windowed fixed dataset vs. streaming fetch-as-you-scroll); deserves its own spike; do NOT combine with V2-11

**Prerequisites:**

- `bds-pagination` bugs fixed (see above), including the responsive text wrapping fix (V2-10)
- V2-11 (virtualization) must remain independent — do not combine with server-side mode

