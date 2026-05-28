# BUG-001: `bds-select` — `valueChange` and `bdsChange` fire twice per selection with inconsistent `detail` values

**Severity:** High  
**Priority:** P1  
**Type:** Functional  
**Status:** Open  
**Component:** `bds-select`  
**Discovered during:** TC-FUNC-001 / TC-FUNC-011  
**Affects:** All consumers of `bds-select` that listen to `bdsChange` or `valueChange`

---

## Environment

- **Component:** `bds-select` (`packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`)
- **Story:** `Default` (Storybook — Forms → bds-select)
- **Browser:** Chrome (latest stable)
- **DevTools:** required for reproduction

---

## Description

Selecting an option from `bds-select` fires each of its two public events — `bdsChange` and `valueChange` — **twice** per selection instead of once. The duplicate firings originate from the slotted child components (`bds-list-menu`, `bds-text-field`) whose events bubble up through the light DOM to the `bds-select` host alongside `bds-select`'s own re-emissions.

More critically, the two `valueChange` firings carry **different `detail` values**:

| Firing | `target` | `detail` |
|--------|----------|----------|
| 1st (from `bds-select`) | `bds-select.hydrated` | `"option2"` — **value key** |
| 2nd (from `bds-text-field`, bubbled) | `bds-text-field...--selectable` | `"Option 2"` — **display label** |

A consumer that reads `event.detail` without checking `event.target` may silently process the display label string as the form value, corrupting state without any visible error.

---

## Steps to Reproduce

1. Open Storybook → Forms → bds-select → `Default` story
2. Open DevTools → Console
3. Select the `<bds-select>` host element in the Elements panel (`$0`)
4. Run in Console:
   ```javascript
   let log = [];
   ['bdsChange', 'valueChange'].forEach(n =>
     $0.addEventListener(n, e => log.push({ type: n, detail: e.detail, from: e.target.tagName }))
   );
   ```
5. Click any option in the dropdown (e.g. `option2`)
6. Run `log` in Console and inspect the array

---

## Expected Behaviour

`log` contains **2 entries** — one `bdsChange` and one `valueChange` — both with `detail` equal to the selected value key (e.g. `"option2"`), both with `from: "BDS-SELECT"`.

---

## Actual Behaviour

`log` contains **4 entries**:

```
[
  { type: "bdsChange",   detail: "option2",  from: "BDS-SELECT" },
  { type: "valueChange", detail: "option2",  from: "BDS-SELECT" },
  { type: "bdsChange",   detail: "option2",  from: "BDS-LIST-MENU" },
  { type: "valueChange", detail: "Option 2", from: "BDS-TEXT-FIELD" }
]
```

Order of last two entries may vary. The final `valueChange` detail is the **display label** (`"Option 2"`), not the value key.

---

## Root Cause

`bds-list-menu` and `bds-text-field` are placed via named slots (`<slot name="list">` / `<slot name="field">`). Slotted elements remain in the **light DOM**, so their events bubble naturally to the `bds-select` host.

`bds-select` registers direct listeners on the children via `addElementListener` (`bds-select.tsx:151`, `bds-select.tsx:161`) and re-emits its own events via `setValue()` (`bds-select.tsx:143-147`). It does not call `event.stopPropagation()` before re-emitting, so both the child's original event and `bds-select`'s own emission reach external listeners.

The `valueChange` inconsistency arises because `bds-select.setValue()` emits `detail: value` (the key), while `bds-text-field`'s `@Watch('value')` emits the string it was last set to — which is the display label (set via `updateElementAttr(this.bdsField, 'value', newValue)` at `bds-select.tsx:70`).

---

## Impact

- **Vue / React framework bindings:** `v-model` / `value` binding on `bds-select` receives `valueChange` twice. Depending on timing, the bound variable may settle on the display label string instead of the value key.
- **Form submissions:** If a consumer derives form data from the last `valueChange` event rather than the hidden `<input>`, submitted values may be human-readable labels instead of programmatic keys.
- **Event-driven side effects:** Any handler that fires on `bdsChange` (e.g. triggering an API call) runs twice per user interaction.

**Workaround (interim):** Consumers can guard with:
```javascript
selectEl.addEventListener('valueChange', e => {
  if (e.target !== e.currentTarget) return; // ignore bubbled child events
  handleChange(e.detail);
});
```

---

## Proposed Fix

All changes are in `bds-select.tsx` only. `bds-text-field` remains standalone-compatible.

**1. Stop `bds-list-menu`'s `bdsChange` before re-emitting (`bds-select.tsx:151`):**
```typescript
addElementListener(this.bdsList, 'bdsChange', (event: Event) => {
  event.stopPropagation();
  if (this.bdsList !== null) {
    const eventDetail = (event as CustomEvent<string | undefined>).detail;
    this.setValue(eventDetail || '');
  }
});
```

**2. Stop `bds-text-field`'s `valueChange` and `bdsChange` from leaking (add to `listenField()`):**
```typescript
addElementListener(this.bdsField, 'valueChange', (event: Event) => {
  event.stopPropagation();
});
addElementListener(this.bdsField, 'bdsChange', (event: Event) => {
  event.stopPropagation();
});
```

---

## Verification

After the fix, repeating the reproduction steps should produce a `log` array with exactly 2 entries, both with `from: "BDS-SELECT"` and `detail` equal to the value key.

Related test case that serves as the pass/fail gate: **TC-FUNC-011** in `ai-work/qa/test-plans/bds-select-test-plan.md`.

---

## Related

- Test plan: `ai-work/qa/test-plans/bds-select-test-plan.md` → TC-FUNC-001, TC-FUNC-011
- Risk row: "Child events bubble up alongside host re-emissions (double-fire)"
- Similar pattern to investigate in other composite components that use `addElementListener` without `stopPropagation`
