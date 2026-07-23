# EOA-16000 — bds-table v4 column grouping, drag/drop reorder, resizing, row expand/collapse, selection refinements, responsive toolbar

**Ticket:** EOA-16000 (continuation of `EOA-14935`/`EOA-15507`; carries forward the spike backlog that neither v2 nor v3 scheduled)
**Status:** Pending
**Goal:** Close out the remaining `bds-table` v2 backlog that v3 (`EOA-15507`, status: `done`) did not schedule — column grouping, drag/drop column reorder, column resizing, row expand/collapse, custom cell content via declarative `<template>` slots, five row-selection refinements (`checkboxSelectionVisibleOnly`, `isRowSelectable`, shift+range selection, `keepNonExistentRowsSelected`, `disableRowSelectionOnClick`), opt-in filter/column-visibility toolbar buttons, and the responsive toolbar behavior below 744px (pending its own UX/UI sign-off).

**Plan:** Not yet written. Each item below needs its own design/scoping pass before task-level planning can begin (same gating pattern the column footer and responsive toolbar already went through in `EOA-15507`) — see Open Questions. A dedicated `ai-work/plans/EOA-16000-bds-table-v4.md` should be authored via the `writing-plans` skill once that scoping is done.

## Scope

**In:**

- Column grouping (`bds-table-column-group`) — new configuration-only Stencil element; `bds-table` walks direct children instead of a flat `querySelectorAll`, replaces `slotchange` with a `MutationObserver({ childList: true, subtree: true })`, and hand-rolls colspan/rowspan for a two-level header
- Column drag/drop reorder ("Button Reorder") — native HTML5 Drag and Drop API on reorderable `<th>` elements, emits `bdsColumnReorder`
- Column resizing — drag-resize handle on `<th>` right edge; switches the pin-offset calculation from the current static `componentDidRender` pass to a `ResizeObserver`, sharing one recompute path with the existing virtualized-scroll throttling rather than duplicating it
- Row expand/collapse — tree-shaped `RowData` with a `children?: RowData[]` field, expand/collapse toggle per row, `bdsExpand` event; requires an explicit virtualizer-remeasure call on every toggle since virtualization now exists (v3 shipped it)
- Custom cell content via declarative `<template slot="cell">` — additive alternative to the existing `formatter` callback; requires imperative `DocumentFragment` cloning tied to the row's `key={rowId}` so virtualized row recycling doesn't leave stale injected content on the wrong row
- Five row-selection refinements, evaluated together since they all touch `handleSelectAll`/the header checkbox/`onDataChange`: `checkboxSelectionVisibleOnly` (scope select-all to the current page), `isRowSelectable` (conditional per-row selectability), shift+range selection, `keepNonExistentRowsSelected` (server-side selection persistence), `disableRowSelectionOnClick` (reserved prop, no current implementation to gate)
- Opt-in `filterable`/`columnLayoutToggle` props gating the built-in Filter/Column-visibility toolbar buttons (currently always rendered) — must also gate their existing `loading`-state skeleton swap, not just the real buttons
- Responsive toolbar behavior below 744px, plus its `bds-pagination` prerequisite (items-per-page label text-wrapping fix) — both blocked on a UX/UI cross-component responsive review with no scheduled owner as of this writing
- A single consolidated mutation-testing pass (Stryker, ≥90% per component, documented survivors for anything below 100%) across every file touched by `EOA-14935`, `EOA-15507`, **and** this ticket's own tasks, run once as the final task — deferred out of the v3 plan specifically so it would run once against the full combined surface area instead of twice

**Deferred further still (not in this ticket either):**

- New reusable `bds-skeleton` primitive (rect/text/circle variants, shimmer via `var(--boreal-*)` tokens) — v3 implemented the loading visual as a private, table-scoped render helper built to this future primitive's exact shape; extracting it is gated on a second real consumer appearing (e.g. `bds-list`, `bds-card`), not scheduled here
- A shared virtualization utility between `bds-table` and `bds-search-bar` — researched and found technically possible only via a larger rearchitecture of `bds-search-bar`'s own list rendering, gated on an accessibility redesign with no scheduled owner. See `ai-work/research/2026-07-06-shared-virtualization-utility.md`
- Multiple header type variants, per-column skeleton dropdown config, explicit scrollbar visibility toggles, and per-cell state variants — visible only in a design playground with no equivalent in the implementation; needs its own design pass to define the actual API surface before it can be scoped into a future ticket

**Out (still not in scope):**

- Any change to `bds-search-bar`'s own large-list performance behavior beyond the deferred shared-utility research above
- Any work that depends on the UX/UI responsive review landing first (responsive toolbar and its `bds-pagination` prerequisite are included above as tracked scope, but implementation cannot start until that review is scheduled)

## Acceptance Criteria

- [ ] `bds-table-column-group` exists and supports grouped column headers with correct colspan/rowspan across a two-level `<thead>`, without regressing ungrouped columns
- [ ] `bds-table-column` headers support drag/drop reorder, emitting `bdsColumnReorder` with the new order; pinned-column offset calculation continues to compute correctly after a reorder
- [ ] `bds-table-column` headers support drag-to-resize; the pin-offset `ResizeObserver` and the resize handler share one recompute path (no duplicate/competing offset calculations)
- [ ] Rows with a `children` array can be expanded/collapsed inline via `bdsExpand`; virtualized tables correctly remeasure on every toggle with no visible layout jump
- [ ] `<bds-table-column>` supports `<template slot="cell">` as an additive alternative to `formatter`, with row-identity-safe content injection under virtualized scroll
- [ ] `checkboxSelectionVisibleOnly`, `isRowSelectable`, shift+range selection, `keepNonExistentRowsSelected`, and `disableRowSelectionOnClick` are all implemented per their spike write-ups, with `handleSelectAll`/header-checkbox/`onDataChange` updated consistently across all five
- [ ] `filterable`/`columnLayoutToggle` props gate the Filter/Column-visibility toolbar buttons (default `false`), including their loading-state skeleton equivalents; `bds-table.mdx` documents the opt-in behavior
- [ ] `bds-table`'s toolbar adapts responsively below 744px, signed off by UX/UI before implementation begins
- [ ] `bds-table.mdx`'s "Current limitations" table has every row this ticket closes removed
- [ ] Every new/changed behavior has passing unit tests (coverage phase) added per task
- [ ] **Final task:** a single mutation-testing pass (Stryker, ≥90% per component, documented survivors for anything below 100%) run once across every component touched by `EOA-14935`, `EOA-15507`, and this ticket combined — carried forward unchanged from `EOA-15507`'s deferred Task 12

## Dependencies

- `EOA-15507-bds-table-v3.md` (shipped, `status: done`) — this ticket continues its deferred backlog; row virtualization (needed for the expand/collapse remeasure requirement) and the pin-offset `ResizeObserver` pattern (needed for column resizing to share a recompute path) both ship there
- `2026-06-16-bds-table-column-api-spike.md` — primary research source; see its "Deferred to v4" table and the "Implementation Plan (2026-07-23)" section for full context on how each item's scope was carried forward
- UX/UI cross-component responsive review — blocks the responsive-toolbar item specifically; no scheduled owner as of this writing

## Open Questions

- **Not yet resolved — every item in this ticket needs its own design/scoping pass before task-level planning can begin**, mirroring how the column footer and responsive toolbar each needed a sign-off gate in `EOA-15507`. In particular:
  - Column grouping, drag/drop reorder, and resizing all need explicit interaction-design decisions (e.g. what happens to a pinned column mid-drag; whether resize handles are visible on hover-only or always) not covered by the original spike, which focused on technical feasibility, not UX
  - Row expand/collapse needs a decision on whether `getSelectedRows()` includes child rows by default
  - The responsive toolbar item cannot be scoped at all until the UX/UI review happens — do not create tasks for it before then
- Whether the five row-selection refinements should ship as one task or five independent tasks — they touch overlapping code (`handleSelectAll`, header checkbox, `onDataChange`) so a combined task may reduce merge-conflict risk, but each has an independent, narrow acceptance criterion suited to separate tasks. Decide during plan-writing.
- Do not start implementation on any item in this ticket until its design/scoping pass is complete.
