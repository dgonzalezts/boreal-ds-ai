# BUG-001: `bds-search-bar`/`bds-select` suggestion-list "virtualization" only repositions DOM nodes — it does not reduce mounted component count

**Severity:** Medium
**Priority:** P2
**Type:** Performance / Correctness
**Status:** Open
**Component:** `bds-search-bar` (`mode="list"`), `VirtualScrollController` (shared utility also usable by `bds-select`'s combobox list)
**Discovered during:** Team feedback meeting reviewing `bds-table` large-dataset handling (2026-07-06); traced back to the `LargeSuggestionsList` Storybook story
**Affects:** Any consumer of `bds-search-bar` (`mode="list"`) or other future consumers of `VirtualScrollController` that render a genuinely large item list (hundreds to thousands of items), plus the Storybook docs/Chromatic build pipeline for the `LargeSuggestionsList` story specifically

---

## Environment

- **Component:** `bds-search-bar` (`packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx`)
- **Underlying utility:** `VirtualScrollController` (`packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts`)
- **Story:** Forms → Search Bar → `LargeSuggestionsList` (`apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.stories.ts:404-442`)
- **Browser:** Chrome (latest stable)
- **URL:** `http://localhost:6006/?path=/story/forms-search-bar--large-suggestions-list`
- **Build:** Storybook docs/deploy pipeline (specific timing details not yet captured — see Known Gaps)

---

## Description

The `LargeSuggestionsList` story's doc comment claims: *"only the `bds-list-menu-item`s near the visible viewport are rendered/positioned — the rest stay in the DOM but hidden — so scrolling stays smooth even with a very large list."* That claim is accurate about what the code does, but it is not the guarantee a reader would reasonably infer from the word "virtualization" in this context. The mechanism only defers **positioning/paint** work for off-screen items; it does not defer or reduce the number of live, mounted custom-element instances. All 1,000 `bds-list-menu-item` elements in the story are created and go through their full Stencil lifecycle synchronously, before virtualization has any chance to act on them.

This was raised in a team feedback meeting as the suspected cause of two reported symptoms: the browser running slower than expected with this story open, and a Storybook deployment timing out on this specific story.

---

## Steps to Reproduce

1. Open Storybook → Forms → Search Bar → `LargeSuggestionsList` story (1,000-item `bds-list-menu` suggestion list)
2. Open browser DevTools → Elements panel, expand the `bds-list-menu` under `slot="list"`
3. Observe: all 1,000 `<bds-list-menu-item>` elements are present as real DOM nodes immediately on story load, before any scrolling or interaction
4. In the Performance/Console panel, note the initial script/render time attributable to component upgrade (constructor + `connectedCallback` + first `render()`) across all 1,000 elements
5. Scroll the suggestion list and confirm only a subset of items are visually positioned (`style.display !== 'none'`) at any time, while the rest remain in the DOM with `display: none`

---

## Expected Behavior

"Virtualization" (as the term is used in the story's own doc comment, and as understood in the broader ecosystem — `react-window`, `@tanstack/virtual`'s intended usage, MUI's windowing pattern) should mean only the currently-visible window of items (plus a small overscan buffer) exists as real, mounted DOM nodes at any given time. Scrolling should swap the *content* of a small, bounded set of elements, not toggle the visibility of a fixed set of 1,000 already-created elements.

---

## Actual Behavior

- `VirtualScrollController.attach()` (`virtual-scroll.ts:37-52`) is called from the consuming component's `componentDidLoad`, by which point the browser has already upgraded every `<bds-list-menu-item>` child present in the light DOM — custom elements upgrade synchronously the moment they're connected, and the story's Lit template inserts all 1,000 unconditionally.
- `collectItems()`/`allManagedItems()` (`virtual-scroll.ts:161-172`) query **already-existing** elements via `querySelectorAll(itemSelector)` — the controller has no mechanism to defer creation, only to reposition what's already there.
- `render()`/`positionItem()` (`virtual-scroll.ts:190-222`) set `display: none` + reset styles on out-of-window items, and `position: absolute` + `transform: translateY(...)` on in-window items. This is a real, working optimization for **scroll-time layout/paint cost**, but it does nothing for the **upfront instantiation cost** already paid before `attach()` ever runs.
- Net effect: the "virtualization" only pays off after the expensive part (creating 1,000 live Stencil component instances) has already happened.

---

## Root Cause

`VirtualScrollController` was designed to operate on children that already exist in the light DOM (it repositions pre-rendered nodes based on scroll offset) — it is positional/visual virtualization, not DOM-instantiation virtualization. This is an architectural limitation, not a simple bug in the positioning math: the controller's entire model assumes the DOM nodes it manages already exist and only need to be shown/hidden/repositioned. True windowed rendering would require the controller (or its consumer) to control *creation* of items from a data source — rendering only the visible window's worth of `bds-list-menu-item` elements and recycling/replacing their content as the window scrolls — which is a different architecture from "reposition existing children."

This was independently confirmed while scoping unrelated work on `bds-table`'s own row-virtualization feature (`EOA-14935`): the same finding led to a decision to *not* reuse `VirtualScrollController` for `bds-table`'s rows, and instead wire `@tanstack/virtual-core`'s `Virtualizer` directly against conditional JSX rendering, so that only the windowed rows exist as real `<tr>` nodes at all.

---

## Finding 2 — Latent correctness risk, not just performance

Follow-up research (2026-07-06, while scoping whether a shared virtualization utility could serve both `bds-search-bar` and `bds-table`) surfaced that `VirtualScrollController` combines `display: none` hiding of off-screen items with `@tanstack/virtual-core`'s rect/offset observation (`observeElementRect`/`observeElementOffset`, wired in `setupVirtualizer()`, `virtual-scroll.ts:130-147`). TanStack's own issue tracker documents this exact combination as a real bug source, independent of the DOM-count problem in Finding 1:

- [`TanStack/virtual#823`](https://github.com/TanStack/virtual/issues/823) — *"Redundant repaints, because of ResizeObserver. It send events when when list got hiden with css display property"* — the `ResizeObserver` fires with a size-0 entry for hidden items, which can reset measurements and cause layout shifts when an item is later re-shown.

This means the risk here is not purely "slower than it should be" — there is a plausible **correctness** issue (redundant repaints / layout shifts on items transitioning between hidden and visible) inherited directly from a documented upstream bug class, on top of the DOM-count issue in Finding 1. This does not require the larger rearchitecture discussed in Finding 1's Option 2 to investigate or mitigate — it's a narrower, independent question of whether `VirtualScrollController`'s current `display:none` + `ResizeObserver` combination actually triggers this specific upstream bug in practice, which has not yet been reproduced/profiled in this codebase (see Known Gaps).

---

## Suggested Fix Direction (Finding 1 — DOM count)

Two independent angles, not mutually exclusive:

1. **Fix the story's claim, not necessarily the mechanism** (lowest-effort): if 1,000 real mounted items is an acceptable cost for this specific use case (a doc-only demonstration story), narrow the doc comment's wording so it no longer implies DOM-count reduction — e.g. "only visible items are positioned; all items remain mounted" — and consider whether 1,000 items is even a representative/necessary story size, or whether a smaller count (e.g. 100) would demonstrate the scroll-smoothness benefit without the instantiation cost.
2. **Fix the mechanism** (higher-effort, needed if real consumers pass genuinely large lists): rework `VirtualScrollController` (or a new sibling utility) to drive conditional creation from a data array rather than repositioning pre-existing light-DOM children — i.e., let `@tanstack/virtual-core`'s `getVirtualItems()` determine which *data* entries are rendered as `bds-list-menu-item` elements at all, recycling a small pool of DOM nodes as the window scrolls, matching the approach independently chosen for `bds-table`'s row virtualization. This is a breaking change to the controller's current "manage existing children" contract and would need its own design pass — it also affects `bds-select`'s combobox list, the only other real (non-story) consumer of this pattern today.

Recommend option 1 immediately (cheap, removes a misleading claim) and treating option 2 as a separate, scoped follow-up ticket if any real consumer is expected to pass lists in the hundreds-to-thousands range — not clear that one currently exists in this codebase. **Update (2026-07-06):** this follow-up ticket has been explicitly deferred as a future spike, not started now — see "Related" below.

## Suggested Fix Direction (Finding 2 — correctness risk)

Reproduce first, fix only if confirmed: instrument `VirtualScrollController.positionItem()`/`resetItemStyles()` (or attach a temporary `ResizeObserver` logging wrapper) against the `LargeSuggestionsList` story to check whether hidden (`display:none`) items actually produce the redundant-repaint/size-0 `ResizeObserver` callbacks described in `TanStack/virtual#823`. If confirmed, the fix is likely narrow (e.g. explicitly unobserving elements before setting `display:none`, or wrapping the callback per the workaround pattern other TanStack Virtual users applied in `TanStack/virtual#531`) rather than a full rearchitecture.

---

## Known Gaps (need follow-up before this can be closed)

- The exact Storybook/Chromatic deploy timeout (which step, how long, what threshold) has not been captured directly — this report relies on the team's verbal account from a feedback meeting, not a reproduced CI failure log. Recommend attaching the actual failed build log/link before prioritizing a fix.
- No profiling data (Performance panel trace, Lighthouse, or `performance.now()` instrumentation) has been captured yet to quantify "slower than expected" — the reproduction steps above describe where to look, but exact timing numbers are not yet in this report.
- Not yet confirmed whether any real (non-Storybook) product consumer of `bds-search-bar`/`bds-select` currently passes a list in the hundreds-to-thousands range — if none does today, this may be lower priority than P2 suggests until a real use case appears.
- Finding 2 (correctness risk) has not been reproduced/profiled in this codebase — it is currently a plausible risk based on an upstream issue match, not a confirmed local defect.

---

## Related

- `bds-table` row-virtualization design decision (ticket `EOA-14935`, plan `ai-work/plans/EOA-14935-bds-table-v2.md`, Task 22) — independently identified the same limitation in `VirtualScrollController` and chose not to reuse it for that reason.
- Shared-virtualization-utility research (2026-07-06): investigated whether one reusable utility could serve both `bds-search-bar` and `bds-table` on top of `@tanstack/virtual-core`. Conclusion: technically possible only via a Vaadin-style windowed-creation model (Vaadin's `@vaadin/component-base/virtualizer.js` shares one class between `vaadin-virtual-list` and `vaadin-grid` via `createElements`/`updateElement` callbacks — built from scratch, no TanStack dependency, cited here as an architectural reference only, not a reusable dependency) — not by generalizing `VirtualScrollController`'s current positional/`MutationObserver` design. **Decision: deferred to a future spike, not scheduled.** Full citations in `/Users/dgonzalez/.claude/plans/let-s-continue-improving-the-calm-balloon.md`.
- Story source: `apps/boreal-docs/src/stories/forms/bds-search-bar/bds-search-bar.stories.ts:404-442`
- Utility source: `packages/boreal-web-components/src/utils/dom/virtualScroll/virtual-scroll.ts`
