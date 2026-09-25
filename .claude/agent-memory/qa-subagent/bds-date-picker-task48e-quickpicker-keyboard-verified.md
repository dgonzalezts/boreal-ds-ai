---
name: bds-date-picker-task48e-quickpicker-keyboard-verified
description: EOA-17662 Task 48e — quick-picker keyboard nav + ARIA verified live (label Enter/Space fix, arrow/Home/End, drill-down, Escape/backdrop, live-region, dual-grid); plus reusable QA harness gotchas for the date-picker popover
metadata:
  type: project
---

# Task 48e (quick-picker keyboard navigation + ARIA) — verified 2026-09-25

Raw-playground QA against `packages/boreal-web-components/src/index.html` scenarios
`#dp-quickpicker-s1..s4`. All 7 checklist items PASS. The previously-failing item
(Tab to `.bds-calendar-grid__label-button` → Enter/Space opens the month picker) now works:
the `grid-navigation.ts` `onActivate` wrapper fired `document.activeElement.click()` exactly
once per keypress (instrumented with a `window.__labelClicks` capture listener on the label),
state stayed stable at 120ms and 400ms (no open-then-close), for both Enter and Space.

## Verified DOM/ARIA facts worth reusing

- Tab order on an open popover (single grid): trigger input → `Close` → `Previous month` →
  **outer label button** (`aria-label="September 2026, choose month"`) → `Next month` →
  the one roving day cell (`tabindex="0"`) → `Clear` → `Cancel` → `Apply`. Tabbing past
  `Apply` leaves the popover and closes it.
- Picker open state: `.bds-calendar-grid__picker-overlay` + `.bds-calendar-grid__picker-card`
  present; day `<table.bds-calendar-grid__day-grid>` keeps `aria-hidden="true"` + `inert`
  (attr and `.inert` prop) + `--dimmed`; outer `.bds-calendar-grid__header` also
  `aria-hidden`+`inert`+`--dimmed`; exactly 12 `.bds-calendar-grid__picker-cell--month`.
- Month grid = 3 cols × 4 rows (Jan..Dec). Year grid = 3 × 4 of `pickerStartYear` (decade
  floor). `wrap: true`. Roving tabindex always exactly one `tabindex="0"`; out-of-range
  (disabled/null) cells are never focus stops or the roving cell.
- `basic` (non-`default`) calendar type does **not** auto-close the popover on day selection
  (`bds-date-picker.tsx` `handleDayClick` only auto-closes when `isDefaultCalendarType`).
  Keyboard and mouse day activation are otherwise byte-identical (`--selected` on the cell).
- Live region `.bds-calendar-grid__quick-picker-live-region` announces only view transitions:
  month→`"Month view"`, year→`"Year view, 2020–2031"`, Escape/backdrop→`"September 2026"`.
  A month/year *selection* sets no new picker announcement (so no duplicate); the separate
  `bds-date-picker__live-region` handles the month change via `bdsMonthNavigate`.
- `#dp-quickpicker-s3` bounds `2026-06-01..2027-03-31`: 5 disabled months (Jan–May 2026),
  10 disabled years (2020–2025, 2028–2031); all skipped correctly as focus stops.

## Harness gotchas (date-picker popover)

- **A forward `Tab` from inside the popover can close the whole popover** once focus passes
  the last focusable (`Apply`) — `bds-popover` closes on focus leaving it. So "Tab to the
  header label" only works from the trigger input (or another in-popover element *before* the
  label); from a focused day cell you must **Shift+Tab** (backwards) or close+reopen first.
  A loop that blindly presses `Tab` from a day cell will silently close the popover.
- Two `.bds-calendar-grid__label-button` elements exist while a picker is open (outer day-grid
  label + inner year label). Scope: outer = `.bds-calendar-grid__header .bds-calendar-grid__label-button`;
  inner year = `.bds-calendar-grid__picker-header .bds-calendar-grid__label-button`.
- To prove "no double-activation" without touching source, add a capture click listener that
  increments `window.__labelClicks` on the label, then assert it incremented by exactly 1.
- For the live region, observe the **grid host** with `MutationObserver({childList,subtree,characterData})`
  and filter records by `region.contains(r.target) || r.target === region`; observing the
  region element directly is fine but the host survives any inner re-render.
- `run-code` scripts: no `setTimeout` (use `page.waitForTimeout`); don't reference `document`
  in the Node-side function body — only inside `page.evaluate`.
- The playground's own pre-existing warnings include 3 `[bds-date-picker]` config warnings
  (expanded-without-range, with-time-without-range, min/max spanning <2 months) from *other*
  scenarios — expected, not 48e regressions. Zero console **errors**.
