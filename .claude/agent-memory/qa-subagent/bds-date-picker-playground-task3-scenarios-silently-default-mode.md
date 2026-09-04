---
name: bds-date-picker-playground-task3-scenarios-silently-default-mode
description: EOA-17138 Task 15b's calendarType default flip (basic → default) silently changed every pre-existing "withTime (Task 3)" index.html scenario that doesn't pin calendar-type explicitly, breaking dp-preload's original test intent
metadata:
  type: project
---

Found during EOA-17138 Task 15c re-verification (2026-08-28), `packages/boreal-web-components/src/index.html`.

**What happened:** Task 15b flipped `bds-date-picker`'s `calendarType` prop default from `'basic'` to `'default'` (Figma-naming-alignment rationale, "safe pre-GA with no real consumers"). The plan's own retrofit scope (Task 15c's "Minimal retrofit" bullet) pinned `calendar-type="basic"` into the shared spec-file test helpers (`renderDatePicker()`, `bds-date-picker.time.spec.ts`'s local helper) and `bds-date-picker.stories.ts`'s `meta.args` — but **not** into `src/index.html`'s pre-existing "bds-date-picker — withTime (EOA-17138 Task 3)" section (8 pickers: `dp1`, `dp-tokyo`, `dp-la`, `dp-preload`, `dp-autoformat`, `dp-explicitformat`, `dp-fresh`, `dp-stale`), none of which set `calendar-type` explicitly.

**Concrete symptom:** all 8 now silently run under `calendarType="default"`. Confirmed via `console warning` dump on fresh page load — 10 occurrences of the new `` `with-time` has no effect when `calendar-type` is 'default' `` warning (8 Task-3 pickers + 2 new Task-15c scenarios), not the expected 2. `dp-preload` (`value="2026-08-24T08:30:00.000Z"`) is the clearest casualty: its own Task 3 Scenario 3 says "should already show day 24 / 08:30 selected when opened" — instead `dp.value` still holds the raw ISO datetime string but the real `<input>`'s displayed value is now blank (`field.value === ''`), because `default` mode's forced `effectiveWithTime=false` tries to parse a UTC ISO datetime as a naive date and fails. This is the exact same failure signature as the original half-applied bug ([[bds-date-picker-default-withtime-half-applied-bug]]) — but here it's a test-fixture drift, not a component bug: the component is behaving correctly for `calendarType='default'`, the playground markup just no longer matches what its own on-page steps claim.

**Why this matters:** any future manual QA session against this file's Task 3 section will see it fail to match its documented steps, and will burn time re-diagnosing a "regression" that is actually just unpinned `calendar-type` colliding with the Task 15b default flip. Not fixed here — reported back to the dispatching agent per QA-subagent scope (don't silently patch playground scenarios outside the task's own file ownership). The fix, if wanted, is a one-line-per-picker `calendar-type="basic"` addition to those 8 elements, mirroring the spec/story retrofit Task 15c already did elsewhere.

**Negative-case testing workaround used:** since no playground scenario pins `calendar-type="basic"` + `with-time` explicitly, verifying the new warning does NOT fire for `basic` mode required injecting a temporary `bds-date-picker` element via `playwright-cli eval` (`document.createElement` + `appendChild`, removed after the check) rather than reusing an existing scenario.

See `ai-work/plans/EOA-17138-bds-date-picker-v2.md` Task 15b/15c for the default-flip rationale and retrofit scope.
