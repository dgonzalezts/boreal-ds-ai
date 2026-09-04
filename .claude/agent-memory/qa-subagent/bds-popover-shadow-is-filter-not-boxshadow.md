---
name: bds-popover-shadow-is-filter-not-boxshadow
description: bds-popover's drop shadow is a CSS `filter: drop-shadow(...)`, not `box-shadow` — asserting computed `boxShadow` on the host returns "none" even when the shadow renders visually
metadata:
  type: project
---

`bds-popover`'s outer container (the `bds-popover` host element itself, class `popover`, light DOM — no shadow root) renders its drop shadow via `filter: drop-shadow(rgba(0, 0, 0, 0.15) 0px 2px 8px)`, not `box-shadow`. `getComputedStyle(popoverEl).boxShadow` returns `"none"` even while the shadow is fully visible on screen — check `filter` instead when scripting a computed-style assertion against a popover container.

Also confirmed while auditing `bds-date-picker`'s `calendarType="default"` mode (EOA-17138 Task 15d): `border-radius: 2px` on the same host is the correct baseline (small, easy to mistake for "no radius" if eyeballing a screenshot) — it matched identically between `basic` and `default` modes, along with `background-color`, `padding` (12px 24px on `.popover-header`/`.popover-content`), and `filter`. `default` mode's day-grid cell styling (border-radius, font, color) was also byte-identical to `basic` mode's — expected, since both modes render through the same shared `bds-calendar-grid` component instance, so a per-cell SCSS audit across `calendarType` values is largely redundant by construction; the real risk area for a "no header/footer chrome" mode is the outer container's corner-radius/shadow surviving with no header/footer siblings to anchor against, which this technique verifies directly.

**How to apply:** when a QA task asks to confirm popover container styling (radius/shadow) is unaffected by a structural change (e.g. removing header/footer chrome), pull `getComputedStyle` values for `border-radius`, `filter`, `background-color`, and `padding` on the `bds-popover` element directly via `playwright-cli eval`, and diff them against a known-good reference scenario in the same page — don't rely on screenshot comparison alone for this class of check.
