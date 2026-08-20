# PR Title

test(web-components): EOA-16692 add Phase 1 unit tests for bds-date-picker

---

# PR Body

## Description of Test Changes

Adds the consolidated Phase 1 unit test suite for `bds-date-picker` (Task 20 of `ai-work/plans/EOA-16692-bds-date-picker-v1.md`), split across six spec files by concern plus a shared test-utils helper. Base branch for this PR is `feature/EOA-16692_bds-date-picker-v1_DG` — this branch was created off it specifically for the test-writing work, per the plan's task sequencing.

## Motivation

- **Coverage gap**: `bds-date-picker.tsx` had zero automated coverage — every behavior from Tasks 14–19 (trigger wiring, draft-until-Apply, footer actions, FACE, styling) was previously verified manually only.
- **Quality gate**: the plan's own two-phase test gate requires ≥90% coverage before the consolidated mutation-testing pass (Task 23) can run.
- **Regression risk closed early**: writing these tests surfaced two real, confirmed bugs before they could ship — see Additional Remarks.

## Test Coverage Added

**New spec files** (`packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/`):

- `bds-date-picker.basics.spec.ts` (18 tests) — trigger open/close, `disabled`/`hideArrow`, missing-slotted-field warning, `selectable`/`disabled` sync
- `bds-date-picker.events.spec.ts` (20 tests) — draft-until-Apply lifecycle, Apply/Cancel/Clean semantics, the Apply-with-no-selection fix, slotted field's `valueChange`/`bdsClear` integration
- `bds-date-picker.form.spec.ts` (14 tests) — `FormData` participation, `formResetCallback`, `required`/`reportValidity()`
- `bds-date-picker.variants.spec.ts` (10 tests) — custom `format`/`locale`, `disabled` cascading
- `bds-date-picker.keyboard.spec.ts` (7 tests) — Tab reachability, Enter/Space popover activation (see Additional Remarks)
- `bds-date-picker.a11y.spec.ts` (7 tests) — `aria-haspopup`/`aria-expanded`, footer button labels
- `date-picker.test-utils.ts` — shared `renderDatePicker`/`openDatePicker`/`findDayCell`/`findFooterButton` helpers

**Coverage on `bds-date-picker.tsx`:**

- **Statements**: 98.23% (111/113)
- **Functions**: 100% (28/28)
- **Lines**: 98.23% (111/113)
- **Branches**: 87.75% (43/49) — the uncovered branches are `this.bdsPopover?.`/`this.bdsField?.` null-fallback paths that are structurally unreachable, since `<bds-popover>` is unconditionally part of this component's own `render()`.

## Type of Test Change

- [x] New unit tests (Stencil spec tests)
- [ ] New integration tests (E2E tests)
- [ ] Fixed failing tests
- [ ] Updated tests to match implementation changes
- [ ] Improved test quality (better assertions, edge cases)
- [ ] Refactored tests (no coverage change)

## Testing Approach

Uses `newSpecPage` throughout (Stencil component tests, not React Testing Library). Every fixture slots a `<bds-text-field slot="field">` trigger, matching the Architecture Correction that made the trigger consumer-supplied rather than self-rendered. Follows the split-spec-file convention already established by `bds-calendar-grid`'s own tests and `bds-toggle`/`bds-tab-group` — one file per concern, no duplicate assertions across files.

## Test Code Quality

- Shared `date-picker.test-utils.ts` extracts fixture rendering, popover opening, and day/button lookup to remove boilerplate across all six spec files.
- No ticket ID or task-number references inside any spec file — `describe`/`it` names describe behavior only, per project convention.
- No inline comments in test files explaining what code does.

## Additional Remarks

**Two real bugs were found and fixed while writing this suite, both included in this PR's commits:**

1. **Apply committed an empty value when nothing was ever selected.** `handleFooterAction`'s `APPLY` case unconditionally called `commitValue(this.draft.selectedDate ?? '')`, so clicking Apply on an untouched draft (e.g. after only clicking an inert outside-month cell) silently overwrote `value` with `''` and emitted `bdsChange`/`valueChange` — contradicting a requirement already written into this same Task 20 spec ("Apply with no draft selection... does not change value and does not emit"). Fixed on the base branch (`feature/EOA-16692_bds-date-picker-v1_DG`, not part of this PR's diff) before this branch was created from it.
2. **Enter/Space never opened the popover.** `bds-popover`'s own `KeyboardController` unconditionally early-returns whenever `managed={true}` (which `bds-date-picker` always sets), so only mouse click worked — contradicting an explicit "baseline keyboard operability ships in Phase 1" commitment in the spike doc. Fixed in this PR: a `keydown` listener on the slotted trigger field mirrors the existing `click` listener. **This PR is therefore not strictly test-only** — it includes this small, test-discovered implementation fix plus a follow-up type correction (the listener needed `(event: Event)` + an internal cast to satisfy `addElementListener`'s signature under `strictFunctionTypes`, matching `bds-search-bar.tsx`'s existing convention — this repo's own `tsc` invocation has strict mode off project-wide, so the mismatch wasn't caught until checked explicitly).

Not covered here (out of scope for Task 20, tracked elsewhere):
- Mutation testing (Stryker) — deferred to the plan's Task 23, a separate consolidated pass across all three testable units.
- Storybook/MDX documentation — Task 21, not yet started.
- React/Vue wrapper parity — Task 22, not yet started.
- Full arrow-key grid navigation inside the calendar — explicitly deferred to Phase 8.

## References

Refs EOA-16692

---

## Checklist

### General

- [x] Follows conventional commit format: `test(scope): TICKET-ID description`
- [x] Ticket reference included
- [ ] No implementation changes (test-only PR) — **not applicable**, see Additional Remarks: one small, test-discovered keyboard-operability fix (plus its type correction) is bundled in
- [x] All tests pass locally (97 tests, 1 todo, 10/10 suites)

### Test Quality

- [x] Tests follow AAA pattern (Arrange, Act, Assert)
- [x] Test names clearly describe what is being tested
- [x] Each test verifies one specific behavior
- [x] Assertions are specific and meaningful
- [ ] No flaky tests (runs 10 times without failure) — not explicitly re-run 10× as part of this PR; single-run pass confirmed multiple times across iterations

### Test Coverage

- [x] Coverage increased or maintained (no decrease) — 0% → 98.23% statements on `bds-date-picker.tsx`
- [x] Critical paths are tested (happy path + error path)
- [x] Edge cases covered (Apply with no selection, missing slotted field, disabled cascading)
- [x] Async behavior tested correctly (`waitForChanges`)
- [x] Error scenarios tested (invalid/empty required field, missing field warning)

### Boreal DS Testing Standards

- [x] Uses `newSpecPage` for Stencil component tests
- [x] ElementInternals mocked correctly for FACE tests
- [x] No hard-coded timeouts (uses `waitForChanges`)
- [x] Test isolation maintained (no shared state between tests)

### Test Coverage Metrics

- [x] Statement coverage ≥ 90% (98.23%)
- [x] Branch coverage ≥ 80% (87.75%)
- [x] Function coverage ≥ 90% (100%)
- [x] Line coverage ≥ 90% (98.23%)
- [x] Coverage report reviewed (no unexpected gaps — remaining branches are structurally unreachable null-fallback paths)

### Test Maintainability

- [x] Test code is readable and well-structured
- [x] Helpers extracted for repeated setup/teardown (`date-picker.test-utils.ts`)
- [x] Test data is clear and representative
- [x] Tests are independent (can run in any order)
- [x] No commented-out test code
