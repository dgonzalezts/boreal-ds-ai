# BUG-005: `bds-color-picker` — HEX/opacity text clips at narrow `custom-width`, and the popover overflows the viewport at mobile widths

**Severity:** Medium
**Priority:** P2
**Type:** UI / Responsive
**Status:** Open
**Component:** `bds-color-picker`
**Discovered during:** TC-VIS-002
**Affects:** Any consumer using a narrow `custom-width`, and all consumers viewed on narrow (mobile) viewports

---

## Environment

- **Component:** `bds-color-picker` (`packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx`, `bds-color-picker.scss`)
- **Playground fixture:** "Visual States and Responsive Layout" section, `label="Visual Test"`, `custom-width="320px"`
- **Browser:** Chrome (latest stable), via `playwright-cli`

---

## Description

Two distinct, related layout defects found while exercising TC-VIS-002 ("Set `custom-width` to a narrow and wide value" / "Resize the browser to desktop, tablet, and mobile widths"):

### Scenario A — narrow `custom-width` clips the HEX/opacity text with no truncation or minimum width

Setting `custom-width` below roughly `180px` causes the HEX input's flex-child wrapper to shrink far below the width its content needs, with no `min-width`, `text-overflow: ellipsis`, or scroll fallback. The result is the color value text (e.g. `#FFFFFF`) becomes almost entirely invisible/clipped — only a sliver of a single character is visible.

Measured at `custom-width="120px"`:
```json
{
  "containerWidth": 120,
  "hexWrapperWidth": 20,
  "hexInputScrollWidth": 58,
  "hexInputClientWidth": 4
}
```
The input needs 58px of content width but is only given 4px. Text becomes readable again only once `custom-width` reaches ~180px (this is the classic flexbox `min-width: auto` sizing issue — a flex child's default `min-width: auto` lets siblings with fixed widths (the swatch, separators) starve it, and nothing here overrides that with an explicit `min-width` or a `flex-shrink`/`text-overflow` strategy).

### Scenario B — the popover overflows the viewport at mobile widths, with no repositioning or width clamp

At a 375px-wide viewport (a standard small mobile breakpoint, e.g. iPhone SE), opening the popover on the (100%-width, non-custom-width) "Default" picker produces a panel whose right edge extends to `x=400px` — 25px past the 375px viewport edge. The popover uses `bds-popover`'s `setAnchorElement()` API (the correct anchoring mechanism, not manual `getBoundingClientRect()` math), so this is not a positioning-calculation bug — it is that the popover's content (driven by `bds-color-controls`' `min-width: $boreal-spatial-layout-l`) has no viewport-aware max-width/collision-avoidance, so `bds-popover` renders it exactly at its intrinsic width even when that exceeds the available viewport.

```json
{
  "left": 0,
  "right": 400,
  "viewportWidth": 375,
  "offscreenRight": true
}
```

`document.documentElement.scrollWidth` stays equal to `window.innerWidth` (no page-level horizontal scrollbar is introduced), meaning the popover is simply hard-clipped at the viewport edge — the right portion of its content (part of the saturation/brightness box, and potentially the hue/opacity sliders depending on exact panel width) is genuinely inaccessible to the user, not just scrolled out of view.

---

## Steps to Reproduce

### Scenario A
1. Open `http://localhost:3333`, scroll to "Visual States and Responsive Layout".
2. In DevTools Console: `document.querySelectorAll('bds-color-picker')[11].setAttribute('custom-width', '120px')`.
3. Screenshot the picker (closed/trigger state) — observe the HEX value is unreadable/clipped.

### Scenario B
1. Resize the browser viewport to 375×667 (e.g. `playwright-cli resize 375 667`, or DevTools device toolbar → iPhone SE).
2. Open the "Default" picker's popover (click its container).
3. Measure the popover panel's bounding box vs. `window.innerWidth`, or simply screenshot the page — the right edge of the panel is visibly cut off at the viewport boundary.

---

## Expected Behaviour

Per TC-VIS-002: "the picker and popover remain usable without clipping" and "the component uses the configured width without breaking its inputs."

- Scenario A: either enforce a sensible minimum `custom-width` below which the component refuses to shrink further, or apply `text-overflow: ellipsis`/an internal scroll so the value remains legible (even if truncated) rather than reducing to ~4px of visible content.
- Scenario B: the popover panel should either shrink to fit the viewport width (with internal scrolling/reflow if needed) or reposition itself (e.g. left-align/clamp against the viewport edge) so no part of its interactive content is rendered off-screen and inaccessible.

---

## Actual Behaviour

See measurements above — both scenarios currently render inaccessible/unreadable content with no fallback.

---

## Impact

- Scenario A: any consumer choosing a compact `custom-width` (a legitimate, documented prop) below ~180px ships an unusable color field — the HEX value is not readable and the input itself is barely clickable.
- Scenario B: any consumer using the default (100%-width) picker on a real mobile device narrower than ~400px cannot fully interact with the popover — parts of the saturation/brightness area and possibly the sliders are rendered outside the visible/tappable viewport.

---

## Suggested Fix

- Scenario A: add an explicit `min-width` to `.bds-color-picker__hex-input` (or its containing flex item) sized to the minimum readable HEX text, and/or `text-overflow: ellipsis` with `overflow: hidden` as a graceful degradation; consider documenting a supported minimum for `custom-width`.
- Scenario B: give the popover content (`bds-color-controls`'s root, or the `bds-popover` itself for this composition) a `max-width: calc(100vw - <margin>)` / viewport-aware collision handling so it never renders wider than the available viewport, consistent with how `bds-popover` is used elsewhere in the design system.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-VIS-002
- Related layout pattern: `.agents/memory/MEMORY.md` § "Cross-Browser — Safari-Specific Rendering & Interaction Bugs" (flexbox `min-width: auto` sizing quirks are a recurring risk category, though this particular finding reproduces in Chrome and is not Safari-specific)
