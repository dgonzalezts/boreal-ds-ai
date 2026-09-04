# PR Title

feat(web-components): EOA-17138 add bds-date-picker v2 (time, min/max, calendarType, range)

---

# PR Body

## Description

Implements `bds-date-picker` v2 (Phases 2–4 of ADR-0003): a timezone-aware time selector, min/max date constraints, the `calendarType` foundation (`default` | `basic` | `expanded`), and range-mode dual-calendar orchestration — without breaking v1's single-date, naive-date `value` contract.

## Implementation Details

- **Phase 2 — Time selector:** timezone-aware date-time → UTC ISO conversion in `date-engine`, plus a new `renderTimeSelector.tsx` composed into the existing popover.
- **Phase 3 — Min/max constraints:** wires already-existing `date-engine`/`bds-calendar-grid` capacity (`isWithinRange`, `compareDates`, `DayCell.isDisabled`) into `bds-date-picker`, with nav guards and helper text.
- **Phase 3.5 — `calendarType` foundation:** new prop (default `'basic'`, non-breaking) adding `default` mode's immediate-commit, chrome-less interaction — a prerequisite for range behavior.
- **Phase 4 — Range mode:** new `range: boolean` prop, independent of calendar count; a second `bds-calendar-grid` is gated on `calendarType === 'expanded'` only. Public `value` becomes `string | { start: string; end: string }` when `range` is on. Includes continuous-band styling, hover-preview band, and FACE validity/form submission for range values.
- Light DOM throughout (ADR-0001); no external calendar library.

## Impact Analysis

- Additive — v1's single-date, naive-date `value` contract is unchanged for existing consumers.
- `bds-table`/`bds-calendar-grid` CSS scoping fix (unscoped selectors were leaking styles between the two components) landed as part of this branch.
- Several Safari/WebKit-specific fixes: popover outside-click/focus race with the Apply click, today-indicator border clipped by range background.
- No breaking API changes.

## Testing Conducted

**Automated:**

- [x] Unit tests added per phase (time selector + date-engine conversion, min/max, calendarType, range) with the two-phase coverage/mutation gate
- [x] Full `boreal-web-components` suite passing post-merge with `release/current`

**Manual:**

- [x] QA pass per phase across web-components, React, and Vue playgrounds
- [x] Cross-browser check surfaced and fixed the Safari popover/Apply race and range-background/today-indicator clipping

## Related Changes

- **boreal-react** / **boreal-vue**: wrapper parity checked and fixed per phase (including a min/max initial FACE-validity race in the framework wrappers)
- **boreal-docs**: Storybook stories and MDX documentation added per phase (time selector, min/max, calendarType, range mode)

## Additional Remarks

- Keyboard-typed date entry in the trigger field remains explicitly out of scope.
- Phases 5–9 (range time, presets, banner/summary, keyboard/a11y/RTL, month/year quick-picker) moved to v3 under EOA-17662.
- Two `bds-popover` follow-ups discovered during this work (coverage backfill, CSS custom-property-inheritance browser test) were re-scoped into their own tracked plans rather than bundled here.
- Full plan: `ai-work/plans/EOA-17138-bds-date-picker-v2.md`

## References

Closes EOA-17138

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): EOA-17138 description`
- [x] Ticket reference included (`Closes EOA-17138`)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] All tests pass locally

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] SCSS follows `@use` pattern (no `@import`)
- [x] Light DOM patterns documented

### Boreal DS — Form Components

- [x] Uses formAssociatedMixin for FACE boilerplate
- [x] Validation tested (min/max, required, range) with built-in validators

### Testing

- [x] Unit test coverage ≥ 90% statements per phase
- [x] Tests cover happy path, error cases, and edge cases
- [x] Manual testing completed across web-components, React, and Vue

### Documentation

- [x] JSDoc added to all public APIs (props, events, methods)
- [x] Storybook story created with usage examples
- [x] Storybook MDX documentation added (usage, API, examples)

### Performance & Compatibility

- [x] No new console warnings or errors
- [x] Compatible across supported browsers (Chrome, Firefox, Safari, Edge) — Safari-specific regressions found and fixed
- [x] No regression in existing functionality
