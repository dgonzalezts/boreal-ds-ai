# Mutation Report — `bds-date-picker` (EOA-17662 Tasks 53a/53d)

**Status:** ⏳ v3 mutation pass **deferred** → `ai-work/tickets/EOA-17662-53d-bds-date-picker-mutation.md` (contains the exact config + reproduction steps).

The v1 baseline (2026-08-19, 93.33%) is preserved verbatim in
`v1-baseline-2026-08-19/mutation-bds-date-picker.md`.

## Why deferred

The full pass is **897 mutants** (after `mutator.excludedMutations: [StringLiteral, ObjectLiteral,
ArrowFunction, BlockStatement]`, down from 1300) and projects **~7 hours** on the 11-core/18GB dev
machine; it exhausted memory (102 MB free, 8 GB compressed). Retunes did not reduce the per-mutant
cost:

- `jest.enableFindRelatedTests: false` let `coverageAnalysis: 'perTest'` select per-mutant covering
  tests, but every mutant still runs a large share of the component's 523 tests because all 16 spec
  files import `bds-date-picker.tsx`.
- `timeoutMS: 10000` halved the timeout cost (`timeoutMS: 30000` → `10000`).

## Partial signal (aborted retuned run, not representative)

44/897 mutants tested before it was stopped: 7 survived, 13 timed out. Insufficient to characterize
the Phase 5-9 gap — treat the area as **unmeasured** until the deferred run completes. Raw partial
log: `run-bds-date-picker-partial-2026-09-25.log`.
