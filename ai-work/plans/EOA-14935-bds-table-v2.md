---
ticket: EOA-14935
component: bds-table
status: done
created: 2026-07-06
completed: 2026-07-09
---

# bds-table v2 High-Priority Limitations Implementation Plan

> **For Claude:** this plan is `done`. Do not re-execute. The remaining scope originally planned here (Tasks 16–25) was moved to a follow-up plan: [`ai-work/plans/EOA-15507-bds-table-v3.md`](./EOA-15507-bds-table-v3.md) (ticket: [`ai-work/tickets/EOA-15507-bds-table-v3.md`](../tickets/EOA-15507-bds-table-v3.md)).

**Goal:** Close four of the six "Priority: High" limitations in `bds-table.mdx` that were tractable without deeper architectural prerequisites, plus a prerequisite `bds-pagination` bug-fix pass and a new `bds-tooltip` manual/imperative-control API, following the `EOA-10576` column-API spike's resolved decisions wherever they apply. The remaining v2-scoped work (dataset/internal pagination, column footer, server-side/skeleton loading, virtualization, large-dataset guardrail) is tracked in the v3 plan linked above.

**Ticket brief:** [`ai-work/tickets/EOA-14935-bds-table-v2.md`](../tickets/EOA-14935-bds-table-v2.md)

**Architecture:** Five features land as independently committable additions across three existing Stencil components (`bds-table`, `bds-pagination`, `bds-tooltip`), each guarded by its own prop and none altering v1's default (all-off) behavior. Two features (`bds-table`'s controlled selection and built-in search) required prerequisite work in `bds-tooltip`/Vue tooling; the pinnable-hover fix and overflow tooltip were self-contained beyond depending on the tooltip's new manual mode.

**Tech Stack:** Stencil (TSX + scoped SCSS), Jest + Stryker for the two-phase unit-test/mutation-score gate.

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
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`               | Modify — controlled selection, `searchable`, pinnable hover, overflow tooltip                       |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/types/ITable.ts`             | Modify — new prop/event types                                                                      |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss`              | Modify — overflow-tooltip truncation, pinnable hover state, search-bar toolbar layout               |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/*.spec.ts`          | Modify/create — cover all features in this plan                                                    |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx`                                          | Modify — remove shipped limitation rows, add new sections/prop tables                              |
| `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`                                   | Modify — new stories per feature                                                                   |
| `packages/boreal-web-components/targets/vue-output-target.ts`                                                      | Modify — add `bds-table` to `componentModels` for `v-model:selectedRows`                           |

**Note:** `bds-table-column.tsx`, row virtualization, skeleton loading, `dataset`/internal pagination, and `maxClientRows` were originally scoped into this same file listing but are not part of this plan's actual shipped work — see the v3 plan.

---

## Utility Discovery (mandatory gate — performed before finalizing tasks below)

| Feature area                          | Search performed                                                                                                                                   | Candidate found                                                                                                                                                                                          | Fit                                                                                                                                                                                                                                                                                                                                                                                               | Decision                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Overflow-tooltip singleton delegation | `src/utils/helpers/overlays/`, `src/utils/dom/`, `src/mixins/anchored.mixin.ts`                                                                    | `getOffset.ts` only; `anchoredMixin`'s `componentDidLoad`/`onBeforeLoad` auto-discovers a trigger once and calls `subscribe()` unconditionally, with no matching "unsubscribe"                           | Does not fit as-is; the auto-discovery path is actively wrong for a singleton reused across hundreds of cells                                                                                                                                                                                                                                                                                     | New `manual` prop on `bds-tooltip` needed to skip auto-discovery entirely (see Task 5) — this is a small, scoped addition to `bds-tooltip.tsx` only, not a change to the shared `anchored.mixin.ts` (keeps blast radius contained).                                                                                                                                                      |
| Vue v-model wiring                    | `packages/boreal-web-components/targets/vue-output-target.ts` `componentModels`                                                                    | Direct `event.detail` → `targetAttr` mapping, no transform support; existing entries use a dedicated `valueChange`-style event, never a domain event carrying a richer payload                           | `bdsSelect`'s `{selectedIds, row}` payload cannot drive `componentModels` directly                                                                                                                                                                                                                                                                                                                | Add a dedicated `selectedRowsChange: EventEmitter<string[]>` event on `bds-table`, matching the `valueChange` convention already used by `bds-search-bar` etc. See corrected Task 7 and new Task 8.                                                                                                                                                                                      |

**Note:** row virtualization, custom cell/footer rendering, skeleton loading rows, large-dataset guardrail logging, and dataset/pagination wiring were originally researched in this same table but belong to the v3 plan — reproduced there instead.

---

## Review of feature ordering (re-examined per explicit request)

- Prerequisite fixes first (pagination, tooltip) since two later features depend on them.
- The two no-blocker quick wins (`selectedRows`, `searchable`) land early for momentum, followed immediately by their own natural companions (Vue wiring for `selectedRows`; the pinnable-hover CSS fix, which is unrelated to any other feature and can land whenever).
- The overflow tooltip depends on the tooltip's new manual mode, so it lands after Task 5–6.

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

**Reverted (2026-07-14) — UX/UI decision reversed, see below.** The acceptance criteria and commit below describe this task's *original* execution (commit `e0582e99`), kept for history. That decision has since been reversed: UX/UI review determined the empty-state page indicator should keep showing "1" — "the table always has a first page," confirmed by Figma — and the original pre-`e0582e99` behavior (bare `<bds-typography variant="helper">1</bds-typography>`, no `getPaginationControls()`/nav arrows, when `totalPages === 0`) was restored in `render()`. The unit tests and manual test below were reverted to match. No new commit message is prescribed here — this correction lands as its own follow-up commit, e.g. `revert(bds-pagination): EOA-14935 restore empty-state literal "1" per UX/UI feedback`.

**Acceptance criteria (original, now reverted):**

- Replace the `isEmpty ? <bds-typography variant="helper">1</bds-typography> : ...` branch with `this.getPaginationControls()` unconditionally — its buttons are already `disabled` via `isPrevButtonDisabled`/`isNextButtonDisabled` when `totalPages === 0`.

**Unit tests to cover (original, now reverted):**

- `totalItems={0}` renders no literal `"1"` anywhere in the controls.
- `totalItems={0}` renders navigation buttons disabled.

**Manual test** _(waiveable, original, now reverted)_:

- Run `pnpm dev:components`, render `bds-pagination` with `total-items="0"`:
  - [ ] Given `total-items="0"`, when rendered, then no stray "1" appears and controls are visibly disabled. Pass: visual inspection confirms no orphaned "1".

**Commit (original, now reverted):** `git commit -m "fix(bds-pagination): EOA-14935 remove stray literal in empty state"`

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

**Status change (2026-07-08):** these three tasks (`bds-skeleton` scaffold, shimmer SCSS, tests+docs) are removed from this plan. The team confirmed a reusable skeleton primitive is valuable long-term, but agreed to defer building it until a second real consumer exists, rather than building it speculatively now. The loading visual `bds-table` needs is implemented as a private, table-scoped render helper in the v3 plan's Task 5 (`ai-work/plans/EOA-15507-bds-table-v3.md`), not in this plan.

The extraction of a real `bds-skeleton` primitive is tracked as a deferred backlog item, not abandoned — see the "Deferred: extract `bds-skeleton` primitive" section in the v3 plan for the trigger condition, scope, and allocation recommendation.

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

**Follow-up (2026-07-14) — pin icon cursor affordance.** This task's original scope only covered the hover-darken color change; it deliberately left `th[data-pinnable]` out of the `cursor: pointer` rule (`th[data-sortable] { cursor: pointer; }`), since for a pinnable-only column the whole `<th>` isn't clickable — only the pin `<i>` icon is (`renderThActions`'s `onClick`/`stopPropagation` sits on the icon, not the header). A later request asked to add `cursor: pointer` for pinnable columns; extending the existing `th[data-sortable]`-style rule to the whole `<th>[data-pinnable]` was considered and rejected for the same reason as above (misleading — most of the header would show a pointer cursor without being clickable). Implemented instead scoped to the icon itself:

- `bds-table.tsx`'s `renderThActions` now gives the pin `<i>` a stable base class, `${PREFIX}__pin-icon` (previously it only carried a conditional `--active` modifier, nothing at rest to target).
- `bds-table.scss` adds `&__pin-icon { cursor: pointer; }`, scoped to the icon — `th[data-sortable]`'s existing whole-header pointer-cursor rule is untouched, since that case is genuinely fully clickable.
- Two tests added to `bds-table.extras.spec.ts` covering both the pinnable-only case and the sortable+pinnable case (where the icon-level class is redundant with the header-level rule but still correctly present).

No new commit message prescribed here — this lands as its own follow-up commit, e.g. `fix(bds-table): EOA-14935 add pointer cursor to the pin icon`.

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

**Revised (2026-07-09) — reviewed against current `bds-table.mdx`/`bds-table.stories.ts` state.** The MDX prose for `searchable`/`bds-search-bar` was already rewritten as part of Task 12's own doc pass (uncommitted, alongside the component change) — do not redo that work. What's actually still stale or missing, verified directly against the current files:

- **Limitations table**: rows 1 ("Hovering a truncated header or cell reveals the full text in a tooltip" — Task 14, done), 3 ("Row selection state can be driven externally via a prop" — Tasks 7/8, done), and 12 ("A built-in search input renders inside the toolbar" — Task 12, done) are still listed as limitations despite being implemented. Remove all three and renumber the remaining rows. Row 2 ("Passing the full dataset once lets the table handle page slicing...") stays — that's Task 16, not yet done.
- **Props ArgTypes**: the `bds-table` `<ArgTypes include={[...]}>` list (currently: `subheading`, `subheading-icon`, `tooltip-text`, `selection-label`, `empty-message`, `max-height`, `selectable`, `bdsSort`, `bdsSelect`, `bdsDelete`, `bdsEdit`, `bdsFilter`, `bdsTableLayout`) is missing `selected-rows`, `selectedRowsChange`, and `searchable` entirely — add them.
- **`WithSearch` story is still broken/stale, contrary to appearances** — the MDX prose already describes `searchable`, but `stories.ts`'s actual `WithSearch` story (referenced by that prose's `<Canvas>`) still renders the old `<bds-text-field slot="search-bar">` pattern, which no longer works at all since that slot was removed from `bds-table.tsx` in Task 12. Rewrite it to use `searchable` + the rendered `bds-search-bar`, wiring `bdsInputDebounced`/`bdsClear` — this is the one piece of Task 12's doc work that didn't actually land.
- **No new `WithTruncatedContent` story needed** — `WithLongHeaderLabel` and `WithLongCellContent` already exist and cover exactly this (header vs. cell, arguably more precise than one combined story would be). Their doc comments and the MDX's "Long header labels"/"Long cell content" prose currently say **"(To be implemented in v2)"** for the hover-tooltip behavior — since Task 14 implemented it, remove that qualifier and describe the actual behavior: the tooltip anchors tightly to the truncated text itself (not the padded cell/header), and is fully independent of the per-column `info` tooltip (both can exist on the same column without interfering).
- **No new `WithPinnableColumn` story needed** — `WithPinnedColumn` already includes a pinnable-only column (`id`, `pinnable` without `sortable`) alongside a pinnable+sortable one (`name`). Update its doc comment to explicitly mention the pinnable-only hover-darkening behavior (Task 13) — currently the comment only describes pinning/scrolling/sorting/info, not hover.
- **New story still needed**: `WithControlledSelection`, demonstrating `selectedRows`/`selectedRowsChange` (Tasks 7/8) — confirmed genuinely missing from `stories.ts`.
- Do not document the `--bds-table-search-width` CSS custom property added this session — this MDX doesn't document any `@prop` CSS custom properties currently (not even the pre-existing `--bds-table-header-height` etc.), so adding one now would be inconsistent with its established scope/convention.

**Manual test:** Run `pnpm dev:docs`, review each story — specifically confirm `WithSearch` actually filters/clears via the rendered search bar (it currently would not, since the story itself hasn't been updated yet), and that the truncation-tooltip and pinnable-hover behaviors are visible in their respective canvases.

**Commit:** `git commit -m "docs(bds-table): EOA-14935 document selectedRows, searchable, overflow tooltip, pinnable hover"`

**Follow-up (2026-07-14) — PR review caught an incomplete execution of the "Props ArgTypes" bullet above.** `selected-rows`, `searchable`, and `selectedRowsChange` had been added to the MDX `<ArgTypes include={[...]}>` list, but the corresponding entries were never actually added to the `argTypes` object in `bds-table.stories.ts` — Storybook's `<ArgTypes include={...}>` silently drops any name that isn't a declared argType, so all three were invisible in the rendered props/events table despite appearing in both source files. Fixed by adding all three to `argTypes` (plus matching `StoryArgs` fields and `args` defaults). While auditing the full prop/event list against `argTypes` for this fix, two more genuine (pre-existing, not part of this task's original scope) gaps were found and closed the same way: `data` and `rowKey`, neither of which had ever been in `argTypes` or the MDX `include` list. `loading`/`loadingRows` were also found missing but were deliberately left out — see the v3 plan note below.

---

## Remaining scope — moved to the v3 plan

Tasks originally numbered 16–25 (+22b) in this plan — `dataset` prop with internal pagination and cross-page selection, the column footer (sign-off gate + implementation + docs), server-side mode with inline skeleton loading, row virtualization (+ its pin-offset throttling follow-up + docs), and the `maxClientRows` guardrail (+ docs) — did not land as part of this plan's execution and are now tracked, renumbered 1–11, in [`ai-work/plans/EOA-15507-bds-table-v3.md`](./EOA-15507-bds-table-v3.md), along with a new consolidated Task 12 for mutation testing across everything in that plan. The "Deferred: extract `bds-skeleton` primitive" and "Related research: shared virtualization utility" sections that supported that work have also been carried forward into the v3 plan.

---

## Execution order

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 12 → 13 → 14 → 15.

(Tasks 9–11 removed per the 2026-07-08 scoping decision — see the stub in their place above. Tasks 16–25 moved to the v3 plan — see above.)

Groups: pagination fixes (1–4) → tooltip singleton API (5–6) → controlled selection + its Vue wiring (7–8) → two no-blocker quick wins plus the pinnable-hover fix (12–13) → overflow tooltip, dependent on Task 5, plus its documentation (14–15).
</content>
