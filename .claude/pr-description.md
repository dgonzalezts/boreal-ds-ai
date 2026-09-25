# PR Title

feat(web-components): EOA-17662 add quick-picker, banner and keyboard navigation

---

# PR Body

## Description

Part 2 of the `bds-date-picker` v3 work, covering TC-23–TC-33 of [Jira Test Plan](https://telesign.atlassian.net/browse/EOA-18534):

- **Month/year quick-picker** — the calendar header's month/year label opens a month grid, then a year grid, as an elevated overlay over the dimmed day grid.
- **Keyboard traversal** — 2D arrow/Home/End navigation, PageUp/PageDown paging, Escape/backdrop return to day view, and live-region announcements.
- **Info banner and footer range summary** — optional dismissible banner and a pluralized days/hours/minutes duration summary in range mode.

## Implementation Details

- New `generateMonthPickerGrid`/`generateYearPickerGrid` generators in `date-engine`, plus `now`/range-bound options on the day grid generator.
- Quick-picker overlays with a nested header and roving tabindex; each `expanded` grid keeps its own independent picker state and resets on preset, clear, and cross-grid day picks.
- Selection state is selection-based (not display-based) and wired for both single and range modes; focus is retained across year-window paging and returns to the day grid on Escape/backdrop.
- Footer summary uses `Intl.PluralRules` for singular/plural unit selection; `renderBanner` and summary helpers use design tokens only, with all new labels optional and English by default.

## Impact Analysis

- Additive to `bds-date-picker` — no breaking API changes; existing usage is unchanged.
- Playground QA examples added to `packages/boreal-web-components/src/index.html`.

## Testing Conducted

**Automated:**

- [x] New suites: quick-picker (`bds-calendar-grid`, `bds-date-picker`), keyboard, banner, range, date-engine grid, a11y navigation
- [x] Full unit suite green (328 suites / 3804 tests)

**Manual (Part 2 scenarios):**

- [x] Banner: `dp-banner-s1`–`s4` (TC-23–TC-26)
- [x] Quick-picker: `dp-quickpicker-s1`–`s4` (TC-27–TC-32)
- [x] Keyboard traversal: `dp-keyboard-s1`–`s3` (TC-33)

## Related Changes

- **boreal-docs**: date-picker stories and MDX updated (quick-picker, banner, keyboard)
- **boreal-react** / **boreal-vue**: no manual changes — wrappers pick up the new props

## Additional Remarks

- Target branch is `release/current`; it is already merged into this branch (`6f66ec5c`), so the PR is conflict-free.
- Playground examples in `index.html` are marked for manual QA (TBD) — remove before merge if the release convention requires a clean playground.

Refs EOA-17662

## Checklist

### General

- [x] Conventional commit format and ticket reference
- [x] TypeScript strict — no `any` or implicit types
- [x] All tests pass locally

### Component Standards

- [x] Design tokens only — no hard-coded colors, spacing, or radii
- [x] `bds-` prefix, explicit prop types, bare `@Event()`, SCSS `@use`

### Testing

- [x] Coverage and mutation thresholds met
- [x] Happy path, error, and edge cases covered; accessibility specs included

### Documentation

- [x] JSDoc on all public APIs
- [x] Storybook story and MDX documentation updated
