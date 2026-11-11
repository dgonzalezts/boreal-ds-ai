---
name: bds-search-bar-items-mode-test-harness
description: How to drive bds-search-bar's items mode (windowed suggestions) inside newSpecPage — template-based items, scroll geometry stubs, and the capture-phase gap
metadata:
  type: project
---

`bds-search-bar`'s `items` mode windows its suggestions through `VirtualWindow` (TanStack). Three
non-obvious requirements when testing it with `newSpecPage` (verified EOA-19597 Task 15):

**1. `items` must be present on the first render — use `template`, not a post-mount assignment.**

```ts
const page = await newSpecPage({
  components: SEARCH_BAR_COMPONENTS,
  template: () => h('bds-search-bar', { items }),
});
```

`componentWillRender` creates the `VirtualWindow`, but `mountVirtualWindow()` (in
`componentDidRender`) bails while `.bds-list-menu__content` does not exist — which is exactly the
render that first introduces the internal list. Assigning `items` after mount therefore leaves the
list empty until an unrelated second render (typing, a new `items` array). `template` + `h` from
`@stencil/core` works in a plain `.ts` spec file and type-checks against `IntrinsicElements`;
`page.root` is still the `bds-search-bar`. Replacing `items` on an already-mounted items-mode bar
is fine — the list already exists, so that render mounts/updates normally.

**Superseded 2026-10-26 (plan T30):** `mountVirtualWindow()` now retries on a bounded
`requestAnimationFrame` loop (`ITEMS_MODE_MOUNT_MAX_FRAMES = 120`), so a post-mount `items`
assignment does mount by itself. `template` is still the simplest fixture, but the async-data path
is now testable: mount with no `items`, assign, then `settleFrames(page)` and the window appears
(mock-doc reproduces the original bug exactly — pre-fix it stays at 0 items and `['0px','0px']`
spacers). See [[bds-search-bar-t30-t31-regression-mechanics]].

**2. The list's scroll element needs `scrollHeight`/`clientHeight`/`scrollTop`/`scrollTo`.**

`VirtualWindow.scrollToIndex()` throws `TypeError: Cannot read properties of undefined (reading
'documentElement')` inside TanStack's `getMaxScrollOffset` because mock-doc elements have no
`scrollHeight`, so the library takes its `Window` branch (`scrollElement.document.documentElement`).
Patch the content element (`.bds-search-bar__list .bds-list-menu__content`) once per page:

```ts
Object.defineProperty(content, 'scrollHeight', { configurable: true, get: () => total * 28 });
Object.defineProperty(content, 'clientHeight', { configurable: true, value: 200 });
Object.defineProperty(content, 'scrollTop', { configurable: true, writable: true, value: 0 });
Object.defineProperty(content, 'scrollTo', {
  configurable: true,
  value: (options: ScrollToOptions) => {
    content.scrollTop = options.top ?? 0;
    content.dispatchEvent(new Event('scroll'));
  },
});
```

Window size still comes from the prototype-wide `setupElementLayoutMock({ viewportHeight: 200,
viewportWidth: 400, itemHeight: 28 })` patch (see [[stencil-tanstack-virtual-core-mock-doc-pattern]]); 200 px / 28 px gives
8 visible + 5 overscan = 13 mounted items at the top of a 1,000-entry list. Any code path that calls
`resetItemsScroll()` (a query change, clear, `items` replacement) needs the geometry in place or it
throws inside the debounce callback, silently leaving `typedText` set.

**3. Keyboard: rAF-driven jumps need a settle loop, and capture-phase interception is untestable.**

`rAF` is `setTimeout(cb, 0)` under `setupAnimationFrameMocks()`, so a scroll-and-focus jump settles
over several real frames — loop `await new Promise(r => setTimeout(r, 4)); await flushMicrotasks();
await page.waitForChanges();` ~8–16 times. Focus is not tracked by mock-doc, so install a tracker
(patch `HTMLElement.prototype.focus` + `Object.defineProperty(document, 'activeElement', …)`), which
also makes the controller's own `document.activeElement` guards behave. Because mock-doc has no
real capture phase ([[stencil-mock-doc-no-capture-phase-ordering]]), `bds-select`'s own bubble
keydown listener runs *before* the search bar's host capture handler, so a closed popover sees two
`openPopover()` calls — assert `toHaveBeenCalled()`, not an exact count, and don't expect the
select's handler to be suppressed.

**4. Asserting a *preserved* window position needs a query that matches the whole list.**

`buildSuggestions(n)` labels are `Item 0…n`, so a narrow query (`'Item 1'` → 11 of 30) leaves fewer
matches than the 13-item window: the window is never shifted and every `aria-posinset` is `1..11`
no matter the `scrollTop`, which makes a "position unchanged" assertion vacuous. To get a genuinely
scrolled window, use `buildSuggestions(60)` + `typeQuery(page, field, 'Item')` (all 60 match) and
`scrollListTo(page, content, 20 * ITEM_HEIGHT)` → `windowItems(root)[0]` reads `aria-posinset`
`"16"` (offset 20 − 5 overscan + 1). With no query, `scrollListTo(..., 10 * ITEM_HEIGHT)` on 30
entries gives `"6"`. `resetItemsScroll()` is private — `jest.spyOn(page.rootInstance as unknown as
{ resetItemsScroll: () => void }, 'resetItemsScroll')` works (own property shadows the prototype
method) and is the only way to observe a reset when `scrollTop` is already 0 (first assignment,
`items = []` → populated); restore it in a `finally`.

Shared fixture helpers live in
`src/components/forms/bds-search-bar/__test__/search-bar-items.test-utils.ts`
(`renderItemsPage`, `buildSuggestions`, `typeQuery`, `scrollListTo`, `settleFrames`,
`installFocusTracker`, `windowItems`, `spacers`, `stubPopover`). Stub the popover's
`getVisibility`/`openPopover` on every page that types: a real `openPopover()` reaches
`@floating-ui`'s `IntersectionObserver`, which is undefined in mock-doc and crashes the worker via an
unhandled rejection from `reopenSuggestions`.
