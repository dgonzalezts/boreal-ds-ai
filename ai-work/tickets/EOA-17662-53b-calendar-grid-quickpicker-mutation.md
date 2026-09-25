# EOA-17662 (Task 53b) — `bds-calendar-grid` quick-picker mutation-test coverage remediation

**Parent:** [EOA-17662](https://telesign.atlassian.net/browse/EOA-17662) (Tasks 53/53a consolidated mutation testing)
**Status:** Open / deferred (logged 2026-09-25)
**Origin:** discovered executing Tasks 53/53a; re-scoped here with user sign-off 2026-09-25.

## Goal

Close the Phase 9 quick-picker mutation-test coverage gap in `bds-calendar-grid.tsx` (bring it to ≥90%), so the EOA-17662 mutation gate can be closed for that area.

## Context

The consolidated Stryker pass (verified re-run) scored `bds-calendar-grid` **77.43%** — 849 killed / 213 survived / 36 no-coverage / 5 timeout. `git blame` shows every `bds-calendar-grid.tsx` survivor is Phase 8/9/10; there are **zero v2 survivors** (the v2 range logic is fully covered). The Phase 8 keyboard/a11y survivors were fixed in Task 53a; the Phase 9 quick-picker survivors are a large, real, weak-assertion gap and are re-scoped here.

## Scope / survivor map (bucketed by `git blame`)

See `ai-work/qa/mutation-reports/TRIAGE-NOTES-eoa17662.md` and `mutation-bds-calendar-grid.md`.

| Commit | Feature |
| --- | --- |
| `49d25ed6` | drill-down, view reset, and the `getPriority*Cell` focus-priority cluster (lines 611-636) |
| `aa1f1ad2` | `PageUp`/`PageDown` paging |
| `39c3fae4` | `<table>`-based picker rendering |
| `21be7773` | month/year drill-down |
| `f255e94b` | quick-picker nested header |
| `95c3704a` | picker selected state for range mode |
| `29a5dd9d` | Task 55a `CALENDAR_GRID_VIEW` constants |
| `b87e9ec4` | overlay superposition |

Extract the current per-line list from the latest run log by re-running the triage script (`triage.sh`, attached to the EOA-17662 worktree during execution) or `git blame`-ing each `[Survived]` line.

## Acceptance criteria

- Every Phase 9 quick-picker survivor is killed by a new assertion in `bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts`, or documented as an equivalent mutant with reasoning.
- `bds-calendar-grid.tsx` reaches ≥90% under a `stryker.bds-calendar-grid.config.mjs`-style run.

## Notes

- Do not regress the Phase 8 keyboard tests added in Task 53a.
- Dev machine is 11-core/18GB — keep Stryker `concurrency: 2` and Jest `maxWorkers: 1` (see `.agents/memory/mutation-testing-workflow-decisions.md`).
- Consider `enableFindRelatedTests: false` and `mutator.excludedMutations` if runtime is an issue.
