# Failure-Mode Catalog — `bds-select`

Audited against `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx` as of 2026-10-23 (working tree contains the EOA-19597 Task 12 changes to `loadValue()` and `@Watch('valueString')`). Rows are derived from reading the component source and its pre-existing spec suite (`__test__/bds-select.{basics,a11y,variants,events,keyboard,slots}.spec.ts`), not from a plan's stated test list.

Scope of this first audit: single-select `loadValue()` text resolution, the `valueString` → field `value` write path, and `managed` mode ownership of the field text. Multiselect paths, keyboard navigation, popover wiring, and flag variant are covered by the existing suite and were only read for cross-checking — failure modes found there would be a separate audit pass.

---

### FM-01 | `value` pointing at an unmounted option leaves a stale `valueString`

- **ID:** FM-01
- **Category:** null-empty
- **Risk:** consumer/state — the component's `valueString` state no longer describes `value`; any later read of it (focus/blur restore via `resetValueField()`, `bds-select` internal reads) resolves a label for an option that is not the committed value.
- **Input that reveals it:** load with `value="1"` (mounted option resolves the label `Option 1`), then set `value` to a value with no matching `bds-list-menu-item`.
- **Observed current behavior:** `loadValue()` sets `this.valueString = ''` when `this.bdsList.querySelector('bds-list-menu-item[value="…"]')` returns `null` (`bds-select.tsx:766-769`).
- **Recommended contract:** `valueString` is empty whenever `value` does not resolve to a mounted option.
- **Contract status:** confirmed
- **Why it matters:** `valueString` is the select's own record of what the field shows; leaving it pointing at a previous option is the bug the change fixes.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should empty valueString without rewriting the field when value has no mounted option`

---

### FM-02 | Clearing `valueString` blanks the field while a value is committed

- **ID:** FM-02
- **Category:** null-empty
- **Risk:** visual — a non-empty `value` that resolves to no mounted option clears `valueString` (FM-01); without a guard the watcher writes `''` into the field and the trigger goes blank even though a value is committed and submitted.
- **Input that reveals it:** with `value` non-empty, drive `valueString` to `''`.
- **Observed current behavior:** `watchValueString()` returns before `updateElementAttr(this.bdsField, 'value', newValue)` when `newValue === ''` and `hasValue` is true (`bds-select.tsx:117-122`); `hasValue` is `value.length > 0` for an array, `value !== ''` for a string.
- **Recommended contract:** clearing `valueString` never writes `''` into the field while `value` is committed (string form or non-empty array form).
- **Contract status:** confirmed
- **Why it matters:** the owner of `value` is the party that can still resolve its label; the select must not destroy the text it cannot reconstruct.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should not blank the field when valueString is cleared while a committed value is a string`; `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should not blank the field when valueString is cleared while a committed value is a non-empty array`

---

### FM-03 | The FM-02 guard over-filters and the field can never be cleared

- **ID:** FM-03
- **Category:** null-empty
- **Risk:** visual/functional — if the guard swallowed every `''` write, clearing the select (clear button, form reset, blur with no value) would leave stale text in the trigger while no value is committed.
- **Input that reveals it:** with no committed `value`, drive `valueString` to `''`.
- **Observed current behavior:** the early return is conditional on `hasValue` (`bds-select.tsx:119-120`); with `value === ''` (or `[]`) the write still happens.
- **Recommended contract:** `valueString === ''` is still written to the field when no value is committed.
- **Contract status:** confirmed
- **Why it matters:** it is the guard against FM-02 becoming an inability to clear.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should clear the field when valueString is cleared and no value is committed`; the clear-button and form-reset paths are already covered by `src/components/forms/bds-select/__test__/bds-select.events.spec.ts::Should clear the selection and text when clear button is clicked` and `src/components/forms/bds-select/__test__/bds-select.events.spec.ts::Should clear the value and deselect the option when the parent form is reset (single select)`

---

### FM-04 | `managed` mode overwrites the parent-owned field text with an option label

- **ID:** FM-04
- **Category:** component-contract-bypass
- **Risk:** visual/functional — in `managed` mode the wrapper owns the field text (it decides between the label and the user's typed filter text). If the select writes the option label after `setSelectedValues`, it clobbers the parent's text and the two owners fight.
- **Input that reveals it:** `managed` select loading a `value` that resolves to a mounted option.
- **Observed current behavior:** `loadValue()` writes `this.valueString = text` only `if (!this.managed)` (`bds-select.tsx:777`); with `managed` the `valueString` state stays `''` and the watcher never writes the field.
- **Recommended contract:** a `managed` select never writes an option label into the field.
- **Contract status:** confirmed
- **Why it matters:** documented on the `managed` prop itself (`bds-select.tsx:63-68`).
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should keep valueString empty and leave the field text untouched in managed mode`

---

### FM-05 | `managed` mode skips the selection side effects along with the label write

- **ID:** FM-05
- **Category:** component-contract-bypass
- **Risk:** functional — the natural "fix" for FM-04 is an early `return` inside the `.then()`, which would also drop `setSelectedValues`' visible result and `scrollIntoView()`/`loadFlag()`.
- **Input that reveals it:** change `value` to another mounted option in `managed` mode.
- **Observed current behavior:** the managed check guards only the `valueString` assignment (`bds-select.tsx:777`); `option.scrollIntoView({ block: 'nearest' })` and the `variant === 'flag'` `loadFlag()` call still run (`bds-select.tsx:778-779`), and `setSelectedValues` is called before the `.then()` (`bds-select.tsx:771-772`).
- **Recommended contract:** `managed` still marks the matching option selected and still scrolls it into view.
- **Contract status:** confirmed
- **Why it matters:** `managed` changes text ownership only, not selection behaviour.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should still select and scroll the option into view in managed mode`

---

### FM-06 | Non-managed mode stops writing the option label (regression on the default path)

- **ID:** FM-06
- **Category:** equivalence
- **Risk:** visual — the default (`managed === false`) path is what every consumer without a wrapper uses; gating the write must not disable it there.
- **Input that reveals it:** `managed` absent, `value` resolves to a mounted option.
- **Observed current behavior:** `if (!this.managed)` is true for the default, so `valueString` becomes the option text and the watcher writes it to the field (`bds-select.tsx:777`, `:121`).
- **Recommended contract:** the default path writes the option text into `valueString` and the field.
- **Contract status:** confirmed
- **Why it matters:** regression guard for FM-04's fix.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should write the option text into the field in non-managed mode`; also pre-existing `src/components/forms/bds-select/__test__/bds-select.events.spec.ts::Should change the option when value prop is updated`

---

### FM-07 | `managed` mode blanks the field when the value field resets on blur or popover close

- **ID:** FM-07
- **Category:** component-contract-bypass
- **Risk:** visual/functional — in `managed` mode the parent owns the field text, and it re-renders the field on its own schedule. `resetValueField()` writing `''` (its no-value branch) between the parent's commit and its next render leaves a blank field while `value` is committed, and the parent's unchanged `fieldText` never re-patches it.
- **Input that reveals it:** `managed` select whose own `value` is still empty, with the field already showing parent-owned text, then `resetValueField()` — reached from `listenBlurInput` and the popover's `onAfterHide`.
- **Observed current behavior:** `resetValueField()` returns immediately when `this.managed` (`bds-select.tsx:690-692`); selection marking and `valueString` handling are unchanged by the guard.
- **Recommended contract:** a `managed` select never writes field text at all — neither an option label nor a reset — on blur, popover close, or Escape from an item. Non-managed behaviour is unchanged: it still blanks on an empty value and still restores `valueString` when one is set.
- **Contract status:** confirmed
- **Why it matters:** it is the root cause of the visible defect logged as `bds-search-bar`'s PD-02 (plan T31); the sibling of FM-04 on the reset path.
- **Covered by:** `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should leave the field text untouched when a managed select resets an empty value`; unmanaged regression guards — `…bds-select.basics.spec.ts::Should blank the field when an unmanaged select resets an empty value`, `…bds-select.basics.spec.ts::Should restore the option label when an unmanaged select resets a committed value`

---

### PD-01 | `value` resolving to no mounted option leaves the previously selected item highlighted

- **ID:** PD-01
- **Category:** component-contract-bypass
- **Risk:** a11y/visual — `value` (and the hidden input that is submitted) now points at an option that is not in the list, while the list still renders the *previous* option with `aria-selected="true"` and `bds-list-item--selected`. Screen-reader users are told the old option is the current selection while the form submits a different value.
- **Input that reveals it:** load with `value="1"` (option `1` mounted and selected), then set `value` to a value with no matching item.
- **Observed current behavior:** the `option === null` branch clears `valueString` and returns *before* calling `bdsList.setSelectedValues(...)` (`bds-select.tsx:766-769`), so the item previously marked selected keeps its `selected` prop. `loadValue()` only calls `setSelectedValues` on the resolved-option and empty-value paths (`bds-select.tsx:757-759`, `:771-772`).
- **Recommended contract:** open question. Two coherent options: (i) clear the list selection (`setSelectedValues('')`) in the null branch so the list agrees with `value`; or (ii) leave it, on the theory that an unmounted option means the list is stale and the owner of `value` will re-render it.
- **Contract status:** pending-decision
- **Why it matters:** it decides whether the list is allowed to disagree with the submitted `value`, and it is decided by the same code path as FM-01. Not tested — awaiting a ruling.
- **Covered by:** —

---

### PD-02 | Clearing `valueString` is the only way to blank field text while `value` is committed

- **ID:** PD-02
- **Category:** component-contract-bypass
- **Risk:** consumer ergonomics — after FM-02, a parent that wants the trigger blank while a `value` is still committed (e.g. showing placeholder text until the popover is opened) has no supported way to ask for it: the watcher refuses `''`, and `resetValueField()` restores `valueString` on the next blur/hide.
- **Input that reveals it:** `value="1"`, set `valueString = ''`, then blur/hide the popover.
- **Observed current behavior:** the watcher early-returns (`bds-select.tsx:119-120`) and `resetValueField()` writes `this.valueString` back into the field whenever it is non-empty (`bds-select.tsx:685-691`).
- **Recommended contract:** open question — is "field text is blank while `value` is committed" a supported state, or must a consumer clear `value` first?
- **Contract status:** pending-decision
- **Why it matters:** it bounds what FM-02 is allowed to forbid. Not tested — awaiting a ruling.
- **Covered by:** —
