# PR Title

feat(web-components): EOA-16692 add bds-date-picker foundation and single-date picker

---

# PR Body

## Description

Implements the foundation and single-date behavior of `bds-date-picker` (ADR-0003 Phases 0–1): a framework-agnostic `date-engine` service, a presentational `bds-calendar-grid` custom element, and the `bds-date-picker` orchestrator itself — a form-associated, draft-until-Apply date picker composing a consumer-supplied `bds-text-field` trigger with a `bds-popover` panel.

This PR does **not** include the time selector (Phase 2) — that scope was split out to its own follow-up ticket/plan (see References) due to sprint time constraints, since nothing in it had been implemented yet.

## Implementation Details

- **`date-engine`** (`src/services/date-engine/`): pure `date-fns`-based month-grid generation, date math, and locale-aware formatting. Zero Stencil/DOM imports; only its own `DateEngineLocale` alias is exposed through the public barrel — no `date-fns` types leak out.
- **`bds-calendar-grid`**: dumb, controlled, presentational element rendering a native `<table role="grid">` (WAI-ARIA APG pattern) rather than a div/CSS-Grid construction, for accessibility semantics "for free." Owns no selection state — day-click and month-nav events are emitted upward; the parent passes the displayed month back down.
- **`bds-date-picker`**: orchestrator composing a **consumer-supplied** `<bds-text-field slot="field">` trigger (not self-rendered — mirrors `bds-select`'s pattern, discovered mid-implementation to be necessary so consumers can configure `label`/`icon`/`helperText`/etc. themselves) with a `bds-popover` panel containing the calendar grid and a Clean/Cancel/Apply footer. Selection is held in internal draft state until Apply; `value`/`bdsChange`/`valueChange` only fire on Apply. Form-associated via `formAssociatedMixin` + `ElementInternals`, with a single `valueMissing` validator for `required`.
- **`bds-popover` enhancement**: added four new CSS custom-property hooks (`--popover-header-padding`, `--popover-header-content-gap`, `--popover-content-padding`, `--popover-footer-padding`), each defaulting to the pre-existing hardcoded value — non-breaking for `bds-select`/`bds-dropdown`/`bds-search-bar`. This was the chosen alternative to `bds-date-picker` reaching into `bds-popover`'s internally-rendered markup with plain selectors, which doesn't work reliably in this project's non-shadow-DOM component model.
- All spacing/sizing/typography in `bds-calendar-grid.scss`/`bds-date-picker.scss` sourced from live Figma pulls against the `Basic`+`Range:off` single-date `calendarPicker` variant, not inferred — see the plan doc for the full research trail.

## Impact Analysis

- New components — no impact on existing component behavior.
- `bds-popover.scss`/`bds-popover.tsx` are modified but additive-only (new opt-in custom-property hooks + a header row already exposed via existing `header`/`closable` props); default rendering for every other `bds-popover` consumer is unchanged, confirmed via manual QA.
- New runtime dependencies: `date-fns@^4.4.0`, `@date-fns/tz@^1.5.0` (the latter used starting in the Phase 2 follow-up, added now since both ship together).
- Framework wrappers (`boreal-react`, `boreal-vue`) will auto-generate for the new components.

## Testing Conducted

**Automated:**

- [x] `date-engine` unit tests (plain Jest): month-grid generation, date math, locale-aware formatting — 100% coverage
- [x] `bds-calendar-grid` unit tests (`newSpecPage`): basics, events, variants, a11y — 100% coverage
- [ ] `bds-date-picker` consolidated unit tests — not yet written (next task in the plan)
- [ ] Mutation testing (Stryker) — deferred to the plan's final task, not yet run

**Manual:**

- [x] Live-verified in Chromium and WebKit via Playwright across every task in this PR: popover open/close, draft-until-Apply day selection, Clean/Cancel/Apply commit semantics, form participation (`FormData`, reset, validity), `disabled`/`hideArrow`/custom `format`/`locale`, and the header row's live date binding
- [x] Popover panel dimensions/padding/footer spacing verified against compiled CSS output, not just source, against the Figma-confirmed 296×434px spec
- [x] Zero new console errors/warnings across every scenario in the `index.html` playground
- [ ] Storybook/Chrome/Firefox/Safari/Edge cross-browser pass — deferred to the plan's documentation task
- [ ] Screen reader verification — not yet performed

## Related Changes

- **No changes to** `boreal-styleguidelines` — reused existing `$boreal-*` tokens throughout, including for the new `bds-popover` custom-property defaults.
- **`boreal-docs`**: no Storybook story/MDX yet — planned as a follow-up task in this same PR's remaining scope (see Additional Remarks).

## Additional Remarks

- **This PR is a work-in-progress checkpoint, not the full Phase 1 scope.** Remaining before Phase 1 is complete: consolidated unit tests, Storybook/MDX documentation, and a React/Vue wrapper parity check (Tasks 20–22 in the plan below). Recommend keeping this as a **draft PR** until those land.
- Two real bugs were found and fixed during implementation, both filed for visibility even though fixed inline: a `bds-calendar-grid` day-highlight cross-fade artifact caused by an unscoped CSS transition (fixed), and an 8px calendar-grid overflow inside the popover caused by `border-spacing` adding edge gaps that Figma's flex-gap layout doesn't have (fixed, `bds-calendar-grid.scss`).
- One defect was found, filed, but **not** fixed here (out of scope, lives entirely in `bds-popover.tsx`): the popover header's close button has no accessible name — tracked as [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133).
- Full task-by-task history, including every design decision, Figma research pull, and QA round, is recorded in `ai-work/plans/EOA-16692-bds-date-picker-v1.md`.
- Phase 2 (time selector) was moved to its own plan/ticket this sprint due to time constraints — see References.

## References

Refs EOA-16692
Refs EOA-17138 (Phase 2 — time selector, follow-up, not in this PR)

Plan: `ai-work/plans/EOA-16692-bds-date-picker-v1.md`

---

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [x] Ticket reference included (`Refs` EOA-16692)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally (`tsc --noEmit`, `eslint`, `stencil build` clean throughout)

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tags use `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()` (no `bubbles`/`composed` unless required)
- [x] SCSS follows project convention (no `@use` of the token package; tokens injected globally)
- [x] Light DOM patterns documented (native `<table role="grid">`, consumer-supplied slotted trigger field)

### Boreal DS — Form Components

- [x] Uses `formAssociatedMixin` for FACE boilerplate
- [x] Implements `IFormControl<string>` interface
- [x] Includes `@Method()` wrappers for `checkValidity()` and `reportValidity()`
- [x] Validation tested with the built-in `required`/`valueMissing` validator

### Testing

- [ ] Unit test coverage ≥ 90% statements — done for `date-engine`/`bds-calendar-grid`, pending for `bds-date-picker`
- [x] Tests cover happy path, error cases, and edge cases (for the units already tested)
- [x] Accessibility verified for `bds-calendar-grid` (dedicated a11y spec file)
- [x] Manual testing completed in Chromium and WebKit

### Documentation

- [ ] JSDoc added to all public APIs — done for `bds-date-picker`/`bds-calendar-grid`; not yet audited against the finalized SCSS
- [ ] Storybook story created — pending
- [ ] Storybook MDX documentation added — pending
- [ ] README updated — n/a, no README change needed

### Performance & Compatibility

- [x] No new console warnings or errors (one known, filed, out-of-scope warning: EOA-17133)
- [ ] Bundle size impact assessed — not yet measured
- [x] Compatible across Chromium and WebKit (manually verified); Firefox/Edge not yet checked
- [x] No regression in existing functionality (verified for `bds-popover`'s other consumers)
