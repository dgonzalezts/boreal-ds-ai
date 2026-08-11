# Keyboard-triggered focus move into newly-opened UI can double-activate the target

A handler triggered by a keyboard activation (Space/Enter) of a button that **also** opens a related UI element (a dropdown, popover, or menu) and then **synchronously** moves focus into that new UI within the same handler can cause the triggering key event to double-fire on the newly-focused target.

Mechanism: pressing Space/Enter on a button fires a `click`/custom-activation event. If that event's handler opens a popover and immediately calls a focus-management method (e.g. a list menu's `focusInitialTarget()`) on one of the popover's items, the still-in-flight Space/Enter keydown can continue propagating and be interpreted as activating whatever element now has focus — since the focus move happened within the same tick as the original key event, not after it finished being processed.

Found on `bds-table`'s Storybook example wiring a Column-visibility toggle button (opens a `bds-popover` containing a `bds-list-menu`, then calls `listMenu.focusInitialTarget()`): pressing Space/Enter on the toggle button caused the first list item to be immediately toggled/checked as a side effect of opening the menu, even though the user only intended to open it. Reproduced across all browsers — this is a general keyboard-event-timing issue, not Safari-specific.

**Fix**: defer the focus-move call via `requestAnimationFrame()` so it lands in a frame after the triggering keydown has fully finished being processed:

```js
popover
  .setAnchorElement(btn)
  .then(() => popover.openPopover())
  .then(() => requestAnimationFrame(() => listMenu.focusInitialTarget()));
```

**General takeaway**: any keyboard-activated handler that opens a related UI and then synchronously moves focus into it is at risk of this double-activation pattern. Defer the focus move to the next animation frame (or at minimum, the next microtask) rather than calling it inline in the same handler that responded to the triggering key event.

**Source**: EOA-16000 `bds-table` v4 Storybook `WithColumnVisibilityDropdown` story keyboard-interaction fix.
