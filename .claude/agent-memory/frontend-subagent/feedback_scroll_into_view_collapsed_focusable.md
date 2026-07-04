---
name: feedback-scroll-into-view-collapsed-focusable
description: Collapsible-trigger components must manage tabindex on every internal focusable descendant, not just the visible trigger — otherwise reverse Tab navigation can silently focus a hidden control and corrupt scroll position.
metadata:
  type: feedback
---

Any component that collapses to a small "icon-only" state and expands on focus (e.g. `bds-search-bar`'s `minimized` trigger) must manage `tabindex` on **every** internal focusable descendant while collapsed — not just the one visible trigger element. If a descendant (like the wrapped `<input>` inside `bds-text-field`) keeps its default focusability, Shift+Tab (reverse navigation) can land directly on it while the component still believes it is collapsed, bypassing whatever forward-focus handler normally triggers the expand.

**Why:** Found in `bds-search-bar` (EOA-15204). The leading icon trigger's `tabIndex` was conditionally managed (`triggerTabIndex` getter → -1 when open), but the `<input>` behind it was not. Forward Tab correctly landed on the trigger button first (expanding the bar via `handleTriggerFocus`). But Shift+Tab from a sibling control skipped the trigger and focused the `<input>` directly — the component stayed collapsed (`isOpen` never flipped), yet the browser's native "scroll focused element into view" behavior fired on the `overflow: hidden` flex container (`.bds-text-field__container`) that wraps both the icon and the input. Because that container's flex content (icon + gap + 0-width input) is *always* wider than its collapsed visible box by design, the browser scrolled it to its max `scrollLeft`, permanently clipping the leading icon out of view (rendered as a stray diagonal sliver, not a full glyph) until manually reset.

**How to apply:** For any collapse/expand trigger pattern:
1. Don't rely solely on a dedicated `focus` handler on the *visible* trigger element — also hook the composite `bdsFocus`/`onBdsFocus` event bubbling from the underlying form control (`bds-text-field`, etc.) so that focus landing on the internal control *by any path* (Shift+Tab, click, programmatic `.focus()`) re-triggers the same expand logic as focusing the trigger.
2. Treat a persistently-nonzero `scrollLeft`/`scrollTop` on an `overflow: hidden` flex container as a plausible root cause whenever a *sibling* flex item (not the one that grew/shrank) visually clips after a width/height transition — check `container.scrollLeft` directly via `getBoundingClientRect()` deltas, not just computed style, since this is invisible in DevTools' Elements panel without explicitly reading the property.
3. A CSS-only fix (`overflow-anchor: none`, clamping, etc.) will not solve this class of bug — the corruption is caused by native focus-navigation scroll-to-reveal, not CSS scroll anchoring. The fix belongs in the focus-handling JS, not the stylesheet.

See also [[stencil-search-bar-scroll-clip-bug]] for the specific fix applied.
