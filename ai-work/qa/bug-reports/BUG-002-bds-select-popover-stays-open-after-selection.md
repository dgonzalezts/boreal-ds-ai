# BUG-002: `bds-select` — Popover does not close after item selection

**Severity:** High  
**Priority:** P1  
**Type:** Functional  
**Status:** Fixed  
**Component:** `bds-select`  
**Discovered during:** TC-FUNC-001 / TC-FUNC-002  
**Affects:** All consumers of `bds-select` in all interaction modes (default and searchable)

---

## Environment

- **Component:** `bds-select` (`packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`)
- **Story:** `Default` (Storybook — Forms → bds-select)
- **Browser:** Chrome (latest stable)

---

## Description

Clicking an option inside the `bds-select` dropdown updates the selected value and emits events correctly, but the popover (dropdown list) **remains open**. The user must click outside the component or press `Escape` to dismiss it manually.

This breaks the standard select UX contract: a single-option select closes its dropdown immediately upon selection.

---

## Steps to Reproduce

1. Open Storybook → Forms → bds-select → `Default` story
2. Click the text field — dropdown opens
3. Click any list item (e.g. `Option 3`)

---

## Expected Behaviour

The dropdown list closes immediately after the item is clicked. The text field shows the label of the selected option. Focus returns to the text field.

---

## Actual Behaviour

The dropdown list **stays open** after the item is clicked. The text field value updates correctly and events fire, but the popover does not dismiss until the user clicks outside or navigates away.

---

## Root Cause

`bds-list-menu-item.handleClick` (`bds-list-menu-item.tsx:138`) calls `e.stopPropagation()` before the native click event can bubble further:

```typescript
private handleClick = (e: MouseEvent) => {
  e.stopPropagation();
  // ... emit bdsSelectItem
};
```

`bds-popover` closes on an inside click via its `onClick` handler on `<Host>` (`bds-popover.tsx:345`), which fires only when a click reaches the popover element. Because `stopPropagation` is called at the item level, the click never reaches `bds-popover`. Any `floatingOptions.closeOnClick`-based approach is therefore permanently bypassed — adding `closeOnClick: true` to `floatingOptions` has no effect.

Since `bds-select.listenListMenu()` does receive the `bdsChange` custom event (custom events are not stopped by `stopPropagation` on the originating click), the selection itself is processed correctly — the popover just never closes.

---

## Impact

- **UX regression:** Users must perform an extra interaction (click outside) to dismiss the dropdown after every selection.
- **Keyboard navigation:** After selecting via `Enter`, the list stays open and focus remains trapped inside it.
- **Searchable mode:** After typing and selecting a result, the dropdown stays open, leaving the filtered list visible.
- **Affects all stories:** `Default`, `Searchable`, `CombiningTexfieldAttributes`, `CombiningListMenuElements`, `FormIntegration`.

---

## Failed Approach

Adding `closeOnClick: true` to `floatingOptions` in `listenPopOver()` does **not** fix this bug. `closeOnClick` is checked inside `bds-popover.handleFloatingClick()` which is only reachable via the `onClick` handler on `<Host>`. Because `bds-list-menu-item.handleClick` stops the click before it bubbles to `bds-popover`, that handler is never invoked.

---

## Fix Applied

Changes span two files:

**`packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx`**

A `@Method()` named `closePopover` is added to expose the mixin's `hide()` lifecycle through the element's public interface. The method name avoids `hide` to prevent a `void` vs `Promise<void>` return-type conflict with all existing `this.hide()` calls inside `bds-popover.tsx`:

```typescript
@Method()
async closePopover(): Promise<void> {
  this.hide();
}
```

`this.hide` here is the bound instance property created in `anchoredMixin.componentWillLoad()` (`this.hide = this.hide.bind(this)`), which resolves to `floatingMixin.hide()`. That runs the full hide lifecycle: checks `isVisible`, calls `hideElement()` → `hidePopover()`, then fires `onAfterHide()`.

**`packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`**

In `listenListMenu()`, call `closePopover()` after `setValue()`. `event.stopPropagation()` is also added here to address BUG-001 (double-fire) in the same change:

```typescript
private listenListMenu() {
  addElementListener(this.bdsList, 'bdsChange', (event: Event) => {
    event.stopPropagation();
    if (this.bdsList !== null) {
      const eventDetail = (event as CustomEvent<string | undefined>).detail;
      this.setValue(eventDetail || '');
      this.bdsPopover?.closePopover();
    }
  });
}
```

`bds-list-menu-item` is not modified — its `stopPropagation` is correct standalone behaviour and must not be changed.

---

## Verification

After the fix:

1. Open Storybook → Forms → bds-select → `Default`
2. Click the text field
3. Click any option
4. **Expected:** Dropdown closes immediately; text field shows selected label; chevron points down
5. Confirm `bdsChange` and `valueChange` still fire exactly once each (guard against regression with BUG-001 fix)

Related test cases: **TC-FUNC-001** (step 3), **TC-FUNC-002** (step 1 post-close).

---

## Related

- Test plan: `ai-work/qa/test-plans/bds-select-test-plan.md` → TC-FUNC-001, TC-FUNC-002
- BUG-001: `ai-work/qa/bug-reports/BUG-001-bds-select-valuechange-double-fire.md` — fix for BUG-001 and this bug must be applied together; verify both in the same test pass
