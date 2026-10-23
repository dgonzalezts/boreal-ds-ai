---
ticket: —
component: bds-search-bar
status: exploring
---

# Virtual list — Approach C: component-owned, data-driven virtualization (no shared util)

## Goal

Make `bds-search-bar` (mode="list") / `bds-select` suggestion lists mount only the visible window of `bds-list-menu-item`s (Finding 1), without touching `bds-table`'s virtualizer and without a shared utility. Also decide what happens to the `display:none` + `ResizeObserver` risk (Finding 2, TanStack/virtual#823) and the Known Gaps. Research only; no source changed.

## Options evaluated

**C1 — `bds-list-menu` gets `options` + `virtual` props, owns a Virtualizer.**
Copy the bds-table wiring (`bds-table.tsx:1037-1054`, `1299-1308`: `new Virtualizer({observeElementRect, observeElementOffset, elementScroll, measureElement})`, `_didMount`/`_willUpdate`, `syncVirtualizerOptions` on count change, conditional JSX) into `bds-list-menu.render()`.

**C2 — Hybrid: `bds-search-bar` `suggestions` prop.**
`suggestions: {value, label, disabled?, group?}[]`; search-bar renders its own `bds-list-menu` + items inside the `bds-select` `slot="list"` and windows them itself. Keeps `bds-select` and `bds-list-menu` untouched.

**C3 — C1 + keep `VirtualScrollController` for slotted children.** Dual path.

## Findings

### How bds-select / bds-list-menu / bds-search-bar find items today (all DOM-based)
- `bds-list-menu`: `childItems` getter = `el.querySelectorAll('bds-list-menu-item')` (~line 247). Used by selection (`updateChildrenState`), `setSelectedValues`, `selectAll`, active/tab-stop sync, arrow-key nav, `getFocusTarget`, `empty` state (`childItems.length === 0`), `initialSelectedValues` (reads `[selected]`).
- `bds-select.tsx`: `searcherElement()` (L685) loops every item, reads text from `.bds-list-item__content-left__text`, sets `hidden`, calls `showParentLabel` (sibling walk), then counts `:not([hidden])` → `empty`. `resetChildren`, `updateLimitState` (L452, toggles `disabled` on every item), `updateSelectAllControl`, `syncTagField` (L488, value→label via DOM), `listenTagRemove` (label→value via DOM), `loadValue` (L755: `querySelector([value=…])` for label + `scrollIntoView`), type-ahead (L203) and Tab-select (L236, `:focus`).
- `bds-search-bar.searchOwnData()` (L206) duplicates the same loop with `textContent`; `virtualScroll.refresh()` after filtering.

### What breaks with only a window mounted
Every one of the above silently operates on ≤ ~20 items: filtering would only hide the windowed ones; value→label lookup returns `null` for off-window selected values (`loadValue` returns early → empty input text; multiselect tags show raw values); selectAll/maxTags counts wrong; type-ahead only matches window; `scrollIntoView` target doesn't exist; `selected` state restored on remount must come from `selectedValues`, not from item attrs. **Conclusion: filtering, label lookup, selection, limit state and keyboard nav must move to a data layer.** This is the real cost of C — not the Virtualizer wiring (~60 lines).

### Needed changes (C1)
- `bds-list-menu`: new `options` prop; internal `visibleOptions` (filtered, state) + `filter` text prop or `@Method() filter(query)`; `childItems` replaced by a data accessor in virtual mode; keyboard nav by *index* with `virtualizer.scrollToIndex()` then focus after render (rAF — see `keyboard-triggered-focus-move-double-activation.md`); `aria-setsize`/`aria-posinset` on each rendered item (required: DOM no longer implies count/position); `aria-activedescendant` or roving focus must survive unmount of the focused row (keep focused index mounted via `rangeExtractor`); groups (`variant="label"`) need flattening into the data list and the `showParentLabel` logic rewritten on data.
- `bds-select`: branch on `bdsList.options !== undefined`; ~8 methods (list above) get a data path. File is 795 lines; this is the largest, riskiest edit. Must also keep DOM path for slotted children → every method has two implementations (C3 is unavoidable for backwards compat).
- `bds-search-bar`: `searchOwnData` delegates to `list.filter(query)`; drop `virtualScroll.attach` in the data path; expose `suggestions`/forward `options`.
- Slotted + scrolling container: list-menu's scroll element (`.bds-list-menu__…` wrapper around `<slot>`) is the Virtualizer scroll element; needs fixed `max-height` + spacer element (`height: getTotalSize()`) and `transform: translateY` rows — same CSS as bds-table (incl. Safari fix `transition:none; will-change:auto`, see `safari-virtualized-row-transition-on-remount.md`).

### C2 (suggestions prop in search-bar) — cheaper
Search-bar already owns the filter loop and the debounce; it renders `<bds-select><bds-list-menu slot="list">…items…</bds-list-menu></bds-select>`. If it renders items from `suggestions` itself, then windowing is just conditional JSX over a *filtered array it owns*; filtering is `Array.filter` (no DOM). Selection/label for the search-bar case is trivial (search-bar's value is the text, not a multi-select). Remaining DOM-coupled pieces are bds-select's (`loadValue`, type-ahead, Tab) and list-menu's `childItems`, which still see only the window — acceptable for single-select search (selected label comes from `suggestions` lookup by search-bar and set on the input), but `bds-list-menu` arrow-key nav only moves within the window and must be taught to request scroll at window edges (`ArrowDown` on last mounted row → advance virtualizer, focus next). Also `bds-list-menu.empty` is already search-bar-settable. Does **not** fix bds-select consumers with large lists (they remain on slotted path) — the bug report names bds-select as only other consumer; no evidence of one with >hundreds items (Known Gap 3).

### Duplication cost vs shared helper
Vs. bds-table: virtualizer setup (init/teardown/options sync/measure) would be copied a 2nd time (~60 lines + CSS) and drift independently (the exact bug class in `safari-virtualized-row-transition-on-remount`). A tiny shared `createWindowVirtualizer(el, getCount, estimate)` factory would remove duplication without changing bds-table's behavior — but this approach C premise says "no shared util"; flag as an alternative, not a requirement. Bigger duplication is the dual DOM/data path in bds-select (not avoidable under C1).

### Finding 1 coverage
C1 and C2 both fix it: only window + overscan items instantiated (story with 1,000 → ~12 elements). C2 fixes it for search-bar only.

### Finding 2 coverage
Fixed structurally in the data path: windowed rows are unmounted, never `display:none`, so no size-0 `ResizeObserver` entries (#823). Retained only on the legacy slotted path (VirtualScrollController) — the narrow repro/mitigation (unobserve before hide, per #531 workaround) is still needed there if it stays supported. Not reproduced locally yet.

### Known Gaps coverage
1. CI timeout log — unaffected; C reduces instantiation work so the story should drop sharply, but must be measured (before/after `performance.now()` around story mount; attach failed build log).
2. No profiling — add a perf spec/story with 1,000 and 10,000 options; record element count (`querySelectorAll('bds-list-menu-item').length`) as the primary metric, deterministic unlike timing.
3. Real >hundreds consumer — unknown; this decides whether C1 (full) or C2 (search-bar only) is justified. Ask product/consumers before committing.
4. Finding 2 unreproduced — see above; the legacy path still needs the reproduction step if kept.

## Recommendation

Do **not** do full C1 now. The Virtualizer wiring is cheap; migrating bds-select's DOM-coupled logic to data (8+ methods, two parallel paths, aria-setsize/posinset, groups, multiselect limit/select-all) is the expensive and risky part, and only pays off if a real large-list consumer exists.

Do **C2** first if large lists are required: `bds-search-bar` `suggestions` prop, search-bar-owned filtering and windowing, `bds-list-menu` gaining only a small, generic capability (`aria-setsize/posinset` pass-through + "navigate past window edge" hook / `virtual` flag disabling its DOM-count-based `empty`). Keep `VirtualScrollController` + slotted path unchanged and documented as "positional only" (also apply the story-wording fix from bug report option 1 immediately). Revisit C1 (and extracting a shared virtualizer factory) only when a bds-select consumer with large lists appears.

### Proposed public API
```ts
interface ISearchSuggestion { value: string; label: string; disabled?: boolean; group?: string }
// bds-search-bar
@Prop() suggestions?: ISearchSuggestion[];           // data mode; mutually exclusive with slotted list
@Prop() virtualThreshold = 100;                      // window only when filtered count exceeds
// (C1 only) bds-list-menu
@Prop() options?: IListMenuOption[]; @Prop() virtual = false;
@Method() filter(query: string): Promise<number>;
```

### Files touched
- C2: `bds-search-bar.tsx`, its `types/` (`ISearchSuggestion`), `.scss` (spacer/rows), stories + MDX, `bds-list-menu.tsx` (small), specs.
- C1 adds: `bds-list-menu.tsx`/`.scss`/types, `bds-select.tsx` (large), `bds-select` stories/docs, `components.d.ts`, Vue/React wrappers regenerate on build.

### Effort / risk / breaking
- C2: ~3–5 days. Risks: window-edge keyboard nav, focus loss when focused row unmounts, Safari remount transition, a11y posinset.
- C1: ~2–3 weeks. Risks: regression in bds-select (largest component spec surface), dual-path drift, group labels, multiselect, FACE value/label sync.
- Breaking: none if opt-in props and slotted path retained; slotted+`options` both set must define precedence (options wins, warn).

### Test impact
- C2: new spec in `bds-search-bar` (suggestions render count ≤ window, filter, empty, aria-setsize/posinset); list-menu spec for pass-through. mock-doc has no layout: `getBoundingClientRect` returns zeros, so mock the scroll element rect/`offsetHeight` to get a non-empty window (check how bds-table specs do this). Browser/Chromatic story for real scrolling and element count.
- C1: ~all `bds-select` (basics/keyboard/events/slots) and `bds-list-menu` specs need a data-mode twin; mutation score bar (100%) means large new test surface.

### a11y
`role=listbox`/`option` rows need `aria-setsize` + `aria-posinset` (1-based, over filtered set); keep focused/active row in `rangeExtractor` so focus never lands on a removed node; announce result count via live region on filter; `scrollToIndex` before focusing.

## Open questions
1. Is there any real consumer (not the story) with hundreds–thousands of options? Decides C1 vs C2.
2. Is `suggestions` allowed to replace the slotted `<bds-list-menu>` in `mode="list"`, or must consumers keep custom item content (icons, avatars, flags)? Needs a render-slot/renderer API if so.
3. Variable-height items (descriptions, groups)? Fixed 28px estimate today; `measureElement` is needed otherwise.
4. Do we want a small shared virtualizer factory after all (removes duplicated init/teardown vs. bds-table)?
5. Keep `VirtualScrollController` long term, or deprecate once the data path exists?
6. Does the `LargeSuggestionsList` story keep 1,000 slotted items (legacy) or move to `suggestions`?
