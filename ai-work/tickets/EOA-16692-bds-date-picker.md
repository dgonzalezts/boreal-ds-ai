# EOA-16692 — bds-date-picker (v1: Phases 0–1; v2: Phases 2–9)

**Ticket:** EOA-16692 ("Implement Date Picker v1") — Phase 0–1 (this file's primary scope, done)
**v2 Ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — dedicated Jira story, sibling to EOA-16692 under the same parent Feature (EOA-14927), linked "relates to" EOA-16692
**Status:** Done (EOA-16692); In Progress (EOA-17138, not started — scope expanded 2026-08-24)
**Goal:** Ship the foundational date-picker contract (`date-engine` + `bds-calendar-grid`) and a working single-date, optional-time `bds-date-picker` component, then extend it in v2 with every remaining ADR-0003 roadmap phase in one sprint (time selector, min/max, range, dual time, presets, banner, keyboard/a11y/RTL, and the month/year quick-picker).

**Scope split (2026-08-19):** due to sprint time constraints, Phase 2 (the time selector) was moved out of the v1 plan into its own `v2` plan, to be picked up next sprint under its own Jira story EOA-17138. v1/EOA-16692 covered Phase 0–1 only (single-date picker, no time) and is now done.

**Scope expansion (2026-08-24):** EOA-17138/v2 was originally scoped to Phase 2 (time selector) alone. Per the decision to close out the entire remaining roadmap next sprint, v2 now also covers Phase 3 (min/max), Phase 4 (range), Phase 5 (dual time), Phase 6 (presets sidebar), Phase 7 (banner + range summary), Phase 8 (keyboard/a11y/RTL), and the previously-unscheduled month/year quick-picker. Keyboard-typed date entry in the trigger field remains explicitly excluded (see "Out" below) — it is not reintroduced by this expansion.

**Spike doc:** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — cross-cutting architecture decisions (no calendar library, `<table role="grid">` markup, component decomposition, single-vs-range component) live there, not duplicated here.

**Plans:**
- [`ai-work/plans/EOA-16692-bds-date-picker-v1.md`](../plans/EOA-16692-bds-date-picker-v1.md) — Phase 0–1, ticket EOA-16692 (`done`)
- [`ai-work/plans/EOA-16692-bds-date-picker-v2.md`](../plans/EOA-16692-bds-date-picker-v2.md) — Phases 2–9, ticket EOA-17138 (`pending`, next sprint)

## Scope

**In:**
- `date-engine` service: pure `date-fns`-based month-grid generation, date math, locale-aware formatting — framework-agnostic, no Stencil/DOM.
- `bds-calendar-grid`: dumb, controlled, presentational custom element rendering a native `<table role="grid">` (month/year header + nav, weekday row, day grid). Registered component with full test suite; documented only as an internal note inside `bds-date-picker.mdx` (no standalone story/MDX).
- `bds-date-picker`: orchestrator composing `bds-text-field` (display trigger) + `bds-popover` (floating panel) + `bds-calendar-grid`. Controlled public `value`/`bdsChange`/`valueChange`, internal draft state until Apply, Clean/Cancel/Apply footer, FACE-compliant.
- `locale` prop (raw `date-fns` `Locale` object) and `timezone` prop (IANA string, default = browser resolved timezone).

**In v2 (moved out of v1, next sprint, scope expanded 2026-08-24 to close the full remaining roadmap):**
- Phase 2: single hour:minute time selector added to the popover; value becomes UTC ISO 8601 datetime when time is enabled.
- Phase 3: min/max date constraints (wiring already-implemented `date-engine`/`bds-calendar-grid` capacity), disabled-date rendering, whole-month-disabled nav guard, helper text — needs its own UX/UI design pass first (blocking gate, v2 plan Task 9), per the spike doc's Roadmap risks item 4.
- Phase 4: date range / dual calendar — `range: boolean` prop, dual `bds-calendar-grid` instances, `value` becomes `string | { start, end }`, range day-states (in-range/start/end), Start/End header labels.
- Phase 5: dual time selector (Inicio/Fin), reusing Phase 2's time-selector helper twice.
- Phase 6: presets sidebar (Today/Yesterday/Last 7 days/Last 30 days/This month/Last month/Custom) — needs a fixed-vs-consumer-configurable decision first (blocking gate, v2 plan Task 28).
- Phase 7: info banner + footer range-summary text.
- Phase 8: keyboard grid navigation (arrow-key 2D traversal via the existing `grid-navigation.ts` utility), live-region announcements, RTL audit.
- Month/year quick-picker (previously unscheduled, folded into v2 as Phase 9): drill-down month-grid/year-grid navigation from the calendar header — needs a UX confirmation of its inferred interaction model first (blocking gate, v2 plan Task 45).

**Out (explicitly excluded from v2's expansion):**
- keyboard-typed date entry in the trigger field (unscheduled, not phase-assigned — see spike doc's "Unscheduled — keyboard-typed date entry" entry, added 2026-08-19, for the full library research, three enforcement levels considered, and Level 3's detailed effort assessment). Deliberately excluded from this expansion — do not pick up as a side effect of any v2 task. Remains a candidate for its own future ticket once Phase 3's min/max UX is resolved and a dedicated Figma research pass is done, per the spike doc's existing recommendation.

## Acceptance Criteria

- [ ] `date-engine` has zero Stencil/DOM imports and is covered by plain-Jest unit tests; never re-exports `date-fns` or its `Locale` type by import path from its public barrel.
- [ ] `bds-calendar-grid` renders as a native `<table role="grid">` (not div+CSS-Grid) and owns no selection state; day-click and month-nav are emitted upward, `displayMonth` is passed back down by the parent.
- [ ] `bds-date-picker` public `value` is canonical ISO 8601 — `yyyy-MM-dd` naive (v1, done); full UTC `Z` ISO string when time is enabled, or `{ start, end }` (each a naive date string or full UTC string depending on `showTime`) when `range` is enabled (v2, next sprint) — decoupled from the `format` display prop.
- [ ] Day clicks/time changes mutate only internal draft state; `value`/`bdsChange`/`valueChange` fire only on Apply.
- [ ] Cancel reverts draft to last committed value and closes the popover without emitting.
- [ ] Clean clears the draft **and commits immediately** (empties `value`, emits with `''` or an equivalent empty range shape, closes popover).
- [ ] `bds-date-picker` is form-associated (FACE) following the `bds-text-field.tsx` pattern.
- [ ] `hideArrow` prop (default `false`) is a genuine opt-in override piped into `floatingOptions.hideArrow`, unlike `bds-select`'s hardcoded `true`. Default flipped from the originally-specified `true` to `false` (2026-08-18 decision) to comply with the codebase's `stencil/ban-default-true` ESLint rule (no boolean `@Prop()` in the codebase defaults to `true`) — the popover's arrow now renders by default and must be explicitly hidden via `hide-arrow="true"`.
- [ ] The popover's `placement` is a fixed `bottom-start` (not user-configurable, not left to `bds-popover`'s own `bottom` default) — matches the reference calendar-dialog design (arrow and panel consistently left-aligned under the trigger field, never centered or flipped). Added 2026-08-18, not in the original ticket scope — caught via design reference review during Task 14.
- [ ] The popover renders a header row (`header={true}`/`closable={true}`, hardcoded calendar-dots icon, title bound live to the draft/committed date, falling back to a new `headerPlaceholder` prop — default `'Select a date'` — when empty; a Start/End labeled pair in range mode, per v2 Phase 4). Added 2026-08-19, not in the original ticket scope — caught via the same design reference review; see the spike doc's Resolved Decisions table for the full rationale.
- [ ] Component registered under the `forms` docs category.
- [ ] Default `format` is `yyyy/MM/dd`.
- [ ] `min`/`max` date constraints correctly disable out-of-range day cells (visually shown, functionally inert) and guard month navigation into a fully-disabled month (v2 Phase 3).
- [ ] `range` mode renders one or two `bds-calendar-grid` instances and computes correct in-range/start/end day-states without any markup change to `bds-calendar-grid`'s native `<table role="grid">` (v2 Phase 4).
- [ ] Presets sidebar and info banner only render in `range` mode, matching the confirmed Figma gating (v2 Phases 6–7).
- [ ] Arrow-key 2D grid traversal works identically across single and dual (range) calendar instances, with month-boundary crossing correctly triggering `bdsMonthNavigate` (v2 Phase 8).
- [ ] Month/year quick-picker drill-down (header label → month grid → year grid, and back) works identically across single and dual calendar instances, with no new public props on `bds-date-picker` (v2 Phase 9).

## Dependencies

- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` must be added as new runtime dependencies of `packages/boreal-web-components` (neither currently present — verified against `package.json`, not recalled).
- Existing `bds-text-field`, `bds-popover`, `formAssociatedMixin`/`useFormField`, `KeyboardController` are reused, not modified (unless a documented gap is found).
- `src/utils/a11y/keyboard/navigation/grid-navigation.ts` (existing, generic) is the confirmed integration point for Phase 8's arrow-key traversal — reused, not reimplemented.
- `date-engine`'s already-implemented but previously-unwired `isWithinRange`/`compareDates` (Phase 3) and `DayCell.isDisabled` (`bds-calendar-grid` types, since v1 Task 7) are reused for min/max — no new date-math primitives expected.
- Phase 4 (range) and Phase 5 (dual time) both depend on Phase 2's `renderTimeSelector.tsx` and Phase 3's day-state rendering patterns landing first — v2 plan tasks are ordered accordingly.

## Open Questions (resolved at the task checkpoint noted in the plan, not before starting)

- Outside-month day cell interactivity (clickable-but-muted vs. inert) — check against Figma at implementation time. *(Resolved in v1.)*
- `useFormField` vs. `formAssociatedMixin` currency — check which recently built form components adopted before wiring FACE. *(Resolved in v1.)*
- `@Listen()` vs. runtime `addElementListener` for `bds-calendar-grid` event wiring inside `bds-popover`'s slotted content. *(Resolved in v1.)*
- Field label ownership (`bds-text-field`'s built-in label vs. a `bds-date-picker`-owned one). *(Resolved in v1.)*
- Translatable footer button text convention (`labels` prop vs. named slots) — check existing i18n precedent first. *(Resolved in v1.)*
- Phase 2 single-date time-selector UI is inferred (not pictured in the provided docs, which only show the range variant's dual Inicio/Fin selector) — needs a design check-in before that task (v2 plan Task 2).
- Phase 3 disabled-date interaction design (tooltip/message, whole-month-disabled behavior, helper text) — no Figma mockup beyond a generic token; resolved via v2 plan Task 9's design check-in.
- Phase 4 popover header Start/End prefix presentation, and whether a single-calendar range mode (`Basic` + `Range: true`, one calendar) needs support alongside the dual-calendar `Expanded` layout — resolved during v2 plan Task 18.
- Phase 6 fixed vs. consumer-configurable presets — resolved via v2 plan Task 28's design/API decision.
- Phase 9 (quick-picker) drill-down interaction model is inferred from mainstream date-picker conventions, not directly observed in a Figma prototype — resolved via v2 plan Task 45's UX confirmation.
- Keyboard-typed date entry in the trigger field remains explicitly out of scope — not an open question for this ticket, tracked only as a future candidate in the spike doc.

## Quality Gates

**v1 (Phase 0–1, done):**
- [x] React/Vue wrapper parity confirmed at the end of Phase 1 (plan Task 22) via the `dev:pack:react`/`dev:pack:vue` pipeline, not a live dev server.
- [x] Coverage-phase Jest tests (≥90%) pass per component as each test task lands; mutation-phase (Stryker, ≥90%) ran once, consolidated, across all three testable units (`date-engine`, `bds-calendar-grid`, `bds-date-picker`).

**v2 (Phases 2–9, next sprint):**
- [ ] React/Vue wrapper parity confirmed per phase (v2 plan Tasks 7, 15, 22, 27, 34, 39, 44, 51) via the same pipeline — per-phase rather than fully consolidated, since the component is already established and shipping by Phase 3 onward.
- [ ] Coverage-phase Jest tests (≥90%) pass per phase as each phase's test task lands; mutation-phase (Stryker, ≥90%) runs exactly once at the very end (v2 plan Task 52), across all three testable units, covering every phase's additions.
- [ ] Blocking design/UX gates resolved before their dependent implementation task starts: Phase 3 min/max UX (Task 9), Phase 6 presets configurability (Task 28), Phase 9 quick-picker drill-down model (Task 45).
