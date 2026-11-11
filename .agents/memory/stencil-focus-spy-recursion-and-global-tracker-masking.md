# Focus Spies: `spyOn(el, 'focus')` Recursion, and Why a Global Prototype Tracker Masks a Fallback Branch

Two related traps when asserting focus moves under `newSpecPage`. Both stem from mock-doc's `focus()` dispatching a real bubbling `focus` event (see `stencil-mock-doc-no-activeelement-focus-tracking.md`).

## 1. Instance-level `jest.spyOn(el, 'focus')` calls through and can recurse

`jest.spyOn(el, 'focus')` keeps the original implementation by default, so the call dispatches mock-doc's `focus` event. If the element — or a host ancestor with an `onFocus` — moves focus again in response, the events re-enter and the spy's call count runs away. Original confirmed case: `bds-text-field`'s host `onFocus` re-focused its inner `<input>`, so spying a text field's host/input focus without stubbing produced a runaway call count.

**That specific loop is fixed (EOA-19597 T57).** `bds-text-field`'s host forwarder now guards on `e.target === e.currentTarget`, so a bubbled descendant `focus` is ignored — see `stencil-mock-doc-no-activeelement-focus-tracking.md` §"Why the `focus` event bubbles in mock-doc". Keep the stubbing habit (`mockImplementation(() => undefined)`) for any *new* host-level `onFocus` forwarder: the trap is generic, and the guard pattern is now the component-side fix to reach for.

Fix: stub the spy so it only records the call — `jest.spyOn(el, 'focus').mockImplementation(() => undefined)` — when the assertion is "`focus()` was called on this element", not "a real focus event fired". See `bds-popover-a11.spec.ts`'s nested-Escape test for the stub form.

## 2. A global `HTMLElement.prototype.focus` tracker masks the "focus first focusable descendant" branch

The usual focus-tracking workaround patches `HTMLElement.prototype.focus` globally and has it record `document.activeElement = this` (see `focus.spec.ts`). That is correct for asserting *where* focus landed, but it changes branch outcomes: `bds-popover`'s `restoreFocusToTrigger()` only reaches its descendant fallback when `document.activeElement !== target` after `target.focus()`. With the global tracker, `target.focus()` sets `document.activeElement = target`, the check is `false`, and the fallback branch is never entered — the branch is masked.

Consequence: the "trigger is not focusable → focus its first focusable descendant" behavior must be tested **without** a global prototype tracker, using separate instance-level spies (`jest.spyOn(wrapper, 'focus')` and `jest.spyOn(inner, 'focus')`) and letting mock-doc's untouched `document.activeElement` stay `undefined` (so `activeElement !== target` is `true` and the fallback runs). See `bds-popover-a11.spec.ts`'s `restores focus to the trigger's first focusable descendant…` tests.

## Source

`bds-popover` focus-restoration testing pass (EOA-17662), 2026-09-28. Cross-ref `ai-work/testing/failure-modes/bds-popover.md` FM-02.
