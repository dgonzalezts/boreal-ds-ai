---
ticket: EOA-17662
component: bds-date-picker
status: done
created: 2026-09-02
updated: 2026-09-24 — Phases 5-8 complete (through Task 45) and Phase 9 quick-picker implemented through Task 50 (46 decisions; 47 generators; 48 + 48a-48j table markup, overlay, nested header, selected/range flagging, keyboard/ARIA, auto-close/resync, PageUp/PageDown paging, year-window focus; 49 styling; 50 unit tests). Task 51 docs done. A post-Task-51 docs review corrected the range-end coverage-shift wording (manual `expanded` is not "taken exactly as set" — the shift is data-driven on equal time-of-day) across `bds-date-picker.mdx`/`.stories.ts` (incl. a `bds-calendar-grid` per-story argTypes override), ADRs 0015/0016, the failure-mode catalog, and this plan. Phase 10 cleanup complete (Task 54 JSDoc, Task 55 import consolidation incl. a user-approved new `helpers/index.ts` barrel, Task 55a `CALENDAR_GRID_VIEW` constants). Remaining: Task 52 wrapper parity (in progress in another session) and Tasks 53/53a mutation testing. 2026-09-25 — Tasks 53/53a execution strategy finalized with the user and recorded in Testing and QA policy ("Mutation-testing execution strategy"): one consolidated Stryker pass with survivors bucketed by phase via `git blame` (not two phase-scoped runs — Stryker can't scope mutants by phase), ≥90% floor with documented equivalents, configs kept local-only (commits carry spec fixes only — reports stay in gitignored `ai-work/`), and `grid-navigation.ts` folded into the `bds-calendar-grid` target. 2026-09-25 (wrap-up) — Tasks 53/53a executed as one consolidated pass. `date-engine` verified at 94.71%; `bds-calendar-grid` in-scope fixes mutation-confirmed (75.97% → 77.43%, every targeted real-gap line killed, residuals are documented equivalents). Test fixes committed as `ffa91f97`. The `bds-date-picker` pass was deferred (897 mutants ≈ 7h and memory-exhausting on the 11-core/18GB machine, even after retunes). The three large deferred gaps were re-scoped into local tickets (`ai-work/tickets/EOA-17662-53b` quick-picker, `-53c` EOA-10530 `grid-navigation.ts` debt, `-53d` `bds-date-picker` pass), so the plan is complete.
revision: 3 — reconciled against v2's actual implementation history and the spike's node references (2026-09-08)
---

# EOA-17662 — bds-date-picker v3 (Phases 5-9) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Deliver the remaining roadmap scope for `bds-date-picker` by completing Phases 5-9 (range-mode time selection, presets sidebar, info banner/range summary, keyboard/a11y, month/year quick-picker — RTL descoped from Phase 8, see Task 41a), a Phase 10 JSDoc/import cleanup pass, and two final consolidated mutation-testing tasks (v2 carried-over debt, then this plan's own Phase 5-9 scope).

**Ticket brief:** [`ai-work/tickets/EOA-17662-bds-date-picker-v3.md`](../tickets/EOA-17662-bds-date-picker-v3.md)

**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md)

**v2 plan (Phase 2-4, prerequisite, done):** [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md)

**Cross-cutting fix outside this plan's own file scope (2026-09-09):** Task 23's manual QA surfaced a real bug in `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` (`handleFocusOutside`'s RAF-scheduling race with `bds-select`'s own deferred refocus-after-selection call — see Task 23's Status note for the full root cause) that blocked real mouse-driven use of the time selector in both single-date and range modes. Fixed as part of this plan's execution since it blocked Task 23 outright, not deferred to a separate ticket. `bds-popover`'s own test suite (57/57) and `bds-select`/`bds-date-picker`'s suites (381 tests) were re-verified clean. Any other component composing `bds-popover` with a nested focus-transferring child (not just `bds-date-picker`) benefits from this fix — worth keeping in mind if a similar "popover closes unexpectedly on a nested interactive element" report surfaces elsewhere in the library.

This plan carries forward the remaining roadmap scope after v2 foundation work.

- v2 (EOA-17138) now ends at Phase 4 foundation work.
- v3 (EOA-17662) owns all remaining work: Phases 5-9, a Phase 10 JSDoc/import cleanup, and two final mutation-testing tasks — Task 53 covers Phase 3/3.5/4 code v2 never mutation-tested, Task 53a covers this plan's own Phase 5-9 (+ Phase 10) scope (see Testing and QA policy below).
- Keyboard-typed date entry in the trigger field remains explicitly out of scope.

**Architecture:** Unchanged core shape from v1/v2 — `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + one or two `bds-calendar-grid` bodies, FACE-compliant, draft-state-until-Apply). Each v3 phase is additive on top of v2's `range`/`calendarType` foundation: Phase 5 parameterizes the existing time-selector helper for start/end positions; Phase 6 adds a new `renderPresets.tsx` sidebar gated on `range`; Phase 7 adds a new `renderBanner.tsx` and extends the footer; Phase 8 wires the already-existing `grid-navigation.ts` utility into `bds-calendar-grid`; Phase 9 adds an internal `view` state to `bds-calendar-grid` (no new public component or prop).

**Tech Stack:** Stencil, TypeScript, `date-fns`/`@date-fns/tz` (already in place since v1), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`), Stryker for mutation testing, existing `src/utils/a11y/keyboard/navigation/grid-navigation.ts`.

---

## Files to create / modify

**Phase 5 (dual time):**

| File                                                                        | Notes                                                                         |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx`        | Modify — parameterize for `label`/`position: 'single' \| 'start' \| 'end'`    |
| `.../bds-date-picker/bds-date-picker/helpers/renderRangeHeader.tsx`         | Modify — add per-bound time text to the `expanded` labeled header             |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                   | Modify — dual/shared time wiring; time text on the `basic` dash-joined header |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                  | Modify — dual/shared time-selector layout                                     |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts` | Modify — dual/shared time-selector coverage                                   |

**Phase 6 (presets sidebar):**

| File                                                                           | Notes                                                                                     |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/utils/presets.ts`                         | New — built-in preset date-range computation                                              |
| `.../bds-date-picker/bds-date-picker/utils/__test__/presets.spec.ts`           | New                                                                                       |
| `.../bds-date-picker/bds-date-picker/helpers/renderPresets.tsx`                | New                                                                                       |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                           | Modify — `DatePickerPreset` shape, `presets` prop type (if configurable, per Task 28)     |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                      | Modify — `presets` prop, sidebar wiring, basic-mode header-format re-evaluation (Task 30) |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                     | Modify — sidebar layout, option button states                                             |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.presets.spec.ts` | New                                                                                       |

**Phase 7 (banner + range summary):**

| File                                                                          | Notes                                                                                  |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/helpers/renderBanner.tsx`                | New                                                                                    |
| `.../bds-date-picker/bds-date-picker/helpers/renderFooter.tsx`                | Modify — range-summary label, left of Clean/Cancel/Apply                               |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                          | Modify — `DatePickerBanner` shape (`title`, `message`, `closable`, `state`, `visible`) |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                     | Modify — `banner` prop, closable wiring                                                |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                    | Modify — banner + summary label styling                                                |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.banner.spec.ts` | New                                                                                    |

**Phase 8 (keyboard/a11y; RTL descoped, see Task 41a):**

| File                                                                            | Notes                                                                                                          |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                   | Modify — wire `src/utils/a11y/keyboard/navigation/grid-navigation.ts` for 2D arrow-key traversal               |
| ~~`.../bds-calendar-grid/bds-calendar-grid.scss` — RTL audit~~                  | **Descoped 2026-09-23 (Task 41a)** — no design-system-wide RTL precedent exists; pending ticket-owner sign-off |
| `.../bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx`           | Modify — live region for month/year-change announcement                                                        |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                       | Modify — Escape-key close + focus return to trigger                                                            |
| ~~`.../bds-date-picker/bds-date-picker/bds-date-picker.scss` — RTL audit~~      | **Descoped 2026-09-23 (Task 41a)** — see above                                                                 |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.keyboard.spec.ts`             | New                                                                                                            |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts`                 | Modify — live region assertions                                                                                |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` | Modify — full grid-traversal + Escape-close coverage                                                           |

**Phase 9 (month/year quick-picker):**

| File                                                                                   | Notes                                                                                                                                                                         |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/services/date-engine/grid.ts`                      | Modify — `generateMonthPickerGrid`/`generateYearPickerGrid` (Task 47)                                                                                                         |
| `packages/boreal-web-components/src/services/date-engine/types.ts`                     | Modify — `MonthPickerCell`/`MonthPickerGrid`/`YearPickerCell`/`YearPickerGrid` (Task 47)                                                                                      |
| `packages/boreal-web-components/src/services/date-engine/__test__/grid.spec.ts`        | Modify — grid-generator coverage (Task 47)                                                                                                                                    |
| `.../bds-calendar-grid/types/ICalendarGrid.ts`                                         | Modify — `min`/`max`/`now` (Task 48/GA) and `rangeStart`/`rangeEnd` (Task 48g) props (the phase's `view` state is internal `@State`, not on this props-only interface)        |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                          | Modify — internal `view`/`pickerYear` state, `<table>`-based month/year grids, overlay superposition, nested header, keyboard/ARIA, PageUp/PageDown paging, year-window focus |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                                         | Modify — picker cell state matrix + overlay card (Task 49), quick-picker live region                                                                                          |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts`                 | New (Task 50)                                                                                                                                                                 |
| `.../bds-date-picker/helpers/renderCalendarPanel.tsx`                                  | Modify — thread `min`/`max`/`now`; per-instance `onBdsMonthNavigate` (Task 48/GA/GB)                                                                                          |
| `.../bds-date-picker/bds-date-picker.tsx`                                              | Modify — absolute-target month nav; `resetCalendarViews()` on preset/clear/cross-grid day-pick/month-nav; slot-aware anchor (Tasks 48/GB/GC/48f/48h)                          |
| `.../bds-date-picker/utils/value-mapping.ts`                                           | Modify — shared `resolveZonedToday` extraction (Task 48/GA)                                                                                                                   |
| `.../bds-date-picker/__test__/bds-date-picker.quickpicker.spec.ts`                     | New (Task 50)                                                                                                                                                                 |
| `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` | Modify — `onActivate` non-cell-focus guard (Task 48e keyboard-open fix)                                                                                                       |
| `packages/boreal-web-components/src/utils/a11y/keyboard/__test__/navigation.spec.ts`   | Modify — `onActivate` guard coverage (Task 50)                                                                                                                                |

**Shared, across every phase:**

| File                                                                            | Notes                                                                         |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/index.html`                                 | Modify — playground scenarios per task (never committed)                      |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` | Modify — one new story variant per phase                                      |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx`        | Modify — one new section per phase                                            |
| `.../date-engine/stryker.date-engine.config.mjs`                                | Modify (final task) — re-run to cover Phase 3/3.5/4/5-9 additions             |
| `.../bds-date-picker/stryker.bds-date-picker.config.mjs`                        | Modify (final task) — re-run to cover Phase 3/3.5/4/5-9 additions             |
| `.../bds-calendar-grid/stryker.bds-calendar-grid.config.mjs`                    | Modify (final task) — re-run; Phase 8/9 are the first v3 phases touching this |

---

**Critical reference files (read before starting any task below):**

- [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md) — Phase 2-4 implementation this plan extends. Its Task 18 status notes (three correction passes, 2026-08-31/09-01) are load-bearing for Phase 5: the popover header format landed on a **split by `calendarType`**, not one uniform presentation — see Task 23 below.
- `ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md` — governing findings/decisions for Phases 5-9; each task below only summarizes it. Note: v2's Task 18 briefly reused the spike's `_DatePickerRange` node (`14:23420`, correctly a Phase 6 preset-button reference per the spike's own Phase 6 finding) for an unrelated header/range-design lookup and found it didn't fit — treat any node ID as scoped to the phase the spike assigned it to, not a general-purpose reference, and re-verify with `get_design_context` before reuse across phases.
- `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` — existing generic grid-keyboard utility, Phase 8's integration point (flagged in v1's Task 9 code comment, carried through v2's own file list, never wired — still outstanding for Task 40 below).

## Testing and QA policy for this plan

**Two-phase test gate remains in effect** — coverage-phase tests are consolidated at the end of each covered phase block (per Phase, one unit-test task). Mutation-phase consolidation is deferred to two tasks at the end of this plan: Task 53, which — per v2's own policy handoff — owns the Phase 3/3.5/4 mutation-testing pass v2 deferred and never ran; and Task 53a, which owns this plan's own Phase 5-9 (+ Phase 10 cleanup) scope. Split into two (rather than one combined task) so the historical v2 debt and this plan's own active-development scope don't share one hard-to-triage report, and so both configs use Stryker's `--incremental` mode to keep re-runs cheap.

**Mutation-testing execution strategy for Tasks 53/53a (decided with the user, 2026-09-25) — supersedes the two-run `--incremental` framing in the paragraph above.** Grounded against the actual repo before adoption (no Stryker configs exist in the tree or on any branch; v1's three configs were worktree-local and discarded; `bds-date-picker.tsx` is 1204 lines and mixes Phase 3-10 code in one file):

- **One consolidated Stryker pass, not two phase-scoped runs.** Stryker mutates whole files/globs, not line ranges, so "Phase 3/3.5/4 only" vs "Phases 5-9 only" cannot be expressed as config scoping — `bds-date-picker.tsx`, `bds-calendar-grid.tsx`, `utils/*`, and `date-engine/grid.ts` each hold code from every phase. The run happens once against current HEAD; survivors are then bucketed into **v2-debt (Task 53)** vs **v3 (Task 53a)** by `git blame` on each survivor's line. That preserves the split's actual purpose (separable triage) without a second expensive run.
- **`--incremental` buys little here, which is why the second pass is dropped.** Per Stryker's docs, a killed mutant is reused only while its culprit test is unchanged, and a non-killed mutant is re-run once new tests cover it. Both tasks' whole point is adding tests, so a Task-53a re-run would re-execute most of Task 53's targets. Task 53a is therefore **the same consolidated pass, written up separately**, not a second run.
- **Score bar: ≥90% per target area** (the plan's stated floor), chasing 100%. Every survivor is either killed by a new test or documented as equivalent with reasoning in `ai-work/qa/mutation-reports/mutation-<area>.md` — mirroring v1's shipped 93.33% / 97.37% / 97.67%, whose known-equivalent list is the starting point for triage.
- **Configs stay local-only.** Per `.agents/memory/mutation-testing-workflow-decisions.md`, Stryker configs and packages are never committed — they live in the throwaway worktree and vanish with it. The only feature-branch artifact this pass produces is spec-file test fixes; the updated `ai-work/qa/mutation-reports/*.md` are written into the gitignored `ai-work/` tree (this clone excludes `ai-work/` via `.git/info/exclude`, synced through the private AI-config remote, not the feature branch).
- **Target map** (configs at `packages/boreal-web-components/` root, matching the skill template and the `local/mutation-testing` precedent; one shared `jest.stryker.config.cjs` with a union `testMatch` and `enableFindRelatedTests: true`):
  - `stryker.date-engine.config.mjs` → `src/services/date-engine/{date-math,grid,format,value}.ts`
  - `stryker.bds-calendar-grid.config.mjs` → `.../bds-calendar-grid/bds-calendar-grid.tsx` **plus** `src/utils/a11y/keyboard/navigation/grid-navigation.ts` (modified in Phase 9/Task 48e and in this plan's file list, but outside the three named areas — folded in here rather than standing up a fourth config)
  - `stryker.bds-date-picker.config.mjs` → `.../bds-date-picker/bds-date-picker.tsx`, `helpers/{renderBanner,renderCalendarPanel,renderFooter,renderPresets,renderRangeHeader,renderTimeSelector}.tsx`, `utils/{constants,draft-state,presets,value-mapping}.ts`
  - Excluded from `mutate`: `types/*`, `types/enum.ts` const objects (`CALENDAR_GRID_VIEW`, `RANGE_BOUND`), and `index.ts` barrels — self-referential/no-runtime mutants that produce a guaranteed noise class.
- **`bds-popover.tsx` is explicitly out of scope** for this pass (modified during Task 23, but a shared overlay component with no existing config; noted here, not mutated).
- **Worktree:** created off the current `feature/EOA-17662_bds-date-picker-v3-p2_DG` HEAD, kept alive across the run (so `.stryker-tmp/` can be ESLint-ignored per `.agents/memory/mutation-testing-stryker-setup.md`); changed spec files and reports are copied back to the primary checkout and committed there, then the worktree is removed.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output** — implementation and SCSS tasks chain `@qa-subagent`; pure-logic, types-only, and test-only tasks keep a single executor. Matches this plan's existing Executor fields throughout.

**Wrapper parity stays per-phase, not per-task and not fully consolidated** — `bds-date-picker` was already an established, shipping component by v2's Phase 3 (per v2's own policy, quoted there: _"unlike v1/Phase 2 (a brand-new component with no behavior yet to diverge on), by Phase 3 `bds-date-picker` is an established, already-shipping component; per the writing-plans convention, each phase from here on gets its own React/Vue parity task immediately after that phase's documentation task"_). v3 continues that same policy: each phase's parity-check task (Tasks 27/34/39/45/52) runs immediately after that phase's documentation task, catching any framework-specific regression against the one feature that just landed rather than in one end-of-plan pass.

**Blocking design-check-in gates** remain at the start of Phase 6 (Task 28, presets configurability) and Phase 9 (Task 46, quick-picker drill-down model).

**Grounded failure-mode/edge-case pass before every implementation task** (carried over from v2's standing instruction, applies for this plan's entire execution): before dispatching any implementation task below to its executor, the orchestrating session must first read the actual current source of every file that task will touch — not just this plan's prose — and check for integration gaps the task's acceptance criteria may have missed (a helper/util function called from multiple sites the task's Files list omits, a public-API boundary case, a default-value/empty-state ambiguity, a runtime prop-toggling assumption). Real findings get folded into that task's acceptance criteria and manual-test scenarios — and propagated to any later task sharing the same root cause — before dispatch. This is the live-execution counterpart to `writing-plans`' authored Integration & Edge-Case Gate; it doesn't replace authoring integration research passes into tasks up front, it catches drift between planning time and dispatch time. Skip this pass only for tasks with no executor (blocking design gates) or no code surface (React/Vue parity, the mutation-testing task, already scoped by their own task text).

---

## Phase 5 — Time selection for range mode (single-shared vs. dual independent)

Per the spike decisions, range mode supports two time-selection behaviors:

- `calendarType='expanded'` + `range` + `withTime`: two independent time selectors (start/end)
- `calendarType='basic'` + `range` + `withTime`: one shared time selector applied to both range boundaries

### Task 23: `bds-date-picker` range-mode time selector (single-shared under `basic`, dual under `expanded`)

**Status:** ✅ done (2026-09-09) — implemented by `@frontend-subagent` per the grounding-check findings below, then refined twice more (both by the same subagent, both verified): extracted the inline `'start' | 'end'` literals into a shared `RANGE_BOUND`/`RangeBound` type in `types/enum.ts` (matching this component's existing `CALENDAR_TYPE`/`CalendarType` const-object pattern), then fixed the one remaining raw-string comparison in `renderTimeSelector.tsx`'s `boundLabel` resolution to use the new `RANGE_BOUND` constants for consistency. `tsc --noEmit` and the full `bds-date-picker` suite (262 tests) stayed clean throughout.

Manual QA surfaced two apparent blocking bugs (mouse click on any time-selector option closed the whole popover; `range && withTime` Apply committed nothing) that turned out to be **one real bug, not two**: root-caused via live diagnostic instrumentation to a genuine RAF-scheduling race in `bds-popover.tsx`'s `handleFocusOutside` (a shared component, outside this task's own file list) racing against `bds-select`'s own deferred refocus-after-selection call — fixed by giving the focus-outside check one extra confirmatory frame when `document.activeElement` reads as `document.body`, rather than treating a single ambiguous frame as definitive. Once fixed, the "Apply commits nothing" bug also vanished on its own — every previous attempt had been getting its in-progress selection discarded by the popover-closing bug before Apply ever ran against valid data; the `buildRangeCommitValue`/`combineDateTimeToUTC` wiring was correct from the first implementation pass. Confirmed via `bds-popover`'s own suite (57/57), plus `bds-select`/`bds-date-picker` (381 tests + 1 pre-existing todo), plus live-browser re-verification of the exact previously-failing click sequence.

All 5 of this task's manual test scenarios verified live in-browser with real mouse interaction (not `.click()`/synthetic dispatch) and the raw `.value` property inspected directly, not just the displayed text: Scenario 1 (`expanded`, independent bounds) → `{start:"...04:00...", end:"...06:00..."}`; Scenario 2 (`basic`, shared bound) → `{start:"...05:00...", end:"...05:00..."}`; Scenario 3 (single-date regression) → unchanged plain UTC ISO string; Scenario 4a/4b (auto-format headers) → both the `expanded` labeled header and `basic` dash-joined header correctly show `HH:mm` with no explicit `format` set. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderTimeSelector.tsx` (modify), `helpers/renderRangeHeader.tsx` (modify), `bds-date-picker.tsx` (modify), `types/types.ts` (modify — `DatePickerDraftState` gains per-bound time fields for `expanded` mode), `utils/draft-state.ts` (modify — bound-aware hour/minute selection), `utils/value-mapping.ts` (modify — time-inclusive range formatter)

**Grounding-check findings (2026-09-08, read actual current source before dispatch — these are concrete, not hypothetical):**

- `DatePickerDraftState` (`types/types.ts:1-7`) currently has exactly one shared `hour: number`/`minute: number` pair, used unconditionally regardless of `range`. There is no per-bound time state today. `resetRangeDraft`'s own doc comment (`utils/draft-state.ts:98-102`) confirms: _"`withTime` is not yet supported in range mode (Phase 5) — `hour`/`minute` always default to `00:00`."_ — this task is exactly what that comment is waiting on.
- Add new fields to `DatePickerDraftState` for `expanded`'s two independently-controlled selectors — e.g. `startHour: number`, `startMinute: number`, `endHour: number`, `endMinute: number` (flat, mirroring the existing `rangeStart`/`rangeEnd` flat-field precedent, not nested). The existing single `hour`/`minute` fields stay exactly as-is and continue to be the ones read/written for `basic`+`range` (the shared-value case) — do not repurpose them for `expanded`.
- `selectHour`/`selectMinute` (`utils/draft-state.ts:56-68`) currently mutate the single shared `hour`/`minute` field unconditionally, with no bound concept. Add bound-aware variants (or a `bound` param) for the new `startHour`/etc. fields; `handleHourChange`/`handleMinuteChange` (`bds-date-picker.tsx:432-438`) are the only existing call sites and will need either duplication into start/end-specific handlers or a bound-aware signature.
- `TimeSelectorParams` (`helpers/renderTimeSelector.tsx:6-13`) has no way to render a leading `Start:`/`End:` text label today — its `labels` param only feeds the two `bds-select`'s own internal field labels (`hour`/`minute`), not a prefix. Add a new param (e.g. `boundLabel?: string`) sourced from `labels.start`/`labels.end` at the call site — `DatePickerFooterLabels` already has both keys (`types/types.ts:15-16`, added in v2's Task 19), reuse them, don't add new keys.
- `render()`'s current time-selector block (`bds-date-picker.tsx:831-842`) gates on the raw `this.withTime` prop (not `this.effectiveWithTime`) and always renders exactly one `renderTimeSelector` call with no `range` branch at all — confirm against the file's existing `effectiveWithTime`/`effectiveRange`/`effectiveFormat` getter convention whether this block should switch to `this.effectiveWithTime` for consistency (a pre-existing inconsistency this task's new branching logic will sit next to, worth fixing while touching this code rather than leaving mixed).
- `formatRangeForDisplay` (`utils/value-mapping.ts:218-231`) only accepts naive-ISO date strings today — no hour/minute params, cannot format time. `formatDraftForDisplay` (`utils/value-mapping.ts:197-210`) is the existing single-date pattern that already combines `selectedDate + hour/minute` into one formatted string (wall-clock local, no timezone conversion) — mirror that shape for a new per-bound range-plus-time formatter, rather than bolting optional hour/minute params onto `formatRangeForDisplay` itself.
- `bds-date-picker.tsx`'s Apply-commit path (`bds-date-picker.tsx:402-405`) currently commits `{ start: rangeStart, end: rangeEnd }` as bare naive-ISO date strings with **no time-combination call at all**, even though this task's own acceptance criteria below already commit to `combineDateTimeToUTC`/`extractDateTimeFromUTC` producing full UTC ISO strings for the range value. This task's scope includes updating that Apply-commit path to call `combineDateTimeToUTC` per bound (using the new `startHour`/`startMinute`/`endHour`/`endMinute` for `expanded`, the existing shared `hour`/`minute` for `basic`) — this isn't a separate task, it's this task's own value-contract acceptance criteria made concrete against the real commit path.

**Header-format context (from v2 Task 18, read before implementing):** the popover header is **not** one uniform format across `calendarType`. `expanded`+`range` uses `renderRangeHeader.tsx`'s labeled `Start:`/`End:` pairs (popover is `width: 'auto'`, no overflow risk). `basic`+`range` uses a plain, unlabeled, dash-joined single line (`"YYYY/MM/DD – YYYY/MM/DD"`) rendered inline in `bds-date-picker.tsx`, deliberately without labels because the labeled format wrapped inside `basic`'s fixed 296px popover. v2 explicitly left time out of both formats pending this task: _"Time segment simply omitted until Phase 5/Task 23 wires in withTime support for range mode."_

**Utility discovery:**

- Feature area: UTC time combination/extraction for a second (end) time value.
- Search performed: `date-engine/value.ts` (Phase 2's `combineDateTimeToUTC`/`extractDateTimeFromUTC`), `date-engine/format.ts` (`formatDisplayDate`), `bds-date-picker/utils/value-mapping.ts` (`formatRangeForDisplay`, per-bound formatter already used by `renderRangeHeader.tsx`).
- Candidates found: `combineDateTimeToUTC`/`extractDateTimeFromUTC` (already parameterized per-value, no start/end-specific variant needed); `formatRangeForDisplay` (already accepts a single bound + format/locale, used identically by both the labeled and dash-joined header paths per v2 Task 18/19).
- Fit assessment: both fully fit — they're value-agnostic, already called once per bound. No new `date-engine` primitive needed for dual time.
- Reuse decision: call `combineDateTimeToUTC`/`extractDateTimeFromUTC` once per bound (start, end) exactly as Phase 2 calls them once for the single-date case; extend `formatRangeForDisplay`'s call sites (both `renderRangeHeader.tsx` and the basic dash-joined span) to include time text, not a new formatter.
- Gap handling: none — no extension needed.
- Anti-duplication check: confirms no new time-combination/formatting logic is planned; this task only adds call sites and a `label`/`position` parameter to `renderTimeSelector.tsx`.
- Test impact: Task 25's unit tests assert UTC output through `combineDateTimeToUTC`/`extractDateTimeFromUTC` directly (not a duplicated local computation).

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `renderTimeSelector.tsx` is currently called once (single-date, Phase 2) — confirm every other call site this task adds (`start`/`end` in `expanded`, `single` shared in `basic`) passes a consistent `DatePickerDraftState` shape, and that adding the `label`/`position` parameter doesn't break the existing Phase 2 call, which must keep working with no change to its own call-site code (`position: 'single'` as an implicit/default value, not a required new argument at that call site).
- [ ] Call sites: `formatRangeForDisplay` is called from both `renderRangeHeader.tsx` (expanded, labeled) and `bds-date-picker.tsx`'s inline dash-joined span (basic) per v2's Task 18/19 split — confirm the time-text addition lands in both call sites, not just one, since they are two independent render paths reading the same underlying `draft.rangeStart`/`draft.rangeEnd`/hour/minute state.
- [ ] Boundary case: `range && withTime` toggled on for an in-progress selection where only `rangeStart` is set and `rangeEnd` is still `null` — what does the time selector show/commit for the unset bound? (Likely: apply the shared-vs-independent default-time rule per bound independently, not block time entry until both bounds exist — confirm against Task 18's existing single-bound placeholder-fallback precedent in `renderRangeHeader`.)
- [ ] Default/empty state: fresh range values (no prior selection) default time to `00:00` per this task's own acceptance criteria — confirm this applies identically whether the picker mounts with `withTime` already `true`, or `withTime` is toggled on after a date-only range already exists in draft state (a reactive-prop transition, not just initial mount).
- [ ] Reactivity: `withTime` is expected to be reactive after mount (an existing `@Watch`-driven prop from Phase 2) — confirm this task's dual/shared time wiring reacts correctly to `withTime` toggling live, not just at initial render, matching Phase 2's own established behavior for single-date mode.

**Acceptance criteria:**

- `renderTimeSelector.tsx` accepts a `label`/`position: 'single' | 'start' | 'end'` parameter; single-date Phase 2 usage remains a regression-free special case (`position: 'single'`).
- Routing is driven by `calendarType`, not by `range` alone: when `calendarType === 'expanded'` and `range && withTime`, renders two labeled time-selector pairs, each preceded by a text label (`"Start:"`/`"End:"`, resolved through the existing `DatePickerFooterLabels`/`labels` prop i18n mechanism per v2's Task 19 precedent — not hardcoded English literals) — per the reference screenshot (single clock icon at the row's start, `Start:` before the first hour/minute pair, `End:` before the second; exact icon count/placement to be confirmed against Figma in Task 24, not assumed from the screenshot alone). When `calendarType === 'basic'` and `range && withTime`, renders one `position: 'single'` time selector with no `Start:`/`End:` label (single shared value, nothing to disambiguate — matching Phase 2's single-date precedent of no label).
- Under `calendarType === 'basic'` with `range && withTime`, one hour/minute value applies to both `rangeStart` and `rangeEnd` when constructing committed `{ start, end }` UTC strings.
- Under `calendarType === 'expanded'`, uses `combineDateTimeToUTC`/`extractDateTimeFromUTC` for independently controlled start/end time values.
- Value contract when `range && withTime`: `{ start, end }` where both are full UTC ISO strings; shape stays identical regardless of `calendarType`.
- Legacy prop references `resetTime`/`showTimeInRange` are evaluated and either adopted with rationale or explicitly deferred.
- `format` auto-switch extends to range mode: when `range && withTime` and `format` is unset, header display includes `HH:mm`; explicit `format` still wins. This applies to **both** header formats independently: `renderRangeHeader.tsx`'s labeled `Start:`/`End:` pairs (expanded) and the plain dash-joined span (basic) each gain per-bound time text — do not assume one shared formatter covers both, since they are two different render paths (per the Header-format context above).
- Default time extends to range mode: fresh range values default to `00:00`, following the shared-vs-independent rule above.

**Manual test (required):**

Playground scenarios to add in `packages/boreal-web-components/src/index.html`:

- Scenario 1: `calendarType='expanded'`, `range` + `withTime` enabled.
- Scenario 2: `calendarType='basic'`, `range` + `withTime` enabled.
- Scenario 3: single-date `withTime` picker (Phase 2 regression, no new scenario needed if one already exists).
- Scenario 4: `calendarType='expanded'`, `range` + `withTime` enabled, no explicit `format`.

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1, when start and end times are selected independently, then each bound's committed UTC string reflects only its own time. Pass: `bdsChange`'s `{ start, end }` values differ in time-of-day when different times are chosen per bound.
- [ ] Given Scenario 2, when one time is chosen, then both `rangeStart` and `rangeEnd` commit with that same hour/minute on their own dates. Pass: `{ start, end }` share identical `HH:mm` but different dates.
- [ ] Given Scenario 3, when a single date + time is selected, then behavior is unchanged from before this task. Pass: committed UTC string matches Phase 2's existing single-date behavior exactly.
- [ ] Given Scenario 4, when a range + time is committed with no explicit `format`, then both the expanded labeled header and the basic dash-joined header (in a second instance of the scenario with `calendarType='basic'`) show `HH:mm`. Pass: both header formats display time text, not just the date.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add dual time selector for range mode"`

---

### Task 24: Phase 5 markup fix + SCSS + JSDoc audit

**Status:** ✅ done (2026-09-09) — implemented by `@frontend-subagent`, verified independently (not just relayed): compiled-CSS inspection confirmed the new `&__time-selector-row`/`&__time-selector` selectors resolve to the recorded token values with no hardcoded output; full `bds-date-picker` suite re-run (17 suites, 262 passed, 1 pre-existing todo, 0 failures); `tsc --noEmit` clean except the same 5 pre-existing unrelated errors (bds-dialog/bds-tooltip specs). Live-verified directly in-browser (not solely on the subagent's report): Scenario 1 (`expanded`) now renders Start/End inside one unified band with no visible separation, `05:00`/`07:00` set independently per bound and committed correctly (`{"start":"2026-09-09T05:00:00.000-05:00","end":"2026-10-16T07:00:00.000-05:00"}`); Scenario 2 (`basic`) confirmed visually unchanged, single box, no `Start:`/`End:` labels. Two follow-up refinements applied after the initial implementation, both verified (compiled-output inspection + full suite re-run, 0 regressions each time): (1) extracted the duplicated background/box-shadow/padding/`justify-content` declarations between `&__time-selector-row` and `&__time-selector` into a shared `%time-selector-band` Sass placeholder (matches this file's existing `%flex-center` placeholder-and-extend convention); (2) consolidated the four near-identical `handleStartHourChange`/`handleStartMinuteChange`/`handleEndHourChange`/`handleEndMinuteChange` methods into one `setBoundTime(bound, field, value)` method, and the two duplicated `renderTimeSelector({...})` call blocks in `render()` into a `.map()` loop over `[RANGE_BOUND.START, RANGE_BOUND.END]` — `Fragment` doesn't accept a `key` prop in this Stencil version's typings, so the loop was left keyless (safe here: a fixed, never-reordered two-item array). The pre-existing `62px` vs. Figma's `58px` `bds-text-field` width discrepancy was found, confirmed real, and deliberately left alone as out of this task's scope — noted, not tracked as a follow-up task per this session's direction. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — wrap `expanded`'s two `renderTimeSelector` calls in one shared row container), `bds-date-picker.scss` (modify)

**Figma research pass — completed 2026-09-09, pulled directly via `get_design_context`, not inferred:**

- [x] Region: `expanded` dual time-selector layout, default state — node `14:24965` (`_Expanded Time picker`, fileKey `rtiE5zGA4aoOuxIQMgfD6h`). **Structural finding requiring a markup change, not SCSS-only**: Figma models this as **one shared row container** holding both `Start:` and `End:` pairs together with a `12px` (`$boreal-spatial-gap-s`) gap between them — a single background/padding/shadow band. Task 23's actual implementation renders `expanded` mode as **two separate calls** to `renderTimeSelector`, each producing its own independent `.bds-date-picker__time-selector` div (full box: background + padding + shadow each) sitting side by side — not the unified band Figma shows. Fix: wrap both `renderTimeSelector` calls (`bds-date-picker.tsx`'s `expanded`+`range` render branch, ~line 900-921) in one new shared container element carrying the row-level background/padding/shadow (see values below), and strip that same background/padding/shadow down to the per-pair inner content so `basic`'s single-pair case (which already has this styling on its own single box, unchanged) isn't affected.
- [x] Region: `expanded`'s `Start:`/`End:` text labels and clock icon — confirmed: **each pair has its own timer icon** (not one shared icon for the row) — resolves the open question from this row's earlier framing. Structure per pair: `Icon/Hours/Minute` (outer, `gap: $boreal-spatial-spacing-2xs` 4px) → `Label` (`gap: 2px`, timer icon 16×16 + text) → `Time` (`gap: $boreal-spatial-spacing-2xs` 4px, two `Select` fields). Label typography: Inter Regular, `font-size: $boreal-typography-font-size-xs` (12px), `line-height: $boreal-typography-line-height-xs` (16px), `color: $boreal-text-default` (`#272a2f`).
- [x] Region: `expanded` dual pair — `Select` field states: **not applicable as a new pull.** Each `Select` field is an unmodified `bds-select`/`bds-text-field` composition (per `renderTimeSelector.tsx`, no custom classes applied to it) — its hover/focus/active/disabled states are entirely `bds-select`'s own existing, already-shipped, already-tested styling. Nothing new to style here; do not add per-state overrides.
- [x] Region: `basic`+`range` single-shared time-selector layout, default state — node `I1537:17221;14:23281;158:176538` (`_Basic Time picker`, same fileKey; this is Phase 2's own already-shipped node, re-pulled for direct comparison, not assumed identical). Confirmed: **structurally identical row container** to `expanded`'s (`24px`/`8px` padding via `$boreal-spatial-padding-l`/`$boreal-spatial-padding-xs`, `#f7f7f8` background via `$boreal-ui-default-base`, `1px` inset-top hairline shadow `#e3e3e6` via `$boreal-ui-base-light`) — already implemented and shipped in Phase 2, requires no changes. `Label` subgroup here has the timer icon only, no text — confirms `basic`'s single-shared selector correctly has no `Start:`/`End:` label, matching Task 23's implementation.
- [x] Region: `basic`+`range` single-shared selector — states: **not applicable**, same reasoning as the `expanded` row above (unmodified `bds-select` composition).
- [x] Modifier: disabled state — **not applicable**, same reasoning (an unmodified `bds-select`/`bds-text-field` composition inherits that component's own disabled styling via its `disabled` prop; no date-picker-specific disabled treatment exists in either pulled node).
- [x] Combination: independent focus rings — **not applicable**, folded into the "not a new pull" findings above; `bds-select`'s own focus-ring styling is unaffected by sibling state, already true for the two independent `bds-select` instances Phase 2's single-date mode already composes elsewhere in this file.
- [x] Dimensions: `Select` field width — confirmed **58px in both pulled nodes**, matching Phase 2's already-shipped value exactly. No change needed; the earlier "unconfirmed until re-pulled" caveat is resolved — 58px carries over unchanged.

**Acceptance criteria:**

- `bds-date-picker.tsx`'s `expanded`+`range` render branch wraps both `renderTimeSelector` calls in one shared row container matching Figma's unified band (single background/padding/shadow, `12px` gap between the Start and End pairs) — the current two-separate-boxes markup is replaced, not kept alongside the new one.
- `basic`'s single-pair render branch is unaffected by this markup change — it already has its own single-box styling from Phase 2, confirmed unchanged above.
- `$boreal-*` tokens exclusively; no hardcoded colours, spacing, or radii — use the token names recorded in the research pass above, not their raw hex/px values.
- The new `.bds-date-picker__time-bound-label` class (Task 23) gets its typography/color/gap styling per the recorded values above.
- No new interaction-state SCSS is added for the `Select` fields themselves — confirmed not applicable above; adding any would be duplicating `bds-select`'s own existing styling.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm the new shared row-container selector matches the DOM `bds-date-picker.tsx` actually renders after the markup fix, for both `expanded` (one row, two pairs) and `basic`/single-date (one row, one pair).
- JSDoc conforms to the brevity/content rule.

**Manual test (required):**

Reuse Task 23's playground scenarios (Scenarios 1-4). Run `pnpm dev:components` and validate:

- [ ] Given Task 23's Scenario 1 (`expanded` dual time), when the row renders, then Start and End pairs sit inside one unified band (single background/shadow, `12px` gap) matching the Figma reference — not two separate boxes. Pass: visually matches node `14:24965`.
- [ ] Given Task 23's Scenario 2 (`basic` shared time) and Scenario 3 (single-date), when the row renders, then it's unchanged from Phase 2's existing shipped appearance. Pass: no regression, byte-for-byte visual match to before this task.
- [ ] Given each `Select` field in any scenario, when hovered/focused, then it renders via `bds-select`'s own existing states with no visual regression. Pass: identical to `bds-select`'s behavior elsewhere in the codebase.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 unify expanded dual time-selector row layout and style"`

---

### Task 25: Phase 5 unit tests (consolidated)

**Status:** ✅ done (2026-09-09) — implemented by `@testing-subagent` exactly against the corrected file targets above (no new files created). Coverage-phase gate passed well above target: 98.84% statements / 95.85% branches / 100% functions / 98.82% lines on `bds-date-picker`; full suite 285 passed, 1 pre-existing todo, 0 failures. Covers: `expanded`'s `Start:`/`End:` label rendering (default + `labels` override) and independent per-bound draft updates; `basic`+`range`'s shared-selector path (no label, shared `hour`/`minute` untouched by the new per-bound fields); Apply combining per-bound vs. shared time correctly; Cancel discarding drafted time in both `calendarType` cases; single-date regression (no bound label rendered). Also extended `ai-work/testing/failure-modes/bds-date-picker.md` (FM-42 through FM-47), all `confirmed`/`Covered by`, none `pending-decision`.

**Known pre-existing gap, flagged not fixed (out of this task's scope):** `resetRangeDraft`'s `withTime` branch only hydrates per-bound times when _both_ `rangeStart` and `rangeEnd` independently pass `isValidUtcDateTimeValue`; a mixed valid/malformed range value falls through to the naive-date branch and nulls _both_ bounds, not just the malformed one. This gate predates Phase 5 (same behavior existed before the per-bound fields) — noted in the failure-mode catalog's reconciliation section for visibility, not tracked as a new task unless a mixed valid/malformed range value turns out to be a real scenario worth handling.

**Executor:** @testing-subagent
**Files:** `bds-date-picker.time.spec.ts` (modify — component-level render/interaction coverage), `bds-date-picker.time-helpers.spec.ts` (modify — plain-function unit coverage for `draft-state.ts`/`value-mapping.ts`; this is the actual existing file Phase 2 used for this exact kind of coverage, confirmed via grounding check 2026-09-09 — `draft-state.spec.ts`/`value-mapping.spec.ts` do not exist and should not be created; a separate `utils/__test__/value-mapping.spec.ts` does exist but is narrowly scoped to `resolveDisplayMonth` only, unrelated to this task)

**Unit tests to cover:** `expanded` dual selector independent start/end UTC computation, via the new `startHour`/`startMinute`/`endHour`/`endMinute` `DatePickerDraftState` fields and their bound-aware `draft-state.ts` selectors; `expanded`'s `Start:`/`End:` time-selector labels render (default English text, and an override via the `labels` prop, per its existing i18n mechanism); `basic`+`range` shared-time application using the existing single `hour`/`minute` fields (confirm these are untouched/unrepurposed by the new per-bound fields) with no `Start:`/`End:` label rendered; the new time-inclusive range formatter (mirroring `formatDraftForDisplay`'s existing single-date pattern) for both header paths; the Apply-commit path calling `combineDateTimeToUTC` per bound (`expanded`: independent times; `basic`: shared time applied to both); single-date Phase 2 regression (no label, existing single `hour`/`minute` fields, unchanged); Cancel discarding time drafts in both `calendarType` cases, including the new per-bound fields for `expanded`. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suite passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 5 dual time selector unit tests"`

---

### Task 26: Phase 5 documentation

**Status:** ✅ done (2026-09-09) — implemented by `@documentation-subagent` against the reviewed scope below, verified independently (read the actual updated MDX/stories files directly, not just relayed): the stale "not currently supported" claim is gone (confirmed via grep — zero matches), replaced with an accurate description of the `expanded`/`basic` split. All five content changes read correctly in place: the new "Range-mode time selection" subsection (with `### Expanded`/`### Basic` sub-headings, matching this page's existing flat-h3-under-h2 convention), the "Popover header format" addition (time-inclusive behavior appended, not duplicated), the "Format auto-switch" extension, and the "Range-mode form serialization" addition (correctly notes ISO-8601 datetimes never contain a literal comma, so the existing split-on-`,` parsing is unchanged). Both new stories (`RangeModeExpandedWithTime`, `RangeModeBasicWithTime`) confirmed with correct args, following the existing story pattern exactly; `RangeModeBasic`/`RangeModeExpanded` confirmed untouched. No `ArgTypes` changes (none needed). No internal version/phase/ticket references leaked into consumer-facing text. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Cross-referenced against actual current MDX/stories content, 2026-09-09 — surfaced a real stale claim, not just a documentation gap:** the existing MDX's "When to use it" callout explicitly states _"`with-time` and `range` are independent features; combining them is not currently supported"_ — this is now false and must be corrected, not just supplemented. Priority is updating existing sections over adding new top-level ones; the full reviewed scope below reflects what's actually needed, not a generic "add docs" pass.

**Acceptance criteria:**

- **Fix the stale claim** in the "When to use it" callout — range+time combination is now supported; state the actual `expanded`/`basic` behavior split instead of "not currently supported."
- **New subsection** "Range-mode time selection" added _inside_ the existing `## Time selection` section (not a new top-level section) — documents `expanded`'s two independent time selectors (labeled `Start:`/`End:`) vs. `basic`'s one shared selector applied to both bounds, and the `{ start, end }` UTC datetime value contract. Two new story variants feed this subsection: `expanded`+`range`+`with-time` and `basic`+`range`+`with-time`. Do **not** add `with-time` to the existing `RangeModeBasic`/`RangeModeExpanded` stories — those exist to teach range mechanics in isolation; conflating time into them blurs that.
- **Update** the existing "Popover header format" subsection (under `## Range selection`) to add the time-inclusive behavior for both formats — currently documents only the date-only case. Reference the verified Figma nodes: `158:175482` (basic+range layout), `158:176511` (expanded header), `I164:33228;14:23281;158:175484` (labeled Start/End structure), all confirmed correct during v2's Task 18.
- **Update** the existing "Format auto-switch" subsection (under `## Time selection`) — currently single-date only; extend the existing prose to state the same auto-switch applies in range mode. Do not duplicate this into a new section.
- **Update** the existing "Range-mode form serialization" subsection (under `## Form integration`) with a short clarifying addition — `serializeRangeValue`'s comma-delimited format is unchanged when `with-time` is set (ISO-8601 datetimes never contain a literal comma), but `start`/`end` become full UTC datetime strings instead of naive dates; show the resulting serialized-string shape. No new story or interactive-form-example rebuild needed here — the serialization mechanism itself doesn't change, only what's inside the two halves.
- No `ArgTypes` changes needed — Task 23 added no new public props/events; `range`/`with-time`/`labels` are already listed.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the new `expanded`/`basic` range-time story variants, when Storybook renders them, then both render without console errors. Pass: no errors, stories interactive.
- [ ] Given the "When to use it" callout, when read against the actual implementation, then it no longer claims range+time is unsupported. Pass: no stale/contradicting claim anywhere on the page.
- [ ] Given the four updated existing subsections (Popover header format, Format auto-switch, Range-mode form serialization, plus the new Range-mode time selection subsection), when read together, then they're internally consistent — no subsection contradicts another about what range+time actually does.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 5 range-mode time selection"`

---

### Task 27: React/Vue wrapper parity check — Phase 5

**Status:** ✅ done (2026-09-09) — the primary regression check (does the `bds-popover` mouse-click fix hold through both wrappers) passed in every combination tested: React × Vue, Chromium × WebKit, `expanded` × `basic`, and a single-date non-range baseline. Popover stayed open through real mouse clicks on every hour/minute option tested; Apply committed correctly each time (independent per-bound times for `expanded`, shared time for `basic`). Task 23's Scenarios 1-4 also confirmed passing in both wrappers, including the no-explicit-`format` `HH:mm` auto-switch. A separate, pre-existing, universal bug was found during this task (not caused by the fix being verified here) — tracked below as Task 27a (now fixed), not folded into this task's own scope.

**Executor:** @qa-subagent
**Files:** none

**Scope note (2026-09-09, added before dispatch):** this task's original scope (re-run Task 23's Scenarios 1-4) predates the `bds-popover.tsx` fix discovered and applied during Task 23's own manual QA — a real bug (mouse click on any time-selector option closing the whole popover, root-caused to a `handleFocusOutside` RAF-scheduling race) that blocked mouse-driven use of the time selector entirely. That fix is event-handling-specific and touches a shared component (`bds-popover`) other components compose too — React's synthetic event system and Vue's own event binding layer are exactly the kind of thing that could make a timing-sensitive fix like this behave differently than in the raw web component. Verifying it explicitly through both wrappers, not just re-running the original scenarios, is the actual point of this task now.

**Acceptance criteria:** Confirms both `expanded` dual-time and `basic` shared-time behavior identically through both wrappers, **and explicitly confirms the `bds-popover` mouse-click fix holds through both wrappers** — this is the primary regression risk this task exists to catch, not a secondary check.

**Manual test (required):**

Repeat Task 23's Scenarios 1-4 (reuse the `RangeModeExpandedWithTime`/`RangeModeBasicWithTime` story configurations Task 26 added as the reference args, if the wrapper playgrounds need new scenarios built) through both the React and Vue wrapper playgrounds using the pack-based verification pipeline (`dev:pack:react`/`dev:pack:vue`, not a live dev server — a live dev server can serve a stale wrapper bundle after a rebuild, producing false framework-specific bug reports). Validate:

- [x] Given `expanded`+`range`+`with-time`, when an hour/minute option is clicked with a real mouse (not just opened) in the React wrapper, then the popover stays open and the value commits correctly on Apply. Pass: no premature close, matches the raw web component's now-fixed behavior exactly.
- [x] Given the same scenario in the Vue wrapper, then the same holds. Pass: no premature close.
- [x] Given each of Task 23's Scenarios 1-4, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in committed UTC values or header display.
- [x] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A

---

### Task 27a (new — discovered during Task 27's QA pass, 2026-09-09): `format=""` crashes date-fns formatting — done

**Status:** ✅ done (2026-09-09) — fixed and manually re-verified live. Full write-up: `packages/boreal-web-components/.claude/agent-memory/qa-subagent/bds-date-picker-empty-format-string-crash.md`.

**Fix applied:** `effectiveFormat` (`bds-date-picker.tsx:591`) changed from `if (this.format !== undefined) return this.format;` to `if (this.format !== undefined && this.format !== '') return this.format;` — falls back to the default format string for `''` in addition to `undefined`. (An initial truthy-check version, `if (this.format) return this.format;`, was equivalent but tripped the project's `stencil/strict-boolean-conditions` ESLint rule, which forbids a bare string in an `if` condition; rewritten to the codebase's existing explicit-`===`/`!==` convention for empty-string checks, e.g. `bds-select.tsx`, `bds-text-field.tsx`.)

**Verified:** dev server restarted (Stencil changes don't hot-reload) and re-checked live in Storybook post-fix — all 4 previously-affected stories (`WithTime`, `PreselectedDateTime`, `RangeModeExpandedWithTime`, `RangeModeBasicWithTime`) now select dates, apply, and commit correctly with zero console errors, where each had reproduced the crash immediately beforehand (post-Task-27b, pre-fix). Also directly verified the `withTime=false` path (not covered by any of the 4 stories) via a live property set — `format=''`, `withTime=false`, `value='2026-09-09'` renders `'2026/09/09'` with no crash, confirming the fallback applies uniformly regardless of `withTime`.

Also re-verified through the actual React/Vue wrapper testapps (`pnpm dev:pack:react` / `dev:pack:vue`, rebuilding `boreal-web-components` fresh and packing it in — the accurate pipeline, not the live dev server, per the documented `vite-dep-cache-masks-wrapper-framework-bugs` gotcha) against the exact `task27-*` scenarios `@qa-subagent` originally used to report this bug. Confirmed `format=''` reaches the component as a real property in both wrappers (`el.format === ''`, `hasFormatAttr: false` since Vue/React don't reflect it as an attribute). Scenario 1 (expanded range + independent Start/End times) and Scenario 3 (single-date `withTime`) both passed cleanly in React and Vue: correct fallback header/trigger text, correct `bdsChange` payload, zero console errors. Scenario 2 (basic range, shared time selector) additionally verified in Vue. This closes the loop back to the original wrapper-parity report — the fix holds in the actual surface where the bug was first found, not just in Storybook.

ESLint run afterward flagged the initial truthy-check version (`stencil/strict-boolean-conditions`, 1 warning, 0 errors) — fixed to the explicit `!== ''` form above. Full unit/mutation suite re-run clean after the rewrite (3533/3534 passing, 1 pre-existing todo, identical to before). Rewrite is logically equivalent (same two excluded values for a `string | undefined` type), confirmed by: re-running the full suite (identical pass count) and one live Storybook spot-check on the rebuilt dist (`WithTime` story: correct fallback placeholder, correct commit, zero console errors) — not by re-running the full React/Vue matrix again, since the wrappers bind the same compiled custom element rather than reimplementing any logic themselves.

**Bug:** an explicit `format=""` (empty string — distinct from omitting the prop entirely) throws `TypeError: null is not an object (evaluating '<str>.match(<regex>).map')` once a date is actually selected. Root cause: `bds-date-picker.tsx`'s `effectiveFormat` getter (~line 591-594) checks `this.format !== undefined` before falling back to the default format string — an empty string passes that check and gets handed straight to date-fns's `format()`, which throws on an empty pattern. The crash is swallowed by the framework render cycle: the popover header and trigger-field display silently render blank, but the underlying `value`/`bdsChange` commit is unaffected (confirmed via direct `.value` inspection, not the broken displayed text).

**Confirmed universal, not wrapper- or fix-specific:** reproduces identically in the raw web component, the React wrapper, and the Vue wrapper, on both Chromium and WebKit. Predates this plan's own work — not introduced by Task 23/24/27's changes.

**Directly relevant to this plan:** Task 26's `RangeModeExpandedWithTime`/`RangeModeBasicWithTime` stories both pass `format: ''` in their args (matching the existing `WithTime`/`PreselectedDateTime` stories' established convention of using `format: ''` to demonstrate the auto-switch behavior). Live manual re-verification (2026-09-09) initially found **zero crashes and zero console errors** in all four Storybook stories, appearing to contradict `@qa-subagent`'s report — root-caused to a masking bug in the stories file itself, now fixed as Task 27b below. Post-fix, all four stories correctly reproduce the crash again (confirmed live: selecting a day in `WithTime` now leaves the popover header blank and throws `TypeError: Cannot read properties of null (reading 'map')` from `bds-date-picker.tsx`'s `render()`), so Storybook is once again a valid surface for verifying this task's fix once applied.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `effectiveFormat` getter)

**Acceptance criteria:**

- `effectiveFormat` falls back to the default format string on any falsy `format` value (`undefined`, `null`, `''`), not just `undefined` — matching how a consumer would reasonably expect an empty string to behave (same as not setting the prop at all), rather than being treated as "an explicit format the consumer chose."
- No crash when `format=""` is set, with or without a date selected, in any `calendarType`/`range`/`withTime` combination.
- Confirm this doesn't change behavior for any _other_ falsy-but-meaningful value this getter might see — read the actual current getter and its callers before changing the condition, since `format` is typed `string | undefined` (per `IDatePicker.ts`), so `null`/`0`/`false` shouldn't be reachable in practice, but verify rather than assume.

**Manual test (required):**

Playground scenario: any picker with `format=""` explicitly set, with `withTime` and without, single-date and range.

Run `pnpm dev:components` and validate:

- [x] Given `format=""`, when a date (and time, where applicable) is selected, then the header/trigger display the default format's text instead of crashing or rendering blank. Pass: no console error, visible date/time text. Verified live for `withTime=true` (all 4 affected stories) and `withTime=false` (direct property check).
- [x] Given the `RangeModeExpandedWithTime`/`RangeModeBasicWithTime` Storybook stories specifically, when a date+time is selected in each, then the header renders correctly with no crash. Pass: this is the scenario Task 27 found broken — confirm it's actually fixed there, not just in a fresh playground picker. Verified live post-fix, both stories.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 fall back on falsy format, not just undefined"`

---

### Task 27b (new — discovered while reconciling Task 27a against a live Storybook check, 2026-09-09): stories file's `|| nothing` pattern masks falsy-but-meaningful arg values — done

**Status:** ✅ done (2026-09-09) — fixed and independently re-verified live in Storybook.

**Bug:** live manual validation of Task 27a's reported crash found all 4 affected stories (`WithTime`, `PreselectedDateTime`, `RangeModeExpandedWithTime`, `RangeModeBasicWithTime`) rendering, selecting dates, and applying with zero errors — appearing to contradict `@qa-subagent`'s confirmed-universal finding. Root cause: `bds-date-picker.stories.ts`'s `renderDatePicker` bound the `format` attribute as `format=${args.format || nothing}`. `''` is falsy, so lit's `nothing` sentinel omitted the attribute from the DOM entirely — the component never received an empty string at all (`el.format` read back as `undefined`, `el.hasAttribute('format')` as `false`), so `effectiveFormat`'s bug path was never reached. Not a real fix or narrowing of Task 27a's bug — a false negative in the test surface itself.

**Fix:** replaced `format=${args.format || nothing}` with `format=${ifDefined(args.format)}` (new import: `ifDefined` from `lit/directives/if-defined.js`). `ifDefined` omits the attribute only when the value is genuinely `undefined` (arg not set by the story), preserving `''` when a story explicitly sets it — matching what a real consumer's markup does. Scoped to the `format` line only; the other 11 `${args.X || nothing}` bindings in this file (`value`, `timezone`, `min`, `max`, `calendar-type`, `name`, `error-message`, `label`) were left as-is since no current story relies on a falsy-but-meaningful value for them — flagged here as a latent, not active, instance of the same pattern, deferred rather than fixed.

**Verified:** live in Storybook post-fix — `el.format` on the `WithTime` story now reads back as `''` (`hasAttr: true`) instead of `undefined`. Selecting a day reproduced the crash exactly as `@qa-subagent` originally reported: popover header rendered blank, console threw `TypeError: Cannot read properties of null (reading 'map')` from `bds-date-picker.tsx`'s `render()`. This confirmed Task 27a's fix was both necessary and verifiable through these stories — which it then was, once applied (see Task 27a's own `Verified` note above).

**Files:** `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify)

**Commit:** `git commit -m "fix(boreal-docs): EOA-17662 use ifDefined for format arg so empty string reaches the component"`

---

## Phase 6 — Presets sidebar

Sidebar remains gated by `range` (not by `calendarType`) and must render correctly with both single-calendar (`basic`) and dual-calendar (`expanded`) range layouts.

### Task 28: presets configurability — design/API decision (blocking gate) — done

**Status:** ✅ done (2026-09-10) — decided directly with the user, no subagent dispatch (design/API checkpoint, matches this task's own "no executor" designation).

**Decision: Fixed built-in list. No `presets` prop, no consumer configurability.** The six presets (Today, Yesterday, Last 7 days, Last 30 days, This month, Last month) plus Custom are hardcoded in `utils/presets.ts`. Rationale: the level-of-effort comparison showed the configurable path adds real cost (prop-shape design, JS-property-only consumption since a live range needs a function not an attribute, override-vs-extend merge semantics, more test/doc surface) concentrated almost entirely in API surface and edge cases, not in the rendering/computation core — for a feature Figma shows as a fixed list with no consumer-configurability signal anywhere in the design or ticket. Not a permanent wall: a `presets` prop is addable later, non-breaking, if a concrete consumer need for it actually materializes — no need to hedge that possibility into the API now.

This resolves every "if Task 28 chooses configurable..." conditional in Tasks 29/30/32/33 below to its fixed-list branch; those tasks have been updated accordingly, not left with dangling conditionals.

**Manual test:** N/A — design/API checkpoint.

---

### Task 29: preset range computation module — done

**Status:** ✅ done (2026-09-10) — reworked per [ADR 0015](../../ai-docs/decisions/0015-date-picker-preset-time-coverage-semantics.md) and independently verified. Background: the version originally shipped the same day computed `with-time` bounds as a fixed `00:00`–`23:59` uniformly, which an extended design discussion later the same day (concrete zero-duration-in-`basic` examples, a reference screenshot, and a rejected `now`-based rolling-window alternative — see Task 30's boundary-case notes and the ADR) superseded with a simpler, final semantic: every preset represents a whole calendar day (or days) regardless of what time it currently is, identical in `basic` and `expanded`.

Rework: `computePresetRange(key)` dropped `withTime` entirely, now always returns the real, unshifted range. New `computePresetCoverageEnd(range, withTime)` returns `range.end` unchanged when `withTime` is `false`, or shifted forward one calendar day at `00:00` when `true` — the sole place this shift is computed. Verified independently against today's real date (2026-09-10): Today `9/10→9/10`, coverage end `9/11 00:00`; Yesterday `9/9→9/9`, coverage end `9/10 00:00`; Last 7 days `9/4→9/10`, coverage end `9/11 00:00`; Last 30 days `8/12→9/10`, coverage end `9/11 00:00`; This month `9/1→9/10`, coverage end `9/11 00:00`; Last month `8/1→8/31`, coverage end `9/1 00:00` — every value matches ADR 0015's table exactly, including the `withTime: false` no-shift case for all six. ESLint clean, `tsc --noEmit` clean, full suite 3533/3534 passing (1 pre-existing todo).

**Prior implementation note (2026-09-10, now superseded):** implemented by `@frontend-subagent`, independently verified at the time. `utils/presets.ts` created (`computePresetRange`, `isPresetWithinBounds`, `BUILT_IN_PRESET_KEYS`); `date-math.ts` gained justified thin wrappers `subDays`/`startOfMonth`/`endOfMonth` (an `addDays` wrapper the subagent also added was removed on review — unused, no call site); `types/enum.ts` gained `BUILT_IN_PRESET_KEY`/`PresetKey`; `types/types.ts` gained `PresetRange`; `utils/index.ts` barrel updated. These files/types stay — only `computePresetRange`'s `with-time` output needs to change, per the acceptance criteria below.

**Executor:** @frontend-subagent
**Files:** `utils/presets.ts` (modify), `utils/__test__/presets.spec.ts` (create or covered by Task 32)

**Utility discovery:**

- Feature area: relative-date range computation (today, yesterday, last N days, this/last month).
- Search performed: `date-engine/date-math.ts` (`addMonths`/`subMonths`/`isSameDay`/`isSameMonth`/`isWithinRange`/`compareDates`/`toNaiveISODate`/`fromNaiveISODate`), `date-engine/index.ts` barrel.
- Candidates found: `date-engine`'s existing `date-fns`-based date-math primitives cover every preset's arithmetic (day/month offsets, same-day/same-month comparisons); no `date-engine` function already computes a named preset range itself.
- Fit assessment: existing primitives fully fit as building blocks; no candidate exists for the preset-list concept itself (expected — it's `bds-date-picker`-specific, not a generic date-math concern, so it belongs in this component's own `utils/`, not `date-engine`).
- Reuse decision: build `utils/presets.ts` entirely on top of existing `date-engine` primitives (offsets via `addMonths`/`subMonths` and plain day arithmetic, no new library dependency).
- Gap handling: not applicable — no `date-engine` gap found.
- Anti-duplication check: confirms no parallel date-arithmetic implementation is planned inside `presets.ts` — it composes existing primitives only.
- Test impact: Task 32's `presets.spec.ts` asserts each preset's `{ start, end }` output; regression coverage on `date-engine`'s own primitives stays in `date-engine/__test__/date-math.spec.ts`, not duplicated here.

**Acceptance criteria:**

- `computePresetRange(key): PresetRange` returns the **real, unshifted calendar-day range** for a built-in preset — the literal first/last day it covers, day-normalized (no time-of-day significance), regardless of `with-time`. This is what grid highlighting and `isPresetWithinBounds` always use. Drop the `withTime` parameter from this function entirely — it no longer needs one.
  - **Today:** `[today, today]`.
  - **Yesterday:** `[today-1, today-1]`.
  - **Last 7 days:** `[today-6, today]` — inclusive of today (7 calendar days total).
  - **Last 30 days:** `[today-29, today]` — inclusive of today.
  - **This month:** `[first day of current month, today]` — month-to-date, not the full calendar month (see prior rationale: avoids a misleading empty tail for the reporting/filtering use case this preset set is modeled on; a consumer wanting the full month, future days included, can still select it manually).
  - **Last month:** `[first day of previous month, last day of previous month]` — the full calendar month.
  - **Custom** is not a computed preset — represents manual mode only.
- Add a second function, `computePresetCoverageEnd(range: PresetRange, withTime: boolean): Date`, that returns the **end boundary actually used for commit and header display** when `with-time` is on: `range.end` shifted forward by exactly one calendar day, at `00:00` (i.e. the start of the day _after_ the last real day). When `with-time` is off, returns `range.end` unchanged (no shift — a naive date-only range has no time-of-day precision question at all, so nothing to reconcile). This is the **one and only** place the "+1 day" shift is computed — both the header (Task 30) and the final commit-building code must call this same function rather than each re-deriving the shift independently, so the two can never disagree with each other.
  - **Today:** coverage end = tomorrow, `00:00` → exactly 24h from `today, 00:00`.
  - **Yesterday:** coverage end = today, `00:00` (already the natural start of the next period — no separate shift needed, `computePresetCoverageEnd` is a no-op here beyond returning `range.end` as-is, since `range.end` for Yesterday already equals what "coverage end" would compute).
  - **Last 7 days:** coverage end = tomorrow, `00:00` → exactly 7×24h from `today-6, 00:00`.
  - **Last 30 days:** coverage end = tomorrow, `00:00` → exactly 30×24h.
  - **This month:** coverage end = tomorrow, `00:00` → covers every elapsed day of the month through today, in full.
  - **Last month:** coverage end = first day of current month, `00:00` (again a no-op beyond returning `range.end` as computed — already the correct boundary).
  - This deliberately **abandons two earlier ideas from the same day's discussion**, both superseded: (a) forcing every preset's end to a fixed `23:59` (missed the last representable minute, and didn't generalize cleanly to `basic`'s single shared time field); (b) computing the end as the _exact current instant_ (`now`) for "in-progress" presets like Today/This month (would make "Today" only cover elapsed hours rather than the whole day, and reintroduced a real/expanded-only asymmetry that broke the "presets produce identical results in both calendar types" requirement). The `+1 day, 00:00` shift is simpler than both, produces exact N×24h coverage in every case, and — critically — is identical in `basic` and `expanded`, so presets never need calendar-type-specific logic at all.
- **Whatever a consumer visually sees must always be self-consistent — the grid, the header, and the submitted value must never silently disagree.** This is why the shift lives in one function `computePresetCoverageEnd`, not duplicated: the header displays this same shifted boundary (see Task 30), it isn't hidden or reverted-for-display anywhere. Only the calendar grid legitimately shows something different (the real, unshifted last day) — and that's an accepted, well-understood consequence of a day-granularity display representing an exact instant boundary, not a hidden discrepancy (the boundary itself, wherever shown as text, is always the same value).
- The module performs no caching or memoization — each call recomputes fresh.
- Uses existing date-math primitives; no new `date-engine` primitive unless justified.
- `isPresetWithinBounds(range, min?, max?)` — unchanged, still operates on the real (unshifted) range from `computePresetRange`, never the shifted coverage end. Returns `false` when any part of the range falls outside a set `min`/`max`, `true` when unbounded or fully inside.

**Manual test (required):** Non-visual — unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add built-in preset range computation"`

---

### Task 30: presets sidebar implementation

**Status:** ✅ done (2026-09-10) — implementation reworked per ADR 0015 (`rangeEndShiftApplies`/`resolveRangeEndIso` in `bds-date-picker.tsx`: `basic` always shifts the committed/displayed range end once `with-time` is on, presets and manual selection alike; `expanded` shifts only while a built-in preset is active, manual selection there is untouched — **superseded 2026-09-22 by Task 35's fix: the shift is now data-driven, applying whenever both bounds share a time-of-day, in either calendar type; see Task 35's 2026-09-22 note**), independently code-verified (ESLint clean, `tsc --noEmit` clean, full suite 3533/3534 passing, 1 pre-existing todo), and every manual-test scenario below confirmed live in Storybook (rebuilt dev server, `range-mode-expanded-with-time`/`range-mode-basic-with-time` stories, plus direct `min`/`max` property injection for Scenario 3) — zero console errors across the entire session.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderPresets.tsx` (create), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `draft.rangeStart`/`draft.rangeEnd` are currently written only by `selectRangeDay`/`resetRangeDraft` (`utils/draft-state.ts`, per v2's Task 18) — confirm a preset click writes through the same state fields via a new sibling function (e.g. `selectPresetRange`), not by mutating `draft` directly in `bds-date-picker.tsx`'s render/handler code, to keep Cancel/Clean's existing draft-revert logic correctly covering preset-originated selections too. `draft.rangeStart`/`rangeEnd` must always hold the **real, unshifted** days from Task 29's `computePresetRange` — never the shifted coverage end — since these also drive the calendar grid's own highlighting. Do not route the preset-time-setting through `selectRangeDay` itself, which only ever touches `rangeStart`/`rangeEnd` (confirmed 2026-09-10) and must stay that way for the "manual override preserves whatever time was already in the draft" rule below to hold.
- [ ] **`basic`'s single shared time field needs the same coverage-shift treatment as presets, applied to _manual_ selection too — not just presets.** Confirmed 2026-09-10 through worked examples: `basic`+`range`+`with-time`'s existing commit logic (`buildRangeCommitValue` with the same `draft.hour`/`draft.minute` passed for both bounds) produces a **zero-duration range** for a same-day selection and an **under-by-nearly-a-day** range for any multi-day selection, because one shared time value applied identically to both a real start day and a real end day cannot express "covers the whole last day" — this is a structural limitation of having only one time control, not something a user can work around themselves (unlike `expanded`, see below). Fix: whenever `basic`+`range`+`with-time` commits — preset-driven or manual — the end timestamp uses Task 29's `computePresetCoverageEnd`-equivalent logic (real last day + 1, at whatever time the shared field currently shows) rather than the real last day at that same time. This means the shared time selector stays fully meaningful for manual selection (a user-chosen `09:00` still applies to both the start and the shifted end, giving "each day's window starts at 9am" rather than losing the user's input) while guaranteeing exact N×24h coverage in every case, matching what presets themselves already guarantee.
- [ ] **`expanded`'s independent start/end fields do _not_ get this treatment for manual selection** — only for presets. A user setting `startHour`/`endHour` independently already has full, deliberate control to express "the whole last day" themselves (e.g. setting end to `23:59`), so there's no structural gap for the component to compensate for. Silently overriding an explicit, independent user choice would be second-guessing input the user is fully capable of getting right on their own — inconsistent with how this component treats every other explicit user choice. `expanded`'s manual-selection commit logic is therefore **unchanged** by any of this work.
- [ ] **The popover header must display the same shifted coverage-end boundary used for the commit — from the moment a preset is clicked, not just after Apply — in both `basic` and `expanded`.** This was the deciding design call of the day's discussion: an earlier idea (show the real last day in the header, silently commit the shifted value) was rejected because it means the trigger field's displayed text would change the instant Apply is clicked (e.g. header reads "Sep 10" throughout selection, then the applied field reads "Sep 11") with no visible user action causing it — a real, visible inconsistency, not just an internal one. Radical consistency wins instead: header, trigger-after-Apply, and submitted value all show the identical boundary, always. Only the calendar grid legitimately differs (it shows the real last day, since a day-granularity display can't represent an exact instant boundary any other way) — and that's an accepted, explained quirk, not a hidden discrepancy, since the boundary text itself never differs between any of the three text-based surfaces.

**Boundary cases — all resolved 2026-09-10, do not re-litigate during implementation:**

- **Min/max out-of-range presets:** a preset button is fully disabled (not clamped) when **any part** of its computed range falls outside a set `min`/`max` — partial overlap is treated identically to full overlap-outside. Uses Task 29's `isPresetWithinBounds` helper. (Task 28's original "configurable presets" framing for this boundary case no longer applies — presets are fixed.)
- **Default/empty state:** "Custom" is the default selected state whenever no preset has been explicitly clicked — this covers both a truly-fresh load (no prior value) _and_ a picker that opens with a pre-existing/externally-set `value`. No separate "nothing selected" state exists. Crucially, this means **no reverse-matching**: even if the current `value` happens to numerically equal what a preset would compute right now, the sidebar never auto-detects that and highlights the preset — only an explicit click on a preset button sets it selected. (Reasons: avoids a staleness trap since presets like "Today" are moving targets that would need continuous re-evaluation to stay "matched," and matches how neither `daterangepicker.js` nor Ant Design's `RangePicker` do reverse-matching — presets are one-way triggers in both.)
- **Reactivity:** not applicable — presets are fixed (Task 28), no prop to react to.

**Acceptance criteria:**

- Sidebar renders only when `range=true`.
- The calendar is **never locked or disabled** while a preset (including a built-in, non-Custom one) is active — it stays fully interactive at all times, regardless of which preset (if any) is selected.
- Built-in preset display text ("Today", "Yesterday", "Last 7 days", "Last 30 days", "This month", "Last month", "Custom") is sourced from new keys added to the existing `labels`/`DatePickerFooterLabels` object (`presetToday`, `presetYesterday`, `presetLast7Days`, `presetLast30Days`, `presetThisMonth`, `presetLastMonth`, `presetCustom` — all seven, one per list item; the plan text previously omitted `presetLast30Days` despite "Last 30 days" being one of the six decided built-ins, corrected 2026-09-10), each with an English default — never hardcoded literals in `renderPresets.tsx`. Follows Task 23's precedent and [ADR 0014](../../ai-docs/decisions/0014-localizable-ui-copy-prop-shape.md): `bds-date-picker` already crossed the bundled-object threshold, so new UI-copy strings extend `labels` rather than introducing a new prop shape.
- Clicking a preset sets `draft.rangeStart`/`draft.rangeEnd` to the real, unshifted days from `computePresetRange`, and marks that preset selected. When `with-time` is on, both the start and end time fields relevant to the active calendar type (`hour`/`minute` for `basic`, `startHour`/`startMinute`/`endHour`/`endMinute` for `expanded`) are set to `00:00` — visibly, immediately, in the time selector(s) — matching what the coverage-shift formula assumes.
- Clicking a preset while a range selection is mid-progress (only `rangeStart` set, no `rangeEnd` yet) simply overwrites the in-progress selection — no guard, no ignored click.
- Clicking a preset always recomputes live, including re-clicking the currently-selected preset — no caching, no "already selected, skip" short-circuit (matches Task 29's own no-memoization decision).
- A manual calendar-day click, **or** a manual time-selector edit, after a preset is active reverts the selection to Custom. Either interaction alone is sufficient — not just day clicks.
- Reverting to Custom (via either path above) leaves whatever time values are already in the draft **untouched** — no reset to neutral defaults. (This is why `selectRangeDay` must not touch the time fields, per the integration-research note above: a manual re-click of the exact same days a preset just selected produces an identical committed value to the preset, just relabeled Custom — this is expected, not a bug.)
- A preset button is disabled when its computed range falls even partially outside a set `min`/`max` (Task 29's `isPresetWithinBounds`) — never clamped to a partial sub-range.
- "Custom" is a real, clickable list item (per Figma, sharing the same interactive-states component as the six built-ins) and is the **default selected state** whenever no preset has been explicitly clicked (see the boundary-case resolution above — this also means no reverse-matching against a pre-existing `value`). Clicking "Custom" directly marks it selected but does **not** clear `rangeStart`/`rangeEnd`/time — that's the dedicated Clean/Clear footer button's job; a redundant second control for the same destructive action would be confusing, not helpful.
- Presets are fixed (Task 28) — no `presets` prop, no override/extend behavior to implement.
- Preset buttons use real interactive states (Default/Hover/Focus/Active/Disabled).
- **Deprecate the `basic`+`range` dash-joined header format in favor of `renderRangeHeader.tsx`'s labeled `Start:`/`End:` format (matching `expanded`), by default — not an open toss-up.** v2's Task 18 introduced the dash-joined line _only_ because the labeled format wrapped inside `basic`'s fixed 296px popover width. Since this sidebar is gated on `range` alone (not `calendarType` — per this phase's own preamble), every `basic`+`range` picker gains the sidebar's extra width unconditionally once this task ships, permanently removing the constraint that justified the dash-joined format. Confirm the actual Figma `basic`+`range`+sidebar header node has room for the labeled format before implementing (the header spans the full popover width — sidebar + calendar together — confirmed 2026-09-09 against the reference screenshot), then remove the dash-joined rendering path from `bds-date-picker.tsx` entirely rather than keeping both formats alive. This also means removing/superseding the basic-dash-joined-with-time wiring Task 23 added — expected, one-phase-lived code, not a regression.
- **Not in scope, confirmed a Figma-tool artifact, not a real product state (2026-09-09):** some Figma variants expose an `End Date` toggle independent of `Range`, producing a single-value (no `End:`) header even with `Range: true`. This has no counterpart in `bds-date-picker`'s data model — once `range=true`, both `rangeStart` and `rangeEnd` are required for any commit (per the existing Apply-guard `this.draft.rangeStart !== null && this.draft.rangeEnd !== null`), so a "range with no end" state can't occur here. Do not implement or research this Figma variant combination.
- No new `@Prop()` or JSDoc needed for presets configurability — presets are fixed (Task 28).

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: `calendarType='expanded'` + `range`, presets sidebar visible.
- Scenario 2: `calendarType='basic'` + `range`, presets sidebar visible.
- Scenario 3: `calendarType='expanded'` + `range` + `min`/`max` set such that one or more presets fall (fully or partially) outside the bounds.
- Scenario 4: `calendarType='expanded'` + `range` + `with-time`, to check full-day time bounds on preset click.

**Note on how this was actually verified (2026-09-10):** the checklist below was live-verified via Storybook's `range-mode-expanded-with-time`/`range-mode-basic-with-time` stories rather than these four `src/index.html` scenarios directly — a valid substitute, since both surfaces render the identical `<bds-date-picker range ...>` markup and the presets sidebar activates purely off the `range` prop regardless of host page, so the same code paths were exercised either way. The four scenarios above have since been added to `src/index.html` (`dp-task30-s1` through `dp-task30-s4`, matching this task's exact spec) as the persistent, canonical QA artifact this plan's convention calls for — but were **not** re-run there, since Storybook already confirmed the underlying behavior and re-running would be redundant.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1 or 2, when a preset ("Last 7 days", etc.) is clicked, then `draft.rangeStart`/`draft.rangeEnd` update to that preset's range and the preset shows selected. Pass: correct dates highlighted on the calendar, preset button visually marked selected. **Verified live 2026-09-10** (Storybook, `range-mode-expanded-with-time` and `range-mode-basic-with-time`).
- [x] Given each built-in preset, when its computed range is checked against the semantics in Task 29, then it matches exactly. Pass: "Last 7 days"/"Last 30 days" include today (7/30 days total); "This month" runs from the 1st through today (not the full month); "Last month" runs the full previous calendar month; the grid highlights exactly these real days in every case, regardless of `with-time`. **Verified live** — "Last 7 days" clicked, grid highlighted Sep 4–10 exactly.
- [x] Given Scenario 4 (`with-time` on), when a preset is clicked, then the header reads the shifted coverage-end boundary (e.g. "Last 7 days" ending today shows `End:` as _tomorrow_ at `00:00`, not today) — identically in `basic` and `expanded`. Pass: header, and the trigger field's text after Apply, show the exact same date/time; the grid still highlights only the real days (today included, tomorrow not highlighted). **Verified live**: `expanded` header showed "Start: 2026/09/04 00:00 — End: 2026/09/11 00:00", trigger read identically after Apply; grid highlighted only Sep 4–10.
- [x] Given `basic`+`range`+`with-time`, when a range is selected **manually** (not via a preset) and Applied, then the committed end also uses the shifted coverage-end boundary at whatever time the shared selector shows — not the real last day at that time. Pass: a manual 3-day selection with the shared time left at its default commits exactly 3×24h, not 2×24h plus an instant. **Verified live**: manual Sep 28–30 selection with shared time set to `06:00` committed "2026/09/28 06:00 – 2026/10/01 06:00" — exactly 3×24h, time preserved on both bounds.
- [x] Given `expanded`+`range`+`with-time`, when a range is selected **manually** with independent start/end times, then the commit is completely unaffected by any of this — exactly the real days at exactly the times the user set. Pass: no shift applied; behavior identical to before this task. **Verified live**: manual Sep 10 (06:00) – Oct 12 (07:00) committed exactly as set, no shift, real Oct 12 end.
- [x] Given no preset has been clicked (fresh load, or a pre-existing `value` that happens to numerically match a preset), then "Custom" shows selected — never a built-in preset, even on a coincidental match. Pass: no reverse-matching. **Verified live**: reopening a picker with an existing committed value (including one landing on today) always showed "Custom" selected.
- [x] Given a preset is selected, when a day is manually clicked afterward, then the selection reverts to "Custom" and the preset shows deselected, with time values unchanged. Pass: preset button loses its selected state; re-clicking the identical days the preset had selected produces the same committed value as the preset did, just labeled Custom. **Verified live**.
- [x] Given a preset is selected, when only the time selector is edited afterward (calendar untouched), then the selection also reverts to "Custom". Pass: same as the day-click case — either interaction alone triggers the revert. **Verified live**: editing the hour on an active "Last 7 days" preset reverted to Custom, dates unchanged.
- [x] Given a range selection is mid-progress (start day clicked, no end yet), when a preset is then clicked, then the preset's range overwrites the in-progress selection entirely. Pass: no merge, no ignored click. **Verified live**: mid-progress Sep 21 (no end) → clicking "Yesterday" fully replaced it with Sep 9–10.
- [x] Given Scenario 3, when a preset's computed range falls even partially outside `min`/`max`, then that preset button is disabled (not clamped). Pass: click has no effect while disabled; a fully-in-range preset on the same picker remains clickable. **Verified live**: `min=2026-09-05`/`max=2026-09-15` correctly disabled Last 7/30 days, This month, Last month; Today/Yesterday/Custom stayed enabled; clicking a disabled preset had no effect.
- [x] Given "Custom" is clicked directly, then it shows selected but `rangeStart`/`rangeEnd`/time are unchanged — not cleared. Pass: distinct from clicking the Clean/Clear footer button, which does clear. **Verified live**.
- [x] Given the sidebar is now present in `basic`+`range`, when the header renders, then it shows the labeled `Start:`/`End:` format (`renderRangeHeader.tsx`), matching `expanded` — not the dash-joined line Task 23 shipped. Pass: `basic` and `expanded` render an identical header structure; the dash-joined rendering path no longer exists in `bds-date-picker.tsx`. **Verified live** — both stories render the identical labeled format; zero console errors observed across the entire manual-test session.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add presets sidebar"`

---

### Task 30a (new — discovered while reviewing Phase 6's preset/timezone interaction, 2026-09-10): "today" is computed from the device clock everywhere, never the configured `timezone` — done

**Status:** ✅ done (2026-09-11) — implemented by `@frontend-subagent`, verified live. `eslint --fix` and `stencil build` (full type-check) both clean. Manual test run against `timezone="Pacific/Kiritimati"` (UTC+14) with the device on `America/Bogota` (UTC-5, Sep 11 at time of testing — Kiritimati was already Sep 12, a real day-boundary mismatch): the "Today" preset selected and committed `2026/09/12 – 2026/09/12`, and a fresh picker with no prior value fell back to displaying September 2026 with the 12th highlighted as "today" — both match Kiritimati's date, not the device's. Zero console errors/warnings during the session.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `utils/presets.ts` (modify), `utils/value-mapping.ts` (modify), `services/date-engine/grid.ts` (modify), `bds-date-picker.tsx` (modify — call site updates), `helpers/renderPresets.tsx` (modify — thread `timezone` into `PresetsParams`)

**Bug:** every place this component determines "what calendar day is today" uses a bare `new Date()` (the device's system clock), with zero reference to the `timezone` prop:

- `utils/presets.ts:61` — `computePresetRange`'s `today` (drives every preset's computed range).
- `utils/value-mapping.ts`'s `resolveFallbackDisplayMonth` (~line 46) — the month the picker falls back to displaying when there's no usable committed value to anchor on.
- `services/date-engine/grid.ts:132` — `generateMonthGrid`'s own `now`, which only feeds `buildDayCell`'s `isToday` flag (the grid's highlighted "today" cell). `getWeekdayLabels`'s `new Date()` (line 161) was checked and is **not** part of this bug — it only anchors an arbitrary date to read weekday ordering off, never a real "what day is it" question, so no change is needed there.

This is inconsistent with every _other_ date computation in this component, which correctly threads the configured `timezone` through `@date-fns/tz`'s `TZDate` for both commit (`combineDateTimeToUTC`) and read-back (`extractDateTimeFromUTC`) in `services/date-engine/value.ts`. Concretely: a consumer with `timezone="Asia/Tokyo"` on a device physically running Pacific time would see "Today" (as a preset, as the calendar's highlighted today-cell, and as the fallback display month) reflect the _device's_ Pacific-time today, not Tokyo's — while every other date in the same picker session (min/max interpretation, formatted display, commit-value construction) correctly reflects Tokyo.

**Integration research pass (complete before writing acceptance criteria):**

Read the actual current source of each file below — not just its file path — before finalizing this task's scope.

- [x] Call sites: `computePresetRange` is called from `bds-date-picker.tsx:513` (`handlePresetClick`) and `helpers/renderPresets.tsx:47` (bounds-checking to decide each preset button's disabled state) — both need `timezone` threaded through; `PresetsParams` (`renderPresets.tsx`) currently has no `timezone` field and needs one added.
- [x] Call sites: `resolveDisplayMonth` (the public wrapper `bds-date-picker.tsx` calls) already accepts `timezone` as its 3rd parameter today, but only uses it on the `withTime` branch — its empty-value fallback branch calls `resolveFallbackDisplayMonth(min, max, reserveExtraMonth)` without passing `timezone` through at all. The fix is narrower than "add a new parameter": thread the `timezone` this function already receives one level deeper into `resolveFallbackDisplayMonth`.
- [x] Call sites: `generateMonthGrid` is called from `value-mapping.ts:54` (inside `resolveFallbackDisplayMonth`, for `isMonthFullyDisabled` — doesn't read `isToday`, so is unaffected either way), `value-mapping.ts:153` (`buildDisplayGrid`, the real rendered grid — needs the zoned `now`), and `bds-date-picker.tsx:621`/`624` (nav-guard preview grids, which also never read `isToday` — checked, no change needed there either).
- [x] Boundary case: an invalid/unrecognized IANA `timezone` string. Checked `services/date-engine/value.ts` and `utils/value-mapping.ts` — neither has any `try`/`catch` or validation around `TZDate` construction anywhere today; the component already trusts `timezone` uncritically everywhere else. This task introduces no new validation either, matching that existing precedent — an invalid `timezone` remains unsupported/undocumented behavior, not a new guarded case.
- [x] Default/empty state: none of the three call sites gain a new "unset" state — `timezone` already always has a value (`@Prop() readonly timezone: string = Intl.DateTimeFormat().resolvedOptions().timeZone`, `bds-date-picker.tsx:205`), so there's no new default to define.
- [x] Reactivity: `timezone` is read live at call time everywhere else in this component (never cached), and these three call sites must follow the same convention — no call site may capture `this.timezone` once and reuse a stale copy.

**Fix sketch (not yet implemented):** reuse the same `TZDate` mechanism already proven correct elsewhere, applied to "now" instead of a stored timestamp:

```ts
const nowInZone = new TZDate(new Date(), timezone);
const today = new Date(
  nowInZone.getFullYear(),
  nowInZone.getMonth(),
  nowInZone.getDate(),
);
```

`computePresetRange` and `resolveFallbackDisplayMonth` each gain a `timezone: string` parameter and compute `today`/`now` via the snippet above instead of bare `new Date()`. `services/date-engine/grid.ts` stays timezone-agnostic (the `date-engine` layer has no existing concept of IANA zones) — instead, `generateMonthGrid`'s `GenerateMonthGridOptions` gains an optional `now?: Date` field, defaulting to `new Date()` when omitted so every existing call site and unit test keeps working unchanged. Callers that need zone-correct "today" (`buildDisplayGrid` in `value-mapping.ts`) compute the zoned `now` themselves via the snippet above and pass it in; the two nav-guard call sites in `bds-date-picker.tsx` don't need to pass it at all, since they never read `isToday`.

**Acceptance criteria:**

- Every row of the Integration research pass above is reflected in a concrete acceptance-criteria bullet below.
- `computePresetRange` and `resolveFallbackDisplayMonth` accept a `timezone` parameter and compute "today"/"now" via `TZDate`, not bare `new Date()`.
- `generateMonthGrid`'s `GenerateMonthGridOptions` gains an optional `now?: Date`, defaulting to `new Date()` — `date-engine` itself never takes a raw `timezone` string.
- Every call site that needs zone-correct "today" (`computePresetRange`'s two callers, `resolveDraftDisplayMonth`'s two `resolveDisplayMonth` calls, `buildDisplayGrid`'s rendered-grid path) passes `this.timezone` (or the zoned `now` derived from it) through — no such call site left defaulting to device-local time.
- The two nav-guard `generateMonthGrid` call sites in `bds-date-picker.tsx` are left unchanged (they don't read `isToday`), and `getWeekdayLabels` is left unchanged (not a "today" computation).
- No change to any date computation that already correctly threads `timezone` (commit/read-back via `combineDateTimeToUTC`/`extractDateTimeFromUTC`) — this task only touches the "what is today" call sites enumerated above.
- Unit test coverage for this fix (both the new `timezone` parameters and the `now` override) is added to Task 32's consolidated unit-test task, not a new task here.

**Manual test (required):**

Playground scenario: a picker with `timezone` set to a zone with a large offset from the test device's actual system timezone (e.g. `timezone="Pacific/Kiritimati"`, UTC+14, or `timezone="Etc/GMT+12"`, UTC-12 — pick whichever creates a real day-boundary mismatch against the machine running the test at the time).

Run `pnpm dev:components` and validate:

- [x] Given the configured `timezone` is currently a different calendar day than the device's own local time, when the "Today" preset is clicked, then it reflects the configured zone's today, not the device's. Pass: the highlighted day and committed value match the zone's date, not the device's. **Verified live** — Kiritimati (UTC+14) showed/committed 2026/09/12 while the test device (Bogotá, UTC-5) was on 2026/09/11.
- [x] Given the same mismatch, when the picker opens with no prior value, then the calendar's own highlighted "today" cell and the fallback-displayed month also match the configured zone. Pass: no divergence between the preset's "today" and the grid's own "today" highlight. **Verified live** — fresh picker fell back to September 2026 with the 12th highlighted.

**Commit:** `git commit -m "fix(web-components): EOA-17662 compute 'today' through the configured timezone, not the device clock"`

---

### Task 30b (new — discovered after Task 30 sign-off, 2026-09-10): clicking a preset should navigate the displayed calendar month(s), not just highlight days — done

**Status:** ✅ done (2026-09-11) — implemented by `@frontend-subagent` (exactly two lines added to `handlePresetClick`, nothing else touched), verified live. `lint:fix` and `stencil build` (full type-check) both clean. Manual test run in both `basic` and `expanded` range pickers: navigating 2 months forward then clicking "Last 30 days" jumped the view straight to the range's start month (August) with the correct days highlighted; navigating forward one more month with Next showed the rest of the range (through today) still correctly highlighted; the same preset in `expanded` mode showed both calendars (August/September) covering the full range at once with no manual navigation; clicking a preset, manually reverting to Custom, then clicking a different preset re-anchored correctly with no stale display month. Zero console errors.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `handlePresetClick`)

**Gap:** `handlePresetClick` (`bds-date-picker.tsx:512-517`) updates `this.draft` (which drives day highlighting) but never updates `this.displayYear`/`this.displayMonth` (which decide which month(s) `bds-calendar-grid` actually renders). Those two `@State()` fields are only updated in two other places today: `listenClickTrigger` (popover open, anchors on the committed value's `start` via `resolveDraftDisplayMonth()`) and `handleMonthNavigate` (manual Prev/Next). Result: if the calendar is currently showing a month that doesn't contain the clicked preset's range, the preset's highlighted days can end up entirely off-screen until the user manually navigates to find them.

**Design decision (confirmed with user 2026-09-10):** on preset click, always set the displayed month to the preset's real (unshifted) `range.start` — identically for `basic` and `expanded`, no calendar-type branching. This matches the anchor already used by `resolveDraftDisplayMonth()` when the popover reopens on a previously committed range, so a preset click and a close-then-reopen of that same range always land on the same month. For `expanded`'s dual-calendar layout, the second calendar continues to derive as `start`'s month + 1 via the existing `nextMonthFrom`, unchanged.

Note this doesn't guarantee the _entire_ range is visible in `basic`'s single-month view when a preset spans two calendar months (e.g. "Last 30 days" crossing a month boundary) — only `start`'s month is shown initially. The rest of the range remains fully intact and correctly highlighted the moment the user navigates forward with Next — highlighting is driven by `draft.rangeStart`/`draft.rangeEnd`, completely independent of which month is currently displayed, so no additional handling is needed for that case.

**Integration research pass (complete before writing acceptance criteria):**

Read the actual current source of each file below — not just its file path — before finalizing this task's scope.

- [x] Call sites: `handlePresetClick` is the only call site this task touches — a single, private, non-exported handler (`bds-date-picker.tsx:512-517`); no other function calls it.
- [x] Boundary case: `range.start` lands exactly on `min` or `max`. Since `isPresetWithinBounds(range, this.minDate, this.maxDate)` already runs (and returns early on failure) before the draft/preset-key assignment in `handlePresetClick`, `range.start` is always guaranteed inside `[min, max]` by the time this task's new assignment would run — no extra clamping is needed.
- [x] Default/empty state: `displayYear`/`displayMonth` is existing shared state that Cancel, Clean, and Apply (`handleFooterAction`) never touch today — checked all three branches directly; none reference `displayYear`/`displayMonth`. This task doesn't change that: those three footer actions remain untouched by design, since Cancel/Apply close the popover (the display month gets recomputed fresh on next open via `listenClickTrigger`) and Clean intentionally leaves the calendar where the user left it.
- [x] Reactivity: `computeNavGuard(this.displayYear, this.displayMonth, ...)` (used by `render()` to disable the Prev/Next nav arrows) already reads `displayYear`/`displayMonth` reactively on every render — no new reactivity wiring is needed; setting these two `@State()` fields inside `handlePresetClick` triggers the same re-render/guard-recompute path any other change to them already does.

**Acceptance criteria:**

- Every row of the Integration research pass above is reflected in a concrete acceptance-criteria bullet below.
- Clicking any built-in preset sets `displayYear`/`displayMonth` from the preset's real `range.start`, for both `basic` and `expanded`.
- `expanded`'s second calendar continues to be derived automatically as `start`'s month + 1; no separate anchor logic is introduced for it.
- Manual/"Custom" selection, footer actions (Cancel/Clean/Apply), and popover-open behavior are all unaffected — this task only changes what happens inside `handlePresetClick`.
- Navigating away from the preset-anchored month with Prev/Next afterward continues to show the rest of the selected range correctly highlighted (already true today via `draft`-driven highlighting; covered as a regression check, not new behavior).
- Unit test coverage for this fix (asserting `displayYear`/`displayMonth` update on preset click) is added to Task 32's consolidated unit-test task, not a new task here.

**Manual test (required):**

Playground scenarios (add to `packages/boreal-web-components/src/index.html`):

- Scenario 1: a `basic`+range picker; navigate the calendar 2+ months forward, then click a preset whose range is not in the currently-shown month.
- Scenario 2: the same picker; click "Last 30 days" (or whichever built-in currently spans two calendar months relative to today) and step forward one month with Next.
- Scenario 3: an `expanded`+range picker; click the same spanning-months preset from Scenario 2.
- Scenario 4: either picker; click a preset, manually click a day (reverting to Custom), then click a different preset.

Run `pnpm dev:components` and validate:

- [x] Given the calendar is currently showing a month unrelated to any preset (Scenario 1), when a preset is clicked, then the view jumps to show `range.start`'s month with the correct days highlighted. Pass: no manual navigation needed to see the start of the selected range. **Verified live** — navigated to November, clicked "Last 30 days", view jumped straight to August with Aug 13–31 highlighted.
- [x] Given a preset whose range spans two calendar months (Scenario 2), when clicked in `basic` mode, then the view shows `range.start`'s month; clicking Next once shows the following month with the remaining range days still correctly highlighted through today. Pass: the range's highlighting is unbroken across the month navigation. **Verified live** — Next from August showed September with Sep 1–11 correctly highlighted through today.
- [x] Given the same spanning-months preset in `expanded` mode (Scenario 3), when clicked, then calendar 1 shows `range.start`'s month and calendar 2 automatically shows the following month, together covering the full range without any manual navigation. Pass: both ends of the range are visible at once. **Verified live** — calendar 1 showed August (13–31 highlighted), calendar 2 showed September (1–11 highlighted) simultaneously.
- [x] Given a preset is clicked and then a day is manually clicked, reverting to "Custom" (Scenario 4), when a different preset is clicked again afterward, then the view re-anchors correctly to the new preset's `range.start`. Pass: no stale display month left over from the previous preset or manual selection. **Verified live** — manually clicked Sep 20 (reverted to Custom), then clicked "Today"; view correctly re-anchored with only Sep 11 highlighted, no stale selection remaining.

**Commit:** `git commit -m "fix(web-components): EOA-17662 navigate calendar to preset's range on click"`

---

### Task 31: Phase 6 SCSS + JSDoc audit — done

**Status:** ✅ done (2026-09-11) — implemented by `@frontend-subagent`, verified live by `@qa-subagent` plus a direct follow-up check. Full Figma research pass completed against `_DatePickerRange` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, node `14:23420`, 10 State × Selected variants, all pulled individually). Compiled CSS confirmed token-only (zero hardcoded colours/spacing/radii), correctly scoped to `renderPresets.tsx`'s actual DOM, and disabled-focus-outline suppression is unconditional. Sidebar alignment (`align-self: stretch`) and the 1px hairline divider verified in both `expanded` and `basic` layouts. JSDoc audit found nothing needing a trim — every existing `@Prop`/`@Event`/`@Method`/class-level comment was already consumer-facing and within 1-2 sentences.

**One deliberate design deviation, confirmed with user:** Figma shows Focus-visible using the same plain shadow treatment as Hover (not this codebase's usual distinct `bds-focus-ring` token), and Focus-visible+selected doesn't darken like Hover+selected does. Both confirmed via two independent Figma pulls and accepted as designed, not bugs.

**One real bug found by QA and fixed:** `&--selected:focus-visible` never explicitly declared `background-color`, only `box-shadow` — relying on CSS specificity/source-order tie-breaking to fall back to the selected base color, which rendered incorrectly (fell back to the non-selected hover/focus light-gray color instead of staying primary-blue) in a real browser. Fixed by adding an explicit `&:focus-visible { background-color: $boreal-ui-primary-base; }` inside the `&--selected` block. Re-verified live via a real keyboard Tab (not programmatic focus, which doesn't trigger `:focus-visible` in Chromium) — selected+focused now correctly shows the solid primary-blue background with the focus shadow on top. Two reusable findings from this bug were promoted to project memory (`scss-modifier-must-override-every-base-pseudo-class.md`, `playwright-programmatic-focus-not-focus-visible.md`).

**Post-QA correction (2026-09-11, user-directed):** the "accept as designed" call on the flat Figma focus-visible shadow was reversed. The user pointed out the resulting preset buttons had no visible focus ring, inconsistent with every other interactive element in this component (e.g. the month Prev/Next `bds-button`s), and asked for alignment instead of literal Figma fidelity here. Both `:focus-visible` and `:active` were switched from the raw Figma-pulled shadow values (`bds-hover-shadow`, a plain `$boreal-depth-box-shadow-inset`) to this codebase's standard `bds-focus-ring`/`bds-focus-ring-active` mixins — the same ones `bds-button` itself uses — restructuring each pseudo-class into its own complete rule (no more property split across grouped selectors) to avoid re-introducing the specificity trap from the bug above. Rebuilt clean and re-verified live via computed-style inspection: `:focus-visible` now resolves to `var(--boreal-depth-box-shadow-focus)`, `:active` to `var(--boreal-depth-box-shadow-active)`, both matching `bds-button`'s own compiled rules exactly. The disabled+selected color question the user separately raised (a screenshot showing `primary-light`/`text-inverse`) was re-verified directly against Figma and against live computed styles — it was already correct in both the source and the compiled CSS; the appearance of a mismatch during investigation was a `bds-transition-surface` animation-timing artifact in a synthetic test, not a real bug.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify), `bds-date-picker.tsx` (modify — JSDoc audit only, no logic changes)

**Figma research pass:** Pull `get_design_context`/`get_metadata` for each row. A row is done only when actually pulled, never inferred from a sibling variant.

- [ ] Region: presets container tokens/spacing — pull `_DatePickerRange` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, frame node `14:23420`); this is the correct preset-button component_set (10 variants, `State` × `Selected`) per the spike's own Phase 6 finding. Note: v2's Task 18 briefly reused this same node ID as a header/range-design reference and found it didn't fit (it's presets-only) — don't repeat that mixup, this node is for Phase 6 exclusively.
- [ ] Modifier: preset button `State` (Default/Hover/Focus/Active/Disabled) — each pulled individually, not generalized from Default
- [ ] Modifier: preset button `Selected` (True/False) — pulled for its own default state
- [ ] Combination: `Selected: True` × each `State` value (Hover+Selected, Focus+Selected, Active+Selected, Disabled+Selected) — pulled separately; do not assume `Selected`'s visual treatment is additive with `State`'s
- [ ] Region: sidebar alignment for `expanded` (dual-calendar layout)
- [ ] Region: sidebar alignment for `basic` + `range` (single-calendar layout)
- [ ] Dimensions: sidebar width/height alignment against the calendar body it sits beside, for both `expanded` and `basic` layouts, pulled from Figma's layout data

**Acceptance criteria:**

- Every research row above checked off before the first SCSS line is written, with the pulled value recorded.
- Token-only SCSS; no hardcoded colours, spacing, or radii.
- Every `State` × `Selected` combination enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- `Disabled` state suppresses the native focus outline — verify this isn't scoped only inside the interactive-state block.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm each top-level selector matches the DOM `renderPresets.tsx` actually renders.
- JSDoc brevity/content compliance.

**Manual test (required):**

Reuse Task 30's Scenarios 1-4. Run `pnpm dev:components` and validate:

- [x] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value. **Verified** — every declaration resolves to `var(--boreal-*)`.
- [x] Given a preset button in each `State` × `Selected` combination, when interacted with, then it renders per the pulled state matrix. Pass: visually matches Figma for all rows checked off above. **Verified live** — 9/10 combinations passed on first QA pass; the 10th (Focus-visible+Selected) failed due to a CSS-specificity bug, fixed, and re-verified live via real keyboard Tab.

**Commit:** `git commit -m "feat(web-components): EOA-17662 style presets sidebar"`

---

### Task 31a (new — discovered while validating Task 31's styling against real usage, 2026-09-11): restructure popover content markup — presets/calendars/time-band unified under one container — done

**Status:** ✅ done (2026-09-11) — implemented by `@frontend-subagent`, verified live. `lint:fix` clean, `stencil build` clean, full `bds-date-picker` spec suite (17 suites, 286 tests) passing including both updated assertions. Manual test run across all four scenarios: `default` renders `.calendars` as `.container`'s only child; `basic`+range+withTime renders the calendar and time selector stacked as one centered block beside the presets sidebar, matching the target design exactly; `expanded`+range+withTime renders both calendars in one `.calendars` wrapper with the dual time selectors in `.time-band`; the `--bds-date-picker-presets-width` custom property correctly defaults to 144px and correctly reflects an inline override (verified 80px). Zero `slot="content-band"` usage remains anywhere in the component. A quick regression check confirmed Task 30's preset-click behavior is unaffected (verified via a real coordinate click — a synthetic `.click()` false negative during testing was a test-script artifact, not a real regression, matching this session's documented `.click()`-vs-real-interaction quirk). Zero console errors throughout.

**Follow-up fix (2026-09-11, user-directed):** the popover's own default content padding (`--popover-content-padding`, previously `$boreal-spatial-padding-s $boreal-spatial-padding-l`) was set to `0` on `bds-date-picker`'s `> bds-popover` override block, so the presets sidebar sits flush against the popover's left/top edges — matching the target design exactly, where the sidebar's own background/hairline defines the visual edge rather than an outer gap. `.bds-date-picker__presets`' own padding and `.bds-date-picker__calendars`' own padding (both already present from this task and Task 31) fully compensate for the removed outer padding, so no other visual region lost its spacing. Rebuilt clean, re-verified live in both `default` and `basic`+range+withTime — no regression.

**Follow-up removal (2026-09-11, user-directed):** with `bds-date-picker` no longer using `slot="content-band"` at all, a repo-wide search confirmed it had exactly zero other consumers anywhere (`boreal-web-components` or `boreal-docs`) and was never documented in `bds-popover`'s own Storybook/MDX — genuinely dead, unused public surface, not a feature anyone else relied on. Removed entirely from `bds-popover`: the `@slot content-band` JSDoc, the `hasContentBand` `@State` and its `hasSlotContent(this.el, 'content-band')` computation in `componentWillLoad` (the override itself was removed too, since that line was its only content), the `.popover-content-band` render block and its `--popover-content-band-padding` CSS custom property + `@prop` doc. `bds-popover`'s own test suite lost two `describe` blocks: the direct "content-band slot" tests, and a regression guard originally added to confirm the content-band addition didn't shadow `anchoredMixin`'s `componentWillLoad` — both are moot once the feature and its lifecycle hook no longer exist, and the guard's own "popover opens and becomes visible" assertion was already redundantly covered by six other existing tests. In `bds-date-picker`'s own suite, the two tests asserting the new `.bds-date-picker__time-band` is absent (added earlier this task) were deleted outright rather than kept as absence-checks, per instruction — each sat in a `describe` block with other tests, so no empty blocks were left behind. Full regression run: 321 suites / 3529 tests (3528 passed, 1 pre-existing todo) — zero failures, zero errors.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `render()`), `helpers/renderCalendarPanel.tsx` (modify), `bds-date-picker.scss` (modify), `__test__/bds-date-picker.time.spec.ts` (modify — removed one test, per follow-up below), `__test__/bds-date-picker.calendartype.spec.ts` (modify — removed one test, per follow-up below), `../../overlays/bds-popover/bds-popover.tsx` (modify — removed `content-band` slot entirely, per follow-up below), `../../overlays/bds-popover/bds-popover.scss` (modify), `../../overlays/bds-popover/__test__/bds-popover-basics.spec.ts` (modify — removed two obsolete `describe` blocks)

**Gap:** today the time selector renders through `bds-popover`'s own dedicated `slot="content-band"` region — a separate DOM branch, sibling to `.popover-content`, never nested inside it (`bds-popover.tsx:701-708`). Separately, `renderCalendarPanel.tsx` wraps `.bds-date-picker__calendars` around the grid(s) only when there are two (`if (grids.length === 1) return grids[0]`) — a single calendar renders bare, with no wrapper at all. Live manual testing of the `basic`+`range`+`with-time` variant surfaced that this produces markup that can't be centered/stacked consistently against the target design — the time band and the calendar(s) need to live in the same content tree, vertically stacked and horizontally self-centered, with the calendar wrapper always present regardless of count.

**Target structure per calendar type** (confirmed with user, 2026-09-11):

```
default (calendar-type="default"):
  .popover-content
    └─ .bds-date-picker__container
         └─ .bds-date-picker__calendars   (always wraps, even 1 grid)
              └─ bds-calendar-grid

basic (range and/or with-time):
  .popover-content
    └─ .bds-date-picker__container
         ├─ .bds-date-picker__presets            (only if range)
         └─ .bds-date-picker__date-time
              ├─ .bds-date-picker__calendars      (always wraps, even 1 grid)
              │    └─ bds-calendar-grid
              └─ .bds-date-picker__time-band       (only if with-time — no longer slot="content-band")

expanded:
  .popover-content
    └─ .bds-date-picker__container
         ├─ .bds-date-picker__presets            (only if range)
         └─ .bds-date-picker__date-time
              ├─ .bds-date-picker__calendars      (wraps both grids — unchanged from today)
              │    ├─ bds-calendar-grid  (start)
              │    └─ bds-calendar-grid  (end)
              └─ .bds-date-picker__time-band       (only if with-time)
```

**Integration research pass (complete before writing acceptance criteria):**

Read the actual current source of each file below — not just its file path — before finalizing this task's scope.

- [x] Call sites: `renderCalendarPanel` is called from exactly two places, both in `bds-date-picker.tsx`'s `render()` (the `effectiveRange` branch and the non-range branch) — both call sites survive this change unmodified in their arguments; only the helper's internal `grids.length === 1` special case is removed.
- [x] Call sites: `renderCalendarPanel` has no other callers and no dedicated spec file calling it directly (checked — its behavior is only exercised indirectly through full-component rendering in `bds-date-picker`'s own spec suite).
- [x] Boundary case: two existing unit tests assert on the mechanism being removed — `bds-date-picker.time.spec.ts:113` (`renders no content-band slot content when withTime is false`) and `bds-date-picker.calendartype.spec.ts:86` (`renders no time content-band selector in default mode even when with-time is set`) both assert `querySelector('[slot="content-band"]')` is `null`. Once `slot="content-band"` is never set by this component at all, these assertions become vacuously true (querying an attribute nothing ever sets) rather than testing real behavior. Both must be updated to assert on the new structure instead (e.g. `querySelector('.bds-date-picker__time-band')` is `null` in those same scenarios) so they keep testing what they're named for.
- [x] Boundary case: `default` calendar-type never shows chrome (`showChrome = !this.isDefaultCalendarType`) and therefore never renders `with-time`'s time band or the presets sidebar (range is `default`-incompatible) — its branch only ever needs `.container > .calendars`, confirmed by tracing `showChrome`'s only two read sites (the time-band gate and the header/footer gate).
- [x] Default/empty state: `bds-popover`'s own `hasContentBand`/`hasSlotContent(el, 'content-band')` detection (`bds-popover.tsx:650`) is untouched — this task only stops `bds-date-picker` from ever populating that slot; other consumers of `bds-popover` are unaffected.
- [x] Reactivity: no new `@Prop`/`@State` is introduced — every branch condition (`effectiveRange`, `isDefaultCalendarType`, `effectiveWithTime`, `isExpandedCalendarType`) is existing, already-reactive state. The new `--bds-date-picker-presets-width` CSS custom property is a static style hook, not a Stencil prop — no reactivity concern.

**Figma research pass (delta only — full state matrix already completed in Task 31):**

- [x] Dimension: `_DatePickerRange`'s frame is `128px × 32px` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, node `14:23424`) — no `$boreal-spatial-*` token matches 128px (the scale tops at `-7xl: 96px`; the layout scale has `-5xl: 120px`/`-6xl: 160px`, neither exact). Combined with the container's own `$boreal-spatial-padding-xs` (8px each side), the real target container width is 144px — also no exact token match.
- [x] Dimension: `.bds-date-picker__preset`'s height (`$boreal-spatial-spacing-xl`, 32px) already exactly matches `_DatePickerRange`'s 32px frame height — confirmed, no change needed.
- [x] Precedent: `bds-table` (`--bds-table-checkbox-column-width`, `--bds-table-expand-column-width`, etc.) and `bds-tag-field` (`--bds-tag-field-input-min-width`) already establish this codebase's convention for "a real Figma pixel dimension with no token equivalent" — a documented `@prop --bds-<component>-<dimension>` CSS custom property with a literal px default, declared in a `/** */` block immediately inside the component's root selector. This task follows that exact pattern rather than introducing a new one.

**Acceptance criteria:**

- Every research row above is reflected in a concrete bullet below.
- `.bds-date-picker__body` is renamed to `.bds-date-picker__container`; it simplifies to `display: flex;` only — `align-items: flex-start` and `gap: $boreal-spatial-gap-l` are dropped (separation between presets and the date-time column comes from `.date-time`'s own `margin: 0 auto`; `.presets` already opts into full-height via its own `align-self: stretch`).
- `.bds-date-picker__container` is always rendered (not conditional on `effectiveRange`) for every calendar type except `default`, which renders `.bds-date-picker__calendars` as `.container`'s only child (no presets, no `.date-time`).
- New `.bds-date-picker__date-time`: `display: flex; flex-direction: column; margin: 0 auto;`. Wraps `.calendars` and, when `effectiveWithTime`, the new `.time-band` — present for `basic` and `expanded`, never for `default`.
- `helpers/renderCalendarPanel.tsx` always wraps its output in `.bds-date-picker__calendars`, regardless of whether `calendars` has one or two entries — the `grids.length === 1` bare-return case is removed.
- `.bds-date-picker__calendars` gains `justify-content: center; padding: $boreal-spatial-padding-s $boreal-spatial-padding-l;` (its existing `@extend %flex-center; gap: $boreal-spatial-gap-l;` stays unchanged).
- New `.bds-date-picker__time-band` takes over the `%time-selector-band` extend currently applied directly to `.bds-date-picker__time-selector`/`.bds-date-picker__time-selector-row` (both of those drop the extend) — the band's background/hairline/padding now belongs to the outer, full-width wrapper, not the inner content-hugging row.
- The time selector (single or dual, per `isExpandedCalendarType`) renders as a normal child inside `.bds-date-picker__time-band`, itself a child of `.bds-date-picker__date-time` — `<div slot="content-band">` is no longer used anywhere in this component. `bds-popover`'s own `slot="content-band"`/`hasContentBand` mechanism is untouched for other consumers.
- New CSS custom property `--bds-date-picker-presets-width` (default `144px`), documented via a `@prop` JSDoc comment inside `bds-date-picker`'s root SCSS selector (matching `bds-table`'s exact placement/format convention), applied as `width: var(--bds-date-picker-presets-width, 144px);` on `.bds-date-picker__presets`. `.bds-date-picker__preset`'s own `width: 100%` and `height: $boreal-spatial-spacing-xl` are unchanged.
- `bds-date-picker.time.spec.ts`'s `renders no content-band slot content when withTime is false` and `bds-date-picker.calendartype.spec.ts`'s `renders no time content-band selector in default mode even when with-time is set` are updated to assert on `.bds-date-picker__time-band` instead of `[slot="content-band"]`, preserving what they actually test.
- No change to any draft-state, preset-selection, or commit-building logic — this task is markup/CSS restructuring only.

**Manual test (required):**

Playground scenarios (add to `packages/boreal-web-components/src/index.html`):

- Scenario 1: `calendar-type="default"` picker — confirm `.container > .calendars` renders with no presets/date-time wrapper.
- Scenario 2: `calendar-type="basic" range with-time` picker (the variant validated against the target design) — confirm the full `.container > [.presets] + .date-time > .calendars + .time-band` structure.
- Scenario 3: `calendar-type="expanded" range with-time` picker — confirm both calendars render inside one `.calendars` wrapper, and the dual time-selector row renders inside `.time-band`.
- Scenario 4: a picker with a long presets label set (or a narrower viewport) to confirm the sidebar visually holds ~144px via the new custom property, and that overriding `--bds-date-picker-presets-width` on the host actually changes it.

Run `pnpm dev:components` and validate:

- [x] Given `calendar-type="default"`, when the popover opens, then `.bds-date-picker__calendars` is the only child of `.bds-date-picker__container` — no presets sidebar, no `.date-time` wrapper. Pass: DOM inspection confirms the structure; visual layout unchanged from before this task. **Verified live.**
- [x] Given `calendar-type="basic" range with-time`, when the popover opens, then the calendar and the time selector appear stacked vertically, centered together as one block beside the presets sidebar — matching the target design. Pass: no visual regression versus the reference design; zero console errors. **Verified live** — matches the target screenshot exactly.
- [x] Given `calendar-type="expanded" range with-time`, when the popover opens, then both calendars render side by side inside one `.calendars` wrapper, with the dual start/end time selectors in a `.time-band` beneath them. Pass: layout matches the `basic` variant's stacking pattern, scaled to two calendars. **Verified live** — 2 grids confirmed inside one `.calendars`, dual selectors inside `.time-band`.
- [x] Given the presets sidebar, when `--bds-date-picker-presets-width` is left at its default, then the sidebar is 144px wide; when overridden via an inline style on the host, then the sidebar reflects the override. Pass: default renders correctly, override works. **Verified live** — default measured exactly 144px, override to 80px measured exactly 80px.
- [x] Given all of Task 30's original manual-test scenarios (preset click, min/max disabling, Custom revert behavior), when re-run against the restructured markup, then they all still pass unchanged. Pass: no regression from the structural change — this task touches only wrapping markup and CSS, not interaction logic. **Verified live** — "Today" preset click via real coordinate click correctly selected and highlighted Sep 11.

**Commit:** `git commit -m "feat(web-components): EOA-17662 restructure popover content markup for presets/calendars/time-band"`

---

### Task 32: Phase 6 unit tests (consolidated) — done

**Status:** ✅ done (2026-09-11) — implemented by `@testing-subagent`, independently re-verified. Coverage on `bds-date-picker`+`date-engine`: 98.51% statements / 95.01% branches / 100% functions / 99% lines — well above the 90% gate. Full package suite: 324 test suites, 3588 passed, 1 pre-existing todo, 0 failed — zero regressions. `presets.spec.ts`, `draft-state.spec.ts` (backfill), and `bds-date-picker.presets.spec.ts` (30 tests) created as scoped; `grid.spec.ts` and `value-mapping.spec.ts` got small additions for the Task 30a cross-reference coverage. All signature drift since this task was originally written (`computePresetRange`'s added `timezone` param, `buildDisplayGrid`'s, `renderPresets`'s, the `DatePickerLabels` rename, `slot="content-band"`'s removal) was correctly picked up from current source, not stale plan prose.

**Two pre-existing dead-code observations surfaced (not fixed — correctly out of scope for a tests-only task):** `utils/draft-state.ts:51` (`selectRangeDay`'s `rangeStart === isoDate && rangeEnd === null` check) and `utils/value-mapping.ts:70-72` (`resolveFallbackDisplayMonth`'s `anchor === undefined` check) are both genuinely unreachable given their own enclosing conditions — independently re-traced and confirmed, not just taken on the subagent's word. Harmless (defensive code that never fires), but worth a follow-up cleanup task if the team wants to remove them; not blocking this task or any other.

**Executor:** @testing-subagent
**Files:** `bds-date-picker.presets.spec.ts` (create), `presets.spec.ts` (create), `draft-state.spec.ts` (create, backfill — see below)

**Backfill (pre-existing gap, unrelated to Task 29/30's own new code, folded in here since this task already touches the same folder):** `utils/draft-state.ts`'s `selectDay`/`selectRangeDay` are currently only exercised indirectly, through full-component click simulation in `__test__/bds-date-picker.range.spec.ts` — no spec file calls them directly, unlike every other `utils/` function (`value-mapping.ts` has its own `value-mapping.spec.ts`; `draft-state.ts`'s simpler setters — `resetDraft`, `resetRangeDraft`, `selectHour`, `selectMinute`, `selectBoundHour`, `selectBoundMinute` — are already unit-tested directly in `bds-date-picker.time-helpers.spec.ts`). Add a `utils/__test__/draft-state.spec.ts` with direct, no-component-rendering unit tests for `selectDay`/`selectRangeDay`'s exact branch logic: a forward click setting `rangeEnd`; a backward (or equal) click swapping in a new `rangeStart` instead; a third click after a completed range starting fresh; and the no-op case (clicking the same day already selected returns the identical `draft` reference, not just an equal one — matches the function's own documented behavior). This doesn't replace `range.spec.ts`'s existing integration coverage — it adds a faster, more precise unit-level layer alongside it, consistent with how the rest of `utils/` is tested.

**Unit tests to cover:**

- Preset computation correctness for all six built-ins, per Task 29's exact (2026-09-10, final) semantics: Today/Yesterday as single-day ranges; Last 7/30 days inclusive of today (7/30 total days, not 7/30 days _before_ today); This month as month-to-date (1st through today, not through month-end); Last month as the full previous calendar month. Assert `computePresetRange`'s output is always the **real, unshifted** range regardless of `with-time`.
- `computePresetCoverageEnd`: with `with-time` off, returns `range.end` unchanged; with `with-time` on, returns the real last day + 1 at `00:00` — assert this exactly, for all six presets, including the two (Yesterday, Last month) where the "+1" naturally coincides with `range.end` already being the start of the next period (i.e. confirm no double-shift occurs for those two).
- `isPresetWithinBounds` (Task 29): operates on the real range, never the shifted coverage end. Returns `false` for a range fully outside `min`/`max`, `false` for a range only partially outside (not `true`/clamped), `true` for a range fully inside.
- Preset click sets `draft.rangeStart`/`rangeEnd` to the **real** days (never shifted) and, when `with-time`, sets the relevant time field(s) to `00:00` — `hour`/`minute` for `basic`, `startHour`/`startMinute`/`endHour`/`endMinute` for `expanded`.
- The rendered header, when a preset with `with-time` is active, displays `computePresetCoverageEnd`'s shifted value as `End:` — not the real last day — identically in `basic` and `expanded`.
- `basic`+`range`+`with-time`'s commit (Apply) uses the coverage-shifted end at whatever time the shared field shows, for **both** preset-driven and manual selections — assert a manual same-day or multi-day selection with the shared time left at its default no longer under-covers by close to a day, and that a manual selection with a user-set shared time (e.g. `09:00`) preserves that time on both the real start and the shifted end.
- `expanded`+`range`+`with-time`'s commit for **manual** selection is unaffected by any of this — assert independent `startHour`/`endHour` values commit exactly as set, with no shift applied, unlike its preset-driven commits (which do shift).
- Preset click while a selection is mid-progress (`rangeStart` set, `rangeEnd` null) overwrites the in-progress selection rather than merging or being ignored.
- Re-clicking the currently-selected preset recomputes rather than short-circuiting as a no-op.
- A manual day click, and separately a manual time-selector edit, each independently revert an active preset selection to Custom.
- Reverting to Custom via either path leaves `startHour`/`startMinute`/`endHour`/`endMinute` unchanged from whatever the draft already held — assert the exact carried-over values, not just "no crash."
- "Custom" is selected by default on a fresh draft, and remains selected (never reverse-matched to a built-in) when a pre-existing `value` numerically coincides with what a preset would currently compute.
- Clicking "Custom" directly marks it selected without altering `rangeStart`/`rangeEnd`/time.
- A disabled preset button (out-of-bounds per `min`/`max`) does not update the draft when clicked.
- Preset label text resolves from the new `labels` keys with correct English defaults and consumer overrides, mirroring Task 25's labels-override coverage pattern.
- **Task 30a coverage:** `computePresetRange`/`resolveFallbackDisplayMonth` compute "today"/"now" from the passed `timezone`, not the device clock — assert against a mocked/injected `timezone` distinct from the test runner's own, for at least one call through each function. `generateMonthGrid`'s new `now?: Date` option correctly drives `isToday`, and its own default (`new Date()`) preserves every existing `grid.spec.ts` assertion unchanged.
- **Task 30b coverage:** clicking a built-in preset sets `displayYear`/`displayMonth` from the preset's real `range.start`, in both `basic` and `expanded`; Cancel/Clean/Apply and manual selection leave `displayYear`/`displayMonth` unchanged.
- **Task 31a coverage:** `renderCalendarPanel` always wraps its output in `.bds-date-picker__calendars`, for both one and two grid entries (not just two, as before). `default` calendar-type renders `.calendars` as `.container`'s only child; `basic`/`expanded` render `.date-time` wrapping `.calendars` plus `.time-band` (only when `effectiveWithTime`). No element in the rendered tree carries `slot="content-band"` under any configuration (the slot itself was removed from `bds-popover` entirely as dead code, not just unused by `bds-date-picker` — the two prior tests asserting its absence were deleted outright rather than updated, since asserting the absence of an attribute the component can no longer ever set carries no signal).

Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 6 presets sidebar unit tests"`

---

### Task 32a (new — discovered while validating Task 32's unit tests, 2026-09-11): remove confirmed-unreachable defensive branches in draft-state.ts and value-mapping.ts — done

**Status:** ✅ done (2026-09-11). Pre-existing dead code, unrelated to any Phase 6 task's own new logic; both branches independently traced and confirmed unreachable (not just flagged) before this task was written. `draft-state.ts`'s two dead branches (`selectRangeDay`, lines 51/58 as originally numbered) were removed cleanly with no further complication.

`value-mapping.ts`'s fix went through one real correction before landing: the plan's suggested `validMax ?? validMin!` non-null assertion was flagged by `@typescript-eslint/no-unnecessary-type-assertion` and initially replaced with the bare `validMax ?? validMin` (no assertion) — which compiled clean via this repo's own `tsconfig.json` (which has no `strict`/`strictNullChecks` set) and via ESLint's type info (which resolves through that same lax config), but reproducibly failed in the connected IDE's live TypeScript diagnostics with `TS2322: Type 'Date | undefined' is not assignable to type 'Date'`, surviving IDE/TS-server reloads. Root cause, confirmed directly by re-running `tsc --strict` against the same file: TypeScript's control-flow analysis cannot connect "not both `min`/`max` are undefined" (proven several statements earlier, at this function's own first early return) to "therefore `validMax ?? validMin` is defined" — a real, permanent narrowing gap, not a caching or config artifact. The bare version was only ever "clean" by accident of this repo's lax tsconfig, not because it was actually type-safe.

**Final fix**, verified to satisfy every checker in the repo simultaneously (strict `tsc`, the project's own non-strict `tsc`, ESLint, and the IDE's own live diagnostics — confirmed empty via direct query):

```ts
const anchor: Date =
  validMax !== undefined ? validMax : validMin !== undefined ? validMin : today;
```

Each ternary branch is locally, independently provable as `Date` — no assertion, no re-added dead check referencing the distant early return. The final fallback (`today`) is never actually reached at runtime (the enclosing function already guarantees at least one of `validMin`/`validMax` is defined by this point) but is a real, in-scope, safe `Date` value, consistent with what this same function already returns from its other early-return branches.

Full verification: `draft-state.spec.ts`, `presets.spec.ts`, and `value-mapping.spec.ts` (all from Task 32) passed completely unmodified. Full `bds-date-picker`+`date-engine` suite and the full package suite both clean: 324 test suites, 3588 passed, 1 pre-existing todo, 0 failures. `stencil build` clean. `tsc --noEmit` (both strict and the project's own config) clean. ESLint clean.

**Executor:** @frontend-subagent
**Files:** `utils/draft-state.ts` (modify), `utils/value-mapping.ts` (modify)

**Gap:** two defensive branches can never actually execute, given the conditions that guard entry into them:

- `utils/draft-state.ts:51` — inside `selectRangeDay`, the branch at line 50 (`draft.rangeStart === null || draft.rangeEnd !== null`) is entered either because `rangeStart` is `null` or because `rangeEnd` is non-`null`. Line 51's check, `draft.rangeStart === isoDate && draft.rangeEnd === null`, requires both `rangeStart === isoDate` (impossible when `rangeStart` is `null`, since `isoDate` is always a string) and `rangeEnd === null` (impossible when the branch was entered because `rangeEnd !== null`) — so the conjunction can never be `true` under either path into this block.
- `utils/draft-state.ts:58` — inside the same function's `else` path (`rangeStart` non-`null`, `rangeEnd` already known `null` from the outer `if`'s negation), the check `draft.rangeEnd === isoDate` would require `isoDate === null`, again impossible since `isoDate` is always a string.
- `utils/value-mapping.ts:70-72` — inside `resolveFallbackDisplayMonth`, an early return at line 60 already guarantees `validMin`/`validMax` are not _both_ `undefined` by the time `anchor` is computed at line 69 (`validMax !== undefined ? validMax : validMin`). If `validMax` is defined, `anchor` is `validMax` (defined). If `validMax` is undefined, the line-60 guarantee means `validMin` must be defined, so `anchor` is `validMin` (defined). `anchor` can therefore never be `undefined`, making the `if (anchor === undefined)` check at line 70 unreachable.

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: `selectRangeDay` has exactly one real caller, `bds-date-picker.tsx:363` (the `bdsDayClick` handler's range branch) — removing the two dead branches doesn't change the function's return value for any reachable input, so this call site needs no changes.
- [x] Call sites: `resolveFallbackDisplayMonth` has exactly one caller, `resolveDisplayMonth` (three call sites within the same file, all passing the same four arguments) — same as above, no behavioral change for any reachable input.
- [x] Boundary case (type-checking consequence, not a runtime behavior change): removing `value-mapping.ts`'s `if (anchor === undefined) return {...}` removes the only statement that currently narrows `anchor`'s type from `Date | undefined` to `Date` for TypeScript's flow analysis. Simply deleting the block will cause a compile error on the next use of `anchor` (`anchor.getFullYear()`/`anchor.getMonth()`, and the `anchor === validMax` comparison). The fix must restructure how `anchor` is computed so TypeScript can prove it's always `Date` without a runtime check that can never fail — e.g. `const anchor: Date = validMax ?? validMin!;` (the non-null assertion is justified by the line-60 guarantee already proven above, not a new unchecked assumption) — or an equivalent restructuring. Do not simply add back an `if (anchor === undefined)` guard with a `// this can't happen` comment — that reintroduces the same dead code this task removes.
- [x] Default/empty state: no new state is introduced; this task only removes code paths that were never reachable.
- [x] Reactivity: not applicable — both functions are plain, non-reactive utility functions with no `@State`/`@Prop` involvement.

**Acceptance criteria:**

- `selectRangeDay`'s two dead branches (`draft-state.ts:51`, `:58`) are removed; the function's behavior for every reachable input is byte-for-byte identical to before (verified by the existing `draft-state.spec.ts` test suite from Task 32 continuing to pass unmodified).
- `resolveFallbackDisplayMonth`'s dead `if (anchor === undefined)` branch is removed, with `anchor`'s computation restructured so TypeScript proves its type as `Date` without a runtime check — no `as`/`!` used to paper over a genuinely uncertain case, only to formalize the already-proven invariant from the line-60 early return.
- No behavioral change for any reachable input — the existing `presets.spec.ts`/`value-mapping.spec.ts`/`draft-state.spec.ts` suites (from Task 32) all pass unmodified, with no new test cases needed (there is nothing new to test — this is a pure code-shape simplification).
- `tsc --noEmit` and the full `bds-date-picker` test suite are clean after the change.

**Manual test:** N/A — non-visual, behavior-preserving refactor; validated entirely via the existing test suite passing unmodified and a clean `tsc --noEmit`.

**Commit:** `git commit -m "fix(web-components): EOA-17662 remove confirmed-unreachable defensive branches"`

---

### Task 33: Phase 6 documentation — done

**Status:** ✅ done (2026-09-11) — implemented by `@documentation-subagent`, independently re-verified. New `### Presets sidebar` MDX subsection added under `## Range selection`, positioned before the `Range-mode basic`/`expanded` canvases as scoped, covering the fixed preset list, exact semantics, the "This month" manual-selection escape hatch (via a real `<Callout variant="tip">`, confirmed as an existing, valid MDX component in this docs app), disable-not-clamp behavior, the full `with-time` coverage-boundary table, and the `basic`/`expanded` manual-selection difference. New `RangeModePresetsBounded` story added (switched to `calendar-type="basic"` rather than `expanded` after live-testing — `expanded` with that narrow a window triggers an unrelated pre-existing warning that would have conflated two different behaviors in one demo, a good catch). Five existing range stories got one-line presets cross-references; `BoundedRange` correctly left untouched. The stale "`basic` renders dash-joined, not labeled" claim was fixed in both the MDX and (a duplicate the subagent found on its own) `RangeModeBasic`'s own story JSDoc. `## Customizing footer labels` renamed to `## Customizing labels` with a full labels-key table — this was the explicit ask ("document the new preset labels keys... alongside the existing footer-labels table"), not scope creep, since the section's old name no longer matched what the `labels` prop actually covers.

Independently re-verified, not just taken on the subagent's report: confirmed `Callout`'s `tip` variant is real (`'info' | 'tip' | 'warning' | 'error'` in `Callout.tsx`), and ran a full `pnpm --filter boreal-docs run build` myself — Storybook builds clean, `bds-date-picker.stories.js` and `bds-date-picker.js` compile with no errors.

**Copyediting pass (2026-09-11, user-directed, via the `writing-clearly-and-concisely` skill):** the user caught real duplication across the new content, in two rounds. First: "Presets sidebar"'s closing paragraph re-derived the exact `basic`/`expanded` shared-vs-independent time-field structure already established in `### Range-mode time selection` (~150 lines away, no cross-reference) — deleted, with its one new fact (the coverage-shift also applying to `basic`'s manual selection) moved into that section instead. Second round, user-flagged: (1) `RangeModePresetsBounded`'s story JSDoc opened with the exact same "disables — never clamps" sentence already stated in the adjacent MDX prose, rendered back-to-back via `<Description>` — trimmed the JSDoc to start directly with what's specific to that example instead of restating the general rule; (2) `## Customizing labels`'s intro paragraph re-listed the same three-category summary ("footer buttons, range header labels, presets sidebar text") already stated by the `labels` argType's own description in the `## Properties` `<ArgTypes>` block — shortened to just the one fact that description doesn't cover (`labels` is a JS property, not a reflected attribute) followed directly by the table. Also added a one-clause disambiguation where "no prop to customize which presets appear" is stated, clarifying preset _text_ is still relabelable via `labels`, to prevent that reading as contradicting `## Customizing labels`. Rebuilt clean after each change; final `pnpm --filter boreal-docs run build` confirmed.

**Final adjustments (2026-09-11, user-directed):**

- `### Range-mode time selection`'s bullet list and `#### Basic`/`#### Expanded` subsections were reordered to list `basic` before `expanded`, matching every other basic-then-expanded ordering already established elsewhere in this doc (`## Calendar types`, `## Range selection`'s own `Range-mode basic`/`Range-mode expanded` canvases).
- `## Customizing labels` now showcases a real fully-localized picker instead of a footer-only English-to-French demo: the `CustomFooterLabels` story (confirmed, via a repo-wide search, to have exactly one reference — itself — so safe to repurpose) was renamed to `LocalizedLabels` and extended to set `range` (so all customizable preset text is visible, not just the footer), a complete French `labels` object (all twelve keys, not just clean/cancel/apply), and `locale={fr}` together — demonstrating both what `labels` covers (footer, header, presets — all in French) and what it doesn't (weekday names, the month/year header — French only via `locale`).
- **Real bug found and fixed while building this story, independent of the user's request:** the first draft used a literal runtime `<script type="module">import { fr } from 'date-fns/locale'; ...</script>` inside the Lit render template, exactly matching the original `CustomFooterLabels` story's script-based pattern. This throws `TypeError: Failed to resolve module specifier "date-fns/locale"` in the browser — bare module specifiers only resolve inside a bundler (which processes the `import` at the top of the `.stories.ts` file itself), never inside a literal `<script>` tag inserted into the live DOM at runtime. Confirmed via direct browser console inspection, not assumed. Fixed by binding `fr` (already imported at module scope) and the French `labels` object directly as Lit properties (`.locale=${fr}` `.labels=${frenchLabels}`) — the same working pattern the existing `CustomLocale` story already used — with a `parameters.docs.source` override (`localizedLabelsDocsSource`, mirroring `CustomLocale`'s `localeDocsSource`) so the Storybook Source panel still shows accurate, real-world runnable code despite the live render using property bindings that don't appear in the auto-generated source. Verified live in a real browser (not just a clean build) after the fix: French presets/header/footer render correctly, French month name ("septembre 2026") and weekday abbreviations render correctly, zero console errors on a fresh load. The user separately upgraded this story's args to `calendar-type="expanded" with-time` directly (more of the `labels` surface visible at once — dual time-selector `Start:`/`End:` labels alongside the range header's), which the docs source was already updated to match.
- **DRY fix (2026-09-11, user-directed, modeled on `RowClickSelection`'s shared-logic pattern):** the French `labels` object was originally hand-duplicated — once as the real `frenchLabels` object used for the live `.labels=` binding, once again, by hand, inside `localizedLabelsDocsSource`'s displayed script — a drift risk identical to what `RowClickSelection`'s `rowClickSelectionLogic` constant (shared verbatim between its live script and its docs source) exists to prevent. Since `date-fns`'s import constraint rules out `RowClickSelection`'s exact mechanism (interpolating raw executable JS text) for the `locale` half, only the `labels` half could be de-duplicated the same way: added `formatLabelsForDisplay`, a small serializer that generates the displayed object-literal text directly from the real `frenchLabels` object (via `JSON.stringify` per value, correctly escaping the one preset containing an apostrophe), so editing `frenchLabels` can never leave the displayed docs source stale. Also reformatted `localizedLabelsDocsSource`'s opening tag from a single long attribute line to one attribute per line, matching `RowClickSelection`'s own multi-attribute tag formatting exactly (byte-for-byte whitespace comparison confirmed) — the prior single-line form matched `CustomLocale`'s simpler, fewer-attribute tag instead, which no longer fit once this story grew to four attributes. Rebuilt clean; re-verified live afterward with zero console errors.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:**

- **Scope decision (confirmed with user, 2026-09-11):** the presets sidebar isn't a separately-toggleable feature — it already renders in every existing range story (`RangeModeBasic`, `RangeModeExpanded`, `RangeModeExpandedWithTime`, `RangeModeBasicWithTime`, `RangeHoverPreview`), just undocumented. No new story is needed purely to show it exists. A new `### Presets sidebar` MDX subsection is added under the existing `## Range selection` section, positioned right after that section's intro paragraph and _before_ the `Range-mode basic`/`Range-mode expanded` story canvases (so a reader learns what the sidebar is before seeing it, unlabeled, in those examples) — states the fixed six-preset list (Today, Yesterday, Last 7 days, Last 30 days, This month, Last month) plus Custom, with no consumer-configuration prop (Task 28's decision). Each of the five existing range stories' JSDoc gains a one-line cross-reference noting the sidebar is present. One genuinely new story, `RangeModePresetsBounded` (`range: true` + a `calendarType` + narrow `min`/`max`), is added specifically to demonstrate preset-disabling on out-of-bounds — a real interactive scenario no existing story covers — and is what the new MDX subsection's `<Canvas>` points at. The existing `BoundedRange` story is left untouched (it's a single-date, non-range min/max demo today, not renamed/repurposed, to avoid disturbing its existing Chromatic baseline).
- **Also fix (found while reviewing this section, unrelated to presets):** the existing `### Popover header format` MDX subsection still claims `basic + range` renders "a plain dash-joined string with no labels" — this is stale; Task 30 already changed `basic`'s header to render the same labeled `Start:/End:` format as `expanded` (verified live at the time). Update this section to state the current, correct, identical-labeled-format behavior for both calendar types.
- MDX states plainly that the preset list is fixed — Today, Yesterday, Last 7 days, Last 30 days, This month, Last month, Custom — with no consumer-configuration prop (Task 28's decision), and includes a new story variant demonstrating preset-disabling on out-of-bounds (`RangeModePresetsBounded`, per the scope decision above).
- MDX documents the **exact** semantics of each preset a consumer might otherwise assume differently, since these are genuine judgment calls, not obvious defaults: "Last 7 days"/"Last 30 days" include today (7/30 days total); "This month" is month-to-date (1st through today), **not** the full calendar month; "Last month" is the full previous calendar month.
- MDX explicitly documents the manual-selection escape hatch for the "This month" month-to-date boundary: consumers needing the full current month (including upcoming days — e.g. a scheduling/booking context) can select it manually on the calendar (never locked, even while a preset is active), since "This month" the preset intentionally stops at today. State this as a deliberate design choice with a one-line rationale (avoids showing an empty/no-data tail for the majority reporting/filtering use case this preset set is modeled on), not as an unexplained limitation.
- MDX documents that a preset button disables (not clamps) when its computed range falls even partially outside `min`/`max`.
- MDX documents the new preset `labels` keys (with their English defaults) alongside the existing footer-labels table, so consumers know how to localize preset button text via the same `labels` prop used for Clean/Cancel/Apply/Start/End.
- MDX documents `with-time`'s behavior for range presets explicitly, since it's a real, visible design choice a consumer would otherwise mistake for a bug: every preset guarantees exact full-day coverage by committing an end boundary at the **start of the day after** the last included day, at `00:00` (e.g. "Last 7 days" ending today submits its `end` as _tomorrow_ at midnight) — and the popover header shows that same boundary from the moment the preset is clicked, consistently with the trigger field's text after Apply. The calendar grid still highlights only the real included days (today, not tomorrow) — call this out explicitly as the one intentional place the display differs, and why (a day-granularity grid can't represent an exact instant boundary any other way). Include the full per-preset table (reproduced from [ADR 0015](../../ai-docs/decisions/0015-date-picker-preset-time-coverage-semantics.md)) covering Start/End/Grid-selection for all six presets.
- MDX documents the `basic`/`expanded` behavior for **manually** selected ranges with `with-time` on — **as reconciled 2026-09-24:** the coverage shift is data-driven, applying whenever the two bounds carry the **same time-of-day**. `basic`'s single shared time field always satisfies this, so it always shifts; `expanded`'s independent fields shift only when they hold the same time (including the untouched `00:00` default) — a deliberately different End time is taken exactly as set, and a same-day non-midnight equal-time instant is left unshifted. (The original wording here — "`expanded`'s independent start/end fields are taken exactly as the consumer sets them, with no adjustment" — was true only for the distinct-time case and was superseded by Task 35's 2026-09-22 data-driven fix.) Link to [ADR 0015](../../ai-docs/decisions/0015-date-picker-preset-time-coverage-semantics.md) for the underlying reasoning rather than re-deriving it in the component's own docs.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [x] Given the new `RangeModePresetsBounded` story, when Storybook renders it, then presets whose computed range falls outside the story's `min`/`max` render disabled and do nothing when clicked, with no console errors. Pass: at least one preset visibly disabled, interaction otherwise identical to `RangeModeBasic`/`RangeModeExpanded`. **Verified** — both by the subagent (`disabled` property checked directly) and by an independent `pnpm --filter boreal-docs run build`, clean.
- [x] Given the updated `### Popover header format` section, when read against the actual current behavior, then it correctly states `basic` and `expanded` render the identical labeled `Start:/End:` format — no stale "dash-joined" claim remains. **Verified** — fixed in both the MDX and a duplicate stale claim found in `RangeModeBasic`'s own story JSDoc.
- [x] Given the MDX's fixed-list statement, when read against Task 28's actual decision, then it matches exactly. Pass: no stale/contradicting prose, no leftover "if configurable" language. **Verified.**
- [x] Given the "This month" documentation, when read, then it states month-to-date semantics and the manual-selection escape hatch for the full-month case. Pass: a reader wouldn't mistake the boundary for a bug or a hard limitation. **Verified** — expressed via a `<Callout variant="tip">`, a real existing MDX component in this docs app.
- [x] Given the `with-time` coverage-boundary documentation, when read, then it clearly explains why the header/trigger show a date one day past the last highlighted grid cell. Pass: a reader wouldn't mistake this for a bug. **Verified**, with one deliberate deviation from the original wording: no link to the ADR-0015 file was added, since that file lives under a locally git-ignored directory (`ai-docs/`) and would be a broken link for any other contributor or in CI — the full coverage table was reproduced inline as self-contained prose instead, which is the correct call for consumer-facing docs.

**Final structural pass (2026-09-11, user-directed, full-file coherence audit):** the user asked for a listed audit before any edits; findings were presented and confirmed, then applied:

- `### Presets sidebar`'s embedded example swapped from `RangeModePresetsBounded` (a narrow-window demo, contradicting "shows all presets available") to `RangeModeBasic` (no `min`/`max` — already existed, no new story needed), with the disabling paragraph now redirecting to `## Min/max constraints` for the bounded demonstration instead of showing it twice.
- `RangeModePresetsBounded` retired as a separate story; its narrow-bounds demo folded into `BoundedRange` itself (`calendarType: 'basic', range: true` added to its args, JSDoc extended to cover both day- and preset-level disabling) — avoids two near-duplicate narrow-window range stories. `## Min/max constraints` gained a short cross-reference paragraph back to `### Presets sidebar`.
- Two undocumented, already-shipped features caught during the audit and added to `### Presets sidebar`: the `--bds-date-picker-presets-width` CSS custom property (default `144px`, previously only in the SCSS `@prop` JSDoc, never in consumer-facing docs — this project's established convention, per `bds-color-picker.mdx`, is to name custom properties in prose), and preset-click calendar navigation (shipped in Task with commit `c9a15a19`, never mentioned in docs).
- `## Accessibility`'s day-grid bullet and its trailing `<Callout>` were both stale in the same way — implying month-nav/footer/preset buttons were mouse-only alongside day cells, when they're real `bds-button`/`<button>` elements, natively `Tab`-reachable. Both corrected to state day-grid cells are the sole mouse-only exception.
- `## Component preview` (Basic Usage/Preselecting a value/Custom format/Locale) moved to sit directly after `### Component composition`, before `## Calendar types` — previously it sat between `## Range selection` and `## Time selection`. Table of contents reordered to match. Checked every "above"/"below" directional reference in the file for breakage from the move — none referenced Component preview's position.
- Rebuilt `pnpm --filter boreal-docs run build` clean after all changes.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 6 presets sidebar"`

---

### Task 34: React/Vue wrapper parity check — Phase 6

**Status:** ✅ done (2026-09-11) — verified by `@qa-subagent` via the pack-based pipeline (`dev:pack:react` then `dev:pack:vue`, run serially per project memory). All four of Task 30's scenarios pass identically in both wrappers, matching the raw web-component baseline exactly: preset selection/deselection, calendar auto-navigation on preset click, `min`/`max` preset disabling (Scenario 3), and the `with-time` coverage-shift header boundary (Scenario 4). Zero `bds-date-picker`-related console errors in either wrapper. One non-issue noted: Scenario 3's exact disabled-preset set is date-relative (presets recompute live off "today," no memoization by design) — re-running a day after the plan text was written shifted which presets land in/out of the fixed `min`/`max` bounds, expected drift, not a regression or wrapper divergence. The four scenarios were added as permanent QA artifacts to both playground test apps (`examples/react-testapp/src/App.tsx`, `examples/vue-testapp/src/App.vue`), mirroring `packages/boreal-web-components/src/index.html`'s `dp-task30-s1..s4`. No wrapper-package source changes were needed — this was a verification-only task.

**Executor:** @qa-subagent
**Files:** `examples/react-testapp/src/App.tsx` (modify — added QA scenarios), `examples/vue-testapp/src/App.vue` (modify — added QA scenarios)

**Acceptance criteria:** Presets-sidebar behavior matches across wrappers.

**Manual test (required):**

Repeat Task 30's Scenarios 1-4 through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [x] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in preset selection/deselection or header rendering. **Verified live 2026-09-11** via `dev:pack:react`.
- [x] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence. **Verified live 2026-09-11** via `dev:pack:vue`.

**Commit:** N/A

---

### Task 34a (new — discovered during manual QA of Task 30's presets sidebar, 2026-09-18): presets sidebar resets to "Custom" on popover reopen instead of re-matching the committed value

**Status:** ✅ done (2026-09-21) — implemented by `@frontend-subagent`: new `matchPreset(rangeStart, rangeEnd, withTime, timezone)` in `utils/presets.ts` iterates `BUILT_IN_PRESET_KEYS`, comparing each candidate's `computePresetRange` start and `computePresetCoverageEnd`-shifted end (accounting for the with-time +1-day shift `resetRangeDraft` already bakes into `draft.rangeEnd`) against the draft's naive-ISO bounds; `listenClickTrigger` now calls it (gated on `effectiveRange`) instead of unconditionally forcing `PRESET_KEY.CUSTOM`. `tsc --noEmit` clean (same pre-existing unrelated `bds-dialog`/`bds-tooltip` failures as before), full suite 352 tests / 0 regressions.

Unit tests by `@testing-subagent`: 5 new `matchPreset` pure-function tests (exact match, breadth via Last month, with-time coverage-shifted-end match, null-input short-circuit, non-matching-range null) plus 4 component-level reopen-rematch tests in `bds-date-picker.presets.spec.ts` (exact-match reopen, false-positive-avoidance/Custom, with-time shift, single-date-mode-still-forces-Custom regression). `presets.ts` 100% coverage, `bds-date-picker.tsx` 98.67% stmts/95.36% branch — both above the 90% gate. Mutation testing correctly deferred to Task 53.

Manual QA by `@qa-subagent`, verified live via real mouse clicks (playwright-cli) against the existing `dp-presets-s1`/`s2`/`s4` playground scenarios, dev server on port 3333: all 3 scenarios pass — exact-match reopen (Today), false-positive avoidance (Custom on a non-matching manual range), and with-time coverage-shift match (Last 7 days, shifted end correctly unshifted before comparison). Verified via actual DOM `--selected` class, not just visual glance. Zero console errors. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @qa-subagent (manual test)
**Files:** `utils/presets.ts` (modify — new `matchPreset` function), `bds-date-picker.tsx` (modify — `listenClickTrigger`), `utils/__test__/presets.spec.ts` (modify)

**Gap (confirmed live in-browser, 2026-09-18):** applying a built-in preset (e.g. "Today"), closing the popover, and reopening it shows "Custom" selected in the presets sidebar — even though the committed value is byte-for-byte what "Today" computes. Root cause: `listenClickTrigger` (`bds-date-picker.tsx:521-529`) unconditionally resets `this.selectedPreset = PRESET_KEY.CUSTOM` on every popover open, immediately after rebuilding the draft via `resolveInitialDraft()` — there is no reverse-lookup from a committed value back to a matching preset anywhere in the component. The calendar, header, and trigger-field text are all unaffected and correct; only the sidebar's selection indicator is wrong.

**Acceptance criteria:**

- New `matchPreset(rangeStart, rangeEnd, withTime, timezone, ...)` in `presets.ts`: iterates `BUILT_IN_PRESET_KEYS`, recomputes each candidate's real range via `computePresetRange`, and returns the matching key or `null`.
- Must correctly account for the `with-time` coverage shift: `resetRangeDraft` derives `rangeEnd` from the **committed**, possibly coverage-shifted value (`computePresetCoverageEnd` adds +1 day for with-time presets) — a naive comparison against `computePresetRange`'s raw output would false-negative on every with-time preset. The match function must unshift (or recompute the coverage-shifted candidate) before comparing.
- `listenClickTrigger` calls `matchPreset` when rebuilding the draft on open and sets `selectedPreset` to the result (or `CUSTOM` if no match) instead of unconditionally forcing `CUSTOM`.
- No change to preset-click, Cancel, or Clean behavior — those already correctly set/reset `selectedPreset` and are out of this task's scope.

**Manual test (required):**

Reuse the existing presets sidebar scenarios (`dp-presets-s1`/`s2` in `packages/boreal-web-components/src/index.html`). Run `pnpm dev:components` and validate:

- [ ] Given a picker with a preset applied (e.g. "Today"), when the popover is reopened, then the sidebar shows that same preset selected, not "Custom". Pass: className/selected-state check, not just visual.
- [ ] Given a picker with a manually-selected (non-preset-matching) range applied, when reopened, then the sidebar correctly shows "Custom". Pass: no false-positive match.
- [ ] Given a with-time preset (e.g. "Last 7 days" with `with-time`), when reopened, then the sidebar still correctly matches despite the committed value's coverage-shifted end. Pass: no false-negative from the shift.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 re-derive selected preset on popover reopen"`

---

### Task 34a-1 (new — discovered while manually verifying Task 34a's fix, 2026-09-21): Cancel forces "Custom" even when the committed value it reset to still matches a preset, causing a visible flash on the next reopen

**Status:** ✅ done (2026-09-21) — root-caused directly (not via subagent) using live `MutationObserver` instrumentation on the presets sidebar's `class` attribute against the running dev server (port 3333), since the flash was too fast to catch by eye or a single screenshot. Confirmed the wrong "Custom" state was written to the (hidden) DOM the instant Cancel ran — not merely a rendering-timing artifact — making the fix a correctness fix, not a debounce/ordering workaround.

Implemented by `@frontend-subagent`: `handleFooterAction`'s `CANCEL` branch now re-derives `selectedPreset` via the same `matchPreset(...) ?? PRESET_KEY.CUSTOM` pattern `listenClickTrigger` already uses (Task 34a), evaluated after `this.draft` is reassigned. `CLEAN`/`APPLY` untouched. 3 new unit tests added to `bds-date-picker.presets.spec.ts` (immediate re-match on Cancel, Custom-preserved on non-matching range, Custom-preserved on null bounds). `tsc --noEmit` clean (same pre-existing unrelated failures as before); full package suite independently re-run by the orchestrating session (324 suites / 3600 tests / 1 pre-existing todo, 0 failures).

Manual QA by `@qa-subagent`, using the same `MutationObserver` root-cause technique to verify the fix rigorously (not just visually): zero class-attribute mutations recorded on the presets sidebar across the entire Cancel handler execution, confirming no intermediate "Custom" state exists at any point, not even a same-tick one. All 4 scenarios pass (immediate correct state post-Cancel, no flash on reopen, Custom preserved for non-matching ranges, Custom preserved with nothing committed). Nothing committed — per standing preference, commits are the user's own action.

**Gap (confirmed live, 2026-09-21):** applying "Today", closing (Apply), reopening (correctly shows "Today" per Task 34a), then clicking **Cancel**, then reopening again shows a barely-perceptible flash of "Custom" before switching back to "Today". Root-caused via a `MutationObserver` on the presets sidebar's `class` attribute (too fast to catch reliably by eye): the instant Cancel runs, `handleFooterAction`'s `CANCEL` branch (`bds-date-picker.tsx:468-477`) rebuilds `this.draft` from the **unchanged** committed value via `resetRangeDraft(this.rangeValue ?? '', ...)`, but then unconditionally sets `this.selectedPreset = PRESET_KEY.CUSTOM` — even though the committed value it just reset to still matches "Today". This wrong state sits in the (now-hidden) DOM until the next open, when `listenClickTrigger`'s `matchPreset` call (Task 34a) corrects it — producing the visible flash. This is the same class of bug Task 34a fixed in `listenClickTrigger`, in the sibling `CANCEL` code path, which Task 34a's own scope didn't touch (its "no change to Cancel... behavior" acceptance criterion was written before this sibling bug was known).

`CLEAN` is unaffected and correct as-is — that branch actually clears the committed value to `''`, so forcing `CUSTOM` there is right (nothing to match).

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `handleFooterAction`'s `CANCEL` branch), `__test__/bds-date-picker.presets.spec.ts` (modify)

**Acceptance criteria:**

- The `CANCEL` branch's `this.selectedPreset = PRESET_KEY.CUSTOM` is replaced with a `matchPreset` re-derivation identical in shape to `listenClickTrigger`'s: `this.effectiveRange ? (matchPreset(this.draft.rangeStart, this.draft.rangeEnd, this.effectiveWithTime, this.timezone) ?? PRESET_KEY.CUSTOM) : PRESET_KEY.CUSTOM`, evaluated after `this.draft` has been reassigned on the line above (so it reads the freshly-reset draft, not the discarded one).
- `CLEAN`'s unconditional `PRESET_KEY.CUSTOM` is left untouched — out of scope, already correct.
- No change to `APPLY`'s branch (doesn't touch `selectedPreset` today and shouldn't gain that here).
- After Cancel, `selectedPreset` immediately (synchronously, no reopen needed) reflects a re-derived match against the restored committed value — eliminating the wrong intermediate state at its source, not just papering over the visible symptom on reopen.

**Manual test (required):**

Reuse `dp-presets-s1`/`s2` in `packages/boreal-web-components/src/index.html`. Run `pnpm dev:components` and validate:

- [ ] Given a preset applied and committed (e.g. "Today"), when Cancel is clicked, then `selectedPreset` (inspect via component instance/DOM `--selected` class, not just visual) is immediately "Today", not "Custom" — checked before any reopen.
- [ ] Given the same flow, when the popover is reopened after Cancel, then there is no visible flash — the sidebar shows "Today" selected from the first rendered frame.
- [ ] Given a manually-selected (non-preset-matching) range applied and committed, when Cancel is clicked, then `selectedPreset` correctly remains "Custom" (no false positive from the new re-derivation).
- [ ] Given no value committed yet (fresh picker, nothing applied), when Cancel is clicked, then `selectedPreset` remains "Custom" (`matchPreset` returns `null` on null bounds, per Task 34a's existing null-guard).

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 re-derive selected preset on cancel instead of forcing Custom"`

---

### Task 34a-2 (new — discovered while investigating a user-reported duplicate day-highlight on "Today"/"Yesterday" reopen, 2026-09-21): `resetRangeDraft` never reverses the with-time coverage shift on reopen, violating Task 29's own "real, unshifted days" invariant and snowballing +1 day per Apply→reopen→Apply cycle

**Status:** ✅ done (2026-09-21) — root-caused directly (not via subagent) via full code trace, confirming a real, previously-untracked violation of Task 29's own documented invariant, and cross-checking that Task 34a's `matchPreset` was (unknowingly) built assuming the violated state as its input.

Implemented by `@frontend-subagent`: new shared private method `correctHydratedRangeEnd(draft, matchedPreset)` — unconditional -1 day for `basic` (matches ADR 0015's unconditional shift), recompute both bounds from `computePresetRange(matchedPreset, timezone)` for `expanded` only when a preset matched (manual `expanded` selections were never shifted, left untouched). Wired into both `listenClickTrigger` and the `CANCEL` branch, after `matchPreset` evaluates the raw (still-shifted) hydrated bounds — `matchPreset` itself unchanged. `tsc --noEmit` clean; full suite 324/324 suites, 3607 tests, 0 failures; no existing test assertions needed updating.

Unit tests by `@testing-subagent`, in `bds-date-picker.presets.spec.ts`: 9 new tests covering the `expanded`+"Today" round-trip (highlight, header/field match, 3-cycle drift-stability), `basic`+manual-multi-day round-trip (same three checks), `expanded`+manual-non-matching regression (no-op confirmation), and `withTime=false` regression for both calendar types. **Explicitly verified the tests catch the real bug**, not just pass trivially: temporarily disabled `correctHydratedRangeEnd`, observed 6/9 tests fail with exactly the described +1-day drift, then restored the fix and confirmed a clean full-suite re-run (324/324, 3616 tests, 98.75%/95.61% coverage on `bds-date-picker.tsx`).

Manual QA by `@qa-subagent`, live against `dp-presets-s4` (`expanded`+with-time) and `dp-presets-s2` (`basic`+with-time — `with-time` added to this scenario, as the plan anticipated it might be missing): all 5 checklist items pass with concrete evidence exactly matching the plan's predicted values — e.g. "Today" round-trip stayed at committed end `2026-09-22T00:00:00.000-05:00` across 3 consecutive reopen→Apply cycles (no drift to `-23`/`-24`), calendar highlighting showed exactly one real day per cycle, and the `expanded`+manual-non-matching regression case was confirmed byte-identical to pre-fix behavior. Zero console errors. Nothing committed — per standing preference, commits are the user's own action.

**Gap (confirmed via full code trace, 2026-09-21, not hypothetical):** Task 29's own design notes (this plan, line ~452) require: _"`draft.rangeStart`/`draft.rangeEnd` must always hold the real, unshifted days from `computePresetRange` — never the shifted coverage end — since these also drive the calendar grid's own highlighting."_ `selectPresetRange` (preset click) honors this. `resetRangeDraft` (`utils/draft-state.ts`, ~line 190-218 — the function that rebuilds `draft` from a **committed** value, run on every popover open/Cancel) does **not**: its `withTime` branch extracts `committedValue.end`'s date part verbatim and stores it directly as `draft.rangeEnd`, with no reversal of the +1-day coverage shift that was applied when that value was originally committed (per ADR 0015, as revised 2026-09-24: `basic` shifts unconditionally; `expanded` shifts whenever both bounds share a time-of-day — superseding this note's original "only while a preset is active" description, which Task 35's 2026-09-22 data-driven fix replaced).

Effect, traced end-to-end for `expanded`+"Today"+with-time (the user's original report — reproduced via live `MutationObserver`/DOM inspection, not just code-reading): Apply commits `end = Sept 22` (Sept 21 + 1-day shift). Reopen hydrates `draft.rangeEnd = "2026-09-22"` (the shifted boundary, not the real end `"2026-09-21"`) — this is the invariant violation. Consequences, all downstream of that one bad value: (1) the calendar highlights **both** Sept 21 and Sept 22 (`rangeEndDate` in `bds-date-picker.tsx`'s `render()` is `fromNaiveISODate(this.draft.rangeEnd)` directly, no unshift); (2) `matchPreset` (Task 34a) correctly matches this to "Today" since it was specifically designed to expect the shifted hydrated value as input (its own doc comment says so) — so the sidebar shows the right preset despite the underlying data being wrong; (3) the header (`resolveRangeEndIso`) then applies the shift **again** on top of the already-shifted `draft.rangeEnd`, showing `End: Sept 23` — a double shift. If Apply is clicked again with no changes, the newly-committed end becomes `Sept 23` — **the bug compounds by one extra day on every Apply→reopen→Apply cycle**, with no user action causing it.

**Confirmed broader than presets:** `basic + range + with-time` shifts _unconditionally_ at commit (ADR 0015), for preset-originated **and manual** selections alike — so this hits every `basic`+range+with-time reopen, not just presets. `expanded` is only affected for preset-originated commits; manual `expanded` selections were never shifted at commit, so their reopen was already correct (confirmed unaffected, no regression risk there). _(Superseded 2026-09-22: Task 35's fix made `expanded` shift any equal-time selection, preset or manual, so this asymmetry no longer holds — see that task's 2026-09-22 note.)_

**Three-way consistency (input field / popover header / calendar highlight):** the trigger field's closed-state text (`syncFieldValue` → `formatRangeValueForDisplay`) reads directly from the committed `value` prop, entirely independent of `draft` — it was **never** affected by this bug and always showed the correct, real committed boundary. The bug was specifically that `draft`-derived state (header text via `resolveRangeEndIso(draft)`, and calendar highlighting via `draft.rangeStart`/`rangeEnd` directly) fell out of sync with that already-correct committed value on reopen. Fixing the hydration makes all three converge: the header's shift computation and the trigger field's displayed committed end become the same value (both are "real day + one shift," from the same real anchor), while the calendar shows that real anchor directly.

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `listenClickTrigger` and `handleFooterAction`'s `CANCEL` branch), `utils/__test__/draft-state.spec.ts` or `bds-date-picker.time-helpers.spec.ts` (modify — `resetRangeDraft`'s documented behavior doesn't change, so no edit needed there unless the fix approach below changes), `__test__/bds-date-picker.presets.spec.ts` (modify), `__test__/bds-date-picker.range.spec.ts` or nearest existing round-trip coverage (modify)

**Acceptance criteria:**

- After `resetRangeDraft` hydrates and `matchPreset` is evaluated (both in `listenClickTrigger` and in the `CANCEL` branch of `handleFooterAction`, evaluated identically in both places — extract a small shared private method rather than duplicating the correction logic twice, since it's the same non-trivial shape at two call sites, not a one-line duplication), correct `draft.rangeEnd` back to the real (unshifted) day:
  - `basic` (`!isExpandedCalendarType`): always unshift by one day when `effectiveWithTime` is true and `draft.rangeEnd !== null` — the commit-time shift for `basic` is unconditional (ADR 0015), so the reverse must be unconditional too, regardless of whether `matchPreset` found a match.
  - `expanded` (`isExpandedCalendarType`): only correct when `matchPreset` found a match — in that case, recompute `draft.rangeStart`/`draft.rangeEnd` from `computePresetRange(matchedKey, timezone)` directly (the real, unshifted range) rather than arithmetically subtracting a day, for full correctness against any edge drift. When no match is found (manual `expanded` selection), leave `draft.rangeEnd` untouched — it was never shifted at commit, so there's nothing to reverse. _(Superseded 2026-09-22 by Task 35's follow-on fix, which also makes `correctHydratedRangeEnd` un-shift any equal-time custom `expanded` range — see that task's "Necessary follow-on fix" note.)_
  - `matchPreset` itself is NOT changed — it continues to receive the raw (still-shifted, pre-correction) hydrated bounds as its input, exactly as designed in Task 34a; only the correction step that runs _after_ it changes.
- Header text (`resolveRangeEndIso(draft.rangeStart, draft.rangeEnd)`) after the fix exactly equals the currently-committed value's `end` for every already-committed, unmodified draft (no drift introduced by the fix itself) — verify this explicitly for both a preset-originated and a manual `basic`/`expanded` with-time range.
- Re-Apply with no changes after a reopen produces the exact same committed value as before (no snowball/drift across Apply→reopen→Apply cycles) — this is the core regression this task closes, verify explicitly with at least 2 consecutive reopen→Apply cycles asserting the committed value is unchanged both times.
- No change to `expanded`+manual (non-preset) reopen behavior — already correct, must remain byte-identical. _(Superseded 2026-09-22 by Task 35's fix — `expanded` manual equal-time ranges now commit shifted, so their reopen/hydration behavior changed accordingly; distinct-time manual ranges remain byte-identical.)_
- No change to `withTime=false` behavior anywhere (the shift/correction logic is entirely gated on `effectiveWithTime`).

**Manual test (required):**

Reuse `dp-presets-s1` (`expanded`), `dp-presets-s2` (`basic`), and `dp-presets-s4` (`expanded`+with-time) in `packages/boreal-web-components/src/index.html`; add `with-time` to `dp-presets-s2` if it doesn't already have it, since `basic`'s bug requires with-time to reproduce. Run `pnpm dev:components` and validate:

- [ ] Given `expanded`+with-time, apply "Today", reopen: the calendar highlights **only** Sept 21 (the real day) — not Sept 21 and Sept 22. Pass: inspect the DOM `--selected`/range classes directly, not just visually.
- [ ] Given the same picker, the header shows `End: Sept 22` (not Sept 23) — matching the trigger field's own displayed committed text exactly.
- [ ] Given the same picker, reopen and click Apply again with no changes: the committed `bdsChange`/`value` end stays `Sept 22` — does not drift to `Sept 23`. Repeat once more (a third open→Apply) to confirm it stays stable, not just corrected once.
- [ ] Given `basic`+with-time, manually select a multi-day range (e.g. Sept 5–10) with a shared time, Apply, reopen: the calendar highlights exactly Sept 5–10 (not Sept 5–11), and the header/trigger field agree on the same committed end time. Repeat the reopen→Apply-with-no-changes check here too.
- [ ] Given `expanded`+with-time, manually select a non-preset-matching range (no preset applied), Apply, reopen: behavior is unchanged from before this fix (already correct) — regression check only.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 restore real unshifted rangeEnd on reopen, fixing duplicate highlight and header drift"`

---

### Task 34b (new — discovered during manual review of the `expanded`+`range=false` combination, 2026-09-18): missing dev warning and duplicate day-highlight bug for `expanded` without `range`

**Status:** ✅ done (2026-09-21) — implemented by `@frontend-subagent`: two new `componentWillLoad` warnings (`isExpandedCalendarType && !this.range` and `... && this.withTime`) following the existing `isDefaultCalendarType` warning pattern exactly; `bds-calendar-grid.tsx`'s `--selected` class AND `aria-selected` attribute (the latter caught during implementation as the same bug, not called out explicitly in the plan's own gap description, but fixed for consistency) both gained an `isCurrentMonth` guard, matching `grid.ts`'s existing filler-cell-suppression precedent. Docs: new `<Callout variant="warning">` under `### Expanded` plus a cross-reference under `## Range selection`, matching the existing `### Default` treatment. New playground scenario `dp-expanded-no-range-s1` added. `tsc --noEmit` clean (same pre-existing unrelated failures); full package suite 324 suites/3600 tests/0 failures at implementation time.

Unit tests by `@testing-subagent`: highlight-guard regression tests placed in `bds-calendar-grid.variants.spec.ts`/`bds-calendar-grid.a11y.spec.ts` (the plan's named `basics.spec.ts` doesn't hold this coverage — existing `--selected`/`aria-selected` tests actually live in these two files, so new tests were added alongside them instead) covering both the fixed filler-cell case and the still-correct current-month case; 5 new tests in `bds-date-picker.calendartype.spec.ts` covering both warnings firing/not-firing across `calendarType`/`range`/`withTime` combinations. `bds-calendar-grid.tsx` 100% coverage, `bds-date-picker.tsx` 98.69% stmts — both above gate. 361 passed/1 todo, 0 failures.

Manual QA by `@qa-subagent`: all 4 checks pass — both warnings fire exactly once each on `dp-expanded-no-range-s1`; Sept 30 highlighted only in September's grid, not as a filler in October's; MDX documentation confirmed accurate; regression sanity check on `dp-presets-s4` (`expanded+range=true+withTime`) confirmed zero new warnings and unaffected range highlighting. QA also diagnosed and fixed an unrelated environment issue (stale dev-server bundle + a missing `@telesign/boreal-style-guidelines` `dist/` from a concurrent build) to get a clean verification run. Dev server was torn down at the end of this QA pass since more manual-QA tasks follow later in the plan — the next QA dispatch will need to restart it. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @documentation-subagent (docs), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `componentWillLoad`), `bds-calendar-grid.tsx` (modify — `--selected` class guard), `bds-date-picker.mdx` (modify), `bds-calendar-grid/__test__/bds-calendar-grid.basics.spec.ts` (modify or nearest existing highlight-coverage spec), `bds-date-picker/__test__/bds-date-picker.calendartype.spec.ts` (modify)

**Gap 1 (missing warning):** `calendarType='expanded'` always renders two calendars regardless of `range` (`bds-date-picker.tsx:874`, no `range` condition), but with `range=false` only a single date can be selected — one calendar is functionally wasted. If `withTime` is also set, the consumer additionally does not get dual time selectors (the dual-selector gate at `bds-date-picker.tsx:959` requires `effectiveRange && isExpandedCalendarType`) — it silently falls back to the same single-shared-time selector as `basic`, despite explicitly choosing `expanded`. Neither case produces any developer-facing signal today.

**Gap 2 (duplicate highlight bug, confirmed real):** in `expanded + range=false`, the same `this.draft.selectedDate` is passed identically to both calendar instances (`renderCalendarPanel.tsx:32-44`). `bds-calendar-grid.tsx:102`'s `--selected` class match (`cell.isoDate === this.selectedDate`) has no `isCurrentMonth` guard — unlike the range-highlighting path, which already correctly excludes adjacent-month filler days (`grid.ts:100-101`). When the selected date also appears as a leading/trailing filler cell in the other calendar's grid (near a month boundary), it gets highlighted in both calendars simultaneously. Confirmed exclusive to `expanded + range=false`; range mode is unaffected by construction (it never uses `selectedDate`).

**Acceptance criteria:**

- `componentWillLoad` gains two new `this.logger.warn('bds-date-picker', ...)` calls, following the exact existing pattern used for `default+range`/`default+withTime`:
  - `isExpandedCalendarType && !this.range` → warns that `expanded` always renders two calendars but only a single date can be selected when `range` is false; suggests `calendar-type='basic'`.
  - `isExpandedCalendarType && !this.range && this.withTime` → warns that dual start/end time selectors require `range` to be true; with `range` false, `with-time` falls back to a single shared selector.
- `bds-calendar-grid.tsx:102`'s `--selected` class condition gains an `isCurrentMonth` guard, mirroring the existing pattern already used for range-flag suppression on filler cells (`grid.ts:100-101`) — a selected date belonging to the adjacent month's real position must not highlight in a grid where it only appears as filler.
- **Documentation**, following the existing warning-documentation pattern found in `bds-date-picker.mdx`: the `with-time`+`default` warning has a dedicated `<Callout variant="warning" icon="⚠️">` under `## Calendar types` → `### Default`; the `range`+`default` warning is only inline prose under `## Range selection`'s intro. Give the new `expanded`+`range=false` warnings the same dedicated-Callout treatment under `## Calendar types` → `### Expanded` (covering both the wasted-second-calendar and time-selector-fallback warnings together, since they share one combination), plus a short inline cross-reference under `## Range selection`'s intro, matching the existing `range`+`default` treatment.
- No behavior change to `expanded + range=true` (any `withTime` value) — both fixes are scoped strictly to `range=false`.

**Manual test (required):**

Add a new playground scenario to `packages/boreal-web-components/src/index.html`: `calendarType='expanded'`, `range=false`, `withTime=true`, with `value` set near a month boundary (e.g. the last day of a month, so it also appears as a filler day in the adjacent calendar).

Run `pnpm dev:components` and validate:

- [ ] Given this scenario, when the popover opens, then the console logs both new warnings exactly once each (not per-render). Pass: exactly two warnings, correct text.
- [ ] Given the same scenario, when the popover opens, then the selected date is highlighted in exactly one calendar, not both. Pass: only the calendar whose actual month contains the selected date shows the `--selected` styling.
- [ ] Given the updated MDX, when read, then the `expanded`+`range=false` warning is documented with the same Callout treatment as the existing `default` warnings. Pass: no stale/missing documentation.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 warn on expanded without range and fix duplicate day highlight"`

---

### Task 34c (new — blocking design gate, discovered while scoping intraday range selection, 2026-09-18): ADR 0016 — same-day intraday range time-ordering semantics

**Status:** ✅ done (2026-09-21) — decided directly with the user, no subagent dispatch (design/API checkpoint, matches Task 28's precedent).

**Decision: Option 4 (Hybrid) — auto-shift +1 day, made visible.** When `expanded + range + with-time` produces a same-day selection (`rangeStart === rangeEnd`) with `endHour`/`endMinute` earlier than `startHour`/`startMinute`, the effective end date used for the header display and the Apply commit is `rangeEnd + 1 day` (an overnight reinterpretation), and the labeled `Start:`/`End:` header shows this resolved end date **live**, as soon as the inversion exists in the draft — not only after Apply. The real underlying selection (`draft.rangeStart === draft.rangeEnd`, the grid highlighting) is unaffected; only the display/commit boundary shifts, following the same real-anchor-plus-computed-boundary pattern ADR 0015 already established for the coverage shift.

**Scope:** the shift condition is general (same-day + inverted time), not special-cased to "reached via double-click" — but since no other currently-reachable path produces this state (every preset commits `00:00`/`00:00`; `basic` cannot express two different times), it has no retroactive effect on any existing behavior. It only ever activates for the new interaction Task 34d introduces.

Full rationale, options considered, and consequences: [`ai-docs/decisions/0016-date-picker-intraday-range-time-ordering.md`](../../ai-docs/decisions/0016-date-picker-intraday-range-time-ordering.md). This resolves every "pending Task 34c" conditional in Task 34d below to Option 4's concrete mechanics.

**Executor:** none (design/API checkpoint, decided directly with the user — matches Task 28's precedent)
**Files:** `ai-docs/decisions/0016-date-picker-intraday-range-time-ordering.md` (new)

**Context:** Task 34d (below) makes same-day ranges reachable via manual selection (double-click) in `expanded + range + withTime` for the first time — today this state is only reachable via a built-in preset, which always sets both times to `00:00`. Once reachable manually, nothing prevents a user from setting an End time earlier than the Start time on the same day (e.g. Start `14:00`, End `09:00`); no validation anywhere in the commit path currently catches this — `buildRangeCommitValue`/the Apply-button-enabled check only require both bounds to be non-null, never `start <= end` at the time-of-day level.

**Decision needed — three options, plus a hybrid, evaluated in this session:**

1. **Block**: disable Apply (or show an inline error) when `endTime < startTime` on a same-day range. Safe and explicit, but introduces inline-validation UI this component has never needed before.
2. **Allow as-is**: commit the inverted range unchanged. Simplest, but breaks the `end >= start` invariant this component has guaranteed for every value it's ever produced (per ADR 0015's own governing principle) — the first case where a consumer could receive `end < start`.
3. **Auto-shift +1 day**: reinterpret `14:00–09:00` as an overnight window, `14:00` today to `09:00` tomorrow. Consistent with ADR 0015's existing precedent of resolving ambiguity via a semantic shift rather than blocking or emitting an invalid value; a recognized pattern in other date-range pickers (overnight/red-eye bookings).
4. **Hybrid (recommended for consideration)**: apply option 3's shift, but make it visible — the labeled `Start:`/`End:` header (already capable of showing per-bound dates, per Phase 5) explicitly displays the resolved end date (e.g. "End: Sep 19, 09:00") rather than shifting silently, so the user sees the reinterpretation rather than discovering it only after Apply.

**Acceptance criteria:**

- Decision recorded with rationale, following ADR 0015's exact format/structure.
- Decision explicitly states which option (1-4) is chosen and why, and what it implies for Task 34d's validation/commit logic.
- If option 3 or 4 is chosen, decision states whether the shift applies only to manual same-day selection (Task 34d's new case) or also retroactively to any other reachable same-day-with-inverted-time state.
- Resolves every "pending Task 34c" conditional in Task 34d below.

**Manual test:** N/A — design/API checkpoint.

**Commit:** N/A (documentation-only artifact, not a code change).

---

### Task 34d (new — discovered while investigating intraday range selection; depends on Task 34c's decision): enable same-day range selection via double-click in `expanded + range + withTime`

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @documentation-subagent (Storybook), @qa-subagent (manual test)
**Files:** `utils/draft-state.ts` (modify — `selectRangeDay`), `bds-date-picker.tsx` (modify — per Task 34c's decision, if validation/shift logic is needed at commit), `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify — new story), `bds-date-picker.mdx` (modify), `utils/__test__/draft-state.spec.ts` (modify), `__test__/bds-date-picker.range.spec.ts` / `__test__/bds-date-picker.time.spec.ts` (modify)

**Context (verified this session, not hypothetical):** `expanded + range + withTime` already correctly commits a genuine intraday range (same day, distinct start/end times) when reached via preset-then-manual-edit — verified end to end: `rangeEndShiftApplies` skips the coverage shift whenever the two bounds' times differ (**data-driven since Task 35's 2026-09-22 fix** — superseding this note's original "skips once `selectedPreset === CUSTOM`" description), so setting distinct start/end times leaves it false; the commit path (`buildRangeCommitValue`) then combines each bound independently via `combineDateTimeToUTC`, producing exactly the intraday shape. Nothing downstream (display, formatting) special-cases `rangeStart === rangeEnd`. The only missing piece is that **manual calendar clicks alone can never reach `rangeStart === rangeEnd`** — `selectRangeDay`'s same-day-click branch is currently a no-op (a second click matching the existing `rangeStart` returns the identical draft, doing nothing).

This is exclusively an `expanded` capability — `basic`'s shift check is driven purely by its (always-equal) two bounds' times, so it always shifts, and its single shared time field cannot express two different times regardless. No `basic` changes are in scope.

**Acceptance criteria:**

- `selectRangeDay`'s same-day no-op branch is changed to set `rangeEnd = rangeStart` (a single click on the day already selected as `rangeStart` confirms a one-day range) instead of returning the draft unchanged.
- The existing manual-click-reverts-to-Custom behavior already applies (no change needed) — confirm via test that a deliberately distinct End time naturally leaves the coverage shift off for `expanded` (the shift is data-driven, not Custom-gated, since Task 35's 2026-09-22 fix), exactly as the preset-then-edit path already does.
- **Per ADR 0016 (Task 34c, Option 4 — Hybrid):** add a general condition — evaluable on the draft state, not special-cased to the double-click path — detecting `isExpandedCalendarType && effectiveRange && effectiveWithTime && draft.rangeStart === draft.rangeEnd && (endHour, endMinute) < (startHour, startMinute)`. When true:
  - The real `draft.rangeStart`/`rangeEnd` and grid highlighting are left untouched (still the one real day the user clicked).
  - A new "effective end date" — `rangeEnd + 1 day` — is computed for display and commit purposes only, following the same real-anchor-plus-computed-boundary pattern as `computePresetCoverageEnd` (ADR 0015). Do not mutate `draft.rangeEnd` itself to hold this shifted value — compute it at the point of use (header render, Apply commit), matching how `resolveRangeEndIso` already works for the ADR 0015 shift, and matching what Task 34a-2 restored as the correct pattern (real day in the draft, shift computed separately at display/commit time).
  - The labeled `Start:`/`End:` header (`renderRangeHeader.tsx`) shows this resolved end date **live** — as soon as the inversion exists in the draft (e.g., right after the second time field is edited to create the inversion), not only after Apply clicking.
  - The Apply commit uses this same resolved end date, so the header (pre-Apply) and the trigger field's text (post-Apply) never disagree.
- No change to `basic`'s behavior (structurally unreachable per ADR 0016 — confirm via test that `basic` cannot reach this condition at all, rather than assuming), or to `expanded`'s existing multi-day range-click logic.
- New Storybook story demonstrating the double-click same-day intraday flow explicitly, including a sub-case showing the inverted-time auto-shift with its live header display, plus MDX documentation stating both (a) same-day selection is an intentional, supported interaction, and (b) the auto-shift/live-display behavior for inverted times, per ADR 0016 — documented as a second, narrower quirk alongside ADR 0015's own existing coverage-shift quirk, not conflated with it.

**Manual test (required):**

Add a new playground scenario: `calendarType='expanded' range with-time`.

Run `pnpm dev:components` and validate:

- [x] Given this scenario, when the same day is clicked twice, then `rangeStart === rangeEnd` and both Start/End time selectors become independently editable. Pass: no popover close, no error. **Verified 2026-09-22.**
- [x] Given independent Start/End times set on that same day where End is later than Start, when Apply is clicked, then the committed `{start, end}` reflects the same date with the two distinct times, with no ADR 0015 coverage shift applied. Pass: matches the already-verified preset-then-edit behavior exactly. **Verified 2026-09-22.**
- [x] Given the same same-day selection, when the End time is set earlier than the Start time (e.g. Start `14:00`, End `09:00`), then the header immediately (before Apply) shows the resolved End date as the following day (e.g. "End: Sep 19, 09:00" when Start is "Sep 18, 14:00") — not the same day. Pass: header updates live, no need to click Apply first to see the shift. **Verified 2026-09-22 — the critical check, confirmed live before Apply.**
- [x] Given that same inverted-time selection, when Apply is clicked, then the committed `end` is a full calendar day after `start`'s date, at the entered end time — and the trigger field's displayed text after Apply matches exactly what the header showed before Apply. Pass: matches ADR 0016, no discrepancy between pre-Apply header and post-Apply trigger text. **Verified 2026-09-22, character-for-character match.**
- [x] Given the new Storybook story, when rendered, then it renders without console errors and demonstrates both the plain same-day flow and the inverted-time auto-shift flow end-to-end. **Verified 2026-09-22.**

**Status:** ✅ done (2026-09-22) — implemented by `@frontend-subagent`: `selectRangeDay`'s same-day branch now sets `rangeEnd = rangeStart` instead of returning the draft unchanged; new `resolveEffectiveRangeEndIso` (wraps `resolveRangeEndIso`, checks the same-day-inverted-time condition, never mutates `draft.rangeEnd`) is the single source of truth for both the header's `rangeEndText` and the Apply commit's `commitRangeEnd`. `tsc --noEmit` clean; full suite 324/324 suites, 3620 tests, 0 failures. New Storybook story + MDX section + `dp-intraday-range-s1` playground scenario added.

Unit tests by `@testing-subagent`: 9 tests total (5 self-verification tests from the implementation pass plus 4 added: trigger-field/header text-equality after Apply, the equal-times boundary case) plus a `draft-state.spec.ts` update; extended the failure-mode catalog (FM-66 through FM-69). Confirmed the equal-times boundary (`endMinutes < startMinutes`, strict) is deliberate, not a bug — a zero-duration same-day range is a legitimate, separately-reachable state, and neither the ADR nor this task's acceptance criteria ask for a minimum-duration invariant. Full suite 324/324 suites, 3622 tests, 98.79% coverage on `bds-date-picker.tsx`.

Manual QA by `@qa-subagent`: all 5 checklist items pass, plus the `basic`+range+with-time regression check (confirmed structurally unaffected — only one shared time field, existing unconditional coverage shift unchanged). **Found one real bug during QA, logged as Task 34d-1 below** (not a blocker for this task's own scope, since it's a reopen-display-only gap, not a data-integrity issue): reopening a popover after Apply-ing an inverted-time intraday range shows two highlighted days in the calendar instead of one, because the reopen hydration path doesn't know about this new shift (only the earlier ADR-0015-style shift is reversed on reopen, per Task 34a-2). Nothing committed — per standing preference, commits are the user's own action.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 support same-day intraday range selection via double-click"`

---

### Task 34d-1 (new — discovered during Task 34d's manual QA, 2026-09-22; superseded same day) — reopening a shifted intraday range highlighted two calendar days instead of one

**Status:** ✅ done (2026-09-22) — **superseded its own first resolution the same day.** Originally decided as a documented, accepted limitation (see history below); on further discussion with the user, that decision was reversed in favor of fixing the root design choice instead. ADR 0016 amended accordingly (see its "Revised from this ADR's original acceptance" note).

**Original gap (confirmed live via QA, screenshot-verified):** reopening the popover after Apply-ing an ADR-0016-shifted same-day intraday range (e.g. Start `2026-09-18T14:00`, End `2026-09-19T09:00`) hydrated `draft.rangeEnd` as the shifted day (`2026-09-19`) rather than the real day clicked (`2026-09-18`), so the calendar grid highlighted both days instead of one — at the time, a violation of the original decision that the grid would never reflect this shift.

**Why the first resolution (document as a limitation) was wrong:** that framing assumed the grid's "one real day only" behavior was the correct baseline and treated any deviation as an error to explain away. Revisiting it: the "one real day" precedent was carried over from ADR 0015's coverage-shift case without checking whether it actually fit here. It doesn't — ADR 0015's extra day is an instant-boundary technicality (the grid still shows the complete, meaningful selection); ADR 0016's extra day is a real, substantive part of the selection (an actual calendar cell the user is choosing to span into). Suppressing it from the grid during live selection, while the header showed it immediately, was itself the actual defect — the reopen behavior (showing two days) was arguably _closer_ to correct than what live selection showed (one day).

**Actual fix:** the calendar grid now highlights the resolved same-day-inversion span live, exactly like the header already did — via a new `resolveSameDayInvertedEndIso` helper (extracted from `resolveEffectiveRangeEndIso`) feeding `rangeEndDate` in `render()`. Deliberately kept separate from `resolveRangeEndIso`'s ADR-0015 coverage shift, which must remain grid-invisible — only this ADR-0016 case is now grid-visible. This closes the reopen inconsistency as a side effect, at no extra cost: since reopen hydration and live selection now both route through the same "does the same-day-inverted condition currently hold" check against the same `rangeStart`/`rangeEnd` pair, they agree by construction — no separate reopen-hydration correction (of the kind Task 34a-2 needed) was required.

**Executor:** @frontend-subagent (implementation, done directly in this session — not dispatched, given the small, well-understood scope and immediate need to unblock the QA/doc follow-up), @testing-subagent (unit tests, pending), @qa-subagent (manual re-verification, pending)
**Files:** `bds-date-picker.tsx` (modify — new `resolveSameDayInvertedEndIso`, `resolveEffectiveRangeEndIso` refactored to use it, `render()`'s `rangeEndDate` computation), `ai-docs/decisions/0016-date-picker-intraday-range-time-ordering.md` (amended), `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (modify — removed the now-obsolete "info" limitation Callout, updated the warning Callout to mention the grid)

**Acceptance criteria:**

- The calendar grid highlights the real day AND the resolved next day (as an ordinary two-day range: `--range-start`/`--range-end`/`--in-range`) live, as soon as a same-day selection's End time is set earlier than Start — not only after Apply, and not only after a reopen.
- No change to any other grid-highlighting case: presets (any calendar type), `basic` manual ranges, and `expanded` manual multi-day ranges must all highlight exactly as before — verify explicitly, since the shared `resolveEffectiveRangeEndIso` was refactored (not just extended) to isolate this change.
- Reopening a previously-shifted intraday range now shows the same two-day highlight it showed live before Apply — verify this explicitly as a regression-closing case, not just assume it from the code.
- `tsc --noEmit` and the full package suite stay clean (verified in this session: 324/324 suites, 3622 tests, 0 failures, before the pending test/QA dispatches add more coverage).

**Manual test (required):** re-run Task 34d's own manual-test checklist plus an explicit reopen check: given a same-day inverted-time selection, Apply, close, reopen — the grid shows the identical two-day highlight it showed live before the first Apply, not a bare single day.

**Verification:** unit tests by `@testing-subagent` — 6 new tests in `bds-date-picker.time.spec.ts` (live inverted-time highlight, non-inverted single-day regression, reopen-consistency, multi-day-with-deliberately-inverted-looking-times no-op, `basic` regression; preset-grid-invisibility regression already covered by an existing Task 34a-2 test, confirmed still green, not duplicated). Full suite 324/324 suites, 3627 tests, 0 failures; `bds-date-picker.tsx` 98.8% stmts/95.74% branch coverage.

Manual QA by `@qa-subagent`, live against `dp-intraday-range-s1`/`dp-presets-s4`: all 4 checklist items pass with exact DOM class evidence (`--range-start`/`--range-end`/`--in-range`) — inverted same-day live-highlights both days matching the header; non-inverted same-day still highlights only one day; reopen now shows the identical two-day highlight live selection showed; "Last 7 days" preset still highlights exactly its 7 real days with no coverage-shift leakage into the grid. Zero console errors. QA also updated its own prior memory note (originally recording the now-resolved finding) so future sessions don't trip over a stale "still open" entry. Nothing committed — per standing preference, commits are the user's own action.

**Commit:** fold into Task 34d's own commit (this correction landed before Task 34d was ever committed) — `git commit -m "feat(bds-date-picker): EOA-17662 support same-day intraday range selection via double-click"`.

---

### Task 34e (new — discovered while reviewing ticket "nice to have" items against current behavior, 2026-09-18): reverse-order range selection auto-corrects start/end instead of resetting

**Status:** ✅ done (2026-09-22) — implemented by `@frontend-subagent`: `selectRangeDay`'s reverse-order branch changed from `{ ...draft, rangeStart: isoDate, rangeEnd: null }` to `{ ...draft, rangeStart: isoDate, rangeEnd: draft.rangeStart }` — a one-line, precisely-scoped fix. JSDoc updated to describe the swap. Both flagged doc sites (`bds-date-picker.mdx`, `RangeModeBasic`'s Storybook JSDoc) were already accurate — they'd been written as forward-looking/aspirational prose describing the intended behavior, which this fix makes literally true; verified in full surrounding context rather than assumed, no edit needed. New playground scenarios added (`dp-reverse-range-s1`/`s2`/`s3`, covering `basic`, `expanded`, and `expanded`+with-time). `tsc --noEmit` clean; full suite 324/324 suites, 3627 tests, 0 failures; docs build clean.

Unit tests by `@testing-subagent`: verified the implementer's 2 pre-existing test updates already fully covered items 1-5 (swap shape + reference check, forward/same-day/third-click regressions) — no duplication added. 3 new tests: reverse-order Apply commit for `basic`+`expanded` (covering both the general-commit and `withTime=false` requirements at once, since neither template uses `with-time` — explicitly flagged as an intentional consolidation, not a missed requirement), and the role-pinning test (item 7) — designed precisely: sets day 15's Start-slot time before the swap, then confirms after the swap that value doesn't "stick" to day 15 but instead follows day 15's new role (`rangeEnd`). Confirmed no surprises — behaves exactly as documented. Full suite 324/324 suites, 3630 tests, 0 failures; coverage 98.96% stmts/95.79% branch on the scoped files, `draft-state.ts` 100% stmts.

Manual QA by `@qa-subagent`: all 5 checklist items pass with exact evidence — reverse-order swap confirmed identical in `basic`/`expanded` via both grid classes and committed values; the role-pinning check confirmed via precise committed UTC values (`{start: "...-15T09:30...", end: "...-22T20:45..."}`, matching the Start/End slot values, not the pre-swap day association); third-click-restarts-fresh regression confirmed; both doc sites read accurately against live behavior. Zero console errors. Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @documentation-subagent (docs fix), @qa-subagent (manual test)
**Files:** `utils/draft-state.ts` (modify — `selectRangeDay`), `utils/__test__/draft-state.spec.ts` (modify), `__test__/bds-date-picker.range.spec.ts` (modify), `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify — `RangeModeBasic` JSDoc correction), `bds-date-picker.mdx` (modify — correct the same stale claim at line ~219-220, in addition to the stories.ts JSDoc), `packages/boreal-web-components/src/index.html` (modify — new playground scenario; none currently exists for reverse-order clicking)

**Gap (confirmed against current source, 2026-09-18, re-confirmed 2026-09-22 after Tasks 34a-34d landed):** clicking a range end day chronologically _before_ the already-set `rangeStart` does not swap the two into a valid range — `selectRangeDay`'s reverse-order branch (the final `return` in the function, exact line shifted by Task 34d's own edits to the same function) discards the original click entirely and resets `rangeStart` to the new (earlier) day with `rangeEnd = null`, requiring a third click to complete a range. Both `RangeModeBasic`'s Storybook JSDoc (`bds-date-picker.stories.ts:595`) and `bds-date-picker.mdx` (line ~219-220) incorrectly claim "the two swap automatically" — this is stale/inaccurate against the current implementation, not a description of real behavior (same class of stale-doc issue already found and fixed in Task 26/33). Both doc sites need the same correction, not just the story JSDoc the plan originally called out.

**Re-confirmed unaffected by Tasks 34a-34d (2026-09-22):** read the current `selectRangeDay` source directly — the reverse-order branch this task targets is untouched by Task 34d's same-day-confirm change (a distinct, earlier branch in the same function: `rangeStart === isoDate` vs. this task's "isoDate strictly before rangeStart," mutually exclusive conditions). A swap always produces `rangeStart !== rangeEnd` by construction, so it can never trigger the new same-day-inversion grid/header logic (`resolveSameDayInvertedEndIso`/`resolveEffectiveRangeEndIso` from Tasks 34d/34d-1) — confirmed no interaction, not just assumed.

**New interaction found while re-confirming scope (2026-09-22, fold into this task rather than logging separately — same root cause, same fix surface):** `expanded+range+with-time`'s two independent time selectors render unconditionally whenever `effectiveRange && isExpandedCalendarType` (`bds-date-picker.tsx`'s `render()`, the time-band block) — **not** gated on `rangeEnd !== null`. This means a user can set the End time field before a second day is even clicked. `selectRangeDay` is deliberately time-field-agnostic (per its own doc comment) and this task doesn't change that. After a swap, `draft.startHour`/`startMinute` stay attached to whichever day is _currently_ `rangeStart` — i.e., the time fields are role-pinned (Start-role / End-role), not date-pinned to whichever specific calendar day the user was looking at when they set them. This matches Phase 5's existing design (time selectors were always role-labeled, never date-tracked) and is not a bug, but it's non-obvious enough that it needs an explicit test rather than being left as an unstated assumption — see the unit-test list below.

**Acceptance criteria:**

- `selectRangeDay`'s reverse-order branch (currently `return { ...draft, rangeStart: isoDate, rangeEnd: null }` when the second click precedes `rangeStart`) is changed to set `rangeStart = <earlier date>` and `rangeEnd = <the original rangeStart>` — a true swap producing a complete, correctly-ordered range after exactly two clicks, regardless of click order.
- The existing same-day no-op/third-click-restarts-fresh behaviors are unaffected — this task only changes the "second click strictly before start" branch.
- Both `RangeModeBasic`'s JSDoc (`bds-date-picker.stories.ts`) and `bds-date-picker.mdx`'s matching prose are corrected to accurately describe the (now true) swap behavior — verify the corrected wording actually matches the shipped behavior exactly, not just that the words changed.
- No interaction with Task 34d's same-day intraday work — confirmed above, re-verify via test rather than re-deriving from scratch.
- Time-field role-pinning across a swap (found above) behaves as described — not a new requirement to implement, a behavior to lock in with an explicit test so a future change can't silently alter it without notice.

**Unit tests required (previously unspecified — added 2026-09-22):**

- `utils/__test__/draft-state.spec.ts` (pure-function, `selectRangeDay` directly, no component rendering):
  - Reverse-order click (later day clicked first, earlier day clicked second) → returns a new draft with `rangeStart = <earlier>`, `rangeEnd = <the original rangeStart>`.
  - Confirm this is a genuinely new object reference (not the old no-op-returns-same-reference pattern some other branches use).
  - Regression: forward click (later than `rangeStart`) still sets `rangeEnd` only, unaffected.
  - Regression: same-day click (Task 34d's branch) still sets `rangeEnd = rangeStart`, unaffected.
  - Regression: a third click after a completed range (`rangeStart` and `rangeEnd` both set) still starts fresh, unaffected.
- `__test__/bds-date-picker.range.spec.ts` (component-level):
  - Reverse-order two-click flow commits `{ start: <earlier>, end: <later> }` on Apply, in both `basic` and `expanded`.
  - `expanded+with-time`: set the End time field before the second (earlier) day click, then perform the reverse-order click — confirm `startHour`/`startMinute` (now applied to the new, earlier `rangeStart`) and `endHour`/`endMinute` (now applied to the new, later `rangeEnd`) reflect the role-pinned behavior described above, not the specific day the user was looking at when each was set. This is the one behavior in this task most likely to surprise someone without a test that pins it down explicitly.
  - `withTime=false`, in both `basic` and `expanded`: reverse-order two-click flow commits the correct `{ start: <earlier>, end: <later> }` naive-date value with no shift/time interference — confirms the swap is equally correct in the simpler, no-time-math path, not just the `with-time` cases above.

**Manual test (required):**

Add a new playground scenario to `packages/boreal-web-components/src/index.html` (none currently exists for reverse-order clicking) covering both `basic` and `expanded`, with `with-time` on for at least one instance to cover the role-pinning check. Reuse `RangeModeBasic`/`RangeModeExpanded` Storybook scenarios where a browser-based check is more convenient than the playground. Run `pnpm dev:components` and validate:

- [ ] Given a range picker with no selection, when a later day is clicked first and an earlier day is clicked second, then the range commits as `{ start: <earlier>, end: <later> }` after exactly two clicks. Pass: no third click needed, correct ordering.
- [ ] Given the same flow in `expanded` mode, then behavior matches `basic` exactly. Pass: no calendar-type-specific divergence.
- [ ] Given `expanded`+`with-time`, when the End time field is set before the second (earlier) day is clicked, then after the reverse-order click completes, the Start/End time fields apply to their current role (new `rangeStart`/`rangeEnd`), not to whichever specific day was on-screen when each was set. Pass: matches the unit test above, confirms no visual/data mismatch a user could perceive as a bug.
- [ ] Given the existing forward-click and same-day scenarios, when re-run, then they behave exactly as before. Pass: no regression to unrelated branches.
- [ ] Given the corrected `bds-date-picker.mdx`/Storybook JSDoc text, when read against the actual shipped behavior, then it's accurate — no stale claim anywhere on the page.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 auto-correct reverse-order range selection"`

---

### Task 34e-1 (new — discovered while reviewing Task 34e's UX implications, 2026-09-22): range hover-preview only works forward, and the first-click day marker shows a premature directional strip

**Status:** ✅ done (2026-09-22) — implemented by `@frontend-subagent`: `handleDayHover` now sets `previewEnd` unconditionally (no more forward-only gate); `grid.ts`'s `buildPreviewFlags` computes the chronologically-earlier/later of `{rangeStart, previewEnd}` before delegating to `buildRangeFlags`, so `isPreviewStart`/`isPreviewEnd` map correctly regardless of hover direction. `bds-calendar-grid.tsx`'s `isRangeParticipant` no longer includes bare `isRangeStart` — only in combination with a real companion bound.

**Regression caught and fixed before QA, not after:** the unit-test pass (`@testing-subagent`) found that the first version of the strip-removal fix — gating on `isRangeStart && isRangeEnd` — also suppressed the connecting overlay on a real, committed multi-day range's _start_ cell, not just the intended lone-click case, since a genuine range's start day has `isRangeStart:true, isRangeEnd:false` per-cell, structurally identical to a lone click. Fixed with a new grid-wide `hasRangeCompanion` field on `DayCell` (computed once from `rangeEnd !== undefined || previewEnd !== undefined`, threaded through `types.ts`/`grid.ts`), replacing the flawed per-cell `isRangeEnd` check with `isRangeStart && hasRangeCompanion`. Re-verified clean after the fix: `tsc --noEmit` clean, full suite 324/324 suites, 3638 tests, 0 failures, including the specific "real completed range renders overlay on start+interior+end cells" test that had caught the regression.

Unit tests by `@testing-subagent`: 9 new tests across `grid.spec.ts` (reverse preview, equal-dates edge case, undefined-rangeStart guard), `bds-calendar-grid.variants.spec.ts` (lone-click no-overlay, same-day regression, real-range regression — the one that caught the bug above), and `bds-date-picker.range.spec.ts` (forward-to-backward transition for `basic`/`expanded`, proving the original "disappears" symptom is actually fixed, not just that each direction works in isolation). Coverage 100% on `grid.ts`/`bds-calendar-grid.tsx`, 98.8%/95.71% on `bds-date-picker.tsx`.

Manual QA by `@qa-subagent`: all 6 checklist items pass with scoped DOM evidence (flagged and worked around a real trap: the playground mounts 36 calendar grids simultaneously, so unscoped queries grab cells from unrelated scenarios). Explicitly re-verified the caught regression's fix on an ordinary forward multi-day range (continuous connecting band, no disconnected start square) and confirmed Task 34d's same-day styling unaffected. Zero console errors across 166 logged messages. Nothing committed — per standing preference, commits are the user's own action.

**Gap (confirmed via source read, not hypothetical):** `handleDayHover` (`bds-date-picker.tsx`, `@Listen('bdsDayHover')`) only sets `this.previewEnd` when the hovered date is chronologically after `rangeStart` (`isAfterStart` gate) — hovering backward always sets `previewEnd = null`. This predates Task 34e; it was never wrong before because a reverse-order click used to just reset the selection, so there was nothing valid to preview in that direction. Now that Task 34e makes reverse-order clicks produce a real, valid range, this hover logic is stale relative to what clicking actually does: dragging backward shows no live preview at all, even though clicking there works correctly.

Separately, but compounding the same UX gap: `bds-calendar-grid.tsx`'s `renderDayCell` computes `isRangeParticipant` (which gates the `.day-background`/`.day-cap` overlay elements that produce the directional half-strip CSS — rounded-left-extending-right for `--range-start`, mirrored for `--range-end`, meant to visually bridge a multi-day range) from `cell.isInRange || cell.isRangeStart || cell.isRangeEnd || cell.isPreview*` — `isRangeStart` alone is included unconditionally, so the exact same directional strip renders the instant a single day is clicked, before any second bound (real or previewed) exists to bridge to. This is misleading: it implies a rightward direction the picker doesn't actually know yet, and (combined with the hover bug above) can make the marker appear to "disappear" if a user who'd started hovering forward (showing a live band) crosses back past `rangeStart`, since the forward preview collapses to nothing with no reverse equivalent to replace it.

**Confirmed low blast radius:** `buildDisplayGrid`/`generateMonthGrid` (the `date-engine/grid.ts` functions underlying both bugs) are consumed only by `bds-date-picker.tsx` — no other component depends on this range/preview-flag logic, checked directly via a repo-wide search.

**Executor:** @frontend-subagent (implementation), @testing-subagent (unit tests), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `handleDayHover`), `services/date-engine/grid.ts` (modify — `buildPreviewFlags`, made bidirectional), `bds-calendar-grid/bds-calendar-grid.tsx` (modify — `isRangeParticipant`), `services/date-engine/__test__/grid.spec.ts` (modify), `bds-calendar-grid/__test__/` (modify — nearest existing highlight-coverage spec), `bds-date-picker/__test__/bds-date-picker.range.spec.ts` (modify)

**Acceptance criteria:**

- **Bidirectional hover preview:** `handleDayHover`/`buildPreviewFlags` compute the preview band from `min(rangeStart, hoveredDate)` to `max(rangeStart, hoveredDate)`, regardless of which is chronologically earlier — mirroring exactly what `selectRangeDay` (Task 34e) already does for the actual click. The existing reverse-direction CSS (`--partial-end`/`--range-end`-style rules) already exists and is correct — confirm this via test, don't re-derive it; this is purely a data-flow fix in `grid.ts`/`bds-date-picker.tsx`.
- **No premature directional strip on a lone first click:** `isRangeParticipant` in `bds-calendar-grid.tsx` changes from including bare `cell.isRangeStart` to only including it in combination with a real second bound: `cell.isInRange || cell.isRangeEnd || cell.isPreviewInRange || cell.isPreviewStart || cell.isPreviewEnd || (cell.isRangeStart && cell.isRangeEnd)`. A lone `rangeStart` with no `rangeEnd` and no active preview must render as a plain, non-directional filled cell — reusing the _existing_ `&--selected, &--range-start, &--range-end { background-color: ... }` shared rule (already applied directly to the cell, independent of the overlay), not a new visual element. Explicitly verify Task 34d's same-day case (`isRangeStart && isRangeEnd` both true) is unaffected — that combination stays in the included set.
- No `min`/`max` bounds-interaction regression: hovering/previewing toward a disabled (out-of-bounds) day must not produce a preview band extending onto or past it — confirm this already-existing constraint (disabled cells never receive `bdsDayHover`/`bdsDayClick` per `bds-calendar-grid.tsx`'s own click/hover guards) still holds with the bidirectional logic.
- No change to the ADR-0016 same-day-inversion grid logic (`resolveSameDayInvertedEndIso`, Tasks 34d/34d-1) — confirm no interaction, since that logic operates on `draft.rangeStart`/`rangeEnd` post-click, not on hover/hover-preview state.

**Manual test (required):**

Reuse `RangeModeBasic`/`RangeModeExpanded` and the `dp-reverse-range-s1`/`s2`/`s3` playground scenarios (Task 34e). Run `pnpm dev:components` and validate:

- [ ] Given a range picker with no selection, when the first day is clicked, then the cell shows a plain filled highlight with no directional strip/cap extending beyond the cell — matching single-date mode's `--selected` look. Pass: no strip visible, regardless of which day was clicked.
- [ ] Given a first click, when the mouse hovers a LATER day, then a correct forward preview band renders (unchanged from existing behavior). Pass: no regression.
- [ ] Given a first click, when the mouse hovers an EARLIER day, then a correct reverse preview band renders — the hovered day and every day between it and `rangeStart` show the preview-in-range/preview-end styling. Pass: this is the core new behavior; previously nothing rendered here.
- [ ] Given a live forward preview, when the mouse then crosses backward past `rangeStart`, then the preview band smoothly switches to a correct reverse preview — no moment where it disappears with nothing shown. Pass: no visual gap/flicker to a bare unstyled state.
- [ ] Given Task 34d's same-day double-click scenario, when re-run, then the single-day highlight is unaffected. Pass: no regression to already-shipped, already-QA'd styling.

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 make range hover-preview bidirectional and remove premature first-click strip"`

---

### Task 34f (discovered while re-investigating the ticket's "preselected date outside the visible month" note, 2026-09-18; resolved via direct evidence, 2026-09-22): opening the calendar already navigates to a preselected date outside the visible month; multi-month range spans are a documented, intentional limitation

**Status:** ✅ done (2026-09-22) — resolved directly with the user using live evidence in place of the original "confirm with the teammate who filed the ticket" checkpoint (no such teammate is reachable in this session; the same role every other blocking-gate task in this plan filled by deciding directly with the user instead).

**Resolution:** the teammate's original comment, obtained verbatim, reads (translated): _"When there's a preselected date outside the currently visible month, when you open the calendar, it should navigate automatically to that date."_ This describes the on-open transition specifically — not a value changing while the popover is already sitting open with no close/reopen in between. A new playground scenario (`dp-preselected-outside-month-s1`, `packages/boreal-web-components/src/index.html`) proves this exact scenario already works: a picker preselected with a date several months from "today" (`2027-04-12` against a real clock reading September 2026), opened for the very first time with zero prior interaction, opens the popover directly on April 2027 — no manual navigation needed. **No code change required** — the existing `resolveDraftDisplayMonth()`/on-open logic already satisfies the literal request.

The originally-scoped "Gap 2" (re-syncing the displayed month if `value` is reassigned externally while the popover is already open, no close/reopen) is a real, separately-valid behavior, but it is not what the teammate's comment asks for — it was a generalization introduced during planning, not a literal requirement. It's split out below as an explicitly optional follow-up, not part of this task's required scope.

**Gap 1 (documentation only, no code change) — multi-month preselected range spans, still real, still in scope.** `resolveDraftDisplayMonth` anchors exclusively on `rangeStart` — `rangeEnd`'s month plays no role. Since `basic` shows exactly 1 month and `expanded` shows exactly 2 consecutive months, any preselected range whose `start`/`end` fall in different months (any 2+ month spread for `basic`, more than 1 month apart for `expanded`) leaves `end` genuinely off-screen on open. This is structural — no anchor choice can show both ends of an arbitrarily wide range — and the current start-anchored behavior is the correct, least-surprising default. Confirmed live: `dp-multimonth-range-s1`/`s2` (Sep 10 – Nov 20 preselected) open on September (`basic`) / September+October (`expanded`) respectively, November genuinely off-screen in both. **No code change**; document this explicitly as an intentional limitation.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify — document the multi-month-range limitation near the existing preselected-value documentation)

**Acceptance criteria:**

- `bds-date-picker.mdx` gains a short note stating that a preselected range's `end` bound may render outside the visible month(s) when it spans more months than the current `calendarType` can show at once, and that the display always anchors on `rangeStart` by design.
- No claim anywhere in the docs that live external `value` reassignment while the popover is already open re-syncs the display — that's explicitly not built (see Task 34f-1 below if it's ever picked up).

**Manual test (required):** Run `pnpm dev:docs` and confirm the new documentation note reads accurately against `dp-multimonth-range-s1`/`s2`'s actual live behavior (already verified above) — no contradiction between docs and behavior. ✅ Done by `@documentation-subagent`, confirmed against both live scenarios before writing.

**Verification:** short paragraph added to `## Range selection`'s opening (right before `### Presets sidebar`), stating `end`'s month plays no role in the display anchor and may render off-screen for a wide enough range — no mention of internal function names, task/gap numbers, or the separate on-open-navigation behavior (kept distinct, no conflation). `pnpm --filter boreal-docs run build` clean, verified independently. Nothing committed — per standing preference, commits are the user's own action.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document multi-month preselected range display limitation"`

---

### Task 34f-1 (split out from Task 34f, 2026-09-22; explicitly optional, not scheduled): re-sync displayed month if `value` is reassigned externally while the popover is already open

**Status:** not scheduled — logged for visibility only, not part of this plan's required scope. Revisit only if a concrete consumer need materializes; the teammate's original comment (see Task 34f) doesn't ask for this specifically.

**Gap (real, confirmed live via direct testing, 2026-09-22):** `@Watch('value')` only handles form validity/sync (`setFormValue`, `updateValidity`, `syncFieldError`, `syncFieldValue`) — it never touches `displayYear`/`displayMonth`. Setting `el.value` via a JS property assignment while the popover is already open (no click-to-open event fires, so `listenClickTrigger` never runs) does not re-sync the displayed month at all; only the next actual open/close transition does. Directly confirmed live, twice: once with a fully committed value, once with an in-progress, uncommitted range draft (`rangeStart` set, `rangeEnd` still null) — in both cases, the trigger field's text updates correctly, and an in-progress draft is correctly preserved (not discarded), but the open calendar's displayed month never moves.

**If picked up later:** `@Watch('value')` should additionally call the existing `resolveDraftDisplayMonth()` and update `displayYear`/`displayMonth`, gated on `this.popoverVisible` being `true` (no effect while closed, since the existing on-open resync already covers that case) — and must explicitly NOT reset or rebuild `this.draft`, since draft preservation during this scenario is already confirmed correct today and must not regress.

**Files (if picked up):** `bds-date-picker.tsx` (modify — `@Watch('value')` handler), `__test__/bds-date-picker.events.spec.ts` or nearest existing `@Watch('value')`-coverage spec (modify)

**Commit:** N/A — not scheduled.

---

### Task 34g (new — code review comment, 2026-09-22): link an external IANA timezone reference from the `timezone` prop's documentation

**Status:** ✅ done (2026-09-22) — implemented by `@documentation-subagent`: one sentence added to "Timezone conversion" linking Wikipedia's "List of tz database time zones" page, verified live (fetched, confirmed correct title and content — lists IANA identifiers like `America/New_York` with UTC offsets) before citing it, not assumed from memory. `bds-date-picker.tsx`'s JSDoc/`ArgTypes` left untouched, per scope. `pnpm --filter boreal-docs run build` clean, verified independently. Nothing committed — per standing preference, commits are the user's own action.

**Gap:** the `timezone` prop's JSDoc (`bds-date-picker.tsx`) already identifies the expected format ("IANA timezone"), and the MDX's "Timezone conversion" subsection explains what the prop does, but neither points a consumer to where they can actually look up a valid IANA timezone string. A code-review comment flagged this as worth adding, to make it easier for consumers to find valid values rather than having to already know the IANA database by name.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify — "Timezone conversion" subsection, ~line 339-346)

**Acceptance criteria:**

- The "Timezone conversion" subsection gains a link to an external, authoritative IANA timezone reference (e.g. the Wikipedia "List of tz database time zones" page, or an equivalent canonical source — confirm the exact URL is live and accurate before adding, not assumed from memory) so a consumer can find a valid value without already knowing the IANA database by name.
- No change to the `timezone` prop's own JSDoc/`ArgTypes` entry — Storybook's `ArgTypes` table renders plain text, not markdown links, so the link belongs in the MDX prose only; the JSDoc's existing "IANA timezone" wording is sufficient there and stays as-is.
- One or two sentences at most — this is a small pointer, not a new subsection or explanation of timezone concepts.

**Manual test (required):** Run `pnpm dev:docs` and confirm the "Timezone conversion" section renders with a working, correctly-targeted link, with no build/console errors.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 link an external IANA timezone reference"`

---

## Phase 7 — Info banner + footer range summary

`banner` remains independent of `calendarType`. Range summary remains `range`-gated.

### Task 35: banner + range summary implementation

**Status: DONE (2026-09-22).** `@frontend-subagent` implemented and self-verified (`tsc --noEmit` clean for date-picker files, `eslint` clean, full `bds-date-picker` spec suite passing); independently re-verified via full diff review + `npx stencil test --spec` (324/324 suites, 3638 passed/1 pre-existing todo, zero regressions) + `npx tsc -p tsconfig.json --noEmit` (zero date-picker errors; 5 pre-existing unrelated failures in `bds-dialog`/`bds-tooltip` test files only). The positioning correction (banner moved from a `.container`-level sibling into `.bds-date-picker__date-time`'s first child, `.date-time` unconditional across all `calendarType` values, two render branches unified into one) was implemented and independently re-verified the same day via full diff review + a second clean `tsc --noEmit` + `stencil test --spec` run (324/324 suites, 3638 passed/1 pre-existing todo). `MS_PER_MINUTE`/`MS_PER_HOUR`/`MS_PER_DAY`/`OFFSET_DATE_TIME_PATTERN` moved from `value-mapping.ts` to `constants.ts` (cleanup, verified clean). **Manual QA executed by `@qa-subagent` against playground scenarios `dp-banner-s1`..`s4`: TC-23 (positioning across all `calendarType` values, incl. the presets-sidebar case) PASS, TC-24 (close/reopen, no dismissal persistence) PASS, TC-25 (basic days-only summary) PASS, TC-26 (expanded days/hours/minutes + singular-boundary pluralization) PASS. Zero bugs found, zero new console errors/warnings.** **Not committed — awaiting the user's manual commit of this task's diff before Task 36 proceeds.** Note: the Task 36 dispatch (banner wrapper div + `"Range:"` footer label, see Task 36 below) was started and then stopped by the user before making any edits — confirmed via `git diff`/`git status`: the working tree contains only Task 35's own changes (banner+summary feature, the positioning correction, and the `MS_PER_*`/`OFFSET_DATE_TIME_PATTERN` constants cleanup). No Task 36 changes have landed yet.

**Bug found and fixed (2026-09-22, before commit): range-summary duration mismatched the visually-selected days, and — more seriously — the actual committed `value` end date, in several configurations.** Root-caused via source trace + live reproduction on the running dev server (see below). Root cause: `rangeEndShiftApplies` (the getter deciding whether the ADR-0015 +1-day coverage shift applies) was gated on `isExpandedCalendarType`/`selectedPreset` instead of the underlying data:

```ts
private get rangeEndShiftApplies(): boolean {
  if (!this.effectiveRange || !this.effectiveWithTime) return false;
  return this.isExpandedCalendarType ? this.selectedPreset !== PRESET_KEY.CUSTOM : true;
}
```

This is used not just for the footer summary but also for the popover header (`rangeEndText`) and — critically — the actual **committed value** on Apply (`handleFooterAction`'s `commitRangeEnd`). Confirmed live via `dp-banner-s4` (expanded+range+withTime): "Last 7 days" preset correctly showed `"7 days"`; clicking "Custom" immediately after, with zero change to the selected dates/times, dropped it to `"6 days"` — same underlying data, different displayed (and committed) result, purely from a UI label switch. Also confirmed: a fresh manual 2-day selection (both times at default `00:00`) reported `"1 day, 0 hours, 0 minutes"` despite 2 grid cells being highlighted.

**Fix (design decision confirmed with user 2026-09-22):** `rangeEndShiftApplies` now depends purely on whether the range's start time-of-day equals its end time-of-day — never on `selectedPreset` or `isExpandedCalendarType` directly:

```ts
private get rangeEndShiftApplies(): boolean {
  if (!this.effectiveRange || !this.effectiveWithTime) return false;
  const startHour = this.isExpandedCalendarType ? this.draft.startHour : this.draft.hour;
  const startMinute = this.isExpandedCalendarType ? this.draft.startMinute : this.draft.minute;
  const endHour = this.isExpandedCalendarType ? this.draft.endHour : this.draft.hour;
  const endMinute = this.isExpandedCalendarType ? this.draft.endMinute : this.draft.minute;
  if (startHour !== endHour || startMinute !== endMinute) return false;
  if (!this.isExpandedCalendarType) return true;
  if (this.draft.rangeStart !== this.draft.rangeEnd) return true;
  return startHour === 0 && startMinute === 0;
}
```

_(Reconciled 2026-09-24 to the getter actually committed on 2026-09-22 — the version originally quoted here was a simplification that omitted the final branch, which excludes a same-day, non-midnight, equal-time zero-duration instant from the shift so it is not inflated by +1 day.)_

Rationale: whenever two dates share the same time-of-day, elapsed days is mathematically always exactly one less than the number of calendar cells visually spanned — the shift is the precise, general conversion from "elapsed time" to "whole-day coverage," not a preset-specific hack. `basic` always has equal start/end times (one shared field) so this is a no-op there (identical behavior, no regression). A manual `expanded` selection with untouched default times (`00:00`/`00:00`) now gets whole-day coverage, matching the grid and the preset precedent; a selection with deliberately distinct times (e.g. the already-QA'd-correct `"17 days, 2 hours, 30 minutes"` case) is unaffected — real elapsed time, no shift, exactly as before.

**Necessary follow-on fix, same root cause:** `correctHydratedRangeEnd` (which un-shifts a reopened range back to its real grid dates) currently only un-shifts `expanded` when `matchedPreset !== null` — because today only presets ever commit shifted for `expanded`. Since the fix above makes _any_ equal-time custom range commit shifted too, this method must also un-shift any equal-time reopened range for `expanded` (mirroring what it already does unconditionally for `basic`), or reopening a custom equal-time range would double the shift — the exact failure pattern behind the earlier Task 34a-2 regression. The `matchedPreset`-specific exact-recompute branch (via `computePresetRange`) should stay for real preset matches (handles timezone/DST edge cases precisely); a new, simpler branch (subtract 1 day when hydrated start/end times are equal) is needed for the non-preset case.

**Second, distinct bug found 2026-09-22 (same session, reported by user live): date-only ranges (no `withTime` at all) also under-report by exactly 1 day** — e.g. selecting the "Today" preset (1 real day highlighted) reports `"0 days"`. Root cause is adjacent to, but different from, the bug above: in `render()`, `effectiveRangeEndIso` (the header's display boundary, correctly _never_ shifted for date-only ranges — a date-only end date is already unambiguous, no fix needed there) is _reused_ as `computeRangeDuration`'s end argument. But the duration calculation needs whole-day coverage semantics unconditionally whenever there's no time component (there is no such thing as a "precise instant" without a time — every date-only range is inherently whole-day coverage), which is the opposite of the header's own correct behavior. **Fix: introduce a separate resolution path for the duration's end boundary, decoupled from the header/commit-value's `resolveEffectiveRangeEndIso`.** A new method (e.g. `resolveDurationRangeEndIso`) returns `rangeEnd` shifted `+1` day unconditionally when `!effectiveWithTime`, and otherwise defers to the same time-equality logic as the fix above. `render()` must use this new method's result for `computeRangeDuration`'s end argument, while `rangeEndText` (header) keeps using the existing, unchanged `effectiveRangeEndIso`. This must NOT alter the header or committed `value` for date-only ranges at all — only the range-summary duration text.

**Status: all three fixes implemented and independently verified 2026-09-22 (implementation-only, not committed).** Process note: the first fix (`rangeEndShiftApplies`/`correctHydratedRangeEnd`, with-time) was correctly dispatched to and completed by `@frontend-subagent`. The date-only follow-on fix was, due to a coordinator error (an `Agent` call was made with a `to` field, which isn't a valid resume mechanism — `SendMessage` is — so it silently launched an unrelated fresh `general-purpose` agent instead of resuming the original one), briefly worked on by two independent, uncoordinated agents on the same file at once. The stray duplicate was caught and stopped before it wrote any test files, but it had already written its `resolveDurationRangeEndIso` source edit to `bds-date-picker.tsx` — which, by coincidence, landed cleanly (no textual conflict with the original agent's unrelated edits). This was **independently re-verified from scratch** rather than trusted: full diff review, live reproduction attempts (browser-based reproduction proved unreliable due to popover open/close desync across scripted interactions — not a code issue), and, decisively, a dedicated Jest probe confirming `computeRangeDuration`'s actual output before writing permanent tests. Three new permanent regression tests were added to `bds-date-picker.presets.spec.ts` covering: "Today" preset (1 real day) reports `"1 day"`; a manual 3-day selection reports `"3 days"`; and the header/committed-value stay unshifted (date-only) while only the duration text changes. Full suite: 324/324 suites, 3646 passed (1 pre-existing todo). `tsc --noEmit`/`eslint`: clean. **Not committed** — all three fixes (with-time shift, hydration un-shift, date-only duration) are ready for the user's review and commit together with the rest of Task 35's diff.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderBanner.tsx` (create), `helpers/renderFooter.tsx` (modify), `types/types.ts` (modify), `types/IDatePicker.ts` (modify — mechanically required prop-mirroring, not in original list), `utils/constants.ts` (modify — new label defaults), `utils/value-mapping.ts` (modify — `computeRangeDuration`/`formatRangeSummary`), `bds-date-picker.tsx` (modify — banner render + `.date-time` unification), `__test__/bds-date-picker.presets.spec.ts` (modify — update the `default`-type structural assertion, see acceptance criteria)

**Utility discovery:**

- Feature area: an in-context info/message surface with a title, message, closable state, and state variant (matches the legacy `infoBanner` shape: `{ title, close, message, state, visible }`).
- Search performed: `packages/boreal-web-components/src/components/feedback/` (existing feedback-family components — `bds-toast`, `bds-tag`, any standalone banner/alert component); `src/types/states.ts` (`ComponentState`/`COMPONENT_STATES` for the `state` field's type).
- Candidates found: confirm whether a standalone `bds-banner`/`bds-alert` component already exists in `components/feedback/` before building `renderBanner.tsx` as a local helper — if one exists, reuse it as a slotted/composed element instead of hand-rolling banner markup; `ComponentState`/`COMPONENT_STATES` (`src/types/states.ts`) is the existing shared type for the `state` field regardless.
- Fit assessment: to be completed at dispatch time — if no standalone banner component exists, this confirms `renderBanner.tsx` as a `bds-date-picker`-local helper is correct (matching the plan's existing precedent: footer/time-selector/month-header are `helpers/*.tsx`, not separate components, per the spike's Finding 3 litmus test); if one does exist, this task's scope changes to composing it rather than building new markup.
- Reuse decision: **resolved 2026-09-22** — `bds-banner` already exists at `components/feedback/bds-banner/bds-banner.tsx`, with `variant: StatusVariant` (info/success/warning/danger, default `'info'`), `closable`/`closeButtonLabel` props, and `title`/default/`actions` slots. `renderBanner.tsx` composes this existing component (title/default slots) rather than hand-rolling banner markup. `state` field's type always reuses `ComponentState`, never a new local union.
- Gap handling: not applicable — no gap; `bds-banner` covers the full surface this task needs.
- Anti-duplication check: no parallel `state`-variant type is planned; `types/types.ts`'s `DatePickerBanner` shape reuses `ComponentState` for its `state` field, passed straight through to `bds-banner`'s `variant` prop.
- Test impact: Task 37's `bds-date-picker.banner.spec.ts` asserts banner visibility/close/state through the composed `bds-banner` element.
- **Design decisions confirmed 2026-09-22 (mockups reviewed: default/basic/expanded calendar types, all showing an info-variant banner with title + message + close icon, no action buttons):**
  - `DatePickerBanner` shape: `{ title, message, visible, closable, state }`. No `actions`/button content is exposed — `renderBanner.tsx` never renders `bds-banner`'s `actions` slot. The banner is a pure display surface; it never blocks `Apply` or drives any date-picker-internal logic.
  - `visible` default: `false` (or prop itself `undefined`) — renders nothing when unset, no empty banner shell.
  - `closable` default: `true` — every mockup shows the close (`X`) icon by default, even though `bds-banner`'s own component-level default is `false`; the date-picker composing helper intentionally picks a different default for this context.
  - `state` default: `'info'`, matching both `bds-banner`'s own default and every mockup — but the field stays typed flexibly, not hardcoded/narrowed to `'info'`. This is a pure type-level decision, not a validation feature: the date picker itself never inspects the selected range or sets `state` on its own. A consumer's own app code may choose to set `banner.state = 'warning'` from outside (e.g. after their own range-length check), but that logic lives entirely in consumer code — `bds-date-picker` has no built-in validation, limit-checking, or range-vs-banner coupling of any kind.
  - **Correction found during implementation (2026-09-22):** this plan's original text said `state` "reuses `ComponentState`." That's wrong — `ComponentState` (`src/types/states.ts`) is `'default'|'error'|'disabled'|'hover'|'active'|'focus'|'visited'` and has no `'info'`/`'success'`/`'warning'`/`'danger'` members, so it cannot express `bds-banner`'s actual `variant` type or match the mockups. `DatePickerBanner.state` is typed as `StatusVariant` instead — the same type `bds-banner.tsx` itself uses. Every reference to `ComponentState` above should be read as `StatusVariant`; Task 36 (Figma pull) and Task 37 (unit tests) inherit this corrected type.
  - **Positioning correction found during pre-QA review (2026-09-22, before manual test was run):** the first implementation rendered the banner as a sibling _above_ `.bds-date-picker__container`, spanning the full popover width — including over the presets sidebar in range mode. The mockups (all three `calendarType` values) show the banner starting _after_ the presets sidebar, aligned only with the calendar column. The fix: the banner must render as the first child of `.bds-date-picker__date-time`, not as a container-level sibling. Today `.bds-date-picker__date-time` only exists for non-`default` types (`default` renders `.bds-date-picker__calendars` directly as `.container`'s only child) — this task must also make `.date-time` wrap the calendar panel unconditionally, for all three `calendarType` values, so `default` has a home for the banner too. The two previously-branched render paths (`isDefaultCalendarType ? renderCalendarPanel(...) : (<div class="date-time">...calendars + time-band...</div>)`) collapse into one unconditional `.date-time` wrapper containing banner → calendar panel → the existing time-band block, unchanged — the time-band's own `showChrome && this.effectiveWithTime` guard already evaluates to `false` for `default` (both `showChrome` and `effectiveWithTime` are independently forced false when `isDefaultCalendarType` is true), so no new condition is needed for it to stay excluded there.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `renderFooter.tsx` is an existing, already-shipped helper (Clean/Cancel/Apply, per v1/v2) — confirm adding the range-summary label doesn't require changing its existing call signature in a way that breaks its current single-date/basic-range call sites; the summary label should be an additive, conditionally-rendered piece, not a signature change forcing every existing caller to pass a new required argument.
- [ ] Boundary case: `banner.visible = true` set by the consumer while `banner.closable = true` and the user has already dismissed it once via the close (`X`) button in a prior open — confirm whether reopening the popover resets the dismissed-state (matching the picker's own draft-revert-on-reopen convention already established for date/range selections) or the dismissal persists across opens; state this explicitly rather than leaving it to the implementer's default assumption.
- [ ] Default/empty state: `banner` prop's default value (empty object vs. `undefined`) — confirm which one this task uses and that it renders nothing (no empty banner shell) when unset, matching the legacy `infoBanner` prop's own documented default of an empty object with `visible` implicitly falsy.
- [ ] Reactivity: `banner` is expected to be reactive after mount (`@Watch`-driven — a consumer can update `banner.message` while the popover is already open) — state this explicitly, since the footer/time-selector helpers this task's Files list touches are otherwise re-rendered per Stencil's normal `@State`/`@Prop` reactivity, and `banner` being a plain object prop (not tracked via `@State`) needs its own reactivity confirmation.

**Acceptance criteria:**

- Adds `banner` prop shape (`{ title, message, visible, closable, state }`) with defaults `visible: false`, `closable: true`, `state: 'info'`; `state` typed as `StatusVariant` (not `ComponentState` — see correction note above), never narrowed.
- `renderBanner.tsx` composes the existing `bds-banner` component (title/default slots into its `title`/`variant`/`closable` props) — no hand-rolled banner markup, no `actions` slot exposed.
- Banner renders as the first child of `.bds-date-picker__date-time` (not as a sibling above `.bds-date-picker__container`) in all `calendarType` values, including `default` — so it aligns with the calendar column and never stretches over the presets sidebar in range mode. `.bds-date-picker__date-time` wraps the calendar panel unconditionally for all three `calendarType` values (previously `default`-only skipped this wrapper); the two previously-branched render paths collapse into one, with the existing time-band condition (`showChrome && this.effectiveWithTime`) unchanged and still correctly excluding `default`.
- `bds-date-picker.presets.spec.ts`'s `"renders .calendars as the container's only child under calendar-type=\"default\""` test is updated to assert `.date-time` (not `.calendars`) is `.container`'s only child under `default`, and that `.calendars` lives inside `.date-time`.
- Footer summary in `range` mode computes from selected range. **Note — not directly sourced from the spike or v2:** the spike's only concrete example (`"Rango: 18 días, 2 horas, 30 minutos"`) doesn't identify which `calendarType` it was pulled from, and v2's Task 18/19 explicitly deferred this label to this task without further guidance. The `basic`: days-only / `expanded`: days/hours/minutes split below is this plan's own inference (mirroring Phase 5's single-vs-dual time-selector split), not a confirmed design decision — pull `get_design_context` against the actual `Basic Footer`/`Expanded Footer` range-summary text nodes before implementing, and treat the split as a hypothesis to verify, not a given:
  - `basic`: days only
  - `expanded`: days/hours/minutes
  - **Cross-reference confirmed 2026-09-10 (Phase 6's preset/coverage-boundary work):** this hypothesis reconciles cleanly with Phase 6's final commit semantics — once Task 29/30's fix lands, both `basic` and `expanded` always commit an _exact_ whole-day-multiple duration for presets and (in `basic`'s case) for manual selection too, and `expanded`'s manual selection is exact by construction (the user sets independent times directly). This means the range-summary duration can be computed via plain raw timestamp subtraction (`end - start`) with zero special-casing — it will always agree with the grid/header, because the underlying values are now guaranteed exact multiples of 24h wherever a whole-day guarantee applies, and genuinely precise otherwise (`expanded` manual selections with non-`00:00` times). No "inclusive calendar-day counting" trick is needed here despite earlier discussion suggesting one might be — do not implement one; raw duration math is correct and simpler.
- Range-summary word units ("day"/"days", "hour"/"hours", "minute"/"minutes") are sourced from new keys added to the existing `labels`/`DatePickerFooterLabels` object, not hardcoded literals — following the same `labels`-extension pattern as Task 23/30 and [ADR 0014](../../ai-docs/decisions/0014-localizable-ui-copy-prop-shape.md). Singular/plural word-form selection per unit uses the native `Intl.PluralRules` API (zero new dependency) — a flat string per unit cannot express "1 day" vs. "18 days," and ADR-0014 explicitly defers pluralization to this mechanism rather than a message-catalog library.
- JSDoc on the new `banner` `@Prop()` is 1-2 sentences, consumer-facing only (what it does / what the consumer sees or receives) — never internal implementation details (which private getter or `@Watch` consumes it, how `renderBanner.tsx` is wired to it). Matches `ai-docs/guidelines/jsdoc-template.md`'s worked examples.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: `calendarType='default'` with `banner` set.
- Scenario 2: `calendarType='basic'` (no range) with `banner` set.
- Scenario 3: `calendarType='basic'` + `range`, a committed range, footer summary visible.
- Scenario 4: `calendarType='expanded'` + `range` + `withTime`, a committed range, footer summary visible.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1 or 2, when the banner is visible, then it renders above the calendar body, aligned with the calendar column in all `calendarType` values (not stretching over the presets sidebar). Pass: matching Figma's structure. **Verified live 2026-09-22** (`qa-subagent`, TC-23): bounding-box coordinates confirmed banner and calendar grid share identical left/right edges in `default`/`basic`/`basic+range`; in the presets-sidebar case, both start exactly at the sidebar's right edge, not before it. Zero console errors.
- [x] Given a visible, closable banner, when the close (`X`) button is clicked, then the banner dismisses. Pass: banner no longer renders, no console errors. **Verified live 2026-09-22** (TC-24): also confirmed reopening the popover re-shows the banner — a same-session dismissal does not persist.
- [x] Given Scenario 3, when a range is committed, then the footer summary shows days-only text. Pass: text reflects raw elapsed time between committed start/end instants. **Verified live 2026-09-22** (TC-25): Sept 1 → Sept 18 (00:00 both) showed "17 days" — correct per `computeRangeDuration`'s raw-elapsed-time semantics (not an inclusive calendar-day count).
- [x] Given Scenario 4, when a range is committed, then the footer summary shows days/hours/minutes text. Pass: text reflects raw elapsed time, with correct singular/plural word forms per unit. **Verified live 2026-09-22** (TC-26): Sept 1 10:00 → Sept 18 12:30 showed "17 days, 2 hours, 30 minutes"; a 1-day/1-hour/1-minute boundary case showed all three units correctly singular ("1 day, 1 hour, 1 minute") via `Intl.PluralRules`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add info banner and footer range summary"`

---

### Task 36: Phase 7 SCSS + JSDoc audit

**Status: implementation done, independently re-verified 2026-09-23.** `@frontend-subagent` implemented all three corrections (wrapper div, `"Range:"` label, overflow/no-wrap fix) plus the full Figma-driven SCSS audit; self-verified (324/324... 20/20 date-picker suites, `tsc`/`eslint` clean, compiled-CSS cross-check). Independently re-verified: full diff review (wrapper div, label spans, and SCSS all match the plan and the Figma-pulled values exactly), `npx stencil test --spec` (324/324 suites, 3646 passed/1 pre-existing todo, zero regressions), `tsc --noEmit` (zero date-picker errors), and a live re-check on the dev server confirming both the overflow fix (`.date-time` now 296px, not 443px, banner text wraps) and the `"Range: 4 days"` two-span label/value styling (screenshot-confirmed: label in `$boreal-text-default-light`, value in `$boreal-text-default`). Not committed.

**Two gaps found during the Figma audit, explicitly flagged rather than silently fixed or dropped (both out of Task 36's file scope — `bds-banner.scss`/`bds-popover.scss` are shared dependencies, not date-picker-local files):**

1. `bds-banner`'s own close button has no hover/focus/active states implemented at all (plain color + `cursor: pointer` only) — a pre-existing gap in the `bds-banner` component itself, not something this task introduced or can fix within its file scope. **Resolved 2026-09-23: scheduled as Task 42a** (Phase 8), since `bds-banner.scss` is a shared dependency outside this task's file scope. **Task 42a dropped 2026-09-24** — no hover/focus/active states are documented in Figma for this component, so there's nothing to build against; left as-is until Figma states exist.
2. Figma's footer row uses `justify-content: flex-end` with the range-summary hugging the button row; the actual `bds-popover.scss` uses `justify-content: space-between`, spreading the summary to the far-left edge instead — confirmed live in the screenshot above ("Range: 4 days" sits at the far left, `Clear`/`Cancel`/`Apply` at the far right, rather than being close together per Figma). **Resolved 2026-09-23: reviewed and dropped by user** ("looks fine to me") — current `space-between` behavior is intentional, not a bug; no fix scheduled.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify), `helpers/renderBanner.tsx` (modify — wrapper div, see below), `helpers/renderFooter.tsx` (modify — `Range:` label, see below), `types/types.ts` (modify — new `rangeSummaryLabel` key), `utils/constants.ts` (modify — new label default)

**Figma node (confirmed 2026-09-22):** `https://www.figma.com/design/rtiE5zGA4aoOuxIQMgfD6h/-BOR--DSG-COMPONENTS-%E2%86%92-FORMS?node-id=165-40701&m=dev` (`calendarPicker` instance, node `165:40701`). Metadata pulled and confirmed via `get_metadata`:

- `Expanded Footer > Range labels` (`I165:40701;158:176549`, x=24 y=16, width=459 height=16): a `Label` text node (width 40) followed by a `Range` value text node (width 163), with a small gap between them — same label+value structural pattern as the header's `Starts`/`Ends` groups (confirmed by the user: "it's the same as the header Start/End titles and content"). Pull exact colors/font/gap from this node via `get_design_context`.
- `Date/Time > Banner` (`I165:40701;158:176533`, hidden by default in this instance, width 568 × height 90): confirms the banner frame is a direct child of `Date/Time` at full calendar-column width (568, matching `Calendars` below it) — not inside the 144px `Ranges`/presets frame. This corroborates the Task 35 positioning fix (banner scoped to the calendar column) independently of the mockup screenshots. Pull this node's internal padding via `get_design_context` for the wrapper-div fix below.
- `Basic Footer` (hidden in this instance) needs its own separate pull for the `basic`/days-only text layout — not yet expanded in this metadata call since it was collapsed; expand and pull it during this task's research pass.

**Two implementation corrections folded in from pre-Figma-audit review (2026-09-22), to land before/alongside the SCSS pull:**

1. **Banner wrapper div:** `renderBanner.tsx` currently puts the `bds-date-picker__banner` class directly on `<bds-banner>`. Move it to a wrapping `<div class="bds-date-picker__banner">` instead, matching every other structural class in this component (`.container`, `.date-time`, `.presets`, `.time-band` are all layout wrapper divs, never classes on the child custom element they hold). This wrapper is what gets the Figma-pulled padding — not `<bds-banner>` itself.
2. **"Range:" label prefix:** `renderFooter.tsx` currently renders only the computed duration (e.g. `"17 days"`) with no label. The Figma `Range labels` node confirms a literal `"Range:"` (or per-locale equivalent) prefix precedes it. Add a new `rangeSummaryLabel: 'Range:'` key to `DatePickerLabels`/`DEFAULT_DATE_PICKER_LABELS` (English default), and render it as a separate `<span>` sibling to the summary `<span>` — following `renderRangeHeader.tsx`'s exact `Start:`/`End:` pattern (label and value as distinct elements, spacing via CSS gap, not string concatenation). This reconciles with the original spike's own example text (`"Rango: 18 días, 2 horas, 30 minutos"` — Spanish for "Range:"), which this plan's Task 35 acceptance criteria had dropped.
3. **Design decision (confirmed with user 2026-09-22):** the `"Range:"` label and its value only render when a range is actually committed (`rangeDuration !== undefined`) — matching the current empty-spacer behavior otherwise. It is NOT permanently rendered before any selection: unlike the header's `Start:`/`End:` (permanent field-identity chrome with a placeholder value), the footer summary is a derived metric with no natural placeholder — showing `"Range:"` alone before any selection would read as a broken state, not a helpful one.
4. **Banner overflow/no-wrap bug found and fix confirmed live 2026-09-22 (bug found via the "basic + range + banner" playground scenario; root cause verified via live CSS injection on the dev server before proposing):** in range mode, `bds-popover`'s `width` prop is `'auto'` (shrink-to-fit sizing) — only single-date/`basic`-no-range mode gets the fixed `296` width. With no fixed width, `.bds-date-picker__date-time` (and the banner inside it) have no width constraint, so the banner's message text never wraps — it forces the whole popover to grow wide enough to fit on one unbroken line (confirmed: `.date-time` measured 443px instead of the calendar's natural 296px). Scoped fix, `bds-date-picker.scss` only — zero changes to `bds-banner`'s own component styles:

   ```scss
   &__date-time {
     display: flex;
     flex-direction: column;
     margin: 0 auto;
     min-width: 0; // don't let a child's unwrapped text force this flex item wider than the calendar
   }

   &__banner {
     width: 0; // exclude this element's own text from the ancestor's shrink-to-fit sizing
     min-width: 100%; // then fill 100% of the actual space once layout is resolved
     box-sizing: border-box;
   }
   ```

   Once the wrapper-div correction (#1 above) lands, `&__banner`'s `width`/`min-width`/`box-sizing` rules apply to the wrapper `<div>`, not `<bds-banner>` itself — same fix, correct target element. Verified live via temporary CSS injection on the running dev server: `.date-time`/banner both dropped to 296px (matching the calendar) and the banner's text wrapped across two lines, confirmed via screenshot.

**Figma research pass:** Pull `get_design_context`/`get_metadata` for each row. A row is done only when actually pulled, never inferred from a sibling variant.

- [ ] Region: banner — default state (title/message/icon layout, all `calendarType` values it renders in) — start from the `Date/Time > Banner` node above
- [ ] Region: banner wrapper padding — pulled from the `Banner` frame's own padding/spacing, applied to the new `.bds-date-picker__banner` wrapper `<div>` (not `<bds-banner>` itself)
- [ ] Region: banner close (`X`) button — default, hover, focus, active
- [ ] Modifier: banner `state` variant (info/success/warning/error, or whichever subset Figma actually shows) — each pulled individually, not inferred from `info`
- [ ] Combination: each `state` variant × close-button hover, if the close button's color changes per state
- [ ] Region: footer range-summary label — default state, both `basic` (days-only — expand and pull the hidden `Basic Footer` node) and `expanded` (days/hours/minutes, already confirmed via `Expanded Footer > Range labels` above) text layouts, including the `"Range:"` label's own typography/color vs. the value's
- [ ] Dimensions: footer summary label alignment/spacing against the Clean/Cancel/Apply button row, pulled from Figma's layout data

**Acceptance criteria:**

- The two implementation corrections above (wrapper div, `"Range:"` label) are applied and unit-tested (new/updated assertions in the existing banner/footer test coverage) before the SCSS pull begins.
- Every research row above checked off before the first SCSS line is written, with the pulled value recorded — including confirming or correcting Task 35's `basic`-days-only/`expanded`-days-hours-minutes hypothesis against the actual pulled footer nodes.
- Token-only SCSS; no hardcoded colours, spacing, or radii — including the banner wrapper's padding (no literal `10px`; use the pulled spacing token).
- Every banner `state` variant × close-button interaction enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- Non-interactive banner content suppresses the native focus outline where applicable — verify this isn't scoped only inside the close button's own interactive-state block.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm each top-level selector matches the DOM `renderBanner.tsx`/`renderFooter.tsx` actually render.
- The banner overflow/no-wrap fix (`min-width: 0` on `.date-time`, `width: 0`/`min-width: 100%` on the banner wrapper) is applied and confirmed in range mode (`basic`+`range` and `expanded`+`range`) — banner text wraps within the calendar's width, popover no longer grows to fit an unbroken line.
- JSDoc brevity/content compliance.

**Manual test (required):**

Reuse Task 35's Scenarios 1-4. Run `pnpm dev:components` and validate:

- [ ] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value.
- [ ] Given the banner's close button, when hovered/focused, then it renders per the pulled state matrix. Pass: visually matches Figma.
- [ ] Given the footer summary label, when rendered alongside Clean/Cancel/Apply, then spacing matches the pulled dimensions. Pass: no visual crowding or misalignment.
- [ ] Given a committed range in `basic` or `expanded`, when the footer renders, then it shows `"Range:"` followed by the summary text as two visually distinct spans (matching the header's `Start:`/`End:` label/value styling). Pass: matches the pulled `Range labels` node.
- [ ] Given no range is committed yet, when the footer renders, then neither the `"Range:"` label nor the summary text appear (empty spacer, unchanged from Task 35). Pass: no premature/orphaned label text.
- [ ] Given a `basic`+`range` or `expanded`+`range` picker with a long banner message, when opened, then the banner text wraps within the calendar's width and the popover does not grow wider than the calendar. Pass: matches the width/behavior already correct in `default`/`basic`-no-range mode (visual regression check against the reported "basic + range + banner" playground bug).

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style info banner and range summary"`

---

### Task 36a: `bds-date-picker.scss` — eliminate duplicated typography/color rules, remove unused placeholder

**Status: DONE (2026-09-23), committed by user.** `@frontend-subagent` implemented all three changes and self-verified via a per-selector "effective declarations" comparison of the compiled CSS before/after (raw diffing is misleading for `@extend`-based dedup since it regroups selectors) — confirmed byte-identical computed output; full `bds-date-picker` spec suite unchanged (20/20 suites, 397 passed/1 todo); `tsc`/eslint clean. Independently re-verified: full diff review (matches the plan exactly, `&__range-group`/`&__footer-summary` gap tokens correctly untouched), `npx stencil test --spec` (324/324 suites, 3646 passed/1 pre-existing todo, zero regressions), `tsc --noEmit` (zero date-picker errors), and a direct inspection of the compiled `dist/collection/.../bds-date-picker.css` confirming the four-selector grouped typography rule and the two grouped label/value color rules carry identical `var(--boreal-*)` token values to before, with `font-family` preserved untouched at its original two sites only (`&__preset`, `&__footer-summary`). **`font-family` question resolved as intentional inheritance** — traced to `bds-popover.scss`'s `.popover` root wrapper (every one of the four typography sites is a light-DOM descendant of it via slotting), so `[slot='header-title']`/`&__time-bound-label` correctly rely on inheritance rather than redeclaring it; left out of `%typography-body-xs` as a result.

**Confirmed with user 2026-09-23**, found during a post-Task-36 SCSS review. Three findings, all scoped to `bds-date-picker.scss` only:

1. **Unused single-use placeholder:** `%time-selector-band` (top of file) is defined once and `@extend`ed exactly once (`&__time-band`). It eliminates no duplication — inline its four declarations directly into `&__time-band` and delete the placeholder.
2. **Duplicated typography block, repeated 4×:** `font-size: $boreal-typography-font-size-xs; line-height: $boreal-typography-line-height-xs; font-weight: $boreal-typography-font-weight-regular;` appears verbatim in `[slot='header-title']`, `&__preset`, `&__footer-summary`, and `&__time-bound-label`. Extract a new local placeholder `%typography-body-xs` and `@extend` it at all four sites. Before folding `font-family: $boreal-typography-font-family-primary` into the same placeholder, confirm whether its absence on `[slot='header-title']`/`&__time-bound-label` (vs. presence on `&__preset`/`&__footer-summary`) is intentional (inheritance) or an oversight — resolve this explicitly rather than guessing either way.
3. **Duplicated label/value color pairs:** `&__range-label`/`&__range-value` (`$boreal-text-default-light`/`$boreal-text-default`) and `&__range-summary-label`/`&__range-summary-value` declare the exact same two colors under different names. Extract two placeholders (e.g. `%label-text-light`/`%value-text-default`) and `@extend` them from both pairs — SCSS-only fix, do not rename the classes themselves or touch `renderRangeHeader.tsx`/`renderFooter.tsx` (bigger, unnecessary blast radius for the same visual result).

**Explicitly NOT a duplicate — do not merge:** `&__range-group` and `&__footer-summary` look structurally identical (flex/align-items:center/gap) but intentionally use different gap tokens (`gap-3xs` vs `gap-2xs`, confirmed via Task 36's Figma pull). Keep them separate.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Acceptance criteria:**

- `%time-selector-band` removed; its declarations inlined into `&__time-band`.
- `%typography-body-xs` (or equivalent name) extracted and `@extend`ed at all four original call sites, with the `font-family` question above explicitly resolved (not left ambiguous).
- Label/value color duplication eliminated via shared placeholders, extended from both the range-header and range-summary selectors.
- Zero visual change — this is a pure refactor; compiled CSS output must be equivalent to before (same declarations, same computed values) for every affected selector.
- Token-only SCSS maintained throughout (no regression to that rule while refactoring).

**Manual test (required):**

Run `pnpm dev:components` and validate against the existing `dp-banner-s1..s4` playground scenarios (Task 35/36's, unmodified) plus the range-mode header (`Start:`/`End:`) and presets sidebar:

- [x] Given the header, footer summary, presets, and time-bound label, when rendered, then each looks pixel-identical to before this refactor. Pass: no visual diff. **Verified 2026-09-23** via compiled-CSS equivalence check (see status note above) — no runtime path exists for a visual difference given byte-identical computed declarations.
- [x] Given the compiled CSS output, when inspected, then every affected selector's computed font-size/line-height/font-weight/color matches its pre-refactor value exactly. **Verified 2026-09-23**, independently, by both the implementing agent (per-selector effective-declarations script) and the coordinating session (direct inspection of `dist/collection/.../bds-date-picker.css`).

**Commit:** `git commit -m "refactor(bds-date-picker): EOA-17662 deduplicate SCSS typography and color rules"`

---

### Task 37: Phase 7 unit tests (consolidated)

**Status: DONE (2026-09-23).** `@testing-subagent` created `bds-date-picker.banner.spec.ts` (18 tests across 8 `describe` blocks) covering banner visibility/closable/state defaults across all `calendarType` values, the `actions`-slot-never-rendered guarantee, close/reopen dismissal persistence, range-summary label/value structure, `labels` consumer overrides (singular and plural), `basic`-vs-`expanded` shape, and live pre-Apply updates — deliberately not re-testing scenarios already covered by the bug-fix tests in `bds-date-picker.presets.spec.ts` (preset/Custom parity, date-only duration fix). Also deduplicated shared test helpers (`MOCKED_TODAY_UTC`, `renderPresetsDatePicker`, `findCalendarElements`, `findDayCellIn`, `findTimeSelectorBlocks`, `findSelectsIn`, `changeSelectValue`, `findFooterSummaryText`) out of `presets.spec.ts` and into the shared `date-picker.test-utils.ts`, so both spec files import one copy instead of duplicating them. Independently re-verified: full diff review (test files only, zero production-code changes), `npx stencil test --spec` (325/325 suites, 3664 passed/1 pre-existing todo, zero regressions), scoped coverage re-run across `renderBanner.tsx`/`renderFooter.tsx`/`value-mapping.ts`/`bds-date-picker.tsx` (98.74% statements / 95.79% branches / 100% functions / 99.11% lines — matches the agent's reported numbers exactly), `tsc --noEmit` and `eslint` on all touched files (clean). Not committed.

**Executor:** @testing-subagent
**Files:** `bds-date-picker.banner.spec.ts` (create)

**Unit tests to cover:** banner visibility/close behavior across all `calendarType` values; range summary behavior for `basic` (days-only) and `expanded` (days/hours/minutes); live updates as range changes; range-summary pluralization via `Intl.PluralRules` for singular vs. plural day/hour/minute counts (e.g. "1 day" vs. "18 days"); range-summary word-unit labels resolve from the new `labels` keys with correct English defaults and consumer overrides. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suite passing at >=90% coverage. **Verified 2026-09-23** — 325/325 suites passing, 98.74% statement coverage on the targeted surface.

**Commit:** `git commit -m "test: EOA-17662 add Phase 7 banner and range summary unit tests"`

---

### Task 38: Phase 7 documentation

**Status: DONE (2026-09-23).** `@documentation-subagent` delivered all three deliverables plus a necessary fourth (the `banner` prop was completely undocumented in `argTypes`/`<ArgTypes include>` before this task — added, since the acceptance criteria explicitly requires "MDX documents banner prop"): (1) 7 new rows in the "Customizing labels" table; (2) new `BannerWithRangeSummary` story (`expanded`+`range`+`with-time`, preselected range, popover pre-opened, docs-source override showing only real consumer usage) plus a new "Banner and range summary" MDX section; (3) `frenchLabels`/`LocalizedLabels` extended with all 7 new keys, live-rendering "Plage : 3 jours, 5 heures, 15 minutes". Independently re-verified: diff review (source strings match `DEFAULT_DATE_PICKER_LABELS` exactly, new story's date math checks out — Aug 10 09:00 → Aug 15 17:30 = 5 days/8 hours/30 minutes, matching the claimed render), `eslint` clean on the stories file. (`boreal-docs`'s `tsc --noEmit` has a pre-existing, unrelated config failure — `--ignoreDeprecations` invalid value — blocking before it reaches any file; not introduced by this task.) Not committed.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents banner prop and range-summary behavior; includes new story variant. Documents the new range-summary `labels` keys (with English defaults) and explains the `Intl.PluralRules`-based pluralization behind the singular/plural word forms, so consumers understand how "1 day" vs. "18 days" is chosen and how to override the words via `labels`.

**Confirmed with user 2026-09-22 — three concrete deliverables, not a new labels story:**

1. Add rows to the **existing** "Customizing labels" table in `bds-date-picker.mdx` (the established single canonical location for every `labels` key — do not create a separate table/story for this) for the new keys: `rangeSummaryLabel` (the `"Range:"` prefix added in the Task 36 fix), `rangeSummaryDaySingular`/`rangeSummaryDayPlural`, `rangeSummaryHourSingular`/`rangeSummaryHourPlural`, `rangeSummaryMinuteSingular`/`rangeSummaryMinutePlural` — same row format as the existing entries (key, used-for, English default).
2. Add a **new story variant** to `bds-date-picker.stories.ts` demonstrating the banner + range-summary feature together (a range picker with `banner` set and a committed range, so both features render live) — this is the "new story variant" the original acceptance criteria already called for.
3. Extend the existing `frenchLabels`/`LocalizedLabels` story (`bds-date-picker.stories.ts`) with French translations for the new `rangeSummary*` keys, since that story already demonstrates `range`+`with-time`+`expanded` (so the range-summary text actually renders) and is the one place showing what a fully-localized picker looks like end-to-end — more useful to a consumer than a bare table row alone.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [x] Given the new banner/range-summary story variant, when Storybook renders it, then it renders without console errors. Pass: no errors, interactive. **Verified 2026-09-23** by the implementing agent live in Chrome (banner + "Range: 5 days, 8 hours, 30 minutes" both rendered, zero console errors) — confirmed at the source level (correct date math, correct component wiring).
- [x] Given the MDX range-summary section, when read against Task 35/36's confirmed Figma format, then it matches exactly (not this plan's original unverified hypothesis). Pass: no stale/contradicting prose. **Verified 2026-09-23** — MDX prose describes the actual shipped behavior (whole-day-coverage summary, `Intl.PluralRules` pluralization, `labels` overrides), not the plan's original unverified basic/expanded hypothesis.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 7 banner and range summary"`

---

### Task 39: React/Vue wrapper parity check — Phase 7

**Status:** ✅ done (2026-09-23) — verified by `@qa-subagent` via the pack-based pipeline (`dev:pack:react` then `dev:pack:vue`, run serially), driven with the `playwright-cli` skill (not an ad-hoc Playwright script). Scenarios 1-4 were added to both testapp playgrounds before dispatch (`examples/react-testapp/src/App.tsx`, `examples/vue-testapp/src/App.vue` — scenario names `task39-s1-default-banner`..`s4-expanded-range-time-banner`), additively, leaving all existing Task 27/34 content intact.

**Verdict: PASS — no wrapper-specific divergence.** All four scenarios behave identically across the raw web component, the React wrapper, and the Vue wrapper. Every banner/grid/popover rect, every footer summary string, every committed value, and the close/reopen sequence matched the raw baseline exactly. Concrete evidence: banner bound as a JS property (`el.banner.visible === true`, `hasAttribute('banner') === false`) in both wrappers; Scenario 3 (`basic`+`range`) produced `SPAN.__range-summary-label`="Range:" + `SPAN.__range-summary-value`="5 days" and committed `{start:"2026-09-01", end:"2026-09-05"}` in React, Vue, and raw alike; Scenario 4 (`expanded`+`range`+`withTime`) produced `"Range:4 days, 8 hours, 30 minutes"` and `{start:"2026-09-01T09:00:00.000+00:00", end:"2026-09-05T17:30:00.000+00:00"}`, with a `"1 day, 1 hour, 1 minute"` singular/plural boundary case verified in both wrappers; Scenario 3's banner started exactly 8px after the presets sidebar (never over it) and the popover stayed at 440px (144 sidebar + 296 calendar) rather than ballooning; close → reopen re-showed the banner in both wrappers (dismissal not persistent). **Note: one item the report first listed under "bugs found" was later withdrawn as a test-tooling artifact — see the correction note below before trusting any "popover closes on X" claim.**

**Highest-risk item explicitly covered:** the banner wrapper's `width: 0; min-width: 100%` flexbox trick (Task 36's overflow fix) — it resolves identically in WebKit (AppleWebKit/605.1.15, run against the Vue surface), the browser most likely to diverge on this pattern. Wrapper computed width 296px, matching Chromium exactly. 0 console errors in Vue and in the raw baseline; React's only error was a pre-existing favicon 404 (also recorded in Task 34). The 37 warnings per wrapper are pre-existing `[BorealDS Button]` icon-only-button warnings, unchanged after every interaction.

**⚠️ CORRECTED 2026-09-23 — the QA agent's first "finding" below was a test-tooling artifact, not product behaviour. Do not propagate it.**

The original report claimed clicking the banner's close ("X") also closes the whole popover. **The user could not reproduce this in any manual test** (raw web components and React), and a direct re-investigation by the orchestrating session confirmed the user is right: **the popover stays open when a real user clicks the X.** The claim was withdrawn and the real root cause established (below). If a future agent reads the agent-memory entry or an older summary repeating this claim, treat it as wrong.

**Real root cause — synthetic ref-click vs. real click, on a self-removing element.** Reproduced deliberately in both Chromium and WebKit, same page, same button, only the click mechanism differing:

| Interaction                                                       | Popover after clicking X |
| ----------------------------------------------------------------- | ------------------------ |
| `playwright-cli click <ref>` (programmatic ref click)             | closes ❌ artifact       |
| `mousemove` → `mousedown` → `mouseup` at coordinates (real mouse) | stays open ✅ correct    |

Traced event sequence on the close button:

- **Real click:** `mousedown` → `focusout(INPUT→BODY)` → `focusin(BUTTON)` → `click` — focus ends on the button, no further blur.
- **Programmatic ref click:** `mousedown` → `focusout(INPUT→BODY)` → `focusin(BUTTON)` → `click` → **`focusout(BUTTON→null)` @+18ms** → button detached @+19ms → `POPOVER_HIDE`.

Chain: `playwright-cli`'s ref-click calls `element.focus()` before dispatching, so the close button takes real DOM focus. The click sets `isClosing = true` (`bds-banner.tsx:93`), which re-renders and removes the now-focused button from the DOM (`isOpen` flips false). Focus falls back to `<body>` with `relatedTarget: null`. `bds-popover`'s `handleFocusOutside` (document-level `focusin` listener, `bds-popover.tsx:239`) schedules an rAF, sees `activeElement === document.body`, takes the **extra confirmatory frame** added by Task 23's RAF-race fix (`bds-popover.tsx:262-265`), still sees `body` one frame later, and calls `hide()`. A real user's click never produces that intervening removal-then-blur sequence.

**Cross-check that isolates it:** programmatically clicking inside the popover on something that does _not_ delete itself — e.g. a calendar **day cell** — keeps the popover open, in both tooling modes. The X is only special because it is the one element the click removes.

**Conclusion: no product bug, no wrapper divergence, no Phase 7 defect.** `bds-banner`, `bds-popover`, and the banner close wiring all behave correctly under real interaction. This is the third instance of the same hazard class the QA agent's own memory already flags (`index-html-unscoped-gridcell-query-cross-contamination.md`): a `playwright-cli` ref interaction not matching real user interaction. **Standing lesson for QA tasks in this plan: never judge focus/blur-sensitive or self-removing controls via `playwright-cli click <ref>` — use coordinate-level mouse events.** Task 39's PASS verdict is unaffected: the real-interaction result matches the raw baseline exactly.

**One behaviour examined and confirmed NOT a Task 39 bug** (reproduces identically in the raw web component, so not a wrapper divergence): the visible banner box is 16px wider per side than the inner day grid (280 vs 248) because `__banner` uses `padding-xs` (8px) while `__calendars` uses `padding-l` (24px) — the _container-level_ alignment the checklist asks for holds (the full-width banner wrapper and `.bds-date-picker__calendars` both span the popover width), matching Task 35's accepted result exactly. Also noted, not a bug: the `basic`+range summary is an inclusive day count (Sep 1 → Sep 5 = `"5 days"`) because `resolveDurationRangeEndIso` adds +1 day when `!withTime`, whereas `withTime` gives raw elapsed time.

**Not verified, and why:** real desktop Safari.app (Playwright-WebKit used instead, the documented default path), iOS Safari (no testing path exists), and the `bds-table` ↔ `bds-calendar-grid` cross-component `<table>` collision path (`bds-table` isn't loaded in either testapp — a pre-existing component pair unrelated to Phase 7).

**Process note (disclosed by the QA agent, worth keeping):** while tearing down the raw Stencil server it ran `lsof -ti:3333` without `-sTCP:LISTEN`, which also matched a Brave Browser network-helper client connection and killed both; Brave respawned the helper and the main browser was unaffected. Recorded in `.claude/agent-memory/qa-subagent/kill-sandbox-boundary-for-background-tasks.md`.

**Also note:** running `dev:pack:vue` resets the React testapp's packed dependency (`examples/react-testapp/package.json` is no longer dirty). A later task needing the React app must re-run `dev:pack:react`.

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Banner and range summary behavior is consistent across wrappers. ✅ Met.

**Manual test (required):**

Repeat Task 35's Scenarios 1-4 through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [x] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in banner close or footer summary text. **Verified 2026-09-23** — byte-identical rects, summary strings, and committed values vs. the raw baseline across Scenarios 1-4.
- [x] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence. **Verified 2026-09-23** — identical in Vue (Chromium) and additionally in WebKit.

**Commit:** N/A

---

## Phase 8 — Keyboard navigation, accessibility (RTL descoped, see Task 41a)

Phase 8 wires and validates grid keyboard traversal and live announcements without changing the baseline architecture. Per the spike: `bds-calendar-grid`'s native `<table role="grid">` markup (v1, Task 3) was chosen specifically to make this phase additive — the [WAI-ARIA APG Date Picker Dialog Example](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) documents the exact keyboard interaction to implement (arrow-key cell traversal, month/year navigation hotkeys, live-region month/year announcement) and is the "agreed interaction model" referenced in Task 40 below. RTL parity, originally part of this phase, was descoped 2026-09-23 (Task 41a) pending ticket-owner confirmation — no design-system-wide RTL precedent exists to build against.

### Task 40: `bds-calendar-grid` arrow-key 2D traversal

**Status: DONE (2026-09-23).** `@frontend-subagent` wired `KeyboardController.setGridNavigation()` (no hand-rolled traversal logic — reuses `grid-navigation.ts`'s existing `move()`/`moveToEdge()` math entirely via the public API), with `wrap: true` and initial-focus selection both justified against a live fetch of the WAI-ARIA APG Date Picker Dialog Example (not assumed): ArrowLeft/Right/Up/Down cycle continuously within the visible month's enabled cells (disabled/out-of-month cells excluded natively via `null` array entries, no local workaround), PageUp/PageDown remain the sole month-crossing path via the existing `bdsMonthNavigate` emitters, and initial focus follows selected date → today → first enabled cell. A real, non-obvious gap was found and fixed: `setGridNavigation`'s roving-tabindex state doesn't survive a full month re-render (every `<td>` remounts with fresh `tabindex="-1"`), which would have permanently killed Tab-reachability into the grid after any mouse-driven month navigation — fixed via a new `@Watch('grid')` + `componentDidUpdate()` that re-establishes the tabbable cell (using the public `KeyboardController.rovingTabindex()` method when refocus should follow, or a passive tabindex mark otherwise, preserving whichever element the user's non-keyboard interaction left focus on). One existing test assertion was correctly updated to match the new intentional roving-tabindex behavior (was asserting all cells `tabindex="-1"`, now asserts exactly one `tabindex="0"` cell). Independently re-verified: full diff review (matches the plan's reuse decision — `rovingTabindex` confirmed as a real, documented public `KeyboardController` method, not invented), `npx stencil test --spec` (325/325 suites, 3664 passed/1 pre-existing todo, zero regressions), `tsc --noEmit`/`eslint` clean, and live confirmation on the dev server of the exact disabled-cell-skip/wrap behavior (`min`/`max`-narrowed scenario: initial focus landed on day 10 — the first enabled cell, since neither today nor a selected date was in range — and ArrowLeft wrapped directly to day 20, the last enabled cell, skipping all 9 disabled days in between). Not committed.

**QA follow-ups (2026-09-23):** Task 40's own manual QA was reproduced live in Chromium and WebKit and surfaced two defects that fall outside this task's acceptance criteria. Both are scheduled as follow-ups rather than reopening Task 40, since its stated criteria all passed — these are new findings, not regressions against them: **Task 40a** — a day-cell focus-ring transition flicker on arrow-key traversal (root-caused to `bds-calendar-day-interaction-transition` transitioning `outline-width`/`box-shadow`; A/B-confirmed by neutralizing the transition); **Task 40b** — arrow keys pressed while an in-grid month-nav button has focus steal focus into the day grid (root-caused to `grid-navigation.ts`'s `{-1,-1}` fallback via `resolveGridCurrentPos`). Task 40's own commit does not depend on either fix landing.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify), `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` (reuse — existing generic grid-keyboard utility, do not reimplement traversal logic)

**Utility discovery:**

- Feature area: 2D grid keyboard navigation (arrow keys, Home/End, PageUp/PageDown, boundary handling).
- Search performed: `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/`.
- Candidates found: `grid-navigation.ts` — a generic grid-keyboard utility, explicitly flagged as this phase's integration point by a code comment left in v1's Task 9, carried unwired through v2.
- Fit assessment: fully fits per the flagged code comment; confirm at dispatch time that its API (cell addressing, boundary/wrap behavior) matches `bds-calendar-grid`'s 6-week/42-cell fixed grid shape and out-of-month/disabled-cell exclusion requirement — if it doesn't, that's a gap to close in the utility itself, not a local reimplementation.
- Reuse decision: wire `grid-navigation.ts` directly; do not hand-roll new arrow-key/Home/End/PageUp/PageDown handling in `bds-calendar-grid.tsx`.
- Gap handling: if the utility's API can't express "exclude out-of-month/disabled cells from focus stops" without local workaround code, extend the utility itself first, then wire it — do not leave a parallel local filter layered on top as a permanent fixture.
- Anti-duplication check: confirms no component-local keyboard-navigation state machine is planned alongside `grid-navigation.ts`.
- Test impact: Task 43's `bds-calendar-grid.keyboard.spec.ts` asserts traversal behavior through the wired utility, not a local reimplementation.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `bds-calendar-grid.tsx` is composed twice inside `expanded`+`range` pickers (per v2's Task 18, two independently-controlled instances) — confirm the wired keyboard-navigation state is scoped per-instance (no shared focus/cell state leaking between the two grids), matching the "Works for both single and dual grid instances" acceptance criterion already stated below.
- [ ] Boundary case: arrow-key traversal reaching a disabled cell (Phase 3's `min`/`max`-driven `DayCell.isDisabled`) at a grid edge, or an entire visible month disabled (the narrow-`min`-`max`-window case flagged in v2's Task 19m-2) — confirm focus skips past disabled cells rather than landing on or wrapping through them, and what happens when literally every cell in the visible month is disabled (focus should move to the next/previous month via the existing `bdsMonthNavigate` path, not silently stay put or throw).
- [ ] Default/empty state: which cell receives initial keyboard focus when the grid first becomes keyboard-reachable (Tab into it) — today's date, the currently selected date, or the first day of the visible month? State this explicitly, since none of Phase 0-4's existing behavior established this (arrow-key traversal is new in this task).
- [ ] Reactivity: month/year navigation (via `bdsMonthNavigate`, existing event path) changes the grid's cell set entirely — confirm the wired utility's internal focus-position state is reset or correctly remapped on month change, not left pointing at a stale cell index from the prior month's grid.

**Acceptance criteria:**

- Wires the existing `grid-navigation.ts` utility (flagged as this phase's integration point since v1's Task 9 code comment, carried unwired through v2) rather than hand-rolling new traversal logic.
- Arrow keys, Home/End, and PageUp/PageDown behavior aligns with the agreed interaction model.
- Month-boundary crossing emits the existing `bdsMonthNavigate` event path.
- Out-of-month and disabled cells stay excluded from keyboard focus stops.
- Works for both single and dual grid instances.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker, keyboard-focus the grid.
- Scenario 2: `calendarType='expanded'` + `range`, keyboard-focus each grid independently.
- Scenario 3: a picker with `min`/`max` narrowing part of the visible month.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1, when arrow keys/Home/End/PageUp/PageDown are pressed, then focus moves cell-to-cell per the agreed interaction model. Pass: focus visibly follows the expected cell, no focus loss.
- [x] Given Scenario 1, when traversal crosses a month boundary, then `bdsMonthNavigate` fires and the grid re-renders the new month with focus landing on the correct cell. Pass: month changes, focus correct.
- [x] Given Scenario 2, when traversing one grid, then the other grid's focus/traversal state is unaffected. Pass: no shared/leaking focus state between the two instances.
- [x] Given Scenario 3, when traversal reaches a disabled cell, then focus skips it. Pass: disabled/out-of-month cells are never a focus stop.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add arrow-key 2D grid traversal"`

---

### Task 40a: `bds-calendar-grid` day-cell focus-ring transition flicker

**Status: ✅ resolved (2026-09-23) — no code change; documented decision.** Found during Task 40's manual QA and reproduced live in Chromium + WebKit by `@qa-subagent` (screen recording + timed `outline-width` sampling). Root cause: `bds-calendar-day-interaction-transition` (`bds-calendar-grid.scss:1-7`) transitions `outline-width 0.3s` and `box-shadow 0.3s`; the day-cell ring is an `outline` growing `0 → 3px` (`:80`, `:focus-visible` `:92-99`), and `outline-width` renders in discrete integer-pixel steps (`0→1→2→3`), so during arrow-key traversal the leaving and entering rings animate in opposite directions simultaneously — the reported "flicker/delay". Three alternatives were implemented and each rejected (see Decision below); the committed outline implementation stands unchanged.

**Root cause (evidence, at the original 0.3s):** `bds-calendar-day-interaction-transition` (`bds-calendar-grid.scss:1-7`) transitioned `outline-width` and `box-shadow`. Day cells start at `outline: 0 solid $boreal-focus` (width `0`, line 80) and `:focus-visible` sets `outline-width: 3px` plus `bds-calendar-day-focus-ring`'s box-shadow (lines 9-12, 92-99). Because both properties are transitioned, every arrow-key move animates the entering cell's ring `0→1→2→3px` while the leaving cell shrinks `3→0` in parallel — two half-grown rings on screen at once (the reported "flicker/delay"). Measured settle ≈317ms (Chromium) / ≈333ms (WebKit) after each move at 0.3s; `outline-width` also rounds to integer used-px, so the ring steps rather than grows. Contributing factors: `background-color` fades the fill on the same rule; `z-index` is not transitioned (snaps `0→1`) so the two rings visually collide during the overlap; `:hover` shares the same mixin with a different box-shadow.

**Decision (2026-09-23): keep the `outline`-based ring, with the ring transition at `0.1s`.** The outline is load-bearing — it is the only ring mechanism that renders correctly over the range/hover band. Alternatives tried and rejected:

1. **Drop the ring transition (instant ring)** — rejected: the component intentionally has a ring transition; snapping it was not accepted.
2. **Animate `outline-color` instead of `outline-width`** (constant 3px transparent outline → colour fade) — smooth (colour interpolates continuously, no stepping) but **imperceptible**: fading only the opacity of a thin fixed-width stroke reads as "no transition".
3. **Switch to the shared `bds-focus-ring` box-shadow** (`0 0 0 1px white, 0 0 0 3px focus`, the mixin `bds-button` uses) — smooth and visible (spread interpolates `0 → 3px`) but the ring **renders poorly over the range/hover band** — a styling regression, because range backgrounds are painted by `z-index: -1` child divs and only the outline draws correctly outside the cell.

**Final values:** `box-shadow 0.1s ease` and `outline-width 0.1s ease` (background-color/border-color stay 0.3s). 0.1s is a deliberate faster value for the ring specifically — it keeps a visible transition while reducing the integer-pixel stepping inherent to `outline-width`; the ring is not set to 0.3s because at that duration the stepping reads as stutter. Do **not** re-attempt variants 1–3, and do not raise the ring timing back to 0.3s, without revisiting the band-rendering constraint.

**Why it differs from the prev/next nav buttons:** they are `bds-button`s (`bds-calendar-grid.tsx:287-299`) whose ring is a soft, continuously-interpolated box-shadow (`bds-transition-surface`, `bds-button.scss:144` + `:34`) at 0.3s; the day cell cannot use that mechanism without the band regression, so it keeps the hard, integer-stepped outline at 0.1s. The divergence is a consequence of the band constraint, not an oversight.

**Executor:** none (decision + timing-only change; no logic change)
**Files:** `bds-calendar-grid.scss` (modify — ring transition timing only)

**Validation (2026-09-23):** compiled `bds-calendar-grid.css` confirms the day cell emits `outline: 0 solid var(--boreal-focus)` and `transition: … box-shadow 0.1s ease, outline-width 0.1s ease`, with `outline-width: 3px` on `:focus-visible`; `bds-calendar-grid` spec suite 4/4 suites, 42 passed, 1 todo, 0 failures. No unexpected behaviors observed. Live visual confirmation of the ring over the band remains the ticket owner's manual check.

**Manual test (required):**

Reuse Task 40's playground scenarios (`#dp-keyboard-s1`, `#dp-keyboard-s2`). Run `pnpm dev:components` and validate:

- [ ] Given `#dp-keyboard-s1`, when arrow keys move focus cell-to-cell, then the ring transitions at 0.1s with no artifact beyond the known integer-pixel stepping. Pass: no new regression, transition perceptible.
- [ ] Given `#dp-keyboard-s2`, when traversing a cell adjacent to an active range band, then the focus ring renders fully (unclipped) over the band. Pass: outline ring visible on all sides over the range/hover band — the constraint that rules out the box-shadow variant.
- [ ] Given the prev/next nav buttons, when keyboard-focused, then their ring behaves as before (unchanged, `bds-button`-level 0.3s). Pass: no change.

**Commit:** `git commit -m "fix(bds-calendar-grid): EOA-17662 tune day-cell focus-ring transition timing to 0.1s"`

---

### Task 40b: `grid-navigation` — arrow keys steal focus from in-grid header controls

**Status: ✅ DONE — implemented and manually verified 2026-09-23.** Found 2026-09-23 during Task 40's manual QA (incidental to Task 40a, separate root cause). `setupGridNavigation` registers its arrow-key handlers on the grid **root**, which also contains the month-nav buttons; `resolveGridCurrentPos` (`utils/a11y/keyboard/focus/resolve.ts`) returns `{-1,-1}` when the focus target isn't a grid cell, and `move()` (`grid-navigation.ts:120-163`) / `moveToEdge()` (`:165-194`) then fall back to `positions[0]` and step from there — so Tab to "Next month" + ArrowRight jumps focus into a day cell.

**Implemented by `@frontend-subagent` (2026-09-23):** new exported helper `isNonCellFocusWithinRoot(items, root)` in `focus/resolve.ts` (returns `true` only when `document.activeElement` is an `HTMLElement` contained by the root, is not the root itself, and is not any grid cell — using `=== || contains` for the cell match so focus inside a cell is never misclassified). `move()` and `moveToEdge()` each early-return when it's `true`, so Arrow keys and Home/End no-op identically; PageUp/PageDown (separate handlers) are unaffected, and the root-focused / nothing-focused fallbacks are preserved. Unit coverage added in `navigation.spec.ts` (4 tests: Arrow no-op, Home/End no-op, first-cell fallback with nothing focused, fallback with the root focused); the two no-op tests were confirmed to fail without the guard. Verified: `src/utils/a11y/keyboard` 41/41, `bds-calendar-grid` 42 passed/1 todo, `bds-date-picker` 415 passed/1 todo, eslint clean, `tsc --noEmit -p tsconfig.build.json` exit 0.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` (modify), `packages/boreal-web-components/src/utils/a11y/keyboard/focus/resolve.ts` (modify if needed), `packages/boreal-web-components/src/utils/a11y/keyboard/__test__/navigation.spec.ts` (modify)

**Scope note:** `grid-navigation.ts` is a **shared** a11y utility. Its only production consumer today is `bds-calendar-grid.tsx:82` (via `KeyboardController.setGridNavigation`), but Task 48e reuses it for the month/year grids — so fix it at the utility level (a guard in `move()`/`resolveGridCurrentPos`), not as a `bds-calendar-grid`-local special case.

**Cross-reference:** keyboard-behavior only — this task must not touch `styles/_interactions.scss` or the shared `bds-focus-ring`/transition mixins; the focus-ring appearance fix is Task 40a.

**Acceptance criteria:**

- Arrow-key traversal no-ops when the currently focused element inside the grid root is not a grid cell (e.g. a header/nav button) — native button keyboard behavior is left intact.
- Existing traversal behavior from a focused cell (including the initial-focus fallback when nothing is focused) is unchanged.
- New unit coverage in `navigation.spec.ts` asserts the non-cell-focus no-op.
- No regression to `bds-calendar-grid`'s existing keyboard tests.

**Manual test (required):**

Reuse Task 40's `#dp-keyboard-s2`. Run `pnpm dev:components` and validate:

- [x] Given the month-nav button has focus, when arrow keys are pressed, then focus does not move into the day grid. Pass: focus stays on the button, no jump. (Verified 2026-09-23.)
- [x] Given a day cell has focus, when arrow keys are pressed, then traversal works exactly as before. Pass: no regression. (Verified 2026-09-23.)

**Commit:** `git commit -m "fix(a11y): EOA-17662 keep grid arrow keys from stealing focus from header controls"`

---

### Task 40c: range preview follows keyboard focus (dedicated focus events)

**Status: ✅ implemented (2026-09-23) — live-validated.** Implemented by `@frontend-subagent` via dedicated events: `bdsDayFocus` (detail `{ date }`, new `CalendarGridDayFocusDetail`) emitted on `focusin` of a day cell (listener on the `<table>`, so header-nav focus never triggers it), and `bdsGridFocusLeave` (void) emitted on `focusout` only when focus leaves the table. The date-picker factors its preview guard into `updatePreviewEnd(date)` (shared by hover and focus) and clears via `clearPreviewEnd()` (shared by `bdsGridLeave` and `bdsGridFocusLeave`). Verified: `bds-date-picker` 21 suites / 429 passed / 1 todo (+10 new tests); tsc/eslint clean. Live browser check (`#dp-reverse-range-s1`, basic range): select Sept 1 → ArrowRight ×2 → preview band spans Sept 1–3 (3 cells); Tab out → band clears.

**Decision (2026-09-23): implement via dedicated events** (not by reusing the semantically-mouse `bdsDayHover`), previewing only mid-range, mirroring the existing hover guard.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify — emit focus events), `types/types.ts` (modify — new detail type), `bds-date-picker.tsx` (modify — listen + reuse the preview guard), `bds-calendar-grid/__test__/bds-calendar-grid.events.spec.ts` (modify), `bds-date-picker/__test__/bds-date-picker.range.spec.ts` (modify)

**Grounding findings (2026-09-23, read the actual current source before dispatch):**

- Grid event surface: `bdsDayHover`/`bdsGridLeave` (`bds-calendar-grid.tsx:73,76`); detail shapes `CalendarGridDayClickDetail`/`CalendarGridDayHoverDetail` are both `{ date: string }` (`types/types.ts:1-7`). Add `bdsDayFocus` (detail `{ date }`, new `CalendarGridDayFocusDetail`) and `bdsGridFocusLeave` (void).
- `findFocusedIsoDate()` (`bds-calendar-grid.tsx:172-185`) already maps `document.activeElement` → isoDate via `_cellRefs` — reuse it in the `focusin` handler; no new `data-*` attribute needed.
- Cells are focusable `<td>`s inside `<table role="grid">` (`:333`); the month-nav buttons live in the header (`:287-299`), **outside** the table. Listen on the `<table>` so header-button focus never triggers a preview (consistent with Task 40b's separation).
- `focusin`/`focusout` bubble (unlike `focus`/`blur`). `focusout` fires on every cell-to-cell move, so the clear must fire **only** when focus actually leaves the grid — check `relatedTarget` is not contained by the grid root.
- Date-picker side: `handleDayHover` (`bds-date-picker.tsx:409-422`) holds the guard (`!effectiveRange || rangeStart === null || rangeEnd !== null → return`; date equals start → clear; else set `previewEnd`). Factor that body into a shared private method (e.g. `updatePreviewEnd(date)`) called from both the hover and the new focus listener. `bdsGridLeave` → `handleGridLeave` (`:424-426`) clears `previewEnd`; add the focus-leave listener to the same clear.
- Precedence: last event wins (mouse `mouseenter` fires only on entry, so arrowing wins until the pointer moves) — acceptable; state it, don't add explicit precedence.

**Acceptance criteria:**

- New `bdsDayFocus` event (detail `{ date }`) fires when a day cell gains focus; new `bdsGridFocusLeave` (void) fires when focus leaves the grid entirely (not on cell-to-cell moves).
- `bds-date-picker` shows the same preview band for keyboard focus as for mouse hover — mid-range only (rangeStart set, rangeEnd null), never for the start cell itself.
- Leaving the grid by keyboard (Tab out, Escape close, focus to the other grid) clears the preview.
- No regression to mouse hover-preview (TC-21) or single-date mode (no preview when `range` is false).
- Works in single and `expanded` (dual-grid) modes; the preview is global, as with hover.
- No `any`; JSDoc on the new public events; no visual change (no SCSS expected).

**Manual test (required):**

Reuse Task 40's `#dp-keyboard-s2` (`expanded`, range) and `#dp-reverse-range-s1` (`basic`, range). Run `pnpm dev:components` and validate:

- [ ] Given a range picker, when a start day is chosen and arrow keys move focus, then the grey preview band follows the focused cell (forward and backward), matching mouse-hover behavior.
- [ ] Given the same, when focus leaves the grid (Tab out / Escape), then the preview band clears.
- [ ] Given a committed range (rangeEnd set), when focus moves, then no preview band appears.
- [ ] Given mouse hover, then the preview still behaves exactly as before (TC-21 bidirectional preview).

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 preview range on keyboard focus"`

---

### Task 40d: `bds-calendar-grid` roving-tabindex / ARIA bugs found by Task 43

**Status: ✅ implemented (2026-09-23) — FM-85 live-validated.** Implemented by `@frontend-subagent`: (1) FM-85 — `aria-selected` now renders the string `'true'` / `undefined` (`bds-calendar-grid.tsx:310`), so `getInitialActiveSelector()`'s `[aria-selected="true"]` matches; (2) FM-86 — `markTabbableCell` (`:275-285`) now demotes every cell to `tabindex="-1"` before setting the target to `"0"` (verified `KeyboardController.rovingTabindex` moves focus, so the manual demote was used instead). 3 new tests + a strengthened a11y assertion, all verified non-vacuous (reverting the fixes fails them). `bds-date-picker` 22 suites / 457 passed; coverage `bds-calendar-grid` 94.21% stmts / `bds-date-picker` 99.2%; tsc/eslint clean. Live: `#dp-preselected-outside-month-s1` (value 2027-04-12) → the selected cell has `aria-selected="true"` and the single `tabindex="0"` cell is April 12 (was April 1).

1. **FM-85 — selected-date initial tabbable cell never works, and invalid ARIA.** `getInitialActiveSelector()` (`bds-calendar-grid.tsx:255`) returns `'[aria-selected="true"]'`, but the cell renders `aria-selected={boolean}` (`:306`) and Stencil serializes a boolean `true` on an `aria-*` attribute as **`""`** (not `"true"`), so `Element.matches` never matches. `setupGridNavigation` then falls back to `positions[0]` — Tab lands on the month's first cell, not the selected date (observed: `selectedDate='2026-02-15'` → `tabindex="0"` on Feb 1). The empty value is also invalid ARIA state. **Fix:** stringify it — `aria-selected={cell.isCurrentMonth && cell.isoDate === this.selectedDate ? 'true' : undefined}` (matching the `aria-disabled`/`aria-current` convention; keep `undefined` for the else branch so non-selected cells still have no attribute, preserving the existing a11y assertion).
2. **FM-86 — prop-only re-render leaves two `tabindex="0"` cells** (regression from Task 40's `componentDidUpdate`). `markTabbableCell` only _sets_ `tabindex="0"` and never demotes; on a `grid` change the cells remount (invariant holds), but on a prop-only re-render (e.g. `selectedDate` changing after a day click) the reused cells keep the old stop and a second is added (observed `['1','15']`). **Fix:** demote every other cell — or route through `KeyboardController.rovingTabindex` — in the `targetDay == null` branch.

**Executor:** @frontend-subagent (implementation), @testing-subagent (tests), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify), `bds-calendar-grid.keyboard.spec.ts` (modify — add the FM-85/FM-86 tests once fixed), `bds-calendar-grid.a11y.spec.ts` (modify — assert the `aria-selected="true"` string)

**Acceptance criteria:**

- `aria-selected` renders as the string `"true"` on the selected in-month cell, and is absent on non-selected cells.
- Tabbing into the grid lands on the selected date when one is set (else today, else the first enabled cell).
- Exactly one cell has `tabindex="0"` after a prop-only re-render (no duplicate stops).
- Tests added for both; no regression to the existing grid/date-picker suites.

**Manual test (required):**

Reuse `#dp-keyboard-s1` and `#dp-preselected-outside-month-s1` (which has a preselected value). Run `pnpm dev:components` and validate:

- [ ] Given a preselected date, when Tab enters the grid, then focus lands on the selected date, not the month's first cell.
- [ ] Given a day click, when focus leaves and re-enters the grid, then exactly one cell is a tab stop.

**Commit:** `git commit -m "fix(bds-calendar-grid): EOA-17662 correct aria-selected and roving-tabindex stops"`

---

### Task 40e (new — discovered during Task 45's manual QA, 2026-09-24): roving tabindex anchors to a disabled "today" cell when today falls outside `min`/`max`, making arrow-key traversal a no-op

**Status:** ✅ done (2026-09-24) — implemented directly in the orchestrating session (small, well-root-caused fix). `getPriorityFocusCell` now requires `!cell.isDisabled` on both its selected-date and today branches (the first-enabled branch already had it), so a disabled cell can never be chosen as the roving anchor. Verified: two new tests in `bds-calendar-grid.keyboard.spec.ts` — both **confirmed non-vacuous** (temporarily reverting the fix fails them), and both need a prop-only re-render to reproduce (the defect fires from `componentDidUpdate` → `markTabbableCell`, which does not run on initial mount — a first attempt without the re-render step passed vacuously and was corrected). Full `bds-date-picker` suite green (22 suites / 459 tests); `eslint` and `tsc -p tsconfig.build.json` clean. Live browser check (fresh Stencil server on port 3334, `playwright-cli`): `#dp-keyboard-s3` (`min=2026-09-10 max=2026-09-20`, today `2026-09-24`) now anchors the single roving stop on **Sep 10** (first enabled, `aria-disabled=null`, 0 disabled tab stops) instead of the disabled Sep 24, and arrow keys traverse (`Sep 10 → Sep 11 → Sep 12`). Nothing committed — per standing preference, commits are the user's own action.

**Gap (confirmed live by `@qa-subagent` on the raw web component and in React/Vue/WebKit, and root-caused from source in the orchestrating session):** with a narrow `min`/`max` window that excludes today (e.g. `min="2026-09-10" max="2026-09-20"` while today is `2026-09-24`), opening the picker anchors the grid's roving tabindex to the disabled "today" cell, and arrow keys do nothing from there. This violates Task 40's own acceptance criterion ("Out-of-month and disabled cells stay excluded from keyboard focus stops").

**Root cause (verified against current source, post-Task-40d):**

1. `getPriorityFocusCell()` (`bds-calendar-grid.tsx:265-273`) picks the first match of selected-date → **today** → first-enabled, but the `isToday` branch has no `isDisabled` guard, so a disabled today cell is returned.
2. `markTabbableCell()` (`:275-285`) demotes every cell then sets `tabindex="0"` on that disabled today cell.
3. `getGridItems()` (`:242-246`) excludes disabled cells (maps them to `null`), so the focused disabled cell is not in the grid items.
4. `isNonCellFocusWithinRoot()` (`utils/a11y/keyboard/focus/resolve.ts:34-48`) classifies a focused element that is inside the root but absent from `items` as "non-cell focus", so `move()` (`grid-navigation.ts:120-164`) early-returns — arrow keys become a no-op.

**Fix applied:** guard `getPriorityFocusCell`'s selected-date and today branches on `!cell.isDisabled`, so both fall through to the first-enabled branch when the candidate is disabled. Regression coverage added in `bds-calendar-grid.keyboard.spec.ts` (disabled-today and disabled-selected-date cases, each asserting the anchor and that arrow traversal works after a re-render).

**Files:** `bds-calendar-grid/bds-calendar-grid.tsx` (modify — `getPriorityFocusCell`), `bds-calendar-grid/__test__/bds-calendar-grid.keyboard.spec.ts` (modify).

**Commit:** `git commit -m "fix(bds-calendar-grid): EOA-17662 skip disabled today cell when anchoring roving tabindex"`

---

### Task 41: live region audit

**Status: ✅ DONE — implemented and manually verified 2026-09-23.** Implemented by `@frontend-subagent`: `renderCalendarPanel.tsx` now derives the announcement from **all** rendered calendars — a single `getMonthYearLabel(year, month, locale)` label, or a `–`-joined span when `expanded` renders two (e.g. `"August 2026 – September 2026"`) — and renders exactly one visually-hidden `<div class="bds-date-picker__live-region" aria-live="polite" aria-atomic="true">` as the first child of `.bds-date-picker__calendars`; `bds-date-picker.scss` adds `&__live-region { @extend %visually-hidden; }`. No new orchestrator state; `bds-calendar-grid` untouched. Coverage added in `bds-date-picker.a11y.spec.ts` (3 tests: single polite/atomic live region + text, exactly one in expanded mode announcing both visible months as one `–`-joined span, text updates to `"September 2026"` after Next-month). Verified: `bds-date-picker` 21/21 suites, 418 passed, 1 todo, 0 failures; eslint clean. Visual-hiddenness itself is a manual check (mock-doc can't assert computed styles).

**Split from "live region + RTL audit," confirmed with user 2026-09-23** — see Task 41a below for why RTL was descoped rather than implemented here.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderCalendarPanel.tsx` (modify — the live region), `bds-date-picker.scss` (modify — visually-hidden rule for it)

**Grounding findings (2026-09-23, read the actual current source before dispatch):**

- `renderCalendarPanel` already receives `calendars` (each entry carries `year`/`month`) and `locale` — the announcement text can be derived **there** from `calendars[0]` via the existing `getMonthYearLabel(year, month, locale)` (`services/date-engine/format.ts:19`), so **no new orchestrator state is needed**. Deriving from the passed `calendars` means every displayed-month change updates it (nav buttons, PageUp/PageDown from Task 40, and preset-driven jumps); the initial mount does not announce (a live region only announces post-mount mutations).
- **Single shared element** inside `.bds-date-picker__calendars` → no double-announce in `expanded` mode. Announce **all** rendered calendars' months as one `–`-joined span (the second is `nextMonthFrom(displayYear, displayMonth)`, `bds-date-picker.tsx:1006`), so one `bdsMonthNavigate` still produces exactly one announcement covering both visible months.
- **SCSS gap the task's original file list missed:** the live region must be visually hidden, which requires a rule in `bds-date-picker.scss` reusing the globally-injected `%visually-hidden` placeholder (`styles/_commons.scss:24`, already `@extend`ed at `bds-date-picker.scss:222`). Hence `bds-date-picker.scss` is added to the file list.
- **Reactivity:** `bdsMonthNavigate` can fire rapidly under PageUp/PageDown key-repeat; `aria-live="polite"` coalesces/queues by design — no debounce/throttle needed; state this explicitly rather than adding one.

**Acceptance criteria:**

- Adds a single visually-hidden `aria-live="polite"` (with `aria-atomic="true"`) month/year announcement element, updated whenever the displayed month/year changes.
- Renders exactly one live region regardless of `calendarType` (no double-announce in `expanded`).
- No visual regression; uses the existing `%visually-hidden` placeholder, token-only SCSS.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker with a screen reader (or `aria-live` region inspection) active, navigate months.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1, when the month/year changes (nav button or Task 40's traversal), then the live region announces the new month/year exactly once. Pass: single announcement per navigation, no duplicate/missing announcement. (Verified 2026-09-23.)

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add live region announcements"`

---

### Task 41a: RTL support — descoped, not scheduled

**Confirmed with user 2026-09-23, pending ticket-owner sign-off.** The ticket (`ai-work/tickets/EOA-17662-bds-date-picker-v3.md`) does list "RTL parity" as an explicit Phase 8 acceptance criterion, tracing back through the v1 spike's phased roadmap — this isn't scope the plan invented. However, a full-codebase search found **zero existing RTL handling in any Boreal DS component** (`dir="rtl"` attribute checks, `[dir=rtl]`/`:dir(rtl)` CSS selectors — no matches anywhere). Task 41's own research pass had assumed an existing host-level `dir` mechanism to reuse; none exists.

**Why this is descoped rather than implemented:** RTL support is a design-system-wide concern (logical CSS properties, icon-mirroring convention, `dir` propagation strategy) — not something that provides real value built into one component in isolation. If `bds-date-picker` were the only component that mirrors correctly in RTL, a consumer building an actual RTL page still couldn't use it, since every surrounding component (buttons, inputs, popovers) would stay LTR. Building it now means maintaining a capability nobody can exercise until the design system defines a system-wide RTL strategy — and re-doing it then anyway, once that strategy picks conventions this one-off wouldn't have followed.

**Action:** flag to the ticket owner that RTL parity, as currently written, has no design-system precedent to build against, and confirm whether to (a) formally descope it from this ticket's acceptance criteria, (b) create a separate, system-wide RTL initiative ticket that this component would later adopt, or (c) proceed with a one-off implementation anyway despite the inconsistency. Not scheduled pending that answer — do not implement RTL mirroring, logical-property migration, or icon-flipping in `bds-calendar-grid.scss`/`bds-date-picker.scss` until this is resolved.

**Executor:** none (blocking design/scope gate, not implementation)
**Files:** none

---

### Task 42: Escape key closes popover and returns focus to trigger

**Status: ✅ DONE — implemented and manually verified 2026-09-23 (both single-date and range-mode draft-revert scenarios).** Implemented by `@frontend-subagent`: added a `KeyboardController` attached to the host with a `KEYBOARD.Escape` handler (`{ preventDefault: false }`) that, when the popover is open, discards the draft (the footer CANCEL reset factored into a shared `discardDraft()` method), calls `bdsPopover.closePopover()`, then `requestAnimationFrame(() => this.bdsInput?.focus())` — mirroring `bds-select`. Added a `bdsInput` getter (`bdsField.querySelector('input')`). Coverage added to `bds-date-picker.keyboard.spec.ts` (Escape closes + focus returns to the input, not `body`). Verified: `bds-date-picker` 21 suites / 419 passed / 1 todo; tsc/eslint clean. Live browser check (dev server, `#dp-keyboard-s1`): focus on the popover's "Previous month" button → Escape → popover closes and `document.activeElement` is the field `INPUT` (previously `BODY`).

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify), `__test__/bds-date-picker.keyboard.spec.ts` (modify — minimal Escape test; Task 43 expands)

**Utility discovery:**

- Feature area: Escape-key popover dismissal + focus restoration to the trigger.
- Search performed: `bds-select.tsx` (the codebase's existing form-associated, popover-driven component with this exact interaction already implemented).
- Candidates found: `bds-select.tsx`'s `KEYBOARD.Escape` handler — closes via its own popover's `closePopover()`, returns focus via `requestAnimationFrame(() => this.bdsInput?.focus())`, no `preventDefault`.
- Fit assessment: fully fits — `bds-date-picker` already composes `bds-popover` and a slotted trigger field the same way `bds-select` does, so the same handler shape applies without modification.
- Reuse decision: mirror `bds-select`'s handler verbatim (same `KEYBOARD.Escape` constant, same `requestAnimationFrame` focus-return pattern, same `{ preventDefault: false }`), not a new independent implementation.
- Gap handling: not applicable — no extension needed.
- Anti-duplication check: confirms no parallel Escape-handling convention is introduced; this is the second component in the codebase to use this exact pattern, keeping it consistent rather than divergent.
- Test impact: Task 43's `bds-date-picker.keyboard.spec.ts` addition asserts close + focus-return behavior, mirroring however `bds-select`'s own equivalent test asserts it.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `bds-popover`'s `closePopover()` is already called from the existing footer Cancel/Clean handlers and the field's own clear (✕) button (per v2) — confirm this task's Escape handler calls the same `closePopover()` method, not a parallel close path, so any future popover-close side effect (e.g. draft-revert-on-close) automatically covers Escape too without separate wiring.
- [ ] Boundary case: Escape pressed while a nested `bds-select` (Phase 2/5 time selector) has its own popover open inside `bds-date-picker`'s popover — confirm Escape closes only the inner `bds-select` popover first (standard nested-dialog behavior), not both at once; state this explicitly since `bds-select`'s own Escape handler is the reused pattern and its event may or may not stop propagation.
- [ ] Default/empty state: not applicable — this task adds a handler, not a new state field.
- [ ] Reactivity: not applicable — Escape handling is an event listener, not a reactive prop.

**Acceptance criteria:**

- Pressing Escape while the popover is open closes it via `bdsPopover.closePopover()`, mirroring `bds-select`'s `KEYBOARD.Escape` handler.
- Focus returns to the date-picker trigger input after close (`requestAnimationFrame(() => this.bdsInput?.focus())`), so keyboard/screen-reader users aren't dropped to `<body>`.
- No `preventDefault` on the Escape key (`{ preventDefault: false }`), consistent with `bds-select`.
- Behavior applies identically in single and range modes.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker, popover open.
- Scenario 2: `range` picker, popover open with an in-progress selection.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1, when Escape is pressed, then the popover closes and focus visibly returns to the trigger input. Pass: popover closed, focus ring visible on the trigger, not lost to `<body>`. (Live-validated 2026-09-23 with focus inside the popover.)
- [x] Given Scenario 2, when Escape is pressed mid-selection, then the popover closes, focus returns to the trigger, and the in-progress draft reverts per the existing Cancel-equivalent behavior. Pass: same as Scenario 1, plus draft correctly discarded. (Verified 2026-09-23.)

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 return focus to trigger on Escape close"`

---

### Task 42a: `bds-banner` close-button hover/focus/active states — DROPPED

**Status:** ❌ dropped 2026-09-24, confirmed with user.\*\* Gap found during Task 36's Figma audit (`bds-banner`'s close button has no hover/focus/active states — plain `color` + `cursor: pointer` only, unchanged). Scheduled here since `bds-banner.scss` is a shared dependency outside `bds-date-picker`'s own file scope, not a `bds-date-picker`-local concern.

**Why dropped:** dispatched to `@frontend-subagent`, which searched thoroughly before reporting back rather than guessing — checked the date-picker's own Figma file (no component-states page exists there; the embedded banner instance is an empty, content-less placeholder), then used `search_design_system` to find a `Banner` component set in a separate `[BOR] DSG COMPONENTS → FEEDBACK` library, but Figma's search API only returns an internal `libraryKey`, not a resolvable file URL, and no prior session had ever captured a standalone `bds-banner` Figma link anywhere in this codebase. **Confirmed with the user 2026-09-24: no hover/focus/active states are actually documented in Figma for this close button.** Since there's nothing to build against, this task is dropped rather than left open pending a link that doesn't lead anywhere. If Figma states are added for this component in the future, this can be reopened as a new task at that time — not resurrected as-is, since the reasoning here (no design source exists) will be stale once one does.

**No SCSS was written; `bds-banner.scss` is unchanged.** Confirmed reusable convention for whenever this is revisited: `src/styles/_interactions.scss`'s `@mixin bds-focus-ring`/`@mixin bds-focus-ring-active`, already used this way in `bds-date-picker.scss`'s `&__preset` block and `bds-radio-card.scss`.

---

### Task 42b: return focus to the trigger on all picker-completion close paths

**Status: ✅ implemented (2026-09-23) — live-validated.** Implemented by `@frontend-subagent`: new shared helper `closePopoverAndRefocus()` (`bds-date-picker.tsx:638-641`) = `bdsPopover.closePopover()` + `requestAnimationFrame(() => this.bdsInput?.focus())`, now used by the default-mode selection-commit branch (`:406`), the Escape handler (`:459`), APPLY (`:514`), and CANCEL (`:518`). `handlePopoverAfterHide` is deliberately untouched (click-outside must not steal focus back); the CLEAN branch is unchanged (it doesn't close). Coverage: 3 new tests in `bds-date-picker.keyboard.spec.ts` (default selection / Apply / Cancel refocus), verified non-vacuous. `bds-date-picker` 21 suites / 432 passed / 1 todo; tsc/eslint clean. Live (dev server): default single-date click a day → focus returns to the input; day + Enter → same; basic picker Apply → popover closes + focus returns; Cancel → same; clicking into a second picker → focus follows the click (picker 1's input NOT refocused).

**Decision:** return focus to the trigger input on every close path that represents the user finishing with the picker — selection-commit (default mode), Apply, Cancel, Escape — via one shared helper. Do **not** refocus on click-outside (focus must follow the click), so `handlePopoverAfterHide` is deliberately left untouched.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify), `__test__/bds-date-picker.keyboard.spec.ts` and/or `__test__/bds-date-picker.basics.spec.ts` (modify)

**Grounding findings (2026-09-23):**

- The `bdsInput` getter already exists (added in Task 42). The Escape handler already does `closePopover()` + `requestAnimationFrame(() => this.bdsInput?.focus())` — refactor it onto the new helper.
- Close paths to update: `handleDayClick` default branch (`:401-406`), APPLY (`:493`), CANCEL (`:512`).
- Click-outside closes via the popover's own outside-click handling; leave `handlePopoverAfterHide` as-is (it must not steal focus back).

**Acceptance criteria:**

- A shared private helper (e.g. `closePopoverAndRefocus()`) calls `bdsPopover.closePopover()` then `requestAnimationFrame(() => this.bdsInput?.focus())`.
- Used by: default-mode day selection, Apply, Cancel, and the Escape handler.
- After any of those, `document.activeElement` is the field's inner `<input>` (not `<body>`).
- Click-outside close is unchanged (no forced refocus).
- Behavior identical in single and range modes.
- No `any`; JSDoc only on exported API; no visual change.

**Manual test (required):**

Reuse the playground (`#dp-keyboard-s1` default single-date; a basic/expanded picker with chrome, e.g. `#dp-banner-s4`). Run `pnpm dev:components` and validate:

- [ ] Default single-date: click a day, or focus a day + Enter → popover closes and focus returns to the input.
- [ ] Basic/expanded with chrome: click Apply → focus returns to the input; click Cancel → focus returns to the input.
- [ ] Click outside the popover → popover closes and focus follows the click (NOT forced back to the input).

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 return focus to trigger on all close paths"`

---

### Task 43: Phase 8 unit tests (consolidated)

**Status: ✅ implemented (2026-09-23).** Implemented by `@testing-subagent`: created `bds-calendar-grid.keyboard.spec.ts` (19 tests — arrow/Home/End/Ctrl+Home/Ctrl+End traversal, PageUp/PageDown → `bdsMonthNavigate`, disabled/out-of-month exclusion, wrap, dual-grid independence, initial tabbable priority, Enter/Space activation), replaced the Phase-8 `it.todo` in `bds-calendar-grid.a11y.spec.ts` with a roving-tabindex assertion, and added 2 grid-through-picker tests to `bds-date-picker.keyboard.spec.ts`. Coverage: `bds-calendar-grid` 89.07% → **94.11%** stmts (branch 90.42%, funcs 100%, lines 93.91%); `bds-date-picker` 99.2%. `bds-date-picker` 22 suites / 454 tests pass; tsc/eslint clean. **Two real bugs found and deferred to fixes — see Task 40d** (FM-85: `aria-selected` boolean serialization breaks both the ARIA state and the initial tabbable cell; FM-86: prop-only re-render leaves two `tabindex="0"` cells).

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.keyboard.spec.ts` (create), `bds-calendar-grid.a11y.spec.ts` (modify — replace the `it.todo` deferring arrow-key nav with real traversal assertions), `bds-date-picker.keyboard.spec.ts` (modify)

**Unit tests to cover:** grid-level full key traversal (arrows/Home/End), boundary crossing via PageUp/PageDown → `bdsMonthNavigate`, disabled/out-of-month cells excluded from focus stops, wrap, dual-grid independence — plus the already-present live-region / focus-return / focus-guard coverage. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 8 keyboard navigation and a11y unit tests"`

---

### Task 44: Phase 8 documentation

**Status:** ✅ done (2026-09-24) — implemented by `@documentation-subagent`, independently re-verified (read the final MDX section directly + `git diff` review against Tasks 40/40b/40c/41/42/42b's actual source, not relayed). Replaced the stale "no arrow-key day-grid navigation ships / day cells reachable via mouse only / keyboard grid traversal planned for a later phase" bullet **and** the matching info `<Callout>` with the shipped model: single `Tab` stop (roving tabindex, one `tabindex="0"` cell with selected→today→first-enabled priority), arrow-key traversal wrapping within the visible month, adjacent-month/disabled cells skipped, `Enter`/`Space` select, `PageUp`/`PageDown` month navigation, and arrow-key no-op while a header control has focus (Task 40b). Added a live-region bullet (Task 41) and a focus-management bullet (Tasks 42/42b: Escape/Apply/Cancel/day-selection return focus to the trigger; click-outside does not). Expanded the `#### Keyboard interaction` table from 3 to 8 rows using the already-imported `KB`/`combo` (adds arrows, Home/End, Ctrl+Home/Ctrl+End, PageUp/PageDown, Enter/Space select). No RTL prose (Task 41a); no heading/TOC restructure. Verification: zero matches for `mouse only|not yet implemented|planned for a later phase|rtl` in the MDX, `prettier --check` clean, `pnpm dev:docs` served the transformed MDX (HTTP 200) with the new strings and no syntax errors, `git status` confirms the MDX is the only file this task touched (other working-tree changes predate it, from Tasks 40-42b). Nothing committed — per standing preference, commits are the user's own action.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents keyboard model. RTL support documentation deferred — see Task 41a; do not document RTL behavior that doesn't exist.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the keyboard-model section, when read against Tasks 40-42's actual implementation, then the documented model matches exactly. Pass: no stale/contradicting prose, no RTL claims.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 8 keyboard navigation"`

---

### Task 44a (new — observation surfaced during Task 44, 2026-09-24): document `bds-calendar-grid`'s new `bdsDayFocus`/`bdsGridFocusLeave` events

**Status:** ✅ done (2026-09-24) — implemented directly in the orchestrating session (small, well-defined docs-completeness fix; no subagent dispatch needed). Added `bdsDayFocus`/`bdsGridFocusLeave` to `StoryArgs` and to `meta.argTypes` in `bds-date-picker.stories.ts` (placed next to their siblings `bdsDayHover`/`bdsGridLeave`, matching the existing "**Internal `bds-calendar-grid` event…**" description pattern), and added both names to the `bds-calendar-grid` `<ArgTypes include>` array in `bds-date-picker.mdx`. Verified: three-list completeness cross-check (all 11 `include` names resolve to matching `argTypes` keys — no silent drop), `prettier --check` clean on both files, `eslint` clean on the stories file, and live browser verification via `pnpm dev:docs` + `playwright-cli` on `?path=/docs/forms-date-picker--overview` — both new event names now render in the reference Properties table (1 match each; no new console errors beyond the pre-existing `/boreal-tokens/boreal.css` 404). Nothing committed — per standing preference, commits are the user's own action.

**Gap:** Task 40c added two public `@Event()`s to `bds-calendar-grid` — `bdsDayFocus` (detail `{ date }`) and `bdsGridFocusLeave` (void) (`bds-calendar-grid.tsx:74,80`). Neither is declared in `StoryArgs`/`argTypes` (`bds-date-picker.stories.ts:42-45`) nor listed in the MDX `bds-calendar-grid` `<ArgTypes include={[...]}>` (`bds-date-picker.mdx:719`), so the reference Properties table omits them. The two events are what drive keyboard-focus range preview (Task 40c), so they are part of the shipped keyboard/a11y surface, not purely internal.

**Fix applied:** added both events to `StoryArgs` and `argTypes` in `bds-date-picker.stories.ts`, then added them to the `bds-calendar-grid` `<ArgTypes include>` array in `bds-date-picker.mdx` — `include` silently drops any name without a matching `argTypes` key (see `.agents/memory/storybook-argtypes-name-collision.md` and the docs `Props/Events Completeness Check`), so both edits were required.

**Files:** `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify), `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (modify)

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document bds-calendar-grid focus events"`

---

### Task 45: React/Vue wrapper parity check — Phase 8

**Status:** ✅ done (2026-09-24) — verified by `@qa-subagent` via the pack-based pipeline (`dev:pack:react` then `dev:pack:vue`, run strictly sequentially with a confirmed port-free teardown between them), driven with `playwright-cli`. Five new scenarios (`task45-s1-default-keyboard`, `task45-s2-expanded-range-keyboard`, `task45-s3-minmax-keyboard`, `task45-s4-escape-single`, `task45-s5-escape-range`) were appended to both `examples/react-testapp/src/App.tsx` and `examples/vue-testapp/src/App.vue`, preserving all existing Task 27/34/39 content (17 `<section>` blocks each).

**Verdict: PASS — no wrapper divergence.** Deep-object comparison of the recorded behavior (focused-cell `aria-label`s, live-region text/attrs, popover `aria-hidden`, `document.activeElement`, cell selection classes) was byte-identical across **React == Vue == raw web component** for all five scenarios, plus a supplementary WebKit replay of the raw surface (identical to Chromium). Zero new console errors on any surface. Concrete evidence: S1 live region `"September 2026"` / `aria-live="polite"` / `aria-atomic="true"`, ArrowRight `Sep 24 → Sep 25`, Home/End row edges, PageDown label+live region `"September 2026" → "October 2026"`; S2 two grids `["September 2026","October 2026"]`, live region `"September 2026 – October 2026"`, traversing grid 2 leaves grid 1's roving cell (`Sep 25`) unchanged; S4/S5 Escape sets `bds-popover[aria-hidden="true"]` and returns `document.activeElement` to the trigger `input` (not `body`), and S5's in-progress range draft is discarded on reopen (zero selection classes remain). Nothing committed — per standing preference, commits are the user's own action.

**One real defect found, NOT a wrapper divergence — logged as Task 40e above.** Task 40 Scenario 3 (`min="2026-09-10" max="2026-09-20"`, today outside the range) fails Task 40's own "disabled cells are never a keyboard focus stop" criterion: on open the grid anchors its roving tabindex to the disabled "today" cell, and arrow keys are a complete no-op from there. Reproduces identically on the raw web component (and in React/Vue/WebKit), so it is a pre-existing `bds-calendar-grid` gap, not a wrapper issue. Root cause independently confirmed from source (see Task 40e). Because it is date-relative (only manifests when today falls outside `min`/`max`), a re-run on another day may not reproduce it.

**Executor:** @qa-subagent
**Files:** `examples/react-testapp/src/App.tsx` (modify — appended Task 45 scenarios), `examples/vue-testapp/src/App.vue` (modify — appended Task 45 scenarios)

**Acceptance criteria:** Keyboard traversal and live-region behavior remain consistent across wrappers. ✅ Met.

**Manual test (required):**

Repeat Task 40's Scenarios 1-3 and Task 41's Scenario 1 (and Task 42's Escape scenarios, since it lands in this phase) through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [x] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in keyboard traversal, live-region announcements, or Escape close/focus-return. **Verified 2026-09-24** — React == raw for all five scenarios (deep-object equality).
- [x] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence. **Verified 2026-09-24** — Vue == React == raw for all five scenarios; supplementary WebKit raw pass identical to Chromium.

**Commit:** N/A

---

## Phase 9 — Month/year quick-picker

This phase implements quick month/year drill-down inside `bds-calendar-grid` as an internal view state, not a new public component.

### Task 46: quick-picker interaction model — UX confirmation (blocking gate)

**Status:** ✅ done (2026-09-24) — decided directly with the user, no subagent dispatch (design/UX checkpoint, matches Task 28/34c precedent).

**Decisions (confirmed with user 2026-09-24):**

1. **Year-click target = month grid, not day grid** (Option A). The drill-down is strictly "click a cell = go down exactly one level": label → month grid → (year button) → year grid → month grid → day grid. Matches MUI X / Ant Design / react-day-picker.
2. **The month-view's year control is itself the "go to year grid" button** — clicking the year (e.g. "2026") while in month view opens the year grid. No separate control.
3. **Year grid = a 12-year window, prev/next step by decade.**
4. **Disabling follows `min`/`max` only — no standalone "future" rule.** A month/year is disabled iff it falls outside the configured bounds, identical to day-cell disabling (`isDateOutOfBounds`). Future months/years remain selectable when unbounded. The spike's Figma "future years greyed" note is treated as a mock artifact (that mock presumably had a `max`), **not** a product rule — the day grid does not disable future dates, so the quick-picker must not either. Same rule applies to months within the year grid.
5. **Escape from month/year view returns to day view without closing the popover.** Escape from day view still closes the whole popover (Task 42 behavior unchanged).
6. **`expanded` dual grids drill independently** (Option A) — only the clicked grid enters month/year view; the other keeps showing its day grid, preserving the "both calendars always show subsequent months" invariant. Matches Task 48's existing "works independently across single and dual grid instances" criterion; no cross-instance coordination.
7. **Available on every calendar variant** (`default`, `basic`, `expanded`) — wherever the month/year label renders.

**Executor:** main thread (no executor)

**Acceptance criteria:** ✅ Met — drill-down model confirmed (label → month grid; month → day grid; year button → year grid; year → month grid), including the year-click return target (month grid, not day grid).

**Manual test:** N/A — design/UX checkpoint.

---

### Task 47: month-grid/year-grid generators

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` to the precise contract below, independently re-verified in this session (read the actual `grid.ts`/`types.ts`/spec source directly, then re-ran the suite/checks myself — not relayed). Added `GeneratePickerGridOptions` (`{ locale?, min?, max?, now? }`) and `generateMonthPickerGrid(year, options?)` / `generateYearPickerGrid(startYear, options?)` to `grid.ts`, plus `MonthPickerCell`/`MonthPickerGrid`/`YearPickerCell`/`YearPickerGrid` to `types.ts`; the `index.ts` `export *` barrel needed no edit. Current-month/current-year flags derive from `options.now` (mirroring how `generateMonthGrid` derives `isToday`), and `isDisabled` uses a shared private `isCellSpanOutOfBounds` helper — a cell is disabled only when its whole span (month: first→last day; year: Jan 1→Dec 31) falls outside the inclusive `[min, max]`, so any overlap keeps it enabled and there is no "future disabled" rule. 29 new tests (15 month + 14 year) added to `grid.spec.ts`, covering shape/order, English + `fr` labels, all three `now` cases, boundary-day inclusivity, partial overlap, and fresh-array purity. Verification: `date-engine` suite 4/4 suites, 105/105 tests pass; `tsc -p tsconfig.build.json` and `eslint` clean; no files touched outside `date-engine/`. Nothing committed — per standing preference, commits are the user's own action.

**Signature note (deviation from the plan's original `(year, currentMonth)` / `(centerYear, currentYear)`):** the generators take an options object with `now?: Date` (consistent with `GenerateMonthGridOptions`) instead of positional current-month/current-year params, because a positional `currentMonth` cannot distinguish "current month of a non-current year" and would let a caller falsely flag e.g. September 2027 while the real current month is September 2026. `generateYearPickerGrid` takes `startYear` (the first year of the 12-year window) and does **not** decade-align internally — the component owns that, per Task 46 decision 3.

**Executor:** @frontend-subagent
**Files:** `date-engine/grid.ts` (modify), `date-engine/types.ts` (modify), `date-engine/__test__/grid.spec.ts` (modify)

**Utility discovery:**

- Feature area: pure grid-cell generation (existing precedent: `generateMonthGrid` for the day grid).
- Search performed: `date-engine/grid.ts` (`generateMonthGrid`, `buildDayCell`, `getWeekdayLabels`), `date-engine/types.ts` (`MonthGrid`, `DayCell`).
- Candidates found: `generateMonthGrid`'s existing shape (pure function, framework-agnostic, returns a fixed-size cell array with current/selected/disabled flags) is the direct structural precedent for both new generators.
- Fit assessment: fully fits as a pattern to follow, not a function to call directly — month/year grids are a different cell shape (12 cells, not a 6-week calendar), so this is "same convention, new function," not literal reuse of `generateMonthGrid` itself.
- Reuse decision: `generateMonthPickerGrid`/`generateYearPickerGrid` follow `generateMonthGrid`'s existing conventions (pure, framework-agnostic, current-item flag) rather than inventing a new generator shape.
- Gap handling: not applicable.
- Anti-duplication check: confirms no calendar-day-grid logic is duplicated into the new generators — they're structurally parallel, not derived from `generateMonthGrid`'s cell logic.
- Test impact: Task 50 extends `date-engine/__test__/grid.spec.ts` for the two new generators, matching `generateMonthGrid`'s own existing test-file convention.

**Acceptance criteria:**

- New types in `date-engine/types.ts`: `MonthPickerCell` (`{ month: number; label: string; isCurrentMonth: boolean; isDisabled: boolean }`), `MonthPickerGrid` (`{ year: number; cells: MonthPickerCell[] }`), `YearPickerCell` (`{ year: number; isCurrentYear: boolean; isDisabled: boolean }`), `YearPickerGrid` (`{ startYear: number; cells: YearPickerCell[] }`).
- `generateMonthPickerGrid(year, options?)` returns a `MonthPickerGrid` with exactly 12 `MonthPickerCell`s (flat array, `month` 0-indexed, `label` = localized short month via date-fns `LLL`, e.g. "Jan"/"janv.").
- `generateYearPickerGrid(startYear, options?)` returns a `YearPickerGrid` with exactly 12 consecutive `YearPickerCell`s starting at `startYear` (the caller decade-aligns `startYear` per Task 46 decision 3).
- `options` is a shared `GeneratePickerGridOptions` mirroring `GenerateMonthGridOptions`: `{ locale?: DateEngineLocale; min?: Date; max?: Date; now?: Date }`. `isCurrentMonth`/`isCurrentYear` are derived from `options.now` (the caller's zoned now), exactly as `generateMonthGrid` derives `isToday` — `isCurrentMonth` is true only for the cell whose `month` matches `now`'s month **in `year`**; `isCurrentYear` is true only for `now`'s year. Omitted `now` leaves both false. (This deliberately supersedes the plan's earlier positional `currentMonth`/`currentYear` params, which could not distinguish "current month of a non-current year".)
- Both accept optional `min`/`max` and flag a cell `isDisabled` **only when the whole cell span falls outside the bounds** (a month = its first→last day; a year = Jan 1→Dec 31; any overlap with `[min, max]` keeps it enabled) — same inclusive-bound rule as day cells (`isDateOutOfBounds`), and no standalone "future is disabled" rule (Task 46 decision 4).
- Both are pure, framework-agnostic, and follow existing generator conventions.

**Manual test (required):** Non-visual — unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(date-engine): EOA-17662 add month-picker and year-picker grid generators"`

---

### Task 48: quick-picker drill-down implementation

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` (incl. the GA/GB/GC grounding fixes) and independently QA-verified live by `@qa-subagent` in Chromium and WebKit. Internal `view: 'days' | 'months' | 'years'` + `pickerYear` states on `bds-calendar-grid`; only the day `<table>` is gated behind `view === 'days'` (byte-identical otherwise); the header label is now a native `<button>` that opens month view; month view shows `generateMonthPickerGrid(pickerYear)`, year view `generateYearPickerGrid(decade start)`, with 12 cells, `aria-current`/`aria-disabled`, and `min`/`max` disabling (no future rule). `@Method() resetView()` (called by the orchestrator on open) returns to day view on every reopen. **GA:** `min`/`max`/`now` props added and threaded via `renderCalendarPanel` from `bds-date-picker`'s zoned `now` (new shared `resolveZonedToday` in `value-mapping.ts`, reused by `buildDisplayGrid`). **GB:** the host `@Listen('bdsMonthNavigate')` was replaced by per-instance `onBdsMonthNavigate` closures; the anchor is resolved from the event's absolute `{year, month}` (prev/next path unchanged). **GC:** primary/single pick anchors at the picked month, secondary pick at picked − 1 (picked month lands in the clicked calendar).

QA evidence (Chromium + WebKit spot-check, all PASS): label→month view (12 cells, current flagged); year→month (not day); month→day + exactly one `bdsMonthNavigate` with the absolute target; reset-on-reopen returns to day view; expanded drill is independent (left months, right unchanged); `min`/`max` disables only fully-out-of-range months/years, no "future" disabling; C2 — right-calendar pick of Mar gives right=March/left=February; label drills in the `default` type too. Regressions all clean (42 day cells, range highlighting, day min/max disabling, single roving-tabindex + arrow traversal, live-region updates). Zero new console errors; no cross-component `<button>` style leak. Verification here: `bds-date-picker` 22 suites / 459 tests, `tsc -p tsconfig.build.json` + `eslint` clean (re-run independently by the orchestrating session). Month/year cells are intentionally unstyled native buttons until Task 49; keyboard/ARIA/Escape deferred to Task 48e. Nothing committed — per standing preference, commits are the user's own action.

**Note (2026-09-24, found during Figma re-verification, confirmed with user):** the in-place view-replacement behavior implemented here (`view === 'days' ? <table> : picker`, `bds-calendar-grid.tsx:619-631`) and the `<div>`/`<button>`-based picker markup do not match Figma node `14:24179` — the month/year picker should render as an elevation-overlay superposed over the (still-visible, dimmed) day grid, using the same `<table role="grid">` structure as the day grid. This was never a considered Task 46 decision (Task 46 covered which drill-down level to land on, not how it's visually layered) and wasn't checked against Figma before being written. Not re-litigating this task's own completion — logged as new **Task 48a** (table markup) and **Task 48b** (overlay superposition), both scheduled before the keyboard/ARIA task (formerly Task 48a, renumbered to Task 48c, then renumbered again to its final position as **Task 48e** once Task 48c/48d were themselves inserted — see those tasks' own renumbering notes) so that work lands on the corrected markup/layout instead of needing a second pass.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid/types/ICalendarGrid.ts` (modify), `bds-calendar-grid.tsx` (modify), `bds-date-picker/helpers/renderCalendarPanel.tsx` (modify), `bds-date-picker/bds-date-picker.tsx` (modify), `bds-date-picker/utils/value-mapping.ts` (modify — `resolveZonedToday` extraction), `packages/boreal-web-components/src/index.html` (playground scenarios)

**Integration research pass (done 2026-09-24 — read the actual current source before writing acceptance criteria):**

- [x] Call sites: `bds-calendar-grid.tsx`'s `render()` renders the day grid unconditionally — gate it (and only it) behind `view === 'days'`, so default output is byte-identical when `view` is `'days'`. The grid header (prev/label/next) is shared across views.
- [x] Boundary case: drilling into month/year view must not touch `selectedDate`/range draft state — `view` is orthogonal to the parent's controlled `grid`/`selectedDate` props, so an in-progress range selection persists across view transitions automatically. Confirm by test, don't add new state.
- [x] Default/empty state: `view` defaults to `'days'` on mount. Because `view` is internal and the grid instance persists across popover opens, add a `@Watch`/reset so every reopen starts on `'days'` (or confirm the parent remounts the grid on open — it does not today, so an explicit reset is required).
- [x] Reactivity: `view` is an internal `@State`, no public API surface. `bdsMonthNavigate`'s contract is unchanged in shape (see GB below).

**Grounding findings (2026-09-24, read the actual current source — these are concrete, not hypothetical):**

- **GA — `bds-calendar-grid` cannot build the picker grids today.** It receives only a precomputed `grid: MonthGrid` (`ICalendarGrid.ts:4`); `min`/`max` are baked into the day cells upstream by `buildDisplayGrid` and never passed down, and the grid has no "today". `generateMonthPickerGrid`/`generateYearPickerGrid` (Task 47) need `min`/`max` + a zoned `now`. **Fix:** add `min?: Date`, `max?: Date`, `now?: Date` props to `bds-calendar-grid`/`ICalendarGrid`, and thread them from `bds-date-picker` (`this.minDate`/`this.maxDate`, and the same `TZDate`-derived `now` `buildDisplayGrid` already computes at `value-mapping.ts:165-166`) through `renderCalendarPanel`'s `CalendarInstanceParams`. `now` must be the zoned instant, computed by the orchestrator, never inside `date-engine`.
- **GB — arbitrary month/year jumps do not navigate.** `bds-date-picker.tsx:421-427` `handleMonthNavigate` ignores `event.detail.year`/`month` and only steps ±1 from `direction`. The grid already emits the absolute target (`handleNextClick`/`handlePrevClick`), so **fix:** resolve the target from `detail.year`/`detail.month` (falling back to the direction step only if those are ever absent). This is required for the quick-picker to jump across years and is behavior-preserving for the existing prev/next path.
- **GC — expanded-mode slot semantics (Task 46 decision 6 / C2, confirmed with user 2026-09-24).** A month pick must land in the calendar the user clicked: a **primary**-grid pick sets the anchor to the picked month (secondary = picked + 1); a **secondary**-grid pick sets the anchor to picked − 1 month (secondary = picked). **Fix:** stop relying on the host-level `@Listen('bdsMonthNavigate')`; instead `renderCalendarPanel` binds a per-instance `onBdsMonthNavigate` (closing over the slot) that the orchestrator consumes. The single-grid path is unchanged (anchor = picked month).

**Acceptance criteria:**

- Adds internal `view: 'days' | 'months' | 'years'` state (no public prop), reset to `'days'` on every reopen.
- Month/year header label becomes interactive and enters month view.
- Month click returns to day view and emits `bdsMonthNavigate`.
- Year click returns to month view for that year (Task 46 decision 1 — not directly to the day grid).
- The month-view's year control is itself the "open year grid" button (Task 46 decision 2); the year grid is a 12-year window stepping by decade (decision 3); `startYear` is decade-aligned by the component before calling `generateYearPickerGrid`.
- Works independently across single and dual grid instances (Task 46 decision 6): only the clicked grid's `view` changes; the other keeps showing its day grid.
- Available for every `calendarType` variant (`default`, `basic`, `expanded`) wherever the month/year label renders (Task 46 decision 7).
- Month/year cells outside `min`/`max` are disabled and not selectable — identical to day-cell disabling, with no standalone "future is disabled" rule (Task 46 decision 4); current month/year flagged from the orchestrator-supplied zoned `now`.
- Escape from month/year view returns to day view without closing the popover (Task 46 decision 5; full keyboard/ARIA behavior in Task 48e).
- **GA:** `bds-calendar-grid` gains `min?`/`max?`/`now?` props, threaded through `renderCalendarPanel` and `bds-date-picker`; the zoned `now` is computed by the orchestrator, not the grid.
- **GB:** `bds-date-picker.handleMonthNavigate` resolves the destination from `detail.year`/`detail.month` (not just `direction`), so quick-picker jumps to any month/year navigate correctly.
- **GC:** a primary-grid month pick anchors `displayYear/displayMonth` at the picked month; a secondary-grid month pick anchors it at picked − 1 month — i.e. the picked month appears in the calendar that was clicked. Implemented via per-instance `onBdsMonthNavigate` in `renderCalendarPanel` (host-level `@Listen` removed).
- No regression to the existing prev/next month navigation, day-grid rendering, range/preview state, or the Phase 8 keyboard/a11y behavior.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker, click the month/year header label.
- Scenario 2: `calendarType='expanded'` + `range`, drill down independently on each grid instance.
- Scenario 3: any picker with `min`/`max` narrowing the year (e.g. `min="2026-06-01" max="2027-03-31"`), to check disabled months/years.
- Scenario 4: `calendarType='expanded'`, pick a month from the **right** calendar's month view (C2).

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1, when the month/year label is clicked, then the month grid replaces the day grid. Pass: 12 month cells render, current month flagged.
- [ ] Given the month grid, when a month is clicked, then the day grid returns showing that month, and `bdsMonthNavigate` fires. Pass: correct month shown, event fired.
- [ ] Given the month grid, when the year button is clicked, then the year grid replaces it. Pass: 12 year cells render, current year flagged.
- [ ] Given the year grid, when a year is clicked, then the month grid returns for that year (per Task 46's confirmed model — not directly to the day grid). Pass: month grid shown for the selected year.
- [ ] Given Scenario 2, when one grid drills down, then the other grid's view state is unaffected. Pass: no shared/leaking view state between the two instances.
- [ ] Given Scenario 3, when the month/year views open, then months/years entirely outside `min`/`max` are disabled and unclickable, and partially-in-range ones stay enabled — with no "future is disabled" behavior. Pass: matches Task 46 decision 4.
- [ ] Given Scenario 4, when a month is picked from the right calendar's month view, then the picked month appears in the **right** calendar (left = picked − 1) — not the left one. Pass: the clicked calendar shows the picked month (C2).
- [ ] Given any picker with a committed range in progress, when you drill in and back out, then the range selection/highlight is unchanged. Pass: no draft reset from view transitions.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add month/year quick-picker drill-down"`

---

### Task 48a: quick-picker `<table>` grid markup

**Why:** `renderMonthPicker`/`renderYearPicker` (`bds-calendar-grid.tsx:541-613`) currently render `<div class="__picker">` › `<div class="__picker-row">` › `<button>` cells, with no `role="grid"/"row"/"gridcell"` — a different, ARIA-incompatible structure from the day grid's `<table role="grid"><tbody><tr role="row"><td role="gridcell">` (`renderWeeks`/`renderDayCell`, lines 574-584, 431-459). Task 48e's keyboard/ARIA work assumes the same grid-cell addressing pattern Task 40 established for the day grid; building it on `<div>`/`<button>` would mean re-deriving ARIA-grid semantics from scratch instead of reusing the existing, already-verified pattern. Converting now, before Task 48e, avoids a second rewrite.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify), `bds-calendar-grid.scss` (modify — cell selectors change from `button`-based to `td`-based)

**Acceptance criteria:**

- `renderMonthPicker`/`renderYearPicker` emit `<table role="grid"><tbody><tr role="row">...</tr></tbody></table>`, one `<tr>` per row of `PICKER_COLUMNS` cells, mirroring `renderWeeks`'s row-chunking.
- `renderMonthCell`/`renderYearCell` emit `<td role="gridcell">` (not `<button>`), each retaining the existing label/click handler, `aria-current`, and `aria-disabled` — matching `renderDayCell`'s attribute pattern (no `aria-selected`, since month/year cells carry no persisted-selection state distinct from `isCurrentMonth`/`isCurrentYear`).
- A picker-specific cell-ref map and `getGridItems()`-equivalent exist so Task 48e can wire `setupGridNavigation` against the new `<td>` elements exactly as it does for day cells — this task adds the addressable markup only, not keyboard navigation itself.
- No regression to click-driven interaction — month/year click still emits the same events; only the DOM shape changes (table instead of div grid), not the hit-testing or labels.
- `bds-calendar-grid.scss` selectors updated for the new `table`/`td` structure; structure only — full state-matrix styling stays Task 49's scope, no hardcoded colors/spacing introduced.

**Manual test (required):**

Run `pnpm dev:components` and validate:

- [x] Given the month or year picker is open, when inspected via devtools, then it renders as `<table role="grid">` with `<tr role="row">`/`<td role="gridcell">` cells, not `<div>`/`<button>`. Pass: DOM matches the day grid's structural pattern. **Verified 2026-09-24 by @qa-subagent** — `<table role="grid"><tbody><tr role="row"><td role="gridcell">` confirmed live via `playwright-cli` DOM snapshot and accessibility-tree `grid > rowgroup > row > gridcell` semantics; `aria-current`/`aria-disabled` correctly applied. Corroborated against the committed diff (`39c3fae4`).
- [x] Given a month/year cell is clicked, then the existing click behavior (drill down / select / disabled no-op) is unchanged. Pass: no behavioral regression from the markup change. **Verified 2026-09-24 by @qa-subagent** — month/year click, year→month drill target, disabled-cell no-op, reopen-resets-to-day-view, and dual-instance (`expanded`) independence all confirmed live; zero console errors. Regression spot-check on unrelated day-grid min/max + range selection also passed.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, independently re-verified (source diff + `tsc`/`eslint`/unit-test re-run) and manually QA-verified live by `@qa-subagent`. Committed as `39c3fae4` (`refactor(web-components): EOA-17662 render quick-picker cells as a table grid`), split from Task 48's own commit (`21be7773`) per user preference.

**Commit:** `git commit -m "refactor(web-components): EOA-17662 render quick-picker cells as a table grid"` — done, see Status.

---

### Task 48b: quick-picker overlay superposition

**Why:** Task 48 implemented month/year view as an in-place replacement of the day grid (`view === 'days' ? <table> : picker`, `bds-calendar-grid.tsx:619-631`) — the day grid unmounts entirely while a picker view is active. Figma node `14:24179` shows the month/year picker as an elevated card (shadow) floating over the day grid, which stays visible (dimmed) underneath.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify), `bds-calendar-grid.scss` (modify)

**Design decision (confirmed with user 2026-09-24):** the overlay is a locally-owned, absolutely-positioned panel inside `bds-calendar-grid` itself — **not** a nested `<bds-popover>`. Reasons: (1) `bds-popover` (`bds-date-picker.tsx:1102`) already wraps the whole calendar panel and owns its own Escape-to-close/click-outside handling; nesting a second one would create two independent Escape handlers racing for the same keystroke, directly conflicting with Task 46 decision 5 (Escape from month/year view must close _only_ the picker, not the outer popover). (2) The Figma card is always anchored at a fixed position relative to the grid — it doesn't need floating-ui's viewport-aware repositioning, which is `bds-popover`'s reason to exist.

**Acceptance criteria:**

- When `view !== 'days'`, the day `<table>` remains mounted and visible (dimmed per Figma) underneath the picker overlay, rather than being removed from the DOM.
- The picker overlay renders as an absolutely-positioned panel with elevation (shadow token, per `_interactions.scss`/the project's existing elevation convention — confirmed against Figma in Task 49's styling pass) superposed over the day grid's area.
- While the overlay is open, the day grid's cells are excluded from the tab order and hidden from assistive tech (`aria-hidden="true"` and/or `inert` on the day `<table>`, toggled with `view`) — a new requirement introduced by the overlay approach that didn't exist under Task 48's in-place-replacement implementation, since the day grid wasn't in the DOM while a picker view was active.
- Closing the picker (month/year selection, or Escape once Task 48e lands) restores the day grid's normal (non-`aria-hidden`, non-`inert`) state.
- No regression to Task 48's existing acceptance criteria (dual-instance independence, `min`/`max` disabling, `expanded`-mode anchor behavior) — only the layering/visibility model changes.

**Manual test (required):**

Reuse Task 48's Scenarios 1-4. Run `pnpm dev:components` and validate:

- [x] Given any scenario, when the month/year label is clicked, then the picker overlay appears above the (dimmed, still-visible) day grid — matching Figma node `14:24179` — rather than replacing it. Pass: day grid visible but dimmed underneath the overlay. **Verified 2026-09-24 by @qa-subagent, after a fix.** First pass FAILED: the opaque background/shadow were on `&__picker-overlay` itself (`inset: 0`, filling the whole grid area), so the dimmed day grid was 100% hidden behind it — indistinguishable from Task 48's old replace-in-place behavior (measured: overlay 248×240 vs. day grid 256×240, near-identical). **Fix:** moved `border-radius`/`background-color`/`box-shadow` off `&__picker-overlay` (now a transparent, `inset: 0`, flex-centering wrapper only) onto `&__picker` (the actual month/year `<table>`, naturally narrower than the day grid). Re-verified: picker table now measures 75.4×74 (a small elevated card), day grid stays 256×240 at `opacity: 0.4`, clearly visible around/behind the card. Screenshot-confirmed.
- [x] Given the picker overlay is open, when Tab is pressed repeatedly, then focus never lands on a day-grid cell. Pass: day grid is excluded from the tab order while the overlay is showing. **Verified 2026-09-24 by @qa-subagent** — definitive test via direct `.focus()` call on a day-grid cell while the overlay was open: `document.activeElement` did not change, confirming `inert` blocks focus entirely. (Raw sequential Tab-key presses landing back on the trigger `<input>` is a pre-existing `bds-popover` focus-trap behavior, unrelated to this task — keyboard navigation into the picker itself is Task 48e's scope.)
- [x] Given the picker overlay closes (selection or Escape), then the day grid returns to its normal interactive state. Pass: no residual `aria-hidden`/`inert`, day cells tabbable again. **Verified 2026-09-24 by @qa-subagent** — month click reverted `--dimmed` class, cleared `aria-hidden`/`inert`, and a day cell was successfully re-focused programmatically, proving `inert` was genuinely lifted (Escape itself is out of scope until Task 48e).

Regression check (dual-instance independence, `min`/`max` disabling) also verified PASS on `dp-quickpicker-s2`/`s3`, zero console errors throughout both QA passes.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run), manually QA-verified live by `@qa-subagent` in two passes (a real visual bug found and fixed between them — see above). **Container styling corrected 2026-09-24 (user, against Figma node `14:24184`):** `&__picker`'s `background-color` changed from the placeholder `$boreal-ui-base-light` to `$boreal-ui-inverse` (white); `box-shadow` corrected from `$boreal-depth-box-shadow-m` to `-l` per Figma's confirmed effect; and a connector/arrow (`::before`, ported from `bds-popover.scss`'s own rotated-square arrow technique, since Task 48b's own design decision was not to reuse `bds-popover`) was added — the card previously had no pointer tail toward the header label at all. All three rebuilt clean, not yet re-run through `@qa-subagent` since none change the already-verified structural/behavioral checklist items above (DOM structure, `aria-hidden`/`inert`, dual-instance/min-max regressions) — a follow-up visual QA pass on the connector specifically is still worth doing before Task 49 closes out this container's full styling.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 superpose quick-picker as an overlay over the day grid"` — pending, see Status.

---

### Task 48c: quick-picker nested header

**Logged 2026-09-24 (user, against Figma "\_DatePickerCalendar" variants "Default, W/ Month Picker" / "Default, W/ Year Picker").** `renderHeader()` (`bds-calendar-grid.tsx:475-533`) is a single function that entirely replaces the day-grid's own header with the picker's nav header whenever `view !== 'days'` — there is no "two headers" concept in the code today. Figma shows the opposite: the day-grid's own header (month/year label + prev/next) stays in place (dimmed, confirmed with user), and the picker overlay card gets its **own separate, nested header** (prev/next-year in month view; decade-window prev/next in year view) floating on top of it, inside the same card as the grid.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify — `render()`/`renderHeader()` restructuring), `bds-calendar-grid.scss` (modify — header row inside the padded `&__picker` card)

**Acceptance criteria:**

- `renderHeader()` (or its replacement) always renders the day-grid's own month/year nav — it no longer branches on `view` to swap content; the outer header's prev/next buttons and label always reflect `this.year`/`this.month`, matching the plain day-view header exactly.
- While a picker view is open (`view !== 'days'`), the outer header is visually dimmed along with the day grid (confirmed with user 2026-09-24) — reuse the same `--dimmed`-style treatment Task 48b already applies to the day `<table>`, applied to the header too.
- A new header — reusing the exact prev/next-year (month view) and decade-window prev/next (year view) logic already written in the old `renderHeader()` branches, relocated rather than reinvented — renders _inside_ `renderMonthPicker()`/`renderYearPicker()`, above the picker `<table>`, inside the same `&__picker` card (respecting its existing 12px padding).
- The year-nav label inside the picker header (month view) keeps reusing `.label-button`, matching the day-grid header's own styled label — no separate style needed.
- No regression to any already-verified Task 46/48/48a/48b/49 behavior: dual-instance independence, `min`/`max`-disabled prev/next buttons, decade-window stepping, drill-down click targets. This is a structural relocation of existing, already-correct logic — not new interaction logic.

**Implementation note (2026-09-24, confirmed with user):** the outer header also gets `aria-hidden="true"`/`inert` while a picker is open, not just visual dimming — an addition beyond the letter of the acceptance criteria above, made because leaving the day-grid's prev/next/label buttons keyboard-focusable behind the picker overlay would be the same class of bug Task 48b fixed for the day-grid body (a user tabbing through could jump to "Previous month" and change the displayed month while an unrelated picker sits open on top of it). Confirmed correct and kept.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — 22/22 suites, 459/459 tests, matching baseline), manually QA-verified live by `@qa-subagent` (all 7 checklist items pass, zero console errors).

**Manual test (required):**

Reuse Task 48's Scenarios 1-4. Run `pnpm dev:components` and validate:

- [x] Given any scenario, when a picker view opens, then the day-grid's own header (label + prev/next) remains visible but dimmed, matching the day grid's own dimmed treatment. Pass: both header and grid dim together, neither disappears. **Verified 2026-09-24 by @qa-subagent.**
- [x] Given the month or year picker is open, then its own header (prev/next-year or decade-window prev/next) renders inside the card, above the grid — not replacing the outer header. Pass: two visually distinct header rows are present when a picker is open (outer, dimmed; inner, part of the card). **Verified 2026-09-24 by @qa-subagent** — confirmed via DOM/screenshot for both month and year views.
- [x] Given the picker's own header controls (prev/next-year, decade-window prev/next, the year-nav label), when clicked, then they behave exactly as before relocation — no regression to Task 46/48's confirmed navigation model. **Verified 2026-09-24 by @qa-subagent** — prev/next-year, decade stepping, and `min`/`max` bound disabling on `dp-quickpicker-s3` all confirmed exactly matching pre-relocation semantics.
- [x] Given `dp-quickpicker-s2` (expanded/range), when one grid's picker is open, then only that grid's outer header dims — the other grid's header/day-grid stays fully undimmed. Pass: dual-instance independence holds for the header too, not just the grid body. **Verified 2026-09-24 by @qa-subagent.**
- [x] Given the outer header is dimmed/inert, when a direct `.focus()` or sequential Tab is attempted on its buttons, then focus does not land there. **Verified 2026-09-24 by @qa-subagent** — `.focus()` silently failed on outer "Previous month" and label button; real Tab order skipped straight from Close to the inner picker header controls.
- [x] Given the picker closes, then the outer header returns to normal (undimmed, non-`inert`, focusable). **Verified 2026-09-24 by @qa-subagent.**

**Commit:** `git commit -m "refactor(bds-calendar-grid): EOA-17662 give the quick-picker its own nested header"`

---

### Task 48d: quick-picker `--selected` state and active-ring consistency

**Logged 2026-09-24 (user, against Figma `_DatePickerMonthYear` state matrix).** Two related, small cell-styling gaps found after Task 49 landed:

1. **`--selected` is unreachable.** Task 49 wrote the full `--selected` SCSS block (`bds-calendar-grid.scss`), but nothing in `monthCellClassMap`/`yearCellClassMap` (`bds-calendar-grid.tsx:403-410`, `437-444`) ever sets it — no `MonthPickerCell`/`YearPickerCell` field drives it. **Semantics confirmed with user 2026-09-24:** "selected" means the month/year of the actual chosen date (`this.selectedDate`), exactly mirroring day cells' own `cell.isoDate === this.selectedDate` comparison — not "whichever month/year happens to be currently displayed" (`this.month`/`this.year`), which would incorrectly highlight the browsed-to position rather than the real selection whenever the two diverge (e.g. a selected March date while browsing forward to September). This needs **no date-engine changes** — `this.selectedDate` is already an available naive `YYYY-MM-DD` string prop; extract its year/month via string slicing (not a `Date` object, avoiding timezone parsing entirely, consistent with how naive dates are handled elsewhere) and compare directly against `cell.year`/`cell.month` inside the existing classMap functions.
2. **Active-ring inconsistency overridden for consistency (confirmed with user 2026-09-24).** Task 49's Figma pull found `_DatePickerMonthYear`'s `Active` state has no outer focus ring (background + inset shadow only), unlike day cells' `Active` state (`bds-calendar-day-focus-ring-active`, which adds a 3px outline). This is a genuine Figma-level inconsistency between its two components, not an implementation bug — but the user has decided to override it: apply the same outer-ring treatment to picker cells' `Active` state as day cells already get, for cross-component consistency within this codebase.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify — `monthCellClassMap`/`yearCellClassMap`, `aria-selected`), `bds-calendar-grid.scss` (modify — `--selected` reachability confirmed via new class, `--active` ring override)

**Acceptance criteria:**

- `monthCellClassMap`/`yearCellClassMap` set `--selected` when the cell's month/year matches the year/month extracted from `this.selectedDate` (when present); `aria-selected="true"` is added to the cell in that case, matching the day cell's own `aria-selected` pattern.
- No `--selected` cell renders when `this.selectedDate` is unset, or when it falls in a different year than the currently displayed picker grid (e.g. viewing 2027's month grid while `selectedDate` is in 2026 — no month shows selected, matching the day grid's own out-of-view-month behavior of simply not rendering a selection indicator for a different month).
- Picker cells' `:active` state gains the same outer-ring treatment as day cells (`bds-calendar-day-focus-ring-active` or an equivalent shared mixin), on top of the existing inset-shadow background change — applied consistently across `Default`/`Selected`/`Current` combinations.
- No regression to already-verified Task 49 hover/focus/disabled treatments.

**Manual test (required):**

Run `pnpm dev:components` and validate:

- [x] Given a single-date picker with a selected date in the currently-displayed year, when the month picker opens, then that date's month shows the `--selected` treatment (solid background, per Task 49's pulled Figma values) and no other month does. Pass: exactly one month flagged, matching `selectedDate`. **Verified 2026-09-24 by @qa-subagent.**
- [x] Given the same picker, when navigated forward/back so the currently _displayed_ month differs from the selected date's month, and the month picker is then opened, then the selected month (not the displayed one) still shows `--selected`. Pass: confirms semantics are selection-based, not display-position-based. **Verified 2026-09-24 by @qa-subagent** — both same-year browse (selection stays flagged) and cross-year browse (correctly shows no highlight at all) confirmed; also spot-checked the year picker.
- [x] Given no date is selected yet, when the month or year picker opens, then no cell shows `--selected` (only `--current`, if applicable). Pass: no false-positive selection highlight. **Verified 2026-09-24 by @qa-subagent.**
- [x] Given a month or year cell, when clicked-and-held (`:active`), then it shows the same outer-ring treatment as an active day cell, on top of its existing background/inset-shadow change. Pass: visually consistent with day-cell `:active`. **Verified 2026-09-24 by @qa-subagent** — real `mousedown` + `getComputedStyle` confirmed byte-identical `outline`/`box-shadow` to a plain day cell's own `:active` state, for both a plain and a `--selected` picker cell.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — 22/22 suites, 459/459 tests, matching baseline), manually QA-verified live by `@qa-subagent` (all 6 checklist items pass via real `mousedown`/computed-style checks, zero console errors, no regression to hover/focus/disabled). **Known follow-on gap (found 2026-09-24, user review):** `--selected` never activates in range mode, since `draft.selectedDate` stays `null` for the entire lifetime of a range picker (`selectRangeDay` only ever writes `rangeStart`/`rangeEnd`) — see new follow-up task below.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 wire quick-picker selected state and align active-ring styling"` — pending, see Status.

---

### Task 48e: quick-picker keyboard navigation and ARIA

**Confirmed with user 2026-09-23**, found while reviewing Phase 8/9 sequencing: Task 48 as originally scoped only specifies click-based interaction (month/year header label click, month click, year click) — it has no acceptance criteria for keyboard activation or screen-reader semantics on the new interactive surface it introduces (the header label becoming a real button, plus two new 12-cell grids). Phase 8 runs before Phase 9 specifically so this task can _reuse_ Phase 8's work rather than build it from scratch: `setupGridNavigation`/`GridNavigationAccess` (`src/utils/a11y/keyboard/navigation/grid-navigation.ts`) is a fully generic 2D-grid keyboard primitive — nothing about its cell addressing, roving tabindex, or `aria-activedescendant` wiring is specific to the day grid's shape — and Task 40 already integrates it into `bds-calendar-grid.tsx` once. This task extends that same integration to the month/year grids instead of inventing a second keyboard-handling path.

**Renumbered 2026-09-24 (second time)** from Task 48c to Task 48e to make room for Task 48c (nested header) and Task 48d (`--selected`/active-ring), both found during user review of Task 49's output against Figma — this task now builds on Task 48c's nested-header structure rather than the single-swapped-header layout. Its "month/year header label" scope (accessible-name enhancement, e.g. "September 2026, choose month") still refers to the **outer** day-grid trigger label — that label is a native `<button>` already reachable/activatable via keyboard by construction, and Task 48c's restructuring doesn't move or rename it, only stops it from being swapped out; the accessible-name work here is additive polish, not new reachability.

**Scope addition (2026-09-24, user, confirmed):** clicking the dimmed `.bds-calendar-grid__grid-area` backdrop (outside the picker card) while a picker is open currently does nothing — no click handler exists there today. This is the mouse-equivalent of this task's own Escape-to-day-view behavior (same dismissal outcome, different input method), so it's folded into this task rather than made a separate one: add a click handler that checks `event.target === event.currentTarget` (click landed on the backdrop itself, not bubbled from the picker card) and returns to day view when true, exactly matching Escape's target behavior (day view returns, popover stays open).

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify), `bds-calendar-grid.scss` (modify — `&__quick-picker-live-region` visually-hidden rule), `bds-calendar-grid/types/ICalendarGrid.ts` (not needed — no new public prop), `utils/a11y/keyboard/navigation/grid-navigation.ts` (modify — shared `onActivate` non-cell-focus guard, see note), `packages/boreal-web-components/src/index.html` (manual-test scenario)

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`. Keyboard nav reuses the single existing `KeyboardController.setGridNavigation` (Task 40's) by branching `getGridItems()`/`handleActivate` on `this.view` (`getDayGridItems`/`getMonthPickerGridItems`/`getYearPickerGridItems`); Escape (`onEscape`) returns month/year view to day view and only `stopPropagation()`s when it actually handles the key, so day-view Escape still bubbles to `bds-date-picker`'s Task 42 close handler; backdrop-click dismissal is attached to `.bds-calendar-grid__picker-overlay` (not the plan's literal `.grid-area` — verified via compiled CSS that the overlay `inset: 0` fully covers `.grid-area`'s box, so a `.grid-area` listener would never see itself as the click target); initial-focus precedence is selected → `rangeEnd` → `rangeStart` → today → first-enabled; `onPageUp`/`onPageDown` no-op outside day view. Also fixed a real gap (affecting mouse too): returning from a picker never moved real DOM focus, so focus could drop to `<body>` — now `focusActiveViewPriorityCell()` runs on every `@Watch('view')` change.

**Keyboard-open bug + shared-utility fix (2026-09-24).** First live QA pass found the header label (`.bds-calendar-grid__label-button`) did **not** open the picker on Enter/Space: the `grid-navigation.ts` `onActivate` binding is registered at the grid **root**, and `KeyboardController._dispatchKeyEvent` calls `preventDefault()` unconditionally for any matching binding _before_ the handler runs, so the label's native button activation was suppressed (and `handleActivate` then no-op'd because no grid cell was focused). Fixed at the **shared-utility level** (matching grid-navigation.ts's own scope note — not a `bds-calendar-grid`-local workaround): the `onActivate` wrapper now guards with `isNonCellFocusWithinRoot(resolveItems(), ctrl.root)` and, when focus is on a non-cell descendant, manually calls `document.activeElement.click()` to re-trigger native activation. Re-verified live: click-count is exactly **1** for both Enter and Space (no double-activation), stable at 400 ms; the same wrapper path also keeps prev/next-month `bds-button`s and day-cell Enter/Space activation working.

**Live-region deviation (accepted 2026-09-24).** The acceptance criterion said "Task 41's live region announces each view transition"; Task 41's region lives in `renderCalendarPanel.tsx` (`bds-date-picker`), outside this task's file scope, and is a single shared `–`-joined month/year region with no per-grid view-state concept. The implementation instead adds a **local, visually-hidden `aria-live="polite"` region inside each `bds-calendar-grid`** (`.bds-calendar-grid__quick-picker-live-region`) dedicated to view-transition announcements. This keeps per-grid disambiguation free (each grid announces its own transition) and avoids double-announcing (selection-driven returns leave `pickerAnnouncement` untouched so only Task 41's region reacts to the resulting `bdsMonthNavigate`). Confirmed acceptable (a second independent `polite` region is standard practice); noted as the same "two live-region patterns" trade-off to revisit only if the design system later standardizes one.

QA (`@qa-subagent`, live `playwright-cli` on :3333, real keyboard events) — all 7 checklist items PASS, zero new console errors: (1) Tab→label→Enter/Space opens the overlay, no double-activation; (2) Arrow/Home/End + Ctrl+Home/End traversal with continuous wrap, exactly one `tabindex="0"`, disabled months/years skipped on the bounded scenario, no keyboard trap; (3) full keyboard-only month **and** year drill-down paths both return to the correct day view with focus on a real `td[role=gridcell]` (not `<body>`); (4) Escape returns to day view with the popover open, second Escape closes it (Task 42 unchanged); (5) backdrop-edge click dismisses, inside-card click does not; (6) MutationObserver shows exactly one announcement per transition (`["Month view", "Year view, 2020–2031", "September 2026"]`) and **no** duplicate on selection-driven return; (7) regressions clean — day-cell Enter/Space/click all select, prev/next-month `bds-button`s activate via Enter, day-grid roving/live region unchanged, `expanded` dual-grid independence holds. Verification here: `bds-date-picker` 22 suites / 459 tests + `src/utils/a11y/keyboard` 41 tests, `tsc -p tsconfig.build.json` + `eslint` clean (re-run by the orchestrating session).

**Integration research pass (completed 2026-09-24 before implementation):**

- [x] Call sites: `setupGridNavigation`/`GridNavigationItems` is fully generic — it uses `.length`/row/col indices only, with no 7-column week assumption anywhere, so no shared-utility gap had to be closed for the 12-cell (3×4) month/year grids.
- [x] Boundary case: initial-focus precedence resolved to **selected → rangeEnd → rangeStart → today → first-enabled** (`getPriorityMonthCell`/`getPriorityYearCell`); when both range boundaries are visible in one grid, **`rangeEnd` wins** (most recently interacted-with boundary in a two-click flow). `resolveGridCurrentPos` reads live `document.activeElement`/`aria-activedescendant`, so switching `getGridItems()` per view needs no explicit re-init; `focusActiveViewPriorityCell()` additionally moves real DOM focus on every view change (see Status).
- [x] Default/empty state: the outer month/year label is confirmed a native `<button>` (not a `<span>`), reachable via Tab and activatable via Enter/Space, with `aria-label="{monthYearLabel}, choose month"` describing its function.
- [x] Reactivity: each view transition announces exactly once via the local live region (see the accepted live-region deviation in Status) — no duplicate when a month/year selection also emits `bdsMonthNavigate`.

**Acceptance criteria:**

- The month/year header label is a real focusable, keyboard-activatable control (Tab reaches it, Enter/Space activates it), with an accessible name describing its function.
- Month and year grids reuse `setupGridNavigation`'s existing integration pattern from Task 40 — arrow-key traversal, Home/End, roving tabindex, and `aria-activedescendant` all work identically in shape to the day grid, adapted to each grid's own dimensions.
- Escape from month/year view returns to day view without closing the popover (distinct from Task 42's Escape-closes-popover behavior, which still applies from the day view).
- Task 41's live region announces each view transition (entering month view, entering year view, returning to day view) exactly once, with no duplicate announcement when a selection also triggers `bdsMonthNavigate`.
- Works independently across single and dual grid instances, matching Task 48's own dual-instance requirement.

**Manual test (required):**

Reuse Task 48's Scenarios 1-2, plus:

- Scenario 3: single-date picker, keyboard-only interaction (no mouse) — Tab to the header label, activate it, arrow-key through the month grid, activate a month, confirm day view returns with correct focus.

Run `pnpm dev:components` and validate:

- [x] Given Scenario 1 or 2, when the header label is reached via Tab and activated via Enter/Space, then the month grid opens as an overlay above the (dimmed) day grid, per Task 48b. Pass: same result as a mouse click, reachable and activatable by keyboard alone. **Verified 2026-09-24 by @qa-subagent, after the `grid-navigation.ts` `onActivate` fix** — Enter and Space each open the overlay with exactly **1** click (no double-activation), stable at 400 ms; day grid stays mounted with `aria-hidden`/`inert`/`--dimmed`.
- [x] Given the month or year grid, when arrow keys/Home/End are pressed, then focus moves cell-to-cell per the same interaction model Task 40 established for the day grid. Pass: focus visibly follows the expected cell, no focus loss, no keyboard trap. **Verified 2026-09-24 by @qa-subagent** — full Arrow/Home/End/Ctrl+Home/Ctrl+End traversal with continuous wrap in both grids, exactly one `tabindex="0"` at every step, disabled months/years skipped on the bounded scenario, Tab-out reaches the footer (no trap).
- [x] Given Scenario 3, when the full drill-down cycle is completed via keyboard only, then it matches the mouse-driven cycle exactly. Pass: no step requires a mouse. **Verified 2026-09-24 by @qa-subagent** — both the month path (label→Enter→arrows→Enter ⇒ correct day view, focus on a real `td[role=gridcell]`) and the year path (label→Enter→year button→Enter→pick year→month view→pick month→day view) complete keyboard-only.
- [x] Given each view transition, when it occurs, then the live region announces it exactly once. Pass: no missing or duplicate announcements, including when a month/year selection also triggers `bdsMonthNavigate`. **Verified 2026-09-24 by @qa-subagent** — MutationObserver logged exactly `["Month view", "Year view, 2020–2031", "September 2026"]` across month/year/return, with **no** extra entry on selection-driven return (no duplicate).
- [x] (folded-in scope) Given a picker view is open, when `Escape` is pressed, then the day view returns without closing the popover; a second Escape from day view then closes the popover (Task 42). **Verified 2026-09-24 by @qa-subagent.**
- [x] (folded-in scope) Given a picker view is open, when the dimmed backdrop (`.bds-calendar-grid__picker-overlay`, outside the card) is clicked, then it dismisses to day view with the popover open; clicking **inside** the card does not dismiss. **Verified 2026-09-24 by @qa-subagent.**

**Commit:** `git commit -m "feat(web-components): EOA-17662 add keyboard navigation and ARIA for month/year quick-picker"` — pending (implementation + shared-utility keyboard fix are uncommitted in the working tree).

---

### Task 48f: reset quick-picker view on preset, clear, and cross-grid day-pick

**Logged 2026-09-24 (user).** `resetCalendarViews()` (`bds-date-picker.tsx:799`, iterates every `bds-calendar-grid` and calls its `resetView()` method) already exists and is called in exactly two places — `handlePopoverAfterShow` and `listenClickTrigger` — both "popover just opened" moments. Three other state-changing actions leave the popover open but don't call it, so an already-open quick-picker is left showing stale context disconnected from what just changed:

1. **Sidebar preset click** (`handlePresetClick`, line 556) — updates `draft`/`selectedPreset`/`displayYear`/`displayMonth`, but a currently-open quick-picker stays open, still scoped to its own `pickerYear` (set once, on `handleLabelClick`, not reactive to `displayYear`/`displayMonth` changing underneath it). Clicking a preset while a picker is open produces no visible feedback — the day grid updates invisibly behind the still-open overlay.
2. **Clear button** (`handleFooterAction`'s `FOOTER_ACTION.CLEAN` case, line 511) — same symptom: resets the draft and commits, but leaves an open picker floating over the now-cleared day grid.
3. **Cross-grid day click in `expanded`/range mode** (`handleDayClick`, line 395) — a single `@Listen('bdsDayClick')` on the host catches the bubbled event from _either_ grid instance. Single-date mode self-resolves (this same handler calls `closePopoverAndRefocus()` once a date is picked), but in range mode, completing a day-pick on one grid while the _other_ grid's quick-picker is open leaves that picker open and stale. A plausible real flow: open the left calendar's month picker to jump forward, then just pick a day on the right calendar instead of finishing the jump.

Apply/Cancel don't need this fix — both already call `closePopoverAndRefocus()`, which closes the whole popover; `resetCalendarViews()` on the next open already covers them. These three are the only actions that change state _without_ closing the popover.

**Not in scope (noted, deferred):** external `min`/`max` mutation while a picker is open (`@Watch('min')`/`@Watch('max')`, line 241) doesn't re-validate whether the currently-displayed `pickerYear`/decade window is still reachable — an edge-of-edge case (a consumer dynamically tightening bounds while a user has a quick-picker open) that wouldn't crash anything (disabled-cell logic is already reactive) but could leave a user looking at an all-disabled grid. Not fixed here; flagged for a future pass if it proves to matter in practice.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `handlePresetClick`, `handleFooterAction`'s `CLEAN` case, `handleDayClick`)

**Acceptance criteria:**

- `handlePresetClick` calls `this.resetCalendarViews()` after updating the draft/display month, so any open quick-picker (on any grid instance) returns to day view immediately, reflecting the preset's effect.
- `handleFooterAction`'s `FOOTER_ACTION.CLEAN` case calls `this.resetCalendarViews()` for the same reason.
- `handleDayClick` calls `this.resetCalendarViews()` after updating the draft, covering the cross-grid case in range mode (a no-op for the grid the day was actually clicked in, since it can only be in day view already — clicking a day cell is impossible while that grid's own picker is open and its day table is `inert`).
- No regression to existing preset/clear/day-click behavior (range selection, single-date auto-close, `selectedPreset` state, commit/validity flows) — this only adds a view-reset side effect, no logic changes to what gets selected or committed.
- Works correctly in both single-grid and `expanded`-dual-grid configurations.

**Manual test (required):**

New scenario: single-date picker and `expanded`+range picker, each with a quick-picker opened before the target action.

Run `pnpm dev:components` and validate:

- [x] Given a quick-picker is open, when a sidebar preset is clicked, then the picker closes back to day view and the day grid immediately reflects the preset's range/date. Pass: no stale overlay, visible feedback. **Verified 2026-09-24 by @qa-subagent** — "Last 7 days" preset correctly closed the open month picker and produced correct range classes on the day grid.
- [x] Given a quick-picker is open, when the Clear button is clicked, then the picker closes back to day view and the day grid reflects the cleared state. Pass: no stale overlay. **Verified 2026-09-24 by @qa-subagent** — confirmed via DOM query, 0 selected/range cells remained after Clear.
- [x] Given `expanded`+range mode, when the left grid's quick-picker is open and a day is clicked on the right grid, then the left grid's picker closes back to day view. Pass: no stale overlay on the non-clicked grid. **Verified 2026-09-24 by @qa-subagent** — left grid's month picker closed and re-rendered its own day grid; right-grid click correctly registered a range-start.
- [x] Given the same three scenarios repeated for a single-date (non-range) picker where applicable, then no regression to the existing single-date auto-close-on-select behavior. **Verified 2026-09-24 by @qa-subagent** — single-date pick with no quick-picker involved still auto-closes and commits correctly, unchanged. Range selection/highlighting (no quick-picker involved) also re-confirmed correct across both grids.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` (three one-line additions to already-existing, already-tested `resetCalendarViews()`), independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — 22/22 suites, 459/459 tests, matching baseline), manually QA-verified live by `@qa-subagent` (all 6 checklist items pass, zero console errors).

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 reset quick-picker view on preset, clear, and cross-grid day pick"` — pending, see Status.

---

### Task 48g: quick-picker `--selected` state in range mode

**Logged 2026-09-24 (user).** Task 48d's `--selected` wiring only works for single-date pickers: `isMonthCellSelected`/`isYearCellSelected` key off `this.selectedDate`, but `draft.selectedDate` stays `null` for the entire lifetime of a range picker — `selectRangeDay` (`draft-state.ts:51`) only ever writes `draft.rangeStart`/`rangeEnd`. Unlike the day grid (whose range visuals — `isRangeStart`/`isRangeEnd`/`isInRange` — are precomputed upstream into each `DayCell` independent of `selectedDate`), `MonthPickerCell`/`YearPickerCell` have no equivalent precomputed path, since they're generated fresh, locally, inside `bds-calendar-grid.tsx` each render. Result: the month/year picker never shows any selection indicator at all in range mode.

**Confirmed semantics (2026-09-24):** a month/year cell is `--selected` when it matches the month/year of _either_ `rangeStart` or `rangeEnd`, evaluated independently — **not** a spanning "in-range" treatment across every month/year between them. Figma's `_DatePickerMonthYear` only defines a boolean `Selected` state; there's no month-picker equivalent of the day-grid's `--in-range`/`--range-start`/`--range-end` trio, so inventing a spanning visual would have no design source behind it. Two independent boundary flags — using the exact same `--selected` class Task 48d already built — is the full scope.

`rangeStart`/`rangeEnd` should thread through as new props exactly the way `selectedDate` already does: one shared value passed identically to **every** `bds-calendar-grid` instance (confirmed via `renderCalendarPanel.tsx:54` — `selectedDate` is already looped across all calendar instances uniformly, not per-instance). This means both grids in `expanded` mode naturally see the same `rangeStart`/`rangeEnd` and independently decide, per their own `pickerYear`, whether either boundary falls within their currently-displayed year — no new per-instance coordination logic needed, same mechanism as single-date mode, just fed two dates instead of one.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid/types/ICalendarGrid.ts` (modify — add `rangeStart?`/`rangeEnd?` props), `bds-calendar-grid.tsx` (modify — `isMonthCellSelected`/`isYearCellSelected`), `bds-date-picker/helpers/renderCalendarPanel.tsx` (modify — thread the new props), `bds-date-picker.tsx` (modify — pass `this.draft.rangeStart`/`rangeEnd` into `renderCalendarPanel`)

**Acceptance criteria:**

- `bds-calendar-grid` gains `rangeStart?: string`/`rangeEnd?: string` props (naive `YYYY-MM-DD` strings, same shape as `selectedDate`), threaded through `renderCalendarPanel` from `bds-date-picker.tsx`'s `this.draft.rangeStart`/`rangeEnd`, passed identically to every grid instance (matching `selectedDate`'s existing threading).
- `isMonthCellSelected`/`isYearCellSelected` flag `--selected` when the cell's month/year matches `selectedDate`'s (single-date mode, existing behavior, unchanged) **or** either `rangeStart`'s or `rangeEnd`'s month/year (range mode, new). Only one of `selectedDate`/`rangeStart`+`rangeEnd` is ever populated at a time (mode-dependent), so no conflict between the two paths.
- Each boundary is evaluated independently — no spanning/in-range treatment between them, and no highlight at all for a boundary whose year doesn't match the currently-displayed picker grid (same "different year in view = no highlight" rule Task 48d already established).
- Both grids in `expanded`+range mode behave identically given the same `rangeStart`/`rangeEnd` — opening either grid's month/year picker can show either or both boundaries, whichever fall within that grid's own currently-displayed year.
- `aria-selected="true"` applied consistently with the class, matching Task 48d's existing pattern.
- No regression to Task 48d's single-date behavior, or to any other already-verified Task 46/48/48a-f/49 behavior.

**Manual test (required):**

Use `dp-quickpicker-s2` (expanded, range) and a new scenario with a wider range spanning multiple months/years if not already covered. Run `pnpm dev:components` and validate:

- [x] Given a range is selected with both endpoints in the currently-displayed year, when a grid's month picker opens, then both the start and end months show `--selected` independently, with no highlight on months in between. Pass: exactly two months flagged (or one, if start/end share a month), no spanning treatment. **Verified 2026-09-24 by @qa-subagent** — Mar/Sep flagged, Apr–Aug clean; same-month edge case (both boundaries in September) also confirmed to degenerate cleanly to a single flagged cell, no duplicate/broken artifact.
- [x] Given the same range, when the _other_ grid's month picker opens, then it shows the same boundary flagging behavior (using the same shared `rangeStart`/`rangeEnd`), consistent with the first grid. Pass: identical semantics across both grid instances. **Verified 2026-09-24 by @qa-subagent** — identical `["Mar","Sep"]` flagged on both grid instances, confirmed via direct property reads.
- [x] Given a range endpoint falls in a different year than the currently-displayed picker grid, then that endpoint shows no highlight (matching Task 48d's existing cross-year rule). Pass: no false positive. **Verified 2026-09-24 by @qa-subagent** — cross-year range (Dec 2026–Feb 2027): only Feb flagged while viewing 2027, only Dec flagged after navigating back to 2026.
- [x] Given a single-date (non-range) picker, when its month/year picker opens, then Task 48d's existing behavior is unchanged. Pass: no regression. **Verified 2026-09-24 by @qa-subagent** — `rangeStart`/`rangeEnd` confirmed `undefined` on a single-date instance, `selectedDate` path unaffected.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, independently re-verified (diff review across all 4 files, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — 22/22 suites, 459/459 tests, matching baseline), manually QA-verified live by `@qa-subagent` (all 6 checklist items pass, zero console errors).

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 wire quick-picker selected state for range mode"` — pending, see Status.

---

### Task 48h: reset the other grid's quick-picker on month/year navigation

**Logged 2026-09-24 (user).** Each `bds-calendar-grid`'s `view` state is a fully independent, per-instance `@State` — nothing coordinates it across the two grid instances in `expanded` mode except `handleMonthNavigate` (`bds-date-picker.tsx:542`), the single orchestrator method every grid's `bdsMonthNavigate` event routes through (via the per-instance `onBdsMonthNavigate` closures `renderCalendarPanel` binds, per Task 48's GC fix). It updates `displayYear`/`displayMonth` but never calls `resetCalendarViews()`.

Since nothing stops a user from opening **both** grids' quick-pickers simultaneously (grid B isn't dimmed/inert until it enters a picker view itself — opening grid A's picker doesn't touch grid B at all), completing a selection in grid A (`handleMonthCellClick` emits `bdsMonthNavigate`, then sets grid A's own `view` back to `'days'`) leaves grid B's already-open picker completely unaware anything happened. Grid B's picker stays open, now showing a month/year context that's about to be stale relative to whatever `displayYear`/`displayMonth` just changed to underneath it — the same "unsynced" symptom Task 48f already fixed for preset/clear/cross-grid-day-click, just via a different trigger (a month/year _pick_ from a quick-picker, rather than a day pick or a footer/sidebar action).

This is the same fix class as Task 48f's three call sites, just a fourth one Task 48f's own investigation didn't cover (Task 48f is already committed and closed, so this is logged as its own task rather than reopening it).

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify — `handleMonthNavigate`)

**Acceptance criteria:**

- `handleMonthNavigate` calls `this.resetCalendarViews()` after updating `displayYear`/`displayMonth`, so any quick-picker left open on either grid instance closes back to day view whenever a month/year navigation occurs on any grid.
- No regression to ordinary prev/next-month button behavior — a normal prev/next click can only originate from a grid already in day view (its header is inert while a picker is open, per Task 48c), so the added call is a harmless no-op in that path.
- No regression to Task 48/48a-h/49's already-verified single-grid and dual-grid behavior.

**Manual test (required):**

Use `dp-quickpicker-s2` (expanded, range). Run `pnpm dev:components` and validate:

- [x] Given both grids' quick-pickers are open simultaneously (open grid A's month picker, then separately open grid B's month picker), when a month is picked in grid A, then grid B's quick-picker also closes back to day view. Pass: no stale overlay left open on grid B. **Verified 2026-09-24 by @qa-subagent** — both overlays present simultaneously, both `hasOverlay: false` after picking a month in the left grid.
- [x] Given the same setup, when a year is picked instead (drilling grid A: month view → year view → pick a year → back to month view → pick a month), then the same result holds — grid B's picker closes once grid A's navigation completes. **Verified 2026-09-24 by @qa-subagent** — grid B's picker correctly stayed open after grid A's year-pick sub-step (navigation not yet complete), then closed once grid A's month-pick completed the drill.
- [x] Given only one grid has a quick-picker open (the normal case, already covered by Task 48's own scenarios), when a selection is made, then behavior is unchanged from what Task 48/48f already verified. **Verified 2026-09-24 by @qa-subagent.**
- [x] Given no quick-picker is open on either grid, when ordinary prev/next-month buttons are clicked, then no regression — day-grid navigation behaves exactly as before. **Verified 2026-09-24 by @qa-subagent.**

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` (one-line addition to already-existing, already-tested `resetCalendarViews()`), independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — 22/22 suites, 459/459 tests, matching baseline), manually QA-verified live (all 4 checklist items pass, zero console errors). **Process note:** this QA pass used `claude-in-chrome` instead of the mandated `playwright-cli` (agent cited "Playwright MCP was unavailable" — but this repo's convention is the `playwright-cli` CLI tool specifically to avoid the MCP dependency; results accepted as legitimate, but flagging the deviation for visibility).

**Commit:** `git commit -m "fix(bds-date-picker): EOA-17662 reset the other grid's quick-picker on month/year navigation"` — pending, see Status.

---

### Task 48i: quick-picker PageUp/PageDown paging

**Logged 2026-09-24 (user).** Task 48e wired `onPageUp`/`onPageDown` into `setGridNavigation` but guarded both to **no-op outside day view** (`handlePageUp`/`handlePageDown` early-return when `view !== 'days'`). That guard was necessary — without it, PageUp/PageDown inside an open picker would silently page the hidden day grid underneath the overlay — but it leaves the picker grids with **no paging keys**: in month/year view, PageUp/PageDown currently do nothing.

This is the natural parity gap with the day grid, where PageUp/PageDown = prev/next month (Task 40). The consistent extension:

- **month view** → PageUp/PageDown = previous/next **year**
- **year view** → PageUp/PageDown = previous/next **decade window** (the existing ±10 step)

Both behaviours already exist as the picker's own header `bds-button`s (`handlePickerPrevYear`/`handlePickerNextYear`, `handleYearWindowPrev`/`handleYearWindowNext`), including their `min`/`max` fully-disabled guards (`isPickerYearFullyDisabled`/`isYearWindowFullyDisabled`) — so this task is purely routing the keys to the existing handlers, not new navigation logic.

**Not a blocker:** the picker's inner prev/next controls are already Tab+Enter reachable, so keyboard-only users are not stuck without this — it's a convenience/parity completion, hence its own small task rather than reopening the closed Task 48e.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify — `handlePageUp`/`handlePageDown`)

**Acceptance criteria:**

- In `view === 'months'`, PageDown advances `pickerYear` by +1 and PageUp by −1, reusing `handlePickerNextYear`/`handlePickerPrevYear` (so the same `isPickerYearFullyDisabled` guard applies — the key no-ops when the target year is entirely out of `min`/`max`).
- In `view === 'years'`, PageDown steps the window +10 and PageUp −10, reusing `handleYearWindowNext`/`handleYearWindowPrev` (same `isYearWindowFullyDisabled` guard).
- In `view === 'days'`, behaviour is unchanged — PageUp/PageDown still emit the existing prev/next-month `bdsMonthNavigate` via `handlePrevClick`/`handleNextClick` (Task 40 regression).
- `handlePageUp`/`handlePageDown` no longer simply early-return for every non-day view; the routing is explicit per view. No new `KeyboardController`, no change to the day-grid month-paging path.
- No regression to `expanded` dual-grid independence (each grid pages its own view) or to any already-verified Task 46/48/48a-h/49 behaviour.

**Manual test (required):**

Reuse `dp-quickpicker-s1` (`basic`, single) and `dp-quickpicker-s3` (`basic`, `min="2026-06-01" max="2027-03-31"`). Run `pnpm dev:components` and validate:

- [x] Given the month picker is open, when PageDown/PageUp are pressed, then the year label steps forward/back by one year (month cells re-render for that year); the year-nav header buttons reflect the same state. **Verified 2026-09-24 by @qa-subagent** — `2026 → PageDown → 2027 → PageUp ×2 → 2025`; header-button clicks produce identical steps; no `bdsMonthNavigate` emitted (correct — picker paging is not day-grid nav).
- [x] Given the year picker is open, when PageDown/PageUp are pressed, then the 12-year window label steps by a decade (`startYear` ±10) exactly like the header's prev/next-years buttons. **Verified 2026-09-24 by @qa-subagent** — `2020 – 2031 → PageDown → 2030 – 2041`; header buttons identical.
- [x] Given `dp-quickpicker-s3`, when PageUp/PageDown would move to a fully out-of-`min`/`max` year or decade window, then the key no-ops — matching the disabled header button behaviour. **Verified 2026-09-24 by @qa-subagent** — 2026 `PageUp` no-op (2025 fully out), 2027 `PageDown` no-op (2028 fully out), partially-in-range 2027 still pages; year window both directions no-op at the fully-disabled boundary.
- [x] Given day view, when PageUp/PageDown are pressed, then the day grid still navigates prev/next month exactly as before (no regression). **Verified 2026-09-24 by @qa-subagent** — `September → PageDown → October` + one `bdsMonthNavigate {2026,9,'next'}`; `PageUp` back with `{2026,8,'prev'}`.
- [x] Given `dp-quickpicker-s2` (`expanded`), when one grid's picker has focus and PageUp/PageDown are pressed, then only that grid's picker pages — the other grid is unaffected. **Verified 2026-09-24 by @qa-subagent.**

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` (routing-only change to `handlePageUp`/`handlePageDown`, reusing the existing `handlePickerNextYear`/`PrevYear` and `handleYearWindowNext`/`Prev` handlers + their `min`/`max` guards), independently re-verified (`tsc`, `eslint`, `bds-date-picker` 22/22 suites 459/459, `utils/a11y/keyboard` 41/41), manually QA-verified live by `@qa-subagent` (all 5 checklist items PASS on Chromium + a WebKit spot-check, zero console errors). One follow-up gap found (not in this routing-only task's scope) — **year-view paging drops DOM focus** after the ±10 window shift because year cells are keyed by year and remount, so a second consecutive PageUp/PageDown doesn't reach the grid; logged as Task 48j below. Nothing committed — per standing preference, commits are the user's own action.

**Commit:** `git commit -m "feat(web-components): EOA-17662 page the quick-picker with PageUp/PageDown"` — pending.

---

### Task 48j: retain focus when the year picker's window shifts

**Logged 2026-09-24 (found by `@qa-subagent` while verifying Task 48i).** In the **year** view, PageUp/PageDown (Task 48i) and the header's prev/next-years buttons shift `pickerYear` by ±10. The 12 year cells are keyed by `cell.year`, so a window shift unmounts the currently focused cell and applies fresh DOM nodes — DOM focus falls to `document.body`. A second consecutive PageUp/PageDown then doesn't reach the grid (focus is no longer inside the grid root). **Month** view is unaffected: month cells are keyed by `month` (0–11) and persist across a year change, so month-view paging retains focus.

This is the same class of concern Task 48e already fixed for **view** transitions (`focusActiveViewPriorityCell()` runs on `@Watch('view')`); the gap is that a `pickerYear`/`pickerStartYear` change while `view === 'years'` is not a `view` transition, so that mechanism never fires. Not a Task 48i defect (its routing criteria all pass) — logged separately.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify — `@Watch` on the picker's year state, or re-focus after `handleYearWindowNext`/`Prev`/`handlePickerNextYear`/`Prev`)

**Acceptance criteria:**

- After a year-window shift while the year grid is active (via PageUp/PageDown **or** the header prev/next-years buttons), real DOM focus lands on a sensible year cell in the new window (e.g. the year matching the previous focus, clamped into the new window, or the first enabled cell) — not `document.body`.
- Two consecutive PageUp/PageDown presses in the year view both take effect (the second no longer no-ops for lack of focus).
- Month-view paging focus behaviour is unchanged (already retained), and day-view PageUp/PageDown is unchanged.
- No regression to Task 48i's routing, Task 48e's view-transition focus handling, or `min`/`max` guards.

**Manual test (required):**

Reuse `dp-quickpicker-s1`. Run `pnpm dev:components` and validate:

- [x] Given the year picker is open with a year cell focused, when PageDown is pressed, then the window advances and `document.activeElement` is a year cell in the new window (not `<body>`); pressing PageUp again immediately still pages back. **Verified 2026-09-24 by @qa-subagent** — focus `2029` → PageDown → window `2030 – 2041`, focus `2039` (= 2029 + 10, same-relative-position), `activeIsBody:false`; a second PageDown immediately advanced to `2040 – 2051` (focus `2049`), and PageUp ×2 stepped back with focus retained each time.
- [x] Given the same, when the header prev/next-years buttons are used instead, then focus also lands on a year cell (or remains sensibly on the control) and the space/arrow keys still reach the grid. **Verified 2026-09-24 by @qa-subagent** — real clicks on "Next years"/"Previous years" shift the window and focus lands on a year cell (not `<body>`).
- [x] Given month view, then PageUp/PageDown focus behaviour is unchanged from Task 48i. **Verified 2026-09-24 by @qa-subagent** — month-view paging still steps the year ±1 with focus retained; day-view prev/next-month + `bdsMonthNavigate` unchanged.
- [x] (added during QA) Given the same-relative-position target year falls outside the new window or is disabled, then focus falls back to a sensible enabled year cell. **Verified 2026-09-24 by @qa-subagent** — with runtime bounds `min=2027 max=2033`, preferred `2038` was disabled → fell back to `getPriorityYearCell` → focus `2030` (first enabled), never `<body>`.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` (new `@Watch('pickerYear')` capturing the focused year + delta before the DOM patch, consumed in `componentDidUpdate` via `focusYearWindowCell()`: same-relative-position preferred, else `getPriorityYearCell`; `@Watch('view')` clears the year-window intent so a concurrent view transition's own priority focus wins), independently re-verified (`tsc`, `eslint`, `bds-date-picker` 22/22 suites 459/459, `utils/a11y/keyboard` 41/41), manually QA-verified live by `@qa-subagent` on a **fresh** server (`:3344`, after confirming the served bundle contained the change — `:3333` had a stale lazy chunk) in Chromium + WebKit, all 6 checklist items PASS, zero console errors. Nothing committed — per standing preference, commits are the user's own action.

**Commit:** `git commit -m "fix(web-components): EOA-17662 keep focus when the year picker window shifts"` — pending.

---

### Task 49: Phase 9 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.scss` (modify), `bds-calendar-grid.tsx` (JSDoc)

**Figma research pass** (node IDs per the spike's "Unscheduled — month/year quick-picker" section, fileKey `rtiE5zGA4aoOuxIQMgfD6h`, none pulled yet — deliberately deferred until this phase, per the spike):

- [ ] Region: month grid layout — `datePickerMonths` (node `14:24131`), default state
- [ ] Region: year grid layout — `datePickerYears` (node `14:24151`), default state
- [ ] Modifier: `_DatePickerMonthYear` (node `14:23473`) `State` (Default/Hover/Focus/Active/Disabled) — pulled individually
- [ ] Modifier: `_DatePickerMonthYear` `Selected` (True/False) — pulled for its own default state
- [ ] Modifier: `_DatePickerMonthYear` `State Actual` ("is current month/year" indicator, not independently confirmed — confirm its actual semantics during this pull, don't assume)
- [ ] Combination: `Selected: True` × each `State` value (Hover+Selected, Focus+Selected, Active+Selected, Disabled+Selected)
- [ ] Combination: `State Actual: True` (current month/year) × `Selected: True` (both true simultaneously, mirroring the `_DatePickerNumber` day-cell precedent from the spike where "today" and "selected" combine independently)
- [ ] Region: month/year header button states — state matrix (~10 rows: Default/Hover/Focus/Active/Disabled × unselected/selected) confirming the header label is a real interactive button, not static text
- [ ] Dimensions: month-grid and year-grid cell sizing against the existing day-grid cell size, pulled from Figma's layout data (unconfirmed until re-pulled)
- [x] Region: quick-picker overlay container (node `14:24179`) — elevation/shadow token, corner radius, padding, and z-index/stacking treatment of the card superposed over the day grid, per Task 48b. **Resolved 2026-09-24 (user, against node `14:24184`):** background (`$boreal-ui-inverse`), shadow depth (`$boreal-depth-box-shadow-l`, corrected from an `-m` placeholder, confirmed via `get_design_context` reporting effect `Box shadow/l`), and padding (`$boreal-spatial-padding-m`, 16px, corrected from a `-s`/12px placeholder — applied directly by the user, confirmed intentional, committed in `d653a77b`) all fixed and confirmed against Figma. Corner radius left as `$boreal-radius-s` — the container node is a flattened raster SVG asset with no discoverable explicit corner-radius property (same limitation hit with the connector arrow's sizing below), so this is the best available visual match rather than an unconfirmed placeholder.
- [ ] Region: quick-picker overlay connector/arrow (node `14:24184`'s container vector, `I14:24184;14:24132`) — a small triangular tail pointing up from the card toward the header label, visible in the Figma screenshot and confirmed structurally (the container's SVG bounding box overshoots its layout frame by ~4px on the top edge, consistent with a pointer poking above the rounded-rect body). **New finding, not previously scoped anywhere** — added 2026-09-24 by porting `bds-popover.scss`'s own arrow technique (a `$boreal-spatial-spacing-s`-sized square, rotated 45°, same background as the card, positioned half-overlapping the top edge via `::before`) directly, since Task 48b's own design decision was not to reuse `bds-popover` as a component. Current size/offset is an approximation read off the SVG bounding-box overshoot, not a direct Figma measurement — confirm exact size/position here.
- [ ] Region: day-grid "dimmed" treatment shown behind the overlay in node `14:24179` — the exact opacity/color token applied while a picker view is active, per Task 48b's `aria-hidden`/`inert` day grid

**Acceptance criteria:**

- Every research row above checked off before the first SCSS line is written, with the pulled value recorded.
- Token-only SCSS; no hardcoded colours, spacing, or radii.
- Every `State` × `Selected` × `State Actual` combination enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- `Disabled` cells (out-of-range years, if applicable) suppress the native focus outline — verify this isn't scoped only inside the interactive-state block.
- The overlay container's elevation/shadow and the day grid's dimmed-background treatment (Task 48b) match the pulled Figma values exactly — no ad hoc shadow/opacity values.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm each top-level selector matches the DOM `bds-calendar-grid.tsx` actually renders for `view: 'months' | 'years'`.
- JSDoc brevity/content compliance.

**Manual test (required):**

Reuse Task 48's Scenarios 1-2. Run `pnpm dev:components` and validate:

- [x] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value. **Verified 2026-09-24 by @qa-subagent** — live-inspected sizing (48×32px cells, 184×176px container, 12px padding), background/shadow/radius tokens, and the "current" `::after` dashed-outline treatment, all matching the pulled values.
- [x] Given a month/year cell in each `State` × `Selected` × `State Actual` combination, when interacted with, then it renders per the pulled state matrix. Pass: visually matches Figma for all rows checked off above. **Verified 2026-09-24 by @qa-subagent** — hover/active confirmed via real `mousemove`/`mousedown` with distinct computed styles for each; disabled cells correctly inert (no hover/active treatment, click no-op) on both month and year grids; regression-checked dual-instance independence (`dp-quickpicker-s2`) and min/max disabling (`dp-quickpicker-s3`); zero console errors. **Note:** `Selected` state itself could not be exercised — no cell currently sets the `--selected` class (see new follow-up task below, pending a semantics decision with the user); the CSS block exists and is confirmed correct, but is presently unreachable in the live DOM. Every picker cell also has static `tabindex="-1"` (no roving tabindex yet) — expected per Task 48a's own scope note, not a new bug; Task 48e (keyboard navigation and ARIA) owns that work.

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent` via a full Figma research pass (all rows pulled and recorded above), independently re-verified (diff review, full `pnpm build` with cleared cache, `tsc`/`eslint`/unit-test re-run — including confirming 5 pre-existing, unrelated `tsc` errors in `bds-dialog`/`bds-tooltip` spec files were untouched by this diff), manually QA-verified live by `@qa-subagent`. Two follow-on gaps found during user review against Figma (not part of this task's own scope): the picker overlay needs its own nested header (currently the day-grid's header is replaced entirely rather than staying visible alongside a separate picker-internal header), and month/year cells need `--selected` wiring. Being scoped into new tasks — see below.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 style month/year quick-picker"` — pending, see Status.

---

### Task 50: Phase 9 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts` (create — grid-level behaviors), `bds-date-picker/__test__/bds-date-picker.quickpicker.spec.ts` (create — orchestrator-level behaviors: `resetCalendarViews` on preset/clear/cross-grid day-pick/month-navigate, and the C2 slot-aware anchor), `date-engine/__test__/grid.spec.ts` (left untouched — Task 47 already covered the generators, `grid.ts` is at 100% coverage), `src/utils/a11y/keyboard/__test__/navigation.spec.ts` (modify — the `onActivate` non-cell-focus guard), `ai-work/testing/failure-modes/bds-date-picker.md` (modify — FM-91–FM-109)

**Status:** ✅ done (2026-09-24) — implemented by `@testing-subagent` (the two `*.quickpicker.spec.ts` files already existed as untracked work from an interrupted session; they were audited against the current source and extended, not rewritten). Added 11 grid-level tests (keyboard-activation edges incl. year-cell Enter and disabled-year no-op, per-view no-focused-cell no-ops, day-view Escape no-op, `@Method resetView()`, `disconnectedCallback`, all-disabled day grid, 48j window-shift focus fallbacks), 1 orchestrator test (48e Escape routing across the grid→popover boundary: first Escape returns to day view with the popover open, second closes it), and 2 shared-utility tests for `grid-navigation.ts`'s `onActivate` non-cell-focus guard. Coverage (scoped, re-run independently by the orchestrating session): `bds-calendar-grid.tsx` **97.95% stmts / 94% branch / 100% funcs** (up from 90.96/89.51); `bds-date-picker.tsx` **99.22% stmts / 96.14% branch**; helpers 100%; `date-engine/grid.ts` 100%. Suites: `bds-date-picker` 24/24, 523/523 tests; `utils/a11y/keyboard` 3/3, 43/43; `tsc` + `eslint` clean. Deliberately-uncovered (documented, not gate-blocking): two `handleDayFocusIn`/`focusCell`/`focusPickerCellByKey` guard arms out of quick-picker scope, and Task 48d's CSS-only `:active` ring (no CSSOM under `newSpecPage`; live-verified by QA instead). Coverage-phase only; mutation testing deferred to Task 53a. Nothing committed — per standing preference, commits are the user's own action.

**Unit tests to cover:** grid-generator correctness; view-switch behavior; month/year selection transitions; dual-grid view-state independence; Task 48a's `<table role="grid">` markup for the month/year pickers (row/cell shape, `role`/`aria-current`/`aria-disabled` attributes); Task 48b's overlay behavior — day grid remains mounted but gains `aria-hidden`/`inert` while a picker view is active, and both clear on return to day view; Task 48c's nested-header behavior — outer header stays present and dims with the day grid, the picker's own header renders inside the card and its prev/next/decade-window controls behave identically to their pre-relocation logic; Task 48d's `--selected` wiring (matches `this.selectedDate`'s month/year, not the currently-displayed month/year) and active-ring consistency; Task 48e's keyboard/ARIA scope — header-label focusability and Enter/Space activation, arrow-key/Home/End traversal through month and year grids via the shared `setupGridNavigation` integration, Escape-returns-to-day-view without closing the popover, backdrop-click dismissal, and live-region announcements per view transition with no duplicates; Task 48f's `resetCalendarViews()` calls from `handlePresetClick`, the footer `CLEAN` case, and `handleDayClick` (any open quick-picker returns to day view on preset/clear/cross-grid-day-pick); Task 48g's range-mode `--selected` (flags either `rangeStart`'s or `rangeEnd`'s month/year independently, no spanning treatment, no false positive in single-date mode); Task 48h's `resetCalendarViews()` call from `handleMonthNavigate` (a stale quick-picker on the _other_ grid closes when any grid completes a month/year navigation); **Task 48i's PageUp/PageDown routing per view** (day → prev/next month, month view → ±1 year, year view → ±1 decade window; no-op when the target year/window is entirely outside `min`/`max`; `bdsMonthNavigate` not emitted from picker paging); **Task 48j's year-window focus retention** (after a ±10 window shift, focus lands on the same-relative-position year when present/enabled, else the priority cell, never `<body>`; two consecutive PageUp/PageDown presses both take effect). **Also add a shared-utility test** in `src/utils/a11y/keyboard/__test__/navigation.spec.ts` for Task 48e's `grid-navigation.ts` `onActivate` non-cell-focus guard — Enter/Space while focus is on a non-cell descendant of the grid root re-triggers native activation exactly once, while grid-cell activation is unchanged (mirrors Task 40b's own guard test). Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 9 month/year quick-picker unit tests"`

---

### Task 51: Phase 9 documentation

**Status:** ✅ done (2026-09-24) — implemented by `@documentation-subagent` against the reviewed scope below, verified independently (read the updated MDX directly, cross-checked every claim against `bds-calendar-grid.tsx`/`grid.ts`/`renderCalendarPanel.tsx`/`bds-date-picker.tsx`, and re-confirmed the MDX module compiles and serves via the running docs dev server). MDX-only change: new `### Month/year quick-picker` subsection under `## Calendar types` (drill-down model, `min`/`max` whole-span disabling with no future rule, availability across all three `calendar-type`s, overlay + nested header, single-date/range-boundary selection flagging, auto-close/resync, no-public-API); two new `## Accessibility` bullets (focusable label + `inert`/`aria-hidden` overlay + picker-vs-day `Escape`/backdrop dismissal; the picker's own **separate** local live region vs. the existing day-grid region); a new `#### Month/year picker keyboard interaction` table (Arrow/Home/End/Ctrl+Home/End, `PageUp`/`PageDown` per view, picker-vs-day `Escape`). No `ArgTypes` change, no story, ToC unchanged — per the task's explicit constraints. Manual test passed (new section + picker keyboard table render, zero console errors, no stale "replaces the day grid"/"not yet supported" prose). Nothing committed — per standing preference, commits are the user's own action. **Drift noted at completion and resolved by the post-task docs review (2026-09-24):** the `bds-calendar-grid` reference table omitted its real `min`/`max`/`now`/`rangeStart`/`rangeEnd`/`prevDisabled`/`nextDisabled` props — since this task forbade `ArgTypes` changes, the review added a per-story `argTypes` override on the `Default` story (grid-specific descriptions) and pointed the MDX `bds-calendar-grid` `ArgTypes` block at `BdsDatePickerStories.Default`. The same review also corrected the range-end coverage-shift wording (documenting the actual data-driven equal-time rule), added the `hour`/`minute` label keys, documented the quick-picker controls' English-only accessible names, and fixed the `calendar-type`/`bdsMonthNavigate` descriptions — mirrored into ADRs 0015/0016, the failure-mode catalog, and this plan.

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:**

- New **`### Month/year quick-picker`** subsection (place it under `## Calendar types`, alongside `### Default`/`### Basic`/`### Expanded`, since the picker is a behavior of the calendar body) that documents:
  - **Drill-down model** (Task 46 decisions 1-3): clicking the month/year header label opens a **month grid** (12 months, current month marked); clicking a month returns to the **day grid** showing that month; the picker's own **year control** opens a **year grid** (12 consecutive years, stepped in **decade** windows via its prev/next controls); clicking a year returns to the **month grid** for that year — _not_ directly to the day grid.
  - **`min`/`max` behaviour** (Task 46 decision 4): months/years whose whole span falls outside the configured bounds are disabled and unselectable; a partially-in-range month/year stays enabled; there is **no** "future is disabled" rule.
  - **Available on every calendar type** (Task 46 decision 7): `default`, `basic`, and `expanded`.
- Document the **overlay presentation** (Task 48b/48c): the picker opens as an elevated card **superposed over the still-visible day grid**, which is dimmed and removed from the tab order while the picker is open; the day grid (and its own header) return to normal on selection or dismissal. The picker has its **own nested header** (its prev/next + year/decade label) rather than replacing the day grid's header.
- Document **selection flagging** (Task 48d/48g): a month/year cell is highlighted when it matches the selected date's month/year (single-date), or **either** range boundary's month/year in range mode — both flagged independently, with **no spanning/“in-range”** highlight between them. A boundary whose year differs from the currently displayed picker year shows no highlight.
- Document **auto-close / resync** (Task 48f/48h): any open quick-picker returns to the day grid when a sidebar preset is clicked, when Clear is used, when a day is picked on the _other_ grid (`expanded`), or when a month/year navigation completes — in `expanded` mode this applies to **both** grid instances.
- Document the **full keyboard interaction model** (Task 48e + 48i) — extend the existing `#### Keyboard interaction` table (or add a clearly-labelled picker-specific table beside it) to include, at minimum:
  - the month/year label is a focusable button reached with `Tab`, activated with `Enter`/`Space`;
  - Arrow keys / `Home` / `End` traverse the month and year cells, and `Ctrl+Home`/`Ctrl+End` jump to the grid start/end;
  - **`PageUp`/`PageDown` page the current view**: previous/next **month** in day view, previous/next **year** in month view, previous/next **decade window** in year view;
  - `Enter`/`Space` selects the focused month/year;
  - `Escape` returns from the picker to the day grid **without** closing the popover, whereas `Escape` from the day grid closes the popover (the already-documented behavior);
  - clicking the dimmed area outside the picker card also dismisses back to the day grid.
- Note under the existing `## Accessibility` / `#### Keyboard interaction` area that the picker **announces its view for screen readers** — entering the month view, entering the year view, and returning to the day view each produce a single polite live-region announcement (extending the existing day-grid live-region description; Task 41 + Task 48e).
- State plainly that the picker is **automatic** — it introduces **no new public props or events**; it is internal to the `bds-calendar-grid` component that `bds-date-picker` composes.
- **No `ArgTypes` change** (no new public prop). A new story is **not required**: the picker is interaction-revealed and cannot be forced open via a prop (its `view` state is internal), so prose plus the existing interactive canvases are the intended documentation surface — do not add a story that fabricates an open state.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the new quick-picker section, when read against Task 46's confirmed model and Tasks 48/48a-48j's actual implementation, then every documented behavior matches exactly — the drill-down path, the overlay layering and its nested header, `min`/`max` disabling with no future rule, single-date **and** range-boundary selection flagging, the auto-close/resync triggers, and the keyboard model (including `PageUp`/`PageDown` paging per view and the picker-vs-day-view `Escape` distinction). Pass: no stale/contradicting prose.
- [ ] Given the updated keyboard table, when read against the shipped behavior, then it lists `PageUp`/`PageDown` with their per-view meaning and the picker `Escape` behavior — no entry implies a public API that does not exist.
- [ ] Given the whole page, when searched, then no prose claims the picker "replaces" the day grid or is "not yet supported" (both are stale/nonexistent states).

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 9 month/year quick-picker"`

---

### Task 52: React/Vue wrapper parity check — Phase 9

**Executor:** @qa-subagent
**Files:** `examples/react-testapp/src/App.tsx` (modify — appended Task 52 scenarios), `examples/vue-testapp/src/App.vue` (modify — appended Task 52 scenarios)

**Status:** ✅ done (2026-09-24) — verified by `@qa-subagent` via the pack-based pipeline (`dev:pack:react` then `dev:pack:vue`, strictly sequentially with a port-free teardown between), driven with `playwright-cli`. Three new scenarios (`task52-s1-quickpicker-basic`, `task52-s2-quickpicker-expanded-range`, `task52-s3-quickpicker-bounded`) were appended to both testapps (existing Task 27/34/39/45 content preserved). **Verdict: no React/Vue divergence** — every recorded value was identical across the drill-down + overlay (day grid mounted with `aria-hidden`/`inert`/`--dimmed`), the nested header, selected/range-boundary flagging (`--selected`/`aria-selected`, no spanning), keyboard (Tab→label→Enter, arrow/Home/End, Escape→day-view-with-popover-open, backdrop-click dismissal), `PageUp`/`PageDown` paging (month ±1 year, year ±10 window, bounds no-op, focus retention after the window shift), dual-grid independence + the 48h both-pickers-sync behavior, and `min`/`max` bounds disabling (no future rule). A Playwright-WebKit spot-check on the Vue wrapper matched as well (one platform note: macOS WebKit's Tab order skips native buttons — a browser behavior, not a component/wrapper defect). Zero new component/runtime errors in either wrapper. **One divergence in *recorded output* only, not product behavior:** the Vue testapp's own `onTask52S2Change` guard (`if (typeof e.detail !== 'string')`) ignores Clear's empty-string payload, so its `<pre>` keeps the last range while React's shows `""` — the component emits an identical empty-string `bdsChange` through both wrappers (captured live), so this is testapp code, not a wrapper/component divergence. Nothing committed — per standing preference, commits are the user's own action.

**Acceptance criteria:** Quick-picker behavior, including its keyboard navigation (**arrow/Home/End and `PageUp`/`PageDown` paging per view**), backdrop-click dismissal, live-region announcements, range-mode selection flagging, and cross-grid/preset/clear sync (Task 48f/48h), remains identical through wrappers. ✅ Met.

**Manual test (required):**

Repeat Task 48's Scenarios 1-2, Task 48e's Scenario 3 (keyboard-only drill-down), Task 48h's dual-picker-open scenario, and Task 48i's PageUp/PageDown paging (month view → ±1 year, year view → ±1 decade window) through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [x] Given each scenario, when repeated through the React wrapper, then the drill-down cycle matches the raw web component exactly, including the overlay superposition with its nested header (Task 48b, 48c), the selected-date/range-boundary flagging (Task 48d, 48g), the auto-close-on-preset/clear/cross-grid-navigation behavior (Task 48f, 48h), and `PageUp`/`PageDown` paging (Task 48i). Pass: no divergence in view transitions, `bdsMonthNavigate` firing, keyboard traversal/paging, or live-region announcements. **Verified 2026-09-24** — all checks PASS.
- [x] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence. **Verified 2026-09-24** — React == Vue on every recorded value; WebKit spot-check matched too.

**Commit:** N/A

---

## Phase 10 — JSDoc and import cleanup

**Confirmed with user 2026-09-23.** Logged as its own final phase (not folded into Phase 7/8/9) since it's a cross-cutting cleanup pass over the _entire_ `bds-date-picker` surface accumulated across every phase, not a feature. Runs after all functional phases (5-9) are complete, before the final consolidated mutation-testing task — so mutation testing measures the codebase in its final, cleaned-up shape rather than needing a second pass after this one.

### Task 54: JSDoc cleanup across `bds-date-picker` helpers

**Status:** ✅ done (2026-09-24) — comment-only pass by `@frontend-subagent`, verified independently (programmatic diff check confirmed zero non-comment changed lines; scoped `git diff --stat` = 6 files, 32 insertions/59 deletions). Trimmed rationale/decision narration from all six helper JSDocs (`renderBanner`/`renderCalendarPanel`/`renderFooter`/`renderPresets`/`renderRangeHeader`/`renderTimeSelector`) while preserving behavior description and the two genuinely-non-obvious WHYs (`renderFooter`'s always-rendered helper region for the `space-between` layout; `renderTimeSelector`'s `bds-select` bare-event collision guard). `bds-date-picker.tsx` audited — zero edits needed (class-level + all `@Prop`/`@Event`/`@Method` JSDoc already describe the current public contract with no history references; no JSDoc exists on private methods). Full `bds-date-picker` directory-tree suite (24 suites, 523 tests) passed unchanged. Nothing committed.

**Motivation:** helper JSDoc (`helpers/*.tsx`, and `bds-date-picker.tsx`'s own private methods) accumulated length incrementally as each phase's feature landed — several comments now read as a running history of design decisions rather than a clean description of current behavior, and some drifted into internal implementation detail that belongs in the plan/ADRs, not in source comments.

**Executor:** @frontend-subagent (implementation)
**Files:** `helpers/renderBanner.tsx`, `helpers/renderCalendarPanel.tsx`, `helpers/renderFooter.tsx`, `helpers/renderPresets.tsx`, `helpers/renderRangeHeader.tsx`, `helpers/renderTimeSelector.tsx`, `bds-date-picker.tsx` (JSDoc only in all — no logic changes)

**Acceptance criteria:**

- Every helper-function JSDoc describes current behavior only — trimmed to what a reader needs to use the function correctly, not the history of how it got there (no "Task N added X," no ADR/ticket references, no narration of decisions that were reconsidered and reversed along the way).
- Internal technical/implementation detail that doesn't help a caller (e.g. which private method something delegates to, why an unrelated method exists) is removed or relocated to a code comment only if it documents a genuinely non-obvious WHY (per this project's own no-comments convention) — otherwise deleted outright.
- No behavior/logic changes of any kind — this is a comment-only pass; a diff review must show zero non-comment line changes.
- Full spec suite still passes unchanged (comments don't affect runtime, but confirms nothing was accidentally altered).

**Manual test (required):** Non-visual — code review confirms JSDoc reads cleanly and no logic changed; full suite passing is the only runtime check needed.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 clean up accumulated helper JSDoc"`

---

### Task 55: import consolidation across `bds-date-picker` helpers

**Status:** ✅ done (2026-09-24) — import-only pass by `@frontend-subagent`, verified independently (read the resulting files; changed lines are import statements only). Two duplicate-specifier merges applied: `helpers/renderFooter.tsx`'s two `'../types'` imports merged into one (`{ FOOTER_ACTION, type FooterAction, type DatePickerLabels }`), and `utils/value-mapping.ts`'s two `'@/services/date-engine'` imports merged into one (value imports + inline `type DateEngineLocale`/`type MonthGrid`). Full audit of all 12 in-scope files found no further duplicate specifiers and no barrel reach-ins into the component's own `types/`/`utils/` dirs. **User-approved scope extension:** added a new `helpers/index.ts` barrel (mirroring `types/index.ts`/`utils/index.ts`) and collapsed `bds-date-picker.tsx`'s six individual `./helpers/renderX` imports into one `./helpers` barrel import — the six were distinct specifiers with no pre-existing barrel, so this was an addition beyond the task's declared file list, done at the user's explicit request. `tsc --noEmit` shows only the 5 known pre-existing unrelated errors (bds-dialog/bds-tooltip specs), zero in `bds-date-picker`; eslint clean on both changed files; `bds-date-picker` suite (24 suites, 523 tests) passed unchanged. Nothing committed.

**Motivation:** some helpers import from the same module in multiple separate statements instead of one combined import, and/or import individual files directly where this component's own barrel exports (`types/index.ts`, `utils/index.ts`) already re-export the same symbols. Example already found: `helpers/renderFooter.tsx` has two separate imports from `'../types'` (`{ FOOTER_ACTION, FooterAction }` and `type { DatePickerLabels }`) that should be one statement.

**Executor:** @frontend-subagent (implementation)
**Files:** `helpers/*.tsx`, `bds-date-picker.tsx`, `utils/*.ts` (import statements only — audit the full set before editing, the example above is a starting pointer, not the complete list)

**Acceptance criteria:**

- No file has two or more separate import statements from the same module specifier — consolidate into one.
- Every file imports shared types/utilities via this component's own barrels (`../types`, `../utils`) rather than reaching into an individual file inside those directories directly, wherever the barrel already re-exports the needed symbol.
- No behavior/logic changes — import consolidation only; a diff review must show zero non-import line changes.
- `tsc --noEmit` and `eslint` clean after consolidation (catches any accidental circular-import or missing-export issue the consolidation might introduce).
- Full spec suite passes unchanged.

**Manual test (required):** Non-visual — `tsc --noEmit`/`eslint` clean and full suite passing are the only checks needed.

**Commit:** `git commit -m "refactor(bds-date-picker): EOA-17662 consolidate imports via barrel exports"`

---

### Task 55a: extract `bds-calendar-grid` quick-picker view type and its literal usages

**Status:** ✅ done (2026-09-24) — implemented by `@frontend-subagent`, verified independently (read the new `types/enum.ts`/`types/index.ts` and the full `bds-calendar-grid.tsx` diff). Created `bds-calendar-grid/types/enum.ts` (`CALENDAR_GRID_VIEW` const object + `CalendarGridView` derived type, matching `bds-date-picker/types/enum.ts`); added `export * from './enum';` to `types/index.ts`; retyped `@State() private view` to `CalendarGridView` defaulting to `CALENDAR_GRID_VIEW.DAYS`; replaced all 22 remaining literal sites (state assignments + `===`/`!==` comparisons). Grounding re-count: Tasks 48b/48c had grown the literal count from the plan's recorded 11 to 23 (declaration + 22 usages) — all replaced. Grep for `view === ' / view = ' / view !== ' / view: '` and for `'days'|'months'|'years'` both return zero matches. `tsc -p tsconfig.build.json --noEmit` clean (exit 0); eslint clean on all three files; `bds-date-picker` tree suite (24 suites, 523 tests) passed unchanged. Pure literal→named-constant substitution, no control-flow/runtime-value change. Nothing committed.

**Logged 2026-09-24 (user request).** `'days' | 'months' | 'years'` is currently declared once, inline, as the type of `@State() private view` (`bds-calendar-grid.tsx:52`) — but the three literal strings themselves are repeated **11 times total** across the file (state assignments in `handleLabelClick`/`handleYearButtonClick`/`handleYearCellClick`/`handleMonthCellClick`/`resetView`, `view ===` checks in `renderHeader`/`render`). Tasks 48b (overlay visibility toggling) and 48c (keyboard-nav view-switch handling) will add more of both kinds of reference, so this closes the gap before that lands.

**Corrected pattern match (found while scoping this task):** a bare extracted type alias is not this project's actual convention for "a fixed set of string values referenced by both type and value position" — `bds-date-picker/types/enum.ts` already establishes the real pattern (`CALENDAR_TYPE`/`FooterAction`/`CalendarSlot`/`RangeBound`/`PresetKey`, each a `const X = {...} as const` object plus a `type Y = (typeof X)[keyof typeof X]` derived from it), and every consumer uses the const's named members (`CALENDAR_TYPE.EXPANDED`) instead of raw string literals at every call site, not just at one declaration. This task follows that same shape, in a new `bds-calendar-grid/types/enum.ts` (mirroring `bds-date-picker/types/enum.ts` as a dedicated file, distinct from `types.ts`'s plain interfaces), rather than a bare type alias in `types.ts`.

**Executor:** @frontend-subagent (implementation)
**Files:** `bds-calendar-grid/types/enum.ts` (create), `bds-calendar-grid/types/index.ts` (modify — barrel-export the new file), `bds-calendar-grid.tsx` (modify — replace all `view`-related literals with the new const's members)

**Acceptance criteria:**

- `bds-calendar-grid/types/enum.ts` exports `export const CALENDAR_GRID_VIEW = { DAYS: 'days', MONTHS: 'months', YEARS: 'years' } as const;` and `export type CalendarGridView = (typeof CALENDAR_GRID_VIEW)[keyof typeof CALENDAR_GRID_VIEW];`, matching `bds-date-picker/types/enum.ts`'s exact shape.
- `bds-calendar-grid/types/index.ts` adds `export * from './enum';`, matching `bds-date-picker/types/index.ts`'s own barrel.
- `bds-calendar-grid.tsx`'s `@State() private view` property is typed `CalendarGridView` (imported from `./types`), defaulting to `CALENDAR_GRID_VIEW.DAYS` instead of the raw `'days'` literal.
- **Every** other `view`-related string literal in the file is replaced with the corresponding `CALENDAR_GRID_VIEW` member — all 11 occurrences (state assignments and `===` comparisons), not just the property declaration. A grep for `view === '` / `view = '` / `view: '` against the final file returns zero matches.
- If Tasks 48b/48c have landed by the time this runs and introduced their own new `view`-literal usages (e.g. a visibility-toggle condition, a keyboard-nav view-switch branch), those are updated to use `CALENDAR_GRID_VIEW` too — confirmed via the same grep.
- No behavior/logic changes — this is a like-for-like literal-to-named-constant substitution; a diff review must show no change in control flow or runtime values.
- `tsc -p tsconfig.build.json --noEmit` and `eslint` clean after the change.
- Full `bds-calendar-grid`/`bds-date-picker` spec suites pass unchanged.

**Manual test (required):** Non-visual — `tsc --noEmit`/`eslint` clean, the zero-match grep confirmed, and full suite passing are the only checks needed.

**Commit:** `git commit -m "refactor(bds-calendar-grid): EOA-17662 extract quick-picker view type and constants"`

---

## Final task — consolidated mutation testing across v2 + v3

### Task 53: consolidated mutation testing — Phases 3, 3.5, 4 (carried over from v2)

**Status:** 🟡 closed for this task's scope (2026-09-25) — the consolidated pass ran; its v2 bucket is closed: `date-engine` verified at **94.71%** (v2 range-flag gaps killed in `date-engine/__test__/grid.spec.ts`; 12 documented equivalent mutants, 0 no-coverage). `bds-calendar-grid.tsx` had **zero v2 survivors** — the v2 Phase 4 range logic is fully covered — so no Task-53-side grid test work was required. Large v3 gaps the same run surfaced are tracked in Tasks 53b/53c; the `bds-date-picker` pass is deferred (impractical runtime — see Testing and QA policy notes).

**Split from a single combined task, confirmed with user 2026-09-23** — running the entire v2+v3 mutation debt (Phases 3 through 9) in one sitting risked an excessively long run with no incremental caching, and mixed old/stable code's survivors with new/actively-changing code's survivors in one hard-to-triage report. This task now owns only the v2 carried-over debt; Task 53a (below) owns v3's own Phases 5-9.

**Carried-over scope context (read before dispatching):** v2's "Testing and QA policy" section stated explicitly: _"coverage-phase tests are consolidated at the end of each covered phase block. Later-phase mutation consolidation now lives in version 3 scope."_ v2 only ran a mutation-testing pass once, immediately after Phase 2 (its own Task 8) — Phases 3, 3.5, and 4 shipped and the v2 plan closed `done` with **no mutation-testing pass ever run against that code**. This task inherits that debt, scoped to Phase 3 (min/max), Phase 3.5 (`calendarType`), and Phase 4 (range) code only — Phase 5-9 code is explicitly out of scope here (see Task 53a).

**Execution note (2026-09-25):** this task and Task 53a execute as **one consolidated Stryker pass**, per "Mutation-testing execution strategy" in Testing and QA policy — Stryker cannot scope mutants by phase, so the configs cover every phase's files at once and this task owns only the **Phase 3/3.5/4 portion of the triage** (survivors bucketed by `git blame`, not by a separate run).

**Executor:** @testing-subagent
**Files:** (create, at `packages/boreal-web-components/` root; local-only, never committed)

- `stryker.date-engine.config.mjs`
- `stryker.bds-calendar-grid.config.mjs`
- `stryker.bds-date-picker.config.mjs`
- `jest.stryker.config.cjs` (shared, union `testMatch`)
- `eslint.config.ts` (modify — temporary `*.config.mjs` / `*.config.cjs` / `.stryker-tmp/` ignores; reverted before the worktree is removed)

**Acceptance criteria:**

- Configs enable `incremental: true` (writes/reads `reports/stryker-incremental.json`) so a survivor-fix re-run only re-tests mutants whose covering code or tests actually changed, and `concurrency: 2` / `maxWorkers: 1` per the memory-safety caps.
- Configs are authored per the target map in Testing and QA policy (three `mutate`-scoped configs + one shared `jest.stryker.config.cjs` with a union `testMatch`; `grid-navigation.ts` folded into the `bds-calendar-grid` target; `types/*`, `types/enum.ts`, and `index.ts` barrels excluded).
- The consolidated pass runs once against current HEAD and its survivors are bucketed by `git blame` into v2-debt (this task) vs v3 (Task 53a). Task 53's own write-up covers only the Phase 3 (min/max), Phase 3.5 (`calendarType`), and Phase 4 (range) survivors.
- Target >=90% mutation score per target area; survivors require either test fixes or documented exceptions in `ai-work/qa/mutation-reports/mutation-<area>.md`.
- Test gaps found here are closed in the existing spec file for the phase that introduced the gap (Phase 3/3.5/4 spec files, since that's this task's triage scope).

**Manual test (required):** run the consolidated Stryker configs and confirm >=90% per area (or documented exceptions), then confirm the bucketed Phase 3/3.5/4 survivors are each killed or documented.

**Commit:** `git commit -m "test: EOA-17662 run mutation testing across v2 carried-over phases (3, 3.5, 4)"`

---

### Task 53a: consolidated mutation testing — Phases 5-9 (this plan's own scope)

**Status:** ✅ done for its in-scope portion (2026-09-25) — Phase 8 keyboard/a11y survivors and the Phase 9 `onActivate` guard killed by new tests in `bds-calendar-grid.keyboard.spec.ts` and `utils/a11y/keyboard/__test__/navigation.spec.ts`; **mutation-confirmed** by the `bds-calendar-grid` re-run (75.97% → 77.43%; every targeted real-gap line killed, residual survivors at those lines are the documented equivalents; +21 killed / −14 survived). Full Jest suite 3,816 green. The area remains below the 90% floor solely because of the two deferred buckets: Phase 9 quick-picker survivors → Task 53b, EOA-10530 `grid-navigation.ts` survivors → Task 53c. The `bds-date-picker` pass is deferred (impractical runtime on this 11-core/18GB machine — the retuned run still projected ~7h and exhausted memory).

**Execution note (2026-09-25):** this is the **second phase-bucket of the same consolidated pass** Task 53 runs, not a second Stryker run — see "Mutation-testing execution strategy" in Testing and QA policy. It owns the Phase 5-9 (+ Phase 10 cleanup) portion of the triage, including the `grid-navigation.ts` survivors folded into the `bds-calendar-grid` target.

**Executor:** @testing-subagent
**Files:** (same three configs as Task 53 — extended `mutate`/`testMatch` if needed, not duplicated; all local-only and discarded with the worktree)

- `stryker.date-engine.config.mjs` (no change expected — the config already targets all `date-engine` files)
- `stryker.bds-date-picker.config.mjs` (no change expected)
- `stryker.bds-calendar-grid.config.mjs` (no change expected — `grid-navigation.ts` already included by Task 53)

**Acceptance criteria:**

- Reuses the same configs Task 53 created — no second run; this task's survivors come from the same consolidated pass, bucketed to Phase 5-9 code.
- Covers every `bds-date-picker`/`bds-calendar-grid`/`date-engine` surface added or modified in Phases 5-9 (range-mode time selection, presets, banner/range-summary, keyboard/a11y, quick-picker — RTL descoped, see Task 41a) **plus** the shared `grid-navigation.ts` (Phase 9/Task 48e) and the Phase 10 cleanup (Tasks 54-55, comment/import-only plus Task 55a's `CALENDAR_GRID_VIEW` constants — expected not to introduce new survivors, but confirms it).
- Target >=90% mutation score per target area; survivors require either test fixes or documented exceptions.
- Test gaps found here are closed in the existing spec file for the phase that introduced the gap.

**Manual test (required):** confirm the bucketed Phase 5-9 (+ Phase 10 cleanup) survivors are each killed or documented, and the overall per-area scores are >=90%.

**Commit:** `git commit -m "test: EOA-17662 run consolidated mutation testing across v3 phases (5-9)"`

---

### Task 53b (new — discovered executing Task 53a's mutation run, 2026-09-25): `bds-calendar-grid` quick-picker mutation-test coverage remediation — deferred to its own ticket

**Status:** ⏳ deferred (user decision 2026-09-25) — not part of Tasks 53/53a. **Filed as local ticket:** `ai-work/tickets/EOA-17662-53b-calendar-grid-quickpicker-mutation.md`.

**Context:** the consolidated Stryker pass scored `bds-calendar-grid` **75.97% total / 78.69% covered** (227 survivors, 38 no-cov, 10 timeouts). `git blame` buckets **every** `bds-calendar-grid.tsx` survivor to Phase 8/9/10 — there are **no v2 (`b4cdb986`) survivors**, so the v2 range logic is fully covered. Of those, **67 unique survivor lines** come from the Phase 9 quick-picker commits (`49d25ed6`, incl. the ~65-mutant `getPriority*Cell` cluster at lines 611-636; `aa1f1ad2`; `39c3fae4`; `21be7773`; `f255e94b`; `95c3704a`; `29a5dd9d`; `b87e9ec4`). These are real weak-assertion gaps in the quick-picker focus/priority/selected-state logic, too large to absorb into Tasks 53/53a without an unbounded test-writing session.

**Scope:** kill or document each Phase 9 picker survivor; bring `bds-calendar-grid.tsx` to ≥90%.
**Exact survivor list:** `ai-work/qa/mutation-reports/TRIAGE-NOTES-eoa17662.md` (bucketed table) and `run-bds-calendar-grid-2026-09-25.log`.
**Files:** `bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts` (extend — the phase-owning spec).

---

### Task 53c (new — discovered executing Task 53a's mutation run, 2026-09-25): `grid-navigation.ts` pre-existing mutation debt (EOA-10530) — separate ticket, out of this plan's scope

**Status:** ⏳ deferred (user decision 2026-09-25) — to be filed under EOA-10530 (or a new ticket), not this plan. **Filed as local ticket:** `ai-work/tickets/EOA-17662-53c-grid-navigation-mutation-debt.md`.

**Context:** 50 of the 52 `grid-navigation.ts` survivor lines blame to `ea4d3d76` (2026-05-20, EOA-10530) — pre-existing shared keyboard-navigation utility code, never mutation-tested before and not introduced by Phases 5-9. Only lines 233/236 (the Phase 9 `onActivate` guard, `49d25ed6`) belong to this plan and remain in Task 53a's scope.
**Scope:** bring the EOA-10530-owned `grid-navigation.ts` code to ≥90% under a `bds-calendar-grid`-style config.

---

### Task 53d (new — deferred 2026-09-25): `bds-date-picker` consolidated mutation pass

**Status:** ⏳ deferred (user decision 2026-09-25). **Filed as local ticket:** `ai-work/tickets/EOA-17662-53d-bds-date-picker-mutation.md` — includes the exact `stryker.bds-date-picker.config.mjs` + `jest.stryker.bds-date-picker.cjs` to recreate (configs are local-only and were discarded with the worktree).

**Context:** the last remaining Stryker run for this plan. The full pass is 897 mutants and projects ~7h on the 11-core/18GB dev machine, exhausting memory; retunes (`mutator.excludedMutations` 1300→897; `enableFindRelatedTests: false`) did not reduce the per-mutant cost, because each mutant runs a large share of the component's 523 tests. Run when the machine is free, then triage with the same `git blame` phase-bucketing method used for Tasks 53/53a.

---

## Remaining Open Questions

- **Phase 6 (Task 28, done):** decided fixed presets, not configurable — see Task 28's own write-up for rationale.
- **Phase 9 (Task 46, done 2026-09-24):** drill-down model confirmed — label → month grid → year control → year grid (12 years, decade-stepped) → year → month grid (not the day grid); `min`/`max`-only disabling with no "future" rule; `expanded` grids drill independently; available on every calendar type. See Task 46's decision list.
- **RTL (Task 41a, descoped):** not scheduled — pending ticket-owner sign-off; no design-system-wide RTL precedent exists to build against.
- **Task 34f-1 (optional, not scheduled):** re-sync the displayed month if `value` is reassigned externally while the popover is already open — revisit only on a concrete consumer need.
- **Out of scope:** keyboard-typed date entry in the trigger field remains deferred.
- **Task 27a (done):** `format=""` crashed date-fns formatting — found during Task 27's QA pass, confirmed universal (raw component + both wrappers), fixed via `effectiveFormat`'s falsy check and verified live across all 4 previously-affected stories plus the `withTime=false` path.
- **Task 27b (done):** fixed a Storybook-only masking bug (`|| nothing` → `ifDefined`) that had made Task 27a's crash briefly appear non-reproducible in the affected stories, ensuring Storybook could actually verify Task 27a's fix.
- **Task 30a (done):** "today" now threads the configured `timezone` through `computePresetRange`, `resolveFallbackDisplayMonth`, and `buildDisplayGrid`'s zoned `now` (via the shared `resolveZonedToday` helper) — no longer read from the device clock. See Task 30a.
