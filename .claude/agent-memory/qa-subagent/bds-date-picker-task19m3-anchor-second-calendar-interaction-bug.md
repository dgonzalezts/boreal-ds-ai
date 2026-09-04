---
name: bds-date-picker-task19m3-anchor-second-calendar-interaction-bug
description: EOA-17138 Task 19m-3 manual QA found a real bug — combining 19m-1's "anchor to max month" fallback with 19m-3's "second calendar = first + 1 month" derivation lands the second calendar entirely out-of-range (fully disabled) whenever the anchor equals the last valid month, even in a wide (>=2-month) min/max window. FIXED and RE-VERIFIED 2026-09-03 — see "Fix verified" section below.
metadata:
  type: project
---

## Fix verified (2026-09-03 re-verification pass)

`resolveFallbackDisplayMonth`/`resolveDisplayMonth` (`utils/value-mapping.ts`) gained a
`reserveExtraMonth` param. `resolveDraftDisplayMonth()`'s range branch now passes
`this.isExpandedCalendarType` as that flag. When the natural anchor would land exactly on
`max`'s month (both bounds set, today outside the whole window) AND `expanded`+`range` is
active, the anchor now backs off one further month — but only if the backed-off month is still
`>= min`'s month (i.e. only when the window is `>=2` months wide).

**Re-verified against `dp-19m3-wide-excl-today`** (`min="2026-06-01" max="2026-08-31"`, real
clock 2026-09-03): now opens directly on **July 2026 / August 2026** — July fully valid (0/42
disabled), August fully valid for all 31 in-month days (the 5 disabled cells are September
*outside-month padding* cells, correctly disabled since September > max). Confirmed via actual
DOM class inspection (`bds-calendar-grid__day--disabled`), not just screenshot. Confirmed a real
day click in each calendar (July 15, August 20) produces a valid `Start: 2026/07/15 End:
2026/08/20` range with no manual recovery step needed.

**Regressions confirmed unaffected:**
- `dp-range-expanded` (no min/max): first-cal Next / second-cal Previous still disabled from
  mount; Previous ×4 on first cal moves both back together (Sep/Oct → Aug/Sep → Jul/Aug →
  Jun/Jul → May/Jun); Next ×4 on second cal moves both forward together (Oct/Nov → Nov/Dec →
  Dec/Jan → Jan/Feb) — always exactly 1 month apart.
- `dp-19m2-wide` (min=2026-06-01, max=2026-12-31, today inside window): still opens on today's
  real month pair (Sep/Oct), unaffected by the reservation logic since the anchor never lands on
  `max` here. Previous stops exactly at June (min); Next stops exactly at Nov/Dec (max).
- `dp-19m2-narrow` (distance <2 months): still shows the documented, accepted single-calendar
  fully-disabled second-month limitation, unchanged — the back-off explicitly no-ops when the
  window is too narrow to reserve a month.
- Day click / range selection / swap (clicking a day before current start resets end) / Apply
  (`bdsChange` fires `{start, end}` in correct ISO shape) all confirmed working end-to-end on
  `dp-range-expanded`.
- Single-date (`basic`, no range) and `basic`+`range` anchor-clamping from Task 19m-1 fully
  unaffected — `reserveExtraMonth` is never passed `true` outside the `expanded`+`range` branch.
  Spot-checked `dp-navguard` (basic, min/max=August) and `dp-19m2-basic-narrow` (basic, no
  range, min/max=August) both still anchor to August as before.

Zero console errors throughout the full re-verification pass (163 messages, 0 errors, 76
pre-existing unrelated `bds-button` icon-accessibility warnings).

**Scope:** `bds-date-picker`, `calendarType="expanded"` + `range`, both `min`/`max` set, current
system date outside the `[min, max]` window, window width >= 2 calendar months (so 19m-2's
narrow-window warning does NOT fire).

**Repro:** `min="2026-06-01" max="2026-08-31"` (June/July/August — a 3-month, i.e.
2-calendar-month-distance window, real system clock 2026-09-03, so today is outside the
window). Task 19m-3's plan text explicitly expected this exact configuration to "open directly
on a valid, selectable consecutive pair (June/July)". **Actual observed behavior on a fresh
page load:** opens on **August 2026 / September 2026** — August is fully valid (0/31 days
disabled) but **September is fully disabled (30/30 days disabled)**, i.e. exactly the "disabled
month requiring manual recovery" state the task's own manual-test explicitly said should NOT
happen. One click of the (still-live) first calendar's "Previous" button recovers to
July/August (fully valid) — so it is not a *total* dead end, but it fails the plan's own stated
acceptance bar of landing directly on a valid pair.

**Root cause (read, not fixed):** `resolveFallbackDisplayMonth()` (Task 19m-1,
`utils/value-mapping.ts`) anchors the **first** calendar to `max`'s month whenever today's month
is fully disabled and both bounds are set ("preferring the most recent valid month when both
bounds are set"). Task 19m-3's second calendar is unconditionally derived as
`nextMonthFrom(displayYear, displayMonth)` — i.e. anchor + 1 month, with zero bounds-awareness
of its own. When the anchor lands exactly on `max`'s month (which 19m-1's own policy makes the
*preferred* outcome), the derived second calendar is `max + 1`, always out of range by
construction. This is an unhandled interaction between two independently-shipped tasks — each
individually correct in isolation (19m-1 for single-calendar/`basic`, 19m-3's coupling
mechanism itself), but composing them exposes exactly the gap 19m-3's own manual-test
description called out and expected to be already fixed.

**Not a regression of item 6 (narrow-window, `dp-19m2-narrow`)** — that's a different, already
*documented and accepted* limitation (Task 19m-2's warning). This is a *new*, wider-window case
that the plan's authors evidently didn't realize could still occur; 19m-2's warning condition
(`distance < 2`) does not fire here (distance is exactly 2), so no warning alerts the consumer
either.

**Suggested fix direction (not implemented):** either (a) anchor the fallback to `max - 1`
month (not `max`) whenever both bounds are set and `expanded`+`range` are both active, so the
derived second calendar (`anchor + 1 = max`) always lands in-range; or (b) make the anchor
resolution itself aware it needs to reserve room for the derived second calendar — i.e. treat
the *effective* usable window as `[min, max - 1 month]` when computing the fallback anchor for
`expanded`+`range`. Option (a)/(b) both need care not to break 19m-1's own single-calendar
(`basic`/`default`) behavior, which correctly wants exactly `max` as the anchor.

**Verification method:** hard page reload (`playwright-cli reload`) before opening the picker,
not just closing/reopening the popover in the same session — confirms it's the *initial anchor
resolution* path, not a leftover in-session state artifact from earlier clicks.
