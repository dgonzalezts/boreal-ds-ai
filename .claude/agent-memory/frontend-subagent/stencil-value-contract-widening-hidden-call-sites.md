---
name: stencil-value-contract-widening-hidden-call-sites
description: Widening a committed value's string shape (e.g. naive-ISO-date to UTC-ISO-datetime) breaks every call site that silently assumed the narrower shape, not just the ones a plan's Files list names
metadata:
  type: project
---

When a task changes what shape a component's committed `value` can take at runtime (e.g. `bds-date-picker`'s range `{ start, end }` going from always-naive-ISO-date strings to full UTC-ISO-datetime strings once `withTime` applies to range mode, EOA-17662 Task 23), grep every reader of that value — not just the ones a plan's Files list names — for a shape assumption baked in as a hardcoded literal or an unconditional call to a narrower-shape-only parser.

Two real regressions found this way in `bds-date-picker.tsx`, neither named in the plan's file list or acceptance criteria, both invisible to `tsc`/unit tests since the narrower-shape code path still type-checks fine against the wider string type:

- `resolveDraftDisplayMonth()`'s range branch called `resolveDisplayMonth(..., false, ...)` with `withTime` hardcoded to `false` — once range values could be UTC datetimes, `isValidNaiveISODate()` on them always failed, silently breaking "reopen the popover anchored on the committed month."
- `syncFieldValue()`'s range branch called `formatRangeForDisplay()` (naive-date-only) — once range values could be UTC datetimes, the trigger field's displayed text silently went blank.

Both were single-line fixes (thread the already-existing `effectiveWithTime`/an analogous time-aware formatter through), but both required tracing every reader of the widened value, not trusting the plan's own "files to modify" list as exhaustive — a plan's grounding-check pass can miss call sites just as easily as an implementer can.

**How to apply:** whenever a task's acceptance criteria describes a value contract getting wider (a union gains a member, a string format gains a new valid shape), grep the whole component for every place that value is read/parsed before implementing, and check each one against the new shape — don't stop at the plan's named files.
