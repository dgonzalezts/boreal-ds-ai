---
ticket: EOA-14935
component: bds-table
status: pending
created: 2026-07-06
---

# bds-table v2 High-Priority Limitations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Close the six "Priority: High" limitations in `bds-table.mdx`, plus the built-in search bar, skeleton loading, and a large-dataset guardrail, following the `EOA-10576` column-API spike's resolved decisions wherever they apply.

**Ticket brief:** [`ai-work/tickets/EOA-14935-bds-table-v2.md`](../tickets/EOA-14935-bds-table-v2.md)

**Architecture:** Ten features land as independently committable additions across four existing Stencil components (`bds-table`, `bds-table-column`, `bds-pagination`, `bds-tooltip`) plus one new small primitive (`bds-skeleton`), each guarded by its own prop and none altering v1's default (all-off) behavior. Three features require prerequisite work in sibling components before the `bds-table`-side work can start.

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
| `packages/boreal-web-components/src/components/helpers/bds-skeleton/bds-skeleton.tsx`                              | Create — new reusable skeleton primitive                                                           |
| `packages/boreal-web-components/src/components/helpers/bds-skeleton/types/ISkeleton.ts`                            | Create — prop types                                                                                |
| `packages/boreal-web-components/src/components/helpers/bds-skeleton/bds-skeleton.scss`                             | Create — shimmer animation, `var(--boreal-*)` tokens only                                          |
| `packages/boreal-web-components/src/components/helpers/bds-skeleton/__test__/*.spec.ts`                            | Create — unit tests                                                                                |
| `apps/boreal-docs/src/stories/helpers/bds-skeleton/bds-skeleton.stories.ts`                                        | Create — Storybook story                                                                           |
| `apps/boreal-docs/src/stories/helpers/bds-skeleton/bds-skeleton.mdx`                                               | Create — MDX documentation                                                                         |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`               | Modify — all `bds-table`-side features                                                             |
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
| Skeleton loading rows                 | Repo-wide search for `skeleton`/`shimmer` in `boreal-web-components` and `boreal-style-guidelines`                                                 | None found outside the existing TODO comment in `bds-table.tsx`                                                                                                                                          | Does not fit                                                                                                                                                                                                                                                                                                                                                                                      | Confirmed with the user: build a new reusable `bds-skeleton` primitive (rect/text variants, shimmer via `var(--boreal-*)` tokens) since the loading mockup shows skeleton needed in at least four places within `bds-table` alone (toolbar, header, cells, pagination row) — enough internal repetition to justify a shared primitive now rather than deferring. See Tasks 9–12.         |
| Large-dataset guardrail logging       | `bds-table.tsx` (`private readonly logger = new Logger()`, line 36)                                                                                | `Logger` service already imported and used                                                                                                                                                               | Fully fits                                                                                                                                                                                                                                                                                                                                                                                        | Reuse `this.logger.warn(...)`.                                                                                                                                                                                                                                                                                                                                                           |
| Dataset/pagination wiring             | `bds-table.tsx` `componentDidLoad`/`componentWillLoad` (existing `querySelectorAll('bds-table-column')` + `MutationObserver` pattern)              | Same slotted-child-query pattern already used for columns                                                                                                                                                | Fully fits                                                                                                                                                                                                                                                                                                                                                                                        | Reuse the identical pattern for querying the slotted `bds-pagination`.                                                                                                                                                                                                                                                                                                                   |
| Vue v-model wiring                    | `packages/boreal-web-components/targets/vue-output-target.ts` `componentModels`                                                                    | Direct `event.detail` → `targetAttr` mapping, no transform support; existing entries use a dedicated `valueChange`-style event, never a domain event carrying a richer payload                           | `bdsSelect`'s `{selectedIds, row}` payload cannot drive `componentModels` directly                                                                                                                                                                                                                                                                                                                | Add a dedicated `selectedRowsChange: EventEmitter<string[]>` event on `bds-table`, matching the `valueChange` convention already used by `bds-search-bar` etc. See corrected Task 7 and new Task 8.                                                                                                                                                                                      |

---

## Review of feature ordering (re-examined per explicit request)

Kept largely as originally sequenced, with the new `bds-skeleton` primitive and Vue wiring slotted in at their natural dependency points:

- Prerequisite fixes first (pagination, tooltip) since two later features depend on them.
- The two no-blocker quick wins (`selectedRows`, `searchable`) land early for momentum, followed immediately by their own natural companions (Vue wiring for `selectedRows`; the pinnable-hover CSS fix, which is unrelated to any other feature and can land whenever).
- `bds-skeleton` (new primitive) must exist before the server-side/loading task that consumes it.
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

## Task 9: `bds-skeleton` — new reusable skeleton primitive (types, scaffold, render)

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/helpers/bds-skeleton/bds-skeleton.tsx` (create)
- `packages/boreal-web-components/src/components/helpers/bds-skeleton/types/ISkeleton.ts` (create)

**Acceptance criteria:**

| Prop      | Type                           | Default  | Description              |
| --------- | ------------------------------ | -------- | ------------------------ |
| `variant` | `'text' \| 'rect' \| 'circle'` | `'rect'` | Shape of the placeholder |
| `width`   | `string`                       | `'100%'` | CSS width                |
| `height`  | `string`                       | `'1rem'` | CSS height               |

- Pure presentational atom — no `@Event()`, no `@Method()`, no form participation, no interaction/keyboard handling (none of those apply here per the leaf-component granularity model).
- `render()` outputs a single `<Host>` with a class map reflecting `variant`, and inline `style` for `width`/`height`.
- JSDoc on the class-level block and every `@Prop()`.
- No `any` types.

**Unit tests to cover** (`__test__/bds-skeleton.spec.ts`):

- Default render produces `variant="rect"` styling.
- Each variant (`text`, `rect`, `circle`) applies its corresponding class.
- `width`/`height` props apply as inline styles.

**Manual test** _(waiveable)_:

- Scenario: render all three variants side by side in the playground.
- Run `pnpm dev:components` and validate:
  - [ ] Given the three variants render, when inspected, then each has visually distinct shape treatment (rect = rounded rectangle, circle = perfect circle, text = short rounded bar). Pass: visual match.

**Commit:** `git commit -m "feat(bds-skeleton): EOA-14935 scaffold new skeleton primitive"`

---

## Task 10: `bds-skeleton` — SCSS shimmer animation

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/helpers/bds-skeleton/bds-skeleton.scss` (create)

**Acceptance criteria:**

- Shimmer treatment built entirely with `var(--boreal-*)` tokens — no hardcoded colors.
- `@keyframes` animation for the shimmer sweep; respects `prefers-reduced-motion` (static, muted-token background instead of animating, for users who request reduced motion).
- Each `variant` gets appropriate `border-radius` (`circle` = `50%`, `text` = small radius, `rect` = standard component radius token).

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`, confirm the shimmer animates smoothly and respects the OS-level reduced-motion setting (toggle in browser devtools' rendering panel).
  - [ ] Given `prefers-reduced-motion: reduce` is simulated, when the skeleton renders, then the shimmer animation is replaced by a static muted background. Pass: no animation, tokens still applied.

**Commit:** `git commit -m "style(bds-skeleton): EOA-14935 add shimmer animation with boreal tokens"`

---

## Task 11: `bds-skeleton` — unit tests and documentation

**Executor:** @testing-subagent (tests) then @documentation-subagent (docs)
**Files:**

- `packages/boreal-web-components/src/components/helpers/bds-skeleton/__test__/*.spec.ts` (finalize)
- `apps/boreal-docs/src/stories/helpers/bds-skeleton/bds-skeleton.stories.ts` (create)
- `apps/boreal-docs/src/stories/helpers/bds-skeleton/bds-skeleton.mdx` (create)

**Acceptance criteria:**

- Tests from Task 9 pass the two-phase gate.
- New Storybook story with variant/width/height controls.
- New MDX doc following the standard component doc structure (How to use it, When to use it, Component preview, Accessibility, Properties).

**Manual test:** Run `pnpm dev:docs`, confirm the story and doc page render correctly.

**Commit:** `git commit -m "test(bds-skeleton): EOA-14935 add tests and documentation"`

---

## Task 12: `bds-table` — built-in search bar (`searchable`)

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)

**Acceptance criteria:**

| Prop         | Type      | Default | Description                                                                     |
| ------------ | --------- | ------- | ------------------------------------------------------------------------------- |
| `searchable` | `boolean` | `false` | Renders a built-in `bds-search-bar` (`mode="search"`) in the toolbar right zone |

- When `true`, `renderToolbarRight()` renders `<bds-search-bar mode="search">` instead of relying on `slot="search-bar"`. The slot remains the escape hatch — both must not render simultaneously; log via `Logger` if both are active.
- `bds-table` does not filter internally; consumer listens to `bdsSearch`/`bdsInputDebounced` and updates `data`/`dataset` externally.
- `hasToolbar` getter includes `this.searchable`.

**Unit tests to cover:**

- `searchable={true}` renders a `bds-search-bar` in the toolbar.
- `hasToolbar` returns `true` when only `searchable` is set.
- Both `searchable` and populated `slot="search-bar"` logs a warning, no double-render.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `searchable`, wire `bdsSearch` to filter a sample dataset.
- Validate:
  - [ ] Given `searchable=true`, when typing and pressing Enter, then `bdsSearch` fires with the current value. Pass: log output matches typed text.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add built-in searchable prop"`

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
- New stories: `WithControlledSelection`, `WithBuiltInSearch`, `WithTruncatedContent`, `WithPinnableColumn` (updated to show the hover state).

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

## Task 20: `bds-table` — server-side mode and finished loading/skeleton visual

**Executor:** @frontend-subagent
**Depends on:** Task 1, Task 3, Tasks 9–11 (`bds-skeleton`)
**Files:**

- `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` (modify)

**Acceptance criteria:**

| Prop         | Type      | Default | Description                                                                        |
| ------------ | --------- | ------- | ---------------------------------------------------------------------------------- |
| `serverSide` | `boolean` | `false` | Disables local sort reordering; `bdsSort` still emits for the consumer to re-fetch |

- When `serverSide` is `true`, `sortedData`/`visibleRows`-aware equivalent returns rows unsorted; `handleSort` still emits `bdsSort` with the correct payload.
- Replace the `onLoadingChange` no-op stub with real behavior: when `loading` is `true`, `renderBody()` renders `loadingRows` rows composed of `<bds-skeleton variant="rect">` instances (Task 9's new component) — one per column plus the checkbox-column gap when `selectable` — instead of using inline shimmer CSS.
- This single implementation satisfies both this task's server-side loading state and the standalone Low-priority "skeleton placeholder" limitation.
- Does not combine `serverSide` with future virtualization-based infinite scroll (documentation-only note, no code enforcement needed).

**Unit tests to cover:**

- `serverSide={true}` + sortable header click emits `bdsSort` but leaves row order unchanged.
- `loading={true}` renders exactly `loadingRows` rows of `bds-skeleton` elements with correct column count.
- `loading={false}` (default) renders real data unaffected.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `serverSide` + a sortable column; toggle `loading`.
- Validate:
  - [ ] Given `serverSide=true`, when clicking a sortable header, then row order stays visually unchanged while the sort icon updates. Pass: visual + icon check.
  - [ ] Given `loading=true`, when rendered, then skeleton rows composed of `bds-skeleton` appear instead of data. Pass: shimmer visible, real data hidden.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add serverSide mode and bds-skeleton-based loading rows"`

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
- `renderBody()` iterates only `getVirtualItems()` when `virtual` is `true`, with a spacer sized via `getTotalSize()`.
- Log via `Logger` if `virtual=true` and `maxHeight === ''`.

**Unit tests to cover:**

- `virtual={false}` (default) renders all rows unchanged (regression guard).
- `virtual={true}` renders only the windowed subset.
- `virtual={true}` without `maxHeight` logs a warning.
- Spacer sized to `getTotalSize()` present when virtualized.

**Manual test** _(waiveable)_:

- Run `pnpm dev:components`; render `bds-table` with `virtual` + `max-height` + ~5,000 rows.
- Validate:
  - [ ] Given `virtual=true` with `maxHeight` set, when scrolling through 5,000 rows, then only a small window of `<tr>` elements exists in the DOM at any time (inspect via devtools). Pass: DOM node count stays roughly constant.
  - [ ] Given `virtual=true` without `maxHeight`, when mounted, then a console warning appears. Pass: warning visible.

**Commit:** `git commit -m "feat(bds-table): EOA-14935 add opt-in row virtualization"`

---

## Task 23: `bds-table` — documentation for virtualization

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.mdx` (modify)
- `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (modify)

**Acceptance criteria:**

- Remove High-priority row 5 ("virtualization").
- New "Virtualization" section, explicitly noting this differs from `bds-search-bar`'s lighter-weight approach (which keeps all DOM nodes mounted) — `bds-table`'s virtualization actually bounds DOM node count.
- New `WithVirtualization` story using a ~5,000-row generated dataset.

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

## Execution order

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 (sign-off) → 18 → 19 → 20 → 21 → 22 → 23 → 24 → 25.

Groups: pagination fixes (1–4) → tooltip singleton API (5–6) → controlled selection + its Vue wiring (7–8) → new `bds-skeleton` primitive (9–11, built before it's consumed by Task 20) → two no-blocker quick wins plus the pinnable-hover fix (12–13) → overflow tooltip, dependent on Task 5 (14–15) → dataset/pagination (16) → footer, gated on sign-off (17–19) → server-side mode + skeleton rows, dependent on `bds-skeleton` (20–21) → virtualization last among rendering-touching work (22–23) → guardrail, dependent on both server-side and virtual (24–25).
