# bds-date-picker: React wrapper skips initial min/max invalid state (FACE validity race) — RESOLVED

**Fixed** by commit `fffd6e62` ("fix(web-components): EOA-17138 correct initial min/max FACE-validity
race in framework wrappers") — adds a second `this.updateValidity()` call at the end of
`componentDidLoad()` (after Stencil's initial prop-settle), leaving `formAssociatedCallback()` and
the existing `isInvalid`/`errorMessage` UI-gating design untouched. Re-verified 2026-08-28 (Task 15a)
across all three surfaces (web components, React, Vue):
- `checkValidity()` returns `false` immediately on mount in all three, even before any submit attempt.
- Real trusted-click form submit is blocked in all three, with `errorMessage="Date is not allowed."`
  surfacing on the slotted field only after that submit attempt (matching the existing Task 11/13 design).
- Scenarios 1/2 regression-checked in React only (disabled-cell rendering, nav guard) — both still pass.

**Side-finding worth keeping in mind for future QA of this component:** calling `checkValidity()`
directly (e.g. via `await dp.checkValidity()` in a script/eval) is itself a genuine validation attempt
per the `ElementInternals` spec — it fires a native `invalid` event synchronously, which
`bds-date-picker`'s own `@Listen('invalid')` handler catches and uses to flip `isInvalid`/show the
error UI. So a raw `checkValidity()` call does NOT leave the UI untouched — if you need to observe
"validity computed correctly but UI still hidden" as two separate facts, check the return value
first via a *fresh, unreloaded* page state, then reload before checking anything else; don't chain a
UI-state check after a `checkValidity()` eval call on the same page instance.

## Original bug report (for context; no longer current behavior)

Found during EOA-17138 Task 15 (React/Vue parity check, Phase 3 min/max).

## Symptom
Loading `<bds-date-picker min="2026-08-10" value="2026-08-05">` through `@telesign/boreal-react`
does **not** mark the field invalid or block native form submission, even though the identical
prop combination correctly blocks submission and shows `errorMessage="Date is not allowed."`
in raw web components (`src/index.html`) and in `@telesign/boreal-vue`.

Confirmed via `dp.checkValidity()` (awaited): returns `true` in React on initial load, `false` in
web components and Vue for the exact same `min`/`value` pair.

## Root cause (traced, not yet fixed)
`bds-date-picker.tsx`'s `formAssociatedCallback()` computes validity once via `updateValidity()`
at whatever `min`/`value` values are readable at that moment. `@Watch('min')`/`@Watch('max')`/
`@Watch('value')` exist and correctly recompute validity — confirmed by forcing a real prop
change post-mount (`dp.min = 'x'; dp.min = original;`) which flips `checkValidity()` to `false`
as expected. But Stencil's `@Watch` decorators do not fire for a prop's very first ("initial")
assignment — only for changes after the component has already mounted with some value. If
React's custom-element property-setting order/timing means `formAssociatedCallback` fires before
both `min` and `value` have their final values, and neither prop is ever reassigned afterward
(both are static/initial-only JSX props in this repro), no `@Watch` ever fires to correct the
stale-valid snapshot — the component is stuck reporting valid indefinitely.

Vue was NOT observed to reproduce this in the same test (its `checkValidity()` was correctly
`false` on load) — likely incidental (Vue's wrapper happens to set/settle props in an order or
timing that avoids the race), not a structural difference that should be relied on.

## Scenarios affected
Only the "stale out-of-range initial `value`" scenario (Task 11 Scenario 3 / Task 15 Scenario 3).
Scenarios 1 (disabled cell rendering) and 2 (nav guard) are unaffected — those are computed fresh
on every render via getters (`minDate`/`maxDate`/`navGuard`), not gated behind `@Watch`-triggered
`this.isInvalid` state.

## Not fixed here
Reported to the plan owner as a new task per `qa-subagent`'s "no inline patches" policy. Likely
fix directions for whoever picks this up: don't rely solely on `formAssociatedCallback` for the
initial validity snapshot — also recompute in `componentDidLoad` (after Stencil has settled all
initial `@Prop`s) via a `requestAnimationFrame`/microtask defer, matching the
`keyboard-triggered-focus-move-double-activation.md` team-memory pattern of deferring past a
synchronous same-tick race.
