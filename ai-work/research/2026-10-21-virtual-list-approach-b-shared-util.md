---
ticket: —
component: bds-search-bar
status: exploring
---

# Virtual list — Approach B: shared windowing helper extracted from bds-table

## Goal

Resolve `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`: only the visible window of suggestions should exist as mounted `bds-list-menu-item` elements (Finding 1), and the `display:none` + `ResizeObserver` bug class (TanStack/virtual#823) should go away (Finding 2). Approach B extracts the `Virtualizer` lifecycle that `bds-table` already runs into one framework-agnostic utility and uses it from both `bds-table` and `bds-search-bar`.

## Options evaluated

1. **B1. Shared lifecycle helper, data-driven items on `bds-search-bar`** (recommended shape). The helper handles the Virtualizer only. Each component renders its own rows.
2. **B2. Shared helper, window over slotted children by detaching and reattaching.** A fallback for consumers who keep the slotted API.
3. **B3. Vaadin-style `createElements(n)` / `updateElement(el, index)` imperative recycler.** Closer to Vaadin's `virtualizer.js`, which shares one class between `vaadin-virtual-list` and `vaadin-grid`.
4. **B4. Leave `VirtualScrollController` as is and only fix the docs** (bug report option 1). Not part of B. Listed as the baseline.

## Findings

### Current state

- `bds-table` (`bds-table.tsx`) runs this lifecycle:
  - `initVirtualizer` (~l.1037): `new Virtualizer({count, getScrollElement, estimateSize, overscan: 10, scrollToFn: elementScroll, observeElementRect, observeElementOffset, measureElement, onChange})`, then `_didMount()` and `_willUpdate()`.
  - `onChange` goes through `scheduleVirtualRerender` (~l.1194), which batches in a microtask and bumps the `@State virtualVersion`.
  - `syncVirtualizerOptions` (~l.1299) calls `setOptions({...options, count})` followed by `_willUpdate()`.
  - `teardownVirtualizer` (~l.1305) runs the `_didMount` cleanup.
  - `renderVirtualRows` (~l.2073) emits spacer rows plus `virtualItems.map`. `ref={el => virtualizer.measureElement(el)}` and `data-index` give dynamic height.
  - The table itself owns `VIRTUAL_ESTIMATED_ROW_HEIGHT` and the `maxClientRows` auto-enable.
- `VirtualScrollController` has the same Virtualizer setup. It differs by `querySelectorAll` collection, `MutationObserver`, a wrapper `div[data-bds-virtual-content]` that it injects and reparents children into, and `display:none` plus `translateY` positioning. It has one consumer: `bds-search-bar.tsx` (attach at l.625, `refresh()` at l.196, l.295, l.363, `scrollToIndex(0)`).
- Search in `bds-search-bar` (`searchOwnData`) and in `bds-select` (`searcherElement`, ~l.685) both iterate `querySelectorAll('bds-list-menu-item')` and set `hidden`. With a window there is nothing to iterate over, so **filtering must move from DOM to data**. This is the main cost of the whole effort.
- `bds-select` couples to mounted items in several places:
  - Roving focus and type-ahead use `querySelectorAll(ENABLED_ITEMS_SELECTOR)` with `el.focus()` (~l.203-225).
  - Enter reads `bds-list-menu-item:focus` (~l.236).
  - Selected-label lookup uses `querySelector('bds-list-menu-item[value=...]')` plus `.bds-list-item__content-left__text` (~l.488, ~l.755).
  - Multiselect and select-all count items (~l.444, l.479).
  - So **a windowed list breaks the selected label** when the chosen item is off-screen. The label text must come from data.
- `bds-list-menu` is a `<slot>` host with no data API. `bds-list-menu-item` is a plain element with `value`, `selected`, `active-item`, `disabled`, `variant`, and the text in the default slot.

### Shared helper design (B1)

New files under `src/utils/dom/virtualWindow/`:

- `virtual-window.ts`
- `types.ts`
- `__test__/virtual-window.spec.ts`

```ts
export interface VirtualWindowOptions {
  count: number;
  getScrollElement: () => Element | null;
  estimateSize: (index: number) => number;
  overscan?: number;
  measure?: boolean;
  getItemKey?: (index: number) => string | number;
  onChange: () => void;
}

export interface VirtualWindowItem { index: number; key: string | number | bigint; start: number; end: number; size: number; }

export class VirtualWindow {
  constructor(options: VirtualWindowOptions);
  mount(): void;
  update(patch: Partial<VirtualWindowOptions>): void;
  unmount(): void;
  getItems(): VirtualWindowItem[];
  getTotalSize(): number;
  getLeadingSize(): number;
  getTrailingSize(): number;
  measureElement(el: Element | null): void;
  scrollToIndex(index: number, opts?: { align?: 'start' | 'center' | 'end' | 'auto' }): void;
  readonly virtualizer: Virtualizer<Element, Element>;
}
```

Behaviours moved out of `bds-table`:

- Create the Virtualizer with `observeElementRect`, `observeElementOffset` and `elementScroll`.
- `mount()` calls `_didMount()` then `_willUpdate()`, and stores the cleanup.
- `update()` is `setOptions` plus `_willUpdate()`, and runs only when `count` or other options changed.
- `onChange` is coalesced in a microtask, so the host can safely bump an `@State` counter.
- `unmount()` runs the cleanup and nulls the Virtualizer.

The helper imports no Stencil. Components keep `@State version` and call `getItems()` in `render()`.

### bds-table refactor

- Replace `initVirtualizer`, `syncVirtualizerOptions`, `scheduleVirtualRerender`, `teardownVirtualizer` and the `_virtualizerCleanup` / `_virtualRerenderScheduled` fields with one `VirtualWindow` field.
- `renderVirtualRows` keeps its JSX and reads `getItems()`, `getLeadingSize()` and `getTrailingSize()`.
- The `@State virtualizer` and `virtualVersion` stay, because the placeholder-before-init render depends on `virtualizer === undefined`.
- Test impact: `bds-table.virtual.spec.ts` (620 lines) asserts DOM (spacer heights, `data-index`, placeholder, row-detail `measureElement` spy, lifecycle). The spy on `measureElement` and any `rootInstance.virtualizer` access will need retargeting to `virtualWindow`. Expect low-to-medium churn in that one file, not in the other 18 table specs.
- Risk: low if the extraction is move-only. Watch these:
  - The microtask-batched rerender must keep its timing, because the pre-virtualizer placeholder test and the "placeholder is replaced after init" test depend on it.
  - The Safari `transition: none` fix (`safari-virtualized-row-transition-on-remount.md`) is CSS on rows. It is untouched, but the new search-bar items will need the same scoped rule, because windowed items remount on scroll.
  - Row-identity keying across sort must be preserved: pass `getItemKey` equal to the row id.

### Data source for search-bar (the real design question)

- **A. New `items` prop on `bds-search-bar`** (recommended): `items: SearchBarSuggestion[]` where `SearchBarSuggestion = { value: string; label: string; disabled?: boolean; group?: string }`.
  - Non-primitive props follow the established storybook pattern: manual source snippet override, per `storybook-source-snippet-non-primitive-props.md`.
  - Search-bar filters the array itself (same case-insensitive `label`/`value` rule as `searchOwnData` today).
  - It renders `<bds-select slot><bds-list-menu slot="list" role=listbox>` plus spacer elements, plus `filtered.slice(window).map(item => <bds-list-menu-item key=value value=... selected=... />)`.
  - Spacers must be **real elements inside the `bds-list-menu` default slot**: a top and a bottom `div[aria-hidden]` of computed height. The `bds-table` model avoids absolute positioning and so avoids the Safari transform transition.
  - Where does it render? `bds-search-bar` currently has the consumer-provided `bds-list-menu` as slotted content of itself and renders `bds-select` around it. With `items` set, `bds-search-bar` must render its own `bds-list-menu` and ignore or warn about slotted ones.
- **B. `items` on `bds-list-menu`** instead. A more general fix, since `bds-select` would get windowing too. But it makes `bds-list-menu` data-aware (today it is a pure slot host with a `menu`/`listbox` role) and drags in selection, groups, label variants and checkboxes. Too broad for this ticket. Revisit later.
- **C. Keep slotted children as a fallback** (B2): **do not.** Parsing consumer light-DOM children into data and then detaching them is fragile:
  - Custom elements are already upgraded at connect time, so the instantiation cost is already paid (Finding 1 stays).
  - It conflicts with Stencil's non-shadow slot relocation (`stencil-non-shadow-slot-relocation-timing.md`).
  - Consumer-owned child lifecycle is violated.
  - The existing path stays as a **deprecated, non-windowed** path (see below).

### bds-select coupling with a windowed list

`bds-search-bar` wraps `bds-select`, which does DOM-based filtering, focus-based navigation and DOM-based label lookup. Options:

1. **Search-bar bypasses bds-select's searcher in `items` mode.** `bds-select` has `managed`, which suggests there is already a mode where the host owns state. Verify exactly what `managed` suppresses (`handleManagedActivate`) before relying on it. Filtering then happens on data.
2. **Keyboard navigation.** `bds-select` roving focus needs a mounted target. Fix: when ArrowDown or ArrowUp goes past the window edge, search-bar scrolls via `scrollToIndex(next)`, waits one render, then focuses the mounted item. Use `requestAnimationFrame` as in `keyboard-triggered-focus-move-double-activation.md`. The `bds-select` change is small: replace "query DOM items" with an optional `getItems` hook, or intercept ArrowUp/Down in search-bar capturing phase.
3. **Selected label.** Search-bar already works from `value` text and `bdsChange`. In `items` mode, resolve the label from the `items` array by `value`, never from a mounted `bds-list-menu-item`.
4. **Multiselect, select-all and count** are not used in `bds-search-bar` (single selection). Do not support in `items` mode and document it.
5. **Spacers inside the list** must be skipped by roving focus (they are not `bds-list-menu-item`, so the existing selector already ignores them).

### A11y

- Roving DOM focus works today and can continue: items get `role=option` from `bds-list-menu-item` under a listbox.
- On each mounted item add `aria-setsize={filtered.length}` and `aria-posinset={index + 1}` (needs `bds-list-menu-item` to accept and forward them, or search-bar sets the attributes after render with `updateElementAttr`). Without these, screen readers announce only the window size.
- Alternative: switch to `aria-activedescendant` on the combobox input, with focus staying on the input. This survives item unmount better (the descendant id can refer to the next window item). It is the better long-term ARIA combobox pattern but is a behaviour change: today's focus-on-item flow with `active-item` styling would need to be re-done. It is a separate decision; **do not combine with this ticket**.
- Announce result count via a polite live region ("N results"), which also covers filtered-to-empty (`empty` prop on `bds-list-menu`, today set in `searchOwnData`).

### Interaction with `VirtualScrollController`

- In `items` mode, search-bar uses `VirtualWindow` and does **not** call `VirtualScrollController.attach`.
- Keep `VirtualScrollController` for slotted mode, marked `@deprecated`, with the doc comment on `LargeSuggestionsList` corrected as in the bug report's option 1. Remove it in the next major.
- Alternative: reimplement `VirtualScrollController` as a thin facade on `VirtualWindow`. That fixes Finding 2 (below) but not Finding 1. A cheap interim for Finding 2 is to `unobserve` before `display:none`, as in TanStack/virtual#531.

### Vaadin-style alternative (B3), brief

- `createElements(n)` plus `updateElement(el, index)` recycling a fixed pool needs no framework render, so it suits both Stencil and plain web components, and it avoids remount churn (and thus the Safari transition problem).
- Costs here:
  - We would write our own recycler, handle scroll anchoring, and drop the TanStack dependency's measurement model.
  - `bds-table` already works with VDOM keyed rows, so moving it to a pool is a rewrite with real regression risk.
  - Mutating `bds-list-menu-item` props from outside Stencil's render fights VDOM.
- Verdict: not worth it. The VDOM windowing already proven in `bds-table` is cheaper.

### How this covers the bug report

- **Finding 1 (DOM count):** fixed for `items` mode. Only the window plus overscan exist as mounted elements. Slotted mode remains unvirtualized in reality and gets honest docs.
- **Finding 2 (hidden + ResizeObserver):** in `items` mode, off-window items are unmounted, never `display:none`, so #823 cannot occur. In slotted mode the issue remains unless the interim `unobserve` workaround is applied.
- **Known gaps:**
  - The Chromatic timeout: re-point `LargeSuggestionsList` at the `items` prop with 1,000 entries. Capture a before/after build log.
  - Profiling: instrument and compare component-instance count (1,000 vs about 15).
  - Whether a real consumer has large lists: unknown. This approach is justified only if one exists or is expected.

## Recommendation

Do B1 with data source A, in two PRs:

1. **PR1:** extract `VirtualWindow`, move `bds-table` onto it. Move-only, with the existing spec as the safety net. Effort about 1.5 days.
2. **PR2:** add an `items` prop to `bds-search-bar` plus `VirtualWindow`, data-side filtering, keyboard scroll-then-focus, `aria-setsize`/`aria-posinset`, a live region, and an updated `LargeSuggestionsList` story. Deprecate slotted `VirtualScrollController` use. Effort about 4-5 days including specs, stories, a Safari manual pass and Chromatic. Total about 1 week.

Do the cheap fixes (doc wording, smaller story count) immediately regardless.

If no real large-list consumer exists, stop after the cheap fixes and keep PR1 as an optional refactor.

### Files touched

- New: `src/utils/dom/virtualWindow/virtual-window.ts`, its `types.ts`, and its spec.
- Edit: `bds-table.tsx`, `bds-table.virtual.spec.ts`.
- Edit: `bds-search-bar.tsx`, `types/` (new `SearchBarSuggestion` interface, with required members before optional), `__test__/` specs (basics, a11y, events), the stories and mdx.
- Edit: `bds-list-menu-item.tsx` (forward `aria-setsize`/`aria-posinset`), `bds-select.tsx` (hook for item source; label lookup).
- Edit: `virtual-scroll.ts` (`@deprecated`, optional `unobserve` fix).
- Possibly the `components.d.ts` and framework wrappers regenerate for the new prop.

### Breaking changes

- None if `items` is additive and slotted mode keeps working. The slotted API is deprecated, not removed.
- Removing `VirtualScrollController` is a major-version item.
- If both `items` and slotted children are present: define precedence (`items` wins, with a console warning).

### Risks

- Regressing `bds-table` virtualization (mitigated by move-only extraction and the existing spec).
- `bds-select` internals assume mounted items (label, focus, type-ahead). They are the highest-risk area and may need a hook.
- Safari: remounted items may animate (apply the `transition: none` rule to windowed list items).
- Scrolling with keyboard: focus after `scrollToIndex` needs a frame; timing flakiness.
- Dynamic heights: `bds-list-menu-item` height is fixed (28 px estimate today), so `measure: false` is acceptable and cheaper.
- Unit-test limits: `newSpecPage` (mock-doc) has no layout, so the window size is 0. Tests have to stub `getBoundingClientRect` or `initialRect`, as `bds-table.virtual.spec.ts` already does. Real scroll behaviour needs a browser pass.

### Test impact

- New `virtual-window.spec.ts` (create/update/unmount, microtask batching, count change).
- Update `bds-table.virtual.spec.ts` for the new field name or spies. Others unchanged.
- Search-bar specs: new `items`-mode tests (window size, filtering by data, `aria-*`, empty state, keyboard edge scrolling). Existing slotted tests stay for the deprecated path.
- A Storybook interaction or Chromatic check on `LargeSuggestionsList`.

## Open questions

1. Is there a real consumer with hundreds of suggestions or more? That decides whether any of this is worth doing past the doc fix.
2. Should `items` also live on `bds-select` (so the same windowing applies to the combobox list)? Search-bar-only is the minimal scope.
3. What does `bds-select`'s `managed` prop disable exactly, and can search-bar use it to bypass `searcherElement`?
4. Roving focus on items vs `aria-activedescendant` on the input. Pick one before PR2.
5. Group headers (`variant="label"`) in a windowed list: supported in v1, or flat items only?
6. Should `VirtualWindow` live in `utils/dom/` next to `VirtualScrollController`, or in a more general `utils/virtual/`?
7. The actual cause of the Storybook timeout is unconfirmed (see bug report Known Gaps). Verify before committing to the larger work.
