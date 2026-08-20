---
ticket: EOA-16692
component: bds-date-picker
status: done
created: 2026-08-12
---

# bds-date-picker v1 (ADR-0003 Phases 0–1) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

> **Scope change (2026-08-19):** Phase 2 (time selector) was originally planned inside this v1 file as Tasks 23–30. Due to sprint time constraints, Phase 2 has been moved out to its own plan — [`ai-work/plans/EOA-16692-bds-date-picker-v2.md`](./EOA-16692-bds-date-picker-v2.md) (`status: pending`, not started) — so v1 can close out cleanly on Phase 0–1 (single-date picker only) this sprint. Nothing in Phase 2 had been implemented at the time of the split (Tasks 23–30 carried planning content only, no code/tests/commits), so this was a pure content relocation, not a migration. This file's own remaining scope (Tasks 20–23: Phase 1 unit tests, docs, wrapper parity, consolidated mutation testing) was unaffected by the split and is now **fully done (2026-08-20)** — see each task's status note below.

**Goal:** Ship `date-engine` (Phase 0 pure logic), `bds-calendar-grid` (Phase 0 presentational grid), and `bds-date-picker` Phase 1 (single date, no time — time selector moved to v2 per the note above), matching the architecture decisions resolved in the spike doc below, without precluding later range/min-max/presets/banner versions.

**Ticket brief:** [`ai-work/tickets/EOA-16692-bds-date-picker.md`](../tickets/EOA-16692-bds-date-picker.md)
**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md)

**Versioning:** This is v1, scoped to Phase 0–1 (single-date picker) as of the 2026-08-19 split above. Phase 2 (time selector) is tracked in [`EOA-16692-bds-date-picker-v2.md`](./EOA-16692-bds-date-picker-v2.md). Future phases beyond that (Phase 3 min/max, Phase 4 range, etc.) get their own further `ai-work/plans/<ticket>-bds-date-picker-vN.md` files, linked from the spike doc — matching `bds-table`'s exact precedent (`EOA-10576-bds-table-v1.md` → `EOA-14935-bds-table-v2.md` → `EOA-15507-bds-table-v3.md`). Do not expand this file to cover Phase 2+.

**Architecture:** Bottom-up build order — `date-engine` (pure functions, plain Jest) ships and is fully tested first; `bds-calendar-grid` (dumb, controlled, light-DOM custom element rendering a native `<table role="grid">`) consumes it and ships fully tested second; `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + `bds-calendar-grid` body, FACE-compliant, draft-state-until-Apply) consumes both as Phase 1 (date-only) in this file — see v2 for the Phase 2 (+ time) extension. No external calendar UI library; light DOM throughout, matching the rest of Boreal.

**Tech Stack:** Stencil, TypeScript, `date-fns@^4.4.0` + `@date-fns/tz@^1.5.0` (new dependencies, verified against the npm registry), `@floating-ui/dom` (already wired via `anchoredMixin`/`bds-popover`), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`).

---

## Testing and QA policy for this plan

**Two-phase test gate, coverage consolidated per component/phase block, mutation testing consolidated at the end** — mirrors `bds-table`'s `EOA-16000` precedent (its Task 15: one Stryker pass across the full surface area, not repeated per task), applied here at the scope of this single plan since there's no prior `bds-date-picker` version to combine with yet. Coverage-phase Jest tests (≥90% coverage) are written in one consolidated unit-test task at the end of each component/phase block (Task 11 for `bds-calendar-grid` a11y, Task 20 for all of Phase 1), not embedded inline in each implementation task — implementation tasks (12–19) carry acceptance criteria and manual tests only; their behaviors are tested by the block's consolidated task. Mutation-phase (Stryker, ≥90% score) is deliberately **not** run per task or per block — it's deferred to Task 23 (renumbered from the original Task 30 when Phase 2 moved to v2; see the scope-change note at the top of this file), run once after every other task in this file is complete, across all three testable units this plan creates (`date-engine`, `bds-calendar-grid`, `bds-date-picker`), each with its own Stryker config file per this project's existing convention. Do not install Stryker or attempt the mutation-phase gate until Task 23.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output**, not every task. Tasks with a chained `**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)` line (8, 9, 10, 14–19) render or restyle something a human needs to look at. Pure-logic, type-only, or config tasks (1–7, 11–13, 20–21) keep a single executor — their manual test is `tsc --noEmit` or a Jest run, which the assigned subagent already validates itself; dispatching `@qa-subagent` there would mean reviewing nothing visual.

**React/Vue wrapper parity is consolidated, not per-task** — Task 22, the last task in this file. `EOA-16000` checked parity per-task because each of its 15 tasks shipped a complete, independently-usable feature on an already-mature, already-cross-framework-shipping component. This plan's implementation tasks are sub-feature layers of a brand-new component that isn't composable or rendering anything meaningful until partway through Phase 1 — a parity check on a stub `<Host></Host>` render or a types-only task would find nothing, every time, and would repeatedly pay the `dev:pack:react`/`dev:pack:vue` pipeline cost for no benefit. One consolidated check at the end of Phase 1, once there's real cross-framework-relevant behavior to compare, is enough. Phase 2's own parity check lives in v2.

---

## Files to create / modify

| File                                                                                                                                | Notes                                                                                                                      |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-web-components/package.json`                                                                                       | Modify — add `date-fns@^4.4.0`, `@date-fns/tz@^1.5.0`                                                                      |
| `packages/boreal-web-components/src/services/date-engine/types.ts`                                                                  | New — `MonthGrid`, `DayCell`, `WeekdayLabel`, `DateEngineLocale` alias                                                     |
| `packages/boreal-web-components/src/services/date-engine/grid.ts`                                                                   | New — `generateMonthGrid`, `getWeekdayLabels`                                                                              |
| `packages/boreal-web-components/src/services/date-engine/date-math.ts`                                                              | New — `addMonths`/`subMonths`/`isSameDay`/`isSameMonth`/`isWithinRange`/`compareDates`/`toNaiveISODate`/`fromNaiveISODate` |
| `packages/boreal-web-components/src/services/date-engine/format.ts`                                                                 | New — `formatDisplayDate`, `getMonthYearLabel`                                                                             |
| `packages/boreal-web-components/src/services/date-engine/index.ts`                                                                  | New — public barrel                                                                                                        |
| `packages/boreal-web-components/src/services/date-engine/__test__/grid.spec.ts`                                                     | New — plain Jest                                                                                                           |
| `packages/boreal-web-components/src/services/date-engine/__test__/date-math.spec.ts`                                                | New — plain Jest                                                                                                           |
| `packages/boreal-web-components/src/services/date-engine/__test__/format.spec.ts`                                                   | New — plain Jest                                                                                                           |
| `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs`                                            | New (Task 23) — per-component Stryker config                                                                               |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx`                       | New — renders as `<table role="grid">`                                                                                     |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.scss`                      | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/ICalendarGrid.ts`                      | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/types.ts`                              | New — event detail types                                                                                                   |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/index.ts`                              | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.basics.spec.ts`   | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.events.spec.ts`   | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.variants.spec.ts` | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts`     | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/stryker.bds-calendar-grid.config.mjs`        | New (Task 23) — per-component Stryker config                                                                               |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`                           | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.scss`                          | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx`               | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderFooter.tsx`                      | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/draft-state.ts`                          | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/value-mapping.ts`                        | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/index.ts`                                | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/IDatePicker.ts`                          | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/enum.ts`                                 | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/types.ts`                                | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/index.ts`                                | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.basics.spec.ts`       | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.events.spec.ts`       | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.variants.spec.ts`     | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.form.spec.ts`         | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts`     | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts`         | New                                                                                                                        |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/stryker.bds-date-picker.config.mjs`            | New (Task 23) — per-component Stryker config                                                                               |
| `packages/boreal-web-components/src/index.html`                                                                                     | Modify — playground scenarios per task (never committed, per project memory)                                               |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts`                                                     | New                                                                                                                        |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx`                                                            | New — includes internal `bds-calendar-grid` implementation note                                                            |

**Critical reference files** (read before implementing):

- `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx` — popover/trigger composition wiring, `getter` pattern for `bdsPopover`/`bdsField`
- `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` — `footer`/`footer-button`/`footer-helper` slots, `floatingOptions.hideArrow`
- `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` — FACE pattern, `selectable` non-editable trigger mechanism
- `packages/boreal-web-components/src/components/data-visualization/bds-table/` — `helpers/`+`utils/`+`types/` file-split model
- `packages/boreal-web-components/src/components/navigation/bds-tab-group/bds-tab-group.tsx` — controlled parent/dumb-child event pattern via `@Listen()`
- `packages/boreal-web-components/src/utils/a11y/keyboard/__test__/navigation.spec.ts` — plain-Jest pure-logic test pattern
- `ai-work/plans/EOA-16000-bds-table-v4.md` — precedent for the consolidated mutation-testing task (its Task 15) and per-task QA/parity dispatch pattern this plan adapts
- [Date Picker Dialog Example — WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) — `<table role="grid">` reference markup for Tasks 9–11

---

## Phase 0 — `date-engine`

### Task 1: Add `date-fns` and `@date-fns/tz` dependencies

**Status:** ✅ done — `date-fns@^4.4.0`/`@date-fns/tz@^1.5.0` added under `dependencies`, verified in `package.json`, `pnpm-lock.yaml`, and `node_modules`. An initial manual `pnpm install` pass added `date-fns-tz@^3.2.0` (an unrelated third-party package) instead of `@date-fns/tz`; caught, corrected, and documented in the Task 1 acceptance-criteria note below.
**Executor:** main thread (no executor)
**Files:**

- `packages/boreal-web-components/package.json` (modify)

**Acceptance criteria:**

- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` (latest per npm registry as of this plan's writing) added under `dependencies` — not `devDependencies`, since both ship at runtime inside `date-engine`.
- `@date-fns/tz` requires date-fns v4+; confirm the installed date-fns major is 4.x before proceeding to Task 23.
- `pnpm install` run at the workspace root; lockfile updated.
- Utility discovery note: searched `package.json` dependencies for any existing date library — none found (`@braintree/sanitize-url`, `@floating-ui/dom`, `@tanstack/virtual-core`, `dompurify` only). No suitable existing utility; new dependency justified per the spike doc's Finding 1.
- **Resolved (2026-08-13):** an install pass initially added `date-fns-tz@^3.2.0` (a similarly-named but unrelated third-party package, maintained by `marnusw`, built for date-fns v3's pre-native-timezone era) instead of `@date-fns/tz@^1.5.0` (the official companion package from the date-fns team itself, confirmed via the date-fns v4 announcement blog post — https://blog.date-fns.org/v40-with-time-zone-support/ — and via npm registry metadata showing its repo under `date-fns/date-fns`). Corrected to `@date-fns/tz@^1.5.0`; verified in `package.json`, `pnpm-lock.yaml` (no `date-fns-tz` entries remain), and `node_modules` (`@date-fns/tz@1.5.0`, `date-fns@4.4.0` both resolved). Task 23's `combineDateTimeToUTC`/`extractDateTimeFromUTC` design depends on `@date-fns/tz`'s `TZDate` object specifically — `date-fns-tz`'s `zonedTimeToUtc`/`utcToZonedTime` function-based API is not a drop-in substitute.

**Manual test (required):**
Non-visual/config task — validate with `pnpm install` completing without errors and `pnpm -w list date-fns @date-fns/tz` (or equivalent) showing the resolved versions inside `packages/boreal-web-components`.

**Commit:**

```bash
git commit -m "chore(boreal-web-components): EOA-16692 add date-fns and @date-fns/tz dependencies"
```

---

### Task 2: `date-engine` core types

**Status:** ✅ done — `types.ts` created (`DayCell`, `MonthGrid`, `WeekdayLabel`, `DateEngineLocale`), verified compliant with the project's Component Naming Conventions guideline (not directly applicable — this is a `services/` module, not a component — but PascalCase type naming and directory precedent both satisfied). `tsc --noEmit` introduces no new errors.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/types.ts` (create)

**Acceptance criteria:**

- Defines `DayCell`: native `Date`, naive-ISO string, `isCurrentMonth`, `isToday`, `isDisabled`, `isSelected` — the latter two are consumer-computed flags this type carries, not flags `date-engine` itself computes.
- Defines `MonthGrid` as a 6×7 (`DayCell[][]`, 6 weeks × 7 days) matrix plus `monthLabel`, `year`, `month` (0-indexed, matching native `Date`).
- Defines `WeekdayLabel` (short/long name + index) for the weekday row.
- Defines `DateEngineLocale` as a type alias for date-fns's `Locale` — the only date-fns type surfaced through the public barrel (Task 6 enforces no other date-fns leakage).
- No `@stencil/core`, no `HTMLElement`, no DOM globals anywhere in this file.
- Utility discovery note: checked `packages/boreal-web-components/src/types/` for an existing date/calendar type — none found. New types justified.

**Manual test (required):**
Non-visual task — validate with `pnpm --filter boreal-web-components exec tsc --noEmit` passing with no errors.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add core type definitions"
```

---

### Task 3: `date-engine` month-grid generation

**Status:** ✅ done — implementation (`grid.ts`: `generateMonthGrid`/`getWeekdayLabels`, date-fns only, pure) by `@frontend-subagent`; unit tests (`grid.spec.ts`) independently reviewed and strengthened by `@testing-subagent` (21 → 25 tests, closing an unasserted-return-shape gap on `isDisabled`/`isSelected`/`year`/`month`/`monthLabel`). 25/25 passing, 100% coverage on `grid.ts`, no new `tsc`/ESLint errors. Mutation testing correctly deferred to Task 30. Going forward, implementation and unit-test authorship for each task are dispatched as separate subagent calls (`@frontend-subagent` then `@testing-subagent`), per explicit direction — a change from this plan's original per-task executor tagging.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/grid.ts` (create)

**Acceptance criteria:**

- Exports `generateMonthGrid(year, month, options: { locale?: DateEngineLocale; weekStartsOn?: 0-6 })` producing a fixed 6×7 (42-cell) matrix, including leading/trailing days from adjacent months marked `isCurrentMonth: false`.
- `weekStartsOn` defaults to the supplied locale's own convention (date-fns `Locale.options.weekStartsOn`) when a `Locale` is given, else `0` (Sunday).
- Uses date-fns functions only (`startOfMonth`, `endOfMonth`, `startOfWeek`, `addDays`, etc.) — no hand-rolled calendar math.
- Exports `getWeekdayLabels(locale?, weekStartsOn?): WeekdayLabel[]` returning 7 labels in display order via date-fns `format`/`Locale.localize`.
- Pure function — no mutation of inputs, no module-level state.

**Unit tests to cover** _(spec file: `services/date-engine/__test__/grid.spec.ts`)_:

- Grid always has exactly 6 rows × 7 columns regardless of month length or starting weekday.
- Leading/trailing adjacent-month days are flagged `isCurrentMonth: false` with the correct calendar date.
- `isToday` is computed correctly relative to an injected/mocked "now" (avoid real-clock flakiness).
- February in a leap year (2024) vs. non-leap year (2023) produce correct day counts, delegating correctness to date-fns.
- `weekStartsOn` shifts the grid's first column correctly (Monday-start vs. Sunday-start).
- `getWeekdayLabels` reflects a custom `Locale`'s day names (e.g. French locale produces French labels).
- Plain Jest only — no `newSpecPage`. Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
Non-visual task — validate via `pnpm --filter boreal-web-components test -- date-engine` passing.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add month-grid generation"
```

---

### Task 4: `date-engine` date math

**Status:** ✅ done — implementation (`date-math.ts`: `addMonths`/`subMonths`/`isSameDay`/`isSameMonth`/`isWithinRange`/`compareDates`/`toNaiveISODate`/`fromNaiveISODate`) by `@frontend-subagent`; unit tests (`date-math.spec.ts`) by `@testing-subagent`. Note: `date-fns`'s `compareAsc` is typed as plain `number`, not a `-1 | 0 | 1` literal union — `compareDates` clamps explicitly via `if/else` rather than a type assertion. **Trimmed post-review (2026-08-13):** the original spec over-tested pure pass-through wrappers (`addMonths`/`subMonths`/`isSameDay`/`isSameMonth`/`isWithinRange`) with exhaustive boundary cases that were really re-testing date-fns's own already-tested correctness, not any logic of ours — these had zero branching/transformation, so only a date-fns bug could ever fail them. Trimmed each to one delegation smoke test (21 → 15 tests); `toNaiveISODate`/`fromNaiveISODate` (deliberate `format`/`parse` choice, avoiding `toISOString`/`new Date(iso)` pitfalls) and `compareDates` (real `number` → `-1|0|1` narrowing) were left untouched since those test genuine logic of ours. Coverage held at 100% on `date-math.ts` after the trim, confirming the dropped assertions added no real signal. 39/39 tests passing across the `date-engine` suite, no new `tsc`/ESLint errors.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/date-math.ts` (create)

**Acceptance criteria:**

- Exports `addMonths`/`subMonths` thin wrappers over date-fns, kept inside `date-engine` so all date-fns usage stays in this module.
- Exports `isSameDay`/`isSameMonth` (used now) and `isWithinRange`/`compareDates` (reserved for Phase 3/4 reuse — implemented now since trivial, but not wired into any Phase 0-2 component; JSDoc must state they're currently unused).
- Exports `toNaiveISODate(date): string` (→ `yyyy-MM-dd`, no timezone conversion) and `fromNaiveISODate(iso): Date` for the reverse.

**Unit tests to cover** _(spec file: `services/date-engine/__test__/date-math.spec.ts`)_:

- `addMonths`/`subMonths` correctly roll over year boundaries.
- `isSameDay`/`isSameMonth` ignore time-of-day components.
- `toNaiveISODate` produces zero-padded `yyyy-MM-dd` with **no timezone shift** — the test most likely to catch a `toISOString()`-style bug near UTC offset boundaries.
- `fromNaiveISODate` round-trips with `toNaiveISODate` including a leap day.
- `isWithinRange`/`compareDates` covered even though currently unused.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
Non-visual task — validate via the `date-engine` test script passing.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add date math and naive-ISO conversion helpers"
```

---

### Task 5: `date-engine` locale-aware formatting

**Status:** ✅ done — implementation (`format.ts`: `formatDisplayDate`/`getMonthYearLabel`) by `@frontend-subagent`; unit tests (`format.spec.ts`) by `@testing-subagent`, test depth matched to logic from the start per the Task 4 trimming precedent — `formatDisplayDate` (near-pure date-fns pass-through) got 3 tests, `getMonthYearLabel` (real logic: 0-indexed `month` → `Date` construction) got 4, including the December→January boundary case. 100% coverage on `format.ts`, 46/46 tests passing across `date-engine`, no new `tsc`/ESLint errors. Confirmed via date-fns's own type signature that `locale: undefined` is already handled safely by `format()` — no defensive guard added.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/format.ts` (create)

**Acceptance criteria:**

- Exports `formatDisplayDate(date, formatString, locale?)` wrapping date-fns `format`, used by `bds-date-picker`'s `format` prop for the trigger's display text.
- Exports `getMonthYearLabel(year, month, locale?)` for the calendar header, reused by `bds-calendar-grid`.
- Both no-op to a sensible default when `locale` is `undefined` — never throw.
- Utility discovery note: `bds-text-field`/`bds-select` have no display-formatting helper (they treat `value` as opaque). No conflict; new formatting utility scoped to `date-engine` only.

**Unit tests to cover** _(spec file: `services/date-engine/__test__/format.spec.ts`)_:

- `formatDisplayDate` respects custom format strings (`yyyy/MM/dd`, `dd/MM/yyyy`, `MMM d, yyyy`).
- `formatDisplayDate` produces locale-correct month names for a non-English `Locale`.
- `getMonthYearLabel` handles December→January boundary months correctly.
- No `locale` does not throw and produces a default-locale label.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
Non-visual task — validate via the `date-engine` test script passing.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add locale-aware formatting helpers"
```

---

### Task 6: `date-engine` public barrel + boundary audit

**Status:** ✅ done — `index.ts` created, mirroring `services/floating/`/`services/logger/`'s barrel pattern (codebase precedent followed over `development-standards.md` §3.3's stricter "no barrel files" text, per explicit 2026-08-13 decision). Boundary-check grep (`@stencil/core`/`document`/`window` across `services/date-engine/*.ts` excluding `__test__/`) returned zero matches; no date-fns leakage beyond `DateEngineLocale`. No new `tsc`/ESLint errors. **Phase 0's `date-engine` module (Tasks 1–6) is complete.**
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/index.ts` (create)

**Acceptance criteria:**

- Re-exports `grid.ts`/`date-math.ts`/`format.ts` public functions and `types.ts` types.
- Does not re-export any date-fns function or its `Locale` type by import path — only `date-engine`'s own `DateEngineLocale` alias is exposed.
- File-header JSDoc states the module is framework-agnostic, pure-function-only; grep for `@stencil/core` and `document`/`window` across `services/date-engine/*.ts` (excluding `__test__/`) must return nothing.
- Mirrors the sibling pattern set by `services/floating/` and `services/logger/` (barrel + types file).

**Manual test (required):**
Non-visual task — validate via `tsc --noEmit` passing and the grep boundary-check returning no matches.

**Commit:**

```bash
git commit -m "feat(date-engine): EOA-16692 add public barrel and finalize module boundary"
```

---

## Phase 0 — `bds-calendar-grid`

### Task 7: `bds-calendar-grid` types

**Status:** ✅ done — `ICalendarGrid.ts`/`types.ts`/`index.ts` created, imports `MonthGrid`/`DateEngineLocale` through the `date-engine` barrel via the `@/` path alias. No `disabled`/`min`/`max` prop added (Phase 3 out of scope); `DayCell.isDisabled` left as the future hook. No new `tsc`/ESLint errors. Confirms the same barrel-file written-guideline-vs-practice gap already resolved for `date-engine` also applies to component `types/` dirs (`bds-toggle`/`bds-text-field`/`bds-tag-field`/`bds-popover`/`bds-dialog` all use `index.ts` barrels despite §3.3's text) — codebase precedent followed, consistent with the 2026-08-13 decision.

**Naming correction (2026-08-13):** `DayClickDetail`/`MonthNavigateDetail` renamed to `CalendarGridDayClickDetail`/`CalendarGridMonthNavigateDetail`, per `development-standards.md` §1.5's documented `{Component}{Action}Detail` convention (its own example: `RadioChangeDetail`) — the original names weren't component-prefixed, an avoidable collision risk once re-exported through a shared barrel. Also confirmed per user instruction: no JSDoc on types/interfaces going forward; the three Task 7 files already had none.

**Structural correction (2026-08-13):** `bds-calendar-grid` was initially placed flat at `components/forms/bds-calendar-grid/`, as a sibling to `bds-date-picker`. Caught before Task 8: every existing multi-component family in this codebase (`bds-table`/`bds-table-column`/`bds-table-column-group`, `bds-tab-group`/`bds-tab`/`bds-tab-content`, `bds-card`/`bds-card-header`/`bds-card-footer`, `bds-list-menu`/`bds-list-menu-item`) nests under a shared parent folder named after the primary/orchestrator component, with the primary itself self-nested one level deeper — confirmed by directly inspecting `data-visualization/bds-table/`'s exact shape. Since `bds-calendar-grid` exists solely to be composed by `bds-date-picker` (and, later, the Phase 4 range picker — still a `bds-date-picker`-family concern), the correct structure is `components/forms/bds-date-picker/{bds-date-picker/, bds-calendar-grid/}`, matching that precedent. Task 7's already-created files were moved (`components/forms/bds-calendar-grid/types/*` → `components/forms/bds-date-picker/bds-calendar-grid/types/*`) and every remaining path reference in this plan (Tasks 8–30's Files lists) was corrected to the nested structure before any further files were created. Verified via `tsc --noEmit` post-move: only the 5 known pre-existing unrelated errors, nothing new. Docs (`apps/boreal-docs/`) are unaffected — that tree doesn't mirror component nesting.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/ICalendarGrid.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/types.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/types/index.ts` (create)

**Acceptance criteria:**

- `ICalendarGrid` declares: `grid: MonthGrid` (from `date-engine`), `selectedDate?: string` (naive ISO), `year: number`, `month: number` (0-indexed), `locale?: DateEngineLocale`.
- `types.ts` declares `CalendarGridDayClickDetail { date: string }` and `CalendarGridMonthNavigateDetail { year: number; month: number; direction: 'prev' | 'next' }`.
- No `disabled`/`min`/`max` props (Phase 3, out of scope) — but `DayCell.isDisabled` (already in `date-engine` types) is left as dead capacity so Phase 3 can wire it without an interface break.
- Utility discovery note: checked `bds-table-column`/`bds-table-column-group` types for a reusable "dumb controlled child" interface — none generic enough (table-specific); new interface justified, the _pattern_ (controlled, no internal state) follows `bds-tab`/`bds-tab-content`.

**Manual test (required):**
Non-visual task — validate via `tsc --noEmit`.

**Commit:**

```bash
git commit -m "feat(bds-calendar-grid): EOA-16692 add component type definitions"
```

---

### Task 8: `bds-calendar-grid` scaffold

**Status:** ✅ done — `bds-calendar-grid.tsx` created (`@Component({ tag: 'bds-calendar-grid' })`, all 5 props, both events, stub `<Host></Host>` render, deliberately zero `@State()`). Manual QA confirmed the element mounts and hydrates cleanly with an empty host and zero console errors, even with required props absent (stub never reads them). No new `tsc`/ESLint errors.
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx` (create)

**Acceptance criteria:**

- `@Component({ tag: 'bds-calendar-grid' })`, no `styleUrl` yet (Task 10), light DOM.
- `@Prop() readonly grid!: MonthGrid`
- `@Prop() readonly selectedDate?: string`
- `@Prop() readonly year!: number`
- `@Prop() readonly month!: number`
- `@Prop() readonly locale?: DateEngineLocale`
- `@Event() bdsDayClick!: EventEmitter<CalendarGridDayClickDetail>`
- `@Event() bdsMonthNavigate!: EventEmitter<CalendarGridMonthNavigateDetail>`
- `render()` returns a stub `<Host></Host>` only.
- Component owns **no** `@State()` for selection or displayed month — the scaffold itself is proof the "dumb, controlled" contract can't silently regress later without a visible diff.

**Manual test (required):**
Non-visual task (stub render) — validate via `tsc --noEmit`; add a temporary scenario to `packages/boreal-web-components/src/index.html` rendering a bare `<bds-calendar-grid>` and confirm `pnpm dev:components` shows no console errors (empty host expected).

**Commit:**

```bash
git commit -m "feat(bds-calendar-grid): EOA-16692 scaffold component with props and events"
```

---

### Task 9: `bds-calendar-grid` render as native `<table role="grid">` + interaction

**Status:** ✅ done (verified against every acceptance-criteria/unit-test/manual-test item individually, 2026-08-14) — full render implemented (native `<table role="grid">`, static month/year label header, prev/next `bds-button` nav emitting `bdsMonthNavigate` via `date-engine`'s `addMonths`/`subMonths`, day cells emitting `bdsDayClick` guarded against out-of-month/disabled cells). Added forward-compatible a11y attributes (`aria-selected`, `aria-current`, `aria-label` via `formatDisplayDate`, labeled nav buttons) ahead of Task 11. `tsc`/ESLint clean. Manual QA: all 3 required scenarios passed (basic grid, selected-date, controlled nav incl. Dec→Jan boundary) in Chromium + WebKit. One defect found and fixed along the way: the stale Task 8 stub scenario in `index.html` threw an uncaught `RangeError` on page load once the real render replaced the stub (missing `year`/`month`/`grid`) — fixed by wiring that scenario's props via the same JS-property pattern as the other scenarios, not by adding a defensive guard in the component (both props are already required `@Prop()`s). Known gap, not a defect: outside-month cells aren't visually muted yet — `bds-calendar-grid.scss` doesn't exist until Task 10. **Unit tests**: 3 spec files (`bds-calendar-grid.basics.spec.ts`/`.events.spec.ts`/`.variants.spec.ts`), 16 tests, all 8 required test topics from the plan individually confirmed present, 16/16 passing (independently re-run, not just trusted from the report), 100% statements/branches/functions/lines on `bds-calendar-grid.tsx` (target was ≥90%). Mutation testing correctly deferred to Task 30. (Correction note: this task was briefly marked done on 2026-08-14 with unit tests skipped entirely — manual QA passing had been mistakenly treated as sufficient; caught by the user asking "are we done, are you sure?", corrected, and unit tests written and independently verified before re-closing.)
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx` (modify — full render, replacing stub)

**Acceptance criteria:**

- Renders as a **native `<table role="grid">`**, per the spike doc's resolved decision (matches the WAI-ARIA APG's own Date Picker Dialog reference markup and `bds-table`'s established "native elements for free a11y" precedent):
  - Month/year label + prev/next nav buttons render in a header region above the `<table>` (not inside `<thead>` as a `<th>`, since nav controls aren't column headers) — using `getMonthYearLabel` from `date-engine`.
    - **Clarifying note (2026-08-14):** the month/year label is intentionally static/non-interactive text for Phase 1/2 — no click handler, no quick-picker. Figma's `_DatePickerCalendar` composite shows a designed month-grid/year-grid quick-picker triggered by clicking this label, but the user confirmed (2026-08-14) this is a deliberate scope deferral, not an oversight. See the spike doc's "Unscheduled — month/year quick-picker" backlog entry (`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`) for detail.
  - `<thead><tr role="row">` contains 7 weekday `<th scope="col">` cells, in order from `getWeekdayLabels`. `role="row"`/`columnheader` are implied by `tr`/`th` per the APG reference — no manual role authoring needed there.
  - `<tbody>` contains 6 `<tr role="row">` week rows, each with 7 `<td role="gridcell">` day cells (role implied by `td`, matching the APG pattern).
  - **Updated (2026-08-14, no-inline-comments tightening):** the reasoning for why `role="grid"` isn't redundant on a native `<table>` (overrides the implicit `role="table"` to signal interactive 2D navigation semantics to assistive tech) lives in the spike doc's Finding #2, not as an inline code comment — the project's comment convention was tightened mid-implementation to disallow even non-obvious-WHY comments, especially ones citing external specs. No code comment on the `role="grid"` attribute.
- Prev/next buttons emit `bdsMonthNavigate` with the computed adjacent year/month (via `date-engine`'s `addMonths`/`subMonths`) and `direction`; component does **not** self-update `year`/`month` — parent re-renders with new props (controlled pattern, matching `bds-tab-group`).
- Day cell click emits `bdsDayClick` with the cell's naive ISO date; cells with `isDisabled: true` (currently none set by any Phase 0-2 caller, dead capacity from Task 7) must not emit, guarding the future Phase 3 wiring point.
- Day cell states via CSS class map: default, hover (`:hover`), focus (`:focus-visible`), selected/active (`selectedDate` match), disabled (dead capacity, styled but unused), today (`isToday`). No in-range/end-range states (Phase 4+, out of scope).
- Nav buttons reuse `bds-button`'s icon-only variant (matching how `bds-popover`'s `closable` header button is implemented) rather than hand-rolled `<button>` markup, unless the 32×32px sizing constraint requires a hand-rolled `<button>` — if so, document why `bds-button` didn't fit.
- Leading/trailing adjacent-month days render visually de-emphasized but remain clickable, **pending confirmation against the actual Figma screenshot at implementation time** (open question — see Remaining Open Questions).
- Utility discovery note: `src/utils/a11y/keyboard/navigation/grid-navigation.ts` exists and is generic for arrow-key grid traversal, but keyboard nav is explicitly out of scope for Phase 0-2 (Phase 8) — do not wire it here. **Updated (2026-08-14, no-inline-comments tightening):** this integration-point note is recorded here in the plan (and in the spike doc if relevant to a future phase's backlog entry), not as an inline code comment near the day cells — no code comment citing `grid-navigation.ts`.

**Unit tests to cover** _(spec files: `bds-calendar-grid.basics.spec.ts`, `bds-calendar-grid.events.spec.ts`, `bds-calendar-grid.variants.spec.ts`)_:

- `basics`: renders as `<table role="grid">` with `<thead>`/`<tbody>`, 42 `<td>` day cells, correct weekday `<th scope="col">` order, correct month/year label for a given `grid`/`year`/`month` combination.
- `basics`: renders using `newSpecPage`, asserting no internal `@State()` drives output — identical props produce identical output (proves the "dumb" contract).
- `events`: clicking a day cell emits `bdsDayClick` with the correct ISO date; clicking prev/next emits `bdsMonthNavigate` with correctly rolled-over year/month at December→January and January→December boundaries.
- `events`: the component's own `year`/`month` props do not change after a nav click unless the parent re-passes new props.
- `variants`: `selectedDate` marks exactly one cell selected/active; `isToday` marks the current-date cell (inject/mock "now").
- `variants`: outside-month cells render with the de-emphasized class and match whichever interactivity behavior was confirmed against Figma.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**

- Scenario 1: render `<bds-calendar-grid>` in `index.html` with a `grid` for August 2026 (has leading July and trailing September days), `year=2026`, `month=7`.
- Scenario 2: same grid but with `selectedDate` set to a mid-month date.
- Scenario 3: wire prev/next buttons via a small inline script in `index.html` that re-computes and re-assigns `grid`/`year`/`month` props on `bdsMonthNavigate`, to visually confirm the controlled round-trip works before `bds-date-picker` exists.

Run: `pnpm dev:components` and validate:

- [ ] Given the August 2026 grid, when rendered, then the header shows "August 2026", the weekday row starts on the locale's configured day, and 42 day cells are visible with July/September days visually muted. Pass: header text and cell count match.
- [ ] Given `selectedDate` set, when rendered, then exactly one cell shows the selected/active style. Pass: single highlighted cell.
- [ ] Given the wired prev/next buttons, when clicking "next", then the header updates to "September 2026" and the grid re-renders for that month, including correctly across the December→January boundary if tested at that range. Pass: header and cell dates advance by exactly one month per click.

**Commit:**

```bash
git commit -m "feat(bds-calendar-grid): EOA-16692 implement table role=grid render and day/month navigation events"
```

---

### Task 10: `bds-calendar-grid` JSDoc audit + SCSS

**Status:** ✅ done (2026-08-15, after an extended reopen — verified against every acceptance-criteria item individually, plus a full computed-style QA pass in Chromium and WebKit) — JSDoc audit found all `@Prop`/`@Event`/class-level docs already accurate. `bds-calendar-grid.scss` created and wired via `styleUrl`, `$boreal-*` tokens exclusively, no `@use` of the token package.

This task was reopened twice after an initial too-early "done" mark, catching real gaps across several rounds — recorded here as one consolidated history rather than per-round, since the sequence of user-caught issues is itself the useful record for future similar tasks:

1. **Missing structure/typography** (first reopen): `__header`/`__table` had no explicit width (drifted independently instead of sharing Figma's fixed 248px `Container` width); `thead`/`th` had zero styling; `:hover`/`:focus-visible`/`:active` were entirely absent, contradicting Task 9's own acceptance criteria. Fixed with the full token mapping: `$boreal-spatial-layout-l` (32px cells), `$boreal-radius-xs` (4px radius), `$boreal-spatial-padding-m`/`-l` (16/24px header padding, superseding the plan's stale "53px" note), `$boreal-text-default`/`-disabled`/`-inverse`, `$boreal-ui-primary-base` (selected fill), `$boreal-stroke-primary-base` (today's ring), plus `font-family`/`font-size`/`font-weight`/`line-height` (Inter, 12px, 400, 16px — matches Figma's `body/xs` style used throughout, `<th>`'s default browser bold explicitly overridden). `border-collapse: separate; border-spacing: ...` used deliberately instead of literal `collapse` (mechanically incompatible with the 4/2px gutter requirement on a bare `<table>`).
2. **Root-selector bug** (second reopen, user-caught): the root SCSS block used `.#{$prefix} { ... }` (a class selector) for host-level typography/`user-select`, but `<Host>` never carries that literal class — the whole block was dead CSS. Restructured to mirror `bds-table.scss`'s exact convention: bare `bds-calendar-grid { }` for the host tag, bare `table`/`thead th` for native table structure, BEM classes only for JS-state-driven parts (`__day` and its modifiers). Also added `display: inline-block` on the host (previously defaulted to `inline`, which block-ified and stretched to fill its container once block children were present — same fix pattern as `bds-table`'s own explicit `display: flex`).
3. **Interaction-state correctness** (same round): the dashed "today" ring was incorrectly applied to every hover/focus/active state instead of only `--today` cells (removed from the base interactive block, relies on `--today`'s independent rule combining naturally); the `--selected` modifier had no hover/focus/active treatment at all and was being silently overridden by the base hover rule's higher specificity (fixed with `$boreal-ui-primary-dark` for Selected+Hover/Active, ring-on-same-blue for Selected+Focus, all decoded from Figma); Selected+Disabled combo added (`$boreal-ui-primary-light` fill, `$boreal-text-inverse` text — initially shipped with the wrong dark disabled-gray text due to CSS source-order, fixed).
4. **Focus outline leak** (final QA round): disabled/outside-month cells (excluded from the custom `:focus-visible` ring by design) still showed a native browser focus outline when genuinely focused via `.focus()`, since `outline: none` only existed inside the interactive block those cells are excluded from. Fixed by moving `outline: none` to the base `__day` rule, covering every variant uniformly.

**Final QA**: full computed-style verification (not eyeballed) in both Chromium and WebKit — cell size/radius/gutters/header padding, all day-cell state colors (default/today/selected/outside/disabled/selected+disabled), all interactive states (hover/focus/active) on ordinary/today/selected/disabled cells, host `display: inline-block` with fixed ~256px width matching the table exactly, weekday `<th>` alignment and non-bold weight, `user-select: none` (confirmed via real drag-select test in WebKit, not just computed-style, which reads unreliably for this property in Playwright's WebKit driver), typography, and the outline fix — all passing identically in both engines, 0 console errors. Task 9's untouched scenarios re-confirmed unaffected (Scenario 2's plain Selected+interactive states, Scenario 3's month nav incl. Dec→Jan boundary). All 16 unit tests still passing, 100% coverage, unaffected throughout (styling-only changes).

**Playground**: a new dedicated Task 10 section (`#calendar-grid-states`) was added to `index.html`, showcasing every day-cell state in one grid via forced `isToday`/`isDisabled` overrides on `buildMonthGrid()` (independent of the real system date), documented with exact DevTools "Force state" steps for the states that require live interaction. Explicitly does not attempt to demo the Figma `_DatePickerNumber` component_set's `Inactive` state (a blank, numberless cell) — unreachable in this implementation, since `generateMonthGrid()` always produces 42 real day cells by design.
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx` (modify — JSDoc only)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.scss` (create)

**Acceptance criteria:**

- Every `@Prop`, `@Event`, and the class-level component JSDoc block are complete and accurate.
- SCSS uses `$boreal-*` tokens exclusively (matching `bds-text-field.scss`'s convention) — no hardcoded hex/px values for colors; spacing/sizing translated to the nearest token scale per the Figma sizing notes (32×32px cells, 53px header padding, 4px/2px grid gutters, 290×290px card, 24px/12px card padding) — if no exact token matches a given pixel value, pick the nearest token and record the delta in this task's plan status note (2026-08-14 tightening: not as an inline SCSS comment).
- Includes a `border-collapse: collapse` / table-default-style reset (removing native `<table>` default border/spacing), since `<table role="grid">` was chosen deliberately and its default browser chrome needs resetting.
- `@Component` gets `styleUrl: 'bds-calendar-grid.scss'` added.

**Manual test (required):**
Reuse Scenarios 1-3 from Task 9; validate:

- [ ] Given the rendered grid, when compared against the Figma sizing spec, then cell sizes, header padding, and card padding visually match within the nearest token's tolerance, and no native `<table>` default border/spacing is visible. Pass: visual match confirmed by side-by-side comparison with the Figma screenshot.

**Commit:**

```bash
git commit -m "feat(bds-calendar-grid): EOA-16692 add SCSS styling and finalize JSDoc"
```

---

### Task 11: `bds-calendar-grid` accessibility unit tests

**Status:** ✅ done (2026-08-14) — created `bds-calendar-grid.a11y.spec.ts` with 6 tests (5 assertions + 1 `it.todo` documenting the deliberate arrow-key-navigation exclusion), covering: `table[role="grid"]` + `th[scope="col"]` structural facts, a day cell's `aria-label` matching the full `formatDisplayDate(..., 'PPPP')` output (not just the visible day number), both nav `bds-button`s' `label` attribute ("Previous month"/"Next month"), today's cell via `aria-current="date"` (absent on other cells), and the selected cell via `aria-selected` presence (Stencil serializes JSX boolean `aria-selected={true}` as an empty-string attribute and omits it entirely when `false` — asserted with `hasAttribute`, not a `"true"/"false"` string comparison, matching the framework's actual runtime output for boolean ARIA props). All 4 sibling spec files (basics/events/variants/a11y) pass together: 21 passed + 1 todo, 100% statement/branch/function/line coverage on `bds-calendar-grid.tsx`. Mutation testing deferred to Task 30 per plan.

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts` (create)

**Acceptance criteria:**

- Follows the split-spec-file convention (`bds-toggle`/`bds-tab-group` `__test__/` layout) — this file covers only accessibility assertions, not duplicating basics/events/variants coverage from Task 9.

**Unit tests to cover:**

- The rendered root is a `<table>` with `role="grid"`, and weekday header cells are `<th scope="col">` (both structural facts asserted directly, confirming the Task 9 markup decision landed correctly).
- Day grid cells expose an accessible name containing the date (exact mechanism is a Task 9 implementation decision; this test asserts the outcome).
- Nav buttons have accessible names (e.g. "Previous month"/"Next month"), not icon-only with no label.
- Today's cell and the selected cell are each distinguishably announced (assert presence of `aria-current`/`aria-selected` or equivalent, whichever Task 9 committed to).
- No keyboard-navigation assertions here (Phase 8, out of scope) — confirm this spec file does not test arrow-key traversal.

**Manual test (required):**
Non-visual (test-only) task — validate via `pnpm --filter boreal-web-components test -- bds-calendar-grid` passing, at ≥90% coverage (coverage-phase only; mutation testing deferred to Task 30).

**Commit:**

```bash
git commit -m "test(bds-calendar-grid): EOA-16692 add accessibility unit tests"
```

---

## Phase 1 — `bds-date-picker` (single date, no time)

### Task 12: `bds-date-picker` types

**Status:** ✅ done — `IDatePicker.ts`/`enum.ts`/`types.ts`/`index.ts` created under the new `bds-date-picker/bds-date-picker/types/` folder, split-folder pattern matching `bds-table`'s and Task 7's (`bds-calendar-grid`) precedent. `FOOTER_ACTION` implemented as a `const` object + derived string-union type (not a TS `enum` keyword), matching `bds-table/types/enum.ts`'s `SORT_DIRECTION` pattern. `DateEngineLocale` imported via the `@/services/date-engine` barrel. No JSDoc on any type/interface (2026-08-13 convention); the user manually removed an initial future-range-value code comment from `types.ts` as unnecessary, since that rationale is already captured in this plan. `tsc --noEmit`: no new errors (5 pre-existing baseline unchanged). **Correction (2026-08-18):** `hideArrow`'s documented default was flipped from `true` to `false` post-implementation to comply with `stencil/ban-default-true` (see Task 13's status note for the full rationale) — `IDatePicker`'s acceptance criteria above updated accordingly; no `IDatePicker.ts` code change was needed since the interface only declares the type (`boolean`), not the default value.
**Reopened (2026-08-19):** `IDatePicker` gained `headerPlaceholder: string;` for Task 14's popover-header rework (see Task 14's 4th reopen note) — a one-line interface addition, no other Task 12 files touched.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/IDatePicker.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/enum.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/types.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/types/index.ts` (create)

**Acceptance criteria:**

- `IDatePicker` declares: `value: string` (public, canonical ISO — naive `yyyy-MM-dd` in Phase 1), `format: string` (date-fns format string, default `yyyy/MM/dd`), `locale?: DateEngineLocale`, `timezone: string` (default resolved via `Intl.DateTimeFormat().resolvedOptions().timeZone`), `hideArrow: boolean` (default `false` — flipped 2026-08-18 from the originally-specified `true` per `stencil/ban-default-true`), `name: string`, `disabled: boolean`, `required: boolean`, `headerPlaceholder: string` (default `'Select a date'` — added 2026-08-19, see Task 14's 4th reopen note).
- `types.ts` declares `DatePickerDraftState { selectedDate: string | null }` for Phase 1 (extended in Phase 2 to add `hour`/`minute`), kept as its own type so later phases can extend it without touching the public interface.
- `types.ts` documents (comment only, not implemented) the future range value shape `{ start: string; end: string }` per the spike doc's Finding 4 — `value`'s type must not be pinned in a way that forces a rename when range ships.
- `enum.ts` declares a footer-action enum (`CLEAN`/`CANCEL`/`APPLY`) used internally for footer button wiring.
- Utility discovery note: checked `bds-select`'s `types/ISelect.ts` (single-file) vs. `bds-text-field`'s `types/` folder (split) — `bds-date-picker`'s complexity (draft state, footer actions, future time fields) justifies the split-folder pattern, matching `bds-table`'s model.

**Manual test (required):**
Non-visual task — validate via `tsc --noEmit`.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add component type definitions"
```

---

### Task 13: `bds-date-picker` scaffold

**Status:** ✅ done — `bds-date-picker.tsx` created under the new `bds-date-picker/bds-date-picker/` directory with all specified props/state/events and a stub `render()` composing empty `<bds-text-field slot="field">` + `<bds-popover>` shells. One-line JSDoc added on every `@Prop`/`@State`/`@Event` (required by `stencil/required-jsdoc`, an `error`-level rule) — the "no JSDoc" 2026-08-13 convention was confirmed to apply to plain type/interface files only, not decorated `.tsx` component members; `bds-calendar-grid.tsx` was checked and follows the same one-line-JSDoc-on-decorators pattern. `tsc --noEmit`: no new errors (10 pre-existing baseline unchanged, confirmed via `diff`). Stencil build succeeds; component registers (`.d.ts` generated). A temporary stub scenario was added to `index.html` (uncommitted, per this plan's convention) for manual verification.
**Correction (2026-08-18):** `hideArrow`'s default was flipped from `true` to `false`, both here and in the landed code — `stencil/ban-default-true` (an ESLint rule from `@stencil/eslint-plugin`, confirmed by reading the rule's source: it unconditionally flags any `@Prop()` boolean literal `true`, with no self-resolving condition) flagged it, and a `grep` across the entire codebase confirmed `hideArrow` would have been the _only_ boolean `@Prop()` anywhere defaulting to `true` — every other boolean prop in the codebase defaults to `false`. Considered and rejected: (a) an inline `eslint-disable` comment (no precedent for that pattern anywhere in this codebase), (b) renaming to `showArrow: boolean = false` with inverted wiring (diverges from `bds-popover`'s own `floatingOptions.hideArrow` naming this component composes against, and from the ticket's literal prop name), (c) a `'true' as unknown as boolean` cast to dodge the rule while keeping the literal meaning "true" (rejected outright — confirmed via direct testing that it passes the linter but is fundamentally dishonest about the type and defeats the rule's actual purpose). Chosen: flip the default to `false` for real, both in code and in the ticket (`ai-work/tickets/EOA-16692-bds-date-picker.md:37`), the spike doc's Resolved Decisions table, and this plan (Tasks 12/13/14/20) — the popover's arrow now renders by default, hidden only via explicit `hide-arrow="true"`. Verified post-change: `stencil/ban-default-true` no longer fires on `bds-date-picker.tsx` (only the expected, self-resolving `stencil/strict-mutable` warning on `value` remains — it fires only because nothing yet assigns `this.value` internally; it will clear on its own once Task 16's Apply/Clean logic adds that assignment, needs no action now); `tsc --noEmit` still clean. Both Task 12 and Task 13 commits (`feat(web-components): EOA-16692 add component type definitions`, `feat(web-components): EOA-16692 scaffold component with props, state, and events`) pushed to `origin/feature/EOA-16692_bds-date-picker-v1_DG`.
**Architecture correction (2026-08-19) — reopened, see the "Architecture Correction" section after Task 16 for full rationale:** the stub `render()`'s self-rendered `<bds-text-field slot="field">` is replaced with `<slot name="field"></slot>` — the consumer now supplies their own `<bds-text-field>`, exactly as `bds-select` requires for its `slot="field"`. Add `@slot field - The trigger field. Use <bds-text-field slot="field">, fully configured by the consumer (label, sublabel, icon, helperText, etc.)` as class-level JSDoc, matching `bds-select`'s own `@slot field` annotation style. `disabled`/`required`/`name`/`value`/`format`/`locale`/`timezone`/`hideArrow`/`labels` all stay as `bds-date-picker`'s own props, unaffected — only the trigger field's own cosmetic configuration moves to the consumer. **Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Nothing outside `render()`/the class JSDoc was touched (confirmed via diff review). Not yet manually re-verified in the browser at this point, since `index.html`'s existing scenarios still had no slotted field — deferred to the `index.html` update step (see Architecture Correction section) and Task 14's own QA pass below, which exercises a slotted composition directly.
**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (create)

**Acceptance criteria:**

- `@Component({ tag: 'bds-date-picker' })`, light DOM, no `styleUrl`/`formAssociated` yet.
- `@Prop({ mutable: true, reflect: true }) value: string = ''`
- `@Prop() readonly format: string = 'yyyy/MM/dd'`
- `@Prop() readonly locale?: DateEngineLocale`
- `@Prop() readonly timezone: string = Intl.DateTimeFormat().resolvedOptions().timeZone` (resolved once as a class field default, not recomputed every render)
- `@Prop() readonly hideArrow: boolean = false` (default flipped 2026-08-18 from the originally-specified `true`, to comply with `stencil/ban-default-true` — no boolean `@Prop()` in the codebase defaults to `true`; the popover's arrow now renders by default, hidden only via explicit `hide-arrow="true"`)
- `@Prop() readonly name: string = ''`
- `@Prop() readonly disabled: boolean = false`
- `@Prop() readonly required: boolean = false`
- `@State() draft: DatePickerDraftState = { selectedDate: null }`
- `@State() popoverVisible: boolean = false`
- `@Event() bdsChange!: EventEmitter<string>`
- `@Event() valueChange!: EventEmitter<string>` (Vue/Angular two-way-binding pair, matching `bds-select`'s naming convention)
- `render()` returns a stub composing empty `<bds-text-field slot="field">` + `<bds-popover>` shells only.

**Manual test (required):**

- Scenario 1: render a bare `<bds-date-picker>` in `index.html`.
  Run: `pnpm dev:components` and validate:
- [ ] Given the bare component, when rendered, then a text field and an (empty, hidden) popover shell appear with no console errors. Pass: no runtime errors.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 scaffold component with props, state, and events"
```

---

### Task 14: `bds-date-picker` popover + trigger wiring

**Status:** ✅ done — `bds-date-picker.tsx` modified per the acceptance criteria: `componentDidLoad()` wires `bdsPopover.setListenElement`/`setAnchorElement` against `bdsInputContainer` (via a defensive null-guard, not a type assertion — see the correction note below); `bds-text-field` renders `selectable={true}`; `bds-popover` gets `managed={true}`, `disabled`, `footer={true}`, `placement="bottom-start"` (see correction below), and `floatingOptions={{ hideArrow: this.hideArrow }}`; trigger click (`listenClickTrigger`, wired via `addElementListener`/`removeElementListener`) calls `openPopover()`. `tsc --noEmit`/build/eslint all clean (only the expected, self-resolving `stencil/strict-mutable` warning on `value`). `index.html` scenarios added (uncommitted, per convention) for the 3 required manual-test cases. Commits pushed: `feat(web-components): EOA-16692 wire text-field trigger and popover composition`.
**Two corrections made post-implementation, before marking this task done:**

1. **Null-safety (2026-08-18):** the initial implementation called `this.bdsPopover?.setListenElement(this.bdsInputContainer)`/`setAnchorElement(this.bdsInputContainer)` directly, where `bdsInputContainer` is typed `HTMLElement | null` but both methods require a non-null `HTMLElement`. This didn't surface as a `tsc --noEmit` error because this repo's `tsconfig.json`/`tsconfig.build.json` (and the workspace-root `tsconfig.json`) don't enable `strict`/`strictNullChecks` anywhere — confirmed by re-running `tsc --noEmit --strictNullChecks`, which reproduced the exact error (`Argument of type 'HTMLElement | null' is not assignable to parameter of type 'HTMLElement'`). `bds-select.tsx` has this same nullable-getter pattern and handles it via `as HTMLElement` casts at the call site (lines 161-162) — the user opted for a defensive null-guard instead (narrowing `const inputContainer = this.bdsInputContainer; if (inputContainer !== null) { ... }`) over matching that cast-based precedent, so both calls are skipped entirely (not wired with a `null` anchor/listen target) if the internal `.bds-text-field__container` isn't present yet when `componentDidLoad()` fires. Re-verified clean under `--strictNullChecks` after the fix. **Process note:** a green `tsc`/`eslint`/build run is not sufficient evidence of null-safety in this codebase, since `strictNullChecks` is off project-wide — call-site types must be manually cross-checked against a getter's declared return type, not just tool output.
2. **Fixed `bottom-start` placement (2026-08-18, not in the original plan text):** `bds-popover`'s own `placement` prop defaults to `'bottom'` (centered) and Task 14's original acceptance criteria never mentioned it, only `floatingOptions.hideArrow`. A user-provided reference design (calendar-dialog behavior spec screenshot) showed the panel/arrow consistently left-aligned under the trigger field across all three example states — i.e. `bottom-start`, not `bottom`, and not user-configurable. Added `placement="bottom-start"` as a hardcoded literal on `<bds-popover>` in `render()`, matching `bds-dropdown.tsx`'s existing `placement="bottom-start"` precedent exactly (a literal string, not the `POPOVER_POSITION.BOTTOM_START` constant — `bds-dropdown.tsx` doesn't use the constant either). Ticket brief, spike doc, and this plan's acceptance criteria below updated to record this as a real (if late-discovered) requirement, not an implementation-detail choice.
   **Manual QA (2026-08-18):** user ran an informal pass first; independently re-verified via Playwright against all 4 checklist items below (open/close + arrow visible by default, `hide-arrow="true"` removes the arrow element from the DOM entirely, `disabled` blocks opening even via a force-dispatched click bypassing the native `disabled` input, and `bottom-start` placement confirmed both via `bds-popover[data-placement="bottom-start"]` and an exact trigger/popover `left` bounding-box match). Zero defects found; one pre-existing, out-of-scope cosmetic note flagged (`bds-popover.tsx`'s internal `data-hidearrow` attribute is inversely named — present when the arrow _is_ shown — lives entirely in `bds-popover.tsx`, not touched by this task). Dev server left running for Tasks 15-19's QA passes. Filed as its own bug, out of scope for this plan: `ai-work/qa/bug-reports/2026-08-18-bds-popover-bug-001.md`, tracked in Jira as [EOA-17085](https://telesign.atlassian.net/browse/EOA-17085) (Sub-task of EOA-16914, linked "relates to" EOA-16692).
   **Architecture correction (2026-08-19) — reopened, see the "Architecture Correction" section after Task 16 for full rationale:** the `bdsField` getter is mechanically unaffected — `el.querySelector('bds-text-field')` finds the consumer's slotted child exactly as it found the previously-self-rendered one. New: a runtime validation warning (`new Logger().warn('bds-date-picker', ...)`, matching `bds-select.tsx`'s own console-warning pattern for its `multiselect`/slotted-element-type check) fires when no `bds-text-field` is found slotted at `componentDidLoad()`. New: `bds-date-picker` pushes `selectable={true}` **and** `disabled={this.disabled}` onto the consumer's field imperatively via `updateElementProp` (confirmed already null-safe — it no-ops on `el === null`, no extra guard needed), in `componentDidLoad()` and via a new `@Watch('disabled')` — decided to sync `disabled` (unlike `bds-select`, which leaves it entirely to the consumer) since `bds-date-picker` already owns `disabled` independently for FACE (Task 17), so requiring the consumer to also set it on their own field would be duplicative and easy to forget. **Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Live Playwright re-verification against 4 new `index.html` scenarios (kept in place, documenting the new behaviors): no warning fires when a field is properly slotted; the warning fires correctly for a bare `<bds-date-picker>` with no slotted field; `selectable` is confirmed `true` on the slotted field after mount; `disabled` syncs correctly both from the initial attribute and via a post-mount JS toggle in both directions (`true`→`false`→`true` all confirmed on the slotted field).
   **Reopened again (2026-08-19) — Slotted Field Props Compatibility Audit** (see the dedicated section after Task 18 for full rationale/audit table): two more required changes to `componentDidLoad()`/`disconnectedCallback()`, alongside the existing missing-field warning and `selectable`/`disabled` sync:
   1. **`bdsClear` wiring (bug fix):** `addElementListener(this.bdsField, 'bdsClear', this.handleFieldClear)` (+ matching `removeElementListener`) — `handleFieldClear` mirrors the footer's Clean action exactly (`commitValue('')`, `this.draft = resetDraft('')`, close the popover if open). Fixes a confirmed silent data-integrity bug: without this, clicking the slotted field's own clear (X) button (when a consumer sets `clearable`/`clear-on-hover`) emptied only the _visual display_, leaving `bds-date-picker`'s real `value` unchanged and undetectable (no event fires, since `valueChange` bubbling is deliberately suppressed) — reopening the popover showed the old date still selected while the trigger looked empty moments before.
   2. **`name`-on-inner-field warning (defensive, matching the existing missing-field `Logger.warn` pattern):** if the slotted field has a non-empty `name`, warn that this causes silent double-submission to `FormData` with a differently-formatted value (confirmed live: submitting produced two entries, the picker's own naive-ISO value and the inner field's own formatted-display value, under two different keys).
      **Verified:** implemented — `handleFieldClear` reuses `handleFooterAction(FOOTER_ACTION.CLEAN)` via a one-line delegate (no logic duplication; `FOOTER_ACTION.CLEAN`'s branch already does exactly the required reset-draft/commit-empty/close-popover steps unconditionally, with no dependency on a prior draft selection existing). `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Live Playwright re-verification: clicking the slotted field's own clear button on a committed `value="2026-08-12"` instance correctly empties `bds-date-picker.value` (not just the field's display), fires `bdsChange`/`valueChange` exactly once each with `''`, and reopening the popover shows no stale day selected — matching the footer's Clean behavior exactly. The `name` warning fires correctly when the slotted field has a non-empty `name`, and does not fire for any of the ~15 other date-picker instances on the page that don't set one.
      **Reopened a 4th time (2026-08-19) — popover header row:** a Figma reference image showed a header row (icon + date/time text + close ✕) above the calendar grid that had been out of scope for this task's original text (only a passing spike-doc mention, no formal backlog entry). Decisions confirmed with the user before implementing: (1) header text is bound live to `this.draft.selectedDate` while the popover is open (updates as the user browses/selects days pre-Apply, falls back to reflecting the committed `value` after Apply/reopen — falls out of the existing draft lifecycle with zero extra branching); (2) an empty-state placeholder is required and must be consumer-customizable, matching MUI X's `toolbarPlaceholder` precedent exactly — added `@Prop() readonly headerPlaceholder: string = 'Select a date'`, used only when the formatted draft/value text is `''`; (3) the close (✕) button reuses `bds-popover`'s existing `closable` prop as-is — confirmed via QA that abandoning via the header close button already correctly reverts the draft on next open, no new wiring needed; (4) icon is a hardcoded `ICONS.CalendarDots` (`bds-icon-calendar-dots`, confirmed to exist in the production icon font, `content: "\e93b"`), not a configurable prop; (5) the header's date format matches the trigger's `format` prop for this v1 (single-date) scope — a future range variant's "Start"/"End" prefix is explicitly out of scope, tracked as a new Phase 4 backlog entry in the spike doc, not here. Implementation: `render()` now passes `header={true}` and `closable={true}` to `<bds-popover>`, plus two new slotted children — `<i slot="header-icon" class={ICONS.CalendarDots} aria-hidden="true"></i>` and `<span slot="header-title">{headerText !== '' ? headerText : this.headerPlaceholder}</span>`, where `headerText = formatValueForDisplay(this.draft.selectedDate ?? '', this.format, this.locale)` (reuses the existing utility, which already returns `''` for an empty input — no new branching needed there either). New `ICONS.CalendarDots` entry added to the shared `Icons.ts` constants file. `IDatePicker.ts` interface gained `headerPlaceholder: string;` (Task 12 reopened for this one-line addition).
      **Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean (including the new `Icons.ts` entry); Stencil build succeeds. QA dispatch (@qa-subagent, live Playwright against the existing `#date-picker-draft-empty` and `#date-picker-draft-value` instances) confirmed all 7 behavioral checks pass: empty-state placeholder shown correctly; live update to the drafted day pre-Apply; header close button closes the popover; reopening an abandoned empty draft reverts to the placeholder (not the abandoned day); a pre-set `value="2026-08-12"` instance shows the committed date formatted, not the placeholder; drafting then abandoning a different day (click-outside) correctly reverts the header back to the original committed date on reopen; zero new console errors across all of the above. **One real defect found, filed, not fixed (out of scope — lives entirely in `bds-popover.tsx`, not `bds-date-picker`):** the header's close (✕) button (`<bds-button>`, icon-only, no `label`/`aria-label`) has no accessible name, firing the existing `[BorealDS Button] No accessible name found` console warning every time any `header`+`closable` popover renders — a third confirmed instance of the same root pattern already tracked in `ai-work/qa/bug-reports/2026-08-06-bds-button-accessible-name-remaining.md` (Finding 3 added 2026-08-19), which also positively located that doc's previously-unconfirmed "Finding 2" (`bds-drawer-header.tsx`'s close button uses the same `aria-label`-on-host anti-pattern). Filed in Jira as [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133) (Sub-task of EOA-16914, linked "relates to" EOA-16692).
      **Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
      **Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- In `componentDidLoad()`, calls `bdsPopover.setListenElement(...)` and `bdsPopover.setAnchorElement(...)` exactly as `bds-select.tsx` does against its `bdsInputContainer` getter — reuse the same getter pattern (`private get bdsField()`, `private get bdsInputContainer()`, `private get bdsPopover()`) querying `this.el` at runtime.
- The composed `bds-text-field` renders with `selectable={true}` (reusing `bds-select`'s non-editable-input mechanism) so the field displays formatted text but isn't directly typable.
- `floatingOptions` passed to `bds-popover` sets `hideArrow: this.hideArrow` (deliberate deviation from `bds-select`/`bds-dropdown`'s hardcoded `true`; `hideArrow` defaults to `false` here — flipped 2026-08-18 per `stencil/ban-default-true` — so the arrow renders by default, unlike `bds-select`/`bds-dropdown`) plus the popover's own `footer` prop enabled so the Clean/Cancel/Apply buttons render in the popover's existing `footer-button` slot.
- `bds-popover`'s `placement` is a fixed `bottom-start` (hardcoded literal on the element, not a `bds-date-picker` prop, not left to `bds-popover`'s own `bottom` default) — matches the reference calendar-dialog design (arrow and panel consistently left-aligned under the trigger field) and `bds-dropdown.tsx`'s existing `placement="bottom-start"` precedent. Added 2026-08-18 — not in this task's original text, caught via design reference review.
- Clicking the trigger opens the popover (`openPopover()`); no calendar content yet (Task 15) — verify only open/close mechanics with an empty popover body.
- `disabled` prevents the popover from opening (mirrors `bds-popover`'s own `disabled` prop wired through `onBeforeShow`).
- **(Added 2026-08-19)** `bds-popover` renders with `header={true}` and `closable={true}`, slotting `<i slot="header-icon" class={ICONS.CalendarDots}>` and `<span slot="header-title">` bound to the live draft (falls back to `headerPlaceholder` when empty). `headerPlaceholder: string` defaults to `'Select a date'`. The header icon is hardcoded, not a consumer-configurable prop. The header's close button needs no extra wiring beyond `closable={true}` — abandoning via that button already correctly reverts the draft on next open, matching click-outside/Cancel behavior.

**Note:** Unit tests for this task's behavior (trigger open/close, `disabled` gating, `hideArrow` divergence) are covered in the consolidated Task 20 (Phase 1 unit tests), not written here.

**Manual test (required):**

- Scenario 1: default props (arrow visible by default); click the trigger to open/close the popover.
- Scenario 2: a second instance with `hide-arrow="true"` to visually confirm the arrow can be hidden.
- Scenario 3: a `disabled` instance confirming the trigger does not open the popover.
- Scenario 4 (added 2026-08-19): an instance with no `value` — verify the header shows the placeholder text, then updates live as a day is drafted (pre-Apply), then reverts to the placeholder on an abandoned-draft reopen.
- Scenario 5 (added 2026-08-19): an instance with a pre-set `value` — verify the header shows the committed date formatted, updates live while drafting a different day, then reverts to the committed date on an abandoned-draft reopen.

Run: `pnpm dev:components` and validate:

- [ ] Given the default instance, when clicking the trigger field, then the popover opens with its arrow visible; clicking outside closes it. Pass: popover visibility toggles correctly, arrow shown by default.
- [ ] Given the `hide-arrow="true"` instance, when opened, then no arrow renders between the popover and the trigger. Pass: arrow element absent.
- [ ] Given the `disabled` instance, when clicking the trigger, then nothing opens. Pass: popover stays hidden.
- [ ] Given any open instance, when the popover appears, then it is positioned bottom-start (arrow and panel left-aligned under the trigger field, not centered). Pass: matches the reference calendar-dialog design.
- [ ] Given an empty instance, when opened, then the header shows the placeholder, a calendar-dots icon, and a close button; clicking a day updates the header live; abandoning and reopening reverts to the placeholder. Pass: confirmed 2026-08-19 via @qa-subagent.
- [ ] Given a pre-set-value instance, when opened, then the header shows the committed date formatted; drafting a different day updates the header live; abandoning and reopening reverts to the committed date. Pass: confirmed 2026-08-19 via @qa-subagent.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 wire text-field trigger and popover composition"
```

---

### Task 15: `bds-date-picker` draft state utility + calendar wiring

**Status:** ✅ done — `utils/draft-state.ts` (`selectDay`/`resetDraft`/`cloneDraftFromValue`, pure, immutable), `utils/value-mapping.ts` (`resolveDisplayMonth`/`buildDisplayGrid` — the only two functions in this component's tree touching `date-engine`'s `fromNaiveISODate`/`generateMonthGrid` directly), `helpers/renderCalendarPanel.tsx` (pure render helper), and `bds-date-picker.tsx` modified: `@State() displayYear`/`displayMonth` added; `@Listen('bdsDayClick')`/`@Listen('bdsMonthNavigate')` wired (tested side-by-side against `addElementListener` first — `@Listen()` reliably catches events from `bds-calendar-grid` even nested inside `bds-popover`'s slot, since `bds-popover` is light DOM with no `shadow: true`, so the child stays a real DOM descendant and events bubble normally — matches the `bds-tab-group` precedent); draft/display-month reset wired into the existing `listenClickTrigger` handler, synchronously before `openPopover()` (ADR-0005 draft-until-Apply). `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) clean; `eslint` clean (only the expected, self-resolving `strict-mutable` warning on `value`); Stencil build clean. All 3 manual-test scenarios independently verified live via Playwright with concrete DOM/state evidence (day-click updates draft only, not `value`; initial `value` pre-highlights the correct day/month; abandoned-click-then-reopen correctly reverts to the committed day).
**Post-implementation defect found, diagnosed, and fixed (2026-08-18) — reported by the user, not caught by the implementing subagent's own Playwright pass:** on reopen (Scenario 3), when the committed day and the abandoned/previously-selected day fall in the **same displayed month**, the user observed the abandoned day's highlight briefly visible before visibly switching/cross-fading to the committed day — reproducible 100% of the time, across Chromium and Safari. Not reproducible across different months. Investigated in three stages:

1. First QA dispatch (JS/state-timing race hypothesis): rAF property-polling, sub-millisecond `MutationObserver` correlation, and video-frame analysis found **no** DOM-mutation-ordering race — `bds-date-picker`'s own state (`draft`/`displayYear`/`displayMonth`) was already fully correct and applied to `bds-calendar-grid`'s props before the popover became visible, in every sampled frame. This dispatch could not reproduce the user's report and initially concluded (incorrectly, in isolation) that it wasn't a real bug — its methodology (DOM-mutation timing) was the wrong lens for what turned out to be a CSS-visual issue, not a JS-ordering one.
2. Direct code read of `bds-calendar-grid.scss` (Task 10 styling, not Task 15) found the actual cause: the base `&__day` rule carried an **unconditional** `@include bds-transition-surface` (`transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease`), not scoped to `:hover`/`:focus-visible`/`:active`. `bds-calendar-grid.tsx` keys each `<td>` by `key={cell.isoDate}` — when both days share a month, Stencil reuses the same existing `<td>` node (only its `--selected` class moves), so the browser visually animates/cross-fades the `background-color` change over 300ms on that reused node — exactly the reported "switch." When months differ, all 42 `<td>` cells are destroyed and recreated (confirmed via a live DOM-node marker test), so a freshly-painted node has no prior color to transition _from_ — no visible animation, even though the same CSS rule still technically applies. This fully explains every one of the user's reported facts: reproducible across browsers (it's CSS, not an engine-specific race), same-month-only (node reuse vs. recreation), and 100% consistent (a deterministic CSS rule, not a timing race).
3. A second, targeted QA dispatch confirmed this specific hypothesis live: `getComputedStyle` showed the `0.3s ease` transition present on the day cells; forcing `transition: none !important` live eliminated the visible switch entirely (highlight snapped instantly); the different-month case was confirmed to recreate DOM nodes (marker-attribute test) rather than reuse them.
   **Fix applied** (in `bds-calendar-grid.scss`, a Task 10 file, not `bds-date-picker.tsx`): moved `@include bds-transition-surface` off the base `&__day` rule and into each of the 6 interactive pseudo-class blocks (`:hover`/`:focus-visible`/`:active`, in both the non-selected and `--selected` variant groups) — so hover/focus/active feedback still animates smoothly, but any `--selected` class change not accompanied by a matching interactive pseudo-class (i.e., any programmatic/prop-driven selection change: draft resets, Apply, external `value` changes) now applies instantly, with no cross-fade. Re-verified live: zero `transitionrun` events on reopen (day 12 selected instantly, no fade); hover/focus/active on both selected and non-selected cells still animate correctly (transition events still fire in those states). `bds-calendar-grid`'s existing unit test suite (21 passed + 1 todo, 100% coverage) unaffected — pure styling change. No regressions found.
   **Process note:** the first diagnostic dispatch's negative result was a lesson in methodology mismatch, not evidence the bug wasn't real — DOM-mutation/state-timing instrumentation (MutationObserver, property polling) cannot detect an _ongoing CSS transition_ animating a property that already mutated correctly at the DOM level; a live `getComputedStyle`/`transitionrun` check (or genuinely uncompressed frame capture) is the correct tool for that class of visual bug, not JS-level state/DOM-mutation timing checks.
   **Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
   **Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/draft-state.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/value-mapping.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/utils/index.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- `draft-state.ts` exports pure functions: `selectDay(draft, isoDate): draft`, `resetDraft(committedValue): draft`, `cloneDraftFromValue(value): draft` — kept out of the `.tsx` file per the `bds-table` file-organization decision.
- `value-mapping.ts` bridges `date-engine`'s `MonthGrid`/`Date` types and the component's naive-ISO `value` string, using `toNaiveISODate`/`fromNaiveISODate` — the only place in `bds-date-picker` that touches `date-engine`'s date-math functions directly.
- `renderCalendarPanel.tsx` composes `<bds-calendar-grid>` inside the popover body, computing its `grid`/`year`/`month`/`selectedDate` props from component `@State`.
- Component adds `@State() displayYear`/`@State() displayMonth` (initialized to the committed `value`'s month, or today's month if `value` is empty) — the orchestrator owns this, `bds-calendar-grid` never does.
- Listens to `bdsDayClick` from the slotted `bds-calendar-grid`. Confirm at implementation time whether Stencil's `@Listen()` decorator reliably catches events from a `bds-calendar-grid` rendered inside `bds-popover`'s slotted content, or whether the `bds-select.tsx`-style runtime `addElementListener` query is required (open question — default to `addElementListener` for consistency with Task 14's own pattern if `@Listen()` doesn't work).
- Day click updates **only** `this.draft` (via `selectDay`) — does not touch `this.value`, does not emit `bdsChange`/`valueChange`, does not close the popover (ADR-0005: draft-until-Apply).
- Listens to `bdsMonthNavigate` and updates `displayYear`/`displayMonth` accordingly, re-rendering the grid for the new month.

**Note:** Unit tests for this task's behavior (draft-only day selection, month-nav display updates, draft reset on reopen) are covered in the consolidated Task 20 (Phase 1 unit tests), not written here.

**Manual test (required):**

- Scenario 1: no initial `value`; open the popover, click a day, confirm the trigger field's text does _not_ change yet.
- Scenario 2: initial `value` (e.g. `2026-08-12`); open the popover, confirm that day is pre-highlighted and the display month matches.
- Scenario 3: click a different day, close the popover (click outside) without applying, reopen — confirm the draft reverted to the original committed day.

Run: `pnpm dev:components` and validate:

- [ ] Given no initial value, when a day is clicked inside the calendar, then the trigger field's text is unchanged and no `bdsChange` fires. Pass: trigger text static, no event.
- [ ] Given an initial value, when the popover opens, then the matching day is pre-selected and the calendar shows the correct month. Pass: correct day highlighted.
- [ ] Given an abandoned day click, when the popover is closed without Apply and reopened, then the original committed day is shown selected again. Pass: draft reverted.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add draft state and calendar grid wiring"
```

---

### Task 16: `bds-date-picker` footer (Clean/Cancel/Apply)

**Status:** ✅ done — `helpers/renderFooter.tsx` created (3 `bds-button`s slotted `slot="footer-button"`, single `onAction` handler keyed by `FooterAction`, `labels` prop with `Clear`/`Cancel`/`Apply` English defaults — checked `bds-select.tsx`/`bds-text-field.tsx` first, confirmed neither has any existing i18n/labels convention to follow, so implemented the plan's own specified shape). `bds-date-picker.tsx` modified: new `@Prop() labels?`, `commitValue()` helper (sets `value`, emits `bdsChange`/`valueChange`), `handleFooterAction()` switch on `FOOTER_ACTION` (Apply commits + closes; Cancel resets draft via `resetDraft` + closes, no event; Clean resets draft empty + commits `''` + closes — closing on Clean was a judgment call, kept symmetric with Apply/Cancel since an open popover showing a just-cleared draft would be a confusing intermediate state). `utils/value-mapping.ts` gained `formatValueForDisplay` (the only place calling `date-engine`'s `formatDisplayDate` directly, mirroring the existing single-touchpoint convention) — wired into `render()`'s `bds-text-field value=...` binding since Scenario 1's "trigger shows the newly formatted date" couldn't otherwise be verified; flagged for Task 18 to audit/confirm rather than re-implement. All verification clean (`tsc` normal + package-scoped `--strictNullChecks`, `eslint` — the previously-noted self-resolving `strict-mutable` warning on `value` is now gone, confirmed, since `commitValue` finally assigns it). All 3 manual-test scenarios independently verified live via Playwright with concrete evidence (`value`/trigger-text/popover-visibility/event-detail for each of Apply/Cancel/Clean), plus `disabled` gating confirmed on all 3 footer buttons.
**Second confirmed bug found and fixed in this task (2026-08-18), caught by the user questioning an "informational, not a defect" note the implementing subagent had dismissed too quickly:** the subagent's own report flagged, as a footnote, that `bds-date-picker`'s `valueChange` event shares its name with `bds-text-field`'s internal `valueChange` (also emitted whenever `bds-text-field`'s own `value` prop changes, via its `@Watch('value')` at `bds-text-field.tsx:253-259`) — and dismissed it as "pre-existing... did not affect the component's own correctness." This was investigated further and found to be a **real, confirmed bug**, not just informational:

- `bds-text-field.tsx`'s `valueChange` is a default Stencil `@Event()` (bubbles: true, composed: true) — since `bds-text-field` is a light-DOM descendant of `bds-date-picker`, this event bubbles straight through `bds-date-picker`'s own host, colliding with `bds-date-picker.tsx`'s own explicit `this.valueChange.emit(this.value)` in `commitValue()`.
- **Existing precedent already solves this for `bds-select.tsx`**, composing the same `bds-text-field` the same way: `addElementListener(this.bdsField, 'valueChange', this.stopFieldValueChange)` + `private stopFieldValueChange = (event: Event) => event.stopPropagation();` — `bds-date-picker.tsx` had no equivalent guard.
- **Confirmed live via Playwright** (attaching a listener directly on the `bds-date-picker` host): one Apply click fired **two** `valueChange` events with two _different_ `detail` values — `"2026-08-19"` (bds-date-picker's own, naive ISO) and `"2026/08/19"` (bds-text-field's bubbled event, the locale-formatted display string). Same double-fire on Clean. `bdsChange` was unaffected (`bds-text-field`'s own `bdsChange` isn't wired to its value-watch, only to its blur handler, which never fires here) — an asymmetric bug, not a symmetric one. Same risk class as the previously-filed `EOA-10544-bds-select-bug-001.md` (`valueChange`/`bdsChange` firing twice with inconsistent `detail` values) — a naive consumer could bind the wrong (formatted-display) value as "the value."
- **Fix applied**: ported `bds-select.tsx`'s exact pattern — added `stopFieldValueChange` and wired it via `addElementListener`/`removeElementListener` in `componentDidLoad()`/`disconnectedCallback()`, alongside the existing `click` listener. Re-verified live: exactly one `valueChange` now fires on the host per Apply/Clean, with the correct naive-ISO detail; `bds-text-field`'s own `valueChange` still fires locally (confirmed by listening directly on the text-field element) — `stopPropagation()` only stops it from bubbling further, it doesn't suppress the event itself.
  **Process note:** a subagent's own "found but dismissed as informational" note should be treated as a lead worth independently verifying, not accepted at face value — this one turned out to be a real, previously-precedented bug class in this exact codebase.
  **Housekeeping (2026-08-18):** a `stencil build --docs` run during this task's own verification step unintentionally generated `readme.md` files across nearly every component in the codebase (Stencil's `--docs` CLI flag enables the `docs-readme` output target project-wide, even though `stencil.config.ts` doesn't declare it) — none of this plan's tasks call for README generation. Cleaned up: all newly-created `readme.md` files removed, the one pre-existing file it overwrote (`bds-typography/readme.md`) reverted via `git checkout`, and a stray `.playwright-cli/` debug-log directory (leftover Playwright session logs, untracked, unrelated to any task) removed.
  **Constants extraction (2026-08-18, user request):** `DEFAULT_FOOTER_LABELS` moved out of `renderFooter.tsx` into a new `utils/constants.ts`, matching `bds-table/utils/constants.ts`'s exact pattern (re-exported via `utils/index.ts`'s barrel). An initial attempt also extracted `format`'s default (`'yyyy/MM/dd'`) as `DEFAULT_DATE_FORMAT` and referenced it in the `@Prop()` initializer (`format: string = DEFAULT_DATE_FORMAT`) — **reverted**, since this violates `ai-docs/guidelines/stencil-best-practices.md`'s "`@Prop()` Type Declaration and Default Value Rules" (§"Always use string literals as default values — never constant or enum references"): Stencil's static analysis records the bare identifier in `custom-elements.json`/Storybook ArgTypes instead of the literal value, leaking an internal implementation detail. Reverted `format`'s default back to the literal `'yyyy/MM/dd'` and removed `DEFAULT_DATE_FORMAT` from `constants.ts` entirely, since it had no other use besides that `@Prop()` initializer (the guideline's "constants may still be used inside logic — just never as the `@Prop()` initializer" carve-out didn't apply here, unlike `DEFAULT_FOOTER_LABELS`, which is only ever read inside `renderFooter`'s own merge logic, never as a `@Prop()` default).
  **Architecture correction (2026-08-19) — reopened, see the "Architecture Correction" section after this task for full rationale:** the declarative `value={formatValueForDisplay(...)}` binding on the (now-removed) internal `<bds-text-field>` is replaced with an imperative push against the consumer's slotted field via a shared `private syncFieldValue = () => updateElementProp(this.bdsField, 'value', formatValueForDisplay(this.value, this.format, this.locale))` helper, called from exactly two places: `componentDidLoad()` (initial `value`, since `@Watch()` doesn't fire for the value already present at mount) and a single new `@Watch('value')` handler (covers every subsequent change — internal Apply/Clean via `commitValue()`'s `this.value = nextValue` reassignment, or a consumer directly mutating `value` externally — the previous declarative binding got this "for free" via re-render, an imperative push does not). Deliberately **not** an explicit push inside `handleFooterAction`'s `APPLY`/`CLEAN` branches — `commitValue()` already reassigns `this.value`, which `@Watch('value')` catches automatically, so an additional explicit push there would have been a redundant double-push. **Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Live Playwright verification confirmed all 5 cases: initial mount reflects the formatted `value`; Apply/Clean/Cancel all correctly update (or correctly don't update, for Cancel) the field's displayed value; an external `value` mutation (not via Apply/Clean) is also correctly reflected via the watch.
  **Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
  **Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/helpers/renderFooter.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Footer renders three `bds-button`s slotted into `bds-popover`'s existing `footer-button` slot region.
- Button text is not hardcoded — expose via a `labels` prop object (`{ clean?: string; cancel?: string; apply?: string }` with English defaults `'Clear' | 'Cancel' | 'Apply'`) unless checking `bds-select`/`bds-text-field` reveals an existing i18n convention to follow instead (open question — check first).
- **Apply**: commits `this.draft.selectedDate` into `this.value` (naive ISO via `value-mapping.ts`), emits `bdsChange`/`valueChange`, updates the text field's displayed formatted text, closes the popover.
- **Cancel**: discards `this.draft`, resets it to the last committed `this.value`, closes the popover, does **not** emit any event.
- **Clean**: resets the draft to empty **and commits immediately** — clears `this.value`, emits `bdsChange`/`valueChange` with `''` (confirmed behavior, no longer an open question).
- All three buttons are keyboard-operable (native `bds-button` semantics) and disabled together with the whole component when `this.disabled` is true.

**Note:** Unit tests for this task's behavior (Apply/Cancel/Clean commit and event semantics, labels override) are covered in the consolidated Task 20 (Phase 1 unit tests), not written here.

**Manual test (required):**

- Scenario 1: no value; open, pick a day, click Apply; confirm trigger text updates to the formatted date and popover closes.
- Scenario 2: a committed value; open, pick a different day, click Cancel; confirm trigger text unchanged and popover closes.
- Scenario 3: a committed value; open, click Clean; confirm trigger text clears immediately.

Run: `pnpm dev:components` and validate:

- [ ] Given a fresh pick + Apply, when Apply is clicked, then the trigger shows the newly formatted date and the popover closes. Pass: visible text update + closed popover.
- [ ] Given a pick + Cancel, when Cancel is clicked, then the trigger's previously committed text is unchanged. Pass: no visible change.
- [ ] Given Clean on a populated field, when Clean is clicked, then the trigger clears immediately. Pass: empty trigger text.
- [ ] Given the browser console open (`index.html`'s Task 16 section logs `bdsChange`/`valueChange` counts and detail per event on each of the 3 scenario elements), when Apply or Clean is clicked, then each event name logs **exactly once**, with the naive-ISO detail (e.g. `"2026-08-19"`), never twice and never with a formatted display string (e.g. `"2026/08/19"`) as a second, separate event. Pass: one log line per event name per click — validates the `bds-text-field` internal `valueChange`-bubbling fix (see this task's status note) stays fixed; a second `valueChange` log would mean the regression returned.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add Clean/Cancel/Apply footer actions"
```

---

### Architecture Correction (2026-08-19): consumer-supplied trigger field

**What changed:** `bds-date-picker` (Tasks 13/14/16) originally rendered its own internal `<bds-text-field slot="field">`, owning 100% of its configuration. This made it impossible for a consumer to set `label`/`sublabel`/`icon`/`helperText`/`placeholder`/`info`/`errorMessage`/`variant`/`customWidth` — none of these were exposed as `bds-date-picker` props, and the internal field was fixed/uncustomizable. Caught by the user asking how non-`bds-date-picker` `bds-text-field` props could be passed through.

**Investigation:** `bds-select.tsx` was read in full to check how it solves the identical problem (it also composes `bds-text-field`/`bds-tag-field` as a trigger). Confirmed:

- `bds-select` never renders its own `<bds-text-field>` — it renders `<slot name="field"></slot>` (line 781) and the **consumer** slots in their own, fully-configured `<bds-text-field label="..." helper-text="..." ... slot="field">` as a light-DOM child (verified against every example in `bds-select.stories.ts`).
- `bds-select` pushes only the few props it must control **imperatively**, via `updateElementProp(this.bdsField, ...)` directly onto the consumer's own field instance — never declaratively through its own render: `value` (computed display text, line 492), `iconRight` (chevron, line 125/425), `clearable`/`entryMode`/`selectable` (line 419-423).
- Everything cosmetic (`label`, `sublabel`, `icon`, `helperText`, `placeholder`, `info`, `errorMessage`, `customWidth`, `pattern`, `autocomplete`, `minLength`/`maxLength`, `type`, `variant`) is entirely the consumer's own concern — `bds-select` doesn't even re-declare `disabled` on itself (no `this.disabled` anywhere in `bds-select.tsx`); the consumer sets `disabled` directly on their own slotted field.
- `bds-select` isn't `formAssociated`/FACE at all — it uses a plain `<input type="hidden" name={this.name} value={...}>` (lines 784-789), an older/simpler mechanism than Task 17's planned `ElementInternals`-based FACE. This distinction matters: `bds-date-picker`'s FACE participation (Task 17) is independent of the trigger-field composition question — they don't have to match `bds-select`'s hidden-input approach just because the slot-composition pattern is being adopted.
- **Mechanically confirmed viable**: `<slot name="field">` works in this project's light-DOM (no Shadow DOM) components because `stencil.config.ts`'s `extras.experimentalSlotFixes`/`experimentalScopedSlotChanges` are already enabled project-wide — this is precisely what makes `bds-select`'s identical pattern function today.
- Cross-checked against the spike doc's Figma Code Connect pull (`_DatePickerField` node): the design genuinely expects `label`, `icon` (`prefixIcon`), `helperText` on the trigger field — confirming this is a real design requirement, not hypothetical.

**Decision: adopt `bds-select`'s exact pattern (full prop inventory and two rejected alternatives — passthrough props on `bds-date-picker` itself, or no change — discussed and decided against in this session's conversation, not reproduced here).** `bds-date-picker` stops rendering its own `<bds-text-field>`; the consumer must now slot in their own, exactly as every `bds-select` story does.

**Tasks affected — each reopened with its own correction note below, or acceptance criteria updated in place for not-yet-started tasks:**

- **Task 13** (done, reopened): `render()` changes from self-rendering `<bds-text-field slot="field" .../>` to `<slot name="field"></slot>`; add `@slot field` JSDoc on the class (matching `bds-select`'s own annotation).
- **Task 14** (done, reopened): `bdsField` getter is mechanically unaffected (`el.querySelector('bds-text-field')` finds the consumer's slotted child the same way). New: a runtime validation warning if no compatible field is slotted (mirroring `bds-select`'s `"Multiselect=true requires <bds-tag-field>..."` pattern). New: `bds-date-picker` pushes `selectable={true}` **and** `disabled` onto the consumer's field imperatively via `updateElementProp` — `disabled` sync decided in favor of syncing (not left purely to the consumer, unlike `bds-select`'s precedent) since `bds-date-picker` already has good independent reasons to keep its own `disabled` (FACE, Task 17), so a consumer shouldn't need to duplicate it in two places.
- **Task 15**: unaffected, no changes — calendar wiring has no field dependency.
- **Task 16** (done, reopened): the declarative `value={formatValueForDisplay(...)}` binding (targeting the now-removed internal field) is replaced with an imperative push via a shared `syncFieldValue` helper, called from `componentDidLoad()` (initial value) and a single `@Watch('value')` handler (covers Apply/Clean and any external `value` mutation alike) — not three separate call sites, to avoid a redundant double-push when `commitValue()`'s own `this.value` reassignment already triggers the watch.
- **Task 17**: no functional change, clarifying note only — `bds-date-picker` keeps its own `disabled`/`required`/`name`/`value` for FACE purposes (Task 17's `ElementInternals`), independent of whatever the slotted field is.
- **Task 18**: acceptance criteria updated — final `render()` exposes `<slot name="field">` (not a self-rendered `bds-text-field`), audits the runtime validation warning and the imperative `value`/`selectable`/`disabled` sync from Tasks 14/16, and the `@slot field` JSDoc. The pre-existing "hidden `<input type="hidden">` matching `bds-select`'s pattern" criterion is **removed** — it conflicts with Task 17's actual `ElementInternals`-based FACE (which doesn't need a hidden input; `bds-select` only uses one because it isn't FACE at all).
- **Task 19**: one open question resolved/removed — "decide whether `bds-text-field`'s built-in label region or a `bds-date-picker`-owned label renders" is now moot, since the consumer's own slotted field always supplies its own label. Otherwise unaffected (SCSS still targets the same DOM structure regardless of who authored the slotted markup).
- **Task 20**: new test requirements — every spec's `newSpecPage` HTML fixture must include a slotted `<bds-text-field slot="field">` child (matching `bds-select`'s own spec-setup convention); new tests for the missing-field warning and the imperative `value`/`selectable`/`disabled` sync (including after Apply/Clean and after an external `value` mutation).
- **Task 21**: Storybook stories must show the composed pattern (`<bds-date-picker><bds-text-field label="..." slot="field"></bds-text-field></bds-date-picker>`), matching `bds-select.stories.ts`'s exact structure, not a bare `<bds-date-picker>`; MDX documents that the consumer supplies and fully configures the trigger field.
- **Spike doc**: "Target light-DOM structure" section's example updated from self-rendered to consumer-supplied composition; new Resolved Decisions table row added.
- **`index.html` playground**: all ~10 existing Task 13-16 scenario elements need their markup updated to wrap a slotted `<bds-text-field slot="field">` child — implementation work, done when each task is reopened.

**Commit (single, consolidated — 2026-08-19 user direction):** this correction spans three already-completed tasks (13, 14, 16) plus `index.html`; it lands as **one commit**, not one per reopened task. **Done** — committed as `7e126c1c`:

```bash
git commit -m "fix(web-components): EOA-16692 use consumer-supplied slot for bds-date-picker trigger field"
```

(Shortened from the originally-drafted message — the first attempt, `"...compose bds-date-picker's trigger field via a consumer-supplied slot instead of self-rendering bds-text-field"`, failed `commitlint`'s `header-max-length` rule at 140 characters against a 100-character limit; re-drafted to 91 characters, same meaning.)

Covers: `render()`'s `<slot name="field">` (Task 13 rework), the missing-field validation warning and imperative `selectable`/`disabled` sync (Task 14 rework), the imperative `value` push via `@Watch('value')` (Task 16 rework). `index.html`'s scenario updates are **not** part of this commit — only `bds-date-picker.tsx` was staged/committed, per this plan's established convention that `index.html` playground changes are never committed. Each reworked task's own draft commit message recorded in its status note above (e.g. "fix(web-components): EOA-16692 render consumer-supplied trigger field...") described what changed at the dispatch level for traceability, but was superseded by this single consolidated commit for the actual `git commit`.

**Final QA (2026-08-19):** a full regression pass re-verified every one of Tasks 13-16's original manual-test scenarios under the new slotted composition (9 scenarios across `disabled`/`hideArrow`/draft-state/footer-action behavior) plus the Architecture Correction's own new scenarios (missing-field warning, `selectable`/`disabled`/`value` sync) — zero regressions, zero unexpected console errors/warnings (89 total console messages: 0 errors, 43 warnings, all accounted for as pre-existing unrelated `bds-button` accessible-name warnings plus exactly the one expected missing-field warning). `tsc`/`eslint`/build all clean.

---

### Task 17: `bds-date-picker` FACE wiring

**Status:** ✅ done — `formAssociated: true` added; class extends `Mixin(formAssociatedMixin)`, implements `IDatePicker, IFormControl<string>`; `@AttachInternals() internals!: ElementInternals` on the class body (per the FACE guideline's placement rule). **Resolved the open question**: `useFormField` (the full text-input-shaped validator pipeline requiring `focused`/`touched`/`dirty`/`bdsFocus`/`bdsBlur`/`customValidators`/`bdsValidationChange`) was rejected as a mismatch — `bds-date-picker` has no keystroke-level interaction (its "input" is a calendar click + Apply) and only one validation rule (`required` + empty `value`). Went with a lightweight, direct `ElementInternals.setValidity()` approach instead, in the spirit of `useFormCheckbox`'s purpose-built pattern for non-typed-input FACE components — a private `validators` getter (single `valueMissing` rule) + `runValidators()` (an existing, already-generic, standalone helper independent of `useFormField`). The existing `@Watch('value')` handler (from the Architecture Correction) was extended in place — not duplicated as a second watcher — to also call `setFormValue(this.internals, next)` and `this.updateValidity()` alongside its existing `syncFieldValue()` call. `formResetCallback` resets `value` to `''`, resets the draft via `resetDraft('')`, and calls `setFormValue(this.internals, null)`. `checkValidity()`/`reportValidity()` `@Method()` wrappers added (native FACE prototype members are blocked by Stencil's element proxy per the guideline — required for external/test access).
**Bug found and fixed, flagged as a deviation from "leave `name` as-is unless conflict":** `name` was `@Prop() readonly name: string = ''` (no `reflect: true`). Confirmed this would have **silently broken FormData participation** — a form-associated custom element's `FormData` entry key comes from the browser reading the host's `name` _content attribute_ directly, not from any JS property; without `reflect: true`, the attribute would never be set, and the picked date would never appear in `FormData` under the right key despite `setFormValue()` correctly wiring the _value_. Changed to `@Prop({ reflect: true }) readonly name`. Confirmed working via the live Playwright FormData test.
**Known gap, flagged for Task 18 (not fixed here, out of this task's bounded scope):** `formAssociatedMixin` expects each component to declare `@State() private isDisabled`/`@Watch('disabled') onDisabledChange` so its `formDisabledCallback` (triggered by an ancestor `<fieldset disabled>`, not by the `disabled` prop) has something to write to and `render()` to react to. `bds-date-picker` doesn't have this — adding an inert `isDisabled` field would fail `noUnusedLocals`, and wiring it into visible behavior requires touching `render()`, which this task's dispatch explicitly protected (Task 18 owns the final render tree). Net effect: today, a `<fieldset disabled>` ancestor has no visible effect on `bds-date-picker` (author-set `disabled` via the prop already works correctly, unaffected). Task 18 should decide whether to add this.
**Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Live Playwright verification confirmed: FormData contains the correct `name`/naive-ISO-`value` pair after Apply + Submit; form reset clears both `value` and the slotted field's displayed text; `required` + empty `value` correctly fails `reportValidity()`, and passes after a date is picked and applied.
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Adds `formAssociated: true` to `@Component()`.
- Class extends `Mixin(formAssociatedMixin)` and implements `IFormControl<string>`, matching `bds-text-field.tsx` — **unless** checking `src/mixins/form-associated.mixin.ts` and `src/utils/form/` at implementation time reveals `useFormField` has become the canonical pattern in more recently built form components (check via `git log` on a newer form component like `bds-tag-field.tsx`), in which case use that instead (open question — determine before wiring, don't assume `bds-text-field.tsx`'s pattern is still current).
- Adds `@AttachInternals() internals!: ElementInternals`.
- Adds `@Watch('value') watchValue(next) { setFormValue(this.internals, next); }` (or the `useFormField`-equivalent, whichever pattern is chosen).
- `formResetCallback` resets `value` to `''` and also resets the internal draft.
- **Note (added 2026-08-19, Architecture Correction):** `disabled`/`required`/`name`/`value` stay as `bds-date-picker`'s own props for FACE purposes here — independent of whatever `bds-text-field` the consumer slots in via `slot="field"`. The slotted field is a visual/cosmetic trigger only (`selectable`, non-typable); it has no FACE participation of its own that matters to `bds-date-picker`'s form submission.

**Note:** Unit tests for this task's behavior (`FormData` participation, `formResetCallback`, required-field validity) are covered in the consolidated Task 20 (Phase 1 unit tests), not written here.

**Manual test (required):**

- Scenario: wrap a `<bds-date-picker name="appointment-date">` inside a `<form>` with a submit button in `index.html`; log `FormData` on submit.

Run: `pnpm dev:components` and validate:

- [ ] Given a date picked and applied inside a form, when the form is submitted, then `FormData` contains the correct `appointment-date` entry. Pass: logged FormData shows the expected value.
- [ ] Given a form reset, when reset is triggered, then the date picker's trigger text clears. Pass: visible reset.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add form-associated (FACE) support"
```

---

### Task 18: `bds-date-picker` full render + JSDoc audit

**Status:** ✅ done — `render()` audited and confirmed correct (`<slot name="field">`, `renderCalendarPanel`/`renderFooter` composition, no hidden input needed — Task 17's FACE handles form participation). Tasks 14/16's imperative sync (missing-field warning, `selectable`/`value` pushes) audited and confirmed correct, no changes needed. **Resolved Task 17's flagged `isDisabled` gap**, mirroring `bds-text-field.tsx`'s exact pattern: added `@State() private isDisabled`, `componentWillLoad()` seeding it from `disabled`, extended the existing `@Watch('disabled')` to also set it, switched `render()`'s `bds-popover`/`renderFooter` `disabled` bindings and the imperative field push to use `this.isDisabled` instead of the raw `disabled` prop. **Added one method beyond the literal bullet list** (flagged, not silently done): overrode `formDisabledCallback` to also imperatively push `disabled` onto the slotted field via `updateElementProp` — the mixin's default `formDisabledCallback` only sets the Stencil `@State() isDisabled`, which the slotted field (living in the default `<slot>`, outside Stencil's own render tree) never observes on its own; without this override, a `<fieldset disabled>` ancestor would correctly gray out the popover/footer but leave the slotted trigger field itself clickable — verified this really was needed via Playwright (see below). JSDoc audit: added a real class-level descriptive paragraph (draft-until-Apply semantics, explicit `value`/`format` decoupling contract — previously missing, only the `@slot field` line existed), extended `@slot field`'s wording to mention the console warning and the auto-managed `selectable`/`disabled`/`value` props, tightened `value`/`format`/`disabled` prop comments for accuracy; all other `@Prop`/`@Event` comments (`locale`, `timezone`, `hideArrow`, `name`, `required`, `labels`, `bdsChange`, `valueChange`) were already accurate, left untouched.
**Class-level JSDoc shortened (2026-08-19, user request):** the class-level block (18 lines: two multi-line paragraphs + a 4-line `@slot` description) was flagged as too long relative to this codebase's convention. Reference: `bds-table.tsx`'s own class doc is 2 lines (one "what it is" sentence, one detail sentence) followed by one-line `@slot` tags. Rewritten to match that density: one sentence describing the composition + draft-until-Apply behavior, one sentence for the `value`/`format` contract, one `@slot field` line — 5 lines total. Also corrected the phrasing: the original said "form-associated" (FACE-spec jargon, not used anywhere else in this codebase's class docs); checked `bds-text-field.tsx`/`bds-tag-field.tsx`'s own class docs, both instead use the plain-English phrase "form integration" woven into the single descriptive sentence — matched that exact precedent rather than inventing new phrasing. Verified: `tsc --noEmit` and `eslint` both clean, no functional change (docs-only).
**Verified:** `tsc --noEmit` (normal + package-scoped `--strictNullChecks`) and `eslint` both clean; Stencil build succeeds. Live Playwright verification: a `<fieldset disabled>` ancestor (with `bds-date-picker`'s own `disabled` prop never explicitly set) correctly disabled the slotted field's own `disabled` attribute, the popover, and all 3 footer buttons — confirming the `formDisabledCallback` override actually closes the gap it was added for. Regression-checked the `disabled` prop set directly (unaffected, still works) and the Task 16 Apply flow (unaffected). A consolidated end-to-end scenario (custom `format`+`hideArrow`+form participation) confirmed `value`/`format` decoupling directly (`value="2026-08-18"` while the field displayed `18/08/2026` under a custom `dd/MM/yyyy` format) and correct `FormData` naive-ISO submission.
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Final `render()` exposes `<slot name="field"></slot>` (the consumer's own `<bds-text-field slot="field">`, per the 2026-08-19 Architecture Correction — not a self-rendered `bds-text-field`), `bds-popover` (with `renderCalendarPanel` body + `renderFooter` footer). No hidden `<input type="hidden">` — **removed** from this criterion (2026-08-19): it conflicted with Task 17's actual `ElementInternals`-based FACE, which doesn't need a hidden input; `bds-select`'s hidden-input pattern only exists because `bds-select` isn't FACE at all.
- Audits Task 14's runtime validation warning (missing slotted field) and Tasks 14/16's imperative `value`/`selectable`/`disabled` sync onto the consumer's field — confirm, don't re-implement.
- Every `@Prop`, `@Event`, and the class-level component JSDoc block (including `@slot field` — the consumer-supplied trigger field, per the Architecture Correction — and any other custom slots, e.g. a `labels` override) are complete.
- Component-level JSDoc explicitly states the `value` contract (naive ISO date, decoupled from `format`).

**Manual test (required):**
Consolidate all prior scenarios into one end-to-end walkthrough in `index.html` covering: default render, custom `format`, custom `locale`, `hideArrow` toggle, disabled state, form participation.

Run: `pnpm dev:components` and validate:

- [ ] Given the consolidated scenario, when each sub-case is exercised in sequence, then all previously-validated behaviors (Tasks 14-17) still pass together without regression. Pass: full walkthrough succeeds.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 finalize render tree and JSDoc"
```

---

### Slotted Field Props Compatibility Audit (2026-08-19)

**What happened:** after the Architecture Correction (consumer-supplied trigger field) and the `validation-timing="submit"` day-click bug fix, a systematic audit was run across every `bds-text-field` prop to identify which ones, when set by a consumer on the slotted field, risk a real functional bug (not just a cosmetic non-sequitur) when composed with `bds-date-picker`. Live-verified via Playwright, not theorized.

**Root cause context:** `bds-date-picker` manages the slotted field **imperatively** via `updateElementProp()` for exactly three props — `selectable`, `disabled`, `value` (`componentDidLoad`/watchers). Every other `bds-text-field` prop is entirely the consumer's own responsibility, never touched, checked, or reconciled by `bds-date-picker`.

**3 confirmed genuine bugs, 4 confirmed safe:**

| Prop                                              | Risk                                                             | Confirmed root cause                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | --------------------------------------------------------------------------------------------------------------------------- |
| `clearable`/`clear-on-hover`                      | **High** — silent value/UI desync                                | Clicking the field's own clear button empties the _display_ only; `bds-date-picker`'s real `value` never changes (no event fires — `valueChange` bubbling is deliberately suppressed via `stopFieldValueChange`, and nothing wires the field's own `bdsClear`). Reopening the popover shows the old date still selected while the trigger looked empty moments before. |
| `name` on inner field                             | **Medium** — double `FormData` submission                        | Confirmed: submission produces two entries — the picker's own (naive ISO) and the inner field's own (formatted display string, e.g. `2026/08/20`) — silently, with mismatched formats.                                                                                                                                                                                 |
| `pattern`                                         | **Medium** — permanent, unfixable invalid state                  | `syncFieldValue()` always writes the `format`-shaped string; a `pattern` expecting a different shape (e.g. dashes vs. slashes) can never match, so the field is permanently invalid no matter what valid date is picked.                                                                                                                                               |
| `max-length`                                      | None — inert                                                     | Native `tooLong` validity only trips on user-driven edits exceeding maxlength, not on programmatic `value` assignment (how `updateElementProp` sets it).                                                                                                                                                                                                               |
| Initial `value` on the slotted field              | None — silently overwritten, but matches the documented contract | `syncFieldValue()` runs unconditionally in `componentDidLoad`; the JSDoc (`@slot field`, Task 18) already states the consumer must not set `value` themselves.                                                                                                                                                                                                         |
| `selectable="false"`                              | None — override race resolved correctly                          | `componentDidLoad`'s imperative push unconditionally wins every mount.                                                                                                                                                                                                                                                                                                 |
| `disabled="false"` (vs. picker `disabled="true"`) | None — override race resolved correctly                          | Same as above.                                                                                                                                                                                                                                                                                                                                                         |
| `readonly="false"`                                | None — safe, but completely inert                                | `bds-text-field`'s own `readOnly={this.readOnly                                                                                                                                                                                                                                                                                                                        |     | this.selectable}`—`selectable`is permanently forced`true`, so `readOnly`can never functionally be`false` once slotted here. |

**Decisions on the 3 confirmed bugs:**

1. **`clearable`/`clear-on-hover` — fix in code, not just documentation.** This is a genuine data-integrity bug (silent desync between what the trigger visually shows and what `bds-date-picker.value` actually holds), not a consumer-configuration gotcha. **Reopens Task 14** (which already owns the field-listener wiring in `componentDidLoad`/`disconnectedCallback`): add `addElementListener(this.bdsField, 'bdsClear', this.handleFieldClear)` (and matching `removeElementListener` in `disconnectedCallback`), where `handleFieldClear` mirrors the footer's Clean action exactly (`commitValue('')`, reset the draft, close the popover if open).
2. **`name` on inner field — document as a required constraint + add a runtime warning.** Mirrors Task 14's existing missing-field `Logger.warn` pattern: if the slotted field has a non-empty `name`, warn that this causes double-submission with a differently-formatted value. **Also reopens Task 14** (same `componentDidLoad` warning-check location as the missing-field warning).
3. **`pattern` — document only, no code fix possible.** There's no safe way for `bds-date-picker` to know what pattern would match its own `format` output dynamically. **Assigned to Task 21** (documentation) as a required "do not set" constraint in the MDX, alongside the existing `validation-timing="submit"` requirement.

**Commit (single, for the two Task 14 code fixes — `bdsClear` wiring + `name` warning):**

```bash
git commit -m "fix(web-components): EOA-16692 wire slotted field's clear button and warn on inner name prop"
```

---

### Task 19: `bds-date-picker` SCSS

**Status:** ✅ done — `bds-date-picker.scss` created (host `display: block; width: 100%`), Figma research pass fully recorded (all 5 rows above), and `<bds-popover>` given a fixed `width={296}` (in `bds-date-picker.tsx`) to match the confirmed 296px panel.

Rather than reaching into `bds-popover`'s internally-rendered `.popover-header`/`.popover-content`/`.popover-footer` divs with plain selectors (fragile — those elements aren't ones `bds-date-picker` itself renders), `bds-popover.scss` gained four new documented CSS custom-property hooks — `--popover-header-padding`, `--popover-header-content-gap`, `--popover-content-padding`, `--popover-footer-padding` — each defaulting to its pre-existing hardcoded value (non-breaking for `bds-select`/`bds-dropdown`/`bds-search-bar`, confirmed via QA), set per-instance from `bds-date-picker.scss`. The header title (`[slot="header-title"]`, 12px/16px/regular) is instead styled directly by `bds-date-picker.scss` targeting its own slotted element — no cross-component hook needed there, since `bds-date-picker` renders that element itself.

**Calendar-grid width bug found and fixed (reopens Task 10):** QA's first live check found the popover's calendar grid overflowing 8px past the panel's intended edge (256px rendered vs. the Figma-confirmed 248px), asymmetric (24px gap left, 16px right). Root cause: CSS `border-spacing` on `bds-calendar-grid`'s `<table>` (`border-collapse: separate`) adds a gap at _every_ boundary — 8 gaps for 7 columns — while Figma's flex-gap layout only gaps _between_ cells (6 gaps). Fixed in `bds-calendar-grid.scss`: `margin: 0 calc(-1 * #{$boreal-spatial-gap-2xs})` on the `table` cancels one edge-gap per side without touching cell size; `.bds-calendar-grid__header`'s width updated to match (`$grid-visual-width`, a new derived constant). Re-verified flush/symmetric (24px both sides) in Chromium and WebKit.

**Close-button sizing — false start, reverted, then a real fix landed:** a review pass asked for the header's close button at 16×16px. Implemented via `--bds-button-width`/`-height`/`-min-height` overrides (new hooks added to `bds-button.scss`, mirroring its existing `--bds-button-min-height`/`--bds-button-radius` precedent) — but 16px is below `bds-button`'s smallest built-in floor (`size="sm"` = 24px natural, 14px icon), so internal padding/icon-centering math (computed in SCSS against the natural size) didn't scale down: QA found the icon off-center and hover/focus box-shadow rings disproportionately large (~50% footprint increase vs. ~12% at natural size). **Decision: reverted to natural sizing** rather than investing in a fully-responsive `bds-button` sizing architecture — removed the override from `bds-date-picker.scss` and, since that was the hook's only consumer, removed the now-unused `--bds-button-width`/`-height` hooks from `bds-button.scss` and `bds-popover.scss` entirely (dead-code cleanup). This unmasked a separate, pre-existing `bds-popover.scss` bug: its own baseline close-button rule set `width`/`height: 20px` but never `min-height`, so `bds-button`'s `sm`-floor (24px) won via CSS's `max(height, min-height)`, rendering 20×24 instead of a 20×20 square — unrelated to anything from this session, just previously masked by the (now-reverted) override. Fixed with one line (`min-height: $boreal-spatial-spacing-ml;`) in `bds-popover.scss`. Final state verified via QA: exactly 20×20px, correct icon centering, proportionate hover/focus states, zero regression on footer/nav buttons — all confirmed in Chromium and WebKit across three QA dispatch rounds.

**Footer polish:** `renderFooter.tsx`'s buttons wrapper (`<div slot="footer-button">`) gained a `bds-date-picker__footer-buttons` class, styled in `bds-date-picker.scss` with `@extend %flex-center; gap: $boreal-spatial-gap-xs;` (8px) — additive only, doesn't collide with `.popover-footer`'s own `justify-content: space-between` (which has no `gap` of its own). Button variant/color values (previously left "illustrative" per the spike doc) were also resolved: Cancel gets `variant="outline"`, Apply gets `color="primary"`, Clean stays default — matching the confirmed Figma footer screenshot exactly. Spike doc and this task's own Figma-research-pass row updated to reflect this.

**Verification:** `tsc --noEmit`, `eslint`, and `stencil build` all clean throughout every round (only the same 5 pre-existing, unrelated `bds-dialog`/`bds-tooltip` test-file baseline errors, unchanged). Manual QA (live Playwright, Chromium + WebKit) independently confirmed: popover panel 296px exact width with correct header/content/footer padding; calendar grid flush/symmetric; close button 20×20 with correct icon centering and proportionate hover/focus; footer button spacing/variants correct; zero regression on `bds-select`/other `bds-popover` consumers' default padding; zero new console errors across every check.

**Files (beyond the one listed below):** `bds-popover.scss` (modify — new padding/gap custom-property hooks, close-button `min-height` fix), `bds-calendar-grid.scss` (modify — Task 10 reopened, border-spacing width fix), `renderFooter.tsx` (modify — footer-buttons class, button variant/color), `bds-date-picker.tsx` (modify — `width={296}` on `bds-popover`).

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.scss` (create)

**Process note (2026-08-15, added after Task 10's post-mortem):** Task 10 (`bds-calendar-grid` SCSS) was reopened twice after user-caught gaps because Figma states/dimensions were pulled reactively, one gap at a time, instead of researched fully up front — missing width alignment, missing weekday styling, entirely missing hover/focus/active states, a dead-CSS root-selector bug, wrong text color on a combo state, and a leaked native focus outline. This task carries more distinct visual regions than `bds-calendar-grid` ever did (trigger field, popover chrome, label, footer) plus an unresolved design question baked into its own acceptance criteria — do not repeat the reactive pattern here.

**Figma research pass (complete before writing any SCSS):**

Pull `get_design_context` / `get_metadata` for each row below directly — a row is done only when it was actually pulled, never when it was inferred from a sibling variant or an earlier partial pull.

- [x] **Region: trigger field** — confirmed via Code Connect: `_DatePickerField` maps directly to `bds-text-field.tsx`, full-width (`w-full`), 32px tall. **Resolved:** since the Architecture Correction makes the trigger entirely consumer-owned, this region needs **no new SCSS** in `bds-date-picker.scss` — nothing to build here beyond confirming there's no conflicting styling need.
- [x] **Region: popover panel — real dimensions/padding, `Basic`+`Range:off`** — pulled fresh via `get_metadata` on the `Container` node (`I1537:17221;14:23281;158:176502`), reading the real `x/y/width/height` of its `Header Basic Time picker`/`Basic Footer` sibling frames (dimensions are real tool data even though these specific siblings are the currently-inactive/hidden variant state; only their _content_ pull is unreliable, per the existing documented lesson). **Total container: 296×434px** (supersedes the stale "290×290px" note) — Header 296×48px; calendar body 296 wide (24px `spatial/padding/l` each side + 248px calendar) × 290 tall (12px `spatial/padding/s` top/bottom + 266px calendar); time-selector row (Task 26) at y=290, 48px tall; Footer 296×48px. Single calendar itself confirmed 248×266px directly from the visible `_DatePickerCalendar` instances in the same pull — matches `bds-calendar-grid`'s existing implementation/tokens exactly, no calendar-internal changes needed.
- [x] **Region: footer — exact spacing/alignment** — pulled the visible `Expanded Footer` node (`I1537:17221;14:23281;158:176548`) directly; its layout tokens are width-independent so they apply identically to the hidden `Basic Footer` sibling (same pattern already confirmed for the header row: `Header Basic Time picker` and `Header Expanded Time picker` are both 48px tall using the same padding tokens despite differing widths, 296px vs 712px). `padding: 8px 24px` (supersedes the stale "16px" note; vertical is `8px`, i.e. `(48px row - 32px button) / 2`, not a named `spatial/padding/*` token on this instance — literal px in the pulled Tailwind), buttons right-aligned (`justify-end`), 32px tall, **8px gap** between buttons. Screenshot confirmed the intended variant mapping: Clean = ghost/text (gray), Cancel = outline, Apply = solid blue. **Update (2026-08-19, post-research):** at the time this row was checked off, Task 16's `renderFooter.tsx` had not yet set any `variant`/`color` props on the three buttons (all rendered as unstyled default). This was closed out later the same day — `renderFooter.tsx` now sets `variant="outline"` on Cancel and `color="primary"` on Apply, matching this screenshot exactly; Clean is left at its default `variant`/`color` (ghost/text look), also matching. See the spike doc's "Target light-DOM structure" section for the corresponding resolution note.
- [x] **Region: popover header (added 2026-08-19)** — pulled via the same `get_design_context` call as the popover panel row, on the visible `Header Expanded Time picker` node (`I1537:17221;14:23281;158:176511`), whose padding/gap tokens apply identically to the hidden `Basic` sibling (same width-independent-token pattern as the footer row): `padding: 24px 24px` (`spatial/padding/l` both sides — this is the "Icon/Date" header, not a generic slot), vertical `16px` (`spatial/padding/m`), `12px` gap (`spatial/gap/s`) between the calendar-dots icon and the date/time text; both the leading icon and the trailing close icon are 16×16px. **Confirmed mismatch against `bds-popover`'s own default header padding** (`bds-popover.scss:33`: `$boreal-spatial-padding-m $boreal-spatial-padding-xs $boreal-spatial-padding-m $boreal-spatial-padding-s` → 16px top/bottom, 12px left, 8px right) — the default is asymmetric and narrower than this composition's Figma-specified 24px/24px/16px/16px. `bds-date-picker.scss` needs an override for its `bds-popover`'s header padding specifically (host-scoped selector targeting `bds-popover`'s header region, not a change to `bds-popover.scss` itself, which stays generic for other consumers).
- [x] **Dimensions: width alignment** — single-calendar body width (296px) = trigger field width (`w-full`) = header width = footer width; all four regions share the same 296px column. Confirmed, no discrepancy.

**Acceptance criteria:**

- Every row of the Figma research pass above is checked off, with the pulled value recorded, before the first SCSS line is written.
- Uses `$boreal-*` tokens exclusively, matching `bds-calendar-grid.scss`'s convention.
- **Resolved (2026-08-19, Architecture Correction — no longer an open question):** the label question ("`bds-text-field`'s built-in label region or a `bds-date-picker`-owned label") is moot — the consumer's own slotted `<bds-text-field>` always supplies its own `label` prop directly; there is no `bds-date-picker`-owned label to design or duplicate.
- Popover content sizing matches the Figma spec re-confirmed in the research pass above, translated to nearest `$boreal-spatial-*` tokens.
- Verified against the **compiled** CSS output, not just the SCSS source, per the Figma Research Gate for Styling Tasks.

**Manual test (required):**
Reuse the consolidated scenario from Task 18.

Run: `pnpm dev:components` and validate:

- [ ] Given the rendered component, when compared against the Figma spec, then label position, field styling, and popover sizing visually match within token tolerance. Pass: visual comparison confirmed.

**Commit:**

```bash
git commit -m "feat(bds-date-picker): EOA-16692 add SCSS styling"
```

---

### Task 20: `bds-date-picker` Phase 1 unit tests (consolidated)

**Status:** ✅ done — 6 spec files + shared `date-picker.test-utils.ts` created by `@testing-subagent` on `feature/EOA-16692_bds-date-picker-v1_tests_DG` (branched off v1_DG, to be merged back via its own PR). 97 tests (1 todo), 98.23% statement / 100% function / 87.75% branch coverage on `bds-date-picker.tsx` — the uncovered branches are structurally-unreachable `bdsPopover?`/`bdsField?` null-fallback paths, since `<bds-popover>` is unconditionally part of `render()`. Every `newSpecPage` fixture slots a `<bds-text-field slot="field">` per the Architecture Correction requirement.

**Two real bugs found and fixed during this task, both committed separately:**
1. **Apply committed an empty value with an untouched draft** — `handleFooterAction`'s `APPLY` case unconditionally called `commitValue(this.draft.selectedDate ?? '')`, so clicking Apply after only clicking an inert outside-month cell silently overwrote `value` with `''` and emitted `bdsChange`/`valueChange` — contradicting this task's own spec ("Apply with no draft selection... does not change value and does not emit"). Found via a QA smoke-check of the reorganized `index.html` (not by the test-writing itself), fixed on `v1_DG` directly, then merged into the tests branch.
2. **Enter/Space never opened the popover** — `bds-popover`'s own `KeyboardController` unconditionally no-ops when `managed={true}` (which `bds-date-picker` always sets), so only mouse click worked, contradicting the spike doc's "baseline keyboard operability ships in Phase 1" commitment. Found while writing `bds-date-picker.keyboard.spec.ts` (the subagent verified empirically rather than assuming the plan was correct). Fixed with a `keydown` listener on the slotted field mirroring the existing `click` listener — required a follow-up type fix (`(event: Event)` + internal cast, not `(event: KeyboardEvent)` directly) since `addElementListener`'s handler param is plain `EventListenerOrEventListenerObject` and this repo's `tsc` has `strictFunctionTypes` off, so the mismatch wasn't caught until checked explicitly with that flag — matches `bds-search-bar.tsx`'s existing convention for the same pattern.

**`index.html` also reorganized** (separate from Task 20's own scope, done first): from ~10 implementation-task-numbered sections down to 8 behavior-oriented sections mapped to `ai-work/qa/test-plans/EOA-16692-bds-date-picker-test-plan.md`'s `TC-*` IDs (a new test plan generated via `/qa-test-planner` in parallel, per this task's own upfront proposal). Dropped: a dead superseded stub, a `TEMPORARY` verification scenario, and 6 of 7 "Props Risk Audit" scratch scenarios (their findings now belong in Task 21's MDX as documented consumer constraints, not live playground scenarios).

**Commits** (on `feature/EOA-16692_bds-date-picker-v1_tests_DG`, PR description drafted separately): `24dd4754` (keyboard fix), `39fbb71f` (the 6 spec files + test-utils), `62fe95b6` (type fix for the keydown listener). The Apply-fix (`6c949389`) lives on `v1_DG` itself, merged into the tests branch via `bd5cfa8c`/`ef0e33d7`.

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.basics.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.events.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.form.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.variants.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts` (create)

**Acceptance criteria:**

- One consolidated task covering every behavior area introduced by Tasks 14–18 — per the Testing Phases policy, unit tests are never written inline in an implementation task.
- Coverage split matches the `bds-toggle`/`bds-tab-group` `__test__/` convention: each file owns a distinct concern, no duplicate assertions.
- **Architecture Correction (2026-08-19):** every spec's `newSpecPage` HTML fixture must include a slotted `<bds-text-field slot="field">` child (matching `bds-select`'s own spec-setup convention) — `bds-date-picker` no longer renders its own trigger field internally.

**Unit tests to cover** _(grouped by spec file)_:

- `basics` (Task 14's behavior): clicking the trigger field opens the popover; clicking outside (or Escape) closes it, reusing `bds-popover`'s own click-outside/escape behavior (assert the integration, not re-testing `bds-popover`'s internals); `disabled={true}` prevents the popover from opening on trigger click; `hideArrow={false}` (default) results in the popover's arrow element being present, `hideArrow={true}` results in no arrow.
- `basics` (Architecture Correction — new): a console warning fires when no `bds-text-field` is slotted; `selectable`/`disabled` are correctly pushed onto the slotted field via `updateElementProp`, including after `disabled` changes post-mount.
- `basics` (Task 14's 4th reopen — popover header, added 2026-08-19): the popover renders with `header={true}`/`closable={true}`; the header title shows `headerPlaceholder` when `draft.selectedDate` is `null` and `value` is `''`; the header title updates live to the formatted drafted date as `bdsDayClick` fires, before Apply; after an abandoned draft (reopen without Apply), the header reflects the last committed `value` (or the placeholder if `value` is still `''`), not the abandoned draft.
- `events` (Task 15's behavior): clicking a day in the calendar updates the visible "selected" state inside the popover but does **not** change the public `value` prop and does **not** emit `bdsChange`/`valueChange` — the single most important behavior in the component, needs an explicit, unambiguous test; clicking month-nav prev/next updates the displayed month/year without affecting the selected day or the draft; reopening the popover after a previous session (without Apply) resets the draft to the last **committed** value, not the abandoned draft.
- `events` (Task 16's behavior): Apply with a selected draft day commits `value`, emits exactly one `bdsChange` and one `valueChange` with the correct naive-ISO string, and closes the popover; Apply with no draft selection (opened and closed without picking a day) does not change `value` and does not emit; Cancel after a day click leaves `value` unchanged, emits no event, and closes the popover; Clean clears `value` to `''` and emits `bdsChange`/`valueChange` with `''`; labels prop/i18n mechanism override changes the rendered button text.
- `events` (Architecture Correction — new): the slotted field's own displayed `value` reflects `formatValueForDisplay(...)` after Apply/Clean and after an external `value` prop mutation (via the new `@Watch('value')`), not just after internal Apply/Clean.
- `form` (Task 17's behavior): component participates in a native `<form>`'s `FormData` with the correct `name`/`value` pair after Apply; `formResetCallback` (triggered by a form `reset`) clears both `value` and any open draft state; `required` + empty `value` produces the expected validity state (`ElementInternals.validity`), consistent with `bds-text-field`'s own required-field validity pattern.
- `variants`: custom `format` changes trigger display text without changing `value`; custom `locale` produces locale-correct month names in both the trigger text and the calendar header.
- `variants`: `disabled` disables the trigger, footer buttons, and prevents popover opening, all together.
- `keyboard`: Tab reaches the trigger field; Enter/Space opens the popover (via `bds-popover`'s own `KeyboardController` mechanism wired in Task 14 — assert the integration outcome). No arrow-key day-grid navigation tested (Phase 8).
- `a11y`: trigger field has correct `aria-haspopup`/`aria-expanded` reflecting popover visibility.
- `a11y`: footer buttons are reachable and labeled correctly for screen readers.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
Non-visual (test-only) task — validate via `pnpm --filter boreal-web-components test -- bds-date-picker` passing at ≥90% coverage (coverage-phase only; mutation testing deferred to Task 30).

**Commit:**

```bash
git commit -m "test(bds-date-picker): EOA-16692 add consolidated Phase 1 unit tests"
```

---

### Task 21: `bds-date-picker` Phase 1 documentation

**Status:** ✅ done — `bds-date-picker.stories.ts` (9 stories: `Default`, `PreselectedValue`, `CustomFormat`, `CustomLocale`, `HideArrow`, `Disabled`, `CustomFooterLabels`, `FormIntegration`, `FieldLevelRequiredPattern`) and `bds-date-picker.mdx` created, following `bds-select`'s story/MDX pair as the structural template. Every story composes `<bds-date-picker><bds-text-field slot="field">...</bds-text-field></bds-date-picker>` per the Architecture Correction — no bare `<bds-date-picker>` story exists. All 10 `@Prop()`s and both `@Event()`s have `argTypes` entries (verified via the Props/Events Completeness Check — component `.tsx` / `.stories.ts` `argTypes` / MDX all agree; the MDX `<ArgTypes of={BdsDatePickerStories} />` has no `include` filter, so nothing can silently drop). Event wiring follows the four-level pattern (`onBdsChange`/`onValueChange` typed callbacks → plain `argTypes` descriptions with no `action:` shorthand → `args: { onBdsChange: action('bdsChange'), ... }` → arrow-wrapped `@bdsChange=${e => args.onBdsChange?.(e.detail)}` template binding, matching the "standalone component" convention since `bds-date-picker` emits these directly, not by re-emitting a child's event).
**`locale` (non-primitive prop) handling:** `control: false` in `argTypes` (an object, not controllable via a Storybook widget) plus a dedicated `CustomLocale` story using a `docs.source.code` override (hoisted top-level const, `/* HTML */`-tagged) showing the consumer-facing `import { fr } from 'date-fns/locale'; el.locale = fr;` pattern — required per the source-snippet-override rule (non-reflected, non-primitive prop set via Lit property binding). The live render imports `fr` at the top of the `.stories.ts` module (bundled correctly by Vite) and binds `.locale=${fr}` directly; an earlier attempt using a raw inline `<script type="module">import('date-fns/locale')` inside the Lit template failed live with `Failed to resolve module specifier 'date-fns/locale'` (bare specifiers don't resolve in an unbundled browser-executed script tag) — caught via a live Playwright check against the running `dev:docs` server, not just a source review, and fixed before considering the task done.
**New devDependency:** `date-fns@^4.4.0` added to `apps/boreal-docs/package.json` (matching the version already pinned in `boreal-web-components`, confirmed current via the npm registry) — required for the `CustomLocale` story to genuinely import a real date-fns locale rather than only showing static, unexecuted example code. `pnpm install` run; lockfile updated. Left uncommitted per this session's instruction (user will commit manually).
**Verified:** `eslint` clean on both new files (`pnpm --filter @telesign/boreal-docs exec eslint`). Live-verified via `pnpm dev:docs` + Playwright (not just a diff review): the Properties panel renders all 10 props + 2 events as individual rows (spot-checked `hide-arrow`, `header-placeholder`, `labels`, `required`, `disabled`, `name`, `locale`, `onBdsChange`, `onValueChange` directly in the rendered table); the `Default` story's full end-to-end flow (open popover → click day 12 → Apply) correctly updates the trigger to `2026/08/12`, closes the popover, and fires exactly 2 actions (`bdsChange`/`valueChange`); the `CustomLocale` story renders genuine French month/weekday labels ("août 2026", "lun./mar./mer...") with the 12th pre-selected; `FormIntegration`, `Disabled`, `HideArrow`, `CustomFooterLabels`, `FieldLevelRequiredPattern`, `PreselectedValue`, `CustomFormat` all load with 0 console errors. One environment-only failure noted, not a real defect: the icon-font `@import` (`boreal-styles.css` from the S3 CDN) is blocked by CORS in this sandboxed browser session — the same pre-existing pattern already used by `bds-select.stories.ts`'s own `styles` const; does not reproduce in a normal networked browser and required no code change.
Note (raw `tsc --noEmit` on `apps/boreal-docs`): pre-existing, unrelated to this task — `tsconfig.json`'s `ignoreDeprecations: "6.0"` is rejected by the installed `typescript@5.9.3` (`TS5103: Invalid value for '--ignoreDeprecations'`) regardless of any file changed; confirmed by reproducing the identical error via `git stash` against the pre-Task-21 tree. The project's real type-checking path is Vite/Storybook's own build pipeline, not a standalone `tsc --noEmit` invocation — `eslint` plus the live `dev:docs` verification above are the checks that actually apply here.
**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (create)
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (create)

**Acceptance criteria:**

- Story/MDX registered under the `forms` category, following the `bds-select` story/MDX pair as the structural template.
- **Architecture Correction (2026-08-19):** every story composes `<bds-date-picker><bds-text-field label="..." slot="field"></bds-text-field></bds-date-picker>`, matching `bds-select.stories.ts`'s exact structure — never a bare `<bds-date-picker>` — since `bds-date-picker` no longer renders its own trigger field internally; the consumer supplies and fully configures it.
- MDX documents `bds-date-picker`'s full public API plus a dedicated internal-implementation-note section documenting `bds-calendar-grid`'s existence, props, and events as an internal note only — no separate `bds-calendar-grid.mdx`/story file (per the spike doc's resolved decision). The internal note also documents the out-of-month day-cell behavior (visually grayed via `text/disabled`, functionally inert — no click, not tab-focusable) alongside props/events.
- MDX explicitly documents the `@slot field` requirement — the consumer must slot a `<bds-text-field>` for the component to render/function, with the runtime warning behavior (Task 14) noted for the case where it's missing.
- Documents the `value` contract explicitly (naive `yyyy-MM-dd` ISO, decoupled from `format`) and the draft-until-Apply behavior including Clean's commit-immediately behavior.
- Includes working Storybook controls for `format`, `locale` (documented as accepting a raw date-fns `Locale` object, with an example import), `timezone`, `hideArrow`, `disabled`, `required`, `headerPlaceholder` (added 2026-08-19 — documents the popover header row: icon + live draft/committed date text + close button, and that the icon is hardcoded, not configurable).
- Follows `documentation-knowledge` skill conventions for action wiring and source-snippet overrides for non-primitive props (the `locale` prop, being an object, needs a source-snippet override).
- **New (2026-08-19, `bds-select` precedent investigation):** MDX documents an additional, complementary pattern for visual/native `required` feedback: consumers may _also_ set `required`/`error-message` directly on their own slotted `<bds-text-field>` (with **no `name`** on that inner field, so it never double-submits to `FormData`), exactly mirroring `bds-select.stories.ts`'s own convention (`<bds-select required><bds-text-field required slot="field">`, no `name` on the inner field). Confirmed via reading both `bds-select.tsx` and `bds-text-field.tsx`: `bds-select` has **no `required` prop of its own at all** — its consumers' "required" UX comes entirely from the slotted field's own independent FACE participation (its own `ElementInternals`, its own `required` validator, native browser red-outline/tooltip on submit). `bds-date-picker`'s own Task 17 FACE (`ElementInternals.setValidity()`, authoritative for the _real_ submitted value) and this field-level pattern (native browser UX on the _visual_ trigger) are complementary, not redundant — since `bds-date-picker` already pushes its formatted `value` onto the slotted field via `syncFieldValue()`, the field's own `required` check genuinely tracks "has a date been picked," matching `bds-select`'s exact mechanism.
- **Required (2026-08-19, bug fix — see below): MDX must document that consumers using the field-level `required` pattern above MUST also set `validation-timing="submit"` on the slotted field.** Without it, clicking a calendar day (draft only, before Apply) genuinely blurs the trigger field — since `bds-calendar-grid` day cells carry `tabIndex={-1}` for accessible keyboard navigation, they're mouse-focusable — and `bds-text-field`'s default `validation-timing="blur"` would incorrectly flag the field invalid mid-selection. This is not optional guidance; it must be called out as a required step, with the reasoning above, not just a passing mention.
- **Bug found and fixed (2026-08-19) — user-reported: "when selecting a day, the error state is triggered and it disappears when applying the selection."** Confirmed via QA dispatch, live-instrumented: `bds-calendar-grid`'s day `<td>` cells carry `tabIndex={-1}` (excluded from Tab order, but mouse-focusable per browser spec, needed for accessible keyboard grid navigation). Clicking a day genuinely blurs the trigger `<input>` (confirmed via `relatedTarget`), and `bds-text-field`'s default `validation-timing="blur"` unconditionally calls its own internal validity check on any blur — since the field's `value` is still empty at that point (correctly, per ADR-0005's draft-until-Apply model; confirmed nothing was pushed prematurely), this incorrectly flags the field `required`-invalid mid-selection, clearing only once Apply commits a real value. **Root cause is structural to `bds-date-picker`'s composition**, not `bds-select`'s: `bds-select`'s own list items aren't focusable by default and it commits on click with no separate draft/Apply window, so it never hits this — but its own stories still set `validation-timing="submit"` on required slotted fields as a matching convention regardless. **Fix**: added `validation-timing="submit"` to the "Complementary pattern" `index.html` scenario's slotted field — zero code changes to `bds-date-picker.tsx`/`bds-calendar-grid.tsx`/`bds-text-field.tsx` needed. Verified live: no error appears during day-selection with this setting; real required-validation still correctly blocks form submission and shows native feedback at actual submit time.
- **Required (2026-08-19, Slotted Field Props Compatibility Audit — see the dedicated section after Task 18 for the full audit table):** MDX must document `pattern` as a "do not set on the slotted field" constraint — there's no safe way for `bds-date-picker` to know what pattern would match its own `format`-shaped output dynamically, so a mismatched `pattern` produces a permanent, unfixable invalid state regardless of what valid date is picked (confirmed live). Also document that `clearable`/`clear-on-hover` on the slotted field are now safe to use (Task 14's `bdsClear` fix wires them to the same commit-empty behavior as the footer's Clean action) and that a `name` set on the slotted field is a "do not set" constraint (causes double `FormData` submission with a differently-formatted value; a runtime warning fires if set, per Task 14's reopened fix).

**Manual test (required):**
Run: `pnpm dev:docs` and validate:

- [ ] Given the Storybook entry, when navigating to Forms → bds-date-picker, then the default story renders correctly and controls (`format`, `hideArrow`, `disabled`) work live. Pass: interactive controls update the rendered component.
- [ ] Given the MDX page, when reading it, then the `bds-calendar-grid` internal note is present but no separate sidebar entry exists for `bds-calendar-grid`. Pass: single sidebar entry for `bds-date-picker` only.

**Commit:**

```bash
git commit -m "docs(bds-date-picker): EOA-16692 add Phase 1 Storybook story and MDX documentation"
```

---

### Task 22: React/Vue wrapper parity check — Phase 1

**Status:** ✅ done — two real regressions found and fixed via `dev:pack:react`/`dev:pack:vue` verification, not caught by the raw web-component test suite:
1. **`bds-date-picker` missing from the Vue output target's `componentModels`** (`packages/boreal-web-components/targets/vue-output-target.ts`) — `v-model` was never wired for it at all; added alongside the other value-bearing components (`bds-tag-field`, `bds-search-bar`, `bds-dropdown`, `bds-number-field`), listening on `valueChange` and targeting the `value` attr, matching the established pattern.
2. **Spurious `valueChange`/`bdsChange` on initial mount with a pre-set `value` attribute** — `componentDidLoad()` called `syncFieldValue()` (which pushes the formatted value onto the slotted `bds-text-field`, triggering that field's own `valueChange` event) *before* `addElementListener(this.bdsField, 'valueChange', this.stopFieldValueChange)` was registered. The stop-propagation guard existed but wasn't listening yet when the first sync fired, so the slotted field's internal `valueChange` bubbled up unguarded — harmless on the raw web component (nothing was listening), but a real bug for the Vue wrapper's new `v-model` binding, which would receive a spurious mount-time update. **Fix:** reordered `componentDidLoad()` to register all `addElementListener` calls (click/keydown/valueChange/bdsClear) before the `updateElementProp`/`syncFieldValue()` calls that can trigger them. Regression test added (`bds-date-picker.events.spec.ts` — "does not emit a spurious valueChange with a malformed value on initial mount") asserting zero `valueChange`/`bdsChange` calls when mounting with a pre-set `value`.
Both fixes and the regression test landed on `feature/EOA-16692_bds-date-picker-v1_tests_DG` (commits `55ce5189`, `66341125`, `f828a47b`). React wrapper showed no divergence — no fix needed there. Full Task 18 end-to-end scenario (default render, custom `format`/`locale`, `hideArrow`, disabled, form participation) re-verified through both `examples/react-testapp` and `examples/vue-testapp` after the fixes, including two-way `v-model` binding on the Vue side.
**Executor:** @qa-subagent
**Files:** none (verification-only task; no new source files)

**Acceptance criteria:**

- Confirms `bds-date-picker`'s Phase 1 behavior (open/close popover, day-selection draft state, Clean/Cancel/Apply commit behavior, FACE form participation) behaves identically through the `boreal-react` and `boreal-vue` output-target wrappers, not just the raw web component.
- Uses the `dev:pack:react`/`dev:pack:vue` pipeline (per project memory `vite-dep-cache-masks-wrapper-framework-bugs.md` — a live `pnpm dev` server can serve a stale wrapper bundle after a rebuild, producing false framework-specific bug reports; pack-based verification avoids that).
- Any framework-specific regression found (event handling, prop/attribute forwarding, `v-model`/`ngModel`-equivalent binding) is logged as a new task before Phase 2 begins, not silently patched inline here.

**Manual test (required):**

- Scenario: repeat Task 18's consolidated end-to-end scenario (default render, custom `format`, custom `locale`, `hideArrow` toggle, disabled state, form participation) through both `examples/react-testapp` and `examples/vue-testapp`.

Run: `pnpm dev:pack:react` and `pnpm dev:pack:vue`, then validate:

- [ ] Given the same scenario exercised on the raw web component in Task 18, when repeated through the React wrapper, then behavior matches exactly (open/close, draft selection, Apply/Cancel/Clean, form value). Pass: no divergence.
- [ ] Given the same scenario, when repeated through the Vue wrapper (including two-way `value` binding), then behavior matches exactly. Pass: no divergence.

**Commit:** N/A — verification-only task; no code changes expected unless a regression is found (in which case, open a new task per the acceptance criteria above rather than fixing inline).

---

## Phase 0–1 — Consolidated mutation testing

### Task 23: Consolidated mutation testing (Stryker) — Phase 0–1 surface

**Status:** ✅ done — ran once per testable unit via the `mutations-testing` skill in an isolated worktree, closed every real coverage gap surviving mutants revealed, documented the rest as equivalent/redundant-code mutants (verified, not assumed). Final scores:

| Unit | Score | Notes |
|---|---|---|
| `date-engine` | 97.37% | `date-math.ts`/`format.ts` 100%; `grid.ts` 95.92% — 2 equivalent mutants (see below) |
| `bds-calendar-grid` | 97.67% | 1 equivalent mutant (Stencil `key` prop, never rendered to the DOM — no assertion can observe it) |
| `bds-date-picker` | 93.33% | `helpers/`/`utils/` 100%; `bds-date-picker.tsx` 91.82% — 13 equivalent mutants (see below) |

**Real gaps closed (new tests, not new source):**
- `date-engine`: a locale missing its `options` object no longer throws inside `resolveWeekStartsOn`'s `?.` guard (was previously untested).
- `bds-calendar-grid`: the header container's class, every day cell's `tabindex="-1"`, and the disabled-cell class all had zero test coverage.
- `bds-date-picker`: the calendar's initial displayed month was silently ignoring the committed `value`'s own month in every existing test (masked because "today" during this test run happens to also fall in August 2026 — the same month used in most fixtures); `locale` affecting the calendar's week-start day (not just its labels) was untested; missing `keydown` listener-removal assertion on `disconnectedCallback`; missing `preventDefault()` assertion on Enter/Space activation; warn-message assertions used `stringContaining` on the message body only, not the `[bds-date-picker]:` prefix, so a mutated component-name argument slipped through; missing required-field revalidation assertions on `formResetCallback`/`formStateRestoreCallback`/`watchValue`.

**Documented equivalent-mutant exceptions** (verified via source-reading, not assumed — each traced to why no test can observe a behavioral difference):
- `grid.ts`: the `weekStartsOn !== undefined` branch guard and the grid-cell loop's `<` vs `<=` boundary are both equivalent — `date-fns`'s own `startOfWeek` already falls back to `locale.options.weekStartsOn` internally when `weekStartsOn` is `undefined`, and the loop's 43rd cell (if generated) is always discarded by the later 6×7 week-slice.
- `bds-date-picker.tsx`: `popoverVisible` state is declared but never read anywhere (genuinely dead — flagged, not removed, since Task 23's scope is tests only); `isDisabled`'s default literal is unobservable since `componentWillLoad` unconditionally overwrites it before first render; `bdsPopover?.` optional chaining across 7 call sites is defensive-only since `bds-popover` is part of this component's own always-rendered template and can never be null when queried; the `this.el !== null` guards in the `bdsField`/`bdsPopover` getters are unobservable since Stencil guarantees `@Element() el` is set before any lifecycle method runs; `formResetCallback`'s `updateValidity()`/`formStateRestoreCallback`'s `setFormValue()`+`updateValidity()` calls are redundant — the `this.value = ...` assignment on the preceding line already triggers the identical calls via `@Watch('value')`.

**Workflow notes:** ran in an isolated worktree per the skill's convention (Stryker packages/configs never committed — local-only). Found and fixed a skill gap along the way: `.stryker-tmp/` sandbox directories weren't excluded from ESLint, which balloons a type-aware `lint-staged` hook from ~13s to 6+ minutes once several Stryker runs have piled up sandbox copies in a persisting worktree — fixed in the skill template and documented in `.agents/memory/mutation-testing-stryker-setup.md`. **Branch-history incident (2026-08-19):** the mutation-testing worktree was initially branched off `docs_DG` (broadest available state) instead of `tests_DG` (its actual merge target); merging back into `tests_DG` pulled `docs_DG`'s entire history along as ancestry, collapsing the two branches' intended scope separation once `tests_DG` was later merged into `docs_DG`. Caught, fully corrected via hard-reset + cherry-pick + force-push (both branches verified clean afterward), and captured as a standing feedback memory (`feedback_branch_off_narrowest_scope_not_broadest.md`) so future branch/worktree setup always branches from the actual merge target.
Full reports: `ai-work/qa/mutation-reports/mutation-date-engine.md`, `mutation-bds-calendar-grid.md`, `mutation-bds-date-picker.md`.
**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/stryker.bds-date-picker.config.mjs` (create)

**Acceptance criteria:**

- Runs Stryker exactly once against each of this file's three testable units — `date-engine`, `bds-calendar-grid`, `bds-date-picker` — each with its own config file, per this project's existing convention (one config file per component; mutation testing stays local-only, never pushed to CI, per project memory `mutation-testing-workflow-decisions.md`).
- **Renumbered from the original Task 30 (2026-08-19)** when Phase 2 moved to [`EOA-16692-bds-date-picker-v2.md`](./EOA-16692-bds-date-picker-v2.md) — re-scoped to cover only this file's Phase 0–1 surface (`date-engine`'s `grid.ts`/`date-math.ts`/`format.ts`, `bds-calendar-grid`, `bds-date-picker`'s Phase 1 behavior). Phase 2's additions (`date-engine`'s `value.ts`, the time selector) get their own consolidated mutation-testing task in v2.
- This is the **only** point in this file where mutation testing runs — every prior testing task (3, 4, 5, 9, 11, 14, 15, 16, 17, 20) validated coverage only; do not re-run Stryker per-task retroactively, this task is the single consolidated pass.
- Target: ≥90% mutation score per component, matching the two-phase quality gate in `testing-knowledge`. Any surviving mutant below threshold gets either a new test closing the gap or a documented, justified exception (per existing project convention for killing `undefined-check`/`StringLiteral`-class mutants).
- Any mutant survivor pattern that reveals a real gap in Tasks 1–22's test coverage is fixed by extending the relevant existing spec file — do not add new source files at this stage; the goal is closing test gaps, not new behavior.

**Manual test (required):**
Non-visual (test-only) task — validate by running each component's Stryker config locally and confirming all three report ≥90% mutation score (or documented exceptions).

**Commit:**

```bash
git commit -m "test: EOA-16692 add consolidated mutation testing for date-engine, bds-calendar-grid, bds-date-picker"
```

---

## Remaining Open Questions (resolve at the task checkpoint noted, not before starting)

1. **Outside-month day cell interactivity — resolved (2026-08-14)**: leading/trailing days from adjacent months are visually shown with their real day number, styled via the `text/disabled` design token (grayed, no separate "muted" cell variant) — matching Figma's `_DatePickerNumber` `Disabled` state (spike doc's `_DatePickerNumber` day-cell properties subsection). Functionally they are **inert**: permanently `tabindex="-1"` (never promoted into the tab sequence) and clicking them does not emit `bdsDayClick` — no navigation, no selection, no event. Visual treatment is sourced from Figma; interaction treatment is sourced from the same WAI-ARIA APG reference implementation already adopted for the `<table role="grid">` markup decision (spike doc Finding #2, now extended with the full reasoning and sources). This does not reopen Task 3 (`generateMonthGrid`, already implemented/tested/100% coverage) — the fixed 6-week/42-cell grid shape is unchanged; `isCurrentMonth` (already a `DayCell` field) drives this render-only distinction.
2. **`useFormField` vs. `formAssociatedMixin` — resolved (Task 17)**: went with `formAssociatedMixin` directly plus a lightweight, purpose-built `ElementInternals.setValidity()` approach — `useFormField`'s full text-input-shaped validator pipeline (`focused`/`touched`/`dirty`/`bdsFocus`/`bdsBlur`/`customValidators`/`bdsValidationChange`) was rejected as a mismatch, since `bds-date-picker` has no keystroke-level interaction and only one validation rule (`required` + empty `value`). See Task 17's status note for the full rationale.
3. **`@Listen()` vs. runtime `addElementListener` — resolved (Task 15)**: `@Listen('bdsDayClick')`/`@Listen('bdsMonthNavigate')` reliably catch events from `bds-calendar-grid` even nested inside `bds-popover`'s slotted content — tested side-by-side against `addElementListener` first, confirmed since `bds-popover` is light DOM (no `shadow: true`), so the child stays a real DOM descendant and events bubble normally. Matches the `bds-tab-group` precedent. See Task 15's status note.
4. **Field label ownership — resolved (2026-08-19 Architecture Correction, after Task 16)**: `bds-date-picker` renders no trigger field or label of its own at all — `render()` uses `<slot name="field"></slot>`, and the consumer supplies and fully configures their own `<bds-text-field slot="field">` (label, sublabel, icon, helperText, etc.), matching `bds-select`'s exact composition model. This superseded the original Task 13 scaffold's self-rendered internal `<bds-text-field>`. See the dedicated "Architecture Correction" section after Task 16 for the full rationale and every task it touched.
5. **Translatable footer button text — resolved (Task 16)**: neither `bds-select.tsx` nor `bds-text-field.tsx` had an existing i18n/labels convention to follow, so implemented this plan's own specified shape — a `labels?: DatePickerFooterLabels` prop object (`Clear`/`Cancel`/`Apply` keys) with English defaults, not named slots. See Task 16's status note.
6. **Collapsed/single-date variant Figma node — resolved (2026-08-14)**: footer button set/order confirmed (Clean, Cancel, Apply; Apply primary), and the single-calendar layout, header format, and time-selector structure are now confirmed via user-provided "Component playground" screenshots plus a successful `get_design_context` pull on the `_Basic Time picker` node — see spike doc's "Not yet resolved" correction and the `_Basic Time picker` subsection. No longer blocking Tasks 9–11 or Task 16.
7. **Presets sidebar — corrected finding (2026-08-14)**: earlier resolved as a "deliberate v1 deviation" from `Basic`'s structure. That framing was incorrect — the sidebar's visibility is controlled by the `Range` property, not bundled unconditionally into `Basic`/`Expanded`. With `Range: off`, no sidebar renders regardless of Calendar Type (confirmed via screenshots of both `Basic`+`Range:off` and `Expanded`+`Range:off`). Phase 1/2's `Basic`+`Range:false`+`End Date:false`+`Banner:false` combination is therefore a **literal, directly-observed Figma state**, not a deviation — the sidebar is simply out of scope because `Range` is off in v1, not because it was omitted from an otherwise-matching structure. See spike doc's `Calendar Type` property enum section for the full correction. Task 21 (Storybook/MDX) does not need a "known deviation from Figma" note for this point.
8. **`_DatePickerNumber` day-cell properties — resolved (2026-08-14)**: the day-cell component exposes four independent properties — `State` (6: Default/Hover/Focus/Active/Disabled/Inactive), `Selection` (3: Default/Partial/Selected), `Type` (4: Default/Start/End/Full), `Actual` (2: True/False) — 144 total variants, confirmed via the `_DatePickerNumber` component_set metadata plus 8 targeted variant pulls. For Phase 1/2 only `Type: Default` and `Selection: Default | Selected` apply (`Partial`/`Start`/`End`/`Full` are Phase 4 range-only). Key correction: `Actual` does **not** mean "in current month" as previously guessed — it means "this date is today" (adds a dashed accent-colored ring). Month-membership (in-month vs. out-of-month) is conveyed entirely via `State: Disabled` (muted `text/disabled` grey, no ring). Full property table, decoded semantics, and the Phase 1/2 state-to-token mapping are in the spike doc's `_DatePickerNumber` day-cell properties subsection. Residual, non-blocking items for Task 9 itself: `Focus`/`Active`/`Hover`+`Actual:False` weren't individually verified against Figma — confirm empirically during implementation rather than another Figma round-trip.

---

## Verification

**Scope note (2026-08-19):** this section originally covered Phases 0–2; it's been trimmed to this file's actual Phase 0–1 scope now that Phase 2 lives in [`EOA-16692-bds-date-picker-v2.md`](./EOA-16692-bds-date-picker-v2.md), which has its own equivalent section.

- **Coverage (consolidated per block)**: gated at ≥90% Jest coverage in each block's consolidated unit-test task (Task 20 for Phase 1; Phase 0's Tasks 3–5, 9, 11 predate this convention) — run `pnpm --filter boreal-web-components test` for the full suite.
- **Mutation score (consolidated)**: Task 23 only — ≥90% Stryker score per component, run once at the end, not per task. See "Testing and QA policy" above for rationale.
- **Type safety**: `pnpm --filter boreal-web-components exec tsc --noEmit` must pass after every task (no `any`, per project rules).
- **Manual/visual (QA-subagent scoped tasks)**: `pnpm dev:components` (web-components playground) for Tasks 8, 9, 10, 14–19; `pnpm dev:docs` (Storybook) for Task 21 — component changes do not hot-reload, restart the dev server after each change per project memory.
- **React/Vue parity (consolidated)**: Task 22, end of Phase 1 — `pnpm dev:pack:react`/`pnpm dev:pack:vue`, not per-task. Phase 2's own parity check is v2's Task 7.
- **End-to-end sanity**: Task 18's consolidated scenario exercises default render, custom `format`, custom `locale`, `hideArrow` toggle, disabled state, and native `<form>` participation together, to catch integration regressions across Tasks 14–17.
