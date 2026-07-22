---
name: stencil-imperative-hide-slotted-component
description: Pattern for hiding a real slotted custom element (not a wrapper div) while preserving its internal state, e.g. bds-table hiding a slotted bds-pagination during loading
metadata:
  type: project
---

When a host component (`bds-table`) needs to hide a *real, separately-mounted* slotted child custom element (e.g. `<bds-pagination slot="paginator">`) during a transient state (`loading`) — without unmounting it, so its internal `@State`/`@Prop` (e.g. `currentPage`) survives — there is no wrapper `<div>` around a bare `<slot>` to toggle a CSS class on (contrast with `[slot="toolbar-actions"]`, which bds-table already wraps in its own `<div class="...--hidden">`, an easy CSS-class toggle target).

**Pattern used (bds-table paginator skeleton, Task 5b, EOA-15507):**
1. Query the slotted element directly: `this.el.querySelector('bds-pagination[slot="paginator"]')`. This is reliable even from `componentWillLoad` in this codebase's non-shadow components — confirmed by the pre-existing `setupRowsPagination()` doing the same query in `componentWillLoad`, and by adding a second call safely in `componentDidRender` (runs after every re-render, same place existing pinned-column offset math already lives).
2. Toggle `paginatorEl.style.display = this.loading ? 'none' : ''` imperatively in `componentDidRender` — not via `@Watch('loading')` alone, because `@Watch` never fires for the initial prop value (see [[feedback_no_jsdoc_default]]-adjacent prop-validation gotcha), and `componentDidRender` already runs on both the initial paint and every subsequent re-render, covering both cases with one code path.
3. Render a `bds-table`-owned skeleton JSX element declaratively in `render()`, gated on a `hasXSlotted` getter (`this.el.querySelector('bds-pagination[slot="paginator"]') !== null`) AND `this.loading` — placed immediately after the real `<slot>` tag so it visually occupies the same position once the real element is `display:none`.
4. `display: none` natively removes the element from both the accessibility tree and tab order — no extra `aria-hidden`/`tabindex` bookkeeping needed, unlike collapsed-trigger-focusable cases (see [[feedback_scroll_into_view_collapsed_focusable]]) where internal focusables needed individual tabindex management.

**Why this differs from the toolbar-actions-slot approach:** that slot's hidden state is a CSS class on a `bds-table`-owned wrapper `<div>` around the `<slot>`. The paginator has no such wrapper (a bare `<slot name="paginator" />`), so the hide target must be the real light-DOM element itself, found by direct query and toggled with an inline style — a JS/imperative technique, not a CSS-class one.
