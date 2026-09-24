---
name: date-picker-reopen-shift-not-restored
description: bds-date-picker ADR-0016 same-day-inversion grid highlighting — history of the reopen-mismatch finding and its resolution; still verify grid DOM/screenshot on reopen for any real-anchor+computed-shift feature
metadata:
  type: project
---

**Resolved 2026-09-22 (Task 34d-1, superseding the finding below).** The two-day-on-reopen
behavior originally reported here was not fixed by restoring the old one-day behavior —
instead ADR 0016 was amended to make the grid intentionally highlight the resolved
same-day-inverted span **live**, during initial selection, not just on reopen (see
`ai-docs/decisions/0016-date-picker-intraday-range-time-ordering.md`). Since live selection
and reopen hydration now both route through the same `resolveSameDayInvertedEndIso`/
`resolveEffectiveRangeEndIso` check in `bds-date-picker.tsx`, they agree by construction.
Re-verified manually: inverted same-day selection (Start 14:00 -> End 09:00) highlights
both the real day (`range-start`) and the next day (`range-end`) live, before Apply;
reopening after Apply shows the identical two-day highlight; non-inverted same-day
selections and preset coverage-shift cases (e.g. "Last 7 days") are unaffected — grid
shows only the real days in both cases.

**Original finding (2026-09-21, Task 34d manual QA — now superseded):** after Apply-ing an
ADR-0016 same-day intraday inverted-time range, reopening the popover hydrated
`draft.rangeEnd` as the shifted day rather than the real day clicked, so the grid showed
two highlighted days on reopen but only one during live selection — a live-vs-reopen
inconsistency, not (as first assumed) a violation of a "grid never shows the shift" rule.

**How to apply going forward:** whenever manually QA-testing any date-picker feature that
computes a display/commit-only shift from a real anchor (ADR 0015's coverage shift, ADR
0016's same-day-inversion shift), always test the **reopen** path in addition to the
initial Apply, and always inspect the grid's highlighted cells directly (`className` via
`eval`, filtering `bds-calendar-grid__day` elements) rather than relying on header/trigger
text alone — text can look identical whether or not the underlying highlighted day set
matches. This is still true even though ADR 0016's own reopen/live mismatch is now closed.
