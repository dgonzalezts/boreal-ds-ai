# PR Title

fix(web-components): EOA-17138 scope bds-table and bds-calendar-grid CSS to their host elements

---

# PR Body

## Description of the Bug

`bds-table` and `bds-calendar-grid` (used by `bds-date-picker`) each shipped unscoped, top-level `table`/`thead`/`th`/`td` CSS selectors outside their component's host block. Once both components' stylesheets loaded on the same page, each leaked its styles onto the other's tables — most visibly, the date picker's weekday headers ("Sun Mon Tue…") wrapping into single letters per line.

## Root Cause

Stencil compiles bare top-level selectors straight into each component's global stylesheet with no scoping. `bds-table.scss` and `bds-calendar-grid.scss` both had `table { }` / `thead th { }` rules sitting outside their `bds-table { }` / `bds-calendar-grid { }` blocks, so they matched any matching element on the page, not just their own markup.

## Description of the Fix

- Nested all previously top-level selectors (including the BEM class block) under their host tag in `bds-table.scss` and `bds-calendar-grid.scss`, so every selector now compiles as a genuine descendant of `bds-table`/`bds-calendar-grid`.
- Fixed a related specificity bug in `apps/boreal-docs/.storybook/styles/preview.css` (`:not()` → `:not(:where())`) that was overriding Storybook's own props-table styling, and removed two now-dead rules.

## Impact of the Fix

- No visual or behavioral change for either component in isolation — compiled CSS rule/declaration counts are identical before and after (pure scoping change).
- No breaking changes, no API changes.

## Testing Conducted

**Automated:**

- [x] Full `boreal-web-components` unit test suite passing (295 suites / 3,209 tests)
- [x] `prettier --check` clean on all touched files

**Manual:**

- [x] Live-verified in Storybook: navigating Table → Date Picker no longer corrupts the calendar header
- [x] Cross-checked table rendering at full width and 775px against the last-released Chromatic build

## References

Refs EOA-17138

Full investigation, root cause, and verification detail: EOA-17495 (subtask under EOA-17277); local copy at `ai-work/qa/bug-reports/2026-08-27-bds-table-bug-001.md`.

## Checklist

- [x] Follows conventional commit format: `fix(web-components): EOA-17138 description`
- [x] Root cause identified and documented
- [x] Fix addresses the root cause, not just symptoms
- [x] Bug no longer reproducible with the fix applied
- [x] Design tokens preserved — no style regressions
- [x] No console warnings or errors introduced
- [x] No breaking changes introduced
