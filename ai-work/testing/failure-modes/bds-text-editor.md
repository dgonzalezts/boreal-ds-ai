# Failure-Mode Catalog — bds-text-editor

Created 2026-11-19 with the component specs (EOA-18739 T8), audited against `bds-text-editor.tsx` at `14e14297`, not against the plan's list. The core helper specs (serializer, counter, plugins) predate this file and are not re-audited here.

Spec files: `packages/boreal-web-components/src/components/forms/bds-text-editor/__test__/bds-text-editor.{basics,a11y,events,form,validation,toolbar,labels,insertion}.spec.ts`.

---

### FM-TE-01 | Hiding the link tool after it rendered threw from `componentDidRender`

- **ID:** FM-TE-01
- **Category:** race-timing
- **Risk:** every runtime `readOnly = true` (or a `toolbar` change that drops `link`) logged `TypeError: Cannot read properties of null (reading 'setAnchorElement')` and left the render lifecycle in an error state
- **Input that reveals it:** mount with the default toolbar, then set `readOnly = true` (or `toolbar = 'fields'`, `''`, `null`)
- **Observed current behavior:** `syncLinkAnchor` now returns early when `linkButton` or `linkPopover` is `undefined` or `null` (Stencil calls `ref` callbacks with `null` when the toolbar unmounts); fixed after the audit
- **Recommended contract:** toggling `readOnly` or `toolbar` after mount never throws and hides the toolbar or the dropped tool; showing the toolbar again anchors the popover to the new link tool
- **Contract status:** confirmed
- **Why it matters:** edit/view mode toggles are a normal consumer flow; same bug class as `stencil-ref-null-on-removal-defeats-undefined-guard`
- **Covered by:** `__test__/bds-text-editor.basics.spec.ts::'hides the toolbar without throwing when read-only is set after mount'`, `::'hides the link tool without throwing when the toolbar prop drops it after mount'`, `::'hides the toolbar without throwing when the toolbar prop is emptied after mount'`, `::'hides the toolbar without throwing when toolbar becomes %s after mount'`, `::'shows the toolbar again after read-only is turned off'`, `::'anchors the link popover to the new link tool after the toolbar is shown again'`

### FM-TE-02 | `valueChange` for values set by the app

- **ID:** FM-TE-02
- **Category:** equivalence
- **Risk:** a Vue `v-model` or a consumer listener must stay in sync with every value change, while `bdsInput` and `bdsChange` must stay user-only
- **Input that reveals it:** `el.value = 'x'` after mount; `formResetCallback()`; fields arriving after the value
- **Observed current behavior:** `onValueChange` always ends in `this.valueChange.emit(normalized)`; `bdsInput` and `bdsChange` are not emitted for app-set values
- **Recommended contract:** `valueChange` is the wrapper-sync event and fires once per actual value change, including app-set values (with the normalised payload, `''` for nullish) and form resets; it does not fire when the value is unchanged (same value set, value equal to what the user just typed, reset at the default, `fields` arriving after the value). `bdsInput` and `bdsChange` never fire for app-set values.
- **Contract status:** confirmed (ruled by the user)
- **Why it matters:** wrappers must receive their own writes back as the sync signal; consumers listening to `bdsInput`/`bdsChange` must only see user edits
- **Covered by:** `__test__/bds-text-editor.events.spec.ts` describe block "valueChange for values set by the app" (all tests) and "values set by the app"

### FM-TE-03 | `aria-invalid` while the visual error is suppressed

- **ID:** FM-TE-03
- **Category:** component-contract-bypass
- **Risk:** a disabled or read-only editor with `error` or a failed validation announced itself as invalid with no visual error
- **Input that reveals it:** `error = true` with `disabled = true` or `readOnly = true`
- **Observed current behavior:** `buildEditableAttributes` now sets `aria-invalid` only when `state.effectiveError && this.isEditable`, matching `showError`; fixed after the audit
- **Recommended contract:** `aria-invalid="true"` is present only while the editor is editable (not disabled, not read-only) and `error` is true or the last validation failed; toggling `disabled`, `readOnly` or the form disabled state at runtime adds and removes it; `aria-disabled` and `aria-readonly` are unaffected
- **Contract status:** confirmed (ruled by the user)
- **Why it matters:** the accessible state must match the visual state
- **Covered by:** `__test__/bds-text-editor.a11y.spec.ts` describe block "invalid state while not editable" (all tests) and "state attributes"

### FM-TE-04 | `insertText` with an empty string or a non-string

- **ID:** FM-TE-04
- **Category:** null-empty
- **Risk:** consumers calling `insertText('')` or `insertText(undefined)` from a slotted tool
- **Observed current behavior:** `insertPlainText` returns `false` for non-strings; `buildTextInsertion` returns `null` for `''` so the method resolves `false`
- **Recommended contract:** `insertText('')` and any non-string resolve `false`, insert nothing, leave a selection untouched, emit no `bdsInput` or `valueChange`, move no focus and never throw; a later valid insertion still works
- **Contract status:** confirmed (ruled by the user)
- **Covered by:** `__test__/bds-text-editor.toolbar.spec.ts` describe block "insertText method" ('resolves false and inserts nothing for an empty string', 'keeps the selected text when the inserted string is empty', 'does not emit input events or move focus for an empty string', 'resolves false without throwing and inserts nothing for the non-string %j', 'does not emit input events or move focus for a non-string', 'still inserts the next valid text after an empty string was rejected'); helper level: `__test__/bds-text-editor.insertion.spec.ts::'returns null for an empty string'`

### FM-TE-05 | Repeated and nullish `toolbar` ids

- **ID:** FM-TE-05
- **Category:** equivalence
- **Observed current behavior:** `parseToolbar` keeps one copy of a repeated tool, keeps repeated dividers (collapsed later) and reads a nullish `toolbar` as `''`
- **Recommended contract:** a repeated tool id renders one tool (`link,link` renders one Link and one popover, `fields,fields` one Fields dropdown) with no warning; a `null` `toolbar`, or `null`/`undefined` set after mount, is treated as `''` (no toolbar unless slotted content, no warning, no throw). An `undefined` at creation is an unset Stencil prop and keeps the default `emoji,link`; that is framework behaviour, not part of this contract.
- **Contract status:** confirmed (ruled by the user)
- **Covered by:** `__test__/bds-text-editor.basics.spec.ts` describe block "toolbar parsing" (the repeated-id rows of the parsing table, 'renders a single link tool and a single popover when the link id is repeated', 'renders a single Fields tool when the fields id is repeated', 'does not warn when a tool id is repeated', 'renders no toolbar when toolbar is null', 'shows only the slotted tool when toolbar is null', 'does not warn when toolbar is null', 'hides the toolbar without throwing when toolbar becomes %s after mount')

### FM-TE-06 | Link submit while the editor became disabled or read-only with the popover open

- **ID:** FM-TE-06
- **Category:** component-contract-bypass
- **Observed current behavior:** `submitLink` skips the insert when not editable, inserts nothing, shows no error and closes the popover
- **Recommended contract:** if the editor becomes disabled or read-only while the link popover is open (or while the URL is being sanitised), submitting inserts nothing, shows no error, moves no focus and closes the popover (a read-only editor has already unmounted it); the submit guard is released so a later submit works
- **Contract status:** confirmed (ruled by the user)
- **Covered by:** `__test__/bds-text-editor.toolbar.spec.ts` describe block "link submission after the editor stops being editable" (all tests)

### FM-TE-07 | An app-set value while focused counts as a change on blur

- **ID:** FM-TE-07
- **Category:** race-timing
- **Observed current behavior:** `commitBlur` compares `value` with `_valueAtFocus`, so `el.value = 'x'` between focus and blur emits `bdsChange`
- **Recommended contract:** a value set by the app between focus and blur counts as a change on blur: `bdsChange` fires once with the current value (same comparison as `bds-text-field`); no `bdsChange` fires when the value at blur equals the value at focus, however it got there; each focus takes a fresh baseline
- **Contract status:** confirmed (ruled by the user)
- **Covered by:** `__test__/bds-text-editor.events.spec.ts` describe block "bdsChange for values set between focus and blur" (all tests)

### FM-TE-08 | Duplicated `bds-text-field` and `bds-dropdown` events leaking out of the composite

- **ID:** FM-TE-08
- **Category:** component-contract-bypass
- **Risk:** the URL field's `bdsInput`, `bdsChange`, `bdsFocus`, `bdsBlur`, `bdsValidationChange`, `valueChange` and the dropdown's `bdsChange` reach consumers as editor events
- **Observed current behavior:** each is stopped (`:381-386`, `:455-459`, `:828-842`)
- **Recommended contract:** none of them reach the host
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.toolbar.spec.ts::'does not let %s from the URL field reach the editor listeners'`, `::'does not let the dropdown choice leak out as an editor change event'`

### FM-TE-09 | Blur decided from a null `relatedTarget`

- **ID:** FM-TE-09
- **Category:** race-timing
- **Risk:** spurious `bdsBlur`/`bdsChange`/validation when a field is inserted, the popover closes or focus is handed back
- **Observed current behavior:** `handleFocusOut` (`:395-407`) defers to `settleFocus` after one frame; `focusEditorLater` (`:588-597`) suppresses it while a refocus is pending
- **Recommended contract:** nothing is emitted when focus returns inside the host; one `bdsBlur` after one frame when it really left; nothing after the host is removed; repeated focusouts decide once
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.events.spec.ts` describe blocks "focus leaving without a related target" and "focus returning after an insertion"; `bds-text-editor.validation.spec.ts::'does not validate when focus leaves with no related target and returns'`

### FM-TE-10 | Limit boundary for insertions

- **ID:** FM-TE-10
- **Category:** boundary
- **Observed current behavior:** `fitsWithinLimit` (`insertion.ts:33-38`) accepts a result equal to the limit and any insertion that lowers the count; the Fields options use `length > space`
- **Recommended contract:** at the limit fits, one over does not, over-limit documents accept only reductions; the Fields option is disabled exactly when its length exceeds the space left
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.toolbar.spec.ts` (insertText, insertField, Fields tool options, link insertion) and `bds-text-editor.insertion.spec.ts`

### FM-TE-11 | Nullish and non-array `fields`, nullish `value`

- **ID:** FM-TE-11
- **Category:** null-empty
- **Observed current behavior:** nullish `fields` is `[]` with no warning; any other non-array warns once per change; `null`/`undefined` `value` is `''` at mount and after mount
- **Recommended contract:** as observed (plan T5 research pass)
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.form.spec.ts` describe blocks "nullish values" and "fields"

### FM-TE-12 | Double submit of the link form

- **ID:** FM-TE-12
- **Category:** race-timing
- **Observed current behavior:** `linkSubmitting` blocks a second submit while the sanitiser promise is pending
- **Recommended contract:** one insertion per pending submit; a later submit works
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.toolbar.spec.ts::'inserts a URL only once when Insert is activated twice before the first insertion settles'` and `::'allows a second insertion after the first one settled'`

### FM-TE-13 | Runtime change of `fieldsButton`, `labels` and `fields`

- **ID:** FM-TE-13
- **Category:** equivalence
- **Observed current behavior:** the trigger, the toolbar texts and the chip prefix follow the props after mount; an invalid `fieldsButton` falls back to `icon` with a warning
- **Recommended contract:** as observed (T5, T13)
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.toolbar.spec.ts` "Fields button display", `bds-text-editor.labels.spec.ts` "reactive changes"

### FM-TE-14 | Pointer press state

- **ID:** FM-TE-14
- **Category:** component-contract-bypass
- **Observed current behavior:** `--pressed` is set on a primary press in the editable only while editable, and cleared by window `pointerup`/`pointercancel` and by disconnect, which also removes both window listeners
- **Recommended contract:** as observed (T7 ruling 9)
- **Contract status:** confirmed
- **Covered by:** `bds-text-editor.events.spec.ts` describe block "pressed state"
