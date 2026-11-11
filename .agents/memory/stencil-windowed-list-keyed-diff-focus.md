---
name: stencil-windowed-list-keyed-diff-focus
description: "When a window shifts, Stencil's keyed diff moves retained nodes with insertBefore inside the list's relocated slot children, which can scramble their order and always blurs the focused element — fix with one stable display:contents wrapper plus value-tracked re-focusing."
---

# Stencil's keyed diff moves retained window items with `insertBefore` — order and focus both depend on it

**Mechanism.** When a window shifts, the overlapping items are retained (same key, same DOM node) and Stencil's keyed diff repositions them to their new index with `insertBefore`. Two consequences, both observed in `bds-search-bar` items mode (EOA-19597):

1. **DOM order.** In a non-shadow component the list's children are relocated by the slot polyfill, so windowed items rendered as direct children of the slotted `bds-list-menu` are moved among siblings whose order the polyfill also manages. After a shift, the retained items could end up out of sequence relative to the spacers (T9).
2. **Focus.** Moving an already-connected, focused element with `insertBefore` fires a real `blur` and drops `document.activeElement` to `<body>`, even when it is the identical node object (T11). This is standard browser behaviour, not a Stencil defect: a vdom `key` guarantees node identity, never focus continuity.

**Fix 1 — diff one stable subtree.** Wrap the windowed items in a single keyed wrapper (`key="bds-search-bar-window"`, class `.bds-search-bar__window`, `display: contents`) between the two spacer siblings. Only that subtree changes between renders, so the spacers and the list's relocated children never move, and `display: contents` keeps the items as direct layout children of the list with no extra box.

**Fix 2 — track focus by value, not by node or index.** Keep the focused item's value in a field; after render, find the mounted item with that value and call `focus({ preventScroll: true })`. Details that matter:

- `preventScroll: true` — otherwise the focus call scrolls the list back and undoes the window move that caused the render.
- While a scroll-and-focus jump is in flight, park focus on the list host (`bds-list-menu`, already `tabIndex="-1"`) so the interim blur-to-`body` is recoverable and keystrokes keep reaching the list.
- If the tracked value is not mounted after the settle loop, clear the tracker and return focus to the input rather than leaving it on `body`.

Reference implementation: `bds-search-bar/helpers/ItemsNavigationController.ts` (`focusedValue`, `focusItemAtIndex()`, `recoverFocus()`), with the wrapper and Safari rule in `bds-search-bar.scss` (`&__window { display: contents }`, `&--items .bds-search-bar__window > bds-list-menu-item { transition: none; will-change: auto }`).

**Testing limit.** mock-doc has no `document.activeElement`, so real focus loss on unmount or reorder is not observable under `newSpecPage`. Assert the tracked value and the attempted `focus()` calls in specs, and confirm actual focus behaviour in a browser (`stencil-mock-doc-no-activeelement-focus-tracking.md`).

**Not the same as the remount-transition bug.** `safari-virtualized-row-transition-on-remount.md` covers Safari animating a *newly mounted* row; this entry covers *retained* nodes being moved by the diff. A windowed list normally needs both rules.

**Source:** EOA-19597 T9 (order) and T11 (focus), verified in Chrome and WebKit.
