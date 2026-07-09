---
ticket: EOA-14935
component: bds-table
status: in progress
created: 2026-07-06
---

# bds-table v2 High-Priority Limitations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Close the six "Priority: High" limitations in `bds-table.mdx`, plus the built-in search bar, skeleton loading, and a large-dataset guardrail, following the `EOA-10576` column-API spike's resolved decisions wherever they apply.

**Ticket brief:** [`ai-work/tickets/EOA-14935-bds-table-v2.md`](../tickets/EOA-14935-bds-table-v2.md)

**Architecture:** Ten features land as independently committable additions across four existing Stencil components (`bds-table`, `bds-table-column`, `bds-pagination`, `bds-tooltip`), each guarded by its own prop and none altering v1's default (all-off) behavior. Three features require prerequisite work in sibling components before the `bds-table`-side work can start. The loading/skeleton visual is implemented as a private, table-scoped render helper this sprint rather than a new reusable primitive — see "Deferred: extract `bds-skeleton` primitive" near the end of this document for the rationale and future extraction path.

**Tech Stack:** Stencil (TSX + scoped SCSS), `@tanstack/virtual-core` (already a direct dependency), Jest + Stryker for the two-phase unit-test/mutation-score gate.

---

## Files to create / modify

| File                                                                                                               | Notes                                                                                              |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx`               | Modify — fix `totalItems` watcher snap-back bug, fix empty-state literal `"1"`, add `loading` prop |
| `packages/boreal-web-components/src/components/data-visualization/bds-pagination/types/*.ts`                       | Modify — add `loading` to `IPagination`                                                            |
| `packages/boreal-web-components/src/components/data-visualization/bds-pagination/__test__/*.spec.ts`               | Modify — cover the above                                                                           |
| `apps/boreal-docs/src/stories/data-visualization/bds-pagination/bds-pagination.stories.ts`                         | Modify — add `loading` to `argTypes` (drives the MDX `<ArgTypes>` table)                           |
| `apps/boreal-docs/src/stories/data-visualization/bds-pagination/bds-pagination.mdx`                                | Modify — no prose change expected beyond what ArgTypes auto-generates; verify                      |
| `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx`                               | Modify — add `show()`, `hide()`, `anchorTo()` `@Method()`s and a `manual` prop                     |
| `packages/boreal-web-components/src/components/overlays/bds-tooltip/types/ITooltip.ts`                             | Modify — add method signatures and `manual` prop type                                              |
| `packages/boreal-web-components/src/components/overlays/bds-tooltip/__test__/*.spec.tsx`                           | Modify — cover the new methods and `manual` mode                                                   |
| `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.mdx`                                                | Modify — "Programmatic control" section                                                            |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`               | Modify — all `bds-table`-side features, including a private table-scoped skeleton render helper    |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts`             | Modify — new prop/event types                                                                      |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss`              | Modify — overflow-tooltip truncation, pinned footer cells, pinnable hover state                    |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/*.spec.ts`          | Modify/create — cover all features                                                                 |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table-column/bds-table-column.tsx` | Modify — no new prop; footer is slot-driven (see Task 17)                                          |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx`                                          | Modify — remove shipped limitation rows, add new sections/prop tables                              |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`                                   | Modify — new stories per feature                                                                   |
| `packages/boreal-web-components/targets/vue-output-target.ts`                                                      | Modify — add `bds-table` to `componentModels` for `v-model:selectedRows`                           |
| `packages/boreal-web-components/package.json`                                                                      | No change expected — `@tanstack/virtual-core@^3.17.1` already present; verify only                 |

---

## Utility Discovery (mandatory gate — performed before finalizing tasks below)

| Feature area                          | Search performed                                                                                                                                   | Candidate found                                                                                                                                                                                          | Fit                                                                                                                                                                                                                                                                                                                                                                                               | Decision                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Row virtualization                    | `packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts`, `package.json`                                                     | `VirtualScrollController<TItem>` (wraps `@tanstack/virtual-core`'s `Virtualizer`), used by `bds-search-bar`                                                                                              | **Partial.** `@tanstack/virtual-core` is already a direct dependency (`^3.17.1`) — no new install needed. But `VirtualScrollController` keeps every child mounted and only toggles `display:none` + absolute positioning; it does not reduce DOM node count. This is the exact mechanism the team flagged as the root cause of `bds-search-bar`'s `LargeSuggestionsList` slowdown/deploy timeout. | Reuse the underlying `@tanstack/virtual-core` dependency directly, not `VirtualScrollController`. `bds-table` needs true conditional JSX rendering (only `getVirtualItems()`-selected rows exist as `<tr>` nodes) which the light-DOM-child model cannot provide for Stencil-rendered rows. No shared-utility extension planned — the two use cases have different DOM ownership models. |
| Overflow-tooltip singleton delegation | `src/utils/helpers/overlays/`, `src/utils/dom/`, `src/mixins/anchored.mixin.ts`                                                                    | `getOffset.ts` only; `anchoredMixin`'s `componentDidLoad`/`onBeforeLoad` auto-discovers a trigger once and calls `subscribe()` unconditionally, with no matching "unsubscribe"                           | Does not fit as-is; the auto-discovery path is actively wrong for a singleton reused across hundreds of cells                                                                                                                                                                                                                                                                                     | New `manual` prop on `bds-tooltip` needed to skip auto-discovery entirely (see Task 5) — this is a small, scoped addition to `bds-tooltip.tsx` only, not a change to the shared `anchored.mixin.ts` (keeps blast radius contained).                                                                                                                                                      |
| Custom cell / footer rendering        | `bds-table.tsx` (`applyCellFormatter`, ~lines 244–249); design playground reference showing footer as a plain boolean toggle, not a computed value | Existing `applyCellFormatter` handles `string \| HTMLElement` via `ref`-based `appendChild`; `slot="empty-state"`/`slot="toolbar-actions"` already establish the light-DOM-slot-moved-into-place pattern | Footer should follow the **slot** pattern, not a new callback prop                                                                                                                                                                                                                                                                                                                                | No new `footer` prop on `bds-table-column`. Consumers slot static markup (`<span slot="footer">...</span>`) as a child of `<bds-table-column>`; `bds-table` moves that node into the matching `<tfoot>` cell once, same mechanism as existing slots. See corrected Task 17.                                                                                                              |
| Skeleton loading rows                 | Repo-wide search for `skeleton`/`shimmer` in `boreal-web-components` and `boreal-style-guidelines`                                                 | None found outside the existing TODO comment in `bds-table.tsx`                                                                                                                                          | Does not fit                                                                                                                                                                                                                                                                                                                                                                                      | **Revised after team discussion (2026-07-08):** defer building a standalone reusable `bds-skeleton` primitive. Implement the loading visual as a private, table-scoped render helper directly in `bds-table.tsx`/`.scss` this sprint, using the exact naming/class structure the future primitive would use (`.bds-skeleton`/`.bds-skeleton--rect\|text\|circle`, `--bds-skeleton-*` tokens, a `renderSkeleton(variant, width, height)` helper signature) so a future extraction is a near-mechanical move rather than a rewrite. See revised Task 20 and "Deferred: extract `bds-skeleton` primitive" near the end of this document. |
| Large-dataset guardrail logging       | `bds-table.tsx` (`private readonly logger = new Logger()`, line 36)                                                                                | `Logger` service already imported and used                                                                                                                                                               | Fully fits                                                                                                                                                                                                                                                                                                                                                                                        | Reuse `this.logger.warn(...)`.                                                                                                                                                                                                                                                                                                                                                           |
| Dataset/pagination wiring             | `bds-table.tsx` `componentDidLoad`/`componentWillLoad` (existing `querySelectorAll('bds-table-column')` + `MutationObserver` pattern)              | Same slotted-child-query pattern already used for columns                                                                                                                                                | Fully fits                                                                                                                                                                                                                                                                                                                                                                                        | Reuse the identical pattern for querying the slotted `bds-pagination`.                                                                                                                                                                                                                                                                                                                   |
| Vue v-model wiring                    | `packages/boreal-web-components/targets/vue-output-target.ts` `componentModels`                                                                    | Direct `event.detail` → `targetAttr` mapping, no transform support; existing entries use a dedicated `valueChange`-style event, never a domain event carrying a richer payload                           | `bdsSelect`'s `{selectedIds, row}` payload cannot drive `componentModels` directly                                                                                                                                                                                                                                                                                                                | Add a dedicated `selectedRowsChange: EventEmitter<string[]>` event on `bds-table`, matching the `valueChange` convention already used by `bds-search-bar` etc. See corrected Task 7 and new Task 8.                                                                                                                                                                                      |

---

## Review of feature ordering (re-examined per explicit request)

Kept largely as originally sequenced, with the new `bds-skeleton` primitive and Vue wiring slotted in at their natural dependency points:

- Prerequisite fixes first (pagination, tooltip) since two later features depend on them.
- The two no-blocker quick wins (`selectedRows`, `searchable`) land early for momentum, followed immediately by their own natural companions (Vue wiring for `selectedRows`; the pinnable-hover CSS fix, which is unrelated to any other feature and can land whenever).
- The loading/skeleton visual is now a table-scoped render helper rather than a new primitive, so the old "`bds-skeleton` must exist before the loading task" ordering constraint no longer applies — Task 20 is self-contained.
- Virtualization stays last among the rendering-touching phases (dataset, server-side/loading, footer, virtualization) because it is the only one that must be aware of all other row-source modes at once. Footer and loading are structurally independent of `<tbody>` row-windowing (a sibling `<tfoot>` and an early-return skeleton guard, respectively), so ordering them before virtualization does not require rework later.
- The large-dataset guardrail comes last regardless, since it reads both `serverSide` and `virtual`.

---

## Task 1: `bds-pagination` — fix `totalItems` watcher snap-back

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx` (modify, line ~127)

**Acceptance criteria:**

- `onTotalItemsChange` re-clamps `this.internalCurrentPage` using `this.normalizePage(this.internalCurrentPage)`, not `this.normalizePage(this.currentPage)`.
- JSDoc on the watcher explains why `internalCurrentPage`, not `currentPage`, is the correct base — matching the existing pattern in `onCurrentPageChange`/`onItemsPerPageChange`.

**Unit tests to cover** (`__test__/bds-pagination.basics.spec.ts` or equivalent):

- Setting `totalItems` after navigating past page 1 preserves the current page when it still fits.
- Setting `totalItems` to a smaller value clamps the current page down based on the page the user is actually on.

**Manual test** _(waiveable)_:

- Scenario: render `bds-pagination` with `total-items="50"`, navigate to page 3, then set `totalItems = 30` via script.
- Run `pnpm dev:components` and validate:
  - [ ] Given the pagination is on page 3 with 50 total items, when `totalItems` is set to 30 via script, then the display stays on the correct clamped page derived from page 3. Pass: displayed page matches `normalizePage(3)` against the new total.

**Commit:** `git commit -m "fix(bds-pagination): EOA-14935 use internal current page in totalItems watcher"`

---

## Task 2: `bds-pagination` — fix empty-state literal "1"

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx` (modify, line ~470)

**Acceptance criteria:**

- Replace the `isEmpty ? <bds-typography variant="helper">1</bds-typography> : ...` branch with `this.getPaginationControls()` unconditionally — its buttons are already `disabled` via `isPrevButtonDisabled`/`isNextButtonDisabled` when `totalPages === 0`.

**Unit tests to cover:**

- `totalItems={0}` renders no literal `"1"` anywhere in the controls.
- `totalItems={0}` renders navigation buttons disabled.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`, render `bds-pagination` with `total-items="0"`:
  - [ ] Given `total-items="0"`, when rendered, then no stray "1" appears and controls are visibly disabled. Pass: visual inspection confirms no orphaned "1".

**Commit:** `git commit -m "fix(bds-pagination): EOA-14935 remove stray literal in empty state"`

---

## Task 3: `bds-pagination` — add `loading` prop

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/types/*.ts` (modify)

**Acceptance criteria:**

| Prop      | Type      | Default | Description                                                                                |
| --------- | --------- | ------- | ------------------------------------------------------------------------------------------ |
| `loading` | `boolean` | `false` | Disables all navigation buttons and the items-per-page select while a request is in flight |

- When `true`, all nav `<bds-button>`s and the items-per-page `bds-select` are forced `disabled`, independent of `totalPages`.
- JSDoc required.

**Unit tests to cover:**

- `loading={true}` disables every nav button regardless of page/total state.
- `loading={true}` disables the items-per-page select.
- `loading={false}` (default) leaves existing behavior untouched.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`, toggle `loading` via script on a rendered `bds-pagination`:
  - [ ] Given `loading=true`, when rendered, then all controls appear disabled. Pass: clicking has no effect.

**Commit:** `git commit -m "feat(bds-pagination): EOA-14935 add loading prop"`

---

## Task 4: `bds-pagination` — tests consolidation and docs

**Executor:** @testing-subagent (tests) then @documentation-subagent (docs)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-pagination/__test__/*.spec.ts` (finalize)
- `apps/boreal-docs/src/stories/data-visualization/bds-pagination/bds-pagination.stories.ts` (modify — add `loading` to the `argTypes` object; this is what actually drives the MDX `<ArgTypes>` table, not the `.mdx` file itself)
- `apps/boreal-docs/src/stories/data-visualization/bds-pagination/bds-pagination.mdx` (verify — confirm no additional prose references the old buggy behavior)

**Acceptance criteria:**

- All tests from Tasks 1–3 pass the two-phase gate (coverage, then mutation score per `.agents/memory/mutation-testing-workflow-decisions.md` — confirm with the team whether the bar is 100% or 90%, document any surviving mutants).
- `loading` appears correctly in the rendered Storybook props table (verify via `pnpm dev:docs`, not just by editing the `.mdx` file).

**Manual test:** Run `pnpm dev:docs` and confirm `loading` appears in the properties table with correct description/default.

**Commit:** `git commit -m "test(bds-pagination): EOA-14935 cover watcher fix, empty state, and loading prop"`

---

## Task 5: `bds-tooltip` — add `manual` mode and `show()`/`hide()`/`anchorTo()` methods

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx` (modify)
- `packages/boreal-web-components/src/components/overlays/bds-tooltip/types/ITooltip.ts` (modify)

**Context (why this is more than adding three methods):** `anchoredMixin`'s `componentDidLoad` → `onBeforeLoad()` auto-discovers a trigger element from the DOM once at mount and calls `subscribeToTrigger()` → `bds-tooltip`'s own `subscribe()`, which unconditionally attaches `mouseenter`/`mouseleave`/`focusin`/`focusout` listeners with **no matching unsubscribe**. A singleton tooltip reused across hundreds of table cells cannot go through this path repeatedly without leaking listeners, and the very first auto-discovered trigger (some arbitrary ambient element) is meaningless for this use case.

**Acceptance criteria:**

| Prop     | Type      | Default | Description                                                                                                                                                       |
| -------- | --------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `manual` | `boolean` | `false` | When `true`, skips automatic trigger discovery/subscription entirely; the consumer drives visibility and anchoring exclusively via `show()`/`hide()`/`anchorTo()` |

- `bds-tooltip` overrides `componentDidLoad()` locally (not in the shared `anchored.mixin.ts`) to skip calling the inherited auto-discovery (`onBeforeLoad()`) when `manual` is `true`.
- `@Method() async show(): Promise<void>` delegates to the existing bound `this.show` (already bound in `componentWillLoad`).
- `@Method() async hide(): Promise<void>` delegates to the existing bound `this.hide`.
- `@Method() async anchorTo(el: HTMLElement): Promise<void>` sets `this.triggerSlot = el` directly — it must **not** call `subscribe()`/`subscribeToTrigger()`, since `manual` mode's consumer (bds-table) owns hover delegation itself.
- All three methods still respect the existing `disabled` guard.
- `ITooltip` updated with the `manual` prop and three method signatures, each with JSDoc. No `any` types.

**Unit tests to cover** (`__test__/bds-tooltip.spec.tsx` or equivalent):

- `manual={true}` does not attach any hover/focus listeners to whatever element `onBeforeLoad` would otherwise have auto-discovered.
- `show()`/`hide()` work without a prior hover/focus event.
- `anchorTo(el)` reassigns `triggerSlot` to `el` without attaching any listeners to `el`.
- Calling `anchorTo()` repeatedly with different elements does not accumulate listeners on any of them.
- `disabled={true}` + programmatic `show()` stays hidden, in both manual and default modes.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render a `manual` `bds-tooltip`, call `anchorTo()`/`show()`/`hide()` from the console against different target elements in sequence.
- Validate:
  - [ ] Given `manual=true`, when `show()` is called without hovering, then the tooltip becomes visible. Pass: visible in DOM.
  - [ ] Given `anchorTo(elementB)` after previously anchoring to `elementA`, when hovering `elementA` afterward, then nothing happens (no leftover listener). Pass: no tooltip appears when hovering `elementA`.

**Commit:** `git commit -m "feat(bds-tooltip): EOA-14935 add manual mode and show/hide/anchorTo methods"`

---

## Task 6: `bds-tooltip` — documentation

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.mdx` (modify)

**Acceptance criteria:**

- New "Programmatic control" section documents `manual`, `show()`, `hide()`, `anchorTo(element)` with a singleton-tooltip code example matching `bds-table`'s future use (Task 11).

**Manual test:** Run `pnpm dev:docs`, confirm the new section renders.

**Commit:** `git commit -m "docs(bds-tooltip): EOA-14935 document manual mode and programmatic control"`

---

## Task 7: `bds-table` — external controlled row selection (`selectedRows`)

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop/Event                   | Type                     | Default | Description                                                                                                                               |
| ---------------------------- | ------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `selectedRows` (Prop)        | `string[]`               | `[]`    | External/controlled row IDs; syncs into internal selection state                                                                          |
| `selectedRowsChange` (Event) | `EventEmitter<string[]>` | —       | Emits the current selection as a plain array, for v-model binding (Task 8); distinct from `bdsSelect`, which carries `{selectedIds, row}` |

- `@Watch('selectedRows')` sets `this.selectedRowIds = new Set(newValue)`.
- `componentWillLoad` initializes `this.selectedRowIds` from `this.selectedRows` when non-empty.
- Every internal mutation of `selectedRowIds` (row click, select-all, clear) also emits `selectedRowsChange` with the resulting array, alongside the existing `bdsSelect` emission — the two events fire together, `bdsSelect` for rich event data, `selectedRowsChange` for simple v-model sync.
- Internal `@State private selectedRowIds` remains the source of truth for rendering.

**Unit tests to cover** (`__test__/bds-table.selection.spec.ts`):

- Setting `selectedRows` after mount updates internal selection state and checkbox rendering.
- `getSelectedRows()` reflects externally-set IDs.
- Every internal selection change emits both `bdsSelect` and `selectedRowsChange` with matching IDs.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render a selectable `bds-table`, set `table.selectedRows = [...]` via script, and log `selectedRowsChange`.
- Validate:
  - [ ] Given a selectable table, when `selectedRows` is set programmatically, then matching checkboxes render checked. Pass: visual match.
  - [ ] Given a row is clicked, when the click registers, then `selectedRowsChange` fires with the new array. Pass: console log matches expected IDs.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add externally controlled selectedRows prop and selectedRowsChange event"`

---

## Task 8: `bds-table` — Vue `v-model:selectedRows` wiring

**Executor:** @release-subagent
**Depends on:** Task 7
**Files:**

- `packages/boreal-web-components/targets/vue-output-target.ts` (modify)

**Acceptance criteria:**

- Add a new `componentModels` entry: `{ elements: ['bds-table'], event: 'selectedRowsChange', targetAttr: 'selectedRows' }`.
- Regenerate the Vue proxies (`../boreal-vue/lib/components.ts`) via the existing build step; do not hand-edit the generated file.

**Manual test:** Build `boreal-vue` and confirm `<BdsTable v-model:selectedRows="mySelection" />` compiles and updates `mySelection` on selection change in a scratch Vue app or the existing framework-integration playground.

**Commit:** `git commit -m "feat(boreal-vue): EOA-14935 wire v-model:selectedRows for bds-table"`

---

## Tasks 9–11: REMOVED — deferred (`bds-skeleton` standalone primitive)

**Status change (2026-07-08):** these three tasks (`bds-skeleton` scaffold, shimmer SCSS, tests+docs) are removed from this plan. The team confirmed a reusable skeleton primitive is valuable long-term, but agreed to defer building it until a second real consumer exists, rather than building it speculatively now. The loading visual `bds-table` needs is implemented directly in Task 20 as a private, table-scoped render helper — see the revised Task 20 below.

The extraction of a real `bds-skeleton` primitive is tracked as a deferred backlog item, not abandoned — see "Deferred: extract `bds-skeleton` primitive" near the end of this document for the trigger condition, scope, and allocation recommendation.

---

## Task 12: `bds-table` — built-in search bar (`searchable`)

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx` (modify — see "Search-bar sub-fixes" below)
- `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.scss` (modify)
- `packages/boreal-web-components/src/components/forms/bds-search-bar/types/*.ts` (modify — add `clearable` prop type)

**Acceptance criteria:**

| Prop         | Type      | Default | Description                                                                     |
| ------------ | --------- | ------- | ------------------------------------------------------------------------------- |
| `searchable` | `boolean` | `false` | Renders a built-in `bds-search-bar` (`mode="search"`) in the toolbar right zone |

- When `true`, `renderToolbarRight()` renders `<bds-search-bar mode="search" async minimized clearable>`. **The `async` prop is required** — verified directly in `bds-search-bar.tsx`'s `handleFieldInput`: in `mode="search"`, `bdsInputDebounced` only fires `if (this.async)`; without it, the event never emits and the documented "listen to `bdsInputDebounced` for filter-as-you-type" pattern silently does nothing. `bdsSearch` (Enter key / icon click) is unaffected either way.
- **Revised (2026-07-08, per UX/UI's explicit decision to enforce `bds-search-bar` as the exclusive search mechanism):** `slot="search-bar"` is removed entirely, not kept as an escape hatch. Unlike the generic `slot="toolbar-actions"`/`slot="row-actions"` (multi-purpose extension points), `search-bar` was a single-purpose named slot that existed only to add search functionality — keeping it functional whenever `searchable={false}` would let consumers bypass `bds-search-bar` entirely, undermining the enforcement. There is nothing left to warn about, since there's no second path left to conflict with.
- `bds-table` does not filter internally; consumer listens to `bdsSearch`/`bdsInputDebounced` and updates `data`/`dataset` externally.
- `hasToolbar` getter includes `this.searchable` (the old `[slot="search-bar"]` check is removed along with the slot itself).

### Search-bar sub-fixes (discovered during manual testing, 2026-07-08 — in scope for this task)

Manual verification via Playwright MCP found two real gaps in `bds-search-bar` itself, not `bds-table`:

1. **`mode="search"` never visually collapses.** `minimized`/`isOpen` toggle internal state (`aria-expanded`, the `bds-search-bar--expanded` host class) but produce **zero width change** — measured identical bounding-box width/position before and after toggling. Root cause: the collapse/expand width CSS (`$bds-search-bar-collapsed-size` ↔ `100%`, `.bds-search-bar__select`/`--expanded`) is scoped exclusively to the `<bds-select>` wrapper that only `mode="list"` renders. `mode="search"` calls `renderTextField(true)` directly with no equivalent wrapper, so it always renders at its natural full width.
   - **Options considered:** (A) new wrapper `<div>` around `renderTextField(true)` in search mode carrying a new class (`bds-search-bar__field-wrap`) that reuses the same collapse tokens/transition as `.bds-search-bar__select`, fully additive, zero risk to `mode="list"`'s tested behavior; (B) generalize `.bds-search-bar__select` into a mode-agnostic class shared by both `<bds-select>` and a new search-mode wrapper — DRYer but touches the already-tested list-mode path for marginal benefit; (C) collapse `bds-text-field` itself via a class toggle, no extra wrapper — risks visual squishing since `bds-text-field`'s internal label/container/icon-slot layout isn't designed to shrink to an exact square.
   - **Decision: Option A.** Add `private get searchFieldWrapClassMap(): StyleModifiers` mirroring `selectClassMap`'s shape (`bds-search-bar__field-wrap`, `--expanded`, `--static`, `--focused`, `--loading`, `--no-transition`); wrap `renderTextField(true)` in a `<div class={this.searchFieldWrapClassMap}>` only when `mode === SEARCH_BAR_MODE.SEARCH`. In SCSS, add a `.bds-search-bar__field-wrap` block reusing `$bds-search-bar-collapsed-size`/`$bds-search-bar-transition-duration` and the same `&--expanded, &--static { width: 100%; }` pattern as `.bds-search-bar__select` — do not touch `.bds-search-bar__select` or any `mode="list"` behavior.
2. **No clear (×) button in `mode="search"`.** Traced: `renderTextField()` passes `clearable={this.canShowClear}` in both modes, and `canShowClear` only returns `true` for `variant === 'static'` (or while loading) — `false` for our default variant regardless of mode. `mode="list"` appears to have one anyway only because `bds-select.tsx` **imperatively overrides** the nested field's `clearable` prop (`updateElementProp(this.bdsField, 'clearable', !this.static)`, `bds-select.tsx:419`), bypassing `bds-search-bar`'s own logic entirely — `mode="search"` never goes through `bds-select`, so that override never applies.
   - **Decision:** add a new opt-in `@Prop() readonly clearable: boolean = false;` at the top level of `bds-search-bar` (consistent with this plan's "no default-behavior change" convention elsewhere) rather than silently changing `canShowClear`'s default for all existing consumers. Update `canShowClear` to also return `true` when `this.clearable && this.value !== ''`. `bds-table` sets this prop when rendering its search bar (see updated `renderToolbarRight()` line above).

**Unit tests to cover:**

- `searchable={true}` renders a `bds-search-bar` in the toolbar.
- `hasToolbar` returns `true` when only `searchable` is set.
- `searchable={false}` (default) renders no search element in the toolbar right zone — confirms the removed slot has no residual effect.
- **`bds-search-bar` (new/updated spec file):**
  - `mode="search"` + `minimized` (default `isOpen=false`) renders `.bds-search-bar__field-wrap` at the collapsed width; clicking the trigger toggles to the expanded class/width.
  - `mode="list"`'s existing collapse tests are unaffected (regression check — no shared class renamed).
  - `clearable={true}` + non-empty `value` in `mode="search"` renders the field's clear affordance; `clearable={false}` (default) does not, regardless of value.
  - `mode="list"`'s existing clear-button behavior (via `bds-select`'s override) is unaffected by the new `clearable` prop.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `searchable`, wire `bdsSearch`/`bdsInputDebounced` to filter a sample dataset.
- Validate:
  - [ ] Given `searchable=true`, when typing and pressing Enter, then `bdsSearch` fires with the current value. Pass: log output matches typed text.
  - [ ] Given `searchable=true`, when the page loads, then the search control renders collapsed (icon-only) immediately adjacent to the Filter/Column-visibility icons — no dead space between them. Pass: visual check via screenshot, not just DOM structure (accessibility tree alone doesn't reveal collapsed-vs-expanded width).
  - [ ] Given the collapsed search icon is activated, then the search bar visibly expands **leftward** — the icon moves left and the input becomes visible to its right — measured via bounding-box width/position change (not just class-name presence), without overflowing the toolbar or overlapping the filter/layout buttons.
  - [ ] Given text is typed, then a clear (×) affordance appears; clicking it (or firing `bdsClear`) restores the full dataset.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add built-in searchable prop; fix(bds-search-bar): add mode=search collapse support and clearable prop"`

---

## Task 13: `bds-table` — pinnable column hover state

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify — `renderTh`)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify)

**Context:** Confirmed in current source — `bds-table.scss` only darkens header action icons on hover via `th[data-sortable]:hover .bds-table__th-actions i`. A column that is `pinnable` but not `sortable` never gets `data-sortable`, so its pin icon never receives the hover-darken treatment sortable columns already get, even though both icons share the same `__th-actions` container.

**Acceptance criteria:**

- `renderTh` stamps a `data-pinnable` attribute on the `<th>` when `col.pinnable` is `true` (parallel to the existing `data-sortable` stamping for `col.sortable`).
- SCSS hover rule extended to cover both cases: `th[data-sortable]:hover .bds-table__th-actions i, th[data-pinnable]:hover .bds-table__th-actions i { color: $boreal-icon-default-ink; }` (or equivalent combined selector) — no change to the existing sortable behavior.

**Unit tests to cover:**

- A `pinnable`-only (not `sortable`) column's `<th>` has `data-pinnable` set.
- A `sortable`-only column is unaffected (no `data-pinnable`, existing behavior unchanged).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render a column with `pinnable` but not `sortable`.
- Validate:
  - [ ] Given a pinnable-only column header, when hovering it, then the pin icon darkens the same way a sortable column's sort icon does. Pass: visual color match on hover.

**Commit:** `git commit -m "fix(bds-table): EOA-14935 add hover state for pinnable-only columns"`

---

## Task 14: `bds-table` — overflow tooltip on truncated text

**Executor:** @frontend-subagent
**Depends on:** Task 5
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify)

**Acceptance criteria:**

- A single `<bds-tooltip manual>` singleton renders once in `render()`, referenced via `ref`.
- `componentDidLoad` attaches delegated `mouseenter`/`mouseleave` (capture phase) on `.bds-table__wrapper`.
- On overflow (`scrollWidth > clientWidth`), calls the singleton's `anchorTo(span)` then `show()`; `mouseleave` calls `hide()`.
- Does not conflate with the existing per-column `info` tooltip (unrelated, unchanged).
- `disconnectedCallback` removes the delegated listeners.

**Unit tests to cover:**

- `mouseenter` on a truncated cell (mocked `scrollWidth`/`clientWidth`) triggers `anchorTo` + `show`.
- `mouseenter` on a non-truncated cell does nothing.
- `mouseleave` triggers `hide`.
- `info` tooltip still renders and behaves independently.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with a narrow column and long text.
- Validate:
  - [ ] Given a truncated header/cell, when hovering it, then the full text appears in a tooltip. Pass: tooltip content matches untruncated value.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add overflow tooltip for truncated text"`

---

## Task 15: Documentation for Tasks 7, 8, 12, 13, 14

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove High-priority rows 1 ("overflow tooltip") and 3 ("external controlled selection"), and Medium-priority row 12 ("built-in search input") from the limitations table.
- Add `selectedRows`, `selectedRowsChange`, `searchable` to the props/events table.
- **Replace the existing `WithSearch` story in place** — rewrite it to use the `searchable` prop and the built-in `bds-search-bar`, wiring `bdsInputDebounced`/`bdsClear` to filter the sample dataset. Remove the `<bds-text-field slot="search-bar">` example entirely; do not add a separate `WithBuiltInSearch` story alongside it — there should be exactly one story demonstrating how to add search. **Revised (2026-07-08):** `slot="search-bar"` no longer exists at all (removed in Task 12, not merely undocumented) — `searchable` is the only way to add search, per UX/UI's decision to enforce `bds-search-bar` exclusively.
- New stories: `WithControlledSelection`, `WithTruncatedContent`, `WithPinnableColumn` (updated to show the hover state).

**Manual test:** Run `pnpm dev:docs`, review each story.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document selectedRows, searchable, overflow tooltip, pinnable hover"`

---

## Task 16: `bds-table` — `dataset` prop, internal pagination, cross-page selection

**Executor:** @frontend-subagent
**Depends on:** Task 1
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop/State                     | Type        | Default | Description                                                     |
| ------------------------------ | ----------- | ------- | --------------------------------------------------------------- |
| `dataset` (Prop)               | `RowData[]` | `[]`    | Full unfragmented dataset; table performs internal page slicing |
| `visibleRows` (State, private) | `RowData[]` | `[]`    | Current page slice derived from `dataset`                       |

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

## Task 17: Design-review checkpoint — column footer as a slot (confirmation gate, no code)

**Executor:** none (requires human/PM sign-off before Task 18 starts)

**Deliverable:** confirm the corrected design before implementation:

- No new prop on `bds-table-column`. Consumers slot static markup as a direct child: `<bds-table-column col-key="amount" label="Amount"><span slot="footer">Total: $1,234</span></bds-table-column>`.
- `bds-table` detects footer content via `col.querySelector(':scope > [slot="footer"]')`, and moves that node into the matching `<tfoot>` `<td>` once — the same "read light-DOM child, project into rendered output" pattern already used for `slot="empty-state"`/`slot="row-actions"`/`slot="toolbar-actions"`.
- Because this is static, consumer-owned markup (not a computed function of rows), there is no "recompute on data change" behavior to build — if a consumer wants a live total, they update the slotted element's content themselves from their own script, same as any other slotted content in this component.
- `<tfoot>` renders only when at least one column has slotted footer content.

**Manual test:** N/A — sign-off gate.

---

## Task 18: `bds-table` — column footer row (slot-based)

**Executor:** @frontend-subagent
**Depends on:** Task 17 (sign-off)
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

## Task 19: `bds-table` — documentation for column footer

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove High-priority row 6 ("column footer") from the limitations table.
- New "Column footers" section documenting the `slot="footer"` pattern, with an example showing a consumer-updated live total.
- New `WithColumnFooter` story.

**Manual test:** Run `pnpm dev:docs`, confirm the new section and story.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document slot-based column footer row"`

---

## Task 20: `bds-table` — server-side mode and inline loading/skeleton visual

**Executor:** @frontend-subagent
**Depends on:** Task 1, Task 3
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss` (modify, or a sibling `_bds-table-skeleton.scss` partial imported by it)

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
  - Shimmer built entirely with `var(--boreal-*)` tokens; `@keyframes` sweep; respects `prefers-reduced-motion` (static, muted-token background instead of animating).
- This single implementation satisfies both this task's server-side loading state and the standalone Low-priority "skeleton placeholder" limitation.
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

## Task 21: `bds-table` — documentation for server-side mode and loading state

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove High-priority row 4 ("server-side mode") and Low-priority row 13 ("skeleton placeholder").
- New "Server-side mode" section with a fetch-wiring example.
- New stories: `WithServerSideMode`, `WithLoadingState`.
- No separate `bds-skeleton` doc page to reference — the loading-state section documents the skeleton visual as a `bds-table` implementation detail only.

**Manual test:** Run `pnpm dev:docs`, confirm sections/stories.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document server-side mode and loading state"`

---

## Task 22: `bds-table` — row virtualization

**Executor:** @frontend-subagent
**Depends on:** Task 16, Task 20
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)
- `packages/boreal-web-components/package.json` (verify only — `@tanstack/virtual-core@^3.17.1` already present)

**Acceptance criteria:**

| Prop/State                     | Type                            | Default | Description                                                 |
| ------------------------------ | ------------------------------- | ------- | ----------------------------------------------------------- |
| `virtual` (Prop)               | `boolean`                       | `false` | Opt-in row virtualization; `false` renders exactly as today |
| `virtualizer` (State, private) | `Virtualizer<Element, Element>` | —       | Drives the windowed row set                                 |

- Per Utility Discovery, do not reuse `VirtualScrollController` — wire `@tanstack/virtual-core`'s `Virtualizer` directly against Stencil's render cycle. **Correction (researched 2026-07-06):** even a fixed/reworked `VirtualScrollController` could not be reused here — its entire architecture (`MutationObserver` + `querySelectorAll` over a consumer's pre-existing light-DOM children) is built to manage markup a consumer already placed, not to drive a declarative render function like `renderBody()`. These are different integration points that happen to share the same underlying `Virtualizer` primitive, not a shared-utility opportunity.
- **No proven reference implementation exists to copy.** `ai-docs/lib/aqua-ds.txt`'s `aq-table-core.tsx` declares `@State() virtualizer: Virtualizer<Element, Element>` but never instantiates or reads it anywhere in the file — it's dead/unused code, not a working example. Aqua's actual windowing pattern (`utils/helpers/virtualScroll.ts`'s `VirtualScroll` class, used by its list/dropdown components, not its table) also only reduces DOM-attachment cost per scroll frame, not the upfront cost of creating every row — the same limitation as our `VirtualScrollController`. This task must be built directly against `@tanstack/virtual-core`'s public API (below) rather than by porting an existing pattern from either codebase.
- `componentDidLoad`, when `virtual` is `true`, initializes with `count` from whichever row-set is active (`data`, `visibleRows`, or `serverSide`-supplied `data`), `getScrollElement` pointing at `.bds-table__wrapper`, `estimateSize: () => 48`, `measureElement` for variable-height rows.
- `renderBody()` iterates only `getVirtualItems()` when `virtual` is `true`, with a spacer sized via `getTotalSize()`, using **explicit `key={rowId}` on every virtualized `<tr>`** — currently absent from `renderBody()` even without virtualization. Without it, Stencil's JSX diffing falls back to positional reconciliation, risking the exact row-identity-cache mismatch class TanStack's own tracker documents upstream ([`TanStack/virtual#1147`](https://github.com/TanStack/virtual/issues/1147)) — except inside our own Stencil reconciliation instead of TanStack's internals. Add this regardless of virtualization, since the underlying data (`sortedData`/`visibleRows`) can already reorder on sort/filter/page-change today.
- Log via `Logger` if `virtual=true` and `maxHeight === ''`.
- **Critical finding (verified 2026-07-06 against TanStack Virtual's own official examples and issue tracker, not assumed):** TanStack's own official `examples/react/table` renders a genuine `<table><thead><tbody><tr><td>` with rows positioned via `transform: translateY(...)` only — the same technique this task uses. That exact example is the subject of open, unresolved bugs ([`#585`](https://github.com/TanStack/virtual/issues/585), [`#591`](https://github.com/TanStack/virtual/issues/591), [`#640`](https://github.com/TanStack/virtual/issues/640)): a sticky `<thead>` "cannot go beyond the bounds of the `<table>` element," and since the table only ever contains the visible+overscan rows, its rendered height is smaller than the true scroll height — so the sticky header breaks/disappears while scrolling. A maintainer states plainly: *"table examples are misleading, we should not use the absolute position[ing]/translateY here."* `bds-table` already has a sticky `<thead>` (`position: sticky; top: 0`), so this is not hypothetical. **Decision (Option B, confirmed with the user): scope out the combination for v1** rather than rearchitecting to a grid/flex-on-semantic-tags layout (which would make `table-layout: fixed` and the existing pinned-column offset math irrelevant — a materially larger change) or prototyping an unvalidated spacer-row alternative. **When `virtual=true`, disable the `<thead>`'s `position: sticky` behavior** (conditional class/style override) and document this as a known v1 limitation — silently leaving `position: sticky` active would reproduce the exact broken behavior found upstream.

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

## Task 22b: `bds-table` — throttle pin-offset recomputation during virtualized scroll

**Executor:** @frontend-subagent
**Depends on:** Task 22
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

## Task 23: `bds-table` — documentation for virtualization

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove High-priority row 5 ("virtualization").
- New "Virtualization" section, explicitly noting this differs from `bds-search-bar`'s lighter-weight approach (which keeps all DOM nodes mounted) — `bds-table`'s virtualization actually bounds DOM node count.
- Document the Option B limitation explicitly: the sticky header (`position: sticky` on `<thead>`) is disabled while `virtual=true`, since combining the two is a documented-broken pattern upstream in TanStack Virtual (not yet resolved by any known technique compatible with real `<table>` layout).
- New `WithVirtualization` story using a ~5,000-row generated dataset, demonstrating the non-sticky header behavior in that mode.

**Manual test:** Run `pnpm dev:docs`, confirm section/story.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document row virtualization"`

---

## Task 24: `bds-table` — large-dataset guardrail (`maxClientRows`)

**Executor:** @frontend-subagent
**Depends on:** Task 20, Task 22
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)
- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts` (modify)

**Acceptance criteria:**

| Prop            | Type     | Default                        | Description                                                                       |
| --------------- | -------- | ------------------------------ | --------------------------------------------------------------------------------- |
| `maxClientRows` | `number` | `1000` (confirm with the team) | Threshold above which a non-blocking warning fires |

**Correction (researched 2026-07-06):** keep this guardrail — do not remove it once virtualization ships. `virtual=true` only bounds DOM node count/paint cost; it does **not** eliminate the cost of `sortedData`'s `[...this.data].sort(...)` running over the full array on every sort, `getSelectedRows()` filtering over the full array, holding the entire dataset in memory, or the network/JSON-parse cost of transferring it — all of these still scale with row count regardless of `virtual`. The original condition (silently exempting `virtual=true` entirely) slightly overstates what virtualization fixes.

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

## Task 25: `bds-table` — documentation for the guardrail

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)

**Acceptance criteria:**

- `maxClientRows` added to the props table.
- Row-count ceiling documented in "Layout constraints", alongside the 800px minimum-width note.

**Manual test:** Run `pnpm dev:docs`, confirm the update.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document maxClientRows guardrail"`

---

## Deferred: extract `bds-skeleton` primitive — not in this plan's scope

**Decision (confirmed with the user, 2026-07-08):** this plan implements `bds-table`'s loading visual as a private, table-scoped render helper (Task 20) instead of building a standalone `bds-skeleton` component (former Tasks 9–11). The team agrees a reusable skeleton primitive is valuable, but is deferring it until there's a second real consumer rather than building it speculatively now.

**Trigger condition to revisit:** a second component (e.g. `bds-list`, `bds-card`, a detail-panel pattern) needs a loading-placeholder visual, or design/product explicitly requests skeleton support outside `bds-table`.

**Why the extraction should stay cheap when that happens:** Task 20 was written to use the future primitive's exact shape today — `.bds-skeleton`/`.bds-skeleton--rect|text|circle` classes, `--bds-skeleton-*` custom properties, and a `renderSkeleton(variant, width, height)` helper signature matching the deferred component's eventual public props. Extracting later should be close to "cut, paste, rename tag, add Stencil registration" rather than a redesign.

**Recommendations for allocating this backlog item:**

- **File it now, in `ai-work/tickets/`**, as a small follow-up ticket linked to EOA-14935 (e.g. `EOA-XXXXX-bds-skeleton-primitive-extraction.md`) rather than leaving it only as plan-file prose — plan files in this repo represent active/completed sprints, not a durable backlog, so the ticket is the thing that survives once this plan is marked `done`.
- **Size it as a single small task**, not a multi-task plan: scaffold + SCSS + tests + docs, essentially former Tasks 9–11 unchanged, since the shimmer/variant logic will already exist proven-out inside `bds-table` — the work is extraction plus a second consumer's integration, not new design.
- **Don't pre-assign it to a specific sprint.** Gate it on the trigger condition above (a second consumer), not a calendar date — pulling it in before a second consumer exists just reproduces the speculative-build risk this decision avoided.
- **Best owner:** whoever picks up the second consuming component's work, not necessarily this plan's author — they'll have the freshest context on what that second consumer actually needs from the primitive (which may reveal the extracted API should differ slightly from `bds-table`'s internal shape).
- **Watch for scope creep in the meantime:** if a third internal spot in `bds-table` itself wants skeleton loading (e.g. a future inline-editing state) before any external consumer appears, treat that as the trigger too — "needed twice inside one component" is the same signal as "needed by two components."

---

## Related research: shared virtualization utility with `bds-search-bar` — deferred, not in this plan's scope

A follow-up question after Tasks 22/24 were corrected: since `VirtualScrollController` (used by `bds-search-bar`) doesn't reduce DOM node count, and `bds-table` needs real virtualization anyway, could ONE reusable utility on `@tanstack/virtual-core` serve both? Researched via three parallel fan-out agents (official docs, prior-art, dedicated counter-evidence), cross-checked against each other. Full findings and citations live in `/Users/dgonzalez/.claude/plans/let-s-continue-improving-the-calm-balloon.md` (the "Research: is a shared virtualization utility possible" section) — summarized here for this plan's record:

- **Conclusion:** technically possible, but only by rearchitecting `bds-search-bar`'s list onto a windowed-creation model (data-driven element recycling) — not by generalizing `VirtualScrollController`'s current positional/`MutationObserver`-driven design, which has no working precedent anywhere researched and independently sits in a real bug class TanStack's own tracker documents (identity-cache races, `ResizeObserver` conflicts with hidden/removed nodes — e.g. `TanStack/virtual#1133`, `#1147`, `#823`).
- **Decision (confirmed with the user):** defer to a separate future spike/ticket. This plan's Task 22 is unaffected — it already builds its own direct `@tanstack/virtual-core` integration without depending on or interfering with `VirtualScrollController` in any way. No task in this plan changes as a result.
- **Does this deprecate `VirtualScrollController`?** Not by this plan. It stays as-is for now; a near-term mitigation (narrowing the misleading "virtualization" claim in `bds-search-bar`'s `LargeSuggestionsList` story, or reducing its item count) is tracked independently in `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md` (now includes a second finding on the `display:none`+`ResizeObserver` correctness risk per `TanStack/virtual#823`).
- **Follow-up spike completed:** `ai-work/research/2026-07-06-shared-virtualization-utility.md` — concludes a small shared `createBdsVirtualizer()` factory (~20-30 lines, extractable from `VirtualScrollController`'s existing plumbing) is a reasonable low-risk future extraction, but `bds-search-bar`'s full windowed-creation rearchitecture is its own larger ticket, gated on an accessibility redesign (no synthetic-focus/`aria-activedescendant` model exists in this codebase today). **Refined after follow-up review:** if `bds-search-bar` renders its own `<bds-list-menu-item>` children via JSX (from a data-array prop) rather than an imperative Vaadin-style pool, it can share the exact same integration pattern as `bds-table`, not a separate adapter — the accessibility redesign remains the real blocker either way. Neither is scheduled; Task 22 above is unaffected either way.

---

## Execution order

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 12 → 13 → 14 → 15 → 16 → 17 (sign-off) → 18 → 19 → 20 → 21 → 22 → 22b → 23 → 24 → 25.

(Tasks 9–11 removed per the 2026-07-08 scoping decision — see the stub in their place above.)

Groups: pagination fixes (1–4) → tooltip singleton API (5–6) → controlled selection + its Vue wiring (7–8) → two no-blocker quick wins plus the pinnable-hover fix (12–13) → overflow tooltip, dependent on Task 5 (14–15) → dataset/pagination (16) → footer, gated on sign-off (17–19) → server-side mode + inline skeleton rows, self-contained (20–21) → virtualization last among rendering-touching work, including its pin-offset throttling follow-up (22–22b) → documentation (23) → guardrail, dependent on both server-side and virtual (24–25).
