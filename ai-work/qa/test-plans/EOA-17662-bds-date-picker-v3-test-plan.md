# Test Plan: `bds-date-picker` Component (Range Time Selection + Presets Sidebar, v3)

## Context

`bds-date-picker` is a composite, form-associated (FACE) date-picker control composing a **consumer-supplied** `bds-text-field` trigger with a `bds-popover` panel containing one or two `bds-calendar-grid` bodies and a Clean/Cancel/Apply footer. This plan covers the newest additions to the component on top of the existing single-date and range-selection baseline (not re-tested here):

- Range-mode time selection: a single shared time field under `calendarType="basic"`, independent start/end time fields under `calendarType="expanded"`.
- Presets sidebar: six built-in relative-date presets (Today, Yesterday, Last 7 days, Last 30 days, This month, Last month) plus a Custom fallback state, shown beside the calendar(s) in range mode — including reopen/Cancel re-matching and reopen shift-correctness.
- `expanded` + `range=false` developer warnings and a duplicate day-highlight fix.
- Same-day intraday range selection via double-click, with an auto-shift-and-live-display behavior for an inverted end time.
- Reverse-order range click auto-correction, and the resulting bidirectional hover-preview / first-click highlight fixes.
- Confirmation that opening the calendar on a preselected date outside the visible month already navigates there correctly.

Component sources:

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/presets.ts`, `draft-state.ts`, `value-mapping.ts`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderPresets.tsx`, `renderTimeSelector.tsx`, `renderCalendarPanel.tsx`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx`
- `packages/boreal-web-components/src/services/date-engine/grid.ts`

Brand theme in scope: **Proximus only** (consistent with v1/v2 plans).
Created: 2026-09-14
Updated: 2026-09-22 — added TC-14 through TC-22 (presets reopen/Cancel/shift correctness, `expanded`+`range=false` warnings, same-day intraday ranges, reverse-order click, bidirectional hover-preview, preselected-date-outside-month confirmation); removed the multi-month preselected-range playground scenario (now a documented, intentional limitation with no dedicated test case — see Out of scope). Added TC-23 through TC-26 (info banner positioning/dismissal, footer range-summary text and pluralization).
Updated: 2026-09-24 — added TC-27 through TC-31 (month/year quick-picker: overlay/nested-header, drill-down, selected-date/range flagging, auto-close/sync on preset/clear/cross-grid actions, keyboard navigation/ARIA). Removed "month/year quick-picker — not yet implemented" from Out of scope (Tasks 46-48h). TC-31 (keyboard/ARIA) covers a task implemented but not yet live-QA-verified as of this update — mark its **Pass?** accordingly until confirmed.
Updated: 2026-09-24 — added TC-32 (quick-picker PageUp/PageDown paging per view, and year-window focus retention after a ±10 shift — Tasks 48i, 48j). TC-31 has since been live-QA-verified.
Updated: 2026-09-24 — added TC-33 (day-grid arrow-key traversal — the Phase 8 keyboard behavior previously only tracked in the implementation plan's Task 43 checklist, now a first-class test case so every playground keyboard section maps to a TC).
Updated: 2026-09-24 — aligned every test case with its `packages/boreal-web-components/src/index.html` playground scenario/element id (new **Playground:** field), aligned TC-11 to the playground's "Last 30 days → Next" scenario, and split the document into **Part 1** (TC-01 – TC-22, validated & merged) and **Part 2** (TC-23 – TC-33, in progress).

---

## Scope

**In scope:**

- Range-mode time selection: single-shared time (`basic`) vs. independent start/end time (`expanded`); popover header time display in both header formats; single-date `withTime` regression.
- Presets sidebar: all six built-in presets' computed ranges, default/fallback Custom state, revert-to-Custom on manual edit, `min`/`max`-based preset disabling, timezone-aware "today", with-time coverage-end boundary display, auto-navigation of the calendar view on preset click, re-matching the correct preset on popover reopen and on Cancel, and reopen shift-correctness (no duplicate-day highlight, no header double-shift, no value drift across repeated Apply cycles).
- `expanded` + `range=false`: developer console warnings and the duplicate day-highlight fix at month boundaries.
- Same-day intraday range selection (double-click the same day under `expanded`+`range`+`with-time`), including the auto-shift-and-live-display behavior when the end time is set earlier than the start time, and its consistency across reopen.
- Reverse-order range click (later day clicked first) auto-correcting to a valid `{ start, end }` range instead of resetting, including role-pinned time-field behavior in `expanded`+`with-time`.
- Bidirectional range hover-preview (forward and backward) and the first-click day marker no longer showing a premature directional strip.
- Confirmation that opening the calendar with a preselected date outside the currently visible month already navigates there automatically (no code change was needed for this — see Out of scope for what remains undone).
- Idempotency of preset selection and trigger toggling.
- Info banner (display-only, no action buttons, positioned as the first child of the calendar column in all `calendarType` values) and footer range-summary text (days-only under `basic`, days/hours/minutes under `expanded`, with `Intl.PluralRules`-based singular/plural word forms).
- Month/year quick-picker: drill-down (label click → month grid → year grid and back), superposed as a dimmed-backdrop overlay with its own nested header over the day grid, selected-date/range-boundary highlighting, auto-close/resync on preset click/Clear/cross-grid day-pick/cross-grid month-year navigation, and its own keyboard navigation, Escape, backdrop-click dismissal, and live-region announcements.

**Out of scope:**

- v1/v2 baseline behavior (single-date, `withTime`, `min`/`max`, `calendarType`, range core selection) — already covered by prior plans, not duplicated here.
- RTL — formally descoped as a blocking gate pending ticket-owner sign-off (see Task 41a in the implementation plan); not implemented, not tested here.
- Banner `state`/`variant` visual styling per severity (info/success/warning/danger) — the type is flexible but visual styling per state is pulled from Figma in a later SCSS-audit task, not tested here.
- Consumer-configurable presets — not implemented; the preset list is fixed.
- **Unified popover content markup** — the playground's `.bds-date-picker__calendars` / `.bds-date-picker__date-time` / `.bds-date-picker__time-band` structural section is a supplementary developer aid, explicitly not tracked as a test case; its observable outcomes are already covered by TC-23 (banner alignment) and TC-27/TC-28 (grid layout).
- **Multi-month preselected range display** — a preselected range whose `start`/`end` fall in different months than the calendar can show at once (e.g. a 3-month spread under `basic`, which shows one month) leaves `end` genuinely off-screen on open. This is a documented, intentional limitation (the display always anchors on `start`), not a bug — no dedicated test case or playground scenario for it.
- **Live external `value` reassignment while the popover is already open** (no close/reopen in between) does not re-sync the displayed month. Confirmed real, but explicitly not built — it isn't what the original request asked for (opening the calendar already navigates correctly; only a value change with the popover already open, no open/close transition, is unhandled). No test case here.
- Linking an external IANA timezone reference from the docs — documentation-only, no runtime behavior to test.
- React/Vue wrapper parity — verify no regressions only if time permits; no dedicated test cases here.

---

## Environment

```bash
fnm use && pnpm dev:components
```

from the monorepo root, opening `packages/boreal-web-components/src/index.html`. Browser: Chrome (latest stable) primary; Safari as secondary spot-check for Apply-flow cases (TC-01, TC-02, TC-10). DevTools console open for `bdsChange` logging and error/warning checks.

## Entry Criteria

- [ ] Dev server running on the branch with these changes
- [ ] `bds-date-picker` renders without console errors in the playground

## Exit Criteria

- [ ] All P0 test cases pass
- [ ] ≥ 90% of P1 test cases pass
- [ ] No open P0 bugs

---

## Test Cases

The plan is split into two parts, matching the playground's two halves. Every test case names the `index.html` playground scenario/element id it maps to in a **Playground:** field, so a tester can jump straight to the right picker.

- **Part 1 — validated & merged:** range-mode time selection, presets sidebar, and the range-selection/highlighting fixes (**TC-01 – TC-22**). Already QA-verified and merged; retained here for regression reference.
- **Part 2 — in progress:** info banner, footer range summary, day-grid keyboard traversal, and the month/year quick-picker (**TC-23 – TC-33**). Not yet validated as a whole at the time of this update.

---

## Part 1 — Range time, presets & range-selection fixes (validated & merged)

### Range-mode time selection

---

#### TC-01: `basic` + range + withTime — single shared time applies to both bounds

**Priority:** P0

**Playground:** `dp-range-time-s2` (basic + range + withTime)

**Steps:**

1. Open a `calendar-type="basic" range with-time` picker, pick a start day and end day, set one shared hour/minute, click Apply
   **Expected:** Logged `bdsChange` `{ start, end }` share identical `HH:mm` but differ in date

---

#### TC-02: `expanded` + range + withTime — independent start/end time

**Priority:** P0

**Playground:** `dp-range-time-s1` (expanded + range + withTime)

**Steps:**

1. Open a `calendar-type="expanded" range with-time` picker, pick a start date/time and end date/time with different hour/minute values, click Apply
   **Expected:** Logged `{ start, end }` UTC strings differ in time-of-day, not just date

---

#### TC-03: Single-date `withTime` regression

**Priority:** P1

**Playground:** `dp-range-time-s3` (basic, single date + withTime)

**Steps:**

1. On a non-range `with-time` picker, pick a day + time, click Apply
   **Expected:** Logged value is a single full UTC ISO string, unchanged from prior behavior

---

#### TC-04: Popover header shows time in both layouts

**Priority:** P1

**Playground:** `dp-range-time-s4a` (expanded, step 1), `dp-range-time-s4b` (basic, step 2)

**Steps:**

1. On `expanded` + range + `with-time`, no explicit `format`, pick a range + time and commit
   **Expected:** Labeled `Start:`/`End:` header shows `HH:mm` alongside each date
2. Repeat on `basic` + range + `with-time`
   **Expected:** Dash-joined header (`"YYYY/MM/DD HH:mm – YYYY/MM/DD HH:mm"`) shows time text, not just dates

---

### Presets sidebar — selection & computation

---

#### TC-05: Each built-in preset highlights the correct days

**Priority:** P0

**Playground:** `dp-presets-s1` (expanded), `dp-presets-s2` (basic)

**Steps:**

1. On both `expanded` + range and `basic` + range pickers, click each of the six presets in turn
   **Expected:** Calendar highlights the correct real days for each (Today = 1 day; Last 7/30 days include today; This month = 1st through today; Last month = full previous month); clicked preset shows selected; "Custom" is selected by default before any preset is clicked
2. On the `basic` picker, inspect the popover header
   **Expected:** Header uses the labeled `Start:`/`End:` format, not the old dash-joined line

---

#### TC-06: Manual edit after a preset reverts selection to Custom

**Priority:** P0

**Playground:** `dp-presets-s1` (expanded), `dp-presets-s2` (basic)

**Steps:**

1. Click a preset, then manually click a calendar day
   **Expected:** Selection reverts to "Custom"; the day click still applies normally
2. Click a preset, then manually change a time selector value
   **Expected:** Selection reverts to "Custom"; the time change is preserved (not discarded)

---

#### TC-07: Clicking "Custom" directly does not clear the selection

**Priority:** P2

**Playground:** `dp-presets-s1` (expanded)

**Steps:**

1. With a preset (or a manual range) already selected, click "Custom" directly
   **Expected:** The current draft selection is left untouched — only the footer's Clean/Clear action clears it

---

### Presets sidebar — bounds & timezone

---

#### TC-08: `min`/`max` disables out-of-bounds presets

**Priority:** P1

**Playground:** `dp-presets-s3` (`min="2026-09-05" max="2026-09-15"`)

**Steps:**

1. Open a picker with `min`/`max` set so some presets' ranges fall partially or fully outside the bounds
   **Expected:** Any preset whose computed range falls even partially outside `min`/`max` renders disabled and does nothing when clicked; presets fully inside the bounds stay clickable

---

#### TC-09: "Today" reflects configured `timezone`, not the device clock

**Priority:** P1

**Playground:** `dp-presets-tz-s1` (step 1), `dp-presets-tz-s2` (step 2) — both `timezone="Pacific/Kiritimati"`

**Steps:**

1. On a picker with a `timezone` far from the local device's zone (e.g. `Pacific/Kiritimati`, UTC+14), click "Today", then click Apply
   **Expected:** Highlighted day (before Apply) and the logged `bdsChange` value plus the trigger field's text (after Apply) match the configured timezone's current date, not the device's local date
2. Open a fresh picker (no prior value) with the same `timezone`
   **Expected:** The grid's own "today" highlight and default display month both match the configured timezone's date — no divergence from the preset's "today"

---

### Presets sidebar — coverage & navigation

---

#### TC-10: With-time coverage-end boundary display

**Priority:** P1

**Playground:** `dp-presets-s4` (expanded + range + withTime)

**Steps:**

1. On `expanded` + range + `with-time`, click a preset (e.g. Last 7 days), note the header, then click Apply
   **Expected:** Popover header's `End:` (before Apply) shows the coverage boundary shifted one day past the last real day, at `00:00`; the calendar still highlights only the real days; after Apply, the trigger field's text and the logged `bdsChange` `end` value both match that same boundary exactly

---

#### TC-11: Preset click auto-navigates the calendar view

**Priority:** P1

**Playground:** `dp-presets-nav-s1` (basic; steps 1-2), `dp-presets-nav-s2` (expanded; step 3)

**Steps:**

1. On `basic` + range, navigate 2+ months forward, then click a preset whose range isn't in the currently-shown month
   **Expected:** View jumps to the preset's start month with correct days highlighted, no manual navigation needed
2. On the same picker, click "Last 30 days" (or whichever built-in spans two calendar months), then click Next once
   **Expected:** The view shows the start month first; clicking Next shows the following month with the remaining range days still highlighted through today
3. On `expanded` + range, click the same spanning-months preset
   **Expected:** Calendar 1 shows the start month, calendar 2 automatically shows the following month, together covering the full range

---

#### TC-12: Re-anchoring after reverting to Custom

**Priority:** P2

**Playground:** `dp-presets-nav-s1` (basic)

**Steps:**

1. Click a preset, manually click a calendar day (reverting to Custom), then click a different preset
   **Expected:** View re-anchors correctly to the new preset's start month — no stale display month left over

---

### Idempotency

---

#### TC-13: Repeated preset click / trigger toggle produces no duplicate side effects

**Priority:** P2

**Playground:** `dp-idempotency-s1` (expanded + range)

**Steps:**

1. Click an already-selected preset a second time
   **Expected:** No change in the highlighted days or selected-preset state, no flicker/re-navigation/thrown error. Note: a preset click only updates the draft — it does not commit, so no `bdsChange` fires here; optionally click Apply once afterward and confirm exactly one `bdsChange` is logged, not two
2. Click the trigger field to open the popover, then click it again while already open
   **Expected:** No re-render or draft reset; popover stays in its current state

---

### Presets sidebar — reopen & Cancel correctness

---

#### TC-14: Presets sidebar re-matches the correct preset on popover reopen

**Priority:** P0

**Playground:** `dp-presets-s1` (expanded), `dp-presets-s4` (expanded + withTime)

**Steps:**

1. Apply a built-in preset (e.g. "Today"), close the popover, then reopen it
   **Expected:** The sidebar shows that same preset selected again — not "Custom" — verified via the selected item's own class, not just a visual glance
2. Apply a manually-selected range that doesn't match any built-in preset, close, then reopen
   **Expected:** The sidebar correctly shows "Custom" (no false-positive match)

---

#### TC-15: Presets sidebar re-matches on Cancel, with no visible flash of the wrong state

**Priority:** P1

**Playground:** `dp-presets-s1` (expanded)

**Steps:**

1. Apply a preset, reopen the popover, then click Cancel
   **Expected:** The sidebar shows the correct preset selected immediately after Cancel — not "Custom" — checked before any reopen
2. Reopen the popover again after Cancel
   **Expected:** No visible flash of "Custom" before the correct preset appears — the sidebar is already correct from the first rendered frame

---

#### TC-16: Reopening a with-time preset shows the real day(s) only, with no header double-shift or value drift

**Priority:** P0

**Playground:** `dp-presets-s4` (expanded + range + withTime)

**Steps:**

1. On a `with-time` picker, apply a preset (e.g. "Today"), close, then reopen
   **Expected:** The calendar highlights only the real day(s) — not one extra day — and the header's `End:` text matches the trigger field's committed text exactly (no double-shift)
2. Reopen and click Apply again with no changes, at least twice in a row
   **Expected:** The committed value stays identical across every cycle — no drift forward by an extra day each time

---

### `expanded` + `range=false`

---

#### TC-17: Developer warnings fire for `expanded` without `range`

**Priority:** P1

**Playground:** `dp-expanded-no-range-s1` (expanded, `range` unset, `with-time`)

**Steps:**

1. Open a `calendar-type="expanded"` picker with `range` not set and `with-time` set
   **Expected:** The console logs exactly two `[bds-date-picker]` warnings, once each — one noting `expanded` renders two calendars but only a single date can be selected without `range`, one noting `with-time` falls back to a single shared time selector without `range`

---

#### TC-18: No duplicate day-highlight at a month boundary under `expanded` + `range=false`

**Priority:** P1

**Playground:** `dp-expanded-no-range-s1` (`value` preset to `2026-09-30`)

**Steps:**

1. On the same picker, set `value` to a date that also appears as a leading filler day in the adjacent calendar's grid (e.g. the last day of a month)
   **Expected:** The selected date is highlighted in exactly one calendar — its real month — not in both

---

### Same-day intraday ranges

---

#### TC-19: Same-day double-click confirms a one-day range; an inverted end time shifts live, consistently across Apply and reopen

**Priority:** P0

**Playground:** `dp-intraday-range-s1` (expanded + range + withTime)

**Steps:**

1. On `expanded` + `range` + `with-time`, click the same day twice
   **Expected:** No popover close, no error — both Start/End time selectors become independently editable; the calendar still highlights only that one day (times are both `00:00`, nothing has inverted yet)
2. Set Start later than End on that same day (e.g. Start 14:00, End 09:00)
   **Expected:** Both the header's `End:` text and the calendar grid update live, before Apply — the following day becomes highlighted as a normal range-end, matching the header
3. Click Apply
   **Expected:** The committed `end` is a full calendar day after `start`'s date; the trigger field's text matches exactly what the header showed pre-Apply
4. Close and reopen the popover
   **Expected:** The calendar shows the identical two-day highlight it showed live before the original Apply — reopening must not collapse it back to a single day
5. Repeat from a fresh same-day selection with Start earlier than End (e.g. Start 14:00, End 18:00)
   **Expected:** No shift — the header, the calendar (single day highlighted), and the commit all agree on the same day for `End`

---

### Reverse-order range click

---

#### TC-20: Clicking a later day first, then an earlier day, auto-corrects to a valid range

**Priority:** P0

**Playground:** `dp-reverse-range-s1` (basic; step 1), `dp-reverse-range-s2` (expanded; step 2), `dp-reverse-range-s3` (expanded + withTime; step 3)

**Steps:**

1. In a `basic` + `range` picker, click a later day first, then an earlier day
   **Expected:** The range completes after exactly two clicks — no third click needed — with the earlier day as Start and the later day as End
2. Repeat in `expanded` + `range`
   **Expected:** Identical behavior to `basic` — no calendar-type-specific divergence
3. In `expanded` + `range` + `with-time`, set the End time field before clicking any day, then click a later day first and an earlier day second
   **Expected:** After the swap, the Start time field applies to the new (earlier) Start day, and the End time field applies to the new (later) End day — the time fields follow their Start/End role, not whichever specific day was on-screen when each was set
4. After a reverse-order range completes, click a third day
   **Expected:** The selection starts fresh from that day (regression check, unrelated to this behavior)

---

### Range hover-preview and first-click highlight

---

#### TC-21: Hover-preview works in both directions; a lone first click shows no premature directional strip

**Priority:** P1

**Playground:** `dp-reverse-range-s1` / `s2` / `s3` (reused from TC-20)

**Steps:**

1. Click a single day (no second click yet)
   **Expected:** The day shows a plain, non-directional filled highlight — no strip/cap extending beyond the cell, matching single-date mode's look
2. With that first click active, hover a later day
   **Expected:** A grey preview band spans from the first-clicked day to the hovered day (forward direction, already worked before)
3. Hover an earlier day instead
   **Expected:** A grey preview band renders in reverse — this previously showed nothing at all
4. Move the mouse from a forward hover to a backward hover, crossing the first-clicked day
   **Expected:** The preview band switches direction smoothly, with no moment where it disappears entirely
5. Complete an ordinary two-click range (forward order)
   **Expected:** The Start day's connecting strip correctly bridges into the rest of the highlighted band — not a disconnected square (a real regression was caught and fixed here before this reached QA; re-confirm it still holds)

---

### Preselected date outside the visible month

---

#### TC-22: Opening the calendar on a preselected date outside the current month navigates there automatically

**Priority:** P1

**Playground:** `dp-preselected-outside-month-s1` (`value` preset to `2027-04-12`)

**Steps:**

1. Set `value` on a fresh (never-opened) picker to a date several months from today, then click the field to open the popover for the first time
   **Expected:** The calendar opens already showing the preselected date's month — not today's month — with no manual navigation needed to reach it

---

## Part 2 — Info banner, keyboard traversal & month/year quick-picker (in progress)

### Info banner and footer range summary

---

#### TC-23: Banner renders correctly positioned in all `calendarType` values, including `default`

**Priority:** P1

**Playground:** `dp-banner-s1` (`default`; step 1), `dp-banner-s2` (`basic`, no range; step 2), `dp-banner-s3` (`basic` + range; step 3) — all seeded with a visible `banner`

**Steps:**

1. Open a `calendarType="default"` picker with `banner` set
   **Expected:** The banner renders above the calendar grid, aligned with it — not stretching over any presets sidebar (none present here), no console errors
2. Open a `calendarType="basic"` picker (no range) with `banner` set
   **Expected:** Same as step 1, under the basic calendar type
3. Open a `calendarType="basic"` + `range` picker with `banner` set (presets sidebar visible)
   **Expected:** The banner starts after the presets sidebar, aligned only with the calendar column — it does not stretch above the sidebar

---

#### TC-24: Banner close button dismisses it; dismissal does not persist across reopen

**Priority:** P1

**Playground:** `dp-banner-s1` (any banner scenario works)

**Steps:**

1. With a visible, closable banner, click the close ("X") button
   **Expected:** The banner dismisses (no longer renders), no console errors
2. Close the popover, then reopen it
   **Expected:** The banner re-appears — a same-session dismissal is not remembered across reopens, matching the picker's draft-revert-on-reopen convention

---

#### TC-25: Footer range summary — `basic` shows days only

**Priority:** P1

**Playground:** `dp-banner-s3` (basic + range)

**Steps:**

1. Under `calendarType="basic"` + `range`, select and Apply a multi-day range, then reopen
   **Expected:** The footer shows a days-only summary aligned against the Clean/Cancel/Apply row, computed as raw elapsed time between the committed start/end instants (e.g. a Sept 1 → Sept 18 range, both at 00:00, is 17 elapsed days — not an inclusive calendar-day count; see `computeRangeDuration`'s own JSDoc)

---

#### TC-26: Footer range summary — `expanded` shows days/hours/minutes, with correct pluralization

**Priority:** P1

**Playground:** `dp-banner-s4` (expanded + range + withTime)

**Steps:**

1. Under `calendarType="expanded"` + `range` + `with-time`, select a range with distinct, non-`00:00` start/end times, Apply, then reopen
   **Expected:** The footer shows a days/hours/minutes summary reflecting raw elapsed time between the committed start/end instants (e.g. Sept 1 10:00 → Sept 18 12:30 is "17 days, 2 hours, 30 minutes")
2. Select a range that resolves to exactly 1 day, 1 hour, and 1 minute
   **Expected:** Each unit renders in its singular form ("1 day, 1 hour, 1 minute"), confirming `Intl.PluralRules`-based singular/plural selection works correctly at the boundary

---

### Month/year quick-picker

---

#### TC-27: Quick-picker overlay superposes over the (dimmed) day grid with its own nested header

**Priority:** P1

**Playground:** `dp-quickpicker-s1` (basic, single date)

**Steps:**

1. Click the month/year header label on `dp-quickpicker-s1` (single-date)
   **Expected:** A white, elevated card with a connector arrow toward the label opens superposed over the day grid; the day grid stays visible underneath, dimmed (~40% opacity), not removed
2. While the month picker is open, inspect the outer (day-grid) header
   **Expected:** The outer header (label + prev/next month buttons) is also dimmed, and the picker card shows its own separate inner header (prev/next-year buttons + year label) — two visually distinct header rows, not one swapped for the other
3. Click the year label inside the picker's own header
   **Expected:** The month grid is replaced by a year grid (12-year window), current year flagged; the outer day-grid header remains dimmed throughout
4. Click a year, then a month
   **Expected:** Drills back down (year → month grid for that year → day grid), outer header and day grid un-dim and return to normal interactivity once back on day view

---

#### TC-28: Drill-down click path — single and `expanded` dual-grid independence

**Priority:** P0

**Playground:** `dp-quickpicker-s1` (step 1), `dp-quickpicker-s2` (step 2), `dp-quickpicker-s3` (step 3), `dp-quickpicker-s4` (step 4)

**Steps:**

1. On `dp-quickpicker-s1`, click a month in the open month picker
   **Expected:** Returns to day view showing that month; `bdsMonthNavigate` fires with the correct target
2. On `dp-quickpicker-s2` (`expanded` + `range`), open the **left** grid's month picker only
   **Expected:** The right grid's day grid is completely unaffected — no dimming, no `aria-hidden`/`inert`, still fully interactive
3. On `dp-quickpicker-s3` (bounded `min`/`max`), open the month and year pickers
   **Expected:** Months/years entirely outside the bounds are disabled and unclickable; partially-in-range ones stay enabled; no "future is disabled" behavior
4. On `dp-quickpicker-s4` (`expanded`), pick a month from the **right** calendar's own month picker
   **Expected:** The picked month appears in the right calendar specifically (left anchors to picked − 1) — the clicked calendar shows the picked month, not the other one

---

#### TC-29: Selected-date and range-boundary highlighting in the quick-picker

**Priority:** P1

**Playground:** `dp-quickpicker-s1` (steps 1-2), `dp-quickpicker-s2` (steps 3-4)

**Steps:**

1. Select a single date (e.g. Sept 15), then open the month picker
   **Expected:** Exactly that date's month shows a solid `--selected` highlight; no other month does
2. Navigate the day grid forward/back to a different month (without selecting a new date), then open the month picker
   **Expected:** The originally *selected* month stays highlighted — not whichever month is currently displayed — confirming selection-based, not display-position-based, semantics
3. On `dp-quickpicker-s2`, select a range with both endpoints in the same year (e.g. Mar 10 – Sep 20), open either grid's month picker
   **Expected:** Both March and September show `--selected` independently; no highlight on the months between them (no spanning "in-range" treatment); both grids show identical flagging since they share the same range
4. Select a range spanning two different years, open a month picker showing only one of those years
   **Expected:** Only the boundary that falls in the currently-displayed year is highlighted; navigate the picker to the other year and the other boundary lights up there instead
5. With no date selected yet, open the month or year picker
   **Expected:** No cell shows `--selected` (only `--current`/today, if applicable) — no false-positive highlight

---

#### TC-30: Quick-picker auto-closes and resyncs on preset, Clear, and cross-grid actions

**Priority:** P1

**Playground:** `dp-quickpicker-s1` or `s2` (steps 1-2), `dp-quickpicker-s2` (steps 3-4)

**Steps:**

1. Open a quick-picker (month or year view), then click a sidebar preset (e.g. "Last 7 days")
   **Expected:** The picker closes back to day view immediately and the day grid reflects the preset's range — no stale overlay left showing unrelated context
2. Reopen a quick-picker, then click the footer "Clear" button
   **Expected:** The picker closes back to day view; the day grid shows the cleared state
3. On `dp-quickpicker-s2`, open the left grid's quick-picker, then click a day on the right grid to make a range selection
   **Expected:** The left grid's quick-picker closes back to day view once the right-grid click completes
4. On `dp-quickpicker-s2`, open **both** grids' quick-pickers simultaneously (open one, then separately open the other), then complete a month or year pick in one of them
   **Expected:** The other grid's quick-picker also closes back to day view — no stale overlay left open on it, even though its own navigation had nothing to do with the pick

---

#### TC-31: Quick-picker keyboard navigation, Escape, backdrop-click dismissal, and live-region announcements

**Priority:** P1

**Playground:** `dp-quickpicker-s1` (single-date; keyboard-only path) and `dp-quickpicker-s2` (expanded range), reusing the scenarios above

**Steps:**

1. Tab to the month/year header label (no mouse), activate with Enter/Space
   **Expected:** The month picker opens as an overlay above the dimmed day grid, identical to a mouse click; the label's accessible name describes its function (e.g. "September 2026, choose month")
2. With the month or year grid focused, use arrow keys and Home/End
   **Expected:** Focus moves cell-to-cell following the same interaction model as the day grid (Task 40); no focus loss, no keyboard trap; a live region announces each view transition (entering month view, entering year view, returning to day view) exactly once, with no duplicate when a selection also triggers `bdsMonthNavigate`
3. With a picker view open, press Escape
   **Expected:** Returns to day view without closing the whole popover (distinct from Escape from day view, which still closes the popover per Task 42); real DOM focus lands on a sensible cell in the day grid, not dropped to `<body>`
4. With a picker view open, click the dimmed backdrop area outside the picker card
   **Expected:** Same result as Escape — returns to day view without closing the popover; clicking inside the card itself has no such effect
5. Complete a full keyboard-only drill-down cycle (Tab to label → Enter → arrow to a month → Enter → back on day view)
   **Expected:** Matches the mouse-driven cycle exactly at every step, with correct final focus

---

#### TC-32: Quick-picker PageUp/PageDown paging and year-window focus retention

**Priority:** P1

**Playground:** `dp-quickpicker-s1` (steps 1-2), `dp-quickpicker-s3` (step 3), `dp-quickpicker-s2` (step 6)

**Steps:**

1. On `dp-quickpicker-s1`, open the month picker and note the inner year label (e.g. "2026")
   **Expected:** Pressing PageDown advances the year by one (the 12 month cells re-render for that year) and PageUp steps back by one — the same result as the picker's own prev/next-year header buttons; no `bdsMonthNavigate` is emitted for picker paging
2. From the month view, click the year button to open the year grid
   **Expected:** PageDown advances the 12-year window by a decade (window label `startYear – startYear+11` → +10) and PageUp steps back −10, matching the header's prev/next-years buttons
3. On `dp-quickpicker-s3` (`min="2026-06-01" max="2027-03-31"`), page toward a fully out-of-range year or decade window
   **Expected:** The key no-ops — the year/window label does not change, matching the disabled header buttons; a partially-in-range year still pages
4. In the year grid, focus a year cell (arrow to it), then press PageDown
   **Expected:** The window advances and `document.activeElement` is a **year cell in the new window** (not `<body>`) — the previously focused year advanced by the same delta where still in-window and enabled. Pressing PageDown again immediately still pages (focus was retained by the first press); PageUp steps back with focus retained each time
5. With the picker closed (day view), press PageUp/PageDown
   **Expected:** The day grid still navigates prev/next month and emits `bdsMonthNavigate` — unchanged (regression)
6. On `dp-quickpicker-s2` (`expanded`), open one grid's picker and page
   **Expected:** Only that grid's picker pages; the other grid is unaffected

---

#### TC-33: Day-grid arrow-key traversal (2D keyboard navigation)

**Priority:** P1

**Playground:** `dp-keyboard-s1` (steps 1-2), `dp-keyboard-s2` (step 3), `dp-keyboard-s3` (step 4)

**Steps:**

1. On `dp-keyboard-s1` (`default`, single-date), Tab into the field, then Tab again into the calendar grid
   **Expected:** Tab enters the grid once (roving tabindex — a single `tabindex="0"` cell); arrow keys / Home / End move focus cell-to-cell per the ARIA APG date-grid pattern, wrapping within the visible month, with no focus loss and disabled/out-of-month cells skipped
2. On the same picker, traverse across a month boundary with PageUp/PageDown
   **Expected:** `bdsMonthNavigate` fires and the grid re-renders the new month with focus landing on the correct cell
3. On `dp-keyboard-s2` (`expanded` + `range`), Tab into each grid in turn and traverse
   **Expected:** Each grid's focus/traversal state is fully independent — no shared/leaking focus state between the two instances
4. On `dp-keyboard-s3` (`min`/`max` narrowing part of the month), traverse near the disabled boundary
   **Expected:** Disabled and out-of-month cells are never a focus stop — traversal skips over them entirely

---

## Test Deliverables

- This document
- Bug reports per defect: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
- Update **Pass?** status inline after each test run

---

## Verification (how to run)

1. `fnm use && pnpm dev:components` from the monorepo root
2. Open `packages/boreal-web-components/src/index.html` — each TC above names the playground element id (**Playground:** field) it maps to
3. Execute in order: **Part 1** — Range-mode time selection → Presets selection/computation → Presets bounds/timezone → Presets coverage/navigation → Idempotency → Presets reopen/Cancel correctness → `expanded`+`range=false` → Same-day intraday ranges → Reverse-order range click → Hover-preview/first-click highlight → Preselected date outside visible month; **Part 2** — Info banner and footer range summary → Month/year quick-picker → Quick-picker keyboard/paging → Day-grid arrow-key traversal
4. Log defects: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
