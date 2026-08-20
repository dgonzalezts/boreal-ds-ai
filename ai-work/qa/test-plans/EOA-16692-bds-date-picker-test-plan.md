# Test Plan: `bds-date-picker` Component (Phase 0–1)

## Context

`bds-date-picker` is a composite, form-associated (FACE) date-picker control composing a **consumer-supplied** `bds-text-field` trigger (slotted, not self-rendered) with a `bds-popover` panel containing a `bds-calendar-grid` body and a Clean/Cancel/Apply footer. Selection is held in internal draft state until Apply — day clicks and month navigation never touch the public `value` until the user explicitly commits. `bds-calendar-grid` is a dumb, controlled, presentational element rendering a native `<table role="grid">`, with no selection state of its own.

This plan covers **Phase 0–1 only** — the single-date picker (`showTime` unset, naive `yyyy-MM-dd` value contract). The time selector (Phase 2: `showTime`, hour/minute selection, UTC-normalized `value`) is out of scope here — it has not been implemented yet and is tracked in a separate follow-up ticket/plan (EOA-17138 / `EOA-16692-bds-date-picker-v2.md`), which will need its own test plan once that work lands.

Figma design reference: `calendarPicker` component_set, file `rtiE5zGA4aoOuxIQMgfD6h` ("[BOR] DSG COMPONENTS → FORMS"), `Basic` + `Range: off` + `End Date: off` + `Banner: off` variant combination — the literal single-date state.
Popover panel spec node: `I1537:17221;14:23281;158:176502` (`Container`, confirmed 296×434px)
Day-cell component_set: `_DatePickerNumber`, frame `14:23554`
Component sources:
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx`

Brand theme in scope: **Proximus only**
Created: 2026-08-20

---

## Scope

**In scope:**

- `bds-calendar-grid`: rendering (native `<table role="grid">`), day-cell visual states, selection prop, month navigation events
- `bds-date-picker`: popover open/close (default, `hideArrow`, `disabled`), draft-until-Apply selection lifecycle, footer actions (Clean/Cancel/Apply), the consumer-supplied slotted-field contract (missing-field warning, `disabled`/`selectable`/`value` sync, clear-button wiring), header row (live date binding, placeholder, close button)
- Form participation (FACE): `FormData` submission, `formResetCallback`, `required` + `reportValidity()`, and the complementary field-level `required` pattern on the slotted field
- `fieldset disabled` ancestor propagation
- Visual / Figma design validation against the confirmed `Basic`+`Range:off` single-date state
- Accessibility / ARIA grid semantics on `bds-calendar-grid`
- Regression smoke suite

**Out of scope:**

- Phase 2 (time selector, `showTime`, UTC value contract) — not yet implemented, separate ticket EOA-17138
- Phase 3+ (min/max, range, presets, banner) — future versions, not yet implemented
- Keyboard grid (arrow-key) navigation inside the calendar — explicitly deferred to Phase 8, not implemented
- Non-Proximus brand themes (Masiv, Telesign, BICS)
- `bds-text-field`, `bds-popover`, `bds-button` internals (covered by their own plans) — this plan only tests the *composition* contract between them and `bds-date-picker`
- React/Vue wrapper parity (covered by the plan's own dedicated Task 22 parity check, not duplicated here)
- Automated e2e tests (manual execution only)

---

## Environment

- **No Storybook stories exist yet** (documentation is Task 21 in the implementation plan, not yet done) — until then, run the local dev-server playground:
  ```bash
  fnm use && pnpm dev:components
  ```
  from the monorepo root, and open the served page (`packages/boreal-web-components/src/index.html`).
- Browser: Chrome (latest stable) primary; Safari/WebKit for interaction-state checks (transitions/box-shadow rendering has previously diverged between engines on this component)
- DevTools: open for ARIA inspection, computed-style checks, and `FormData`/event console logging
- **Once Task 21 documentation lands**, update this section to point at the `bds-date-picker` Storybook stories instead of the playground, mirroring `bds-select`'s test plan.

---

## Entry Criteria

- [ ] `bds-date-picker`/`bds-calendar-grid` render without console errors in the playground
- [ ] Dev server running locally on the `feature/EOA-16692_bds-date-picker-v1_DG` branch (or `main` once merged)
- [ ] DevTools accessibility panel available (Chrome ≥ 120)

## Exit Criteria

- [ ] All P0 test cases pass
- [ ] ≥ 90% of P1 test cases pass
- [ ] All Figma visual discrepancies documented
- [ ] All ARIA failures logged as bugs
- [ ] No open P0 bugs (one known P2 gap already tracked — see Known Design Gaps)

---

## Risk Assessment

| Risk                                                                                  | Probability | Impact | Mitigation                                                                                          |
| -------------------------------------------------------------------------------------- | ----------- | ------ | ----------------------------------------------------------------------------------------------------- |
| Day click inside the calendar prematurely commits `value` (breaks draft-until-Apply)    | L           | H      | TC-FUNC-004 explicitly asserts `value`/`bdsChange` stay untouched until Apply                        |
| Consumer's own slotted-field props (`clearable`, `name`, `pattern`) desync from picker  | M           | H      | Dedicated TC-FUNC-* cases per known-risky prop, matching the plan's own Slotted Field Props audit    |
| Popover panel dimensions drift from the Figma-confirmed 296×434px spec on future edits  | M           | M      | TC-UI-001/002 pin exact computed-style values, not just visual impression                            |
| Calendar-grid table `border-spacing` reintroduces the 8px edge-overflow bug             | L           | M      | TC-UI-003 explicitly re-checks flush/symmetric left-right gap                                        |
| `fieldset disabled` ancestor doesn't propagate to the slotted field                     | L           | M      | TC-FUNC-011 tests this specific propagation path, not just the `disabled` prop directly              |
| Close button's missing accessible name (known gap, EOA-17133) masks a *new* a11y defect | M           | L      | TC-ACC checks explicitly separate the known gap from new findings; do not re-file the same defect     |

---

## Test Cases

### Functional — `bds-calendar-grid`

---

#### TC-FUNC-001: Basic grid render

**Priority:** P0

**Preconditions:**

- [ ] `bds-calendar-grid` rendered for August 2026 (`year=2026`, `month=7`), no `selectedDate`

**Steps:**

1. Observe the rendered element
   **Expected:** Root element is a native `<table role="grid">`; header shows "August 2026"; weekday row starts on the locale's configured day (Sunday by default); 42 `<td>` day cells total; July/September leading/trailing days render visually muted (`text/disabled` styling)

---

#### TC-FUNC-002: Day-cell selection prop

**Priority:** P1

**Steps:**

1. Set `selected-date="2026-08-14"` on the grid
   **Expected:** Exactly one cell (August 14) shows the selected/active style (solid fill, contrasting text); no other cell is marked selected

---

#### TC-FUNC-003: Month navigation events

**Priority:** P0

**Steps:**

1. Click the "Next month" nav button
   **Expected:** `bdsMonthNavigate` fires with the correctly rolled-over `year`/`month`; the grid's own `year`/`month` props do **not** change on their own — the parent must re-pass them
2. Wire the event to re-render with the new month/year, then click "Next" repeatedly through a December → January boundary
   **Expected:** Year increments correctly across the boundary; no off-by-one month errors
3. Click a day cell in an outside-month (grayed) position
   **Expected:** No `bdsDayClick` fires; cell is not tab-reachable (`tabindex="-1"` permanently, never promoted)
4. Click an ordinary in-month day cell
   **Expected:** `bdsDayClick` fires once with the correct naive-ISO date in `event.detail.date`

---

#### TC-FUNC-004 (visual states): today / disabled / selected combinations

**Priority:** P1

**Steps:**

1. Force one day as "today" (independent of the real system date) and a different day as `isDisabled`
   **Expected:** Today's cell shows a dashed accent ring with no fill; the disabled cell shows muted text and `cursor: not-allowed`, and does not emit `bdsDayClick` on click
2. Set `selectedDate` to the same disabled day (Selected + Disabled combo)
   **Expected:** Light-blue fill with white text — visually distinct from a plain Selected cell (solid blue fill)

---

### Functional — `bds-date-picker`

---

#### TC-FUNC-005: Popover open/close, default and `hideArrow`

**Priority:** P0

**Preconditions:**

- [ ] `<bds-date-picker>` with a slotted `<bds-text-field slot="field">` (required — see TC-FUNC-009 for the unslotted case)

**Steps:**

1. Click the trigger field
   **Expected:** Popover opens, anchored `bottom-start` under the trigger field, arrow visible by default
2. Click outside the popover
   **Expected:** Popover closes
3. On a second instance with `hide-arrow="true"`, open the popover
   **Expected:** No arrow element renders between the popover and the trigger

---

#### TC-FUNC-006: `disabled` prevents opening

**Priority:** P0

**Steps:**

1. Set `disabled="true"` on `<bds-date-picker>`, click the trigger field
   **Expected:** Nothing happens — the popover does not open; the slotted field also renders visually disabled

---

#### TC-FUNC-007: Draft-until-Apply — day click does not commit

**Priority:** P0

**Steps:**

1. On an instance with no initial `value`, open the popover and click any day
   **Expected:** The clicked day highlights inside the calendar, but the trigger field's displayed text stays empty; no `bdsChange`/`valueChange` fires (verify via a listener/console log)

---

#### TC-FUNC-008: Draft revert on abandoned reopen

**Priority:** P0

**Steps:**

1. On an instance with `value="2026-08-12"`, open the popover — confirm the 12th is pre-highlighted and the calendar shows August 2026
2. Click a different day (e.g. the 20th), then close the popover by clicking outside (do **not** Apply)
3. Reopen the popover
   **Expected:** The originally committed day (the 12th) is shown selected again — the abandoned click's draft did not persist

---

#### TC-FUNC-009: Missing slotted field — console warning

**Priority:** P1

**Steps:**

1. Render a bare `<bds-date-picker>` with no `<bds-text-field slot="field">` child
   **Expected:** A console warning fires (`Expected a <bds-text-field slot="field"> child — none was found.`); the component does not throw

---

#### TC-FUNC-010: Footer actions — Apply, Cancel, Clean

**Priority:** P0

**Steps:**

1. **Apply:** open the popover, pick a day, click Apply
   **Expected:** Trigger text updates to the newly formatted date; popover closes; exactly one `bdsChange` and one `valueChange` fire, each with the naive-ISO detail (never a formatted display string as a second event)
2. **Cancel:** on an instance with `value="2026-08-12"`, open the popover, pick a different day, click Cancel
   **Expected:** Trigger text remains unchanged ("2026/08/12"); popover closes; no event fires
3. **Clean:** on an instance with a committed value, open the popover, click Clean
   **Expected:** Trigger text clears immediately; popover closes; `bdsChange`/`valueChange` fire once each with `''`

---

#### TC-FUNC-011: `fieldset disabled` ancestor propagation

**Priority:** P1

**Steps:**

1. Wrap a `<bds-date-picker>` (with **no** `disabled` prop set directly) inside `<fieldset disabled>`
2. Click the trigger field
   **Expected:** The slotted field itself renders disabled; clicking it does not open the popover; footer buttons (if force-opened for inspection) render disabled too — this must hold even though the `disabled` *prop* was never explicitly set

---

#### TC-FUNC-012: Slotted-field clear button commits, not just clears display

**Priority:** P1

**Steps:**

1. On an instance with a committed `value`, set `clearable="true"` on the slotted field, click the field's own clear (×) button
   **Expected:** `bds-date-picker`'s real `value` becomes `''` (not just the visual display) — `bdsChange`/`valueChange` fire once each with `''`; reopening the popover shows no stale day selected

---

#### TC-FUNC-013: Form participation (FACE)

**Priority:** P0

**Steps:**

1. Wrap `<bds-date-picker name="appointment-date">` in a `<form>`, pick a date, Apply, submit the form
   **Expected:** `FormData` contains `"appointment-date"` with the naive-ISO value (not the display-formatted string)
2. Trigger a native form reset
   **Expected:** Both `value` and the slotted field's displayed text clear
3. On a `required="true"` instance with no value, call `reportValidity()`
   **Expected:** Returns `false`; native validation UI shown
4. Pick a date and Apply, then call `reportValidity()` again
   **Expected:** Returns `true`

---

#### TC-FUNC-014: Complementary field-level `required` pattern

**Priority:** P1

**Steps:**

1. Set `required="true"` and `validation-timing="submit"` directly on the slotted field (no `name` on that inner field), leave the field empty, click Submit
   **Expected:** The browser blocks submission and shows its native "please fill out this field" UI directly on the trigger field, without `bds-date-picker`'s own `reportValidity()` being called
2. Open the popover and click a day (draft only, no Apply)
   **Expected:** No error state appears on the trigger field during day selection (regression check — day cells are mouse-focusable via `tabIndex={-1}`, which previously blurred the trigger and falsely triggered `blur`-timed validation)

---

### Visual / Figma Validation

Figma spec: `Basic`+`Range:off`+`End Date:off`+`Banner:off` variant of the `calendarPicker` component_set (file `rtiE5zGA4aoOuxIQMgfD6h`).
Use DevTools **Computed** tab to inspect CSS custom property resolved values, not just visual impression.

---

#### TC-UI-001: Popover panel dimensions

**Priority:** P0
**Figma node:** `I1537:17221;14:23281;158:176502` (`Container`)

| Property                     | Expected token (resolved value)                                | Actual | Pass? |
| ----------------------------- | ---------------------------------------------------------------- | ------ | ----- |
| Panel width                  | `296px`                                                          |        | [ ]   |
| Header padding                | `16px` vertical / `24px` horizontal (`spatial/padding/m`/`l`)   |        | [ ]   |
| Header icon↔title gap        | `8px` (`spatial/gap/xs`)                                        |        | [ ]   |
| Body (calendar) padding       | `12px` vertical / `24px` horizontal (`spatial/padding/s`/`l`)   |        | [ ]   |
| Footer padding                 | `8px` vertical / `24px` horizontal (`spatial/padding/xs`/`l`)   |        | [ ]   |
| Header title font              | `12px` / `16px` line-height / regular weight                    |        | [ ]   |

---

#### TC-UI-002: Popover header row

**Priority:** P1
**Story/scenario:** default instance, popover open

| Property                          | Expected                                                          | Actual | Pass? |
| ------------------------------------ | -------------------------------------------------------------------- | ------ | ----- |
| Icon                                | hardcoded calendar-dots glyph, 16×16px                              |        | [ ]   |
| Title (no value)                    | shows `headerPlaceholder` text (default `"Select a date"`)         |        | [ ]   |
| Title (draft, pre-Apply)             | updates live as the user browses/selects days, tracking the draft   |        | [ ]   |
| Title (after Apply/reopen)           | reflects the committed `value`, not an abandoned draft              |        | [ ]   |
| Close button                        | closes the popover; abandoning via it reverts the draft on reopen   |        | [ ]   |

---

#### TC-UI-003: Calendar grid flush/symmetric within panel

**Priority:** P0

**Steps:**

1. Open the popover, inspect the calendar grid's left/right edges against the popover's own padding box
   **Expected:** 24px gap on **both** left and right (regression check — a prior bug produced 24px/16px asymmetry from `border-spacing` adding an extra edge gap)

---

#### TC-UI-004: Footer button variants

**Priority:** P2

| Button | Expected variant/color                              | Actual | Pass? |
| ------ | ------------------------------------------------------ | ------ | ----- |
| Clean  | default (`variant="default"`, `color="default"`) — ghost/text look |        | [ ]   |
| Cancel | `variant="outline"`                                    |        | [ ]   |
| Apply  | `color="primary"` — solid blue fill                    |        | [ ]   |

---

#### TC-UI-005: Day-cell state visuals

**Priority:** P1
**Figma node:** `_DatePickerNumber` component_set, frame `14:23554`

| State              | Expected                                                   | Actual | Pass? |
| -------------------- | -------------------------------------------------------------- | ------ | ----- |
| Default (in-month)  | plain text, no fill/ring                                       |        | [ ]   |
| Today               | dashed accent-color ring, no fill                               |        | [ ]   |
| Selected            | solid blue fill, white text                                     |        | [ ]   |
| Outside-month        | muted `text/disabled` grey, not clickable, not tab-reachable    |        | [ ]   |
| Disabled             | muted text, `cursor: not-allowed`                               |        | [ ]   |
| Selected + Disabled  | light-blue fill, white text (distinct from plain Selected)      |        | [ ]   |

---

### Accessibility (ARIA)

Use DevTools → Accessibility panel or axe DevTools extension.

---

#### TC-ACC-001: Calendar grid structural roles

**Priority:** P0

**Steps:**

1. Inspect the rendered `bds-calendar-grid` root
   **Expected:** `<table role="grid">` (not the implicit `role="table"`); weekday header cells are `<th scope="col">`

---

#### TC-ACC-002: Day-cell accessible names

**Priority:** P1

**Steps:**

1. Inspect any day `<td>`'s accessible name
   **Expected:** Full date, not just the visible day number (e.g. full `formatDisplayDate(..., 'PPPP')` output); today's cell additionally carries `aria-current="date"`; the selected cell carries `aria-selected`

---

#### TC-ACC-003: Nav button accessible names

**Priority:** P1

**Steps:**

1. Inspect the prev/next month nav buttons
   **Expected:** Both have real accessible names ("Previous month"/"Next month"), not icon-only with no label

---

#### TC-ACC-004: Trigger field `aria-haspopup`/`aria-expanded`

**Priority:** P1

**Steps:**

1. Inspect the slotted trigger field before/after opening the popover
   **Expected:** `aria-haspopup`/`aria-expanded` correctly reflect popover visibility

---

#### TC-ACC-005: Keyboard reachability (baseline, not full grid navigation)

**Priority:** P1

**Steps:**

1. Tab to the trigger field, press `Enter`/`Space`
   **Expected:** Popover opens (via `bds-popover`'s own keyboard handling)
2. Tab through the footer buttons
   **Expected:** All three (Clean/Cancel/Apply) are reachable and labeled correctly for screen readers

   > **Known gap (P2, tracked as EOA-17133):** the popover header's close (✕) button has no accessible name — do not re-file this as a new defect if found here; it's a pre-existing, already-tracked issue in `bds-popover.tsx`, not specific to `bds-date-picker`.

3. Confirm arrow-key navigation **within** the day grid is **not** expected to work
   **Expected:** No arrow-key day-to-day movement — this is explicitly deferred to Phase 8, not a defect

---

### Regression Smoke Suite

Run after any change to `bds-date-picker.tsx`, `bds-calendar-grid.tsx`, or a shared dependency (`bds-popover`, `bds-text-field`, `bds-button`).

| #     | Check                                             | Expected                                       | Pass? |
| ----- | ---------------------------------------------------- | ------------------------------------------------- | ----- |
| S-001 | Both components render without console errors        | No errors in DevTools console                     | [ ]   |
| S-002 | Popover opens/closes on trigger click / outside click | Visibility toggles correctly                       | [ ]   |
| S-003 | Day click updates draft only, not `value`             | No `bdsChange` until Apply                         | [ ]   |
| S-004 | Apply commits and emits exactly once                  | One `bdsChange` + one `valueChange`, naive-ISO     | [ ]   |
| S-005 | Cancel discards draft, no event                       | Trigger text unchanged, no event fires             | [ ]   |
| S-006 | Clean commits empty value immediately                 | Trigger clears, one event pair with `''`           | [ ]   |
| S-007 | `disabled` blocks opening                              | Popover stays closed on click                      | [ ]   |
| S-008 | Form submit includes correct naive-ISO value           | Correct key/value pair in `FormData`               | [ ]   |
| S-009 | Calendar grid renders flush within the popover panel   | 24px gap both sides, no overflow                    | [ ]   |

---

## Known Design Gaps (flag to team)

| Gap                                       | Details                                                                                                                                                                                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Popover close-button accessible name**    | No accessible name on the icon-only close button inside `bds-popover`'s header (`header`+`closable`). Lives in `bds-popover.tsx`, affects every consumer using that combination, not just `bds-date-picker`. Tracked as [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133). |
| **Month/year quick-picker**                 | Figma's `_DatePickerCalendar` composite shows a month-grid/year-grid quick-picker triggered by clicking the header label — not implemented; the label is static text in this v1. Deliberate scope deferral, not a bug — see the spike doc's "Unscheduled" backlog entry. |
| **Keyboard-typed date entry**                | The trigger field is `selectable` (non-editable) — no keyboard-typed date entry into the field itself. Unscheduled, not phase-assigned — see the spike doc's dedicated research entry. |

---

## Test Deliverables

- This document (`ai-work/qa/test-plans/EOA-16692-bds-date-picker-test-plan.md`)
- Bug reports per defect: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
- Update **Pass?** checkboxes inline after each test run

---

## Verification (how to run)

1. **Start the dev-server playground:**
   ```bash
   fnm use && pnpm dev:components
   ```
2. Open the served page and locate (or re-add, per the plan's own cleanup task) the relevant `bds-date-picker`/`bds-calendar-grid` scenarios
3. Execute test cases in order: Functional (`bds-calendar-grid` → `bds-date-picker`) → Visual → Accessibility → Regression
4. ARIA inspection: DevTools → Elements → Accessibility tab (or axe DevTools extension)
5. Computed styles: DevTools → Elements → Computed tab, filter by `padding`, `gap`, `border`, `box-shadow`, `width`
6. Log defects:
   ```bash
   .claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa
   ```
7. Once Task 21 (Storybook documentation) lands, update the Environment section above to point at the Storybook stories instead of the raw playground, matching `bds-select`'s test plan convention.
