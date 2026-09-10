---
name: bds-date-picker-empty-format-string-crash
description: bds-date-picker's format="" (empty string, distinct from omitting the prop) crashes date-fns formatting universally across web components, React, and Vue
metadata:
  type: project
---

`bds-date-picker.tsx`'s `effectiveFormat` getter (around line 591) does `if (this.format !== undefined) return this.format;` before falling back to `DEFAULT_DATE_TIME_FORMAT`/`DEFAULT_DATE_FORMAT`. An explicitly-set empty string (`format=""` in React/Vue JSX, or a bare `format=""` attribute in HTML/Lit) passes the `!== undefined` check and is returned as-is, so date-fns's `format(date, '')` is called downstream in `value-mapping.ts`'s `formatDisplayDate`/`formatRangeForDisplay`/`formatRangeValueForDisplay`/`formatDraftForDisplay`. date-fns throws `TypeError: null is not an object (evaluating '<formatStr>.match(<tokenRegex>).map')` on an empty format string.

Confirmed universal — reproduces identically in the raw web component (injected via a temporary DOM element, not committed to `src/index.html`), React, and Vue, on both Chromium and WebKit. Effects: the popover header text and the trigger field's displayed value silently render as `''` (crash is swallowed by the framework's render cycle), but the underlying `value`/`bdsChange` commit is unaffected — selecting dates/times and clicking Apply still produces the correct `{ start, end }` (or single-date) value.

Root cause confirmed at `packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:591-594`. Not a wrapper-specific bug — do not conflate with React/Vue synthetic-event behavior. The existing `RangeModeExpandedWithTime`/`RangeModeBasicWithTime` Storybook stories (`apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts`) pass `format: ''` in their args, so this same crash is very likely already reproducible in Storybook too — not yet confirmed there.

Found during EOA-17662 Task 27 (React/Vue wrapper parity + `bds-popover` mouse-click regression check). Not the subject of that task's fix — flagged as a separate, pre-existing defect. Needs a `frontend-subagent` fix: `effectiveFormat` should fall back on falsy (`''`), not just `undefined`, or `formatDisplayDate` should guard against an empty format string itself.
