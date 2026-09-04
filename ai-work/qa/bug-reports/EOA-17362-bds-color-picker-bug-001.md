# BUG-001: `bds-color-picker` — internal `bds-number-field`/`bds-text-field` `valueChange` events bubble to the host and are indistinguishable from the component's own public event

**Severity:** High
**Priority:** P1
**Type:** Functional
**Status:** Open
**Component:** `bds-color-picker` (composed with `bds-color-controls`, `bds-color-format`, `bds-alpha-slider`)
**Discovered during:** TC-FUNC-001 (page-load console check) and TC-FORM-001
**Affects:** Every consumer of `bds-color-picker` that listens to `valueChange` or `bdsChange`

---

## Environment

- **Component:** `bds-color-picker` (`packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx`)
- **Playground:** `packages/boreal-web-components/src/index.html`, "Form Reset" section (`id="test-color-picker"`), reproducible on every `bds-color-picker` instance on the page
- **Browser:** Chrome (latest stable), via `playwright-cli`
- **Dev server:** `pnpm --filter boreal-web-components exec stencil build --dev --watch --serve --port 3333`

---

## Description

`bds-color-picker` declares its own public `@Event() valueChange!: EventEmitter<string>` (`bds-color-picker.tsx:107`), documented and used by consumers (including the Vue `v-model` convention per `.agents/memory/MEMORY.md`) as always carrying the current committed color as a hex string.

However, several internal light-DOM sub-components — at minimum the opacity `bds-number-field` used inside both `bds-color-controls` (closed-state trigger, class `bds-color-picker__alpha-input`) and `bds-color-format` (popover panel, class `bds-color-format__alpha-input`), and the various format-channel `bds-text-field`/`bds-number-field` inputs used for HEX/RGB/HSL/HSB editing — **also** emit their own bubbling, composed `valueChange` CustomEvent as part of their normal internal lifecycle/typing behavior. Because `bds-color-picker` never calls `event.stopPropagation()` on these children's events before (or instead of) re-emitting its own `valueChange`, every child firing reaches any listener attached to the `bds-color-picker` host — indistinguishable from the host's own canonical event.

This is the same bug class already fixed once in `bds-select` (`ai-work/qa/bug-reports/EOA-10544-bds-select-bug-001.md`) and documented as a recurring pattern in `ai-docs/guidelines/stencil-best-practices.md` § "Composite Light DOM Event Boundary".

### Consequences observed

1. **Spurious events fire at mount, before any user interaction.** Adding a capturing `document.addEventListener('valueChange', ...)` and reloading the page produces ~36 `valueChange` events (two per `bds-color-picker` instance on the page) with `target` = `BDS-NUMBER-FIELD.bds-color-picker__alpha-input` / `BDS-NUMBER-FIELD.bds-color-format__alpha-input` and `detail: "100"` — a bare numeric string, not a hex color.
2. **`detail` type is inconsistent and sometimes not a color at all.** During a single Form Reset (`TC-FORM-001`), the console log (wired to `colorPicker.addEventListener('valueChange', e => console.log(e.detail))`) recorded, for one logical reset action:
   ```
   valueChange: 35
   valueChange: #FFF000
   valueChange:      (empty string)
   valueChange: 100
   valueChange:      (empty string)
   valueChange: 100
   valueChange: #FFF000
   valueChange: #fff000
   ```
   Only the final `#FFF000` reflects the component's actual, documented value. A consumer relying on the *last* `valueChange` for correctness would happen to be safe here, but a consumer reacting to *every* `valueChange` (e.g. autosave-on-change, undo-stack push, analytics) processes six bogus intermediate events per reset, several of which are not even syntactically valid hex strings (`"35"`, `"100"`, `""`).
3. Same pattern reproduces during ordinary typing in the HEX/RGB/HSL/HSB channel fields inside the popover — each keystroke's underlying `bds-text-field`/`bds-number-field` re-emits its own `valueChange` in addition to (or interleaved with) the host's.

---

## Steps to Reproduce

1. Open `http://localhost:3333` (playground).
2. In DevTools Console, run:
   ```javascript
   document.addEventListener('valueChange', e =>
     console.log(e.type, e.target.tagName + '.' + e.target.className, JSON.stringify(e.detail)), true);
   ```
3. Reload the page.
4. Observe dozens of `valueChange` events fire immediately, before any interaction, with `target` = internal `BDS-NUMBER-FIELD` elements and `detail: "100"`.
5. Scroll to the "Form Reset" section, change the color and opacity, then click **Reset Form**.
6. Observe the console group `FORM RESET` logs multiple `valueChange:` lines with inconsistent values (`35`, `100`, empty string, `#FFF000`, `#fff000`) for the single reset action.

---

## Expected Behaviour

`bds-color-picker`'s `valueChange` should fire **only** when the component's own committed `value` changes, with `detail` **always** a normalized hex string (or whatever the documented contract is) — never a bare number, never an empty string, and never as a side effect of an internal sub-component's own event lifecycle. Internal child `valueChange`/`bdsChange` events must be stopped (`event.stopPropagation()`) before they can reach the host's external listeners, exactly as `bds-select.tsx` now does for `bds-list-menu`/`bds-text-field`.

---

## Actual Behaviour

Internal `bds-number-field`/`bds-text-field` `valueChange` events bubble unimpeded to the `bds-color-picker` host and are received by any external listener on that host, with `detail` values that do not match the component's documented `EventEmitter<string>` contract (numeric strings, empty strings, and lowercase-vs-uppercase hex duplicates all observed).

---

## Impact

- **Vue `v-model` binding:** since `valueChange` is the reserved event Vue wrapper uses for `v-model`, a bound variable can transiently (or, depending on timing, permanently) receive `"100"`, `""`, or other non-color values instead of the picker's actual color.
- **Any consumer-side `valueChange` handler** (autosave, undo stack, telemetry, cross-field sync) fires multiple extra times per user action with garbage payloads.
- **Page-load noise:** every page that mounts a `bds-color-picker` fires spurious events immediately on mount, before the user does anything, which is surprising and hard to filter defensively (there is no reliable way from outside to distinguish "real" vs. "leaked" events other than an `event.target !== event.currentTarget` guard, which most consumers won't think to add).

**Workaround (interim):** consumers can guard with the same pattern documented in `EOA-10544-bds-select-bug-001.md`:
```javascript
colorPicker.addEventListener('valueChange', (e) => {
  if (e.target !== e.currentTarget) return; // ignore bubbled child events
  handleChange(e.detail);
});
```

---

## Suggested Fix

In `bds-color-picker.tsx`, wherever internal `bds-number-field`/`bds-text-field` children are wired via `addElementListener` (or JSX inline handlers) for `bdsInput`/`bdsChange`/`valueChange`, call `event.stopPropagation()` inside those handlers before deriving and emitting the host's own `valueChange`/`bdsChange`. Apply the same treatment to `bds-color-controls.tsx` and `bds-color-format.tsx`, since both compose the affected `bds-number-field`/`bds-text-field` instances directly.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-FUNC-001, TC-FORM-001
- Prior occurrence, same root cause and fix pattern: `ai-work/qa/bug-reports/EOA-10544-bds-select-bug-001.md`
- Canonical guidance: `ai-docs/guidelines/stencil-best-practices.md` § "Composite Light DOM Event Boundary"
