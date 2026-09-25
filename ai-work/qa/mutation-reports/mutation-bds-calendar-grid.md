# Mutation Report — `bds-calendar-grid` (+ `grid-navigation.ts`) (EOA-17662 Tasks 53/53a, v3 re-run)

**Run:** 2026-09-25, worktree `.worktrees/mutation-eoa17662`, Stryker 10.0.0, Jest runner,
`coverageAnalysis: 'perTest'`, `mutate` = `bds-calendar-grid.tsx` + `grid-navigation.ts`.
Config: `stryker.bds-calendar-grid.config.mjs` (local-only). v1 baseline preserved in
`v1-baseline-2026-08-19/mutation-bds-calendar-grid.md`.

## Result: **77.43%** total / 80.04% covered (below the 90% floor — see Deferrals)

| File | Score | Killed | Timeout | Survived | No coverage |
| --- | --- | --- | --- | --- | --- |
| All files | 77.43% | 849 | 5 | 213 | 36 |
| `bds-calendar-grid.tsx` | 79.62% | 620 | 1 | 154 | 5 |
| `grid-navigation.ts` | 72.14% | 229 | 4 | 59 | 31 |

Baseline (before Task 53a test fixes) was 75.97% / 227 survived / 38 no-cov. The re-run confirms
**+21 killed / −14 survived**; the residual survivors at every line the new tests targeted are
the documented equivalent mutants, not failed kills.

## Kills confirmed by this re-run (Task 53a)

`bds-calendar-grid.tsx` real-gap mutants killed by the new `bds-calendar-grid.keyboard.spec.ts`
tests: lines **164, 168, 187, 188, 502, 664**, plus the non-equivalent mutants at **232** and
**515**. `grid-navigation.ts`: the full-`true` and `onActivate != null` variants at **233**
(non-equivalent; the two `activateKeys`-only variants remain as equivalents).

Verified equivalent survivors at the targeted lines (confirmed via the incremental JSON's
AST-preserving mutant, not the lossy clear-text diff):
- `bds-calendar-grid.tsx:232:9` — `cell == null` → `false` (unreachable; `isoDate` non-null implies a registered cell).
- `bds-calendar-grid.tsx:515:9` — `index === -1` → `false` (`flatItems.indexOf(null) === -1` already no-ops).
- `grid-navigation.ts:233:29` (×2) — `activateKeys.length > 0` → `true` / `>= 0` (only differs for an empty key array, which is a no-op).
- `grid-navigation.ts:236:13` — `document.activeElement instanceof HTMLElement` → `true` (branch only reachable when that check already passed).

## Deferrals (why this area is below 90%)

These two buckets are tracked separately and are **not** covered by Task 53/53a test fixes:

- **Task 53b** — Phase 9 quick-picker survivors in `bds-calendar-grid.tsx` (commits `49d25ed6`,
  `aa1f1ad2`, `39c3fae4`, `21be7773`, `f255e94b`, `95c3704a`, `29a5dd9d`, `b87e9ec4`; 67 unique
  lines incl. the `getPriority*Cell` cluster at 611–636). Real weak-assertion gaps in the
  quick-picker interaction logic — require a dedicated test-writing pass.
- **Task 53c** — `grid-navigation.ts` survivors blamed to `ea4d3d76` (EOA-10530, 2026-05-20),
  pre-existing shared-utility debt (50 lines), out of this plan's scope.

`bds-calendar-grid.tsx` has **zero v2 (`b4cdb986`) survivors** — the v2 Phase 4 range logic is
fully covered. Every survivor is Phase 8/9/10 or pre-existing.

**Timeouts (5):** undetected (exceeded 30s); left as-is.

## Reference

Bucketed per-line ownership: `TRIAGE-NOTES-eoa17662.md`. Raw logs:
`run-bds-calendar-grid-2026-09-25.log` (baseline) and
`run-bds-calendar-grid-verified-2026-09-25.log` (this verified re-run).
