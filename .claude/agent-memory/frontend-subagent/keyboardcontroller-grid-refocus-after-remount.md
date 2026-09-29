---
name: keyboardcontroller-grid-refocus-after-remount
description: KeyboardController.setGridNavigation has no built-in way to keep a tabbable/focused cell alive across a full grid remount (e.g. month navigation) - pattern for wiring it manually, found in bds-calendar-grid Task 40 (EOA-17662).
metadata:
  type: project
---

`KeyboardController.setGridNavigation({ items, onPageUp, onPageDown, ... })` (in
`src/utils/a11y/keyboard/KeyboardController.ts`) registers arrow/Home/End/PageUp/PageDown
bindings and does its own DOM-attribute-based roving tabindex (via
`resolveGridCurrentPos`, which reads `document.activeElement` — there is NO internally
cached row/col index). This means:

1. `initialActiveSelector` is evaluated exactly once, synchronously, inside the
   `setGridNavigation()` call (normally from `componentDidLoad()`). It is never
   re-evaluated later, so it only controls which cell is tabbable on first mount.
2. If a consumer's `items` producer function derives elements from a `@Prop()` that gets
   fully replaced (e.g. a new `MonthGrid` object on month navigation, where every `<td>` is
   keyed by `isoDate` and therefore fully remounted), **every** cell in the new DOM re-renders
   with whatever default `tabIndex` JSX gave it (typically `-1`). Nothing in
   `grid-navigation.ts`/`KeyboardController` re-establishes a `tabindex="0"` cell after that —
   the whole grid becomes permanently unreachable via Tab from then on, silently, with no
   error and no failing default-path unit test.
3. There is no public grid-shaped "re-focus without stealing DOM focus" method.
   `KeyboardController.rovingTabindex(items, activeIndex)` is the only public roving-tabindex
   entry point and it is FLAT-list-only (`HTMLElement[]`), and it unconditionally calls
   `.focus()` — there is no public equivalent of the internal `initGridRovingTabindex`
   (tabindex-only, no focus steal).

**Fix pattern (used in `bds-calendar-grid.tsx`, Task 40 / EOA-17662):**

- `@Watch('grid')` (or whatever prop drives the remount) captures, from the *old* value
  (Stencil gives you `(newValue, oldValue)` for free — no need to snapshot `this.grid`
  yourself, since the instance field is already reassigned by the time the watcher runs),
  whether the currently focused element was one of the component's own cells, and if so what
  its "identity" was (e.g. day-of-month number, for APG's "PageUp/PageDown lands on the same
  day number" behavior).
- `componentDidUpdate()` (fires after every subsequent render, not the first) resolves the
  new target cell in the new grid and either:
  - **moves real focus** — when the prior interaction was keyboard-driven from within the
    grid — by flattening `items` (2D → `HTMLElement[]`) and calling the PUBLIC
    `KeyboardController.rovingTabindex(flatItems, index)`. This reuses existing traversal
    utility code rather than re-implementing roving tabindex.
  - **only marks a tabbable cell, without stealing focus** — when the prior interaction was
    NOT keyboard-driven from within the grid (e.g. a mouse click on a header
    prev/next button) — via a tiny 3-line local helper that just does
    `cellEl.setAttribute('tabindex', '0')` on the target (safe without a full reset loop,
    since every cell in a freshly-remounted grid already defaults to `tabindex="-1"` from JSX).
    This is NOT "hand-rolling navigation logic" (no arrow-key/wrap math) — it's just the
    "which cell is the single Tab stop" bookkeeping the public API doesn't expose a
    no-focus-steal version of.

Without the second (no-steal) branch, ANY mouse-driven or otherwise non-keyboard-triggered
grid update permanently kills Tab-reachability into the whole grid for the rest of that
component instance's life (`componentDidLoad()` only runs once). This is easy to miss because
it produces zero console errors/warnings and the grid still *looks* fine — it only manifests
as "Tab silently skips the whole calendar" on manual keyboard QA.

See also [[claude-in-chrome-testing-gotchas-for-keyboard-nav]] for how this was actually
verified live (macOS click-focus quirk + real vs. synthetic wait timing).
