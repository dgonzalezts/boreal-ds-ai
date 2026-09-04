---
name: bds-date-picker-task18a-range-face-nested-textfield-invalid
description: Task 18a range FACE validity manual test found a real bug — the slotted bds-text-field's own independent form-associated validity blocks form submission even though bds-date-picker's own internals are correctly valid.
metadata:
  type: project
---

EOA-17138 Task 18a manual test (`ai-work/plans/EOA-17138-bds-date-picker-v2.md`): `bds-date-picker`'s own `checkValidity()`/`internals` correctly report valid after applying a range on a `required range` picker (confirmed: `value` becomes `{ start, end }`, `internals.checkValidity()` returns `true`). But `form.checkValidity()`/`form.reportValidity()` at the FORM level still return `false`, and the field's `--error` CSS class reappears the moment form-level validation runs.

**Root cause (confirmed via direct repro):** the slotted `bds-text-field` (`packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`) is **itself independently form-associated** (`formAssociated: true`, own `@AttachInternals() internals`) and participates in the same `<form>` as a second, separate constraint-validation candidate. `bds-date-picker.tsx`'s `watchValue`'s range branch (`bds-date-picker.tsx:361`) never calls `this.syncFieldValue()` (only the `string` branch does, at line ~356) — so the slotted text-field's own `.value` stays `''` while `required` is forwarded `true`, making the text-field's own internals report itself invalid (valueMissing), completely independent of and undermining the date-picker's own correctly-valid state. The 'invalid' event bubbling up from the text-field re-triggers `bds-date-picker`'s `@Listen('invalid') handleInvalid`, resetting `isInvalid = true` and reapplying the error class — masking that the picker's own value/validity is actually fine.

**Proof:** manually setting `textField.value = 'Aug 10 - Aug 15'` on the slotted field (simulating what a fix would look like) flips `form.checkValidity()` from `false` to `true` immediately, with no other change. Single-date mode is unaffected — its `watchValue` string branch does call `syncFieldValue()`, so its slotted text-field's own value/validity stay in sync and the whole regression scenario (Scenario 3) passes cleanly.

**Practical impact:** a `required range` `bds-date-picker` inside a real `<form>` can never actually submit natively — `form.requestSubmit()`/clicking a submit button is silently blocked by the browser's own constraint validation, even though the picker's own value is complete and valid. Scenario 2 (submitted `FormData` carrying the delimited range string) could not be verified through an actual submit because of this — it's blocked upstream.

**Fix direction (not applied by QA):** `watchValue`'s range branch needs to also call `this.syncFieldValue()` (or otherwise keep the slotted text-field's own `value`/`required` state such that it never independently reports invalid) after a range value is committed — mirroring what the string branch already does.

See [[bds-date-picker-task18-range-dual-calendar]] for the separate, already-known "range value never displays in the text field" issue — this is the same missing `syncFieldValue()` call, but now shown to have a validity-breaking consequence, not just a cosmetic one.
