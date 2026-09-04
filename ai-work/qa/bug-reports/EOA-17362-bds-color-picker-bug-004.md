# BUG-004: `bds-color-picker` — invalid/unsupported external `.value` assignment is accepted into the property/attribute with no event and no error, even though the rendered UI correctly falls back to the last valid color

**Severity:** High
**Priority:** P1
**Type:** Functional / Data integrity
**Status:** Open
**Component:** `bds-color-picker`
**Discovered during:** TC-EDGE-006; extended 2026-09-04 while answering a user question about Vue `v-model` reachability of BUG-003
**Affects:** Any consumer that sets `.value` programmatically (external sync, form libraries, controlled-component patterns in React/Vue wrappers) — **and, specifically, anyone trying to programmatically control transparency/opacity, since that turns out to be entirely unsupported**

---

## Environment

- **Component:** `bds-color-picker` (`packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx`)
- **Playground fixture:** "Popover and Lifecycle Edge Cases" section, `id="edge-case-picker"`, wired to "Set valid value" / "Set invalid value" buttons that set `edgeCasePicker.value = '#00AAFF'` / `'#NOT-A-COLOR'`
- **Browser:** Chrome (latest stable), via `playwright-cli`

---

## Description

TC-EDGE-006 requires that an invalid externally-assigned value "does not corrupt the visible color state." The **visible UI** does in fact behave correctly — the HEX field text and the swatch both continue showing the last valid color after an invalid external assignment. However, the component's own **internal state is not actually protected**: the invalid string is accepted verbatim into the `value` property/attribute, and `checkValidity()` reports the (invalid) state as valid.

This is a UI-vs-model divergence: the picker *looks* fine, but its programmatic state is silently corrupted underneath.

## Addendum (2026-09-04): there is no public API for opacity/transparency at all, and this same bug is how you'd discover it

A user asked whether BUG-003 (the opacity-field display race) can be triggered through Vue `v-model` or by programmatically setting transparency. Investigating that surfaced a more fundamental gap:

**`bds-color-picker` has no public `@Prop()` for opacity/alpha at all.** Grepping the component (`bds-color-picker.tsx`) confirms opacity lives only in `@State() alphaDraft` / `hsva.alpha` — internal state, driven exclusively by direct UI interaction with the popover's opacity slider/field. The public `value` prop is parsed via `parseColor(value, alpha, ...)`, which **always reuses the current internal `alpha`** and ignores any alpha information in the incoming string. So:

- **BUG-003's specific race cannot be reached through `v-model`/programmatic assignment**, because there is no programmatic path to opacity in the first place — not even a buggy one.
- But the *natural* way a Vue/React consumer would try to control transparency — passing an 8-digit `#RRGGBBAA` hex, a 4-digit `#RGBA` shorthand, or an `rgba(...)` string into `.value` (all valid, standard CSS color formats) — hits this exact bug (BUG-004), generalized beyond the original `#NOT-A-COLOR` garbage-string case:

| Assigned to `.value` | `.value` / attribute after assignment | Rendered swatch/hex/opacity fields | `valueChange`/`bdsChange` fired? |
| --- | --- | --- | --- |
| `#FF000080` (8-digit hex+alpha) | Echoed back verbatim, `#FF000080` | **Unchanged** — stayed on the prior color, 100% opacity | **No** — neither event fires |
| `#F008` (4-digit hex+alpha) | Echoed back verbatim, `#F008` | **Unchanged** | **No** |
| `rgba(255, 0, 0, 0.5)` | Echoed back verbatim | **Unchanged** | **No** |
| `red` (CSS named color) | Echoed back verbatim, `"red"` | **Unchanged** | **No** |

All four were tested with the picker's opacity field/swatch showing zero change after the assignment, confirmed by direct DOM inspection, and none of them fire `valueChange` or `bdsChange` — verified by attaching listeners before the assignment and confirming an empty event log 400ms later.

**This is the important part for Vue specifically:** `v-model` on a Stencil component works by the wrapper setting `.value` and listening for `valueChange` to sync the bound variable back. Since none of these assignments fire `valueChange`, **Vue's own reactive variable stays exactly what the consumer set it to** (e.g. `#FF000080`) while the rendered picker silently keeps showing the old color — there is no event, warning, or validity signal of any kind that tells the Vue app its `v-model`-bound value and the visible picker have diverged. A developer would only notice by comparing the bound variable against a screenshot.

**One thing that is *not* a problem, and was checked directly because it's the closest real-world proxy for "Vue reactivity setting `.value` quickly":** rapidly assigning five different **valid** 6-digit hex values to `.value` back-to-back with no delay between them (simulating a fast-changing reactive prop) settles correctly and consistently — final `.value`, attribute, swatch, hex field, and opacity field all agreed with the last-assigned color in every trial. So ordinary fast/reactive re-assignment of a *valid* color is safe; the divergence only appears for value shapes the component doesn't recognize as a plain 6-/3-digit hex (which currently includes every alpha-carrying or named-color format).

---

## Steps to Reproduce

1. Open `http://localhost:3333`, scroll to "Popover and Lifecycle Edge Cases".
2. Note the picker's initial value: `document.getElementById('edge-case-picker').value === "#AA5500"`.
3. Click **Set valid value** (`edgeCasePicker.value = '#00AAFF'`). Confirm `.value === "#00AAFF"`, field and swatch show `#00AAFF`.
4. Click **Set invalid value** (`edgeCasePicker.value = '#NOT-A-COLOR'`).
5. Inspect:
   - `document.getElementById('edge-case-picker').value` → `"#NOT-A-COLOR"` (the raw invalid string, echoed back)
   - `getAttribute('value')` → `"#NOT-A-COLOR"` (also reflects the raw invalid string)
   - the HEX field's own `<input>.value` → `"#00AAFF"` (correctly still showing the last valid color — UI is fine)
   - the swatch's `--swatch-color` → `#00AAFF` (correctly still showing the last valid color — UI is fine)
   - `await picker.checkValidity()` → `true` (no validation failure reported)

---

## Expected Behaviour

Either:
- (a) an invalid external `.value` assignment should be rejected/coerced back to the last valid color at the property level too — so `.value` always reads back a valid hex string, consistent with what's rendered; **or**
- (b) if the component intentionally echoes back whatever was assigned (accepting the consumer's responsibility for valid input), then `checkValidity()` **must** report `false` for the invalid value, so form submission / validation correctly blocks on it.

Right now neither holds: the property silently diverges from the rendered UI, **and** validity reports "valid" regardless.

---

## Actual Behaviour

```json
{
  "componentValue": "#NOT-A-COLOR",
  "attrValue": "#NOT-A-COLOR",
  "fieldDisplay": "#00AAFF",
  "swatchColor": "#00AAFF",
  "checkValidity": true
}
```

---

## Impact

- Any consumer code that reads `colorPicker.value` after assigning it (a very common controlled-component pattern, e.g. immediately persisting the new value to a backend or store) will read back and act on the raw, unrecognized string it assigned — while the picker visually keeps showing a completely different color to the end user. This is exactly the kind of silent state/UI divergence that is very difficult to debug in production, since the picker "looks fine" during manual QA or a demo.
- Because `checkValidity()` returns `true`, a native `<form>` submission (per TC-FORM-001's pattern) will **not** block on this corrupted value, and `reportValidity()` will not surface any error to the user either.
- **Vue/React `v-model`/controlled-value consumers specifically**: since none of the unsupported formats fire `valueChange`/`bdsChange`, there is no event for the wrapper to react to — the framework-level bound value and the rendered component silently diverge with zero signal, not even a delayed or eventually-consistent one.
- **Opacity/transparency has no supported programmatic entry point at all** — 8-digit hex, 4-digit hex-with-alpha, and `rgba()` are all standard, reasonable formats a consumer would try, and all three currently no-op. Any product requirement that says "consumers can set an initial or controlled transparency value" is currently unimplementable through the public API, independent of BUG-003.

---

## Suggested Fix

- Route external `.value` assignments through the same normalization/validation path used for user-typed HEX input (the one already correctly restoring the UI to the last valid color) — reject/coerce anything that isn't a supported format, rather than silently accepting it into the property.
- Decide and document what `.value` is actually meant to accept — if only plain 6-/3-digit hex is intentional, reject everything else loudly (and update `checkValidity()` accordingly); if 8-digit hex/`rgba()`/named colors are meant to work (a reasonable expectation for a general-purpose color input), implement parsing for them and thread the alpha channel through to `hsva.alpha` instead of always overwriting it with the current internal alpha in `parseColor()`.
- If opacity is meant to be programmatically controllable (likely, given `bds-color-picker` is a full HSV/alpha color model internally), expose a public `@Prop()` for it — today it is unreachable from outside the component in any form, framework or vanilla.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-EDGE-006
- Related pattern (inverted): `.agents/memory/face-composite-child-value-sync-on-non-string-branch.md` — a different FACE value-sync gap found in a prior QA pass
