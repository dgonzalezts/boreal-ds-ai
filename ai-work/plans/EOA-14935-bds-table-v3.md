---
ticket: EOA-14935
component: bds-table
status: in progress
created: 2026-07-09
---

# bds-table v3 — Dataset Mode, Column Footer, Server-Side/Loading, Virtualization, Guardrail

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Close out the remaining `bds-table` v2 scope that did not land in the v2 plan/PR: full-dataset internal pagination with cross-page selection, a slot-based column footer, server-side mode with an inline skeleton loading visual, opt-in row virtualization, and a large-dataset guardrail warning.

**Ticket brief:** [`ai-work/tickets/EOA-14935-bds-table-v3.md`](../tickets/EOA-14935-bds-table-v3.md)

**Relationship to v2:** This plan is a direct continuation of `ai-work/plans/EOA-14935-bds-table-v2.md` (status: `done`), which shipped Tasks 1–15 (pagination fixes, tooltip manual mode, controlled selection, built-in search, pinnable hover state, overflow tooltip, and their docs). Tasks below were originally numbered 16–25 (+22b) in that plan; they are renumbered 1–11 here for a clean, self-contained v3 sequence. Original task numbers are noted alongside each title for traceability back to the v2 plan's history/discovery tables.

**Architecture:** Five features land as independently committable additions to `bds-table` (one, the column footer, also touches no other component). Two depend on prerequisite work already shipped in v2 (the `bds-pagination` fixes); the rest are new dependencies purely within this plan's own task sequence.

**Tech Stack:** Stencil (TSX + scoped SCSS), `@tanstack/virtual-core` (already a direct dependency), Jest + Stryker for the two-phase unit-test/mutation-score gate.

---

## Testing policy for this plan (changed from v2)

**Each task below adds unit tests only** (coverage-phase). **Mutation testing (Stryker) is deliberately not run per task** — it is consolidated into a single final task (Task 12) run once, after all other tasks in this plan are complete, across every component touched anywhere in this plan. This mirrors how the v2 plan was actually executed in practice (mutation testing was run as a batched pass across `bds-search-bar`/`bds-table` together, not per-task) and avoids re-running Stryker's ~4-minute-per-component cost after every single task.

Do not install Stryker, create `stryker.*.config.mjs` files, or attempt the two-phase gate until Task 12. If a task's own manual verification surfaces a bug that needs a regression test, add that test in the task's own commit — that's still coverage-phase unit testing, not mutation testing.

---

## Carried-forward reference material from the v2 plan

The following research/decisions from the v2 plan remain directly relevant to tasks in this plan and are reproduced here so this plan is self-contained (not requiring the v2 plan to still be open alongside it):

### Utility Discovery (relevant rows only — see v2 plan's history for the full original table)

| Feature area | Search performed | Candidate found | Fit | Decision |
| --- | --- | --- | --- | --- |
| Row virtualization | `packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts`, `package.json` | `VirtualScrollController<TItem>` (wraps `@tanstack/virtual-core`'s `Virtualizer`), used by `bds-search-bar` | **Partial.** `@tanstack/virtual-core` is already a direct dependency (`^3.17.1`) — no new install needed. But `VirtualScrollController` keeps every child mounted and only toggles `display:none` + absolute positioning; it does not reduce DOM node count. | Reuse the underlying `@tanstack/virtual-core` dependency directly, not `VirtualScrollController`. `bds-table` needs true conditional JSX rendering (only `getVirtualItems()`-selected rows exist as `<tr>` nodes) which the light-DOM-child model cannot provide for Stencil-rendered rows. No shared-utility extension planned. |
| Custom cell / footer rendering | `bds-table.tsx` (`applyCellFormatter`); design playground reference showing footer as a plain boolean toggle, not a computed value | Existing `applyCellFormatter` handles `string \| HTMLElement` via `ref`-based `appendChild`; `slot="empty-state"`/`slot="toolbar-actions"` already establish the light-DOM-slot-moved-into-place pattern | Footer should follow the **slot** pattern, not a new callback prop | No new `footer` prop on `bds-table-column`. Consumers slot static markup (`<span slot="footer">...</span>`) as a child of `<bds-table-column>`; `bds-table` moves that node into the matching `<tfoot>` cell once, same mechanism as existing slots. See Task 2 (sign-off) and Task 3. |
| Skeleton loading rows | Repo-wide search for `skeleton`/`shimmer` in `boreal-web-components` and `boreal-style-guidelines` | None found outside the existing TODO comment in `bds-table.tsx` | Does not fit | Defer building a standalone reusable `bds-skeleton` primitive. Implement the loading visual as a private, table-scoped render helper directly in `bds-table.tsx`/`.scss` (Task 5), using the exact naming/class structure a future primitive would use (`.bds-skeleton`/`.bds-skeleton--rect\|text\|circle`, `--bds-skeleton-*` tokens, a `renderSkeleton(variant, width, height)` helper signature) so a future extraction is a near-mechanical move rather than a rewrite. See "Deferred: extract `bds-skeleton` primitive" below. |
| Large-dataset guardrail logging | `bds-table.tsx` (`private readonly logger = new Logger()`) | `Logger` service already imported and used | Fully fits | Reuse `this.logger.warn(...)`. |
| Dataset/pagination wiring | `bds-table.tsx` `componentDidLoad`/`componentWillLoad` (existing `querySelectorAll('bds-table-column')` + `MutationObserver` pattern) | Same slotted-child-query pattern already used for columns | Fully fits | Reuse the identical pattern for querying the slotted `bds-pagination`. |

---

## Task 1 (was Task 16): `bds-table` — `dataset` prop, internal pagination, cross-page selection

**Executor:** @frontend-subagent
**Depends on:** v2 Task 1, `bds-pagination`'s `totalItems` watcher fix — already shipped in the v2 PR.
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop/State | Type | Default | Description |
| --- | --- | --- | --- |
| `dataset` (Prop) | `RowData[]` | `[]` | Full unfragmented dataset; table performs internal page slicing |
| `visibleRows` (State, private) | `RowData[]` | `[]` | Current page slice derived from `dataset` |

- `@Watch('dataset')` resets pagination to page 1 and clears `selectedRowIds`.
- `componentDidLoad`, when `dataset.length > 0`: queries the slotted `bds-pagination`, sets `paginationEl.totalItems = this.dataset.length`, attaches an internal `bdsPageChange` listener that slices into `visibleRows`.
- `render()`/`sortedData`/`renderBody` read from `visibleRows` when `dataset.length > 0`.
- `getSelectedRows()` resolves against `dataset` in this mode.
- `handleSelectAll()` and header checkbox scope default to current-page (`visibleRows.length`), not full-dataset scope.
- Warn via `Logger` if both `data` and `dataset` are set simultaneously.
- Re-emit `bdsPageChange` after internal slicing.

**Unit tests to cover:**

- `dataset` slices correctly per `bdsPageChange`.
- `dataset` change resets page/selection.
- `getSelectedRows()` resolves correctly across page navigations (cross-page selection).
- Select-all scope reflects current-page.
- Both `data`+`dataset` set logs a warning.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `dataset` (50 rows) + slotted `bds-pagination` (`items-per-page="10"`), selectable.
- Validate:
  - [ ] Given `dataset` with 50 rows, when mounted, then the paginator shows 5 pages with no consumer-side slicing. Pass: matches `50/10`.
  - [ ] Given a row selected on page 1, when navigating to page 2 and back, then it remains selected. Pass: checkbox still checked.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add dataset prop with internal pagination and cross-page selection"`

---

## Task 2 (was Task 17): Design-review checkpoint — column footer as a slot (confirmation gate, no code)

**Executor:** none (requires human/PM sign-off before Task 3 starts)

**Deliverable:** confirm the corrected design before implementation:

- No new prop on `bds-table-column`. Consumers slot static markup as a direct child: `<bds-table-column col-key="amount" label="Amount"><span slot="footer">Total: $1,234</span></bds-table-column>`.
- `bds-table` detects footer content via `col.querySelector(':scope > [slot="footer"]')`, and moves that node into the matching `<tfoot>` `<td>` once — the same "read light-DOM child, project into rendered output" pattern already used for `slot="empty-state"`/`slot="row-actions"`/`slot="toolbar-actions"`.
- Because this is static, consumer-owned markup (not a computed function of rows), there is no "recompute on data change" behavior to build — if a consumer wants a live total, they update the slotted element's content themselves from their own script, same as any other slotted content in this component.
- `<tfoot>` renders only when at least one column has slotted footer content.

**Manual test:** N/A — sign-off gate.

---

## Task 3 (was Task 18): `bds-table` — column footer row (slot-based)

**Executor:** @frontend-subagent
**Depends on:** Task 2 (sign-off)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify — pinned footer cell treatment matching header/body)

**Acceptance criteria:**

- `private get hasFooter(): boolean` — `true` when any column has a direct child matching `[slot="footer"]`.
- `renderFooter()` produces one `<tfoot><tr>` with one `<td>` per column plus an empty `<td>` for the checkbox-column gap when `selectable` — mirrors `renderBody`'s structure.
- Pinned columns' footer cells receive the same `data-pinned`/`style.left` treatment as header/body cells — extend the existing pinned-offset loop in `componentDidRender`.
- Reuse/extract the shared node-appending helper identified in the Utility Discovery table (the same `ref`-based append pattern as `applyCellFormatter`) so footer-cell projection and formatter-driven cell rendering share one implementation rather than duplicating the append logic.
- `<tfoot>` renders only when `hasFooter` is `true`.

**Unit tests to cover:**

- No `<tfoot>` when no column has slotted footer content.
- `<tfoot>` renders one `<td>` per column plus checkbox gap when `selectable`.
- Slotted footer content actually appears inside the correct `<td>`.
- Pinned footer cells receive matching `style.left` offsets.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with one column slotting `<span slot="footer">Total: 42</span>`.
- Validate:
  - [ ] Given a column with slotted footer content, when the table renders, then the footer row shows that content in the correct column position. Pass: visual match, correct alignment with pinned columns if applicable.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add slot-based column footer row"`

---

## Task 4 (was Task 19): `bds-table` — documentation for column footer

**Executor:** @documentation-subagent
**Depends on:** Task 3
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove the limitations-table row covering column footers (re-check current row numbering against the live `bds-table.mdx` before editing — v2's doc pass renumbered the table; do not assume the original v2-plan row numbers still apply).
- New "Column footers" section documenting the `slot="footer"` pattern, with an example showing a consumer-updated live total.
- New `WithColumnFooter` story.

**Manual test:** Run `pnpm dev:docs`, confirm the new section and story.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document slot-based column footer row"`

---

## Task 5 (was Task 20): `bds-table` — server-side mode and inline loading/skeleton visual

**Executor:** @frontend-subagent
**Depends on:** v2 Tasks 1 and 3 (`bds-pagination` watcher fix and `loading` prop) — already shipped in the v2 PR.
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify, or a sibling `_bds-table-skeleton.scss` partial imported by it)

**Acceptance criteria:**

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `serverSide` | `boolean` | `false` | Disables local sort reordering; `bdsSort` still emits for the consumer to re-fetch |

- When `serverSide` is `true`, `sortedData`/`visibleRows`-aware equivalent returns rows unsorted; `handleSort` still emits `bdsSort` with the correct payload.
- Replace the `onLoadingChange` no-op stub with real behavior: when `loading` is `true`, `renderBody()` renders `loadingRows` rows composed of a private `renderSkeleton(variant, width, height)` helper — one per column plus the checkbox-column gap when `selectable` — instead of real data.
- **No new component is created.** The skeleton markup/CSS lives entirely inside `bds-table`'s own files, but is named and structured as if it were the future extracted primitive, to keep a later extraction cheap:
  - CSS classes: `.bds-skeleton` root class with `.bds-skeleton--rect`, `.bds-skeleton--text`, `.bds-skeleton--circle` modifiers (not `.bds-table__skeleton*`).
  - Custom properties: `--bds-skeleton-*` (not `--bds-table-skeleton-*`), matching the `bds-divider` `--bds-divider-*` convention.
  - Private TSX helper signature: `renderSkeleton(variant: 'text' | 'rect' | 'circle', width: string, height: string)` — a signature-for-signature match to the deferred `bds-skeleton` primitive's eventual public props.
  - Shimmer built entirely with `var(--boreal-*)` tokens; `@keyframes` sweep; respects `prefers-reduced-motion` (static, muted-token background instead of animating).
- This single implementation satisfies both this task's server-side loading state and the standalone "skeleton placeholder" limitation.
- Does not combine `serverSide` with future virtualization-based infinite scroll (documentation-only note, no code enforcement needed).

**Unit tests to cover:**

- `serverSide={true}` + sortable header click emits `bdsSort` but leaves row order unchanged.
- `loading={true}` renders exactly `loadingRows` rows of skeleton placeholder cells with correct column count.
- `loading={false}` (default) renders real data unaffected.
- The reduced-motion class/attribute is present on the skeleton markup when `loading={true}` (absorbs the manual-test reduced-motion criterion into an automated check, since there's no separate `bds-skeleton` spec file to hold it).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `serverSide` + a sortable column; toggle `loading`.
- Validate:
  - [ ] Given `serverSide=true`, when clicking a sortable header, then row order stays visually unchanged while the sort icon updates. Pass: visual + icon check.
  - [ ] Given `loading=true`, when rendered, then skeleton placeholder rows appear instead of data. Pass: shimmer visible, real data hidden.
  - [ ] Given `prefers-reduced-motion: reduce` is simulated (browser devtools rendering panel), when `loading=true`, then the shimmer animation is replaced by a static muted background. Pass: no animation, tokens still applied.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add serverSide mode and inline skeleton loading rows"`

---

## Task 6 (was Task 21): `bds-table` — documentation for server-side mode and loading state

**Executor:** @documentation-subagent
**Depends on:** Task 5
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove the limitations-table rows covering server-side mode and skeleton placeholder loading (re-check current row numbering against the live `bds-table.mdx` before editing).
- New "Server-side mode" section with a fetch-wiring example.
- New stories: `WithServerSideMode`, `WithLoadingState`.
- No separate `bds-skeleton` doc page to reference — the loading-state section documents the skeleton visual as a `bds-table` implementation detail only.
- **Props ArgTypes — confirmed still missing as of 2026-07-14, do not skip:** `loading`, `loadingRows`, and this task's new `serverSide` prop are not currently in `bds-table.stories.ts`'s `argTypes` object, nor in the MDX `<ArgTypes include={[...]}>` list (verified directly against both files while auditing v2's docs). Add all three the same way `data`/`rowKey`/`selectedRows`/`searchable`/`selectedRowsChange` were added in the v2 plan's Task 15 follow-up. **Known pitfall from that same follow-up:** adding a name to the MDX `include` array alone does nothing — Storybook's `<ArgTypes>` silently drops any entry without a matching `argTypes` object entry in `.stories.ts`. Add to `argTypes` first, then the MDX `include` list, and verify via `pnpm dev:docs` that the rows actually render — don't just check the source diff.

**Manual test:** Run `pnpm dev:docs`, confirm sections/stories.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document server-side mode and loading state"`

---

## Task 7 (was Task 22): `bds-table` — row virtualization

**Executor:** @frontend-subagent
**Depends on:** Task 1, Task 5
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/package.json` (verify only — `@tanstack/virtual-core@^3.17.1` already present)

**Acceptance criteria:**

| Prop/State | Type | Default | Description |
| --- | --- | --- | --- |
| `virtual` (Prop) | `boolean` | `false` | Opt-in row virtualization; `false` renders exactly as today |
| `virtualizer` (State, private) | `Virtualizer<Element, Element>` | — | Drives the windowed row set |

- Per Utility Discovery, do not reuse `VirtualScrollController` — wire `@tanstack/virtual-core`'s `Virtualizer` directly against Stencil's render cycle. Even a fixed/reworked `VirtualScrollController` could not be reused here — its entire architecture (`MutationObserver` + `querySelectorAll` over a consumer's pre-existing light-DOM children) is built to manage markup a consumer already placed, not to drive a declarative render function like `renderBody()`.
- **No proven reference implementation exists to copy.** Build directly against `@tanstack/virtual-core`'s public API rather than porting an existing pattern from another codebase (verified during v2 planning: neither this repo's `aq-table-core.tsx` reference nor Aqua's own list/dropdown virtualization solves the "reduce upfront row-creation cost for a real `<table>`" problem this task needs).
- `componentDidLoad`, when `virtual` is `true`, initializes with `count` from whichever row-set is active (`data`, `visibleRows`, or `serverSide`-supplied `data`), `getScrollElement` pointing at `.bds-table__wrapper`, `estimateSize: () => 48`, `measureElement` for variable-height rows.
- `renderBody()` iterates only `getVirtualItems()` when `virtual` is `true`, with a spacer sized via `getTotalSize()`, using **explicit `key={rowId}` on every virtualized `<tr>`** — currently absent from `renderBody()` even without virtualization. Without it, Stencil's JSX diffing falls back to positional reconciliation, risking row-identity-cache mismatches. Add this regardless of virtualization, since the underlying data (`sortedData`/`visibleRows`) can already reorder on sort/filter/page-change today.
- Log via `Logger` if `virtual=true` and `maxHeight === ''`.
- **Known upstream limitation (verified against TanStack Virtual's own official examples and issue tracker during v2 planning):** combining a sticky `<thead>` with a windowed `<tbody>` in a real `<table>` element is a documented-broken pattern upstream (TanStack/virtual#585, #591, #640) — the table's rendered height is smaller than its true scroll height since only visible+overscan rows exist, breaking sticky positioning. **Decision (Option B, confirmed previously): scope out the combination for v1.** When `virtual=true`, disable the `<thead>`'s `position: sticky` behavior (conditional class/style override) and document this as a known limitation — do not silently leave `position: sticky` active.

**Unit tests to cover:**

- `virtual={false}` (default) renders all rows unchanged (regression guard).
- `virtual={true}` renders only the windowed subset.
- `virtual={true}` without `maxHeight` logs a warning.
- Spacer sized to `getTotalSize()` present when virtualized.
- Each virtualized `<tr>` carries the correct `key={rowId}`; row/checkbox selection state stays attached to the correct row after a sort or filter while `virtual=true`.
- `virtual={true}` disables `<thead>` sticky behavior (Option B); `virtual={false}` leaves it unchanged.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `virtual` + `max-height` + ~5,000 rows.
- Validate:
  - [ ] Given `virtual=true` with `maxHeight` set, when scrolling through 5,000 rows, then only a small window of `<tr>` elements exists in the DOM at any time (inspect via devtools). Pass: DOM node count stays roughly constant.
  - [ ] Given `virtual=true` without `maxHeight`, when mounted, then a console warning appears. Pass: warning visible.
  - [ ] Given a virtualized table, when sorting or filtering while rows are selected, then the correct rows remain checked (not rows that happen to share the same scroll position). Pass: selection follows the data, not the position.
  - [ ] Given `virtual=true`, when scrolling, then the header does not stick (Option B) rather than visibly breaking/disappearing mid-scroll. Pass: header behaves consistently (non-sticky), no flicker.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add opt-in row virtualization"`

---

## Task 8 (was Task 22b): `bds-table` — throttle pin-offset recomputation during virtualized scroll

**Executor:** @frontend-subagent
**Depends on:** Task 7
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)

**Context:** `componentDidRender` already runs a `querySelectorAll('th[data-pinned]')` + `offsetWidth` read on *every* render to compute pinned-column offsets. With virtualization enabled, every scroll-driven re-render triggers this same DOM query and layout read, reintroducing exactly the kind of per-frame cost virtualization is meant to remove.

**Acceptance criteria:**

- Guard the existing pin-offset computation so it only recomputes when `pinnedColKeys` or `columns` actually change, not on every scroll-triggered re-render while `virtual=true`.
- No behavior change when `virtual=false` (default).

**Unit tests to cover:**

- Pin-offset computation does not re-run on a scroll-only re-render while `virtual=true` and `pinnedColKeys`/`columns` are unchanged.
- Pin-offset computation still runs correctly when a column is pinned/unpinned or the column set changes.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render a virtualized table with several pinned columns and ~5,000 rows.
- Validate:
  - [ ] Given a virtualized table with pinned columns, when scrolling rapidly, then scrolling stays smooth with no visible lag or incorrect pin offsets. Pass: compare scroll smoothness before/after this fix using the browser's Performance panel.

**Commit:** `git commit -m "perf(bds-table): EOA-14935 throttle pin-offset recomputation during virtualized scroll"`

---

## Task 9 (was Task 23): `bds-table` — documentation for virtualization

**Executor:** @documentation-subagent
**Depends on:** Task 7
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove the limitations-table row covering virtualization (re-check current row numbering against the live `bds-table.mdx` before editing).
- New "Virtualization" section, explicitly noting this differs from `bds-search-bar`'s lighter-weight approach (which keeps all DOM nodes mounted) — `bds-table`'s virtualization actually bounds DOM node count.
- Document the Option B limitation explicitly: the sticky header (`position: sticky` on `<thead>`) is disabled while `virtual=true`, since combining the two is a documented-broken pattern upstream in TanStack Virtual.
- New `WithVirtualization` story using a ~5,000-row generated dataset, demonstrating the non-sticky header behavior in that mode.

**Manual test:** Run `pnpm dev:docs`, confirm section/story.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document row virtualization"`

---

## Task 10 (was Task 24): `bds-table` — large-dataset guardrail (`maxClientRows`)

**Executor:** @frontend-subagent
**Depends on:** Task 5, Task 7
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `maxClientRows` | `number` | `1000` (confirm with the team) | Threshold above which a non-blocking warning fires |

- Keep this guardrail even with virtualization shipped — `virtual=true` only bounds DOM node count/paint cost; it does **not** eliminate the cost of `sortedData`'s `[...this.data].sort(...)` running over the full array on every sort, `getSelectedRows()` filtering over the full array, holding the entire dataset in memory, or the network/JSON-parse cost of transferring it.
- When `(dataset.length > 0 ? dataset.length : data.length) > maxClientRows`, log a warning via `Logger` unless `serverSide` is `true` (server-side genuinely eliminates the client-side cost, since the browser never holds the full dataset). Do **not** fully suppress the warning just because `virtual` is `true` — instead, when `virtual` is `true`, adjust the warning's wording to acknowledge that DOM rendering is windowed, but sort/selection/memory/transfer cost still scales with dataset size, and very large datasets should still consider `serverSide`.
- Non-blocking — rendering is unaffected either way.

**Unit tests to cover:**

- Warning fires when exceeded and `serverSide` is `false`, with `virtual` either `false` or `true` (differing message content between the two).
- Warning does not fire when `serverSide` is `true`, or when under threshold.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with 1,500 rows, no `serverSide`/`virtual`.
- Validate:
  - [ ] Given 1,500 rows with neither mode enabled, when mounted, then a console warning recommends server-side or virtual mode. Pass: warning visible; table still renders all rows.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add maxClientRows guardrail warning"`

---

## Task 11 (was Task 25): `bds-table` — documentation for the guardrail

**Executor:** @documentation-subagent
**Depends on:** Task 10
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)

**Acceptance criteria:**

- `maxClientRows` added to the props table.
- Row-count ceiling documented in "Layout constraints", alongside the 800px minimum-width note.

**Manual test:** Run `pnpm dev:docs`, confirm the update.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document maxClientRows guardrail"`

---

## Task 12 (new): Mutation testing for all v3 changes

**Executor:** @testing-subagent
**Depends on:** Tasks 1–11 all complete and merged/committed.
**Files:** none directly — this task only adds test cases as needed to kill surviving mutants; no product source changes.

**Context:** Per this plan's testing policy (see top of document), mutation testing is run once here, across every file touched by Tasks 1–11, instead of after each individual task. This was also how the v2 plan's mutation-testing phase was actually executed in practice.

**Acceptance criteria:**

- Work directly in the current checkout/branch — **do not create a git worktree or separate branch** for the Stryker run (a recurring mistake in the v2 plan's execution that produced invalid, discarded reports run inside `.worktrees/`).
- Install Stryker scoped to `boreal-web-components` only (`pnpm add -D --filter boreal-web-components @stryker-mutator/core @stryker-mutator/jest-runner`), never at the workspace root.
- One Stryker config per touched component (at minimum `bds-table`; add configs for any other component this plan's tasks modified, e.g. if `bds-pagination` or `bds-table-column` needed changes).
- Target: 100% mutation score per component. 90–99% is acceptable only if every surviving mutant is documented with equivalence reasoning in that component's `ai-work/qa/mutation-reports/mutation-<component>.md` — no blanket exemption below 90%, per `.agents/memory/mutation-testing-workflow-decisions.md`.
- When done: fully clean up all Stryker scratch artifacts (`package.json`/lockfile devDependency entries, `stryker.*.config.mjs`, `jest.stryker.config.cjs`, `.stryker-tmp/`, `reports/`) — confirm via `git status` that nothing Stryker-related remains tracked or untracked.

**Manual test:** N/A — this task's own output (mutation score + report files) is its verification.

**Commit:** `git commit -m "test(bds-table): EOA-14935 close mutation-testing gate for v3 changes"`

---

## Deferred: extract `bds-skeleton` primitive — not in this plan's scope

**Decision (carried forward from the v2 plan):** this plan implements `bds-table`'s loading visual as a private, table-scoped render helper (Task 5) instead of building a standalone `bds-skeleton` component. A reusable skeleton primitive is valuable long-term, but building it is deferred until a second real consumer exists.

**Trigger condition to revisit:** a second component (e.g. `bds-list`, `bds-card`, a detail-panel pattern) needs a loading-placeholder visual, or design/product explicitly requests skeleton support outside `bds-table`.

**Why the extraction should stay cheap when that happens:** Task 5 uses the future primitive's exact shape today — `.bds-skeleton`/`.bds-skeleton--rect|text|circle` classes, `--bds-skeleton-*` custom properties, and a `renderSkeleton(variant, width, height)` helper signature matching the deferred component's eventual public props. Extracting later should be close to "cut, paste, rename tag, add Stencil registration" rather than a redesign.

**Recommendation:** file this as its own small follow-up ticket (e.g. `EOA-XXXXX-bds-skeleton-primitive-extraction.md`) once the trigger condition is met, sized as a single small task (scaffold + SCSS + tests + docs), not pre-assigned to a sprint.

---

## Related research: shared virtualization utility with `bds-search-bar` — deferred, not in this plan's scope

Carried forward from the v2 plan's own research: since `VirtualScrollController` (used by `bds-search-bar`) doesn't reduce DOM node count, and `bds-table` needs real virtualization anyway (Task 7), a shared reusable utility on `@tanstack/virtual-core` was investigated as a possible consolidation.

- **Conclusion:** technically possible, but only by rearchitecting `bds-search-bar`'s list onto a windowed-creation model (data-driven element recycling) — not by generalizing `VirtualScrollController`'s current positional/`MutationObserver`-driven design, which sits in a real bug class TanStack's own tracker documents (identity-cache races, `ResizeObserver` conflicts with hidden/removed nodes).
- **Decision:** deferred to a separate future spike/ticket. Task 7 above is unaffected — it builds its own direct `@tanstack/virtual-core` integration without depending on or interfering with `VirtualScrollController`.
- Full research: `ai-work/research/2026-07-06-shared-virtualization-utility.md`. Related bug tracked at `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`. Neither is scheduled against this plan.

---

## Execution order

1 → 2 (sign-off) → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12.

Groups: dataset/internal pagination (1) → footer, gated on sign-off (2–4) → server-side mode + inline skeleton rows (5–6) → virtualization, including its pin-offset throttling follow-up (7–9) → guardrail (10–11) → mutation-testing gate for everything in this plan (12).
</content>
