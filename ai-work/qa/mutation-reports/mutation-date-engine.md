# Mutation Report — `date-engine` (EOA-17662 Tasks 53/53a, v3 re-run)

**Run:** 2026-09-25, worktree `.worktrees/mutation-eoa17662`, Stryker 10.0.0, Jest runner,
`coverageAnalysis: 'perTest'`, `mutate` = `date-math.ts`, `grid.ts`, `format.ts`, `value.ts`.
Config: `stryker.date-engine.config.mjs` (local-only). v1 baseline preserved in
`v1-baseline-2026-08-19/mutation-date-engine.md`.

## Result: **94.71%** (≥90% floor met)

| File | Score | Killed | Timeout | Survived | No coverage |
| --- | --- | --- | --- | --- | --- |
| All files | **94.71%** | 210 | 5 | 12 | 0 |
| `date-math.ts` | 100% | 27 | 0 | 0 | 0 |
| `format.ts` | 100% | 5 | 0 | 0 | 0 |
| `grid.ts` | 93.75% | 175 | 5 | 12 | 0 |
| `value.ts` | 100% | 3 | 0 | 0 | 0 |

First baseline run (before test fixes) was 88.55% / 22 survivors / 4 no-coverage. The 4
no-coverage mutants were a `testMatch` scoping artifact — the Phase 6 `addDays`/`subDays`/
`startOfMonth`/`endOfMonth` wrappers are exercised only by `bds-date-picker`'s
`presets.spec.ts`; adding that spec to the `date-engine` Jest `testMatch` resolved it.

## Real gaps closed (new tests in `src/services/date-engine/__test__/grid.spec.ts`)

| Line | Mutant | Test |
| --- | --- | --- |
| `grid.ts:94` | `compareDates(cellEnd, min) < 0` → `<= 0` | month-picker: min at the last instant of June keeps June enabled |
| `grid.ts:112` | `compareDates(date, rangeEnd) < 0` → `<= 0` | range-end cell is `isRangeEnd` and **not** `isInRange` |
| `grid.ts:132` | `{ isPreview*: false }` → `{}` | preview-absent assertions strengthened to strict `toBe(false)` |
| `grid.ts:167` (×7) | `hasRangeCompanion` literal / `&&` / partial-`false` / `=== undefined` variants | `hasRangeCompanion` matrix over neither / rangeStart-only / rangeEnd-only / previewEnd-only |

## Documented equivalent mutants (12, no test can observe a difference)

- `grid.ts:62` — `weekStartsOn !== undefined` guard: `startOfWeek` falls back to
  `locale.options.weekStartsOn` identically.
- `grid.ts:78`, `94:7`, `98:10` — `min`/`max !== undefined` guards: `compareDates(valid, undefined)`
  yields `NaN → 0`, so both branches fall through the same way (verified against date-fns v4).
- `grid.ts:106`, `107` — `rangeStart`/`rangeEnd !== undefined` guards: `isSameDay(valid, undefined)`
  is `false`, matching the fall-through.
- `grid.ts:109` (×2), `110` — dropped-bound `!== undefined` guards and `||` variant: the dropped
  term evaluates `0 < 0` / `0 > 0` = `false`, identical to the short-circuit.
- `grid.ts:135` — `compareDates(previewEnd, rangeStart) < 0` → `<= 0`: only differs when both are
  the same instant; swapping identical bounds yields identical range flags.
- `grid.ts:207` — `index < GRID_CELL_COUNT` → `<=`: the 43rd cell is discarded by the 6×7 slice
  (v1-documented, re-confirmed).

**Timeouts (5):** undetected mutants that exceeded the 30s limit; left as-is (they do not affect
the ≥90% score, only the undetected count).
