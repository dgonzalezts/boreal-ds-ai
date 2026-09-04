---
ticket: EOA-17662
component: bds-date-picker
status: planned
created: 2026-09-02
updated: 2026-09-02
revision: 3
---

# EOA-17662 — bds-date-picker v3 (Phases 5-9) Implementation Plan

This plan carries forward the remaining roadmap scope after v2 foundation work.

- v2 (EOA-17138) now ends at Phase 4 foundation work.
- v3 (EOA-17662) owns all remaining work: Phases 5-9 plus final consolidated mutation testing.
- Keyboard-typed date entry in the trigger field remains explicitly out of scope.

## Phase 5 — Time selection for range mode (single-shared vs. dual independent)

Per the spike decisions, range mode supports two time-selection behaviors:

- `calendarType='expanded'` + `range` + `withTime`: two independent time selectors (start/end)
- `calendarType='basic'` + `range` + `withTime`: one shared time selector applied to both range boundaries

### Task 23: `bds-date-picker` range-mode time selector (single-shared under `basic`, dual under `expanded`)

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderTimeSelector.tsx` (modify), `bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- `renderTimeSelector.tsx` accepts a `label`/`position: 'single' | 'start' | 'end'` parameter; single-date Phase 2 usage remains a regression-free special case (`position: 'single'`).
- Routing is driven by `calendarType`, not by `range` alone: when `calendarType === 'expanded'` and `range && withTime`, renders two labeled time-selector pairs. When `calendarType === 'basic'` and `range && withTime`, renders one `position: 'single'` time selector.
- Under `calendarType === 'basic'` with `range && withTime`, one hour/minute value applies to both `rangeStart` and `rangeEnd` when constructing committed `{ start, end }` UTC strings.
- Under `calendarType === 'expanded'`, uses `combineDateTimeToUTC`/`extractDateTimeFromUTC` for independently controlled start/end time values.
- Value contract when `range && withTime`: `{ start, end }` where both are full UTC ISO strings; shape stays identical regardless of `calendarType`.
- Legacy prop references `resetTime`/`showTimeInRange` are evaluated and either adopted with rationale or explicitly deferred.
- `format` auto-switch extends to range mode: when `range && withTime` and `format` is unset, Start/End display includes `HH:mm`; explicit `format` still wins.
- Default time extends to range mode: fresh range values default to `00:00`, following the shared-vs-independent rule above.

**Manual test (required):** `pnpm dev:components` — Scenario 1: `calendarType='expanded'`, range + time enabled, select start/end times independently and verify UTC values. Scenario 2: `calendarType='basic'`, range + time enabled, choose one time and verify both committed values share that hour/minute with different dates. Scenario 3: confirm single-date Phase 2 usage still works unchanged. Scenario 4: range + time without explicit `format` shows `HH:mm` in Start/End display.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add dual time selector for range mode"`

---

### Task 24: Phase 5 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass (complete before writing any SCSS):**

- [ ] Region: `expanded` dual time-selector layout (side-by-side start/end pairs)
- [ ] Region: `basic`+`range` single-shared time-selector layout
- [ ] Interaction: dual pair states beyond the single selector defaults

**Acceptance criteria:** Every research row checked before SCSS; `$boreal-*` tokens exclusively; JSDoc conforms to the brevity/content rule.

**Manual test (required):** Reuse Task 23 scenarios visually.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style dual time selector"`

---

### Task 25: Phase 5 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.time.spec.ts` (modify)

**Unit tests to cover:** `expanded` dual selector independent start/end UTC computation; `basic`+`range` shared-time application; single-date Phase 2 regression; Cancel discarding time drafts in both `calendarType` cases. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suite passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 5 dual time selector unit tests"`

---

### Task 26: Phase 5 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents both range-mode time behaviors and the shared `{ start, end }` UTC contract; includes story variants for both `calendarType` cases.

**Manual test (required):** `pnpm dev:docs` — new stories render and behave correctly.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 5 range-mode time selection"`

---

### Task 27: React/Vue wrapper parity check — Phase 5

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Confirms both `expanded` dual-time and `basic` shared-time behavior identically through both wrappers.

**Manual test (required):** Repeat Task 23 scenarios in both wrapper playgrounds.

**Commit:** N/A

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

**Acceptance criteria:**

- Sidebar renders only when `range=true`.
- Clicking a preset sets `draft.rangeStart`/`draft.rangeEnd` and marks preset selected; manual day selection afterward returns to Custom.
- If Task 28 chooses configurable presets, custom presets override/extend built-ins per decision.
- Preset buttons use real interactive states (Default/Hover/Focus/Active/Disabled).
- Re-check range header rendering in `basic` mode once sidebar is in place, and align with the shared header strategy.

**Manual test (required):** verify preset behavior and layout in both `expanded` and `basic` range configurations; verify deselection on manual day click; verify configurable path if enabled.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add presets sidebar"`

---

### Task 31: Phase 6 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass:**

- [ ] Presets container tokens/spacing
- [ ] Preset button state matrix (selected/unselected)
- [ ] Sidebar alignment for `expanded`
- [ ] Sidebar alignment for `basic` + `range`

**Acceptance criteria:** checked research rows, token-only SCSS, explicit state coverage, JSDoc brevity/content compliance.

**Manual test (required):** Reuse Task 30 scenarios visually against pulled values.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style presets sidebar"`

---

### Task 32: Phase 6 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.presets.spec.ts` (create), `presets.spec.ts` (create)

**Unit tests to cover:** preset computation correctness; preset click updates draft + selected state; manual click returns to Custom; configurable overrides (if enabled). Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 6 presets sidebar unit tests"`

---

### Task 33: Phase 6 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents presets behavior and configurability decision; includes new story variant.

**Manual test (required):** `pnpm dev:docs`.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 6 presets sidebar"`

---

### Task 34: React/Vue wrapper parity check — Phase 6

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Presets-sidebar behavior matches across wrappers.

**Manual test (required):** Repeat Task 30 scenarios through both wrappers.

**Commit:** N/A

---

## Phase 7 — Info banner + footer range summary

`banner` remains independent of `calendarType`. Range summary remains `range`-gated.

### Task 35: banner + range summary implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderBanner.tsx` (create), `helpers/renderFooter.tsx` (modify), `types/types.ts` (modify), `bds-date-picker.tsx` (modify)

**Acceptance criteria:**

- Adds `banner` prop shape with title/message/closable/state/visible support.
- Banner renders above calendar body and works in all `calendarType` values (including `default`).
- Footer summary in `range` mode computes from selected range and is `calendarType`-aware:
  - `basic`: days only
  - `expanded`: days/hours/minutes

**Manual test (required):** validate banner in `basic` and `default`, and summary behavior in `basic` and `expanded` range scenarios.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add info banner and footer range summary"`

---

### Task 36: Phase 7 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-date-picker.scss` (modify)

**Figma research pass:**

- [ ] Banner default + close hover state
- [ ] Banner variant states (if supported)
- [ ] Footer summary spacing with action buttons

**Acceptance criteria:** all research rows checked, token-only SCSS, JSDoc brevity/content compliance.

**Manual test (required):** Reuse Task 35 scenarios visually.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 style info banner and range summary"`

---

### Task 37: Phase 7 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-date-picker.banner.spec.ts` (create)

**Unit tests to cover:** banner visibility/close behavior across all `calendarType` values; range summary behavior for `basic` (days-only) and `expanded` (days/hours/minutes); live updates as range changes. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suite passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 7 banner and range summary unit tests"`

---

### Task 38: Phase 7 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.stories.ts` (modify), `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents banner prop and range-summary behavior; includes new story variant.

**Manual test (required):** `pnpm dev:docs`.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 7 banner and range summary"`

---

### Task 39: React/Vue wrapper parity check — Phase 7

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Banner and range summary behavior is consistent across wrappers.

**Manual test (required):** Repeat Task 35 scenarios through both wrappers.

**Commit:** N/A

---

## Phase 8 — Keyboard navigation, accessibility, RTL

Phase 8 wires and validates grid keyboard traversal, live announcements, and RTL behavior without changing the baseline architecture.

### Task 40: `bds-calendar-grid` arrow-key 2D traversal

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.tsx` (modify)

**Acceptance criteria:**

- Arrow keys, Home/End, and PageUp/PageDown behavior aligns with the agreed interaction model.
- Month-boundary crossing emits the existing `bdsMonthNavigate` event path.
- Out-of-month and disabled cells stay excluded from keyboard focus stops.
- Works for both single and dual grid instances.

**Manual test (required):** verify traversal and month-boundary behavior in single and range dual-calendar scenarios.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add arrow-key 2D grid traversal"`

---

### Task 41: live region + RTL audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `helpers/renderCalendarPanel.tsx` (modify), `bds-calendar-grid.scss` (modify), `bds-date-picker.scss` (modify)

**Acceptance criteria:**

- Adds aria-live month/year announcement updates.
- Completes RTL audit for grid, sidebar, footer, and navigation icons.
- No LTR visual regression.

**Manual test (required):** validate live-region updates and full `dir='rtl'` rendering checks.

**Commit:** `git commit -m "feat(bds-date-picker): EOA-17662 add live region announcements and RTL support"`

---

### Task 42: Phase 8 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.keyboard.spec.ts` (create), `bds-calendar-grid.a11y.spec.ts` (modify), `bds-date-picker.keyboard.spec.ts` (modify)

**Unit tests to cover:** full key traversal, boundary crossing, disabled/out-of-month exclusions, live-region updates, dual-grid independence. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 8 keyboard navigation and a11y unit tests"`

---

### Task 43: Phase 8 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents keyboard model and RTL support.

**Manual test (required):** `pnpm dev:docs`.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 8 keyboard navigation and RTL support"`

---

### Task 44: React/Vue wrapper parity check — Phase 8

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Keyboard traversal and RTL rendering remain consistent across wrappers.

**Manual test (required):** Repeat Tasks 40/41 scenarios through both wrappers.

**Commit:** N/A

---

## Phase 9 — Month/year quick-picker

This phase implements quick month/year drill-down inside `bds-calendar-grid` as an internal view state, not a new public component.

### Task 45: quick-picker interaction model — UX confirmation (blocking gate)

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

### Task 46: month-grid/year-grid generators

**Executor:** @frontend-subagent
**Files:** `date-engine/grid.ts` (modify), `date-engine/types.ts` (modify), `date-engine/__test__/grid.spec.ts` (modify)

**Acceptance criteria:**

- `generateMonthPickerGrid(year, currentMonth)` returns 12 month cells with current-month flag.
- `generateYearPickerGrid(centerYear, currentYear)` returns 12 year cells with current-year flag and applicable disabled handling.
- Both are pure, framework-agnostic, and follow existing generator conventions.

**Manual test (required):** Non-visual — unit tests and `tsc --noEmit`.

**Commit:** `git commit -m "feat(date-engine): EOA-17662 add month-picker and year-picker grid generators"`

---

### Task 47: quick-picker drill-down implementation

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid/types/ICalendarGrid.ts` (modify), `bds-calendar-grid.tsx` (modify)

**Acceptance criteria:**

- Adds internal `view: 'days' | 'months' | 'years'` state.
- Month/year header label becomes interactive and enters month view.
- Month click returns to day view and emits `bdsMonthNavigate`.
- Year click returns to month view for that year.
- Works independently across single and dual grid instances.

**Manual test (required):** verify full drill-down cycle in component playground.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 add month/year quick-picker drill-down"`

---

### Task 48: Phase 9 SCSS + JSDoc audit

**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-calendar-grid.scss` (modify), `bds-calendar-grid.tsx` (JSDoc)

**Figma research pass:**

- [ ] Month grid layout
- [ ] Year grid layout
- [ ] Month/year cell matrix (state x selected x current)
- [ ] Month/year header button states

**Acceptance criteria:** checked research rows, token-only SCSS, JSDoc brevity/content compliance.

**Manual test (required):** Reuse Task 47 scenarios visually against pulled values.

**Commit:** `git commit -m "feat(bds-calendar-grid): EOA-17662 style month/year quick-picker"`

---

### Task 49: Phase 9 unit tests (consolidated)

**Executor:** @testing-subagent
**Files:** `bds-calendar-grid.quickpicker.spec.ts` (create), `date-engine/__test__/grid.spec.ts` (modify)

**Unit tests to cover:** grid-generator correctness; view-switch behavior; month/year selection transitions; dual-grid view-state independence. Coverage-phase only (>=90%).

**Manual test (required):** Non-visual — suites passing at >=90% coverage.

**Commit:** `git commit -m "test: EOA-17662 add Phase 9 month/year quick-picker unit tests"`

---

### Task 50: Phase 9 documentation

**Executor:** @documentation-subagent
**Files:** `bds-date-picker.mdx` (modify)

**Acceptance criteria:** MDX documents quick-picker behavior needed by consumers and keeps it as automatic behavior (no new public props).

**Manual test (required):** `pnpm dev:docs`.

**Commit:** `git commit -m "docs(bds-date-picker): EOA-17662 document Phase 9 month/year quick-picker"`

---

### Task 51: React/Vue wrapper parity check — Phase 9

**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:** Quick-picker behavior remains identical through wrappers.

**Manual test (required):** Repeat Task 47 scenarios through both wrapper playgrounds.

**Commit:** N/A

---

## Final task — consolidated mutation testing across v3

### Task 52: consolidated mutation testing — Phases 5-9

**Executor:** @testing-subagent
**Files:**

- `date-engine/stryker.date-engine.config.mjs` (modify)
- `bds-date-picker/stryker.bds-date-picker.config.mjs` (modify)
- `bds-calendar-grid/stryker.bds-calendar-grid.config.mjs` (modify)

**Acceptance criteria:**

- Mutation testing runs once for v3 scope (not per phase).
- Target >=90% mutation score per target area; survivors require either test fixes or documented exceptions.
- Test gaps found here are closed in existing phase spec files.

**Manual test (required):** run all three Stryker configs and confirm >=90% or documented exceptions.

**Commit:** `git commit -m "test: EOA-17662 run consolidated mutation testing across all v3 phases (5-9)"`

---

## Remaining Open Questions

- **Phase 6 (Task 28):** fixed vs. configurable presets.
- **Phase 9 (Task 45):** final drill-down model confirmation (especially year-click return target).
- **Out of scope:** keyboard-typed date entry in the trigger field remains deferred.
