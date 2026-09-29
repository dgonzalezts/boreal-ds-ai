# ADR 0017 — `bds-date-picker` keyboard month-boundary navigation

**Date:** 2026-09-28
**Status:** Accepted

---

## Context

The [ARIA APG date-picker pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) lets arrow keys cross month boundaries: its reference `moveFocusToNextDay()` detects that the next day falls outside the rendered month and re-renders the grid for the new month instead of stopping at the edge. `bds-calendar-grid`'s day grid previously did the opposite — arrow keys were confined to the displayed month (an edge move wrapped within it), and the only keyboard routes to another month were PageUp/PageDown and the header buttons.

That was defensible while a calendar showed a single month, but `calendar-type="expanded"` renders two consecutive months side by side. The month immediately adjacent to the grid's edge is usually already on screen, so confining arrows to one of two visible months is both surprising and inconsistent with the APG reference.

Making arrows cross boundaries raised two design questions:

1. How should the **generic** grid-navigation utility report "focus is leaving my populated area" without acquiring any date/calendar knowledge?
2. What does "crossing" mean when the destination month is **already rendered by a sibling grid**, versus when it is not rendered at all?

A related, previously latent defect surfaced while implementing this: in the day view, PageUp/PageDown routed into the same handlers the header buttons use and bypassed the `prevDisabled`/`nextDisabled` guards those buttons enforce. That is addressed here as Decision C because it is part of making month navigation from the keyboard coherent.

---

## Non-Goals

- Does not change Home / End / Ctrl+Home / Ctrl+End. They intentionally remain within the displayed month (row start/end, grid start/end) and are not routed through the boundary mechanism.
- Does not change the shared utility's behavior when `onBoundary` is omitted or `wrap` is `false` — grid navigation wraps/confines exactly as before.
- Does not add a consumer-facing prop or attribute. The only new public surface is a `@Method()` on `bds-calendar-grid` (see Consequences).
- Does not change the month/year quick-picker's own PageUp/PageDown year-window navigation, which already had its own fully-disabled guards.

---

## Options Considered

### Rejected — detect boundaries in the consumer via `onNavigate`

`onNavigate(row, col, items)` is called by the shared utility *instead of* applying focus, so in principle a consumer could take over every move and decide for itself when focus left the month. But the callback only ever fires with a cell the utility has already resolved as an in-grid target. There is no `onNavigate` invocation meaning "there is no cell in this direction" — the utility simply returns early. A consumer cannot distinguish "no move possible" from "moved within the grid" without duplicating the utility's own position/row resolution. Rejected.

### Rejected — sentinel cells

Represent the boundary as a sentinel/placeholder entry in the item matrix and act when focus lands on it. This leaks a fake element into the grid's DOM and identity model, complicates roving-tabindex indexing (the utility indexes the flat item list), and every other operation would need to filter it out. Disproportionate and error-prone. Rejected.

### Rejected — `wrap: false` plus a consumer-side row-wrap reimplementation

Disable wrapping at the utility and re-implement horizontal row-wrap (last column → first column of the next row) inside `bds-calendar-grid`. This moves correct, already-tested generic behavior into the component and creates a second, divergent implementation of it. Rejected.

### Chosen — a generic `onBoundary` extension point

Add `onBoundary?: (direction: GridBoundaryDirection) => void` to the shared grid-navigation config. The utility fires it only at the precise point where it would otherwise wrap past its own populated bounds, then stops — the callback owns focus and state from there. The utility stays date-agnostic (it reports a direction, never a date) while giving the consumer everything it needs.

### Rejected (focus hand-off) — always shift the month window on a boundary crossing

Simplest for `expanded`: any boundary crossing advances or retreats the two-month window. But when the destination month is already rendered by the adjacent calendar, shifting the whole window would move a month the user can already see, discarding a visible grid for a redundant re-render and dropping the focused date. Rejected in favor of handing focus into the already-visible sibling.

---

## Decision

### Decision A — shared `GridNavigationConfig.onBoundary` extension point

`GridNavigationConfig.onBoundary?: (direction: GridBoundaryDirection) => void` is added to the generic grid-navigation utility (`utils/a11y/keyboard/navigation/grid-navigation.ts`; type in `utils/a11y/keyboard/types/IKeyboardController.ts`). It fires only when an arrow move would wrap past the grid's own populated bounds — i.e. only when `wrap` is `true` and no populated row exists in the requested direction (`findRowWithCells(..., wrap: false) === -1`). When it fires, the utility does not move focus; the callback takes over focus and state.

`bds-calendar-grid` passes `onBoundary: this.handleGridOutOfBounds` alongside its existing `wrap: true`. The utility currently has a **single component consumer** (`bds-calendar-grid`), so this extension point's blast radius today is that one component. It is nonetheless defined generically — direction is a `GridBoundaryDirection` (`'left' | 'right' | 'up' | 'down'`, from `GRID_BOUNDARY_DIRECTION`) with no date semantics — so future grid consumers can reuse it. `bds-calendar-grid` maps each direction to a day offset (`left: -1`, `right: +1`, `up: -7`, `down: +7`).

### Decision B — expanded focus hand-off, with window-shift fallback

When a day-grid boundary crossing would land in a month that is **already displayed by the sibling calendar** (`calendar-type="expanded"`), focus is handed off into that sibling and the two-month window is left unchanged. When the crossing leaves the outer edge of both displayed months, the window shifts as before. `basic` and `default` have no sibling, so they always shift.

Mechanically:

- `CalendarGridMonthNavigateDetail` gains an optional `focusDate?: string` (naive ISO `YYYY-MM-DD`). `handleGridOutOfBounds` sets `this._pendingFocusIsoDate` to the crossing date and emits `bdsMonthNavigate` with `focusDate` set.
- `bds-calendar-grid` exposes `@Method() focusDate(isoDate: string | null): Promise<boolean>`. It moves the day grid's roving-tabindex focus to `isoDate` (clamping to the nearest enabled day when the exact date is disabled) and resolves whether focus was actually applied.
- `bds-date-picker`'s `handleMonthNavigate` first calls `tryHandOffFocus(slot, detail)`. That returns `false` for non-expanded types or a missing `focusDate`; otherwise it checks whether `focusDate` falls in the sibling calendar's displayed month (the next month when the crossing came from the primary/left grid, the current month when it came from the secondary/right grid). If so it calls the sibling's `focusDate`; when that resolves `true` it clears the origin grid's pending focus; when it resolves `false` (the sibling cannot take focus — e.g. its quick-picker overlay is open) it falls through to `applyMonthNavigate`. If the target month is not the sibling's, it returns `false` and `applyMonthNavigate` runs directly.
- `applyMonthNavigate` keeps its existing meaning: it shifts the window, anchoring the secondary slot one month earlier. In expanded, a crossing off the right edge (from the secondary/right calendar) or the left edge (from the primary/left calendar) shifts the window by one month; the inner edges are handled by hand-off.

The fallback is deliberate: a hand-off that cannot complete must never dead-end. If the sibling cannot focus the date, the crossing degrades to the ordinary window shift, which is always available.

**`focusDate` contract (recorded as part of this date-picker series).** `focusDate` resolves `true` only when the requested date — or its `min`/`max` clamp — exists as an enabled cell in the currently displayed month. Otherwise it resolves `false` and leaves focus untouched; it does not silently focus some other date. `focusDate(null)` clears any pending focus and resolves `false`. This contract is what makes the fallback reliable: the caller can treat `false` as "the sibling could not take this date" and shift the window instead. The rejected alternative would have had `focusDate` coerce the request into *some* neighbouring date and always resolve `true`, which would leave the hand-off unable to detect that the sibling cannot show the requested date — reintroducing the dead-end this contract exists to prevent.

### Decision C — PageUp/PageDown guard parity

`handleNextClick`/`handlePrevClick` now early-return on `nextDisabled`/`prevDisabled`. Previously, in the day view PageUp/PageDown routed straight into those handlers and bypassed the guards the header buttons enforce.

- In `expanded`, the primary (left) calendar is rendered with `nextDisabled` forced `true` and the secondary (right) with `prevDisabled` forced `true`, so PageUp/PageDown now mirror the header buttons: forward only from the right calendar, back only from the left.
- In every variant, when the adjacent month is fully outside `min`/`max` (fully disabled), the key is now a no-op instead of navigating into a month with no selectable days.
- The quick-picker's own month/year views still route PageUp/PageDown to the picker year-window handlers, which already had their own fully-disabled guards; this decision only aligns the day view.

---

## Consequences

- **New public `@Method()`:** `bds-calendar-grid.focusDate(isoDate: string | null): Promise<boolean>` joins the component's public API (and the framework wrappers generated from `custom-elements.json`). Its return type is load-bearing — `false` is the signal the parent uses to fall back to a window shift — so it must not be changed to `void`. It resolves `false` for `null`, for a date absent from the displayed month (and with no `min`/`max` clamp present in it), and for a non-day grid view.
- **`focusDate`'s Option B contract (success only when the requested date or its clamp exists in the displayed month; otherwise `false` with focus untouched)** is the hand-off's failure detector. Changing it to always resolve `true` would silently break the `expanded` fallback.
- **A generic "boundary escape" extension point now exists in shared keyboard infrastructure.** Future grid consumers that must act when focus leaves their populated area should use `onBoundary` rather than reimplementing position logic. Direction is the only contract; the utility remains date-agnostic.
- **Arrow keys now cross month boundaries in the day grid** — a behavior change from "arrows stay within the displayed month." In `expanded`, arrows cross into the visible sibling; at the outer edges, and in `basic`/`default`, the month window changes.
- **Home / End / Ctrl+Home / Ctrl+End remain within the displayed month, by design.** They are `moveToEdge` operations and are not routed through `onBoundary`.
- **When `onBoundary` is omitted or `wrap` is `false`, the utility wraps/confines exactly as before.** The shared spec covers both the boundary-fires path and the unchanged-wrap path.
- **PageUp/PageDown are now consistent with the header buttons** across all calendar types, including no-oping when the adjacent month is fully outside `min`/`max`.
