# bds-popover close-path focus restore + its test-observability trap

## The fix

`bds-popover`'s own header close button (`popover-header__close` → `closeFromInside()`) called
`hide()` with **no focus restore**, so activating it with keyboard dropped focus to `<body>`.
Escape already restored focus inline (`(this.listenTarget ?? this.triggerSlot)?.focus()`), but that
is a no-op when the listen/anchor target is not focusable — which is exactly `bds-date-picker`'s
case: it sets the popover's listen+anchor element to the field's `.bds-text-field__container` div,
which has **no `tabindex`**; the real focusable node is the inner `input.bds-text-field__control`.

New private helper (called from `closeFromInside()` and the Escape handler):

```ts
private restoreFocusToTrigger(): void {
  const target = this.listenTarget ?? this.triggerSlot;
  if (target === null || target === undefined) return;
  target.focus();
  if (document.activeElement !== target) {
    target
      .querySelector<HTMLElement>('input, select, textarea, button, a[href], [tabindex]:not([tabindex="-1"])')
      ?.focus();
  }
}
```

Do **not** touch `handleClickOutside`/`evaluateFocusOutside` — click-outside focus deliberately
follows the click. Only the close-button path and Escape restore.

## PD-03 follow-up: the non-managed `setupKeyboard()` Escape binding

There are **two** Escape paths, and the non-managed one hid the popover before the document handler
could restore focus:

- `setupKeyboard()` (non-managed only) attaches an Escape binding on `triggerSlot` via
  `KeyboardController`. For the documented/story markup the popover is nested inside the trigger, so
  the `keydown` bubbles to `triggerSlot`, this binding fires **first** and calls `hide()`.
- The document-level `attachEscapeHandler()` then runs, but its guard is `if (key === Escape &&
  this.isVisible)` — `isVisible` is already `false`, so it skips `restoreFocusToTrigger()`. Net:
  focus lost to `<body>`.

Fix: that binding now does `hide()` **then** `restoreFocusToTrigger()`:

```ts
const kb = this._keyboard.attach(this.triggerSlot).set(KEYBOARD.Escape, () => {
  this.hide();
  this.restoreFocusToTrigger();
});
```

`managed === true` (bds-date-picker) still returns early, unchanged; document-level handler,
click-outside and other composers untouched. Order matters: `hide()` must run first (it detaches
listeners via `onAfterHideHandler`), then focus is restored.

## PD-04: Enter-on-close re-opens the popover — defer the focus move + ignore synthesized clicks

Live regression from the focus-restore work (Chromium + WebKit): focus the header close button of a
closable popover whose trigger is focusable, press **Enter**. `restoreFocusToTrigger()` focused the
trigger synchronously inside the Enter keydown; the browser then dispatched the Enter-generated
`click` (`detail === 0`) to the newly focused trigger, whose `handleClick` toggled it back open.
Trace: `keydown Enter` → `bdsClose` → `TRIG:focus` → `TRIG:keypress` → `TRIG:click (detail=0)` →
`bdsOpen`. Space is unaffected (its activation click is generated on keyup, after focus settles).

Two-part fix:
1. `restoreFocusToTrigger()` now wraps its focus logic in `requestAnimationFrame(...)` — same target
   resolution + descendant fallback, just deferred to the next frame.
2. `handleClick(event: MouseEvent)` now returns early on `event.detail === 0` (keyboard-synthesized).
   The ACTIVE-mode registration had to start forwarding the event
   (`(event: Event) => this.handleClick(event as MouseEvent)`); FOCUS/CLICK register `this.handleClick`
   by reference so the browser passes the event. `removeListeners` still removes `this.handleClick`.

**rAF, not a microtask.** A microtask runs before the browser's keypress/click default action for the
same key event, so focus would still move to the trigger in time for the click — only a full task
boundary (rAF) breaks the cycle. The team memory's "or at minimum the next microtask" is not enough
for this activation-click-retargeting case.

**Test fallout (reported, not rewritten).** Deferring breaks 8 focus-restoration assertions that
expect synchronous focus after `await waitForChanges()` — `waitForChanges`/`flushAll` flushes
Stencil's internal tick queue but NOT global `requestAnimationFrame` (mock-doc implements rAF as
`setTimeout(cb, 0)`). Affected: 4 committed + 2 sibling-added in `bds-popover-a11.spec.ts`
("bds-popover focus restoration"), and 2 in `bds-date-picker` (`keyboard.spec.ts` Escape-returns-focus,
`a11y.spec.ts` header-close-button). All need `await new Promise(r => requestAnimationFrame(r))`
before asserting (the date-picker keyboard one also needs the popover's deferred fallback to not
override the date-picker's own `bdsInput.focus()` rAF — in a real browser `container.focus()` is a
no-op so the fallback re-focuses the input either way; only the mock focus tracker makes it flaky).
The `detail === 0` guard itself broke nothing: `bds-select`/`bds-dropdown`/`bds-color-picker` and all
mouse/keyboard-open popover tests stayed green.



## Test-observability trap (important for the regression-test task)

The date-picker spec focus trackers (`bds-date-picker.keyboard.spec.ts`'s local `trackFocus` /
inline tracker, and `navigation.spec.ts`) patch `HTMLElement.prototype.focus` to **unconditionally
record `this` as the active element**, and expose it via `document.activeElement`:

```ts
HTMLElement.prototype.focus = function (this: HTMLElement) { focusState.element = this; };
```

Under that tracker, `container.focus()` on a non-focusable div *appears to succeed* — so
`document.activeElement === container`, the `!==` guard is false, and the **descendant fallback is
never exercised**. The existing date-picker Escape test still passes because `bds-date-picker`'s own
`closePopoverAndRefocus()` runs a `requestAnimationFrame(() => this.bdsInput?.focus())` that wins the
race and lands focus on the input regardless.

Consequence: a new `bds-popover` regression test for the close button must make the fallback
runnable — e.g. leave the default mock-doc `focus` (no tracker), so `document.activeElement` stays
`undefined` and `!==` target is true, then assert the first focusable descendant received focus.
Patching `focus` to only record real focusable targets works too. Asserting `document.activeElement`
without a tracker is otherwise dead (mock-doc `MockDocument` has no `activeElement`).
