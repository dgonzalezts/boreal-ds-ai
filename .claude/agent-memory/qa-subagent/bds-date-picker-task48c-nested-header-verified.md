---
name: bds-date-picker-task48c-nested-header-verified
description: Task 48c quick-picker nested header (outer day-grid header dimmed+inert, picker gets its own separate header) confirmed live across dp-quickpicker-s1/s2/s3 — all 4 checklist items pass, zero regressions.
metadata:
  type: project
---

EOA-17662 Task 48c manual QA: confirmed via live DOM/computed-state checks (not just screenshots) on `pnpm dev:components` (:3333) using `dp-quickpicker-s1` (basic), `dp-quickpicker-s2` (expanded/range), `dp-quickpicker-s3` (basic, min=2026-06-01/max=2027-03-31).

**DOM structure found:** `.bds-calendar-grid__grid-area` contains, as siblings: the day `<table class="...day-grid--dimmed" aria-hidden inert>` and a new `.bds-calendar-grid__picker-overlay` > `.bds-calendar-grid__picker-card` > `.bds-calendar-grid__picker-header` (own prev/next + label) + `<table class="...picker">` (month/year grid). The **outer** `.bds-calendar-grid__header` (day-grid's own header) is a sibling of `.grid-area`, gets `--dimmed` class + `aria-hidden="true"` + `inert` while any picker view is open, and reverts fully (no dimmed class, no aria-hidden, no inert) when the picker closes.

**All 4 checklist items PASS:**
1. Two distinct header rows confirmed live and via screenshot: outer "September 2026" (dimmed) stays visible; inner picker header ("2026" in month view, "2020 – 2031" non-interactive label in year view) renders inside the white card, not dimmed.
2. Outer header controls proven unreachable: direct `.focus()` on outer "Previous month" button and the outer label button both fail silently (`document.activeElement` stays at `BODY`/whatever it was) — `inert` genuinely blocks focus, not just visual dimming. Real sequential `Tab` presses from the trigger's text input also confirmed the outer month-nav controls are skipped entirely (order observed: Close → inner Previous year → inner label → inner Next year → footer buttons → wraps to next scenario's field).
3. Inner header controls work exactly as pre-relocation: prev/next-year step the month grid's displayed year (2026→2025→2026); clicking the year label opens the year grid with its own decade-window header; decade prev/next step by 10 (2020–2031 → 2010–2021 → 2020–2031). On `dp-quickpicker-s3` (bounded), prev/next-year and decade prev/next both correctly disable exactly at full-year/full-decade out-of-range boundaries (verified via `.disabled` on the `bds-button`'s inner `<button>` — matches Task 48's existing min/max semantics, no "future disabled" beyond `max`).
4. Closing (month click → day click) restores the outer header/day-grid to fully normal state and re-enables `.focus()` on the outer "Previous month" button.

**Regression check (dp-quickpicker-s2):** confirmed via querying both `bds-calendar-grid` instances directly — only the grid whose label was clicked (left, "September 2026") gets `--dimmed`/`aria-hidden`/`inert`/overlay; the untouched grid (right, "October 2026") stays fully normal. Dual-instance independence holds for the header exactly as it already did for the day-grid body (Task 48b).

Zero console errors throughout (`playwright-cli console error` → 0 errors, only pre-existing icon-only-button accessible-name INFO/WARNING noise, unrelated).

**Gotcha avoided:** a `bds-button`'s internal native `<button>` needs a real click (see [[qa-subagent-synthetic-click-vs-real-click]]), but the outer/inner **label** buttons here are plain native `<button class="bds-calendar-grid__label-button">` elements (not wrapped in `bds-button`) — a JS `.click()` on those works fine and was used to drive the second `dp-quickpicker-s2` grid without a real pointer event.
