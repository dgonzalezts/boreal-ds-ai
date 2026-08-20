# EOA-16692 — bds-date-picker (v1: Phases 0–1; v2: Phase 2)

**Ticket:** EOA-16692 ("Implement Date Picker 0,1,2") — Phase 0–1 (this file's primary scope)
**v2 Ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — dedicated Jira story for Phase 2, sibling to EOA-16692 under the same parent Feature (EOA-14927), linked "relates to" EOA-16692
**Status:** In Progress (EOA-16692); Open (EOA-17138, not started)
**Goal:** Ship the foundational date-picker contract (`date-engine` + `bds-calendar-grid`) and a working single-date, optional-time `bds-date-picker` component, without precluding the range/min-max/presets/banner features planned for later versions.

**Scope split (2026-08-19):** due to sprint time constraints, Phase 2 (the time selector) was moved out of the v1 plan into its own `v2` plan, to be picked up next sprint under its own Jira story EOA-17138. v1/EOA-16692 now covers Phase 0–1 only (single-date picker, no time). Nothing in Phase 2 had been implemented at the time of the split.

**Spike doc:** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — cross-cutting architecture decisions (no calendar library, `<table role="grid">` markup, component decomposition, single-vs-range component) live there, not duplicated here.

**Plans:**
- [`ai-work/plans/EOA-16692-bds-date-picker-v1.md`](../plans/EOA-16692-bds-date-picker-v1.md) — Phase 0–1, ticket EOA-16692 (`in progress`)
- [`ai-work/plans/EOA-16692-bds-date-picker-v2.md`](../plans/EOA-16692-bds-date-picker-v2.md) — Phase 2, time selector, ticket EOA-17138 (`pending`, next sprint)

## Scope

**In:**
- `date-engine` service: pure `date-fns`-based month-grid generation, date math, locale-aware formatting — framework-agnostic, no Stencil/DOM.
- `bds-calendar-grid`: dumb, controlled, presentational custom element rendering a native `<table role="grid">` (month/year header + nav, weekday row, day grid). Registered component with full test suite; documented only as an internal note inside `bds-date-picker.mdx` (no standalone story/MDX).
- `bds-date-picker`: orchestrator composing `bds-text-field` (display trigger) + `bds-popover` (floating panel) + `bds-calendar-grid`. Controlled public `value`/`bdsChange`/`valueChange`, internal draft state until Apply, Clean/Cancel/Apply footer, FACE-compliant.
- `locale` prop (raw `date-fns` `Locale` object) and `timezone` prop (IANA string, default = browser resolved timezone).

**In v2 (moved out of v1, next sprint):**
- Phase 2: single hour:minute time selector added to the popover; value becomes UTC ISO 8601 datetime when time is enabled.

**Out (explicitly, later versions per the spike doc's Roadmap risks section):**
- min/max constraints (Phase 3 — needs its own UX/UI design pass, see spike doc item 4)
- date range / dual calendar (Phase 4)
- dual time selector (Phase 5)
- presets sidebar (Phase 6)
- banner + footer range summary (Phase 7)
- keyboard grid navigation / broader a11y / RTL polish beyond baseline (Phase 8)
- keyboard-typed date entry in the trigger field (unscheduled, not phase-assigned — see spike doc's "Unscheduled — keyboard-typed date entry" entry, added 2026-08-19, for the full library research, three enforcement levels considered, and Level 3's detailed effort assessment)

## Acceptance Criteria

- [ ] `date-engine` has zero Stencil/DOM imports and is covered by plain-Jest unit tests; never re-exports `date-fns` or its `Locale` type by import path from its public barrel.
- [ ] `bds-calendar-grid` renders as a native `<table role="grid">` (not div+CSS-Grid) and owns no selection state; day-click and month-nav are emitted upward, `displayMonth` is passed back down by the parent.
- [ ] `bds-date-picker` public `value` is canonical ISO 8601 — `yyyy-MM-dd` naive (v1, shipping this sprint); full UTC `Z` ISO string when time is enabled (v2, next sprint) — decoupled from the `format` display prop.
- [ ] Day clicks/time changes mutate only internal draft state; `value`/`bdsChange`/`valueChange` fire only on Apply.
- [ ] Cancel reverts draft to last committed value and closes the popover without emitting.
- [ ] Clean clears the draft **and commits immediately** (empties `value`, emits with `''`, closes popover).
- [ ] `bds-date-picker` is form-associated (FACE) following the `bds-text-field.tsx` pattern.
- [ ] `hideArrow` prop (default `false`) is a genuine opt-in override piped into `floatingOptions.hideArrow`, unlike `bds-select`'s hardcoded `true`. Default flipped from the originally-specified `true` to `false` (2026-08-18 decision) to comply with the codebase's `stencil/ban-default-true` ESLint rule (no boolean `@Prop()` in the codebase defaults to `true`) — the popover's arrow now renders by default and must be explicitly hidden via `hide-arrow="true"`.
- [ ] The popover's `placement` is a fixed `bottom-start` (not user-configurable, not left to `bds-popover`'s own `bottom` default) — matches the reference calendar-dialog design (arrow and panel consistently left-aligned under the trigger field, never centered or flipped). Added 2026-08-18, not in the original ticket scope — caught via design reference review during Task 14.
- [ ] The popover renders a header row (`header={true}`/`closable={true}`, hardcoded calendar-dots icon, title bound live to the draft/committed date, falling back to a new `headerPlaceholder` prop — default `'Select a date'` — when empty). Added 2026-08-19, not in the original ticket scope — caught via the same design reference review; see the spike doc's Resolved Decisions table for the full rationale.
- [ ] Component registered under the `forms` docs category.
- [ ] Default `format` is `yyyy/MM/dd`.

## Dependencies

- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` must be added as new runtime dependencies of `packages/boreal-web-components` (neither currently present — verified against `package.json`, not recalled).
- Existing `bds-text-field`, `bds-popover`, `formAssociatedMixin`/`useFormField`, `KeyboardController` are reused, not modified (unless a documented gap is found).

## Open Questions (resolved at the task checkpoint noted in the plan, not before starting)

- Outside-month day cell interactivity (clickable-but-muted vs. inert) — check against Figma at implementation time.
- `useFormField` vs. `formAssociatedMixin` currency — check which recently built form components adopted before wiring FACE.
- `@Listen()` vs. runtime `addElementListener` for `bds-calendar-grid` event wiring inside `bds-popover`'s slotted content.
- Field label ownership (`bds-text-field`'s built-in label vs. a `bds-date-picker`-owned one).
- Translatable footer button text convention (`labels` prop vs. named slots) — check existing i18n precedent first.
- Phase 2 single-date time-selector UI is inferred (not pictured in the provided docs, which only show the range variant's dual Inicio/Fin selector) — needs a design check-in before that task (see v2 plan Task 2, was Task 24 before the v1/v2 split).

## Quality Gates

**v1 (Phase 0–1, this sprint):**
- [ ] React/Vue wrapper parity confirmed at the end of Phase 1 (plan Task 22) via the `dev:pack:react`/`dev:pack:vue` pipeline, not a live dev server.
- [ ] Coverage-phase Jest tests (≥90%) pass per component as each test task lands; mutation-phase (Stryker, ≥90%) runs once, consolidated, after every other task (plan Task 23) across all three testable units (`date-engine`, `bds-calendar-grid`, `bds-date-picker`).

**v2 (Phase 2, next sprint):**
- [ ] React/Vue wrapper parity confirmed at the end of Phase 2 (v2 plan Task 7) via the same pipeline.
- [ ] Coverage-phase Jest tests (≥90%) pass for the time-selector additions; mutation-phase (Stryker, ≥90%) re-runs the `date-engine`/`bds-date-picker` configs (v2 plan Task 8) to cover the new files.
