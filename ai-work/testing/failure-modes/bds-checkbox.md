# Failure-Mode Catalog — `bds-checkbox`

Audited against `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox/bds-checkbox.tsx`, `.../bds-checkbox/types/ICheckbox.ts` and `.../bds-checkbox/utils/checkbox-form-association.ts` as of 2026-10-27 (branch `feature/EOA-19936_increase-unit-test-coverage-popover-slider-checkbox_DG`, working tree clean). Rows are derived from reading the component source, `formAssociatedMixin`, `KeyboardController` and the pre-existing spec suite (`__test__/bds-checkbox.{basics,a11y,variants,events,keyboard}.spec.ts` and `bds-checkbox-keyboard.spec.ts`), not from a plan's stated test list. Several observed behaviors were additionally confirmed with throwaway probe specs (deleted; no test or source file changed by this audit).

Scope: `bds-checkbox` only. `bds-checkbox-button`, `bds-checkbox-card` and `bds-checkbox-group` are out of scope except where `bds-checkbox` behavior depends on them (`useFormCheckbox` is shared with the card and the button; the group writes `checked`/`disabled`/`error` onto child checkboxes; the card makes the checkbox `aria-hidden`).

All `Covered by:` paths below are relative to `packages/boreal-web-components/` and name a spec under `src/components/forms/bds-checkbox/bds-checkbox/__test__/` unless stated otherwise. `None (gap)` means no existing test asserts the row.

Rows marked `pending-decision` have no test; they must be ruled on by the user before any test or source change lands. Rows marked `confirmed` whose observed behavior contradicts the recommended contract are real defects (flagged `BUG` in the title): the matching test must fail against current code and be handed to `frontend-subagent`, never "fixed" by editing the test.

## Coverage after first test pass (2026-10-27)

Own suite (8 files, 90 tests; new: `bds-checkbox.form.spec.ts`, `bds-checkbox.lifecycle.spec.ts`), scoped to `bds-checkbox.tsx` + `utils/`: statements 100% (87/87), branches 95.12% (39/41), functions 100% (30/30), lines 100% (83/83). The two uncovered branches are `bds-checkbox.tsx:251` (`labelId || undefined`, dead right operand, tied to FM-33) and `bds-checkbox.tsx:279` (`info &&` falsy arm, FM-37 gap). Statement/line coverage over defect rows is incidental: tests for the defect and pending rows are not written, so a green coverage number does not imply those contracts hold.

## Coverage baseline (Phase 1, 2026-10-27, before new specs)

Run with `bds-checkbox/__test__` scoped path and `--collectCoverageFrom` on the component and `utils/`:

| Metric | Own suite (6 files, 44 tests) |
| --- | --- |
| Statements | 74.71% (65/87) — below the 80% gate |
| Branches | 80.48% (33/41) |
| Functions | 53.33% (16/30) |
| Lines | 74.69% (62/83) |

`bds-checkbox.tsx` alone: 82.81% statements, 54.54% functions (uncovered: 123, 137-174, 263). `checkbox-form-association.ts` alone: 50% statements, 50% functions (uncovered: 11, 27-44). Running the broader positional path `bds-checkbox/bds-checkbox` also matches the card/button/group suites and inflates the number to 85.05% statements; that figure is incidental (the shared `useFormCheckbox` util is exercised by the card/button specs) and says nothing about the `bds-checkbox` FACE callbacks, none of which any `bds-checkbox` spec calls.

Zero tests exist for: `formAssociatedCallback`, `formResetCallback`, `formStateRestoreCallback`, `formDisabledCallback`, `checkValidity()`, `reportValidity()`, the `invalid` listener, the `required`/`info`/`error`/`value` props, the `disconnectedCallback`, and the inner `<input>` `onFocus` delegation. The existing spec files named like "form field value enabled" (`bds-checkbox.keyboard.spec.ts`) only assert the inner `<input>.checked`, never `internals.setFormValue`.

---

## A. Toggle, events, and the checked contract

### FM-01 | A click toggles `checked` once and emits once

- **ID:** FM-01
- **Category:** race-timing
- **Risk:** event contract — duplicate `bdsChange` double-counts in `bds-checkbox-group` and in consumer handlers.
- **Input that reveals it:** `click()` on the host; `click()` on the rendered `.bds-checkbox__label`; click on the inner `<input>`.
- **Observed current behavior:** the `Host` `onClick` calls `toggle()` (`bds-checkbox.tsx:253,180-188`). The inner `<input>` has `pointer-events: none` (`bds-checkbox.scss:17`), so only the host click path exists; a click on the label bubbles to the host and toggles once (probe: `checked` true after one label click).
- **Recommended contract:** one user click produces exactly one state flip and one `bdsChange` plus one `valueChange`.
- **Contract status:** confirmed
- **Why it matters:** the group's capture listener (`bds-checkbox-group.tsx:175-187`) turns each `bdsChange` into a group `bdsChange`.
- **Covered by:** `bds-checkbox.events.spec.ts::should toggle checked on click` (host click, one `bdsChange`, `aria-checked` true). Label-text click: None (gap).

---

### FM-02 | Event payloads and order

- **ID:** FM-02
- **Category:** equivalence
- **Risk:** event contract / v-model — `valueChange` is the Vue `v-model` event (boolean); `bdsChange` carries `{ checked, value }`. A wrong payload (stale `checked`, default `value` instead of the configured one) breaks group selection bookkeeping (`checkbox.value` read in `bds-checkbox-group.tsx:181`).
- **Input that reveals it:** toggle a checkbox with a custom `value="subscribed"`; toggle on then off; listen to both events.
- **Observed current behavior:** `checked` is flipped first, then `valueChange.emit(this.checked)` then `bdsChange.emit({ checked: this.checked, value: this.value })` (`bds-checkbox.tsx:184-187`).
- **Recommended contract:** after a toggle, `valueChange.detail` is the new boolean; `bdsChange.detail` is `{ checked: <new>, value: <current value prop> }`; `valueChange` fires before `bdsChange`.
- **Contract status:** confirmed
- **Why it matters:** both consumers (v-model and group) read the detail rather than the element.
- **Covered by:** `bds-checkbox.keyboard.spec.ts::should emit bdsChange with correct payload { checked: true, value: "on" }` (default value, checked=true only). `valueChange` payload, uncheck payload, custom `value` payload and emission order: None (gap). Presence of `valueChange` on Space: `bds-checkbox-keyboard.spec.ts::should emit valueChange on Space keydown` (count only).

---

### FM-03 | Programmatic `checked` changes do not emit events

- **ID:** FM-03
- **Category:** race-timing
- **Risk:** event contract — if a controlled consumer or `bds-checkbox-group.syncCheckboxStates` (`bds-checkbox-group.tsx:244-248`) writes `checked` and the checkbox re-emitted, the group would loop (`bdsChange` → write → `bdsChange`).
- **Input that reveals it:** `el.checked = true` after mount, with listeners on `bdsChange`/`valueChange`.
- **Observed current behavior:** only `toggle()` emits; the `@Watch('checked')` only calls `syncFormValue()` (`bds-checkbox.tsx:130-133`).
- **Recommended contract:** setting `checked` programmatically updates visuals, `aria-checked` and the form value but emits no event.
- **Contract status:** confirmed
- **Why it matters:** it is what prevents the group <-> child feedback loop.
- **Covered by:** `bds-checkbox.lifecycle.spec.ts::programmatic checked changes > does not emit bdsChange or valueChange when checked is set programmatically`; `bds-checkbox.lifecycle.spec.ts::programmatic checked changes > updates aria-checked and the form value when checked is set programmatically`; `bds-checkbox.lifecycle.spec.ts::programmatic checked changes > does not emit events when checked is cleared programmatically`.

---

### FM-04 | Rapid double click flips twice and emits twice

- **ID:** FM-04
- **Category:** race-timing
- **Risk:** event contract — a debounce or "already handled" guard that swallows the second click would desync the visual state from what the user did.
- **Input that reveals it:** two synchronous `click()` calls, then `waitForChanges()`.
- **Observed current behavior:** no guard; each click runs `toggle()` (`bds-checkbox.tsx:180-188`), final state equals initial, two `bdsChange` emitted.
- **Recommended contract:** each click is a discrete toggle (native checkbox behavior).
- **Contract status:** confirmed
- **Why it matters:** documents the absence of debounce so a future "optimization" does not eat user clicks.
- **Covered by:** None (gap).

---

## B. Disabled and readonly

`bds-checkbox` has no `readonly` prop (not declared in `ICheckbox.ts` or `bds-checkbox.tsx`); there is no readonly edge case to catalog. The disabled contract has two writers, the `disabled` prop (via `@Watch`) and `formDisabledCallback` (fieldset), both writing the single `isDisabled` state.

### FM-05 | A disabled checkbox cannot be driven by click or Space

- **ID:** FM-05
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — a disabled control that still toggles changes submitted data the user cannot see as editable.
- **Input that reveals it:** `disabled` attribute; click and Space keydown; additionally `el.disabled = true` set after mount.
- **Observed current behavior:** `toggle()` returns early when `isDisabled` (`bds-checkbox.tsx:181`); the Space handler also checks `isDisabled` (`bds-checkbox.tsx:113-115`); `@Watch('disabled')` mirrors later prop changes into `isDisabled` (`bds-checkbox.tsx:135-138`).
- **Recommended contract:** no state change and no event from click or Space while disabled, including when `disabled` is set after mount.
- **Contract status:** confirmed
- **Why it matters:** the two guards are independent; mutating either alone must not reopen the bypass.
- **Covered by:** `bds-checkbox.events.spec.ts::should not toggle when disabled`; `bds-checkbox-keyboard.spec.ts::should not toggle when disabled on Space keydown`; `bds-checkbox-keyboard.spec.ts::should not emit bdsChange when disabled on Space keydown`; `bds-checkbox.keyboard.spec.ts::should NOT toggle when disabled and Space is pressed`; `bds-checkbox.keyboard.spec.ts::should NOT emit bdsChange when disabled and Space is pressed`. `disabled` set after mount (watcher path): `bds-checkbox.lifecycle.spec.ts::disabled set after mount > does not toggle on click once disabled is set programmatically`; `bds-checkbox.lifecycle.spec.ts::disabled set after mount > does not toggle on Space once disabled is set programmatically`.

---

### FM-06 | BUG: re-enabling a fieldset overrides the component's own `disabled` prop

- **ID:** FM-06
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — a checkbox authored `disabled` inside a `<fieldset>` becomes interactive again when the fieldset is toggled from disabled to enabled, and can be toggled and submitted.
- **Input that reveals it:** `<bds-checkbox disabled>`, then `formDisabledCallback(true)` followed by `formDisabledCallback(false)`. Probe result: `aria-disabled` null, class lacks `bds-checkbox--disabled`, a click then sets `checked` true.
- **Observed current behavior:** `formDisabledCallback` assigns `component.isDisabled = disabled` unconditionally (`checkbox-form-association.ts:43-45`, via `bds-checkbox.tsx:155-157` and the mixin), discarding the `disabled` prop that `componentWillLoad`/`@Watch` had mirrored.
- **Recommended contract:** the effective disabled state is `disabled` prop OR fieldset-disabled; a fieldset becoming enabled never enables a checkbox whose own `disabled` prop is true.
- **Contract status:** confirmed
- **Why it matters:** the `formDisabledCallback` JSDoc on the mixin states it only reflects fieldset state; a native disabled control never becomes enabled because an ancestor fieldset re-enabled.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-07 | `formDisabledCallback(true)` disables an enabled checkbox

- **ID:** FM-07
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — `<fieldset disabled>` must lock the control.
- **Input that reveals it:** call `formDisabledCallback(true)` on an enabled checkbox, then click / Space.
- **Observed current behavior:** `isDisabled` becomes true, so `toggle()` and the Space handler no-op and `aria-disabled="true"`, `tabindex=-1`, class `bds-checkbox--disabled` render.
- **Recommended contract:** fieldset-disabled checkboxes behave exactly like `disabled` for interaction and ARIA.
- **Contract status:** confirmed
- **Why it matters:** this is the only reachable path for the `formDisabledCallback` function (`bds-checkbox.tsx:155-157` is uncovered).
- **Covered by:** `bds-checkbox.form.spec.ts::formDisabledCallback > renders the disabled state when the fieldset disables an enabled checkbox`; `bds-checkbox.form.spec.ts::formDisabledCallback > does not toggle on click when the fieldset disables the checkbox`; `bds-checkbox.form.spec.ts::formDisabledCallback > does not toggle on Space when the fieldset disables the checkbox`.

---

### FM-08 | Inner native `<input>` and error styling ignore the fieldset-disabled state

- **ID:** FM-08
- **Category:** equivalence
- **Risk:** visual/a11y — the inner `<input disabled={this.disabled}>` (`bds-checkbox.tsx:259`) and `isError` (`this.error && !this.disabled`, `bds-checkbox.tsx:194-197`) read the `disabled` prop, not `isDisabled`. A fieldset-disabled checkbox keeps an enabled inner input and, if `error` is set, still paints error styling, while a prop-disabled one does not.
- **Input that reveals it:** `<bds-checkbox error>` then `formDisabledCallback(true)`; inspect `.bds-checkbox--error` and `input.disabled`.
- **Observed current behavior:** error class stays; inner input stays enabled.
- **Recommended contract:** one of: (a) both sources of disabled are equivalent everywhere (error suppressed, inner input disabled); (b) deliberately different. No evidence in code, plan or Figma for (b).
- **Contract status:** pending-decision
- **Why it matters:** inconsistent visuals between two disabled paths; low a11y impact because the inner input is `aria-hidden` and `pointer-events: none`.
- **Covered by:** None (blocked on decision).

---

## C. Indeterminate

### FM-09 | Click or Space on an unchecked indeterminate checkbox clears indeterminate and checks

- **ID:** FM-09
- **Category:** equivalence
- **Risk:** a11y/visual — a tri-state control that stays "mixed" after interaction traps users.
- **Input that reveals it:** `<bds-checkbox indeterminate>` then click, then separately Space.
- **Observed current behavior:** `toggle()` sets `indeterminate = false` then flips `checked` (`bds-checkbox.tsx:183-184`).
- **Recommended contract:** an unchecked indeterminate checkbox becomes checked and not indeterminate on one interaction.
- **Contract status:** confirmed
- **Why it matters:** consistent with the native checkbox.
- **Covered by:** `bds-checkbox.events.spec.ts::should clear indeterminate on click`; `bds-checkbox-keyboard.spec.ts::should clear indeterminate state on Space keydown`; `bds-checkbox.keyboard.spec.ts::should clear indeterminate and check when Space is pressed while indeterminate`.

---

### FM-10 | Indeterminate AND `checked` together: what does one interaction do?

- **ID:** FM-10
- **Category:** equivalence
- **Risk:** functional — `<bds-checkbox indeterminate checked>` (e.g. a parent checkbox in a tree whose children are partly selected, with `checked` left true) goes to `checked=false, indeterminate=false` after one click (probe). The native checkbox does the same (clears indeterminate and flips `checked`), but many tri-state patterns resolve "mixed" to "checked".
- **Input that reveals it:** `<bds-checkbox indeterminate checked>` then click.
- **Observed current behavior:** result is `checked=false`, `indeterminate=false` (`bds-checkbox.tsx:183-184`).
- **Recommended contract:** either (a) keep native semantics (flip `checked`), or (b) mixed always resolves to checked.
- **Contract status:** pending-decision
- **Why it matters:** the visual shows "mixed" so the user sees no checkmark, then the click appears to "uncheck" something that looked unchecked.
- **Covered by:** None (blocked on decision). No existing test conflicts: the existing indeterminate tests all start with `checked=false`.

---

### FM-11 | Indeterminate takes visual and ARIA precedence over checked

- **ID:** FM-11
- **Category:** equivalence
- **Risk:** a11y — `aria-checked` must be `mixed` while indeterminate even when `checked` is true; the icon must be the solid-line, not the check.
- **Input that reveals it:** `<bds-checkbox indeterminate checked>`.
- **Observed current behavior:** `getAriaChecked()` returns `'mixed'` first (`bds-checkbox.tsx:202-205`); `renderCheckIcon()` returns the solid-line icon first (`bds-checkbox.tsx:211-219`); both classes `--checked` and `--indeterminate` are applied (`getClasses`).
- **Recommended contract:** with both set: `aria-checked="mixed"`, solid-line icon, no check icon.
- **Contract status:** confirmed
- **Why it matters:** precedence is implicit in two separate early-returns.
- **Covered by:** indeterminate alone is covered (`bds-checkbox.a11y.spec.ts::should have aria-checked="mixed" when indeterminate`; `bds-checkbox.basics.spec.ts::should render solid line icon when indeterminate`). Combined precedence: None (gap).

---

### FM-12 | `indeterminate` never changes the submitted value or validity

- **ID:** FM-12
- **Category:** equivalence
- **Risk:** FACE/form submission — a "mixed" checkbox that is `checked` submits its value; one that is unchecked and `required` stays invalid.
- **Input that reveals it:** set `indeterminate` on checked and unchecked checkboxes, observe `internals.setFormValue`/`setValidity`.
- **Observed current behavior:** `updateFormValue`/`updateFormValidity` only read `checked` and `required` (`checkbox-form-association.ts:5-16`); there is no `@Watch('indeterminate')`.
- **Recommended contract:** form value and validity depend on `checked` and `required` only (native checkbox semantics).
- **Contract status:** confirmed
- **Why it matters:** documents that toggling `indeterminate` must not clear a submitted value.
- **Covered by:** None (gap).

---

## D. FACE: form value, reset, restore, validation, submit

The jest `ElementInternals` mock (`src/utils/testing/mocks/elementInternals.ts`) exposes `setFormValue`, `setValidity`, `checkValidity`, `reportValidity` as `jest.fn`, reachable via `page.rootInstance.internals`, so these rows are assertable.

### FM-13 | Form value is `value` when checked, `null` when unchecked, set on load and on every `checked` change

- **ID:** FM-13
- **Category:** equivalence
- **Risk:** FACE/form submission — wrong value means wrong `FormData`.
- **Input that reveals it:** `<bds-checkbox name="n" checked>`; then uncheck; then re-check via click and Space.
- **Observed current behavior:** `componentDidLoad` calls `syncFormValue()` (`bds-checkbox.tsx:112`); `@Watch('checked')` calls it again; `updateFormValue` sets `component.checked ? component.value : null` (`checkbox-form-association.ts:5-7`).
- **Recommended contract:** `setFormValue(value)` when checked, `setFormValue(null)` when unchecked, at load and after each change; default `value` is `'on'`.
- **Contract status:** confirmed
- **Why it matters:** this is the entire submit contract.
- **Covered by:** `bds-checkbox.form.spec.ts::form value > submits the default value when the checkbox loads checked`; `...::submits the configured value when the checkbox loads checked`; `...::submits null when the checkbox loads unchecked`; `...::submits the value after a click checks the checkbox`; `...::submits null after a click unchecks the checkbox`; `...::submits the value again after Space re-checks the checkbox`.

---

### FM-14 | `value=""` submits an empty string when checked (boundary)

- **ID:** FM-14
- **Category:** boundary
- **Risk:** FACE/form submission — a falsy-value shortcut (`value ? value : null`) would drop a checked control from the form.
- **Input that reveals it:** `<bds-checkbox name="n" value="" checked>`. Probe: `setFormValue` called with `''`.
- **Observed current behavior:** `checked ? value : null` keeps `''` (`checkbox-form-association.ts:6`).
- **Recommended contract:** a checked checkbox with an empty `value` submits `''` (native `<input type="checkbox" value="">` submits `name=`).
- **Contract status:** confirmed
- **Why it matters:** protects the exact-comparison semantics of the util.
- **Covered by:** `bds-checkbox.form.spec.ts::form value > submits an empty string when a checked checkbox has an empty value`; `...::submits null when an unchecked checkbox has an empty value`.

---

### FM-15 | BUG: changing `value` after mount does not refresh the form value

- **ID:** FM-15
- **Category:** race-timing
- **Risk:** FACE/form submission — a framework wrapper (React/Vue) that sets `value` after the element upgrades leaves the old value in the submission while checked.
- **Input that reveals it:** `<bds-checkbox name="n" checked>` then `el.value = 'x'`. Probe: `setFormValue` call count is 0 after the change.
- **Observed current behavior:** only `@Watch('checked')` triggers `syncFormValue()` (`bds-checkbox.tsx:130-133`); there is no `@Watch('value')`.
- **Recommended contract:** while checked, `internals` form value tracks the current `value` prop.
- **Contract status:** confirmed
- **Why it matters:** stale submission data, no console error.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-16 | `required` + unchecked reports `valueMissing` on the host; checking clears it

- **ID:** FM-16
- **Category:** null-empty
- **Risk:** FACE/form submission — a required unchecked checkbox must block submission and a checked one must not.
- **Input that reveals it:** `<bds-checkbox required name="n">` unchecked, then check; then uncheck.
- **Observed current behavior:** `updateFormValidity` calls `setValidity({ valueMissing: true }, ' ', component.el)` when required and unchecked, otherwise `setValidity({})` (`checkbox-form-association.ts:9-15`).
- **Recommended contract:** `valueMissing` while `required && !checked`, cleared otherwise; the anchor is the host element.
- **Contract status:** confirmed
- **Why it matters:** line `checkbox-form-association.ts:11` is the single uncovered line in that util for the `bds-checkbox` suite.
- **Covered by:** `bds-checkbox.form.spec.ts::required validity > reports valueMissing anchored to the host when required and unchecked`; `...::clears the validity error once the required checkbox is checked`; `...::reports valueMissing again when the required checkbox is unchecked`; `...::stays valid when the checkbox is not required and unchecked`.

---

### FM-17 | The `valueMissing` message is a single space

- **ID:** FM-17
- **Category:** null-empty
- **Risk:** a11y — `internals.validationMessage` is `' '`, so a consumer reading it for an error message gets a blank string; the built-in bubble is suppressed by `handleInvalid`'s `preventDefault` (FM-20), so no UI exposes a message either.
- **Input that reveals it:** `validationMessage` after a required-unchecked state.
- **Observed current behavior:** `setValidity({ valueMissing: true }, ' ', ...)` (`checkbox-form-association.ts:11`).
- **Recommended contract:** either keep blank deliberately (error text owned by a wrapper like the group's `errorMessage`) or provide a default message.
- **Contract status:** pending-decision
- **Why it matters:** the group owns its own message (`bds-checkbox-group.tsx:284`); a standalone checkbox has none.
- **Covered by:** None (blocked on decision).

---

### FM-18 | BUG: changing `required` after mount does not refresh validity

- **ID:** FM-18
- **Category:** race-timing
- **Risk:** FACE/form submission — a wrapper that sets `required` after upgrade leaves the control valid while unchecked (or invalid after `required` is removed).
- **Input that reveals it:** `<bds-checkbox name="n">`, then `el.required = true`. Probe: `setValidity` call count is 0 after the change.
- **Observed current behavior:** no `@Watch('required')`; validity is recomputed only on `checked` changes and association (`bds-checkbox.tsx:130-133`).
- **Recommended contract:** validity tracks the current `required` and `checked` at all times.
- **Contract status:** confirmed
- **Why it matters:** native-form blocking depends on it.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-19 | `formAssociatedCallback` re-syncs value and validity

- **ID:** FM-19
- **Category:** race-timing
- **Risk:** FACE/form submission — association can occur after load (moving the element into a form, `form` attribute change).
- **Input that reveals it:** call `formAssociatedCallback()` on a checked required checkbox after clearing mocks.
- **Observed current behavior:** delegates to `syncFormValue()` (`bds-checkbox.tsx:143-145`, `checkbox-form-association.ts:26-28`).
- **Recommended contract:** form value and validity are (re)computed from the current props.
- **Contract status:** confirmed
- **Why it matters:** `bds-checkbox.tsx:144` is uncovered by the `bds-checkbox` suite.
- **Covered by:** `bds-checkbox.form.spec.ts::formAssociatedCallback > re-syncs the form value and validity from a checked required checkbox`; `...::re-syncs a null form value and valueMissing from an unchecked required checkbox`.

---

### FM-20 | `invalid` event marks the control invalid, cancels the native bubble, and clears on a valid state

- **ID:** FM-20
- **Category:** component-contract-bypass
- **Risk:** a11y/visual — `invalid` must switch error styling and `aria-invalid`; its default must be prevented so the browser does not show a bubble for a hidden control; a later valid state must clear it.
- **Input that reveals it:** dispatch a cancelable `invalid` event on a required unchecked checkbox, then check it. Probe: `defaultPrevented` true; class `bds-checkbox--error` and `aria-invalid="true"` appear; both cleared after the click.
- **Observed current behavior:** `handleInvalid` (`bds-checkbox.tsx:171-175`) prevents default and sets `isInvalid`; `updateFormValidity` resets `isInvalid` when valid (`checkbox-form-association.ts:14`).
- **Recommended contract:** as observed.
- **Contract status:** confirmed
- **Why it matters:** the whole standalone required-checkbox error UX.
- **Covered by:** `bds-checkbox.form.spec.ts::invalid event > cancels the native validation bubble when the invalid event fires`; `...::applies error styling and aria-invalid when the invalid event fires`; `...::clears error styling and aria-invalid once the checkbox becomes valid`.

---

### FM-21 | `checkValidity()` and `reportValidity()` delegate to the internals

- **ID:** FM-21
- **Category:** component-contract-bypass
- **Risk:** functional — the public `@Method()` results must reflect `ElementInternals` and `reportValidity` must be what fires `invalid`.
- **Input that reveals it:** call each method after making the mock return `false`/`true`.
- **Observed current behavior:** return `this.internals.checkValidity()` / `reportValidity()` (`bds-checkbox.tsx:159-169`). The JSDoc says "the group's validity", a copy-paste from the group.
- **Recommended contract:** delegate unchanged; JSDoc should describe the checkbox.
- **Contract status:** confirmed
- **Why it matters:** public API surface with zero coverage (`bds-checkbox.tsx:161-168`).
- **Covered by:** `bds-checkbox.form.spec.ts::validity methods > returns the internals result from checkValidity`; `...::returns the internals result from reportValidity`. JSDoc wording is a docs follow-up, not a test.

---

### FM-22 | Reset clears `checked`, `indeterminate` and `isInvalid`, and nulls the form value

- **ID:** FM-22
- **Category:** equivalence
- **Risk:** FACE/form submission — `form.reset()` must leave no checked state and no submitted value.
- **Input that reveals it:** `<bds-checkbox checked indeterminate>` then `formResetCallback()`; with a pending `isInvalid`. Probe: `checked=false`, `indeterminate=false`.
- **Observed current behavior:** `formResetCallback` sets all three false, calls `setFormValue(null)` and `updateFormValidity()` (`checkbox-form-association.ts:30-36`).
- **Recommended contract:** after reset the control is unchecked, non-indeterminate, valid-state-cleared, and the form value is `null`; a `required` control reports `valueMissing` again.
- **Contract status:** confirmed
- **Why it matters:** reset is a core FACE callback; unchecked is also the group's reset behavior (`bds-checkbox-group.tsx:151-163`).
- **Covered by:** `bds-checkbox.form.spec.ts::formResetCallback > unchecks a checked checkbox`; `...::clears the indeterminate state`; `...::sets the form value to null`; `...::clears a pending invalid state`; `...::reports valueMissing again for a required checkbox`.

---

### FM-23 | Reset ignores the initial `checked` attribute (native resets to `defaultChecked`)

- **ID:** FM-23
- **Category:** equivalence
- **Risk:** FACE/form submission — `<bds-checkbox checked>` followed by user interaction and `form.reset()` ends unchecked, whereas a native `<input type="checkbox" checked>` returns to checked.
- **Input that reveals it:** `<bds-checkbox checked>` then `formResetCallback()`. Probe: `checked=false`.
- **Observed current behavior:** `checked` is `reflect: true` and mutable, so the attribute tracks live state and there is no remembered default; reset always yields `false` (`checkbox-form-association.ts:31`).
- **Recommended contract:** either (a) reset always unchecks (current, matches the group), or (b) reset restores the initial `checked` like a native checkbox, which requires capturing the default at load.
- **Contract status:** pending-decision
- **Why it matters:** differs from native; changing it would be a breaking behavior change for consumers relying on reset-to-empty.
- **Covered by:** None (blocked on decision).

---

### FM-24 | Reset emits no `valueChange`/`bdsChange`

- **ID:** FM-24
- **Category:** race-timing
- **Risk:** event contract — a v-model consumer bound to `valueChange` stays `true` after `form.reset()` because the component state became `false` silently; the group's own reset also writes `checked=false` without events, so the group relies on this silence.
- **Input that reveals it:** `<bds-checkbox checked>`, `formResetCallback()`, listeners on both events.
- **Observed current behavior:** `formResetCallback` writes props directly and emits nothing (`checkbox-form-association.ts:30-36`).
- **Recommended contract:** either (a) silent reset (current; consistent with FM-03) or (b) emit `valueChange(false)` so v-model stays in sync.
- **Contract status:** pending-decision
- **Why it matters:** Vue `v-model` desync after reset; the emission would also reach the group's capture listener and fight its reset.
- **Covered by:** None (blocked on decision).

---

### FM-25 | BUG: restoring state compares against a stale `value` snapshot

- **ID:** FM-25
- **Category:** race-timing
- **Risk:** FACE/form submission — after back/forward or autofill restore, a checkbox whose `value` was changed after mount restores to the wrong checked state: restoring the current value yields unchecked, restoring the original default yields checked.
- **Input that reveals it:** `<bds-checkbox name="a">`, `el.value = 'yes'`, `formStateRestoreCallback('yes')`. Probe: `checked=false`; then `formStateRestoreCallback('on')` gives `checked=true`.
- **Observed current behavior:** `useFormCheckbox(this, this.value)` captures `value` once as a function parameter (`bds-checkbox.tsx:88`); `formStateRestoreCallback` compares `restoreState === value` against that snapshot (`checkbox-form-association.ts:38-41`), while `updateFormValue` reads the live `component.value` (`checkbox-form-association.ts:6`).
- **Recommended contract:** restore compares against the current `value` prop, the same value that was stored by `setFormValue`.
- **Contract status:** confirmed
- **Why it matters:** the stored state is `component.value`, so the comparison must use the same source; consumers (Vue/React) commonly set `value` after upgrade.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-26 | Restore with `null`, non-matching or non-string state unchecks and re-syncs

- **ID:** FM-26
- **Category:** null-empty
- **Risk:** FACE/form submission — restore must never throw and must leave a coherent form value.
- **Input that reveals it:** `formStateRestoreCallback(null)`, `('other')`, and the stored `value`; then read `internals.setFormValue` calls.
- **Observed current behavior:** `checked = restoreState === value` then `syncFormValue()` (`checkbox-form-association.ts:38-41`), no `typeof` check; non-string states compare unequal and uncheck.
- **Recommended contract:** matching value checks the control; anything else unchecks; form value and validity are re-synced either way.
- **Contract status:** confirmed
- **Why it matters:** `checkbox-form-association.ts:39-40` are the uncovered util lines.
- **Covered by:** `bds-checkbox.form.spec.ts::formStateRestoreCallback > checks the checkbox when the restored state equals its value`; `...::unchecks the checkbox when the restored state is a different string`; `...::unchecks the checkbox without throwing when the restored state is null`; `...::re-syncs validity as valid when a required checkbox is restored as checked`; `...::re-syncs validity as valueMissing when a required checkbox is restored with a non-matching state`. Restore with a `value` changed after mount is FM-25 (defect), not covered.

---

### FM-27 | Restore does not emit events

- **ID:** FM-27
- **Category:** race-timing
- **Risk:** event contract — same v-model desync as FM-24 for the restore path.
- **Input that reveals it:** `formStateRestoreCallback(value)` with `valueChange` listener.
- **Observed current behavior:** no emission (`checkbox-form-association.ts:38-41`).
- **Recommended contract:** follows whichever rule FM-24 settles.
- **Contract status:** pending-decision
- **Why it matters:** keep reset and restore consistent.
- **Covered by:** None (blocked on decision).

---

### FM-28 | Inner `<input type="checkbox" required>` is a second constraint-validation owner

- **ID:** FM-28
- **Category:** component-contract-bypass
- **Risk:** FACE/form submission — the host is form-associated through `ElementInternals` and also renders a native `<input required>` (`bds-checkbox.tsx:255-264`) inside the same `<form>`. A required unchecked checkbox therefore has two invalid controls. The host's `invalid` is cancelled (FM-20) but the inner input's `invalid` event (non-bubbling) is not, so the browser may try to focus and report a zero-size, `aria-hidden`, non-focusable input ("An invalid form control is not focusable").
- **Input that reveals it:** real browser: submit a `<form>` containing an unchecked `<bds-checkbox required>`.
- **Observed current behavior:** the input carries `required` and `disabled` from the props; it has no `name`, so it never submits, but it validates.
- **Recommended contract:** one validity owner, and submission blocked with visible feedback; unknown whether the inner `required` is intentional.
- **Contract status:** pending-decision
- **Why it matters:** cannot be asserted in mock-doc (no native validation); needs a Playwright check through `qa-subagent` before any decision. A unit test can only assert the `required` attribute passes through to the inner input.
- **Covered by:** None (blocked on decision; browser-only).

---

### FM-29 | Group dependency: `checked`, `disabled`, `error` written onto a mounted checkbox

- **ID:** FM-29
- **Category:** race-timing
- **Risk:** functional — `bds-checkbox-group` assigns `checked`, `disabled` and `error` on children (`bds-checkbox-group.tsx:247,257-261`); `disabled`/`error` are declared `readonly` on the checkbox and rely on Stencil's runtime setters.
- **Input that reveals it:** group disables, then enables its children while a child carries its own `disabled`.
- **Observed current behavior:** group writes win over the child's authored `disabled` (same mechanism as FM-06).
- **Recommended contract:** the checkbox honors external writes to `checked`/`disabled`/`error` exactly like authored attributes (covered by FM-03, FM-05, FM-13).
- **Contract status:** confirmed
- **Why it matters:** the group is the main in-repo consumer.
- **Covered by:** group specs under `src/components/forms/bds-checkbox/bds-checkbox-group/__test__/` cover the group side; no `bds-checkbox`-side test. The "child authored `disabled` overwritten when the group re-enables" interaction is a group-scope observation, out of scope here.

---

## E. Rendering and props

### FM-30 | BUG: default-slot label is never rendered

- **ID:** FM-30
- **Category:** null-empty
- **Risk:** functional/a11y — the JSDoc says the default slot supplies the label "when no `label` prop is provided", but `showLabelContent` ignores slotted content. `<bds-checkbox>Accept terms</bds-checkbox>` renders no label wrapper, so there is no `<slot>` for the text and Stencil's slot relocation leaves it unplaced (probe output: the text node becomes a `<!--s-nt-Accept terms-->` reference comment and no `.bds-checkbox__content` exists). The text appears only when `info` or `required` is also set (they force the wrapper).
- **Input that reveals it:** `<bds-checkbox>Accept terms</bds-checkbox>` with no `label`, `info` or `required`.
- **Observed current behavior:** `showLabelContent = this.label.trim() !== '' || this.info !== '' || this.required` (`bds-checkbox.tsx:239`).
- **Recommended contract:** slotted label content renders, with the slot present whenever the label prop is empty.
- **Contract status:** confirmed
- **Why it matters:** the documented API silently shows an unlabelled checkbox. The `icon` slot has the same dependency on the wrapper.
- **Covered by:** None (gap). `bds-checkbox.basics.spec.ts::should not render content area when no label, info, or required` encodes the no-wrapper behavior but uses no slotted text, so it does not conflict. Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-31 | BUG: `label` set to `undefined`/`null` after mount throws in render

- **ID:** FM-31
- **Category:** null-empty
- **Risk:** functional — React/Vue wrappers pass `undefined` for an omitted optional prop; render throws and the component stops updating.
- **Input that reveals it:** mount with `label="x"`, then `el.label = undefined`. Probe: `TypeError: Cannot read properties of undefined (reading 'trim')`.
- **Observed current behavior:** `this.label.trim()` is called unguarded twice (`bds-checkbox.tsx:239,272`).
- **Recommended contract:** a missing label behaves as the empty string.
- **Contract status:** confirmed
- **Why it matters:** every other string prop is read without trim, so only `label` can crash.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-32 | Whitespace-only `label` with `info`/`required` renders an empty `<label>`

- **ID:** FM-32
- **Category:** boundary
- **Risk:** a11y — `aria-labelledby` (FM-33) then references an element with empty text; the checkbox has no accessible name.
- **Input that reveals it:** `<bds-checkbox label="  " info="hi">`. Probe: `<label id=... class="bds-checkbox__label"></label>` (empty).
- **Observed current behavior:** `trim()` makes the label count as empty, falls to `<slot />`, and renders an empty label (`bds-checkbox.tsx:272`).
- **Recommended contract:** either render no `<label>` element (and no `aria-labelledby`) when there is nothing to name the control, or keep the empty element. Intent of the `trim()` is clearly "whitespace means empty"; what the surrounding wrapper should do is not specified.
- **Contract status:** pending-decision
- **Why it matters:** depends on how FM-33 is resolved.
- **Covered by:** None (blocked on decision).

---

### FM-33 | BUG: `aria-labelledby` always points at an id that may not exist

- **ID:** FM-33
- **Category:** null-empty
- **Risk:** a11y — with no `label`, `info` or `required`, no `<label id="...-label">` is rendered, yet the host always carries `aria-labelledby="<id>-label"` (dangling IDREF).
- **Input that reveals it:** `<bds-checkbox></bds-checkbox>`. Probe: `aria-labelledby` set, no `<label>` in the DOM.
- **Observed current behavior:** `aria-labelledby={labelId || undefined}` (`bds-checkbox.tsx:251`); `labelId` is a non-empty template string, so the `|| undefined` branch is dead code.
- **Recommended contract:** `aria-labelledby` is omitted unless the label element is rendered.
- **Contract status:** confirmed
- **Why it matters:** the `|| undefined` shows the intent to omit; a consumer's `aria-label` still works because AT ignores a dangling IDREF, but tooling flags it.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-34 | Consumer-provided ARIA is partly overwritten by the component

- **ID:** FM-34
- **Category:** equivalence
- **Risk:** a11y — `inheritAriaAttributes(this.el)` moves the host's aria attributes into `inheritedAttributes` (`bds-checkbox.tsx:105-108`) but they are spread before the explicit `role`, `aria-checked`, `aria-disabled`, `aria-invalid`, `aria-hidden`, `aria-labelledby`, `tabindex` (`bds-checkbox.tsx:243-252`). A consumer `aria-labelledby="mine"` is replaced by the internal id; `aria-label` survives (probe) and `aria-describedby` survives.
- **Input that reveals it:** `<bds-checkbox aria-labelledby="mine" aria-label="Mine" aria-hidden="false" role="switch">`.
- **Observed current behavior:** `aria-label` kept; `aria-labelledby`, `aria-hidden`, `role` overridden.
- **Recommended contract:** either the consumer's `aria-labelledby` wins when provided, or it is deliberately overridden; no evidence for either.
- **Contract status:** pending-decision
- **Why it matters:** the standard way to name a checkbox from an external label element is `aria-labelledby`.
- **Covered by:** None (blocked on decision).

---

### FM-35 | `aria-checked` follows state (`false`, `true`, `mixed`)

- **ID:** FM-35
- **Category:** equivalence
- **Risk:** a11y.
- **Input that reveals it:** default, `checked`, `indeterminate`; transitions after click and Space.
- **Observed current behavior:** `getAriaChecked()` (`bds-checkbox.tsx:202-205`).
- **Recommended contract:** as observed.
- **Contract status:** confirmed
- **Why it matters:** the primary AT signal.
- **Covered by:** `bds-checkbox.a11y.spec.ts::should have aria-checked="false" by default`; `...::should have aria-checked="true" when checked`; `...::should have aria-checked="mixed" when indeterminate`; `bds-checkbox.keyboard.spec.ts::should update aria-checked to "true" after Space press`; `...::should update aria-checked to "false" after second Space press`.

---

### FM-36 | `required` renders `aria-required`, the `*` indicator and the label wrapper

- **ID:** FM-36
- **Category:** null-empty
- **Risk:** a11y/visual.
- **Input that reveals it:** `<bds-checkbox required>`; without `required`.
- **Observed current behavior:** `aria-required="true"` or absent (`bds-checkbox.tsx:246`); `.bds-checkbox__required-indicator` rendered with `aria-hidden` (`bds-checkbox.tsx:275-277`); `required` alone makes `showLabelContent` true (`bds-checkbox.tsx:239`).
- **Recommended contract:** as observed.
- **Contract status:** confirmed
- **Why it matters:** announced "required" state.
- **Covered by:** None (gap).

---

### FM-37 | `info` renders the info icon and tooltip; empty `info` renders neither

- **ID:** FM-37
- **Category:** null-empty
- **Risk:** visual/a11y.
- **Input that reveals it:** `info="hint"`, `info=""`.
- **Observed current behavior:** `{this.info && <span class="bds-checkbox__info">...<bds-tooltip>{this.info}</bds-tooltip>}` (`bds-checkbox.tsx:279-284`); `info !== ''` also forces the label wrapper (`bds-checkbox.tsx:239`).
- **Recommended contract:** as observed.
- **Contract status:** confirmed
- **Why it matters:** `info` is a public prop with no coverage.
- **Covered by:** None (gap).

---

### FM-38 | `error` styling: class and `aria-invalid`, suppressed when disabled

- **ID:** FM-38
- **Category:** equivalence
- **Risk:** visual/a11y — an error state on a disabled control is misleading and conflicts with the disabled styling.
- **Input that reveals it:** `error`; `error disabled`. Probe: `error disabled` renders only `bds-checkbox--disabled`.
- **Observed current behavior:** `isError = (error && !disabled) || isInvalid` (`bds-checkbox.tsx:194-197`); class and `aria-invalid` use `isError`.
- **Recommended contract:** `error` sets `bds-checkbox--error` and `aria-invalid="true"`; `disabled` suppresses the `error` prop.
- **Contract status:** confirmed
- **Why it matters:** the suppression is an explicit `!this.disabled`.
- **Covered by:** `bds-checkbox.variants.spec.ts::should apply class bds-checkbox--error when error="true"` (class only). `aria-invalid`, `error` + `disabled` suppression: None (gap).

---

### FM-39 | `isInvalid` is not suppressed by `disabled`

- **ID:** FM-39
- **Category:** component-contract-bypass
- **Risk:** visual/a11y — `(error && !disabled) || isInvalid` lets a stale `isInvalid` paint error styling on a control that was disabled after a failed submit.
- **Input that reveals it:** trigger `invalid` (FM-20), then set `disabled`.
- **Observed current behavior:** `isInvalid` stays true until `updateFormValidity` sees a valid state, so the disabled control keeps `aria-invalid="true"` and the error class.
- **Recommended contract:** either disabled suppresses both sources of error, or only the `error` prop.
- **Contract status:** pending-decision
- **Why it matters:** edge case reachable by fieldset-disabling after a validation failure.
- **Covered by:** None (blocked on decision).

---

### FM-40 | PENDING A11Y: disabled checkboxes are hidden from assistive technology

- **ID:** FM-40
- **Category:** component-contract-bypass
- **Risk:** a11y — `hideFromScreenReaders` is `closest('bds-checkbox-card') !== null || isDisabled` and drives both `aria-hidden="true"` and `tabindex=-1` (`bds-checkbox.tsx:207-209,250,252`). A disabled checkbox with `role="checkbox"` and `aria-disabled="true"` is thereby removed from the accessibility tree: a screen-reader user never learns the option exists. The `aria-disabled` set on the same element is then unreachable.
- **Input that reveals it:** `<bds-checkbox disabled label="x">`. Probe: `aria-hidden="true"`.
- **Observed current behavior:** `aria-hidden="true"` for disabled.
- **Recommended contract:** either (a) disabled stays perceivable (`aria-disabled` only, with or without `tabindex=-1`), or (b) hidden by design. Hiding the checkbox inside a card (the card owns the semantics) is clearly intended and separate.
- **Contract status:** pending-decision
- **Why it matters:** WCAG 4.1.2 concern; the existing a11y test only asserts `aria-disabled` and `tabindex=-1`, not `aria-hidden`, so there is no conflicting test.
- **Covered by:** `bds-checkbox.a11y.spec.ts::should have aria-disabled and tabindex="-1" when disabled` covers the non-conflicting half (blocked on decision for `aria-hidden`).

---

### FM-41 | Inside `bds-checkbox-card` the checkbox is hidden from AT and removed from tab order

- **ID:** FM-41
- **Category:** component-contract-bypass
- **Risk:** a11y — the card owns the interaction; a nested focusable `role="checkbox"` would double-announce and double-stop.
- **Input that reveals it:** a `bds-checkbox` rendered as a descendant of `<bds-checkbox-card>` (both registered).
- **Observed current behavior:** `this.el.closest('bds-checkbox-card') !== null` is evaluated per render (`bds-checkbox.tsx:207-209`), so reparenting the element into a card without a re-render leaves it exposed.
- **Recommended contract:** `aria-hidden="true"` and `tabindex="-1"` while inside a card.
- **Contract status:** confirmed
- **Why it matters:** dependency on the card contract.
- **Covered by:** None (gap) in the `bds-checkbox` suite; the card suites cover the card side.

---

### FM-42 | `tabindex` and tab-stop: `0` when enabled, `-1` when disabled

- **ID:** FM-42
- **Category:** equivalence
- **Risk:** a11y — keyboard reachability.
- **Input that reveals it:** default and disabled.
- **Observed current behavior:** `tabindex={hideFromScreenReaders ? -1 : 0}` (`bds-checkbox.tsx:252`).
- **Recommended contract:** `0` for an enabled checkbox outside a card; `-1` otherwise.
- **Contract status:** confirmed
- **Why it matters:** the tab stop is the host.
- **Covered by:** `bds-checkbox.a11y.spec.ts::should have tabindex="0" when not disabled`; `bds-checkbox.a11y.spec.ts::should have aria-disabled and tabindex="-1" when disabled`.

---

### FM-43 | Focus on the inner `<input>` is forwarded to the host

- **ID:** FM-43
- **Category:** race-timing
- **Risk:** a11y — if the inner input ever receives focus (label `for`, browser validation focus attempt), focus must land on the real tab stop; a forwarder that recurses (host focus -> input focus) would loop.
- **Input that reveals it:** dispatch `focus` on the inner `<input>`; spy on `el.focus`.
- **Observed current behavior:** `onFocus={() => (this.el as HTMLElement).focus()}` (`bds-checkbox.tsx:263`, currently uncovered).
- **Recommended contract:** exactly one `host.focus()` call per inner-input focus, no recursion. Per project memory, a `focus` spy must use `mockImplementation(() => undefined)` in mock-doc.
- **Contract status:** confirmed
- **Why it matters:** the only uncovered render branch; see FM-28.
- **Covered by:** `bds-checkbox.lifecycle.spec.ts::inner input focus > forwards focus on the inner input to the host exactly once`.

---

### FM-44 | Slotted/descendant interactive content toggles the checkbox on click and Space

- **ID:** FM-44
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — the host handles `click` and the `KeyboardController` handles `keydown` on the whole host (`bds-checkbox.tsx:253,116-119`), so clicking or pressing Space on a link, button or the tooltip icon inside the label (e.g. "I accept the <a>terms</a>") toggles the checkbox and, for Space, calls `preventDefault`. A native `<label>` does not toggle for clicks on interactive descendants.
- **Input that reveals it:** `label` plus an `info` icon; click the `.bds-checkbox__info` element; dispatch Space on a descendant.
- **Observed current behavior:** any bubbling click or keydown from a descendant reaches the host handlers; there is no `event.target` filter.
- **Recommended contract:** either descendants that are interactive do not toggle, or all descendants toggle (current). Not determinable from code or plan.
- **Contract status:** pending-decision
- **Why it matters:** terms-link and info-tooltip use cases are the common ones; also see FM-30 on slot rendering.
- **Covered by:** None (blocked on decision).

---

## F. Keyboard

### FM-45 | Space and Shift+Space toggle; other keys do not

- **ID:** FM-45
- **Category:** equivalence
- **Risk:** a11y — APG checkbox pattern is Space-only (Enter submits a form instead).
- **Input that reveals it:** Space, Shift+Space, Enter, ArrowDown, Escape.
- **Observed current behavior:** `componentDidLoad` registers `Space` and `[Space, Shift]` bindings to the same handler (`bds-checkbox.tsx:116-119`).
- **Recommended contract:** Space and Shift+Space toggle exactly once; Enter, arrows and Escape do nothing.
- **Contract status:** confirmed
- **Why it matters:** documented pattern.
- **Covered by:** `bds-checkbox.keyboard.spec.ts::should check the checkbox when Space is pressed while unchecked`; `...::should check the checkbox when Shift+Space is pressed while unchecked`; `...::should emit bdsChange when Shift+Space is pressed`; `...::should uncheck the checkbox when Space is pressed while checked`; `...::should NOT toggle on Enter (Space-only pattern)`; `...::should NOT toggle on ArrowDown`; `...::should NOT toggle on Escape`; `bds-checkbox-keyboard.spec.ts::should not toggle on Enter keydown (Space-only pattern)`; `...::should not toggle on ArrowDown keydown`. These two keyboard spec files overlap heavily (same behaviors twice); only the Shift+Space cases are unique to `bds-checkbox.keyboard.spec.ts`.

---

### FM-46 | Held Space (auto-repeat) and unbound modifier combinations do not toggle

- **ID:** FM-46
- **Category:** race-timing
- **Risk:** a11y/functional — holding Space would flip the checkbox at the repeat rate; Ctrl/Alt/Meta+Space belongs to the browser/OS/IME.
- **Input that reveals it:** `keydown` Space with `repeat: true`; Ctrl+Space; Alt+Space; Meta+Space; a `keyup` Space.
- **Observed current behavior:** `_matchesTrigger` rejects `event.repeat` unless the binding opts in (`KeyboardController.ts:357-360`); only `space` and `shift+space` combinations are bound. Probe: `repeat: true` and Ctrl+Space both left `checked=false`.
- **Recommended contract:** one toggle per physical press; no toggle on repeat, on unbound modifier combinations, or on `keyup`.
- **Contract status:** confirmed
- **Why it matters:** the test pins the controller defaults the checkbox depends on.
- **Covered by:** `bds-checkbox.lifecycle.spec.ts::Space key edge cases > toggles once for a single Space press` (positive control); `...::does not toggle on an auto-repeated Space keydown`; `...::does not toggle on Space combined with ctrlKey`; `...::does not toggle on Space combined with altKey`; `...::does not toggle on Space combined with metaKey`; `...::does not toggle on Space keyup`.

---

### FM-47 | BUG: Space handling is not re-attached after the element is moved or reconnected

- **ID:** FM-47
- **Category:** race-timing
- **Risk:** a11y/functional — `disconnectedCallback` calls `_keyboard.detach()` (`bds-checkbox.tsx:122-124`) but the only `attach()` is in `componentDidLoad` (`bds-checkbox.tsx:111-120`), which does not re-run on reconnect. Any re-parenting (framework list reordering, drag-and-drop, moving a node into a card or group) leaves a checkbox that works by click but ignores Space for keyboard users.
- **Input that reveals it:** `appendChild` the loaded checkbox into another container. Probe on `rootInstance._keyboard`: `detach` called 1 time, `attach` called 0 times after the move. The probe could not observe the lost Space handling directly because mock-doc ignores `AbortSignal` aborts and the listeners survive; a test must therefore spy `attach` (or assert the spy count) rather than dispatch a key.
- **Observed current behavior:** no `connectedCallback` re-attach.
- **Recommended contract:** after disconnect + reconnect the keyboard bindings are attached again.
- **Contract status:** confirmed
- **Why it matters:** silent keyboard regression for moved nodes.
- **Covered by:** None (gap). Test must fail against current code; hand off to `frontend-subagent`.

---

### FM-48 | `disconnectedCallback` detaches the keyboard controller

- **ID:** FM-48
- **Category:** race-timing
- **Risk:** memory/listener leak — document-level `pointerdown`/`keydown` listeners are registered by `attach` (`KeyboardController.ts:attach`).
- **Input that reveals it:** remove the host and spy on `_keyboard.detach`.
- **Observed current behavior:** `detach()` is called (probe: count 1 after a move, 2 after removal) (`bds-checkbox.tsx:122-124`, currently uncovered).
- **Recommended contract:** `detach` called on disconnect.
- **Contract status:** confirmed
- **Why it matters:** mock-doc ignores abort so the call must be asserted via a spy on the controller method.
- **Covered by:** `bds-checkbox.lifecycle.spec.ts::disconnection > detaches the keyboard controller when the host is removed`; `...::does not detach the keyboard controller while the host stays connected`.

---

### FM-49 | Space on a disabled checkbox is still `preventDefault`ed

- **ID:** FM-49
- **Category:** component-contract-bypass
- **Risk:** a11y — page scroll is suppressed while a disabled checkbox holds focus (it is `tabindex=-1` but can still be focused by click).
- **Input that reveals it:** Space keydown on a disabled checkbox, inspecting `defaultPrevented`.
- **Observed current behavior:** the binding is attached unconditionally with `preventDefault: true` default; the handler no-ops when disabled (`bds-checkbox.tsx:113-119`, `KeyboardController.ts:326-333`).
- **Recommended contract:** either suppress or allow the default scroll for a disabled checkbox; not specified.
- **Contract status:** pending-decision
- **Why it matters:** minor; the user cannot scroll with Space after clicking a disabled checkbox.
- **Covered by:** None (blocked on decision).

---

## Reconciliation notes

- **Existing tests that encode a possible bug:** none found. The only candidates (`should not render content area when no label, info, or required`, `should have aria-disabled and tabindex="-1" when disabled`) do not assert the behaviors FM-30 and FM-40 question.
- **Existing tests with misleading names:** `bds-checkbox.keyboard.spec.ts::should check the checkbox (form field value enabled) after toggling with Space` and `...::should uncheck the checkbox (form field value removed) after unchecking with Space` assert the inner `<input>.checked`, not the form value (FM-13 remains uncovered).
- **Duplicated spec files:** `bds-checkbox-keyboard.spec.ts` and `bds-checkbox.keyboard.spec.ts` both live in `__test__/` and overlap; consolidating is a cleanup, not a coverage gain.
- **No `suppressConsoleWarn()` is called in the existing `bds-checkbox` specs**; they pass without it. New specs should mirror the existing `suppressConsoleError()` + `attachInternals()` boilerplate and add `suppressConsoleWarn()` only if a Stencil dev-mode warning appears.

## Summary table

| Status | Rows |
| --- | --- |
| confirmed, covered | FM-05 (partial), FM-09, FM-35, FM-42, FM-45 |
| confirmed, partially covered | FM-01, FM-02, FM-11, FM-38 |
| confirmed, gap (test should pass today) | FM-03, FM-04, FM-07, FM-12, FM-13, FM-14, FM-16, FM-19, FM-20, FM-21, FM-22, FM-26, FM-29, FM-36, FM-37, FM-41, FM-43, FM-46, FM-48 |
| confirmed BUG (test must fail until source fixed) | FM-06, FM-15, FM-18, FM-25, FM-30, FM-31, FM-33, FM-47 |
| pending-decision | FM-08, FM-10, FM-17, FM-23, FM-24, FM-27, FM-28, FM-32, FM-34, FM-39, FM-40, FM-44, FM-49 |
