---
name: a11y-grid-navigation-non-cell-focus-guard
description: setupGridNavigation no-ops arrow/Home/End when a non-cell element inside the root has focus; how the guard is implemented and how navigation.spec.ts simulates focus
metadata:
  type: project
---

`setupGridNavigation` (`src/utils/a11y/keyboard/navigation/grid-navigation.ts`) registers its key handlers on the grid **root**, which also contains non-cell controls (e.g. `bds-calendar-grid`'s header month-nav `bds-button`s). Both `move()` and `moveToEdge()` previously fell back to `positions[0]` whenever `resolveGridCurrentPos` returned `{-1,-1}`, so Arrow/Home/End pressed while a header button had focus stole focus into the grid (EOA-17662 Task 40b).

Guard added (EOA-17662 T40b): `isNonCellFocusWithinRoot(items, root)` in `src/utils/a11y/keyboard/focus/resolve.ts`, called early in both `move()` and `moveToEdge()` (after the `positions.length === 0` early-out). It returns `true` only when `document.activeElement` is an `HTMLElement`, is inside `root`, is not `root` itself, and is not within any cell. Returns `false` for the root-focused (`aria-activedescendant`) and nothing-focused cases, preserving the first-cell fallback.

- Cell match is `cell === focused || cell?.contains(focused)` — mirrors `resolveCurrentIndex`'s containment semantics rather than `resolveGridCurrentPos`'s strict `===`, so focus on a descendant inside a cell is not misclassified as non-cell focus.
- `root.contains(focused)` is correct for shadow-host focus: a focused `bds-button`'s `document.activeElement` is the host, which is a light-DOM child of the root. mock-doc's `Node.contains` resolves nested elements correctly (only `contains(self)` was previously documented).
- PageUp/PageDown are registered directly (`onPageUp`/`onPageDown`), not via `move`/`moveToEdge`, so they are unaffected.

**Test harness** (`src/utils/a11y/keyboard/__test__/navigation.spec.ts`): `beforeAll` monkey-patches `HTMLElement.prototype.focus` to set a module-level `activeElement`; `beforeEach` redefines `document.activeElement`'s getter to return it. To simulate focus in a test just call `el.focus()` (no real focus in mock-doc). Cells are `createButton(root, 'A')`-style buttons; a non-cell is any other element appended to the same root. Confirmed the new no-op tests fail without the guard (removing the two guard lines re-introduces the focus jump).
