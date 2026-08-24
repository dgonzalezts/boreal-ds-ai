---
name: stencil-date-engine-tzdate-timezone-conversion
description: date-engine's value.ts uses @date-fns/tz's TZDate for wall-clock<->UTC ISO conversion; TZDate constructor/accessor semantics and DST test technique
metadata:
  type: project
---

`packages/boreal-web-components/src/services/date-engine/value.ts` (EOA-16692 Task 1) exports `combineDateTimeToUTC(datePart, hour, minute, timezone): string` and `extractDateTimeFromUTC(isoUtc, timezone): DateTimeParts` (the `DateTimeParts` interface lives in `types.ts`, per this module's convention of centralizing shared interfaces there rather than inline in the function file — see `component-types-dir-barrel-convention`).

**TZDate semantics** (`@date-fns/tz`, already a dependency at `^1.5.0`): `new TZDate(year, month, date, hours, minutes, timezone)` builds a date whose wall-clock fields are interpreted *in that timezone*; it extends `Date`, so `.toISOString()` still returns the standard UTC ISO string. The inverse, `new TZDate(isoUtcString, timezone)`, then has its own `getFullYear()/getMonth()/getDate()/getHours()/getMinutes()` overridden to return the wall-clock values *in the target timezone* (not UTC) — this is the mechanism that makes the round-trip correct across DST without any manual offset math.

**DST test technique**: don't just assert a round-trip works — assert the *offset itself* differs by comparing `new Date(isoUtc).getUTCHours()` for the same local wall-clock time in winter vs. summer for a DST-observing zone (e.g. `America/Los_Angeles`: 12:00 local → 20:00 UTC in January, 19:00 UTC in July) vs. a non-DST zone (e.g. `Asia/Tokyo`: constant offset year-round). Also worth one explicit spring-forward-gap case (a wall-clock time that doesn't exist, e.g. `America/Los_Angeles` 2026-03-08 02:30) asserting no silent off-by-one-hour instead of asserting a specific "correct" resolution — the library's own gap-resolution choice isn't this module's contract to pin down.
