---
ticket: EOA-15507
component: bds-table
status: in progress
created: 2026-07-09
---

# bds-table v3 — Dataset Mode, Column Footer, Server-Side/Loading, Virtualization, Guardrail

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Close out the remaining `bds-table` v2 scope that did not land in the v2 plan/PR: full-dataset internal pagination with cross-page selection, a slot-based column footer, server-side mode with an inline skeleton loading visual, opt-in row virtualization, and a large-dataset guardrail warning.

**Ticket brief:** [`ai-work/tickets/EOA-15507-bds-table-v3.md`](../tickets/EOA-15507-bds-table-v3.md)

**Relationship to v2:** This plan is a direct continuation of `ai-work/plans/EOA-15507-bds-table-v2.md` (status: `done`), which shipped Tasks 1–15 (pagination fixes, tooltip manual mode, controlled selection, built-in search, pinnable hover state, overflow tooltip, and their docs). Tasks below were originally numbered 16–25 (+22b) in that plan; they are renumbered 1–11 here for a clean, self-contained v3 sequence. Original task numbers are noted alongside each title for traceability back to the v2 plan's history/discovery tables.

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

| Feature area                    | Search performed                                                                                                                      | Candidate found                                                                                                                                                                                          | Fit                                                                                                                                                                                                                                                          | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Row virtualization              | `packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts`, `package.json`                                        | `VirtualScrollController<TItem>` (wraps `@tanstack/virtual-core`'s `Virtualizer`), used by `bds-search-bar`                                                                                              | **Partial.** `@tanstack/virtual-core` is already a direct dependency (`^3.17.1`) — no new install needed. But `VirtualScrollController` keeps every child mounted and only toggles `display:none` + absolute positioning; it does not reduce DOM node count. | Reuse the underlying `@tanstack/virtual-core` dependency directly, not `VirtualScrollController`. `bds-table` needs true conditional JSX rendering (only `getVirtualItems()`-selected rows exist as `<tr>` nodes) which the light-DOM-child model cannot provide for Stencil-rendered rows. No shared-utility extension planned.                                                                                                                                                                                                     |
| Custom cell / footer rendering  | `bds-table.tsx` (`applyCellFormatter`); design playground reference showing footer as a plain boolean toggle, not a computed value    | Existing `applyCellFormatter` handles `string \| HTMLElement` via `ref`-based `appendChild`; `slot="empty-state"`/`slot="toolbar-actions"` already establish the light-DOM-slot-moved-into-place pattern | Footer should follow the **slot** pattern, not a new callback prop                                                                                                                                                                                           | No new `footer` prop on `bds-table-column`. Consumers slot static markup (`<span slot="footer">...</span>`) as a child of `<bds-table-column>`; `bds-table` moves that node into the matching `<tfoot>` cell once, same mechanism as existing slots. See Task 2 (sign-off) and Task 3.                                                                                                                                                                                                                                               |
| Skeleton loading rows           | Repo-wide search for `skeleton`/`shimmer` in `boreal-web-components` and `boreal-style-guidelines`                                    | None found outside the existing TODO comment in `bds-table.tsx`                                                                                                                                          | Does not fit                                                                                                                                                                                                                                                 | Defer building a standalone reusable `bds-skeleton` primitive. Implement the loading visual as a private, table-scoped render helper directly in `bds-table.tsx`/`.scss` (Task 5), using the exact naming/class structure a future primitive would use (`.bds-skeleton`/`.bds-skeleton--rect\|text\|circle`, `--bds-skeleton-*` tokens, a `renderSkeleton(variant, width, height)` helper signature) so a future extraction is a near-mechanical move rather than a rewrite. See "Deferred: extract `bds-skeleton` primitive" below. |
| Large-dataset guardrail logging | `bds-table.tsx` (`private readonly logger = new Logger()`)                                                                            | `Logger` service already imported and used                                                                                                                                                               | Fully fits                                                                                                                                                                                                                                                   | Reuse `this.logger.warn(...)`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Dataset/pagination wiring       | `bds-table.tsx` `componentDidLoad`/`componentWillLoad` (existing `querySelectorAll('bds-table-column')` + `MutationObserver` pattern) | Same slotted-child-query pattern already used for columns                                                                                                                                                | Fully fits                                                                                                                                                                                                                                                   | Reuse the identical pattern for querying the slotted `bds-pagination`.                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

---

## Task 1 (was Task 16): `bds-table` — `rows` prop, internal pagination, cross-page selection **✅ COMPLETE**

> **Amendment (2026-07-16, during execution):** the prop is named **`rows`**, not `dataset` — `dataset` shadows the native `HTMLElement.prototype.dataset` API (the standard `data-*` attribute map) on the host element; verified against Stencil 4.42.1's runtime during implementation and renamed with user sign-off (mirrors MUI DataGrid's `rows`). Every reference to `dataset`/`dataset.length`/"dataset mode" in this task and in Tasks 6, 7, 10, and the docs tasks means `rows` from here on. Commits on this branch use ticket ID **EOA-15507**, matching the plan and ticket brief's frontmatter (both renamed from EOA-14935 on 2026-07-16 to align with branch convention).

**Executor:** @frontend-subagent
**Depends on:** v2 Task 1, `bds-pagination`'s `totalItems` watcher fix — already shipped in the v2 PR.
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop/State                     | Type        | Default | Description                                                     |
| ------------------------------ | ----------- | ------- | --------------------------------------------------------------- |
| `rows` (Prop)                  | `RowData[]` | `[]`    | Full unfragmented dataset; table performs internal page slicing |
| `visibleRows` (State, private) | `RowData[]` | `[]`    | Current page slice derived from `rows`                          |

- `@Watch('rows')` resets pagination to page 1 and clears `selectedRowIds`.
- `componentDidLoad`, when `rows.length > 0`: queries the slotted `bds-pagination`, sets `paginationEl.totalItems = this.rows.length`, attaches an internal `bdsPageChange` listener that slices into `visibleRows`.
- `render()`/`sortedData`/`renderBody` read from `visibleRows` when `rows.length > 0`.
- `getSelectedRows()` resolves against `rows` in this mode.
- `handleSelectAll()` and header checkbox scope default to current-page (`visibleRows.length`), not full-dataset scope.
- Warn via `Logger` if both `data` and `rows` are set simultaneously.
- Re-emit `bdsPageChange` after internal slicing.

**Unit tests to cover:**

- `rows` slices correctly per `bdsPageChange`.
- `rows` change resets page/selection.
- `getSelectedRows()` resolves correctly across page navigations (cross-page selection).
- Select-all scope reflects current-page.
- Both `data`+`rows` set logs a warning.
- `rows` prop does not shadow native `HTMLElement.dataset` API.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `rows` (50 rows) + slotted `bds-pagination` (`items-per-page="10"`), selectable.
- Validate:
  - [x] Given `rows` with 50 rows, when mounted, then the paginator shows 5 pages with no consumer-side slicing. Pass: matches `50/10`.
  - [x] Given a row selected on page 1, when navigating to page 2 and back, then it remains selected. Pass: checkbox still checked.

**Unit test results:** 11 tests passing in `bds-table.rows.spec.ts` (see `pnpm --filter @telesign/boreal-web-components test -- bds-table.rows.spec.ts`)

> **Follow-up fix (2026-07-21, found while validating Task 3):** a full-suite test run surfaced a Stencil dev-mode warning — `The state/prop "visibleRows" changed during "componentDidLoad()"...` — firing 8x, only from this task's `rows`-mode setup. Root cause: `componentDidLoad()` called `setupRowsPagination()`, which synchronously mutates `@State() visibleRows` via `sliceVisibleRows()`; mutating `@State()` during `componentDidLoad()` is a Stencil anti-pattern that forces an extra unnecessary re-render on every initial `rows`-mode mount. Fixed by moving the `if (this.rows.length > 0) { this.setupRowsPagination(); }` call from `componentDidLoad()` into `componentWillLoad()` (`bds-table.tsx`) — safe because `setupRowsPagination()` only needs the slotted `<bds-pagination>` sibling, already queryable via light-DOM `querySelector` at `componentWillLoad()` time, the same pattern already used one line earlier for `bds-table-column` children. Independently verified by `@testing-subagent`: reproduced the original warning by temporarily reverting the fix, confirmed it's gone after restoring it, all 146 tests across the component's 10 spec files still pass, `bds-table.rows.spec.ts`'s dynamic-pagination-added-after-mount scenario (line 141) is unaffected since it goes through a different code path (`onRowsChange()`), and coverage is unchanged (98.05% statements, uncovered lines unrelated to this change).

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add rows prop with internal pagination and cross-page selection"`

---

## Task 1b (new): `bds-table` — documentation for `rows` prop / dataset mode **✅ COMPLETE**

**Executor:** @documentation-subagent
**Depends on:** Task 1
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Add `rows` to the props table: type `RowData[]`, default `[]`, description "Full unfragmented dataset; table performs internal page slicing and manages pagination via slotted `bds-pagination`"
- New "### Dataset mode (`rows` prop)" section covering:
  - Difference from `data` (consumer-managed vs internal pagination)
  - Cross-page selection behavior (selection persists across page navigation)
  - `rows` + `bds-pagination` wiring example
  - Warning when both `data` and `rows` are set simultaneously
- New `WithRowsPagination` story demonstrating 50 rows, selectable, slotted `bds-pagination` with `items-per-page="10"`, page navigation preserving selection
- `rows` added to `argTypes` in `bds-table.stories.ts` with appropriate control, then added to MDX `<ArgTypes include={[...]}>` list

> **Amendment (2026-07-16, during execution):** "### Paginator integration" (Component Anatomy) was also restructured into a two-mode overview (`rows` recommended / `data` manual, with a link down to this section) so a reader hits the `rows` recommendation before the legacy `data`-slicing example — it was not previously in scope but was a direct consequence of adding `rows` documentation. Two pre-existing doc bugs were fixed in the same pass: `e.detail.page` → `e.detail.currentPage` in the `data`-mode example (verified against `bds-pagination.tsx`'s actual `bdsPageChange` detail shape), and a precedence contradiction in the `data`+`rows` warning callout (verified against the actual `Logger.warn` string in `bds-table.tsx` — `rows` takes precedence, not `data`). Additionally, the "Cross-page selection behavior" paragraph was corrected post-review: it originally claimed a toolbar selection tag with a close icon, but `WithRowsPagination` sets only `selectable` (no `subheading`/`searchable`/action-slot content), so `hasToolbar` never renders — the story has no toolbar. Reworded to describe only checkbox-driven selection persisting across pages, cleared via `table.clearSelection()`.

**Manual test:** Run `pnpm dev:docs`, confirm the new section and story render correctly.
- [x] Manual review of rendered MDX confirms the restructured "Paginator integration" section and "Dataset mode" section are consistent and no longer reference nonexistent toolbar UI.

**Commit:** `ac5f06fb docs(web-components): EOA-15507 document rows prop and dataset mode` (includes the Paginator integration restructure and the Selection-tag wording fix)

---

## Task 2 (was Task 17): Design-review checkpoint — column footer as a slot (confirmation gate, no code) **✅ COMPLETE**

**Executor:** none (requires human/PM sign-off before Task 3 starts)

**Deliverable:** confirm the corrected design before implementation:

- No new prop on `bds-table-column`. Consumers slot static markup as a direct child: `<bds-table-column col-key="amount" label="Amount"><span slot="footer">Total: $1,234</span></bds-table-column>`.
- `bds-table` detects footer content via `col.querySelector(':scope > [slot="footer"]')`, and moves that node into the matching `<tfoot>` `<td>` once — the same "read light-DOM child, project into rendered output" pattern already used for `slot="empty-state"`/`slot="row-actions"`/`slot="toolbar-actions"`.
- Because this is static, consumer-owned markup (not a computed function of rows), there is no "recompute on data change" behavior to build — if a consumer wants a live total, they update the slotted element's content themselves from their own script, same as any other slotted content in this component.
- `<tfoot>` renders only when at least one column has slotted footer content.

**Manual test:** N/A — sign-off gate.

---

## Task 3 (was Task 18): `bds-table` — column footer row (slot-based) **✅ COMPLETE**

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
  - [x] Given a column with slotted footer content, when the table renders, then the footer row shows that content in the correct column position. Pass: visual match, correct alignment with pinned columns if applicable. Verified in `src/index.html` playground via `pnpm dev:components` + Playwright across four scenarios (kept live in the playground for future re-verification, not deleted after this pass):
    1. **Minimal footer table** (no id, second `bds-table` on the page) — "Total" / "$1,234.00" aligned under ID/Amount; pinning ID then Item (80px width) produced `th`/body-`td`/footer-`td` all reporting `left: 0px` and `left: 80px` respectively.
    2. **`#footer-toolbar-table`** — toolbar (title+tooltip, search, filter/column-visibility icons, `toolbar-actions` slot), `selectable`, `rows`-mode pagination (`items-per-page="5"`, `perPageOptions` overridden to `[5, 10, 25, 50]` via JS property since 5 isn't in the component's default option list), a `bds-button`-based row-actions formatter on the pinnable "Action" column (120px), and a formatter-driven status pill on "Status". Confirmed the footer stays correctly attached and aligned after a real page-2 navigation (not just initial render), and that pin offsets (`left: 50px`/`140px`) match across `th`/body/footer once "Action" and "Campaign" are both pinned, with a checkbox column present. The footer (`.footer-total`, stacked "Total:" / count layout) is wired to `selectedRowsChange` to show a live selection count — verified "20" → "2 selected" → "1 selected" → back to "20" on `clearSelection()` — concretely exercising the "consumer updates the slotted element from their own script" behavior called out in Task 2's sign-off.
    3. **`#pin-table`** — 8 columns, only "ID" and "Name" pinnable, confirming the footer renders correctly with a mix of empty and populated footer cells, including a "Total salary" figure under "Salary" computed live via `.reduce()` over `table.data` (not hardcoded) — verified as `$370,000` for the 3-row dataset.

> **Follow-up fix (2026-07-21, after the manual pass above):** the initial `tfoot td { border-top: 1px solid $boreal-stroke-default-light; }` rule doubled up with `tbody tr td`'s own `border-bottom: 1px solid $boreal-stroke-default-lighter` at the body/footer seam (both declarations render at the same pixel position under `border-collapse: separate`), producing a mismatched-color seam most visible when the last row is selected. Fixed by adding `tbody:has(+ tfoot) tr:last-child td { border-bottom: none; }` (bds-table.scss:255-257) so the footer's stronger border-top exclusively owns that seam — mirroring how the header's own `border-bottom` already exclusively owns the header/body seam. Scoped with `:has(+ tfoot)` (already used elsewhere in this file and in `bds-radio-card.scss`) so tables without a footer keep their normal last-row divider unaffected — verified via computed styles: footer-table last row `border-bottom-width: 0px`, no-footer-table last row unchanged at `1px solid $boreal-stroke-default-lighter`, and visually confirmed no doubled/mismatched line with the last row selected.

> **Bug found and fixed during this manual pass:** `#footer-toolbar-table` initially set `<bds-pagination items-per-page="5">` without adjusting `perPageOptions` (default `[10, 25, 50, 100]`); since 5 isn't a valid option, the pagination widget's own dropdown/range display silently fell back to showing "10"/"1-10 of 20 items" while the table's actual row-slicing correctly used 5 — a real display/data mismatch, not a table bug. Fixed in the playground by setting `perPageOptions = [5, 10, 25, 50]` via JS property (array-typed Stencil props aren't reliably parsed from a comma-separated HTML attribute). Worth keeping in mind for the Task 6 (server-side/loading) and Task 9 (virtualization) docs work, since both also pair `bds-table` with `bds-pagination`.

> **Amendment (2026-07-21, during execution):** two deviations from the literal task wording, both verified and intentional. (1) `col.querySelector(':scope > [slot="footer"]')` was replaced with `Array.from(col.children).find(child => child.getAttribute('slot') === 'footer')` — `@stencil/core/mock-doc` (the DOM `newSpecPage` actually renders against) throws a hard error on the `:scope` selector; the replacement has identical direct-child semantics and works in mock-doc, jsdom, and real browsers alike. (2) A real bug was found and fixed beyond the task's literal scope: because `appendChildNode` physically moves the footer node out of `bds-table-column` via `appendChild`, a naive re-query of `col.children` on every render finds nothing after the first render, causing Stencil to silently unmount `<tfoot>` on any unrelated re-render (e.g. row selection). Fixed by caching the discovered node per `colKey` in a private `_footerNodes` Map. Verified as a real regression (not theoretical) by an independent second pass: the fix was temporarily reverted, the regression test failed as predicted, then the fix was restored and the suite went green again.

**Unit test results:** 7/7 tests passing in `bds-table.footer.spec.ts`; full `bds-table` suite 133/133 passing. Independently reviewed by `@testing-subagent`, which verified test validity by breaking and restoring the caching fix rather than trusting the tests because they were green.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add slot-based column footer row"`

---

## Task 4 (was Task 19): `bds-table` — documentation for column footer **✅ COMPLETE**

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

- [x] `WithColumnFooter` story renders with 0 console errors; `<tfoot>` shows one `<td>` per column plus checkbox gap, correctly positioned. Live-total behavior confirmed end-to-end by clicking a real row checkbox: footer text transitioned "5 users" → "1 selected". MDX page confirmed: "Column footers" heading renders in the correct position (between Component Anatomy and Component preview, matching the TOC), limitations table renumbered sequentially (1–15, footer row removed) with no gaps, `#pinned-columns` cross-reference resolves to a real `### Pinned columns` heading.

> **Bug found and fixed during review of this task's output (2026-07-21):** the "Static footer content" MDX example was internally inconsistent — the source snippet only slotted `<span slot="footer">$1,234.00</span>` on the "Amount" column, but the "Rendered footer row" comment directly below it showed `<td>Total</td><td>$1,234.00</td>`, implying the "Item" column also had footer content slotted. The very next `<Callout>` explicitly says "a plain 'Total' label cell like the one shown above must be slotted on its own column the same way" — confirming the intent was for both columns to have footer content, matching the original playground scenario 1 exactly (ID: "Total" / Amount: "$1,234.00"). Fixed by adding `<span slot="footer">Total</span>` to the "Item" column in the source snippet so the example, the rendered-output comment, and the Callout are all consistent.

> **Structural refinement (2026-07-21):** the `WithColumnFooter` `<Canvas>` was moved out of the standalone `## Column footers` prose section and into `## Component preview` as its own `### Column footers` subsection (after "Custom cell formatter", before "Empty state") — matching how every other feature's live example already lives under Component preview (`### Pinned columns`, `### Custom cell formatter`, etc.) rather than embedded in prose. Storybook's heading slugger disambiguates the resulting duplicate "Column footers" title as `#column-footers` (h2, prose) and `#column-footers-1` (h3, Component preview canvas); both directions of the cross-link between them were verified to resolve correctly.

**Commit:** `git commit -m "docs(bds-table): EOA-15507 document slot-based column footer row"`

---

## Task 5 (was Task 20): `bds-table` — server-side mode and inline loading/skeleton visual **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** v2 Tasks 1 and 3 (`bds-pagination` watcher fix and `loading` prop) — already shipped in the v2 PR.
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify, or a sibling `_bds-table-skeleton.scss` partial imported by it)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` (new — JSX-returning skeleton render helpers, imported into `bds-table.tsx`; see code-organization decision below)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.skeleton.spec.ts` (new — follows the existing flat `__test__/` convention, not a nested `helpers/__test__/`)

> **Code organization (2026-07-21, decided with user):** skeleton rendering logic lives in a new `helpers/bds-table-skeleton.tsx` file, not inline as private methods on `bds-table.tsx` (Option 1) and not in the existing `utils/bds-table-utils.ts` (which stays pure-logic-only, no JSX, per its current contents — `compareValues`/`toCellString`/etc.). This is a deliberate first-time pattern for this codebase (confirmed via repo-wide search: no other component splits JSX-returning render helpers out of the main `.tsx` file today) — chosen for encapsulation and to keep the future `bds-skeleton` primitive extraction to "move one file," rather than hunting through `bds-table.tsx` for scattered loading-branches across `renderTh`/`renderToolbarLeft`/`renderCell`/etc. Scoped to `bds-table`'s own component folder (`bds-table/bds-table/helpers/`), **not** the `data-visualization/bds-table/` group-parent folder — `bds-table-column` renders no visible DOM and has no use for skeleton rendering, so a group-level shared folder would misrepresent this as shared code when it's `bds-table`-only. Task 5b's paginator-skeleton render function belongs in this same `helpers/bds-table-skeleton.tsx` file, not a separate one.

**Acceptance criteria:**

| Prop         | Type      | Default | Description                                                                        |
| ------------ | --------- | ------- | ---------------------------------------------------------------------------------- |
| `serverSide` | `boolean` | `false` | Disables local sort reordering; `bdsSort` still emits for the consumer to re-fetch |

- When `serverSide` is `true`, `sortedData`/`visibleRows`-aware equivalent returns rows unsorted; `handleSort` still emits `bdsSort` with the correct payload.
- Replace the `onLoadingChange` no-op stub with real behavior: when `loading` is `true`, `renderBody()` renders `loadingRows` rows composed of a private `renderSkeleton(variant, width, height)` helper — one per column plus the checkbox-column gap when `selectable` — instead of real data.
- **No new component is created.** The skeleton markup/CSS lives entirely inside `bds-table`'s own files, but is named and structured as if it were the future extracted primitive, to keep a later extraction cheap:
  - CSS classes: `.bds-skeleton` root class with `.bds-skeleton--rect`, `.bds-skeleton--text`, `.bds-skeleton--circle` modifiers (not `.bds-table__skeleton*`).
  - Custom properties: `--bds-skeleton-*` (not `--bds-table-skeleton-*`), matching the `bds-divider` `--bds-divider-*` convention.
  - Private TSX helper signature: `renderSkeleton(variant: 'text' | 'rect' | 'circle', width: string, height: string)` — a signature-for-signature match to the deferred `bds-skeleton` primitive's eventual public props.
  - Pulse animation, not a shimmer sweep (corrected 2026-07-21 — the original "shimmer/sweep" wording predates checking the actual Figma tokens, which specify only a single flat fill color, no second gradient/highlight color to sweep with):
    ```scss
    .bds-skeleton {
      background-color: var(--boreal-alpha-black-10);
      animation: bds-skeleton-pulse 1.5s ease-in-out infinite;
    }

    @keyframes bds-skeleton-pulse {
      0%, 100% {
        background-color: var(--boreal-alpha-black-10); // #272a2f1a, ~10% alpha
      }
      50% {
        background-color: var(--boreal-alpha-black-5); // #272a2f0d, ~5% alpha
      }
    }
    ```
    Animate `background-color` between the two real `--boreal-alpha-black-5`/`-10` tokens — **not** a CSS `opacity` animation layered on top of the already-translucent `background-color`, which would multiply the two alphas together (e.g. `opacity: 0.6` on a 10%-alpha fill yields an effective ~6% alpha, `opacity: 0.3` yields ~3% — nearly invisible against a white background, and does not match the clearly-visible bar in the Figma screenshot). Respects `prefers-reduced-motion`: `animation: none` and a static `background-color: var(--boreal-alpha-black-10)` (no fade).
- This single implementation satisfies both this task's server-side loading state and the standalone "skeleton placeholder" limitation.
- Does not combine `serverSide` with future virtualization-based infinite scroll (documentation-only note, no code enforcement needed).

> **Amendment (2026-07-21, scope expanded against Figma):** the design at [`node-id=1150-56028`](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29/-BOR--DSG-COMPONENTS-%E2%86%92-DATA-VISUALIZATION?node-id=1150-56028&m=dev) shows a full-page loading state, not just skeleton body rows. Confirmed with the user and expanded this task's scope accordingly — **the paginator-skeleton portion of that scope is split out into Task 5b below** (it's the one piece that hides a real mounted child component rather than just swapping `bds-table`'s own render output, so it gets its own focused implementation/test/manual-verify pass):
> - **In scope for this task (Task 5), matching Figma:** toolbar title (`renderToolbarLeft`) skeletonizes to a single bar when `loading=true` and a `subheading` is set; column header labels (`renderTh`/`renderThLabel`) skeletonize instead of showing real text; the checkbox column renders a small `.bds-skeleton--rect` square (header **and** body rows) instead of either a real checkbox or an empty gap — this supersedes the original "checkbox-column gap" wording above, which is no longer accurate.
> - **Explicitly out of scope (both 5 and 5b):** the Figma frame's "Skeleton - Collapse Row" variant (an expanded/nested row-detail skeleton panel, Figma nodes `_Row expanded` / `Collapse content`) — `bds-table` has no row-expansion feature at all (unscheduled Low-priority backlog item), so there is nothing to skeletonize there. Ignore this part of the design entirely.
> - **Tokens confirmed via Figma `get_variable_defs`** (all already exist in this codebase — no new tokens needed): skeleton bar fill `--boreal-alpha-black-10` (`#272a2f1a`); border/divider `--boreal-stroke-default-light` (already used elsewhere in `bds-table.scss`); radii `--boreal-radius-xs2` (2px, small elements) and `--boreal-radius-m` (12px, larger bars) — confirm exact per-element radius against the Figma screenshots below before finalizing SCSS, don't assume the mapping.
> - **Reference screenshots** (Figma asset URLs are short-lived, ~7 days — re-fetch via `get_screenshot`/`get_design_context` on these node IDs rather than relying on a stale link): full frame `1150:56028`, toolbar skeleton `1150:74502` (title bar + 3 square icon placeholders, 756×32), header cell skeleton `2:47879` ("Skeleton" variant of `_Header`), body cell skeleton `2:47477` ("Skeleton" variant of `_Cell`).

**Unit tests to cover:**

- `serverSide={true}` + sortable header click emits `bdsSort` but leaves row order unchanged.
- `loading={true}` renders exactly `loadingRows` rows of skeleton placeholder cells with correct column count.
- `loading={false}` (default) renders real data unaffected.
- The reduced-motion class/attribute is present on the skeleton markup when `loading={true}` (absorbs the manual-test reduced-motion criterion into an automated check, since there's no separate `bds-skeleton` spec file to hold it).
- `loading={true}` renders a skeleton bar in place of the toolbar `subheading` text (when `subheading` is set) and skeleton bars for each column header label.
- `loading={true}` renders a `.bds-skeleton--rect` in the checkbox column for both the header row and every body row when `selectable` is true.
- No `<tfoot>`/footer-related skeleton regressions when both `loading` and column footers are used together (footer content is static and consumer-owned per Task 3 — confirm it still renders normally, unaffected by `loading`).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `serverSide` + a sortable column; toggle `loading`.
- Validate:
  - [x] Given `serverSide=true`, when clicking a sortable header, then row order stays visually unchanged while the sort icon updates. Pass: visual + icon check. Verified in `src/index.html` playground (`#skeleton-table`) via `pnpm dev:components` + Playwright, using deliberately non-alphabetical seed data (Eva/Carol/Alice/David/Bob) so a real reorder would be visible if `serverSide` didn't work — clicking "Name" left row order exactly unchanged while the header's sort-icon showed active/ascending and `bdsSort` fired with `{colKey:"name",direction:"asc"}`.
  - [x] Given `loading=true`, when rendered, then skeleton placeholder rows, header labels, toolbar title, and checkbox-column squares all appear instead of real content. Pass: pulse animation visible, real data/labels hidden. Verified: exactly 31 `.bds-skeleton` elements render (20 body cells [5 rows × 4 cols] + 6 checkbox squares [header + 5 rows] + 4 header labels + 1 toolbar title, all counted and matched programmatically), `getComputedStyle` confirmed `animation-name: bds-skeleton-pulse` / `animation-duration: 1.5s` actively running; toggling `loading` back off restores all real content with 0 skeleton elements remaining.
  - [x] Given `prefers-reduced-motion: reduce` is simulated, when `loading=true`, then the pulse animation is replaced by a static muted background. Pass: no animation, tokens still applied. Verified via code review rather than browser emulation (the Playwright MCP tools available in this session don't expose `emulateMedia`) — confirmed `@media (prefers-reduced-motion: reduce) { .bds-skeleton { animation: none; background-color: var(--bds-skeleton-color, var(--boreal-alpha-black-10)); } }` is present and syntactically correct in `bds-table.scss`, a standard low-risk declarative CSS feature.

> **Fix applied during review (2026-07-21):** the implementation initially hardcoded `var(--boreal-alpha-black-10)`/`-5` directly in `.bds-skeleton`/`@keyframes bds-skeleton-pulse`, missing the plan's explicit `--bds-skeleton-*` custom-property requirement (matching the `bds-divider`/`--bds-divider-*` convention — confirmed by reading `bds-divider.scss`'s own `@prop` doc comments). Fixed by wrapping both colors in `var(--bds-skeleton-color, var(--boreal-alpha-black-10))` / `var(--bds-skeleton-pulse-color, var(--boreal-alpha-black-5))` and adding matching `@prop` JSDoc entries to `bds-table.scss`'s existing host-selector doc block (same location as `--bds-table-header-height` etc.), so consumers can now override the skeleton's colors the same way they can already override a divider's.

**Unit test results:** 20 new tests in `bds-table.skeleton.spec.ts` + 4 new `serverSide` tests in `bds-table.sort.spec.ts`. Full component suite: 11 spec files, 168/168 passing (independently re-confirmed). Coverage: 98.34% statements / 91.4% branches / 100% functions / 99.27% lines on `bds-table.tsx`; `helpers/bds-table-skeleton.tsx` at 100% all metrics. `prefers-reduced-motion` CSS could not be asserted via `newSpecPage` (no CSSOM/stylesheet evaluation in Stencil's mock-doc test runtime — confirmed no precedent anywhere in this codebase for asserting raw `.scss` from a spec); substituted DOM-level class-presence assertions and left the visual reduced-motion behavior to this task's manual-test checklist, where it was verified via code review (see above).

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add serverSide mode and inline skeleton loading visual"`

---

## Task 5b (new): `bds-table` — paginator skeleton during loading **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** Task 5 (shares the `renderSkeleton()` helper and `helpers/bds-table-skeleton.tsx` file Task 5 introduces)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` (modify — add the paginator-skeleton render function here, alongside Task 5's helpers, not in a new file)

**Context:** split out from Task 5 (see that task's 2026-07-21 amendment) because this is the one piece of the loading visual that doesn't just swap `bds-table`'s own render output — it must hide a real, separately-mounted child component (`bds-pagination`, slotted via `slot="paginator"`) and render a replacement in its place. That's a different risk profile (a11y: hidden-but-potentially-focusable content; state preservation across the loading transition) from the other "just render a skeleton bar instead" areas, so it gets its own focused pass.

**Design reference:** [`_paginator-skeleton`, node-id=1145-45839](https://www.figma.com/design/XIpn2Us0GpDNUxB1D2BY29/-BOR--DSG-COMPONENTS-%E2%86%92-DATA-VISUALIZATION?node-id=1145-45839) — title bar (left) + 6 square button placeholders (right), 1248×56 original size. Same tokens as Task 5 (`--boreal-alpha-black-10` fill, `--boreal-radius-xs2`/`--boreal-radius-m` radii — confirm per-element against the screenshot).

**Decision (confirmed with user 2026-07-21):** `bds-table` renders its own paginator-skeleton rather than adding real skeleton-rendering support to `bds-pagination` itself — keeps this addition single-component, matching the plan's stated architecture ("independently committable additions to `bds-table`"), and reuses the one shared `renderSkeleton()` helper instead of a second bespoke implementation. (`bds-pagination`'s own `loading` prop today only disables its nav buttons — confirmed via source read; not modified by this task.)

**Acceptance criteria:**

- When `loading` is `true` and a `bds-pagination` is slotted (`slot="paginator"`), hide it via `display: none` (do **not** unmount/remove it from the DOM — this preserves its internal state, e.g. `currentPage`/`itemsPerPage`, across the loading transition) and render a `bds-table`-owned paginator-skeleton in its place, built from the same private `renderSkeleton()` helper Task 5 introduces.
- The hidden `bds-pagination` must not be reachable via keyboard/tab order or assistive tech while hidden (verify `display:none` actually removes it from the accessibility tree — it should, but confirm rather than assume).
- When `loading` is `false`, the real slotted `bds-pagination` is shown again (`display` reset) with its state unchanged from before the loading transition; the paginator-skeleton is removed.
- No-op (no skeleton rendered, no visibility changes) when no `bds-pagination` is slotted at all.

**Unit tests to cover:**

- `loading={true}` with a slotted `bds-pagination` hides it (`display:none`) and renders the paginator-skeleton instead.
- `loading={false}` restores the real slotted paginator with its state intact (e.g. `currentPage`/`itemsPerPage` unchanged from before the loading transition).
- Hidden `bds-pagination` is not present in the accessibility tree / not focusable while `loading={true}`.
- No paginator-skeleton renders and no error occurs when `loading={true}` but no `bds-pagination` is slotted.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with a slotted `bds-pagination` (some non-default `currentPage`/`itemsPerPage`), toggle `loading`.
- Validate:
  - [x] Given `loading=true`, when rendered, then the real paginator is replaced by the skeleton placeholder (title bar + square buttons), matching the Figma reference. Pass: visual match, no real paginator visible or focusable.
  - [x] Given `loading` toggles back to `false`, when rendered, then the real paginator reappears with the same `currentPage`/`itemsPerPage` it had before `loading` was set. Pass: state preserved, no reset to page 1.

Verified in `src/index.html` playground (`#skeleton-table`, extended with a slotted `<bds-pagination items-per-page="2">` rather than a new example, per user request) via `pnpm dev:components` + Playwright. Set `currentPage = 2` on the real paginator, toggled `loading=true`: confirmed `pag.style.display === 'none'`, `.bds-table__paginator-skeleton` present with exactly 6 `.bds-skeleton--rect` squares plus a title bar, and `pag.currentPage` still reads `2` while hidden (proving it wasn't unmounted). Screenshot confirms close visual match to the Figma `_paginator-skeleton` reference. Toggling back to `loading=false` restored `pag.style.display === ''` and `currentPage === 2` unchanged — no reset to page 1. Required a dev-server restart mid-verification (same stale-`index.html`-snapshot behavior seen in prior tasks; a page reload/cache-bust alone is insufficient).

> **Three playground bugs found and fixed post-verification (2026-07-22, caught by the user):** (1) the slotted `<bds-pagination>` had no `total-items` set; since `#skeleton-table` used `data` mode at the time, `bds-table` never auto-wires a paginator's `totalItems` — that only happens in `rows` mode — so the paginator sat at its own default (`totalItems=0`) and rendered as empty ("0-0 of 0 items"), completely disconnected from the 5 real rows. Initially fixed by adding `total-items="5"`, later superseded (see (3) below). (2) The same `perPageOptions` gap found earlier in this plan (Task 3's playground work) recurred here: `items-per-page="2"` isn't in `bds-pagination`'s default `perPageOptions` (`[10, 25, 50, 100]`), so its own range display silently fell back and showed "1-5 of 5 items" instead of the correct 2-per-page range. Fixed the same way as before — setting `perPageOptions = [2, 10, 25, 50]` via JS property after mount (array-typed Stencil props aren't reliably parsed from an HTML attribute); this fix stands. (3) Deeper issue caught by the user after (1)/(2) landed: the table body always showed all 5 rows regardless of which page was selected — because `data` mode never auto-slices by page at all (only `rows` mode does), so the paginator was cosmetically functional but had zero effect on the table body. **Fixed by switching `#skeleton-table` from `table.data = [...]` to `table.rows = [...]`** (one-line change), which also let the manual `total-items="5"` attribute from fix (1) be removed entirely, since `rows` mode auto-wires `totalItems` from `rows.length` for free. Re-verified end-to-end: page 1 shows "Eva Torres"/"Carol Smith", clicking to page 2 (via a real Playwright click on the actual nested `<button>`, since `bds-pagination`'s ARIA-labelled wrapper isn't itself clickable) correctly slices to "Alice Martin"/"David Lee", and a full loading→loaded cycle afterward still shows the page-2 slice — confirming pagination state is genuinely preserved through the skeleton swap, not just a decorative property. Also confirmed the fixed 6-square paginator-skeleton (vs. this table's real 3-page control layout) is an accepted, deliberate approximation, not a bug — discussed and left as-is per Task 5b's Option A architecture (bds-table draws a generic placeholder rather than duplicating `bds-pagination`'s internal page-chunking layout logic).

**Unit test results:** 6 new tests added to `bds-table.skeleton.spec.ts` (new `describe('paginator skeleton', ...)` block). Full component suite: 11 spec files, 183/183 passing (independently re-confirmed). Coverage: 98.42% statements / 91.91% branches / 100% functions / 99.31% lines on `bds-table.tsx` (two pre-existing uncovered lines, unrelated to this task); `helpers/bds-table-skeleton.tsx` stayed at 100% all metrics.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add paginator skeleton during loading"`

---

## Task 5c (new): `bds-table` — toolbar-right skeleton completeness **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** Task 5 (shares `renderSkeleton()`/`helpers/bds-table-skeleton.tsx`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify, only if a hide-state style hook is needed beyond a plain `display:none`)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` (modify — add the filter/column-visibility skeleton render function here, alongside Task 5's helpers)

**Context:** discovered after Task 5 shipped, while reviewing it against the Figma `TableToolbar` reference (`node-id=1150-74502`), which shows **3** square skeleton placeholders on the toolbar-right side — Task 5 only skeletonized the toolbar-left title, leaving `renderToolbarRight()`'s filter/column-visibility buttons, and the `toolbar-actions` slot, fully real and interactive during `loading`. Confirmed with the user (2026-07-21) this was an underspecification in Task 5's original scope amendment, not a deliberate exclusion, and that it should be closed out — but as its own task rather than reopening the already-complete Task 5, matching how Task 5b was already split out for a similar reason.

**Decisions (confirmed with user 2026-07-21):**
- **Filter + column-visibility buttons:** skeletonize using the same swap-not-disable pattern already established by `renderTh`/the checkbox column — replace the real `<bds-button-group>` with skeleton squares entirely (not a `disabled` real button). This inherently removes interactivity (no `onClick` handler exists on a skeleton `<span aria-hidden="true">`) without needing a separate disabled-state mechanism, and matches the existing precedent throughout this component.
- **No new gating logic needed:** both buttons render unconditionally today whenever `hasToolbar` is true (there's no prop to hide them individually — see the `V2-19` research spike, amended the same day to note this dependency). The skeleton version inherits the same implicit gating by living inside `renderToolbarRight()` exactly where the real version does; no new condition to add.
- **`toolbar-actions` slot:** hide it (`display:none`) while `loading`, do not skeletonize it and do not disable-in-place. Reasoning: it's arbitrary consumer-owned content (commonly a single action button) whose real shape `bds-table` cannot know, so faking a skeleton shape risks a visual mismatch/jump when real content reappears — same reasoning already applied to the paginator in Task 5b. Also, its typical use (an action tied to the current dataset, e.g. export/add-row) is exactly the kind of interaction that shouldn't fire mid-load, so hiding (removing interactivity entirely) is the more defensible default over merely disabling.
- **Footer content: explicitly NOT touched by this task.** Already correctly handled by Task 3's original design (static, consumer-owned markup, never recomputed by `bds-table`) — footer is informational/non-interactive, so the "last known good value stays visible while refreshing" behavior it already has is acceptable, unlike the interactive toolbar-actions case. No change needed here; noted only to make clear this was a deliberate no-op, not an oversight.
- **Out of scope:** `V2-19`'s `filterable`/`columnLayoutToggle` opt-in-visibility props do not exist yet and are not part of this task — building them is unrelated, unscheduled Low-priority backlog work; this task only needs to make the *existing* always-rendered buttons skeletonize correctly during loading, matching their current real-render behavior exactly.

> **Correction (2026-07-22, caught by the user after this task's first implementation pass):** the original decisions above excluded `searchable`'s `<bds-search-bar>` from skeletonizing, on the reasoning that the Figma's 3rd toolbar-right square was unconfirmed. That exclusion was never actually agreed — the question of whether the search bar maps to the 3rd square was raised as an open question during planning and left unresolved, then silently decided as "leave untouched" when this task's plan section was first written, without re-surfacing that specific point for explicit sign-off. **Corrected scope: `searchable`'s `<bds-search-bar>` also skeletonizes as a third square** (same size, same wrapper) while `loading=true` — full parity with the Figma `TableToolbar` reference (3 squares total). `renderTableActionsSkeleton(searchable: boolean)` now conditionally renders a leading third square when `searchable` is true, matching how the real `<div class="__search-bar-slot">` already renders conditionally in the same position. `renderToolbarRight()`'s real-search-bar branch is now gated `this.searchable && !this.loading` (previously `this.searchable` alone). Fixed directly (small, well-understood change matching the existing pattern exactly) rather than a full subagent round-trip; one existing test (`'leaves the bds-search-bar rendering unaffected by loading (regression guard)'`) was rewritten to assert the corrected behavior (search bar absent + 3 skeleton squares while loading, real search bar restored when idle) and a new test added confirming exactly 2 squares render when `searchable` is `false`.

**Acceptance criteria:**

- When `loading` is `true`, the filter and column-visibility `<bds-button>`s inside `renderToolbarRight()`'s `<bds-button-group label="Table actions">` are replaced with skeleton squares (same helper/sizing approach as the checkbox-column skeleton) — two squares normally, or three when `searchable` is also `true` (see correction above), rendered only when `hasToolbar` is true (unchanged existing gate — no new condition).
- When `loading` is `false`, the real button-group (and real search bar, when `searchable`) render exactly as they did before this task (no regression).
- When `loading` is `true` and `[slot="toolbar-actions"]` has content, the slot wrapper is hidden via `display: none` (not unmounted — consistent with Task 5b's paginator-hide approach, in case slotted content holds its own internal state).
- When `loading` is `false`, the `toolbar-actions` slot content is shown again, unchanged.
- The footer is explicitly **not** touched by this task (regression guard — confirm it renders exactly as it did before this task, real/untouched, regardless of `loading`).

**Unit tests to cover:**

- `loading={true}` renders skeleton squares in place of the filter/column-visibility buttons; `loading={false}` renders the real buttons unchanged.
- `loading={true}` with `searchable={true}` renders a third skeleton square and no real `<bds-search-bar>`; `loading={false}` restores the real search bar unchanged (mode/async/minimized/clearable attributes intact).
- `loading={true}` with `searchable={false}` renders exactly two skeleton squares (no phantom third square).
- Filter/column-visibility skeleton only renders when `hasToolbar` is true (matches existing real-button gating — no skeleton renders on a table with no toolbar at all).
- `loading={true}` with slotted `toolbar-actions` content hides it (`display:none`); `loading={false}` restores it, unchanged from before the loading transition.
- No skeleton/hide behavior applied to `toolbar-actions` when nothing is slotted there (no-op, no error).
- Regression guard: footer content renders normally regardless of `loading` (unaffected by this task).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `subheading`, `searchable`, a `toolbar-actions`-slotted button, and column footer content all present; toggle `loading`.
- Validate:
  - [x] Given `loading=true`, when rendered, then filter/column-visibility AND the search bar all render as three skeleton squares (not real, not clickable), matching the Figma `TableToolbar` reference exactly, while `toolbar-actions` content is hidden entirely. Pass: no interactive filter/column-visibility/search/toolbar-actions controls visible or clickable during loading; visual match to Figma's 3-square toolbar.
  - [x] Given `loading=true`, when rendered, then the footer row (if present) still shows its real, last-known content unchanged. Pass: footer unaffected by loading, confirming the deliberate no-op.
  - [x] Given `loading` toggles back to `false`, when rendered, then filter/column-visibility buttons, the search bar, and `toolbar-actions` content all return to their real, fully-interactive state. Pass: no leftover skeleton, no leftover hidden state.

Verified in `src/index.html` playground (`#skeleton-table`, extended from Task 5's example rather than duplicated, per user request) via `pnpm dev:components` + Playwright, across two passes (before and after the search-bar correction above). Second pass required a dev-server restart mid-verification — the server was serving a stale pre-edit snapshot of `index.html` (same caching behavior seen earlier in this plan's execution; a plain page reload/cache-bust is insufficient, a full restart is required). Final confirmed state via DOM queries and a screenshot matching the Figma reference: `loading=true` → exactly 3 `.bds-skeleton--rect` squares in the toolbar-right zone, `bds-search-bar` absent from the DOM, `toolbar-actions-slot--hidden` class applied, footer cells read `["Total", "5"]` unchanged. Toggling back to `loading=false` restored the real button-group, the real search bar (`mode="search"` confirmed), and removed the hidden class — all confirmed via DOM query.

**Unit test results:** 8 new tests added to `bds-table.toolbar.spec.ts` (new `describe('toolbar-right skeleton (loading)', ...)` block), plus one test rewritten and one added during the search-bar correction. Full component suite: 11 spec files, 177/177 passing. Coverage re-measured after the correction: 98.36% statements / 91.7% branches / 100% functions / 99.28% lines on `bds-table.tsx` (uncovered lines 420/646 pre-existing, unrelated to this task); `helpers/bds-table-skeleton.tsx` (including `renderTableActionsSkeleton()`) and `bds-table-column.tsx` both at 100% all metrics.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 skeletonize toolbar filter/column-visibility buttons and hide toolbar-actions slot during loading"`

---

## Task 5d (new): `bds-table` — loading-visual refinements (row-count sync, footer skeleton) **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** Task 5, Task 5b (shares `renderSkeleton()`/`helpers/bds-table-skeleton.tsx`; reads the paginator via the same pattern as `hasPaginator`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/helpers/bds-table-skeleton.tsx` (modify — add a footer-cell skeleton render function)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify — `loadingRows` becomes optional)

**Context:** discovered post-Task-5c, during manual review of the `#skeleton-table` playground example. Two visual issues, both confirmed as genuine (not working-as-intended):
1. `loadingRows` defaults to a flat `5` regardless of the slotted paginator's `itemsPerPage` — when they differ (e.g. `items-per-page="2"` with the default 5 skeleton rows), the table visibly jumps size the moment real data replaces the skeleton. Confirmed low-risk to fix in both `serverSide` and non-`serverSide` modes: `itemsPerPage` is a purely client-side display setting, synchronously available on the slotted `<bds-pagination>` element regardless of where sorting/filtering happens.
2. Column footer content (`<tfoot>`) was explicitly left real/unskeletonized in Task 5c, reasoned as "arbitrary consumer content whose shape `bds-table` can't know." On review this reasoning doesn't hold up against precedent: body cells face the exact same "arbitrary shape" problem (a `col.formatter` can produce anything) and are already skeletonized with a generic text-bar approximation regardless. A fully-real footer row sitting directly under six pulsing skeleton body rows reads as visually inconsistent. Decision: apply the same generic-approximation treatment already accepted for body cells, rather than treating footer as a special case.

**Decisions (confirmed with user 2026-07-22):**
- **Row-count sync:** `loadingRows` becomes optional (`@Prop() readonly loadingRows?: number` — no default value in the decorator). Add a private `effectiveLoadingRows` getter: `this.loadingRows ?? this.el.querySelector<HTMLBdsPaginationElement>('bds-pagination[slot="paginator"]')?.itemsPerPage ?? 5`. Query the DOM directly (same pattern as the `hasPaginator` getter from Task 5b) rather than relying on `this.paginationEl` (which is only populated in `rows` mode) — this way the auto-derivation also benefits `data`-mode tables with an externally-wired slotted paginator, not just `rows` mode. Tables with no slotted paginator at all are completely unaffected (still fall back to `5`). An explicit `loadingRows` value the consumer sets always wins over the derived value.
- **Footer skeleton:** reuse the exact same `renderSkeleton('text', BODY_CELL_SKELETON_WIDTH, BODY_CELL_SKELETON_HEIGHT)` shape already used for body cells (not a new size/variant) — the footer row should read as "one more skeleton row," visually continuous with the body rows above it. Swap-not-disable, same as every other skeleton element in this component: real footer content is entirely replaced by the skeleton bar during `loading`, not dimmed or hidden.

**Acceptance criteria:**

- `loadingRows` is optional; when unset and a `bds-pagination` is slotted, the effective skeleton row count matches that paginator's `itemsPerPage`. When unset and no paginator is slotted, falls back to `5` (unchanged default behavior). When explicitly set, always wins regardless of any slotted paginator.
- `renderFooter()`/`renderFooterCell()` render skeleton bars (matching body-cell sizing) for every footer cell when `loading` is `true`, replacing real footer content entirely — footer column count/pinned-offset attributes stay consistent with the real footer's structure (mirrors how `renderSkeletonRows` already carries `SkeletonColumnMeta`'s pinned attributes for body cells).
- `<tfoot>` still only renders when `hasFooter` is `true` — `loading` does not cause a footer to appear on a table that has none.
- No change to tables without a footer or without a slotted paginator — both refinements are purely additive for the cases that need them.

**Unit tests to cover:**

- `loadingRows` unset + a slotted `bds-pagination` with `itemsPerPage=N` → exactly `N` skeleton rows render while loading.
- `loadingRows` unset + no slotted paginator → exactly `5` skeleton rows render while loading (regression guard, unchanged default).
- `loadingRows` explicitly set to a value → that value wins even when a slotted paginator has a different `itemsPerPage`.
- `loading={true}` with footer content present → footer cells render skeleton bars, not real content; `loading={false}` restores real footer content unchanged.
- `hasFooter=false` (no column has footer content) + `loading={true}` → no `<tfoot>` renders at all (regression guard).
- Pinned-column footer skeleton cells carry the same `data-pinned`/`data-col-key` attributes as their real counterparts (mirrors the existing pinned-footer-offset test from Task 3).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with a slotted `bds-pagination` (`items-per-page` different from `5`) and column footer content, toggle `loading`.
- Validate:
  - [x] Given a slotted paginator with `items-per-page="N"` and no explicit `loadingRows`, when `loading=true`, then exactly `N` skeleton rows render — no size jump when `loading` toggles back to `false`. Pass: row count matches before/after the loading transition.
  - [x] Given column footer content, when `loading=true`, then the footer row shows skeleton bars instead of real content, visually continuous with the skeleton body rows above it. Pass: no jarring real-content-under-skeleton-rows visual.

Verified in `src/index.html` playground (`#skeleton-table`, `items-per-page="2"`) via `pnpm dev:components` + Playwright. Toggling `loading=true` produced exactly 2 skeleton body rows (matching `itemsPerPage`, not the old flat 5) and 4 `.bds-skeleton--text` footer bars (one per real column, checkbox-gap cell correctly excluded); screenshot confirms the footer row now reads as visually continuous with the skeleton body rows above it, resolving the "crisp real text under pulsing skeletons" inconsistency. Toggling back to `loading=false` restored real content with the row count unchanged (`bodyRowCount: 2`, matching the real page-2 slice — no jump) and real footer text (`["Total", "5"]`) restored exactly.

**Unit test results:** 5 new tests added to `bds-table.skeleton.spec.ts` (row-count-derivation cases in the existing `body rows` block, plus a new `footer skeleton` block), plus 2 existing tests updated by the implementer to match the corrected footer behavior. Full component suite: 11 spec files, 188/188 passing (independently re-confirmed). Coverage: 98.44% statements / 92.33% branches / 100% functions / 99.32% lines on `bds-table.tsx` (two pre-existing uncovered lines, unrelated); `helpers/bds-table-skeleton.tsx` (including the new `renderFooterCellSkeleton()`) at 100% all metrics.

> **Real bug found and fixed during implementation:** the initial footer-skeleton wiring toggled a `<td>` between two render strategies — real content injected imperatively via a `ref` callback vs. skeleton content as declared JSX children — without giving either branch a distinct `key`. Traced through Stencil 4.42.1's vdom `patch()`/`isSameVnode` logic and confirmed this caused the skeleton to render *alongside* stale, vdom-invisible real content instead of replacing it, on the second and subsequent `loading` toggles (not on first render, which is why a naive single-render test wouldn't have caught it). Fixed by giving each branch a distinct `key` (`` `${col.colKey}-footer-skeleton` `` vs. the real-content key), forcing Stencil to fully destroy and recreate the cell on every toggle. A dedicated toggle-transition test (idle → loading → idle → loading → idle within one `newSpecPage` instance) was added specifically to catch a regression to the old no-key behavior, since neither of the single-state tests would have caught it.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 sync skeleton row count to pagination itemsPerPage and skeletonize footer content during loading"`

---

## Task 5e (new): `bds-pagination`/`bds-table` — fix stale pagination props, remainder-aware skeleton rows, `serverSide`+`rows` warning **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** none (bug found while reviewing Task 5d's `effectiveLoadingRows`, but the defect lives primarily in `bds-pagination`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/__test__/*.spec.ts` (modify/add — align with existing spec file naming in this directory)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify — `effectiveLoadingRows` remainder-aware math, `serverSide`+`rows` warning)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.skeleton.spec.ts` (modify)

**Context (found 2026-07-22, via `@frontend-subagent` review requested by the user):** `bds-table`'s `effectiveLoadingRows` getter (`bds-table.tsx:459-465`) reads `itemsPerPage` directly off the live slotted `<bds-pagination>` DOM element rather than caching a value from an event. This was assumed to reflect the paginator's current page size at all times. It does not: `itemsPerPage`/`currentPage` are declared `@Prop() readonly` on `bds-pagination` (`bds-pagination.tsx:76`, `:88`), and internal interactions with the component (picking a new page size from its own dropdown, clicking a page/prev/next control) only ever update private `@State` fields (`internalItemsPerPage`/`internalCurrentPage`) — `handleItemsPerPageChange` (`bds-pagination.tsx:302-312`) and `emitPageChange` (`bds-pagination.tsx:266-276`) both mutate internal state and emit `bdsPageChange` with the new value in the event detail, but never write back to the public prop. Any code that reads `paginationEl.itemsPerPage`/`paginationEl.currentPage` directly off the DOM — as `bds-table` does — sees only the value set at mount, forever, after the very first user interaction with the paginator. This is not a narrow race condition; it is the common case for any table with a page-size selector once a user touches it once.

This also silently breaks Task 5d's stated acceptance criterion ("the effective skeleton row count matches that paginator's `itemsPerPage`") for the entire lifetime of a session after the first page-size change, and is the direct root cause of `bds-table`'s `data`-mode skeleton sync being "accidentally correct only at mount" (that mode has no `bdsPageChange` listener of its own — see Task 6's docs note below — so the live DOM read is the *only* thing keeping it in sync, and that read is stale).

**Decision (confirmed with user 2026-07-22):** fix at the source — make `bds-pagination` a well-behaved "mutable prop, reflects current state" component, matching the existing `bds-table.selectedRows` precedent already in this codebase (`@Prop({ mutable: true }) selectedRows: string[]`, which "reflects the current selection back to itself on every internal mutation, so framework `v-model` bindings that read this prop off the DOM element ... stay in sync" — `bds-table.tsx:148-152`). Do not fix this by having `bds-table` cache the last `bdsPageChange` event detail instead — that would only patch `bds-table`'s one call site and leave `bds-pagination` itself lying about its own current state to any other consumer/DOM read (including this plan's own Task 5d manual-test scenario, which reads `pag.currentPage`/`pag.itemsPerPage` directly to assert state preservation across a loading toggle).

**Acceptance criteria:**

- `itemsPerPage`: `@Prop() readonly itemsPerPage: number = 10` → `@Prop({ mutable: true }) itemsPerPage: number = 10`. In `handleItemsPerPageChange` (`bds-pagination.tsx:302-312`), after computing `normalizedItemsPerPage`, also assign `this.itemsPerPage = normalizedItemsPerPage` (in addition to the existing `this.internalItemsPerPage = normalizedItemsPerPage`) before calling `emitPageChange`.
- `currentPage`: `@Prop() readonly currentPage: number = 1` → `@Prop({ mutable: true }) currentPage: number = 1`. In `emitPageChange` (`bds-pagination.tsx:266-276`), after computing `normalizedNext`, also assign `this.currentPage = normalizedNext` (in addition to the existing `this.internalCurrentPage = normalizedNext`).
- Verify the existing `@Watch('itemsPerPage')`/`@Watch('currentPage')` handlers (`bds-pagination.tsx:133-140`) do not create a feedback loop or extra render when the prop is written back to its own already-current value — Stencil's `@Watch` only fires on an actual value change, so writing the same normalized value the watcher would have produced is idempotent; confirm this holds with a test rather than assuming it.
- No change to `bds-pagination`'s externally-controlled behavior: setting `itemsPerPage`/`currentPage` from outside (e.g. a framework binding) must continue to work exactly as today via the existing `@Watch` handlers — this task only adds the missing write-back direction (internal interaction → prop), it does not touch prop-in → internal-state flow.
- `effectiveLoadingRows` (`bds-table.tsx:459-465`) becomes remainder-aware once `bds-pagination`'s props are reliable: query `totalItems` (already reliable — `@Prop() readonly totalItems: number = 0` on `bds-pagination`, `bds-pagination.tsx:48`, set only externally by the consumer and never mutated internally, so it was never stale) alongside the now-fixed `itemsPerPage`/`currentPage`. When `totalItems > 0`, compute `Math.max(1, Math.min(itemsPerPage, totalItems - (currentPage - 1) * itemsPerPage))` instead of returning raw `itemsPerPage`. Falls back to raw `itemsPerPage` when `totalItems` is `0`/unset (e.g. before any fetch has established a total). An explicit `loadingRows` value still always wins over any derived value, unchanged.
- Add a `serverSide`+`rows` warning to `bds-table.tsx`, mirroring the existing `checkDataRowsConflict` pattern (`bds-table.tsx:436-443`, which already warns via `this.logger.warn(...)` when both `data` and `rows` are set): log a warning when `this.serverSide` is `true` and `this.rows.length > 0`, since `rows` mode requires the full dataset client-side, which contradicts `serverSide`'s per-page-fetch premise. Check in the same places `checkDataRowsConflict` is already called (`componentWillLoad`, `onDataChange`, `onRowsChange`) — either extend that existing method or add a sibling one following the identical pattern.

**Unit tests to cover (in `bds-pagination`'s own spec suite):**

- Clicking a page/prev/next control updates `currentPage` (the public prop, read directly off the element), not just the rendered active-page indicator.
- Changing the items-per-page dropdown updates `itemsPerPage` (the public prop, read directly off the element).
- Externally setting `currentPage`/`itemsPerPage` via the prop (simulating a framework binding) still updates internal rendering exactly as before this fix (no regression to the existing controlled-mode behavior).
- No infinite loop / extra render cycle when a prop is written back to the same value the watcher would have derived (assert render count, not just final state).

**Unit tests to cover (in `bds-table`):**

- `effectiveLoadingRows` reflects a post-mount `itemsPerPage` change on the slotted paginator (the scenario that was silently broken before this fix).
- `effectiveLoadingRows` returns the remainder (not raw `itemsPerPage`) when `currentPage` is the last page and `totalItems` isn't an exact multiple of `itemsPerPage` (e.g. `totalItems=47`, `itemsPerPage=10`, `currentPage=5` → `7`).
- `effectiveLoadingRows` returns full `itemsPerPage` on a non-last page even when `totalItems` isn't an exact multiple (regression guard — remainder math only applies to the actual last page).
- `effectiveLoadingRows` falls back to raw `itemsPerPage` when `totalItems` is `0`/unset.
- An explicit `loadingRows` value still wins over the remainder-aware derivation.
- Setting both `serverSide={true}` and a non-empty `rows` logs a warning (mirrors the existing `data`+`rows` conflict test for `checkDataRowsConflict`).
- Setting `serverSide={true}` with `data` (no `rows`) does not log the warning (regression guard — only the `rows` combination is flagged).

**Manual test** _(not waiveable — @frontend-subagent must add the example cases to `src/index.html`, reusing the existing `#skeleton-table` example rather than creating a new one; format the description as a numbered steps list, not a paragraph, matching the convention applied across this file)_:

- Run `pnpm dev:components`; render the `#skeleton-table` playground example (slotted `bds-pagination`, `items-per-page="2"`).
- Validate:
  - [x] Given the paginator's items-per-page dropdown is changed to a new value (e.g. `10`), when reading `pag.itemsPerPage` directly from devtools/console, then it reflects the newly selected value, not the original `items-per-page="2"` attribute. Pass: `pag.itemsPerPage === 10` after the change.
  - [x] Given the same scenario, when `loading` is then toggled to `true`, then the skeleton renders 10 rows (matching the new page size), not 2. Pass: skeleton row count matches the current, not original, page size.
  - [x] Given a paginator navigated to a partial last page (e.g. 5 rows, `items-per-page="2"` → last page has 1 row), when `loading=true`, then the skeleton renders exactly 1 row, not 2. Pass: no over-render/shrink-on-load for the last page.
  - [x] Given a table with both `server-side` and `rows` set, when mounted, then a console warning is logged. Pass: warning visible, matching the existing `data`+`rows` warning's tone/format.

Verified in `src/index.html` playground (`#skeleton-table`, reused rather than duplicated) via `pnpm dev:components` + Playwright, exercising the real UI (dropdown open/click, page navigation) rather than direct property assignment. Confirmed all four checks live: `pag.itemsPerPage` read `10` immediately after a real dropdown interaction (mount attribute unchanged at `2`, as expected — attributes don't reflect); toggling `loading` after that change rendered exactly 5 skeleton rows (the dataset's full remaining count at `itemsPerPage=10`); navigating to the partial last page (`items-per-page="2"`, page 3, 1 remaining row) rendered exactly 1 skeleton row; the `serverSide`+`rows` conflict warning fired on page load for this table (which intentionally combines both, also exercising the pre-existing `serverSide` sort-disable test). 0 console errors; no stray re-render/normalization-warning spam confirming the prop write-back is idempotent in practice, not just in theory.

**Unit test results:** `bds-pagination`: 134 tests, 100% statements/branches/functions/lines. `bds-table` (whole component): 195 tests, 98.8% statements / 92.56% branches / 100% functions / 99.35% lines (two pre-existing uncovered lines, unrelated to this task — `applyCellFormatter`'s non-string branch and `renderTh`'s missing-`colKey` warning; this task's own changed code, `effectiveLoadingRows` and `checkServerSideRowsConflict`, is fully covered). Full `data-visualization` regression check: 370/370 passing across 25 suites. Independently re-confirmed by re-running both suites directly (170/170 combined `bds-pagination`+`bds-table.skeleton`, 195/195 full `bds-table`). One pre-existing test assertion was corrected as part of this fix (`bds-pagination.basics.spec.ts`): `instance.currentPage` was previously asserted to stay `1` after internal page navigation — that assertion was encoding the pre-fix bug itself; updated to assert `3`, matching the now-intentional write-back.

**Commit:** `git commit -m "fix(bds-pagination,bds-table): EOA-15507 write back pagination props, add remainder-aware skeleton rows, warn on serverSide+rows"`

---

## Task 6 (was Task 21): `bds-table` — documentation for server-side mode and loading state **✅ COMPLETE**

**Executor:** @documentation-subagent
**Depends on:** Task 5, Task 5b, Task 5c, Task 5d, Task 5e
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove the limitations-table rows covering server-side mode and skeleton placeholder loading (re-check current row numbering against the live `bds-table.mdx` before editing).
- New "Server-side mode" section, structured around an explicit **client (`rows`) vs. server (`data`+`serverSide`) mode comparison** — the two are easy to conflate (confirmed as a live point of confusion while reviewing this plan) and the existing `src/index.html` playground's `#skeleton-table` example (`rows` + `server-side` together) does not itself demonstrate real server-side pagination, only the `serverSide` sort-disable behavior — call this out explicitly so readers don't copy that combination as a server-mode template:
  - `rows`: table owns pagination, requires the full dataset client-side, slices internally. This is **client mode** — page/page-size changes re-slice synchronously, no `loading`/skeleton involvement needed or expected.
  - `data` + `serverSide`: consumer owns pagination, passes only the current page's rows, listens to the slotted `bds-pagination`'s own `bdsPageChange` directly (`bds-table` does not attach a listener to a `data`-mode paginator), fetches, and sets `data`/`loading` accordingly. This is **server mode** — this is the fetch-wiring example the section should center on.
  - Document that `serverSide` + `rows` together is an unusual, likely-unintended combination (`rows` requires the full dataset upfront, which defeats the point of server-side per-page fetching) — **as of Task 5e, this combination now logs a console warning** (mirroring the existing `data`+`rows` conflict warning), so document it as an actively-flagged anti-pattern, not a silent caveat.
- **`WithServerSideMode` story**: uses a **mock fetch** (`setTimeout` + an in-memory dataset sliced by the story's own code, not a real network call — matches the pattern already used by every other example in `src/index.html` and avoids introducing network flakiness into Storybook/Chromatic CI) wired to the slotted `bds-pagination`'s `bdsPageChange` event: on page/page-size change, set `loading=true`, "fetch" (simulated latency) the requested page's slice, then set `data` to that slice and `loading=false`. This is the first place in this component's docs/playground that exercises the full page-size-change → skeleton-row-count-sync path end-to-end (depends on Task 5e's fixes — verify the skeleton row count tracks a live page-size change during this story's simulated fetch, not just at mount, **and** correctly shrinks to the exact remainder on the dataset's final partial page).
- **`WithLoadingState` story**: demonstrates the full skeleton visual (toolbar, header, body, checkbox column, footer, paginator) via a manual loading toggle, not tied to pagination — mirrors the existing `#skeleton-table` playground scenario already manually verified in Tasks 5/5b/5c/5d.
- Document the skeleton row count as **remainder-aware as of Task 5e**: `effectiveLoadingRows` now accounts for `totalItems`/`currentPage` so the last page's skeleton matches its actual (possibly shorter) row count — no longer a caveat, this is correct behavior. Include the `WithServerSideMode` story's dataset size deliberately not being an exact multiple of its page size, so the last-page behavior is directly demonstrable.
- Document one remaining known approximation as an explicit caveat (not fixed in code — out of scope, per Task 5b's original architecture decision):
  - **Fixed 6-square paginator skeleton:** the paginator-skeleton placeholder (Task 5b) always renders a generic 6-square layout regardless of the real paginator's actual page count — a deliberate approximation to avoid duplicating `bds-pagination`'s internal page-chunking layout logic inside `bds-table`.
- No separate `bds-skeleton` doc page to reference — the loading-state section documents the skeleton visual as a `bds-table` implementation detail only.
- **Props ArgTypes — confirmed still missing as of 2026-07-14, do not skip:** `loading`, `loadingRows`, and this task's new `serverSide` prop are not currently in `bds-table.stories.ts`'s `argTypes` object, nor in the MDX `<ArgTypes include={[...]}>` list (verified directly against both files while auditing v2's docs). Add all three the same way `data`/`rowKey`/`selectedRows`/`searchable`/`selectedRowsChange` were added in the v2 plan's Task 15 follow-up. **Known pitfall from that same follow-up:** adding a name to the MDX `include` array alone does nothing — Storybook's `<ArgTypes>` silently drops any entry without a matching `argTypes` object entry in `.stories.ts`. Add to `argTypes` first, then the MDX `include` list, and verify via `pnpm dev:docs` that the rows actually render — don't just check the source diff.

**Manual test:** Run `pnpm dev:docs`, confirm sections/stories. Specifically verify `WithServerSideMode`'s simulated page-size change updates the skeleton row count correctly, and that navigating to the dataset's last (partial) page renders the correctly-shrunk skeleton row count rather than a full page's worth (Task 5e regression checks, end-to-end via the docs story rather than just the unit test).

- [x] Verified via Playwright against `pnpm dev:docs`: `WithServerSideMode`'s dataset (23 items, page size 10 → 10/10/3) navigated to page 3 mid-fetch showed `loading` flip to `true` with exactly 3 skeleton rows rendered (not 10), then real 3-row page data after ~600ms simulated latency — remainder-aware derivation confirmed end-to-end through a real fetch cycle, not just the unit test. `WithLoadingState` toggled the full skeleton visual (checkbox/body skeleton classes, hidden+skeleton paginator, `toolbar-actions` slot gaining the `--hidden` class without unmounting) with 0 console errors. The rendered Properties table on the component's docs page shows `loading`, `loading-rows`, `server-side` as real rows (not just present in MDX source), confirming the `argTypes`-then-`include` ordering pitfall was avoided.

Independently re-verified: both files lint clean (`eslint` on `bds-table.stories.ts`, 0 errors); diff reviewed directly — limitations table correctly renumbered 1–13 with the two shipped rows removed and stale "planned for v2" language corrected, new "Server-side mode"/"Loading state" MDX sections match the plan's client-vs-server comparison and remainder-aware/fixed-6-square-caveat requirements, `WithServerSideMode`'s mock fetch listens directly to the paginator's `bdsPageChange` (not relying on any table-side auto-wiring, correctly reflecting that `data` mode has none), `argTypes` entries for `loading`/`loadingRows`/`serverSide` added before the MDX `include` list (correct order per the known pitfall). `apps/boreal-docs`'s pre-existing, unrelated `tsc --noEmit` failure (`tsconfig.json`'s `--ignoreDeprecations` value) predates this task and was not introduced by it.

**Commit:** `git commit -m "docs(bds-table): EOA-15507 document server-side mode and loading state"`

---

## Task 7 (was Task 22): `bds-table` — row virtualization **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** Task 1, Task 5
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/package.json` (verify only — `@tanstack/virtual-core@^3.17.1` already present)

**Acceptance criteria:**

| Prop/State                     | Type                            | Default | Description                                                 |
| ------------------------------ | ------------------------------- | ------- | ----------------------------------------------------------- |
| `virtual` (Prop)               | `boolean`                       | `false` | Opt-in row virtualization; `false` renders exactly as today |
| `virtualizer` (State, private) | `Virtualizer<Element, Element>` | —       | Drives the windowed row set                                 |

- Per Utility Discovery, do not reuse `VirtualScrollController` — wire `@tanstack/virtual-core`'s `Virtualizer` directly against Stencil's render cycle. Even a fixed/reworked `VirtualScrollController` could not be reused here — its entire architecture (`MutationObserver` + `querySelectorAll` over a consumer's pre-existing light-DOM children) is built to manage markup a consumer already placed, not to drive a declarative render function like `renderBody()`.
- **No proven reference implementation exists to copy.** Build directly against `@tanstack/virtual-core`'s public API rather than porting an existing pattern from another codebase (verified during v2 planning: neither this repo's `aq-table-core.tsx` reference nor Aqua's own list/dropdown virtualization solves the "reduce upfront row-creation cost for a real `<table>`" problem this task needs).
- `componentDidLoad`, when `virtual` is `true`, initializes with `count` from whichever row-set is active (`data`, `visibleRows`, or `serverSide`-supplied `data`), `getScrollElement` pointing at `.bds-table__wrapper`, `estimateSize: () => 48`, `measureElement` for variable-height rows.
- `renderBody()` iterates only `getVirtualItems()` when `virtual` is `true`, with a spacer sized via `getTotalSize()`, using **explicit `key={rowId}` on every virtualized `<tr>`** — currently absent from `renderBody()` even without virtualization. Without it, Stencil's JSX diffing falls back to positional reconciliation, risking row-identity-cache mismatches. Add this regardless of virtualization, since the underlying data (`sortedData`/`visibleRows`) can already reorder on sort/filter/page-change today.
- Log via `Logger` if `virtual=true` and `maxHeight === ''`.
- **Sticky-header workaround dropped (revisited 2026-07-22, before implementation started):** the plan previously assumed, based on TanStack Virtual's general issue-tracker claims (TanStack/virtual#585, #591, #640), that combining a sticky `<thead>` with a windowed `<tbody>` is a documented-broken pattern, and planned to disable `<thead>`'s `position: sticky` while `virtual=true` ("Option B"). Before implementing, this was empirically validated against `bds-table`'s exact CSS configuration (`border-collapse: separate`, sticky thead, spacer-row virtualization) via two Playwright-driven spikes in `src/index.html` (left in place, clearly labeled, not committed — see "SPIKE" sections): round 1 with fixed-height rows found the sticky `<thead>` stayed pinned across the full 5,000-row scroll range with zero divergence between `wrapper.scrollHeight` and `getTotalSize()`. Round 2, using variable-height rows with a real `measureElement` callback and adversarial rapid scroll-jumps into never-rendered territory (the scenario most likely to trigger the upstream failure mode), found a real but purely JS-side transient divergence between `wrapper.scrollHeight` and the virtualizer's `getTotalSize()` bookkeeping (up to ~950px, resolving within one `requestAnimationFrame`) — but the sticky `<thead>` never broke, jumped, or detached in any of 21 logged frames across both stress runs, because CSS `position: sticky` is computed by the browser against the real laid-out DOM, not against the virtualizer's internal accounting. **Decision: keep `<thead>`'s sticky behavior active while `virtual=true` — no conditional override.** Caveat: both spikes used a vanilla `<table>` with `requestAnimationFrame`-coalesced corrections, not Stencil's own render/state-update scheduling — so this task's manual test (below) must independently confirm the same holds against the real, built `bds-table` component before this decision is considered fully verified, not just against the vanilla-JS proxy.

**Unit tests to cover:**

- `virtual={false}` (default) renders all rows unchanged (regression guard).
- `virtual={true}` renders only the windowed subset.
- `virtual={true}` without `maxHeight` logs a warning.
- Spacer sized to `getTotalSize()` present when virtualized.
- Each virtualized `<tr>` carries the correct `key={rowId}`; row/checkbox selection state stays attached to the correct row after a sort or filter while `virtual=true`.
- `<thead>`'s sticky styling/classes are unaffected by `virtual` — identical whether `virtual` is `true` or `false` (regression guard reflecting the dropped Option B — confirms no conditional override was accidentally left in place).
- **(Added 2026-07-22, regression test for the crash bug fixed above):** with `virtual={true}` and `virtualizer` still `undefined` (i.e. before `componentDidLoad`'s deferred `initVirtualizer()` has run), `renderBody()` renders `renderVirtualPlaceholder()` — a single bounded spacer row — not the full `sortedData` via `renderAllRows()`. Assert the rendered `<tbody>` contains exactly one `<tr>` regardless of dataset size (e.g. assert this holds identically for both a 10-row and a 5,000-row dataset), and that its spacer height equals `VIRTUAL_ESTIMATED_ROW_HEIGHT * sortedData.length`.
- Once `virtualizer` is initialized (post-`componentDidLoad`), `renderVirtualPlaceholder()` is no longer used — `renderVirtualRows()` takes over (regression guard distinguishing the two branches).

**Manual test** _(not waiveable — this is the real-component confirmation the dropped-Option-B decision above depends on, not just a general feature check)_:

- Run `pnpm dev:components`; render `bds-table` with `virtual` + `max-height` + ~5,000 rows, including a mix of variable-height row content (to exercise `measureElement`, mirroring spike round 2's setup).
- Validate:
  - [x] Given `virtual=true` with `maxHeight` set, when scrolling through 5,000 rows, then only a small window of `<tr>` elements exists in the DOM at any time (inspect via devtools). Pass: DOM node count stays roughly constant.
  - [x] Given `virtual=true` without `maxHeight`, when mounted, then a console warning appears. Pass: warning visible.
  - [x] Given a virtualized table, when sorting or filtering while rows are selected, then the correct rows remain checked (not rows that happen to share the same scroll position). Pass: selection follows the data, not the position.
  - [x] Given `virtual=true` with variable-height rows, when scrolling normally and when jumping rapidly to distant/unmeasured scroll positions (mirroring spike round 2's stress scenario), then the header stays visually pinned at all times with no jump, detachment, or flicker — confirming the dropped-Option-B decision holds against the real Stencil-rendered component, not just the vanilla-JS spike. Pass: header remains stable through both normal and adversarial rapid scrolling.

Verified by the user directly in `src/index.html`'s `#virtual-table`/`#virtual-warning-table` playground section (`pnpm dev:components`) rather than via automated Playwright — the implementing subagent stalled mid-Playwright-verification and was redirected to hand off manual instructions instead (its code/playground output was independently reviewed and confirmed sound before handoff: no sticky-header override present anywhere, `tsc --noEmit` clean on the changed file). Results: rendered `<tr>` count oscillated in a bounded 13–27 range while scrolling through all 5,000 rows rather than a fixed constant — confirmed as expected, not a regression, given `overscan: 10` (up to 20 extra rows beyond whatever's visible) combined with variable row heights (1/3/5-line "Notes" content, ~48/96/144px) changing how many rows fit the 500px viewport at any given scroll position; the important signal (no unbounded growth as scrolling continued deeper into the dataset) held. Selection-survives-sort, the no-`maxHeight` warning, and the sticky-header-through-rapid-jumps check all passed as specified.

> **Follow-up fix (2026-07-22, found by the user after initial manual verification):** two real bugs surfaced through continued manual testing, both fixed directly (small, well-understood changes) rather than a full subagent round-trip:
> 1. **Stencil dev-mode warning — "state changed during componentDidLoad()"** for `virtualizer`/`virtualVersion`. `initVirtualizer()` needs `.bds-table__wrapper` (only resolved after the first render), so it can't move to `componentWillLoad()` the way Task 1's analogous fix did. Fixed by deferring the `componentDidLoad()` call site through a microtask (`void Promise.resolve().then(() => this.initVirtualizer())`), letting `componentDidLoad()` return before the `@State()` mutations happen.
> 2. **Stencil dev-mode warning — "state changed during rendering"** for `virtualVersion`, escalating in real Chromium testing to confirm it was a bounded-but-wasteful burst (21 cascading full-table re-renders during initial mount, one per row as `measureElement` corrected each newly-rendered row's real height against the `estimateSize` guess — not a literal infinite loop, verified via Playwright with 700+ stress-scroll frames producing no runaway growth). Root cause: `onChange` bumped `virtualVersion` directly and synchronously on every firing, and `measureElement`'s corrections happen from a `ref` callback invoked during Stencil's render/commit phase. Fixed by coalescing all `onChange` firings within a microtask window into a single deferred re-render (new `scheduleVirtualRerender()` method, using a `_virtualRerenderScheduled` guard flag) instead of one per correction. Verified via Playwright: warning count dropped from 26 (mostly this one, repeating) to 3 (all pre-existing/unrelated), with 0 regressions across the full 211-test `bds-table` suite.
>
> **Critical bug found by the user immediately after (2026-07-22): the browser crashed on first load with the full 5,000-row dataset; reducing to 1,000 rows loaded successfully.** Root cause, confirmed by tracing the actual render sequence: `renderBody()`'s branch condition was `this.virtual && this.virtualizer !== undefined ? renderVirtualRows() : renderAllRows()`. `initVirtualizer()` cannot run before `componentDidLoad()` (needs `.bds-table__wrapper`, which only exists after the table's own first render commits) — so the *very first render*, unconditionally, fell through to `renderAllRows()` and mounted the **entire unbounded dataset** as real DOM nodes (5,000 `<tr>`s, several `<td>`s each, some with multi-line formatter-generated child `<div>`s) before the virtualizer had ever been created. Only the *second* render (after the deferred `initVirtualizer()` completed) actually virtualized down to a bounded window. This gap has existed since Task 7 was first implemented — it was not introduced or worsened by the two warning fixes above. It directly explains the crash: a one-time synchronous construction of 5,000+ DOM nodes was expensive enough to crash a tab at 5,000 rows while surviving at 1,000. **Not a candidate fix for Task 10's `maxClientRows`** — that guardrail is explicitly non-blocking (a console warning only, rendering unaffected) and is scoped to discourage *not* using `virtual`/`serverSide`, the opposite of this bug, which occurs precisely when `virtual={true}`. Fixed by adding a new `renderVirtualPlaceholder()` method: when `virtual` is `true` but `virtualizer` is `undefined`, render a single bounded spacer `<tr>` (sized via a new `VIRTUAL_ESTIMATED_ROW_HEIGHT` module constant × `sortedData.length`, approximating the real scrollbar height so there's no visible jump once the virtualizer initializes moments later) instead of `renderAllRows()`. `estimateSize: () => 48` in `initVirtualizer()` was refactored to reference the same constant, removing the previous duplication. Verified via Playwright with the real 5,000-row dataset: page loads without crashing, exactly 18 `<tr>` elements exist in `<tbody>` on first paint (16 data rows + 2 spacers, not 5,000), growing to a bounded 27 after a 2-second rapid-scroll stress pass, 0 new console warnings, full 211-test suite still passing with no regressions.

**Unit test results:** 4 new tests added to `bds-table.virtual.spec.ts` (new `describe('pre-virtualizer render (placeholder)', ...)` block) covering: exactly one placeholder `<tr>` regardless of dataset size (asserted at both 10 and 5,000 rows), the placeholder spacer's `style.height` equals `VIRTUAL_ESTIMATED_ROW_HEIGHT * rowCount`, and a before/after transition confirming the placeholder is replaced by `renderVirtualRows()`'s real windowed output once `initVirtualizer()` runs. Used a `jest.spyOn` on `BdsTable.prototype.initVirtualizer` to deterministically freeze the pre-init state, since `newSpecPage()` already flushes the deferred microtask by the time it resolves — timing alone can't observe this window. Full component suite: 12 spec files, 215/215 passing (independently re-confirmed). Coverage: 97.73% statements / 89.81% branches / 100% functions / 99.36% lines on `bds-table.tsx`.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add opt-in row virtualization"`

---

## Task 8 (was Task 22b): `bds-table` — throttle pin-offset recomputation during virtualized scroll **✅ COMPLETE**

**Executor:** @frontend-subagent
**Depends on:** Task 7
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)

**Context:** `componentDidRender` already runs a `querySelectorAll('th[data-pinned]')` + `offsetWidth` read on _every_ render to compute pinned-column offsets. With virtualization enabled, every scroll-driven re-render triggers this same DOM query and layout read, reintroducing exactly the kind of per-frame cost virtualization is meant to remove.

> **Reconfirmed still needed (2026-07-22, before implementation started):** re-evaluated after Task 10 introduced auto-enabled virtualization — confirmed this is still real and, if anything, more important now than when originally scoped. TanStack Virtual's `onChange` (and this component's own `scheduleVirtualRerender()` coalescing, added during Task 7) only reduces render *count* during bursts (e.g. initial-mount settling) — it does not change what runs *inside* a render that does happen, and continuous scrolling still shifts the virtualizer's visible window (and triggers a real re-render) far more often than a one-time burst. Task 10 also means tables can now become virtualized without the consumer ever setting `virtual` themselves — raising, not lowering, the bar for virtualized scrolling to be smooth by default, since these consumers made no deliberate performance trade-off to opt into.
>
> **Correctness gap found in the original guard condition, folded into acceptance criteria below:** "recompute only when `pinnedColKeys` or `columns` change" misses that pin offsets are derived from each `<th>`'s live `offsetWidth`, which can also change from a browser window resize (responsive column widths) without `pinnedColKeys`/`columns` themselves changing — under the original wording, a resize while pinned columns are showing could leave stale, misaligned offsets. `bds-table.tsx` itself has no existing `ResizeObserver` to build on, but `bds-pagination.tsx` (`resizeObserver` field, `setupResizeObserver()`, `bds-pagination.tsx:27,189-190`) already establishes the pattern this codebase uses for exactly this kind of case — reuse that pattern, not a novel one.

**Acceptance criteria:**

- Guard the existing pin-offset computation so it only recomputes when `pinnedColKeys` or `columns` actually change, not on every scroll-triggered re-render while `virtual=true` (or `effectiveVirtual=true` post-Task-10).
- Also recompute on an actual layout-affecting resize (new `ResizeObserver` on the table wrapper element, following `bds-pagination.tsx`'s existing `resizeObserver`/`setupResizeObserver()` pattern) so pinned-column offsets don't go stale after a responsive width change that isn't accompanied by a `pinnedColKeys`/`columns` change. Clean up the observer in `disconnectedCallback`, mirroring how this component already tears down its other observers/listeners there.
- No behavior change when `virtual=false` (default) and no pinned columns are present — the guard should be a pure optimization, not alter output.

**Unit tests to cover:**

- Pin-offset computation does not re-run on a scroll-only re-render while `virtual=true` and `pinnedColKeys`/`columns` are unchanged.
- Pin-offset computation still runs correctly when a column is pinned/unpinned or the column set changes.
- Pin-offset computation re-runs when the table wrapper resizes, even with `pinnedColKeys`/`columns` unchanged (regression test for the correctness gap above).
- `ResizeObserver` is disconnected in `disconnectedCallback` (no leaked observer).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render a virtualized table with several pinned columns and ~5,000 rows.
- Validate:
  - [x] Given a virtualized table with pinned columns, when scrolling rapidly, then scrolling stays smooth with no visible lag or incorrect pin offsets. Pass: compare scroll smoothness before/after this fix using the browser's Performance panel.
  - [x] Given a virtualized table with pinned columns, when the browser window is resized, then pinned-column offsets stay correctly aligned (not stale from before the resize). Pass: visual check, pinned column headers/cells stay flush with their real rendered position after resizing.

Verified via Playwright against `#virtual-table` (Task 7's example, temporarily given pinnable `id`/`name` columns for this verification) and `#pin-table` (non-virtualized regression check, unaffected). Scrolled through all 5,000 virtualized rows: newly-scrolled-in rows correctly received their pinned `left` offsets. Resize scenario (the specific correctness gap found during planning): narrowed the wrapper 750px→550px with `email` also pinned — `name`'s width recomputed 142px→75px and `email`'s offset correctly recomputed 252px→185px on both `<th>` and all live `<td>`, confirming the `ResizeObserver` path re-reads live widths rather than leaving stale values.

> **Real correctness gap found during implementation (2026-07-22), beyond the plan's original single-guard wording:** a single-phase guard (skip the whole computation unless `pinnedColKeys`/`columns` changed) broke pinned-column alignment during virtualized scrolling — TanStack Virtual swaps in fresh, differently-keyed `<td>` elements as new rows scroll into view, and those never received their `left` style since the guard's tracked state hadn't changed. Fixed by splitting `updatePinnedColumnOffsets()` into two phases: a guarded, expensive **read** phase (the `querySelectorAll` + live `offsetWidth` pass, only reruns when `pinnedColKeys`/`columns` change by reference or `force=true` is passed from the resize observer) and an unconditional, cheap **write** phase (re-applies cached offsets from a `_pinOffsetsByColKey` map to whatever `td[data-col-key]` elements currently exist, every call). This keeps the expensive part throttled while guaranteeing newly-rendered virtualized rows always get styled correctly.

**Unit test results:** 5 new tests added in a new `bds-table.pin-offsets.spec.ts` file, covering: the guarded phase skipping on a virtualizer-only re-render (via a `querySelectorAll` selector-string spy) while the cheap apply phase still runs, pin/unpin and column-set-change regression correctness, resize-triggered force recompute (via the mocked `ResizeObserver`'s captured callback), and `disconnectedCallback` calling `resizeObserver.disconnect()`. 7 pre-existing spec files also required a `setupResizeObserverMock()` addition (mechanical test-environment fix, not new test logic — `bds-table.tsx` now unconditionally creates a `ResizeObserver`, so every spec mounting `BdsTable` needs the mock or `newSpecPage()` throws). Full component suite: 13 spec files, 220/220 passing (independently re-confirmed by re-running the suite directly, separate from both the implementing and testing subagents' own reports). Coverage: 97.58% statements / 89.51% branches / 100% functions / 99.39% lines on `bds-table.tsx` (two pre-existing uncovered lines, unrelated to this task).

**Commit:** `git commit -m "perf(bds-table): EOA-15507 throttle pin-offset recomputation during virtualized scroll"`

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
- **No sticky-header limitation to document** — Task 7 dropped the originally-planned "disable sticky thead while `virtual=true`" workaround after empirical validation showed the combination doesn't break against `bds-table`'s actual configuration (see Task 7's "Sticky-header workaround dropped" note). The header stays sticky in both `virtual={true}` and `virtual={false}` — document this as a positive feature (sticky header works normally, even with virtualization enabled), not as a caveat.
- **Document the `loadingRows` + `virtual` constraint (decided 2026-07-22, no code change):** the loading skeleton's rows are never routed through the virtualizer — `renderBody()`'s loading branch always renders `effectiveLoadingRows` as real, unvirtualized `<tr>` elements, regardless of `virtual`. This is fine as long as `loadingRows`/`effectiveLoadingRows` stays page-sized (its normal derivation, post-Task-5e), but explicitly warn against setting `loadingRows` to a large explicit value (e.g. a full expected large-dataset row count) while `virtual={true}` — doing so would materialize that many real skeleton rows unvirtualized, defeating the DOM-node-bounding purpose of `virtual` at exactly the moment (the loading transition) it matters most.
- **Document `virtual` + server mode as alternative, not complementary, strategies (decided 2026-07-22, no code change, no live example — guidance-only):** `virtual`'s `count` is `sortedData.length` (`bds-table.tsx`, `initVirtualizer`), which in `data`+`serverSide` mode only ever equals the current page's row count — server-side pagination's entire premise is that the browser never holds more than one page's worth of rows at once. Combining `virtual` with server mode is not broken (nothing warns or misbehaves), it simply provides little-to-no benefit, since there's rarely enough in-memory data in that mode to need windowing. Document `virtual` as intended for large in-memory datasets (`rows` mode, or a large un-paginated `data` array) — an alternative to server-side pagination for solving the "large dataset" problem, not a feature meant to be stacked on top of it. No dedicated story/example needed for this combination; a prose note in the "Virtualization" section is sufficient.
- **Document that `estimateSize`/`overscan` are internally fixed, not configurable (decided 2026-07-22, no code change — considered and deliberately not exposed as props):** row height is estimated internally (48px) and self-corrects per row via `measureElement` once rendered, so variable-height content is fully supported without any consumer configuration; overscan (extra rows rendered beyond the viewport) is fixed at `10`, TanStack Virtual's own commonly-recommended default. One or two sentences in the "Virtualization" section noting neither is currently exposed as a prop is sufficient — no need to justify the decision in depth.
- New `WithVirtualization` story using a ~5,000-row generated dataset, demonstrating that the header remains sticky/pinned while scrolling in that mode.
- **Document automatic virtualization above `maxClientRows` (added 2026-07-22, see Task 10's rewritten scope):** a new subsection (e.g. "Automatic virtualization for large datasets") explaining that `bds-table` auto-enables `virtual` internally once the active row count exceeds `maxClientRows` (default `1000`), even if the consumer never set `virtual` themselves — a safety measure motivated by a real precedent of users adding excessive rows to a table in another internal component library without realizing the consequences. Cover: it only applies when `serverSide` is `false` (in `serverSide` mode `data` normally holds just one page, so there's rarely enough in-memory data to matter); it's sticky (once triggered, stays on even if the dataset later shrinks back under the threshold); it overrides an explicit `virtual={false}` (Stencil can't distinguish "left at default" from "explicitly set to the default value," and this is a safety guardrail, so the safer behavior wins); and it does **not** eliminate sort/selection/memory/transfer cost, which still scales with dataset size regardless — `serverSide` remains the complete answer for very large datasets. Cross-link with the "Layout constraints" section (Task 11).

**Manual test:** Run `pnpm dev:docs`, confirm section/story.

**Commit:** `git commit -m "docs(bds-table): EOA-15507 document row virtualization"`

---

## Task 10 (was Task 24): `bds-table` — large-dataset guardrail (`maxClientRows`, auto-enable `virtual`)

**Executor:** @frontend-subagent
**Depends on:** Task 5, Task 7
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Context (rescoped 2026-07-22, before implementation started):** originally scoped as a purely advisory, non-blocking console warning. Reconsidered after the user raised whether this was worth keeping at all now that virtualization (Task 7) is fully working — the initial read was that it risked being speculative/overengineered (unvalidated default threshold, advisory-only, no evidence of real demand). That changed once the user surfaced **real precedent: users adding excessive rows to a table in another internal component library at the same company.** Given that precedent, and the further finding that Task 7's own crash fix does **not** protect this scenario at all (`virtual` is opt-in and defaults to `false`, so a consumer who doesn't know to set it gets zero benefit from anything built in Task 7), a passive console warning was judged insufficient — the same population that didn't know to reach for a virtualization/server-side pattern elsewhere is unlikely to be watching devtools output here either. Decision: **auto-enable virtualization internally, non-destructively (no data hidden or dropped), when the threshold is crossed and `serverSide` isn't already handling it** — keep the sort/selection/memory-cost warning for the remaining risk auto-virtualization can't fix. Explicitly rejected: silent truncation (hides real data — a data-integrity anti-pattern, worse than the original perf problem), a hard block/throw (too disruptive for a design-system component, especially with a threshold that's still not independently validated by the team), and visible truncation with a UI indicator (a genuine product/UX decision needing its own design pass, out of scope for this engineering-only pass).

**Acceptance criteria:**

| Prop            | Type     | Default                                                                                          | Description                                                                                                                       |
| --------------- | -------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `maxClientRows` | `number` | `DEFAULT_MAX_CLIENT_ROWS` (new module-level `const DEFAULT_MAX_CLIENT_ROWS = 1000;`, `bds-table.tsx`, mirroring the existing `VIRTUAL_ESTIMATED_ROW_HEIGHT` constant pattern from Task 7 — one place to bump the default later, no duplicated literals) | Threshold above which `virtual` is auto-enabled internally (if not already active) and a non-blocking warning about remaining sort/selection/memory/transfer cost is logged |

- New private `effectiveVirtual` getter: `this.virtual || (!this.serverSide && this.activeRowCount > this.maxClientRows)`, where `activeRowCount` follows the same `this.rows.length > 0 ? this.rows.length : this.data.length` pattern already used elsewhere in this component to resolve the active row source. The public `virtual` prop itself is **never mutated** — it stays `readonly`; auto-enabling only changes which internal rendering path runs.
- Every internal call site that currently branches on the raw `this.virtual` to decide whether virtualization actually runs switches to `this.effectiveVirtual`: `renderBody()`'s `virtual`/placeholder/`renderVirtualRows` branch, `componentDidLoad()`'s deferred `initVirtualizer()` call, `componentWillRender()`'s `syncVirtualizerOptions()` guard, and `checkVirtualMaxHeight()`'s warning gate (a consumer who never touched `virtual` still needs the `maxHeight` reminder if auto-enable just kicked in without a bounded scroll container).
- Auto-enable only applies when `serverSide` is `false` — matches Task 9's existing "`virtual` and `serverSide` are alternative, not complementary, strategies" guidance; in `serverSide` mode `data` normally holds only the current page, so there's rarely enough in-memory data to justify virtualizing.
- Auto-enable is **sticky, not reactive to shrinking**: once `effectiveVirtual` has been `true` at any point in the component's lifetime, it stays `true` even if the dataset later shrinks back below `maxClientRows` — avoids flicker/jank from toggling virtualization on and off as row count fluctuates near the boundary; harmless to leave on for a smaller dataset (it still renders correctly, just computes a full-sized window).
- Auto-enable **takes priority over an explicit `virtual={false}`** — Stencil has no way to distinguish "prop left at its default" from "prop explicitly set to the same value as the default," so there is no reliable way to carve out an opt-out exception. Since this is a safety guardrail protecting against a real, precedented failure mode, prioritizing the protective behavior is the correct default. No escape-hatch prop is added for this — out of scope, consistent with this plan's established bias against speculative API surface (see the `estimateSize`/`overscan` non-configurability decision in Task 9).
- Re-evaluate `effectiveVirtual` (and call the already-idempotent `initVirtualizer()` if it now resolves `true`) from: initial mount (`componentDidLoad`, once `.bds-table__wrapper` exists), `@Watch('data')`, `@Watch('rows')`, `@Watch('serverSide')`, and `@Watch('maxClientRows')` — any prop change that could shift the threshold comparison.
- Logging via the existing `Logger` service (three distinct cases):
  - `serverSide={true}`: no warning at all.
  - `serverSide={false}` and `virtual` was already explicitly `true`: log only the sort/selection/memory/transfer-cost warning (DOM cost is already handled by the consumer's own explicit choice), recommending `serverSide` for very large datasets. This is the original Task 10 warning, unchanged in substance.
  - `serverSide={false}` and `virtual` was `false` (i.e., this task's auto-enable just activated): log a distinct warning stating virtualization was automatically enabled because the row count exceeded `maxClientRows`, **plus** the same sort/selection/memory/transfer-cost caveat — auto-enabling `virtual` does not fix that half of the problem.
- No longer "rendering is unaffected either way" (the original scoping's wording) — auto-enabling `virtual` does change what actually renders (windowed vs. full). Still non-blocking in the sense that it never throws, halts rendering, or drops/hides any data.

**Unit tests to cover:**

- `activeRowCount > maxClientRows`, `serverSide=false`, `virtual` not set → `effectiveVirtual` resolves `true`; the rendered `<tbody>` uses the virtualized/placeholder path, not `renderAllRows()`.
- Same scenario logs both the "auto-enabled" warning and the sort/selection-cost warning.
- `activeRowCount > maxClientRows`, `serverSide=false`, `virtual={true}` explicitly set → only the sort/selection-cost warning logs (no "auto-enabled" wording).
- `activeRowCount > maxClientRows`, `serverSide={true}` → no warning at all; `effectiveVirtual` stays `false` unless `virtual` was explicitly set.
- `activeRowCount <= maxClientRows` → no warnings; `effectiveVirtual` matches the raw `virtual` prop exactly (no auto-enable below threshold).
- Explicit `virtual={false}` with `activeRowCount > maxClientRows` and `serverSide=false` → `effectiveVirtual` still resolves `true` (regression guard for the "auto-enable overrides explicit false" decision).
- Auto-enable is sticky: dataset grows past the threshold (auto-enables), then shrinks back below it → `effectiveVirtual` remains `true` (regression guard for the "sticky, not reactive to shrinking" decision).
- `maxClientRows` explicitly set to a custom value changes the threshold accordingly (regression guard that the prop, not just the constant, is respected).
- `maxClientRows` defaults to `1000` when unset (regression guard confirming `DEFAULT_MAX_CLIENT_ROWS` is wired correctly to the prop decorator).

**Manual test** _(not waiveable — this guardrail exists specifically because a passive/waiveable check already proved insufficient for this exact scenario in another internal library)_:

- Run `pnpm dev:components`; render `bds-table` with ~1,500 rows, no explicit `virtual`/`serverSide` set.
- Validate:
  - [ ] Given 1,500 rows with neither `virtual` nor `serverSide` set, when mounted, then the table renders via the virtualized path (bounded `<tr>` count, not all 1,500) and two console warnings appear: one noting virtualization was auto-enabled, one noting remaining sort/selection/memory/transfer cost. Pass: bounded DOM node count confirmed via devtools/script query, both warnings visible, no crash.
  - [ ] Given the same table, when explicitly setting `virtual={false}`, then virtualization still activates (auto-enable overrides). Pass: bounded `<tr>` count even with `virtual={false}` explicitly set.
  - [ ] Given `serverSide={true}` with the same row count, when mounted, then no warnings appear and no auto-enable occurs (unless `virtual` was also explicitly set). Pass: full render (if `virtual` not set) or virtualized render (if it was), no console warnings.

**Commit:** `git commit -m "feat(bds-table): EOA-15507 add maxClientRows guardrail with auto-enabled virtualization"`

---

## Task 11 (was Task 25): `bds-table` — documentation for the guardrail

**Executor:** @documentation-subagent
**Depends on:** Task 10
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)

**Acceptance criteria:**

- `maxClientRows` added to the props table — description reflects the rescoped behavior (auto-enables `virtual` above the threshold, not just a passive warning).
- Row-count ceiling documented in "Layout constraints", alongside the 800px minimum-width note — rewritten to describe auto-enable, not just "a warning fires."
- Cross-link to Task 9's new "Automatic virtualization for large datasets" subsection (under "Virtualization") rather than duplicating that explanation — "Layout constraints" states the threshold/prop, the "Virtualization" section carries the full behavioral explanation (sticky, overrides explicit `virtual={false}`, doesn't apply under `serverSide`, doesn't eliminate sort/selection cost).
- Briefly note the real-world motivation (a precedent of users adding excessive rows in another internal component library) only if it reads naturally as user-facing guidance — otherwise keep the doc focused on behavior, not internal history; use judgment on tone rather than copying the plan's internal rationale verbatim.

**Manual test:** Run `pnpm dev:docs`, confirm the update, and confirm the "Layout constraints" ↔ "Virtualization" cross-link resolves correctly.

**Commit:** `git commit -m "docs(bds-table): EOA-15507 document maxClientRows guardrail"`

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

**Commit:** `git commit -m "test(bds-table): EOA-15507 close mutation-testing gate for v3 changes"`

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
- **Decision:** deferred to a separate future spike/ticket. Task 7 abo
  ve is unaffected — it builds its own direct `@tanstack/virtual-core` integration without depending on or interfering with `VirtualScrollController`.
- Full research: `ai-work/research/2026-07-06-shared-virtualization-utility.md`. Related bug tracked at `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`. Neither is scheduled against this plan.

---

## Execution order

1 → 2 (sign-off) → 3 → 4 → 5 → 5b → 5c → 5d → 5e → 6 → 7 → 8 → 9 → 10 → 11 → 12.

Groups: dataset/internal pagination (1) → footer, gated on sign-off (2–4) → server-side mode + inline skeleton visual, table-surface then paginator then toolbar-right completeness then loading-visual refinements then the `bds-pagination` stale-prop fix (5–5e) → docs for all (6) → virtualization, including its pin-offset throttling follow-up (7–9) → guardrail (10–11) → mutation-testing gate for everything in this plan (12).
</content>
