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
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderPresets.tsx`, `renderTimeSelector.tsx`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx`
- `packages/boreal-web-components/src/services/date-engine/grid.ts`

Brand theme in scope: **Proximus only** (consistent with v1/v2 plans).
Created: 2026-09-14
Updated: 2026-09-22 — added TC-14 through TC-22 (presets reopen/Cancel/shift correctness, `expanded`+`range=false` warnings, same-day intraday ranges, reverse-order click, bidirectional hover-preview, preselected-date-outside-month confirmation); removed the multi-month preselected-range playground scenario (now a documented, intentional limitation with no dedicated test case — see Out of scope). Added TC-23 through TC-26 (info banner positioning/dismissal, footer range-summary text and pluralization).

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

**Out of scope:**

- v1/v2 baseline behavior (single-date, `withTime`, `min`/`max`, `calendarType`, range core selection) — already covered by prior plans, not duplicated here.
- Keyboard/arrow-key grid navigation and RTL, month/year quick-picker — not yet implemented on this branch.
- Banner `state`/`variant` visual styling per severity (info/success/warning/danger) — the type is flexible but visual styling per state is pulled from Figma in a later SCSS-audit task, not tested here.
- Consumer-configurable presets — not implemented; the preset list is fixed.
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

### Range-mode time selection

---

#### TC-01: `basic` + range + withTime — single shared time applies to both bounds

**Priority:** P0

**Steps:**

1. Open a `calendar-type="basic" range with-time` picker, pick a start day and end day, set one shared hour/minute, click Apply
   **Expected:** Logged `bdsChange` `{ start, end }` share identical `HH:mm` but differ in date

---

#### TC-02: `expanded` + range + withTime — independent start/end time

**Priority:** P0

**Steps:**

1. Open a `calendar-type="expanded" range with-time` picker, pick a start date/time and end date/time with different hour/minute values, click Apply
   **Expected:** Logged `{ start, end }` UTC strings differ in time-of-day, not just date

---

#### TC-03: Single-date `withTime` regression

**Priority:** P1

**Steps:**

1. On a non-range `with-time` picker, pick a day + time, click Apply
   **Expected:** Logged value is a single full UTC ISO string, unchanged from prior behavior

---

#### TC-04: Popover header shows time in both layouts

**Priority:** P1

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

**Steps:**

1. On both `expanded` + range and `basic` + range pickers, click each of the six presets in turn
   **Expected:** Calendar highlights the correct real days for each (Today = 1 day; Last 7/30 days include today; This month = 1st through today; Last month = full previous month); clicked preset shows selected; "Custom" is selected by default before any preset is clicked

---

#### TC-06: Manual edit after a preset reverts selection to Custom

**Priority:** P0

**Steps:**

1. Click a preset, then manually click a calendar day
   **Expected:** Selection reverts to "Custom"; the day click still applies normally
2. Click a preset, then manually change a time selector value
   **Expected:** Selection reverts to "Custom"; the time change is preserved (not discarded)

---

#### TC-07: Clicking "Custom" directly does not clear the selection

**Priority:** P2

**Steps:**

1. With a preset (or a manual range) already selected, click "Custom" directly
   **Expected:** The current draft selection is left untouched — only the footer's Clean/Clear action clears it

---

### Presets sidebar — bounds & timezone

---

#### TC-08: `min`/`max` disables out-of-bounds presets

**Priority:** P1

**Steps:**

1. Open a picker with `min`/`max` set so some presets' ranges fall partially or fully outside the bounds
   **Expected:** Any preset whose computed range falls even partially outside `min`/`max` renders disabled and does nothing when clicked; presets fully inside the bounds stay clickable

---

#### TC-09: "Today" reflects configured `timezone`, not the device clock

**Priority:** P1

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

**Steps:**

1. On `expanded` + range + `with-time`, click a preset (e.g. Last 7 days), note the header, then click Apply
   **Expected:** Popover header's `End:` (before Apply) shows the coverage boundary shifted one day past the last real day, at `00:00`; the calendar still highlights only the real days; after Apply, the trigger field's text and the logged `bdsChange` `end` value both match that same boundary exactly

---

#### TC-11: Preset click auto-navigates the calendar view

**Priority:** P1

**Steps:**

1. On `basic` + range, navigate 2+ months forward, then click a preset whose range isn't in the currently-shown month
   **Expected:** View jumps to the preset's start month with correct days highlighted, no manual navigation needed
2. On `expanded` + range, click a preset spanning two calendar months
   **Expected:** Calendar 1 shows the start month, calendar 2 automatically shows the following month, together covering the full range

---

#### TC-12: Re-anchoring after reverting to Custom

**Priority:** P2

**Steps:**

1. Click a preset, manually click a calendar day (reverting to Custom), then click a different preset
   **Expected:** View re-anchors correctly to the new preset's start month — no stale display month left over

---

### Idempotency

---

#### TC-13: Repeated preset click / trigger toggle produces no duplicate side effects

**Priority:** P2

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

**Steps:**

1. Apply a built-in preset (e.g. "Today"), close the popover, then reopen it
   **Expected:** The sidebar shows that same preset selected again — not "Custom" — verified via the selected item's own class, not just a visual glance
2. Apply a manually-selected range that doesn't match any built-in preset, close, then reopen
   **Expected:** The sidebar correctly shows "Custom" (no false-positive match)

---

#### TC-15: Presets sidebar re-matches on Cancel, with no visible flash of the wrong state

**Priority:** P1

**Steps:**

1. Apply a preset, reopen the popover, then click Cancel
   **Expected:** The sidebar shows the correct preset selected immediately after Cancel — not "Custom" — checked before any reopen
2. Reopen the popover again after Cancel
   **Expected:** No visible flash of "Custom" before the correct preset appears — the sidebar is already correct from the first rendered frame

---

#### TC-16: Reopening a with-time preset shows the real day(s) only, with no header double-shift or value drift

**Priority:** P0

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

**Steps:**

1. Open a `calendar-type="expanded"` picker with `range` not set and `with-time` set
   **Expected:** The console logs exactly two `[bds-date-picker]` warnings, once each — one noting `expanded` renders two calendars but only a single date can be selected without `range`, one noting `with-time` falls back to a single shared time selector without `range`

---

#### TC-18: No duplicate day-highlight at a month boundary under `expanded` + `range=false`

**Priority:** P1

**Steps:**

1. On the same picker, set `value` to a date that also appears as a leading filler day in the adjacent calendar's grid (e.g. the last day of a month)
   **Expected:** The selected date is highlighted in exactly one calendar — its real month — not in both

---

### Same-day intraday ranges

---

#### TC-19: Same-day double-click confirms a one-day range; an inverted end time shifts live, consistently across Apply and reopen

**Priority:** P0

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

**Steps:**

1. Set `value` on a fresh (never-opened) picker to a date several months from today, then click the field to open the popover for the first time
   **Expected:** The calendar opens already showing the preselected date's month — not today's month — with no manual navigation needed to reach it

---

### Info banner and footer range summary

---

#### TC-23: Banner renders correctly positioned in all `calendarType` values, including `default`

**Priority:** P1

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

**Steps:**

1. With a visible, closable banner, click the close ("X") button
   **Expected:** The banner dismisses (no longer renders), no console errors
2. Close the popover, then reopen it
   **Expected:** The banner re-appears — a same-session dismissal is not remembered across reopens, matching the picker's draft-revert-on-reopen convention

---

#### TC-25: Footer range summary — `basic` shows days only

**Priority:** P1

**Steps:**

1. Under `calendarType="basic"` + `range`, select and Apply a multi-day range, then reopen
   **Expected:** The footer shows a days-only summary aligned against the Clean/Cancel/Apply row, computed as raw elapsed time between the committed start/end instants (e.g. a Sept 1 → Sept 18 range, both at 00:00, is 17 elapsed days — not an inclusive calendar-day count; see `computeRangeDuration`'s own JSDoc)

---

#### TC-26: Footer range summary — `expanded` shows days/hours/minutes, with correct pluralization

**Priority:** P1

**Steps:**

1. Under `calendarType="expanded"` + `range` + `with-time`, select a range with distinct, non-`00:00` start/end times, Apply, then reopen
   **Expected:** The footer shows a days/hours/minutes summary reflecting raw elapsed time between the committed start/end instants (e.g. Sept 1 10:00 → Sept 18 12:30 is "17 days, 2 hours, 30 minutes")
2. Select a range that resolves to exactly 1 day, 1 hour, and 1 minute
   **Expected:** Each unit renders in its singular form ("1 day, 1 hour, 1 minute"), confirming `Intl.PluralRules`-based singular/plural selection works correctly at the boundary

---

## Test Deliverables

- This document
- Bug reports per defect: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
- Update **Pass?** status inline after each test run

---

## Verification (how to run)

1. `fnm use && pnpm dev:components` from the monorepo root
2. Open `packages/boreal-web-components/src/index.html` — each TC above maps to a labeled section with matching scenario IDs
3. Execute in order: Range-mode time selection → Presets selection/computation → Presets bounds/timezone → Presets coverage/navigation → Idempotency → Presets reopen/Cancel correctness → `expanded`+`range=false` → Same-day intraday ranges → Reverse-order range click → Hover-preview/first-click highlight → Preselected date outside visible month → Info banner and footer range summary
4. Log defects: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
