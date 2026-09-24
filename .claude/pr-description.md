# PR Title

feat(web-components): EOA-17662 add range-mode time selection and presets sidebar to bds-date-picker

---

# PR Body

## Description

Extends `bds-date-picker`'s range mode with time-of-day selection and a built-in date presets sidebar.

- **Range-mode time selection**: `basic` calendar type gets a single shared time field applied to both range bounds; `expanded` calendar type gets independent start/end time fields.
- **Presets sidebar**: a fixed list of six relative-date presets (Today, Yesterday, Last 7 days, Last 30 days, This month, Last month) plus a Custom state, shown alongside the calendar(s) in range mode. Selecting a preset computes and applies the corresponding range and navigates the calendar to it; any manual edit to the draft reverts selection to Custom.

## Impact Analysis

- Purely additive to `bds-date-picker`'s existing range-mode API — no breaking changes to single-date or non-range usage.
- `labels` prop gains optional preset button-text overrides; all new fields are optional with English defaults.
- Minor unrelated fix: `bds-popover` cleanup included in this branch.

## Testing Conducted

**Automated:**

- [x] Unit tests for the dual/single time selector and its draft-state logic
- [x] Unit tests for preset range computation and the presets sidebar (selection, bounds-checking, calendar navigation on click)
- [x] Coverage and mutation thresholds met per project quality gates

**Manual:**

- [x] Verified in Storybook across `basic`/`expanded` calendar types, with/without `withTime`, and with `min`/`max` bounds restricting preset availability

## Related Changes

- **boreal-docs**: Storybook story and MDX documentation updated for both features
- **boreal-react** / **boreal-vue**: no manual changes needed — wrappers pick up the new props automatically

## Design Decisions

Two architecture decisions were made as part of this work:

- **Localizable UI copy prop shape**: a threshold rule — a component with a single localizable string uses a flat `@Prop() <name>Label`, two or more uses a bundled `labels` object. The `labels` prop's growth in this PR (preset button-text overrides) follows this rule; no shipped component's API changes as a result.
- **Preset date/time coverage semantics**: with `with-time` on, each preset's submitted end boundary is shifted to the start of the day after its last real day (e.g. "Last 7 days" submits an end of tomorrow at `00:00`), producing an exact whole-day-multiple duration identical across both calendar types. The calendar grid still highlights only the real days; the popover header and trigger field always display the same shifted boundary that gets submitted, so nothing silently disagrees.

## Additional Remarks

This PR covers range-mode time selection and the presets sidebar only. Still outstanding for `bds-date-picker` and out of scope here:

- Info banner and footer range summary
- Full keyboard navigation, accessibility, and RTL audit
- Month/year quick-picker
- Presets are a fixed built-in list — no consumer-configurable presets API in this PR

## References

Refs EOA-17662

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [x] Ticket reference included (`Refs` EOA-17662)
- [x] Code adheres to TypeScript strict mode — no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally

### Boreal DS — Component Standards

- [x] Design tokens used exclusively — no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()` (no `bubbles`/`composed` unless required)
- [x] SCSS follows `@use` pattern (no `@import`)

### Boreal DS — Form Components

- [x] Implements `IFormControl<T>` interface (unchanged from prior work)
- [x] Validation unaffected by new range/preset behavior

### Testing

- [x] Unit test coverage ≥ 90% statements
- [x] Tests cover happy path, error cases, and edge cases (min/max bounds, custom fallback)
- [x] Manual testing completed in Storybook

### Documentation

- [x] JSDoc added to all public APIs (props, events, methods)
- [x] Storybook story updated with usage examples
- [x] Storybook MDX documentation updated

### Performance & Compatibility

- [x] No new console warnings or errors
- [x] No regression in existing functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01MmVJGQ2qQTnHmRR8RjitFx
