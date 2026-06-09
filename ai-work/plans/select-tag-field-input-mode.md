---
status: done
---

# `bds-tag-field` `inputMode` prop — Restrict tag creation and enable searchable multiselect

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Two gaps exist when `bds-tag-field` is used as the trigger field inside `bds-select` multiselect:

1. **Free-form tag creation must be blocked.** `bds-tag-field` commits new tags on Enter or comma. When driven by a select list, tags must only come from menu selection — not from typed text.
2. **Searchable multiselect must be supported.** `bds-text-field` supports a `searchable` mode where typing filters the dropdown options. `bds-tag-field` should support the same: typing filters the list but does **not** commit the typed text as a tag.

**Recommendation:** Proposal 3 — `inputMode` enum — covers both requirements in a single prop and avoids impossible boolean combinations.

**Where the change belongs:** `bds-tag-field` and the `bds-select` orchestration layer. `bds-text-field` is already correct.

---

## Files to create / modify

| File | Notes |
|------|-------|
| `src/components/forms/bds-tag-field/types/ITagField.ts` | Add `inputMode: TagFieldInputMode` and export `TagFieldInputMode` type |
| `src/components/forms/bds-tag-field/types/index.ts` | Re-export `TagFieldInputMode` |
| `src/components/forms/bds-tag-field/bds-tag-field.tsx` | Add `inputMode` prop; guard `handleCommit`, `handleBackspace`; set `readOnly` on input; update `classMap` |
| `src/components/forms/bds-select/bds-select.tsx` | Replace `!this.multiselect` guard with a per-branch block; wire `listenFocusInput` / `listenMouseDown` for multiselect+searchable |
| `apps/boreal-docs/src/stories/forms/bds-select/bds-select.stories.ts` | Add `Multiselect` and `MultiselectSearchable` stories — neither exists today |

---

## Implementation tasks

### Task 1 — Add `TagFieldInputMode` type and `inputMode` prop to `bds-tag-field`

**`types/ITagField.ts`**
- Export `type TagFieldInputMode = 'free' | 'constrained' | 'search'`
- Add `inputMode: TagFieldInputMode` to `ITagField`

**`bds-tag-field.tsx`**
- Import `TagFieldInputMode` from `./types`
- New prop: `@Prop() readonly inputMode: TagFieldInputMode = 'free'`
- `classMap`: add `[`${PREFIX}--selectable`]: this.inputMode === 'constrained'`
- Input element: add `readOnly={this.inputMode === 'constrained'}`
- `handleKeyDown`: wrap `handleCommit` call with `if (this.inputMode === 'free')`
- `handleBackspace`: wrap body with `if (this.inputMode === 'free')`
- `handleInput`: no change — always fires (needed for `'search'` filtering)

**Reference:** `bds-text-field.tsx` line 135 (`selectable` prop) and line 435 (`readOnly={this.readOnly || this.selectable}`) for the exact pattern to mirror.

---

### Task 2 — Update `bds-select` to set `inputMode` for multiselect

**`bds-select.tsx` — `loadDefaultTextFieldProps` (line 213)**

Replace:
```ts
if (!this.multiselect) {
  updateElementProp(this.bdsField, 'selectable', !this.searchable);
}
```

With:
```ts
if (this.multiselect) {
  updateElementProp(this.bdsField, 'inputMode', this.searchable ? 'search' : 'constrained');
} else {
  updateElementProp(this.bdsField, 'selectable', !this.searchable);
}
```

**`bds-select.tsx` — `assignListeners` (line 175)**

Extend the `if (this.searchable)` block to also cover the multiselect+searchable case:
```ts
if (this.searchable || (this.multiselect && this.searchable)) {
  addElementListener(this.bdsInput, 'focus', this.listenFocusInput);
  addElementListener(this.el, 'mousedown', this.listenMouseDown);
}
```
(Note: the condition simplifies to just `if (this.searchable)` — no change needed if multiselect searchable uses the same listeners.)

Verify that `listenField` (which calls `searcherElement`) already fires for tag-field input events — it listens on `bdsInput` which `bds-tag-field` emits from `handleInput` via the native `onInput` handler.

---

### Task 3 — Add SCSS for `--selectable` modifier (if not already present)

Check `bds-tag-field.scss` for an existing `bds-tag-field--selectable` rule. If absent, add:
```scss
&--selectable {
  .bds-tag-field__control {
    cursor: pointer;
    caret-color: transparent;
  }
}
```
Mirror the approach in `bds-text-field.scss`.

---

### Task 4 — Add Storybook stories for multiselect

**File:** `apps/boreal-docs/src/stories/forms/bds-select/bds-select.stories.ts`

Neither a `Multiselect` nor a `MultiselectSearchable` story exists today. Both are required for manual verification and for future regression.

Add two new exports following the existing pattern. Each story places a `bds-tag-field` in `slot="field"` with `multiselect` on the `bds-select`:

**`Multiselect`** — `multiselect=true`, `searchable=false`
- `bds-tag-field` with `label`, `placeholder`, `variant`, `disabled`, `error`, `errorMessage`, `validationTiming` forwarded from args
- `bds-list-menu` with the same six grouped options used in `Default`

**`MultiselectSearchable`** — `multiselect=true`, `searchable=true`
- Same structure; demonstrates that typing filters options without creating tags

Also extend `StoryArgs` and `argTypes` with `multiselect: boolean` and `values: string[]` as needed.

---

### Task 5 — Unit tests

Add/update specs in `bds-tag-field.spec.tsx`:

| Test case | Expected behaviour |
|-----------|-------------------|
| `inputMode='constrained'` + press Enter | `handleCommit` not called; no new tag added |
| `inputMode='constrained'` + press comma | Same |
| `inputMode='constrained'` + Backspace on non-empty value list | Last tag NOT removed |
| `inputMode='search'` + press Enter | No new tag added |
| `inputMode='search'` + Backspace | Last tag NOT removed |
| `inputMode='free'` (default) | All existing tag-creation tests pass unchanged |

---

## Verification

1. Run the unit test suite: `pnpm --filter boreal-web-components test`
2. In Storybook, open the `bds-select` **`Multiselect`** story and confirm:
   - Typing in the tag-field input is blocked (no characters appear, `readOnly` applied)
   - Enter key does not create a rogue tag
   - Backspace does not remove the last tag
   - Selecting an item from the list still adds it as a tag correctly
3. In Storybook, open the `bds-select` **`MultiselectSearchable`** story and confirm:
   - Typing filters the dropdown list
   - Enter key does not commit the typed text as a new tag
   - Selecting a filtered item from the list adds it as a tag
   - Clearing the input resets the visible list items
4. Open the standalone `bds-tag-field` story and confirm default `inputMode='free'` behaviour is unchanged (tags created on Enter/comma, Backspace removes last).
