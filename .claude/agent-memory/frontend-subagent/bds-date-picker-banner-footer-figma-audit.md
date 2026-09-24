---
name: bds-date-picker-banner-footer-figma-audit
description: EOA-17662 Task 36 Figma pull findings for bds-date-picker's banner wrapper and footer range-summary label — unbound literal padding, footer/header gap token mismatch, and a popover-footer layout discrepancy left unfixed due to file scope.
metadata:
  type: project
---

Figma node `165:40701` (`calendarPicker` instance, file `rtiE5zGA4aoOuxIQMgfD6h`) pulled via `get_metadata`/`get_design_context` for Task 36 of `ai-work/plans/EOA-17662-bds-date-picker-v3.md`. Three non-obvious findings worth knowing before re-touching this area:

1. **Banner outer-frame padding (10px) has no bound Figma variable.** `get_variable_defs` on node `158:176533` ("Banner ", the frame wrapping the `bds-banner` instance) returned `{}` — the `p-[10px]` in the pulled code is a raw literal, not backed by any token. Since the project requires token-only spacing and no available `$boreal-spatial-padding-*` token equals 10px (nearest are `-xs`=8px and `-s`=12px, both 2px off), resolved to `$boreal-spatial-padding-xs` (8px) as the nearest token and documented the 2px approximation rather than hardcoding 10px.

2. **Footer's label/value gap (4px) differs from the header's Start:/End: group gap (2px).** The header's `.bds-date-picker__range-group` already uses `$boreal-spatial-gap-3xs` (2px) between a bound's label and value. The footer's "Range labels" node (`158:176549`, and the identical `Basic Footer` node `158:176540`) pulls a distinct 4px gap — matching `$boreal-spatial-gap-2xs`, not `-3xs`. Don't assume the footer's label/value spacing reuses the header's token just because the pattern looks the same — verify each region's own pulled value independently.

3. **Deferred/unfixed: Figma's footer layout hugs the button row; the live implementation spreads the summary to the far left.** Figma's pulled Basic/Expanded Footer frames use `justify-content: flex-end` with the range-summary block set to `flex: 1 0 0; text-align: right` — visually placing "Range: X days" immediately before the Clean/Cancel/Apply buttons. The actual `bds-popover.scss` `.popover-footer` rule uses `justify-content: space-between` for its two footer slots (`footer-helper`/`footer-button`), which pushes the summary to the far-left edge instead. Fixing this would require editing `bds-popover.scss` (shared by every `bds-popover` consumer, not just `bds-date-picker`) — out of Task 36's file scope (`bds-date-picker.scss` + helpers/types/constants only). Left as an explicitly documented, unresolved visual discrepancy rather than silently expanding scope; a fix would need either a `--popover-footer-justify` custom property or a deliberate, separately-scoped change to the shared popover.

4. **Hidden Figma frames are still pullable.** Nodes marked `hidden="true"` in `get_metadata` (the `Banner`, `Basic Footer`, and `Header Basic Time picker` frames in this instance) still return full, high-fidelity data from `get_design_context` — hidden-in-this-variant is not the same as inaccessible. Always try the direct pull on a hidden node's ID before falling back to "can't inspect, using mockup screenshots instead."

See also [[bds-date-picker-presets-figma-token-mapping]] for the sibling presets-sidebar Figma audit from the same plan.
