---
name: grid-wrap-tests-location-and-locale-coupling
description: "Where grid wrap tests actually live, and why the two 'wraps focus from … row …' test names are locale-coupled rather than locale-independent wrap coverage."
---

Two facts for anyone touching grid keyboard tests.

**1. Where wrap coverage lives.** The generic grid-navigation util's spec (`src/utils/a11y/keyboard/__test__/navigation.spec.ts`, inside `describe('setupGridNavigation')`) contains exactly one generic wrap test — `wraps horizontally and vertically at the edges when onBoundary is omitted` — alongside its `onBoundary` tests. It does **not** cover the calendar's month-boundary escape. That behavior is tested in `src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.keyboard.spec.ts` (ArrowRight/Left/Up/Down leaving the month → `bdsMonthNavigate` with `focusDate`), and the `expanded` hand-off in `src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts`.

A prior brief stated `navigation.spec.ts` contains no grid wrap tests; that is not accurate — it has one generic wrap test. The real gap is that it has no *calendar-boundary* coverage.

**2. The two "wraps focus from … row …" tests are locale-coupled.** In `bds-calendar-grid.keyboard.spec.ts`:

- `wraps focus from the end of a row to the start of the next row` — focus day 7, ArrowRight, expect day 8.
- `wraps focus from the start of a row to the end of the previous row` — focus day 8, ArrowLeft, expect day 7.

Both use a February-2026 grid from `renderGrid(2026, 1)` with **no locale**, so `generateMonthGrid`'s default **Sunday** start applies: Feb 7 is the last column of row 0 and Feb 8 the first column of row 1, making these genuine row wraps *as written*. Under a Monday-start grid (explicit `weekStartsOn: 1`, or a locale such as `fr`), Feb 7 and Feb 8 are adjacent in the same row and both assertions still pass without any wrap occurring.

Do not treat these names as locale-independent wrap coverage. If a guaranteed wrap assertion is needed, pin the locale (or `weekStartsOn`) explicitly, or assert the cells' row membership directly rather than relying on the day numbers alone.
