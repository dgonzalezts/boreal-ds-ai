# BUG-003: `bds-select[multiselect]` — `max-tags` limit on slotted `bds-tag-field` is not enforced for list selections

**Severity:** High
**Priority:** P1
**Type:** Functional
**Status:** Fixed (2026-06-11 — enforcement guard + derived disable layer in `bds-select`; composite-scoped input persistence, overflow derivation, and aria-live at-limit message in `bds-tag-field`; verified in Storybook via Playwright)
**Component:** `bds-select` (multiselect composition with `bds-tag-field`)
**Discovered during:** QA session on story `forms-select--combining-tag-field-attributes` (2026-06-11)
**Affects:** All consumers of `bds-select multiselect` that set `max-tags` on the slotted `bds-tag-field`

---

## Environment

- **Components:**
  - `bds-select` (`packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`)
  - `bds-tag-field` (`packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx`)
- **Story:** `Combining TagField Attributes` (Storybook — Forms → Select, `bds-select multiselect searchable` + `bds-tag-field max-tags="3" max-visible-tags="2"`)
- **Browser:** Chrome (latest stable, via Playwright MCP)
- **URL:** `http://localhost:6006/?path=/docs/forms-select--overview#combining-tagfield-attributes`

---

## Description

In multiselect mode, `bds-select` lets the user check an unlimited number of options in the list menu even when the slotted `bds-tag-field` declares `max-tags="3"`. The limit is only _flagged_ after the fact (error message, red border, `4/3` counter) — it is never _enforced_. The component documentation states that selection limits "must be configured through the `max-tags` … properties exposed by `<bds-tag-field>`", so consumers reasonably expect the composition to honour it.

All over-limit values are real state: they populate `bds-select.value`, render as hidden `<input>` elements, and would be submitted with a form (FACE validity is the only safety net blocking native submission).

---

## Steps to Reproduce

1. Open Storybook → Forms → Select → docs section **Combining TagField Attributes** (or story `forms-select--combining-tag-field-attributes`)
2. Click the field — dropdown opens with 6 options in 2 groups
3. Check `Option 1`, `Option 2`, `Option 3` — counter shows `3/3`, badge shows `3` (limit reached)
4. Click `Option 4`
5. Click `Option 5`

---

## Expected Behaviour

At step 4 the click on `Option 4` is rejected: the checkbox does not check, `bds-select.value` stays at 3 entries, counter stays `3/3`, no error state appears.

Full behavioural specification for the `maxTags` contract in the composition (note: `bds-list-menu` has no max-selection concept of its own — `handleMultipleSelection`, `bds-list-menu.tsx:208`, appends unconditionally — so `bds-select` must orchestrate this, as it already does for `selectionMode`/`checkable` in `loadDefaultListMenuProps`):

**A. While the limit is reached (`value.length === maxTags`):**

1. Selected items stay checked and stay interactive — unchecking one must always be possible to free a slot.
2. All _unselected_, non-label items are disabled (`disabled` attribute → `aria-disabled`, excluded from the keyboard controller's roving tabindex, which already filters `:not([disabled])` at `bds-list-menu.tsx:155`). Clicking them produces no state change and no events.
3. No error state appears from list interaction — the limit can never be exceeded this way, so "Maximum of 3 tags allowed." never renders. The counter caps at `3/3`.
4. The "Select All" control (`selectControls`) is disabled or hidden when `maxTags` is smaller than the number of selectable options; it must never select past the limit (`handleToggleSelect`, `bds-list-menu.tsx:267`, currently would).
5. Opening the dropdown while already at the limit shows items in their disabled state from the start.
6. The search input remains rendered and functional (filtering still works); the user can still inspect the list and their selections.
7. The state is communicated non-visually: the limit being reached is announced to assistive technology (e.g. `aria-live` on the counter/helper region), not only shown as a visual counter.
8. The helper line shows a neutral (non-error) message while at the limit — e.g. "Maximum of 3 selections reached" — explaining why the remaining options are dimmed. It reverts to the regular `helperText` once a slot is freed.
9. A within-limit selection is never hidden behind the overflow chip **in the select composition**: when `entryMode !== 'free'` and `maxVisibleTags` is unset, `effectiveMaxVisible` derives from `maxTags` (not `maxTags - 1`), so all tags of a full valid selection are visible. Scope note: the current `maxTags - 1` derivation (`bds-tag-field.tsx:184-188`) is _documented standalone behaviour_ (argTypes: "`0` derives from `maxTags - 1`", paired with "When the limit is reached the input is hidden") and stays untouched for `free` mode — the `-1` reserves the input's slot, a rationale that disappears in composite mode where the input remains rendered (A6). An explicit `max-visible-tags` always wins, in every mode.

**B. Recovery — selection re-enables when a slot is freed. The disabled state is derived from the current count and recomputed on every change, never a one-way latch.** All of these paths must re-enable previously disabled items immediately:

10. Removing a single tag via its chip ✕.
11. Unchecking a selected item in the list.
12. The clear-all button.
13. Closing the `+N` overflow chip — this removes _several_ tags in one gesture (`handleOverflowClose`, `bds-tag-field.tsx:334`, emits one `bdsTagRemove` per value); the list resync in `bds-select.listenTagRemove` must survive the burst.
14. A parent form reset (`listenFormReset`).
15. Focus is never stranded: if the input was previously removed/restored around the limit, keyboard focus must remain inside the component, not drop to `<body>`.

**C. Programmatic / controlled path:**

16. If a consumer sets `value` with more than `maxTags` entries programmatically, the controlled prop is accepted and flagged by the existing `rangeOverflow` validator (current behaviour, correct) — but the list must still disable further additions.

---

## Actual Behaviour

Steps 4 and 5 both succeed. Final state:

- `bds-select.value === ['option1','option2','option3','option4','option5']`
- `bds-tag-field.value` holds 5 display texts; `maxTags` is still `3`
- 5 hidden `<input>` elements rendered for form submission
- Badge `5`, counter `5/3` in red, error message "Maximum of 3 tags allowed.", red border
- `checkValidity() === false`, host matches `:invalid`

---

## Visual Evidence

- Over-limit selections with popover open: [`assets/bug-maxtags-overflow-5of3.png`](./assets/bug-maxtags-overflow-5of3.png)
- Closed state showing badge `5`, counter `5/3`, error message: [`assets/bug-maxtags-after-escape.png`](./assets/bug-maxtags-after-escape.png)
- Retracted false positive (automation artifact, see Secondary Defects): [`assets/bug-maxtags-outside-click-no-close.png`](./assets/bug-maxtags-outside-click-no-close.png)

Console contained no component errors (only unrelated favicon 404, S3 CORS for icon CSS, and Lit dev-mode warnings).

---

## Root Cause

Neither side of the composition owns the `maxTags` invariant:

- `bds-tag-field` enforces `maxTags` only in `handleCommit()` (`bds-tag-field.tsx:300`) — the typed-entry path. Programmatic `value` assignment bypasses enforcement because `value` is a controlled prop; the `rangeOverflow` validator (`bds-tag-field.tsx:177-180`) only reports the violation after it has happened.
- `bds-select.listenListMenu()` (`bds-select.tsx:357-383`) accepts whatever array the list menu emits, assigns it to `this.value`, and pushes display texts into the tag-field via `syncTagField()` (`bds-select.tsx:301-310`) without ever reading the tag-field's `maxTags`.

---

## Secondary Defects (same investigation)

1. **Search input removed from the DOM at the limit.** `bds-tag-field` swaps the `<input>` for a spacer when `value.length >= maxTags` (`inputHidden`, `bds-tag-field.tsx:401,452`). In `bds-select[searchable]` this silently disables filtering and orphans every listener `bds-select` bound to that input in `assignListeners()` (blur, keydown, focus).
2. **No affordance at the limit:** list items beyond the limit stay enabled and clickable with no visual indication.

**Retracted (2026-06-11):** an earlier draft reported "popover no longer closes on outside click in the over-limit state". Manual testing disproved this — light dismiss works with the input removed; dismissal is native popover behaviour, independent of the input-bound listeners. The automated reproduction was a false positive: `locator('body').click()` targets the centre of the body's layout box, and since the top-layer popover contributes no body height, the synthetic click landed inside the component rather than outside. `assets/bug-maxtags-outside-click-no-close.png` records the false positive.

---

## Impact

- **Data integrity:** Forms can carry more values than the declared maximum; only consumers that call `checkValidity()`/native submission are protected.
- **UX:** The user is shown an error for an action the component itself allowed, and must manually remove tags to recover.
- **Searchable mode:** Filtering breaks entirely once the limit is reached (input removed).

---

## Suggested Fix Direction

Two complementary layers, plus one tag-field change:

1. **Invariant guard** — in `bds-select.listenListMenu()` (multiselect branch), read `maxTags` from the slotted tag-field; when `nextValues.length` exceeds it, reject the selection and revert the list state with `this.bdsList.setSelectedValues(this.value)`. This also protects against keyboard activation, Select All, and any programmatic list event that bypasses disabled styling.
2. **UX layer** — after every value change, `bds-select` derives the at-limit state and toggles `disabled` on unselected, non-label list items (and on the Select All control). Derived from the current count on each change — never latched — so every recovery path (chip ✕, uncheck, clear-all, `+N` overflow close, form reset) re-enables automatically.
3. **Tag-field** — three changes:
   - Do not remove the `<input>` from the DOM when `entryMode !== 'free'` (`inputHidden`, `bds-tag-field.tsx:401,452`), so filtering, the select's input-bound listeners, and focus survive at the limit.
   - In the `effectiveMaxVisible` derivation (`bds-tag-field.tsx:184-188`), derive `maxTags` instead of `maxTags - 1` **only when `entryMode !== 'free'`**, so a full valid selection in the select composition shows all its tags. Standalone `free` mode keeps the documented `maxTags - 1` derivation and input-hiding pair.
   - When `value.length === maxTags`, render a neutral at-limit helper message (e.g. "Maximum of 3 selections reached") in place of `helperText`, in an `aria-live` region; revert when below the limit.

See plan tasks 2–3.

---

## Verification (post-fix)

Limit enforcement:

1. Open the story, select 3 options — counter `3/3`, no error state, **all 3 tags visible** (no `+1` overflow chip with `max-visible-tags` unset — composite-mode derivation), helper line shows the neutral "Maximum of 3 selections reached" message. Control test: the standalone `WithMaxTags` and `WithOverflow` tag-field stories keep their current documented behaviour.
2. Click a 4th option — **Expected:** checkbox never checks, counter stays `3/3`, badge `3`, no error message, `bdsChange`/`valueChange` do not fire
3. Confirm the 3 unselected options render disabled (`aria-disabled`, skipped by Arrow-key navigation) while the 3 selected ones remain interactive
4. Attempt selection via keyboard (`Enter` on a disabled item) — **Expected:** rejected the same as click
5. Close and reopen the dropdown while at the limit — **Expected:** items already disabled on open

Recovery (each path must re-enable disabled items immediately):

6. Remove one tag via its chip ✕ → counter `2/3`, all items selectable again, helper line reverts to the regular `helperText`; re-select a different option to confirm
7. Uncheck a selected item in the list → same result
8. Reach the limit, close the `+N` overflow chip → all hidden tags removed, list resynced (unchecked), items re-enabled
9. Clear-all button → counter `0/3`, everything re-enabled
10. Submit-context: form reset → same as 9

Composite integrity at the limit:

11. Search input still present; typing filters the list
12. Outside click closes the popover (regression check only — confirmed working pre-fix by manual test)
13. Keyboard focus stays inside the component throughout (never drops to `<body>`)
14. Screen reader (VoiceOver spot check): reaching the limit is announced; disabled items are announced as dimmed/unavailable

Regression guard: `bdsChange`/`valueChange` fire exactly once per accepted selection (BUG-001) and the popover close-on-selection behaviour for single select is unaffected (BUG-002).

---

## Related

- Story source: `apps/boreal-docs` — Forms / Select → Combining TagField Attributes
- BUG-001, BUG-002: previous `bds-select` event/popover fixes — re-verify single-fire events and close-on-selection are unaffected by the fix
