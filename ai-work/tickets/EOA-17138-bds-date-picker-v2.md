# EOA-17138 — bds-date-picker v2 (Phases 2-4)

**Ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138)
**Status:** In Progress
**Goal:** Complete the version 2 foundation for `bds-date-picker` by delivering Phases 2-4 only: time-selector baseline, min/max constraints, and range-mode orchestration/styling foundations.

## Scope

**In:**

- Phase 2: single-date time selector with timezone-aware UTC value support.
- Phase 3: min/max constraint behavior, disabled-day handling, month-navigation guard, validation messaging behavior.
- Phase 3.5: `calendarType` foundation (`default` / `basic` / `expanded`) and default-mode behavior.
- Phase 4: range-mode value contract and dual/single-calendar orchestration foundations, including range visuals and form-association alignment.

**Out:**

- Phases 5-9 and final mutation consolidation (moved to EOA-17662 / version 3).
- Keyboard-typed date entry in the trigger field (still deferred).

## Acceptance Criteria

- [ ] Existing single-date behavior remains non-breaking when range/time features are not enabled.
- [ ] `withTime` supports UTC datetime value mode and preserves expected formatting behavior.
- [ ] `min`/`max` constraints disable out-of-range dates and prevent invalid month navigation targets.
- [ ] `calendarType` controls default/basic/expanded presentation and behavior as defined.
- [ ] `range` value shape and rendering foundations are in place for later feature expansion.
- [ ] Foundation changes pass unit tests and wrapper parity checks for the covered phases.

## Dependencies

- Requires version 1 foundational work (EOA-16692) to remain intact.
- Reuses existing date-engine and calendar-grid primitives introduced in prior phases.

## Notes

- This ticket is now strictly a v2 foundation ticket.
- Remaining roadmap scope continues under EOA-17662 as version 3.
