# PR Title

feat(web-components): EOA-16000 add bds-table v4 feature set — grouping, reorder, resize, right-pinning, row detail, selection refinements

---

# PR Body

## Description

Closes out the remaining `bds-table` v2 backlog that `EOA-15507` (v3) deliberately deferred rather than risk scope creep on an already-large release. v3 shipped virtualization, server-side mode, the column footer, and the `maxClientRows` guardrail; this PR delivers everything that was left on the table, plus right-edge column pinning — pulled into scope after a feasibility check found it shares the exact offset-recompute/resize-observer infrastructure the resizing work already touches, making it cheaper to bundle now than to reopen the same code later.

Every feature is **additive and opt-in**. A table that does not set any of the new props or slots renders exactly as it does today.

**What ships:**

| Area | API added |
|---|---|
| Column grouping | `<bds-table-column-group label info>` (new component) |
| Column drag/drop reorder | `bds-table-column.reorderable`, `bdsColumnReorder` |
| Column resizing | `bds-table-column.resizable`, `bdsColumnResize` |
| Right-edge column pinning | `bds-table-column.pinDirection: 'left' \| 'right'` |
| Row expand/collapse | `<template slot="row-detail">`, `bdsExpand` |
| Custom cell content | `<template slot="cell">` on `bds-table-column` |
| Selection refinements | `selectAllPages`, `rowSelectable`, shift+click range selection, `persistSelection`, `rowClickSelects` |
| Opt-in toolbar buttons | `filterable`, `columnLayoutToggle`, `bdsFilter`, `bdsTableLayout` |

Two things stayed deliberately out of scope: the responsive toolbar (and its `bds-pagination` text-wrap prerequisite), which is blocked on an unscheduled UX/UI cross-component review; and tree-shaped row data — row expansion was re-scoped mid-planning to a **master-detail** model after a design reference showed one full-width detail panel per row rather than nested child rows.

---

## Implementation Details

Fourteen tasks landed as incremental, independently committable additions, sequenced so each builds on infrastructure the previous ones introduced rather than re-deriving it.

**Shared infrastructure first.** The `_formatterNodes` map and its `cached.row === row` identity guard were extracted into a standalone `CellContentCache` before any feature used it, so the master-detail slot (`detail:${rowId}`) and `<template slot="cell">` (`${colKey}:${rowId}`) write into the *same* cache instance under different key prefixes instead of each building a parallel one. This is what makes virtualized row recycling correct for all three content paths with no per-feature guard code.

**Reused, not reinvented.** Column resizing calls the existing `updatePinnedColumnOffsets(true)` from its drag handler; right-edge pinning adds a sibling `updatePinnedColumnOffsetsRight()` driven from the same `ResizeObserver` callback — no third recompute mechanism. Resize `pointermove` bursts are collapsed with the same microtask-flag throttle shape `scheduleVirtualRerender()` already uses.

**Internal precedent over external.** The reorder handle mirrors `bds-card-header`'s already-shipped `reorder` prop verbatim — one always-visible `bds-icon-six-dots` handle, `role="button"`/`tabIndex`, `KeyboardController`-driven keys, and native `draggable` armed only for the duration of a press gesture. An original citation claiming AG Grid and Fluent UI pair drag with explicit Move-left/right buttons was checked against real sources and found inaccurate; the Figma `_Header` component likewise defines exactly one reorder icon. `ArrowLeft`/`ArrowRight` keyboard movement is genuinely new behavior — `bds-card-header`'s `Enter`/`Space` only re-arms dragging because `bds-card` delegates reordering to consumer script, which `bds-table` cannot do since it owns `columnOrder` itself.

**Column discovery went recursive.** The flat `querySelectorAll('bds-table-column')` became a recursive walk of `Array.from(el.children)` producing both a `columnTree` (header rendering only) and the existing flattened leaf `columns` array — unchanged in shape, so cells, sort, footer, pin-offsets, and skeleton consumers are all unaffected. The `MutationObserver` upgraded to `{ childList: true, subtree: true }` to see columns added inside a group.

**Grouped headers use filler cells, not `rowSpan`.** Corrected against Figma nodes `53:38140`/`53:42699`: ungrouped column labels sit at row 2's baseline, not centered across both header rows, so row 1 renders an empty borderless `<th>` above them. Groups may be interspersed between ungrouped columns, not just trailing.

**Shift+range works around a real gap.** `bds-checkbox`'s `bdsChange` carries a boolean, never the originating `MouseEvent`, so `shiftKey` is unreachable from the public event. Rather than change the checkbox's public API, `bds-table` reuses its own established capture-phase delegation on `_tableWrapperEl` to stash the modifier before `bdsChange` fires.

**Toolbar features are inert by design.** `filterable`/`columnLayoutToggle` render buttons that emit `bdsFilter`/`bdsTableLayout` and nothing else — the filter drawer and column-visibility dropdown are built entirely in Storybook story script, matching the existing `BulkEdit`/`WithAddRow` convention of consumer-owned dialog wiring. No centralizing helper was introduced for two usages.

---

## Impact Analysis

- **No breaking changes.** Every prop defaults to `false`/existing behavior; both new slots are absent by default. `selectAllPages` specifically defaults to page-scoped select-all — identical to today — rather than adopting the cross-page default the original spike suggested, precisely to avoid a silent behavior change.
- **`RowData` is unchanged** (`Record<string, unknown>`). The master-detail re-scope means no `children` field, no selection cascading, no tree-aware sort, no indentation CSS.
- **One structural rendering change affects all tables:** an unconditional `<colgroup>`/`<col>` per column now backs column widths. This was required because `table-layout: fixed` only reads widths from the table's first `<tr>` (CSS 2.1 §17.5.2.1) — once grouping introduced a second `<thead>` row, every leaf column's `width` was silently ignored and pinned offsets broke. `<col>` is exempt from that restriction. Covered by the existing pin-offset and sizing suites.
- **One fix outside `bds-table`:** `bds-checkbox` now also registers `Shift+Space` for its toggle handler (see Testing).
- **New shared SCSS mixin:** `bds-transition-collapse` in `_interactions.scss`, written generically so a future `bds-collapse`/accordion component can reuse it verbatim.
- Framework wrappers for `bds-table-column-group` auto-generate in `boreal-react` and `boreal-vue`.

---

## Testing Conducted

**Automated:**

- [x] Unit tests with ≥ 90% coverage — seven new spec files (`expand`, `template-cell`, `grouping`, `reorder`, `resize`, `pin-offsets` extensions, `column-group.basics`) plus substantial additions to `selection`, `toolbar`, `utils`, `virtual`, and `extras`
- [x] Full component suite green at every task boundary — 2574 → 2595 → 2615 → 2625 → 2655 → 2659 → 2668 tests passing as tasks landed
- [x] Toolbar suite 44/44 at Task 13, 48/48 after the divider follow-up fix
- [x] Accessibility tests — reorder handle `role="button"`/keyboard move, resize handle `role="separator"`/`aria-orientation`/`aria-valuenow`, expand toggle `aria-expanded`
- [x] Regression guards — expand toggle never mutates `selectedRowIds`; virtualized row recycling never leaks detail or templated content onto the wrong row; a table with zero groups renders the original single-row `<thead>` unchanged
- [ ] Mutation testing — **descoped from this ticket** (see Additional Remarks)

**Manual:**

- [x] Every implementation task (1–13) was manually verified in a purpose-built, from-scratch `src/index.html` playground scenario before being marked complete — manual tests were mandatory, non-waiveable gates for this plan
- [x] **React and Vue parity checked per task**, not once at the end, using the `boreal-react` and `boreal-vue` wrapper playgrounds (`examples/react-testapp`, `examples/vue-testapp`)
- [x] Cross-browser verification (Chrome, Firefox, Safari) for the native drag-and-drop + `position: sticky` interaction, which no authoritative source confirms behaves identically across engines
- [x] Task 14's docs-only stories verified in `pnpm dev:docs` — delete removed exactly the targeted row, the toolbar-actions slot held exactly one button, and the downloaded `users.csv` was verified byte-for-byte against the story's dataset

**Bugs found by manual QA that unit tests alone did not catch** (all root-cause-fixed, all with regression tests added):

- Dropping a column onto its immediate right neighbor was a silent no-op — `moveColumn`'s insert-before semantics, fixed with a direction-aware insert
- Keyboard focus desynced from column identity after a reorder, making arrow keys oscillate — fixed with `key={col.colKey}` plus an explicit `componentDidRender` refocus (moving a keyed node via `insertBefore` blurs it even as the same DOM object)
- `updatePinnedColumnOffsets`'s dirty-check did not track `columnOrder`, leaving pinned header offsets stale after an unrelated reorder
- Relocating the six-dot handle set `display: flex` directly on `<th>`, overriding its `table-cell` role and breaking table layout entirely — caught by visual inspection, fixed with an inner wrapper span
- `currentColumnWidthPx` measured a `<col>` element's `getBoundingClientRect()`, which generates no rendered box (CSS 2.1 §17.2.1) and returns zero in real browsers while jsdom masked it
- Unpin never *cleared* `style.left`/`style.right`, only ever set it — invisible for three tasks because every earlier test unpinned the outermost column, where the leftover offset is `0`
- Shift+click also triggered the browser's native text-selection-extend gesture, highlighting all cell text between click points
- **Shift+Space did nothing at all** — root cause was in `bds-checkbox`, whose `KeyboardController` registered bare `Space` and does exact-modifier-match lookup. Undetected because every prior test dispatched `bdsChange` synthetically or used mouse clicks. Fixed, covered by new `bds-checkbox` keyboard tests plus an end-to-end `bds-table` test that drives a real keydown, and a keyboard-only step was added to all three playground files so future QA exercises this path
- `applyCellTemplate` raced React's `useEffect`-driven late population of `template.content` and gave up silently — fixed with a one-shot, per-column-deduped `MutationObserver` that triggers `forceUpdate` once content lands; confirmed deterministic across 5 fresh React reloads

A suspected React/Vue-only first-keyboard-resize no-op was investigated twice and never reproduced against a correctly built package — both times the live `pnpm dev` server was serving a stale wrapper bundle (Vite's dependency pre-bundling cache does not invalidate when a linked workspace package's dist changes). Confirmed across four clean-build attempts via `dev:pack:react`/`dev:pack:vue`; no code change was needed.

---

## Related Changes

- **`bds-checkbox`** (`web-components`): registers `Shift+Space` alongside `Space` for its toggle handler — a real bug surfaced by Task 10's keyboard-only shift-range step, fixed at the source rather than worked around in `bds-table`.
- **`_interactions.scss`** (`web-components`): new `bds-transition-collapse` mixin, deliberately written for future accordion/collapse reuse.
- **Test utilities** (`web-components`): new `dragDrop` and `pointerCapture` mocks under `src/utils/testing/mocks/`.
- **`boreal-docs` — documentation-only additions (Task 14).** A docs-only task with no component code: `WithActionsColumn` demonstrates interactive cell content via the already-shipped `formatter` (chosen over `<template slot="cell">` so the canonical example stays framework-agnostic), and `WithRefresh` was renamed to `WithExport`, its Refresh button replaced with a client-side CSV download. MDX cross-references were updated accordingly.
- **Follow-up fix — toolbar divider.** The toolbar divider rendered even when the `toolbar-table-actions` container was empty. Fixed with a new `hasToolbarTableActions` getter gating it; toolbar suite went 44/44 → 48/48.
- **Follow-up fix — `WithColumnVisibilityDropdown` positioning.** The story's dropdown mispositioned on Storybook's Docs page, where the story renders inside a second nested iframe. Story-level fix; no component change.
- **`boreal-react` / `boreal-vue`:** wrapper proxies for `bds-table-column-group` auto-generate from the Stencil output targets — no hand-written wrapper code.
- **No changes to** `boreal-styleguidelines` — all new styling uses existing `var(--boreal-*)` tokens.

---

## Additional Remarks

- **Mutation testing was descoped, not deferred as a TODO.** The plan originally carried a fifteenth task — one consolidated Stryker pass across the combined v2+v3+v4 surface. It was dropped by explicit decision on 2026-08-05. Tasks 1–14 are the full delivered scope of `EOA-16000`.
- **Grouping is two-level only** — a group contains `bds-table-column` leaves directly; nested groups are not supported and this is documented.
- **Row detail is master-detail only** — one full-width panel per row. It does not support recursive tree row grouping, and the MDX says so explicitly. Detail-slot content is entirely consumer-owned and is never counted toward `getSelectedRows()`.
- **`bdsExpand` carries the full `row` object**, not just `rowId`, specifically so consumers can build nested content (e.g. a sub-table from an array field) that `data-*` attributes cannot express.
- **Detail-panel animation is non-virtual only.** In `virtual` mode the detail row is added and removed instantly. Animating a row's height while the virtualizer concurrently tracks its scroll position needs continuous remeasurement mid-transition — a materially harder problem, scoped out explicitly rather than attempted.
- **Known minor UX behavior:** while a reorder drag is armed, `draggable="true"` disables normal text selection within that `<th>` (Alt+drag restores it). Documented.
- **Pinned columns are excluded from reorder in both pin directions.**
- **Scope grew slightly in Task 4:** `bds-table-column-group` gained an opt-in `info` prop (tooltip), mirroring `bds-table-column.info` and `bds-card-header.info`.
- **A pre-existing pagination bug was bundled in by explicit decision.** `onRowsChange`/`setupRowsPagination` read the slotted `bds-pagination`'s `itemsPerPage` property before Stencil finishes hydrating it, silently falling back to the class default of `10`. Fixed defensively via `getEffectiveItemsPerPage()`, narrowed after review so it only consults the raw attribute while the property still sits at its un-hydrated default. This is a scoped workaround, not the principled `componentOnReady()`-based fix — see the follow-up note in the plan.
- **Out of scope, should be its own ticket:** the `bds-dialog` backdrop-click-closes-on-inside-click regression found during Task 13 research. It predates this plan and affects every `bds-dialog` consumer.
- **A future ticket could extract a shared `ReorderHandleController`** reusable by both `bds-card-header` and `bds-table`. Not attempted here — `bds-card` is already released and refactoring it was out of scope.
- Full plan with per-task status notes, discovered bugs, and locked design decisions: `ai-work/plans/EOA-16000-bds-table-v4.md`. Column-resizing deep dive: `ai-work/research/2026-08-03-bds-table-column-resizing-explained.md`.

---

## References

Closes EOA-16000
Refs EOA-15507 (v3, the plan this directly continues)
Refs EOA-14935 (v2, whose deferred backlog this closes)

---

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [x] Ticket reference included (`Closes EOA-16000`)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally (`.agents/scripts/with-node.sh pnpm test`)

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix (`bds-table-column-group`)
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()` (`bdsExpand`, `bdsColumnReorder`, `bdsColumnResize`, `bdsFilter`, `bdsTableLayout`)
- [x] SCSS follows `@use` pattern (no `@import`)
- [x] Light DOM patterns documented — `<template slot="row-detail">` and `<template slot="cell">` contracts are both documented in MDX, including the React/Vue caveat that `<template>` content must be populated imperatively

### Boreal DS — Form Components

Not applicable — `bds-table` is not a form-associated component.

### Testing

- [x] Unit test coverage ≥ 90% statements
- [x] Tests cover happy path, error cases, and edge cases
- [x] Accessibility verified (keyboard navigation for reorder, resize, expand, and shift+range selection)
- [x] Manual testing completed across Chrome, Firefox, and Safari, and across all three consumption surfaces (web components, React, Vue)
- [ ] Mutation-score gate — descoped from this ticket by explicit decision

### Documentation

- [x] JSDoc added to all public APIs (props, events, slots)
- [x] Storybook stories created for every new feature (`Grouped headers`, `ReorderableColumns`, `ResizableColumns`, `ResizableColumnsVirtualized`, `ResizableRightPinnedColumn`, `CustomCellContent`, `CustomCellContentFormatterPrecedence`, `WithConditionalSelection`, `WithCrossPageRangeSelection`, `WithFilterDrawer`, `WithColumnVisibilityDropdown`, `WithActionsColumn`, `WithExport`)
- [x] Storybook MDX documentation added — new anatomy sections for column grouping, reorder, resizing, and pinning (which previously had none), plus keyboard documentation consolidated into a single canonical table in "Accessibility" after it had drifted into per-feature duplicates
- [x] "Current limitations" rows resolved by this work were removed from the MDX

### Performance & Compatibility

- [x] No new console warnings or errors
- [x] Bundle size impact assessed — additive, and every feature is gated behind an opt-in prop or an absent slot
- [x] Compatible across supported browsers (Chrome, Firefox, Safari, Edge) — DnD + sticky interaction explicitly cross-browser tested
- [x] No regression in existing functionality — full component suite green, with explicit regression guards for the ungrouped/single-row `<thead>` path and the unchanged flat `columns` array shape
