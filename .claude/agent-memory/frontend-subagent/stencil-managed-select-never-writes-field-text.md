---
name: stencil-managed-select-never-writes-field-text
description: bds-select managed mode must not write the slotted field's text anywhere (loadValue AND resetValueField) — Stencil will not re-patch an unchanged vdom value, so an imperative child write leaves the field blank while the parent's committed value stands
metadata:
  type: project
---

Found in EOA-19597 T31 (`bds-search-bar` `items` mode), confirmed under `newSpecPage` and in the browser.

**Symptom:** type free text → Tab away. `value` became the typed text (the parent commits the pending debounced query on blur) but the field went blank. Same class of bug on popover close (`onAfterHide`) and Escape-from-item, because all three funnel through `bds-select.resetValueField()`.

**Root cause:** `bds-select` is `managed` when rendered by `bds-search-bar` (only consumer). The sequence on blur is:

1. `bds-text-field` emits `bdsBlur` → the search bar's `handleBlur` commits the pending query (`value` = typed text, `typedText = null`).
2. Still inside the same native `blur` dispatch, the select's `listenBlurInput` → `resetValueField()` → `bdsField.setAttribute('value', this.valueString)` (or `''` when `value` was still the pre-commit value on the select's own prop).
3. The queued render computes the same `fieldText` as before (the committed typed text equals what was typed), so Stencil's vdom diff sees no change and **never re-patches** the field. Result: blank field, committed value.

`loadValue` already had `if (!this.managed) this.valueString = text` (T12); `resetValueField` was the missing half. Popover close is the same bug with `bdsClose` (search bar commits) followed by `floating.mixin.ts`'s `hooks.onAfterHide`/`floatingOptions.onAfterHide` → `resetValueField`, and Escape-from-item closes the popover through the same `hide()` path.

**Rule:** in `managed` mode the parent owns the field text completely, so `bds-select` performs **no** `setAttribute('value', …)` on the slotted field — neither an option label nor a reset. Guard both `loadValue` (label write) and `resetValueField` (`if (this.managed) return;` at the top). Keep the rest of the blur handler (`resetChildren()`, selection state) — managed mode still needs the list-state reset.

**Safety check before changing this class of guard:** grep for `<bds-select` renders with a `managed` attribute. Only `bds-search-bar` sets it; `bds-pagination`'s items-per-page and `bds-date-picker`'s hour/minute selects are unmanaged, so unmanaged label/reset behaviour (and its specs) is unaffected.

**Related trap:** the same "no re-patch when `fieldText` is unchanged" property is what makes managed mode require this discipline — the parent cannot rely on a re-render to restore text that a child blanked imperatively.
