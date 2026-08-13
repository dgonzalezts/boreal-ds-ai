---
name: stencil-date-fns-compareasc-number-not-literal-union
description: date-fns's compareAsc is typed to return `number`, not `-1 | 0 | 1`, despite only ever returning those three values at runtime — narrow explicitly, don't cast
metadata:
  type: project
---

`date-fns@4`'s `compareAsc(dateLeft, dateRight)` is typed to return plain `number`, even though its documented/runtime behavior only ever produces `-1`, `0`, or `1`. A `date-engine` function whose own signature promises `-1 | 0 | 1` (e.g. a `compareDates` comparator, per `ai-work/plans/EOA-16692-bds-date-picker-v1.md` Task 4's acceptance criteria) fails `tsc` with TS2322 if it returns `compareAsc(...)` directly.

**Why:** Boreal DS's no-implicit-`any`/explicit-typing convention makes a blind `as -1 | 0 | 1` cast the wrong fix — it would silently accept a future date-fns version returning some other magnitude. An explicit `if (result > 0) return 1; if (result < 0) return -1; return 0;` clamp is self-documenting and safe against that drift.

**How to apply:** Any `date-engine` (or future date-math) function delegating to `compareAsc` (or similarly "documented tri-state, typed as `number`" date-fns functions) for a literal-union return type needs this explicit narrowing wrapper, not a type assertion. See `packages/boreal-web-components/src/services/date-engine/date-math.ts`'s `compareDates`.
