---
ticket: EOA-19597
component: bds-search-bar
status: in progress
created: 2026-10-21
---

# bds-search-bar — Real Windowed Suggestions via Shared `VirtualWindow` Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Render only the visible window of `bds-search-bar` suggestions as mounted `bds-list-menu-item` elements by extracting `bds-table`'s proven TanStack wiring into a shared `VirtualWindow` utility, then removing the positional `VirtualScrollController`.

**Ticket brief:** [`ai-work/tickets/EOA-19597-bds-search-bar-virtual-suggestions.md`](../tickets/EOA-19597-bds-search-bar-virtual-suggestions.md)

**Source bug:** [`ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`](../qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md)

**Research spikes:** `ai-work/research/2026-10-21-virtual-list-approach-{a-positional,b-shared-util,c-component-owned}.md`

**Architecture:** One PR, ordered commits. (1) Extract `VirtualWindow` (Virtualizer lifecycle only, no Stencil imports) and move `bds-table` onto it with no behaviour change. (2) Add a data-driven `items` prop to `bds-search-bar` that renders its own `bds-select` + `bds-list-menu` and windows `bds-list-menu-item`s with spacer elements. The search bar owns filtering, keyboard navigation and label lookup, so `bds-select` and `bds-list-menu` stay untouched. (3) Delete `VirtualScrollController`; the slotted `list` path remains for small lists, unvirtualized.

**Tech Stack:** Stencil, `@tanstack/virtual-core` (already a dependency), Jest `newSpecPage`, Storybook.

**Decisions already made (do not reopen without the user):**

- No real consumers today → no deprecation path; `VirtualScrollController` is removed in this PR (not exported from any barrel).
- `bds-select`, `bds-list-menu`, `bds-list-menu-item` source is **not modified**. `bds-pagination` and `bds-date-picker` use `bds-select`, so they are out of the blast radius by construction.
- Slotted `<bds-list-menu slot="list">` keeps working for small lists with no virtualization. `items` is the large-list path.
- `items` v1 is single-select, flat (no `variant="label"` group headers), fixed row height.
- No `aria-activedescendant` migration (separate decision). Focus stays on mounted `bds-list-menu-item`s.

**Facts verified in source while planning** (re-verify at execution time, plans go stale):

- `bds-search-bar` already renders `<bds-select managed>`; `bds-select.listenField` returns early when `managed`, so the search bar already owns filtering (`searchOwnData`).
- `bds-list-menu` keyboard uses `setLinearNavigation({ wrap: true })` over mounted, non-hidden, non-disabled items; `bds-select.handleArrowNavigation` calls `bdsList.focusFromTriggerKey`, where ArrowUp prefers the *last mounted* item. Both only see the window, so they cannot be trusted at window edges. The search bar must intercept those keys itself in `items` mode.
- `bds-list-menu` `.bds-list-menu__content` already has `overflow-y: auto; max-height: var(--bds-list-menu-max-height, 240px)` and is the scroll element `VirtualScrollController` used.
- `bds-list-menu` shows its empty text when `empty || childItems.length === 0`.
- `bds-select.loadValue` returns early when the option for `value` is not mounted.
- `bds-list-menu-item` uses the `bds-transition-surface` mixin → remounted windowed items carry the Safari remount-transition risk (`.agents/memory/safari-virtualized-row-transition-on-remount.md`).
- `bds-table.virtual.spec.ts` reads private `instance.virtualizer` and spies `BdsTable.prototype.initVirtualizer`; it must be retargeted.
- `bds-table` embeds `<bds-search-bar mode="search" async minimized clearable>`; `mode="search"` behaviour must not change.

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md` | Modify — correct `bds-select` claim, Finding 2 verdict, link to this plan |
| `packages/boreal-web-components/src/utils/dom/virtualWindow/virtual-window.ts` | New — framework-agnostic Virtualizer lifecycle wrapper |
| `packages/boreal-web-components/src/utils/dom/virtualWindow/types.ts` | New — options / item types |
| `packages/boreal-web-components/src/utils/dom/virtualWindow/index.ts` | New — barrel; also exported from `src/utils/dom/index.ts` |
| `packages/boreal-web-components/src/utils/dom/virtualWindow/__test__/virtual-window.spec.ts` | New — unit tests |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` | Modify — move onto `VirtualWindow`, no behaviour change |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.virtual.spec.ts` | Modify — retarget private-field access / spies |
| `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.max-client-rows.spec.ts` | Modify only if it touches the old fields |
| `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx` | Modify — `items` prop, windowed render, data filtering, keyboard, remove controller |
| `packages/boreal-web-components/src/components/forms/bds-search-bar/types/ISearchBar.ts`, `types.ts`, `index.ts` | Modify — `SearchBarSuggestion`, `items` |
| `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.scss` | Modify — spacer + Safari transition rules |
| `packages/boreal-web-components/src/components/forms/bds-search-bar/__test__/*.spec.ts` | Modify / create — `items`-mode specs |
| `packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts` | Delete |
| `packages/boreal-web-components/src/components.d.ts` | Regenerated by build (not hand-edited) |
| `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.stories.ts`, `.mdx` | Modify — `items` story, corrected wording |
| `.agents/memory/` | New entry via knowledge-keeper |

Not touched: `bds-select`, `bds-list-menu`, `bds-list-menu-item`, `bds-pagination`, `bds-date-picker`, `boreal-react`/`boreal-vue` sources (generated).

---

## Progress

| Task | Status |
| --- | --- |
| T1 Correct the bug report | done |
| T2 `VirtualWindow` types and scaffold | done |
| T3 `VirtualWindow` implementation | done |
| T4 `VirtualWindow` unit tests | done |
| T5 Move `bds-table` onto `VirtualWindow` | done |
| T6 Retarget `bds-table` virtual specs | done |
| T7 `bds-table` manual regression check | done |
| T8 Search-bar types and `items` prop scaffold | pending |
| T9 Windowed rendering in `items` mode | done |
| T10 Data-side filtering, clear, empty state | done |
| T10b Fix text wipe / focus loss on Tab to the clear button | done |
| T10c Reopen the suggestions popover when typing | done |
| T11 Keyboard navigation in `items` mode | pending |
| T12 Selection and label resolution | pending |
| T12b Early React/Vue wrapper smoke check | pending |
| T13 Remove `VirtualScrollController` and slotted-path wiring | pending |
| T14 SCSS: spacers and Safari remount rule | pending |
| T15 Search-bar unit tests | pending |
| T16 Story and MDX | pending |
| T17 Search-bar manual QA and measurement | pending |
| T18 React/Vue wrapper parity | pending |
| T19 Consolidated mutation testing | pending |
| T20 Full gate and Chromatic timing | pending |
| T21 Knowledge capture | pending |
| T22 Pre-existing duplicate/spurious `bds-search-bar` event emissions (both modes) | deferred |

---

### Task 1: Correct the bug report

**Status:** done
**Executor:** main thread (no executor)
**Files:**

- `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md` (modify)

**Acceptance criteria:**

- States that `bds-select` does not use `VirtualScrollController`; `bds-search-bar` is its only consumer.
- Finding 2 is annotated: the controller never calls `measureElement`, so TanStack/virtual#823 does not apply to it (verified against the installed `@tanstack/virtual-core` source). Remaining controller hazards (fixed 28 px estimate, O(N) `refresh()`) are noted as moot because the controller is removed.
- Status and Related sections link to this plan; "deferred" wording on option 2 is replaced with the chosen approach.
- Known Gaps keep the Chromatic timeout and profiling items open (closed in T17/T20).

**Manual test:** N/A — docs-only; read the file and confirm each bullet above.

**Commit:** `docs(web-components): EOA-19598 correct virtualization bug report findings`

---

### Task 2: `VirtualWindow` types and scaffold

**Status:** done
**Executor:** @frontend-subagent
**Files:**

- `utils/dom/virtualWindow/types.ts` (create)
- `utils/dom/virtualWindow/virtual-window.ts` (create, stub class)
- `utils/dom/virtualWindow/index.ts` (create) and `utils/dom/index.ts` (modify — add export)

**Utility discovery:**

- Feature area: Virtualizer lifecycle (create / mount / update / unmount / batched change notification).
- Search: `src/utils/dom`, `src/utils/helpers`, `src/utils/a11y`; terms `virtual`, `Virtualizer`, `tanstack`.
- Candidates: `VirtualScrollController` (partial fit — positional, DOM-collecting, `MutationObserver`; does not fit), `bds-table.tsx` inline wiring (fits, but component-local).
- Reuse decision: extract `bds-table`'s wiring (T5 migrates it); `VirtualScrollController` is deleted in T13. No parallel implementation allowed to remain.
- Types: checked `src/types/` (no virtual/list-item type exists). New types live beside the utility.

**Acceptance criteria:**

- Options interface covers: `count`, `getScrollElement`, `estimateSize`, optional `overscan`, optional `getItemKey`, optional `measure` (dynamic height on/off), `onChange`.
- Item type exposes `index`, `key`, `start`, `end`, `size`.
- Class surface: `mount`, `update(patch)`, `unmount`, `getItems`, `getTotalSize`, `getLeadingSize`, `getTrailingSize`, `measureElement`, `scrollToIndex`. Methods are stubs.
- No Stencil imports; no `any`; required members before optional members in every interface.
- Exported through `utils/dom/index.ts`.
- Public members carry JSDoc (exported API only, no inline comments).

**Manual test:** non-visual — `pnpm --filter @pxglobal/boreal-web-components build` compiles; no behaviour to check.

**Commit:** `feat(web-components): EOA-19598 scaffold VirtualWindow utility`

---

### Task 3: `VirtualWindow` implementation

**Status:** done
**Executor:** @frontend-subagent
**Files:**

- `utils/dom/virtualWindow/virtual-window.ts` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read `bds-table.tsx` `initVirtualizer`, `syncVirtualizerOptions`, `scheduleVirtualRerender`, `teardownVirtualizer` as they exist at execution time; behaviour must be moved, not redesigned.
- [ ] Call sites: only `bds-table` (T5) and `bds-search-bar` (T9) will use it.
- [ ] Default/empty state: `count: 0` → `getItems()` returns `[]`, sizes are `0`, no throw.
- [ ] Reactivity: `update()` is the only way options change after `mount()`; it must be a no-op when nothing changed.

**Acceptance criteria:**

- Creates the Virtualizer with `observeElementRect`, `observeElementOffset`, `elementScroll`, matching the table's current configuration (default overscan, `measureElement` only when `measure` is true).
- `mount()` runs `_willUpdate()`/`_didMount()` in the same order the table does today and stores the cleanup; calling it twice does not double-mount.
- `update(patch)` applies `setOptions` with the merged options and `_willUpdate()`; a call with an unchanged `count` and options does not re-notify.
- `onChange` notifications are coalesced into one microtask per burst so a host can bump a render counter safely (same timing as the table's `_virtualRerenderScheduled`).
- `unmount()` runs cleanup, clears pending notification, and makes later `getItems()` return `[]`.
- Leading/trailing sizes equal the first item's `start` and `getTotalSize() - last.end` (0 when empty).

**Manual test:** non-visual — validated by T4 specs.

**Commit:** `feat(web-components): EOA-19598 implement VirtualWindow lifecycle`

---

### Task 4: `VirtualWindow` unit tests

**Status:** done
**Executor:** @testing-subagent
**Files:**

- `utils/dom/virtualWindow/__test__/virtual-window.spec.ts` (create)
- `src/utils/testing/` (modify only if a shared rect/ResizeObserver stub is needed)

**Unit tests to cover:**

- Lifecycle: mount, double-mount guard, update with changed/unchanged count, unmount, use after unmount.
- Microtask coalescing: N synchronous changes → one `onChange` after `await flushMicrotasks()` (exported from `@/utils`).
- Windowing math: with a stubbed scroll rect and fixed `estimateSize`, `getItems()` returns window + overscan; leading/trailing sizes sum with item sizes to `getTotalSize()`.
- `scrollToIndex` moves the window; `count: 0` returns empty results.
- `getItemKey` keys are surfaced on items.
- Utility discovery for tests: check `src/utils/testing/` and the stub already used by `bds-table.virtual.spec.ts` first; if it is local to the table spec, move it to the shared testing utils and have both specs import it.
- Coverage-phase only (≥80%); mutation testing deferred to T19.

**Manual test:** N/A — validated via `pnpm test` scoped to this spec (use a bare positional path + `--collectCoverageFrom`, see `stencil-scoped-test-invocation.md`).

**Commit:** `test(web-components): EOA-19598 cover VirtualWindow lifecycle and windowing`

---

### Task 5: Move `bds-table` onto `VirtualWindow`

**Status:** done
**Executor:** @frontend-subagent
**Files:**

- `bds-table.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read the current `bds-table.tsx`; list every use of `virtualizer`, `_virtualizerCleanup`, `_virtualRerenderScheduled`, `virtualVersion`, and `measureElement` (`commitExpandChange`, `renderVirtualRows`, `renderVirtualDetailRow`).
- [ ] Call sites: `initVirtualizer` is reached from `checkClientRowsThreshold`, `onVirtualPropChange`, `componentDidLoad`; `teardownVirtualizer` from `onVirtualPropChange` and `disconnectedCallback`; `syncVirtualizerOptions` from `componentWillRender`. All must route through the new field.
- [ ] Boundary: placeholder render depends on the virtualizer being `undefined` before init — preserve that observable state (spec depends on it).
- [ ] Reactivity: `virtual`, `maxHeight`, `maxClientRows`, `data`, `rows` watchers keep their current behaviour.
- [ ] Safari: confirm the scoped `transition: none` rule for virtualized rows in `bds-table.scss` is untouched.

**Acceptance criteria:**

- All Virtualizer creation, option sync, change batching, and teardown go through `VirtualWindow`; the table keeps only a render-version counter and the "initialized" signal.
- Spacer rows, `data-index`, `measureElement` refs, row-key identity across sort, `VIRTUAL_ESTIMATED_ROW_HEIGHT`, overscan (10) and `maxClientRows` auto-enable are unchanged.
- No new public prop, event, or method; no behaviour change in any table feature.
- No leftover direct import of `Virtualizer`/`elementScroll`/`observeElement*` in `bds-table.tsx`.

**Manual test _(required — not waiveable)_:**

Playground scenarios in `packages/boreal-web-components/src/index.html`:

- Scenario 1: `bds-table` with `virtual` and `max-height`, 5,000 rows.
- Scenario 2: same table with sort enabled, selection enabled, and a row-detail template (expand a row).
- Scenario 3: table with 200 rows and no `virtual` but `max-client-rows="100"` (auto-enable).

Run `pnpm dev:components`:

- [ ] Given Scenario 1, when scrolling top to bottom, then only ~20–30 `tr` exist at any time and no blank gaps appear. Pass: DOM row count bounded; scrollbar proportional.
- [ ] Given Scenario 2, when sorting then scrolling, then rows keep identity and expanded detail rows remeasure without jumps. Pass: no flicker, no console errors.
- [ ] Given Scenario 3, when the page loads, then a single warning is logged and virtualization is active. Pass: matches pre-change behaviour.

**Commit:** `refactor(web-components): EOA-19598 move row virtualization onto VirtualWindow`

---

### Task 6: Retarget `bds-table` virtual specs

**Status:** done
**Executor:** @testing-subagent
**Files:**

- `bds-table.virtual.spec.ts` (modify)
- `bds-table.max-client-rows.spec.ts` (modify only if it reads the old private fields)

**Unit tests to cover:**

- Existing assertions keep their intent: teardown on disconnect, toggle `virtual` on/off after mount, placeholder-before-init (10 and 5,000 rows), real windowed rows + spacers after init, `measureElement` on row detail.
- Replace access to the private `virtualizer` field and the `BdsTable.prototype.initVirtualizer` spy with the new equivalents; do not weaken any assertion to make it pass.
- The rest of the `bds-table.*.spec.ts` files pass **unmodified**; any failure outside the two files above is a regression in T5, not a spec to edit.
- Coverage-phase only; mutation testing deferred to T19.

**Manual test:** N/A — validated via `pnpm test` for the whole `bds-table` directory.

**Commit:** `test(web-components): EOA-19598 retarget virtual specs to VirtualWindow`

---

### Task 7: `bds-table` manual regression check

**Status:** done
**Executor:** @qa-subagent
**Files:** none (verification-only)

**Acceptance criteria:**

- Re-runs T5's three scenarios in Chrome and Safari (Safari row-remount transition note must still hold: no animated flash on scroll).
- Also verifies the toolbar `searchable` button (`bds-search-bar mode="search"`) still renders and emits `bdsInputDebounced`.
- Optional smoke check: a `virtual` `bds-table` renders and scrolls through the React wrapper (pack-based build); the refactor is internal, so a pass here is expected.
- Any regression is logged as a new task, not fixed inline.

**Manual test (required):**

- [ ] Given a virtual table with 5,000 rows in Safari, when scrolling quickly, then no row animates on mount. Pass: no visible transition artifacts.
- [ ] Given `searchable` on a table, when typing, then `bdsInputDebounced` fires and the table behaves as before. Pass: matches `bds-table.toolbar.spec.ts` expectations.

**Commit:** N/A — verification-only task.

---

### Task 8: Search-bar types and `items` prop scaffold

**Status:** pending
**Executor:** @frontend-subagent
**Files:**

- `bds-search-bar/types/types.ts`, `ISearchBar.ts`, `index.ts` (modify)
- `bds-search-bar.tsx` (modify — prop declaration only)

**Utility discovery:**

- Feature area: suggestion item type.
- Search: `src/types/` (`menu.ts` has role/behavior types only), component `types/` folders; terms `Option`, `Suggestion`, `ListItem`. No reusable item type found.
- Reuse decision: new `SearchBarSuggestion` in the search bar's `types/`.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read `bds-search-bar.tsx` as it exists; list consumers of slotted mode (stories, mdx, specs) that must keep working.
- [ ] Boundary case: `items` set together with `mode="search"` → ignored with a `Logger` warning (no list exists in that mode).
- [ ] Boundary case: `items` set together with slotted `slot="list"` children → `items` wins, `Logger` warning once.
- [ ] Default/empty state: `items` is `undefined` by default → slotted mode. `items=[]` (defined, empty) → items mode showing the list's empty text. State this explicitly in JSDoc.
- [ ] Reactivity: `items` is reactive after mount; replacing it recomputes the filtered list for the current query and resets scroll to the top.
- [ ] Non-primitive prop → Vue/React pass it as a property; Storybook needs a manual source snippet (T16).

**Acceptance criteria:**

| name | type | default | reflect | description |
| --- | --- | --- | --- | --- |
| `items` | `SearchBarSuggestion[] \| undefined` | `undefined` | no | Suggestions rendered with windowing; only visible entries are mounted. |

- `SearchBarSuggestion`: required `value: string`, `label: string`; optional `disabled?: boolean`. Required members before optional.
- `ISearchBar` gains `items?`; interface field ordering rule respected.
- JSDoc on `items` is 1–2 sentences, consumer-facing only — never internal implementation details (which private getter or `@Watch` computes/consumes it, how it's wired to another member internally). Matches `ai-docs/guidelines/jsdoc-template.md`'s own worked examples.
- Prop has no behaviour yet (stub).

**Manual test:** non-visual — build compiles and `components.d.ts` regenerates with `items`.

**Commit:** `feat(web-components): EOA-19598 scaffold items prop and SearchBarSuggestion type`

---

### Task 9: Windowed rendering in `items` mode

**Status:** done
**Executor:** @frontend-subagent
**Files:**

- `bds-search-bar.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read `render()`, `componentDidLoad`, `disconnectedCallback`, `bdsListMenuEl` getter. Today the list is slotted via `<slot name="list">`; in `items` mode the search bar renders its own `<bds-list-menu slot="list" menu-role="listbox">` inside `bds-select`.
- [ ] Confirm scroll element: `.bds-list-menu__content` (`overflow-y: auto`, `max-height: var(--bds-list-menu-max-height, 240px)`). Use it directly; do not inject wrappers or inline overflow styles.
- [ ] Confirm which element carries `role="option"` inside `bds-list-menu-item` and where `aria-setsize`/`aria-posinset` must be set so assistive tech reads them (list-menu-item source must not be edited; set attributes on the host element from the search bar's render).
- [ ] Popover visibility: the list is hidden until the popover opens. Verify `observeElementRect` (ResizeObserver) picks up the 0 → N size change on open, otherwise mount/update on popover open.
- [ ] Item height: confirm rendered `bds-list-menu-item` height vs the 28 px estimate used today.

**Acceptance criteria:**

- In `items` mode only the virtual window (plus overscan 2, same as today) is rendered as `bds-list-menu-item`, keyed by `value`; 1,000 items mount at most ~20 elements.
- Top and bottom spacer elements are real, `aria-hidden` elements inside the list with computed heights (leading/trailing size); no absolute positioning, no `display: none` on items.
- Each mounted item carries `aria-setsize` = filtered count and `aria-posinset` = absolute index + 1.
- `VirtualWindow` is mounted/unmounted with the component lifecycle and updated when filtered count changes; no direct TanStack imports in the component.
- Slotted mode is unchanged by this task (still wired to the old controller until T13).
- Uses `VirtualWindow`; no component-local virtualizer logic.

**Manual test _(required — not waiveable)_:**

Playground scenarios in `src/index.html`:

- Scenario 1: `bds-search-bar` with `items` set to 1,000 generated entries.
- Scenario 2: same with 5 entries (smaller than the window).

Run `pnpm dev:components`:

- [ ] Given Scenario 1, when opening the list and inspecting the DOM, then ≤ ~20 `bds-list-menu-item` exist. Pass: count bounded, spacers present.
- [ ] Given Scenario 1, when scrolling to the bottom, then items swap and the last entry is reachable without gaps. Pass: scrollbar proportional, no blank area.
- [ ] Given Scenario 2, then all 5 render with zero-height spacers. Pass: no layout shift.

**Commit:** `feat(web-components): EOA-19598 render windowed suggestions from items`

---

### Task 10: Data-side filtering, clear and empty state

**Status:** done
**Executor:** @frontend-subagent
**Files:**

- `bds-search-bar.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `searchOwnData` is called from `scheduleDebounced` and `handleFieldClear`; `virtualScroll.refresh()` from `scheduleDebounced`, `handleFocus`, `handleFieldClear`. List each and decide per mode.
- [ ] Verify `bds-select` does not filter in this configuration: `managed` makes `listenField` return before `searcherElement`; confirm still true at execution time.
- [ ] Match today's rule exactly: case-insensitive `includes` against both label text and `value`.
- [ ] Default/empty state: empty query → full list, scroll reset to top (`scrollToIndex(0)`); zero matches → `list.empty = true`.
- [ ] Debounce: filtering runs after the existing unconditional debounce in `mode="list"`; do not change timing.

**Acceptance criteria:**

- In `items` mode the filtered list is computed from the array (not the DOM), stored as the window's `count` source, and `searchOwnData` is not used.
- Clearing resets the query, window scroll, and filtered list; `bdsClear`/`bdsInput`/`valueChange` emissions are unchanged.
- Zero matches sets `empty` on the rendered `bds-list-menu`; a polite live region announces the result count ("N results", 0 handled).
- Slotted mode keeps `searchOwnData` unchanged.

**Manual test _(required — not waiveable)_:**

- Scenario 1: `items` = 1,000 entries named "Item 1…1000".

Run `pnpm dev:components`:

- [ ] Given Scenario 1, when typing "99", then the list shows only matches and the scrollbar shrinks. Pass: matches Item 99, 199…, count announced.
- [ ] Given a query with no matches, then the empty text shows. Pass: no items mounted.
- [ ] Given a filtered list, when clearing, then the full list returns scrolled to the top. Pass: first item visible.

**Commit:** `feat(web-components): EOA-19598 filter windowed suggestions from data`

---

### Task 10b: Fix text wipe and focus loss on Tab to the clear button

**Status:** done
**Executor:** @frontend-subagent (fix), @testing-subagent (regression spec), @qa-subagent (manual test)
**Origin:** reported during T10 review; QA proved it is pre-existing (identical on `096ae1ad`), present in every `clearable` `mode="list"` search bar (slotted and `items`), and absent in `mode="search"` (the table's search bar). Fixed in this PR at the user's request.
**Files:**

- `bds-search-bar.tsx` (modify — `handleSelectChange`)
- `__test__/bds-search-bar.events.spec.ts` (modify)

**Root cause (QA stack traces):** typing and then pressing Tab fires the browser's native `change` on the input; `bds-text-field` forwards it as `bdsChange` with an object detail `{ value, event }`; it bubbles through `bds-select` to `handleSelectChange`, which treats every `bdsChange` as a select commit and sets `value` to `''`. That emits `valueChange ""` / `bdsSearch ""`, re-renders the host with an empty value, wipes the typed text and removes the clear (X) button while it is focused, so focus falls to `body`. The same path emits the spurious `valueChange ""` / `bdsSearch ""` before a pick that follows typed text. Ruled out: `bds-select.listenBlurInput`, popover dismissal, `bds-text-field` itself.

**Acceptance criteria:**

- `handleSelectChange` keeps `stopPropagation()` and ignores events whose target is not the `bds-select` itself (`e.target !== e.currentTarget`); genuine select commits behave as before.
- Type a query, press Tab: the text is kept, focus lands on the X, Enter/Space clears the text and returns focus to the input.
- A realistic click (mouse held 300 ms) on the X clears the text and emits `bdsClear`.
- Picking an item after typing emits exactly one `bdsSearch` with the picked value (no preceding `bdsSearch ""` / `valueChange ""`).
- Expected UX: a search box does not discard typed text only because focus moved. QA reports what happens when Tab continues past the X (text, `value`, popover, events). Any change to that behaviour needs the user's decision first; none is made in this task.
- `mode="search"` behaviour unchanged.
- No change to `bds-select` or other components.

**Unit tests:** regression tests in the events spec for list and `items` mode: forwarded text-field `bdsChange` keeps `value` and emits nothing; genuine select pick / clear still work; typed text then a pick emits exactly one `bdsSearch`.

**Manual test _(required — not waiveable)_:** real keyboard and mouse input in Chrome, scenarios D, F, A (slotted `clearable`, plain, `items`) and the table search bar:

- [ ] Given typed text, when pressing Tab, then the text is kept and the X is focused. Pass: text intact, `document.activeElement` is the X.
- [ ] Given the X focused, when pressing Enter or Space, then the text clears, `bdsClear` fires and focus returns to the input.
- [ ] Given a click held 300 ms on the X, then the text clears and `bdsClear` fires. Pass: not removed mid-press.
- [ ] Given typed text, when picking an item, then exactly one `bdsSearch` with the item value. Pass: no empty emission first.
- [ ] Given typed text, when Tabbing past the X, then report what happens (text, value, popover, events) for the UX decision.
- [ ] Table search bar unchanged.

**Commit:** `fix(web-components): EOA-19598 ignore text-field change events in search bar select handler`

---

### Task 10c: Reopen the suggestions popover when typing

**Status:** done
**Executor:** @qa-subagent (baseline), @frontend-subagent (fix), @testing-subagent (regression spec), @qa-subagent (manual test)
**Origin:** reported during T10b review. After the popover closes (pick, Escape, keyboard clear), typing again does not reopen it; the user must press Enter or Escape. Hypothesis from source: the search bar always renders `<bds-select managed>`, and `bds-select.listenField` returns on `managed` (line ~605) before its `openPopover()` call (line ~613), so typing never opens the popover in the search bar, while an unmanaged searchable `bds-select` opens it. Expected behaviour per the W3C APG combobox pattern: for an editable combobox with list autocomplete, the popup appears as the user types.
**Files:**

- `bds-search-bar.tsx` (modify — input handling)
- `__test__/bds-search-bar.events.spec.ts` or `basics.spec.ts` (modify)

**Baseline QA (before any change):** side by side, with real keyboard input, a searchable `bds-select` vs the search bar (slotted 30 items, `items` 1,000, and the `clearable` variant): type, pick, type again; type, Escape, type again; type, clear via X (mouse and keyboard), type again; record popover open/closed, `aria-expanded`, and events after each step. Purpose: confirm the hypothesis and that the select reopens on typing, so the fix targets the search bar.

**Acceptance criteria:**

- In `mode="list"`, typing a non-empty value opens the popover when it is closed and the bar has a list (an `items` list or a slotted list), in slotted and `items` mode; an already-open popover is not toggled or re-opened (no flicker, no repeated open events).
- Typing after a pick, after Escape, and after clearing (mouse or keyboard) reopens the list.
- `mode="search"` is unchanged (no list).
- Clearing by emptying the text via the keyboard does not leave the popover stuck; behaviour matches the baseline select where the select is the reference.
- No change to `bds-select`.

**Manual test _(required — not waiveable)_:** the side-by-side QA above, repeated after the fix; plus keyboard checks that ArrowDown still moves into the list and Escape still closes it.

**Commit:** `fix(web-components): EOA-19598 reopen suggestions popover on typing`

---

### Task 11: Keyboard navigation in `items` mode

**Status:** pending
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `bds-search-bar.tsx` (modify)

**Utility discovery:**

- Feature area: keyboard navigation / roving focus.
- Search: `src/utils/a11y/keyboard/` (`KeyboardController`, `navigation/`, `focus/`), usage in `bds-list-menu` (`setLinearNavigation`) and `bds-select`.
- Candidates: `KeyboardController` — fits for key binding (it supports capture listeners; confirm API). `setLinearNavigation` operates over mounted DOM items — does not fit windowed navigation.
- Gap handling: bind via the shared controller (or `addElementListener` with capture) and only reuse its key constants; windowed index math lives in the search bar since the shared navigation assumes all items mounted. Document the gap in the task write-up.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read `bds-list-menu._setupKeyboard` (linear nav with `wrap: true` over mounted items) and `bds-list-menu.focusFromTriggerKey` (ArrowUp prefers last mounted); read `bds-select.handleArrowNavigation`. All see only the window.
- [ ] Decide interception point: a capture-phase listener on the search bar host runs before both the input's select handlers and the list-menu's bubble-phase controller; confirm with a spike before relying on it, and confirm `stopPropagation` prevents list-menu wrap.
- [ ] Keys to own in `items` mode: ArrowUp, ArrowDown, Home, End, PageUp, PageDown (when the list is open). Enter/Escape/Tab keep current behaviour (Tab-select uses `bds-list-menu-item:focus`, still valid for a mounted focused item).
- [ ] Boundary: moving past the window edge → `scrollToIndex(target)`, wait one `requestAnimationFrame` (see `keyboard-triggered-focus-move-double-activation.md`), then focus the mounted target and set `active-item`/`tabindex` exactly as `bds-list-menu` does.
- [ ] Wrap behaviour: preserve today's `wrap: true` semantics across the whole filtered list, not the window.
- [ ] Disabled items are skipped by index, not by DOM query.

**Acceptance criteria:**

- ArrowDown/ArrowUp/Home/End/PageUp/PageDown navigate the whole filtered list, wrapping at the ends, skipping disabled entries, including across window boundaries.
- Opening via ArrowDown/ArrowUp from the input focuses the first / last relevant entry of the **full** list (ArrowUp with nothing selected → true last entry), not the last mounted one.
- Focus lands on a mounted item after scroll; no double activation; no focus loss when the focused item is unmounted by scrolling with the mouse.
- Slotted mode keyboard behaviour is unchanged.

**Manual test _(required — not waiveable)_:**

- Scenario 1: `items` = 1,000 entries, item 500 disabled.

Run `pnpm dev:components`:

- [ ] Given the list open, when holding ArrowDown past the window, then focus advances item by item and the list scrolls. Pass: no skipped items, 500 skipped.
- [ ] Given focus on the last entry, when pressing ArrowDown, then focus wraps to the first. Pass: first item focused and visible.
- [ ] Given the list closed, when pressing ArrowUp on the input, then the last entry (1,000) is focused. Pass: item 1,000 visible.
- [ ] Given a screen reader or the accessibility tree, then each item exposes position/set size. Pass: `aria-posinset` correct after scrolling.

**Commit:** `feat(web-components): EOA-19598 window-aware keyboard navigation for items`

---

### Task 12: Selection and label resolution

**Status:** pending
**Executor:** @frontend-subagent
**Files:**

- `bds-search-bar.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Read `handleSelectChange`, `value` watcher, `renderTextField`, and how `bds-select.loadValue` sets `valueString`/the field text. Record what the field shows today in slotted mode when `label !== value`; `items` mode must match that observable behaviour, not improve on it.
- [ ] Confirm `bds-select.loadValue` returns early when the option is not mounted → for a programmatic `value` outside the window, the label must come from `items`, not the DOM.
- [ ] Reactivity: `value` set externally (after mount) to an entry outside the window shows the correct label and marks the entry selected when it scrolls into view.
- [ ] Boundary: `value` that matches no entry → treated as free text, no selection (as today).

**Acceptance criteria:**

- Each mounted item gets `selected` from `value`; picking an item emits `bdsSearch`/`valueChange`/`bdsChange` handling exactly as `handleSelectChange` does today.
- Label for the current `value` is resolved from `items`.
- Multiselect, select-all, and groups are explicitly unsupported in `items` mode and documented (T16).

**Manual test _(required — not waiveable)_:**

- [ ] Given `value` set programmatically to entry 900, when the list opens, then entry 900 is marked selected once visible and the field shows its label. Pass: label correct without scrolling first.
- [ ] Given a pick via click, then `bdsSearch` fires with the entry's value. Pass: event payload matches.

**Commit:** `feat(web-components): EOA-19598 resolve selection and labels from items`

---

### Task 12b: Early React / Vue wrapper smoke check

**Status:** pending
**Executor:** @qa-subagent
**Files:** none (verification-only)

**Why here:** T9–T12 are verified against the raw web component only. Wrapper problems (array props, `v-model`, event names) are cheaper to catch before T13–T16 build on top of them. T18 stays as the final full parity pass.

**Acceptance criteria:**

- Builds the wrappers with the pack-based pipeline (`validate:pack`, see `.agents/memory/scripts-boreal-pack-pipeline.md`), not a live dev server.
- React: `items` with 1,000 entries is applied as a property, only the window mounts (≤ ~20 `bds-list-menu-item`), typing filters, a pick emits `bdsSearch` with the entry's value.
- Vue: same scenario with `v-model` on `value`; the value round-trips after a pick and after clearing.
- Regressions are logged as new tasks, not fixed inline.
- Scenarios (or a note on where they live) are left in the local playground / validation app for reference; the decision to push them is made at the end of the plan.

**Manual test (required):**

- [ ] Given the React wrapper with 1,000 `items`, then only the window mounts, filtering works, and picking emits `bdsSearch`. Pass: matches the raw component.
- [ ] Given the Vue wrapper with `v-model`, then value updates round-trip. Pass: matches the raw component.

**Commit:** N/A — verification-only task.

---

### Task 13: Remove `VirtualScrollController` and slotted-path wiring

**Status:** pending
**Executor:** @frontend-subagent
**Files:**

- `bds-search-bar.tsx` (modify)
- `utils/dom/virtualScroll/virtual-scroll.ts` (delete)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Re-grep the repo for `VirtualScrollController`/`virtualScroll` (planning-time result: only `bds-search-bar.tsx` imports it; not exported from any barrel).
- [ ] Call sites to remove: import, field, `attach` in `componentDidLoad`, `detach` in `disconnectedCallback`, `refresh()` in `scheduleDebounced`/`handleFocus`/`handleFieldClear`, `scrollToIndex(0)` in `handleFieldClear`.
- [ ] Slotted mode afterwards: all items stay mounted and unvirtualized; `searchOwnData` (DOM filter) is the only filtering path there.

**Acceptance criteria:**

- No reference to the controller remains; file deleted.
- Slotted-mode behaviour (filtering, selection, empty state) unchanged except that it is no longer positioned/virtualized.
- The class JSDoc/`@slot list` documentation no longer claims automatic virtualization; it points to `items` for large lists.

**Manual test _(required — not waiveable)_:**

- Scenario 1: slotted `bds-list-menu` with 30 items.

Run `pnpm dev:components`:

- [ ] Given Scenario 1, when typing and picking, then filtering/selection work and items are normally laid out. Pass: no absolute positioning or `display: none` on visible items.
- [ ] Given the slotted search bar with 30 items rendered through the React and Vue wrappers (pack-based build), when typing and picking, then filtering/selection work as in the raw component. Pass: no behavioural difference. This covers the slotted path, which T12b and T18 do not.

**Commit:** `refactor(web-components)!: EOA-19598 remove VirtualScrollController in favor of items`

---

### Task 14: SCSS — spacers and Safari remount rule

**Status:** pending
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `bds-search-bar.scss` (modify)

**Figma research pass (complete before writing any SCSS):**

This task introduces no new designed regions. The pass confirms nothing visual changes:

- [ ] Region: suggestion list item — default state: confirm computed height equals the 28 px estimate and matches the slotted rendering pixel-for-pixel. Value (unconfirmed — re-measure in browser).
- [ ] Region: suggestion list item — hover / focus / active / selected / disabled: rendered identically to slotted mode (no Figma pull needed; no appearance change; record "no difference").
- [ ] Combination: selected + hover and active-item + hover on windowed items: same as slotted.
- [ ] Dimensions: list item height vs `estimateSize` — if they differ, update the estimate in T9 rather than adding styles.

**Acceptance criteria:**

- Spacer elements have zero visual footprint other than height (no margin/padding/border); no hard-coded colours, spacing or radii; tokens via `var(--boreal-*)` only.
- Rule disabling the item transition (`transition: none`, `will-change: auto`) is scoped to windowed items in `items` mode only, per `safari-virtualized-row-transition-on-remount.md`. The host-level selector is the search-bar root tag block (light DOM; no `:host`), and every selector is nested inside it.
- Verified against the **compiled** CSS output that each selector matches DOM the component actually renders.
- Chained executor manual test covers Safari.

**Manual test _(required — not waiveable)_:**

- [ ] Given a 1,000-item `items` list in Safari, when scrolling quickly, then items do not animate on mount. Pass: no transition artifacts.
- [ ] Given Chrome, then spacing/hover/selected visuals match the slotted list. Pass: no visual diff.

**Commit:** `style(web-components): EOA-19598 spacer and windowed item rules`

---

### Task 15: Search-bar unit tests

**Status:** pending
**Executor:** @testing-subagent
**Files:**

- `__test__/bds-search-bar.basics.spec.ts` (modify)
- `__test__/bds-search-bar.items.spec.ts` (create — windowing, precedence, reactivity)
- `__test__/bds-search-bar.events.spec.ts` (modify)
- `__test__/bds-search-bar.a11y.spec.ts` (modify)
- `__test__/bds-search-bar.keyboard.spec.ts` (create)

**Unit tests to cover** _(grouped by spec file)_:

- `items` — only the window renders for 1,000 entries; spacers' heights; `items=[]` vs `undefined`; `items` + slotted children (items wins, warning); `items` + `mode="search"` (ignored, warning); replacing `items` recomputes and resets scroll.
- `basics` — data-side filtering rule (case-insensitive label/value), clear resets, empty state, debounce timing unchanged; slotted mode still filters via `searchOwnData`.
- `events` — pick emits `bdsSearch`/`valueChange` with the entry value; label vs value resolution; programmatic `value` outside window.
- `a11y` — `aria-setsize`/`aria-posinset`, live region count, spacers `aria-hidden`.
- `keyboard` — window-edge navigation, wrap across full list, disabled skipping, ArrowUp-to-last on open. Window size stubbing follows the shared rect stub from T4; scroll-then-focus uses `flushMicrotasks()` before `waitForChanges()`.
- Existing slotted-mode specs pass unmodified (except removed controller assumptions).
- Coverage-phase only (≥80%); mutation testing deferred to T19.

**Manual test:** N/A — non-visual task, validated via `pnpm test` and the coverage report only.

**Commit:** `test(web-components): EOA-19598 cover windowed items mode`

---

### Task 16: Story and MDX

**Status:** pending
**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.stories.ts` (modify)
- `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.mdx` (modify)
- `apps/boreal-docs/src/stories/forms/bds-select/bds-select.mdx` (modify)

**Acceptance criteria:**

- `LargeSuggestionsList` uses `items` with 1,000 entries via Lit property binding; the "Show code" snippet is overridden with manual HTML + `<script>` per `storybook-source-snippet-non-primitive-props.md`.
- Doc comments no longer claim slotted lists are virtualized; they state: slotted = small lists, all mounted; `items` = large lists, only visible entries mounted.
- MDX documents `items`/`SearchBarSuggestion`, precedence rules, v1 limitations (single-select, flat, fixed row height), and the keyboard/a11y behaviour.
- `bds-select.mdx`: fix the wrong tag name (`<bds-searchbar>` → `bds-search-bar`), point large local lists (hundreds to thousands) to `bds-search-bar` with `items`, keep the async/server-search pointer for server-driven data, and link to the comparison section.
- `bds-search-bar.mdx`: replace the "Performance" section's claim of automatic virtualization (and the "hundreds–1000 items" guidance) with the `items` explanation, and add a short "`bds-select` vs `bds-search-bar`" decision section that leads with intent, then size. Intent: choose one of the allowed values (multiselect, groups, enforced selection) → `bds-select`; search with suggestions where free text is allowed → `bds-search-bar`. Size, as a consequence: ≤ ~200 options → `bds-select`; hundreds to thousands of local suggestions → `bds-search-bar` `items` (windowed); server-driven → `mode="search"` + `async`. State the `items` v1 limits plainly (single-select, flat, fixed row height; no multiselect, select-all or groups). Do not claim `bds-select` will never be virtualized; list "windowing for `bds-select`" only as a possible future ticket in the plan notes, not in user-facing docs. Verify against source whether the search bar participates in form validation/submission before documenting any form behaviour.
- The story comment and the class JSDoc/`@slot list` text no longer claim automatic virtualization of slotted lists; `items` is named as the large-list path.
- Story argTypes/actions follow `ai-docs/guidelines/storybook-patterns.md`.
- Docs state that slotted-list filtering matches on each item's `value` only, while `items` filtering matches `label` or `value` (case-insensitive), and that `mode="search"` only emits `bdsInputDebounced` when `async` is set (observed in T10 QA).

**Manual test _(required — not waiveable)_:**

Run `pnpm dev:docs`:

- [ ] Given Forms → Search Bar → `LargeSuggestionsList`, when the story loads, then it renders quickly and DOM shows only the window. Pass: ≤ ~20 items in DOM; snippet shows the `items` assignment.

**Commit:** `docs(docs): EOA-19598 document items mode and large suggestion list`

---

### Task 17: Search-bar manual QA and measurement

**Status:** pending
**Executor:** @qa-subagent
**Files:** none (verification-only)

**Acceptance criteria:**

- Runs T9–T12 scenarios end to end in Chrome and Safari, and the T16 story in Storybook.
- Records before/after for `LargeSuggestionsList`: mounted `bds-list-menu-item` count (1,000 vs window) and initial script/render time (Performance panel or `performance.now()`), closing the bug report's profiling Known Gap.
- Regression pass for the untouched `bds-select` consumers: `bds-pagination` items-per-page and `bds-date-picker` time selector open, select, and keyboard-navigate as before; and the slotted search bar with 30 items.
- Any regression is logged as a new task.

**Manual test (required):**

- [ ] Given the story before/after numbers are captured, then the report shows the instance-count drop. Pass: numbers recorded in the bug report's Known Gaps.
- [ ] Given pagination and date-picker selects, then behaviour is unchanged. Pass: no differences.

**Commit:** N/A — verification-only task.

---

### Task 18: React / Vue wrapper parity

**Status:** pending
**Executor:** @qa-subagent
**Files:** none (verification-only)

**Acceptance criteria:**

- Re-verifies T9–T12 scenarios through both wrappers using the pack-based pipeline (`validate:pack`), not a live dev server.
- Specifically checks that the array `items` prop is applied as a property in React and Vue, and that `bdsSearch`/`valueChange` (v-model) behave as in the raw component.
- Final pass after T14 and T16: also covers the SCSS/Safari behaviour and re-checks the T12b scenarios plus keyboard navigation through the wrappers. T12b is the early smoke check; this task is the full parity pass.
- Regressions are logged as new tasks.

**Manual test (required):**

- [ ] Given the React wrapper with 1,000 `items`, then only the window mounts and picking emits `bdsSearch`. Pass: matches raw component.
- [ ] Given the Vue wrapper with `v-model`, then value updates round-trip. Pass: matches raw component.

**Commit:** N/A — verification-only task.

---

### Task 19: Consolidated mutation testing

**Status:** pending
**Executor:** @testing-subagent
**Files:**

- Stryker configs for `VirtualWindow`, `bds-search-bar` (one config per unit, create or extend)

**Acceptance criteria:**

- Read `.agents/memory/mutation-testing-stryker-setup.md` and `mutation-testing-workflow-decisions.md` first; apply the bar those files require (the testing gate is ≥90%; the workflow-decisions file states a stricter bar — follow the stricter one).
- Survivors that reveal real gaps are closed by extending the earlier spec files (T4, T6, T15); no new behaviour is introduced.
- Stryker stays local-only (never pushed).

**Manual test:** N/A — validated via Stryker reports.

**Commit:** `test(web-components): EOA-19598 close mutation survivors`

---

### Task 20: Full gate and Chromatic timing

**Status:** pending
**Executor:** @release-subagent
**Files:** none

**Acceptance criteria:**

- Lint, build, and the full unit suite pass; `components.d.ts` diff contains only the `items` addition.
- Wrapper validation (`validate:pack` / `validate:all`) passes.
- Storybook build timing for `LargeSuggestionsList` is captured before/after, or the actual failed-build log is attached to the bug report, closing the Known Gap on the Chromatic timeout.

**Manual test:** N/A — CI-style verification; record results in the bug report.

**Commit:** N/A unless a fix is needed.

---

### Task 21: Knowledge capture

**Status:** pending
**Executor:** @knowledge-keeper (via `subagent`)
**Files:**

- `.agents/memory/` (new entry + `MEMORY.md` index row)

**Acceptance criteria:**

- Records: windowed lists need data-side filtering/keyboard because `bds-list-menu`'s linear navigation and `bds-select` item queries only see mounted items; `managed` bypasses `bds-select` filtering; `VirtualWindow` is the shared wrapper; positional `display:none` virtualization was rejected and why.
- Does not duplicate content already in the bug report or research spikes; links to them.

**Manual test:** N/A — docs-only.

**Commit:** `docs(workspace): EOA-19598 record windowed list constraints`

---

### Task 22: Pre-existing duplicate / spurious `bds-search-bar` event emissions (both modes)

**Status:** deferred
**Executor:** to be decided with the user (separate ticket candidate)
**Origin:** logged from T10 QA (Chrome, same event sequences in slotted and `items` mode, so not introduced by EOA-19597).

**Observations (current code, both modes):**

- One X-clear click emits `bdsClear` and `valueChange ""` more than once (the inner `bds-select` / `bds-text-field` events bubble to the host in addition to the component's own emission).
- Escape emits `bdsInput ""` and `valueChange ""` twice.
- Picking an item after typing a query first emits `valueChange ""` and `bdsSearch ""` before the real `bdsSearch {value}`; picking with no query does not. **Resolved by T10b** (same root cause); keep it here only as a regression reference.
- "Pre-existing" means also present in slotted mode on the current code; it was not compared against a pre-EOA-19597 build.

**Acceptance criteria:** none yet. Decide with the user whether to fix here, in a separate ticket, or leave. The plan cannot be marked `done` until this is completed or explicitly re-scoped into its own ticket (plan-execution rule).

**Commit:** N/A until scoped.
