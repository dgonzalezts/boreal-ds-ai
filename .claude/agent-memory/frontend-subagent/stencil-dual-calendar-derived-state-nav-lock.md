---
name: stencil-dual-calendar-derived-state-nav-lock
description: Coupling two sibling calendar instances to stay exactly one month apart via derived state, not independent @State + guarded buttons (bds-date-picker expanded range, EOA-17138 Task 19m-3)
metadata:
  type: project
---

When a dual-calendar range picker (`calendarType="expanded"`) must keep its two calendars permanently consecutive (never non-consecutive, identical, or reversed), don't model the second calendar's displayed month as independent `@State` guarded reactively by disabled nav buttons — that only patches the symptom and still allows drift if any guard is missed. Instead, convert the second calendar's `year`/`month` into a **value derived fresh every render** from the first calendar's `@State` pair (e.g. `private get secondDisplayYear(): number { return this.nextMonthFrom(this.displayYear, this.displayMonth).year; }`), matching React Aria's single-`focusedDate`-plus-`visibleDuration` model and React Day Picker's single-`month`-plus-`numberOfMonths` model. This makes the "two calendars can drift apart" bug class structurally impossible rather than merely guarded against.

**Consequences of the derived-state approach:**
- The nav-event handler (`handleMonthNavigate`, wired via `@Listen`) no longer needs to know *which* calendar instance emitted the event — since there's only one shared anchor pair to update, branch on `event.detail.direction` (`'prev' | 'next'`, already present on `CalendarGridMonthNavigateDetail`) and shift the anchor by ±1 month with `addMonths`/`subMonths`, not on `event.target`.
- Any `ref` callback that existed solely to give the listener an `event.target === this.secondCalendarEl` discriminator becomes dead code once removed — `tsc`'s `noUnusedLocals` will flag the field as "declared but its value is never read" (it's still *assigned* via the ref, but assignment alone doesn't count as a read) — delete the field and the `ref` callback together, don't just stop reading it.
- Disabling the "impossible" nav directions unconditionally (first calendar's Next, second calendar's Prev) is now a **UI consequence** of the derivation, not the mechanism preventing drift — OR it on top of the existing min/max guard (`firstGuard.nextDisabled || this.isExpandedCalendarType`), don't replace the guard.
- The narrow-min/max-window case (where the derived second month falls entirely outside `max`, or vice versa) can still leave one calendar permanently fully-disabled — that's an accepted, separately-warned-about limitation (see Task 19m-2's `warnIfNarrowExpandedRangeWindow`), not something this pattern is expected to route around.

**Why:** implementing `bds-date-picker`'s dual-calendar consecutive-month lock (EOA-17138 Task 19m-3). Prior to this, `secondDisplayYear`/`secondDisplayMonth` were independent `@State` initialized once and then updated only via their own `bdsMonthNavigate` — nothing coupled them to the first calendar, so a user could navigate the two into a non-consecutive or reversed state.
