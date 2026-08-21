# PR Descriptions

This file contains all requested PR descriptions, separated by branch.

---

## 1) `bugfix/EOA-17133-a11y-buttons`

### PR Title

`fix(web-components): EOA-17133 fix button accessible-name warnings in pagination and overlays`

### PR Body

## Description of the Bug

`[BorealDS Button] No accessible name found` warnings were still emitted in common overlay and pagination flows, primarily from icon-only buttons and pagination controls without explicit labels.

## Steps to Reproduce

1. Open Storybook examples that render pagination and closable overlays.
2. Interact with numbered/ellipsis pagination controls and close/maximize overlay controls.
3. Check console warnings.
4. Observe accessible-name warnings from `bds-button` in those contexts.

## Root Cause

Several `bds-button` usages relied on visual/icon context without a guaranteed accessible name at render time.

## Description of the Fix

- Added explicit `label` values to pagination controls, including ellipsis controls (`Jump pages`).
- Updated icon-only controls in dialog/drawer/popover headers to provide button labels and keep decorative icons `aria-hidden`.
- Added regression coverage to ensure pagination render path does not emit the no-accessible-name warning.

## Impact of the Fix

- Eliminates noisy and valid accessibility warnings in affected scenarios.
- Preserves existing component APIs and user-facing behavior.
- Improves a11y baseline across shared overlays and pagination.

## Testing Conducted

**Automated:**

- [x] Regression assertions added/updated in pagination a11y tests
- [x] Existing test suites pass

**Manual:**

- [x] Verified in Storybook flows for pagination, dialog, drawer, and popover
- [x] Confirmed no target accessible-name warnings remain

## Additional Remarks

- This PR addresses the remaining scope tracked under EOA-17133 for accessible-name warnings.

## References

Closes EOA-17133

---

## 2) `bugfix/EOA-17085-popover-tooltip-arrow-attr`

### PR Title

`fix(web-components): EOA-17085 rename hidearrow data attr semantics`

### PR Body

## Description of the Bug

`data-hidearrow` was present when the arrow was visible in popover/tooltip, making the attribute name semantically inverted and misleading during DOM inspection and test assertions.

## Steps to Reproduce

1. Render `bds-popover` or `bds-tooltip` with arrow visible.
2. Inspect rendered attributes.
3. Observe `data-hidearrow` present despite arrow being shown.

## Root Cause

The state flag used for arrow visibility was bound to an attribute name that implied the opposite condition.

## Description of the Fix

- Replaced `data-hidearrow` with `data-arrow-visible` in `bds-popover` and `bds-tooltip`.
- Updated affected specs to assert the corrected attribute behavior.

## Impact of the Fix

- Clarifies debug semantics and avoids future confusion in tests and DOM diagnostics.
- No functional/UI behavior change for arrow rendering.
- No public API change.

## Testing Conducted

**Automated:**

- [x] Updated popover/tooltip specs pass
- [x] Existing suite remains green

**Manual:**

- [x] Verified attribute presence/absence matches arrow visibility behavior in Storybook

## Additional Remarks

- This is a semantic DOM-attribute correction aligned with existing behavior, not a feature change.

## References

Closes EOA-17085

---

## 3) `bugfix/EOA-17093-shared-field-error-message`

### PR Title

`fix(web-components): EOA-17093 align errorMessage with validation errors`

### PR Body

## Description of the Bug

For shared field components (`bds-text-field`, `bds-tag-field`, `bds-number-field`), a provided `errorMessage` did not override built-in validation messaging unless `error=true` was also forced.

## Steps to Reproduce

1. Render a field with validation constraints (for example `min-length`) and set `error-message`.
2. Trigger internal validation failure.
3. Observe helper/footer text.
4. Custom `errorMessage` is not shown unless `error` is manually set.

## Root Cause

Shared helper-content derivation prioritized `errorMessage` only when `error` was true, instead of also honoring internal `validationError` state.

## Description of the Fix

- Updated shared render-state logic to apply `errorMessage` when either `error` or `validationError` is true.
- Added regression tests for text/tag/number fields to enforce override behavior.
- Updated field component docs/JSDoc wording to reflect actual behavior.
- Follow-up docs alignment commit removed Storybook `argTypes` conditional hiding of `error-message` in text/number/tag stories so docs snippets match runtime behavior.

## Impact of the Fix

- Makes `errorMessage` behavior consistent across shared form fields.
- Improves predictability for consumers relying on internal validation.
- No breaking API changes.

## Testing Conducted

**Automated:**

- [x] Added validation regression tests in text/tag/number field suites
- [x] Pre-push full test suite passed

**Manual:**

- [x] Verified Storybook validation examples now reflect custom message behavior
- [x] Confirmed docs snippets now expose `error-message` where expected

## Additional Remarks

- Branch includes two commits:
  - `fix(web-components): EOA-16692 align errorMessage with validation errors`
  - `docs(docs): EOA-17093 align error-message docs with validation state`
- Both are intentionally included to keep implementation and docs behavior aligned.

## References

Closes EOA-17093
