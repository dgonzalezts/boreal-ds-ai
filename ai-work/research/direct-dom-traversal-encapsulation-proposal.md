# Direct DOM Traversal & Encapsulation — Proposal

**Date:** 2026-06-26
**Source finding:** Memory-Guided Review §3, `2026-06-26-commit-67019ad0-head-review.md`
**Scope:** `bds-text-field`, `bds-search-bar`, `bds-select`

---

## Problem

Both `bds-search-bar` and `bds-select` reach inside `bds-text-field` to access its
internal DOM directly. Because `bds-text-field` is a light-DOM component the queries work
at runtime, but they create hard coupling to the internal template. Any structural change
to `bds-text-field` (renaming a class, wrapping the input, adding a shadow root) silently
breaks every parent that traverses it.

### `bds-search-bar` — traversal sites

| Getter / call site | Pierces into | Used for |
|----|----|----|
| `bdsInputEl` → `bdsFieldEl?.querySelector('input')` | `<input>` inside `bds-text-field` | `focus()`, `blur()`, `aria-label`, `value` attr, `keydown` listener |
| `bdsTriggerBtnEl` → `bdsFieldEl?.querySelector('bds-button')` | `<bds-button>` inside `bds-text-field` | `focus` listener for open-on-tab |
| `bdsField` → `this.el.querySelector('bds-text-field')` | host element | `iconRight` prop setter |

The `bdsFieldEl` getter chains through `bdsSelectEl`, so it returns `null` in `mode="search"`
(no `<bds-select>` wrapper). This is what causes the **SEARCH mode keydown bug** confirmed
in the code review: `addElementListener(null, 'keydown', ...)` is a no-op, so pressing Enter
never fires `emitSearch`.

### `bds-select` — traversal sites

| Getter | Pierces into | Used for |
|----|----|---|
| `bdsInput` → `bdsField.querySelector('input')` | `<input>` | Popover listen-element, searcherElement, focus |
| `bdsInputContainer` → `bdsField.querySelector('.bds-text-field__container')` | Internal container class | Popover anchor positioning |
| `bdsInputContainer` → `bdsField.querySelector('.bds-tag-field__container')` | Internal container class | Same, multiselect variant |
| `bdsFlag` → `bdsField.querySelector('bds-flag')` | `<bds-flag>` child | Flag variant text update |

---

## Proposed Solution

Add a minimal set of public methods and props to `bds-text-field` (and `bds-tag-field`)
that give parents everything they need **without** crossing the component boundary.

### 1. Add `focus()` and `blur()` public methods to `bds-text-field`

`bds-text-field` already calls `this.el.querySelector<HTMLInputElement>('input')?.focus()`
internally (lines 319, 408). The fix is to expose that as a `@Method`.

```ts
// bds-text-field.tsx — add after reportValidity()
@Method()
async focus(): Promise<void> {
  (this.el as HTMLElement).querySelector<HTMLInputElement>('input')?.focus();
}

@Method()
async blur(): Promise<void> {
  (this.el as HTMLElement).querySelector<HTMLInputElement>('input')?.blur();
}
```

**Replaces in `bds-search-bar`:**
```ts
// Before
this.bdsInputEl?.focus();
this.bdsInputEl?.blur();

// After
void this.bdsField?.focus();
void this.bdsField?.blur();
```

`bdsField` already queries `this.el.querySelector('bds-text-field')` directly and works in
both `list` and `search` modes — no getter change needed.

---

### 2. Add `inputAriaLabel` prop to `bds-text-field`

`syncInputAccessibility` sets `aria-label` directly on the inner `<input>` because
`bds-text-field` has no prop for a standalone `aria-label` on the input element (it uses
`aria-labelledby` when `label` is provided, which `bds-search-bar` sets to `""`).

```ts
// bds-text-field.tsx
/** Overrides the accessible label on the inner <input> when no visible label is used. */
@Prop() readonly inputAriaLabel: string = '';
```

In the render function, update the `<input>` binding:

```tsx
// bds-text-field.tsx render — existing input element
<input
  ...
  aria-label={this.inputAriaLabel !== '' ? this.inputAriaLabel : undefined}
  aria-labelledby={this.label !== '' ? labelId : undefined}
  ...
/>
```

**Replaces in `bds-search-bar`:**
```ts
// Before — syncInputAccessibility
updateElementAttr(this.bdsInputEl, 'aria-label', this.placeholder || this.searchButtonLabel);

// After
updateElementProp(this.bdsField, 'inputAriaLabel', this.placeholder || this.searchButtonLabel);
```

The `@Watch('placeholder')` and `@Watch('searchButtonLabel')` watchers already call
`syncInputAccessibility`, so the trigger chain is unchanged.

---

### 3. Replace keydown listener target with the `bds-text-field` host

Because `bds-text-field` is light DOM, a `keydown` event originating on the inner `<input>`
**already bubbles** through the `bds-text-field` host element. Parents can attach their
listener to the host instead of the input.

```ts
// bds-search-bar.tsx — assignListeners / removeListeners

// Before
addElementListener(this.bdsInputEl, 'keydown', this.listenKeydown);
removeElementListener(this.bdsInputEl, 'keydown', this.listenKeydown);

// After
addElementListener(this.bdsField, 'keydown', this.listenKeydown);
removeElementListener(this.bdsField, 'keydown', this.listenKeydown);
```

`bdsField` (`this.el.querySelector('bds-text-field')`) is available in both `list` and
`search` modes, fixing the SEARCH mode keydown regression at the same time.

---

### 4. Replace trigger-button focus listener with `bdsFocus` event bubbling

`bds-search-bar` attaches a `focus` listener directly to the `<bds-button>` inside
`bds-text-field`. `bds-button` already emits a `bdsFocus` custom event when focused.
Custom events do bubble; the parent can listen on the `bdsField` host or on the component
host itself.

```ts
// bds-search-bar.tsx — assignListeners / removeListeners

// Before
addElementListener(this.bdsTriggerBtnEl, 'focus', this.handleTriggerFocus);
removeElementListener(this.bdsTriggerBtnEl, 'focus', this.handleTriggerFocus);

// After — listen for bds-button's bdsFocus which bubbles to bds-text-field
addElementListener(this.bdsField, 'bdsFocus', this.handleTriggerFocus);
removeElementListener(this.bdsField, 'bdsFocus', this.handleTriggerFocus);
```

> **Note:** Verify that `bdsFocus` from `bds-button` doesn't conflict with `bdsFocus` from
> `bds-text-field` itself (which also emits `bdsFocus` when the input is focused). If both
> fire, `handleTriggerFocus` would run twice. An alternative is to scope the check inside
> the handler by inspecting `e.target`:
>
> ```ts
> private handleTriggerFocus = (e: CustomEvent): void => {
>   if ((e.target as HTMLElement)?.tagName !== 'BDS-BUTTON') return;
>   if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
>     void this.openSearchBar();
>   }
> };
> ```

---

### 5. Expose an anchor contract for `bds-select`

`bds-select` accesses `.bds-text-field__container` and `.bds-tag-field__container` to feed
an element reference to `bds-popover` as an anchor. This is the tightest coupling in the
set because it relies on internal CSS class names.

Two possible approaches:

**Option A — Expose `getAnchorElement()` on `bds-text-field` and `bds-tag-field`:**

```ts
// bds-text-field.tsx
@Method()
async getAnchorElement(): Promise<HTMLElement | null> {
  return (this.el as HTMLElement).querySelector<HTMLElement>('.bds-text-field__container');
}
```

```ts
// bds-select.tsx — assignPopoverListeners()
// Before
const container = (this.bdsField as HTMLElement).querySelector('.bds-text-field__container');
void this.bdsPopover?.setAnchorElement(container as HTMLElement);

// After
const container = await (this.bdsField as HTMLBdsTextFieldElement).getAnchorElement();
void this.bdsPopover?.setAnchorElement(container as HTMLElement);
```

**Option B — Make `bds-popover` accept the host element as anchor directly** by using
`getBoundingClientRect()` on the host. This eliminates the need for any internal element
reference and is the deeper fix (the popover positions relative to the field's own bounding
box, not an inner wrapper). This requires a change to `bds-popover`'s anchor contract and
is a larger scope.

*Recommendation: start with Option A as a non-breaking incremental step.*

---

## Migration Path

The changes to `bds-text-field` are **additive** (new methods and one new optional prop)
and require no breaking change. The refactors in `bds-search-bar` and `bds-select` are
internal-only; no public API changes.

Suggested order:

1. Add `focus()`, `blur()`, `inputAriaLabel`, `getAnchorElement()` to `bds-text-field` and `bds-tag-field`
2. Refactor `bds-search-bar` — eliminates the SEARCH mode keydown bug as a side effect
3. Refactor `bds-select` — largest changeset; update tests for `bdsInput` getter removal
4. Delete the now-dead `bdsInputEl`, `bdsFieldEl`, `bdsTriggerBtnEl` getters from `bds-search-bar`
5. Delete `bdsInput`, `bdsInputContainer` getters from `bds-select`

---

## Impact on SEARCH Mode Bug

The SEARCH mode keydown bug (finding #3 in the 2026-06-26 code review) is a **direct
consequence** of `bdsFieldEl` routing through `bdsSelectEl`. After step 2 above:

- `addElementListener(this.bdsField, 'keydown', ...)` uses the `bdsField` getter which
  queries `this.el.querySelector('bds-text-field')` — works in both modes
- The listener fires for any `keydown` that bubbles from inside the text field, including
  Enter from the `<input>`, in all modes

No separate bug fix is needed; it falls out of the encapsulation refactor.
