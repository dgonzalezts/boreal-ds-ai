# Follow-up ticket from EOA-19936 — `bds-popover` defects

**Source:** `ai-work/testing/failure-modes/bds-popover.md`
**Suggested project:** EOA · type: Bug · component: `bds-popover`

## Summary

Defects found while increasing unit test coverage (EOA-19936). A test for each fails against current source, so fix first, then add the test.

## Defects

- **FM-33:** `activation="active"` registers anonymous listeners that cannot be removed. Switching activation modes leaves a double toggle.
- **FM-34:** setting `managed` to true at runtime does not remove the click listeners or the keyboard binding.
- **PD-06:** `setAnchorElement(null)` logs a warning, then throws a `TypeError` from `subscribe(null)`. The warning text suggests rejection was intended, so it should return without throwing. Contract needs confirming.
- **FM-14:** a start placement with `arrowData.x` undefined pins the arrow at 20px (`undefined !== 0` is true). Absent offsets should clear the axis.
- **FM-15:** after re-anchoring while open, the new anchor is stamped `aria-expanded="false"` although the popover is open.

## Not in scope

- Click on `<html>` not dismissing popovers (FM-20 to FM-25) is already fixed in commit `838b6600` on `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`, with `bds-popover.click-outside.spec.ts`.
- `pending-decision` rows (PD-04, PD-05, PD-07 to PD-18) need a contract ruling before they are bugs.

## Acceptance criteria

- Each defect above is fixed in `bds-popover.tsx`.
- A unit test per defect, failing before the fix and passing after.
- Existing `bds-popover` specs still pass; coverage stays at or above 80%.
- Stryker mutation score is at least 90% once the fixes land.
