# Code Review — bds-slider

**Branch:** `test/test-doc-slider-component`
**Commit:** `a1d46375`
**Date:** 2026-05-27
**Files reviewed:** `packages/boreal-web-components/src/components/forms/bds-slider/**`

---

## Summary

All-new slider component built on noUiSlider. Introduces the main component (`bds-slider.tsx`), two helper classes (`SliderAdapter`, `SliderDOMController`), utility functions, full type definitions, and a six-file unit test suite.

---

## Findings

### 🔴 Critical — Bugs / Memory Leaks

**1. Click listener accumulates on every slider rebuild (`bds-slider.tsx`)**

`setListeners()` is called by `buildSlider()`, which is called by `rebuildSlider()`. `rebuildSlider()` calls `destroySlider()` first, but `destroySlider()` only tears down the noUiSlider instance — it never removes the `click` listener from `this.el`. Each prop change that triggers `rebuildSlider()` (`discrete`, `min`, `max`, `step`, `disabledHandlers`) stacks another click listener.

**Status: Fixed.** Click handler stored in `clickHandler` field; removed in `destroySlider()`.

---

**2. `blockDisabledHandleInteraction` adds duplicate event listeners (`SliderDOMController.ts`)**

`applyDisabledHandlers()` calls `blockDisabledHandleInteraction(handle)` every time it runs, adding `pointerdown`, `mousedown`, and `touchstart` capture listeners to the same handle element — without ever removing them.

**Status: Fixed.** `data-blocked` sentinel attribute prevents re-attaching listeners to the same handle element. Enable path clears the sentinel via `delete handle.dataset['blocked']`.

---

**3. Tooltip IDs collide when multiple sliders are on the same page (`SliderDOMController.ts`)**

`id="bds-slider-tooltip-${i}"` uses only the handle index. Two `<bds-slider>` components on a page produce duplicate `bds-slider-tooltip-0` IDs, breaking `aria-describedby` association.

**Status: Fixed.** A module-level `_sliderUidCounter` generates a per-instance `uid` in `componentWillLoad`. The `SliderDOMController` now accepts `sliderUid` as a constructor parameter and uses it to namespace tooltip IDs: `${sliderUid}-tooltip-${i}`.

---

### 🟠 High — Correctness Risks

**4. Watchers fire before adapter is mounted (`bds-slider.tsx`)**

`onDisabledChange` and `onValueChange` both call into `this.adapter.getInstance()` before the adapter is initialized. If a parent component sets these props before the custom element connects to the DOM (before `componentDidLoad`), the adapter is uninitialized and `getInstance()` throws.

**Status: Fixed.** Both watchers return early with `if (this.sliderInstance === null) return;`.

---

**5. `setInternalValues` uses wrong fallback (`bds-slider.tsx`)**

```ts
private setInternalValues(raw: SliderRawValue): void {
  this.internalValues = parseValues(raw); // ← fallback defaults to [0]
}
```

Every other call-site passes `this.minFallback`. A slider with `min=20` and an invalid value would silently fall back to `0`, which is out of range.

**Status: Fixed.** `parseValues(raw, this.minFallback)`.

---

**6. Vue `componentModels` registration**

Per project conventions, every form component with a `value` prop must be registered in `vue-output-target.ts`.

**Status: N/A — already registered.** `bds-slider` was already present in `componentModels`.

---

### 🟡 Medium — Accessibility & API Consistency

**7. `buildTooltips` sets `disabled="true"` on a `<div>` (`SliderDOMController.ts`)**

`handle.setAttribute('disabled', 'true')` on a `<div>` is a non-standard HTML attribute. The correct attribute for communicating disabled state to AT is `aria-disabled="true"`.

**Status: Fixed.** Changed to `aria-disabled="true"`.

---

**8. `emitChange` guard uses unusual negation (`bds-slider.tsx`)**

`if (this.isDisabled !== false) return;` is logically equivalent to `if (this.isDisabled) return;` but unexpected for readers.

**Status: Fixed.** Changed to `if (this.isDisabled) return;`.

---

**9. `mountServices` calls `getInstance()` twice redundantly (`bds-slider.tsx`)**

`this.sliderInstance = this.adapter.getInstance()` is stored, then `const sliderInstance = this.adapter.getInstance()` is called again for the `SliderDOMController` constructor.

**Status: Fixed.** `this.sliderInstance` passed directly to the `SliderDOMController` constructor.

---

**10. `formResetCallback` bypasses adapter (`bds-slider.tsx`)**

`this.sliderInstance?.set(...)` called directly instead of through the adapter, inconsistent with the rest of the component.

**Status: Fixed.** `if (this.sliderInstance !== null) this.adapter.getInstance().set(initial.map(String))`.

---

**11. `margin === step` in noUiSlider config (`SliderAdapter.ts`)**

`margin: Number(this.options.step)` enforces a minimum distance between handles equal to the step size. For range sliders this means handles can never be adjacent (even one step apart). This should be intentional and documented, or exposed as a `minRange` prop.

**Status: Flagged — team decision required.** Not changed; the implications need product sign-off before exposing as a prop.

---

### 🔵 Low — Style & Convention

**12. JSDoc typo (`bds-slider.tsx`)**

`"Defa ults to "focus""` — stray space.

**Status: Fixed.**

---

**13. `parserRawValue` method name has a typo (`bds-slider.tsx`)**

Should be `parseRawValue`. Private method only, no public API impact.

**Status: Fixed.** Renamed across all call-sites.

---

**14. Dead null-coalescing in `componentWillLoad` (`bds-slider.tsx`)**

`parseValues(this.value ?? [this.min], this.minFallback)` — `this.value` has a default of `[0]` and is typed `string | number[]`, so `??` never evaluates.

**Status: Fixed.** Simplified to `parseValues(this.value, this.minFallback)`.

---

**15. `sliderEl` type conflicts with `!` assertion (`bds-slider.tsx`)**

`private sliderEl!: HTMLDivElement | undefined;` — `!` contradicts `| undefined`.

**Status: Fixed.** `!` removed.

---

## Pre-existing Issue (not introduced by this PR)

The `bds-slider` test suite fails with `"Cannot use import statement outside a module"` because `noUiSlider` is an ESM-only package excluded from Jest's transform pipeline. Fix: add `nouislider` to `transformIgnorePatterns` allowlist in the project Jest config.

---

## Verification Steps

1. `pnpm test --filter @telesign/boreal-web-components -- --testPathPattern=bds-slider` — all spec files pass once the ESM transform issue is resolved.
2. Manual: place two `<bds-slider>` components on a Storybook page, inspect DOM — confirm tooltip IDs are unique (`bds-slider-1-tooltip-0` vs `bds-slider-2-tooltip-0`).
3. Manual: use a slider with `discrete`, then change `min` prop — confirm click event fires only once per click (no stacking).
4. Manual: use a slider with `disabledHandlers="[20]"`, trigger several `disabledHandlers` prop changes in devtools — confirm no event listener stacking via the Elements panel.
