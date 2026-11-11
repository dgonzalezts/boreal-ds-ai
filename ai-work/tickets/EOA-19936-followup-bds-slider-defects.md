# Follow-up ticket from EOA-19936 — `bds-slider` defects

**Source:** `ai-work/testing/failure-modes/bds-slider.md`
**Suggested project:** EOA · type: Bug · component: `bds-slider`

## Summary

Defects found while increasing unit test coverage (EOA-19936). A test for each fails against current source (or cannot be written safely), so fix first, then add the test.

## Crashes and hangs

- **FM-SL-43:** switching `tooltip` from `focus` to `never` at runtime throws a `TypeError`. Stencil calls the ref with `null` when the tooltip is removed, and the guards only check `undefined`.
- **FM-SL-44:** setting `label = null` throws in `classMap` and `renderLabel`.
- **FM-SL-08:** `discrete` with `step="0"` loops forever (found by reading the code, not run).

## Track click and range

- **FM-SL-14, FM-SL-20:** a track click on a zero-width track stores `NaN`; coincident range handles `[0,0]` or `[100,100]` are pushed to `-1` or `101`, outside `[min, max]`.
- **FM-SL-27:** after `setValues`, mutating `event.detail.value` changes the slider's internal state (payload aliasing).

## Form value

- **FM-SL-30:** changing the `value` prop after mount does not update the form value.
- **FM-SL-34:** resetting a disabled slider leaves the old form value.
- **FM-SL-35:** `formStateRestoreCallback` is not normalized: `"20,70"` on a single slider renders two handles, and `"500"` is stored out of range.

## Runtime prop changes

- **FM-SL-39:** toggling `discrete` resets the user's value back to the `value` prop.
- **FM-SL-41:** shrinking `max` leaves the stored value above the new max.

## Enum validation

- **FM-SL-45:** invalid `type` / `tooltip` values are not validated. `type="foo"` is treated as `single` by `resolveValues` and `applyCollision` but as `range` by `getConnectSegment` and `handleTrackClick`, so a track click yields `[10, 50]` and two inputs on a nominally single slider. Expected: fall back to the documented defaults (`single`, `focus`) via `validatePropValue` in `componentWillLoad`, like `bds-text-field`, `bds-flag` and `bds-radio-group`.

## Accessibility

- **FM-SL-46:** native range inputs have no accessible name; the label's `for` points at the empty host id.
- **FM-SL-47:** `aria-describedby` points at a missing id when `tooltip="never"`.

## Parsing

- **FM-SL-01:** `parseValues('')` returns `[0]` instead of the fallback; `disabled-handlers=""` disables the handle whose value is 0.
- **FM-SL-11:** `discrete min=0 max=2.1 step=0.3` yields a pip at 100%.

## Shared mixin

- **FM-SL-38:** `formDisabledCallback(false)` overrides the `disabled` prop. Same root cause as the `bds-checkbox` defect FM-06; fix once in the shared FACE mixin.

## Not in scope

`pending-decision` rows (e.g. FM-SL-48 tooltip id uniqueness; FM-SL-04 to 07, 10, 12, 15, 16, 18, 19, 21 to 25, 29, 33, 40, 49) need a contract ruling first.

## Acceptance criteria

- Each defect above is fixed in the slider source.
- A unit test per defect, failing before the fix and passing after.
- Existing `bds-slider` specs still pass; coverage stays at or above 80%.
- Stryker mutation score is at least 90% once the fixes land.
