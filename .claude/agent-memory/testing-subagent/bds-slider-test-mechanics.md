---
name: bds-slider-test-mechanics
description: How to drive bds-slider track clicks, handle events and form-value assertions in newSpecPage, plus which catalog rows are known-failing
metadata:
  type: project
---

Track click: assign `track.getBoundingClientRect = () => ({ left, width, ... }) as DOMRect` on `.bds-slider__track-base`, then dispatch `new MouseEvent('click', { clientX, bubbles: true })` on `.bds-slider__wrapper` (mock-doc honors `clientX`). Without the stub width is 0 and the value becomes NaN (known defect).

Form value: `(page.rootInstance as BdsSlider).internals.setFormValue as jest.Mock` is the mock from `attachInternals()`; `mockClear()` after mount, then assert `toHaveBeenLastCalledWith('10,20')`. The `input` event already registers the form value, `change` also emits `bdsChange`.

Handle events: set `input.value = 'N'` then dispatch `new Event('input'|'change', { bubbles: true })`; focus/blur tooltip classes work with a plain dispatched `Event('focus')` (no recursion, unlike `.focus()`).

`SliderService.snapToStep` clamps to `max` after snapping, so with `step=30` a far-above value returns `100`, only values that round onto the step return `90`.

Known source defects (tests would fail today, leave untested until fixed): `discrete` with fractional step renders a pip at `max` (`min=0 max=2.1 step=0.3`), empty `disabled-handlers`/`value` parse to `[0]`.

**Why:** avoids re-deriving the harness each session. **How to apply:** reuse for any further bds-slider spec work.
