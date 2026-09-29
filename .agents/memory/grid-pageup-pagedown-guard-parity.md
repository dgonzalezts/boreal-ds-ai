---
name: grid-pageup-pagedown-guard-parity
description: "PageUp/PageDown in bds-calendar-grid's day view previously bypassed the prevDisabled/nextDisabled and fully-disabled-month guards the header buttons enforce; now aligned."
---

In `bds-calendar-grid`'s day view, `handlePageUp`/`handlePageDown` route to `handlePrevClick`/`handleNextClick`. Those handlers now early-return on `prevDisabled`/`nextDisabled`. Previously they built the target month and emitted `bdsMonthNavigate` unconditionally, bypassing the guard the header buttons already enforced.

Consequences:

- In `expanded`, the primary (left) calendar renders `nextDisabled` forced `true` and the secondary (right) `prevDisabled` forced `true`, so PageUp/PageDown now mirror the header buttons — forward only from the right calendar, back only from the left.
- In every variant, when the adjacent month is fully outside `min`/`max` (fully disabled), the key is a no-op instead of navigating into a month with no selectable days.
- The quick-picker's month/year views are unaffected: there PageUp/PageDown route to the year-window handlers, which already had their own fully-disabled guards.

Covered by `bds-date-picker.keyboard.spec.ts` → `does not page into a fully-disabled adjacent month with PageUp or PageDown`. Introduced by ADR 0017 (`ai-docs/decisions/0017-date-picker-keyboard-month-boundary-navigation.md`).
