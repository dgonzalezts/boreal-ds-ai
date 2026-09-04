---
name: bds-date-picker-min-max-nav-guard
description: bds-date-picker min/max implementation — validator key choice, nav-guard placement, and the unregistered-vs-registered child custom element attribute/property test gotcha hit while testing it
metadata:
  type: project
---

Implemented `bds-date-picker` Task 11 (EOA-17138): `min`/`max` props, nav-guard, and
constraint-validation wiring, on top of Task 10's already-complete `date-engine` min/max
support (`generateMonthGrid`'s `min`/`max` options, `isMonthFullyDisabled`).

**Validator keys:** used the native `ValidityStateFlags` keys `rangeUnderflow`/`rangeOverflow`
(two separate `IFormValidator` entries) rather than one combined custom key — matches the
constraint-validation API's own vocabulary and keeps each check independently testable via
`setValiditySpy.toHaveBeenCalledWith({ rangeUnderflow: true }, ...)`.

**Nav guard owner:** `bds-calendar-grid` is documented "fully controlled by its parent — owns
no internal state," so `prevDisabled`/`nextDisabled` are computed in `bds-date-picker.tsx` (a
`navGuard` getter that runs `generateMonthGrid` + `isMonthFullyDisabled` against only the
immediately-adjacent prev/next month, not every reachable month) and passed down as plain
boolean `@Prop()`s on `bds-calendar-grid`, applied directly to the two `bds-button`
`disabled` props in `renderHeader()`. No defense-in-depth guard was added inside
`handleMonthNavigate` — a disabled native `<button>` never dispatches a `click` event at all,
so `bds-button`'s own `disabled || loading` internal guard plus the disabled attribute is
already sufficient; a synthetic-event bypass isn't a realistic threat model here.

**Test gotcha confirmed (extends [[stencil-child-component-props-in-tests]]):** whether a
child custom element's non-reflected `@Prop()` (e.g. `bds-button`'s `label`, `disabled`) shows
up via `getAttribute()` on the *outer* tag in a spec depends on whether that child component
class is in the current spec file's `newSpecPage({ components: [...] })` list:
- **Unregistered** child (e.g. `bds-calendar-grid`'s own spec files, which only register
  `BdsCalendarGrid`) — Stencil's h() falls back to plain `setAttribute` for unknown elements,
  so `outerBdsButton.getAttribute('disabled')`/`.getAttribute('label')` both work directly.
- **Registered** child (e.g. `bds-date-picker`'s specs, which register `BdsButton` too via
  `DATE_PICKER_COMPONENTS`) — Stencil manages it as a real component instance and sets
  non-reflected props as JS properties only; `outerBdsButton.getAttribute(...)` returns `null`.
  Must instead assert on the *rendered inner DOM* — `bds-button`'s own `render()` puts
  `disabled={this.disabled || this.loading}` and `aria-label={this.label}` on its internal
  native `<button>`, so query `bdsButtonEl.querySelector('button')` and assert there.

  Added a `findNavButton()` test helper to `bds-date-picker/__test__/date-picker.test-utils.ts`
  that locates the calendar header's nav `bds-button`s via their inner `<button>`'s
  `aria-label` (icon-only buttons have no visible text, so `textContent` matching — the
  existing `findFooterButton()` pattern — doesn't apply here).

**ElementInternals mock limitation confirmed:** `utils/testing/mocks/elementInternals.ts`'s
`setValidity`/`reportValidity` are bare `jest.fn()`s that never actually populate
`internals.validationMessage` — so a test asserting `field.errorMessage` after
`reportValidity()`/a dispatched `invalid` event will always see `undefined`, regardless of
what the component actually passed to `setValidity()`. Assert on `setValiditySpy` call args
for message content instead; only `field.error` (boolean) is verifiable end-to-end through a
real `dispatchEvent(new Event('invalid'))`.
