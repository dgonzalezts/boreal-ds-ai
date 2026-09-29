---
name: calendar-grid-focus-states-figma-gap
description: "Figma does not model focus states for bds-calendar-grid's custom controls (its Focus block copies Hover); the implementation deliberately diverges from Figma to add accessible :focus-visible rings. Do not revert."
---

**Figma has no focus-state source of truth for `bds-calendar-grid`'s custom controls.** For these elements the Figma **Focus** block is a copy of the **Hover** block — it carries the hover background/shadow but no distinct focus ring, and gives no spec for `:focus-visible`. As a result the implementation originally shipped with missing focus indicators and had to be fixed **twice in the same file** by deliberately diverging from Figma for accessibility.

The two divergences (both in `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.scss`):

1. **Month/year picker cells** (`.bds-calendar-grid__picker-cell`) — `:focus-visible` only applied the hover background/shadow and never animated the ring, so `outline-width` stayed `0`. Fixed by applying the day cell's `bds-calendar-day-focus-ring` / `bds-calendar-day-focus-ring-active` mixins (both on the base cell and the `--selected` variant).
2. **The month/year trigger** (`.bds-calendar-grid__label-button`) — worse: it set `outline: none;` with **no replacement**, so there was no focus indicator at all. Fixed by restoring the base outline (`outline: 0 solid $boreal-focus;` + `outline-offset: 1px;`) and applying the same two mixins.

**The day cell is the convention.** `.bds-calendar-grid__day` already had the correct ring and was used as the source of truth for the fix. The reusable pieces are the top-of-file mixins `bds-calendar-day-focus-ring` (`outline-width: 3px; box-shadow: 0 0 0 1px $boreal-white;`) and `bds-calendar-day-focus-ring-active` (adds the inset active shadow), paired with the `bds-calendar-day-interaction-transition` mixin that animates `outline-width`. Every focusable control in this component uses the same base pattern (`outline: 0 solid $boreal-focus` at rest, mixin grows it to `3px` on `:focus-visible`/`:active`) — reuse these, do not invent new visual language.

**Practical warning — do not "restore Figma parity".** The focus rings on `__picker-cell` and `__label-button` are intentional accessibility divergences, not drift. Reverting them to match Figma's Hover-shaped Focus block would remove required focus indicators and re-introduce the bugs above. Treat Figma as authoritative for layout/colour/hover here, but **not** for `:focus-visible`.

**Same gap likely elsewhere.** Any component whose Figma Focus block merely duplicates Hover has no focus-state spec either, so its implementation may be missing a ring. A concrete smell to grep for: **`outline: none` (or `outline: 0`) with no replacement `:focus-visible` ring on the same element.** (Related: `safari-focus-ring-transform-child-ghosting.md` — the reverse pairing rule, where a custom ring must always replace the native outline.)

**Where to look / how to verify:**

- SCSS: mixins `bds-calendar-day-focus-ring` / `-active` / `bds-calendar-day-interaction-transition` at the top of `bds-calendar-grid.scss`; selectors `&__day`, `&__picker-cell`, `&__label-button`.
- Compiled output: `dist/collection/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.css` — each control's `:focus-visible` block must contain `outline-width: 3px;`. Confirmed present for `__label-button`, `__picker-cell` (base + `--selected`), and `__day` (base + `--selected`/`--range-start`/`--range-end`).
