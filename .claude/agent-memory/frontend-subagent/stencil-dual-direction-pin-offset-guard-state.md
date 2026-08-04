---
name: stencil-dual-direction-pin-offset-guard-state
description: Sibling recompute methods sharing a "did inputs change" guard must NOT share the same cache fields, or the second call in the same tick always sees "unchanged"
metadata:
  type: project
---

When adding `updatePinnedColumnOffsetsRight()` alongside the existing `updatePinnedColumnOffsets()` in `bds-table.tsx` (EOA-16000 Task 7, right-edge pinning), the two methods must NOT reuse the same guard/cache instance fields (`_pinOffsetPinnedColKeys`, `_pinOffsetColumns`, `_pinOffsetColumnOrder`). If they did, calling both in sequence within the same render tick would break: the first call sets the guard fields to the current values, so the second call's "did `this.pinnedColKeys`/`this.columns`/`this.columnOrder` change since last computed" check reads false even though the right-side offsets have never been computed. Fixed by giving the right-side method its own fully separate set: `_pinOffsetColumnOrderRight`, `_pinOffsetColumnsRight`, `_pinOffsetPinnedColKeysRight`, `_pinOffsetsByColKeyRight`.

**Also:** `componentDidRender()` must call both offset functions, not just the one the dispatching task description called out (it only mentioned `setupResizeObserver`/`scheduleResizeRecompute`). Without it, toggling a right-pin via the pin-icon click (a state change, not a resize/ResizeObserver event) wouldn't recompute the right offsets until the next forced trigger.

**Why:** discovered while implementing dual-direction (left+right) column pinning that shares Task 6's throttled-recompute pattern — a naive "mirror the existing method" copy-paste silently breaks if the guard state is shared.

**How to apply:** any time a new "shadow" method is added that mirrors an existing method's change-detection guard, give it independent guard state, and check every code path that calls the original for whether the new sibling needs the same call added — not just the paths a task's dispatch message explicitly names.
