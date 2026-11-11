# Follow-up ticket from EOA-19597 — `bds-popover` hardening + coverage

**Source plan:** `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md` (tasks T36, T37, T38)
**Suggested project:** EOA · type: Task · component: `bds-popover`

**Status (2026-10-28):** open. One adjacent fix has already shipped — do not redo it.
**Already shipped (do not re-implement):** click-outside dismissal for clicks over the document root (`documentElement`) is fixed in EOA-19597 (`838b6600`) with 6 specs in `bds-popover.click-outside.spec.ts`. That is **not** §1/§2/§3 below.
**Coverage (§4):** partially done — those 6 click-outside specs were added; isolation coverage is still below the 80% bar, so only the remaining branches need tests.
**Overlaps:** §1 and §3 touch the same `clickedInsideTrigger` / `evaluateFocusOutside` logic; decide §3 first (it defines the contract) and implement §1 under it. `EOA-19597-followup-shared-components.md` §1 (reconnect) also touches `bds-popover` listener wiring — land reconnect re-wiring before/with §2 to avoid touching the same attach/detach code twice.


## Summary

Three pre-existing `bds-popover` defects found while fixing click-outside dismissal (T33), plus a coverage increase for the component in isolation (67.8% statements / 55.2% branches measured during T33).

## 1. Consumer-supplied trigger-slot chrome dismisses the overlay — OPEN (was T36)

Clicking the date picker's slotted `<bds-text-field slot="field">` label closes the calendar and discards a pending day selection. The target is neither the document root, the body, nor an ancestor of the popover host, so it is not the T33 guard.

- **Fix shape:** include the trigger slot's own subtree (label, helper text, wrapper chrome) in the `clickedInsideTrigger` test, not only `listenTarget`/`triggerEl`/`triggerSlot`.
- **AC:** clicking any part of a consumer-supplied trigger keeps the overlay open; clicking a genuinely outside element still dismisses; all overlay consumers' suites green; browser check in Chrome and WebKit.

## 2. `closeOnClickOutside: false` leaks the document listener — OPEN (was T37)

Reproduced deterministically: open with the option `true`, set it to `false`, click outside → closes and emits `bdsClickOut`; reopen (option still `false`) → still closes. `detachClickOutside()` early-returns when the option is `false`, and there is no `@Watch('floatingOptions')`.

- **Fix shape:** attach/detach keyed off the option value, or re-evaluate attachment in a watcher.
- **AC:** setting `closeOnClickOutside: false` before or after mount disables dismissal; restoring `true` re-enables it; spec covering both orders.

## 3. Focus-outside dismissal ownership — OPEN, decide first (was T38)

Clicking non-focusable consumer chrome (`div.bds-text-field__container`) closes the popover via `evaluateFocusOutside()` **without** `bdsClickOut`, which contradicts the "click-outside is focus-neutral" contract in spirit.

- **Decision needed:** emit `bdsClickOut` on that path, keep it silent and document, or restrict when focus-outside dismissal applies.
- **AC:** the chosen behaviour is documented in `ai-work/testing/failure-modes/bds-popover.md` and covered by a spec.

## 4. Coverage increase — PARTIAL (click-outside specs shipped)

Raise `bds-popover.tsx` isolation coverage to the repo bar (≥80% statements/branches) before or alongside the fixes, since all three defects sit in currently-untested branches.
