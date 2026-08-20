---
name: bds-button-hover-focus-shadows-fixed-size-tokens
description: bds-button's hover-shadow, focus-ring, and sm-variant padding/icon-size are fixed absolute values that don't scale down when --bds-button-width/height/min-height are overridden well below the size variant's natural floor — found on bds-date-picker's 16px popover close button (EOA-16692)
metadata:
  type: project
---

`bds-button-logic` mixin's `:hover` and `:focus` states (`bds-hover-shadow` → `$boreal-depth-box-shadow-xs`, `bds-focus-ring` → `$boreal-depth-box-shadow-focus`, both in `packages/boreal-web-components/src/styles/_interactions.scss`) resolve to fixed absolute `box-shadow` values independent of button size:

- hover: `0px 1px 2px 0px rgba(28,31,34,0.15)`
- focus-visible: `0px 0px 0px 1px #fff, 0px 0px 0px 3px #98b4ff` (effectively +4px per side)

These are proportionate at a button's *natural* size-variant floor (sm=24px, md=32px, lg=44px, per `--bds-button-min-height` default in `bds-button.scss`), but `bds-date-picker.scss`'s `.popover-header__close` overrides `--bds-button-width/height/min-height` to 16px — well below the `sm` variant's natural 24px floor. At 16px:

- Border-radius (4px, `$boreal-radius-xs`, unchanged) becomes 25% of box size vs 12.5% at natural 24px sm / 6.25% at the calendar nav's 32px md buttons — visibly more "pill-shaped."
- The focus ring's fixed 4px total spread swells the visual footprint by ~50% (16px→24px) vs ~12.5% at a natural 32px button — looks bloated/disproportionate, confirmed via screenshot.
- The `sm` variant's `content-padding`/icon `font-size` (from `bds-button-size` mixin, calibrated for the natural 24px sm box) also don't rescale: measured the icon glyph inside the 16px override sitting off-center by ~2.26px horizontally and overflowing the button's own right edge by ~0.5px (`getBoundingClientRect()` on `i.bds-icon-close` vs the button box). Confirmed via real hover (`mousemove` + `:hover` check) and real keyboard Tab (`:focus-visible` check) — not CDP force-pseudo-state, per [[cdp-force-pseudo-state-unreliable]].
- Comparison: the calendar-grid's prev/next nav `bds-button`s render at their natural default (md, 32px, no override) and show none of this — icon perfectly centered, hover/focus shadow proportionate.

**Why:** `--bds-button-width/height/min-height` only override the outer box dimensions; they don't touch the size variant's own padding, icon-size, or the interaction mixins' box-shadow spread, all of which are separate fixed values. Shrinking a button below its natural size-variant floor via these CSS custom properties alone is not a safe operation without also compensating padding/icon-size/shadow spread.

**How to apply:** any future task overriding `--bds-button-width/height/min-height` below a size variant's natural floor should flag this as a likely visual defect, not just check that the box itself renders at the target dimensions. Related to [[bds-button-height-hook-clamped-by-min-height]] (same override mechanism, different symptom).
