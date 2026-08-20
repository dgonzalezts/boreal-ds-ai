---
ticket: EOA-17138
component: bds-date-picker
status: pending
created: 2026-08-19
---

# bds-date-picker v2 (ADR-0003 Phase 2 — Time Selector) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

> **This plan is `pending` — not started.** It was split out of [`EOA-16692-bds-date-picker-v1.md`](./EOA-16692-bds-date-picker-v1.md) on 2026-08-19, where it existed as Tasks 23–30 ("Phase 2 — Time selector"), because sprint time constraints required v1 to close out on Phase 0–1 (single-date picker) alone this sprint. Nothing here had been implemented at the time of the split — no code, no tests, no commits — so every task below is exactly as originally planned in v1, just renumbered, with a `(was Task N)` breadcrumb on each heading for traceability. Do not begin work here until v1 (Tasks 1–23) is fully done and this sprint's follow-up confirms Phase 2 is back in scope.

**Goal:** Extend `bds-date-picker` (already shipped in v1 as a single-date picker) with an optional time selector — `showTime` prop, hour/minute selection, and a UTC-normalized `value` contract when time is enabled — without breaking v1's naive-date `value` contract when it isn't.

**Jira ticket:** [EOA-17138 "Implement Date Picker v2"](https://telesign.atlassian.net/browse/EOA-17138) — its own dedicated story, linked "relates to" [EOA-16692](https://telesign.atlassian.net/browse/EOA-16692) (v1's ticket). Not a subtask of EOA-16692 — a sibling story under the same parent Feature (EOA-14927).
**Ticket brief:** [`ai-work/tickets/EOA-16692-bds-date-picker.md`](../tickets/EOA-16692-bds-date-picker.md) — shared with v1; this file's own Jira story (EOA-17138) mirrors the "In v2" section of that brief.
**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md) — see in particular the `_Basic Time picker` subsection (real, tool-verified Figma structure for the hour/minute fields) and the "Collapsed/single-date variant Figma node" finding.
**v1 plan (Phase 0–1, prerequisite):** [`EOA-16692-bds-date-picker-v1.md`](./EOA-16692-bds-date-picker-v1.md) — read its "Remaining Open Questions" section for background on decisions already resolved during Phase 0–1 that inform this file (footer button set/order, the day-cell state model, etc.).

**Versioning:** This is v2, scoped to Phase 2 (time selector) only. Further phases (Phase 3 min/max, Phase 4 range, etc.) get their own `ai-work/plans/EOA-16692-bds-date-picker-vN.md` files, linked from the spike doc — matching `bds-table`'s exact precedent (`EOA-10576-bds-table-v1.md` → `EOA-14935-bds-table-v2.md` → `EOA-15507-bds-table-v3.md`). Do not expand this file to cover Phase 3+.

**Architecture:** Unchanged from v1 — `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + `bds-calendar-grid` body, FACE-compliant, draft-state-until-Apply) gets a `showTime` prop that additively composes a new `renderTimeSelector.tsx` helper alongside the existing calendar panel and footer. No new registered custom element — the time selector is two `bds-select` instances (hour/minute), matching the confirmed Figma structure.

**Tech Stack:** Stencil, TypeScript, `date-fns@^4.4.0` + `@date-fns/tz@^1.5.0` (already added in v1's Task 1), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`).

---

## Testing and QA policy for this plan

**Two-phase test gate, coverage consolidated at the end of the phase, mutation testing consolidated at the very end** — same convention as v1. Coverage-phase Jest tests (≥90% coverage) are written in one consolidated unit-test task (Task 5) at the end of this phase, not embedded inline in each implementation task — implementation tasks (1, 3, 4) carry acceptance criteria and manual tests only. Mutation-phase (Stryker, ≥90% score) is deferred to Task 8, the last task in this file — it re-runs/extends the three Stryker configs v1's Task 23 already created, now covering the Phase 2 files added here. Do not attempt the mutation-phase gate until Task 8.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output**, not every task — Tasks 3 and 4 render or restyle something a human needs to look at. Task 1 (pure logic) and Task 5 (tests only) keep a single executor. Task 2 is a design checkpoint, not a code task, and has no executor at all.

**React/Vue wrapper parity is consolidated, not per-task** — Task 7, the second-to-last task in this file, extending v1's Task 22 Phase 1 check rather than duplicating it.

---

## Files to create / modify

| File                                                                                                                          | Notes                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| `packages/boreal-web-components/src/services/date-engine/value.ts`                                                            | New — `combineDateTimeToUTC`, `extractDateTimeFromUTC` via `@date-fns/tz`            |
| `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts`                                              | New — plain Jest                                                                    |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx`         | New                                                                                  |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/types.ts`                         | Modify — extend `DatePickerDraftState` with `hour`/`minute`                          |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`                    | Modify — `showTime` prop, time-selector wiring, UTC `value` computation on Apply    |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.scss`                   | Modify — time-selector styling                                                       |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts`  | New                                                                                  |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts`  | Modify — extend for hour/minute selects                                              |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` | Modify — regression check only                                                    |
| `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs`                                     | Modify (Task 8) — re-run to cover `value.ts`                                         |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/stryker.bds-date-picker.config.mjs`     | Modify (Task 8) — re-run to cover the time selector                                  |
| `packages/boreal-web-components/src/index.html`                                                                               | Modify — playground scenarios per task (never committed, per project memory)         |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts`                                                | Modify — add a `showTime` variant story                                              |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx`                                                       | Modify — Phase 2 value contract, `timezone` behavior                                |

**Critical reference files** (read before implementing):

- `EOA-16692-bds-date-picker-v1.md` — the finished Phase 0–1 implementation this plan extends; read `bds-date-picker.tsx`'s current state (draft/Apply lifecycle, `formatValueForDisplay`, `resetDraft`) before adding time fields to it.
- `ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md` — `_Basic Time picker` subsection for the confirmed hour/minute field structure.
- `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx` — the component the hour/minute fields compose.
- `ai-work/plans/EOA-16000-bds-table-v4.md` — precedent for the consolidated mutation-testing task pattern this plan adapts.

---

## Phase 2 — Time selector

### Task 1 (was Task 23): `date-engine` timezone-aware value conversion

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/value.ts` (create)
- `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts` (create)

**Acceptance criteria:**

- Confirm the date-fns major pinned in v1's Task 1 is v4+ (required for `@date-fns/tz`) before starting.
- Exports `combineDateTimeToUTC(datePart: Date, hour: number, minute: number, timezone: string): string` — interprets the given wall-clock date+time _as if in_ `timezone`, returns the UTC ISO 8601 string (`...Z` suffix), via `@date-fns/tz`'s `TZDate`.
- Exports `extractDateTimeFromUTC(isoUtc: string, timezone: string): { date: Date; hour: number; minute: number }` — the reverse, for populating draft state from an existing datetime `value`.
- Handles DST transitions correctly (a wall-clock time ambiguous or nonexistent during a DST fold/gap must not silently produce a wrong-by-one-hour UTC value).
- Utility discovery note: confirmed no existing timezone utility anywhere in `packages/boreal-web-components/src/`. New module justified; document the library choice (`@date-fns/tz`, version) in this file's header comment.

**Note:** Unit tests for this task's behavior (zone conversion correctness, DST handling, round-trip, invalid-timezone handling) are covered in the consolidated Task 5 (Phase 2 unit tests), not written here.

**Manual test (required):**
Non-visual task — no automated test suite exists yet for this module (deferred to Task 5). Validate via `pnpm --filter boreal-web-components exec tsc --noEmit` passing, plus a quick manual REPL/console check of `combineDateTimeToUTC`/`extractDateTimeFromUTC` against at least one positive-offset zone (e.g. `Asia/Tokyo`) and one negative-offset zone with a DST boundary (e.g. `America/Los_Angeles`), confirming the computed UTC strings by hand.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add timezone-aware date-time to UTC ISO conversion"
```

---

### Task 2 (was Task 24): `bds-date-picker` time selector — design check-in (blocking gate)

**Executor:** main thread (no executor) — not an implementation task

**Acceptance criteria:**

- Before Task 3 begins, present the inferred single-date time-selector UI (hour:minute dropdown pair) to the user for confirmation or correction, since the provided docs only show the dual Inicio/Fin range variant.
- Document the confirmed design as a short addendum to this plan before proceeding.

**Manual test:** N/A — design confirmation checkpoint, not a code task.

---

### Task 3 (was Task 25): `bds-date-picker` time selector implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/types.ts` (modify — extend `DatePickerDraftState` with `hour`/`minute`)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Adds `@Prop() readonly showTime: boolean = false` (or the name confirmed at Task 2) gating whether the time selector renders inside the popover body alongside the calendar.
- Time selector composes two `bds-select` instances (hour 00-23, minute 00-59, per the confirmed design) inside `renderTimeSelector.tsx` — not a new registered custom element.
- Time changes update `this.draft.hour`/`this.draft.minute` only — same draft-until-Apply contract as day selection.
- When `showTime` is `false` (Phase 1 behavior), the value contract remains the naive `yyyy-MM-dd` string, untouched — proves Phase 2 is additive, not breaking.
- When `showTime` is `true`, Apply computes the final UTC ISO string via `combineDateTimeToUTC`, using `this.timezone` and the draft's date+hour+minute.
- Loading an existing `showTime=true` datetime `value` on init correctly pre-populates the draft's date, hour, and minute via `extractDateTimeFromUTC`.

**Note:** Unit tests for this task's behavior (Phase 1 value-contract regression, UTC computation on Apply, `timezone` override, pre-population on load, Cancel discarding time draft) are covered in the consolidated Task 5 (Phase 2 unit tests), not written here.

**Manual test (required):**

- Scenario 1: `show-time` enabled, no initial value; pick a day, set hour/minute, Apply; confirm the emitted `value` is a full UTC ISO string.
- Scenario 2: two instances side by side with different `timezone` props but the same manual date/time selection; confirm their emitted UTC values differ by the expected offset.
- Scenario 3: instance pre-loaded with an existing UTC datetime `value`; open the popover; confirm day/hour/minute are all correctly pre-selected.

Run: `pnpm dev:components` and validate:

- [ ] Given a day+time selection and Apply, when the emitted value is inspected, then it is a full UTC ISO string reflecting the correct offset for the configured timezone. Pass: logged value matches expected UTC computation.
- [ ] Given two instances with different timezones and identical wall-clock selections, when both are applied, then their emitted UTC values differ by the correct offset delta. Pass: values differ as expected.
- [ ] Given a pre-loaded datetime value, when the popover opens, then day/hour/minute are all correctly pre-populated. Pass: visible pre-selection matches the source value.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add single time selector for Phase 2"
```

---

### Task 4 (was Task 26): `bds-date-picker` Phase 2 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.scss` (modify)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify — JSDoc for new `showTime`/time-related props)

**Process note:** same Figma-first requirement as v1's Task 19 — that task was reopened twice for pulling states reactively instead of up front; don't repeat that here. The time selector's base field structure was decoded during v1's spike session (`_Basic Time picker`: timer icon + two bordered 58px hour/minute fields), but its interaction states were never pulled — do not assume they match `bds-calendar-grid`'s day-cell interaction states or any other component's pattern by default.

**Figma research pass (complete before writing any SCSS):**

Pull `get_design_context` / `get_metadata` for each row below directly — a row is done only when it was actually pulled, never when it was inferred from a sibling variant or another component's pattern.

- [ ] Region: hour/minute fields — default state _(already decoded in v1's spike session: timer icon + two bordered 58px fields — confirm no further detail is missing)_
- [ ] Interaction: hour/minute fields — hover / focus / active _(not yet pulled)_
- [ ] Modifier: hour/minute fields — validation/error state, if the design has one _(not yet pulled — confirm whether it exists before assuming it doesn't)_
- [ ] Dimensions: hour/minute field width/height and spacing against the popover body's existing spacing conventions from v1's Task 19 (confirmed 296×434px panel, 24px/12px padding)

**Acceptance criteria:**

- Every row of the Figma research pass above is checked off, with the pulled value recorded, before the first SCSS line is written.
- Time selector styling uses `$boreal-*` tokens, matching the popover body's existing spacing conventions from v1's Task 19.
- Hover/focus/active states on the hour/minute selects are implemented from confirmed Figma states (per the research pass above), not assumed.
- JSDoc for `showTime` and any new props/state added in Task 3 is complete and accurate.

**Manual test (required):**
Reuse Task 3's scenarios.

Run: `pnpm dev:components` and validate:

- [ ] Given the time-enabled instance, when compared visually against the confirmed Task 2 design, then spacing and alignment match. Pass: visual match confirmed.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 style time selector and finalize Phase 2 JSDoc"
```

---

### Task 5 (was Task 27): `bds-date-picker` + `date-engine` Phase 2 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.time.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts` (extend)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` (extend)

**Acceptance criteria:**

- One consolidated task covering every behavior area introduced by Tasks 1 and 3–4 — per the Testing Phases policy, unit tests are never written inline in an implementation task.
- Extends the existing Phase 1 spec files (from v1's Task 20) for a11y/keyboard rather than creating parallel duplicate files, keeping the split-by-concern convention intact.

**Unit tests to cover** _(grouped by spec file)_:

- `value` (Task 1's behavior, plain Jest, no `newSpecPage`): combining a date+time in a positive-UTC-offset zone (e.g. `Asia/Tokyo`) produces the correctly shifted UTC ISO string; combining a date+time in a negative-UTC-offset zone (e.g. `America/Los_Angeles`) produces the correctly shifted UTC ISO string, including across that zone's DST "spring forward"/"fall back" transition dates for the relevant year; `extractDateTimeFromUTC` round-trips with `combineDateTimeToUTC` for a sample of zones/times including at least one DST-boundary case; an invalid IANA timezone string does not silently produce a wrong result — throws or falls back predictably (document and test whichever is chosen).
- `time` (Task 3's behavior): with `showTime=false`, `value` after Apply remains a naive `yyyy-MM-dd` string (regression check against Phase 1 contract); with `showTime=true`, selecting a day + hour + minute then Apply produces a correctly UTC-normalized ISO string for a non-UTC `timezone` prop; with `showTime=true` and an explicit `timezone` override, the same wall-clock selection produces a different UTC value than with the default browser timezone (proves the `timezone` prop is honored); loading a component with an existing datetime `value` and `showTime=true` correctly pre-populates hour/minute; Cancel with `showTime=true` discards time draft changes exactly like date draft changes (v1 Task 16's contract extended consistently).
- `a11y`: hour/minute `bds-select` instances are reachable via Tab and correctly labeled for screen readers (reusing `bds-select`'s own established a11y behavior — assert the integration).
- `keyboard`: `showTime` toggling doesn't break the Phase 1 keyboard flow already covered in v1's Task 20.
- Coverage-phase only (≥90%); mutation testing deferred to Task 8.

**Manual test (required):**
Non-visual (test-only) task — validate via the full `date-engine` and `bds-date-picker` test suites passing at ≥90% coverage (coverage-phase only; mutation testing deferred to Task 8).

**Commit:**

```bash
git commit -m "test: EOA-16692 add consolidated Phase 2 unit tests for date-engine value conversion and bds-date-picker time selector"
```

---

### Task 6 (was Task 28): `bds-date-picker` Phase 2 documentation

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify — add a `showTime` variant story)
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (modify)

**Acceptance criteria:**

- MDX documents the Phase 2 value contract explicitly: `value` becomes a full UTC ISO 8601 string when `showTime` is enabled, contrasted clearly against the Phase 1 naive-date contract already documented in v1's Task 21.
- MDX explicitly notes that the single time-selector UI was an inferred design (per Task 2's resolution — update this note to reflect whatever was actually confirmed).
- Documents `timezone` prop behavior with a concrete before/after example (same wall-clock input, two different `timezone` values, two different emitted UTC strings).

**Manual test (required):**
Run: `pnpm dev:docs` and validate:

- [ ] Given the new `showTime` story, when navigating to it, then hour/minute controls render and interact correctly in Storybook. Pass: interactive time selection works.
- [ ] Given the MDX value-contract section, when read, then the naive-date vs. UTC-datetime distinction is unambiguous. Pass: reviewer confirms clarity.

**Commit:**

```bash
git commit -m "docs(bds-date-picker): EOA-16692 document Phase 2 time selector and UTC value contract"
```

---

### Task 7 (was Task 29): React/Vue wrapper parity check — Phase 2

**Executor:** @qa-subagent
**Files:** none (verification-only task; no new source files)

**Acceptance criteria:**

- Confirms `showTime`/time-selector behavior (hour/minute selection, UTC-normalized `value`, `timezone` prop honoring) behaves identically through `boreal-react` and `boreal-vue`, extending v1's Task 22 Phase 1 check rather than duplicating it.
- Uses the `dev:pack:react`/`dev:pack:vue` pipeline, same rationale as v1's Task 22.
- Any regression found is logged as a new task, not patched inline here.

**Manual test (required):**

- Scenario: repeat Task 3's three scenarios (time-enabled Apply, cross-timezone comparison, pre-loaded datetime value) through both `examples/react-testapp` and `examples/vue-testapp`.

Run: `pnpm dev:pack:react` and `pnpm dev:pack:vue`, then validate:

- [ ] Given Task 3's scenarios, when repeated through the React wrapper, then behavior matches exactly, including the emitted UTC value. Pass: no divergence.
- [ ] Given the same scenarios, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A — verification-only task; no code changes expected unless a regression is found.

---

### Task 8 (new): Consolidated mutation testing (Stryker) — Phase 2 additions

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs` (modify — re-run, now covering `value.ts`)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/stryker.bds-date-picker.config.mjs` (modify — re-run, now covering the time selector)

**Acceptance criteria:**

- Unlike v1's Task 23 (a fresh, first-ever Stryker pass), this task **re-runs** the same two config files v1 already created — `bds-calendar-grid`'s config is untouched by Phase 2 and does not need re-running — now that Phase 2 added `date-engine/value.ts` and `bds-date-picker`'s time-selector code/tests to their respective components.
- Target: ≥90% mutation score per component, matching the two-phase quality gate in `testing-knowledge`. Any surviving mutant below threshold gets either a new test closing the gap or a documented, justified exception.
- Any mutant survivor pattern that reveals a real gap in Tasks 1–7's test coverage is fixed by extending the relevant existing spec file — do not add new source files at this stage.
- This is the only point in this file where mutation testing runs; do not re-run Stryker per-task retroactively.

**Manual test (required):**
Non-visual (test-only) task — validate by running the two Stryker configs locally and confirming both report ≥90% mutation score (or documented exceptions).

**Commit:**

```bash
git commit -m "test: EOA-16692 extend mutation testing for date-engine value conversion and bds-date-picker time selector"
```

---

## Remaining Open Questions (resolve at the task checkpoint noted, not before starting)

None specific to Phase 2 remain open — v1's own "Remaining Open Questions" section covered every design/architecture question raised during the whole component's spike session, and all of them were resolved before v1 closed out Task 19. Re-read that section (and the spike doc it links) for background before starting Task 1 above; nothing here needs re-litigating.
