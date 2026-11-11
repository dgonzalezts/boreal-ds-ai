# Follow-up ticket from EOA-19936 — `bds-checkbox` defects

**Source:** `ai-work/testing/failure-modes/bds-checkbox.md`
**Suggested project:** EOA · type: Bug · component: `bds-checkbox`

## Summary

Defects found while increasing unit test coverage (EOA-19936). A test for each fails against current source, so fix first, then add the test.

## Defects

- **FM-06:** re-enabling a fieldset sets `isDisabled` to false even when the `disabled` prop is true, so the checkbox becomes interactive again. Root cause is the shared `formDisabledCallback` overwriting `isDisabled` unconditionally; likely affects other components using `formAssociatedMixin` (also `bds-slider` FM-SL-38). Fix once in the shared mixin.
- **FM-15:** changing `value` after mount does not refresh the submitted form value (no `@Watch('value')`).
- **FM-18:** changing `required` after mount does not refresh validity (no `@Watch('required')`).
- **FM-25:** restoring form state compares against a `value` captured once at `bds-checkbox.tsx:88`, so a later `value` change makes restore pick the wrong checked state.
- **FM-30:** a default-slot label never renders. `<bds-checkbox>Accept terms</bds-checkbox>` shows no label unless `info` or `required` is also set.
- **FM-31:** setting `label` to `undefined` after mount throws on `.trim()` in render.
- **FM-33:** `aria-labelledby` is always set, even when no label element renders; the `|| undefined` fallback is dead code.
- **FM-47:** `disconnectedCallback` detaches the keyboard controller but only `componentDidLoad` attaches it, so a moved or reconnected checkbox loses Space handling.

## Not in scope

`pending-decision` rows (FM-08, 10, 17, 23, 24, 27, 28, 32, 34, 39, 40, 44, 49) need a contract ruling first. FM-40 (disabled checkboxes get `aria-hidden="true"`) is an accessibility question worth prioritising.

## Acceptance criteria

- Each defect above is fixed in `bds-checkbox.tsx` or the shared mixin.
- A unit test per defect, failing before the fix and passing after.
- Existing `bds-checkbox` specs still pass; coverage stays at or above 80%.
- Stryker mutation score is at least 90% once the fixes land.
