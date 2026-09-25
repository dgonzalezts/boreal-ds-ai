# EOA-17662 (Task 53c) — `grid-navigation.ts` pre-existing mutation debt (owner: EOA-10530)

**Parent surfaced under:** [EOA-17662](https://telesign.atlassian.net/browse/EOA-17662) (Tasks 53/53a consolidated mutation testing)
**Owner ticket:** EOA-10530 (keyboard-navigation core) — **not** EOA-17662.
**Status:** Open / deferred (logged 2026-09-25)

## Goal

Close the pre-existing mutation-test gaps in `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts`.

## Context

Surfaced while mutation-testing `bds-calendar-grid` for EOA-17662 (the file was folded into that config because Phase 9 modified its `onActivate` guard). Of the 52 survivor lines, **50 blame to `ea4d3d76` (2026-05-20, EOA-10530)** — pre-existing shared-utility code, never mutation-tested before due to EOA-17662. Only lines 233/236 (the Phase 9 `onActivate` guard) belong to EOA-17662 and were fixed in Task 53a.

Score: `grid-navigation.ts` **72.14%** (229 killed / 59 survived / 31 no-coverage / 4 timeout).

## Acceptance criteria

- `grid-navigation.ts` reaches ≥90% (or all survivors documented as equivalents with reasoning) under a config whose `mutate` is `grid-navigation.ts` and whose Jest `testMatch` is `src/utils/a11y/keyboard/__test__/navigation.spec.ts`.
- No regression to `bds-calendar-grid`'s keyboard behavior.

## Notes

- Machine is 11-core/18GB — Stryker `concurrency: 2`, Jest `maxWorkers: 1`.
- `mock-doc` ignores `AbortSignal`, so keyboard-listener teardown mutants must be verified via a spy on `KeyboardController.detach()` (see `.agents/memory/mutation-testing-stryker-setup.md`).
