# Failure-Mode Catalog — `bds-slider`

Audited against `packages/boreal-web-components/src/components/forms/bds-slider/bds-slider.tsx` (plus `helpers/SliderService.ts`, `helpers/parseValues.ts`, `helpers/SliderDOMController.ts`) as of 2026-10-27, on branch `feature/EOA-19936_increase-unit-test-coverage-popover-slider-checkbox_DG`. Rows are derived from reading the component source and its pre-existing spec suite (`__test__/bds-slider.{basics,a11y,variants,events,methods}.spec.ts`, 70 tests, all passing), not from a plan's stated test list.

Scope of this first audit: the whole component — props, runtime prop reactivity, events, FACE/form behavior, keyboard/pointer/a11y, min/max/step/range edge cases and the three helpers. Behaviors marked "(probed)" were reproduced against current code with a throwaway `newSpecPage` probe (deleted afterwards, nothing committed); the others are derived from static reading and say so.

Coverage baseline for this audit (`src/components/forms/bds-slider`, scoped `--collectCoverageFrom`): **statements 73.75% (208/282), branches 54.41% (74/136), functions 76.25%, lines 76.37%** — below the 80% gate on all four.

| File | % Stmts | % Branch | Uncovered lines |
| --- | --- | --- | --- |
| `bds-slider.tsx` | 70.31 | 65.71 | 159-196 (all `@Watch` handlers, `formAssociatedCallback`), 305-313 (`onHandleFocus`/`onHandleBlur`/`onHandleInactive`), 354, 432-436 (`input`/`focus`/`blur`/`pointerup` handlers), 457-491 (entire `handleTrackClick`), 506, 563-564, 575 |
| `helpers/SliderService.ts` | 80.55 | 34.28 | 32-42 (entire `applyCollision`) |
| `helpers/SliderDOMController.ts` | 66.66 | 0 | 9-19 (`addTooltipsStates`/`removeTooltipsStates`) |
| `helpers/parseValues.ts` | 86.95 | 57.14 | 24-25 (non-JSON string fallback), 45 (range with a single value) |

Legend: rows marked **confirmed** can be tested now; rows marked **pending-decision** need a ruling first (and one of them conflicts with an existing test, see FM-SL-48). `Covered by: none` means the row is a gap.

---

## A. Value parsing and normalization

### FM-SL-01 | Empty-string `value` / `disabledHandlers` parses to `[0]` instead of the fallback

- **ID:** FM-SL-01
- **Category:** null-empty
- **Risk:** functional — `disabled-handlers=""` (an empty attribute, or a framework binding an empty string) silently disables whichever handle sits at value `0`; `value=""` yields `[0]` rather than the "malformed → fallback" result.
- **Input that reveals it:** `parseValues('', [])`; `<bds-slider value="[0]" disabled-handlers="">`.
- **Observed current behavior:** (probed) `JSON.parse('')` throws, the `catch` branch runs `Number('')`, which is `0` (not `NaN`), so `[0]` is returned (`helpers/parseValues.ts:21-25`). The handle at `0` renders `disabled`. `'null'` also parses to `[0]` and `'true'` to `[1]`.
- **Recommended contract:** an empty or whitespace-only string is "no values" and returns the caller's fallback; the `parseValues` docblock already states "anything malformed → safe fallback".
- **Contract status:** confirmed
- **Why it matters:** `disabledHandlers` defaults to `"[]"`, so an empty string must behave the same as the default.
- **Covered by:** none (the row is `confirmed` but current behavior returns `[0]`, so a test would fail today; left to the defect fix)

### FM-SL-02 | Value arity is normalized to the slider `type`

- **ID:** FM-SL-02
- **Category:** equivalence
- **Risk:** visual/functional — the rendered handle count and `getValues()` length must match `type` regardless of the shape of `value`.
- **Input that reveals it:** `single` with `[10,20]`; `range` with `[10]`; `range` with `[10,20,30]`; `[]`; `"abc"`; `[1,"x"]`; bare attribute `value="50"`.
- **Observed current behavior:** (probed) `single` + `[10,20]` -> `[10]`; `range` + `[10]` -> `[10, max]` (`[10,100]`); `range` + `[10,20,30]` -> `[10,20]`; `[]` and `"abc"` -> `[min]` after clamp; `[1,"x"]` -> `[1]` (`parseValues.ts:12-29`, `resolveValues` `:37-49`).
- **Recommended contract:** exactly 1 value for `single`, exactly 2 for `range`; missing second value defaults to `max`; surplus values are dropped; unparseable input falls back to `min`.
- **Contract status:** confirmed
- **Why it matters:** `value` is documented as accepting `number`, `number[]` or a JSON string for vanilla HTML.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — resolveValues` (keeps only the first value for a single slider given two values; defaults the missing second value of a range slider to max; uses the configured max as the default second value of a range slider; drops surplus values beyond the second one for a range slider; falls back to min for an empty array / an unparseable string / an empty JSON array string; ignores non-numeric entries inside a JSON string; accepts a bare numeric string as a single value); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — value normalization › arity follows the slider type` (renders one handle and keeps the first value when a single slider receives two values; defaults the second handle to max when a range slider receives one value; drops surplus values on a range slider; falls back to min for an unparseable value; falls back to min for an empty JSON array; ignores non-numeric entries inside a JSON value; accepts a bare numeric attribute as a single value). Pre-existing: `bds-slider.basics.spec.ts::Should render one input for a single-value slider`, `::Should render two inputs for a range slider`.

### FM-SL-03 | Initial and programmatic values are clamped to `[min, max]` at the boundaries

- **ID:** FM-SL-03
- **Category:** boundary
- **Risk:** visual/form — a value outside the range renders a handle off the track and submits an out-of-range number.
- **Input that reveals it:** `value="[-1]"`, `[0]`, `[100]`, `[101]` with `min=0 max=100`; the same through the `value` attribute, `setValues`, and the `value` watcher.
- **Observed current behavior:** `resolveValues` maps every parsed value through `service.clamp` (`bds-slider.tsx:345-348`); `clamp` is `Math.min(Math.max(v, min), max)` (`SliderService.ts:10-12`).
- **Recommended contract:** the stored value is always within `[min, max]` inclusive; the exact boundary values are preserved.
- **Contract status:** confirmed
- **Why it matters:** this is the primary range invariant (see FM-SL-14, FM-SL-41 and FM-SL-35 for the paths that break it).
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderService.clamp` (raises a value below min to min; lowers a value above max to max; preserves the exact min boundary; preserves the exact max boundary; leaves an in-range value untouched); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — value normalization › values stay within min and max` (stores an initial value below min / exactly min / exactly max / above max as the expected boundary; clamps an initial value against a non-zero min and max; clamps each handle of an initial range; stores the exact clamped value after setValues above max; stores the exact clamped value after setValues below min; preserves the exact boundaries passed to setValues; clamps a value assigned after load; renders the clamped value on the native input).

### FM-SL-04 | Programmatic values are not snapped to `step`

- **ID:** FM-SL-04
- **Category:** equivalence
- **Risk:** visual/form — the internal value, tooltip, `aria-valuenow` and submitted value can disagree with what the native `<input type="range">` displays (browsers snap `value` to the nearest step).
- **Input that reveals it:** `step=10`, `setValues([55])` or `value="[55]"`.
- **Observed current behavior:** (probed) `resolveValues` only clamps; `getValues()` returns `[55]`. User interaction goes through `snapToStep` (`:278-296`), programmatic input does not.
- **Recommended contract:** unknown — either snap programmatic values (consistent with interaction) or preserve them (consistent with `value` semantics).
- **Contract status:** pending-decision
- **Why it matters:** decides whether `getValues()` can ever return an off-step number.
- **Covered by:** none

### FM-SL-05 | Range handles can be inverted or coincident through `value` / `setValues` / form restore

- **ID:** FM-SL-05
- **Category:** boundary
- **Risk:** visual — the connect bar gets a negative width (invalid CSS, bar disappears or inverts); the handles contradict the "min handle <= max handle" model that `applyCollision` assumes.
- **Input that reveals it:** `type="range" value="[80,20]"`; `value="[50,50]"`; `setValues([90,10])`.
- **Observed current behavior:** (probed) `[80,20]` is stored as-is; the connect element gets `left: 80%; width: -60%`. `applyCollision` is only applied to the handle being dragged (`handleInputEvent`, `handleTrackClick`), never to incoming values (`bds-slider.tsx:345-348`).
- **Recommended contract:** unknown — sort the pair, apply collision, or leave it to the consumer.
- **Contract status:** pending-decision
- **Why it matters:** a consumer-supplied unsorted pair is a likely real-world input (e.g. a saved filter).
- **Covered by:** none

### FM-SL-06 | `min > max` and `min == max`

- **ID:** FM-SL-06
- **Category:** boundary
- **Risk:** visual/form — degenerate ranges produce meaningless percentages and collapsed values.
- **Input that reveals it:** `min=100 max=0`; `min=50 max=50`.
- **Observed current behavior:** (probed) `min>max`: `clamp(50)` returns `0` (`Math.min(Math.max(50,100),0)`), `toPercent(50)` returns `50`; `min==max`: `toPercent` returns `0` through the `range === 0` guard (`SliderService.ts:48-52`).
- **Recommended contract:** unknown (reject/warn and fall back, swap, or document as undefined).
- **Contract status:** pending-decision
- **Why it matters:** the `range === 0` guard shows division by zero was considered for `min==max` but `min>max` was not.
- **Covered by:** none

### FM-SL-07 | Non-numeric attributes and non-positive `step` propagate `NaN`

- **ID:** FM-SL-07
- **Category:** boundary
- **Risk:** form/event/a11y — `NaN` is stored, emitted in `bdsChange`, serialized as the string `"NaN"` into the form value, and rendered in the tooltip.
- **Input that reveals it:** `min="abc"`; `step="0"` then a `change` event; negative `step`.
- **Observed current behavior:** (probed) `min="abc"` -> prop `NaN` -> `internalValues = [NaN]`. `step="0"`: `snapToStep` computes `Math.round(x/0) * 0 + min` -> `NaN`; after a `change` event the form value is registered as `"NaN"` (`SliderService.ts:17-19`). `step` is documented "Must be a positive number" but nothing enforces it.
- **Recommended contract:** unknown fallback (default `1` and warn, vs clamp to a minimum), but a stored or emitted value must never be `NaN`.
- **Contract status:** pending-decision
- **Why it matters:** the doc comment states the positive-number precondition, not what happens when it is violated.
- **Covered by:** none

### FM-SL-08 | `discrete` with `step <= 0` never terminates

- **ID:** FM-SL-08
- **Category:** boundary
- **Risk:** functional — the tab hangs rendering pips; `step=0` makes `total = Infinity`.
- **Input that reveals it:** `<bds-slider discrete step="0">` (derived by static reading; not run because it would not terminate).
- **Observed current behavior:** `getPipPositions` loops `for (let i = 1; i < total; i++)` with `total = (max - min) / step` (`SliderService.ts:78-89`); `step=0` gives `Infinity`.
- **Recommended contract:** pip generation always terminates; with an invalid step no pips are rendered (the value fallback is decided in FM-SL-07).
- **Contract status:** confirmed
- **Why it matters:** a hang is never an acceptable failure mode for a prop typo, whatever the fallback ruling.
- **Covered by:** none

### FM-SL-09 | `step` that does not divide the range makes `max` unreachable by interaction

- **ID:** FM-SL-09
- **Category:** boundary
- **Risk:** functional — the user cannot select `max`.
- **Input that reveals it:** `min=0 max=100 step=30`, change event with value `100`.
- **Observed current behavior:** (probed) `snapToStep(100)` returns `90` (`SliderService.ts:17-19`), which matches the native `<input type="range">` rule.
- **Recommended contract:** the highest interaction value is the largest `min + k*step <= max`, matching native range semantics; the result never exceeds `max`.
- **Contract status:** confirmed
- **Why it matters:** documents that this is intentional parity with the platform rather than a snapping bug.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderService.snapToStep` (snaps to the largest step multiple not above max when the step does not divide the range; never returns a value above max); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › step snapping › stops at the largest step multiple when the step does not divide the range`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.track-click.spec.ts::bds-slider — track click › single slider › snaps a click at the right edge to the largest step not above max`.

### FM-SL-10 | Fractional steps leak floating-point noise into the value

- **ID:** FM-SL-10
- **Category:** boundary
- **Risk:** visual/form — tooltips, `bdsChange` payloads and the submitted value show `0.30000000000000004`.
- **Input that reveals it:** `step=0.1`, interaction value `0.3`.
- **Observed current behavior:** (probed) `snapToStep(0.3)` -> `0.30000000000000004`, `snapToStep(0.7)` -> `0.7000000000000001`.
- **Recommended contract:** unknown (round to the decimal precision of `step`/`min`, or leave the raw float).
- **Contract status:** pending-decision
- **Why it matters:** the value is rendered verbatim in the tooltip (`String(value)`) and written to `FormData`.
- **Covered by:** none

### FM-SL-11 | A pip can be rendered on top of `max`

- **ID:** FM-SL-11
- **Category:** boundary
- **Risk:** visual — a duplicate pip at 100% overlaps the `max` end of the track.
- **Input that reveals it:** `discrete min=0 max=2.1 step=0.3` (`2.1 / 0.3 = 7.000000000000001`).
- **Observed current behavior:** derived by static reading plus a numeric check of the division; the loop condition `i < total` admits `i = 7`, whose value is `max`. The method's docblock says "excluding min and max" (`SliderService.ts:75-89`).
- **Recommended contract:** pips are generated strictly between `min` and `max`.
- **Contract status:** confirmed
- **Why it matters:** floating-point `total` makes the `< total` exclusion of `max` unreliable.
- **Covered by:** none (the pip-count test uses `0..1000 step 100` only, which is exact)

### FM-SL-12 | Pip count is unbounded

- **ID:** FM-SL-12
- **Category:** boundary
- **Risk:** performance — `discrete min=0 max=100000 step=1` renders ~100k DOM nodes.
- **Input that reveals it:** large `(max - min) / step` with `discrete`.
- **Observed current behavior:** `renderPips` maps every position (`bds-slider.tsx:522-534`); no cap.
- **Recommended contract:** unknown (cap, hide pips above a density threshold, or leave to the consumer).
- **Contract status:** pending-decision
- **Why it matters:** same bug class as `bds-table` windowing: an unbounded `.map` in `render()`.
- **Covered by:** none

---

## B. Range collision, pointer and track interaction

### FM-SL-13 | Range collision keeps handles at least one step apart

- **ID:** FM-SL-13
- **Category:** boundary
- **Risk:** functional — handles overlap or cross.
- **Input that reveals it:** `range [49,50]`, `change` on the min handle with `60`; `change` on the max handle with a value below the min handle; `single` type with the same call.
- **Observed current behavior:** `applyCollision` caps handle 0 at `values[1] - step`, floors handle 1 at `values[0] + step`, and is a no-op for `single` (`SliderService.ts:26-43`). (probed) a drag past the other handle is corrected back to `[49,50]`.
- **Recommended contract:** after any interaction in range mode `values[1] - values[0] >= step`; `single` never changes through collision.
- **Contract status:** confirmed
- **Why it matters:** the whole range-mode invariant depends on it.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderService.applyCollision` (caps the min handle one step below the max handle; floors the max handle one step above the min handle; uses the configured step as the minimum distance between handles; allows the handles to sit exactly one step apart; leaves non-colliding moves untouched; does not touch the handle that was not changed; returns a copy and leaves the input array untouched; never changes the values of a single slider; never changes a range slider holding fewer than two values); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › range collision` (keeps the min handle one step below the max handle; keeps the max handle one step above the min handle; uses the configured step as the minimum distance between handles; writes the corrected value back to the dragged input; shows the corrected value in the tooltip of the dragged handle; keeps the other handle untouched when one handle is committed; emits the collision-corrected pair on commit; lets the single slider move past any value without collision correction). Collision-correction inputs that start outside `[min, max]` are FM-SL-14 and are not tested.

### FM-SL-14 | Collision correction can push a value outside `[min, max]`

- **ID:** FM-SL-14
- **Category:** boundary
- **Risk:** form/visual — a value below `min` or above `max` is stored, emitted and submitted.
- **Input that reveals it:** `type="range" value="[0,0]"`, `change` on the min handle (any value); `value="[100,100]"`, `change` on the max handle.
- **Observed current behavior:** (probed) `[0,0]` -> `[-1, 0]`; `[100,100]` -> `[100, 101]`. `applyCollision` computes `maxVal - margin` / `minVal + margin` and the result is never re-clamped (`SliderService.ts:34-41`; `handleInputEvent` `:278-296` applies no clamp afterwards).
- **Recommended contract:** values always stay within `[min, max]` (FM-SL-03); when collision cannot be satisfied the handle stays put.
- **Contract status:** confirmed
- **Why it matters:** produces out-of-range submitted values from a legal initial state (coincident handles are accepted per FM-SL-05).
- **Covered by:** none

### FM-SL-15 | A `change` event whose corrected value equals the previous state still emits

- **ID:** FM-SL-15
- **Category:** race-timing
- **Risk:** event contract — consumers get a `bdsChange`/`valueChange` for a no-op, triggering redundant work.
- **Input that reveals it:** `range [49,50]`, `input` with `60`, then `change` with `50` on the min handle.
- **Observed current behavior:** (probed) the value is corrected to `[49,50]` and `bdsChange` still fires with `{ value: [49,50] }` (`handleChangeEvent` `:299-303` emits unconditionally).
- **Recommended contract:** unknown — suppress emission when nothing changed, or keep emitting per native `change`.
- **Contract status:** pending-decision
- **Why it matters:** same family as the reference-stable-update rule in `testing-knowledge`.
- **Covered by:** none

### FM-SL-16 | The `input` event updates state but emits nothing until `change`

- **ID:** FM-SL-16
- **Category:** race-timing
- **Risk:** event contract — Vue `v-model` (wired to `valueChange`) and React consumers are not updated during a drag, only on release; the form value, tooltip and connect bar are updated live.
- **Input that reveals it:** dispatch `input` on a handle.
- **Observed current behavior:** (probed) `bdsChange` call count stays `0` after `input`; `internalValues` and the form value already changed (`handleInputEvent` `:278-296`, `onInput` at `:432`).
- **Recommended contract:** unknown — keep native "commit on release" semantics, or add a live-change event.
- **Contract status:** pending-decision
- **Why it matters:** the `bdsChange` JSDoc says "whenever the slider value(s) change due to user interaction".
- **Covered by:** none (`bds-slider.events.spec.ts::Should emit bdsChange when input event fires on the handle` dispatches a `change` event despite its name)

### FM-SL-17 | Track click selects, snaps and clamps the value

- **ID:** FM-SL-17
- **Category:** boundary
- **Risk:** functional — clicking the track is the main mouse gesture besides dragging.
- **Input that reveals it:** stub `getBoundingClientRect` on `.bds-slider__track-base` to a known width; click `.bds-slider__wrapper` at `clientX` left of the track, at the left edge, at the midpoint, at the right edge, past the right edge; single and range; on the native input (must be ignored); when `disabled`.
- **Observed current behavior:** `handleTrackClick` ignores clicks when disabled, ignores clicks whose target is `.bds-slider__input`, clamps the percent to `[0,1]`, snaps via `snapToStep`, picks the nearest handle in range mode, applies collision, then syncs and emits (`bds-slider.tsx:456-491`).
- **Recommended contract:** the clicked position maps linearly to `[min, max]` and snaps to `step`; out-of-track clicks pin to `min`/`max`; the nearest handle moves in range mode; disabled sliders and clicks on the native input do nothing; one `bdsChange` + one `valueChange` per accepted click.
- **Contract status:** confirmed
- **Why it matters:** none of lines 457-491 are executed by the current suite.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.track-click.spec.ts::bds-slider — track click` — single: maps a click at the middle of the track to the middle of the range; maps a click on the left edge of the track to min; maps a click on the right edge of the track to max; pins a click left of the track to min; pins a click right of the track to max; maps a click linearly over a range that does not start at zero; snaps the clicked value to the nearest step; snaps a click at the right edge to the largest step not above max; reflects the clicked value on the input and the tooltip; registers the clicked value as the form value; emits exactly one bdsChange / one valueChange with the clicked value. Range: moves the min handle when the click is nearer to it; moves the max handle when the click is nearer to it; snaps the clicked value to the step before moving a handle; pins a click past the right edge to max for the max handle; emits exactly one bdsChange with both handle values; registers both handle values as the form value. Ignored: ignores a click on a disabled slider; ignores a click that lands on the native input. Not covered: collision on track click (only reachable with tied/coincident handles, FM-SL-18) and the zero-width track (FM-SL-20).

### FM-SL-18 | Track click with equidistant or coincident handles moves the min handle

- **ID:** FM-SL-18
- **Category:** equivalence
- **Risk:** functional — clicking to the right of two overlapping handles shoves the min handle left instead of moving the max handle right.
- **Input that reveals it:** `range [50,50]`, click at 80%.
- **Observed current behavior:** derived by static reading: `distanceToMin <= distanceToMax` picks handle 0, then collision caps it at `max - step` (`:477-487`).
- **Recommended contract:** unknown (tie-break toward the handle on the click's side).
- **Contract status:** pending-decision
- **Why it matters:** coincident handles are accepted input (FM-SL-05) and the tie-break is directionless.
- **Covered by:** none

### FM-SL-19 | Track click whose nearest handle is individually disabled is a silent no-op

- **ID:** FM-SL-19
- **Category:** component-contract-bypass
- **Risk:** functional — the user clicks near an enabled handle that is farther than a disabled one and nothing happens.
- **Input that reveals it:** `range [10,90] disabled-handlers="[10]"`, click at 20%.
- **Observed current behavior:** derived by static reading: nearest handle is 0, `isHandleDisabled(nextValues[0])` returns `true`, the function returns before touching handle 1 (`:484`).
- **Recommended contract:** unknown (stay a no-op, or move the nearest enabled handle).
- **Contract status:** pending-decision
- **Why it matters:** the intended affordance for per-handle disabling is unspecified.
- **Covered by:** none

### FM-SL-20 | Track click on a zero-width track stores `NaN`

- **ID:** FM-SL-20
- **Category:** boundary
- **Risk:** form/event — a click when the track has no layout width (hidden, collapsed container, programmatic `click()`, and `newSpecPage` itself) divides by zero.
- **Input that reveals it:** click `.bds-slider__wrapper` with `getBoundingClientRect().width === 0`.
- **Observed current behavior:** (probed) `(clientX - left) / 0` is `NaN`, `Math.min(Math.max(NaN,0),1)` is `NaN`, `internalValues` becomes `[NaN]` and a change is emitted (`:463-467`).
- **Recommended contract:** a click on a zero-width track is ignored; a stored or emitted value is never `NaN`.
- **Contract status:** confirmed
- **Why it matters:** also means any future track-click test that forgets to stub the rect gets `NaN` rather than a failure.
- **Covered by:** none

### FM-SL-21 | Track click ignores text direction

- **ID:** FM-SL-21
- **Category:** equivalence
- **Risk:** functional — in `dir="rtl"` the native range input mirrors, but the click percentage is always measured from the left edge.
- **Input that reveals it:** slider inside an RTL container, click near the visual start.
- **Observed current behavior:** derived by static reading (`:463-464`); not verifiable in mock-doc.
- **Recommended contract:** unknown (RTL support not specified for the component).
- **Contract status:** pending-decision
- **Why it matters:** low priority; route to manual QA if RTL is in scope.
- **Covered by:** none

### FM-SL-22 | `disabledHandlers` matches by value, so a handle moved onto a listed value becomes stuck

- **ID:** FM-SL-22
- **Category:** component-contract-bypass
- **Risk:** functional — a user drags an enabled handle onto a value listed in `disabledHandlers`; it becomes `disabled` and can never be moved off.
- **Input that reveals it:** `value="[10]" disabled-handlers="[30]"`, `change` to `30`.
- **Observed current behavior:** (probed) value becomes `[30]` and the input is re-rendered `disabled` (`isHandleDisabled` `:368-372`; JSDoc says each number "must match a value present in the `value` prop").
- **Recommended contract:** unknown (index-based disabling, or forbid moving onto a listed value).
- **Contract status:** pending-decision
- **Why it matters:** value-based matching is documented, but the stuck-handle consequence is probably unintended.
- **Covered by:** none; `bds-slider.variants.spec.ts::Should disable only the matching handle when disabled-handlers is set` and `bds-slider.a11y.spec.ts::Should set aria-disabled="true" on the input of a disabled-handler handle` cover only the static render.

### FM-SL-23 | A disabled slider still mutates its value when an `input`/`change` event is dispatched

- **ID:** FM-SL-23
- **Category:** component-contract-bypass
- **Risk:** functional — browsers drop user events on a `disabled` input, but programmatic dispatch (tests, automation, extensions) still changes state and the form value while only the emit is skipped.
- **Input that reveals it:** `disabled`, `value="[10]"`, dispatch `change` with value `90`.
- **Observed current behavior:** (probed) `internalValues` becomes `[90]`; `handleInputEvent` has no disabled guard and `handleChangeEvent` checks `isDisabled` only after mutation (`:299-303`).
- **Recommended contract:** unknown (the late `isDisabled` guard suggests intent to ignore, but it runs after the mutation).
- **Contract status:** pending-decision
- **Why it matters:** real users cannot reach this; only automation can, so risk is low.
- **Covered by:** none

### FM-SL-24 | `bdsClick` fires for a disabled slider

- **ID:** FM-SL-24
- **Category:** component-contract-bypass
- **Risk:** event contract — a disabled slider reports user clicks.
- **Input that reveals it:** `disabled`, `root.click()`.
- **Observed current behavior:** (probed) `bdsClick` fires once; `handleClick` has no guard (`:316-319`).
- **Recommended contract:** unknown (other Boreal controls suppress click events when disabled; this one does not).
- **Contract status:** pending-decision
- **Why it matters:** inconsistency with the disabled contract elsewhere in the library.
- **Covered by:** none (`bds-slider.events.spec.ts::Should emit bdsClick when the host element is clicked` covers the enabled path only)

### FM-SL-25 | Clicking a tooltip suppresses `bdsClick` and the track click

- **ID:** FM-SL-25
- **Category:** equivalence
- **Risk:** event contract — `bdsClick` is "emitted when the user clicks on the slider" but a click on a tooltip never reaches the host listener.
- **Input that reveals it:** click `.bds-slider__tooltip`.
- **Observed current behavior:** (probed) `bdsClick` call count is `0`; the tooltip's `onClick` calls `stopPropagation()` (`:505-507`).
- **Recommended contract:** unknown (deliberate to stop the tooltip from triggering `handleTrackClick`, but it also swallows `bdsClick`).
- **Contract status:** pending-decision
- **Why it matters:** the intent (avoid moving the value on a tooltip click) is probably right; swallowing the host event is a side effect.
- **Covered by:** none

---

## C. Events and public API

### FM-SL-26 | `setValues` and form reset emit `bdsChange` and `valueChange` exactly once with the normalized payload

- **ID:** FM-SL-26
- **Category:** equivalence
- **Risk:** event contract — v-model and listeners must see one event per change, with clamped values.
- **Input that reveals it:** `setValues([200])` (clamped), `setValues('[20,70]')`, form reset, with and without `disabled`.
- **Observed current behavior:** `emitChange` emits `bdsChange` `{ value }`, then `valueChange`, then syncs the form value; it returns immediately when `isDisabled` (`:358-366`).
- **Recommended contract:** one `bdsChange` (`{ value: number[] }`) and one `valueChange` (`number[]`) per call, payload already clamped; none while disabled.
- **Contract status:** confirmed
- **Why it matters:** this is the framework two-way-binding contract.
- **Covered by:** `bds-slider.events.spec.ts::Should emit bdsChange with a number array payload after setValues()`; `::Should emit bdsChange with a two-value array for a range slider`; `::Should emit valueChange alongside bdsChange with the same value array`; `::Should not emit bdsChange when the slider is disabled`; `::Should not emit valueChange when the slider is disabled`; `::Should emit bdsChange on formResetCallback`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — public API contract` (emits the clamped value in bdsChange after setValues above max; emits the clamped value in valueChange after setValues above max; emits both handles in a single bdsChange and valueChange for a JSON string); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::bds-slider — form association › form reset` (notifies listeners with the restored pair; notifies valueChange listeners with the restored pair); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › step snapping › emits a valueChange with the committed value` (user-driven valueChange).

### FM-SL-27 | Emitted payload shares its array with internal state

- **ID:** FM-SL-27
- **Category:** race-timing
- **Risk:** state — a listener that mutates `event.detail.value` (or the `valueChange` array) corrupts the slider's state.
- **Input that reveals it:** listen to `bdsChange`, push into `detail.value`, then read `getValues()`.
- **Observed current behavior:** (probed) after `setValues([50])`, pushing `999` into the event array makes internal state `[50, 999]`: `emitChange(parsed)` receives the same array stored in `internalValues`, and `bdsChange` and `valueChange` receive the same reference as each other (`:243-251`, `:350-366`). User-driven paths pass a copy (`[...this.internalValues]`).
- **Recommended contract:** event payloads are copies; mutating them never changes slider state.
- **Contract status:** confirmed
- **Why it matters:** the `setValues` and form-reset paths differ from the user path in aliasing, which is a classic inconsistent-copy bug.
- **Covered by:** none

### FM-SL-28 | `getValues()` returns a copy

- **ID:** FM-SL-28
- **Category:** race-timing
- **Risk:** state — returning the internal array would let a caller mutate it.
- **Input that reveals it:** mutate the array returned by `getValues()`.
- **Observed current behavior:** (probed) returns `[...this.internalValues]`; internal state is unchanged by mutation (`:234-236`). The JSDoc says single-handle returns `number`, but the method returns `number[]` for both.
- **Recommended contract:** always a fresh `number[]`.
- **Contract status:** confirmed
- **Why it matters:** locks the copy behavior; the JSDoc discrepancy is a separate documentation task, not tested.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — public API contract › returns a fresh array on every getValues call`; `::keeps the slider state intact when the returned array is mutated`.

### FM-SL-29 | `setValues` / form reset on a disabled slider mutate state silently

- **ID:** FM-SL-29
- **Category:** component-contract-bypass
- **Risk:** consumer/state — the value changes with no `bdsChange`, so a v-model parent diverges from the slider.
- **Input that reveals it:** `disabled`, `setValues([60])`, then `getValues()`.
- **Observed current behavior:** (probed) `internalValues` becomes `[60]`; no events; `setValues` syncs the form value explicitly (`:243-251`), form reset does not (FM-SL-34).
- **Recommended contract:** unknown (programmatic writes allowed but silent, or blocked while disabled).
- **Contract status:** pending-decision
- **Why it matters:** current emit suppression is covered, but whether the state change itself is intended is not.
- **Covered by:** `bds-slider.events.spec.ts::Should not emit bdsChange when the slider is disabled` covers only the emit suppression.

---

## D. Form-associated (FACE) behavior

### FM-SL-30 | Changing the `value` prop after mount does not update the form value

- **ID:** FM-SL-30
- **Category:** race-timing
- **Risk:** form — the slider shows the new value, but a native `<form>` submission still carries the previous one.
- **Input that reveals it:** inside a form, `el.value = '[70]'` after load; submit/`FormData`.
- **Observed current behavior:** (probed) `internalValues` becomes `[70]` but `internals.setFormValue` is not called: `onValueChange` (`:169-173`) calls `syncDOMUpdates`, which never calls `syncFormValue`. Initial registration only happens in `formAssociatedCallback` (`:195`).
- **Recommended contract:** the form value always mirrors the current internal value.
- **Contract status:** confirmed
- **Why it matters:** silent wrong-data submission, invisible to unit tests of `getValues()`.
- **Covered by:** none

### FM-SL-31 | Form value serialization and registration points

- **ID:** FM-SL-31
- **Category:** equivalence
- **Risk:** form — single and range sliders submit different shapes under one `name`.
- **Input that reveals it:** single `[10]`, range `[10,20]`, after `formAssociatedCallback`, `input`/`change`, `setValues`.
- **Observed current behavior:** `serializeFormValue` joins with `,` (`parseValues.ts:33-35`) -> `"10"` / `"10,20"`; registered in `formAssociatedCallback`, every `input`/`change` (via `handleInputEvent`), `setValues`, `emitChange` and `formStateRestoreCallback`.
- **Recommended contract:** single -> `"10"`, range -> `"10,20"`; the registered value is updated on every interaction, including before the `change` commit.
- **Contract status:** confirmed
- **Why it matters:** the consumer-visible format of the submitted data.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::bds-slider — form association › form value registration` (registers a single value as a plain number string when associated with a form; registers a range as comma separated values when associated with a form; registers the normalized value after setValues; registers both handles after setValues on a range slider); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::state restore` (registers the restored state as the form value; applies a matching, in-range state to a range slider); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › live feedback while dragging` (registers the live value as the form value on the input event; registers both handle values as the form value on a range input event; registers the committed value as the form value on the change event); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.track-click.spec.ts::bds-slider — track click` (registers the clicked value as the form value; registers both handle values as the form value); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — serializeFormValue`. The `emitChange` registration after a reset is covered by FM-SL-32.

### FM-SL-32 | Form reset restores the `value` prop and emits

- **ID:** FM-SL-32
- **Category:** equivalence
- **Risk:** form — reset must return to the initial value of the control.
- **Input that reveals it:** `setValues([90])` then `formResetCallback()`.
- **Observed current behavior:** `formResetCallback` re-resolves `this.value` (the current prop, clamped), updates state, syncs DOM and emits (`:199-204`).
- **Recommended contract:** reset returns to the clamped `value` prop and notifies listeners.
- **Contract status:** confirmed
- **Why it matters:** standard FACE reset contract.
- **Covered by:** `bds-slider.methods.spec.ts::Should reset to the initial value on formResetCallback`; `bds-slider.events.spec.ts::Should emit bdsChange on formResetCallback`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::bds-slider — form association › form reset` (restores a range slider to its initial pair; restores the value prop that was set after load; clamps the restored value into the current range; notifies listeners with the restored pair; notifies valueChange listeners with the restored pair; registers the restored value as the form value). Reset on a disabled slider is FM-SL-34 and is not tested.

### FM-SL-33 | Reset does not drive a real `<form>` reset event

- **ID:** FM-SL-33
- **Category:** race-timing
- **Risk:** form — the callbacks are invoked directly in tests, not through the form, so the association wiring is never exercised.
- **Input that reveals it:** `<form><bds-slider/></form>` then `form.reset()`.
- **Observed current behavior:** the mock `attachInternals` sets `internals.form = this.closest('form')` but does not dispatch the lifecycle callbacks; direct calls are the established test pattern.
- **Recommended contract:** n/a — test through direct callback calls as for other FACE components.
- **Contract status:** pending-decision
- **Why it matters:** documents a harness limitation so no one writes a test that cannot pass; ruling needed on whether a Storybook/QA check should cover it.
- **Covered by:** none

### FM-SL-34 | Reset on a disabled slider leaves a stale form value, and reset emits before syncing the form value

- **ID:** FM-SL-34
- **Category:** race-timing
- **Risk:** form — re-enabling a slider (or reading `FormData` in a `bdsChange` listener during reset) sees the pre-reset value.
- **Input that reveals it:** `disabled`, `setValues([60])`, `formResetCallback()`, inspect `setFormValue` calls; or read form data inside a `bdsChange` listener during reset.
- **Observed current behavior:** (probed) disabled reset updates `internalValues` to `[10]` but `setFormValue` is never called: `formResetCallback` relies on `emitChange` to sync, and `emitChange` returns early when disabled before reaching `syncFormValue` (`:199-204`, `:358-366`). When enabled, `syncFormValue` runs after the listeners.
- **Recommended contract:** the form value always mirrors `internalValues` after reset, independent of `disabled`, and before listeners run.
- **Contract status:** confirmed
- **Why it matters:** `formResetCallback` and `setValues` are inconsistent — `setValues` syncs explicitly.
- **Covered by:** none

### FM-SL-35 | `formStateRestoreCallback` stores unnormalized values

- **ID:** FM-SL-35
- **Category:** boundary
- **Risk:** visual/form — restoring `"20,70"` into a `single` slider renders two handles; restoring `"500"` stores an out-of-range value.
- **Input that reveals it:** `single` slider, `formStateRestoreCallback('20,70', 'restore')` and `('500', 'restore')`; `range` with `'20'`.
- **Observed current behavior:** (probed) `[20, 70]` with two `<input>` elements on a `single` slider; `[500]` with `max=100`. The parsed numbers bypass `resolveValues` (`:206-218`).
- **Recommended contract:** restored values go through the same arity/clamp normalization as `value` (FM-SL-02, FM-SL-03).
- **Contract status:** confirmed
- **Why it matters:** browser form restore (back/forward) is exactly when saved state may no longer match the slider's configuration.
- **Covered by:** `bds-slider.methods.spec.ts::Should restore state from a valid string via formStateRestoreCallback` and `::Should restore multi-handle state via formStateRestoreCallback` cover only matching-shape, in-range input.

### FM-SL-36 | `formStateRestoreCallback` ignores unusable state

- **ID:** FM-SL-36
- **Category:** null-empty
- **Risk:** form — a non-string, empty or non-numeric state must leave the value alone.
- **Input that reveals it:** `null` (covered), `''`, `'abc'`, `','`, `undefined`, a `FormData`.
- **Observed current behavior:** non-string returns early; strings with no parseable number return early (`:206-213`).
- **Recommended contract:** unusable state is ignored, never throws, never changes value or form value.
- **Contract status:** confirmed
- **Why it matters:** browsers may pass any state previously saved.
- **Covered by:** `bds-slider.methods.spec.ts::Should ignore formStateRestoreCallback when state is not a string` (`null`); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::bds-slider — form association › state restore` (ignores an empty string / a non-numeric string / only separators / undefined / an object / a number without changing the value, each also asserting the form value is not touched and nothing throws; does not emit change events when restoring state). Not covered: a partially valid state such as `'10,abc'`, whose handling depends on FM-SL-35.

### FM-SL-37 | Fieldset-disabled (`formDisabledCallback`) disables the slider

- **ID:** FM-SL-37
- **Category:** component-contract-bypass
- **Risk:** functional/a11y — a slider inside `<fieldset disabled>` must be unusable.
- **Input that reveals it:** `formDisabledCallback(true)` then render.
- **Observed current behavior:** (probed) the mixin writes `isDisabled`; the host gets `bds-slider--disabled`, the inputs get `disabled`, and `aria-disabled="true"` renders (`src/mixins/form-associated.mixin.ts` `formDisabledCallback`; host attribute at `bds-slider.tsx:573`).
- **Recommended contract:** the slider is disabled in all the same ways as the `disabled` prop; events are suppressed.
- **Contract status:** confirmed
- **Why it matters:** the only non-prop path to disabled.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.face.spec.ts::bds-slider — form association › fieldset disabled` (disables the host through formDisabledCallback; disables every native input through formDisabledCallback; suppresses change events while disabled by the fieldset; re-enables the slider when the fieldset is enabled again).

### FM-SL-38 | `formDisabledCallback(false)` overrides the `disabled` prop

- **ID:** FM-SL-38
- **Category:** component-contract-bypass
- **Risk:** functional — a slider with `disabled` set inside a fieldset that is later re-enabled becomes enabled.
- **Input that reveals it:** `disabled` prop `true`, then `formDisabledCallback(false)`.
- **Observed current behavior:** derived by static reading: the mixin sets `isDisabled = disabled` argument only (`form-associated.mixin.ts`), ignoring the `disabled` prop. Shared by all FACE components, not specific to the slider.
- **Recommended contract:** unknown — probably `isDisabled = disabledProp || callbackArg`; belongs to the mixin.
- **Contract status:** pending-decision
- **Why it matters:** cross-cutting; fixing it in the slider alone would diverge from other components.
- **Covered by:** none

---

## E. Runtime prop reactivity

### FM-SL-39 | Toggling `discrete` discards the user's value

- **ID:** FM-SL-39
- **Category:** race-timing
- **Risk:** functional — the slider jumps back to the original `value` prop whenever `discrete` changes.
- **Input that reveals it:** `value="[10]"`, `setValues([60])` (or a user drag), then `el.discrete = true`.
- **Observed current behavior:** (probed) `[10]`. `onConfigChange` is shared by `@Watch('type')` and `@Watch('discrete')` and always re-resolves from `this.value` (`:174-181`), which is not mutable and never reflects user changes.
- **Recommended contract:** toggling `discrete` leaves the current value unchanged.
- **Contract status:** confirmed
- **Why it matters:** a Storybook control toggle or a consumer binding hits this immediately.
- **Covered by:** none

### FM-SL-40 | Switching `type` single <-> range: which value survives

- **ID:** FM-SL-40
- **Category:** equivalence
- **Risk:** functional — the handle count changes and the value source is ambiguous.
- **Input that reveals it:** `single value="[10]"` -> `type = 'range'`; range `[20,70]` -> `single`.
- **Observed current behavior:** (probed) single -> range gives `[10, 100]` and two inputs, derived from the `value` prop, not the current internal state (`:174-181`).
- **Recommended contract:** unknown — derive from current internal values (preserving user edits) or reset to the `value` prop.
- **Contract status:** pending-decision
- **Why it matters:** companion to FM-SL-39; the answer decides the fix for both.
- **Covered by:** none (`onConfigChange` lines 176-181 uncovered)

### FM-SL-41 | `min` / `max` / `step` changes do not re-clamp or re-snap the current value

- **ID:** FM-SL-41
- **Category:** boundary
- **Risk:** form/visual — shrinking `max` leaves the internal value, tooltip and form value above the new maximum while the native input shows it clamped.
- **Input that reveals it:** `value="[80]"`, `el.max = 50`.
- **Observed current behavior:** (probed) `internalValues` stays `[80]`; `onRangeChange` only rebuilds the service and syncs the DOM (`:183-189`). The form value is not re-synced either.
- **Recommended contract:** after any range-config change the stored value is re-normalized into `[min, max]` and the form value updated.
- **Contract status:** confirmed
- **Why it matters:** violates the FM-SL-03 invariant on a runtime path.
- **Covered by:** none

### FM-SL-42 | Runtime `disabled` and `disabledHandlers` changes update the render

- **ID:** FM-SL-42
- **Category:** component-contract-bypass
- **Risk:** functional/a11y — toggling after mount must change the class, the host `aria-disabled`, and each input's `disabled`/`aria-disabled`.
- **Input that reveals it:** `el.disabled = true`, then `false`; `el.disabledHandlers = '[50]'`.
- **Observed current behavior:** (probed) `disabled` toggle updates class and `aria-disabled="true"` correctly (`:157-162`); `onDisabledHandlersChange` (`:164-166`) re-renders through the prop change.
- **Recommended contract:** both update on the next render; enabling restores emission.
- **Contract status:** confirmed
- **Why it matters:** watchers are the uncovered part of the component (`bds-slider.tsx:159-196`).
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — runtime prop changes › disabled` (applies the disabled class and aria-disabled when disabled is set after load; disables the native input when disabled is set after load; removes the disabled markup when disabled is cleared after load; stops emitting once disabled is set after load; resumes emitting once disabled is cleared after load); `::disabledHandlers` (disables the handle whose value is listed after load; re-enables a handle when its value is removed from the list).

### FM-SL-43 | Switching `tooltip` from `focus` to `never` after mount throws

- **ID:** FM-SL-43
- **Category:** null-empty
- **Risk:** functional — a Storybook control or consumer toggle throws `TypeError: Cannot set properties of null (setting 'textContent')`, aborting the update.
- **Input that reveals it:** `<bds-slider value="[10]">`, then `el.tooltip = 'never'`.
- **Observed current behavior:** (probed) the removed tooltip nodes call their `ref` with `null`, which the `el !== undefined` guard accepts, so `tooltipEls[0]` becomes `null`; `syncTooltip` only guards `=== undefined` and dereferences `null` (`:331-337`, ref at `:508-511`). `SliderDOMController.addTooltipsStates`/`removeTooltipsStates` have the same `=== undefined`-only guard (`SliderDOMController.ts:8-19`).
- **Recommended contract:** switching `tooltip` at runtime never throws and removes the tooltips cleanly; switching back restores them.
- **Contract status:** confirmed
- **Why it matters:** `tooltip` is a documented user-facing prop.
- **Covered by:** none

### FM-SL-44 | `label` set to `null` / `undefined` throws during render

- **ID:** FM-SL-44
- **Category:** null-empty
- **Risk:** functional — the component crashes when a framework passes `null`/`undefined` (or removes the attribute).
- **Input that reveals it:** `el.label = null`.
- **Observed current behavior:** (probed) `TypeError: Cannot read properties of null (reading 'trim')` from `classMap` (`:391`); `renderLabel` also calls `this.label.trim()` before its `=== undefined` check, which is therefore dead code (`:537-538`).
- **Recommended contract:** a missing label behaves like `''`: no label element, no `--label` class, no throw.
- **Contract status:** confirmed
- **Why it matters:** other string props (`name`) already use `?? ''`.
- **Covered by:** `bds-slider.basics.spec.ts::Should not render a label when label prop is empty`; `bds-slider.variants.spec.ts::Should not apply label class when label prop is empty` cover only the empty-string case.

### FM-SL-45 | Invalid `type` / `tooltip` values are not validated and `type` corrupts state

- **ID:** FM-SL-45
- **Category:** equivalence
- **Risk:** functional — `type="foo"` is treated as `single` by `resolveValues` and `applyCollision`, but as `range` by `getConnectSegment` and `handleTrackClick`.
- **Input that reveals it:** `type="foo"` then a track click; `tooltip="always"`.
- **Observed current behavior:** (probed) `type="foo"` + track click yields `[10, 50]` and two inputs on a nominally single slider. `tooltip="always"` renders `--tooltip` (truthy, not `never`) and `__tooltip--always` with neither `--tooltip-focus` nor `--tooltip-never`. The component defines `SLIDER_TYPE`/`SLIDER_TOOLTIP` const-objects but no `validatePropValue` call (`utils/helpers/validateProps.ts`, used by `bds-text-field`, `bds-flag`, `bds-radio-group`).
- **Recommended contract:** invalid enum values fall back to the documented default (`single`, `focus`) like other enum props in the library.
- **Contract status:** confirmed
- **Why it matters:** repo convention for enum props (const-object plus validation in `componentWillLoad`).
- **Covered by:** none

---

## F. Keyboard, focus and accessibility

### FM-SL-46 | The native range inputs have no accessible name

- **ID:** FM-SL-46
- **Category:** component-contract-bypass
- **Risk:** a11y (WCAG 4.1.2 / 1.3.1) — screen readers announce an unnamed slider; in range mode, two unnamed sliders.
- **Input that reveals it:** `label="Volume"`; read the inputs' accessible name.
- **Observed current behavior:** (probed) the `<bds-typography class="bds-slider__label" for="">` points at `this.el.id` (empty unless the consumer sets an id) and the host is not a labelable element; neither input has `aria-label` or `aria-labelledby` (`:537-545`, inputs `:414-444`).
- **Recommended contract:** each range input is named by `label` (and, in range mode, distinguishable, for example minimum/maximum).
- **Contract status:** confirmed
- **Why it matters:** the label is currently decorative.
- **Covered by:** none (`bds-slider.basics.spec.ts::Should render a label when label prop is provided` asserts only that the element exists)

### FM-SL-47 | `aria-describedby` dangles when `tooltip="never"`

- **ID:** FM-SL-47
- **Category:** null-empty
- **Risk:** a11y — the input references an id that does not exist in the document.
- **Input that reveals it:** `tooltip="never"`.
- **Observed current behavior:** (probed) the input keeps `aria-describedby="bds-slider-tooltip-0"` while no tooltip is rendered (`:431`, `renderTooltip` returns `null` at `:495`).
- **Recommended contract:** `aria-describedby` is omitted when there is no tooltip element.
- **Contract status:** confirmed
- **Why it matters:** invalid ARIA reference.
- **Covered by:** none

### FM-SL-48 | Tooltip ids are not unique across instances

- **ID:** FM-SL-48
- **Category:** equivalence
- **Risk:** a11y — two sliders on one page both use `bds-slider-tooltip-0`, so `aria-describedby` resolves to the first tooltip in the document.
- **Input that reveals it:** two `<bds-slider>` in the same document.
- **Observed current behavior:** ids are `bds-slider-tooltip-${handleIndex}` (`:431`, `:498`). Existing tests encode this exact scheme.
- **Recommended contract:** unknown — a per-instance unique id.
- **Contract status:** pending-decision
- **Why it matters:** CONFLICT with existing tests, surfaced per the audit rule and not edited: `bds-slider.a11y.spec.ts::Should set aria-describedby on the input linking to its tooltip id` (expects `'bds-slider-tooltip-0'`), `::Should set matching id on each tooltip element` and `::Should set aria-describedby on each range input linking to its tooltip id` assert the non-unique scheme. Resolving requires ruling on the new id format, after which those tests change in their own step.
- **Covered by:** none for uniqueness (see conflict above)

### FM-SL-49 | `pointerup` blurs the handle

- **ID:** FM-SL-49
- **Category:** component-contract-bypass
- **Risk:** a11y — after a mouse or touch drag, keyboard focus is dropped to `<body>`, so the user cannot continue with arrow keys.
- **Input that reveals it:** `pointerup` on a handle.
- **Observed current behavior:** `onHandleInactive` calls `input.blur()` (`:310-314`) and passes the `<input>` (not the tooltip) to `removeTooltipsStates`, which only works because the blur then fires `onHandleBlur`. It dereferences `this.inputEls[handleIndex]` without a guard.
- **Recommended contract:** unknown — keep the tooltip's visible state tied to focus without removing the user's focus, or document blur-on-release as intended.
- **Contract status:** pending-decision
- **Why it matters:** looks designed for tooltip dismissal, but it breaks the WCAG focus-retention expectation.
- **Covered by:** none

### FM-SL-50 | Keyboard changes follow the same snap/collision/emit path as pointer changes

- **ID:** FM-SL-50
- **Category:** component-contract-bypass
- **Risk:** a11y/functional — arrow keys, Home/End and PageUp/PageDown change the native value and dispatch `input` + `change`; they must obey `step`, collision and per-handle disabling.
- **Input that reveals it:** mock-doc cannot press keys; dispatch `input` then `change` on a handle at the collision boundary and at `min`/`max`.
- **Observed current behavior:** the component adds no `keydown` handling; everything goes through `handleInputEvent`/`handleChangeEvent` (`:278-303`). Native behavior itself is not testable in mock-doc.
- **Recommended contract:** each committed change emits one snapped, collision-respecting `bdsChange`; focus and blur toggle the tooltip visibility classes.
- **Contract status:** confirmed
- **Why it matters:** keyboard operability is a core accessibility requirement; verify native key behavior manually.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › step snapping` (snaps a committed value to the nearest step; emits a single bdsChange carrying the snapped value; accepts the min boundary as a committed value; accepts the max boundary as a committed value; pins a committed value above max to max; pins a committed value below min to min) and `::range collision` (emits the collision-corrected pair on commit). Native key behavior (arrows, Home/End, PageUp/PageDown) is not testable in mock-doc and must be verified manually; per-handle disabling on keyboard commits is not asserted because of FM-SL-22.

### FM-SL-51 | Tooltip visibility classes follow focus and blur

- **ID:** FM-SL-51
- **Category:** component-contract-bypass
- **Risk:** visual/a11y — `--visible`/`--active` on the tooltip must be added on focus and removed on blur, and a missing tooltip (`tooltip="never"`) must not throw.
- **Input that reveals it:** `focus`/`blur` on a handle with `tooltip="focus"` and `tooltip="never"`.
- **Observed current behavior:** `addTooltipsStates`/`removeTooltipsStates` toggle `bds-slider__tooltip--visible` and `--active` (`SliderDOMController.ts:8-19`); the `tooltip="never"` case throws after a runtime switch (FM-SL-43).
- **Recommended contract:** classes added on focus, removed on blur; no throw when tooltips are absent.
- **Contract status:** confirmed
- **Why it matters:** the only visibility mechanism for `tooltip="focus"` (the CSS is the other half, not Jest-assertable).
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › tooltip visibility on focus` (marks the tooltip visible and active when its handle gains focus; clears the visible and active state when the handle loses focus; leaves the tooltip hidden before any focus; shows only the tooltip of the focused handle on a range slider); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderDOMController tooltip states` (adds / removes the classes; does not throw when adding or removing states on a missing tooltip; keeps unrelated classes). Not covered: the runtime switch to `tooltip="never"` (FM-SL-43).

### FM-SL-52 | Refs are cleared in `disconnectedCallback` but not restored on reconnect

- **ID:** FM-SL-52
- **Category:** race-timing
- **Risk:** functional — a slider moved in the DOM (reorder, portal) loses its input/tooltip refs until the next render, so a `pointerup` right after the move can throw.
- **Input that reveals it:** detach and re-attach the element, then `pointerup` on a handle.
- **Observed current behavior:** derived by static reading (`:562-565`, `onHandleInactive` `:310-314`); not reproduced — a DOM move in mock-doc did not throw.
- **Recommended contract:** unknown (low priority).
- **Contract status:** pending-decision
- **Why it matters:** unverified; kept so the next audit pass can confirm or retire it.
- **Covered by:** none

---

## G. Render output and helpers

### FM-SL-53 | Connect bar geometry

- **ID:** FM-SL-53
- **Category:** boundary
- **Risk:** visual — the filled segment must start at `0` for `single` and span between the handles for `range`.
- **Input that reveals it:** `single [25]`, `range [20,60]`, `min=50 max=150`; `value = min`, `value = max`.
- **Observed current behavior:** `getConnectSegment` returns `left: 0, width: toPercent(v0)` for `single` and `left: toPercent(v0), width: toPercent(v1 - v0 + min)` for `range` (`SliderService.ts:59-73`); applied through `SliderDOMController.moveConnect` (`:44-47`).
- **Recommended contract:** `single` -> `left 0%`, `width` = percent of value; `range` -> `left` = percent of v0, `width` = percent of (v1 - v0), including a non-zero `min`.
- **Contract status:** confirmed
- **Why it matters:** `updateProgress` runs on every render but its output is never asserted; the `+ min` term is a subtle correctness point.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderService.getConnectSegment` (single: fills from the start up to the value percent; measures the fill relative to min; no fill at min; full fill at max; no fill without values. Range: spans between the two handles; spans between the two handles when min is not zero; zero width when both handles coincide; extends to max when it has no values or a single value; full track from min to max); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderDOMController positioning and sync › positions the connect element with percentage left and width`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › live feedback while dragging` (moves the connect bar on the input event; spans the connect bar between both handles on a range slider).

### FM-SL-54 | `showLimits` renders the current `min` and `max`

- **ID:** FM-SL-54
- **Category:** equivalence
- **Risk:** visual — the limits text must show the configured range and track runtime changes.
- **Input that reveals it:** `show-limits min=10 max=120`; change `max` at runtime.
- **Observed current behavior:** `renderMinMax` renders `this.min` and `this.max` in two `bds-typography` helpers (`:446-454`).
- **Recommended contract:** two limit nodes with the `min` and `max` text, in that order.
- **Contract status:** confirmed
- **Why it matters:** the existing tests check only presence of the container.
- **Covered by:** `bds-slider.basics.spec.ts::Should render limits when show-limits is set`; `::Should not render limits when show-limits is false`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — show-limits rendering` (renders the min and max text in that order; updates the max text when max changes after load; updates the min text when min changes after load).

### FM-SL-55 | Tooltip text and position stay in sync with the handle

- **ID:** FM-SL-55
- **Category:** equivalence
- **Risk:** visual — the tooltip must show the current value and sit on the handle.
- **Input that reveals it:** `input` event with a new value; `setValues`; range slider.
- **Observed current behavior:** text is set by `syncTooltip` through `textContent`; position `left` is a percentage on first render and a pixel value afterwards (`getThumbPosition` uses `getBoundingClientRect` and `getComputedStyle`, both unavailable in mock-doc).
- **Recommended contract:** text equals `String(value)` for each handle after any change; position is not Jest-assertable (route to Storybook/manual).
- **Contract status:** confirmed
- **Why it matters:** the tooltip is also the `aria-describedby` target.
- **Covered by:** `bds-slider.methods.spec.ts::Should update the tooltip text content after setValues()`; `bds-slider.variants.spec.ts::Should display the initial value as the tooltip text content`; `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.interaction.spec.ts::bds-slider — handle interaction › live feedback while dragging` (updates the tooltip text on the input event; updates only the tooltip of the dragged handle on a range slider); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.reactivity.spec.ts::bds-slider — tooltip text` (shows each handle value in its own tooltip for a range slider; updates each tooltip after setValues on a range slider); `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.track-click.spec.ts::bds-slider — track click › single slider › reflects the clicked value on the input and the tooltip`. Tooltip pixel position is not Jest-assertable.

### FM-SL-56 | Service math helpers

- **ID:** FM-SL-56
- **Category:** boundary
- **Risk:** visual — `toPercent`, `getThumbCSSPosition` and `snapToStep` feed every rendered position.
- **Input that reveals it:** `toPercent(min)`, `toPercent(max)`, `toPercent(v)` when `min == max`; `getThumbCSSPosition(value, trackWidth, thumbSize)` at `0`, `50`, `100`; `snapToStep` at exact steps, halfway points, below `min`, above `max`.
- **Observed current behavior:** `toPercent` guards `range === 0` (`SliderService.ts:48-52`); `getThumbCSSPosition` is `percent * (trackWidth - thumbSize) + thumbSize / 2` (`:98-103`); `snapToStep` rounds half up and clamps.
- **Recommended contract:** the formulas above; the thumb centre never leaves `[thumbSize/2, trackWidth - thumbSize/2]`.
- **Contract status:** confirmed
- **Why it matters:** pure functions, cheap to pin directly.
- **Covered by:** `packages/boreal-web-components/src/components/forms/bds-slider/__test__/bds-slider.helpers.spec.ts::bds-slider — SliderService.toPercent` (maps min to 0; maps max to 100; maps an intermediate value linearly; returns 0 instead of dividing by zero when min equals max); `::SliderService.getThumbCSSPosition` (centres the thumb half a thumb size from the start at min; places the thumb in the middle of the usable width at the midpoint; centres the thumb half a thumb size from the end at max); `::SliderService.snapToStep` (keeps a value that already sits on a step; rounds a halfway value up to the next step; rounds a value just below the halfway point down; anchors the steps at min when min is not a multiple of step; never returns a value below min).

---

## Observations not rated as failure modes

- `Host aria-disabled` is applied to a generic element (no role) and the native range inputs carry redundant `aria-valuemin/max/now`; harmless, not asserted beyond what the a11y spec already covers.
- No `required` prop or constraint validation: `setValidity` is never called. Appears intentional (a slider always has a value); not tracked.
- No render-time memoization exists in this component, so the caching-test rule in `testing-knowledge` does not apply.
- `SliderService` builds a new instance on every `buildAdapter()` and the `value`/`disabled`/`name`/`discrete` options it receives are never read by its methods (dead option fields).

## Reconciliation against the existing suite

- Original suite: 70 tests across 5 files, all passing; they concentrated on render output, ARIA attribute presence and `setValues` / `getValues`, and none exercised a pointer interaction, a collision, a runtime prop change, or `internals.setFormValue`.
- Added after the first audit (all passing against current source): `bds-slider.helpers.spec.ts` (service/helpers/DOM-controller unit tests), `bds-slider.track-click.spec.ts`, `bds-slider.interaction.spec.ts`, `bds-slider.face.spec.ts`, `bds-slider.reactivity.spec.ts` (175 tests). Suite total: 245 tests across 10 files.
- Scoped coverage after the additions (`src/components/forms/bds-slider`, `--collectCoverageFrom` over `**/*.{ts,tsx}`): **statements 93.26% (263/282), branches 82.35% (112/136), functions 93.75%, lines 95.27%**; the Phase 1 gate (>= 80% on all four) is met. Remaining uncovered lines: `bds-slider.tsx` 177-180 (`onConfigChange`, FM-SL-39/40), 311-313 (`onHandleInactive`, FM-SL-49), 354 (`updateValues` emit branch, unreachable: every caller passes `shouldEmit=false`), 436 (`onPointerUp` binding, FM-SL-49), 506 (tooltip `stopPropagation`, FM-SL-25), 563-564 (`disconnectedCallback`, FM-SL-52); `SliderService.ts` 34-39 (`?? options.max/min` fallbacks behind the `length < 2` guard, unreachable); `parseValues.ts` 25 (non-JSON string fallback, FM-SL-01) and 42-48 (`?? Number(min/max)` on a non-empty array, unreachable).
- One existing assertion encodes behavior flagged by this catalog: the a11y spec's tooltip-id tests (FM-SL-48, `pending-decision`); not edited.
- One existing test is misnamed rather than conflicting: `bds-slider.events.spec.ts::Should emit bdsChange when input event fires on the handle` dispatches a `change` event (FM-SL-16); not edited.
- Rows with a `confirmed` contract that are NOT tested because current source violates the contract (a test would fail today and must wait for the fix): FM-SL-01, 08 (would hang), 11 (probed: `discrete min=0 max=2.1 step=0.3` renders a pip at 100%), 14, 20, 27, 30, 34, 35, 39, 41, 43, 44, 45, 46, 47. Once each is fixed, add its test and record it in the row's `Covered by`.
- Not covered on purpose: all `pending-decision` rows (FM-SL-04..07, 10, 12, 15, 16, 18, 19, 21..25, 29, 33, 38, 40, 48, 49, 52).

## Top uncovered failure modes (priority order)

1. FM-SL-20: `handleTrackClick` on a zero-width track stores `NaN` (confirmed defect; the rest of `handleTrackClick` is now covered).
2. FM-SL-14: collision correction can push a value outside `[min, max]` (confirmed defect; the nominal collision behavior is now covered).
3. FM-SL-43 / FM-SL-44: runtime `tooltip` -> `never` and `label = null` throw (bugs, probed).
4. FM-SL-30 / FM-SL-34 / FM-SL-35: form value is stale after a `value` change and after a disabled reset; restore is not normalized.
5. FM-SL-39 / FM-SL-41: `discrete` toggle resets the user's value; `max` shrink leaves the value above `max`.
6. FM-SL-46 / FM-SL-47: the native inputs have no accessible name; `aria-describedby` dangles for `tooltip="never"`.
7. FM-SL-27: emitted payload aliases internal state on the `setValues` / reset paths.
8. FM-SL-01 / FM-SL-08 / FM-SL-11: `disabled-handlers=""` disables the `0` handle; `discrete step=0` hangs; fractional `discrete` ranges render a pip on top of `max`.
9. FM-SL-45: invalid `type` / `tooltip` values are not validated.
