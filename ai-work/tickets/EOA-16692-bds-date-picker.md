# EOA-16692 — bds-date-picker (v1: Phases 0–1)

**Ticket:** EOA-16692 ("Implement Date Picker v1") — Phase 0–1, done
**v2 ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — dedicated Jira story, sibling to EOA-16692 under the same parent Feature (EOA-14927), linked "relates to" EOA-16692. Own ticket brief: [`ai-work/tickets/EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md)
**Status:** Done
**Goal:** Ship the foundational date-picker contract (`date-engine` + `bds-calendar-grid`) and a working single-date, optional-time `bds-date-picker` component.

**Scope split (2026-08-19):** due to sprint time constraints, Phase 2 (the time selector) was moved out of this v1 plan into its own `v2` plan under a dedicated Jira story, EOA-17138. This file now covers Phase 0–1 only (single-date picker, no time) and is done. v2's full scope (Phases 2–9, further expanded 2026-08-24) is tracked in its own ticket brief, linked above — split out on 2026-08-24 so each ticket's scope, acceptance criteria, and open questions stay independently readable rather than interleaved in one file.

**Spike doc:** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — cross-cutting architecture decisions (no calendar library, `<table role="grid">` markup, component decomposition, single-vs-range component) live there, not duplicated here.

**Plans:**

- [`ai-work/plans/EOA-16692-bds-date-picker-v1.md`](../plans/EOA-16692-bds-date-picker-v1.md) — Phase 0–1, ticket EOA-16692 (`done`)
- v2 plan and ticket now live separately — see [`ai-work/tickets/EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md)

## Scope

**In:**

- `date-engine` service: pure `date-fns`-based month-grid generation, date math, locale-aware formatting — framework-agnostic, no Stencil/DOM.
- `bds-calendar-grid`: dumb, controlled, presentational custom element rendering a native `<table role="grid">` (month/year header + nav, weekday row, day grid). Registered component with full test suite; documented only as an internal note inside `bds-date-picker.mdx` (no standalone story/MDX).
- `bds-date-picker`: orchestrator composing `bds-text-field` (display trigger) + `bds-popover` (floating panel) + `bds-calendar-grid`. Controlled public `value`/`bdsChange`/`valueChange`, internal draft state until Apply, Clean/Cancel/Apply footer, FACE-compliant.
- `locale` prop (raw `date-fns` `Locale` object) and `timezone` prop (IANA string, default = browser resolved timezone).

**Out:** everything covered by v2 (time selector, min/max, range, dual time, presets, banner, keyboard/a11y/RTL, quick-picker) — see [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md).

## Acceptance Criteria

- [x] `date-engine` has zero Stencil/DOM imports and is covered by plain-Jest unit tests; never re-exports `date-fns` or its `Locale` type by import path from its public barrel.
- [x] `bds-calendar-grid` renders as a native `<table role="grid">` (not div+CSS-Grid) and owns no selection state; day-click and month-nav are emitted upward, `displayMonth` is passed back down by the parent.
- [x] `bds-date-picker` public `value` is canonical ISO 8601 — `yyyy-MM-dd` naive.
- [x] Day clicks mutate only internal draft state; `value`/`bdsChange`/`valueChange` fire only on Apply.
- [x] Cancel reverts draft to last committed value and closes the popover without emitting.
- [x] Clean clears the draft **and commits immediately** (empties `value`, emits with `''`, closes popover).
- [x] `bds-date-picker` is form-associated (FACE) following the `bds-text-field.tsx` pattern.
- [x] `hideArrow` prop (default `false`) is a genuine opt-in override piped into `floatingOptions.hideArrow`, unlike `bds-select`'s hardcoded `true`. Default flipped from the originally-specified `true` to `false` (2026-08-18 decision) to comply with the codebase's `stencil/ban-default-true` ESLint rule — the popover's arrow now renders by default and must be explicitly hidden via `hide-arrow="true"`.
- [x] The popover's `placement` is a fixed `bottom-start` (not user-configurable, not left to `bds-popover`'s own `bottom` default) — matches the reference calendar-dialog design. Added 2026-08-18, not in the original ticket scope — caught via design reference review during Task 14.
- [x] The popover renders a header row (`header={true}`/`closable={true}`, hardcoded calendar-dots icon, title bound live to the draft/committed date, falling back to a new `headerPlaceholder` prop — default `'Select a date'` — when empty). Added 2026-08-19, not in the original ticket scope — caught via the same design reference review; see the spike doc's Resolved Decisions table for the full rationale.
- [x] Component registered under the `forms` docs category.
- [x] Default `format` is `yyyy/MM/dd`.

## Dependencies

- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` added as new runtime dependencies of `packages/boreal-web-components` (verified against `package.json`, not recalled). Reused by v2, not re-added.
- Existing `bds-text-field`, `bds-popover`, `formAssociatedMixin`/`useFormField`, `KeyboardController` are reused, not modified (unless a documented gap is found).

## Open Questions — resolved

- Outside-month day cell interactivity (clickable-but-muted vs. inert) — resolved: checked against Figma at implementation time.
- `useFormField` vs. `formAssociatedMixin` currency — resolved: checked which recently built form components adopted before wiring FACE.
- `@Listen()` vs. runtime `addElementListener` for `bds-calendar-grid` event wiring inside `bds-popover`'s slotted content — resolved.
- Field label ownership (`bds-text-field`'s built-in label vs. a `bds-date-picker`-owned one) — resolved.
- Translatable footer button text convention (`labels` prop vs. named slots) — resolved: checked existing i18n precedent first.

## Quality Gates

- [x] React/Vue wrapper parity confirmed at the end of Phase 1 (plan Task 22) via the `dev:pack:react`/`dev:pack:vue` pipeline, not a live dev server.
- [x] Coverage-phase Jest tests (≥90%) pass per component as each test task lands; mutation-phase (Stryker, ≥90%) ran once, consolidated, across all three testable units (`date-engine`, `bds-calendar-grid`, `bds-date-picker`).
