---
name: feedback_guard_expensive_read_not_cheap_write
description: when guarding a componentDidRender DOM-sync pass for performance, split it into a guarded expensive-read phase and an unconditional cheap-write phase — never guard the whole thing by reference-equality on @State() alone if virtualization/keyed-vdom can swap in fresh unstyled elements between guarded runs
metadata:
  type: feedback
---

When adding a change-detection guard to a `componentDidRender()` DOM-sync routine (e.g. "only recompute X when `@State()` field Y changed"), reference-equality guarding is correct for the *computation* but can silently break correctness for the *application* of that computation if any part of the DOM being written to can be recreated by something other than the guarded state (e.g. TanStack Virtual swapping in fresh `<tr>`/`<td>` elements for newly-scrolled-into-view rows via keyed vdom, independent of the guarded `pinnedColKeys`/`columns` state).

**Why:** found during `bds-table.tsx` Task 8 (EOA-15507) — guarding the entire pinned-column-offset computation (including the `td.style.left = ...` writes) by `pinnedColKeys !== lastPinnedColKeys` broke pinned-column alignment during virtualized scrolling: scrolling creates new `<td>` elements with different vdom keys every render, but since `pinnedColKeys`/`columns` hadn't changed, the guard skipped writing `left` onto those new elements entirely, leaving them unstyled. This was NOT caught by the existing unit test suite (which doesn't exercise scroll-driven virtualized re-renders against pinned columns) — only caught via manual Playwright verification against a live `#virtual-table` example with pinned columns.

**How to apply:** split into two phases:
1. Guarded, cached **read** phase — the layout-forcing `offsetWidth` reads and the per-column offset *computation*. Only reruns on real state change (or an explicit force flag, e.g. from a `ResizeObserver`). Cache the result (e.g. a `Map<colKey, offset>`).
2. Unconditional, cheap **write** phase — re-applies the cached values to every currently-matching element on every call. Plain `style.property = value` writes don't force synchronous layout the way reads like `offsetWidth`/`getBoundingClientRect()` do, so this stays cheap even running every render, and it's what actually needs to run every time to catch freshly-created elements.

Never assume "the guarded state didn't change" implies "the relevant DOM elements are the same objects as last time" when virtualization or any keyed vdom reconciliation is in play anywhere near the code being guarded.
