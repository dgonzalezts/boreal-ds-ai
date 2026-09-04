# Test Plan: `bds-date-picker` Component (Phase 2–4, v2)

## Context

`bds-date-picker` is a composite, form-associated (FACE) date-picker control composing a **consumer-supplied** `bds-text-field` trigger (slotted, not self-rendered) with a `bds-popover` panel containing one or two `bds-calendar-grid` bodies and a Clean/Cancel/Apply footer. Selection is held in internal draft state until Apply — day clicks and month navigation never touch the public `value` until the user explicitly commits.

This plan covers **Phase 2 through Phase 4 only** (`EOA-17138-bds-date-picker-v2.md`, now `done`), on top of the Phase 0–1 baseline already covered by `EOA-16692-bds-date-picker-test-plan.md` (not re-tested here except where a v2 change touches shared code):

- **Phase 2** — `withTime`: hour/minute selection, UTC-normalized `value` contract, timezone conversion, `format` auto-switch/override.
- **Phase 3** — `min`/`max` date constraints: disabled out-of-range days, whole-month nav guard, `rangeUnderflow`/`rangeOverflow` form validation.
- **Phase 3.5** — `calendarType: 'default' | 'basic' | 'expanded'`: `default`'s immediate-commit/no-chrome interaction model.
- **Phase 4** — `range: boolean`: dual-calendar (`expanded`) vs. single-calendar (`basic`) range selection, `{ start, end }` value contract, range day-state visuals (two-layer cap geometry, committed/hover/preview states), consecutive-month nav lock, and a set of interaction-correctness fixes discovered during this phase's own QA (Clean-stays-open, the `validation-timing="submit"` requirement, the today-indicator clipping fix, and a Safari/WebKit-only Apply-button regression).

Component sources:

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx`
- `packages/boreal-web-components/src/services/date-engine/` (`value.ts`, `date-math.ts`, `grid.ts`)
- `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` (Task 19r's fix lives here, not in `bds-date-picker` itself, but is only reachable through this component's Apply flow)

Brand theme in scope: **Proximus only** (matches v1's plan; not re-litigated here).
Created: 2026-09-03

---

## Scope

**In scope:**

- Time selector (`withTime`): hour/minute UI, UTC value conversion round-trip, timezone-dependent conversion, `format` auto-switch vs. explicit override, default-time (`00:00`) behavior, stale/malformed value handling.
- `min`/`max`: disabled out-of-range days, whole-month nav guard (Previous/Next disabled when the adjacent month is entirely out of range), `rangeUnderflow`/`rangeOverflow` form validation and error messaging, initial-mount FACE-validity race (Task 15a fix).
- `calendarType`: `default`'s immediate-commit-and-close/no-chrome interaction model, `withTime`/`range` no-ops under `default`, required-field validation parity with `basic`.
- `range`: `{ start, end }` value contract under both `basic` (single calendar) and `expanded` (dual calendar); dual-calendar consecutive-month nav lock; range day-state rendering (two-layer `Bkgd`/`Selected` cap geometry, committed hover states, live hover-preview band); range FACE validity and native `<form>` serialization (`${start},${end}`); Clean-stays-open vs. Cancel-closes in range mode; the `basic` (plain dash-joined) vs. `expanded` (labeled `Start:`/`End:`) header-format split; no duplicate range band across an `expanded` month boundary; narrow `min`–`max` window warning for `expanded`+`range`.
- Cross-cutting fixes discovered during Phase 4 QA that affect **every** `bds-date-picker` configuration, not just range: the today-indicator dashed-border clipping fix (Task 19p), the `required` + `validation-timing="submit"` requirement (Task 19o), and the Safari/WebKit-only popover Apply-button regression (Task 19r).
- Visual / Figma validation for the new range day-state geometry and hover states.
- Regression smoke suite covering v1 behavior alongside every v2 addition.

**Out of scope:**

- Phase 0–1 (single-date baseline) test cases already covered by `EOA-16692-bds-date-picker-test-plan.md` — not duplicated here except where a v2 change (e.g. Task 19r, Task 19p) touches shared code and needs a regression check.
- Phase 5–9 (range time, presets, banner/summary, keyboard/a11y grid navigation, month/year quick-picker) — tracked separately under `EOA-17662-bds-date-picker-v3.md`, not yet implemented.
- Keyboard-typed date entry into the trigger field — deferred, unscheduled, not implemented in any phase to date.
- `bds-text-field`, `bds-popover`, `bds-button`, `bds-select` internals — covered by their own plans; this plan only tests the *composition* contract between them and `bds-date-picker`, plus the one popover-internal fix (Task 19r) whose only symptom surfaces through this component.
- React/Vue wrapper parity — already covered by the parent plan's own Task 20 (`✅ done`, re-verified on real Safari.app); not duplicated here.
- Automated e2e tests (manual execution only).
- `bds-popover`'s own coverage backfill and the CSS custom-property-inheritance browser regression test — both re-scoped into their own dedicated plans (`bds-popover-coverage-backfill.md`, `bds-popover-css-custom-property-inheritance-browser-test.md`), not part of this component-level plan.

---

## Environment

- **Storybook documentation exists** (Task 22, `bds-date-picker.stories.ts`/`.mdx`) — prefer it once verifying against a built Storybook (`pnpm build:storybook` or Chromatic) is convenient; otherwise the local dev-server playground remains the primary environment for this plan, since it already carries every scenario below as a dedicated, labeled section:
  ```bash
  fnm use && pnpm dev:components
  ```
  from the monorepo root, opening `packages/boreal-web-components/src/index.html`.
- Browser: Chrome (latest stable) primary. **Safari/WebKit is mandatory for any Apply-flow scenario** (range value emission, Clean/Cancel/field-clear, required-range form submit, hover-preview commit) — Task 19r's regression was invisible to Playwright-WebKit across every automated re-run and only ever reproduced on real Safari.app. Firefox as a secondary spot-check.
- DevTools: open for console warnings/errors, computed-style checks (range day-state geometry), and `FormData`/event console logging (every scenario below wires a `bdsChange` listener and/or a form-submit console log).
- Real system clock matters for two scenarios (Task 19m-1's display-month fallback, Task 19m-3's "excludes today's month" case) — note the actual test date when running them, since expected behavior is defined relative to "today," not a fixed date.

## Entry Criteria

- [ ] `bds-date-picker`/`bds-calendar-grid` render without console errors in the playground
- [ ] Dev server running locally on `feature/EOA-17138_bds-date-picker-v2_DG` (or `main`/`release/current` once merged)
- [ ] DevTools accessibility panel available (Chrome ≥ 120)
- [ ] Real Safari.app available (not just Playwright-WebKit) for Apply-flow scenarios

## Exit Criteria

- [ ] All P0 test cases pass, on both Chrome and Safari where the case is Apply-flow-relevant
- [ ] ≥ 90% of P1 test cases pass
- [ ] All Figma visual discrepancies documented
- [ ] All ARIA failures logged as bugs
- [ ] No open P0 bugs

---

## Risk Assessment

| Risk                                                                                          | Probability | Impact | Mitigation                                                                                                    |
| ----------------------------------------------------------------------------------------------- | ----------- | ------ | ----------------------------------------------------------------------------------------------------------------- |
| Safari/WebKit-only regressions invisible to Chrome and to Playwright-WebKit automation          | M           | H      | Every Apply-flow test case below is explicitly flagged for real-Safari execution, matching Task 19r's precedent  |
| Range day-state CSS regresses to the pre-Task-19i pseudo-element technique or reintroduces a seam/clip at cap boundaries | L           | M      | TC-UI-1xx pins exact `.day-background`/`.day-cap` geometry and hover/focus paint order, not just visual impression |
| `calendarType="default"` silently re-enables `withTime`/`range` chrome instead of no-op'ing them | L           | M      | TC-FUNC-3xx explicitly re-confirms both no-ops, not just the base click-commit flow                            |
| A `required` picker shows a premature invalid flash without `validation-timing="submit"` set on the slotted field | M           | M      | TC-FUNC-5xx tests this exact trap directly, matching Task 19o's discovery                                       |
| `expanded`+`range`'s two calendars drift out of consecutive months after repeated nav clicks    | L           | H      | TC-FUNC-4xx exercises the nav lock through several clicks in both directions, not just the initial mount state  |
| Narrow `min`–`max` window under `expanded`+`range` produces a total dead end (both calendars disabled) | L           | H      | TC-FUNC-4xx explicitly confirms at least one calendar stays navigable                                          |
| Timezone conversion silently drifts by one day at a DST boundary                                | L           | H      | TC-FUNC-1xx reuses the plan's own DST-boundary-aware scenarios (Tokyo vs. Los Angeles), not a single naive check |

---

## Test Cases

### Functional — Time selector (Phase 2)

---

#### TC-FUNC-101: `withTime` basic Apply commits a UTC ISO string

**Priority:** P0

**Preconditions:**

- [ ] `<bds-date-picker with-time timezone="UTC">` with a slotted field, `bdsChange` logged to console

**Steps:**

1. Open the popover, pick a day, set an hour/minute, click Apply
   **Expected:** Popover closes; console logs a UTC ISO string (e.g. `2026-09-14T00:00:00.000+00:00`); trigger field shows the formatted date + time

---

#### TC-FUNC-102: Timezone conversion — same wall-clock time, different UTC value

**Priority:** P0

**Steps:**

1. On a `timezone="Asia/Tokyo"` picker and a `timezone="America/Los_Angeles"` picker, pick the same day and the same wall-clock hour/minute on both, Apply each
   **Expected:** The logged UTC `bdsChange` values differ between the two, correctly reflecting each zone's UTC offset (verify against the zone's real offset for that date, including DST if applicable for LA)

---

#### TC-FUNC-103: Pre-loaded value opens with the correct day/time selected

**Priority:** P1

**Steps:**

1. Reload a picker with a pre-set UTC ISO `value`, open the popover
   **Expected:** The correct day is pre-highlighted and the hour/minute selects show the correct pre-converted wall-clock time for that picker's `timezone`

---

#### TC-FUNC-104: `format` auto-switch vs. explicit override

**Priority:** P1

**Steps:**

1. On a picker with `with-time` and no explicit `format`, open it
   **Expected:** Trigger + popover header show `HH:mm` alongside the date (auto-switched default)
2. On a picker with `with-time` and an explicit `format="MM/dd/yyyy HH:mm"`
   **Expected:** Shows exactly that format, not the auto-switched default — an explicit format always wins, even when functionally similar to the default

---

#### TC-FUNC-105: Fresh picker defaults time selects to `00:00`

**Priority:** P1

**Steps:**

1. Open a `with-time` picker with no initial `value`, pick a day without touching the hour/minute selects, click Apply
   **Expected:** Apply is not blocked; the committed time is `00:00`

---

#### TC-FUNC-106: Stale naive `value` with `withTime` — no console error

**Priority:** P1

**Steps:**

1. Reload a `with-time` picker whose `value` is a bare naive date (`"2026-08-24"`, not a UTC ISO string)
   **Expected:** No console error on open; time selects default to `00:00`

---

### Functional — Min/max constraints (Phase 3)

---

#### TC-FUNC-201: Out-of-range days are disabled and unclickable

**Priority:** P0

**Steps:**

1. Open a picker with `min`/`max` set to a mid-month window
   **Expected:** Days before `min` and after `max` render dimmed/disabled and do not respond to click; days within the window render normally and are selectable

---

#### TC-FUNC-202: Whole-month nav guard

**Priority:** P0

**Steps:**

1. Open a picker whose `min`/`max` both fall within the current month, navigate to the next month
   **Expected:** "Next month" is disabled (the following month is entirely out of range); same check for "Previous month" toward the prior, entirely-out-of-range month

---

#### TC-FUNC-203: Stale out-of-range value blocks form submission

**Priority:** P0

**Steps:**

1. On a `required`-adjacent form with a picker pre-loaded with a `value` below `min`, click Submit without changing anything
   **Expected:** The slotted field shows an invalid state with an error message; the form does not submit (no "form submitted" console log)

---

#### TC-FUNC-204: Initial-mount FACE-validity race (Task 15a regression guard)

**Priority:** P1

**Steps:**

1. In React specifically (the framework where this race originally reproduced), mount a picker with a stale out-of-range `value` and call `checkValidity()` immediately on load, before any interaction
   **Expected:** Returns `false` immediately — not just after a later prop change or interaction

---

### Functional — `calendarType` (Phase 3.5)

---

#### TC-FUNC-301: `default` type — click commits immediately, no chrome

**Priority:** P0

**Steps:**

1. Open a `calendar-type="default"` picker and click any enabled day
   **Expected:** Popover closes immediately (no Apply click needed); the field's value updates to the clicked day
2. Re-open the same picker
   **Expected:** No header (icon/title), no close (✕) button, and no footer (Clean/Cancel/Apply) render at any point while open
3. Re-open again, click outside the popover
   **Expected:** Popover dismisses; value is unchanged from before the click-outside

---

#### TC-FUNC-302: `default` + `withTime`/`range` — silent no-ops

**Priority:** P1

**Steps:**

1. Open a `calendar-type="default" with-time` picker
   **Expected:** Renders a single bare calendar — no hour/minute selects, no dual calendar; clicking a day still commits and closes immediately, exactly like a plain `default` picker
2. Repeat with `calendar-type="default" range` set
   **Expected:** Same — `range` has no visible effect under `default`; a single day click commits a plain single-date value, not a range

---

#### TC-FUNC-303: `default` + `required` — validation parity with `basic`

**Priority:** P1

**Steps:**

1. Submit a form containing a `calendar-type="default" required` picker with no value selected
   **Expected:** The slotted field shows an invalid state with an error message, visually identical to `basic`-mode's own required-field error; form does not submit

---

#### TC-FUNC-304: `default` + `withTime` + `min`/`max` — validation still fires

**Priority:** P1

**Steps:**

1. Submit a form containing a `calendar-type="default" with-time` picker pre-loaded with a value below `min`, without changing anything
   **Expected:** `rangeUnderflow` fires correctly — invalid state + error message, form does not submit (regression guard: this previously stayed silently inert because internal branching keyed off raw `withTime` instead of an effective value forced `false` under `default`)

---

### Functional — Range core (Phase 4)

---

#### TC-FUNC-401: Range value emission — `basic` and `expanded`

**Priority:** P0
**Browser:** Chrome + **Safari** (Apply-flow)

**Steps:**

1. On an `expanded`+`range` picker, click a start day then an end day after it
   **Expected:** Header shows the labeled `Start: ... End: ...` structure; day cells in both calendars carry the correct range-state classes
2. Repeat the same two clicks on a `basic`+`range` picker (single calendar)
   **Expected:** Header shows a plain dash-joined string (`"2026/09/10 – 2026/09/15"`) with **no** `Start:`/`End:` labels — this is a deliberate, permanent split between the two calendar types, not a bug if `basic` looks different from `expanded`
3. Click a day before the current start on either picker
   **Expected:** That day becomes the new start; the previous end clears (swap-to-fresh-selection behavior)
4. Click Apply on each
   **Expected:** Console logs a `bdsChange` detail shaped `{ start, end }` with correct ISO dates, identical shape in both `calendarType` modes

---

#### TC-FUNC-402: Range regression — plain single-date picker unaffected

**Priority:** P0

**Steps:**

1. On a picker with `range` unset, exercise day click, Apply, Cancel, and Clean
   **Expected:** All behave exactly as a v1 single-date picker — `value` stays a plain string, never `{ start, end }`

---

#### TC-FUNC-403: Range day-state rendering in isolation (`bds-calendar-grid`)

**Priority:** P1

**Steps:**

1. On a standalone `bds-calendar-grid` driven by mock `DayCell` flags, mark one day range-start, several in-range, one range-end
   **Expected:** The three class modifiers (`--range-start`, `--in-range`, `--range-end`) appear on exactly the intended cells, no new DOM elements, no ARIA changes
2. Clear the flags
   **Expected:** Classes removed; day click and month nav continue to work normally

---

#### TC-FUNC-404: Range FACE validity and native form submission

**Priority:** P0

**Steps:**

1. With nothing selected on a `required range` picker, call `checkValidity()`
   **Expected:** Returns `false`
2. Apply a valid range (two clicks + Apply)
   **Expected:** `checkValidity()` now returns `true`; invalid-state styling clears
3. Submit the containing form
   **Expected:** The logged `FormData` entry for this picker's `name` is a single comma-delimited string (`"<start>,<end>"`, e.g. `"2026-08-10,2026-08-15"`)
4. Regression: repeat 1–3 on a `required`, non-range picker in the same form
   **Expected:** `checkValidity()`/submission behavior unchanged from v1 — a plain ISO date string, not comma-delimited

---

#### TC-FUNC-405: Dual-calendar consecutive-month nav lock

**Priority:** P0
**Browser:** Chrome + **Safari** (Apply-flow at the end)

**Steps:**

1. Open an `expanded`+`range` picker
   **Expected:** First (left) calendar's "Next month" and second (right) calendar's "Previous month" are both disabled from the start
2. Click the first calendar's "Previous month" 3–4 times
   **Expected:** Both calendars move back together, staying exactly one month apart at every step
3. Click the second calendar's "Next month" 3–4 times
   **Expected:** Both calendars move forward together, staying exactly one month apart at every step
4. With a `min`/`max` window set, navigate toward each bound
   **Expected:** The two live buttons correctly disable exactly at the `min`/`max` bound
5. Click a start day on the first calendar and an end day on the second, click Apply
   **Expected:** Range renders correctly across both calendars; value commits; popover closes

---

#### TC-FUNC-406: Narrow `min`–`max` window — no dead end, one-time warning

**Priority:** P1

**Steps:**

1. Hard-reload a page with an `expanded`+`range` picker whose `min`/`max` span fewer than 2 calendar months
   **Expected:** Console logs exactly one `[bds-date-picker]` warning on mount; the warning does not re-fire on later interaction
2. Confirm the same narrow window under `basic` (no `range`) and under `expanded` without `range`
   **Expected:** No such warning in either case
3. Confirm an `expanded`+`range` picker with a window ≥ 2 months wide
   **Expected:** No warning
4. On the narrow-window picker, confirm at least one calendar remains selectable/navigable
   **Expected:** Not a complete dead end — the calendar containing the valid month stays usable, even though the other stays permanently disabled

---

#### TC-FUNC-407: Wide window excluding today's real month

**Priority:** P2

**Steps:**

1. Open an `expanded`+`range` picker whose `min`–`max` window is 3 calendar months wide but excludes the real current month
   **Expected:** Opens directly on a valid, selectable consecutive pair of months within the window — not a disabled month requiring manual recovery

---

### Functional — Range interaction refinements

---

#### TC-FUNC-501: Clean stays open, Cancel/Apply still close — single date and range

**Priority:** P0
**Browser:** Chrome + **Safari**

**Steps:**

1. Single-date: select a day, click Clean
   **Expected:** Popover stays open, field clears immediately, a new day can be picked right away without reopening
2. Range (`basic` and `expanded`): select a start (and optionally end) date, click Clean
   **Expected:** Popover stays open with both endpoints cleared; hovering/selecting a fresh range immediately afterward shows no stale preview band flash
3. Cancel/Apply regression, all pickers above
   **Expected:** Both still close the popover as before
4. Slotted field's own clear (✕) button: Apply a value, then click the field's own clear icon (not the footer)
   **Expected:** Value clears immediately; if the popover is reopened first, clicking the field's clear icon leaves the popover open, exactly like the footer's Clean action

---

#### TC-FUNC-502: `validation-timing="submit"` requirement for `required` pickers

**Priority:** P0

**Steps:**

1. On a `required` picker (`calendarType="default"` is the scenario that originally surfaced this) **without** `validation-timing="submit"` set on the slotted field, click a day mid-selection
   **Expected:** A transient invalid flash appears on the field before any submit attempt — this is the bug, reproduce it once to confirm the trap is real
2. On the equivalent picker **with** `validation-timing="submit"` set
   **Expected:** No premature invalid flash during selection; the field only shows invalid after an actual submit attempt

---

#### TC-FUNC-503: Range hover-preview band

**Priority:** P1

**Steps:**

1. Click a start day, do not click a second day yet
2. Hover forward across several later days
   **Expected:** A live grey preview band appears and updates as the mouse moves — same rounded-cap geometry as a committed range, monochrome grey (no blue)
3. Move the mouse outside the calendar entirely
   **Expected:** Preview band clears completely
4. Hover back onto the start day itself
   **Expected:** No preview band renders against it
5. Click a second day to complete the range
   **Expected:** Final committed styling (blue start/end caps, flat grey interior) takes over cleanly, no leftover preview styling; `bdsDayHover` fires exactly once per hover, no double-fire; a real `mouseleave` on the grid fires `bdsGridLeave` exactly once

---

#### TC-FUNC-504: No duplicate range band across an `expanded` month boundary

**Priority:** P1

**Steps:**

1. On an `expanded`+`range` picker, select a range that spans into a month whose filler (outside-month) cells fall in the adjacent month, then navigate so that boundary is visible
   **Expected:** No phantom-row band duplication — the range visual renders exactly once per participating day, with no ghost row bleeding into the filler cells

---

### Cross-cutting fixes (affect every `calendarType`/`range` combination)

---

#### TC-FUNC-601: Today-indicator not clipped by range background (Task 19p)

**Priority:** P1

**Steps:**

1. In range mode, make today's date part of a committed range (start, end, or interior day)
   **Expected:** The dashed today-indicator ring renders fully unclipped, with no visible gap or truncation from the range background/cap layering underneath it
2. Combine today + focus/active state on the same cell
   **Expected:** The solid focus/active ring and the dashed today ring both render simultaneously and fully, with no mutual clipping

---

#### TC-FUNC-602 (Safari-mandatory): Apply button commits the draft value

**Priority:** P0
**Browser:** **Real Safari.app required** — this bug was invisible to Chrome, Firefox, and Playwright-WebKit across every automated re-run; only real Safari.app reproduced it

**Steps:**

1. On a plain single-date picker, click a day, click Apply
   **Expected:** Popover closes; field shows the newly selected value (not the previous value); `bdsChange` fires with the correct date
2. On a range picker (`basic` and `expanded`), click a start and end day, click Apply
   **Expected:** Same — popover closes, field shows the committed range, `bdsChange` fires with `{ start, end }`
3. Repeat both in a fresh private Safari window with a hard-cleared cache
   **Expected:** Identical results — regression guard against the exact three-layered root cause this bug had (WebKit-specific focus-fallback/ancestor-detection interaction with `bds-popover`'s outside-click/focus-outside listeners)

---

### Visual / Figma Validation

Use DevTools **Computed** tab to inspect CSS custom property resolved values and exact pixel geometry, not just visual impression. **These cases have no dedicated playground markup** — each one's `Scenario` line points at an existing functional scenario in `src/index.html` and inspects its rendered output, rather than requiring its own unique setup.

---

#### TC-UI-101: Range two-layer cap geometry — no corner peek-through

**Priority:** P1
**Scenario:** `range-grid` (TC-FUNC-403's section) — click "Set range flags" for a deterministic, reproducible start/in-range/end layout rather than depending on a live picker's current selection

**Steps:**

1. Zoom-screenshot the boundary between a range-start day and its adjacent in-range day, and between an in-range day and the range-end day
   **Expected:** No grey/white sliver visible at either cap's rounded corners; `Full`/interior days render flat grey with no blue; `Start`/`End` show the blue rounded cap with correct directional `Bkgd` bridging into the neighbor

---

#### TC-UI-102: Committed-range hover states — no seam

**Priority:** P1
**Scenario:** `range-grid` after "Set range flags" (same as TC-UI-101), or any live range picker (e.g. `dp-range-basic`) after a committed selection

**Steps:**

1. Hover a range-start day, an interior day, and the range-end day in turn
   **Expected:** Each shows a full, seamless rounded highlight with drop-shadow (darker blue for start/end, light grey for interior) and no visible trim/seam at the cell's connecting edges

---

#### TC-UI-103: Focus/active ring not clipped by a neighboring cell

**Priority:** P2
**Scenario:** `range-grid` after "Set range flags." Note: the grid uses roving `tabindex` with no arrow-key traversal yet (Phase 8, v3 scope), so `Tab` alone cannot reach an arbitrary interior day cell — click the target cell first to give it real focus, then re-tab past and back onto it, or inspect via `:focus-visible` directly in DevTools' Force element state menu.

**Steps:**

1. Tab-focus a range-participating day cell (start, end, or interior)
   **Expected:** The focus ring renders fully unclipped on all sides, including the edge facing an adjacent range cell — not truncated by the neighbor's background painting over it

---

#### TC-UI-104: `calendarType="default"` renders with no visible header/footer chrome

**Priority:** P2
**Scenario:** `dp-default-click` (TC-FUNC-301's section)

**Steps:**

1. Open a `default`-type picker
   **Expected:** Popover shows the bare calendar only — no icon/title header row, no close button, no footer buttons, and no layout artifact (stray padding/corner-radius) where that chrome would normally sit

---

### Accessibility (ARIA) — deltas from v1

Use DevTools → Accessibility panel or axe DevTools extension. Baseline grid/day-cell ARIA semantics are already covered by the v1 plan (`TC-ACC-001`–`005`); only new v2-introduced surfaces are covered here. Same as the Visual section above — no dedicated markup, each `Scenario` line reuses an existing functional scenario.

---

#### TC-ACC-101: Hour/minute selects have accessible labels

**Priority:** P1
**Scenario:** `dp1` (TC-FUNC-101's section)

**Steps:**

1. Inspect the hour and minute `bds-select` elements on a `with-time` picker
   **Expected:** Each has a real accessible name (`aria-labelledby` correctly wired to a visually-hidden label), not a bare, unlabeled control

---

#### TC-ACC-102: Range day-cell accessible state

**Priority:** P1
**Scenario:** `range-grid` after "Set range flags" (TC-FUNC-403's section), or any live range picker after a committed selection

**Steps:**

1. Inspect a range-start, in-range, and range-end day cell's accessible name/state
   **Expected:** Each still carries the same full-date accessible name pattern as v1's single-date cells; `aria-selected` (or equivalent) correctly reflects range participation, not just plain selection

---

### Regression Smoke Suite

Run after any change to `bds-date-picker.tsx`, `bds-calendar-grid.tsx`, `bds-popover.tsx`, or a shared date-engine module.

| #     | Check                                                              | Expected                                                | Pass? |
| ----- | --------------------------------------------------------------------- | ------------------------------------------------------------ | ----- |
| S-101 | v1 single-date baseline (open/close, draft-until-Apply, Cancel/Clean/Apply, form participation) | Unchanged from `EOA-16692` plan's own smoke suite       | [ ]   |
| S-102 | `withTime` Apply commits correct UTC value                        | Console logs correct ISO string                              | [ ]   |
| S-103 | `min`/`max` disables out-of-range days and guards whole-month nav | Dimmed/unclickable days; nav buttons disabled correctly       | [ ]   |
| S-104 | `calendarType="default"` commits on click, no chrome renders        | Immediate commit-and-close; no header/footer                  | [ ]   |
| S-105 | Range Apply emits `{ start, end }` in both `basic` and `expanded`   | Correct shape, both modes                                     | [ ]   |
| S-106 | Range Clean stays open; Cancel/Apply still close                    | Verified across all `calendarType`/`range` combinations       | [ ]   |
| S-107 | Required range picker blocks/allows form submit correctly            | Invalid before applying, valid after, correct `FormData` shape | [ ]   |
| S-108 | Safari: Apply commits the draft value (single-date and range)        | **Real Safari.app**, no stale-value regression                | [ ]   |
| S-109 | No console errors/warnings on any playground scenario                | Clean console, except the one intentional narrow-window warning | [ ]  |

---

## Known Design Gaps (flag to team)

| Gap                                       | Details                                                                                                                                                                                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Popover close-button accessible name**    | Carried over from v1, unchanged. Tracked as [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133). |
| **Keyboard-typed date entry**                | Still not implemented in v2 — the trigger field remains `selectable` (non-editable). Unscheduled. |
| **Arrow-key 2D grid navigation**             | Still deferred to Phase 8 (v3 scope, `EOA-17662`) — not implemented in v2. Tab-based focus works; arrow-key day-to-day movement does not. |
| **`basic`+`range` header format regresses to plain text (no `Start:`/`End:` labels)** | Deliberate engineering tradeoff (Task 19k's third follow-up) to avoid popover-width overflow at the fixed 296px `basic` width — not a bug. Expected to regain the labeled format once the Phase 6 presets sidebar (v3 scope) widens `basic`+`range`'s popover. |
| **`bds-popover` CSS custom-property inheritance has no automated regression coverage** | Confirmed manually multiple times during this plan but has no checked-in browser-level test yet — tracked separately in `bds-popover-css-custom-property-inheritance-browser-test.md`. |

---

## Test Deliverables

- This document (`ai-work/qa/test-plans/EOA-17138-bds-date-picker-v2-test-plan.md`)
- Bug reports per defect: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
- Update **Pass?** checkboxes inline after each test run

---

## Verification (how to run)

1. **Start the dev-server playground:**
   ```bash
   fnm use && pnpm dev:components
   ```
2. Open the served page — `packages/boreal-web-components/src/index.html` now carries one labeled section per test-case group above (cleaned up alongside this plan to drop scenarios this plan doesn't reference)
3. Execute test cases in order: Functional (Time selector → Min/max → `calendarType` → Range core → Range refinements → Cross-cutting fixes) → Visual → Accessibility → Regression
4. **Apply-flow test cases (TC-FUNC-401, 405, 501, 602; S-105, S-106, S-108) must be re-run on real Safari.app**, not just Chrome/Firefox or Playwright-WebKit automation — this bug class has a confirmed history of false-passing there
5. ARIA inspection: DevTools → Elements → Accessibility tab (or axe DevTools extension)
6. Computed styles: DevTools → Elements → Computed tab, filter by `padding`, `gap`, `outline`, `box-shadow`, `background-color`
7. Log defects:
   ```bash
   .claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa
   ```
