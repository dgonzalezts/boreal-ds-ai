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

## 3. `applyRovingTabindex` only demotes cells that are IN the `items` list (FM-CG-21)

`applyRovingTabindex(items, activeIndex)` finds the current stop via
`items.findIndex(item => item.getAttribute('tabindex') === '0')` and only demotes *that* item. So if
the caller builds `items` with disabled cells filtered out (`cell.isDisabled ? null : …` — as
`getMonthPickerGridItems`/`getYearPickerGridItems` do), a stale `tabindex="0"` sitting on a
**now-disabled** cell is invisible to it and is **never demoted** → two cells claim the tab stop,
one dead.

How a stale stop on a disabled cell arises: picker cells are keyed by `month`/`year`, so the same
`<td>` DOM node persists across a `pickerYear` change while its `isDisabled` flips. Stencil's vdom
diff skips re-writing `tabIndex={-1}` because the *vnode* value is unchanged (it never knew about
the imperative `0`), so the DOM keeps the stale `0`.

Fix (`focusPickerCellByKey`): explicitly `setAttribute('tabindex','-1')` on **every rendered picker
cell** — `this.el.querySelectorAll('td.bds-calendar-grid__picker-cell')` — before calling
`this._keyboard.rovingTabindex(flatItems, index)`. Demote from the **rendered DOM**, not just
`_pickerCellRefs.values()`: the map is normally complete at `componentDidUpdate` time (traced live:
`refsKeys=0..11`), but the DOM query is robust regardless of ref-callback timing. Doing it in the
shared `focusPickerCellByKey` covers both the month and year picker focus-restoration paths.

**Live-verification gotcha (FM-CG-21 false alarm):** the first "the fix does not work in a real
browser" report was a **stale dev-server chunk**, not a logic failure. `pnpm dev:components`
(`stencil build --dev --watch --serve`) served a pre-fix content-hashed chunk
(`p-<hex>.entry.js`, old mtime) while the watcher only rewrote a friendly-named
`bds-calendar-grid.entry.js` that the browser never loaded — the stale-lazy-chunk issue. After
`rm -rf .stencil www dist` + restart, the fresh build emitted **friendly-named** `*.entry.js` chunks
(which the browser loads directly), and the invariant held immediately (`stopCount:1`,
`anyDisabledStop:false`). Before trusting any live repro of a component change here, confirm the
served chunk is fresh via `performance.getEntriesByType('resource')` and a full clean rebuild.

Year picker: **no reachable leak** — a year cell's `isDisabled` depends only on `min`/`max`, which a
±10 window shift doesn't change, so a cell that was enabled when focused can't flip to disabled while
its key persists; a non-persistent key's node is removed entirely. (The shared demote hardens it
anyway.) Day grid already avoided this via `markTabbableCell`/`applyGridRovingTabindex` demote-all.
