# Failure-Mode Catalog — bds-calendar-grid

Created 2026-09-28, first dedicated catalog for this component (its earlier keyboard/boundary rows live in
`bds-date-picker.md`'s FM-78 – FM-109, written before this file existed). This file covers the cross-month
boundary + `focusDate` surface added for EOA-17662, audited independently against `bds-calendar-grid.tsx`,
`grid-navigation.ts`'s `onBoundary` handling, and `KeyboardController.setGridNavigation`.

Scope note: the generic 2D-nav math (arrows/Home/End/wrap/skip) is catalogued and covered in
`bds-date-picker.md` FM-78 – FM-84. Rows here cover only what that surface did not: `onBoundary`, the
cross-month `bdsMonthNavigate` emit, the `@Method() focusDate` contract, the new `handleNextClick`/
`handlePrevClick` guards, and the `componentDidUpdate` pending-ISO guard.

---

### FM-CG-01 | `onBoundary` fires the direction of the arrow that would leave the grid's populated rows, instead of wrapping, and does not move focus itself

- **ID:** FM-CG-01
- **Category:** boundary
- **Risk:** a caller extending navigation beyond the grid (e.g. to an adjacent month) would never be told the
  user reached the edge, or focus would jump to the opposite edge instead of handing off — the entire
  cross-month arrow feature dies silently
- **Input that reveals it:** a 2×2 grid with `wrap: true` and `onBoundary` set; ArrowRight on the last cell of
  the last row, ArrowLeft on the first cell of the first row, ArrowUp on the first cell, ArrowDown on the last
- **Observed current behavior:** `grid-navigation.ts:139-142` (vertical) and `:164-167` (horizontal) call
  `onBoundary(GRID_BOUNDARY_DIRECTION.<dir>)` and `return` before `applyFocus` when `findRowWithCells(...,
  wrap: false)` reports no row in that direction
- **Recommended contract:** each of the four edge moves calls `onBoundary` once with `'left'`/`'right'`/`'up'`/
  `'down'` respectively, focus stays on the origin cell
- **Contract status:** confirmed
- **Why it matters:** the shared-util extension point every grid consumer relies on; asserted at the util level so
  the contract survives independent of any one component's wiring
- **Covered by:** `src/utils/a11y/keyboard/__test__/navigation.spec.ts::'fires onBoundary with the boundary direction instead of wrapping, without moving focus'`

### FM-CG-02 | `onBoundary` does not fire for a horizontal move that wraps within the grid

- **ID:** FM-CG-02
- **Category:** boundary
- **Risk:** an over-eager boundary check would fire `onBoundary` on every row transition, so a calendar would
  skip months on an ordinary intra-month row-to-row arrow
- **Input that reveals it:** a 2×2 grid, `wrap: true`, `onBoundary` set; ArrowRight on the last column of the
  first row (which wraps to the first cell of the second row)
- **Observed current behavior:** the horizontal boundary check (`grid-navigation.ts:164`) only runs its
  `findRowWithCells(..., wrap: false) === -1` test; a populated next row makes it false, so `applyFocus` runs
- **Recommended contract:** no `onBoundary` call; focus moves to the wrapped cell
- **Contract status:** confirmed
- **Why it matters:** distinguishes a true grid edge from a row end — the exact distinction the cross-month
  feature depends on
- **Covered by:** `src/utils/a11y/keyboard/__test__/navigation.spec.ts::'does not fire onBoundary for a horizontal move that wraps within the grid'`

### FM-CG-03 | `onBoundary` does not fire when `wrap` is false

- **ID:** FM-CG-03
- **Category:** boundary
- **Risk:** a non-wrapping grid would emit its boundary callback on an edge arrow even though the documented
  gate is `wrap === true`, spuriously telling the caller to navigate away
- **Input that reveals it:** a 2×2 grid with `wrap: false`, `onBoundary` set; ArrowRight on the last cell,
  ArrowLeft on the first
- **Observed current behavior:** the horizontal wrap block is gated on `wrap && items.length > 1`
  (`grid-navigation.ts:159`); the vertical check carries an explicit `wrap &&` (`:139`); with `wrap: false`
  both fall through to the clamped `edgeCell` focus, never `onBoundary`
- **Recommended contract:** no `onBoundary` call; focus stays on the edge cell
- **Contract status:** confirmed
- **Why it matters:** `onBoundary` is documented as firing only "while `wrap` is `true`"
- **Covered by:** `src/utils/a11y/keyboard/__test__/navigation.spec.ts::'does not fire onBoundary when wrap is false'`

### FM-CG-04 | Omitting `onBoundary` preserves the pre-existing wrap behavior

- **ID:** FM-CG-04
- **Category:** equivalence
- **Risk:** a regression in the new `onBoundary` branch could turn an omitted callback into an early `return`,
  breaking wrapping for every existing grid consumer that never opted into the extension point
- **Input that reveals it:** a 2×2 grid, `wrap: true`, no `onBoundary`; ArrowRight/ArrowLeft/ArrowUp/ArrowDown
  from every edge
- **Observed current behavior:** every boundary branch is guarded by `onBoundary != null && ...`, so an omitted
  callback falls through to the original `applyFocus` wrap targets (`grid-navigation.ts:139`, `:164`)
- **Recommended contract:** horizontal wrap crosses into the adjacent row's first/last cell; vertical wrap
  cycles to the closest column of the first/last row
- **Contract status:** confirmed
- **Why it matters:** this generic wrap path had no direct test before the extension point was added
- **Covered by:** `src/utils/a11y/keyboard/__test__/navigation.spec.ts::'wraps horizontally and vertically at the edges when onBoundary is omitted'`

### FM-CG-05 | `KeyboardController.setGridNavigation({ onBoundary })` forwards the callback to the utility

- **ID:** FM-CG-05
- **Category:** component-contract-bypass
- **Risk:** the config field could be dropped between the public controller API and `setupGridNavigation`, leaving
  `onBoundary` inert for every consumer even though the util supports it
- **Input that reveals it:** attach a controller to a 2×2 root, `setGridNavigation({ wrap: true, onBoundary })`,
  ArrowRight on the last cell
- **Observed current behavior:** `KeyboardController.setGridNavigation` (`KeyboardController.ts:642-655`) passes the
  whole `config` straight into `setupGridNavigation`; no per-field filtering
- **Recommended contract:** the callback fires with `'right'` and focus does not wrap
- **Contract status:** confirmed
- **Why it matters:** the public API seam between the controller and the util
- **Covered by:** `src/utils/a11y/keyboard/__test__/KeyboardController.spec.ts::'forwards onBoundary to the grid utility when an arrow key leaves the grid edge'`

### FM-CG-06 | The grid emits `bdsMonthNavigate` with the exact `focusDate` target for each boundary direction

- **ID:** FM-CG-06
- **Category:** boundary
- **Risk:** a wrong day-offset mapping (left/right ±1, up/down ∓7) or a stale `focusDate` would land keyboard focus
  on the wrong day after the parent shifts months, or fail to land at all
- **Input that reveals it:** February 2026; ArrowRight on day 28, ArrowLeft on day 1, ArrowDown on day 28,
  ArrowUp on day 1; January 2026, ArrowDown on day 31
- **Observed current behavior:** `handleGridOutOfBounds` (`bds-calendar-grid.tsx:288-324`) maps
  `GRID_BOUNDARY_DAY_OFFSET` (`:36-41`) onto `addDays(cell.date, offset)`, sets `_pendingFocusIsoDate =
  toNaiveISODate(target)`, and emits `{ year, month, direction: dayOffset > 0 ? 'next' : 'prev', focusDate }`
- **Recommended contract:** right = next month day 1 (`2026-03-01`); left = previous month's last day
  (`2026-01-31`); down = +7 days (`2026-03-07`); up = −7 days (`2026-01-25`); Jan 31 + down = `2026-02-07`;
  `direction` follows the sign of the offset
- **Contract status:** confirmed
- **Why it matters:** `focusDate` is the whole point of the hand-off — the parent uses it verbatim
- **Covered by:** `bds-calendar-grid.keyboard.spec.ts::'emits bdsMonthNavigate with the next month and first day when ArrowRight leaves the last day'`, `'emits bdsMonthNavigate with the previous month and last day when ArrowLeft leaves the first day'`, `'emits bdsMonthNavigate seven days ahead when ArrowDown leaves the last week'`, `'emits bdsMonthNavigate seven days back when ArrowUp leaves the first week'`, `'emits bdsMonthNavigate with the exact same-weekday target for a week crossing (Jan 31 + ArrowDown)'`

### FM-CG-07 | The grid suppresses the boundary emit when the crossed target stays in the displayed month

- **ID:** FM-CG-07
- **Category:** boundary
- **Risk:** with a `min` cutting the leading days of a month, an edge arrow whose ±1/±7 target is still inside the
  displayed month would emit a `bdsMonthNavigate` the parent would honour, navigating away from the month the
  user is already looking at
- **Input that reveals it:** September 2026 with `min = 2026-09-10`; focus the first enabled day (10) and
  ArrowLeft
- **Observed current behavior:** `handleGridOutOfBounds` (`bds-calendar-grid.tsx:308-310`) returns before
  emitting when `targetYear === this.year && targetMonth === this.month`
- **Recommended contract:** no emit, focus unchanged
- **Contract status:** confirmed
- **Why it matters:** the exact `min`-cuts-day-1 boundary case the plan calls out
- **Covered by:** `bds-calendar-grid.keyboard.spec.ts::'does not emit bdsMonthNavigate when the crossed target stays in the displayed month'`

### FM-CG-08 | The grid suppresses the boundary emit when the adjacent month is fully disabled

- **ID:** FM-CG-08
- **Category:** boundary
- **Risk:** a bounded picker could navigate into an entirely unselectable month (e.g. past `max`), stranding the
  user in an empty grid
- **Input that reveals it:** October 2026 with `max = 2026-10-31`; focus day 31 and ArrowRight (November is
  entirely after `max`)
- **Observed current behavior:** `handleGridOutOfBounds` (`bds-calendar-grid.tsx:312-314`) returns when
  `isMonthFullyDisabled(generateMonthGrid(targetYear, targetMonth, { min, max }))`
- **Recommended contract:** no emit, focus unchanged
- **Contract status:** confirmed
- **Why it matters:** protects the `min`/`max` "never enter a fully-disabled adjacent month" contract named in
  TC-33 scenario 5
- **Covered by:** `bds-calendar-grid.keyboard.spec.ts::'does not emit bdsMonthNavigate when the adjacent month is fully disabled by max'`

### FM-CG-09 | `handleNextClick`/`handlePrevClick` no-op when `nextDisabled`/`prevDisabled` is set

- **ID:** FM-CG-09
- **Category:** component-contract-bypass
- **Risk:** the header buttons are gated by `bds-button`'s own `disabled`, but PageDown/PageUp call the handlers
  directly — without the in-handler guard a bounded picker could still page into a fully-disabled month via the
  keyboard, bypassing the disabled button entirely
- **Input that reveals it:** a grid with `nextDisabled = true` and PageDown; `prevDisabled = true` and PageUp;
  and the rendered header Next/Previous buttons in each state
- **Observed current behavior:** `handleNextClick` (`bds-calendar-grid.tsx:361-368`) and `handlePrevClick`
  (`:422-429`) each begin with an `if (this.nextDisabled|prevDisabled) return;` guard before emitting
- **Recommended contract:** no `bdsMonthNavigate` from a disabled direction via keyboard or button; an enabled
  direction still emits `{ year, month, direction }`
- **Contract status:** confirmed
- **Why it matters:** TC-33 scenarios 4-5 rely on PageUp/PageDown matching the disabled header buttons
- **Covered by:** `bds-calendar-grid.keyboard.spec.ts::'does not emit bdsMonthNavigate from PageDown when nextDisabled is set'`, `'does not emit bdsMonthNavigate from PageUp when prevDisabled is set'`, `'emits bdsMonthNavigate with the following month from PageDown when nextDisabled is clear'`, `bds-calendar-grid.methods.spec.ts::'does not emit bdsMonthNavigate from the header Next button when nextDisabled is set'`, `'does not emit bdsMonthNavigate from the header Previous button when prevDisabled is set'`, `'emits bdsMonthNavigate from the header Next button when nextDisabled is clear'`

### FM-CG-10 | `focusDate` moves focus to an exact enabled cell and reports success

- **ID:** FM-CG-10
- **Category:** equivalence
- **Risk:** the parent's `expanded` hand-off relies on this returning `true` and actually moving focus; a silent
  `false` would trigger the fallback window shift on every cross-calendar arrow
- **Input that reveals it:** a February 2026 grid; `focusDate('2026-02-15')`
- **Observed current behavior:** `focusDate` (`bds-calendar-grid.tsx:484-496`) resolves the exact current-month,
  non-disabled cell and delegates to `focusCell` (`:587-607`), which applies roving tabindex and returns `true`
- **Recommended contract:** resolves `true`, DOM focus lands on the exact cell, which becomes the single
  `tabindex="0"` stop
- **Contract status:** confirmed
- **Why it matters:** the primary success path of the public `@Method()`
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'focuses an exact enabled day and reports success'`

### FM-CG-11 | `focusDate(null)` returns `false` and clears any pending ISO

- **ID:** FM-CG-11
- **Category:** null-empty
- **Risk:** the parent calls `focusDate(null)` on the origin grid after a successful hand-off specifically to drop
  the pending ISO that would otherwise later steal focus back; if it didn't clear, focus would bounce
- **Input that reveals it:** a grid with a pending ISO set; `focusDate(null)`
- **Observed current behavior:** `focusDate` (`bds-calendar-grid.tsx:485-490`) assigns
  `this._pendingFocusIsoDate = null` before the `isoDate == null` early `return false`
- **Recommended contract:** resolves `false`; the pending ISO is `null`
- **Contract status:** confirmed
- **Why it matters:** the counterpart to the success path — without it the hand-off races its own origin
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'returns false and clears a pending ISO when given null'`

### FM-CG-12 | `focusDate` clamps a disabled target to the nearest enabled bound in the direction (min forward, max back)

- **ID:** FM-CG-12
- **Category:** boundary
- **Risk:** a hand-off to a day outside `min`/`max` would either fail (forcing a needless window shift) or land
  focus on a disabled, unselectable cell
- **Input that reveals it:** February 2026 with `min = 2026-02-10` and `focusDate('2026-02-05')`; with
  `max = 2026-02-20` and `focusDate('2026-02-25')`
- **Observed current behavior:** `getClampedFocusCell` (`bds-calendar-grid.tsx:638-654`) clamps to `minIso` when
  the target precedes it and to `maxIso` when it follows it, then resolves that exact enabled cell
- **Recommended contract:** each resolves `true` and focuses the min/max day respectively
- **Contract status:** confirmed
- **Why it matters:** the clamping rule the `@Method()` JSDoc documents by name
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'clamps a target before min forward to the min day and reports success'`, `'clamps a target after max back to the max day and reports success'`

### FM-CG-13 | `focusDate` returns `false` for a non-day view or an unresolvable target cell

- **ID:** FM-CG-13
- **Category:** null-empty
- **Risk:** the hardened-fallback path in the parent depends on `false` meaning "the sibling could not take
  focus"; a spurious `true` would leave focus stranded on the origin with no window shift
- **Input that reveals it:** a grid with an open quick-picker (`view !== 'days'`), `focusDate('2026-02-15')`;
  and a grid whose clamped bound resolves to a day absent from the displayed month
- **Observed current behavior:** in a non-day view `focusCell` cannot find the day cell among
  `getGridItems()`'s picker items (`index === -1` → `false`, `:601-603`); when `getClampedFocusCell`
  (`:649-653`) finds no matching cell it hands `focusCell(undefined)` → `false` (`:588-590`)
- **Recommended contract:** both resolve `false` and leave focus where it was
- **Contract status:** confirmed
- **Why it matters:** the exact boolean the parent's hardened-fallback branch keys on
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'returns false when the grid is not showing the day view'`, `'returns false when the clamped boundary day is not part of the displayed month'`

### FM-CG-14 | The `componentDidUpdate` pending-ISO guard only steals focus for an ISO present in the displayed month

- **ID:** FM-CG-14
- **Category:** race-timing
- **Risk:** a pending ISO left over from an earlier boundary crossing (e.g. after the sibling took the hand-off)
  could re-steal focus on an unrelated later re-render; conversely a legitimate pending ISO in the displayed
  month must land focus after the parent shifts it
- **Input that reveals it:** set `_pendingFocusIsoDate` to a day outside the displayed month, then trigger a
  prop-only re-render; repeat with a day inside the displayed month
- **Observed current behavior:** `componentDidUpdate` (`bds-calendar-grid.tsx:170-203`) computes
  `isoDateInDisplayedMonth`, calls `focusCell` when it (or a `_pendingFocusDayOfMonth`) matches, and otherwise
  only `markTabbableCell`s — never moving DOM focus
- **Recommended contract:** an out-of-month pending ISO leaves DOM focus untouched; an in-month one moves it to
  that exact day
- **Contract status:** confirmed
- **Why it matters:** the guard the manual hand-off race is built around
- **Covered by:** `bds-calendar-grid.keyboard.spec.ts::'leaves focus untouched when a pending ISO is not part of the displayed month'`, `'moves focus to a pending ISO that is part of the displayed month'`

### FM-CG-15 | `focusDate` state is per-instance — two grids never share focus

- **ID:** FM-CG-15
- **Category:** equivalence
- **Risk:** shared module-level focus/pending state would make a hand-off into one `expanded` grid move the
  other's stop, or clear the wrong pending ISO
- **Input that reveals it:** two grids in one page; `focusDate` on the first, inspect the second's single
  `tabindex="0"` stop
- **Observed current behavior:** `_cellRefs`, `_keyboard`, and `_pendingFocusIsoDate` are all instance fields
  (`bds-calendar-grid.tsx:57-64`)
- **Recommended contract:** the first grid's focus moves; the second's initial stop is unchanged
- **Contract status:** confirmed
- **Why it matters:** refines FM-89 (arrow-traversal independence) for the `focusDate` entry point the
  `expanded` hand-off uses
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'keeps the focusDate target independent between two grid instances'`

## Closed pending-decision row (ruled 2026-09-28 — Option B)

### FM-CG-16 | `focusDate` for an ISO that is not in the displayed month and has no clamping bound

- **ID:** FM-CG-16
- **Category:** null-empty
- **Risk:** the boolean feeds `bds-date-picker`'s hand-off decision, so a `true` for a date `focusDate` did not
  actually focus (falling back to the month's priority cell) would stop `true` meaning "the requested date was
  focused" — a silent contract violation for any consumer, even though the current internal caller happens to
  pre-check the sibling's displayed month
- **Input that reveals it:** February 2026 with `min = 2026-01-01` / `max = 2026-03-31`; `focusDate('2026-03-15')`
  — a date inside the bounds but absent from the displayed month
- **Observed current behavior:** `getClampedFocusCell` (`bds-calendar-grid.tsx:638-654`) returns `undefined` when
  neither the min nor the max clamp applies (`:649-651`), so `focusDate` resolves `false` and leaves focus
  untouched; the pre-ruling fallback instead returned `getPriorityFocusCell()`, focusing February's first enabled
  day and reporting `true`
- **Recommended contract:** **Ruled 2026-09-28 (Option B).** `focusDate(iso)` reports success only when the
  requested date — or its `min`/`max` clamp — exists in the currently displayed month. A date that is within
  bounds but absent from the displayed month resolves `false` and leaves focus untouched; it must NOT fall back to
  the month's priority cell.
- **Contract status:** confirmed
- **Why it matters:** the method is named `focusDate` and its boolean is consumed by `bds-date-picker`'s hand-off
  decision, so `true` must mean "the requested date was focused." The internal caller already pre-checks the
  sibling's displayed month, so the ruling changes no production path — it only makes the public contract honest.
  Business reasoning captured from the 2026-09-28 ruling.
- **Covered by:** `bds-calendar-grid.methods.spec.ts::'returns false without moving focus when the target is in bounds but absent from the displayed month'`

## Reconciliation against the cross-month boundary + `focusDate` unit-test list

The task list — util `onBoundary` direction/negatives/regression, controller passthrough, grid boundary emits
with exact `focusDate`, the `focusDate` `@Method()` contract, the nav-click guards, the pending-ISO guard, and
per-instance independence — maps onto FM-CG-01 – FM-CG-15. No listed item rested on FM-CG-16, which was the one
`pending-decision` row; it was ruled Option B on 2026-09-28 and is now `confirmed` and covered. No
`pending-decision` rows remain in this catalog.

---

## Month-view quick-picker paging focus (added 2026-09-28)

Covers the `bds-calendar-grid` fix that makes `PageUp`/`PageDown` in the **month** quick-picker view land real
DOM focus on a *selectable* month after the year changes, instead of leaving it on the same month number (which
can be a disabled cell once that month falls outside `min`/`max`). Audited independently against
`bds-calendar-grid.tsx`'s `@Watch('pickerYear')` MONTHS branch, `componentDidUpdate`'s consumption,
`focusMonthViewCell`, and `getNearestEnabledMonthCell`. The pre-existing "no-op when the target year is entirely
outside `min`/`max`" regression guard (`quickpicker.spec.ts`) was additionally extended to assert that focus is
retained on the current month cell, not dropped.

### FM-CG-17 | Month-view paging keeps focus on the equivalent month when it is still enabled

- **ID:** FM-CG-17
- **Category:** equivalence
- **Risk:** paging the month view would drop real DOM focus to `<body>` (or to no picker cell), so the next
  `PageUp`/`PageDown`/arrow key never reaches the grid
- **Input that reveals it:** September 2026 month view with the `Sep` cell focused; `PageDown`
- **Observed current behavior:** `@Watch('pickerYear')`'s MONTHS branch records the focused month key and
  `Math.sign(newYear - oldYear)` (`bds-calendar-grid.tsx:121-130`); `componentDidUpdate` (`:212-219`) calls
  `focusMonthViewCell(preferredMonth, direction)`, which resolves the same month number in the new year when it
  is enabled (`:662-677`)
- **Recommended contract:** focus stays on the same month number in the new year; exactly one picker cell
  carries `tabindex="0"` and it is that cell
- **Contract status:** confirmed
- **Why it matters:** the no-regression baseline for the whole month-view paging focus contract
- **Covered by:** `bds-calendar-grid.quickpicker.spec.ts::'keeps real focus on the equivalent month cell after a month-view year page'`

### FM-CG-18 | Month-view paging falls back to the nearest enabled month when the equivalent month is disabled

- **ID:** FM-CG-18
- **Category:** boundary
- **Risk:** paging to a year where the previously focused month is out of `min`/`max` would land focus on a
  disabled, unselectable cell (or nowhere), leaving the keyboard stuck
- **Input that reveals it:** `min = 2026-06-01` / `max = 2027-03-31`, June 2026 focused, `PageDown`; and the
  symmetric `PageUp` from March 2027
- **Observed current behavior:** `focusMonthViewCell` looks for the exact enabled cell, then falls through to
  `getNearestEnabledMonthCell` (`bds-calendar-grid.tsx:662-677`, `:745-769`), which picks the enabled month of
  minimum absolute distance from the preferred month — March 2027 for the `PageDown` case, June 2026 for the
  `PageUp` case
- **Recommended contract:** focus lands on that nearest enabled month; `document.activeElement` is never a cell
  carrying `aria-disabled="true"`
- **Contract status:** confirmed
- **Why it matters:** the core of the fix — a disabled cell must never receive paging focus
- **Covered by:** `bds-calendar-grid.quickpicker.spec.ts::'lands on the nearest enabled month when the equivalent month is disabled by the range maximum'`, `'lands on the nearest enabled month in the previous year when paging up from the range maximum'`

### FM-CG-19 | The nearest-enabled search prefers the paging-direction side on an equidistant tie

- **ID:** FM-CG-19
- **Category:** boundary
- **Risk:** when two enabled months are equidistant from the preferred (disabled) month, a cell on the
  opposite side of the paging direction would win, reversing the direction the user just paged
- **Input that reveals it:** a month picker whose enabled months are only `3` and `7`, preferred month `5`;
  direction `+1` must select `7`, direction `-1` must select `3`
- **Observed current behavior:** `getNearestEnabledMonthCell` (`bds-calendar-grid.tsx:759-765`) breaks a tie
  toward a cell where `(cell.month - preferredMonth) * direction > 0`
- **Recommended contract:** the paging-direction side wins an equidistant tie
- **Contract status:** confirmed
- **Why it matters:** keeps the tie-break intentional rather than "whichever month comes first in iteration
  order". **Reachability note:** `min`/`max` always yield a *contiguous* enabled run of months (a month is
  disabled only when its whole span precedes `min` or follows `max`), so no real range can place two enabled
  months equidistant around a disabled preferred month. The branch is therefore reachable only through the
  search helper directly; the test builds the cell array by hand rather than via a range.
- **Covered by:** `bds-calendar-grid.quickpicker.spec.ts::'prefers the paging-direction side when two enabled months are equidistant from the preferred month'`

### FM-CG-20 | Month-view paging with no picker cell focused falls back to the priority month cell

- **ID:** FM-CG-20
- **Category:** null-empty
- **Risk:** paging while focus is not on a picker cell (e.g. on a header control) would leave
  `_pendingMonthViewFocusTarget` null and could throw or strand focus
- **Input that reveals it:** month view open, focus cleared, `PageDown`
- **Observed current behavior:** `handlePickerYearChange` stores `focusedMonth ?? null`
  (`bds-calendar-grid.tsx:124-127`); `focusMonthViewCell(null, direction)` then takes the
  `getPriorityMonthCell` branch (`:671-676`)
- **Recommended contract:** no throw; focus lands on the year's priority enabled month cell
- **Contract status:** confirmed
- **Why it matters:** the same "nothing focused" resilience the year-window focus path documents
- **Covered by:** `bds-calendar-grid.quickpicker.spec.ts::'falls back to the priority month cell when the month view pages with no picker cell focused'`

### FM-CG-21 | A picker page leaves exactly one enabled roving stop and never leaves a disabled stop behind

- **ID:** FM-CG-21
- **Category:** component-contract-bypass
- **Risk:** after paging to a year where the previously roving month cell is disabled, that disabled cell kept
  `tabindex="0"` while the newly focused enabled cell also got `tabindex="0"` — two roving stops, one of them
  on an `aria-disabled` cell, contradicting the component's single-roving-stop invariant (FM-86 in
  `bds-date-picker.md`, plus `'sets tabindex -1 on every non-active day cell…'`)
- **Input that reveals it:** `min = 2026-06-01` / `max = 2027-03-31`, June 2026 focused, `PageDown`; the
  symmetric `PageUp` from March 2027; the unbounded month-view equivalent; and the year-window shift
- **Observed current behavior:** `focusPickerCellByKey` (`bds-calendar-grid.tsx:633-656`) now demotes every
  rendered picker cell (`td.bds-calendar-grid__picker-cell` → `tabindex="-1"`, `:651-653`) before delegating to
  `this._keyboard.rovingTabindex(flatItems, index)` (`:655`). Pre-fix, `applyRovingTabindex`
  (`focus/roving-tabindex.ts:14-26`) could only demote a previous stop still present in `flatItems`; disabled
  picker cells are mapped to `null` (`getMonthPickerGridItems` `:744-746`, `getYearPickerGridItems` `:814-816`),
  so a now-disabled cell that held `tabindex="0"` was never demoted. Month cells are keyed by month number, so
  the June `<td>` (`:986`) persisted across the year change and kept its imperatively-set `tabindex="0"`
  (`:988`); live verification observed the two stops as `['Mar', 'Jun']` with `Jun` carrying
  `aria-disabled="true"`
- **Recommended contract:** **Ruled 2026-09-28 (fix it).** After any month- or year-picker page, exactly one
  picker cell carries `tabindex="0"`, it is enabled, and no `aria-disabled` picker cell holds `tabindex="0"`
- **Contract status:** confirmed
- **Why it matters:** a roving-tabindex leak on a disabled control is a real a11y defect — it adds a second Tab
  stop to the picker grid and lands it on a cell the user cannot activate. Business reasoning captured from the
  2026-09-28 ruling. Live-verified after the fix (fresh build, Chromium): after `PageDown` `stopCount === 1`,
  `anyDisabledStop === false`, active = Mar 2027; `PageUp` back → Jun 2026, one enabled stop; unbounded Sep 2026
  → Sep 2027, one enabled stop; year view both directions, one enabled stop. Reachability note: the year-picker
  leak is unreachable in practice — a year cell's `isDisabled` derives only from `min`/`max`, which do not change
  during paging, so a year cell never transitions from an enabled stop to a disabled one; the year-view
  assertions are a one-stop regression guard
- **Covered by:** `bds-calendar-grid.quickpicker.spec.ts::'keeps real focus on the equivalent month cell after a month-view year page'`, `'keeps exactly one enabled month stop when paging up in the unbounded month view'`, `'lands on the nearest enabled month when the equivalent month is disabled by the range maximum'`, `'lands on the nearest enabled month in the previous year when paging up from the range maximum'`, `'keeps real focus on the equivalent year cell after a year-window shift'`, `'falls back to the priority enabled year cell when the equivalent year is out of range'`

