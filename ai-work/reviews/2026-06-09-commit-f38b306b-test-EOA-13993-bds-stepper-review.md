# Code Review — bds-stepper

**Branch:** `test/EOA-13993-test-doc-step`
**Commit:** `f38b306b`
**Date:** 2026-06-09
**Reviewer:** Claude (automated)
**Effort:** medium
**Target:** `packages/boreal-web-components/src/components/navigation/bds-stepper/bds-stepper.tsx`

---

## Summary

6 findings across 2 correctness bugs, 1 test gap, 1 documentation mismatch, and 2 cleanup items. The two correctness bugs share a common root: `internalSteps` and `originalStatus` are mutated by different code paths without a single source of truth enforcing consistency.

---

## Findings

### 🔴 Bug — `setActive()` leaves previous step as ACTIVE

**File:** `bds-stepper.tsx` · **Line:** 174

`setActive()` mutates `this.activeStep` before the `internalSteps.map()`, so the condition at line 183 (`currentStepNumber === this.activeStep`) now matches the **new** target step — not the old one. The previously-active step is never reset and stays `ACTIVE` in `internalSteps`.

**Failure scenario:** Step 1 is active (`internalSteps[0].status === ACTIVE`). Call `setActive(3)`. Line 174 sets `this.activeStep = 3`. Inside the map, step 1 matches neither condition (both reference `3`) and falls through unchanged. `resolveStepStatus` for step 1 returns `step.status = ACTIVE`. Both step 1 and step 3 render as active simultaneously.

**Fix:** Capture `const previousIndex = this.activeStep - 1` before mutating `this.activeStep`, then use that local variable inside the map to reset the old step — the same pattern `handleStepClick` uses correctly.

---

### 🔴 Bug — `setError()` state is silently lost when the `steps` prop changes

**File:** `bds-stepper.tsx` · **Line:** 224

`setError()` writes `originalStatus.set(stepNumber, COMPLETED_ERROR)` (line 160). When the parent later updates the `steps` prop, `processSteps()` calls `this.originalStatus.clear()` (line 224) then re-populates from the incoming prop. If the new prop doesn't include `COMPLETED_ERROR` for that step, the error is gone.

**Failure scenario:** Call `setError(3)` — the step shows an error indicator. Parent updates `steps` with step 3 as `pending`. `onStepsChange` → `processSteps` → `originalStatus.clear()` → `originalStatus.set(3, PENDING)`. `resolveStepStatus` for active step 3 now returns `ACTIVE` instead of `ERROR`. The error indicator disappears without any user action.

**Fix:** In `processSteps`, before clearing `originalStatus`, carry forward any `COMPLETED_ERROR` entries for steps that are not explicitly overridden by the incoming prop.

---

### 🟡 Test gap — `setActive()` has zero test coverage

**File:** `bds-stepper.methods.spec.ts` · **Line:** 1

No test in any spec file calls `root.setActive()`. The stale-ACTIVE regression above has no coverage and would pass the entire suite.

**Missing test:** Call `setActive(3)` while step 1 is active, then assert that step 1's status is no longer `ACTIVE` and step 3's status is `ACTIVE`. Also test that `setActive` on a disabled step is a no-op.

---

### 🟡 Doc mismatch — JSDoc says `"linear"` but default is `NO_LINEAR`

**File:** `bds-stepper.tsx` · **Line:** 41

```ts
/** Navigation type of the stepper. Accepts `STEPPER_NAVIGATION` values. Defaults to `"linear"`. */
@Prop({ reflect: true }) readonly navigation: StepperNavigation = STEPPER_NAVIGATION.NO_LINEAR;
```

The comment claims the default is `"linear"` but the prop defaults to `STEPPER_NAVIGATION.NO_LINEAR` (`'no-linear'`). LINEAR is forward-only; NO_LINEAR allows navigating back to any completed step — meaningfully different behaviour.

**Fix:** Change the comment to `Defaults to "no-linear"`.

---

### 🔵 Cleanup — `_wasCompleted` is a dead field in `BdsStepperItem`

**File:** `types/IStepper.ts` · **Line:** 21

`_wasCompleted?: boolean` is declared in the interface but has zero references anywhere in the codebase. Any consumer who populates it expecting persistence behaviour gets a silent no-op.

**Fix:** Remove the field from the interface.

---

### 🔵 Cleanup — Dual resize handlers do redundant work

**File:** `bds-stepper.tsx` · **Line:** 298 and 466

Both `ResizeObserver.observe(this.el)` (line 304) and `window.addEventListener('resize', this.handleWindowResize)` (line 466) independently schedule `requestAnimationFrame(() => updateResponsiveOrientation())`. Every window resize fires the update twice. `ResizeObserver` already covers element-level size changes.

**Fix:** Remove `handleWindowResize` and the `window.addEventListener` / `removeEventListener` calls. The `ResizeObserver` path is sufficient and more precise.

---

## Findings Summary

| # | Severity | Location | Description |
|---|----------|----------|-------------|
| 1 | 🔴 Bug | `bds-stepper.tsx:174` | `setActive` previous step stays ACTIVE in internalSteps |
| 2 | 🔴 Bug | `bds-stepper.tsx:224` | `setError` state wiped when steps prop changes |
| 3 | 🟡 Gap | `bds-stepper.methods.spec.ts` | No test coverage for `setActive()` |
| 4 | 🟡 Doc | `bds-stepper.tsx:41` | JSDoc default "linear" doesn't match actual NO_LINEAR |
| 5 | 🔵 Cleanup | `types/IStepper.ts:21` | `_wasCompleted` unused dead field |
| 6 | 🔵 Cleanup | `bds-stepper.tsx:298,466` | Dual resize handlers fire updateResponsiveOrientation twice |
