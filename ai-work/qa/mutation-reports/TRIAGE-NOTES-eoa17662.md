# EOA-17662 Tasks 53/53a — Mutation-Triage Notes

Working notes for the consolidated Stryker pass (strategy recorded in
`ai-work/plans/EOA-17662-bds-date-picker-v3.md` → Testing and QA policy →
"Mutation-testing execution strategy"). This file is a triage aid, not a deliverable
report; the per-area deliverables are `mutation-{date-engine,bds-calendar-grid,bds-date-picker}.md`.

The v1 (2026-08-19) baselines are preserved verbatim in `v1-baseline-2026-08-19/`.

## Phase-bucketing method (v2 debt vs v3)

Stryker cannot scope mutants by phase, so survivors are bucketed by `git blame` on the
survivor's `file:line`. Commit lineage for the relevant paths:

| Commit | Meaning | Bucket |
| --- | --- | --- |
| `7da8fb40` | v1 foundation / single-date picker (Phase 0-1) | already covered by the v1 report |
| `b4cdb986` | v2 — time, min/max, `calendarType`, range (Phases 2-4, squashed into one commit) | **Task 53** (Phase 3/3.5/4) |
| any other `EOA-17662` commit | v3 Phases 5-10 | **Task 53a** |

For `date-engine`: `b4cdb986` covers the v2 additions (bounds/range); `6318017b`
(month/year picker generators), `95acc9a9` (zoned today), `39aaea63`/`7368ce6f`
(presets) are v3. `grid-navigation.ts`'s Phase 9 change is `49d25ed6`/`87472749` (v3).

## v1 documented equivalents — re-verified against current source (2026-09-25)

The v1 report's equivalent list is **partly stale**; do not copy it forward blindly.

- **`bds-date-picker.tsx` `@State() popoverVisible = false` — NO LONGER equivalent.**
  v1 documented it as "declared but never read". It is now read at `listenClickTrigger`
  (`if (this.popoverVisible) return;`) and written by `handlePopoverAfterShow`/`AfterHide`.
  The `false` default now guards the first trigger click, so the `BooleanLiteral → true`
  mutant should be killed by the "clicking the trigger opens the popover" spec. If it
  survives, that is a real gap, not an equivalent.
- **`bds-date-picker.tsx` `@State() isDisabled = false` — still equivalent.**
  `componentWillLoad()` unconditionally assigns `this.isDisabled = this.disabled`
  (`disabled` defaults `false`) before first render, so the literal is unobservable.
- **`bds-date-picker.tsx` `this.bdsPopover?.` — count dropped 7 → 2 sites**
  (`openPopover()` line ~592, `closePopover()` line ~648). Re-judge equivalence for the
  two remaining sites specifically; the v1 blanket "7 call sites" rationale no longer applies.
- **`date-engine/grid.ts` `weekStartsOn !== undefined` (line ~62) and the
  `index < GRID_CELL_COUNT` loop bound (line ~207) — v1 equivalents, still present,
  likely still equivalent** (`date-fns` falls back to `locale.options.weekStartsOn`;
  the 43rd cell is discarded by the 6×7 week-slice). Confirm, don't assume.
- **`bds-calendar-grid.tsx` `key={\`week-${weekIndex}\`}` StringLiteral — v1 equivalent,
  likely still equivalent** (Stencil `key` never reaches the DOM). Note Phase 9 added
  `<table>`-based month/year grids with their own `key`s — re-check each.

## Other known noise classes (from `.agents/memory/mutation-testing-stryker-setup.md`)

- `logger.warn(component, message)` component-name literal → assert the `[bds-date-picker]:`
  prefix, not just the message.
- `validateNumericProp`/`validatePropValue` prop-name string args → assert the prop name
  appears in the warning.
- Optional CSS custom properties → assert the *absent* state (`''`) as well as the set state.
- `@State`/`getter` dead `undefined` branches → equivalent when the type is `T | null`.

## Triage checklist

1. Run all three configs once; capture clear-text output per area.
2. For each `[Survived]` / errored mutant, `git blame -L <line>,<line> -- <file>`.
3. Bucket by the table above; kill real gaps with a spec fix in the phase-owning spec file.
4. Document the rest as verified equivalents in the area report.
5. Target ≥90% per area (chase 100%).

---

## Bucketed results (2026-09-25 runs)

Scores: `date-engine` 88.55% total / 90.13% covered (196 killed, 22 survived, 5 timeout,
4 no-cov); `bds-calendar-grid` 75.97% total / 78.69% covered (828 killed, 227 survived,
10 timeout, 38 no-cov). Counts below are **unique (file:line,tag)** after de-duplication;
real mutant counts are higher where one line produced several mutants.

> **Run-config caveat:** `date-engine` and `bds-calendar-grid` ran with the full mutator
> set. The `bds-date-picker` run was retuned (2026-09-25) with
> `excludedMutations: [StringLiteral, ObjectLiteral, ArrowFunction, BlockStatement]` and
> `timeoutMS: 10000` after the full-set run projected 4–12h on the 11-core/18GB machine.
> Its score is therefore **not directly comparable** to the other two — the excluded
> mutators are low-signal noise, but note the difference in any write-up. Do not compare
> raw percentages across areas; compare logic-mutator (Conditional/Equality/Logical)
> survivor counts.

### `date-engine` → in scope, small, unit-testable

| Bucket | Commit | Lines | Action |
| --- | --- | --- | --- |
| v2 range flags | `b4cdb986` | `grid.ts` 78, 106, 107, 109, 110, 112, 132 | Task 53 — fix |
| v3 hover-preview | `2f25c5e9` | `grid.ts` 135, 167 | Task 53a — fix |
| Phase 9 month/year generator bounds | `6318017b` | `grid.ts` 94, 98 | Task 53a — fix |
| Phase 6 date-math wrappers (NoCov) | `7368ce6f`, `39aaea63` | `date-math.ts` 21, 29, 33, 37 | scoping artifact — covered by `presets.spec.ts`; add that spec to the date-engine Jest `testMatch` |
| v1 equivalents | `7da8fb40` | `grid.ts` 62, 207 | documented equivalents (unchanged) |

### `bds-calendar-grid` → three destinations

| Bucket | Commits | Lines | Action |
| --- | --- | --- | --- |
| **Phase 9 quick-picker** | `49d25ed6` (31), `aa1f1ad2` (9), `39c3fae4` (6), `21be7773` (6), `f255e94b` (5), `95c3704a` (5), `29a5dd9d` (4), `b87e9ec4` (1) — 67 lines incl. the `getPriority*Cell` cluster 611-636 | **follow-up ticket** |
| **Phase 8 keyboard/a11y** | `af378301` (19), `cf2a1883` (6), `a162e10d` (1) — 26 lines | Task 53a — fix |
| Phase 9 `onActivate` guard | `49d25ed6` — `grid-navigation.ts` 233, 236 | Task 53a — fix |
| **Pre-existing EOA-10530** | `ea4d3d76` — `grid-navigation.ts` 50 lines | **separate ticket** (not this plan) |
| v1 | `7da8fb40` — `bds-calendar-grid.tsx` 898 | check for equivalent |

Note: `bds-calendar-grid.tsx` had **zero v2 (`b4cdb986`) survivors** — the v2 Phase 4
range logic in the grid is well covered. All its survivors are Phase 8/9/10 (v3).
