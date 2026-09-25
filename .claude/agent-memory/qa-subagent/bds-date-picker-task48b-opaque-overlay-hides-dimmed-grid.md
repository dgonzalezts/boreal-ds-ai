---
name: bds-date-picker-task48b-opaque-overlay-hides-dimmed-grid
description: Task 48b quick-picker overlay's opaque, near-identical-size background fully hid the dimmed day grid it's supposed to be visible through — DOM state (aria-hidden/inert/dimmed class) was all correct, only the visual composition failed. Fixed and re-verified 2026-09-24.
metadata:
  type: project
---

**RESOLVED 2026-09-24.** Fix: moved `border-radius`/`background-color`/`box-shadow` off `&__picker-overlay` (now a transparent, `inset:0`, flex-centering wrapper only) onto `&__picker` (the actual month/year `<table>`) in `bds-calendar-grid.scss`. Re-verified live on `dp-quickpicker-s1`: overlay rect 248x240 with `background-color: rgba(0,0,0,0)` and `box-shadow: none`; picker `<table>` rect only 75x74 (3-column month grid) with the card styling (`rgb(227,227,230)` bg + drop shadow); day grid stays 256x240 at `opacity: 0.4` with class `bds-calendar-grid__day-grid--dimmed`. Screenshot confirms the dimmed day-grid numbers are visible around the small centered month-picker card. All 4 checklist items now pass.

Task 48b (`bds-calendar-grid.tsx`/`.scss`, EOA-17662) makes the day `<table>` stay mounted with a `--dimmed` class (`opacity: 0.4`) while `.bds-calendar-grid__picker-overlay` renders on top. Manually measured via `getBoundingClientRect()`: the overlay's rect (248x240) is within a few px of the dimmed day-grid's rect (256x240) — same position, near-identical size — and the overlay's `background-color` is `var(--boreal-ui-base-light)` at `opacity: 1` (fully opaque).

Net effect: the dimmed day grid is 100% visually obscured by the overlay. A screenshot shows the overlay panel with no hint of the day grid underneath — visually indistinguishable from Task 48's old in-place-replacement behavior, even though the DOM technically satisfies every Task 48b criterion (`aria-hidden="true"`, `inert`, `--dimmed` class with `opacity: 0.4` all present and correctly toggling).

**Why this matters:** don't rely on DOM/attribute checks alone to verify a "dimmed/visible underneath" visual requirement — a `getBoundingClientRect()` + computed `backgroundColor`/`opacity` check on the overlay itself (or a screenshot) is required to catch an overlay that's sized/opaque enough to fully hide what it's supposed to let show through. This bug reproduced in Task 48b's initial implementation on 2026-09-24, reported to `@frontend-subagent` via the team lead, not yet fixed as of this writing.

**How to apply:** for any future overlay/dimming acceptance criterion, always pair the DOM-attribute check with a geometry+opacity check (or screenshot) of the actual overlay vs. the element it's supposed to dim-but-not-hide.
