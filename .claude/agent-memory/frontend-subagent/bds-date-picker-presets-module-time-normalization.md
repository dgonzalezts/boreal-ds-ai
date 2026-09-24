---
name: bds-date-picker-presets-module-time-normalization
description: date-fns endOfMonth/endOf* return 23:59:59.999 (seconds+ms), which conflicts with bds-date-picker's minute-only time model — presets.ts normalizes every boundary to local midnight before deciding whether to apply the 00:00/23:59 full-day bounds.
metadata:
  type: project
---

`utils/presets.ts` (EOA-17662 Task 29, `bds-date-picker`) computes six built-in date-range presets (Today/Yesterday/Last 7/Last 30/This month/Last month) with an optional uniform full-day time bound (`00:00` start, `23:59` end).

Non-obvious pitfall: `date-fns`'s `endOfMonth` (and `endOfDay`/`endOfWeek` etc.) returns an instant at `23:59:59.999` — seconds and milliseconds included. `bds-date-picker`'s time model is minute-only (confirmed via `helpers/renderTimeSelector.tsx` — `HOUR_OPTIONS`/`MINUTE_OPTIONS` only, no seconds selector anywhere). Using `date-fns`'s raw `endOfMonth` result directly as a preset boundary would silently carry stray seconds/ms that don't match the component's own value contract.

**Fix pattern:** normalize every raw-computed boundary down to local midnight first (`toDayStart` — reconstruct via `new Date(y, m, d)`), regardless of which `date-engine` primitive produced it. Only then, if `withTime` is requested, bump the `end` boundary to an explicit `23:59` via a second local reconstruction (`toFullDayEnd` — `new Date(y, m, d, 23, 59)`), never trusting a library's own "end of day" instant.

**Why:** keeps the module's non-time-mode output ("just the calendar day") and time-mode output ("exactly 00:00/23:59, uniformly across all presets") both correct without a special case for "This month"/"Last month" (the only two presets whose raw arithmetic touches a month-boundary primitive).

**How to apply:** any future date-range/date-boundary computation in this component (or a sibling minute-only-time component) that calls `date-engine`'s `startOfMonth`/`endOfMonth` (added in this same task, thin `date-fns` wrappers with no bespoke normalization of their own) must re-normalize the result the same way — the wrappers intentionally stay "thin" (no minute-only awareness baked in), so normalization is the caller's job every time, not something to expect from `date-math.ts` itself.

Also confirms: closed string-literal-set types local to one component's internal (non-`@Prop()`) computation — e.g. `BuiltInPresetKey`/`PresetKey` here — still belong in that component's `types/enum.ts` as a `const`-object + derived type (mirroring `RANGE_BOUND`/`RangeBound`, which is likewise never a `@Prop()`), not declared inline in the `utils/*.ts` file that consumes them. See [[component-enum-prop-const-object-pattern]] for the `@Prop()`-specific variant of this same convention.
