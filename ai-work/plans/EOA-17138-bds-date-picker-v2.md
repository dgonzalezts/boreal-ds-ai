---
ticket: EOA-17138
component: bds-date-picker
status: in progress
created: 2026-08-19
updated: 2026-08-24
---

# EOA-17138 — bds-date-picker v2 (ADR-0003 Phases 2–9) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

> **Scope expansion (2026-08-24):** originally this file covered Phase 2 (time selector) only, per the 2026-08-19 split from v1. Per the decision to close out the entire remaining roadmap next sprint, this file now also covers Phase 3 (min/max), Phase 4 (range), Phase 5 (dual time), Phase 6 (presets sidebar), Phase 7 (banner + range summary), Phase 8 (keyboard/a11y/RTL), and the previously-unscheduled month/year quick-picker (folded in here as Phase 9, since it has no cross-cutting reuse dependency on any other phase and no other version file exists for it). Tasks 1–8 (Phase 2) are unchanged from the original file. Tasks 9+ are new.
>
> **Explicitly excluded from this expansion:** keyboard-typed date entry in the trigger field (spike doc's "Unscheduled — keyboard-typed date entry" section, added 2026-08-19). This remains deferred, out of scope for `EOA-17138`, for the reasons already documented there (new architecture-decision spike, dependency on Phase 3's min/max UX, no Figma research done) — it is not implicitly reintroduced by this expansion and should not be picked up as a side effect of any task below.

**Goal:** Extend `bds-date-picker` (shipped in v1 as a single-date picker) with every remaining ADR-0003 roadmap phase in one sprint: an optional time selector, min/max constraints, date-range (dual calendar) support, dual time selection, a presets sidebar, an info banner with a footer range summary, full keyboard/a11y/RTL parity, and the month/year quick-picker — without breaking v1's naive-date `value` contract for consumers who use none of the above.

**Jira ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — sibling story to [EOA-16692](https://telesign.atlassian.net/browse/EOA-16692) (v1) under the same parent Feature (EOA-14927). Scope expanded 2026-08-24 to cover the full remaining roadmap (see ticket description).
**Ticket brief:** [`ai-work/tickets/EOA-17138-bds-date-picker-v2.md`](../tickets/EOA-17138-bds-date-picker-v2.md)
**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — see in particular the "Version Backlog (ADR-0003 Phases 3–8)" section and the "Unscheduled — month/year quick-picker" section, both now in scope here.
**v1 plan (Phase 0–1, prerequisite, done):** [`EOA-16692-bds-date-picker-v1.md`](./EOA-16692-bds-date-picker-v1.md)

**Versioning:** This file now covers Phases 2–9 in full — the last version file needed to close ADR-0003's originally-scoped roadmap, plus the quick-picker. Anything discovered mid-sprint that isn't covered by Phases 2–9 or the quick-picker (e.g. keyboard-typed entry, if ever picked up) still gets its own future `ai-work/plans/EOA-16692-bds-date-picker-vN.md` file per the established convention.

**Architecture:** Unchanged core shape from v1 — `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + one or two `bds-calendar-grid` bodies, FACE-compliant, draft-state-until-Apply). Each phase below is additive:

- Phase 2 composes a new `renderTimeSelector.tsx` helper.
- Phase 3 wires already-existing-but-unwired `date-engine`/`bds-calendar-grid` capacity (`isWithinRange`, `compareDates`, `DayCell.isDisabled`) — no new primitives expected.
- Phase 4 introduces the `range: boolean` prop (per ADR-0006/spike Finding 4) and a second `bds-calendar-grid` instance; the public `value` contract becomes `string | { start: string; end: string }` when `range` is on.
- Phase 5 reuses Phase 2's `renderTimeSelector.tsx`, parameterized for a start/end pair.
- Phase 6 adds a new `renderPresets.tsx` helper (presets sidebar) and a `utils/presets.ts` computation module.
- Phase 7 adds a new `renderBanner.tsx` helper and extends `renderFooter.tsx` with a range-summary label.
- Phase 8 wires the existing `src/utils/a11y/keyboard/navigation/grid-navigation.ts` utility into `bds-calendar-grid`, adds a live region, and audits RTL.
- Phase 9 (quick-picker) adds an internal `view: 'days' | 'months' | 'years'` state to `bds-calendar-grid` itself — it passes the reuse litmus test from the spike doc (a mode of the same dumb, controlled, reusable grid component), not a new registered element.

No external calendar UI library at any phase; light DOM throughout, matching the rest of Boreal (ADR-0001).

**Tech Stack:** Stencil, TypeScript, `date-fns@^4.4.0` + `@date-fns/tz@^1.5.0` (already added in v1's Task 1), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`), existing `src/utils/a11y/keyboard/navigation/grid-navigation.ts`.

---

## Testing and QA policy for this plan

**Two-phase test gate, coverage consolidated at the end of each phase block, mutation testing consolidated once at the very end of the whole file** — same convention as v1 and the original Phase 2 scope. Coverage-phase Jest tests (≥90% coverage) are written in one consolidated unit-test task per phase block, not embedded inline in implementation tasks. Mutation-phase (Stryker, ≥90% score) is deferred to the final task in this file (now renumbered to the last task overall) — it re-runs/extends the same three Stryker configs v1's Task 23 created, now covering every file every phase in this plan touches. Do not attempt the mutation-phase gate until that final task.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output** — implementation and SCSS tasks chain `@qa-subagent`; pure-logic, types-only, and test-only tasks keep a single executor.

**Blocking design-check-in gates** exist at the start of Phase 3 (min/max UX has no Figma mockup beyond a generic disabled-day token) and Phase 6 (presets configurability isn't resolved by any existing design or legacy-prop reference), and the quick-picker's drill-down interaction model (Phase 9) needs a UX confirmation before implementation, per the spike doc's own note that its interaction model is "inferred... not yet UX/UI-validated." Do not begin the corresponding implementation task until its gate is resolved.

**Wrapper parity is per-phase, not fully consolidated** — unlike v1/Phase 2 (a brand-new component with no behavior yet to diverge on), by Phase 3 `bds-date-picker` is an established, already-shipping component; per the writing-plans convention, each phase from here on gets its own React/Vue parity task immediately after that phase's documentation task, so a framework-specific regression is caught against the one feature that just landed, not buried in a single end-of-sprint pass.

**Grounded failure-mode/edge-case pass before every implementation task (added 2026-08-24, applies for the rest of this plan's execution):** before dispatching any remaining implementation task (Task 4 onward) to its executor, the orchestrating session must first read the actual current source of every file that task will touch — not just this plan's prose — and check for integration gaps the task's acceptance criteria may have missed (e.g. a helper/util function called from multiple sites that the task's Files list omitted, a public-API boundary case like a malformed prop value, a default-value/empty-state ambiguity, a runtime prop-toggling assumption). Real findings get folded into that task's acceptance criteria and manual-test scenarios (and propagated to any later task sharing the same root cause) before dispatch, the same way Task 3 was amended for the `utils/draft-state.ts` gap, the malformed-`value` fallback, the `00:00` default-time decision, and the `format` auto-switch. This is a standing instruction for this plan, not a one-off — any session picking this plan back up must do the same before dispatching Task 4, 6 (docs — lighter pass, mostly N/A), 9/10/11 (Phase 3), etc. Skip this pass only for tasks with no executor (blocking design gates) or no code surface (React/Vue parity, mutation-testing re-runs already scoped by their own task text).

---

## Files to create / modify

**Phase 2 (unchanged from original file):**

| File                                                                             | Notes                                                                     |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/services/date-engine/value.ts`               | New — `combineDateTimeToUTC`, `extractDateTimeFromUTC` via `@date-fns/tz` |
| `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts` | New — plain Jest                                                          |
| `.../bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx`             | New                                                                       |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                             | Modify — extend `DatePickerDraftState` with `hour`/`minute`               |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                        | Modify — `withTime` prop, time-selector wiring                            |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                       | Modify — time-selector styling                                            |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts`      | New                                                                       |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts`      | Modify                                                                    |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts`  | Modify — regression check only                                            |

**Phase 3 (min/max):**

| File                                                                          | Notes                                                                                             |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                          | Modify — extend `DatePickerDraftState`/props with `min`/`max`                                     |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                     | Modify — `min`/`max` props, helper-text wiring, whole-month-disabled guard on nav                 |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                 | Modify — wire already-existing `DayCell.isDisabled` fully (nav guard signal)                      |
| `packages/boreal-web-components/src/services/date-engine/date-math.ts`        | Modify (if needed) — wire already-implemented `isWithinRange`/`compareDates` into grid generation |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                    | Modify — disabled-date/helper-text styling                                                        |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.minmax.spec.ts` | New                                                                                               |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.variants.spec.ts`           | Modify — disabled-date regression                                                                 |

**Phase 4 (range):**

| File                                                                         | Notes                                                                                                                                 |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                         | Modify — `DatePickerDraftState` gains `rangeStart`/`rangeEnd`; public `value` type becomes `string \| { start: string; end: string }` |
| `.../bds-calendar-grid/types/ICalendarGrid.ts`                               | Modify — `DayCell` gains range-state fields (`isInRange`, `isRangeStart`, `isRangeEnd`)                                               |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                | Modify — render range day-states as CSS classes on the same `<td role="gridcell">`                                                    |
| `.../bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx`        | Modify — render one or two `bds-calendar-grid` instances based on `range`                                                             |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                    | Modify — `range: boolean` prop, dual-grid orchestration, start/end draft selection logic, header Start/End labels                     |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                   | Modify — dual-calendar layout per spike's Phase 4 pixel specs                                                                         |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                               | Modify — day-in-range/day-start/day-end token-driven styles                                                                           |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.range.spec.ts` | New                                                                                                                                   |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.variants.spec.ts`          | Modify — range day-state regression                                                                                                   |

**Phase 5 (dual time):**

| File                                                                        | Notes                                                                                      |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `.../bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx`        | Modify — parameterize for a label/position (`start`/`end`) so it's directly reusable twice |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                   | Modify — dual time wiring when `range && withTime`                                         |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                  | Modify — dual time-selector layout                                                         |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts` | Modify — dual time-selector coverage                                                       |

**Phase 6 (presets sidebar):**

| File                                                                           | Notes                                                                                                                         |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/helpers/renderPresets.tsx`                | New                                                                                                                           |
| `.../bds-date-picker/bds-date-picker/utils/presets.ts`                         | New — preset date-range computation (today/yesterday/last7/last30/thisMonth/lastMonth)                                        |
| `.../bds-date-picker/bds-date-picker/utils/__test__/presets.spec.ts`           | New                                                                                                                           |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                           | Modify — `DatePickerPreset` shape, `presets` prop type                                                                        |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                      | Modify — `presets` prop (built-in default + consumer-configurable override), sidebar wiring, only rendered when `range` is on |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                     | Modify — sidebar layout, option button states                                                                                 |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.presets.spec.ts` | New                                                                                                                           |

**Phase 7 (banner + range summary):**

| File                                                                          | Notes                                                                                                 |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `.../bds-date-picker/bds-date-picker/helpers/renderBanner.tsx`                | New                                                                                                   |
| `.../bds-date-picker/bds-date-picker/helpers/renderFooter.tsx`                | Modify — range-summary label (`"Range: {n} days"`) to the left of Clean/Cancel/Apply, range mode only |
| `.../bds-date-picker/bds-date-picker/types/types.ts`                          | Modify — `DatePickerBanner` shape (`title`, `message`, `closable`, `state`, `visible`)                |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.tsx`                     | Modify — `banner` prop, closable wiring                                                               |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                    | Modify — banner + summary label styling                                                               |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.banner.spec.ts` | New                                                                                                   |

**Phase 8 (keyboard/a11y/RTL):**

| File                                                                            | Notes                                                                                            |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                   | Modify — wire `src/utils/a11y/keyboard/navigation/grid-navigation.ts` for 2D arrow-key traversal |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                                  | Modify — RTL audit (logical properties, mirrored nav icons)                                      |
| `.../bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx`           | Modify — live region for month/year-change announcement                                          |
| `.../bds-date-picker/bds-date-picker/bds-date-picker.scss`                      | Modify — RTL audit for popover/footer/sidebar                                                    |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.keyboard.spec.ts`             | New                                                                                              |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts`                 | Modify — live region assertions                                                                  |
| `.../bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` | Modify — full grid-traversal coverage                                                            |

**Phase 9 (month/year quick-picker):**

| File                                                                            | Notes                                                                                                                                  |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `.../bds-calendar-grid/types/ICalendarGrid.ts`                                  | Modify — `view` state type, `MonthGridCell`/`YearGridCell` types                                                                       |
| `packages/boreal-web-components/src/services/date-engine/grid.ts`               | Modify — `generateMonthPickerGrid`/`generateYearPickerGrid` (pure functions, 12-month and 12-year-range grids)                         |
| `packages/boreal-web-components/src/services/date-engine/__test__/grid.spec.ts` | Modify — new grid generator coverage                                                                                                   |
| `.../bds-calendar-grid/bds-calendar-grid.tsx`                                   | Modify — internal `view: 'days' \| 'months' \| 'years'` state, drill-down/drill-up handlers, month-year header label becomes clickable |
| `.../bds-calendar-grid/bds-calendar-grid.scss`                                  | Modify — month-grid/year-grid cell styling                                                                                             |
| `.../bds-calendar-grid/__test__/bds-calendar-grid.quickpicker.spec.ts`          | New                                                                                                                                    |

**Shared, across every phase:**

| File                                                                            | Notes                                                                                                |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/index.html`                                 | Modify — playground scenarios per task (never committed)                                             |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` | Modify — one new story variant per phase                                                             |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx`        | Modify — one new section per phase                                                                   |
| `.../date-engine/stryker.date-engine.config.mjs`                                | Modify (final task) — re-run to cover every phase's `date-engine` additions                          |
| `.../bds-date-picker/stryker.bds-date-picker.config.mjs`                        | Modify (final task) — re-run to cover every phase's additions                                        |
| `.../bds-calendar-grid/stryker.bds-calendar-grid.config.mjs`                    | Modify (final task) — re-run; Phase 4/8/9 are the first phases since v1 to touch `bds-calendar-grid` |

**Critical reference files** (read before implementing):

- `EOA-16692-bds-date-picker-v1.md` — Phase 0–1 implementation this plan extends.
- `ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md` — read the full "Version Backlog" and "Unscheduled — month/year quick-picker" sections before starting the corresponding phase; each phase's task below only summarizes it.
- `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts` — existing generic grid-keyboard utility, Phase 8's integration point (already flagged in v1's Task 9 code comment).
- `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx` — the component the hour/minute fields compose (Phase 2/5).

---

## Phase 2 — Time selector

_(Tasks 1–8 unchanged from the original file — see full acceptance criteria as originally written; summarized here for continuity.)_

### Task 1 (was Task 23): `date-engine` timezone-aware value conversion

**Status:** ✅ done (2026-08-24) — `value.ts` created (`combineDateTimeToUTC`/`extractDateTimeFromUTC` via `@date-fns/tz`'s `TZDate`), exported through the `date-engine` barrel (`index.ts`). `types.ts` gained a `DateTimeParts` interface (`{ date: Date; hour: number; minute: number }`), matching this module's convention of centralizing shared interfaces there rather than declaring them inline. 5 tests in `value.spec.ts` (round-trip for a DST-observing zone and a non-DST zone, differing UTC offset across the LA DST boundary, constant offset for Tokyo, and a spring-forward-gap edge case), independently re-run: 5/5 passing. No `any` types. `tsc --noEmit`: no new errors (pre-existing unrelated errors in other components confirmed unaffected via grep). `eslint`: clean.

**Executor:** @frontend-subagent
**Files:** `packages/boreal-web-components/src/services/date-engine/value.ts` (create), `.../date-engine/__test__/value.spec.ts` (create)

**Acceptance criteria:**

- Exports `combineDateTimeToUTC(datePart: Date, hour: number, minute: number, timezone: string): string` and `extractDateTimeFromUTC(isoUtc: string, timezone: string): { date: Date; hour: number; minute: number }` via `@date-fns/tz`'s `TZDate`.
- Handles DST transitions correctly (no silent wrong-by-one-hour result on a fold/gap).
- No existing timezone utility found anywhere in `src/` — new module justified; document the library choice in the file's header comment.

**Manual test (required):** Non-visual — validate via `tsc --noEmit` plus a manual console check against `Asia/Tokyo` and `America/Los_Angeles` (DST boundary).

**Commit:** `git commit -m "feat(date-engine): EOA-17138 add timezone-aware date-time to UTC ISO conversion"`

---

### Task 2 (was Task 24): `bds-date-picker` time selector — design check-in (blocking gate)

**Status:** ✅ done (2026-08-24) — resolved via a user-provided reference screenshot; see the confirmed-design note below.

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Before Task 3 begins, confirm the inferred single-date hour:minute UI with the user (Figma only shows the dual Inicio/Fin range variant).
- Document the confirmed design as a short addendum before proceeding.

**Confirmed design (2026-08-24):** the single-date time selector is a bare, unlabeled hour/minute field pair — clock icon followed by the two 58px bordered `Select` fields (as already described in the Task 4 Figma research pass), with no "Inicio"/"Fin"-style label, since a single date has nothing to disambiguate. Confirmed against a reference screenshot showing the header `2021/07/20 08:30` panel: clock icon + unlabeled `08`/`30` fields. The range variant (Phase 5) does carry `Start:`/`End:` labels next to each pair, per the same reference — consistent with the spike doc's existing Phase 5 documentation.

**Manual test:** N/A — design checkpoint.

---

### Task 3 (was Task 25): `bds-date-picker` time selector implementation

**Status:** ✅ done (2026-08-24) — independently verified, not just trusted from the subagent report: read `bds-date-picker.tsx`/`utils/draft-state.ts`/`utils/value-mapping.ts`/`helpers/renderTimeSelector.tsx` line-by-line against every amended acceptance criterion (all matched); independently re-ran `node -e` against `@date-fns/tz`'s `TZDate#toISOString()` to confirm the subagent's offset-preservation claim (verified true — a corrected, load-bearing memory entry, `stencil-date-engine-tzdate-timezone-conversion.md`, now documents this); independently re-ran the full `bds-date-picker` test suite (137 passed, 1 pre-existing todo — matches report exactly) and `tsc --noEmit` (zero date-picker errors, 5 pre-existing unrelated). Real bug found and fixed during implementation: `bds-select`'s bubbling `bdsChange`/`valueChange` collided by name with `bds-date-picker`'s own public events — fixed via `stopPropagation()` in `renderTimeSelector.tsx`. One design gap caught during review (not a Task 3 code issue): the hour/minute fields need `label="Hour"`/`label="Minute"` set for `aria-labelledby` to wire correctly (`bds-text-field` has no accessible-name mechanism when `label=''`, and no attribute-forwarding for a raw `aria-label`), which conflicts with Task 2's "bare, unlabeled" Figma reference. Resolved via a visually-hidden/`sr-only` CSS treatment of the already-rendered `bds-typography` label element (light DOM, no `bds-text-field` changes needed) — folded into Task 4's acceptance criteria, not a Task 3 rework.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderTimeSelector.tsx` (create), `types/types.ts` (modify), `bds-date-picker.tsx` (modify), `utils/draft-state.ts` (modify — `resetDraft` must derive `hour`/`minute` from a committed `value` when `withTime=true`, and `commitValue`'s Apply-time computation must combine `draft.selectedDate` + `draft.hour`/`draft.minute` via `combineDateTimeToUTC` instead of using the naive date string directly)

**Acceptance criteria:**

- `@Prop() readonly withTime: boolean = false` gates the time selector rendering inside the popover body.
- Composes two `bds-select` instances (hour 00–23, minute 00–59) — not a new registered custom element.
- Time changes update `this.draft.hour`/`this.draft.minute` only.
- `withTime=false` keeps the naive `yyyy-MM-dd` value contract (Phase 1 regression check).
- `withTime=true` computes the UTC ISO string via `combineDateTimeToUTC` on Apply, using `this.timezone` — `resetDraft` and the Apply-path `commitValue` call (currently `this.commitValue(this.draft.selectedDate)`, a naive-string passthrough) are the two integration points that must change; both are reused as-is by Cancel/Clean/`formResetCallback`/`listenClickTrigger`, so fixing them here is sufficient — no separate per-caller changes needed.
- Loading an existing `withTime=true` datetime `value` pre-populates draft date/hour/minute via `extractDateTimeFromUTC`.
- **Default time (confirmed 2026-08-24):** a fresh draft with no time to pre-populate — no prior committed `value`, or the malformed-value fallback below — defaults `draft.hour`/`draft.minute` to `0`/`0` (`00:00`), the same as any other form default; Apply is never blocked on the user having touched the time selects.
- **Malformed/mismatched `value` guard:** if `withTime=true` but the committed `value` doesn't parse as a valid UTC ISO datetime (e.g. a stale naive-date string left over from `withTime` being toggled on after a v1-style value was already set), `resetDraft` falls back to the same `00:00` default used for a fresh, value-less draft, rather than propagating a `NaN`/`Invalid Date` into the time selects or throwing. Add a unit test for this fallback in Task 5.
- Hour/minute `bds-select` labels use the existing `labels?: DatePickerFooterLabels`-style override mechanism, not hardcoded strings.
- **Runtime `withTime` toggling is unsupported and undocumented behavior**, matching `range`'s expected static-config usage (Phase 4) — `withTime` is set once at mount by the consumer, not flipped live in response to user interaction. No `@Watch('withTime')` reconciliation is implemented in this phase; note this explicitly in the JSDoc for `withTime` (Task 4) so it isn't silently assumed to be reactive.
- **`format` auto-switch (confirmed 2026-08-24, per Figma's `_DatePickerField` `Format` variant property — `YYYY/MM/DD` vs. `YYYY/MM/DD HH:mm`):** when `withTime=true` and the consumer has not explicitly overridden `format` (i.e. `this.format` is still the class's static default `'yyyy/MM/dd'`), the trigger field and popover header display using `'yyyy/MM/dd HH:mm'` instead. An explicitly-set `format` prop (any value, including one identical to the default) always wins over the auto-switch — implemented by comparing against the literal default constant, not by adding `@Watch` tracking of "was this prop passed." `withTime=false` leaves `format`'s existing v1 default/behavior untouched (regression guard).

**Manual test (required):** `pnpm dev:components` — Scenario 1: enable `with-time`, pick day+time, Apply, confirm UTC ISO output. Scenario 2: two instances, different `timezone`, same wall-clock selection, confirm differing UTC output. Scenario 3: pre-loaded datetime `value`, confirm day/hour/minute pre-selected on open. Scenario 4: enable `with-time` without setting `format`, confirm trigger field and popover header both display `HH:mm` alongside the date. Scenario 5: enable `with-time` AND pass an explicit `format` (e.g. `'MM/dd/yyyy HH:mm'`), confirm the explicit value is used, not the auto-switched default.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add single time selector for Phase 2"`

---

### Task 4 (was Task 26): `bds-date-picker` Phase 2 SCSS + JSDoc audit

**Status:** 🔄 in progress (2026-08-24) — icon and label/gap/JSDoc work verified done (see prior note below). Background-band gap found via Figma comparison; first fix attempt used `background: $boreal-ui-default-base` + negative-margin full-bleed, but independent verification (re-checking the compiled bundle, not just the report) found two real problems: (1) `-$boreal-spatial-padding-l` in Sass produces invalid CSS (`margin: 0 -var(--boreal-spatial-padding-l)`) since these tokens resolve to `var()` references, not literal numbers — the exact gotcha already documented in `sass-design-tokens-are-css-vars-not-literals.md`; the margin declaration was silently dropped, so no full-bleed happened; (2) `$boreal-ui-default-base` resolves to pure white (`#ffffff`) in the Proximus theme at runtime, which initially looked like a wrong-token mismatch against Figma's `#f7f7f8` fallback — **corrected**: the user provided Figma's own Layer Properties panel, confirming `ui(components)/default-base` (= `$boreal-ui-default-base`) IS the correct background token; the panel's theme mode was "Auto (engage)," not Proximus, so the apparent value mismatch was expected theme-token variance, not a wrong token choice. Panel also confirmed padding (`spatial/padding/xs` top/bottom, `spatial/padding/l` left/right — already correct), the inner-shadow spec (`X:0 Y:1 Blur:0 Spread:0`, `ui(components)/base-light` — already correct), `Height: Hug (48px)`, and content dimensions `248×32px` (confirming the earlier `elWidth: 248` measurement was correct all along, not a bug — it's the right content width once the row escapes `popover-content`'s own padding). **Architecture changed per user direction**: instead of negative-margin/padding tricks to fake full-bleed inside `bds-popover`'s padded content area, render the time-selector as a genuinely full-width sibling region — matching how `.popover-header`/`.popover-content`/`.popover-footer` already exist as three sibling `<div>`s in `bds-popover.tsx`'s own render tree. This requires a new named slot on `bds-popover` itself (shared by `bds-select`/`bds-dropdown` too — confirmed blast radius: only 3 consumers total), auto-detected via the existing `hasSlotContent(el, slotName)` utility (zero new public prop, backward-compatible for the other two consumers).

**`content-band` slot implemented and independently verified**: full-bleed geometry confirmed exact via direct measurement (`left: 240` matching the popover's own edge, `width: 296` matching the popover's full width, `height: 48` matching Figma's `Height: Hug (48px)` spec) — not just trusted from the report. Test suite independently re-run: 28 suites, 336 tests, 0 failures. One genuine implementation-time bug the subagent caught and fixed correctly, confirmed by tracing `anchoredMixin.componentWillLoad` directly: a first-pass `componentWillLoad()` on `BdsPopover` without `override`/`super.componentWillLoad()` silently shadowed the Mixin's own lifecycle hook (which constructs `positionEngine`), breaking every `openPopover()` call across the whole suite — caught via a before/after test diff, not luck.

**A second, real, pre-existing regression found during my own independent live verification (2026-08-24) — not caught by the automated suite**: opening the hour/minute `bds-select` dropdowns shows an empty-looking list, only 10px wide (confirmed via `getBoundingClientRect()` — items exist with correct text "00"-"23"/"00"-"59", just clipped invisible). Root cause traced and confirmed via computed-style inspection: `bds-date-picker.scss`'s `bds-popover { --popover-content-padding: ...; }` rule (nested under `bds-date-picker { ... }`) compiles to the descendant selector `bds-date-picker bds-popover`, which matches _every_ `bds-popover` inside the tree — including the deeply-nested `bds-select`'s own internal dropdown popover, not just the date-picker's immediate one. Confirmed the nested select's popover computed `--popover-content-padding: 12px 24px` (the date-picker's own value, wrongly inherited) — 58px trigger width − 24px × 2 = 10px, matching the observed bug exactly. This bug has existed since Task 3 first introduced the time selector; never surfaced until a dropdown was actually opened during verification. Confirmed `bds-popover` is a direct child of `bds-date-picker` in the DOM, so the fix is scoping the selector to a direct-child combinator. Re-dispatched to `@frontend-subagent`.

**Status:** ✅ done (2026-08-24) — the direct-child-combinator fix alone was insufficient; the subagent found and corrected a more precise root cause I under-specified: the nested `bds-select` popover isn't merely "somewhere in the DOM subtree" — it's a literal descendant of the date-picker's _own_ `bds-popover` element (confirmed via `pop.contains(selectPop) === true`), so CSS custom-property _inheritance_ keeps carrying the value down regardless of which selector originally set it, independent of the `>` combinator fix. Final fix: kept `bds-date-picker > bds-popover { ... }` (still correct, prevents the rule from setting wrong values elsewhere) plus an explicit `initial` reset on all four `--popover-*-padding`/`-gap` custom properties for any `bds-popover` nested inside it, so a nested popover falls through to `bds-popover`'s own component defaults via `var(--x, <default>)`. `[slot='header-title']` investigated and confirmed safe (only the date-picker's own header assigns to that slot name anywhere in the codebase). Independently re-verified, not just trusted from the report: re-ran the affected test suite myself (28 suites, 336 tests, 0 failures — matches exactly); live `playwright-cli` check confirmed the hour select's dropdown now shows all 24 items ("00"-"23") at a readable 34px width (was ~10px, clipped), `--popover-content-padding` computed as empty/unset on the nested popover (correctly falling through to component default) instead of the leaked `12px 24px`; visually confirmed via screenshot. Separately, re-pulled Figma's raw `get_metadata` on node `14:24957` after the user raised doubt about the Figma reading's accuracy — confirmed the `"Start:"`/"Label" text child the user's structure screenshot showed is `hidden="true"` for this single-date instance (consistent with Task 2's already-confirmed no-visible-label decision), and every other structural measurement (icon/gap/field-size/padding) is internally consistent with what's already implemented. **Task 4 is now fully complete**, closing out the timer icon, visually-hidden label, full-width background band, and this nested-popover-padding-leak fix — four real bugs found and fixed via independent live-browser verification beyond what the automated test suite alone would have caught.

**Status (2026-08-26) — follow-up items resolved:**
- The user manually applied a fifth fix outside the SCSS the subagent produced: `bds-select`'s own nested dropdown list was overflowing horizontally (list items wider than the 58/62px hour/minute field), matched against a Figma before/after screenshot. Their first version zeroed padding via a raw `.popover-content { padding: 0; }` class selector nested inside `.bds-date-picker__time-selector` — I validated it against the actual DOM (`bds-select.tsx:791` renders its own light-DOM `<bds-popover>`, so the selector does correctly reach it, and its `(0,2,0)` specificity reliably wins) but flagged the coupling risk: it reaches into `bds-popover`'s internal implementation class name instead of its own documented `--popover-content-padding` custom property, the same public-API mechanism the file already uses two rules above it for the outer popover reset. Replaced with `bds-select bds-popover { --popover-content-padding: 0; }`, scoped to only the selects' own nested popovers — independently re-verified live via `playwright-cli` (hour dropdown renders at full field width, no scrollbar, no clipping).
- Considered and rejected styling the list's native OS scrollbar to match Figma's polish more closely: no `scrollbar` CSS exists anywhere in `boreal-web-components` today, Figma's "Basic Time Picker" component defines no scrollbar state to match against, and a one-off override here would make this list inconsistent with every other scrollable surface in the design system (`bds-list-menu`, `bds-table`, etc.). Left out of scope; if ever wanted, it belongs as a token-driven treatment on `bds-list-menu.scss` itself, not a `bds-date-picker`-local hack — not logged as a plan task per user direction (explicitly out of scope for now, not deferred).
- The `content-band` slot itself was reconsidered against three less-intrusive, `bds-popover`-code-untouched alternatives (reusing the existing `footer-helper` slot with `order: -1`; a `calc()`-based negative-margin workaround; zeroing `--popover-content-padding` and pushing padding into each child) — user confirmed keeping `content-band` as implemented; alternatives documented in conversation only (not written into the plan, since the decision didn't change).
- **The subagent's recommended CSS-custom-property-inheritance regression test is *not* the same gap as the `content-band` slot's missing unit coverage** — the former needs real browser layout/computed-style (out of `newSpecPage`'s reach, still an open follow-up, not yet scoped to a task) and the latter (`hasContentBand` slot-detection logic, and the `componentWillLoad` mixin-shadowing guard) *is* directly unit-testable and was a genuine, previously untracked gap — folded into Task 5's scope below.

**Prior verification (icon/label/gap/JSDoc), independently confirmed, not just trusted from subagent reports:** `$boreal-spatial-gap-2xs` (4px) is a real token matching Figma exactly; `--bds-text-field-width` is a genuine documented `bds-text-field` custom property; `%visually-hidden` in `_commons.scss` uses the correct standard clip-to-1px technique (never `display:none`); `effectiveFormat`'s JSDoc removed, matching every sibling private getter's undocumented convention; `ICONS.Timer` added and rendered via `bds-icon()` mixin at `$boreal-icons-m` (confirmed 16px), verified live via `playwright-cli` at exactly 16×16px with `aria-hidden="true"`, no regression to accessible names or console warning count. Hover/focus/active states correctly deferred (shared `_form-field-shell.scss` component, out of scope — recommend a separate follow-up task). Error state confirmed already correct via existing generic `&--error` rule.

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify), `bds-date-picker.tsx` (modify — JSDoc), `helpers/renderTimeSelector.tsx` (modify — add the missing timer icon, found during review), `src/utils/constants/common/Icons.ts` (modify — add `Timer: 'bds-icon-timer'`)

**Figma research pass (complete before writing any SCSS):**

- [x] Region: hour/minute fields — default state — **pulled 2026-08-24** via `get_design_context` on node `14:24957` (`_Basic Time picker`, fileKey `rtiE5zGA4aoOuxIQMgfD6h`): field background `var(--ui-(components)/inverse, white)`; border `var(--stroke/xs, 1px)` solid `var(--stroke/default-light, #e3e3e6)`; radius `var(--radius/xs, 4px)`; padding `var(--spatial/padding/xs, 8px)` left, `var(--spatial/padding/1xs, 6px)` right/vertical; value text Inter Regular 14px, `var(--typography/line-height/sm, 20px)`, `var(--text/default-darker, #131316)`; icon+fields gap `var(--spacing/2xs, 4px)`; gap between the two Select fields `var(--spatial/gap/2xs, 4px)`; field-internal gap (value↔disclosure) `var(--spatial/gap/xs, 8px)`; disclosure icon 20×20px; timer icon 16×16px. **Known gap in the current placeholder**: `bds-date-picker.scss`'s `.bds-date-picker__time-selector` rule (added incidentally during Task 3) uses `$boreal-spatial-gap-xs` (8px) — must be corrected to the 4px (`2xs`) gap confirmed above.
- [ ] Interaction: hour/minute fields — hover/focus/active _(not yet pulled)_
- [ ] Modifier: hour/minute fields — validation/error state, if it exists _(not yet pulled)_
- [ ] Dimensions: hour/minute field width/height against the popover body's confirmed 296×434px panel, 24px/12px padding

**Acceptance criteria:**

- Every research-pass row checked off, with the pulled value recorded, before the first SCSS line.
- `$boreal-*` tokens exclusively.
- **JSDoc audit scope (confirmed 2026-08-24):** limited to `@Prop`/`@State`/`@Event`/`@Method` members only — the file's existing, established pattern (`bdsField`/`bdsPopover`/`validators`/`validityAnchor` private getters, `handleDayClick`/`listenClickTrigger`-style private handlers all carry zero JSDoc; `@Method() checkValidity`/`reportValidity` are the only non-Prop/State/Event members that legitimately do, as genuine public API surface). Verified `withTime`, `value`, `format`, `timezone`, and `draft` already have accurate JSDoc from Task 3. **One real fix required**: `effectiveFormat` (a private getter Task 3 added) currently carries a JSDoc block — remove it to match every sibling private getter's undocumented convention; its behavior is already covered by `format`'s own `@Prop` JSDoc, which documents the auto-switch from the public-API side.
- **Label accessibility (confirmed 2026-08-24):** the hour/minute `bds-select`/`bds-text-field` pair keeps `label="Hour"`/`label="Minute"` (per Task 3) so `aria-labelledby` wires correctly on each inner `<input>` — `bds-text-field` has no accessible-name mechanism when `label=''`, and no attribute-forwarding mechanism for a raw host-level `aria-label` either, so an empty label would leave the field with no accessible name at all. Instead, the rendered `bds-typography` label element (light DOM, directly targetable — no `bds-text-field` changes needed) is visually hidden within `.bds-date-picker__time-selector` using the standard visually-hidden/`sr-only` technique (clipped, 1px, `overflow: hidden` — never `display: none`, which strips some browser/AT combinations from the accessibility tree). Net result: bare visually (matching Task 2's confirmed Figma reference), with a real accessible name for screen readers.

**Manual test (required):** Reuse Task 3's scenarios; `pnpm dev:components` — visual match against the confirmed Task 2 design. Additional scenario: inspect the hour/minute fields' accessible name via the browser DevTools accessibility panel (or a screen reader), confirm "Hour"/"Minute" is announced despite no visible label text on screen.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style time selector and finalize Phase 2 JSDoc"`

---

### Task 5 (was Task 27): `bds-date-picker` + `date-engine` Phase 2 unit tests (consolidated)

**Status:** ✅ done (2026-08-26) — first end-to-end run of the new failure-mode catalog pipeline (`testing-knowledge`'s "Failure-Mode Catalog"). Catalog created at `ai-work/testing/failure-modes/bds-date-picker.md` (16 rows; none existed before, so the whole component was audited, not just this task's diff). 15 rows confirmed and covered (`Covered by` recorded per row); 1 (FM-10) surfaced a genuine gap between Task 3's stated acceptance criterion ("an explicit `format` always wins over the auto-switch, even one identical to the default") and what the shipped `effectiveFormat` getter could actually distinguish — ruled to fix properly rather than document as a limitation. `frontend-subagent` closed it by making `format` genuinely optional (`undefined` as the true unset sentinel) instead of adding a provenance flag; blast radius confirmed to two read sites in the whole file. 13 new tests added (`bds-date-picker.time.spec.ts`, new file, 13 tests; `bds-popover-basics.spec.ts` extended, 3 tests for the `content-band` slot and its `componentWillLoad` mixin-shadowing regression guard). Coverage gate passed: 96.11% statements / 87.23% branches / 150 passed, 1 pre-existing todo. Mutation testing correctly deferred per this file's own policy (consolidated at the final task). `bds-popover`'s pre-existing 69% aggregate coverage (unrelated to this task's addition, which is itself fully covered) logged separately as Task 8b rather than folded in here.

**Executor:** @testing-subagent
**Files:** `value.spec.ts`, `bds-date-picker.time.spec.ts`, `bds-date-picker.a11y.spec.ts` (extend), `bds-date-picker.keyboard.spec.ts` (extend), `bds-popover-basics.spec.ts` (extend — new `content-band` slot, shared with `bds-select`/`bds-dropdown`)

**Unit tests to cover:** zone conversion (positive/negative offset, DST boundary), round-trip, invalid-timezone handling; `withTime=false` naive-date regression; `withTime=true` UTC computation, `timezone` override, pre-population, Cancel discarding time draft; `resetDraft`'s fallback to default hour/minute when `withTime=true` and the committed `value` doesn't parse as a valid UTC datetime (malformed/mismatched-shape guard); `format` auto-switch to `'yyyy/MM/dd HH:mm'` when `withTime=true` and `format` unset, explicit `format` always overriding the auto-switch, and `withTime=false` leaving `format`'s default behavior unchanged; a11y (Tab reachability, labeling); keyboard regression.

**`bds-popover` `content-band` slot (new in this task's SCSS/JSDoc audit, currently zero coverage in any `bds-popover` spec file):** `.popover-content-band` renders when content is assigned to the `content-band` slot, and is absent when it isn't (regression guard for the other two consumers — `bds-select`/`bds-dropdown` — that don't use this slot and must see no behavior change); `hasContentBand` is computed once in `componentWillLoad`, before Stencil's light-DOM slot relocation; regression guard for the `override componentWillLoad` + `super.componentWillLoad()` chain — assert `anchoredMixin`'s own setup (e.g. `positionEngine` construction / `openPopover()` still functioning) is intact, protecting against the exact mixin-shadowing bug this task's implementation hit and fixed. Coverage-phase only (≥90%); mutation deferred.

**Manual test (required):** Non-visual — full suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add consolidated Phase 2 unit tests for date-engine value conversion and bds-date-picker time selector"`

---

### Task 6 (was Task 28): `bds-date-picker` Phase 2 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the Phase 2 UTC value contract vs. Phase 1 naive-date contract; notes the single time-selector UI was an inferred design; documents `timezone` behavior with a before/after example.

**Manual test (required):** `pnpm dev:docs` — new `withTime` story renders and interacts correctly; MDX contrast is unambiguous.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 2 time selector and UTC value contract"`

---

### Task 7 (was Task 29): React/Vue wrapper parity check — Phase 2

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms `withTime` behavior identically through `boreal-react`/`boreal-vue` via `dev:pack:react`/`dev:pack:vue`. Regressions logged as new tasks, not patched inline.

**Manual test (required):** Repeat Task 3's three scenarios through both wrapper playgrounds.

**Commit:** N/A — verification-only.

---

### Task 8 (was original Task 8): consolidated mutation testing for Phase 2

> **Superseded — renumbered.** This task is now folded into the final consolidated mutation-testing task at the end of this file (covering every phase, not just Phase 2), to avoid running Stryker twice against overlapping configs in one sprint. Do not run mutation testing here; proceed directly to Phase 3.

---

### Task 8b (new — discovered during Task 5's failure-mode catalog audit, 2026-08-26): `bds-popover` coverage backfill — pending

**Status:** 🔲 pending, not yet scoped to an executor or sprint.

**Discovered by:** `testing-subagent`'s failure-mode catalog audit for Task 5. `bds-popover`'s aggregate statement coverage sits at 69% — the specific lines Task 5 itself added (the `content-band` slot's `hasContentBand`/`componentWillLoad` override and its render block) are fully covered; the gap is entirely pre-existing, in unrelated areas (focus/click-outside edge cases, arrow positioning) that predate this plan and aren't part of any phase's stated scope here.

**Why this isn't folded into Task 5 or any other task in this file:** `bds-popover` is shared infrastructure (`bds-select`/`bds-dropdown` are its other two consumers, confirmed during Task 4's `content-band` slot work) — a coverage pass on it is a `bds-popover`-scoped effort, not a `bds-date-picker`-scoped one, and expanding Task 5 to cover it would have been exactly the kind of silent scope creep `plan-execution.md` warns against.

**Next step:** re-scope into its own ticket/plan (likely `ai-work/plans/` filed against `bds-popover` directly, not this date-picker plan) before picking it up — not implicitly reintroduced by any later phase in this file.

---

## Phase 3 — Min/max date constraints (single)

Per the spike doc's Roadmap risks item 4: design coverage is thin (only a generic "Day disabled" style token, no interaction spec for boundary dates). `isWithinRange`/`compareDates` (date-engine) and `DayCell.isDisabled` (`bds-calendar-grid` types) are already implemented and unwired since v1's Task 7 — this phase wires them, it does not build new date-math primitives.

### Task 9: min/max UX design check-in (blocking gate)

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Present a proposed interaction design to the user for confirmation before Task 11 begins, covering: whether a disabled cell shows a tooltip/message explaining why, what happens when an entire visible month falls outside `min`/`max` (per the React Aria pitfall the spike doc flags — a month can become unreachable via navigation), and whether `min`/`max` violations surface via the trigger field's helper text (Vaadin's recommended pattern, cited in the spike doc) or silently.
- Reference points to bring to the check-in: React Aria's `isDateUnavailable` predicate model, Vaadin's helper-text-pairing recommendation, react-day-picker's `aria-disabled` + `aria-live` pattern, Ant Design's `disabledDate`, MUI X's `shouldDisableDate` (and its "runs against every possible date" performance pitfall — avoid this from the start).
- Document the confirmed design as a short addendum before Task 11 starts.

**Manual test:** N/A — design checkpoint.

---

### Task 10: `date-engine` min/max wiring

**Executor:** @frontend-subagent
**Files:** `packages/boreal-web-components/src/services/date-engine/date-math.ts` (modify if needed), `.../date-engine/__test__/date-math.spec.ts` (modify)

**Utility discovery note:** `isWithinRange`/`compareDates` already exist and are fully implemented (v1 Task 4) but unwired — confirm their existing signatures satisfy this phase's needs before adding anything new; do not duplicate.

**Acceptance criteria:**

- `generateMonthGrid` (or a thin wrapper called from `bds-calendar-grid`) accepts optional `min`/`max` `Date` bounds and marks each `DayCell.isDisabled = true` when the cell's date falls outside them, using the existing `isWithinRange`.
- No change to the fixed 6-week/42-cell grid shape.
- Whole-month-disabled detection: exposes a way for the caller to determine whether every cell in the currently displayed month is disabled (for the nav-guard in Task 11).

**Manual test (required):** Non-visual — validate via unit test additions and `tsc --noEmit`.

**Commit:** `git commit -m "feat(date-engine): EOA-17138 wire min/max bounds into month grid generation"`

---

### Task 11: `bds-date-picker` min/max props + nav guard + helper text

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `types/types.ts` (modify), `bds-date-picker.tsx` (modify), `bds-calendar-grid.tsx` (modify — pass disabled state through, no new markup)

**Acceptance criteria:**

- `@Prop() readonly min?: string` / `@Prop() readonly max?: string` (naive ISO date strings, matching the `value` contract), both optional and unbounded when absent.
- Disabled day cells (per Task 10's wiring) are visually shown (`text/disabled` token, matches v1's out-of-month treatment) and functionally inert — no click, not tab-focusable — reusing the exact interactivity pattern v1 already established for out-of-month cells (avoids reopening `bds-calendar-grid`'s core click/tab logic).
- Month navigation is guarded per Task 9's confirmed design when an entire target month would be fully disabled (e.g. disable the nav button, or skip past it — whichever was confirmed).
- Helper text on the consumer's slotted trigger field communicates the accepted range when `min`/`max` are set, per Task 9's confirmed design (if that was the chosen behavior) — pushed via the same `updateElementProp` mechanism already used for `value`/`selectable`/`disabled`.
- A date outside `min`/`max` passed in as an existing `value` on load is handled per Task 9's confirmed design (documented, not silently accepted).

**Manual test (required):** `pnpm dev:components` — Scenario 1: set `min`/`max`, confirm out-of-range cells are inert and correctly styled. Scenario 2: navigate to a month entirely outside range, confirm the guarded nav behavior. Scenario 3: confirm helper text appears/updates per the confirmed design.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add min/max date constraints"`

---

### Task 12: Phase 3 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify), `bds-calendar-grid.scss` (modify), `bds-date-picker.tsx` / `bds-calendar-grid.tsx` (JSDoc)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: disabled day cell — confirm `text/disabled` treatment matches the out-of-month styling exactly (already pulled in v1's spike, re-verify no drift)
- [ ] Region: helper text (if Task 9 confirmed it) — default and error/warning variants on the trigger field
- [ ] Modifier: disabled nav button (if Task 9 confirmed guarding nav rather than skipping)

**Acceptance criteria:** Every row checked off before SCSS; `$boreal-*` tokens exclusively; JSDoc for `min`/`max` complete.

**Manual test (required):** Reuse Task 11's scenarios visually.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style min/max constraints and finalize JSDoc"`

---

### Task 13: Phase 3 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.minmax.spec.ts` (create), `bds-calendar-grid.variants.spec.ts` (modify), `date-math.spec.ts` (modify)

**Unit tests to cover:** date-math bound-checking correctness at boundary edges (inclusive `min`/`max`); disabled-cell rendering and inertness (no click, `tabindex="-1"`); whole-month-disabled nav-guard behavior; helper-text rendering per Task 9's confirmed design; out-of-range initial `value` handling. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 3 min/max unit tests"`

---

### Task 14: Phase 3 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents `min`/`max` props, boundary behavior, and the whole-month-disabled nav guard; new story variant demonstrating a bounded range.

**Manual test (required):** `pnpm dev:docs` — new story renders and behaves correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 3 min/max constraints"`

---

### Task 15: React/Vue wrapper parity check — Phase 3

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms `min`/`max` behavior identically through both wrappers via the pack-based pipeline.

**Manual test (required):** Repeat Task 11's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 4 — Dual calendar (date range)

Per the spike doc's Findings §4/Resolved Decisions: one `bds-date-picker`, a `range: boolean` prop — not a second custom element. Day states unique to range mode (day-in-range, day-range-start, day-range-end) render as additional CSS classes on the existing `<td role="gridcell">`, not a markup change.

### Task 16: types — range value contract and day-state fields

**Executor:** @frontend-subagent
**Files:** `types/types.ts` (modify), `bds-calendar-grid/types/ICalendarGrid.ts` (modify)

**Acceptance criteria:**

- Public `value` type becomes `string | { start: string; end: string }`; `range=false` (default) keeps the existing `string` shape untouched — verified as a non-breaking union widening, not a rename.
- `DatePickerDraftState` gains `rangeStart: string | null` / `rangeEnd: string | null`.
- `DayCell` gains `isInRange: boolean`, `isRangeStart: boolean`, `isRangeEnd: boolean` — all default `false`, purely additive to the existing type.

**Manual test (required):** Non-visual — `tsc --noEmit` passes with both `bds-date-picker.tsx` and existing consumers of `DayCell` unaffected in single-date mode.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add range value contract and day-state types"`

---

### Task 17: `bds-calendar-grid` range day-state rendering

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify)

**Acceptance criteria:**

- Renders `isInRange`/`isRangeStart`/`isRangeEnd` as CSS class modifiers on the same `<td role="gridcell">` used today — no new DOM elements, no new ARIA roles.
- `bds-calendar-grid` remains a dumb, controlled component: it does not compute range membership itself, only renders whatever `DayCell` flags the parent orchestrator sets.
- Existing single-date/disabled/today rendering is unaffected when every range flag is `false` (regression guard).

**Manual test (required):** `pnpm dev:components` — Scenario: manually set `isInRange`/`isRangeStart`/`isRangeEnd` on a grid's mock data via the playground and confirm the three visual states render distinctly.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17138 render range day-states"`

---

### Task 18: `bds-date-picker` dual-calendar orchestration

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `types/types.ts` (modify), `bds-date-picker.tsx` (modify), `helpers/renderCalendarPanel.tsx` (modify)

**Acceptance criteria:**

- `@Prop() readonly range: boolean = false`.
- When `range=true`, `renderCalendarPanel.tsx` renders two `bds-calendar-grid` instances side by side (per the spike's confirmed `Expanded` structural match), each independently controlled (own `displayMonth`/`displayYear`) but computing `isInRange`/`isRangeStart`/`isRangeEnd` from one shared `draft.rangeStart`/`draft.rangeEnd`.
- Selection logic: first click sets `rangeStart` (clears any prior `rangeEnd`); a click after that sets `rangeEnd` if the clicked date is after `rangeStart`, otherwise swaps (clicked date becomes the new `rangeStart`) — reuses `date-engine`'s `compareDates`.
- Popover header shows the Start/End labeled pair (per the spike's new backlog item, "popover header Start/End prefix") instead of the single date/time string used in single-date mode — exact presentation (one line vs. two) decided here, not deferred further.
- `value`/`bdsChange`/`valueChange` on Apply emit `{ start, end }` when `range=true`, the plain string when `range=false` — verified non-breaking for existing single-date consumers.
- Clean/Cancel behave identically to single-date mode but operate on both `rangeStart`/`rangeEnd`.

**Manual test (required):** `pnpm dev:components` — Scenario 1: click two dates, confirm range highlighting across both calendars and correct header labels. Scenario 2: click a date before the current `rangeStart`, confirm the swap behavior. Scenario 3: Apply, confirm emitted `{ start, end }` value shape.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add range prop and dual-calendar orchestration"`

---

### Task 19: Phase 4 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify), `bds-calendar-grid.scss` (modify), JSDoc in both `.tsx` files

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: dual-calendar layout spacing — per spike's Phase 4 pixel specs (unconfirmed — re-pull before use): Header 48px/16px icon/24px h-padding/16px v-padding; Calendar body 12px h-padding/24px v-padding; Footer 48px/24px h-padding/16px v-padding
- [ ] Modifier: day-in-range — default and hover
- [ ] Modifier: day-range-start / day-range-end — default, hover, and combined with `today`
- [ ] Combination: range-start/end + disabled (Phase 3 min/max interplay)
- [ ] Dimensions: two calendars' shared width/alignment

**Acceptance criteria:** Every row checked off before SCSS; `$boreal-*` tokens exclusively; every state × modifier combination enumerated has an explicit rule or a documented "no visual difference" note.

**Manual test (required):** Reuse Task 18's scenarios visually against the pulled Figma values.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style range mode and finalize Phase 4 JSDoc"`

---

### Task 20: Phase 4 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.range.spec.ts` (create), `bds-calendar-grid.variants.spec.ts` (modify)

**Unit tests to cover:** range-value union type at the public API boundary (both shapes accepted/emitted correctly); start/end selection and swap logic; dual-calendar independent month navigation; range day-state rendering (`isInRange`/`isRangeStart`/`isRangeEnd`) in isolation from single-date rendering; Clean/Cancel on range draft; Apply emitting the correct `{ start, end }` shape. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 4 range mode unit tests"`

---

### Task 21: Phase 4 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the `range` prop, the `{ start, end }` value contract, and the header Start/End presentation decided in Task 18; new `range` story variant.

**Manual test (required):** `pnpm dev:docs` — new story renders and behaves correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 4 range mode"`

---

### Task 22: React/Vue wrapper parity check — Phase 4

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms `range` behavior (dual-calendar selection, `{ start, end }` value emission) identically through both wrappers.

**Manual test (required):** Repeat Task 18's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 5 — Dual time selection (start/end)

Per the spike doc: "Inicio: 08:00" / "Fin: 10:30" dual selector pairs, visually identical to Phase 2's single selector repeated twice. `renderTimeSelector.tsx` is designed here to accept a label/position parameter, directly reusable rather than needing new component logic.

### Task 23: `bds-date-picker` dual time selector

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderTimeSelector.tsx` (modify), `bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- `renderTimeSelector.tsx` accepts a `label`/`position: 'single' | 'start' | 'end'` parameter; single-date Phase 2 usage is a regression-free special case of the same helper (`position: 'single'`).
- When `range && withTime`, renders two labeled time-selector pairs ("Inicio"/"Fin" per the confirmed Figma reference, or the translatable-labels equivalent via the existing `labels` override mechanism).
- Combines with `combineDateTimeToUTC`/`extractDateTimeFromUTC` (Task 1) for both `rangeStart`+time and `rangeEnd`+time independently.
- Value contract when `range && withTime`: `{ start, end }` where both are full UTC ISO strings.
- Legacy prop reference `resetTime`/`showTimeInRange` noted in the spike doc are evaluated for relevance and either adopted (documented rationale) or explicitly deferred — not silently ignored.
- `format` auto-switch (per Task 3's confirmed decision) extends to range mode: when `range && withTime` and `format` is unset, the header Start/End display uses the time-inclusive default for each date independently — same "explicit `format` always wins" rule as Task 3, no new decision needed here.
- Default time (per Task 3's confirmed decision) extends to range mode: a fresh `rangeStart`/`rangeEnd` with no time to pre-populate defaults to `00:00` independently for each end, same malformed-value fallback rule as Task 3 — no new decision needed here.

**Manual test (required):** `pnpm dev:components` — Scenario 1: range + time enabled, select start day+time and end day+time, Apply, confirm both UTC values. Scenario 2: confirm `renderTimeSelector.tsx`'s single-date Phase 2 usage still works unchanged. Scenario 3: range + time enabled without setting `format`, confirm both Start/End header values display `HH:mm`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add dual time selector for range mode"`

---

### Task 24: Phase 5 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: dual time-selector layout (side-by-side Inicio/Fin pairs) — spacing against the confirmed single-selector dimensions (v1 spike: 58px fields, timer icon)
- [ ] Interaction: dual pair — confirm no new interaction states beyond the single selector's already-pulled default

**Acceptance criteria:** Every row checked off before SCSS; `$boreal-*` tokens exclusively; JSDoc complete.

**Manual test (required):** Reuse Task 23's scenarios visually.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style dual time selector"`

---

### Task 25: Phase 5 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.time.spec.ts` (modify)

**Unit tests to cover:** dual time selector independent start/end hour/minute state; UTC computation for both ends; single-date Phase 2 regression (position `'single'` unaffected); Cancel discarding both time drafts. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suite passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 5 dual time selector unit tests"`

---

### Task 26: Phase 5 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the dual time selector and its combined `{ start, end }` UTC value contract; new story variant (`range` + `withTime`).

**Manual test (required):** `pnpm dev:docs` — new story renders and behaves correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 5 dual time selector"`

---

### Task 27: React/Vue wrapper parity check — Phase 5

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms dual time-selector behavior identically through both wrappers.

**Manual test (required):** Repeat Task 23's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 6 — Presets sidebar

Per the spike doc: fixed list — Today/Yesterday/Last 7 days/Last 30 days/This month/Last month/Custom — visible only when `range` is on (per the corrected 2026-08-14 finding that the sidebar is gated by `Range`, not by `Calendar Type`).

### Task 28: presets configurability — design/API decision (blocking gate)

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Decide, and document, whether the preset list is a fixed built-in set or consumer-configurable — the legacy `ranges` prop (per the spike doc) suggests configurability was a solved problem elsewhere; this must be a deliberate decision, not a silent carry-over or a silent omission.
- If configurable, confirm the shape of the `presets` prop (array of `{ label, compute: () => { start: Date; end: Date } }` or similar) before Task 30 begins.

**Manual test:** N/A — design/API checkpoint.

---

### Task 29: `date-engine`-adjacent preset computation

**Executor:** @frontend-subagent
**Files:** `.../bds-date-picker/utils/presets.ts` (create), `.../utils/__test__/presets.spec.ts` (create, or covered by Task 32 if consolidating)

**Utility discovery note:** confirmed no existing "preset date range" utility anywhere in `src/`; this is single-use to `bds-date-picker`, so it lives in the component's own `utils/`, not `date-engine` (per the spike doc's decomposition litmus test — this fails the reuse test, it's not shared across other orchestrators).

**Acceptance criteria:**

- Computes the six built-in preset ranges (today, yesterday, last 7 days, last 30 days, this month, last month) as `{ start: Date; end: Date }` pairs, using `date-engine`'s existing date-math primitives (no new `date-engine` primitives needed).
- "Custom" is not a computed preset — it's the free-form manual-selection mode, selected by default whenever the user picks dates manually rather than clicking a preset button.

**Manual test (required):** Non-visual — validate via unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add built-in preset range computation"`

---

### Task 30: `bds-date-picker` presets sidebar implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderPresets.tsx` (create), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Sidebar renders only when `range=true`, per the spike's confirmed Figma gating.
- Clicking a preset sets `draft.rangeStart`/`draft.rangeEnd` from Task 29's computation and visually marks that preset selected (solid-blue per the spike's Style-page reference); clicking a day manually afterward reverts to "Custom" (deselects the preset).
- If Task 28 decided on consumer-configurable presets, a `presets` prop overrides or extends the built-in six; otherwise the six are fixed.
- Preset button states (Default/Hover/Focus/Active/Disabled, per the spike's `_DatePickerRange` node reference) are real interactive elements matching the day-cell's own established real-button precedent (v1's Hover-state finding).

**Manual test (required):** `pnpm dev:components` — Scenario 1: click each preset, confirm the correct range is selected and highlighted. Scenario 2: click a preset then manually click a day, confirm the preset deselects. Scenario 3 (if configurable): pass a custom `presets` list, confirm it renders instead of/alongside the built-ins per Task 28's decision.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add presets sidebar"`

---

### Task 31: Phase 6 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: `_DatePickerRange` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, frame node `14:23420`) — pull `get_design_context` for exact tokens/spacing, deliberately deferred until now per the spike doc
- [ ] Interaction: preset button — Default/Hover/Focus/Active/Disabled × Selected/Unselected (10 variants total)
- [ ] Dimensions: sidebar width and alignment against the dual-calendar layout from Phase 4's Task 19

**Acceptance criteria:** Every row checked off before SCSS; `$boreal-*` tokens exclusively; every state × selected combination has an explicit rule.

**Manual test (required):** Reuse Task 30's scenarios visually against the pulled Figma values.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style presets sidebar"`

---

### Task 32: Phase 6 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.presets.spec.ts` (create), `presets.spec.ts` (create)

**Unit tests to cover:** each built-in preset computes the expected `{ start, end }` pair for a fixed reference date; clicking a preset updates draft and marks it selected; manual day click after a preset selection reverts to Custom; consumer-configurable `presets` override behavior if Task 28 chose that path. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 6 presets sidebar unit tests"`

---

### Task 33: Phase 6 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the presets sidebar, the built-in list, and the configurability decision from Task 28; new story variant.

**Manual test (required):** `pnpm dev:docs` — new story renders and behaves correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 6 presets sidebar"`

---

### Task 34: React/Vue wrapper parity check — Phase 6

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms presets-sidebar behavior identically through both wrappers.

**Manual test (required):** Repeat Task 30's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 7 — Info banner + footer range summary

Per the spike doc: an info banner (blue background, info icon, title "Info", message, closable) inside the popover above the calendar; a footer range-summary text ("Range: 18 days, 2 hours, 30 minutes") to the left of Clean/Cancel/Apply.

### Task 35: `bds-date-picker` banner + range summary implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderBanner.tsx` (create), `helpers/renderFooter.tsx` (modify), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- `@Prop() readonly banner?: { title: string; message: string; closable?: boolean; state?: string; visible?: boolean }` — shape adapted from the spike's cited legacy `infoBanner` prop (prop name changed to match Boreal conventions, shape kept as reasonable prior art).
- Banner renders above the calendar body inside the popover when `visible` (or when the prop is present, per whichever default Task 35's implementer confirms against the shape above); closable via an `X` button when `closable`.
- Footer range-summary text renders only in `range` mode, to the left of the footer buttons, computed from `draft.rangeStart`/`draft.rangeEnd` (days/hours/minutes granularity per the spike's example, using `date-engine` date-math — no new primitives expected).

**Manual test (required):** `pnpm dev:components` — Scenario 1: set a `banner` prop, confirm it renders and is closable. Scenario 2: select a range, confirm the footer summary text updates live and matches the selected span.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add info banner and footer range summary"`

---

### Task 36: Phase 7 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: info banner — default, and its closable-hover state
- [ ] Modifier: banner `state` variants (info/warning/error, if the design supports more than one — confirm before assuming info-only)
- [ ] Region: footer range-summary label — spacing against the existing Clean/Cancel/Apply buttons (confirmed 48px footer height, 24px/16px padding from Phase 4's Task 19)

**Acceptance criteria:** Every row checked off before SCSS; `$boreal-*` tokens exclusively.

**Manual test (required):** Reuse Task 35's scenarios visually.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 style info banner and range summary"`

---

### Task 37: Phase 7 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.banner.spec.ts` (create)

**Unit tests to cover:** banner renders/hides per `visible`; close button removes/hides the banner and does not affect draft state; footer range-summary text computes the correct days/hours/minutes span and updates live as the range changes. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suite passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 7 banner and range summary unit tests"`

---

### Task 38: Phase 7 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the `banner` prop shape and the footer range-summary behavior; new story variant.

**Manual test (required):** `pnpm dev:docs` — new story renders and behaves correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 7 banner and range summary"`

---

### Task 39: React/Vue wrapper parity check — Phase 7

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms banner/range-summary behavior identically through both wrappers.

**Manual test (required):** Repeat Task 35's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 8 — Keyboard navigation, accessibility, RTL

Per the spike doc: only calendar-specific arrow-key 2D grid traversal is deferred to this phase — baseline keyboard operability already ships via `bds-popover`. `src/utils/a11y/keyboard/navigation/grid-navigation.ts` already exists and is generic; `bds-calendar-grid`'s native `<table role="grid">` markup was chosen specifically to make this phase additive.

### Task 40: `bds-calendar-grid` arrow-key 2D grid traversal

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify)

**Utility discovery note:** `src/utils/a11y/keyboard/navigation/grid-navigation.ts` is the confirmed integration point (flagged by a code comment left in v1's Task 9) — this task wires it, it does not reimplement grid-traversal logic.

**Acceptance criteria:**

- Arrow keys move focus cell-to-cell within the visible grid (including across week rows); Home/End jump to the first/last day of the visible week or month per the WAI-ARIA APG reference; PageUp/PageDown (or the APG's specified equivalent) navigate months.
- Focus crossing a month boundary via arrow keys triggers the same `bdsMonthNavigate` event already used for the prev/next buttons — no duplicate navigation code path.
- Out-of-month and disabled cells remain excluded from arrow-key focus stops per the interactivity contract already established in v1/Phase 3.
- Works correctly for both single and dual (range-mode) grid instances independently.

**Manual test (required):** `pnpm dev:components` — Scenario: tab into the grid, use arrow keys to traverse across a full month boundary in both directions, confirm focus and `bdsMonthNavigate` firing correctly; repeat in range mode across both calendars independently.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17138 add arrow-key 2D grid traversal"`

---

### Task 41: live region + RTL audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderCalendarPanel.tsx` (modify), `bds-calendar-grid.scss` (modify), `bds-date-picker.scss` (modify)

**Acceptance criteria:**

- An `aria-live` region (visually hidden) announces the current month/year on navigation, per the WAI-ARIA APG reference and react-day-picker's cited pattern.
- RTL audit across `bds-calendar-grid` and `bds-date-picker`: logical CSS properties (`margin-inline-start`/`inset-inline-*`, etc.) replace any remaining physical-direction properties; nav-icon mirroring confirmed for RTL locales; sidebar (Phase 6)/footer (all phases) layout confirmed to flip correctly.
- No visual regression in LTR mode.

**Manual test (required):** `pnpm dev:components` — Scenario 1: navigate months with a screen reader active (or inspect the live region's DOM update), confirm announcement. Scenario 2: force `dir="rtl"` on the playground host, confirm calendar, sidebar, footer, and nav icons all mirror correctly.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17138 add live region announcements and RTL support"`

---

### Task 42: Phase 8 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.keyboard.spec.ts` (create), `bds-calendar-grid.a11y.spec.ts` (modify), `bds-date-picker.keyboard.spec.ts` (modify)

**Unit tests to cover:** arrow-key traversal in every direction including month-boundary crossing; Home/End/PageUp/PageDown per the confirmed keymap; disabled/out-of-month cells excluded from focus stops; live-region text updates on navigation; dual-grid (range mode) independent traversal. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 8 keyboard navigation and a11y unit tests"`

---

### Task 43: Phase 8 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents the full keyboard interaction model (arrow keys, Home/End, month/year hotkeys) and RTL support.

**Manual test (required):** `pnpm dev:docs` — MDX reviewed for clarity and accuracy against the shipped behavior.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 8 keyboard navigation and RTL support"`

---

### Task 44: React/Vue wrapper parity check — Phase 8

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms keyboard traversal and RTL rendering identically through both wrappers.

**Manual test (required):** Repeat Tasks 40/41's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Phase 9 — Month/year quick-picker

Per the spike doc's "Unscheduled — month/year quick-picker" section: clicking the month/year header label opens an inline month-grid or year-grid replacing the day grid, letting the user jump directly to a target month/year. Confirmed present in Figma (`datePickerMonths`/`datePickerYears`/`_DatePickerMonthYear` nodes) but never UX/UI-validated for its drill-down interaction model — this phase starts with that validation.

This lives inside `bds-calendar-grid` itself (not a new registered element), per the spike doc's decomposition litmus test: it's a mode of the same reusable, dumb, controlled grid component shared by every orchestrator, not a consumer-composed or single-use piece.

### Task 45: quick-picker interaction model — UX confirmation (blocking gate)

**Executor:** main thread (no executor)

**Acceptance criteria:**

- Confirm or correct the spike doc's inferred three-level drill-down model with the user before Task 47 begins: click the month/year label → month grid (12 months, middle button = year, prev/next steps by year) → click a month → back to day grid for that month; click the middle year button while in the month grid → year grid (12-year range, prev/next steps by decade) → click a year → back to the month grid for that year.
- In particular, confirm step 4 (clicking a year returns to the month grid, not directly to a day) — the spike doc flags this as inferred from the universal pattern, not directly observed in a Figma prototype.
- Document the confirmed model as a short addendum before Task 47 starts.

**Manual test:** N/A — design/UX checkpoint.

---

### Task 46: `date-engine` month-grid/year-grid generators

**Executor:** @frontend-subagent
**Files:** `packages/boreal-web-components/src/services/date-engine/grid.ts` (modify), `.../date-engine/types.ts` (modify), `.../date-engine/__test__/grid.spec.ts` (modify)

**Acceptance criteria:**

- `generateMonthPickerGrid(year: number, currentMonth: number): MonthGridCell[]` — 12 cells (Jan–Dec), each flagging whether it's the currently-displayed month (dashed-outline indicator per Figma).
- `generateYearPickerGrid(centerYear: number, currentYear: number): YearGridCell[]` — a 12-year range, each flagging whether it's the current year and whether it's disabled (future years greyed/disabled per the spike's Figma note — confirm against Task 45's confirmed model whether this applies to Boreal's use case or was an artifact of the source mockup).
- Both are pure functions, framework-agnostic, following `generateMonthGrid`'s existing testing/typing conventions exactly.

**Manual test (required):** Non-visual — validate via unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(date-engine): EOA-17138 add month-picker and year-picker grid generators"`

---

### Task 47: `bds-calendar-grid` quick-picker drill-down implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid/types/ICalendarGrid.ts` (modify), `bds-calendar-grid.tsx` (modify)

**Acceptance criteria:**

- Internal `@State() private view: 'days' | 'months' | 'years' = 'days'` — not exposed as a public `@Prop`, matching `bds-calendar-grid`'s existing "dumb but internally stateful for rendering" pattern (it already owns `hover`/`focus` interaction state internally; this is the same class of concern).
- The month/year header label becomes a real interactive button (per the spike's confirmed `_Button/month-year` finding, already noted as a dropdown-styled button rather than plain text since v1) — clicking it switches `view` to `'months'`.
- Month-grid cell click resolves back to `view: 'days'`, updating `displayMonth` and emitting `bdsMonthNavigate` upward (reusing the existing event, not a new one) so the orchestrator's `@State` stays in sync.
- Year-grid cell click resolves to `view: 'months'` for the clicked year, per Task 45's confirmed model (not directly to `'days'`).
- Middle year-button inside the month grid switches `view` to `'years'`.
- Works correctly for both single and dual (range-mode) grid instances independently — each grid instance manages its own `view` state.

**Manual test (required):** `pnpm dev:components` — Scenario 1: click the month/year label, confirm the month grid replaces the day grid. Scenario 2: click a month, confirm it resolves back to the day grid showing that month. Scenario 3: from the month grid, click the year button, confirm the year grid appears; click a year, confirm it resolves to the month grid for that year (per Task 45's confirmed model).

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17138 add month/year quick-picker drill-down"`

---

### Task 48: Phase 9 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.scss` (modify), `bds-calendar-grid.tsx` (JSDoc)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: `datePickerMonths` grid (node `14:24131`) — cell layout, spacing
- [ ] Region: `datePickerYears` grid (node `14:24151`) — cell layout, spacing
- [ ] Region: `_DatePickerMonthYear` cell (node `14:23473`) — `State` (Default/Hover/Focus/Active/Disabled) × `State Actual` (True/False, presumed "is current") × `Selected` (True/False) — none of these three nodes pulled yet per the spike doc; pull all now
- [ ] Region: month/year header label button — the confirmed `_Button/month-year` state matrix (~10 rows: Default/Hover/Focus/Active/Disabled × unselected/selected)

**Acceptance criteria:** Every row checked off before SCSS, with pulled values recorded; `$boreal-*` tokens exclusively; JSDoc for the new internal `view` state complete.

**Manual test (required):** Reuse Task 47's scenarios visually against the pulled Figma values.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17138 style month/year quick-picker"`

---

### Task 49: Phase 9 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.quickpicker.spec.ts` (create), `date-engine/__test__/grid.spec.ts` (modify)

**Unit tests to cover:** `generateMonthPickerGrid`/`generateYearPickerGrid` correctness (12 cells/range, current-item flagging); header-label click switches `view`; month-cell click resolves to `'days'` and updates `displayMonth`/emits `bdsMonthNavigate`; year-cell click resolves to `'months'` for the clicked year (per Task 45's confirmed model); independent `view` state across dual grid instances in range mode. Coverage-phase only (≥90%).

**Manual test (required):** Non-visual — suites passing at ≥90% coverage.

**Commit:** `git commit -m "test: EOA-17138 add Phase 9 month/year quick-picker unit tests"`

---

### Task 50: Phase 9 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify) — internal-only note, per `bds-calendar-grid`'s existing no-standalone-docs convention

**Acceptance criteria:** MDX's internal `bds-calendar-grid` note is extended to describe the quick-picker drill-down behavior at a level consumers of `bds-date-picker` need to understand (it's automatic, no new public props), consistent with the existing internal-documentation-only convention for `bds-calendar-grid`.

**Manual test (required):** `pnpm dev:docs` — MDX reviewed for clarity.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17138 document Phase 9 month/year quick-picker"`

---

### Task 51: React/Vue wrapper parity check — Phase 9

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms quick-picker drill-down behavior identically through both wrappers.

**Manual test (required):** Repeat Task 47's scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Final task — Consolidated mutation testing (Stryker) across all of v2

### Task 52: Consolidated mutation testing — Phases 2–9

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs` (modify — re-run, now covering `value.ts`, min/max wiring, and the Phase 9 grid generators)
- `.../bds-date-picker/stryker.bds-date-picker.config.mjs` (modify — re-run, now covering every Phase 2–8 addition)
- `.../bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` (modify — re-run; first time since v1 this config needs re-running, now covering Phase 4 range rendering, Phase 8 keyboard traversal, and Phase 9 quick-picker)

**Acceptance criteria:**

- This is the single point in the entire v2 scope where mutation testing runs — not per phase, not per task.
- Target: ≥90% mutation score per component. Any surviving mutant below threshold gets either a new test closing the gap (in the relevant phase's existing spec file) or a documented, justified exception.
- Any mutant survivor pattern revealing a genuine test-coverage gap from any earlier phase is fixed by extending that phase's existing spec file — do not add new source files at this stage.

**Manual test (required):** Non-visual — run all three Stryker configs locally, confirm ≥90% mutation score (or documented exceptions) for each.

**Commit:** `git commit -m "test: EOA-17138 run consolidated mutation testing across all v2 phases (2-9)"`

---

## Remaining Open Questions (resolve at the task checkpoint noted, not before starting)

- **Phase 3 (Task 9):** disabled-date interaction design — no Figma mockup exists beyond the generic "Day disabled" token; must be resolved via the design check-in before Task 11.
- **Phase 4 (Task 18):** exact popover header Start/End prefix presentation (one line vs. two; whether `headerPlaceholder` needs a start/end pair of its own) — the spike doc flags this as deliberately deferred to whoever picks up this phase; resolve it in Task 18, not before.
- **Phase 4:** the spike doc notes an as-yet-unexplored Figma combination — `Basic` `Calendar Type` with `Range: true` and a single calendar (not the dual `Expanded` layout) — confirm during Task 18 whether Boreal's range mode should support this single-calendar range variant, or whether dual-calendar (`Expanded`) is the only supported range presentation for v2.
- **Phase 6 (Task 28):** fixed vs. consumer-configurable presets — the legacy `ranges` prop suggests configurability was solved elsewhere; must be a deliberate decision, not a silent carry-over.
- **Phase 9 (Task 45):** the quick-picker's drill-down interaction model is inferred from the universal MUI X/Ant Design/react-day-picker/Vaadin pattern, not directly observed in a Figma prototype — especially step 4 (year click → month grid, not day grid). Confirm with the user before Task 47.
- **Explicitly not a question for this plan:** keyboard-typed date entry in the trigger field remains deferred per the 2026-08-19 decision in the spike doc — do not resolve or reopen it as a side effect of any task above.
