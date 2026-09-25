# mock-doc node-identity assertion printing + rovingTabindex focus semantics (EOA-17662 T40d)

Two findings from the `bds-calendar-grid` FM-85/FM-86 fix.

## 1. `expect(nodeA).toBe(nodeB)` fails with "Unimplemented" under `newSpecPage`

When a `newSpecPage` spec asserts DOM-node identity via `expect(tabbable[0]).toBe(findDayCell(...))`
and the assertion **fails**, Jest's pretty-format tries to serialize the mock-doc elements and throws
`Unimplemented` instead of printing a `Expected/Received` diff. The test still fails (so it is
non-vacuous), but the failure message is useless for diagnosis.

Fix for readable failures: assert on a scalar DOM property instead of the node itself, e.g.
`expect(tabbableCells(el).map(c => c.textContent?.trim())).toEqual(['15'])`, or a boolean
`expect(a === b).toBe(true)`. Existing codebase tests that use `expect(document.activeElement).toBe(...)`
pass, so the problem only surfaces on failure — but prefer the scalar form in new tests.

## 2. `KeyboardController.rovingTabindex` moves real focus

- `rovingTabindex(items, i)` → `applyRovingTabindex` → **calls `.focus()`** (focus + set tabindex 0 + demote prev).
- `initGridRovingTabindex(items, row, col)` / `initRovingTabindex` → **set tabindex only, no focus** (demote-all + set target).

So any "restore the single roving-tabindex stop during a prop-only update" path (must not steal focus)
must NOT route through `rovingTabindex`. Use `initGridRovingTabindex`, or demote every cell manually
then set the target. `bds-calendar-grid.markTabbableCell` (called from `componentDidUpdate`'s
`targetDay == null` branch) does the manual demote-all over `_cellRefs.values()` + set target.

Related: Stencil serializes a boolean `true` on an `aria-*` attribute as `""`, not `"true"` — so a
selector like `[aria-selected="true"]` never matches. Always stringify ARIA state booleans
(`cond ? 'true' : undefined`), matching the `aria-disabled`/`aria-current` convention.
