# BUG-002: `bds-color-picker` — oversized HEX input does not restore the last valid color, it silently commits a truncated, unrelated color

**Severity:** Medium
**Priority:** P1
**Type:** Functional
**Status:** Open
**Component:** `bds-color-picker`
**Discovered during:** TC-EDGE-003
**Affects:** Any consumer allowing free-text HEX entry (default trigger field behavior)

---

## Environment

- **Component:** `bds-color-picker` (`packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx`)
- **Playground fixture:** "Input Edge Cases" section, `label="Edge Case Input"`, initial `value="#123456"`
- **Browser:** Chrome (latest stable), via `playwright-cli`

---

## Description

TC-EDGE-003 requires that invalid or oversized HEX input, once blurred, restores the **last committed valid color** without corrupting it. This holds for `#GGGGGG`, `#12345` (too short), and symbol strings — but **not** for a 7-hex-digit ("oversized by one") string such as `#1234567`, and not for an arbitrarily long pasted string.

Typing `#1234567` (7 hex digits after `#`) into the trigger's HEX field and blurring does not restore the prior committed color. Instead, the component silently accepts the **first 6 characters** of the typed string as a brand-new committed color, discarding the trailing character with no rejection, warning, or visual indication that the input was invalid.

The same happens for a long pasted string of repeated characters (e.g. 50× `A`) — it commits as `#AAAAAA` (the first 6 characters) rather than being rejected.

This is inconsistent with `#12345` (5 digits, too short) and `#GGGGGG` (invalid characters), both of which are correctly rejected and correctly restore the prior valid color — the only difference is that the *truncated prefix* of the 7+ character strings happens to be syntactically valid hex, so the component accepts it as if the user had typed exactly that shorter string on purpose.

---

## Steps to Reproduce

1. Open `http://localhost:3333`, scroll to "Input Edge Cases".
2. Set a known baseline: click the HEX field, select all, type `#AABBCC`, press Tab. Confirm `document.querySelectorAll('bds-color-picker')[12].value === "#AABBCC"`.
3. Click the HEX field again, select all, type `#1234567` (8 characters including `#`, 7 hex digits).
4. Observe the field visibly shows the full `#1234567` while focused (`input.value === "#1234567"` — not truncated during typing).
5. Press Tab to blur.
6. Read `document.querySelectorAll('bds-color-picker')[12].value`.

---

## Expected Behaviour

Per TC-EDGE-003: "the last committed color is preserved, the draft recovers safely, and no console errors appear." `#1234567` is 7 hex digits — not a valid 6-digit (or 3-digit) hex color — so the component should reject it on blur and restore `#AABBCC`, exactly as it does for `#12345` and `#GGGGGG`.

---

## Actual Behaviour

`document.querySelectorAll('bds-color-picker')[12].value` becomes `"#123456"` — a color the user never explicitly requested, silently substituted for the actually-typed (invalid) `#1234567`, discarding the prior committed `#AABBCC` entirely.

Verified with instrumentation:
```json
{
  "afterValidCommit": "#AABBCC",
  "duringTyping": "#1234567",
  "afterOversizedBlur": "#123456"
}
```

No console errors were observed in either case.

---

## Impact

- A user who fat-fingers one extra hex digit gets a **different, unrelated color** silently applied instead of either being told the input is invalid or having their last valid color preserved — the truncation is invisible unless the user notices the swatch changed color.
- The behavior is inconsistent with the component's own handling of other invalid-length HEX input (`#12345`), which correctly preserves the last valid color. There is no single coherent validation rule from the user's perspective: "too short" is rejected, "too long by 1" is silently truncated and accepted, and "too long by many" (paste) is also silently truncated and accepted only when the resulting 6-character prefix happens to be valid hex.

---

## Suggested Fix

Validate the **full** entered string length and character set before commit — reject (and restore the last valid color) for any string whose stripped hex payload is not exactly 3, 4, 6, or 8 valid hex characters (per whatever lengths the component's HEX grammar supports), rather than truncating to the first 6 characters and validating only the prefix.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-EDGE-003
