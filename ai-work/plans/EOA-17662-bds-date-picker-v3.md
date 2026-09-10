---
ticket: EOA-17662
component: bds-date-picker
status: pending
created: 2026-09-02
updated: 2026-09-09
revision: 3 — reconciled against v2's actual implementation history and the spike's node references (2026-09-08)
---

# EOA-17662 — bds-date-picker v3 (Phases 5-9) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Deliver the remaining roadmap scope for `bds-date-picker` by completing Phases 5-9 (range-mode time selection, presets sidebar, info banner/range summary, keyboard/a11y/RTL, month/year quick-picker) plus a final consolidated mutation-testing pass.

**Ticket brief:** [`ai-work/tickets/EOA-17662-bds-date-picker-v3.md`](../tickets/EOA-17662-bds-date-picker-v3.md)

**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md)

**v2 plan (Phase 2-4, prerequisite, done):** [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md)

**Cross-cutting fix outside this plan's own file scope (2026-09-09):** Task 23's manual QA surfaced a real bug in `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` (`handleFocusOutside`'s RAF-scheduling race with `bds-select`'s own deferred refocus-after-selection call — see Task 23's Status note for the full root cause) that blocked real mouse-driven use of the time selector in both single-date and range modes. Fixed as part of this plan's execution since it blocked Task 23 outright, not deferred to a separate ticket. `bds-popover`'s own test suite (57/57) and `bds-select`/`bds-date-picker`'s suites (381 tests) were re-verified clean. Any other component composing `bds-popover` with a nested focus-transferring child (not just `bds-date-picker`) benefits from this fix — worth keeping in mind if a similar "popover closes unexpectedly on a nested interactive element" report surfaces elsewhere in the library.

This plan carries forward the remaining roadmap scope after v2 foundation work.

- v2 (EOA-17138) now ends at Phase 4 foundation work.
- v3 (EOA-17662) owns all remaining work: Phases 5-9, plus a final consolidated mutation-testing pass that also covers Phase 3/3.5/4 code v2 never mutation-tested (see Testing and QA policy below, and Task 53).
- Keyboard-typed date entry in the trigger field remains explicitly out of scope.

**Architecture:** Unchanged core shape from v1/v2 — `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + one or two `bds-calendar-grid` bodies, FACE-compliant, draft-state-until-Apply). Each v3 phase is additive on top of v2's `range`/`calendarType` foundation: Phase 5 parameterizes the existing time-selector helper for start/end positions; Phase 6 adds a new `renderPresets.tsx` sidebar gated on `range`; Phase 7 adds a new `renderBanner.tsx` and extends the footer; Phase 8 wires the already-existing `grid-navigation.ts` utility into `bds-calendar-grid`; Phase 9 adds an internal `view` state to `bds-calendar-grid` (no new public component or prop).

**Tech Stack:** Stencil, TypeScript, `date-fns`/`@date-fns/tz` (already in place since v1), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`), Stryker for mutation testing, existing `src/utils/a11y/keyboard/navigation/grid-navigation.ts`.

---

## Files to create / modify

**Phase 5 (dual time):**

| File                                                                        | Notes                                                                                       |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx`        | Modify — parameterize for `label`/`position: 'single' \| 'start' \| 'end'`                    |
| `.../bds-date-picker/bds-date-picker/helpers/renderRangeHeader.tsx`         | Modify — add per-bound time text to the `expanded` labeled header                            |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                   | Modify — dual/shared time wiring; time text on the `basic` dash-joined header                |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                  | Modify — dual/shared time-selector layout                                                    |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts` | Modify — dual/shared time-selector coverage                                                  |

**Phase 6 (presets sidebar):**

| File                                                                            | Notes                                                                                                                         |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/utils/presets.ts`                          | New — built-in preset date-range computation                                                                                    |
| `.../bds-date-picker/bds-date-picker/utils/__test__/presets.spec.ts`            | New                                                                                                                             |
| `.../bds-date-picker/bds-date-picker/helpers/renderPresets.tsx`                 | New                                                                                                                             |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                            | Modify — `DatePickerPreset` shape, `presets` prop type (if configurable, per Task 28)                                          |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                       | Modify — `presets` prop, sidebar wiring, basic-mode header-format re-evaluation (Task 30)                                      |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                      | Modify — sidebar layout, option button states                                                                                  |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.presets.spec.ts`  | New                                                                                                                             |

**Phase 7 (banner + range summary):**

| File                                                                          | Notes                                                                                    |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `.../bds-date-picker/bds-date-picker/helpers/renderBanner.tsx`               | New                                                                                        |
| `.../bds-date-picker/bds-date-picker/helpers/renderFooter.tsx`               | Modify — range-summary label, left of Clean/Cancel/Apply                                   |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                         | Modify — `DatePickerBanner` shape (`title`, `message`, `closable`, `state`, `visible`)     |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                    | Modify — `banner` prop, closable wiring                                                    |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                   | Modify — banner + summary label styling                                                    |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.banner.spec.ts`| New                                                                                        |

**Phase 8 (keyboard/a11y/RTL):**

| File                                                                             | Notes                                                                                              |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                    | Modify — wire `src/utils/a11y/keyboard/navigation/grid-navigation.ts` for 2D arrow-key traversal      |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                                   | Modify — RTL audit (logical properties, mirrored nav icons)                                           |
| `.../bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx`            | Modify — live region for month/year-change announcement                                               |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                        | Modify — Escape-key close + focus return to trigger                                                   |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                       | Modify — RTL audit for popover/footer/sidebar                                                         |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.keyboard.spec.ts`              | New                                                                                                   |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts`                  | Modify — live region assertions                                                                       |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts`  | Modify — full grid-traversal + Escape-close coverage                                                  |

**Phase 9 (month/year quick-picker):**

| File                                                                             | Notes                                                                                                                                     |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/services/date-engine/grid.ts`                | Modify — `generateMonthPickerGrid`/`generateYearPickerGrid`                                                                                   |
| `packages/boreal-web-components/src/services/date-engine/types.ts`               | Modify — month/year grid cell types                                                                                                            |
| `packages/boreal-web-components/src/services/date-engine/__test__/grid.spec.ts`  | Modify — new grid-generator coverage                                                                                                           |
| `.../bds-calendar-grid/types/ICalendarGrid.ts`                                   | Modify — `view: 'days' \| 'months' \| 'years'` state type                                                                                       |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                    | Modify — internal `view` state, drill-down/drill-up handlers, clickable month/year header label                                               |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                                   | Modify — month-grid/year-grid cell styling                                                                                                     |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts`           | New                                                                                                                                            |

**Shared, across every phase:**

| File                                                                            | Notes                                                                          |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/index.html`                                 | Modify — playground scenarios per task (never committed)                       |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` | Modify — one new story variant per phase                                       |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx`        | Modify — one new section per phase                                             |
| `.../date-engine/stryker.date-engine.config.mjs`                                | Modify (final task) — re-run to cover Phase 3/3.5/4/5-9 additions              |
| `.../bds-date-picker/stryker.bds-date-picker.config.mjs`                        | Modify (final task) — re-run to cover Phase 3/3.5/4/5-9 additions              |
| `.../bds-calendar-grid/stryker.bds-calendar-grid.config.mjs`                    | Modify (final task) — re-run; Phase 8/9 are the first v3 phases touching this  |

---

**Critical reference files (read before starting any task below):**

- [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md) — Phase 2-4 implementation this plan extends. Its Task 18 status notes (three correction passes, 2026-08-31/09-01) are load-bearing for Phase 5: the popover header format landed on a **split by `calendarType`**, not one uniform presentation — see Task 23 below.
- `ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md` — governing findings/decisions for Phases 5-9; each task below only summarizes it. Note: v2's Task 18 briefly reused the spike's `_DatePickerRange` node (`14:23420`, correctly a Phase 6 preset-button reference per the spike's own Phase 6 finding) for an unrelated header/range-design lookup and found it didn't fit — treat any node ID as scoped to the phase the spike assigned it to, not a general-purpose reference, and re-verify with `get_design_context` before reuse across phases.
- `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` — existing generic grid-keyboard utility, Phase 8's integration point (flagged in v1's Task 9 code comment, carried through v2's own file list, never wired — still outstanding for Task 40 below).

## Testing and QA policy for this plan

**Two-phase test gate remains in effect** — coverage-phase tests are consolidated at the end of each covered phase block (per Phase, one unit-test task). Mutation-phase consolidation is deferred to a single task at the end of this plan (Task 53) — and, per v2's own policy handoff, that task also owns the Phase 3/3.5/4 mutation-testing pass v2 deferred and never ran.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output** — implementation and SCSS tasks chain `@qa-subagent`; pure-logic, types-only, and test-only tasks keep a single executor. Matches this plan's existing Executor fields throughout.

**Wrapper parity stays per-phase, not per-task and not fully consolidated** — `bds-date-picker` was already an established, shipping component by v2's Phase 3 (per v2's own policy, quoted there: *"unlike v1/Phase 2 (a brand-new component with no behavior yet to diverge on), by Phase 3 `bds-date-picker` is an established, already-shipping component; per the writing-plans convention, each phase from here on gets its own React/Vue parity task immediately after that phase's documentation task"*). v3 continues that same policy: each phase's parity-check task (Tasks 27/34/39/45/52) runs immediately after that phase's documentation task, catching any framework-specific regression against the one feature that just landed rather than in one end-of-plan pass.

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

- `DatePickerDraftState` (`types/types.ts:1-7`) currently has exactly one shared `hour: number`/`minute: number` pair, used unconditionally regardless of `range`. There is no per-bound time state today. `resetRangeDraft`'s own doc comment (`utils/draft-state.ts:98-102`) confirms: *"`withTime` is not yet supported in range mode (Phase 5) — `hour`/`minute` always default to `00:00`."* — this task is exactly what that comment is waiting on.
- Add new fields to `DatePickerDraftState` for `expanded`'s two independently-controlled selectors — e.g. `startHour: number`, `startMinute: number`, `endHour: number`, `endMinute: number` (flat, mirroring the existing `rangeStart`/`rangeEnd` flat-field precedent, not nested). The existing single `hour`/`minute` fields stay exactly as-is and continue to be the ones read/written for `basic`+`range` (the shared-value case) — do not repurpose them for `expanded`.
- `selectHour`/`selectMinute` (`utils/draft-state.ts:56-68`) currently mutate the single shared `hour`/`minute` field unconditionally, with no bound concept. Add bound-aware variants (or a `bound` param) for the new `startHour`/etc. fields; `handleHourChange`/`handleMinuteChange` (`bds-date-picker.tsx:432-438`) are the only existing call sites and will need either duplication into start/end-specific handlers or a bound-aware signature.
- `TimeSelectorParams` (`helpers/renderTimeSelector.tsx:6-13`) has no way to render a leading `Start:`/`End:` text label today — its `labels` param only feeds the two `bds-select`'s own internal field labels (`hour`/`minute`), not a prefix. Add a new param (e.g. `boundLabel?: string`) sourced from `labels.start`/`labels.end` at the call site — `DatePickerFooterLabels` already has both keys (`types/types.ts:15-16`, added in v2's Task 19), reuse them, don't add new keys.
- `render()`'s current time-selector block (`bds-date-picker.tsx:831-842`) gates on the raw `this.withTime` prop (not `this.effectiveWithTime`) and always renders exactly one `renderTimeSelector` call with no `range` branch at all — confirm against the file's existing `effectiveWithTime`/`effectiveRange`/`effectiveFormat` getter convention whether this block should switch to `this.effectiveWithTime` for consistency (a pre-existing inconsistency this task's new branching logic will sit next to, worth fixing while touching this code rather than leaving mixed).
- `formatRangeForDisplay` (`utils/value-mapping.ts:218-231`) only accepts naive-ISO date strings today — no hour/minute params, cannot format time. `formatDraftForDisplay` (`utils/value-mapping.ts:197-210`) is the existing single-date pattern that already combines `selectedDate + hour/minute` into one formatted string (wall-clock local, no timezone conversion) — mirror that shape for a new per-bound range-plus-time formatter, rather than bolting optional hour/minute params onto `formatRangeForDisplay` itself.
- `bds-date-picker.tsx`'s Apply-commit path (`bds-date-picker.tsx:402-405`) currently commits `{ start: rangeStart, end: rangeEnd }` as bare naive-ISO date strings with **no time-combination call at all**, even though this task's own acceptance criteria below already commit to `combineDateTimeToUTC`/`extractDateTimeFromUTC` producing full UTC ISO strings for the range value. This task's scope includes updating that Apply-commit path to call `combineDateTimeToUTC` per bound (using the new `startHour`/`startMinute`/`endHour`/`endMinute` for `expanded`, the existing shared `hour`/`minute` for `basic`) — this isn't a separate task, it's this task's own value-contract acceptance criteria made concrete against the real commit path.

**Header-format context (from v2 Task 18, read before implementing):** the popover header is **not** one uniform format across `calendarType`. `expanded`+`range` uses `renderRangeHeader.tsx`'s labeled `Start:`/`End:` pairs (popover is `width: 'auto'`, no overflow risk). `basic`+`range` uses a plain, unlabeled, dash-joined single line (`"YYYY/MM/DD – YYYY/MM/DD"`) rendered inline in `bds-date-picker.tsx`, deliberately without labels because the labeled format wrapped inside `basic`'s fixed 296px popover. v2 explicitly left time out of both formats pending this task: *"Time segment simply omitted until Phase 5/Task 23 wires in withTime support for range mode."*

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

**Known pre-existing gap, flagged not fixed (out of this task's scope):** `resetRangeDraft`'s `withTime` branch only hydrates per-bound times when *both* `rangeStart` and `rangeEnd` independently pass `isValidUtcDateTimeValue`; a mixed valid/malformed range value falls through to the naive-date branch and nulls *both* bounds, not just the malformed one. This gate predates Phase 5 (same behavior existed before the per-bound fields) — noted in the failure-mode catalog's reconciliation section for visibility, not tracked as a new task unless a mixed valid/malformed range value turns out to be a real scenario worth handling.

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

**Cross-referenced against actual current MDX/stories content, 2026-09-09 — surfaced a real stale claim, not just a documentation gap:** the existing MDX's "When to use it" callout explicitly states *"`with-time` and `range` are independent features; combining them is not currently supported"* — this is now false and must be corrected, not just supplemented. Priority is updating existing sections over adding new top-level ones; the full reviewed scope below reflects what's actually needed, not a generic "add docs" pass.

**Acceptance criteria:**

- **Fix the stale claim** in the "When to use it" callout — range+time combination is now supported; state the actual `expanded`/`basic` behavior split instead of "not currently supported."
- **New subsection** "Range-mode time selection" added *inside* the existing `## Time selection` section (not a new top-level section) — documents `expanded`'s two independent time selectors (labeled `Start:`/`End:`) vs. `basic`'s one shared selector applied to both bounds, and the `{ start, end }` UTC datetime value contract. Two new story variants feed this subsection: `expanded`+`range`+`with-time` and `basic`+`range`+`with-time`. Do **not** add `with-time` to the existing `RangeModeBasic`/`RangeModeExpanded` stories — those exist to teach range mechanics in isolation; conflating time into them blurs that.
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
- Confirm this doesn't change behavior for any *other* falsy-but-meaningful value this getter might see — read the actual current getter and its callers before changing the condition, since `format` is typed `string | undefined` (per `IDatePicker.ts`), so `null`/`0`/`false` shouldn't be reachable in practice, but verify rather than assume.

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

### Task 28: presets configurability — design/API decision (blocking gate)

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Decide and document whether presets are fixed or consumer-configurable.
- If configurable, define `presets` prop shape before Task 30.

**Manual test:** N/A — design/API checkpoint.

---

### Task 29: preset range computation module

**Executor:** @frontend-subagent
**Files:** `utils/presets.ts` (create), `utils/__test__/presets.spec.ts` (create or covered by Task 32)

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

- Computes built-in presets (today, yesterday, last 7, last 30, this month, last month) as `{ start: Date; end: Date }`.
- Uses existing date-math primitives; no new `date-engine` primitive unless justified.
- "Custom" represents manual mode and is not computed as a built-in preset.

**Manual test (required):** Non-visual — unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add built-in preset range computation"`

---

### Task 30: presets sidebar implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderPresets.tsx` (create), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `draft.rangeStart`/`draft.rangeEnd` are currently written only by `selectRangeDay`/`resetRangeDraft` (`utils/draft-state.ts`, per v2's Task 18) — confirm a preset click writes through the same state fields via a new sibling function (e.g. `selectPresetRange`), not by mutating `draft` directly in `bds-date-picker.tsx`'s render/handler code, to keep Cancel/Clean's existing draft-revert logic correctly covering preset-originated selections too.
- [ ] Boundary case: a consumer-configured `presets` prop (if Task 28 chooses configurable) with a malformed entry — e.g. `end` before `start`, or a preset whose computed range falls entirely outside a set `min`/`max` — confirm this task's acceptance criteria state the resolution (clamp, ignore, or a `componentWillLoad` warning matching Phase 3.5's existing warning-log precedent), not left to the implementer to invent.
- [ ] Default/empty state: no preset is "selected" by default when a picker opens with no prior range — confirm whether "Custom" itself needs an explicit selected/unselected default state distinct from "no preset active yet," since the spike's preset list treats "Custom" as representing manual mode, not literally as a clickable list item with its own state.
- [ ] Reactivity: the `presets` prop (if configurable) — is it expected to be reactive after mount (`@Watch`-driven, sidebar re-renders if the consumer swaps the array) or a set-once config value read only at first render? State this explicitly per Task 28's decision.

**Acceptance criteria:**

- Sidebar renders only when `range=true`.
- Built-in preset display text ("Today", "Yesterday", "Last 7 days", "This month", "Last month", "Custom") is sourced from new keys added to the existing `labels`/`DatePickerFooterLabels` object (e.g. `presetToday`, `presetYesterday`, `presetLast7Days`, `presetThisMonth`, `presetLastMonth`, `presetCustom`), each with an English default — never hardcoded literals in `renderPresets.tsx`. Follows Task 23's precedent and [ADR 0014](../../ai-docs/decisions/0014-localizable-ui-copy-prop-shape.md): `bds-date-picker` already crossed the bundled-object threshold, so new UI-copy strings extend `labels` rather than introducing a new prop shape.
- Clicking a preset sets `draft.rangeStart`/`draft.rangeEnd` and marks preset selected; manual day selection afterward returns to Custom.
- If Task 28 chooses configurable presets, custom presets override/extend built-ins per decision.
- Preset buttons use real interactive states (Default/Hover/Focus/Active/Disabled).
- **Deprecate the `basic`+`range` dash-joined header format in favor of `renderRangeHeader.tsx`'s labeled `Start:`/`End:` format (matching `expanded`), by default — not an open toss-up.** v2's Task 18 introduced the dash-joined line *only* because the labeled format wrapped inside `basic`'s fixed 296px popover width. Since this sidebar is gated on `range` alone (not `calendarType` — per this phase's own preamble), every `basic`+`range` picker gains the sidebar's extra width unconditionally once this task ships, permanently removing the constraint that justified the dash-joined format. Confirm the actual Figma `basic`+`range`+sidebar header node has room for the labeled format before implementing (the header spans the full popover width — sidebar + calendar together — confirmed 2026-09-09 against the reference screenshot), then remove the dash-joined rendering path from `bds-date-picker.tsx` entirely rather than keeping both formats alive. This also means removing/superseding the basic-dash-joined-with-time wiring Task 23 added — expected, one-phase-lived code, not a regression.
- **Not in scope, confirmed a Figma-tool artifact, not a real product state (2026-09-09):** some Figma variants expose an `End Date` toggle independent of `Range`, producing a single-value (no `End:`) header even with `Range: true`. This has no counterpart in `bds-date-picker`'s data model — once `range=true`, both `rangeStart` and `rangeEnd` are required for any commit (per the existing Apply-guard `this.draft.rangeStart !== null && this.draft.rangeEnd !== null`), so a "range with no end" state can't occur here. Do not implement or research this Figma variant combination.
- JSDoc on the new `presets` `@Prop()` (if Task 28 chooses configurable) is 1-2 sentences, consumer-facing only (what it does / what the consumer sees or receives) — never internal implementation details (which private getter or `@Watch` computes/consumes it, how it's wired to `draft.rangeStart`/`rangeEnd` internally). Matches `ai-docs/guidelines/jsdoc-template.md`'s worked examples.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: `calendarType='expanded'` + `range`, presets sidebar visible.
- Scenario 2: `calendarType='basic'` + `range`, presets sidebar visible.
- Scenario 3 (if Task 28 chooses configurable presets): a consumer-supplied `presets` override.

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1 or 2, when a preset ("Last 7 days", etc.) is clicked, then `draft.rangeStart`/`draft.rangeEnd` update to that preset's range and the preset shows selected. Pass: correct dates highlighted on the calendar, preset button visually marked selected.
- [ ] Given a preset is selected, when a day is manually clicked afterward, then the selection reverts to "Custom" and the preset shows deselected. Pass: preset button loses its selected state.
- [ ] Given Scenario 3, when the consumer's custom presets are supplied, then they render per Task 28's decision. Pass: matches documented override/extend behavior.
- [ ] Given the sidebar is now present in `basic`+`range`, when the header renders, then it shows the labeled `Start:`/`End:` format (`renderRangeHeader.tsx`), matching `expanded` — not the dash-joined line Task 23 shipped. Pass: `basic` and `expanded` render an identical header structure; the dash-joined rendering path no longer exists in `bds-date-picker.tsx`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add presets sidebar"`

---

### Task 31: Phase 6 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

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

Reuse Task 30's Scenarios 1-3. Run `pnpm dev:components` and validate:

- [ ] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value.
- [ ] Given a preset button in each `State` × `Selected` combination, when interacted with, then it renders per the pulled state matrix. Pass: visually matches Figma for all rows checked off above.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style presets sidebar"`

---

### Task 32: Phase 6 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.presets.spec.ts` (create), `presets.spec.ts` (create)

**Unit tests to cover:** preset computation correctness; preset click updates draft + selected state; manual click returns to Custom; configurable overrides (if enabled); preset label text resolves from the new `labels` keys with correct English defaults and consumer overrides, mirroring Task 25's labels-override coverage pattern. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 6 presets sidebar unit tests"`

---

### Task 33: Phase 6 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents presets behavior and configurability decision; includes new story variant. Documents the new preset `labels` keys (with their English defaults) alongside the existing footer-labels table, so consumers know how to localize preset button text via the same `labels` prop used for Clean/Cancel/Apply/Start/End.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the new presets story variant, when Storybook renders it, then it renders without console errors and preset clicks work in the docs canvas. Pass: no errors, interactive.
- [ ] Given the MDX configurability section, when read against Task 28's actual decision, then it matches exactly. Pass: no stale/contradicting prose.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 6 presets sidebar"`

---

### Task 34: React/Vue wrapper parity check — Phase 6

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Presets-sidebar behavior matches across wrappers.

**Manual test (required):**

Repeat Task 30's Scenarios 1-3 through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [ ] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in preset selection/deselection or header rendering.
- [ ] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A

---

## Phase 7 — Info banner + footer range summary

`banner` remains independent of `calendarType`. Range summary remains `range`-gated.

### Task 35: banner + range summary implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderBanner.tsx` (create), `helpers/renderFooter.tsx` (modify), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Utility discovery:**

- Feature area: an in-context info/message surface with a title, message, closable state, and state variant (matches the legacy `infoBanner` shape: `{ title, close, message, state, visible }`).
- Search performed: `packages/boreal-web-components/src/components/feedback/` (existing feedback-family components — `bds-toast`, `bds-tag`, any standalone banner/alert component); `src/types/states.ts` (`ComponentState`/`COMPONENT_STATES` for the `state` field's type).
- Candidates found: confirm whether a standalone `bds-banner`/`bds-alert` component already exists in `components/feedback/` before building `renderBanner.tsx` as a local helper — if one exists, reuse it as a slotted/composed element instead of hand-rolling banner markup; `ComponentState`/`COMPONENT_STATES` (`src/types/states.ts`) is the existing shared type for the `state` field regardless.
- Fit assessment: to be completed at dispatch time — if no standalone banner component exists, this confirms `renderBanner.tsx` as a `bds-date-picker`-local helper is correct (matching the plan's existing precedent: footer/time-selector/month-header are `helpers/*.tsx`, not separate components, per the spike's Finding 3 litmus test); if one does exist, this task's scope changes to composing it rather than building new markup.
- Reuse decision: recorded at dispatch time per the search above; `state` field's type always reuses `ComponentState`, never a new local union.
- Gap handling: not applicable unless a partial-fit banner component is found — if so, extend it rather than fork a parallel implementation, and note the extension here before proceeding.
- Anti-duplication check: no parallel `state`-variant type is planned; `types/types.ts`'s `DatePickerBanner` shape reuses `ComponentState` for its `state` field.
- Test impact: Task 37's `bds-date-picker.banner.spec.ts` asserts banner visibility/close/state through whichever implementation this discovery step lands on.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `renderFooter.tsx` is an existing, already-shipped helper (Clean/Cancel/Apply, per v1/v2) — confirm adding the range-summary label doesn't require changing its existing call signature in a way that breaks its current single-date/basic-range call sites; the summary label should be an additive, conditionally-rendered piece, not a signature change forcing every existing caller to pass a new required argument.
- [ ] Boundary case: `banner.visible = true` set by the consumer while `banner.closable = true` and the user has already dismissed it once via the close (`X`) button in a prior open — confirm whether reopening the popover resets the dismissed-state (matching the picker's own draft-revert-on-reopen convention already established for date/range selections) or the dismissal persists across opens; state this explicitly rather than leaving it to the implementer's default assumption.
- [ ] Default/empty state: `banner` prop's default value (empty object vs. `undefined`) — confirm which one this task uses and that it renders nothing (no empty banner shell) when unset, matching the legacy `infoBanner` prop's own documented default of an empty object with `visible` implicitly falsy.
- [ ] Reactivity: `banner` is expected to be reactive after mount (`@Watch`-driven — a consumer can update `banner.message` while the popover is already open) — state this explicitly, since the footer/time-selector helpers this task's Files list touches are otherwise re-rendered per Stencil's normal `@State`/`@Prop` reactivity, and `banner` being a plain object prop (not tracked via `@State`) needs its own reactivity confirmation.

**Acceptance criteria:**

- Adds `banner` prop shape with title/message/closable/state/visible support.
- Banner renders above calendar body and works in all `calendarType` values (including `default`).
- Footer summary in `range` mode computes from selected range. **Note — not directly sourced from the spike or v2:** the spike's only concrete example (`"Rango: 18 días, 2 horas, 30 minutos"`) doesn't identify which `calendarType` it was pulled from, and v2's Task 18/19 explicitly deferred this label to this task without further guidance. The `basic`: days-only / `expanded`: days/hours/minutes split below is this plan's own inference (mirroring Phase 5's single-vs-dual time-selector split), not a confirmed design decision — pull `get_design_context` against the actual `Basic Footer`/`Expanded Footer` range-summary text nodes before implementing, and treat the split as a hypothesis to verify, not a given:
  - `basic`: days only
  - `expanded`: days/hours/minutes
- Range-summary word units ("day"/"days", "hour"/"hours", "minute"/"minutes") are sourced from new keys added to the existing `labels`/`DatePickerFooterLabels` object, not hardcoded literals — following the same `labels`-extension pattern as Task 23/30 and [ADR 0014](../../ai-docs/decisions/0014-localizable-ui-copy-prop-shape.md). Singular/plural word-form selection per unit uses the native `Intl.PluralRules` API (zero new dependency) — a flat string per unit cannot express "1 day" vs. "18 days," and ADR-0014 explicitly defers pluralization to this mechanism rather than a message-catalog library.
- JSDoc on the new `banner` `@Prop()` is 1-2 sentences, consumer-facing only (what it does / what the consumer sees or receives) — never internal implementation details (which private getter or `@Watch` consumes it, how `renderBanner.tsx` is wired to it). Matches `ai-docs/guidelines/jsdoc-template.md`'s worked examples.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: `calendarType='default'` with `banner` set.
- Scenario 2: `calendarType='basic'` (no range) with `banner` set.
- Scenario 3: `calendarType='basic'` + `range`, a committed range, footer summary visible.
- Scenario 4: `calendarType='expanded'` + `range` + `withTime`, a committed range, footer summary visible.

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1 or 2, when the banner is visible, then it renders above the calendar body with title/message/state styling. Pass: matches the pulled Figma structure.
- [ ] Given a visible, closable banner, when the close (`X`) button is clicked, then the banner dismisses. Pass: banner no longer renders, no console errors.
- [ ] Given Scenario 3, when a range is committed, then the footer summary shows the days-only text (or whatever the Figma pull in Task 36 confirms). Pass: summary text matches the confirmed format, not this plan's unverified hypothesis.
- [ ] Given Scenario 4, when a range is committed, then the footer summary shows days/hours/minutes (or whatever the Figma pull confirms). Pass: summary text matches the confirmed format.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add info banner and footer range summary"`

---

### Task 36: Phase 7 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass:** Pull `get_design_context`/`get_metadata` for each row. A row is done only when actually pulled, never inferred from a sibling variant.

- [ ] Region: banner — default state (title/message/icon layout, all `calendarType` values it renders in)
- [ ] Region: banner close (`X`) button — default, hover, focus, active
- [ ] Modifier: banner `state` variant (info/success/warning/error, or whichever subset Figma actually shows) — each pulled individually, not inferred from `info`
- [ ] Combination: each `state` variant × close-button hover, if the close button's color changes per state
- [ ] Region: footer range-summary label — default state, both `basic` (days-only, per Task 35's hypothesis pending Figma confirmation) and `expanded` (days/hours/minutes) text layouts
- [ ] Dimensions: footer summary label alignment/spacing against the Clean/Cancel/Apply button row, pulled from Figma's layout data

**Acceptance criteria:**

- Every research row above checked off before the first SCSS line is written, with the pulled value recorded — including confirming or correcting Task 35's `basic`-days-only/`expanded`-days-hours-minutes hypothesis against the actual pulled footer nodes.
- Token-only SCSS; no hardcoded colours, spacing, or radii.
- Every banner `state` variant × close-button interaction enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- Non-interactive banner content suppresses the native focus outline where applicable — verify this isn't scoped only inside the close button's own interactive-state block.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm each top-level selector matches the DOM `renderBanner.tsx`/`renderFooter.tsx` actually render.
- JSDoc brevity/content compliance.

**Manual test (required):**

Reuse Task 35's Scenarios 1-4. Run `pnpm dev:components` and validate:

- [ ] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value.
- [ ] Given the banner's close button, when hovered/focused, then it renders per the pulled state matrix. Pass: visually matches Figma.
- [ ] Given the footer summary label, when rendered alongside Clean/Cancel/Apply, then spacing matches the pulled dimensions. Pass: no visual crowding or misalignment.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style info banner and range summary"`

---

### Task 37: Phase 7 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.banner.spec.ts` (create)

**Unit tests to cover:** banner visibility/close behavior across all `calendarType` values; range summary behavior for `basic` (days-only) and `expanded` (days/hours/minutes); live updates as range changes; range-summary pluralization via `Intl.PluralRules` for singular vs. plural day/hour/minute counts (e.g. "1 day" vs. "18 days"); range-summary word-unit labels resolve from the new `labels` keys with correct English defaults and consumer overrides. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suite passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 7 banner and range summary unit tests"`

---

### Task 38: Phase 7 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents banner prop and range-summary behavior; includes new story variant. Documents the new range-summary `labels` keys (with English defaults) and explains the `Intl.PluralRules`-based pluralization behind the singular/plural word forms, so consumers understand how "1 day" vs. "18 days" is chosen and how to override the words via `labels`.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the new banner/range-summary story variant, when Storybook renders it, then it renders without console errors. Pass: no errors, interactive.
- [ ] Given the MDX range-summary section, when read against Task 35/36's confirmed Figma format, then it matches exactly (not this plan's original unverified hypothesis). Pass: no stale/contradicting prose.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 7 banner and range summary"`

---

### Task 39: React/Vue wrapper parity check — Phase 7

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Banner and range summary behavior is consistent across wrappers.

**Manual test (required):**

Repeat Task 35's Scenarios 1-4 through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [ ] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in banner close or footer summary text.
- [ ] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A

---

## Phase 8 — Keyboard navigation, accessibility, RTL

Phase 8 wires and validates grid keyboard traversal, live announcements, and RTL behavior without changing the baseline architecture. Per the spike: `bds-calendar-grid`'s native `<table role="grid">` markup (v1, Task 3) was chosen specifically to make this phase additive — the [WAI-ARIA APG Date Picker Dialog Example](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) documents the exact keyboard interaction to implement (arrow-key cell traversal, month/year navigation hotkeys, live-region month/year announcement) and is the "agreed interaction model" referenced in Task 40 below.

### Task 40: `bds-calendar-grid` arrow-key 2D traversal

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

- [ ] Given Scenario 1, when arrow keys/Home/End/PageUp/PageDown are pressed, then focus moves cell-to-cell per the agreed interaction model. Pass: focus visibly follows the expected cell, no focus loss.
- [ ] Given Scenario 1, when traversal crosses a month boundary, then `bdsMonthNavigate` fires and the grid re-renders the new month with focus landing on the correct cell. Pass: month changes, focus correct.
- [ ] Given Scenario 2, when traversing one grid, then the other grid's focus/traversal state is unaffected. Pass: no shared/leaking focus state between the two instances.
- [ ] Given Scenario 3, when traversal reaches a disabled cell, then focus skips it. Pass: disabled/out-of-month cells are never a focus stop.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add arrow-key 2D grid traversal"`

---

### Task 41: live region + RTL audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderCalendarPanel.tsx` (modify), `bds-calendar-grid.scss` (modify), `bds-date-picker.scss` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `renderCalendarPanel.tsx` renders one or two `bds-calendar-grid` instances depending on `calendarType`/`range` (per v2's Task 18) — confirm the live region is a single shared announcement element (not duplicated per grid instance, which would double-announce in `expanded` mode) even though it's driven by month/year state that exists per-instance.
- [ ] Boundary case: `expanded`'s consecutive-month navigation lock (v2's Task 19m — only the outer two nav buttons are live, the inner two are permanently disabled) — confirm the live-region announcement fires once per navigation action (both calendars' months changing together) rather than twice (once per calendar), which would read as a confusing double-announcement to screen-reader users.
- [ ] Default/empty state: RTL audit — confirm `dir="rtl"` is read from the existing host-level mechanism (if any) already used elsewhere in the codebase, not a new prop invented for this task; state which existing pattern this follows.
- [ ] Reactivity: month/year live-region text must update on every `bdsMonthNavigate` firing (existing event, already reactive) — confirm no debounce/throttle is needed given rapid PageUp/PageDown-driven navigation from Task 40 could fire this in quick succession; state whether rapid consecutive announcements are acceptable or need coalescing.

**Acceptance criteria:**

- Adds aria-live month/year announcement updates.
- Completes RTL audit for grid, sidebar, footer, and navigation icons.
- No LTR visual regression.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker with a screen reader (or `aria-live` region inspection) active, navigate months.
- Scenario 2: `calendarType='expanded'` + `range`, `dir='rtl'` set on the host.
- Scenario 3: `calendarType='basic'` + presets sidebar, `dir='rtl'` set.

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1, when the month/year changes (nav button or Task 40's traversal), then the live region announces the new month/year exactly once. Pass: single announcement per navigation, no duplicate/missing announcement.
- [ ] Given Scenario 2, when rendered RTL, then grid, footer, and navigation icons mirror correctly. Pass: no visual/logical direction bugs, nav icons point the correct mirrored direction.
- [ ] Given Scenario 3, when rendered RTL, then the sidebar mirrors to the correct side. Pass: no LTR layout leaking into RTL mode, and a matching LTR scenario confirms no LTR regression.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add live region announcements and RTL support"`

---

### Task 42: Escape key closes popover and returns focus to trigger

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.tsx` (modify)

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

- [ ] Given Scenario 1, when Escape is pressed, then the popover closes and focus visibly returns to the trigger input. Pass: popover closed, focus ring visible on the trigger, not lost to `<body>`.
- [ ] Given Scenario 2, when Escape is pressed mid-selection, then the popover closes, focus returns to the trigger, and the in-progress draft reverts per the existing Cancel-equivalent behavior. Pass: same as Scenario 1, plus draft correctly discarded.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 return focus to trigger on Escape close"`

---

### Task 43: Phase 8 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.keyboard.spec.ts` (create), `bds-calendar-grid.a11y.spec.ts` (modify), `bds-date-picker.keyboard.spec.ts` (modify)

**Unit tests to cover:** full key traversal, boundary crossing, disabled/out-of-month exclusions, live-region updates, dual-grid independence, Escape-key close + focus return (Task 42). Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 8 keyboard navigation and a11y unit tests"`

---

### Task 44: Phase 8 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents keyboard model and RTL support.

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the keyboard-model and RTL sections, when read against Tasks 40-42's actual implementation, then the documented model matches exactly. Pass: no stale/contradicting prose.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 8 keyboard navigation and RTL support"`

---

### Task 45: React/Vue wrapper parity check — Phase 8

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Keyboard traversal and RTL rendering remain consistent across wrappers.

**Manual test (required):**

Repeat Task 40's Scenarios 1-3 and Task 41's Scenarios 1-3 (and Task 42's Escape scenarios, since it lands in this phase) through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [ ] Given each scenario, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence in keyboard traversal, live-region announcements, RTL rendering, or Escape close/focus-return.
- [ ] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A

---

## Phase 9 — Month/year quick-picker

This phase implements quick month/year drill-down inside `bds-calendar-grid` as an internal view state, not a new public component.

### Task 46: quick-picker interaction model — UX confirmation (blocking gate)

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Confirm drill-down model before implementation:
  - month/year label click -> month grid
  - month click -> day grid for selected month
  - month-grid year button click -> year grid
  - year click -> month grid for selected year
- Specifically confirm year-click return target (month grid, not direct day grid).

**Manual test:** N/A — design/UX checkpoint.

---

### Task 47: month-grid/year-grid generators

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

- `generateMonthPickerGrid(year, currentMonth)` returns 12 month cells with current-month flag.
- `generateYearPickerGrid(centerYear, currentYear)` returns 12 year cells with current-year flag and applicable disabled handling.
- Both are pure, framework-agnostic, and follow existing generator conventions.

**Manual test (required):** Non-visual — unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(date-engine): EOA-17662 add month-picker and year-picker grid generators"`

---

### Task 48: quick-picker drill-down implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid/types/ICalendarGrid.ts` (modify), `bds-calendar-grid.tsx` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `bds-calendar-grid.tsx`'s `render()` currently renders the day grid unconditionally — confirm every existing render branch (single/dual instance, `min`/`max`-disabled cells, range day-states) is gated correctly behind `view === 'days'`, so introducing `view` doesn't silently change day-grid output when `view` is at its default.
- [ ] Boundary case: drilling into month/year view while a range selection is in progress (`rangeStart` set, `rangeEnd` unset) — confirm the in-progress selection persists correctly when drilling back to day view (it must, since Task 40's keyboard traversal and this task's drill-down both operate on the same grid instance's internal state) rather than being reset by the view transition.
- [ ] Default/empty state: `view` defaults to `'days'` on mount and on every reopen (mirroring the existing draft-reset-on-reopen convention) — confirm this explicitly, since a picker reopening mid-month-view (if `view` persisted across a close/reopen cycle) would surprise a returning user expecting the day grid.
- [ ] Reactivity: `view` is an internal `@State`, not a public prop — confirm this task's acceptance criteria don't imply any public API surface (per the phase's own framing: "internal view state, not a new public component"), and that `bdsMonthNavigate`'s existing event contract is unchanged by the addition (still fires only for day-grid month changes, not month/year-grid drill transitions, unless explicitly decided otherwise here).

**Acceptance criteria:**

- Adds internal `view: 'days' | 'months' | 'years'` state.
- Month/year header label becomes interactive and enters month view.
- Month click returns to day view and emits `bdsMonthNavigate`.
- Year click returns to month view for that year.
- Works independently across single and dual grid instances.

**Manual test (required):**

Playground scenarios to add:

- Scenario 1: single-date picker, click the month/year header label.
- Scenario 2: `calendarType='expanded'` + `range`, drill down independently on each grid instance.

Run `pnpm dev:components` and validate:

- [ ] Given Scenario 1, when the month/year label is clicked, then the month grid replaces the day grid. Pass: 12 month cells render, current month flagged.
- [ ] Given the month grid, when a month is clicked, then the day grid returns showing that month, and `bdsMonthNavigate` fires. Pass: correct month shown, event fired.
- [ ] Given the month grid, when the year button is clicked, then the year grid replaces it. Pass: 12 year cells render, current year flagged.
- [ ] Given the year grid, when a year is clicked, then the month grid returns for that year (per Task 46's confirmed model — not directly to the day grid). Pass: month grid shown for the selected year.
- [ ] Given Scenario 2, when one grid drills down, then the other grid's view state is unaffected. Pass: no shared/leaking view state between the two instances.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add month/year quick-picker drill-down"`

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

**Acceptance criteria:**

- Every research row above checked off before the first SCSS line is written, with the pulled value recorded.
- Token-only SCSS; no hardcoded colours, spacing, or radii.
- Every `State` × `Selected` × `State Actual` combination enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- `Disabled` cells (out-of-range years, if applicable) suppress the native focus outline — verify this isn't scoped only inside the interactive-state block.
- Verified against the **compiled** CSS output, not just the SCSS source — confirm each top-level selector matches the DOM `bds-calendar-grid.tsx` actually renders for `view: 'months' | 'years'`.
- JSDoc brevity/content compliance.

**Manual test (required):**

Reuse Task 48's Scenarios 1-2. Run `pnpm dev:components` and validate:

- [ ] Given each pulled Figma research row, when the compiled CSS is inspected, then every declared value matches the pulled value. Pass: no unaccounted-for hardcoded value.
- [ ] Given a month/year cell in each `State` × `Selected` × `State Actual` combination, when interacted with, then it renders per the pulled state matrix. Pass: visually matches Figma for all rows checked off above.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 style month/year quick-picker"`

---

### Task 50: Phase 9 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.quickpicker.spec.ts` (create), `date-engine/__test__/grid.spec.ts` (modify)

**Unit tests to cover:** grid-generator correctness; view-switch behavior; month/year selection transitions; dual-grid view-state independence. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 9 month/year quick-picker unit tests"`

---

### Task 51: Phase 9 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents quick-picker behavior needed by consumers and keeps it as automatic behavior (no new public props).

**Manual test (required):**

Run `pnpm dev:docs` and validate:

- [ ] Given the quick-picker MDX section, when read against Task 46's confirmed drill-down model and Task 48's actual implementation, then the documented behavior matches exactly. Pass: no stale/contradicting prose, no implied public API that doesn't exist.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 9 month/year quick-picker"`

---

### Task 52: React/Vue wrapper parity check — Phase 9

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Quick-picker behavior remains identical through wrappers.

**Manual test (required):**

Repeat Task 48's Scenarios 1-2 through both wrapper playgrounds using the pack-based verification pipeline. Validate:

- [ ] Given each scenario, when repeated through the React wrapper, then the drill-down cycle matches the raw web component exactly. Pass: no divergence in view transitions or `bdsMonthNavigate` firing.
- [ ] Given each scenario, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A

---

## Final task — consolidated mutation testing across v2 + v3

### Task 53: consolidated mutation testing — Phases 3, 3.5, 4 (carried over from v2) plus Phases 5-9

**Carried-over scope context (read before dispatching):** v2's "Testing and QA policy" section stated explicitly: *"coverage-phase tests are consolidated at the end of each covered phase block. Later-phase mutation consolidation now lives in version 3 scope."* v2 only ran a mutation-testing pass once, immediately after Phase 2 (its own Task 8) — Phases 3, 3.5, and 4 shipped and the v2 plan closed `done` with **no mutation-testing pass ever run against that code**. This task inherits that debt: it is not scoped to Phases 5-9 alone. Since the three Stryker configs below are package-wide (not per-phase), running them once naturally covers Phase 3/3.5/4 code alongside Phase 5-9 code — but the acceptance criteria must hold this task accountable for that coverage explicitly, not leave it as an incidental side effect.

**Executor:** @testing-subagent
**Files:**

- `date-engine/stryker.date-engine.config.mjs` (modify)
- `bds-date-picker/stryker.bds-date-picker.config.mjs` (modify)
- `bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` (modify)

**Acceptance criteria:**

- Mutation testing runs once, covering every `bds-date-picker`/`bds-calendar-grid`/`date-engine` surface added or modified since Phase 2's own mutation pass (v2's Task 8) — explicitly including Phase 3 (min/max), Phase 3.5 (`calendarType`), and Phase 4 (range) code that v2 never mutation-tested, not just Phases 5-9.
- Target >=90% mutation score per target area; survivors require either test fixes or documented exceptions.
- Test gaps found here are closed in the existing spec file for the phase that introduced the gap (Phase 3/3.5/4 spec files included, not only Phase 5-9 ones).

**Manual test (required):** run all three Stryker configs and confirm >=90% or documented exceptions, across the full carried-over scope above — not just Phase 5-9 files.

**Commit:** `git commit -m "test: EOA-17662 run consolidated mutation testing across v2 carried-over phases (3, 3.5, 4) and v3 phases (5-9)"`

---

## Remaining Open Questions

- **Phase 6 (Task 28):** fixed vs. configurable presets.
- **Phase 9 (Task 46):** final drill-down model confirmation (especially year-click return target).
- **Out of scope:** keyboard-typed date entry in the trigger field remains deferred.
- **Task 27a (done):** `format=""` crashed date-fns formatting — found during Task 27's QA pass, confirmed universal (raw component + both wrappers), fixed via `effectiveFormat`'s falsy check and verified live across all 4 previously-affected stories plus the `withTime=false` path.
- **Task 27b (done):** fixed a Storybook-only masking bug (`|| nothing` → `ifDefined`) that had made Task 27a's crash briefly appear non-reproducible in the affected stories, ensuring Storybook could actually verify Task 27a's fix.
