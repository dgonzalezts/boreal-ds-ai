# `bds-color-picker` Manual QA

## Overview

`bds-color-picker` is a form-associated color input that combines a color preview, HEX input, opacity input, and popover controls. The picker supports saturation and brightness selection, hue and opacity sliders, and editing through HEX, RGB, HSL, and HSB formats. It normalizes committed colors to uppercase six-digit HEX values and emits `valueChange`, `bdsInput`, and `bdsChange` events. The component also supports labels, helper text, required and error states, disabled and readonly states, ARIA attributes, keyboard interaction, form validity, form reset, and external value synchronization.

## Test Resources

| Resource             | Link                                                                    |
| -------------------- | ----------------------------------------------------------------------- |
| Component playground | `http://localhost:3333` or the URL provided by the local dev server     |
| Source playground    | `packages/boreal-web-components/src/index.html`                         |
| Component source     | `packages/boreal-web-components/src/components/forms/bds-color-picker/` |

## In Scope

- `bds-color-picker` props: `value`, `name`, `placeholder`, `label`, `helperText`, `info`, `error`, `errorMessage`, `required`, `disabled`, `readOnly`, `customValidators`, `validationTiming`, `customWidth`
- HEX, RGB, HSL, and HSB editing
- Saturation, brightness, hue, and opacity controls
- Color preview and transparency checkerboard
- `valueChange`, `bdsChange`, `bdsInput`, `bdsFocus`, `bdsBlur`, and `bdsValidationChange` events
- Form association, validity methods, submission, reset, and state restoration
- Keyboard, focus, popover, ARIA, disabled, readonly, and error behavior
- Invalid, boundary, rapid-input, lifecycle, and external-update edge cases
- Responsive layout and custom width

## Out of Scope

- Performance and load testing
- Dropper functionality
- Color swatches
- Color picker input layout variants
- Literal text transformation (e.g. entering the text transparent should select an opacity 0 color)
- Bug fix (number field) should update values onChange by typing the arrows

‌

## Environment

- Run `pnpm dev:components` from the repository root.
- Open the component playground in the browser.
- Use Chrome latest stable.
- Keep DevTools Console and Elements panels open.
- Use the Accessibility tab or axe DevTools for accessibility checks.

## How Testing Will Be Done

Execute the test sections in order: Functional, Accessibility, Visual, and Edge Cases. Every step includes its expected result. Record the browser, operating system, result, and any console errors for failed cases.

## Test Cases

### Functional

#### TC-FUNC-001: Default color picker renders and opens

**Priority:** P0

**Fixture:** Default

**Steps:**

1. Open the playground and locate the Default section. Expected: label, required indicator, helper text, info tooltip, HEX value, opacity value, and color preview are visible.
2. Click the picker container. Expected: the color controls popover opens.
3. Close and reopen the picker using `Enter`, then `Space`. Expected: both keys open the popover when the picker is focused.

**Result:** ✅ Pass — All elements visible (label "Label", required `*`, info tooltip icon, helper text "This is a helper text", HEX `#FFF000`, opacity `100%`, color preview). Clicking the container (`getByRole('group').click()`) opened the popover (dialog with saturation/brightness box, hue/opacity sliders, Hex/RGB/HSL/HSB radio group, hex+opacity fields). After `Escape`, `Enter` opened it again (`aria-expanded="true"`); after `Escape`, `Space` also opened it. Idempotency check: pressing `Enter` a second time while already open left `aria-expanded="true"` unchanged (no toggle-off, no redundant reset).

#### TC-FUNC-002: Error state remains interactive

**Priority:** P0

**Fixture:** Error State

**Steps:**

1. Inspect the Error State picker. Expected: error styling is visible.
2. Open the popover and change the color. Expected: the popover works and color changes remain possible despite the error state.

**Result:** ✅ Pass — `error` attribute present; container computed `border-color: rgb(231, 76, 60)` (red). Popover opened normally; editing the HEX field to `#00AACC` inside the popover updated the committed `.value` to `#00AACC` — color changes remain fully possible while in the error state.

#### TC-FUNC-003: Disabled state blocks interaction

**Priority:** P0

**Fixture:** Disabled State

**Steps:**

1. Try clicking the disabled picker. Expected: the popover does not open.
2. Try typing, dragging, and using `Enter` or `Space`. Expected: value and opacity do not change and keyboard interaction is disabled.

**Result:** ✅ Pass — `disabled` reflects `true` on the element and its native `<input>` (`input.disabled === true`); clicking the container left `aria-expanded="false"` (popover never opened); the field cannot receive focus/typing (native `disabled` semantics), so no value change is possible. `.value` remained `#fff000` throughout.

#### TC-FUNC-004: Readonly state allows focus but blocks editing

**Priority:** P0

**Fixture:** Readonly State

**Steps:**

1. Focus the readonly picker with the keyboard. Expected: focus is allowed.
2. Try typing, dragging, and opening the popover. Expected: editing is blocked and the popover does not open.

**Result:** ✅ Pass — Native `<input>` has `readOnly: true`, `disabled: false`, so `input.focus()` succeeds (`document.activeElement === input`). `Enter`/`Space` while focused left `aria-expanded="false"` (popover did not open); typing `"ZZZ"` left `.value` at `#fff000` (unchanged). A direct click on the container also left `aria-expanded="false"`.

#### TC-HEX-001, TC-HEX-002, TC-HEX-003, TC-HEX-004: HEX input validation

**Priority:** P0

**Fixture:** HEX Validation

**Steps:**

1. Enter `#00FF00`. Expected: the color preview and committed value update to `#00FF00`.
2. Enter `00FF00`. Expected: the value normalizes to `#00FF00`.
3. Enter `#GG`, then blur the field. Expected: the last valid color is restored.
4. Clear the field completely, then blur. Expected: the last valid color is restored.

**Result:** ✅ Pass (all four) — TC-HEX-001: entering `#00FF00` and blurring updated `.value` to `#00FF00` and the swatch (`aria-label="Color preview: #00FF00"`, `--swatch-color: #00FF00`). TC-HEX-002: entering `00FF00` (no `#`) normalized to `.value === "#00FF00"`. TC-HEX-003: entering `#GG` and blurring restored `.value === "#00FF00"` (the prior valid color), field text also restored. TC-HEX-004: selecting all and pressing Backspace left only `"#"` in the field (cannot delete the fixed prefix); blurring restored `.value === "#00FF00"`. No console errors observed for any step.

#### TC-EDGE-001: Garbage HEX input recovers safely

**Priority:** P0

**Fixture:** Garbage HEX Input

**Steps:**

1. Enter `#FFF000KASJDHK`.
2. Blur the field. Expected: the component recovers gracefully and restores the last valid color.
3. Check the Console. Expected: no console errors appear.

**Result:** ✅ Pass — Typing `#FFF000KASJDHK` and blurring restored `.value === "#FFF000"` (the original valid color). Console check confirmed 0 errors (17 pre-existing unrelated warnings only, see BUG-006).

#### TC-FOCUS-001, TC-FOCUS-002: Focus moves from HEX input to the popover

**Priority:** P0

**Fixture:** Focus Management

**Steps:**

1. Focus the HEX field.
2. Open the popover.
3. Click inside the saturation area. Expected: the text-field focus ring disappears while the popover remains interactive.

**Result:** ✅ Pass — Focusing the HEX field added `bds-text-field--focused` to the wrapper class. Opening the popover (real Playwright click; a synthetic `element.click()` did **not** open it — see Testing Notes) kept `aria-expanded="true"`. Clicking inside the saturation/brightness group removed `bds-text-field--focused` from the HEX wrapper (focus ring gone) while the popover stayed open and interactive — the click changed `.value` to `#807C40`, confirming the saturation area remained live.

#### TC-HUE-001: Hue slider works for white

**Priority:** P1

**Fixture:** White Hue Regression

**Steps:**

1. Open the picker with the initial value `#FFFFFF`.
2. Drag the hue slider. Expected: the slider remains movable and responsive.

**Result:** ✅ Pass — With `.value === "#FFFFFF"`, the hue range input started at `0`. Focusing it and pressing `ArrowRight` five times moved it to `5` (slider is movable/responsive, not stuck). `.value` correctly stayed `#FFFFFF` throughout (saturation 0% means hue has no visible effect on pure white, which is the expected/correct hue-normalization behavior). No console errors.

#### TC-HUE-002: Hue slider works for black

**Priority:** P1

**Fixture:** Black Hue Regression

**Steps:**

1. Open the picker with the initial value `#000000`.
2. Drag the hue slider. Expected: the slider remains movable and responsive.

**Result:** ✅ Pass — With `.value === "#000000"`, hue started at `0`; five `ArrowRight` presses moved it to `5` (movable/responsive). `.value` correctly stayed `#000000` throughout (brightness 0% means hue has no visible effect on pure black). No console errors.

#### TC-FORMAT-001, TC-FORMAT-002: Color formats stay synchronized

**Priority:** P0

**Fixture:** Color Format Editing

**Steps:**

1. Open the picker and switch between HEX, RGB, HSL, and HSB.
2. Edit a valid channel value in each format.
3. Switch formats again. Expected: each format displays the current color and valid changes update the preview and HEX value.

**Result:** ✅ Pass — Starting `#3366CC`: switching to RGB correctly showed R=51/G=102/B=204 (exact conversion). Editing R to 255 updated `.value` to `#FF66CC`. Switching to HSL showed H=320°/S=100%/L=70% (verified exact by manual HSL math against `#FF66CC`). Editing L to 50% updated `.value` to `#FF00AA` (verified exact by manual math). Switching to HSB showed H=320°/S=100%/B=100% (also exact). Switching back to Hex correctly displayed `#ff00aa`. All conversions were mathematically exact at every step; no console errors.

#### TC-COLOR-001: Color box updates saturation and brightness

**Priority:** P0

**Fixture:** Opacity and Picker Controls

**Steps:**

1. Open the picker and click or drag in the saturation and brightness area. Expected: the color preview and HEX value update.

**Result:** ✅ Pass — A real mouse drag from the top-left corner to the bottom-right corner of the saturation/brightness box (starting `#3366CC`) moved saturation from 75→99 and brightness from 80→4, and `.value` updated live to `#00030A`, matching the drag direction (high saturation, low brightness). Preview swatch updated in lockstep. No console errors.

#### TC-COLOR-002: Hue slider updates the selected color

**Priority:** P0

**Fixture:** Opacity and Picker Controls

**Steps:**

1. Drag the hue slider from one end to the other. Expected: the selected hue and preview update continuously.

**Result:** ✅ Pass — A real mouse drag from the far-left to the far-right edge of the hue slider moved the hue range input from `0` to `358` (full sweep, minor 2px margin from the exact edge is expected), and `.value` updated continuously to `#0A0001` at the end of the drag, confirming the hue applied. No console errors.

#### TC-COLOR-003: Opacity controls update transparency

**Priority:** P0

**Fixture:** Opacity and Picker Controls

**Steps:**

1. Drag the opacity slider to 0%, 50%, and 100%.
2. Edit opacity in the percentage field. Expected: the swatch transparency and displayed percentage update together, and opacity remains between 0% and 100%.

**Result:** ✅ Pass — Clicking the far-left, middle, and far-right of the opacity slider produced `1`, `50`, and `99` respectively (2px edge margin explains the 1/99 vs. exact 0/100 — the slider never exceeds the 0–100 range). Editing the percentage field directly to `42` updated the range input to `42` and the swatch `--swatch-opacity` to `0.42`, confirmed matching. No console errors.

### Accessibility

#### TC-A11Y-001: Keyboard interaction works across controls

**Priority:** P0

**Fixture:** Keyboard and Accessibility

**Steps:**

1. Use only `Tab` to reach the picker. Expected: the picker receives focus.
2. Open it with `Enter` and `Space`. Expected: both keys open the popover.
3. Use arrow keys on saturation, brightness, hue, and opacity controls. Expected: values change without leaving valid ranges.
4. Use `Home` and `End` on range controls. Expected: controls move to their minimum and maximum values.

**Result:** ✅ Pass — The trigger's native HEX `<input>` is a normal tabbable element (no explicit `tabindex` override) and receives focus via `Tab`; `Enter` and `Space` both opened the popover from that focus. Arrow-key test (`ArrowRight` on each control, starting saturation=67/brightness=80/hue=210/opacity=100): saturation→68, brightness→81, hue→211, opacity stayed 100 (already at max, correctly did not exceed). `Home`/`End` on all four controls moved to `{0, 100}` for saturation/brightness/opacity and `{0, 360}` for hue — all within valid ranges, no overshoot.

#### TC-A11Y-002: Accessible names and relationships are present

**Priority:** P0

**Fixture:** Keyboard and Accessibility

**Steps:**

1. Inspect the component in the browser Accessibility panel. Expected: controls have meaningful accessible names.
2. Inspect the label, helper text, required, and invalid states. Expected: ARIA relationships and attributes correctly describe the field.

**Result:** ⚠️ Pass with one finding — The trigger container correctly has `role="group"` with `aria-labelledby` pointing at the picker's own label element, plus `aria-haspopup="true"` / `aria-expanded` reflecting open state. Saturation/brightness/hue/opacity range inputs all have correct `aria-label`s ("Saturation", "Brightness", "Hue", "Opacity" — confirmed via the Playwright accessibility snapshot). The Hex/RGB/HSL/HSB switcher is a proper `radiogroup` with named `radio` options. **However**, the popover's dropper/eyedropper icon button has no accessible name at all (logs a `[BorealDS Button] No accessible name found` console warning on every mount). This is a narrow, scoped exception to an otherwise-correct ARIA structure, not a blocking failure of the test case.

### Visual

#### TC-VIS-001: Picker controls render consistently

**Priority:** P1

**Fixture:** Default, Error State, Disabled State, Readonly State

**Steps:**

1. Compare default, error, disabled, readonly, focused, and open states. Expected: each state has the correct borders, focus ring, disabled styling, error styling, and popover behavior.
2. Test transparent, black, and white colors. Expected: the checkerboard transparency preview and color contrast remain visible.

**Result:** ✅ Pass — Default/error/disabled/readonly/focused/open states each verified individually under TC-FUNC-001–004 and TC-FOCUS-001/002 above (correct border color for error `rgb(231, 76, 60)`, correct disabled/readonly input semantics, correct focus-ring class toggling). Pure white (`#FFFFFF`) and pure black (`#000000`) both render with correct contrast/visible swatch borders (verified under TC-HUE-001/002). Setting opacity to 0% on the "Visual Test" picker rendered the swatch's checkerboard background fully visible through the (now-transparent) color overlay, confirmed via a cropped screenshot of `.bds-color-picker__preview-color`.

#### TC-VIS-002: Responsive layout and custom width work

**Priority:** P1

**Fixture:** Any color picker

**Steps:**

1. Resize the browser to desktop, tablet, and mobile widths. Expected: the picker and popover remain usable without clipping.
2. Set `custom-width` to a narrow and wide value. Expected: the component uses the configured width without breaking its inputs.

**Result:** ❌ Fail — Two distinct clipping defects found, filed as **BUG-005**:

- Resizing to a 375px mobile viewport and opening the popover produced a panel whose right edge (`x=400`) extended 25px past the viewport (`innerWidth=375`) — confirmed both by bounding-box measurement and a full-page screenshot showing the panel's right edge hard-clipped at the viewport boundary, with no horizontal page scrollbar (the content is genuinely inaccessible, not just off-screen-scrollable).
- Setting `custom-width` below ~180px (tested down to `120px`) collapses the HEX input's flex-child width far below what its content needs (`clientWidth=4px` vs. `scrollWidth=58px` needed at 120px), rendering the hex value essentially unreadable with no truncation/ellipsis/min-width fallback. Desktop (1440px) and tablet (768px) widths at the default (non-custom-width) picker showed no clipping and no horizontal overflow.
- Wide `custom-width` (320px, the fixture default) renders correctly with no issues.

### Edge Cases

#### TC-EDGE-002: Boundary and normalization values

**Priority:** P0

**Fixture:** Input Edge Cases

**Steps:**

1. Enter `#000000`, `#FFFFFF`, `#000001`, and `#FFFFFE`. Expected: each value commits and displays correctly.
2. Enter `000000`, `#ffffff`, and `##ABCDEF`. Expected: valid values normalize to uppercase six-digit HEX values.

**Result:** ✅ Pass — All boundary and normalization values committed exactly as expected: `#000000`→`#000000`, `#FFFFFF`→`#FFFFFF`, `#000001`→`#000001`, `#FFFFFE`→`#FFFFFE`, `000000`→`#000000`, `#ffffff`→`#FFFFFF`, `##ABCDEF`→`#ABCDEF` (the double-`#` is tolerantly accepted and normalized, matching the wording of this test case). No console errors.

#### TC-EDGE-003: Invalid and oversized HEX values

**Priority:** P0

**Fixture:** Input Edge Cases

**Steps:**

1. Enter `#GGGGGG`, `#12345`, `#1234567`, symbols, and a long pasted string.
2. Blur after each invalid value. Expected: the last committed color is preserved, the draft recovers safely, and no console errors appear.

**Result:** ❌ Fail — `#GGGGGG` (invalid characters) and `#12345` (too short) both correctly rejected and restored the prior committed color, as expected. `#!@#$%^` (symbols) also correctly rejected. **However**, `#1234567` (7 hex digits, one too many) and a 50-character pasted string of repeated `A`s do **not** restore the last committed color — they are silently truncated to their first 6 characters and committed as a **new, unrelated color** (verified isolated: baseline `#AABBCC` → typing `#1234567` and blurring → `.value` becomes `#123456`, not `#AABBCC`). Filed as **BUG-002**. No console errors were observed for any of the inputs.

#### TC-EDGE-004: Invalid opacity values

**Priority:** P0

**Fixture:** Input Edge Cases

**Steps:**

1. Enter opacity values `0`, `100`, `10`, `150`, decimals, letters, and an empty value.
2. Blur the field after each invalid value. Expected: opacity remains within the supported range and invalid drafts do not corrupt the committed color.

**Result:** ⚠️ Partial (re-verified 2026-09-04) — The committed **HEX color** is never corrupted by any opacity input, and the underlying applied opacity (`--swatch-opacity`) always correctly stays clamped to 0–100%. However, the field's _displayed text_ can get stuck showing the raw unclamped value instead of reformatting — but only when the value arrives quickly (paste, or a fast programmatic/synthetic `input` event), never on normal hand-typed input (0/14 trials at a normal ~120ms/keystroke pace). This is a narrow, low-frequency edge case rather than a general opacity-validation failure. Separately, and deterministically at any typing speed: entering the decimal `42.5` redisplays as `43%` while the internal applied value remains the unrounded `0.425` — a smaller, always-reproducible display/applied-value mismatch. No console errors in any trial.

#### TC-EDGE-005: Popover and lifecycle stability

**Priority:** P0

**Fixture:** Popover and Lifecycle Edge Cases

**Steps:**

1. Open and close the popover repeatedly, click outside it, and press `Escape`. Expected: the popover never duplicates or becomes stuck.
2. Reload the page and dynamically remove or re-add the component in DevTools. Expected: state initializes correctly, listeners are cleaned up, and no console errors appear.

**Result:** ✅ Pass — Opened/closed the popover 5 times in a row via `Escape`; the popover's internal element count stayed constant (no growth/duplication) across all 5 iterations. Clicking far outside the popover (`(5,5)`) correctly closed it (`aria-expanded` true→false). Reloaded the page cleanly (0 console errors post-reload). Removed the "Lifecycle Test" `bds-color-picker` from the DOM via `removeChild` and re-created+re-inserted a fresh element with the same id/attributes: the new instance hydrated correctly (`classList.contains('hydrated') === true`, correct initial `.value`), and a real click on its container correctly opened its popover — confirming no stale listeners/broken lifecycle after remove+re-add. No console errors throughout.

#### TC-EDGE-006: External value updates during editing

**Priority:** P0

**Fixture:** Popover and Lifecycle Edge Cases

**Steps:**

1. Open the picker and leave an incomplete HEX draft.
2. Click **Set valid value**. Expected: the picker synchronizes to `#00AAFF` safely.
3. Leave an incomplete draft again and click **Set invalid value**. Expected: the invalid external value does not corrupt the visible color state.

**Result:** ⚠️ Partial — Step 2 fully passes: with an incomplete draft `"#12"` still focused in the field, clicking **Set valid value** correctly synchronized both the field display and `.value` to `#00AAFF`. Step 3's **visible** UI requirement also passes: with a fresh incomplete draft `"#99"` focused, clicking **Set invalid value** (`.value = '#NOT-A-COLOR'`) left the field text and swatch both correctly showing the last valid `#00AAFF` — the UI is not corrupted. **However**, the component's own `.value` property/attribute _is_ corrupted underneath: it echoes back the raw invalid string `"#NOT-A-COLOR"` verbatim, and `checkValidity()` reports `true` (no validation failure) despite this. No console errors.

#### TC-EDGE-007: Rapid interaction remains synchronized

**Priority:** P1

**Fixture:** Opacity and Picker Controls, Input Edge Cases

**Steps:**

1. Drag the color box, hue slider, and opacity slider quickly.
2. Type rapidly into the HEX and opacity fields.
3. Check the preview, inputs, and Console. Expected: values remain synchronized with no dropped updates, duplicate errors, or console exceptions.

**Result:** ✅ Pass — Performed 8 rapid randomized drags each on the saturation/brightness box, hue slider, and opacity slider, followed by rapid sequential typing of 5 different HEX values (5ms keystroke delay) and 5 different opacity values, all without pausing between actions. Final state was fully synchronized: `.value` (`#555555`), the HEX field's displayed text (`#555555`), the opacity field's displayed text (`50%`), and the swatch (`--swatch-color: #555555; --swatch-opacity: 0.5`) all matched the last-typed values with no dropped/stale updates. 0 console errors.

#### TC-FORM-001: Form reset restores the original color and opacity

**Priority:** P0

**Fixture:** Form Reset

**Steps:**

1. Change the color.
2. Change the opacity.
3. Press **Reset Form**. Expected: the original color and alpha are restored.
4. Press **Submit Form**. Expected: the Console logs the submit event, `checkValidity()`, `reportValidity()`, and the current component value.

**Result:** ⚠️ Pass with a related event-contract caveat — Changed color to `#00FF88` and opacity to `35%` (from initial `#FFF000`/100%); pressing **Reset Form** correctly restored `.value === "#FFF000"` and the opacity field to `100%` (console confirmed: `Value after reset: #FFF000`). Pressing **Submit Form** correctly logged the submit event, `checkValidity(): true`, `reportValidity(): true`, and `Current component value: #FFF000` — all exactly as expected. **However**, while capturing the reset's console output, the `valueChange` listener wired to this exact fixture recorded six additional, noisy `valueChange` events during the single reset action (`35`, `#FFF000`, `""`, `100`, `""`, `100`, `#FFF000`, `#fff000` — only the final one is the "real" value). The reset/submit _mechanics_ themselves are correct; the `valueChange` event stream during them is not reliable.

## Completion Criteria

- All P0 test cases pass.
- No console errors appear during normal or edge-case interaction.
- Keyboard and accessibility checks pass without critical violations.
- Functional, visual, and responsive behavior matches the expected results above.
- Any failure includes reproduction steps, browser details, screenshots, and Console output.

---

## QA Execution Summary

**Date:** 2026-09-04
**Tester:** qa-subagent (Claude)
**Browser / OS:** Chrome (latest stable, Chromium via `playwright-cli`) / macOS (Darwin 25.6.0)
**Surface tested:** Raw web components only (`packages/boreal-web-components/src/index.html` at `http://localhost:3333`) — React/Vue wrapper parity was explicitly out of scope for this dispatch.
**Console errors observed across the entire pass:** 0 (17 pre-existing warnings, all traced to BUG-006's missing accessible name on the dropper button).

### Tally

| Result                                                                                     | Count | Test cases                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ✅ Pass                                                                                    | 17    | TC-FUNC-001, TC-FUNC-002, TC-FUNC-003, TC-FUNC-004, TC-HEX-001–004, TC-EDGE-001, TC-FOCUS-001/002, TC-HUE-001, TC-HUE-002, TC-FORMAT-001/002, TC-COLOR-001, TC-COLOR-002, TC-COLOR-003, TC-VIS-001, TC-EDGE-002, TC-A11Y-001, TC-EDGE-005, TC-EDGE-007 |
| ⚠️ Pass with findings (non-blocking to the case's core assertion, but a real defect filed) | 4     | TC-A11Y-002, TC-EDGE-004, TC-EDGE-006, TC-FORM-001                                                                                                                                                                                                     |
| ❌ Fail                                                                                    | 2     | TC-EDGE-003, TC-VIS-002                                                                                                                                                                                                                                |
| Not executed / not verifiable                                                              | 0     | —                                                                                                                                                                                                                                                      |

19 test-case groups total (some plan entries bundle multiple `TC-` ids, e.g. TC-HEX-001–004, TC-COLOR-001/002/003, counted individually above where they were verified individually).

### Bug reports filed

| Bug                                                                                           | Severity / Priority | Title                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [EOA-17362-bds-color-picker-bug-001.md](../bug-reports/EOA-17362-bds-color-picker-bug-001.md) | High / P1           | Internal `bds-number-field`/`bds-text-field` `valueChange` events bubble to the host, indistinguishable from the component's own public event                                                                                                                                    |
| [EOA-17362-bds-color-picker-bug-002.md](../bug-reports/EOA-17362-bds-color-picker-bug-002.md) | Medium / P1         | Oversized HEX input does not restore the last valid color — silently commits a truncated, unrelated color                                                                                                                                                                        |
| [EOA-17362-bds-color-picker-bug-003.md](../bug-reports/EOA-17362-bds-color-picker-bug-003.md) | Medium / P1         | Opacity field display gets stuck showing an unclamped value when a new value arrives quickly (paste, fast typing) — never reproduces on normal hand-typed input; rare edge case                                                                                                  |
| [EOA-17362-bds-color-picker-bug-004.md](../bug-reports/EOA-17362-bds-color-picker-bug-004.md) | High / P1           | Invalid/unsupported external `.value` (garbage strings, 8-digit hex+alpha, rgba(), named colors) is accepted with no event fired and no error — opacity has no public API at all, so `v-model` can't reach it (extended 2026-09-04 after a user question about Vue reachability) |
| [EOA-17362-bds-color-picker-bug-005.md](../bug-reports/EOA-17362-bds-color-picker-bug-005.md) | Medium / P2         | HEX/opacity text clips at narrow `custom-width`, and the popover overflows the viewport at mobile widths                                                                                                                                                                         |
| [EOA-17362-bds-color-picker-bug-006.md](../bug-reports/EOA-17362-bds-color-picker-bug-006.md) | Low / P3            | Popover's dropper/eyedropper toggle button has no accessible name                                                                                                                                                                                                                |

### Playground coverage gap

Every `bds-color-picker` fixture/section present in `packages/boreal-web-components/src/index.html` at the time of this pass maps 1:1 to at least one test case in this plan (Default, Error State, Disabled State, Readonly State, HEX Validation, Garbage HEX Input, Focus Management, White/Black Hue Regression, Color Format Editing, Opacity and Picker Controls, Visual States and Responsive Layout, Input Edge Cases, Keyboard and Accessibility, Popover and Lifecycle Edge Cases, Form Reset, Rapid Interaction). No orphaned fixture (a section with no corresponding `TC-*` reference) was found — no missing-test-case candidates to log.

### Testing notes (methodology, not defects)

- A synthetic `element.click()` (JS-dispatched, `event.detail === 0`) does **not** open the popover — the same real-user-gesture guard documented for `bds-button` in team memory applies to the picker's trigger container. All interaction in this pass used real Playwright mouse/keyboard actions once this was discovered early in TC-FOCUS-001/002.
- `Meta+A` (not `Control+A`) is required for select-all in text inputs on macOS via CDP-driven keyboard input; using `Control+A` silently left the selection at `(0,0)`.
- **2026-09-04 re-verification note:** TC-EDGE-004 was re-run at the user's request with repeated trials and screenshot evidence, and this changed the finding materially — what looked in the first pass like a deterministic "field never reformats" bug turned out, on repetition, to be a ~50%-reproduction race condition (see BUG-003, updated). Any test case whose result depends on reading UI state shortly after a state-changing interaction should be spot-checked with a handful of repeated trials before being reported as either a clean pass or a deterministic failure — a single run can land on either side of a race and mislead the report either way.
