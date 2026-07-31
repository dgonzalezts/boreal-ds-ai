---
ticket: EOA-16000
component: bds-table
status: in progress
created: 2026-07-29
---

# bds-table v4 — Column Grouping, Drag/Drop Reorder, Resizing, Right-Edge Pinning, Row Expand/Collapse, Selection Refinements, Opt-in Toolbar

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

## Context

`EOA-15507` (v3) shipped virtualization, server-side mode, the column footer, and the `maxClientRows` guardrail, but deliberately deferred the remaining `bds-table` v2 backlog (documented in `ai-work/research/2026-06-16-bds-table-column-api-spike.md`'s "Deferred to v4" table) to a follow-up ticket rather than risk scope creep on an already-large release. `EOA-16000` is that follow-up: it closes out column grouping, drag/drop reorder, resizing, row expand/collapse, declarative custom cell content, five row-selection refinements, and opt-in toolbar buttons — plus right-edge column pinning, added to this plan's scope after a feasibility check found it shares the exact offset-recompute/resize-observer infrastructure the resizing task already touches, making it cheap to bundle now rather than reopen the same code a second time later.

Two things intentionally stayed out of scope after review: the responsive toolbar (and its `bds-pagination` text-wrap prerequisite) remains blocked on an unscheduled UX/UI cross-component review and is excluded entirely (not even a placeholder task) until that review is scheduled; and the row-expansion feature was re-scoped mid-planning away from the ticket's original literal text (`children?: RowData[]` tree data) to a **master-detail slot** model, after a provided design reference showed a single full-width detail panel per row rather than nested child rows — this turned out to simplify the feature substantially, since it removes the selection-cascading, tree-sort, and indentation concerns tree data would have introduced.

**Goal:** Close out the remaining `bds-table` v2 backlog that `EOA-15507` (v3, shipped) did not schedule: column grouping (`bds-table-column-group`), column drag/drop reorder, column resizing, right-edge column pinning, row expand/collapse via a master-detail slot, custom cell content via `<template slot="cell">`, five row-selection refinements (`selectAllPages`, `rowSelectable`, shift+range selection, `persistSelection`, `rowClickSelects`), and opt-in `filterable`/`columnLayoutToggle` toolbar-button props — finishing with one consolidated Stryker mutation-testing pass across the combined v2+v3+v4 surface.

**Ticket brief:** [`ai-work/tickets/EOA-16000-bds-table-v4.md`](../tickets/EOA-16000-bds-table-v4.md)

**Relationship to v3:** This plan is a direct continuation of `ai-work/plans/EOA-15507-bds-table-v3.md` (status: `done`). It reuses v3's virtualization (`@tanstack/virtual-core` `Virtualizer`), pin-offset `ResizeObserver` (`updatePinnedColumnOffsets`), and formatter cache (`_formatterNodes`) as direct building blocks rather than re-deriving any of that infrastructure. Explicitly out of this plan: the responsive toolbar (V2-9) and its `bds-pagination` text-wrap prerequisite (V2-10) — both blocked on an unscheduled UX/UI review.

**Architecture:** Fifteen tasks land as incremental, independently committable additions to `bds-table` and its two column-declaration children (`bds-table-column`, plus a new `bds-table-column-group`). Tasks are sequenced so later tasks build on infrastructure earlier tasks introduce: the shared cell-content cache (Task 1) is extracted *first*, since both row expand/collapse (Task 2) and `<template slot="cell">` (Task 3) write into it rather than each building a separate cache. Column grouping (Task 4) lands before reorder (Task 5) so reorder's header-rendering assumptions already account for grouped headers. Resizing (Task 6) and right-edge pinning (Task 7) share one offset-recompute path, so pinning is sequenced immediately after resizing rather than earlier. The five selection refinements (Tasks 8–12) are ordered so each can assume the guards introduced by the one before it. Task 14 is a documentation-only addition (actions-column and CSV-export story examples) needing no new component code. The final task (15) is a single consolidated Stryker pass across every file touched by `EOA-14935` (v2), `EOA-15507` (v3), and this ticket — carried forward unchanged from v3's deferred Task 12.

**Tech Stack:** Stencil (TSX + scoped SCSS), `@tanstack/virtual-core` (already a direct dependency), native HTML5 Drag and Drop API and Pointer Events (no new dependency), Jest + Stryker for the two-phase unit-test/mutation-score gate.

---

## Testing policy for this plan (unchanged from v3)

**Each task below adds unit tests only** (coverage-phase). Mutation testing (Stryker) is deliberately not run per task — it is consolidated into Task 15, run once after every other task in this plan is complete, across every component this plan *and* `EOA-15507` *and* `EOA-14935` touched. Do not install Stryker, create `stryker.*.config.mjs` files, or attempt the two-phase gate until Task 15.

**Manual tests are mandatory gates, not waiveable, for this plan** — this deliberately overrides `.agents/rules/plan-execution.md`'s default ("the test passes or is explicitly waived by the user"). No task in this plan may be marked complete until its manual test has been run and passes; do not proceed to the next task on a waiver.

**Each task's manual test uses its own fresh `src/index.html` playground scenario, built from scratch — do not extend or reuse v3's `#skeleton-table`/`#pin-table`/`#virtual-table` sections.** This is deliberate: v3's fixtures back v3-shipped behavior, and this plan's tasks must be manually verifiable in isolation from v3's component version, not coupled to fixture state a different version of the component produced. Each task below names its own dedicated scenario. `src/index.html` remains dev-only scratch content and is never committed, per existing convention.

**Every implementation task's manual test (Tasks 1–13) includes a final React/Vue parity check** — confirm the same scenario behaves identically through the `boreal-react` and `boreal-vue` output-target wrapper playgrounds, not just the raw web-component. This component has 15+ opt-in features crossing three framework surfaces; checking parity per-task, scoped to the one feature that just landed, catches framework-specific regressions (synthetic event handling, prop/attribute forwarding) immediately rather than in one large, hard-to-debug pass at the end. Task 14 (documentation-only) and Task 15 (mutation testing) are exempt — neither touches framework-wrapper behavior.

---

## Files to create / modify

| File | Change | Tasks |
|---|---|---|
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` | modify | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` | modify | 2, 4, 5, 6, 7, 8 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` | modify | 2 (`BdsExpandEventDetail`), 5 (`bdsColumnReorder`), 6 (`bdsColumnResize`), 8, 9, 10, 11, 12, 13 (new props) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/utils/bds-table-utils.ts` | modify | 10 (range-index helper) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/utils/CellContentCache.ts` | new | 1 (used by 2, 3) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` | modify | 13 (gate filter/layout skeleton) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.expand.spec.ts` | new | 2 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.utils.spec.ts` | modify | 1, 10 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.formatter.spec.ts` | modify | 1, 3 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.template-cell.spec.ts` | new | 3 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.grouping.spec.ts` | new | 4 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.reorder.spec.ts` | new | 5 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.resize.spec.ts` | new | 6 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.pin-offsets.spec.ts` | modify | 5, 6, 7 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.virtual.spec.ts` | modify | 2 (remeasure-on-toggle regression) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` | modify | 8, 9, 10, 11, 12 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.toolbar.spec.ts` | modify | 13 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` | modify | 3 (JSDoc), 5 (`reorderable`), 6 (`resizable`), 7 (`pinDirection`) |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/types/ITableColumn.ts` | modify | 3, 5, 6, 7 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/__test__/bds-table-column.basics.spec.ts` | modify | 5, 6, 7 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/bds-table-column-group.tsx` | new | 4 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/types/ITableColumnGroup.ts` | new | 4 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/__test__/bds-table-column-group.basics.spec.ts` | new | 4 |
| `packages/boreal-web-components/src/utils/constants/common/Icons.ts` | modify | 2 (verify existing expand/collapse chevron glyph — Task 5 needs no icon change, reuses `bds-icon-six-dots`, already shipped for `bds-card-header`) |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` | modify | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` | modify | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 |

`packages/boreal-web-components/src/components.d.ts` and the `boreal-react`/`boreal-vue` output-target proxy files are auto-generated by the Stencil build — not listed above, never hand-edited.

---

## Utility Discovery

| Feature area | Existing pattern to reuse | Why it fits | Decision |
|---|---|---|---|
| Row-detail / cell content caching | `_formatterNodes: Map<string, {row, node}>` + `applyCellFormatter`'s identity guard (`cached.row === row`) | Already solves "don't re-clone/re-append when the row reference is unchanged, but do when a `<tr>` is recycled to a different row under virtualization" — exactly what both the master-detail slot (Task 2) and `<template slot="cell">` (Task 3) need | Extract into `CellContentCache` (Task 1) first; both consumers write into the *same* cache instance, keyed by their own prefix (`detail:${rowId}` / `${colKey}:${rowId}`), rather than building separate caches |
| Row expand/collapse virtualizer remeasure | `renderVirtualRows()`'s `ref={el => virtualizer.measureElement(el ?? null)}` (already ships in v3) | The detail `<tr>` is modeled as one more entry in the flattened virtualizer list, so it's measured for free the same way any row is; only the *toggled row itself* needs an explicit remeasure call for its own potential height change (e.g. chevron reflow) | Reuse `virtualizer.measureElement()` directly; add a synthetic detail-entry to the flattened list rather than a parallel rendering path |
| Footer content relocation | `footerNode(col)` / `_footerNodes` Map / `appendChildNode()` (`Array.from(col.children).find(...)`, not `:scope` — confirmed broken in `@stencil/core/mock-doc`) | Identical "read a light-DOM child once, cache by key, project into rendered output" shape needed for both the row-detail template (read once on `bds-table` itself) and `<template slot="cell">` (read once per column) | Reuse the same `Array.from(children).find(...)` pattern for `rowDetailTemplate` (Task 2) and `templateNode(col)` (Task 3) |
| Pin-offset recompute (resize + right-edge pinning) | `updatePinnedColumnOffsets(force)` + `setupResizeObserver()`'s `ResizeObserver` | Both Task 6 (resizing) and Task 7 (right-edge pinning) need the exact same DOM-order-walk/offset-accumulation shape mid-drag and on resize — building new recompute paths for either would reproduce the Task 8/22b (v3) layout-thrash bug this method was built to avoid | Task 6 calls `updatePinnedColumnOffsets(true)` directly from the resize-drag handler; Task 7 adds a sibling `updatePinnedColumnOffsetsRight()` invoked from the same `ResizeObserver` callback — no third recompute mechanism |
| Rapid-event throttling | `scheduleVirtualRerender()`'s microtask-flag pattern (`_virtualRerenderScheduled`) | `pointermove` during a resize drag fires far more often than one recompute needs; same "collapse a burst of events into one state update per frame" problem `scheduleVirtualRerender` already solves for virtualized scroll | Add a `scheduleResizeRecompute()` using the identical boolean-flag + microtask/rAF throttle shape, not a bespoke debounce |
| Column discovery / mutation watching | `componentWillLoad`'s `querySelectorAll('bds-table-column')` + `componentDidLoad`'s `MutationObserver({ childList: true })` | Grouping needs to walk a tree (`bds-table-column-group` containing `bds-table-column` leaves) instead of a flat query, and needs `subtree: true` to see mutations inside a group | Replace the flat query with a recursive `Array.from(el.children)` walk producing both a tree (`columnTree`) and a flattened leaf list (`columns`, unchanged shape/consumers); upgrade the observer to `{ childList: true, subtree: true }` |
| Column reorder persistence across DOM order | Existing pin-offset loop already re-derives offsets from *rendered* `<th>` DOM order every render (not a cached index) | Confirmed in the 2026-06-16 spike (Low risk): once rendering iterates a reordered array, `querySelectorAll('th[data-pinned]')` naturally reflects the new order for free | No change needed to `updatePinnedColumnOffsets` for reorder — just add regression tests confirming reorder + pinning together still compute correct offsets |
| Existing per-column boolean-opt-in convention | `sortable`, `pinnable` on `ITableColumn` | Establishes the "one boolean per column-level feature, default `false`" shape already used twice | Add `reorderable`/`resizable` as new per-column booleans on `ITableColumn` (Tasks 5–6); add `pinDirection` as an additive, non-boolean per-column enum read only when `pinnable` is true (Task 7) — all follow the per-column convention rather than table-level props |
| Existing per-feature boolean-opt-in convention (table-level) | `searchable`, `selectable`, `serverSide` on `ITable` | Establishes the "one flat boolean per feature" shape for table-level toggles | `filterable`/`columnLayoutToggle` (Task 13) and all five selection refinements (Tasks 8–12) follow this same flat-boolean shape, matching the spike's Option B decision for V2-19 |
| Shift-key access from a checkbox click | **Gap found, not an existing pattern** — `bds-checkbox`'s public `bdsChange` emits `CheckboxChangeDetail` (a boolean), never the originating `MouseEvent`; its internal `handleClick` does not forward `shiftKey` | `bds-table` already delegates native events on `_tableWrapperEl` via capture-phase listeners for the overflow tooltip (`handleOverflowMouseEnter`/`handleOverflowMouseLeave`, added `{ capture: true }` in `componentDidLoad`) | Reuse that exact delegation pattern: add one more capture-phase `click`/`keydown` listener on `_tableWrapperEl` to stash `shiftKey` in a private field *before* `bdsChange` fires (Task 10), instead of modifying `bds-checkbox` |
| Test scaffolding | `setupMutationObserverMock()`, `setupResizeObserverMock()`, `assertExists()`, `suppressConsoleError()` (all already imported from `@/utils` in existing specs) | Every new spec file needs the same mocks the existing ones already use for `MutationObserver`/`ResizeObserver` | Reuse verbatim in every new spec file introduced by this plan; do not write new mocks |

---

## Task 1: `bds-table` — extract shared cell-content cache

**Status:** ✅ done
**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** none (pure refactor of already-shipped v3 code; sequenced first so Tasks 2 and 3 can both write into it)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/utils/CellContentCache.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.utils.spec.ts` (modify — new direct tests of `CellContentCache`)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.formatter.spec.ts` (modify — confirm no behavior change)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify — no visible behavior change)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify — no visible behavior change)

**Context:** This task has **no user-visible behavior change** — it is a pure internal refactor, done first so both Task 2 (master-detail slot) and Task 3 (`<template slot="cell">`) can write into the same cache `formatter` already uses, rather than each building a separate one. The existing `_formatterNodes: Map<string, { row: RowData; node: Node }>`, keyed `` `${col.colKey}:${rowId}` ``, with its `cached.row === row` identity guard in `applyCellFormatter`, is extracted verbatim into a standalone class that accepts an arbitrary string key (so Task 2 can key its entries `detail:${rowId}` in the same map without collision). Because there is no new visible behavior, the doc/story files receive no content changes in this task — they are listed only because the task template requires a documentation pass; the `@documentation-subagent` step for this task is a no-op confirmation that nothing in the public docs needs updating (record this explicitly rather than silently skipping the executor step).

**Documentation:** No new story or MDX content — the `@documentation-subagent` step confirms `bds-table.mdx` and `bds-table.stories.ts` require zero changes and records that confirmation in the task's completion notes.

**Acceptance criteria:**

- New `CellContentCache` class in `utils/CellContentCache.ts`:
  ```typescript
  export class CellContentCache {
    private readonly nodes = new Map<string, { row: RowData; node: Node }>();
    get(key: string, row: RowData): Node | undefined { /* identity-guarded */ }
    set(key: string, row: RowData, node: Node): void { /* ... */ }
    clear(): void { /* ... */ }
  }
  ```
- `bds-table.tsx` replaces `private readonly _formatterNodes = new Map(...)` with `private readonly _cellContentCache = new CellContentCache()`.
- `applyCellFormatter` reads/writes through `_cellContentCache.get`/`.set` instead of touching a `Map` directly; behavior (including the identity guard) is unchanged.
- `onDataChange`/`onRowsChange` call `this._cellContentCache.clear()` instead of `_formatterNodes.clear()`.
- All existing `bds-table.formatter.spec.ts` assertions pass unmodified (aside from any import/reference renames needed for the refactor) — this task must not change formatter behavior.

**Unit tests to cover:**

- `CellContentCache.get` returns `undefined` for an unset key.
- `CellContentCache.set` then `get` with the *same* row reference returns the cached node.
- `CellContentCache.get` with a *different* row reference at the same key misses (identity guard), matching today's `cached.row === row` behavior.
- Two different key prefixes (e.g. `formatter-key:1` and `detail:1`) coexist in the same cache instance without collision.
- `CellContentCache.clear()` empties all entries.
- Full existing formatter suite (`bds-table.formatter.spec.ts`) still passes with zero behavior changes.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render the existing formatter-driven "Status" pill column playground scenario used in v3.
- Validate:
  - [ ] Given the existing formatter-driven pill column, when the table re-renders (e.g. after a row selection), then the pill content is unchanged and does not flash/re-clone — confirming the extraction preserved the identity-guard optimization exactly.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "refactor(bds-table): EOA-16000 extract shared cell-content cache from formatter path"`

---

## Task 2: `bds-table` — row expand/collapse via master-detail slot

**Status:** ✅ done — implementation, unit tests (`bds-table.expand.spec.ts`, 278/278 passing), docs, and manual QA (web components + React + Vue parity) all verified. Includes a hit-target follow-up fix (expand-toggle enlarged to 24×24px) landed after the original manual-test pass.
**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 1 (writes row-detail content through the shared `CellContentCache`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — detail-row and expand-toggle styling)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify — `BdsExpandEventDetail`; `RowData` is unchanged, no `children` field needed)
- `packages/boreal-web-components/src/styles/_interactions.scss` (modify — new `bds-transition-collapse` mixin, reused by a future collapse/accordion component)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.expand.spec.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.virtual.spec.ts` (modify — remeasure regression)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:**

- **Re-scoped mid-planning, deliberately:** the ticket's original text ("tree-shaped `RowData` with a `children?: RowData[]` field") described nested child rows. A provided design reference instead showed a single full-width detail panel per row (checkbox + chevron + column cells on top, one full-width "Slot" region below when expanded) — a master-detail pattern, not a tree. This task implements that: `RowData` stays `Record<string, unknown>`, entirely unchanged. This simplifies the feature substantially: there is no cascading-vs-independent selection question (the detail panel is not a row in `bds-table`'s selection model at all), no tree-aware sort requirement, and no indentation/depth CSS.
- A `<template slot="row-detail">` declared once as a **direct child of `<bds-table>` itself** (not per-column, not per-row) is the row-detail content source, read via the same "read a light-DOM child once, cache by key" pattern as `footerNode()`: a private `rowDetailTemplate` getter — `Array.from(this.el.children).find(child => child.tagName === 'TEMPLATE' && child.getAttribute('slot') === 'row-detail')`.
- `hasRowDetail` getter is `true` when `rowDetailTemplate` is present. When true, **every** row renders an expand/collapse toggle — there is no per-row gating in this task's scope (e.g. no `isRowExpandable`); if a future need arises to exclude specific rows from expansion, that is a small, separately-scoped follow-up, not built speculatively here.
- Expanding a row clones `rowDetailTemplate.content` through the shared `_cellContentCache` from Task 1, keyed `` `detail:${rowId}` ``, with the same row-identity guard already proven correct for the formatter path — reusing the exact mechanism Task 3 also uses for per-cell templates, rather than inventing a third caching path. The cloned fragment's root element receives the row's data stamped as `data-*` attributes, the same convention Task 3 uses, so consumer markup/listeners inside the detail template can read `element.dataset`. **In addition, `bdsExpand`'s event detail carries the full `row` object** (see event shape below) — MUI's own reference example (`Collapse` + nested `<Table>` built from `row.history`, a nested array field) can't be reproduced through `data-*` attributes alone, since HTML attributes can't carry array/object values. Passing the full row lets a consumer's own `bdsExpand` listener build and populate arbitrarily nested content (e.g. a mini sub-table) into the already-cloned template region themselves, without `bds-table` needing any new "nested renderable data" concept.
- **Rendering:** when a row is expanded, a `<tr class="bds-table__tr-detail">` renders immediately after that row's own `<tr>`, containing one `<td colSpan={totalColumnCount}>` (leaf columns + checkbox column if `selectable` + this task's own expand-toggle column) wrapping the cloned content.
- **Expand toggle isolation (locked decision):** the toggle is a dedicated `<td class="bds-table__td-expand">`, rendered only when `hasRowDetail` is true, positioned after the checkbox column (if `selectable`) and before the first data column. Its `<button>`'s `onClick` calls only `toggleExpand(rowId)` — it must never call `handleRowSelect`, verified via MUI's own bug history (`mui-x#3945`, where an identical leak — clicking a master-detail expand icon also selecting the row — was treated as a bug and fixed) rather than left to `rowClickSelects` (Task 12) to guard.
- **Chevron rotation:** reuses `_form-field-elements.scss`'s existing dropdown-chevron pattern verbatim — `@include bds-transition-action` (already transitions `transform`, `_interactions.scss:40-45`) on the toggle icon, plus `[aria-expanded='true'] .bds-table__td-expand-icon { transform: rotate(180deg); }` mirroring `_form-field-elements.scss:54-58`'s `&[aria-expanded='true'] ~ .#{$prefix}__actions .#{$prefix}__action--icon-right` rule. No new mixin needed for the chevron itself.
- **Detail-panel reveal transition (non-virtualized mode only — confirmed):** in non-`virtual` mode, the detail `<tr>` stays mounted once a row is first expanded and toggles a `.is-expanded` class rather than being added/removed from the DOM outright, so the reveal can animate via a new `@mixin bds-transition-collapse` added to `_interactions.scss` (the `grid-template-rows: 0fr → 1fr` technique — no JS height measurement, works for arbitrary/dynamic content height, and is written generically enough for a future `bds-collapse`/accordion component to reuse verbatim):
  ```scss
  @mixin bds-transition-collapse {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.3s ease;

    > * {
      overflow: hidden;
    }

    &.is-expanded {
      grid-template-rows: 1fr;
    }
  }
  ```
  This wraps the content *inside* the `<td>` (a `<div>`), not the `<tr>`/`<td>` themselves, since CSS Grid track-sizing transitions don't apply to table-display elements directly. **In `virtual` mode, this task keeps the current instant show/hide** (detail `<tr>` added/removed outright as a synthetic virtualizer entry, no animation) — animating height while the virtualizer concurrently tracks that row's scroll position is a materially harder problem (continuous remeasurement mid-transition, not a single post-toggle `measureElement` call), and was explicitly scoped out rather than attempted speculatively. If a future ticket wants animated reveal under `virtual` too, it needs its own design pass.
- **Virtualizer remeasure:** since there's no tree to flatten, the existing flat row list is unaffected in shape — only each expanded row now conceptually occupies an extra slot for its detail `<tr>`. Add a `visibleFlatRows` getter that maps `sortedData` and inserts a synthetic `{ type: 'detail', rowId }` entry immediately after any `{ type: 'row', row }` entry whose row is expanded; `initVirtualizer`'s `count` and `syncVirtualizerOptions` read `visibleFlatRows.length` instead of `sortedData.length`. `toggleExpand(rowId)` updates `expandedRowIds` (changing `visibleFlatRows`), then explicitly calls `this.virtualizer?.measureElement(rowEl)` for the **toggled row's own** `<tr>` (tracked via a `_rowElRefs: Map<string, HTMLTableRowElement>` populated by the existing `ref` callback in `renderRow`), since the toggle can change that row's own rendered height too (e.g. chevron rotation reflow). The new detail `<tr>` itself is measured for free through the existing `renderVirtualRows` ref-based `measureElement` call, same as any other row entering the flat list. This remeasure path is unchanged by the animated-reveal decision above, since `virtual` mode keeps the instant show/hide.
- **Selection requires zero changes:** because the detail panel is not a row in `bds-table`'s data/selection model, `selectedRowIds`, `handleSelectAll()`, and `getSelectedRows()` need no modification in this task. Document in `bds-table.mdx` that content inside the detail slot is entirely consumer-owned, including any selection UI a consumer chooses to build inside it — `bds-table` has no awareness of it and does not count it toward `getSelectedRows()`.
- Verify an existing chevron/expand icon is available in the icon set before wiring it (mirroring Task 5's own "verify the glyph exists" note) — reuse an existing icon (e.g. one already used by `bds-select`/`bds-accordion`-style disclosure affordances) rather than assuming one exists.

**Documentation:** New story `Row Detail` (or `Expandable Rows`) in `bds-table.stories.ts`, deliberately modeled on the MUI Collapsible Table reference reviewed during planning: each row carries a nested array field (e.g. `row.history`, an order's line-items or a customer's transaction history), and the story's own `bdsExpand` listener reads `event.detail.row.history` to build and populate a small nested `<table>` inside the cloned `<template slot="row-detail">` region — demonstrating the full-row-payload pattern end-to-end, not just flat `data-*` stamped fields. Include a variant with and without `virtual`+`maxHeight`. `bds-table.mdx` gets a new "Row expand/collapse" section documenting the `slot="row-detail"` contract, the `bdsExpand` event shape (including the full `row` field and why it exists — nested/array fields can't be expressed as `data-*` attributes), an explicit callout that this pattern is *master-detail only* (one detail panel per row) and does **not** support MUI/simple-table-style recursive tree row grouping, and the existing note that detail-slot content is entirely consumer-owned and never counted toward `getSelectedRows()`. Its "Current limitations" row #1 is removed per the acceptance criteria below.

**Acceptance criteria:**

| Prop/State/Event | Type | Default | Description |
|---|---|---|---|
| `expandedRowIds` (State, private) | `Set<string>` | `new Set()` | Currently expanded row IDs |
| `bdsExpand` (Event) | `EventEmitter<{ rowId: string; expanded: boolean; row: RowData }>` | — | Emitted on every toggle, carrying the full row so consumers can populate nested/complex detail content (e.g. a sub-table from a nested array field) themselves |

- A `<template slot="row-detail">` declared on `<bds-table>` enables an expand/collapse toggle on every row; omitting it renders the table exactly as today, with no toggle column at all (zero visual change for existing consumers).
- Clicking the toggle expands/collapses that row's detail panel (a full-width `<tr class="bds-table__tr-detail">` immediately below it), emits `bdsExpand` (with `rowId`, `expanded`, and the full `row`), and never mutates `selectedRowIds`.
- The detail panel's cloned content is stamped with the row's data via `data-*` attributes, cached identically to Task 3's per-cell templates, so virtualized row recycling never leaks stale detail content onto the wrong row.
- In non-`virtual` mode, the detail `<tr>` stays mounted after first expansion and animates open/close via the new `bds-transition-collapse` mixin (`.is-expanded` class toggling `grid-template-rows`); in `virtual` mode, the detail `<tr>` is added/removed instantly as a synthetic virtualizer entry, no animation.
- Under `virtual`, expanding/collapsing correctly adjusts the virtualizer's `count` (accounting for the synthetic detail entry) and remeasures with no visible layout jump.
- `bds-table.mdx`'s "Current limitations" row #1 is removed and replaced with documentation of `slot="row-detail"` usage.

**Unit tests to cover:**

- No `template[slot="row-detail"]` present: no expand-toggle column renders at all (regression guard).
- With the template present: every row renders a toggle button.
- Clicking the toggle expands/collapses, renders/hides the detail `<tr>` immediately after the row, and emits `bdsExpand` with the correct `{ rowId, expanded, row }` (including the full row object, not just its `id`).
- Clicking the toggle button does not call `handleRowSelect` / does not change `selectedRowIds` (regression guard, including when `selectable` is also `true`).
- The detail row's `<td colSpan>` matches the actual total rendered column count (varies with `selectable`).
- Detail content is cloned per row via the shared cache, keyed `detail:${rowId}`, with correct row-identity-guard behavior (mirrors Task 1/3's cache tests).
- Non-virtualized mode: expanding a row adds the `.is-expanded` class (triggering the `bds-transition-collapse` reveal) rather than an instant DOM insert; the detail `<tr>` remains mounted after collapse (class removed, not the element).
- Virtualized mode: expanding a row updates the virtualizer's `count` by one (the synthetic detail entry, added/removed instantly, no `.is-expanded` class involved); the toggled row's `measureElement` is called on toggle (spy-asserted); scrolling/recycling never leaks one row's detail content into another's.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with a `<template slot="row-detail">` (e.g. an order's line-items) both with and without `virtual`+`maxHeight`.
- Validate:
  - [ ] Given the row-detail template in non-virtualized mode, when a row's toggle is clicked, then the detail panel smoothly animates open (no snap), showing the correct row's data with no layout jump.
  - [ ] Given the row-detail template in `virtual` mode, when a row's toggle is clicked, then the detail panel appears instantly (no animation), matching the documented virtual-mode exception.
  - [ ] Given `virtual` is enabled, when a row near the visible edge is expanded, then no rows overlap or jump after the toggle.
  - [ ] Given `selectable` is also enabled, when the toggle button is clicked (not the checkbox), then no row selection state changes.
  - [ ] Given the detail template contains its own interactive content (e.g. a mini checklist the consumer built), when interacted with, then `bds-table`'s own selection state is completely unaffected.
  - [ ] Given a `bdsExpand` listener reading `event.detail.row` (including a nested array field), when a row expands, then the listener can populate a nested sub-table into the detail region using that data (confirming the full-row event payload works end-to-end).
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add row expand/collapse via master-detail slot"`

---

## Task 3: `bds-table-column` — custom cell content via `<template slot="cell">`

**Status:** ✅ done — implementation, unit tests (`bds-table.template-cell.spec.ts`, 9/9 passing incl. a late-template-content regression suite), docs (`CustomCellContent`/`CustomCellContentFormatterPrecedence` stories + MDX section), and manual QA (web components + React + Vue parity) all verified. A real bug was found and root-cause-fixed mid-task: `applyCellTemplate` raced React's `useEffect`-driven late population of `template.content` and silently gave up with no retry; fixed via a one-shot, per-column-deduped `MutationObserver` on `template.content` (`watchForLateTemplateContent`) that triggers `forceUpdate` once content lands. Confirmed deterministic across 5 fresh React reloads.

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 1 (writes into `CellContentCache`, does not build a second cache)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` (modify — JSDoc only, no behavior change)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.template-cell.spec.ts` (new)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** Reuses the same "read a light-DOM child once, cache by key, project into rendered output" pattern `footerNode()`/`_footerNodes` already established for `slot="footer"` — add a parallel `templateNode(col)` that finds `Array.from(col.children).find(child => child.getAttribute('slot') === 'cell' && child.tagName === 'TEMPLATE')` (not `:scope`, confirmed broken in `@stencil/core/mock-doc` during v3). `formatter` takes precedence when both are present on the same column (per the spike's recommendation) — log a `Logger.warn` if a column defines both, since it signals developer confusion, not a supported combination.

**Documentation:** New story `Custom Cell Content` (or a new variant on the existing formatter story) demonstrating `<template slot="cell">` with interactive markup reading `data-*` attributes, plus a variant showing the `formatter`-takes-precedence warning path. `bds-table.mdx` gets a new "Custom cell content via template" section next to the existing `formatter` documentation, stating the precedence rule explicitly.

**Acceptance criteria:**

- `<bds-table-column>` accepts an optional `<template slot="cell">` direct child, additive to the existing `formatter` prop.
- `renderCell(col, row)` precedence: `formatter` (existing path, unchanged) → else `templateNode(col)` present → clone `tpl.content` per row and inject via the **shared** `_cellContentCache` from Task 1, keyed identically (`` `${col.colKey}:${rowId}` ``) with the same row-identity guard → else existing plain-text rendering (unchanged).
- The cloned fragment's root element receives the row's data stamped as `data-*` attributes (e.g. `data-row-id`, and one `data-<colKey>` per row field) so consumer-authored markup/listeners inside the template can read row context via `element.dataset`.
- A column defining both `formatter` and a `<template slot="cell">` uses `formatter` and logs one `Logger.warn` per column (not per row) noting the template will be ignored.
- Virtualized row recycling: because content is written through the same identity-guarded cache as `formatter` (and as Task 2's detail panel), a `<tr>` recycled to a different row misses the cache and re-clones correctly — no additional guard code needed (verified by test, not just asserted).

**Unit tests to cover:**

- A column with only a `<template slot="cell">` renders the cloned template content inside the cell, per row.
- The clone's root element carries `data-row-id` (and other stamped `data-*` fields) matching the row.
- A column with both `formatter` and a template uses the formatter and logs exactly one warning.
- Under virtualized scroll, recycling a `<tr>` to a different row re-clones the template content (not stale content from the previous row) — same regression style as the existing formatter identity-guard test.
- A column with neither `formatter` nor a template still renders plain text via `toCellString`, unaffected.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; add a column with `<template slot="cell"><span class="badge" data-row-id></span></template>` styled/scripted to read `data-*` values.
- Validate:
  - [ ] Given a templated column, when the table renders, then each cell shows the cloned template content correctly reflecting that row's data.
  - [ ] Given `virtual` is enabled with a scrollable dataset, when scrolling recycles rows, then no cell shows another row's stale templated content.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add template slot=cell custom cell content"`

---

## Task 4: `bds-table-column-group` — column grouping

**Status:** ✅ done — implementation, unit tests (`bds-table-column-group.basics.spec.ts` + `bds-table.grouping.spec.ts`, 2574/2574 suite-wide passing), docs (`Column grouping` anatomy section, `Grouped headers` preview story), and manual QA (web components + React + Vue parity) all verified. Scope grew slightly beyond the original plan: added an opt-in `info` prop (tooltip via `bds-typography variant="label"`) to `bds-table-column-group`, mirroring `bds-table-column.info`/`bds-card-header.info`. A real bug was found and root-cause-fixed mid-task: `table-layout: fixed` only reads column widths from a table's first `<tr>` (CSS 2.1 §17.5.2.1), so once grouping added a second `<thead>` row, every leaf column's `width` was silently ignored and pinned-column offsets broke; fixed via an unconditional `<colgroup>`/`<col>` per column (`<col>` is exempt from the first-row restriction).

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** none
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/bds-table-column-group.tsx` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/types/ITableColumnGroup.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column-group/__test__/bds-table-column-group.basics.spec.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — group header cell styling)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.grouping.spec.ts` (new)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:**

- `bds-table-column-group` is configuration-only, matching `bds-table-column`'s own pattern: `@Prop() readonly label: string = ''`, renders `<Host style={{ display: 'none' }} />`. Groups are **two-level only** in this ticket's scope — a group contains `bds-table-column` leaves directly; nested groups are not supported.
- `bds-table.tsx`'s column discovery switches from the flat `querySelectorAll('bds-table-column')` to a recursive walk of `Array.from(this.el.children)`, producing both: a `columnTree` (ordered list of `bds-table-column | bds-table-column-group` direct children, used only by header rendering) and the existing flattened `columns: HTMLBdsTableColumnElement[]` (leaf-only, unchanged shape — every other consumer of `this.columns` — cells, sort, footer, pin-offsets, skeleton — is unaffected).
- The `MutationObserver` in `componentDidLoad` upgrades from `{ childList: true }` to `{ childList: true, subtree: true }`, since shallow mutation detection is blind to a `<bds-table-column>` being added/removed *inside* a `bds-table-column-group`.
- **Header rendering (corrected against Figma nodes [53:38140](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29?node-id=53-38140) [grouped] and [53:42699](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29?node-id=53-42699) [ungrouped baseline]):** the design does **not** use `rowSpan={2}` for ungrouped columns. In the grouped reference (a 4-col group, a 2-col group, 4 *ungrouped* columns positioned between them, then a 2-col group — groups can be interspersed with plain columns, not just trailing), row 1 shows a group-label bar only over the grouped ranges — nothing at all above the ungrouped columns, not a merged cell. Row 2 shows every column's own label at identical vertical alignment, including the ungrouped ones — confirming their label lives in row 2, not centered across both rows. When any group is present (`hasGroups`), `<thead>` renders two `<tr>`s: row 1 has one `<th colSpan={leafCount}>` per group, plus an **empty, borderless filler `<th>`** (no label, no background) for every ungrouped top-level column and for the `selectable` checkbox column if present; row 2 has a normal leaf `<th>` for **every** column, grouped or not — this is simpler than the original `rowSpan` design, not more complex, since every row-2 cell is now treated identically regardless of grouping.
- **Width constraint (locked decision):** group header `<th>`s must never carry an explicit `width` — only leaf-row `<th>`s do, since `table-layout: fixed` only reads width from cells that actually appear in the sizing row. This must be an explicit, commented constraint in the header-group renderer, not an implicit omission.
- `colSpan` per group = count of immediate `bds-table-column` children (two-level only, no recursive descendant counting needed).

**Documentation:** New story `Grouped Columns` in `bds-table.stories.ts` showing a mix of one `bds-table-column-group` (2+ leaf columns) and ungrouped columns, some pinnable/sortable within the group. `bds-table.mdx` gets a new "Column grouping" section documenting `bds-table-column-group`'s `label` prop and the two-level-only constraint; its "Current limitations" row for grouping is removed.

**Acceptance criteria:**

| Element | Prop | Type | Default | Description |
|---|---|---|---|---|
| `bds-table-column-group` | `label` | `string` | `''` | Group header text |

- `<bds-table-column-group label="...">` wrapping one or more `<bds-table-column>` renders a correctly `colSpan`'d group header above the wrapped columns' own leaf headers, in a two-row `<thead>`.
- Ungrouped top-level columns (and the `selectable` checkbox column) render an **empty, borderless filler `<th>` in row 1** and their normal label `<th>` in row 2 whenever at least one group exists elsewhere in the table — never a `rowSpan={2}` merged cell (confirmed against the Figma reference: ungrouped labels sit at row 2's baseline, not vertically centered across both rows).
- No group `<th>` ever has an inline `width` style; only leaf `<th>`s do.
- Adding/removing a `bds-table-column` inside an existing `bds-table-column-group` after initial mount is detected (via the upgraded `subtree: true` observer) and re-renders correctly.
- Sorting, pinning, formatter/template cells, and footer rendering are all unaffected by grouping (leaf `columns` array is unchanged in shape).
- `bds-table.mdx`'s "Current limitations" row for column grouping is removed.

**Unit tests to cover:**

- A table with one group + two ungrouped columns renders a two-row `<thead>` with a correctly `colSpan`'d group `<th>`, empty filler `<th>`s in row 1 above the ungrouped columns (not `rowSpan`), and a leaf `<th>` for every column in row 2.
- A group positioned between two ungrouped columns (not just trailing) renders correctly — groups and plain columns can be interspersed in any order, matching the Figma reference's 4-group / 2-group / 4-ungrouped / 2-group layout.
- The group `<th>` has no `width` style even when its child columns individually specify `width`.
- Adding a `bds-table-column` to a `bds-table-column-group` after mount (simulating the `MutationObserver` firing) is picked up and re-renders.
- `columns` (flat leaf array) is unaffected by grouping — sort/pin/footer/formatter tests from other spec files continue to pass with a grouped table fixture.
- A table with zero groups renders the original single-row `<thead>` unchanged (regression guard).

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with a mix of one `bds-table-column-group` (2 leaf columns) and 2 ungrouped columns, some pinnable/sortable.
- Validate:
  - [ ] Given the grouped table, when rendered, then the group header correctly spans its two leaf columns, and ungrouped columns show an empty row-1 cell with their label sitting at row 2's baseline — vertically aligned with every other column's row-2 label, not centered across both rows.
  - [ ] Given a pinned column exists inside a group, when scrolled horizontally, then its offset still computes correctly across the two-row header.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add bds-table-column-group for grouped column headers"`

---

## Task 5: `bds-table` — column drag/drop reorder

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 4 (must render header cells consistently whether or not groups exist)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — reorder-handle styling, drop-target highlight)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify — `BdsColumnReorderEventDetail`)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` (modify — `reorderable` prop)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/types/ITableColumn.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/__test__/bds-table-column.basics.spec.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.reorder.spec.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.pin-offsets.spec.ts` (modify — reorder+pin regression)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:**

- **Design corrected against two verified sources, not the originally-cited AG Grid/Fluent UI precedent:** (1) the Figma `_Header` component (node [2:47879](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29?node-id=2-47879)) defines a single `buttonReorder` boolean that renders exactly one icon, layer-named "Order," glyph `chevron-up-down` — never two Move-left/right buttons; (2) this codebase already ships an equivalent pattern on `bds-card-header.tsx` (`reorder: boolean` prop, `bds-icon-six-dots` glyph, `role="button"`/`tabIndex`/`KeyboardController`-driven `Enter`/`Space`, native `draggable` armed only for the duration of a press gesture via the `bdsReorderCard` event). `bds-table`'s reorder handle now mirrors `bds-card-header`'s exact shape rather than inventing a new one, with one deliberate addition (see below) since `bds-card-header` itself has no solved keyboard-move mechanism — its `Enter`/`Space` path only re-arms `draggable`, it doesn't move anything, because `bds-card` delegates all actual reordering to consumer script. `bds-table` can't delegate that way — it owns `columnOrder` itself — so this gap has to be closed here, not copied as-is.
- New per-column opt-in `@Prop() readonly reorderable: boolean = false` on `bds-table-column` (matching the existing `sortable`/`pinnable` per-column boolean convention rather than a table-level flag).
- `@State() private columnOrder: string[] = []`, initialized from `this.columns.map(c => c.colKey)` in `componentDidLoad`. Add an `orderedColumns` getter that maps `columnOrder` back to live `HTMLBdsTableColumnElement`s and appends any column not yet present in `columnOrder` (self-healing against dynamically added/removed columns). `renderHeader`, `renderRow`, `renderFooterCell`, and `skeletonColumns` all iterate `orderedColumns` instead of `this.columns` directly (`this.columns.length` — used for `colSpan` math — is unaffected by order).
- **Reorder handle — single icon, always visible, matching `bds-card-header` (locked decision, revised):** each reorderable `<th>` renders exactly one `<i class="bds-table__reorder-icon bds-icon-six-dots" role="button" tabIndex={0}>` next to the sort/pin action icons in `${PREFIX}__th-actions` — no separate Move-left/Move-right buttons. Visibility is gated by `reorderable` alone (`visibility: hidden` when not reorderable, matching `bds-card-header`'s own show/hide convention), **not** by hover — a hover-only reveal would make the handle undiscoverable on touch devices, which have no hover state at all; this differs deliberately from Task 6's resize handle, which is a transient per-interaction affordance rather than a persistent structural control.
- **Native DnD, press-scoped arming (revised to match `bds-card-header`'s pattern):** the `<th>` itself is **not** unconditionally `draggable` whenever `reorderable`. Instead, `onMouseDown` on the six-dot icon sets `draggable = true` on the parent `<th>` (mirroring `bds-card-header`'s `bdsReorderCard`-driven `card.draggable = true`/`false` arming exactly), and it's reset to `false` on `dragend`/`drop`. This avoids accidentally arming a drag from clicking anywhere else in the header cell (e.g. its sort/pin icons or title text) — a precision improvement over unconditionally-draggable `<th>`s. `handleDragStart` sets `e.dataTransfer.setData('text/plain', col.colKey)` + `effectAllowed = 'move'`; `handleDragOver` calls `e.preventDefault()` (required to allow a drop) and may add a drop-target highlight class; `handleDrop` reads the source `colKey` from `dataTransfer`, computes the new `columnOrder` with the source moved to the target's position, and emits `bdsColumnReorder: EventEmitter<{ order: string[] }>` with the **full** column order (including non-reorderable/pinned columns).
- **Keyboard — `Enter`/`Space` wiring reused from `bds-card-header`, `ArrowLeft`/`ArrowRight` added as new behavior (locked decision):** the six-dot icon is wired via the same `KeyboardController` utility `bds-card-header` already uses. `Enter`/`Space` on the focused icon are kept for consistency (announce/confirm interaction, no-op beyond that here since there's nothing to "arm" further) but the actual move is driven by `ArrowLeft`/`ArrowRight` on the same focused element, swapping the column with its adjacent reorderable neighbor in `columnOrder` and emitting `bdsColumnReorder` — same event, same payload shape, as the native-drop path. This is new behavior beyond what `bds-card-header` does today, since nothing in this codebase (or AG Grid, or Fluent UI, per the earlier research) has a solved keyboard-move mechanism to copy; `bds-table` can close this gap because, unlike `bds-card`, it owns the list being reordered and can execute a well-defined move immediately, without needing a consumer script in between.
- **Pinned columns excluded from drag targets (locked decision, unchanged):** `onDragOver`/`onDrop` handlers (and `ArrowLeft`/`ArrowRight` moves) are only enabled for non-pinned, `reorderable` `<th>`s, so a pinned column's `<th>` is never a valid drop target either. This exclusion must read `col.pinnable` **regardless of `pinDirection`** (Task 7), so right-pinned columns (once that task lands) are excluded too — confirm during implementation rather than assuming it falls out for free.
- **Known UX note, not a blocker:** `draggable="true"` (while armed) disables normal text selection within the `<th>` (Alt+drag restores it) — document as a minor known behavior.
- **Cross-browser `<th>` + `position: sticky` interaction — flagged, not assumed safe:** no authoritative documentation confirms native `<th>`-specific DnD behaves identically across browsers combined with sticky-pinned columns. This task's manual-test step must include cross-browser verification (Chrome + Firefox + Safari), not just a single-browser pass.
- **Open interaction with Task 4 (grouping) — flagged for confirmation, not silently decided:** a `bds-table-column-group`'s `colSpan` is computed from its *light-DOM* children count/order, which `columnOrder` does not touch. Dragging a leaf column out of its group's DOM containment would desynchronize the group header's `colSpan` from the rendered leaf order underneath it. **Recommended default: grouped columns (any leaf that is a child of a `bds-table-column-group`) are excluded from `reorderable` drag targets, the same treatment as pinned columns** — only top-level (ungrouped) columns are reorderable in this ticket. Confirm this default during execution before building; reordering *within* a group needs its own design pass and should be a follow-up task, not absorbed silently here.
- **Future opportunity, not built now:** the six-dot handle's render markup + `KeyboardController` wiring + press-scoped `draggable` arming is structurally identical to `bds-card-header`'s own implementation. A future ticket could extract a shared `ReorderHandleController` (or similar) reusable by both components — deliberately not attempted in this ticket, since `bds-card-header` is an already-shipped, released component and touching it here would be scope creep on a `bds-table`-scoped plan. Building `bds-table`'s handle to mirror the existing shape now keeps that future extraction close to mechanical.

**Documentation:** New story `Reorderable Columns` in `bds-table.stories.ts` with 4+ `reorderable` columns (one pinned, one inside a `bds-table-column-group` if Task 4's default holds), demonstrating both native drag/drop and `ArrowLeft`/`ArrowRight` keyboard reordering; wire `bdsColumnReorder` to the Storybook Actions panel. `bds-table.mdx` gets a new "Column reorder" section documenting `reorderable`, the pinned/grouped exclusion, and the keyboard interaction; its "Current limitations" row for reorder is removed.

**Acceptance criteria:**

| Prop/Event | Type | Default | Description |
|---|---|---|---|
| `bds-table-column.reorderable` (Prop) | `boolean` | `false` | Opts the column into drag/drop + keyboard reordering via its six-dot handle |
| `bdsColumnReorder` (Event) | `EventEmitter<{ order: string[] }>` | — | Emitted after a successful drop or `ArrowLeft`/`ArrowRight` move, with the full new colKey order |

- Reorderable, non-pinned, non-grouped `<th>`s show exactly one `bds-icon-six-dots` handle (always visible when `reorderable`, never hover-gated) — no additional Move buttons.
- Pressing (mouse) the handle arms `draggable` on the `<th>` for the duration of that gesture only; dropping a dragged column onto another reorderable `<th>` reorders `columnOrder`, re-renders header/body/footer cells in the new order, and emits `bdsColumnReorder`; `draggable` resets to `false` on `dragend`/`drop`.
- Focusing the handle and pressing `ArrowLeft`/`ArrowRight` swaps the column with its adjacent reorderable neighbor and emits `bdsColumnReorder`, identical payload shape to the drop path.
- Pinned columns (either direction) and grouped-leaf columns are never draggable, never valid drop targets, and their handles (if rendered) do not respond to `ArrowLeft`/`ArrowRight`.
- Pin-offset computation (`updatePinnedColumnOffsets`) continues to compute correct offsets after a reorder, with no code change to that method itself.
- `bds-table.mdx`'s "Current limitations" row for column reorder is removed.

**Unit tests to cover:**

- A `reorderable` column renders exactly one `bds-icon-six-dots` handle, always visible (not hover-gated); a non-`reorderable` column renders none.
- `<th>` is not `draggable` until the handle receives `mousedown`; it becomes `draggable` at that point and resets to non-`draggable` on `dragend`.
- Simulated `dragstart`/`dragover`/`drop` between two reorderable columns updates render order and emits `bdsColumnReorder` with the correct full order.
- `ArrowLeft`/`ArrowRight` on a focused handle swap adjacent reorderable columns and emit `bdsColumnReorder`; boundary positions are no-ops (no event, no state change).
- `Enter`/`Space` on a focused handle do not error and do not change `columnOrder` (parity check against `bds-card-header`'s own `Enter`/`Space` handling, confirming it's retained but inert beyond arming).
- A pinned column never renders an armable handle, and dropping onto it is a no-op.
- Reorder + pinning together: after reordering, `updatePinnedColumnOffsets` still computes correct `left` offsets matching the new rendered order (regression test added to `bds-table.pin-offsets.spec.ts`).
- A dynamically added column (after initial `componentDidLoad`) appends to the end of `columnOrder` via the self-healing `orderedColumns` getter.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with 4+ `reorderable` columns, at least one pinned and (if Task 4's confirmed default holds) one inside a `bds-table-column-group`.
- Validate:
  - [ ] Given two reorderable columns, when one is dragged (via its six-dot handle) and dropped on the other, then column order updates correctly across header, body, and footer, and `bdsColumnReorder` fires with the correct order.
  - [ ] Given a reorderable column, when its handle is focused via Tab and `ArrowRight` is pressed repeatedly, then it moves one position at a time until reaching the boundary, where further presses are a no-op.
  - [ ] Given a touch device (or Chrome DevTools touch emulation), when no hover is available, then the six-dot handle is still visible and usable (confirms the always-visible, non-hover-gated decision).
  - [ ] Given a pinned column, when a drag is attempted over it, then it is not a valid drop target and pin offsets remain correct afterward.
  - [ ] Cross-browser check (Chrome, Firefox, Safari): drag reorder combined with a pinned `position: sticky` column behaves consistently in all three; note and file any divergence rather than assuming parity.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then native drag/drop and `ArrowLeft`/`ArrowRight` keyboard reordering behave identically to the web-components version — no framework-specific regression (React's synthetic event system in particular is worth double-checking against native `dragstart`/`dragover`/`drop`).

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add column drag/drop reorder via six-dot handle, mirroring bds-card-header"`

---

## Task 6: `bds-table` — column resizing

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 5 (renders columns via `orderedColumns`; resize handles attach to the same rendered `<th>`s)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — hover/focus-only resize handle)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify — `BdsColumnResizeEventDetail`)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` (modify — `resizable` prop)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/types/ITableColumn.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/__test__/bds-table-column.basics.spec.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.resize.spec.ts` (new)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.pin-offsets.spec.ts` (modify — resize+pin regression)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:**

- New per-column opt-in `@Prop() readonly resizable: boolean = false` on `bds-table-column`, same convention as `sortable`/`pinnable`/`reorderable`.
- `@State() private columnWidths: Record<string, string> = {}` stores an explicit CSS length per resized column's `colKey`; `renderTh` applies `columnWidths[col.colKey] ?? col.width` as the `<th>`'s `style.width` (falls back to the existing `col.width` prop when never resized).
- **Handle is hover/focus-only visible (locked decision):** a `<div class="bds-table__resize-handle" role="separator" aria-orientation="vertical" aria-valuenow={currentWidthPx} tabIndex={0}>` is appended as the last child of each `resizable` `<th>`, styled `opacity: 0` by default with `th:hover &, &:focus-visible { opacity: 1 }` in `bds-table.scss` — never always-rendered.
- **Interaction model — pointer drag + keyboard, using the `role="separator"` splitter pattern** (the de facto standard for resize handles, distinct from the DnD-reorder gap flagged in Task 5 — this one has an established accessible pattern): `onPointerDown` captures the pointer (`setPointerCapture`) and begins tracking `pointermove`/`pointerup`; `ArrowLeft`/`ArrowRight` on the focused handle adjust width by a fixed step (e.g. 8px); `Home` resets to the column's original `width`/auto.
- **Shared recompute path (locked decision, highest-risk item in this task):** during `pointermove`, do **not** call `updatePinnedColumnOffsets` directly on every event — that reproduces the exact per-frame layout-thrash Task 8/22b (v3) was built to prevent for virtualized scroll. Add `scheduleResizeRecompute()`, mirroring `scheduleVirtualRerender()`'s microtask-flag throttle shape exactly, which at most once per frame: (a) updates `columnWidths[colKey]` and (b) calls the **existing** `updatePinnedColumnOffsets(true)` — the same method the `ResizeObserver` already calls, not a second implementation of the offset-walk loop.
- On `pointerup`/keyboard commit, emit `bdsColumnResize: EventEmitter<{ colKey: string; width: string }>` once (not per intermediate `pointermove`).

**Documentation:** New story `Resizable Columns` in `bds-table.stories.ts` with a `resizable` + pinned column combination and a `virtual`+`maxHeight` variant; wire `bdsColumnResize` to the Storybook Actions panel. `bds-table.mdx` gets a new "Column resizing" section documenting `resizable`, the hover/focus-only handle behavior, and keyboard interaction (`ArrowLeft`/`ArrowRight`/`Home`); its "Current limitations" row for resizing is removed.

**Acceptance criteria:**

| Prop/Event | Type | Default | Description |
|---|---|---|---|
| `bds-table-column.resizable` (Prop) | `boolean` | `false` | Adds a hover/focus-visible resize handle to the column's right edge |
| `bdsColumnResize` (Event) | `EventEmitter<{ colKey: string; width: string }>` | — | Emitted once per completed resize (pointer release or keyboard commit) |

- A `resizable` column's `<th>` shows a resize handle only on hover or keyboard focus, never persistently visible.
- Dragging the handle (pointer) resizes the column live, throttled to at most one recompute per animation frame, sharing `updatePinnedColumnOffsets` — no second/competing offset-recompute path exists anywhere in the diff.
- `ArrowLeft`/`ArrowRight` on a focused handle resize the column by a fixed step; `Home` resets it.
- Pinned-column offsets remain correct throughout a resize drag (not just after it ends).
- `bdsColumnResize` fires exactly once per completed resize gesture with the correct `{ colKey, width }`.
- `bds-table.mdx`'s "Current limitations" row for column resizing is removed.

**Unit tests to cover:**

- A `resizable` column renders a resize handle; a non-`resizable` column does not.
- Simulated `pointerdown`→`pointermove`(×N)→`pointerup` resizes the column and calls `updatePinnedColumnOffsets` at most once per throttled frame, not once per `pointermove` (spy-count assertion).
- `bdsColumnResize` emits exactly once per gesture, with the final width.
- `ArrowLeft`/`ArrowRight`/`Home` keyboard interactions resize/reset correctly.
- Resize + pinning together: pin offsets remain correct after a resize (regression test added to `bds-table.pin-offsets.spec.ts`).
- The resize handle has no visible/opacity-1 state by default (class/attribute assertion; visual opacity itself is a manual-test concern).

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with a `resizable` + pinned column combination, and one under `virtual`+`maxHeight`.
- Validate:
  - [ ] Given a resizable column, when the mouse is elsewhere, then no resize handle is visible; when hovering or focusing the `<th>`, then it appears.
  - [ ] Given a drag-resize in progress, when a pinned column is present, then its `left` offset stays correct throughout the drag, not just after release.
  - [ ] Given `virtual` is enabled, when resizing a column while scrolled, then no visible layout thrash/jank occurs.
  - [ ] Keyboard: focus the handle via Tab, use ArrowLeft/ArrowRight to resize, Home to reset.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression (Pointer Events forwarding through React/Vue synthetic props is worth double-checking).

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add column resizing sharing the pin-offset recompute path"`

---

## Task 7: `bds-table-column` — right-edge column pinning

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 6 (shares the resize task's `ResizeObserver`-driven recompute callback; left- and right-pinned offset functions are invoked from the same observer callback)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — right-pinned `th`/`td` styles, left-edge divider mirrored)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` (modify — `pinDirection` prop)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/types/ITableColumn.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/__test__/bds-table-column.basics.spec.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.pin-offsets.spec.ts` (modify — right-side offset tests, combined left+right test)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:**

- **Added to this ticket's scope after a feasibility check**, having originally been flagged in the ticket's Open Questions as needing its own scoping pass. Because Tasks 5–6 already touch the drag-target predicate and the `ResizeObserver`-driven offset recompute, right-edge pinning's design is ~90% identical incremental work on already-open code paths rather than a second effort reopening stable code later.
- **Additive, non-breaking API (confirmed against six libraries — AG Grid, Vaadin, and `simple-table.com` use a per-column property; TanStack/Nuxt UI/MUI use a table-level `{left, right}` list; `bds-table`'s existing per-column shape makes the per-column model the natural fit):** keep `pinnable: boolean` exactly as-is; add a new `@Prop() readonly pinDirection: 'left' | 'right' = 'left'` on `bds-table-column`, read only when `pinnable` is true. Existing `pinnable` usage across the codebase's own tests is entirely unaffected. Boreal DS is pre-1.0 (`0.1.0-alpha.10`), so a breaking change (replacing `pinnable` with a `pinned` enum) would have been tolerable, but there is no functional benefit to taking one here for zero gain — additive was chosen over breaking specifically because it costs nothing extra in implementation complexity.
- New `updatePinnedColumnOffsetsRight()`, mirroring `updatePinnedColumnOffsets()`: walks `th[data-pinned-right]` in **right-to-left** DOM order, accumulates `offsetWidth`, sets `style.right` (not `style.left`) on both `<th>` and matching `<td>`. Reuses the identical per-colKey caching/guard shape as the existing method — two clearly named sibling methods (not one parameterized-by-direction function), since the direction-specific DOM-order walk is the part that differs, not the caching logic.
- The shared `ResizeObserver` callback (`setupResizeObserver()`) invokes both `updatePinnedColumnOffsets(true)` and `updatePinnedColumnOffsetsRight(true)` — one observer, two recompute passes, additive rather than a structural change to the resize-observation mechanism.
- Task 6's `scheduleResizeRecompute()` calls **both** offset functions regardless of which side the resized column belongs to — the cost of the unaffected side's recompute is a cheap DOM-order walk over a typically-small pinned set, and unconditionally calling both avoids branching complexity for negligible gain.
- CSS divider: the right-pinned group's divider renders on its own **left** edge (mirroring today's left-pinned group's divider on its right edge, via `bds-table.scss`'s existing `[data-pin-last]::after` pattern) — add a `data-pin-first` (or equivalent) attribute for the right-pinned group's leftmost cell.
- **Reorder exclusion (consistency with the Task 5 locked decision):** right-pinned columns are excluded from Task 5's drag targets identically to left-pinned columns — confirm during implementation that Task 5's `isPinned`/`col.pinnable` check already covers this regardless of `pinDirection`, rather than assuming it falls out for free.

**Documentation:** Extend the existing pinned-columns story (or add `Right-Edge Pinning`) in `bds-table.stories.ts` with one left-pinned and one right-pinned column shown simultaneously, plus a resizable + right-pinned combination. `bds-table.mdx`'s existing pinning section gets a `pinDirection` example and the deferred "right-edge pinning" open question from the ticket is marked resolved.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `bds-table-column.pinDirection` | `'left' \| 'right'` | `'left'` | Which edge a pinnable column anchors to; read only when `pinnable` is `true` |

- A column with `pinnable pinDirection="right"` renders pinned to the table's right edge via `style.right`, computed by `updatePinnedColumnOffsetsRight()`.
- Existing `pinnable` columns with no `pinDirection` specified continue to pin left, identical to today's behavior (regression guard — zero migration needed for existing consumers).
- A table with both left- and right-pinned columns simultaneously computes both offsets correctly and independently.
- The right-pinned group's divider renders on its left edge; the left-pinned group's divider is unchanged (still on its right edge).
- Right-pinned columns are excluded from Task 5's drag/reorder targets, identical treatment to left-pinned columns.
- Resizing a right-pinned column (Task 6) correctly triggers `updatePinnedColumnOffsetsRight()` recompute, sharing the same throttled recompute path as left-pinned resizing.
- `bds-table.mdx` documents `pinDirection` with an example; the ticket's deferred "right-edge pinning" open question is resolved.

**Unit tests to cover:**

- `pinDirection="right"` pins to the right edge with correct `style.right` values across 2+ right-pinned columns.
- Default (`pinDirection` unset) on a `pinnable` column still pins left (regression guard).
- Combined left+right pinned columns: both offsets compute correctly and independently in the same render.
- `ResizeObserver` callback invokes both offset functions (spy-count assertion).
- Right-pinned columns are excluded from drag targets (regression test alongside Task 5's existing left-pinned exclusion test).
- Resizing a right-pinned column triggers the right-side recompute correctly.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with one left-pinned and one right-pinned column, plus resizing/reorder enabled on non-pinned columns.
- Validate:
  - [ ] Given a right-pinned column, when scrolled horizontally, then it stays anchored to the right edge with a visible divider on its left edge.
  - [ ] Given both left- and right-pinned columns, when scrolled, then both remain correctly anchored simultaneously with no visual overlap.
  - [ ] Given a resizable, right-pinned column, when resized, then its offset and any other right-pinned columns' offsets remain correct throughout the drag.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add right-edge column pinning via pinDirection"`

---

## Task 8: `bds-table` — `selectAllPages`

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** none (first of the five independent selection-refinement tasks)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** **Re-polarized from the spike's original `pagedSelectAll`/`checkboxSelectionVisibleOnly` framing (default `false` = select-all spans the full dataset, MUI convention), which was flagged as a real default-behavior change against today's shipped v3 behavior.** Today, `handleSelectAll()`/`renderSelectAllTh()` both scope over `this.activeRows`, which in `rows` mode already resolves to only the *current page*. Naming this prop `selectAllPages` and defaulting it to `false` removes that risk entirely: default `false` means select-all stays page-scoped, byte-for-byte identical to today's shipped behavior with zero migration impact, and `true` opts a consumer into the more powerful cross-page select-all. This matches the opt-in/default-`false` convention every other prop in this plan follows.

**Documentation:** Extend the existing `rows`+`bds-pagination`+`selectable` story with a `selectAllPages` control toggle so both scopes are directly comparable in Storybook. `bds-table.mdx`'s selection section gets a new "Select-all scope" subsection documenting `selectAllPages` as an explicit opt-in for cross-page select-all, noting the default introduces no behavior change from today.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `selectAllPages` | `boolean` | `false` | When `true`, the header select-all checkbox spans every page of the dataset in `rows` mode; when `false` (default), it scopes to the currently visible page only (today's shipped behavior, unchanged) |

- New `selectAllScope` getter: `selectAllPages && this.isRowsMode ? this.rows : this.activeRows`.
- `handleSelectAll()` and `renderSelectAllTh()`'s `checked`/`indeterminate` computations both read from `selectAllScope` instead of `activeRows`.
- In `data` mode, behavior is unchanged (already full-dataset via `activeRows`).
- Default (`false`) is a pure regression guard — select-all continues to scope to the current page exactly as it does today, in every mode. `selectAllPages={true}` is required to opt into cross-page select-all in `rows` mode.

**Unit tests to cover:**

- Default (`false`) in `rows` mode: clicking select-all on page 1 selects only that page's rows — no behavior change from today (regression guard).
- `selectAllPages={true}` in `rows` mode: clicking select-all on page 1 selects rows from every page, not just the visible one.
- Header checkbox `checked`/`indeterminate` reflect the correct scope in both modes.
- `data` mode is unaffected by the prop either way (regression guard).

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `rows` (30+ rows) + `bds-pagination` (`items-per-page="10"`), `selectable`.
- Validate:
  - [ ] Given default props, when clicking the header checkbox on page 1, then only that page's 10 rows become selected (verify via `getSelectedRows()`) — matching today's shipped behavior exactly.
  - [ ] Given `selectAllPages`, when clicking the header checkbox on page 1, then all 30 rows become selected across every page.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add selectAllPages for cross-page select-all opt-in"`

---

## Task 9: `bds-table` — `rowSelectable`

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 8 (shares `selectAllScope`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Documentation:** Extend the `selectable` story with a `rowSelectable` example gating selection by a row field (e.g. `row.status !== 'locked'`), showing disabled checkboxes on non-selectable rows. `bds-table.mdx`'s selection section gets a new "Conditional row selectability" subsection documenting the `rowSelectable` predicate contract and its interaction with select-all.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `rowSelectable` | `(row: RowData) => boolean` | `undefined` | When set, gates per-row checkbox selectability |

- `renderSelectTd`: `const selectable = this.rowSelectable ? this.rowSelectable(row) : true;` — passes `disabled={!selectable}` to that row's `<bds-checkbox>`.
- `handleRowSelect` early-returns (no-op) for a row where `rowSelectable(row)` is `false`.
- `selectAllScope` (from Task 8) is additionally filtered through `rowSelectable` before computing the next `Set` and before computing `checked`/`indeterminate` counts, so non-selectable rows never get force-selected by "select all" and never count toward "all selected."

**Unit tests to cover:**

- A row where `rowSelectable` returns `false` renders its checkbox `disabled`.
- Clicking a disabled/non-selectable row's checkbox does not add it to `selectedRowIds`.
- Select-all skips non-selectable rows entirely (never added, excluded from the "all selected" count so the header checkbox can still show `checked` when every *selectable* row is selected).
- No `rowSelectable` prop set: all rows behave exactly as before (regression guard).

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `rowSelectable={row => row.status !== 'locked'}` against a dataset with some `locked` rows.
- Validate:
  - [ ] Given locked rows, when rendered, then their checkboxes are visibly disabled and unclickable.
  - [ ] Given a mix of locked/unlocked rows, when select-all is clicked, then only unlocked rows become selected, and the header checkbox shows fully checked (not indeterminate) once all unlocked rows are selected.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add rowSelectable for conditional row selectability"`

---

## Task 10: `bds-table` — shift+range selection

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 9 (range fill must respect `rowSelectable`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/utils/bds-table-utils.ts` (modify — range-index helper)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.utils.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** **Real technical gap found and must be worked around, not assumed away:** `bds-checkbox`'s public `bdsChange` event emits `CheckboxChangeDetail` (a boolean), never the originating `MouseEvent`/`KeyboardEvent` — its internal `handleClick` does not forward `shiftKey`. Rather than modify `bds-checkbox` (out of this ticket's scope), reuse the capture-phase event-delegation pattern `bds-table` already uses for the overflow tooltip: add one more capture-phase `click` and `keydown` listener on `_tableWrapperEl` that, when the event targets a `.bds-table__td-checkbox`, stashes `e.shiftKey` into a private `_pendingShiftKey` field *before* `bds-checkbox`'s own bubble-phase click handler runs (and therefore before `bdsChange`/`handleRowSelect` fire). `handleRowSelect` reads and clears `_pendingShiftKey` when deciding whether to do a range-select. Per the spike's explicit constraint, range computation must operate entirely on the data array (`this.isRowsMode ? this.rows : this.data`, never `this.visibleRows` alone) so it is correct for cross-page ranges and never queries the DOM — intermediate rows in a range may not be mounted at all under virtualization, so a DOM-based fill would silently break.

**Documentation:** Extend the `selectable` story with a play function (Storybook interaction test) demonstrating click row 2 → shift+click row 5 selecting the range; include a `rows`+pagination variant showing cross-page range selection. `bds-table.mdx`'s selection section gets a new "Shift+range selection" subsection documenting the anchor-row behavior and its interaction with `rowSelectable`.

**Acceptance criteria:**

| State | Type | Default | Description |
|---|---|---|---|
| `lastSelectedRowId` (State, private) | `string` | `''` | Anchor row ID for the next shift+click range |

- Shift+clicking a checkbox selects every row between `lastSelectedRowId` and the clicked row (inclusive), computed over the full data array (`rows` or `data`), never the DOM.
- Shift+Space on a focused, non-shift-clicked checkbox performs the same range-select using the same anchor.
- A normal (non-shift) click/Space updates `lastSelectedRowId` to the clicked row and performs the existing single-row toggle, unchanged.
- Range selection respects `rowSelectable` (Task 9) — non-selectable rows within the range are skipped, not force-selected.
- Select-all (header checkbox) resets `lastSelectedRowId` to `''` so a subsequent shift+click has a well-defined (empty → no-op) anchor rather than a stale one.
- Range selection works correctly across pages in `rows` mode (cross-page range), consistent with existing cross-page selection support.

**Unit tests to cover:**

- Click row 2, shift+click row 5: rows 2–5 all become selected.
- The same, in reverse order (click row 5, shift+click row 2): rows 2–5 all become selected (range direction-agnostic).
- A non-selectable row (per `rowSelectable`) inside the range is skipped, not selected.
- Shift+click with no prior `lastSelectedRowId` set (first-ever click) performs a normal single-row toggle, not a range.
- Select-all resets `lastSelectedRowId`.
- Cross-page range in `rows` mode: click a row on page 1, shift+click a row on page 2, all rows between (across both pages) become selected.
- The range computation never calls any DOM query method (`querySelector`/`querySelectorAll`) — asserted via a spy on those methods staying uncalled during the range-select code path.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `selectable` and, separately, with `rows`+pagination for the cross-page case.
- Validate:
  - [ ] Given rows 2 and 5, when row 2 is clicked then row 5 is shift+clicked, then rows 2–5 are all selected.
  - [ ] Given `rows` mode across two pages, when a row on page 1 is clicked and a row on page 2 is shift+clicked, then every row in between (spanning both pages) is selected.
  - [ ] Given a non-selectable row inside a shift+click range, then it remains unselected/disabled after the range-select.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression (shiftKey capture-phase delegation is worth double-checking against React/Vue synthetic event wiring).

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add shift+click range selection"`

---

## Task 11: `bds-table` — `persistSelection`

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** none (independent of Tasks 8–10; only touches `onDataChange`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** This is the server-side/`data`-mode equivalent of the cross-page selection persistence `rows` mode already gets for free. It gates only the `@Watch('data')`/`onDataChange` selection-clear — `onRowsChange` is untouched, since `rows` mode already has its own correct cross-page persistence design from v3 and does not need this prop.

**Documentation:** Extend the existing `data`+`serverSide` story with a `persistSelection` toggle and a simulated page-2 fetch button, so consumers can see selection surviving a full `data` replacement. `bds-table.mdx`'s server-side section gets a new "Selection persistence" subsection documenting `persistSelection` and its relationship to consumer-managed `selectedRows`.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `persistSelection` | `boolean` | `false` | When `true`, replacing `data` does not clear `selectedRowIds` for rows no longer present |

- `onDataChange()`'s existing `if (this.selectedRowIds.size > 0) { clear... }` becomes `if (!this.persistSelection && this.selectedRowIds.size > 0) { clear... }`.
- `onRowsChange()` is unchanged (this prop does not apply to `rows` mode).
- Default (`false`) preserves today's shipped behavior exactly (regression guard).

**Unit tests to cover:**

- Default (`false`): replacing `data` clears `selectedRowIds` (existing behavior, regression-guarded).
- `persistSelection={true}`: replacing `data` with a completely different page of rows does **not** clear `selectedRowIds`, even though none of the previously selected IDs exist in the new `data`.
- `onRowsChange` clearing behavior is unaffected by this prop either way.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `data`+`serverSide`+`persistSelection`, simulating a page-2 fetch that replaces `data` entirely.
- Validate:
  - [ ] Given rows selected on a simulated "page 1" `data` set, when `data` is replaced with a simulated "page 2" set and the consumer re-passes the previously selected IDs via `selectedRows`, then selection state is preserved rather than cleared by the table itself.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add persistSelection for server-side selection persistence"`

---

## Task 12: `bds-table` — `rowClickSelects`

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** Task 9 (row-click selection must respect `rowSelectable`), Task 2 (expand toggle isolation must hold regardless of this prop's value, per the locked decision)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.selection.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** **Renamed and re-polarized from the ticket's `disableRowSelectionOnClick`, which resolves the scope ambiguity the spike originally flagged.** The 2026-06-16 spike scoped the ticket's version as a no-op *reservation* ("no implementation change needed... becomes essential once formatter-rendered interactive elements are inside cells"), since v1/v2/v3 never added click-anywhere-in-row selection, and left implementing the real behavior as an open question for this ticket. Naming this prop positively — `rowClickSelects`, default `false` — settles that question by construction: default `false` means row-click selection is **off** (today's shipped checkbox-only behavior, zero migration impact for existing consumers), and `true` opts a consumer into clicking anywhere in the row to select it. This also matches every other new prop in this plan (`reorderable`, `resizable`, `filterable`, `columnLayoutToggle`, `selectAllPages`, `persistSelection` all default `false` and require explicit opt-in), rather than the ticket's original negative-polarity, default-on framing — no separate reservation-vs-implementation decision needs to be made during execution.

Add an `onClick` handler on each `<tr>` (`renderRow`) that, when `this.selectable && this.rowClickSelects`, calls `handleRowSelect(id, row)` unless the click originated inside an excluded element — checked via `(e.target as HTMLElement).closest('button, a[href], [role="button"], input, select, textarea, .bds-table__resize-handle, [draggable="true"], .bds-table__td-checkbox, .bds-table__td-expand')`. This exclusion list is why the expand toggle (Task 2) and the checkbox cell must never double-fire selection — both are already excluded structurally, and this task's isolation test must prove the expand-toggle exclusion holds regardless of `rowClickSelects`'s value, per the locked decision.

**Documentation:** Extend the `selectable` story with a `rowClickSelects` toggle, a formatter-rendered `<bds-button>` column, and expandable rows (Task 2), so the exclusion behavior is directly demonstrable. `bds-table.mdx`'s selection section gets a new "Row-click selection" subsection documenting `rowClickSelects` and the interactive-element/expand-toggle exclusion list.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `rowClickSelects` | `boolean` | `false` | When `true`, clicking anywhere in a row (outside excluded interactive elements) toggles its selection, in addition to the checkbox |

- Default (`false`): clicking anywhere in a `selectable` row's `<tr>` does nothing to selection — only the checkbox toggles it (today's shipped behavior, unchanged).
- `rowClickSelects={true}`: clicking anywhere in the row (outside excluded interactive elements) toggles that row's selection, same as clicking its checkbox.
- Clicking a formatter/template-rendered interactive element (e.g. a `<bds-button>`) inside a cell never toggles row selection, regardless of this prop's value.
- Clicking the expand/collapse toggle (Task 2) never toggles row selection, regardless of this prop's value (regression-guarded, per the locked decision).
- `rowSelectable` (Task 9) is respected: a non-selectable row does not toggle via row-click even when `rowClickSelects` is `true`.

**Unit tests to cover:**

- Default (`false`): clicking a cell's plain text area does not toggle selection; clicking the checkbox still does (regression guard).
- `rowClickSelects={true}`: clicking a cell's plain text area toggles that row's selection.
- Clicking a `<button>` inside a formatter-rendered cell does not toggle row selection, in either mode.
- Clicking the expand-toggle button (Task 2's dedicated cell) does not toggle row selection in either mode (explicit regression test for the locked isolation decision).
- A non-selectable row (`rowSelectable` returns `false`) does not toggle via row-click even when `rowClickSelects` is `true`.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `selectable`, a formatter-rendered `<bds-button>` column, and expandable rows (Task 2), toggling `rowClickSelects`.
- Validate:
  - [ ] Given default props, when clicking a plain cell, then nothing happens; the checkbox still works.
  - [ ] Given `rowClickSelects`, when clicking a plain cell, then the row toggles selected.
  - [ ] Given either mode, when clicking a formatter-rendered button or the expand toggle, then row selection never changes.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add rowClickSelects opt-in row-click selection"`

---

## Task 13: `bds-table` — opt-in `filterable`/`columnLayoutToggle` toolbar props

**Executor:** @frontend-subagent (implementation) then @testing-subagent (tests) then @documentation-subagent (docs) then @qa-subagent (manual test)
**Depends on:** none
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` (modify — gate skeleton equivalents)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.toolbar.spec.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Context:** Per the spike's Option B decision, two independent booleans (not one combined flag, not a structured object), matching the existing `searchable`/`selectable`/`serverSide` flat-boolean convention. **Must also gate the loading-state skeleton swap** (`renderTableActionsSkeleton(this.searchable)` inside `renderToolbarRight()`) exactly the same way as the real buttons — otherwise the skeleton placeholder becomes the one remaining always-rendered path once these props ship. A new `hasToolbarRight` getter folds in `searchable`, `filterable`, `columnLayoutToggle`, and the existing slot checks, gating the entire toolbar-right `<div>` so a `subheading`-only table doesn't render a hollow right-side flex container once these buttons stop being unconditional.

**Documentation:** `bds-table` itself stays inert here — `handleFilter()`/`handleTableLayout()` continue to only emit `bdsFilter`/`bdsTableLayout` (confirmed: no dialog/drawer/dropdown rendering exists anywhere inside `bds-table` today, and this task does not add any). The actual panels are consumer-owned, demonstrated entirely in story script, matching the existing convention already used by `BulkEdit`/`BulkDeleteWithUndo`/`WithAddRow` (each builds its own `bds-dialog` inline in response to a `bds-table` event) — no new internal helper or centralizing abstraction is introduced for only two usages. Concretely:

- `WithToolbar` is trimmed to demonstrate only generic toolbar chrome (subheading, icon, tooltip, `searchable`) — it stops implicitly using `filterable`/`columnLayoutToggle` now that both default `false`, since demonstrating the two new panels deserves its own dedicated stories rather than overloading the generic one.
- New story `WithFilterDrawer`: sets `filterable`, listens for `bdsFilter`, and opens a `bds-drawer` (`position="right"`, `backdropClose`) containing a small filter form; on apply, filters the story's own `rows` array client-side and reassigns `table.rows`.
- New story `WithColumnVisibilityDropdown`: sets `columnLayoutToggle`, listens for `bdsTableLayout`, and opens a `bds-dropdown` (multiselect, one entry per column) anchored to the toolbar button; toggling an entry sets that column's `bds-table-column` to `display: none` via the story's own script (no new `bds-table` API — this is purely a story-level demonstration of hiding columns via existing DOM APIs, not a new column-visibility feature on the component).
- `bds-table.mdx`'s "Filter panel" and "Column visibility" sections' opening sentences are updated from "always rendered" to opt-in via these props, cross-referencing the two new stories as the canonical usage examples; the "Current limitations" row for this item is removed.

**Acceptance criteria:**

| Prop | Type | Default | Description |
|---|---|---|---|
| `filterable` | `boolean` | `false` | Renders the built-in Filter toolbar button |
| `columnLayoutToggle` | `boolean` | `false` | Renders the built-in Column-visibility toolbar button |

- `renderToolbarRight()` gates each `<bds-button>` individually: `{this.filterable && <bds-button aria-label="Filter">...}` / `{this.columnLayoutToggle && <bds-button aria-label="Column visibility">...}`.
- The `<bds-button-group label="Table actions">` wrapper itself is gated on `this.filterable || this.columnLayoutToggle` — an empty group must not render.
- The `loading`-state skeleton equivalents in `helpers/bds-table-skeleton.tsx` are gated identically: `{this.filterable && (this.loading ? <skeleton> : <real button>)}` per button, not a single always-rendered skeleton block.
- New `hasToolbarRight` getter gates the entire toolbar-right `<div>`.
- Default (`false` for both) means neither button renders unless explicitly opted in — this is a behavior change from today's always-on buttons; document it prominently as a breaking default in `bds-table.mdx`.
- `bds-table.mdx`'s "Filter panel" and "Column visibility" sections' opening sentences are updated from "always rendered" to reflect the new opt-in props; the "Current limitations" row for this item is removed.

**Unit tests to cover:**

- Default (`false`/`false`): neither the Filter nor Column-visibility button renders; the button-group wrapper itself is absent.
- `filterable={true}` alone: only the Filter button renders (Column-visibility absent).
- `columnLayoutToggle={true}` alone: only the Column-visibility button renders.
- Both `true`: both render, wrapped in one `<bds-button-group>`.
- `loading={true}` with `filterable={true}`: the Filter button's skeleton placeholder renders instead of the real button; with `filterable={false}`, no skeleton for it renders either.
- `hasToolbarRight` correctly reflects all four contributing conditions (`searchable`, `filterable`, `columnLayoutToggle`, slot content).

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:components`; render `bds-table` with `subheading` only (no other toolbar-right content), then add `filterable`/`columnLayoutToggle` combinations, then toggle `loading`.
- Run `pnpm dev:docs`; open the `WithFilterDrawer` and `WithColumnVisibilityDropdown` stories.
- Validate:
  - [ ] Given `subheading` only (no opt-in props), when rendered, then no hollow/empty toolbar-right container appears.
  - [ ] Given `filterable` + `loading=true`, when rendered, then the Filter button's skeleton (not the Column-visibility skeleton) appears alone.
  - [ ] Given `WithFilterDrawer`, when the Filter button is clicked, then a `bds-drawer` opens from the right and applying a filter narrows the visible rows.
  - [ ] Given `WithColumnVisibilityDropdown`, when the Column-visibility button is clicked, then a `bds-dropdown` opens listing every column and toggling an entry hides/shows that column.
  - [ ] Given the same scenario rendered through the `boreal-react` and `boreal-vue` wrapper playgrounds, then behavior is identical to the web-components version — no framework-specific regression.

**Commit:** `git commit -m "feat(bds-table): EOA-16000 add opt-in filterable/columnLayoutToggle toolbar props"`

---

## Task 14: Documentation-only additions — actions column, CSV export (replaces WithRefresh)

**Executor:** @documentation-subagent (only — no component code changes) then @qa-subagent (manual test)
**Depends on:** none (pure Storybook-story additions; both build entirely on already-shipped v2/v3 capabilities)
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)

**Context:** Both items surfaced during v4 planning as documentation gaps rather than missing component behavior — neither needs a new `bds-table`/`bds-table-column` prop, event, or internal state, so this task is scoped as docs-only, mirroring Task 15's test-only precedent (see below).

- **Actions column:** no story currently demonstrates rendering interactive buttons as cell content (`WithFormatter`/`BulkCustomAction` only render a static `bds-tag` via `formatter`). New story `WithActionsColumn` uses the already-shipped `formatter` capability to render `bds-button` icons (edit/delete/duplicate) per row, wired to a bubbling custom event the story listens for and reacts to (e.g. removing the row from its local `rows` array on a delete action) — structurally identical to v3's `#footer-toolbar-table` playground scenario, whose `actionCol.formatter` already renders a `bds-button` per row and whose script listens for a `bdsDelete`-style event to filter `rows`. No new `bds-table` API is needed; this is purely an additional canonical usage example.
- **`WithRefresh` → `WithExport` (renamed):** `WithRefresh` (bds-table.stories.ts) currently demonstrates a single `slot="toolbar-actions"` Refresh button that simulates a 1-second async fetch. This task **replaces** that Refresh button with an Export button and renames the story to `WithExport` — the story keeps exactly one slotted `toolbar-actions` element, not two, and the rename avoids a `WithRefresh` story that no longer refreshes anything. No new `bds-table` API is needed: the story's own script serializes its in-memory `rows` to a CSV string and triggers a client-side download (e.g. a `Blob` + temporary `<a download>`), the same consumer-owned-script pattern already established by v3's `#footer-toolbar-table` scenario (where the page's own script kept a live footer count in sync with `selectedRowsChange` rather than `bds-table` doing it internally).

**Acceptance criteria:**

- `WithActionsColumn` renders an "Actions" column via `formatter`, with edit/delete/duplicate `bds-button` icons per row; the delete action removes the row from the story's local dataset and re-assigns `table.rows`.
- `WithRefresh` is renamed to `WithExport`; its Refresh button in `slot="toolbar-actions"` is replaced with an "Export CSV" button — the story retains only one slotted toolbar-actions element; clicking it downloads a CSV file reflecting the story's current in-memory `rows`.
- `bds-table.mdx` cross-references `WithActionsColumn` from the existing `formatter` documentation as the canonical "interactive cell content" example, and updates any reference to `WithRefresh` to `WithExport`.

**Manual test** _(required — not waiveable; executed by @qa-subagent)_:

- Run `pnpm dev:docs`; open `WithActionsColumn` and the renamed `WithExport` story.
- Validate:
  - [ ] Given `WithActionsColumn`, when the delete button on a row is clicked, then that row disappears from the table.
  - [ ] Given `WithExport`, then only one button ("Export CSV") appears in the toolbar-actions slot — the old Refresh button is gone, not duplicated alongside it.
  - [ ] Given `WithExport`, when "Export CSV" is clicked, then a CSV file downloads containing every row currently in the table.

**Commit:** `git commit -m "docs(bds-table): EOA-16000 add actions-column and CSV export story examples"`

---

## Task 15: Consolidated mutation-testing pass across the full v2+v3+v4 surface

**Executor:** @testing-subagent
**Depends on:** Tasks 1–14 all complete and merged/committed.
**Files:** none directly — this task only adds test cases as needed to kill surviving mutants; no product source changes.

**Context:** Carried forward unchanged from `EOA-15507`'s deferred Task 12 (see that plan's Task 12 and `ai-work/research/2026-06-16-bds-table-column-api-spike.md`'s "Implementation Plan (2026-07-23)" section) — run once here, across every file touched by `EOA-14935` (v2), `EOA-15507` (v3), and this ticket's Tasks 1–14 combined, instead of running it three separate times. Task 14 is documentation-only and touches no component source, so it contributes no new mutation surface.

**Acceptance criteria:**

- Work directly in the current checkout/branch — **do not create a git worktree or separate branch** for the Stryker run (a recurring mistake in the v2 plan's execution that produced invalid, discarded reports run inside `.worktrees/`).
- Install Stryker scoped to `boreal-web-components` only (`pnpm add -D --filter boreal-web-components @stryker-mutator/core @stryker-mutator/jest-runner`), never at the workspace root.
- One Stryker config per touched component (at minimum `bds-table`, `bds-table-column`, `bds-table-column-group`; add configs for any other component this ticket's tasks modified, e.g. `bds-checkbox` only if Task 10's exploration ultimately required touching it — it should not have, per that task's delegation-based design).
- Target: 100% mutation score per component. 90–99% is acceptable only if every surviving mutant is documented with equivalence reasoning in that component's `ai-work/qa/mutation-reports/mutation-<component>.md` — no blanket exemption below 90%, per `.agents/memory/mutation-testing-workflow-decisions.md`.
- When done: fully clean up all Stryker scratch artifacts (`package.json`/lockfile devDependency entries, `stryker.*.config.mjs`, `jest.stryker.config.cjs`, `.stryker-tmp/`, `reports/`) — confirm via `git status` that nothing Stryker-related remains tracked or untracked.

**Manual test:** N/A — this task's own output (mutation score + report files) is its verification.

**Commit:** `git commit -m "test(bds-table): EOA-16000 close mutation-testing gate for combined v2+v3+v4 surface"`

---

## Execution order

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15.

Groups: shared cell-content cache extraction, then row expand/collapse (master-detail slot) and `<template slot="cell">` both built on top of it (1–3) → column grouping, a prerequisite for reorder's header-rendering assumptions (4) → column reorder, then column resizing sharing its recompute path, then right-edge pinning sharing that same recompute path (5–7) → the five selection refinements, ordered so each can assume the guard the previous one introduced — page-scoped-by-default select-all, then per-row selectability, then shift+range (which needs the selectability guard), then server-side persistence (independent, but placed here for thematic grouping), then click-to-select (which needs both the selectability guard and Task 2's expand-isolation guard) (8–12) → opt-in toolbar buttons, independent of everything else in this plan (13) → documentation-only additions needing no new component code (14) → mutation-testing gate for the full combined v2+v3+v4 surface (15).

One item surfaced during exploration is flagged for confirmation rather than silently resolved, and should be settled before or during its task: Task 5's interaction with Task 4 (grouped columns are recommended-excluded from reorder, matching the pinned-column exclusion, pending confirmation). Task 12's scope — real click-to-select behavior vs. the original spike's "reserve the prop, no-op" scoping — is now resolved by naming the prop `rowClickSelects` with a default of `false`: this makes the new behavior purely additive/opt-in, matching every other prop in this plan, so no reservation-vs-implementation ambiguity remains.

## Design decisions locked during planning (for reference)

- Five selection refinements ship as five separate tasks (Tasks 8–12), not one combined task.
- Row expand/collapse is a **master-detail slot** (`<template slot="row-detail">` on `<bds-table>`), not tree-shaped `children?: RowData[]` — re-scoped after review of a design reference. Selection is entirely unaffected by expansion (the detail panel is not a selectable row).
- The expand/collapse toggle is structurally isolated from row selection in all cases, verified against MUI's own bug history (`mui-x#3945`).
- `bdsExpand`'s event detail carries the full `row` object (not just `rowId`), so consumers can populate nested/complex detail content (e.g. a sub-table from a nested array field, matching MUI's own reference example) without any new `bds-table` API.
- The detail-panel reveal animates via a new `bds-transition-collapse` mixin (`_interactions.scss`, `grid-template-rows: 0fr → 1fr`) in non-`virtual` mode only; `virtual` mode keeps the existing instant show/hide to avoid animating a row's height while the virtualizer concurrently tracks its position — confirmed as an explicit scope boundary, not an oversight.
- Task 4's grouped-column header uses an **empty filler `<th>`** in row 1 for ungrouped columns (and the `selectable` checkbox column), not `rowSpan={2}` — corrected against Figma nodes `53:38140`/`53:42699`, whose ungrouped-column labels sit at row 2's baseline rather than centered across both header rows. Groups may also be interspersed between ungrouped columns (not just trailing), per the same reference (4-group / 2-group / 4-ungrouped / 2-group layout).
- **RESOLVED:** Column reorder's original citation ("verified against... AG Grid and Fluent UI DetailsList both pair drag with an explicit control") was checked against real sources and found inaccurate — neither library uses inline Move-left/right buttons (AG Grid uses `Shift+←/→` on the focused header; Fluent UI uses a header context menu). Rather than adopt either external pattern, Task 5 now mirrors an **internal** precedent instead: `bds-card-header.tsx`'s already-shipped `reorder` prop (single `bds-icon-six-dots` handle, `role="button"`/`tabIndex`/`KeyboardController`-driven `Enter`/`Space`, press-scoped native `draggable` arming). This also matches the Figma `_Header` component (node `2:47879`), which defines exactly one `buttonReorder` icon, never two Move buttons. `ArrowLeft`/`ArrowRight` keyboard movement is added on top, since `bds-card-header` itself has no solved keyboard-move mechanism (its `Enter`/`Space` only re-arms dragging, it doesn't move anything) — this is new behavior `bds-table` needs and no internal or external precedent already solves, not something borrowed from elsewhere. The handle is always visible when `reorderable` (never hover-gated), since hover has no touch equivalent. A future ticket could extract a shared `ReorderHandleController` reusable by both `bds-card-header` and `bds-table` — not attempted in this ticket, since `bds-card` is an already-shipped, released component and refactoring it is out of this plan's scope.
- The column resize handle is hover/focus-only visible, never always-rendered.
- Pinned columns (either direction) are excluded from drag/reorder targets entirely.
- Right-edge column pinning ships in this ticket via an additive `pinDirection: 'left' | 'right' = 'left'` prop (not a breaking change to `pinnable`), sharing Task 6's offset-recompute infrastructure.
- The responsive toolbar and its `bds-pagination` prerequisite are excluded entirely from this plan, blocked on an unscheduled UX/UI review.
- `selectAllPages` (Task 8) defaults `false` = page-scoped select-all, identical to today's shipped behavior — the spike's original MUI-derived default (cross-page by default) was rejected specifically to avoid an unnecessary default-behavior change.
- Task 13's filter drawer and column-visibility dropdown are built entirely in Storybook story script, matching the existing `BulkEdit`/`BulkDeleteWithUndo`/`WithAddRow` convention of consumer-owned `bds-dialog` wiring — `bds-table` itself stays inert (`bdsFilter`/`bdsTableLayout` only), and no centralizing helper is introduced for two usages.
- Manual tests in this plan are mandatory gates, never waiveable (deviates from `.agents/rules/plan-execution.md`'s default, which allows a user waiver) — no task may be marked complete without its manual test actually passing. Each task's manual test also builds its own fresh `src/index.html` scenario from scratch rather than reusing v3's `#skeleton-table`/`#pin-table`/`#virtual-table`, to keep this plan's manual verification isolated from v3's component version.
- The bds-dialog backdrop-click-closes-on-inside-click regression (found during Task 13 research) is explicitly out of scope for this ticket — it predates this plan, affects every `bds-dialog` consumer, and should be filed and fixed as its own ticket rather than absorbed here.
