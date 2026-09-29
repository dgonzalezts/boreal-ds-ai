# `bds-popover` — Escape Focus-Restore Ordering, and the Deliberately Focus-Neutral Dismissals

## Two Escape paths, one shared restore

`bds-popover` hides-and-restores on Escape from either of two handlers, and both call the shared `restoreFocusToTrigger()`:

- the document-level `keydown` handler attached on show (`attachEscapeHandler`, `bds-popover.tsx:244-252`): when `key === 'Escape'` and `isVisible`, it calls `hide()` then `restoreFocusToTrigger()`;
- the trigger's own `KeyboardController` Escape binding set in `setupKeyboard()` (`bds-popover.tsx:566-572`): `hide()` then `restoreFocusToTrigger()`, attached to `this.triggerSlot`.

**Ordering nuance:** for a non-`managed` popover nested inside its focusable trigger, a `keydown` originating inside the popover bubbles to the trigger and is handled by the trigger's binding **first** (hide + restore), before it reaches `document`. The document handler then finds `isVisible === false`, so its guard skips a second restore. The trigger binding is therefore the handler that actually restores focus; `stopPropagation` still defaults to `false`, so the event does reach `document`. This ordering is a locked contract — failure-mode row PD-03.

## Deliberately focus-neutral dismissals (the component does *not* restore focus)

- **Click-outside** — `handleClickOutside()` (`bds-popover.tsx:293-313`) only emits `bdsClickOut` and calls `hide()`; focus follows the user's own click. This asymmetry with Escape/close-button is intentional and **confirmed** (FM-05).
- **Programmatic `closePopover()`** — `closePopover()` (`bds-popover.tsx:620-627`) calls `hide()` only. The consumer owns refocus in practice (`bds-date-picker` does its own `closePopoverAndRefocus()`, `bds-date-picker.tsx:687`). Whether the component or the consumer *should* own this is recorded as an **open decision** in the catalog (PD-01, `pending-decision`) — do not record it as a settled contract.
- **Focus-outside** — `handleFocusOutside()` / `evaluateFocusOutside()` (`bds-popover.tsx:256-286`) call `hide()` only. Same class as click-outside, but not covered by the focus fix's stated scope; recorded as an open decision (PD-02, `pending-decision`).

## Source

`bds-popover` focus-restoration testing pass (EOA-17662), 2026-09-28. Full contract catalog: `ai-work/testing/failure-modes/bds-popover.md` (FM-04, FM-05, PD-01, PD-02, PD-03).
