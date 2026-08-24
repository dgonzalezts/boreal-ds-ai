# EOA-17138 — bds-date-picker v2 (Phases 2–9)

**Ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — dedicated Jira story, sibling to [EOA-16692](https://telesign.atlassian.net/browse/EOA-16692) (v1, done) under the same parent Feature (EOA-14927), linked "relates to" EOA-16692
**Status:** In Progress (scope expanded 2026-08-24)
**Goal:** Extend v1's foundational single-date `bds-date-picker` with every remaining ADR-0003 roadmap phase in one sprint: an optional time selector, min/max constraints, date-range (dual calendar) support, dual time selection, a presets sidebar, an info banner with a footer range summary, full keyboard/a11y/RTL parity, and the month/year quick-picker — without breaking v1's naive-date `value` contract for consumers who use none of the above.

**Scope expansion (2026-08-24):** EOA-17138 was originally scoped to Phase 2 (time selector) alone. Per the decision to close out the entire remaining roadmap next sprint, it now also covers Phase 3 (min/max), Phase 4 (range), Phase 5 (dual time), Phase 6 (presets sidebar), Phase 7 (banner + range summary), Phase 8 (keyboard/a11y/RTL), and the previously-unscheduled month/year quick-picker (folded in as Phase 9). Keyboard-typed date entry in the trigger field remains explicitly excluded — it is not reintroduced by this expansion.

**Spike doc:** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — cross-cutting architecture decisions (no calendar library, `<table role="grid">` markup, component decomposition, single-vs-range component) live there, not duplicated here.

**Plan:** [`ai-work/plans/EOA-17138-bds-date-picker-v2.md`](../plans/EOA-17138-bds-date-picker-v2.md) — 52 tasks across 8 phases, `in progress`.

**v1 ticket (prerequisite, done):** [`ai-work/tickets/EOA-16692-bds-date-picker.md`](./EOA-16692-bds-date-picker.md) — Phase 0–1, foundational `date-engine` + `bds-calendar-grid` + single-date `bds-date-picker`.

**Subtasks:** the 52-task plan is tracked day-to-day at the task level in the plan file; this ticket's own Jira subtasks group that work into the team's standard cadence:

- `EOA-17243` — 01-Initial Review & Planning
- `EOA-17290` — 02-Add time selector and min/max constraints (Phase 2 + Phase 3)
- `EOA-17294` — 03-Add date range, dual time selector, and presets sidebar (Phase 4 + Phase 5 + Phase 6)
- `EOA-17297` — 04-Add info banner, keyboard/a11y/RTL support, and month/year quick-picker (Phase 7 + Phase 8 + Phase 9)
- `EOA-17295` — 05-Add unit tests and mutation testing coverage
- `EOA-17291` — 06-Add Storybook stories and MDX docs
- `EOA-17292` — 07-Verify web component and React/Vue parity
- `EOA-17296` — 08-Perform Manual QA
- `EOA-17293` — 09-Check for the Definition of Done

## Scope

**In:**

- Phase 2: single hour:minute time selector added to the popover; value becomes UTC ISO 8601 datetime when time is enabled.
- Phase 3: min/max date constraints (wiring already-implemented `date-engine`/`bds-calendar-grid` capacity), disabled-date rendering, whole-month-disabled nav guard, helper text — needs its own UX/UI design pass first (blocking gate, plan Task 9), per the spike doc's Roadmap risks item 4.
- Phase 4: date range / dual calendar — `range: boolean` prop, dual `bds-calendar-grid` instances, `value` becomes `string | { start, end }`, range day-states (in-range/start/end), Start/End header labels.
- Phase 5: dual time selector (Inicio/Fin), reusing Phase 2's time-selector helper twice.
- Phase 6: presets sidebar (Today/Yesterday/Last 7 days/Last 30 days/This month/Last month/Custom) — needs a fixed-vs-consumer-configurable decision first (blocking gate, plan Task 28).
- Phase 7: info banner + footer range-summary text.
- Phase 8: keyboard grid navigation (arrow-key 2D traversal via the existing `grid-navigation.ts` utility), live-region announcements, RTL audit.
- Month/year quick-picker (previously unscheduled, folded in as Phase 9): drill-down month-grid/year-grid navigation from the calendar header — needs a UX confirmation of its inferred interaction model first (blocking gate, plan Task 45).

**Out (explicitly excluded from this expansion):**

- keyboard-typed date entry in the trigger field (unscheduled, not phase-assigned — see spike doc's "Unscheduled — keyboard-typed date entry" entry, added 2026-08-19, for the full library research, three enforcement levels considered, and Level 3's detailed effort assessment). Deliberately excluded from this expansion — do not pick up as a side effect of any v2 task. Remains a candidate for its own future ticket once Phase 3's min/max UX is resolved and a dedicated Figma research pass is done, per the spike doc's existing recommendation.

## Acceptance Criteria

- [ ] `bds-date-picker` public `value` extends v1's naive `yyyy-MM-dd` baseline to: full UTC `Z` ISO string when time is enabled, or `{ start, end }` (each a naive date string or full UTC string depending on `withTime`) when `range` is enabled — decoupled from the `format` display prop, non-breaking for existing single-date consumers.
- [ ] The popover header row's title binds live to the draft/committed date in single-date mode, and to a Start/End labeled pair in range mode (Phase 4).
- [ ] `min`/`max` date constraints correctly disable out-of-range day cells (visually shown, functionally inert) and guard month navigation into a fully-disabled month (Phase 3).
- [ ] `range` mode renders one or two `bds-calendar-grid` instances and computes correct in-range/start/end day-states without any markup change to `bds-calendar-grid`'s native `<table role="grid">` (Phase 4).
- [ ] Presets sidebar and info banner only render in `range` mode, matching the confirmed Figma gating (Phases 6–7).
- [ ] Arrow-key 2D grid traversal works identically across single and dual (range) calendar instances, with month-boundary crossing correctly triggering `bdsMonthNavigate` (Phase 8).
- [ ] Month/year quick-picker drill-down (header label → month grid → year grid, and back) works identically across single and dual calendar instances, with no new public props on `bds-date-picker` (Phase 9).

## Dependencies

- Requires EOA-16692 v1 (Phase 0–1: `date-engine`, `bds-calendar-grid`, single-date `bds-date-picker`) fully done first — done.
- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` already added as runtime dependencies of `packages/boreal-web-components` (v1 Task 1) — reused, not re-added.
- `src/utils/a11y/keyboard/navigation/grid-navigation.ts` (existing, generic) is the confirmed integration point for Phase 8's arrow-key traversal — reused, not reimplemented.
- `date-engine`'s already-implemented but previously-unwired `isWithinRange`/`compareDates` (Phase 3) and `DayCell.isDisabled` (`bds-calendar-grid` types, since v1 Task 7) are reused for min/max — no new date-math primitives expected.
- Phase 4 (range) and Phase 5 (dual time) both depend on Phase 2's `renderTimeSelector.tsx` and Phase 3's day-state rendering patterns landing first — plan tasks are ordered accordingly.

## Open Questions (resolved at the task checkpoint noted in the plan, not before starting)

- Phase 2 single-date time-selector UI is inferred (not pictured in the provided docs, which only show the range variant's dual Inicio/Fin selector) — needs a design check-in before that task (plan Task 2).
- Phase 3 disabled-date interaction design (tooltip/message, whole-month-disabled behavior, helper text) — no Figma mockup beyond a generic token; resolved via plan Task 9's design check-in.
- Phase 4 popover header Start/End prefix presentation, and whether a single-calendar range mode (`Basic` + `Range: true`, one calendar) needs support alongside the dual-calendar `Expanded` layout — resolved during plan Task 18.
- Phase 6 fixed vs. consumer-configurable presets — resolved via plan Task 28's design/API decision.
- Phase 9 (quick-picker) drill-down interaction model is inferred from mainstream date-picker conventions, not directly observed in a Figma prototype — resolved via plan Task 45's UX confirmation.
- Keyboard-typed date entry in the trigger field remains explicitly out of scope — not an open question for this ticket, tracked only as a future candidate in the spike doc.

## Quality Gates

- [ ] React/Vue wrapper parity confirmed per phase (plan Tasks 7, 15, 22, 27, 34, 39, 44, 51) via the `dev:pack:react`/`dev:pack:vue` pipeline — per-phase rather than fully consolidated, since the component is already established and shipping by Phase 3 onward.
- [ ] Coverage-phase Jest tests (≥90%) pass per phase as each phase's test task lands; mutation-phase (Stryker, ≥90%) runs exactly once at the very end (plan Task 52), across all three testable units, covering every phase's additions.
- [ ] Blocking design/UX gates resolved before their dependent implementation task starts: Phase 3 min/max UX (Task 9), Phase 6 presets configurability (Task 28), Phase 9 quick-picker drill-down model (Task 45).
