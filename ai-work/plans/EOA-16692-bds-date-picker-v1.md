---
ticket: EOA-16692
component: bds-date-picker
status: pending
created: 2026-08-12
---

# bds-date-picker v1 (ADR-0003 Phases 0–2) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Ship `date-engine` (Phase 0 pure logic), `bds-calendar-grid` (Phase 0 presentational grid), and `bds-date-picker` (Phase 1 single date + Phase 2 single time), matching the architecture decisions resolved in the spike doc below, without precluding later range/min-max/presets/banner versions.

**Ticket brief:** [`ai-work/tickets/EOA-16692-bds-date-picker.md`](../tickets/EOA-16692-bds-date-picker.md)
**Spike doc (architecture decisions — read before starting, do not duplicate here):** [`ai-work/research/2026-08-12-bds-date-picker-architecture-spike.md`](../research/2026-08-12-bds-date-picker-architecture-spike.md)

**Versioning:** This is v1. Future versions (Phase 3 min/max, Phase 4 range, etc.) get their own `ai-work/plans/<ticket>-bds-date-picker-vN.md`, linked from the spike doc — matching `bds-table`'s exact precedent (`EOA-10576-bds-table-v1.md` → `EOA-14935-bds-table-v2.md` → `EOA-15507-bds-table-v3.md`). Do not expand this file to cover Phase 3+.

**Architecture:** Bottom-up build order — `date-engine` (pure functions, plain Jest) ships and is fully tested first; `bds-calendar-grid` (dumb, controlled, light-DOM custom element rendering a native `<table role="grid">`) consumes it and ships fully tested second; `bds-date-picker` (orchestrator: `bds-text-field` trigger + `bds-popover` panel + `bds-calendar-grid` body, FACE-compliant, draft-state-until-Apply) consumes both, first as Phase 1 (date-only), then extended in Phase 2 (+ time). No external calendar UI library; light DOM throughout, matching the rest of Boreal.

**Tech Stack:** Stencil, TypeScript, `date-fns@^4.4.0` + `@date-fns/tz@^1.5.0` (new dependencies, verified against the npm registry), `@floating-ui/dom` (already wired via `anchoredMixin`/`bds-popover`), SCSS with `$boreal-*` tokens, Jest (`newSpecPage` for components, plain Jest for `date-engine`).

---

## Testing and QA policy for this plan

**Two-phase test gate, coverage embedded per task, mutation testing consolidated at the end** — mirrors `bds-table`'s `EOA-16000` precedent (its Task 15: one Stryker pass across the full surface area, not repeated per task), applied here at the scope of this single plan since there's no prior `bds-date-picker` version to combine with yet. Coverage-phase Jest tests (≥90% coverage) run per task, as normal. Mutation-phase (Stryker, ≥90% score) is deliberately **not** run per task — it's deferred to Task 30, run once after every other task in this plan is complete, across all three testable units this plan creates (`date-engine`, `bds-calendar-grid`, `bds-date-picker`), each with its own Stryker config file per this project's existing convention. Do not install Stryker or attempt the mutation-phase gate until Task 30.

**QA-subagent dispatch is scoped to tasks with real visual/behavioral output**, not every task. Tasks with a chained `**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)` line (8, 9, 10, 14–19, 24, 25) render or restyle something a human needs to look at. Pure-logic, type-only, or config tasks (1–7, 11–13, 20–23, 26–28) keep a single executor — their manual test is `tsc --noEmit` or a Jest run, which the assigned subagent already validates itself; dispatching `@qa-subagent` there would mean reviewing nothing visual.

**React/Vue wrapper parity is consolidated, not per-task** — Tasks 22 and 29. `EOA-16000` checked parity per-task because each of its 15 tasks shipped a complete, independently-usable feature on an already-mature, already-cross-framework-shipping component. This plan's 27 implementation tasks are sub-feature layers of a brand-new component that isn't composable or rendering anything meaningful until partway through Phase 1 — a parity check on a stub `<Host></Host>` render or a types-only task would find nothing, every time, and would repeatedly pay the `dev:pack:react`/`dev:pack:vue` pipeline cost for no benefit. One consolidated check at the end of each phase, once there's real cross-framework-relevant behavior to compare, is enough.

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `packages/boreal-web-components/package.json` | Modify — add `date-fns@^4.4.0`, `@date-fns/tz@^1.5.0` |
| `packages/boreal-web-components/src/services/date-engine/types.ts` | New — `MonthGrid`, `DayCell`, `WeekdayLabel`, `DateEngineLocale` alias |
| `packages/boreal-web-components/src/services/date-engine/grid.ts` | New — `generateMonthGrid`, `getWeekdayLabels` |
| `packages/boreal-web-components/src/services/date-engine/date-math.ts` | New — `addMonths`/`subMonths`/`isSameDay`/`isSameMonth`/`isWithinRange`/`compareDates`/`toNaiveISODate`/`fromNaiveISODate` |
| `packages/boreal-web-components/src/services/date-engine/format.ts` | New — `formatDisplayDate`, `getMonthYearLabel` |
| `packages/boreal-web-components/src/services/date-engine/value.ts` | New (Phase 2) — `combineDateTimeToUTC`, `extractDateTimeFromUTC` via `@date-fns/tz` |
| `packages/boreal-web-components/src/services/date-engine/index.ts` | New — public barrel |
| `packages/boreal-web-components/src/services/date-engine/__test__/grid.spec.ts` | New — plain Jest |
| `packages/boreal-web-components/src/services/date-engine/__test__/date-math.spec.ts` | New — plain Jest |
| `packages/boreal-web-components/src/services/date-engine/__test__/format.spec.ts` | New — plain Jest |
| `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts` | New (Phase 2) — plain Jest |
| `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs` | New (Task 30) — per-component Stryker config |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.tsx` | New — renders as `<table role="grid">` |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.scss` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/ICalendarGrid.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/types.ts` | New — event detail types |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/index.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/__test__/bds-calendar-grid.basics.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/__test__/bds-calendar-grid.events.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/__test__/bds-calendar-grid.variants.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` | New (Task 30) — per-component Stryker config |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.scss` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderCalendarPanel.tsx` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderFooter.tsx` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderTimeSelector.tsx` | New (Phase 2) |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/draft-state.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/value-mapping.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/index.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/types/IDatePicker.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/types/enum.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/types/types.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/types/index.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.basics.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.events.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.variants.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.form.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts` | New |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.time.spec.ts` | New (Phase 2) |
| `packages/boreal-web-components/src/components/forms/bds-date-picker/stryker.bds-date-picker.config.mjs` | New (Task 30) — per-component Stryker config |
| `packages/boreal-web-components/src/index.html` | Modify — playground scenarios per task (never committed, per project memory) |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` | New |
| `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` | New — includes internal `bds-calendar-grid` implementation note |

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

**Executor:** main thread (no executor)
**Files:**
- `packages/boreal-web-components/package.json` (modify)

**Acceptance criteria:**
- `date-fns@^4.4.0` and `@date-fns/tz@^1.5.0` (latest per npm registry as of this plan's writing) added under `dependencies` — not `devDependencies`, since both ship at runtime inside `date-engine`.
- `@date-fns/tz` requires date-fns v4+; confirm the installed date-fns major is 4.x before proceeding to Task 23.
- `pnpm install` run at the workspace root; lockfile updated.
- Utility discovery note: searched `package.json` dependencies for any existing date library — none found (`@braintree/sanitize-url`, `@floating-ui/dom`, `@tanstack/virtual-core`, `dompurify` only). No suitable existing utility; new dependency justified per the spike doc's Finding 1.

**Manual test (required):**
Non-visual/config task — validate with `pnpm install` completing without errors and `pnpm -w list date-fns @date-fns/tz` (or equivalent) showing the resolved versions inside `packages/boreal-web-components`.

**Commit:**
```bash
git commit -m "chore(boreal-web-components): EOA-16692 add date-fns and @date-fns/tz dependencies"
```

---

### Task 2: `date-engine` core types

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

**Executor:** @frontend-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/ICalendarGrid.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/types.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/types/index.ts` (create)

**Acceptance criteria:**
- `ICalendarGrid` declares: `grid: MonthGrid` (from `date-engine`), `selectedDate?: string` (naive ISO), `year: number`, `month: number` (0-indexed), `locale?: DateEngineLocale`.
- `types.ts` declares `DayClickDetail { date: string }` and `MonthNavigateDetail { year: number; month: number; direction: 'prev' | 'next' }`.
- No `disabled`/`min`/`max` props (Phase 3, out of scope) — but `DayCell.isDisabled` (already in `date-engine` types) is left as dead capacity so Phase 3 can wire it without an interface break.
- Utility discovery note: checked `bds-table-column`/`bds-table-column-group` types for a reusable "dumb controlled child" interface — none generic enough (table-specific); new interface justified, the *pattern* (controlled, no internal state) follows `bds-tab`/`bds-tab-content`.

**Manual test (required):**
Non-visual task — validate via `tsc --noEmit`.

**Commit:**
```bash
git commit -m "feat(bds-calendar-grid): EOA-16692 add component type definitions"
```

---

### Task 8: `bds-calendar-grid` scaffold

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.tsx` (create)

**Acceptance criteria:**
- `@Component({ tag: 'bds-calendar-grid' })`, no `styleUrl` yet (Task 10), light DOM.
- `@Prop() readonly grid!: MonthGrid`
- `@Prop() readonly selectedDate?: string`
- `@Prop() readonly year!: number`
- `@Prop() readonly month!: number`
- `@Prop() readonly locale?: DateEngineLocale`
- `@Event() bdsDayClick!: EventEmitter<DayClickDetail>`
- `@Event() bdsMonthNavigate!: EventEmitter<MonthNavigateDetail>`
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

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.tsx` (modify — full render, replacing stub)

**Acceptance criteria:**
- Renders as a **native `<table role="grid">`**, per the spike doc's resolved decision (matches the WAI-ARIA APG's own Date Picker Dialog reference markup and `bds-table`'s established "native elements for free a11y" precedent):
  - Month/year label + prev/next nav buttons render in a header region above the `<table>` (not inside `<thead>` as a `<th>`, since nav controls aren't column headers) — using `getMonthYearLabel` from `date-engine`.
  - `<thead><tr role="row">` contains 7 weekday `<th scope="col">` cells, in order from `getWeekdayLabels`. `role="row"`/`columnheader` are implied by `tr`/`th` per the APG reference — no manual role authoring needed there.
  - `<tbody>` contains 6 `<tr role="row">` week rows, each with 7 `<td role="gridcell">` day cells (role implied by `td`, matching the APG pattern).
  - A code comment on the `<table>`'s `role="grid"` attribute explicitly states why it's not redundant on a native `<table>` (overrides the implicit `role="table"` to signal interactive 2D navigation semantics to assistive tech), so a future maintainer doesn't "clean it up."
- Prev/next buttons emit `bdsMonthNavigate` with the computed adjacent year/month (via `date-engine`'s `addMonths`/`subMonths`) and `direction`; component does **not** self-update `year`/`month` — parent re-renders with new props (controlled pattern, matching `bds-tab-group`).
- Day cell click emits `bdsDayClick` with the cell's naive ISO date; cells with `isDisabled: true` (currently none set by any Phase 0-2 caller, dead capacity from Task 7) must not emit, guarding the future Phase 3 wiring point.
- Day cell states via CSS class map: default, hover (`:hover`), focus (`:focus-visible`), selected/active (`selectedDate` match), disabled (dead capacity, styled but unused), today (`isToday`). No in-range/end-range states (Phase 4+, out of scope).
- Nav buttons reuse `bds-button`'s icon-only variant (matching how `bds-popover`'s `closable` header button is implemented) rather than hand-rolled `<button>` markup, unless the 32×32px sizing constraint requires a hand-rolled `<button>` — if so, document why `bds-button` didn't fit.
- Leading/trailing adjacent-month days render visually de-emphasized but remain clickable, **pending confirmation against the actual Figma screenshot at implementation time** (open question — see Remaining Open Questions).
- Utility discovery note: `src/utils/a11y/keyboard/navigation/grid-navigation.ts` exists and is generic for arrow-key grid traversal, but keyboard nav is explicitly out of scope for Phase 0-2 (Phase 8) — do not wire it here; leave a code comment identifying it as the correct future integration point.

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

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.tsx` (modify — JSDoc only)
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/bds-calendar-grid.scss` (create)

**Acceptance criteria:**
- Every `@Prop`, `@Event`, and the class-level component JSDoc block are complete and accurate.
- SCSS uses `$boreal-*` tokens exclusively (matching `bds-text-field.scss`'s convention) — no hardcoded hex/px values for colors; spacing/sizing translated to the nearest token scale per the Figma sizing notes (32×32px cells, 53px header padding, 4px/2px grid gutters, 290×290px card, 24px/12px card padding) — if no exact token matches a given pixel value, pick the nearest token and document the delta in a code comment.
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

**Executor:** @testing-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/__test__/bds-calendar-grid.a11y.spec.ts` (create)

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

**Executor:** @frontend-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/types/IDatePicker.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/types/enum.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/types/types.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/types/index.ts` (create)

**Acceptance criteria:**
- `IDatePicker` declares: `value: string` (public, canonical ISO — naive `yyyy-MM-dd` in Phase 1), `format: string` (date-fns format string, default `yyyy/MM/dd`), `locale?: DateEngineLocale`, `timezone: string` (default resolved via `Intl.DateTimeFormat().resolvedOptions().timeZone`), `hideArrow: boolean` (default `true`), `name: string`, `disabled: boolean`, `required: boolean`.
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

**Executor:** @frontend-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (create)

**Acceptance criteria:**
- `@Component({ tag: 'bds-date-picker' })`, light DOM, no `styleUrl`/`formAssociated` yet.
- `@Prop({ mutable: true, reflect: true }) value: string = ''`
- `@Prop() readonly format: string = 'yyyy/MM/dd'`
- `@Prop() readonly locale?: DateEngineLocale`
- `@Prop() readonly timezone: string = Intl.DateTimeFormat().resolvedOptions().timeZone` (resolved once as a class field default, not recomputed every render)
- `@Prop() readonly hideArrow: boolean = true`
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

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- In `componentDidLoad()`, calls `bdsPopover.setListenElement(...)` and `bdsPopover.setAnchorElement(...)` exactly as `bds-select.tsx` does against its `bdsInputContainer` getter — reuse the same getter pattern (`private get bdsField()`, `private get bdsInputContainer()`, `private get bdsPopover()`) querying `this.el` at runtime.
- The composed `bds-text-field` renders with `selectable={true}` (reusing `bds-select`'s non-editable-input mechanism) so the field displays formatted text but isn't directly typable.
- `floatingOptions` passed to `bds-popover` sets `hideArrow: this.hideArrow` (deliberate deviation from `bds-select`/`bds-dropdown`'s hardcoded `true`) plus the popover's own `footer` prop enabled so the Clean/Cancel/Apply buttons render in the popover's existing `footer-button` slot.
- Clicking the trigger opens the popover (`openPopover()`); no calendar content yet (Task 15) — verify only open/close mechanics with an empty popover body.
- `disabled` prevents the popover from opening (mirrors `bds-popover`'s own `disabled` prop wired through `onBeforeShow`).

**Unit tests to cover** _(spec file: `bds-date-picker.basics.spec.ts`)_:
- Clicking the trigger field opens the popover; clicking outside (or Escape) closes it, reusing `bds-popover`'s own click-outside/escape behavior (assert the integration, not re-testing `bds-popover`'s internals).
- `disabled={true}` prevents the popover from opening on trigger click.
- `hideArrow={false}` results in the popover's arrow element being present; `hideArrow={true}` (default) results in no arrow — the one behavior that deliberately diverges from `bds-select`'s hardcoded value, needs explicit coverage.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
- Scenario 1: default props; click the trigger to open/close the popover.
- Scenario 2: a second instance with `hide-arrow="false"` to visually confirm the arrow renders.
- Scenario 3: a `disabled` instance confirming the trigger does not open the popover.

Run: `pnpm dev:components` and validate:
- [ ] Given the default instance, when clicking the trigger field, then the popover opens; clicking outside closes it. Pass: popover visibility toggles correctly.
- [ ] Given the `hide-arrow="false"` instance, when opened, then a visible arrow points from the popover to the trigger. Pass: arrow element visible.
- [ ] Given the `disabled` instance, when clicking the trigger, then nothing opens. Pass: popover stays hidden.

**Commit:**
```bash
git commit -m "feat(bds-date-picker): EOA-16692 wire text-field trigger and popover composition"
```

---

### Task 15: `bds-date-picker` draft state utility + calendar wiring

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/draft-state.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/value-mapping.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/utils/index.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderCalendarPanel.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- `draft-state.ts` exports pure functions: `selectDay(draft, isoDate): draft`, `resetDraft(committedValue): draft`, `cloneDraftFromValue(value): draft` — kept out of the `.tsx` file per the `bds-table` file-organization decision.
- `value-mapping.ts` bridges `date-engine`'s `MonthGrid`/`Date` types and the component's naive-ISO `value` string, using `toNaiveISODate`/`fromNaiveISODate` — the only place in `bds-date-picker` that touches `date-engine`'s date-math functions directly.
- `renderCalendarPanel.tsx` composes `<bds-calendar-grid>` inside the popover body, computing its `grid`/`year`/`month`/`selectedDate` props from component `@State`.
- Component adds `@State() displayYear`/`@State() displayMonth` (initialized to the committed `value`'s month, or today's month if `value` is empty) — the orchestrator owns this, `bds-calendar-grid` never does.
- Listens to `bdsDayClick` from the slotted `bds-calendar-grid`. Confirm at implementation time whether Stencil's `@Listen()` decorator reliably catches events from a `bds-calendar-grid` rendered inside `bds-popover`'s slotted content, or whether the `bds-select.tsx`-style runtime `addElementListener` query is required (open question — default to `addElementListener` for consistency with Task 14's own pattern if `@Listen()` doesn't work).
- Day click updates **only** `this.draft` (via `selectDay`) — does not touch `this.value`, does not emit `bdsChange`/`valueChange`, does not close the popover (ADR-0005: draft-until-Apply).
- Listens to `bdsMonthNavigate` and updates `displayYear`/`displayMonth` accordingly, re-rendering the grid for the new month.

**Unit tests to cover** _(spec file: `bds-date-picker.events.spec.ts`)_:
- Clicking a day in the calendar updates the visible "selected" state inside the popover but does **not** change the public `value` prop and does **not** emit `bdsChange`/`valueChange` — the single most important behavior in the component, needs an explicit, unambiguous test.
- Clicking month-nav prev/next updates the displayed month/year without affecting the selected day or the draft.
- Reopening the popover after a previous session (without Apply) resets the draft to the last **committed** value, not the abandoned draft.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
- Scenario 1: no initial `value`; open the popover, click a day, confirm the trigger field's text does *not* change yet.
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

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderFooter.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- Footer renders three `bds-button`s slotted into `bds-popover`'s existing `footer-button` slot region.
- Button text is not hardcoded — expose via a `labels` prop object (`{ clean?: string; cancel?: string; apply?: string }` with English defaults `'Clear' | 'Cancel' | 'Apply'`) unless checking `bds-select`/`bds-text-field` reveals an existing i18n convention to follow instead (open question — check first).
- **Apply**: commits `this.draft.selectedDate` into `this.value` (naive ISO via `value-mapping.ts`), emits `bdsChange`/`valueChange`, updates the text field's displayed formatted text, closes the popover.
- **Cancel**: discards `this.draft`, resets it to the last committed `this.value`, closes the popover, does **not** emit any event.
- **Clean**: resets the draft to empty **and commits immediately** — clears `this.value`, emits `bdsChange`/`valueChange` with `''` (confirmed behavior, no longer an open question).
- All three buttons are keyboard-operable (native `bds-button` semantics) and disabled together with the whole component when `this.disabled` is true.

**Unit tests to cover** _(spec file: `bds-date-picker.events.spec.ts`, extending Task 15's file)_:
- Apply with a selected draft day commits `value`, emits exactly one `bdsChange` and one `valueChange` with the correct naive-ISO string, and closes the popover.
- Apply with no draft selection (opened and closed without picking a day) does not change `value` and does not emit.
- Cancel after a day click leaves `value` unchanged, emits no event, and closes the popover.
- Clean clears `value` to `''` and emits `bdsChange`/`valueChange` with `''`.
- Labels prop/i18n mechanism override changes the rendered button text.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
- Scenario 1: no value; open, pick a day, click Apply; confirm trigger text updates to the formatted date and popover closes.
- Scenario 2: a committed value; open, pick a different day, click Cancel; confirm trigger text unchanged and popover closes.
- Scenario 3: a committed value; open, click Clean; confirm trigger text clears immediately.

Run: `pnpm dev:components` and validate:
- [ ] Given a fresh pick + Apply, when Apply is clicked, then the trigger shows the newly formatted date and the popover closes. Pass: visible text update + closed popover.
- [ ] Given a pick + Cancel, when Cancel is clicked, then the trigger's previously committed text is unchanged. Pass: no visible change.
- [ ] Given Clean on a populated field, when Clean is clicked, then the trigger clears immediately. Pass: empty trigger text.

**Commit:**
```bash
git commit -m "feat(bds-date-picker): EOA-16692 add Clean/Cancel/Apply footer actions"
```

---

### Task 17: `bds-date-picker` FACE wiring

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- Adds `formAssociated: true` to `@Component()`.
- Class extends `Mixin(formAssociatedMixin)` and implements `IFormControl<string>`, matching `bds-text-field.tsx` — **unless** checking `src/mixins/form-associated.mixin.ts` and `src/utils/form/` at implementation time reveals `useFormField` has become the canonical pattern in more recently built form components (check via `git log` on a newer form component like `bds-tag-field.tsx`), in which case use that instead (open question — determine before wiring, don't assume `bds-text-field.tsx`'s pattern is still current).
- Adds `@AttachInternals() internals!: ElementInternals`.
- Adds `@Watch('value') watchValue(next) { setFormValue(this.internals, next); }` (or the `useFormField`-equivalent, whichever pattern is chosen).
- `formResetCallback` resets `value` to `''` and also resets the internal draft.

**Unit tests to cover** _(spec file: `bds-date-picker.form.spec.ts`)_:
- Component participates in a native `<form>`'s `FormData` with the correct `name`/`value` pair after Apply.
- `formResetCallback` (triggered by a form `reset`) clears both `value` and any open draft state.
- `required` + empty `value` produces the expected validity state (`ElementInternals.validity`), consistent with `bds-text-field`'s own required-field validity pattern.
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

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

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- Final `render()` assembles: `bds-text-field` (slot="field", `selectable`, formatted display value via `formatDisplayDate`), `bds-popover` (with `renderCalendarPanel` body + `renderFooter` footer), and a hidden `<input type="hidden">` mirroring `value` for form-submission parity, matching `bds-select`'s own hidden-input pattern.
- Every `@Prop`, `@Event`, and the class-level component JSDoc block (including `@slot` docs for any custom slots, e.g. a `labels` override) are complete.
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

### Task 19: `bds-date-picker` SCSS

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.scss` (create)

**Acceptance criteria:**
- Uses `$boreal-*` tokens exclusively, matching `bds-calendar-grid.scss`'s convention.
- Decide whether `bds-text-field`'s built-in label region or a `bds-date-picker`-owned label (via `renderFieldLabel` from `src/components/forms/common/`) renders — avoid duplicating (open question, resolve here).
- Popover content sizing approximates 290×290px content with 24px/12px padding per the Figma spec, translated to nearest `$boreal-spatial-*` tokens.

**Manual test (required):**
Reuse the consolidated scenario from Task 18.

Run: `pnpm dev:components` and validate:
- [ ] Given the rendered component, when compared against the Figma spec, then label position, field styling, and popover sizing visually match within token tolerance. Pass: visual comparison confirmed.

**Commit:**
```bash
git commit -m "feat(bds-date-picker): EOA-16692 add SCSS styling"
```

---

### Task 20: `bds-date-picker` remaining Phase 1 unit tests

**Executor:** @testing-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.basics.spec.ts` (extend from Task 14)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.variants.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts` (create)

**Acceptance criteria:**
- Coverage split matches the `bds-toggle`/`bds-tab-group` `__test__/` convention: each file owns a distinct concern, no duplicate assertions.

**Unit tests to cover:**
- `variants`: custom `format` changes trigger display text without changing `value`; custom `locale` produces locale-correct month names in both the trigger text and the calendar header.
- `variants`: `disabled` disables the trigger, footer buttons, and prevents popover opening, all together.
- `keyboard`: Tab reaches the trigger field; Enter/Space opens the popover (via `bds-popover`'s own `KeyboardController` mechanism wired in Task 14 — assert the integration outcome). No arrow-key day-grid navigation tested (Phase 8).
- `a11y`: trigger field has correct `aria-haspopup`/`aria-expanded` reflecting popover visibility.
- `a11y`: footer buttons are reachable and labeled correctly for screen readers.

**Manual test (required):**
Non-visual (test-only) task — validate via `pnpm --filter boreal-web-components test -- bds-date-picker` passing at ≥90% coverage (coverage-phase only; mutation testing deferred to Task 30).

**Commit:**
```bash
git commit -m "test(bds-date-picker): EOA-16692 add variants, keyboard, and a11y unit tests"
```

---

### Task 21: `bds-date-picker` Phase 1 documentation

**Executor:** @documentation-subagent
**Files:**
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (create)
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (create)

**Acceptance criteria:**
- Story/MDX registered under the `forms` category, following the `bds-select` story/MDX pair as the structural template.
- MDX documents `bds-date-picker`'s full public API plus a dedicated internal-implementation-note section documenting `bds-calendar-grid`'s existence, props, and events as an internal note only — no separate `bds-calendar-grid.mdx`/story file (per the spike doc's resolved decision).
- Documents the `value` contract explicitly (naive `yyyy-MM-dd` ISO, decoupled from `format`) and the draft-until-Apply behavior including Clean's commit-immediately behavior.
- Includes working Storybook controls for `format`, `locale` (documented as accepting a raw date-fns `Locale` object, with an example import), `timezone`, `hideArrow`, `disabled`, `required`.
- Follows `documentation-knowledge` skill conventions for action wiring and source-snippet overrides for non-primitive props (the `locale` prop, being an object, needs a source-snippet override).

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

## Phase 2 — Time selector

### Task 23: `date-engine` timezone-aware value conversion

**Executor:** @frontend-subagent
**Files:**
- `packages/boreal-web-components/src/services/date-engine/value.ts` (create)
- `packages/boreal-web-components/src/services/date-engine/__test__/value.spec.ts` (create)

**Acceptance criteria:**
- Confirm the date-fns major pinned in Task 1 is v4+ (required for `@date-fns/tz`) before starting.
- Exports `combineDateTimeToUTC(datePart: Date, hour: number, minute: number, timezone: string): string` — interprets the given wall-clock date+time *as if in* `timezone`, returns the UTC ISO 8601 string (`...Z` suffix), via `@date-fns/tz`'s `TZDate`.
- Exports `extractDateTimeFromUTC(isoUtc: string, timezone: string): { date: Date; hour: number; minute: number }` — the reverse, for populating draft state from an existing datetime `value`.
- Handles DST transitions correctly (a wall-clock time ambiguous or nonexistent during a DST fold/gap must not silently produce a wrong-by-one-hour UTC value).
- Utility discovery note: confirmed no existing timezone utility anywhere in `packages/boreal-web-components/src/`. New module justified; document the library choice (`@date-fns/tz`, version) in this file's header comment.

**Unit tests to cover** _(spec file: `services/date-engine/__test__/value.spec.ts`)_:
- Combining a date+time in a positive-UTC-offset zone (e.g. `Asia/Tokyo`) produces the correctly shifted UTC ISO string.
- Combining a date+time in a negative-UTC-offset zone (e.g. `America/Los_Angeles`) produces the correctly shifted UTC ISO string, including across that zone's DST "spring forward"/"fall back" transition dates for the relevant year.
- `extractDateTimeFromUTC` round-trips with `combineDateTimeToUTC` for a sample of zones/times including at least one DST-boundary case.
- An invalid IANA timezone string does not silently produce a wrong result — throws or falls back predictably (document and test whichever is chosen).
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

**Manual test (required):**
Non-visual task — validate via the `date-engine` test script passing, including the DST-boundary cases specifically.

**Commit:**
```bash
git commit -m "feat(date-engine): EOA-16692 add timezone-aware date-time to UTC ISO conversion"
```

---

### Task 24: `bds-date-picker` time selector — design check-in (blocking gate)

**Executor:** main thread (no executor) — not an implementation task

**Acceptance criteria:**
- Before Task 25 begins, present the inferred single-date time-selector UI (hour:minute dropdown pair) to the user for confirmation or correction, since the provided docs only show the dual Inicio/Fin range variant.
- Document the confirmed design as a short addendum to this plan before proceeding.

**Manual test:** N/A — design confirmation checkpoint, not a code task.

---

### Task 25: `bds-date-picker` time selector implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/helpers/renderTimeSelector.tsx` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/types/types.ts` (modify — extend `DatePickerDraftState` with `hour`/`minute`)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify)

**Acceptance criteria:**
- Adds `@Prop() readonly showTime: boolean = false` (or the name confirmed at Task 24) gating whether the time selector renders inside the popover body alongside the calendar.
- Time selector composes two `bds-select` instances (hour 00-23, minute 00-59, per the confirmed design) inside `renderTimeSelector.tsx` — not a new registered custom element.
- Time changes update `this.draft.hour`/`this.draft.minute` only — same draft-until-Apply contract as day selection.
- When `showTime` is `false` (Phase 1 behavior), the value contract remains the naive `yyyy-MM-dd` string, untouched — proves Phase 2 is additive, not breaking.
- When `showTime` is `true`, Apply computes the final UTC ISO string via `combineDateTimeToUTC`, using `this.timezone` and the draft's date+hour+minute.
- Loading an existing `showTime=true` datetime `value` on init correctly pre-populates the draft's date, hour, and minute via `extractDateTimeFromUTC`.

**Unit tests to cover** _(spec file: `bds-date-picker.time.spec.ts`)_:
- With `showTime=false`, `value` after Apply remains a naive `yyyy-MM-dd` string (regression check against Phase 1 contract).
- With `showTime=true`, selecting a day + hour + minute then Apply produces a correctly UTC-normalized ISO string for a non-UTC `timezone` prop.
- With `showTime=true` and an explicit `timezone` override, the same wall-clock selection produces a different UTC value than with the default browser timezone (proves the `timezone` prop is honored).
- Loading a component with an existing datetime `value` and `showTime=true` correctly pre-populates hour/minute.
- Cancel with `showTime=true` discards time draft changes exactly like date draft changes (Task 16's contract extended consistently).
- Coverage-phase only (≥90%); mutation testing deferred to Task 30.

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

### Task 26: `bds-date-picker` Phase 2 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.scss` (modify)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker.tsx` (modify — JSDoc for new `showTime`/time-related props)

**Acceptance criteria:**
- Time selector styling uses `$boreal-*` tokens, matching the popover body's existing spacing conventions from Task 19.
- JSDoc for `showTime` and any new props/state added in Task 25 is complete and accurate.

**Manual test (required):**
Reuse Task 25's scenarios.

Run: `pnpm dev:components` and validate:
- [ ] Given the time-enabled instance, when compared visually against the confirmed Task 24 design, then spacing and alignment match. Pass: visual match confirmed.

**Commit:**
```bash
git commit -m "feat(bds-date-picker): EOA-16692 style time selector and finalize Phase 2 JSDoc"
```

---

### Task 27: `bds-date-picker` Phase 2 unit tests (a11y/keyboard extension)

**Executor:** @testing-subagent
**Files:**
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts` (extend)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/__test__/bds-date-picker.keyboard.spec.ts` (extend)

**Acceptance criteria:**
- Extends existing Phase 1 spec files rather than creating parallel duplicate files, keeping the split-by-concern convention intact.

**Unit tests to cover:**
- Hour/minute `bds-select` instances are reachable via Tab and correctly labeled for screen readers (reusing `bds-select`'s own established a11y behavior — assert the integration).
- `showTime` toggling doesn't break the Phase 1 keyboard flow already covered in Task 20.

**Manual test (required):**
Non-visual (test-only) task — validate via the full `bds-date-picker` test suite passing at ≥90% coverage (coverage-phase only; mutation testing deferred to Task 30).

**Commit:**
```bash
git commit -m "test(bds-date-picker): EOA-16692 extend a11y and keyboard tests for time selector"
```

---

### Task 28: `bds-date-picker` Phase 2 documentation

**Executor:** @documentation-subagent
**Files:**
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` (modify — add a `showTime` variant story)
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` (modify)

**Acceptance criteria:**
- MDX documents the Phase 2 value contract explicitly: `value` becomes a full UTC ISO 8601 string when `showTime` is enabled, contrasted clearly against the Phase 1 naive-date contract.
- MDX explicitly notes that the single time-selector UI was an inferred design (per Task 24's resolution — update this note to reflect whatever was actually confirmed).
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

### Task 29: React/Vue wrapper parity check — Phase 2

**Executor:** @qa-subagent
**Files:** none (verification-only task; no new source files)

**Acceptance criteria:**
- Confirms `showTime`/time-selector behavior (hour/minute selection, UTC-normalized `value`, `timezone` prop honoring) behaves identically through `boreal-react` and `boreal-vue`, extending Task 22's Phase 1 check rather than duplicating it.
- Uses the `dev:pack:react`/`dev:pack:vue` pipeline, same rationale as Task 22.
- Any regression found is logged as a new task, not patched inline here.

**Manual test (required):**
- Scenario: repeat Task 25's three scenarios (time-enabled Apply, cross-timezone comparison, pre-loaded datetime value) through both `examples/react-testapp` and `examples/vue-testapp`.

Run: `pnpm dev:pack:react` and `pnpm dev:pack:vue`, then validate:
- [ ] Given Task 25's scenarios, when repeated through the React wrapper, then behavior matches exactly, including the emitted UTC value. Pass: no divergence.
- [ ] Given the same scenarios, when repeated through the Vue wrapper, then behavior matches exactly. Pass: no divergence.

**Commit:** N/A — verification-only task; no code changes expected unless a regression is found.

---

### Task 30: Consolidated mutation testing (Stryker) — full v1 surface

**Executor:** @testing-subagent
**Files:**
- `packages/boreal-web-components/src/services/date-engine/stryker.date-engine.config.mjs` (create)
- `packages/boreal-web-components/src/components/forms/bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` (create)
- `packages/boreal-web-components/src/components/forms/bds-date-picker/stryker.bds-date-picker.config.mjs` (create)

**Acceptance criteria:**
- Runs Stryker exactly once against each of this plan's three testable units — `date-engine`, `bds-calendar-grid`, `bds-date-picker` — each with its own config file, per this project's existing convention (one config file per component; mutation testing stays local-only, never pushed to CI, per project memory `mutation-testing-workflow-decisions.md`).
- This is the **only** point in the plan where mutation testing runs — every prior testing task (3, 4, 5, 9, 11, 14, 15, 16, 17, 20, 23, 25, 27) validated coverage only; do not re-run Stryker per-task retroactively, this task is the single consolidated pass.
- Target: ≥90% mutation score per component, matching the two-phase quality gate in `testing-knowledge`. Any surviving mutant below threshold gets either a new test closing the gap or a documented, justified exception (per existing project convention for killing `undefined-check`/`StringLiteral`-class mutants).
- Any mutant survivor pattern that reveals a real gap in Tasks 1–29's test coverage is fixed by extending the relevant existing spec file — do not add new source files at this stage; the goal is closing test gaps, not new behavior.

**Manual test (required):**
Non-visual (test-only) task — validate by running each component's Stryker config locally and confirming all three report ≥90% mutation score (or documented exceptions).

**Commit:**
```bash
git commit -m "test: EOA-16692 add consolidated mutation testing for date-engine, bds-calendar-grid, bds-date-picker"
```

---

## Remaining Open Questions (resolve at the task checkpoint noted, not before starting)

1. **Outside-month day cell interactivity** (Task 9): whether leading/trailing days from adjacent months are clickable-but-muted or fully inert — check directly against the Figma screenshot at implementation time.
2. **`useFormField` vs. `formAssociatedMixin`** (Task 17): both exist in the codebase; check which more recently built form components adopted before wiring FACE.
3. **`@Listen()` vs. runtime `addElementListener`** (Task 15): confirm whether Stencil's `@Listen()` decorator reliably catches `bdsDayClick`/`bdsMonthNavigate` from a `bds-calendar-grid` rendered inside `bds-popover`'s slotted content, or whether the `bds-select.tsx`-style runtime query is required.
4. **Field label ownership** (Task 19): `bds-text-field` already renders its own label; decide whether `bds-date-picker` reuses that or renders its own via `renderFieldLabel`, to avoid a duplicate label.
5. **Translatable footer button text** (Task 16): check `bds-select`/`bds-text-field` for an existing i18n convention before deciding between a `labels` prop object or named slots.

---

## Verification

- **Coverage (per task)**: each `date-engine` module and Stencil component spec file, as written per task above, gated at ≥90% Jest coverage — run `pnpm --filter boreal-web-components test` for the full suite.
- **Mutation score (consolidated)**: Task 30 only — ≥90% Stryker score per component, run once at the end, not per task. See "Testing and QA policy" above for rationale.
- **Type safety**: `pnpm --filter boreal-web-components exec tsc --noEmit` must pass after every task (no `any`, per project rules).
- **Manual/visual (QA-subagent scoped tasks)**: `pnpm dev:components` (web-components playground) for Tasks 8, 9, 10, 14–19, 24, 25; `pnpm dev:docs` (Storybook) for Tasks 21, 28 — component changes do not hot-reload, restart the dev server after each change per project memory.
- **React/Vue parity (consolidated)**: Tasks 22 (end of Phase 1) and 29 (end of Phase 2) — `pnpm dev:pack:react`/`pnpm dev:pack:vue`, not per-task.
- **End-to-end sanity**: Task 18's consolidated scenario exercises default render, custom `format`, custom `locale`, `hideArrow` toggle, disabled state, and native `<form>` participation together, to catch integration regressions across Tasks 14–17 before moving to Phase 2.
