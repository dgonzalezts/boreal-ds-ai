---
name: bds-date-picker-default-withtime-half-applied-bug
description: FIXED (2026-08-28, same session) — calendarType='default' + withTime=true previously left the trigger field blank + logged a spurious console warning; now resolved via an effectiveWithTime getter
metadata:
  type: project
---

**Status: FIXED and re-verified.** Originally found and reported during Task 15c manual QA; fixed later the same session (by `@frontend-subagent`, evidenced by a new `effectiveWithTime` getter in the component diff) and independently re-verified live via `playwright-cli` against the rebuilt dev server. Field now correctly displays the committed date, no spurious warning, and `rangeUnderflow`/`rangeOverflow` validation (previously also silently inert for this combo via the same root cause) now fires correctly too. Keeping this entry for the root-cause detail below, in case the pattern recurs elsewhere.

Found during EOA-17138 Task 15c manual QA (2026-08-28), `calendarType="default"` combined with `with-time` (`packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`).

**Repro:** open a `bds-date-picker` with `calendar-type="default" with-time`, click any day.
- `dp.value` correctly becomes a naive `YYYY-MM-DD` string (`handleDayClick` hardcodes `buildCommitValue(..., false, ...)` for the default-mode commit path — this part is correct).
- But the slotted `<bds-text-field>`'s displayed text goes blank (`bds-text-field.value === ''`, real DOM `<input>` value also empty) instead of showing the picked date.
- Console logs a spurious warning: `` `value` "2026-08-15" is not a valid UTC ISO datetime — treating it as unset. ``

**Root cause:** `render()` correctly gates the time-selector UI on `showChrome = !isDefaultCalendarType`, satisfying the plan's "time selector... never render[s] regardless of `withTime`'s value" acceptance criterion. But several *derived helpers* still branch on the raw `this.withTime` prop instead of an effective/forced-false value when `calendarType === 'default'`:
- `syncFieldValue()` → `formatValueForDisplay(this.value, ..., this.withTime, ...)` (`utils/value-mapping.ts`) — sees `withTime=true`, tries to parse the naive committed value as a UTC datetime, fails, returns `''`. This is the blank-field bug.
- `warnIfInvalidValue()` — same branch, same mismatch, produces the spurious console warning.
- `valueDate` getter (feeds `min`/`max`/`required` validators) — same branch; likely also silently drops `value` from range-validation consideration in this combo (not separately verified with an actual min/max prop set, but same code path).

**Why this matters:** Task 15c's own acceptance criteria explicitly required `withTime`/`range` to be "force-ignored (documented no-op, not thrown)... never render regardless of those props' values" and separately warned against being "silently half-applied." This is exactly that failure mode — the plan's own risk callout. Reported back to the dispatching agent as a bug for `@frontend-subagent` to fix (did not fix it myself, per QA-subagent scope). Fix likely needs an "effective withTime" (`this.withTime && !this.isDefaultCalendarType`) used consistently everywhere `withTime` is read outside `render()`, not just at the JSX gate.

See also [[dev-pack-pipeline-commands]] and the plan file `ai-work/plans/EOA-17138-bds-date-picker-v2.md` Task 15c for full acceptance-criteria text.

**Resolved (2026-08-28 re-verification):** `@frontend-subagent` fixed this via a new `effectiveWithTime` getter (`false` when `calendarType === 'default'`, else raw `this.withTime`) threaded through `effectiveFormat`, `syncFieldValue`, `warnIfInvalidValue`, and the `valueDate` getter. Re-tested live on `#dp-default-withtime` (`calendar-type="default" with-time timezone="UTC"`): clicking day 15 sets `dp.value === "2026-08-15"` (naive) AND the real `<input>` element's value correctly shows `"2026/08/15"` (previously blank) — checked via `field.shadowRoot?.querySelector('input') ?? field.querySelector('input')`, not just the component property. No "not a valid UTC ISO datetime" (or any "UTC ISO") warning appears anywhere in the console across the whole session. A new intentional `componentWillLoad` warning was added and confirmed: `` [bds-date-picker]: `with-time` has no effect when `calendar-type` is 'default' — it only applies to 'basic'/'expanded'. `` — fires for `calendarType='default'`+`withTime` pickers, confirmed absent for a `calendarType='basic'`+`withTime` picker (tested via a temporary injected element, since no pre-existing playground scenario pins `calendar-type="basic"` explicitly — see [[bds-date-picker-playground-task3-scenarios-silently-default-mode]]). The min/max regression is also fixed: a new `#dp-default-withtime-minmax` scenario (`calendar-type="default" with-time min="2026-08-10" value="2026-08-05"`) now correctly fails `checkValidity()` (`false`) and shows `field.error === true` / `errorMessage === "Date is not allowed."` — identical to the pre-existing basic-mode `#dp-stale-range` min/max scenario — confirming `rangeUnderflow` is no longer silently inert.
