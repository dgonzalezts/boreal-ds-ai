---
name: bds-popover-managed-mode-skips-keyboardcontroller
description: bds-popover's managed={true} mode disables its own KeyboardController entirely — Enter/Space on the trigger will not open the popover unless the consumer wires its own keyboard-to-open path
metadata:
  type: project
---

`bds-popover.setupKeyboard()` (`packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx`) starts with `if (this.managed === true) return;` — when a consumer renders `<bds-popover managed={true}>` (to hand-manage trigger subscription itself, e.g. via `setAnchorElement`/`setListenElement`), the popover's own `KeyboardController` (Enter/Space → toggle, Escape → hide) is never attached to the trigger at all. Escape-to-close and click-outside-to-close still work in managed mode (`attachEscapeHandler`/`attachClickOutside` run unconditionally from `onAfterShowHandler`, independent of `managed`) — only the *opening* keyboard path is gated.

Verified empirically on `bds-date-picker` (`packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx`), which composes `<bds-popover managed={true}>` and relies entirely on its own `click`-only listener (`addElementListener(this.bdsField, 'click', this.listenClickTrigger)`) to open. Its slotted `<bds-text-field>` trigger has no keydown-to-click synthesis either (its `selectable` prop only sets `readOnly` on the inner `<input>`, not a keyboard handler). Net result: as of 2026-08-19, `bds-date-picker`'s trigger field is Tab-reachable but Enter/Space on it does **not** open the popover — a real, undocumented gap between the component's own plan/acceptance-criteria wording ("Enter/Space opens the popover via bds-popover's own KeyboardController") and actual behavior.

**Why:** discovered writing Task 20's Phase 1 unit tests (`bds-date-picker.keyboard.spec.ts`) — the plan assumed the KeyboardController path worked; empirical `newSpecPage` testing (dispatching `keydown` Enter/Space on the field and the field's `.bds-text-field__container`, asserting `HTMLElement.prototype.showPopover`) proved it doesn't fire.

**How to apply:** before writing a keyboard-activation test for any `bds-popover managed={true}` consumer, verify empirically (don't assume the plan's acceptance criteria is accurate) whether the consumer itself wires a keydown→open path. If it doesn't, write the test to lock in the *actual* current behavior (with an honest, descriptive name) rather than asserting a feature that doesn't exist — and flag the gap to the user/parent agent as a candidate follow-up implementation task, since fixing it is out of testing-subagent's scope. Candidate for promotion to `.agents/memory/` if another `managed={true}` popover consumer surfaces the same gap.
