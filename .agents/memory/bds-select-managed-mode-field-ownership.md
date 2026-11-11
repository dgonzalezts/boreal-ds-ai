---
name: bds-select-managed-mode-field-ownership
description: "In managed mode bds-select must write nothing into the slotted field (no option label, no reset — Stencil never re-patches an unchanged value), must not report a clear as a bdsChange, and must clear the list selection when value has no mounted option; the parent owns the field text and the clear events."
---

# `bds-select` in `managed` mode: the parent owns the field text and the selection state

`bds-search-bar` is the only component that renders `<bds-select managed>` (grep `<bds-select` for `managed`; `bds-pagination`'s items-per-page and `bds-date-picker`'s time selectors are unmanaged). Two rules hold in managed mode, both established in EOA-19597.

**1. Never write the field text.** Neither an option's label (`loadValue`) nor a reset (`resetValueField`) may call `setAttribute('value', …)` on the slotted `bds-text-field`. `resetValueField()` early-returns when `managed`; `loadValue` only writes `valueString` when not managed.

Why this is not cosmetic: the parent renders the field text itself. If the child writes the *same* text the parent's vdom already rendered, Stencil sees no change and never re-patches; if it writes nothing or `''`, the field goes blank while the parent's committed `value` stands, and the parent's identical `fieldText` still prevents a re-patch. Observed as "type free text, Tab away → field blank, `value` committed" (`bds-search-bar` items mode, T31). The same path runs on popover close (`onAfterHide`) and Escape-from-item.

**2. Clear the selection when `value` has no mounted option.** `loadValue()`'s single-select `option === null` branch must set `valueString = ''` *and* clear the list selection — `void this.bdsList.setSelectedValues('').catch(() => undefined)`. The rejection is swallowed deliberately: an unmounted option is a normal state for a windowed list, so warning on it would spam consumers. Otherwise the previously selected item stays highlighted while the committed `value` says otherwise (T25 / PD-01).

**Managed also means no filtering.** `listenField()` returns at `bds-select.tsx:615` when `managed`, before `searcherElement()` — a managed select never filters its items. The host must filter from data; see `stencil-windowed-list-data-ownership.md`.

**3. A clear is the parent's event, but the list reset still belongs to the select.** `listenClearInput()` must not call `setValue('')` when `managed`: `setValue` emits `bdsChange`, the host's `handleSelectChange` runs its *pick* path on it, and one X-clear ends up as two `valueChange` plus a spurious `bdsSearch {value: ''}` (PD-05). Return early — but **not** before `resetChildren()`: that call is what unhides the items and, via `refreshNavigationState()`, reduces the roving tab stop back to one. Dropping it leaves every slotted item on `tabindex="0"` after a filtered clear (multiple tab stops). The committed value still resets without `setValue`, because the host writes `value = ''` and `watchValue → loadValue()` clears the list selection. Keep `resetChildren()` in the managed branch; the host's own `searchOwnData('')`/`applyItemsQuery('')` restores visibility but does not touch tab stops.

**Blast-radius rule.** Any change to these guards must leave the unmanaged path identical in behaviour: run the `bds-select`, `bds-pagination` and `bds-date-picker` specs, then re-check the items-per-page selector and the time selectors in a browser.

**Source:** EOA-19597 T12 revision, T25 (PD-01), T31 and the PD-05 clear fix.
