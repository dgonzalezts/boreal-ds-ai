---
name: stencil-calendar-grid-render-pattern
description: bds-calendar-grid Task 9 render implementation — CSS class names, a11y attribute choices, and click/tabindex guards, needed unchanged by Task 10 (SCSS) and Task 11 (a11y specs)
metadata:
  type: project
---

`bds-calendar-grid.tsx` (EOA-16692 Task 9) implements the controlled `<table role="grid">` render. Facts Task 10/11 executors need without re-reading the whole file:

- BEM class names emitted (Task 10 SCSS must target these exactly): `bds-calendar-grid__header`, `__label`, `__table`, `__day`, `__day--outside`, `__day--today`, `__day--selected`, `__day--disabled`. No `__day--default`/`__day--hover`/`__day--focus` classes — those three states are pure CSS (`:hover`, `:focus-visible`) on the base `__day` class, not JS-driven modifiers.
- Every `<td>` gridcell carries `tabIndex={-1}` unconditionally (including today/selected/current-month cells) — this matches the WAI-ARIA APG reference's default, deferring roving-tabindex management to the unbuilt Phase 8 keyboard-nav integration (`src/utils/a11y/keyboard/navigation/grid-navigation.ts`). Task 11's a11y spec should not expect any cell at `tabIndex 0`.
- Accessible name per cell: `aria-label={formatDisplayDate(cell.date, 'PPPP', locale)}` (date-fns long-format, e.g. "Friday, August 14th, 2026") — not the raw ISO string. Task 11's "accessible name containing the date" assertion should check for this formatted string, not `cell.isoDate`.
- Today marker: `aria-current="date"` (not `aria-current="true"`). Selected marker: `aria-selected={cell.isoDate === selectedDate}` (always present, boolean, per gridcell ARIA convention — not conditionally omitted).
- Nav buttons: bare `bds-button` with `size={BUTTON_SIZES.SMALL}` and a `label` prop ("Previous month"/"Next month") for accessible name — no `variant` set (matches `bds-popover`'s closable-button precedent exactly, default variant). Icons are `ICONS.ChevronLeft`/`ICONS.ChevronRight`.
- Click guard on day cells: `if (!cell.isCurrentMonth || cell.isDisabled) return;` before emitting `bdsDayClick` — out-of-month cells never emit regardless of a future `isDisabled` wiring.
- Component intentionally has zero `@State()` — every render input is a `@Prop`; nav clicks only `emit`, never mutate `year`/`month` locally (controlled pattern, like `bds-tab-group`).
- `@/services` barrel (`packages/boreal-web-components/src/services/index.ts`) re-exports `DayCell`, `WeekdayLabel`, `MonthGrid`, `DateEngineLocale`, and all `date-engine` functions (`getMonthYearLabel`, `getWeekdayLabels`, `formatDisplayDate`, `addMonths`, `subMonths`) directly — no need to import from the deeper `@/services/date-engine` path.
