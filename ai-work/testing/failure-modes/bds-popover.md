# Failure-Mode Catalog — `bds-popover`

Audited against `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` as of 2026-09-28 (working tree contains the uncommitted `restoreFocusToTrigger` focus-loss fix). Rows are derived from reading the component source and its current (pre-existing) spec suite, not from any plan's stated test list.

Scope of this audit: the focus-restoration fix landed in `closeFromInside()` / the Escape handler, plus the surrounding focus/activation behaviors this fix touches. Rows outside that scope that the audit surfaced are recorded as `pending-decision` rather than tested.

---

### FM-01 | Header close button leaves focus on `<body>`

- **ID:** FM-01
- **Category:** component-contract-bypass
- **Risk:** a11y — a keyboard user activating the popover's header close button (Enter/Space on the focused `<bds-button>`) loses their place; focus falls to `<body>` instead of returning to the control that opened the popover.
- **Input that reveals it:** open a popover with `header` + `closable` from a focusable trigger, then activate the header close button.
- **Observed current behavior:** `closeFromInside()` calls `hide()` then `restoreFocusToTrigger()` (`bds-popover.tsx:506-522`); `restoreFocusToTrigger()` focuses `this.listenTarget ?? this.triggerSlot` and falls back to the target's first focusable descendant.
- **Recommended contract:** activating the header close button returns focus to the trigger, or — when the trigger itself cannot take focus — to the trigger's first focusable descendant.
- **Contract status:** confirmed
- **Why it matters:** without it, dismissing a popover by keyboard strands focus on `<body>`, breaking the next Tab stop.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::restores focus to the trigger button when the header close button is activated`

---

### FM-02 | Close button cannot restore focus when the trigger is a non-focusable wrapper

- **ID:** FM-02
- **Category:** component-contract-bypass
- **Risk:** a11y — when the trigger resolves to a non-focusable wrapper (e.g. `bds-date-picker`'s `.bds-text-field__container` div, wired via `setListenElement`/`setAnchorElement`), calling `.focus()` on the wrapper is a no-op, so focus is never restored.
- **Input that reveals it:** open a `managed` popover whose anchor/listen target is a non-focusable `<div>` containing an `<input>`, then activate the header close button.
- **Observed current behavior:** `restoreFocusToTrigger()` (`bds-popover.tsx:511-522`) focuses the target, then — when `document.activeElement !== target` — focuses `target.querySelector('input, select, textarea, button, a[href], [tabindex]:not([tabindex="-1"])')`.
- **Recommended contract:** focus lands on the wrapper's first focusable descendant (the real inner control) rather than being lost.
- **Contract status:** confirmed
- **Why it matters:** this is the exact `bds-date-picker` scenario the fix was written for; without the fallback the close button never returns focus to the field input.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::restores focus to the trigger's first focusable descendant when the trigger itself cannot take focus`

---

### FM-03 | Restore target resolution prefers `triggerSlot` over `listenTarget`

- **ID:** FM-03
- **Category:** equivalence
- **Risk:** when `listenTarget` and `triggerSlot` differ (a `managed` popover told to listen on one element and anchor to another), focus is restored to the wrong element.
- **Input that reveals it:** set the listen element and the anchor element to two different focusable buttons, open, then activate the header close button.
- **Observed current behavior:** `restoreFocusToTrigger()` resolves `const target = this.listenTarget ?? this.triggerSlot` (`bds-popover.tsx:512`).
- **Recommended contract:** the listen target wins when both are present.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` is the only current `managed` consumer and sets both to the same container, but the precedence is still a real branch.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::prefers the listen target over the anchor element when restoring focus`

---

### FM-04 | Escape closes the popover without restoring focus

- **ID:** FM-04
- **Category:** component-contract-bypass
- **Risk:** a11y — pressing Escape while the popover is open closes it but strands focus.
- **Input that reveals it:** open a popover, then press Escape.
- **Observed current behavior:** the document `keydown` handler calls `this.hide(); this.restoreFocusToTrigger();` when Escape is pressed while visible (`bds-popover.tsx:244-252`).
- **Recommended contract:** Escape closes the popover and restores focus to the trigger using the same resolution as FM-01/FM-02.
- **Contract status:** confirmed
- **Why it matters:** Escape is the primary keyboard dismissal gesture.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::restores focus to the trigger when the popover is closed with Escape`

---

### FM-05 | Click-outside must not move focus back

- **ID:** FM-05
- **Category:** component-contract-bypass
- **Risk:** moving focus on a click-outside dismissal would fight the user's own click destination (the browser moves focus there); restoring focus would yank it away.
- **Input that reveals it:** open the popover, then `mousedown` on an element outside both the trigger and the popover.
- **Observed current behavior:** `handleClickOutside()` only calls `emitClickOut()` and `hide()` (`bds-popover.tsx:293-313`) — deliberately does not touch focus (unlike `closeFromInside`/Escape).
- **Recommended contract:** click-outside closes without changing focus (focus follows the click).
- **Contract status:** confirmed
- **Why it matters:** regression guard for the deliberate asymmetry between click-outside and keyboard/close-button dismissal.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::leaves focus untouched when the popover closes from a click outside`

---

### FM-06 | Close button rendered without its required `header` region

- **ID:** FM-06
- **Category:** boundary
- **Risk:** visual/structural — a close button rendered in the absence of the header region it belongs to.
- **Input that reveals it:** render the popover with `closable` true and `header` false.
- **Observed current behavior:** the close button is nested inside the `{this.header && (...)}` block and further gated by `{this.closable && (...)}` (`bds-popover.tsx:679-700`).
- **Recommended contract:** the close button renders only when both `header` and `closable` are true.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` passes `closable={showChrome}` and `header={showChrome}` — the two must stay locked together.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-variants.spec.ts::Should not render close button when header is false even though closable is true` (the `header && closable` and `!closable` cases were already covered by the two sibling tests in the same file)

---

### FM-07 | Focus restoration throws when no trigger target exists

- **ID:** FM-07
- **Category:** null-empty
- **Risk:** a runtime `TypeError` escaping an event handler if a popover is dismissed before any trigger/listen target was ever resolved.
- **Input that reveals it:** call `restoreFocusToTrigger()` with both `listenTarget` and `triggerSlot` unset.
- **Observed current behavior:** the guard `if (target === null || target === undefined) return;` (`bds-popover.tsx:513`).
- **Recommended contract:** focus restoration is a safe no-op when there is no target.
- **Contract status:** confirmed
- **Why it matters:** defensive guard on a path only reachable on a misconfigured/late-removed popover; protects against an uncaught handler error.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::does not throw when the popover closes with no trigger to restore focus to`

---

### FM-08 | `bds-date-picker` close button does not return focus to the field input

- **ID:** FM-08
- **Category:** component-contract-bypass
- **Risk:** a11y integration — in `bds-date-picker` the popover's trigger resolves to the non-focusable `.bds-text-field__container` div, so the header close button must reach the descendant fallback (FM-02) to land focus on the real `<input>`.
- **Input that reveals it:** open a `bds-date-picker` and activate the popover header close button.
- **Observed current behavior:** `bds-date-picker.tsx:339-344` wires `setListenElement(inputContainer)` / `setAnchorElement(inputContainer)`; the popover's `restoreFocusToTrigger()` then focuses the container and falls back to its first focusable descendant (the field `<input>`).
- **Recommended contract:** activating the header close button places focus on the field `<input>`.
- **Contract status:** confirmed
- **Why it matters:** this is the consumer-level regression the fix was written for.
- **Covered by:** `src/components/forms/bds-date-picker/bds-date-picker/__test__/bds-date-picker.a11y.spec.ts::returns focus to the field input when the popover header close button is activated`

---

### FM-09 | Runtime watchers do not take effect immediately

- **ID:** FM-09
- **Category:** race-timing
- **Risk:** changing `activation` or `managed` after mount leaves the previous listener wiring in place — the trigger keeps the old mode's behavior (or the new mode never activates).
- **Input that reveals it:** set `activation` from `click` to `focus` at runtime and then focus the trigger; set `managed` at runtime.
- **Observed current behavior:** `@Watch('activation') onActivationChange()` re-subscribes the trigger (`bds-popover.tsx:129-133`); `@Watch('managed') onManagedChange()` re-subscribes and re-runs `setupKeyboard()` (`bds-popover.tsx:135-139`).
- **Recommended contract:** both watchers apply the new wiring on the next change cycle.
- **Contract status:** confirmed
- **Why it matters:** `bds-select`/`bds-dropdown`/`bds-date-picker` toggle these props; stale wiring silently changes open/close gestures.
- **Covered by:** `bds-popover-variants.spec.ts::re-subscribes the trigger with the new mode when activation changes at runtime`, `bds-popover-variants.spec.ts::re-subscribes the trigger and reconfigures the keyboard when managed changes at runtime`

---

### FM-10 | Focus/active activation modes mishandle pointer-vs-keyboard and blur

- **ID:** FM-10
- **Category:** equivalence
- **Risk:** `activation="focus"` opens on the focus that follows a mouse click; `activation="active"` fails to open on one of its two triggers; a focus-mode popover fails to close (or closes too eagerly) on blur.
- **Input that reveals it:** a `mousedown` then `focus` on the trigger; a genuine `focus`; a `blur` with focus either fully outside or still inside the floating content; `activation="active"` click and focus.
- **Observed current behavior:** `subscribe()` wires `focus`/`active` modes (`bds-popover.tsx:419-431`); `handlePointerDown` sets `isPointerInteraction` (`:459-461`); `handleFocus` early-returns on it (`:463-466`); `handleBlur` conditionally hides (`:468-477`).
- **Recommended contract:** keyboard focus alone opens a focus/active popover; the focus that follows a pointer press does not; blur hides only when focus truly left the popover.
- **Contract status:** confirmed
- **Why it matters:** pointer-vs-keyboard focus is the core of `activation="focus"`.
- **Covered by:** `bds-popover-variants.spec.ts::suppresses the focus-driven open that follows a pointer interaction in focus mode`, `::opens a focus-activated popover when the trigger receives focus`, `::closes a focus-activated popover when focus leaves it entirely`, `::keeps a focus-activated popover open when focus moves into its content`, `::opens an active-activated popover on click`, `::opens an active-activated popover on focus`

---

### FM-11 | Focus-outside misclassifies focus inside the popover/trigger/ancestor

- **ID:** FM-11
- **Category:** equivalence
- **Risk:** the popover closes while focus is still legitimately inside the trigger, the floating content, or one of its own ancestors (the Safari `activeElement`-is-an-ancestor case), or fails to close when focus genuinely leaves.
- **Input that reveals it:** run the containment check with `document.activeElement` set to each of the trigger, the floating content, an ancestor of the popover, an outside element, and the document body.
- **Observed current behavior:** `evaluateFocusOutside()` (`bds-popover.tsx:271-286`) OR's `listenTarget`/`triggerEl`/`triggerSlot` containment, floating-content containment, and an ancestor check; `handleFocusOutside()` defers and re-checks for the body fallback (`:256-269`).
- **Recommended contract:** hide only when focus is outside all three categories.
- **Contract status:** confirmed
- **Why it matters:** false-positive hiding is the exact bug class fixed earlier for Safari's ancestor `activeElement`.
- **Covered by:** `bds-popover-events.spec.ts::keeps the popover open while focus is inside the trigger`, `::keeps the popover open while focus is inside the floating content`, `::keeps the popover open while focus is on one of its own ancestors`, `::closes the popover when focus is outside both the trigger and the popover`, `::closes the popover when a focus-in event reports focus outside it`, `::closes the popover when a focus-in event reports focus on the document body`

---

### FM-12 | Deferred outside-detection acts after the popover already closed

- **ID:** FM-12
- **Category:** race-timing
- **Risk:** a `requestAnimationFrame`-deferred focus/click-outside check hides an already-closed popover (running the hide lifecycle a second time, re-emitting visibility events).
- **Input that reveals it:** schedule a focus-outside or click-outside check, close the popover before the frame fires.
- **Observed current behavior:** both deferred callbacks re-check `if (!this.isVisible) return;` (`bds-popover.tsx:259-260`, `:298-299`); the synchronous entry guards are `:257` and `:294`.
- **Recommended contract:** a deferred check is a no-op once the popover is no longer visible, and a check invoked while already closed does nothing.
- **Contract status:** confirmed
- **Why it matters:** prevents duplicate hide lifecycles and stray `bdsVisibilityUpdate` emissions.
- **Covered by:** `bds-popover-methods.spec.ts::aborts a pending focus-outside check when the popover closes first`, `::aborts a pending click-outside check when the popover closes first`, `::leaves a closed popover untouched when a click-outside runs`, `bds-popover-events.spec.ts::leaves a closed popover untouched when focus-outside runs`

---

### FM-13 | Full-width popover does not adopt the trigger width

- **ID:** FM-13
- **Category:** equivalence
- **Risk:** a `width="full"` popover stays at its previous width (or needlessly re-renders) when the trigger's width changes.
- **Input that reveals it:** run a position update with `width="full"` where the trigger and floating-content widths differ, and where they already match.
- **Observed current behavior:** `handlePosition()` sets the floating content width only when `Math.round`ed widths differ, then re-invokes `updatePosition` with a callback re-applying placement/arrow (`bds-popover.tsx:345-356`).
- **Recommended contract:** adopt the trigger width on a real difference; leave it untouched otherwise.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` uses `width="full"`/`"auto"` for its panel sizing.
- **Covered by:** `bds-popover-basics.spec.ts::applies the trigger width to a full-width popover when the widths differ`, `::leaves the width untouched when a full-width popover already matches the trigger`

---

### FM-14 | Arrow positioning for start placements and zero offsets

- **ID:** FM-14
- **Category:** boundary
- **Risk:** the arrow is placed at a wrong offset (or left over from a previous position) for `top-start`/`bottom-start` placements and when an axis offset is `0`/absent; the arrow is repositioned while the popover is disabled.
- **Input that reveals it:** `setArrowPosition` with `arrowData.x` non-zero and `0`, `arrowData.y` absent, and with `disabled` true.
- **Observed current behavior:** `setArrowPosition()` pins the start placement to `20px` only for a non-zero `x`, clears each axis when its value is nullish, and skips entirely when disabled or the arrow is disconnected (`bds-popover.tsx:377-392`).
- **Recommended contract:** start placements use the fixed inset; zero/absent offsets clear the axis; disabled popovers are not repositioned.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` uses `placement="bottom-start"`.
- **Covered by:** `bds-popover-methods.spec.ts::positions the arrow at the start offset and clears it for zero coordinates`

---

### FM-15 | Changing the anchor while open does not reposition

- **ID:** FM-15
- **Category:** race-timing
- **Risk:** a `managed` popover re-anchored while visible keeps its old position.
- **Input that reveals it:** `setAnchorElement(newAnchor)` while the popover is visible, and while it is not visible.
- **Observed current behavior:** `setAnchorElement()` re-subscribes the new anchor and calls `updatePosition` only when `isVisible` (`bds-popover.tsx:632-643`).
- **Recommended contract:** reposition when open; do not when closed.
- **Contract status:** confirmed
- **Why it matters:** `managed` consumers (e.g. `bds-table`'s dropdown) re-anchor dynamically.
- **Covered by:** `bds-popover-basics.spec.ts::repositions the popover when the anchor changes while it is open`

---

### FM-16 | Slot content change does not re-wire the trigger

- **ID:** FM-16
- **Category:** race-timing
- **Risk:** the trigger passed by slot changes, but the popover keeps listeners on the old node.
- **Input that reveals it:** fire the default slot's `slotchange` after mount.
- **Observed current behavior:** `handleSlotUpdate` delegates to `handleSlotChange(e, show, hide)` (`bds-popover.tsx:362-368`), which detaches the previous trigger and attaches focus/blur to the new slot target.
- **Recommended contract:** the new slot target drives open/close after a slot change.
- **Contract status:** confirmed
- **Why it matters:** `bds-select`/`bds-dropdown` render the slot's trigger dynamically. (Not observable through a rendered `<slot>` in `newSpecPage` — mock-doc does not render slot elements — so the handler is exercised directly.)
- **Covered by:** `bds-popover-basics.spec.ts::re-wires the trigger when the default slot content changes`

---

### FM-17 | Disconnect leaves position tracking / listeners running

- **ID:** FM-17
- **Category:** race-timing
- **Risk:** a removed popover keeps an `autoUpdate` loop and document listeners alive (leak), or throws when it had no resolved trigger.
- **Input that reveals it:** run `disconnectedCallback()` with and without a resolved target.
- **Observed current behavior:** `disconnectedCallback()` guards the target (`bds-popover.tsx:656-664`) then detaches keyboard/click-outside/focus-outside/escape and `stopAutoUpdate()`.
- **Recommended contract:** teardown is always safe, including with no target.
- **Contract status:** confirmed
- **Why it matters:** overlay components are frequently mounted/unmounted.
- **Covered by:** `bds-popover-basics.spec.ts::stops position tracking when the popover is disconnected`, `bds-popover-methods.spec.ts::skips listener removal when the popover disconnects without a trigger`

---

### FM-18 | Trigger-less subscribe/unsubscribe or non-managed listen-target set throws or mutates state

- **ID:** FM-18
- **Category:** null-empty
- **Risk:** keying helpers called without a trigger (or before `managed`) either throw or wrongly mutate `listenTarget`.
- **Input that reveals it:** `subscribe(undefined)`, `unsubscribe(undefined)`, `unsubscribe(detachedElement)`, `setListenElement(el)` on a non-managed popover.
- **Observed current behavior:** `subscribe`/`unsubscribe` early-return on `undefined` (`bds-popover.tsx:399-401`, `:438-440`); `setListenElement` early-returns unless `managed` (`:645-649`); `unsubscribe` recomputes `listenTarget` via `closest(...) || querySelector(...)` and falls back to `triggerEl` (`:449-454`).
- **Recommended contract:** these are safe no-ops / correct fallbacks.
- **Contract status:** confirmed
- **Why it matters:** the mixin calls these during lifecycle/consumer interactions.
- **Covered by:** `bds-popover-methods.spec.ts::ignores subscribe and unsubscribe calls without a trigger`, `::removes listeners from a trigger that is not an anchored element`, `::ignores setListenElement on a popover that is not managed`

---

### FM-19 | Option/placement getters do not fall back to defaults

- **ID:** FM-19
- **Category:** null-empty
- **Risk:** an unset `placement`/`floatingOptions` produces `undefined` positioning rather than the documented defaults.
- **Input that reveals it:** read `options`/`getPlacement` with `placement` unset and with `floatingOptions.hideArrow` set.
- **Observed current behavior:** `options` resolves `placement ?? 'bottom'` and `hideArrow ? undefined : arrowElement` (`bds-popover.tsx:171-180`); `getPlacement` returns `placement || 'bottom'` (`:593-595`).
- **Recommended contract:** unset values resolve to `bottom`; `hideArrow` suppresses the arrow element.
- **Contract status:** confirmed
- **Why it matters:** positioning options are consumed by the floating adapter on every update.
- **Covered by:** `bds-popover-methods.spec.ts::resolves floating options from the placement and floatingOptions props`

---

### PD-01 | Programmatic `closePopover()` is focus-neutral (caller owns refocus)

- **ID:** PD-01
- **Category:** component-contract-bypass
- **Risk:** a consumer closing the popover programmatically does not get focus moved implicitly — changing the API to restore focus would fight the caller's own focus intent (e.g. `bds-date-picker` moves focus back to the field itself via `closePopoverAndRefocus()` for day-click/Apply/Cancel).
- **Input that reveals it:** `await popoverElement.closePopover()` while open.
- **Observed current behavior:** `closePopover()` calls `this.hide()` only (`bds-popover.tsx:620-624`); focus restoration lives exclusively in `closeFromInside()` and the Escape handler.
- **Recommended contract:** `closePopover()` is intentionally focus-neutral — the programmatic API is caller-owned and each consumer decides where focus goes after calling it.
- **Contract status:** confirmed
- **Why it matters:** a programmatic close is an explicit consumer action, not a user gesture on the popover chrome; moving focus implicitly would surprise consumers and duplicate/conflict with the consumer's own refocus (today `bds-date-picker` owns this via `closePopoverAndRefocus()`). User ruling (2026-09-28): keep the current focus-neutral behavior; it must not be changed to move focus implicitly.
- **Covered by:** — (no test warranted: the intentional absence of an implicit focus move is the contract, and each consumer's refocus is that consumer's concern)

---

### PD-02 | Focus-outside dismissal is focus-neutral

- **ID:** PD-02
- **Category:** component-contract-bypass
- **Risk:** hiding on focus-outside does not return focus to the trigger — and deliberately so: restoring would fight the user's own focus move.
- **Input that reveals it:** move focus from inside the popover to an element outside both the trigger and the popover.
- **Observed current behavior:** `handleFocusOutside()` → `evaluateFocusOutside()` call `this.hide()` only (`bds-popover.tsx:256-286`).
- **Recommended contract:** focus-outside dismissal is intentionally focus-neutral — focus follows the user's move, mirroring the click-outside contract already recorded for `bds-popover` (FM-05).
- **Contract status:** confirmed
- **Why it matters:** the user is moving focus themselves; yanking it back to the trigger would fight that action and diverge from the click-outside contract (FM-05). User ruling (2026-09-28): keep the current focus-neutral behavior.
- **Covered by:** — (no test warranted: intentional no-restore contract; the hide-on-focus-outside behavior itself is already covered by FM-11/FM-12)

---

### PD-03 | Non-managed Escape must restore focus to the trigger (nested-popover ordering)

- **ID:** PD-03
- **Category:** race-timing
- **Risk:** a11y — with focus inside a non-`managed` popover nested in its trigger, pressing Escape hides the popover but leaves focus on `<body>`: the trigger's own `KeyboardController` Escape binding fires first (the bubbled `keydown` reaches the trigger before `document`) and hides the popover, so the document-level Escape handler's `isVisible` guard skips its own focus restore.
- **Input that reveals it:** open a non-managed popover nested inside its focusable trigger, move focus into the popover content, press Escape.
- **Observed current behavior:** `setupKeyboard()`'s Escape binding calls `this.hide(); this.restoreFocusToTrigger();` (`bds-popover.tsx:566-572`), so the binding that hides first also restores focus; the document-level handler (`:244-252`) then no-ops on its `isVisible` guard. `stopPropagation` still defaults to `false` (`IKeyboardController.ts:135-136`), so the event does reach `document`.
- **Recommended contract:** pressing Escape with focus inside a non-managed popover hides the popover **and** returns focus to the trigger (via `restoreFocusToTrigger`, including its descendant fallback).
- **Contract status:** confirmed
- **Why it matters:** focus must not be lost when Escape is pressed with focus inside the popover; because a nested popover's `keydown` bubbles through the trigger first, the trigger's own binding is the only handler positioned to restore focus before the visibility flag flips. This is what the fix changed, so the ordering is a locked contract rather than an open question.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover-a11.spec.ts::restores focus to the trigger when Escape is pressed inside the popover content`

---

### PD-04 | `hasHeaderSlot` / `hasFooterSlot` are dead code

- **ID:** PD-04
- **Category:** component-contract-bypass
- **Risk:** none runtime — the getters (`bds-popover.tsx:600-609`) are never referenced in `render()` (which reads the `header`/`footer` props directly) nor anywhere else in the repo.
- **Input that reveals it:** repo-wide grep for `hasHeaderSlot` / `hasFooterSlot`.
- **Observed current behavior:** unreferenced public class getters.
- **Recommended contract:** undecided — deletion candidate vs. keep as a public-ish hook. Deletion of non-`private` class members is a judgment call outside a test-only change (mirrors `bds-popover-coverage-backfill.md` Task 6).
- **Contract status:** pending-decision
- **Why it matters:** writing tests for genuinely dead code would inflate coverage without protecting a consumer contract.
- **Covered by:** —

---

### PD-05 | `ignoreNextClick` guard is unreachable

- **ID:** PD-05
- **Category:** component-contract-bypass
- **Risk:** none runtime — `ignoreNextClick` is declared (`bds-popover.tsx:39`) and read in `handleClick` (`:496-504`) but never assigned `true` anywhere in the repo, so the guard's true branch never executes.
- **Input that reveals it:** repo-wide grep for `ignoreNextClick` — only the declaration, the read, and the reset inside the branch itself.
- **Observed current behavior:** the branch resets the flag and `isPointerInteraction` and returns without toggling; unreachable via any public interaction.
- **Recommended contract:** undecided — deletion candidate (dead state) vs. wiring it to a real interaction. Same class as PD-04.
- **Contract status:** pending-decision
- **Why it matters:** a test for it would only inflate statement/branch coverage of dead code.
- **Covered by:** —

---

### PD-06 | `setAnchorElement(null)` warns but then throws

- **ID:** PD-06
- **Category:** null-empty
- **Risk:** a consumer passing `null`/an invalid anchor gets a warning and then a `TypeError` from `subscribe(null)` (`trigger.setAttribute` on `null`), instead of a clean no-op after the guard.
- **Input that reveals it:** `await popoverElement.setAnchorElement(null)` on a `managed` popover.
- **Observed current behavior:** `setAnchorElement()` logs `Invalid or null anchor element received` (`bds-popover.tsx:634`) but does not `return`; it proceeds to `unsubscribe`, assigns `triggerSlot = null`, and calls `subscribe(null)` (`:635-637`).
- **Recommended contract:** undecided — the warning implies an early return is intended, but the current code continues. Changing it affects consumers' dynamic re-anchoring paths.
- **Contract status:** pending-decision
- **Why it matters:** the `el === undefined || el === null` guard's true branch is otherwise unreachable without throwing, so it is left uncovered.
- **Covered by:** —
