---
name: bds-calendar-grid-picker-cell-figma-state-matrix
description: Full Figma State x Selected x State-Actual resolution for _DatePickerMonthYear (node 14:23473), used for bds-calendar-grid's month/year quick-picker cells
metadata:
  type: project
---

Pulled 2026-09-24 for EOA-17662 Task 49. `_DatePickerMonthYear` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, node `14:23473`) is a 5(State) x 2(Selected) x 2(State Actual) = 20-variant component set, reused identically for both picker cells (`14:24131`/`14:24151`) and the day/month/year header label pill.

Resolved values (Default/unselected already existed; documenting the rest):

- Hover (unselected): `bg-ui-default-lighter` (#f7f7f8) + `$boreal-depth-box-shadow-xs` (matches the existing `bds-hover-shadow` mixin exactly).
- Focus (unselected): **byte-identical style block to Hover** in Figma's own generated code — same bg, same drop-shadow, no distinct ring. Implemented `:focus-visible` to alias `:hover` rather than inventing a ring not in the design. Confirmed via two independent `get_design_context` pulls (nodes `14:23482` Hover vs `14:23490` Focus).
- Active (unselected): `bg-ui-default-lighter` + inset shadow `inset 0 1px 2px 0px rgba($boreal-black-rgb, 0.15)` — no outer ring, unlike day cells' `bds-calendar-day-focus-ring-active` (which adds an `outline-width:3px` ring on top). Do not reuse that day mixin here; the inset-only shadow is correct for picker cells.
- Disabled (unselected): bg unchanged (`$boreal-ui-inverse`), text `$boreal-text-disabled`.
- Selected (Default): bg `$boreal-ui-primary-base`, text `$boreal-text-inverse`.
- Selected+Hover/Focus: bg `$boreal-ui-primary-dark` + `$boreal-depth-box-shadow-xs`.
- Selected+Active: bg `$boreal-ui-primary-dark` + inset shadow (same inset value as unselected Active).
- Selected+Disabled: bg `$boreal-ui-primary-light`, text stays `$boreal-text-inverse` — mirrors the day-grid `--day--disabled.--day--selected` precedent exactly (same token pairing).
- State Actual (current month/year, unselected): dashed 1px outline, `$boreal-stroke-primary-base`, `outline-offset: -1px` — identical treatment to the day grid's `--today::after`.
- State Actual + Selected: same dashed outline but recolored to `$boreal-stroke-inverse` (white) since the cell bg is now the primary-base blue — mirrors `--day--today` recoloring to `$boreal-text-inverse` when `--selected` is also present.
- State Actual never got an explicit pull crossed with Hover/Focus/Active/Disabled — treated as an independent `::after` overlay (like day's `--today`), so it composes automatically with any interaction-state background change without needing 4x more combination pulls. Consistent with existing `--day--today` precedent in this same file.

Cell sizing: both month (`14:24131`) and year (`14:24151`) grids render 32px-tall cells (`$boreal-spatial-layout-l`, same token day cells use) at ~48-50px width; the closest real token is `$boreal-spatial-layout-xl` (48px) — used for `.picker-cell` width. Row/column gap is a uniform 4px (`$boreal-spatial-gap-2xs`) in both directions (unlike the day grid's asymmetric 4px/2px `border-spacing`).

Card container (`.picker`, the `<table>`): 12px padding (`$boreal-spatial-padding-s`) around the grid, applied directly to the `<table>` element (valid with default `border-collapse: separate`). Corner radius/exact arrow geometry could NOT be independently re-verified beyond what Task 48b already implemented — Figma exports the whole card+shadow+arrow as one flattened SVG raster (`_DatePickerMonths`' own background layer), not decomposed CSS properties, so `$boreal-radius-s` and the `bds-popover`-ported arrow technique remain the best available token-based approximation.

No `isSelected` field exists anywhere in `MonthPickerCell`/`YearPickerCell` (`services/date-engine/types.ts`) — the `--selected` SCSS block written for this state matrix is fully defined but currently **unreachable** (no class ever applies it). This is a real gap between the design and the data model, out of scope for a SCSS-only task; flagged back to the plan owner rather than silently adding a prop.

See also [[bds-date-picker-banner-footer-figma-audit]] for a similar "flattened SVG asset, can't decompose exact px" limitation pattern.
