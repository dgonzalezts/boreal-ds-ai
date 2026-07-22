---
name: stencil-tanstack-virtual-core-mock-doc-pattern
description: How to make @tanstack/virtual-core's Virtualizer produce a real windowed subset inside newSpecPage's mock-doc environment
metadata:
  type: project
---

`@stencil/core/mock-doc` never implements layout metrics: `offsetHeight`/`offsetWidth` are entirely
absent from `MockHTMLElement` (read as `undefined`), and `getBoundingClientRect()` is hardcoded to
return an all-zero rect. Without intervention, any `@tanstack/virtual-core` `Virtualizer` mounted
inside `newSpecPage` collapses to a zero-height viewport and produces no meaningful window.

**The fix — patch two things at the `HTMLElement.prototype` level, before any `newSpecPage()` call
in the file (top-level `beforeAll`):**

```ts
let originalGetBoundingClientRect: typeof HTMLElement.prototype.getBoundingClientRect;

beforeAll(() => {
  originalGetBoundingClientRect = HTMLElement.prototype.getBoundingClientRect;
  (HTMLElement.prototype as unknown as Record<string, unknown>).offsetHeight = VIEWPORT_HEIGHT;
  (HTMLElement.prototype as unknown as Record<string, unknown>).offsetWidth = VIEWPORT_WIDTH;
  HTMLElement.prototype.getBoundingClientRect = (): DOMRect =>
    ({ bottom: 0, height: ROW_HEIGHT, left: 0, right: 0, top: 0, width: VIEWPORT_WIDTH, x: 0, y: 0 }) as DOMRect;
});

afterAll(() => {
  HTMLElement.prototype.getBoundingClientRect = originalGetBoundingClientRect;
  delete (HTMLElement.prototype as unknown as Record<string, unknown>).offsetHeight;
  delete (HTMLElement.prototype as unknown as Record<string, unknown>).offsetWidth;
});
```

This works because `global.HTMLElement` inside a Stencil spec file IS mock-doc's `MockHTMLElement`
(same pattern already relied on by `src/utils/testing/mocks/popover-mock.ts`, which assigns
`HTMLElement.prototype.showPopover` directly) — a prototype patch in one spec file is invisible to
other spec files since Jest gives each test file its own module registry.

**Why this specific pair is sufficient, and why nothing else (ResizeObserver mocks, scroll
simulation) is needed:**

- The scroll-container viewport size comes from `@tanstack/virtual-core`'s `observeElementRect`,
  which does `handler(getRect(element))` — a synchronous read of `offsetWidth`/`offsetHeight` —
  *before* it ever touches `ResizeObserver`. That one synchronous call is what seeds
  `virtualizer.scrollRect`, and it's all these tests need since none of them scroll or resize.
- Per-row measured height comes through whatever `measureElement` callback the *consuming
  component* wired (e.g. `bds-table`'s `measureElement: el => el.getBoundingClientRect().height`),
  called directly and synchronously from the `ref` on each rendered row — patching
  `getBoundingClientRect()` covers this path directly, no library internals involved.
- **`page.win.ResizeObserver` (i.e. `scrollElement.ownerDocument.defaultView.ResizeObserver`,
  what `@tanstack/virtual-core` actually calls `new` on) is mock-doc's own `MockResizeObserver` —
  a permanent no-op whose constructor ignores its callback and whose `observe()` does nothing.**
  This is a *different object* from `global.ResizeObserver`, which is what
  `setupResizeObserverMock()` (`src/utils/testing/mocks/observers.ts`) patches — that helper does
  **not** affect `@tanstack/virtual-core`'s internal ResizeObserver usage at all. Don't reach for
  it when testing virtualization; it solves a different problem (components that call the ambient
  global `ResizeObserver` directly, not `this.win.ResizeObserver`).

**Consequence:** the virtualizer's `scrollRect` is seeded once, synchronously, at construction time
and never updates again (no real resize/scroll events fire in this environment). That's fine for
window-size and row-count assertions; it is NOT sufficient for testing anything that depends on a
live resize or scroll offset change — there is no known pattern for that in this codebase yet.

Verified building `bds-table.virtual.spec.ts` for `bds-table`'s `virtual` prop (EOA-15507 Task 7,
2026-07-22) — 200-row dataset windowed down to well under 100 real `<tr>`s with a 480px mocked
viewport and 48px mocked row height, matching `bds-table`'s own `estimateSize: () => 48`.

No existing spec file in this codebase tested `@tanstack/virtual-core` before this (grepped:
`src/utils/dom/virtualScroll/virtual-scroll.ts`'s `VirtualScrollController`, used by
`bds-search-bar`, has zero spec coverage of its own). This is the first such pattern — worth
promoting to `.agents/memory/` if another component (e.g. a future `VirtualScrollController` spec)
needs the same mock.
