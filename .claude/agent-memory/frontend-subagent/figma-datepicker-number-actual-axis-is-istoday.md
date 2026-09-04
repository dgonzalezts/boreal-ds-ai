---
name: figma-datepicker-number-actual-axis-is-istoday
description: Figma DatePickerNumber component's `actual` boolean variant axis is the isToday flag, not a spec-vs-implementation toggle
metadata:
  type: project
---

In the `[BOR] DSG COMPONENTS → FORMS` library (fileKey `rtiE5zGA4aoOuxIQMgfD6h`), the `DatePickerNumber` day-cell component (node `14:23554`) exposes a Component Properties axis literally named `actual: boolean`. It is easy to misread as "spec column vs. actual-implementation column" (a screenshot capture earlier in EOA-17138 described it that way). It is not — every `actual=true` variant adds a `1px dashed var(--stroke/primary-base)` border on top of whatever `state`/`selection`/`type` combo it's paired with, which is exactly `bds-calendar-grid.scss`'s pre-existing `--today` treatment. So `actual` is Figma's naming for `isToday`, crossed with every other axis (state × selection × type), not a separate concern.

Also relevant on that same node: `selection: 'Partial'` (→ `isInRange`) shows no directional/positional bleed difference across `type: 'Default'|'Start'|'End'|'Full'` — the "Bkgd" rectangle some `Partial`+`Start`/`End` variants render is the same flat color as the day cell itself, so it's visually a no-op, not a cap/pill shape. `selection: 'Selected'` (→ `isRangeStart`/`isRangeEnd`) likewise renders identically across `Start`/`End`/`Full` — solid `$boreal-ui-primary-base` fill, no distinct endpoint shape. Confirmed via [[feedback_figma_first_for_styling_tasks]]-style full-dump pull during Task 19 SCSS work.

**Why:** saved so a future session styling range/multi-day calendar variants from this same Figma library doesn't re-litigate what `actual` means or waste time hunting for a start/end cap shape that doesn't exist in this design.

**How to apply:** when pulling `DatePickerNumber` (or similarly-named `_DatePickerNumber` instance nodes) via `get_design_context`, treat `actual=true` as `isToday`, and don't expect `type`-axis-driven shape differences for `Partial`/`Selected` — expect only interaction-state (`Hover`/`Focus`/`Active`/`Disabled`) color differences.
