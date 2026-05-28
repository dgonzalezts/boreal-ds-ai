# bds-slider: Native UI vs noUISlider

**Date:** 2026-05-27
**Branch:** `test/test-doc-slider-component`
**Trigger:** Code review of the `bds-slider` PR raised the question of whether noUISlider is justified for the design requirements.

---

## Context

The current `bds-slider` implementation wraps [noUISlider](https://refreshless.com/nouislider/) behind two abstraction layers (`SliderAdapter`, `SliderDOMController`). The library handles drag interaction, step snapping, keyboard navigation, pip/tick rendering, and multi-handle collision prevention.

The question: can the same feature set be built with native browser primitives, eliminating the dependency?

---

## Figma Design Analysis

**File:** `-BOR- DSG COMPONENTS → FORMS`, node `79:63907`

The design specifies the following Figma properties, which map directly to component features:

| Property | Value | Implementation impact |
|---|---|---|
| Show Header | true | Label + optional tooltip icon |
| Active Partial | true | Track fill from 0 → handle position |
| Show Discrete | true | Tick/segment dividers on the track |
| Show Percent | true | Tooltip above active handle |
| **Show Range** | **true** | **Two handles — the decisive feature** |
| Select State | Default / Disabled | `isDisabled` CSS modifier |

**Visual structure:**
- Track: 4px height, `--ui(components)/base-light` background, `border-radius: 4px`
- Fill: `--ui(components)/primary` color, positioned as a `%`-based segment
- Handle: 16px × 16px circle with drop shadow
- Tooltip: white card, `box-shadow/xs`, `border-radius/xs`, 12px text
- Discrete dividers: 2px wide `<span>` elements at step positions inside the track
- Footer: min/max value labels at track ends
- Header: `<bds-typography variant="label">`

None of the visual structure requires noUISlider. The decisive question is the **range (two-handle) mode**.

---

## Reference Implementations

### BEEQ (`bq-slider.tsx` — Stencil + Shadow DOM)

BEEQ solves the range slider entirely with **two stacked native `<input type="range">` elements**. No third-party library.

**Core technique:**

```tsx
// Both inputs are absolutely positioned on top of each other.
// pointer-events: none on both; z-index decides which one intercepts clicks.
<input
  type="range"
  class="absolute start-0 pointer-events-none"
  style={{ zIndex: zIndexValue('min') }}
  onInput={e => handleInputChange('min', e)}
/>
<input
  type="range"
  class="absolute start-0 pointer-events-none"
  style={{ zIndex: zIndexValue('max') }}
  onInput={e => handleInputChange('max', e)}
/>
```

**Collision prevention — one line of math:**

```ts
// Min handle: cannot exceed maxValue - gap
this.minValue = Math.min(value, this.maxValue - this.gap);
// Max handle: cannot go below minValue + gap
this.maxValue = Math.max(value, this.minValue + this.gap);
```

**Fill segment — pure CSS %:**

```ts
private updateProgressTrack = () => {
  const left  = this.isRangeType ? this.calculatePercent(this.minValue) : 0;
  const width = this.calculatePercent(this.maxValue - this.minValue + this.min);
  this.progressElem.style.insetInlineStart = `${left}%`;
  this.progressElem.style.inlineSize = `${width}%`;
};
```

**What the browser provides for free:** drag (mouse + touch + pen), step snapping, keyboard arrow navigation, ARIA `aria-valuenow/min/max`, and native form reset.

BEEQ uses Shadow DOM, so it keeps `formAssociated: true` + `internals.setFormValue()` for form participation. The native inputs are used only for interaction — they have no `name` attribute.

---

### Ignite UI (`range-slider.ts` + `slider-base.ts` — Lit + Pointer Events API)

Ignite UI uses custom `<div role="slider">` thumbs wired to the **Pointer Capture API** — the modern standard for drag that tracks the pointer even when it leaves the element.

**Drag calculation:**

```ts
private calculateTrackUpdate(mouseX: number): number {
  const { width, left } = this.activeThumb.getBoundingClientRect();
  const { width: trackWidth } = this.base.getBoundingClientRect();
  const thumbX = left + width / 2;
  const scale = trackWidth / this.distance;           // px per value unit
  const change = mouseX - thumbX;
  return Math.round(change / (scale * this.step)) * this.step; // step-snapped
}

private pointerDown(event: PointerEvent) {
  this.setPointerCapture(event.pointerId); // captures all subsequent move events
  this.pointerCaptured = true;
  this.updateSlider(event.clientX);
}
```

**Closest handle detection for range:**

```ts
protected override closestHandle(event: PointerEvent): HTMLElement {
  const fromOffset = this.thumbFrom.offsetLeft + this.thumbFrom.offsetWidth / 2;
  const toOffset   = this.thumbTo.offsetLeft   + this.thumbTo.offsetWidth   / 2;
  const xPointer   = event.clientX - this.getBoundingClientRect().left;
  const match      = this.closestTo(xPointer, [fromOffset, toOffset]);
  return match === fromOffset ? this.thumbFrom : this.thumbTo;
}
```

**Handle crossing / collision:**

```ts
protected override updateValue(increment: number) {
  let [lower, upper] = [this.lower, this.upper];
  if (this.activeThumb === this.thumbFrom) lower += increment;
  else upper += increment;

  if (lower >= upper) {
    [this.lower, this.upper] = [upper, lower]; // swap values
    this.toggleActiveThumb();                  // move focus to crossed handle
  } else {
    [this.lower, this.upper] = [lower, upper];
  }
}
```

Keyboard is wired via a keybindings controller: `ArrowLeft/Right/Up/Down → ±step`, `Home/End → min/max`, `PageUp/Down → ±10%`.

---

## What noUISlider Provides vs. What Replaces It

| noUISlider responsibility | BEEQ replacement | Ignite UI replacement |
|---|---|---|
| Pointer / drag math | Native `<input type="range">` — zero JS | Pointer Events API + `setPointerCapture` |
| Step snapping | Native (browser) | One `Math.round` expression |
| Keyboard (arrows) | Native (browser) | `addKeybindings` utility (~10 lines) |
| Touch / pen support | Native (browser, unified) | Pointer Events API (unified) |
| Multi-handle collision | `Math.min/max` clamp | Value swap + focus shift |
| Track fill segment | `<span>` with `%` CSS | `<div>` with `%` CSS |
| Discrete ticks | Custom `<span>` DOM | Custom tick DOM |
| ARIA attributes | Native `<input>` | Hand-written `aria-valuenow/min/max` |

---

## Effect on the ESM / Jest Issue

The current test suite fails with:

```
SyntaxError: Cannot use import statement outside a module
```

This happens because `noUiSlider` is an ESM-only package not included in Jest's `transformIgnorePatterns`. The fix is to add it to the transform allowlist — but **replacing noUISlider with native inputs eliminates the problem entirely**. No package to transform.

---

## Form Association (`formAssociated: true` and the Mixin)

Switching to native inputs does **not** mean dropping `formAssociated: true` or `formAssociatedMixin`. The two layers solve different problems:

| Layer | Purpose | Needed with native inputs? |
|---|---|---|
| `formAssociated: true` + `setFormValue` | Controls the exact value submitted to the form (single serialized string, not two raw input values) | **Yes** — two `<input name="price">` would submit two entries |
| `formAssociatedMixin.formDisabledCallback` | Syncs `isDisabled` when an ancestor `<fieldset>` is disabled | **Yes** — without FACE, the component shell doesn't observe fieldset state |
| `formResetCallback` | Resets internal state on `form.reset()` | **Yes** — gives explicit control over what "reset" means for the serialized value |
| `formStateRestoreCallback` | Restores state on back/forward navigation | **Yes** — for correct multi-handle state restoration |

**Recommended approach:** Keep `formAssociated: true` and the mixin. Give the native `<input type="range">` elements **no `name` attribute** — they are interaction primitives only. Call `internals.setFormValue()` with the serialized value (`"20,80"`) from the component's `@Watch` handlers, exactly as today. This is the same pattern BEEQ follows.

---

## Conclusion

noUISlider is **not needed** for the Boreal DS slider design. Both BEEQ and Ignite UI ship production range sliders without any third-party interaction library.

**Recommended path: adopt the BEEQ approach** (two stacked native `<input type="range">`) because:

1. Zero JS for pointer, touch, and keyboard handling — the browser provides it
2. Eliminates `SliderAdapter` (~115 lines) and `SliderDOMController` (~120 lines) entirely
3. Eliminates the noUISlider ESM/Jest transform problem
4. Step snapping and arrow key behavior are native and spec-compliant
5. Reduces the dependency footprint (~30KB noUISlider minified removed)

The remaining custom work is:
- Style the native input with `appearance: none` + CSS custom properties for the thumb and track
- Render discrete tick `<span>` elements from a computed array
- Keep the existing form association layer (`formAssociated: true`, mixin, `internals.setFormValue()`) unchanged

The `formAssociatedMixin`, the form callbacks, and `setFormValue` architecture stay intact — they are independent of the interaction mechanism.
