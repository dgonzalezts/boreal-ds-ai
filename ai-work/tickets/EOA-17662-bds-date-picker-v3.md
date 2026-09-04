# EOA-17662 — bds-date-picker v3 (Phases 5-9)

**Ticket:** [EOA-17662 "Date Picker - Version 3"](https://telesign.atlassian.net/browse/EOA-17662)
**Status:** Open
**Goal:** Deliver the remaining roadmap scope for `bds-date-picker` by completing Phases 5-9 and the final consolidated mutation test gate.

## Scope

**In:**

- Phase 5: range-mode time selection (`basic` shared-time and `expanded` dual-time).
- Phase 6: presets sidebar (including configurability decision and implementation).
- Phase 7: info banner and footer range summary behavior.
- Phase 8: keyboard traversal, accessibility live-region updates, and RTL parity.
- Phase 9: month/year quick-picker drill-down flow.
- Final consolidated mutation testing for all v3-delivered areas.

**Out:**

- v2 foundation work (Phases 2-4), which remains tracked under EOA-17138.
- Keyboard-typed date entry in the trigger field (still deferred).

## Acceptance Criteria

- [ ] Phase 5 time behavior works in both `basic` and `expanded` range configurations with correct UTC value output.
- [ ] Presets sidebar behavior and selection flow are implemented with documented API decision.
- [ ] Banner and range-summary behavior are implemented and consistent across calendar types where applicable.
- [ ] Keyboard + a11y + RTL behavior meets parity and regression expectations.
- [ ] Quick-picker drill-down flow is validated and implemented as internal grid behavior.
- [ ] React/Vue wrapper parity is verified per phase.
- [ ] Final mutation gate runs once for v3 scope and meets threshold or documents justified exceptions.

## Dependencies

- Depends on v2 foundation already established in EOA-17138.
- Reuses date-engine, bds-calendar-grid, and bds-date-picker scaffolding delivered in earlier versions.

## Notes

- This ticket is the continuation point for all remaining Date Picker roadmap work after v2 split.
