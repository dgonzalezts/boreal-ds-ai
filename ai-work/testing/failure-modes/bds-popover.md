# Failure-Mode Catalog — `bds-popover`

Originally audited against `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` as of 2026-09-28 (focus-restoration fix). **Extended 2026-10-27 to the full component** (all props, events, methods, lifecycle, trigger modes, keyboard/a11y, edge cases) against the source on branch `feature/EOA-19936_increase-unit-test-coverage-popover-slider-checkbox_DG` (HEAD `d3288d22`, clean tree). Rows are derived from reading the component source, the `anchoredMixin`/`floatingMixin` it extends, `KeyboardController`, and the existing spec suite — not from any plan's stated test list.

Existing FM-01…FM-25 and PD-01…PD-06 are kept. Line references for rows touched in this pass were refreshed to the current source (`bds-popover.tsx` is 719 lines).

## Coverage after the 2026-10-27 test pass

9 suites, 184 tests, all passing. Statements **95.83%** (253/264), Branches **88.11%** (178/202), Functions **92.85%** (78/84), Lines **96.59%** (227/235). Still uncovered: `363-366` (FM-16 / PD-16), `498-500` (PD-05), `604-611` (PD-04) — all gated on open decisions.

## Coverage grounding (2026-10-27)

Run: `pnpm --filter @pxglobal/boreal-web-components run test:coverage -- src/components/overlays/bds-popover --collectCoverageFrom="src/components/overlays/bds-popover/**/*.tsx"` — 5 suites, 60 tests, all passing.

| Metric | Result |
| --- | --- |
| Statements | **67.8%** (179/264) |
| Branches | **54.95%** (111/202) |
| Functions | 70.23% (59/84) |
| Lines | 71.48% (168/235) |

Uncovered lines in `bds-popover.tsx`: `131-138` (activation/managed watchers), `257-284` (focus-outside), `346-355` (full-width resize), `363-366` (slot update), `420-424` (focus mode), `428-430` (active mode), `449-456` (unsubscribe), `460`, `464-465`, `469-475` (pointer/focus/blur handlers), `498-500` (`ignoreNextClick`), `560-563` (`removeListeners`), `604-611` (dead getters), `644` (re-anchor while open), `660-666` (`disconnectedCallback`). Fails the repo's 80% gate on all four metrics.

## Branch and spec-suite provenance (read before trusting any `Covered by`)

- The spec suite on this branch is exactly five files: `bds-popover.{a11y,basics,events,methods,variants}.spec.ts` (dotted names). The prior catalog's `Covered by` links for FM-09…FM-19 pointed at hyphenated files (`bds-popover-variants.spec.ts`, `bds-popover-events.spec.ts`, `bds-popover-methods.spec.ts`, `bds-popover-basics.spec.ts`) and test names that **do not exist in the repo**; they belong to `ai-work/plans/bds-popover-coverage-backfill.md`, which is `status: pending` and was never executed. Those links have been corrected to gaps below.
- FM-20…FM-25 describe the click-outside document-root fix (commit `838b6600`, EOA-19598 T33) and its spec `bds-popover.click-outside.spec.ts`. Both exist **only** on `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`; `838b6600` is not an ancestor of this branch. On this branch the source guard (`bds-popover.tsx:306`) lacks `target !== document.documentElement`, so FM-20 is a live defect here, not a covered row.
- FM-01…FM-05 and FM-07 are covered by tests present in `bds-popover.a11y.spec.ts` (file path corrected from `bds-popover-a11.spec.ts`).
- **2026-10-27 test pass:** four spec files added (`bds-popover.activation.spec.ts`, `.dismissal.spec.ts`, `.positioning.spec.ts`, `.lifecycle.spec.ts`) and `bds-popover.variants.spec.ts` was appended to. No `Covered by` entry above is forward-looking any more except FM-20…FM-25, which point at the other branch's `bds-popover.click-outside.spec.ts` by design (no equivalent test is written here, to avoid duplicating it).

## Status index

| Status | Rows |
| --- | --- |
| Covered by a test present on this branch | FM-01, FM-02, FM-03, FM-04, FM-05, FM-07, FM-08, FM-09, FM-10, FM-11, FM-12, FM-13, FM-14, FM-17, FM-18, FM-19, FM-26, FM-27, FM-30, FM-31, FM-32, FM-35, FM-37, FM-42, FM-44, FM-45, FM-47, PD-03, PD-01 (intentionally none), PD-02 (intentionally none) |
| Partially covered (named gaps in row) | FM-06 (closable-without-header now covered; remaining gap none), FM-15 (stale `aria-expanded` on new anchor is a defect), FM-28, FM-29, FM-36, FM-38, FM-39, FM-40 (`bdsClickIn` silence is PD-12), FM-41 (nested trigger/content presses are FM-23/FM-24), FM-43, FM-46 |
| Covered only on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (`bds-popover.click-outside.spec.ts`, commit `838b6600`, not an ancestor) | FM-20, FM-21, FM-22, FM-23, FM-24, FM-25 |
| Gap — `confirmed`, intentionally untested | FM-16 (hinges on PD-16), FM-33, FM-34 (defects), PD-06 (defect) |
| `pending-decision` (no test allowed yet) | PD-04, PD-05, PD-07, PD-08, PD-09, PD-10, PD-11, PD-12, PD-13, PD-14, PD-15, PD-16, PD-17, PD-18 |
| Expected to FAIL against current code if tested (real defect, hand off to `frontend-subagent`) | FM-20 (this branch only), FM-33, FM-34, PD-06, plus two sub-assertions: FM-14 start placement with absent `x` (pins `20px`), FM-15 new-anchor `aria-expanded` stays `false` while open |


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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::restores focus to the trigger button when the header close button is activated`

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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::restores focus to the trigger's first focusable descendant when the trigger itself cannot take focus`

---

### FM-03 | Restore target resolution prefers `triggerSlot` over `listenTarget`

- **ID:** FM-03
- **Category:** equivalence
- **Risk:** when `listenTarget` and `triggerSlot` differ (a `managed` popover told to listen on one element and anchor to another), focus is restored to the wrong element.
- **Input that reveals it:** set the listen element and the anchor element to two different focusable buttons, open, then activate the header close button.
- **Observed current behavior:** `restoreFocusToTrigger()` resolves `const target = this.listenTarget ?? this.triggerSlot` (`bds-popover.tsx:512`).
- **Recommended contract:** the listen target wins when both are present.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` is the only current `managed` consumer and sets both to the same container, but the precedence is still a real branch. (Row title is a legacy misnomer: the code and the contract both prefer `listenTarget`.)
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::prefers the listen target over the anchor element when restoring focus`

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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::restores focus to the trigger when the popover is closed with Escape` (exercises the document-level handler only; the trigger-binding path is PD-03)

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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::leaves focus untouched when the popover closes from a click outside`

---

### FM-06 | Close button rendered without its required `header` region

- **ID:** FM-06
- **Category:** boundary
- **Risk:** visual/structural — a close button rendered in the absence of the header region it belongs to.
- **Input that reveals it:** render the popover with `closable` true and `header` false.
- **Observed current behavior:** the close button is nested inside the `{this.header && (...)}` block and further gated by `{this.closable && (...)}` (`bds-popover.tsx:682-703`).
- **Recommended contract:** the close button renders only when both `header` and `closable` are true.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` passes `closable={showChrome}` and `header={showChrome}` — the two must stay locked together.
- **Covered by:** `bds-popover.variants.spec.ts::Should render close button only when closable is true` (header + closable renders), `::Should not render close button when closable is false` (header, not closable), `::Should not render a close button when closable is true but header is false`

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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.a11y.spec.ts::does not throw when the popover closes with no trigger to restore focus to`

---

### FM-08 | `bds-date-picker` close button does not return focus to the field input

- **ID:** FM-08
- **Category:** component-contract-bypass
- **Risk:** a11y integration — in `bds-date-picker` the popover's trigger resolves to the non-focusable `.bds-text-field__container` div, so the header close button must reach the descendant fallback (FM-02) to land focus on the real `<input>`.
- **Input that reveals it:** open a `bds-date-picker` and activate the popover header close button.
- **Observed current behavior:** `bds-date-picker.tsx` wires `setListenElement(inputContainer)` / `setAnchorElement(inputContainer)`; the popover's `restoreFocusToTrigger()` then focuses the container and falls back to its first focusable descendant (the field `<input>`).
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
- **Observed current behavior:** `@Watch('activation') onActivationChange()` re-subscribes the trigger (`bds-popover.tsx:129-133`); `@Watch('managed') onManagedChange()` re-subscribes and re-runs `setupKeyboard()` (`bds-popover.tsx:135-139`). Lines 131-138 are uncovered. The `active` and `managed` true-direction defects are tracked separately (FM-33, FM-34).
- **Recommended contract:** both watchers apply the new wiring on the next change cycle.
- **Contract status:** confirmed
- **Why it matters:** `bds-select`/`bds-dropdown`/`bds-date-picker` toggle these props; stale wiring silently changes open/close gestures.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::opens on trigger focus after activation changes from click to focus`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::toggles exactly once per click after activation changes at runtime`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::attaches the activation listeners when managed changes from true to false`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::attaches the keyboard activation when managed changes from true to false` (the `active`-mode un-removable-listener and managed-to-true directions are FM-33/FM-34, not tested)

---

### FM-10 | Focus/active activation modes mishandle pointer-vs-keyboard and blur

- **ID:** FM-10
- **Category:** equivalence
- **Risk:** `activation="focus"` opens on the focus that follows a mouse click; `activation="active"` fails to open on one of its two triggers; a focus-mode popover fails to close (or closes too eagerly) on blur.
- **Input that reveals it:** a `mousedown` then `focus` on the trigger; a genuine `focus`; a `blur` with focus either fully outside or still inside the floating content; `activation="active"` click and focus.
- **Observed current behavior:** `subscribe()` wires `focus`/`active` modes (`bds-popover.tsx:419-431`); `handlePointerDown` sets `isPointerInteraction` (`:459-461`); `handleFocus` early-returns on it (`:463-466`); `handleBlur` conditionally hides (`:468-477`). Lines 420-424, 428-430, 460, 464-465, 469-475 are uncovered.
- **Recommended contract:** keyboard focus alone opens a focus/active popover; the focus that follows a pointer press does not (focus mode); blur hides only when focus truly left the popover. The pointer-click-on-focusable-trigger behavior of `active` mode is PD-10.
- **Contract status:** confirmed
- **Why it matters:** pointer-vs-keyboard focus is the core of `activation="focus"`.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::opens when the trigger receives keyboard focus`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::does not open from the focus that follows a pointer press`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::opens once from the click that completes a pointer press`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::opens from keyboard focus once a previous pointer press has blurred away`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::closes on blur when focus moved outside the popover`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::stays open on blur when focus moved into the popover content`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::active activation › opens when the trigger receives focus`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::active activation › opens when the trigger is clicked` (pointer click on a focusable trigger in `active` mode is PD-10, not tested)

---

### FM-11 | Focus-outside misclassifies focus inside the popover/trigger/ancestor

- **ID:** FM-11
- **Category:** equivalence
- **Risk:** the popover closes while focus is still legitimately inside the trigger, the floating content, or one of its own ancestors (the Safari `activeElement`-is-an-ancestor case), or fails to close when focus genuinely leaves.
- **Input that reveals it:** run the containment check with `document.activeElement` set to each of the trigger, the floating content, an ancestor of the popover, an outside element, and the document body.
- **Observed current behavior:** `evaluateFocusOutside()` (`bds-popover.tsx:271-286`) OR's `listenTarget`/`triggerEl`/`triggerSlot` containment, floating-content containment, and an ancestor check; `handleFocusOutside()` defers and re-checks for the body fallback (`:256-269`). Lines 257-284 are entirely uncovered.
- **Recommended contract:** hide only when focus is outside all three categories.
- **Contract status:** confirmed
- **Why it matters:** false-positive hiding is the exact bug class fixed earlier for Safari's ancestor `activeElement`.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::closes when focus moves to an element outside the popover and its trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::stays open when focus is on the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::stays open when focus is inside the popover content`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::stays open when focus is on the popover host itself`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::stays open when focus falls back to an ancestor of the popover`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::closes after the deferred re-check when focus falls to the document body`

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
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::does not schedule a focus check while the popover is closed`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::ignores a pending focus check when the popover closes before the frame fires`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::ignores a pending click-outside check when the popover closes before the frame fires`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::does not schedule a click-outside check while the popover is closed`

---

### FM-13 | Full-width popover does not adopt the trigger width

- **ID:** FM-13
- **Category:** equivalence
- **Risk:** a `width="full"` popover stays at its previous width (or needlessly re-renders) when the trigger's width changes.
- **Input that reveals it:** run a position update with `width="full"` where the trigger and floating-content widths differ, and where they already match.
- **Observed current behavior:** `handlePosition()` sets the floating content width only when `Math.round`ed widths differ, then re-invokes `updatePosition` with a callback re-applying placement/arrow (`bds-popover.tsx:341-360`). Lines 346-355 uncovered; the `else if (width === 'auto')` reset (`:357-358`) is also unasserted.
- **Recommended contract:** adopt the trigger width on a real difference; leave it untouched otherwise; `auto` clears any previously applied inline width.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` uses `width="full"`/`"auto"` for its panel sizing.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::writes the resolved placement onto the floating content`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::adopts the trigger width when the full-width popover differs from it`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::leaves the width untouched when the popover already matches the trigger width`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::repositions against the trigger and reapplies the placement and arrow after a full-width update`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not touch the width of a fixed-width popover`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::clears a previously applied inline width for an auto-width popover`

---

### FM-14 | Arrow positioning for start placements and zero offsets

- **ID:** FM-14
- **Category:** boundary
- **Risk:** the arrow is placed at a wrong offset (or left over from a previous position) for `top-start`/`bottom-start` placements and when an axis offset is `0`/absent; the arrow is repositioned while the popover is disabled.
- **Input that reveals it:** `setArrowPosition` with `arrowData.x` non-zero and `0`, `arrowData.y` absent, and with `disabled` true.
- **Observed current behavior:** `setArrowPosition()` pins the start placement to `20px` only for a non-zero `x`, clears each axis when its value is nullish, and skips entirely when disabled or the arrow is disconnected (`bds-popover.tsx:377-392`). Branches 378, 383, 388, 389 uncovered.
- **Recommended contract:** start placements use the fixed inset; zero/absent offsets clear the axis; disabled popovers are not repositioned.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` uses `placement="bottom-start"`.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::applies the computed x and y offsets for a centered placement`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::clears the horizontal offset when the computed x is zero`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::clears the vertical offset when the computed y is absent`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::pins the arrow to the fixed inset for top-start placement`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::pins the arrow to the fixed inset for bottom-start placement`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::clears the horizontal inset for a start placement when the computed x is zero`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not reposition the arrow when the popover is disabled`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not reposition the arrow when the result carries no arrow data`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not reposition the arrow when the result has no middleware data`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not throw when the arrow element is hidden from the render` **Not tested:** a start placement with `arrowData.x` absent (`undefined`) currently pins the arrow to `20px` (`x !== 0` is true for `undefined`), contradicting "absent offsets clear the axis"; hand off to `frontend-subagent` or rule on it before a test is written.

---

### FM-15 | Changing the anchor while open does not reposition

- **ID:** FM-15
- **Category:** race-timing
- **Risk:** a `managed` popover re-anchored while visible keeps its old position. Secondary: the new anchor is stamped `aria-expanded="false"` by `subscribe()` while the popover is still open, so the new trigger's expanded state is stale until the next show/hide.
- **Input that reveals it:** `setAnchorElement(newAnchor)` while the popover is visible, and while it is not visible.
- **Observed current behavior:** `setAnchorElement()` re-subscribes the new anchor and calls `updatePosition` only when `isVisible` (`bds-popover.tsx:635-646`); line 644 uncovered. `updateAriaExpanded` is not re-run after re-anchoring.
- **Recommended contract:** reposition when open; do not when closed; the new anchor reflects the current visibility in `aria-expanded`.
- **Contract status:** confirmed
- **Why it matters:** `managed` consumers (e.g. `bds-table`'s dropdown) re-anchor dynamically.
- **Covered by:** partial — `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::repositions against the new anchor when it changes while the popover is open`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::does not reposition when the anchor changes while the popover is closed`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::stamps the new anchor and removes the attributes from the previous one`. **Gap (expected to FAIL):** the new anchor is stamped `aria-expanded="false"` while the popover is open; not tested, defect for `frontend-subagent`.

---

### FM-16 | Slot content change does not re-wire the trigger

- **ID:** FM-16
- **Category:** race-timing
- **Risk:** the trigger passed by slot changes, but the popover keeps listeners on the old node.
- **Input that reveals it:** fire the default slot's `slotchange` after mount.
- **Observed current behavior:** `handleSlotUpdate` delegates to `handleSlotChange(e, show, hide)` (`bds-popover.tsx:362-368`), which detaches the previous trigger and attaches focus/blur to `e.target`. **Audit note 2026-10-27:** `e.target` of a `slotchange` is the popover's own internal `<slot>` element, not a consumer trigger, and `handleSlotUpdate` passes fresh closures each time so `detachTriggerListeners` can never remove the previous pair — see PD-16 for whether this wiring has any real effect.
- **Recommended contract:** the new slot target drives open/close after a slot change.
- **Contract status:** confirmed
- **Why it matters:** `bds-select`/`bds-dropdown` render the slot's trigger dynamically. (Not observable through a rendered `<slot>` in `newSpecPage` — mock-doc does not render slot elements — so the handler is exercised directly.)
- **Covered by:** — (skipped: the row depends on PD-16, which questions whether the slot wiring has any real-browser effect; a test would pin a synthetic-target behavior)

---

### FM-17 | Disconnect leaves position tracking / listeners running

- **ID:** FM-17
- **Category:** race-timing
- **Risk:** a removed popover keeps an `autoUpdate` loop and document listeners alive (leak), or throws when it had no resolved trigger.
- **Input that reveals it:** run `disconnectedCallback()` with and without a resolved target; remove an open popover.
- **Observed current behavior:** `disconnectedCallback()` guards the target (`bds-popover.tsx:659-667`) then detaches keyboard/click-outside/focus-outside/escape and `stopAutoUpdate()`. It overrides the mixin's `disconnectedCallback` entirely (the mixin's `hide()`/`floatingDisconnect` never run). Lines 660-666 uncovered.
- **Recommended contract:** teardown is always safe, including with no target.
- **Contract status:** confirmed
- **Why it matters:** overlay components are frequently mounted/unmounted.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::stops position syncing when an open popover is removed`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::detaches the keyboard controller when the popover is removed`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::stops reacting to the trigger click after removal`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::stops reacting to outside presses after removal`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::stops reacting to Escape after removal`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::tears down safely when no trigger was ever resolved`

---

### FM-18 | Trigger-less subscribe/unsubscribe or non-managed listen-target set throws or mutates state

- **ID:** FM-18
- **Category:** null-empty
- **Risk:** keying helpers called without a trigger (or before `managed`) either throw or wrongly mutate `listenTarget`.
- **Input that reveals it:** `subscribe(undefined)`, `unsubscribe(undefined)`, `unsubscribe(detachedElement)`, `setListenElement(el)` on a non-managed popover.
- **Observed current behavior:** `subscribe`/`unsubscribe` early-return on `undefined` (`bds-popover.tsx:399-401`, `:438-440`); `setListenElement` early-returns unless `managed` (`:648-652`); `unsubscribe` recomputes `listenTarget` via `closest(...) || querySelector(...)` and falls back to `triggerEl` (`:449-454`). Lines 449-456, 560-563 uncovered.
- **Recommended contract:** these are safe no-ops / correct fallbacks.
- **Contract status:** confirmed
- **Why it matters:** the mixin calls these during lifecycle/consumer interactions.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::ignores a subscribe call without a trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::ignores an unsubscribe call without a trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::strips the ARIA attributes and stops listening when a trigger is unsubscribed`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::unsubscribes a trigger that is detached from the document without throwing`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::ignores a listen element on a popover that is not managed`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::adopts the listen element on a managed popover`

---

### FM-19 | Option/placement getters do not fall back to defaults

- **ID:** FM-19
- **Category:** null-empty
- **Risk:** an unset `placement`/`floatingOptions` produces `undefined` positioning rather than the documented defaults.
- **Input that reveals it:** read `options`/`getPlacement` with `placement` unset and with `floatingOptions.hideArrow` set.
- **Observed current behavior:** `options` resolves `placement ?? 'bottom'` and `hideArrow ? undefined : arrowElement` (`bds-popover.tsx:171-180`); `getPlacement` returns `placement || 'bottom'` (`:596-598`). Branches 173, 174, 175 uncovered.
- **Recommended contract:** unset values resolve to `bottom`; `hideArrow` suppresses the arrow element.
- **Contract status:** confirmed
- **Why it matters:** positioning options are consumed by the floating adapter on every update.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::resolves the documented defaults for placement, strategy, shift and flip`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::exposes the arrow element in the options by default`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::omits the arrow element from the options when hideArrow is set`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::uses the placement prop for the options and the rendered placement`

---

### FM-20 | A click on the document root never dismisses

- **ID:** FM-20
- **Category:** component-contract-bypass
- **Risk:** a click on the page gutter/margin (anything that resolves the event target to `<html>`) leaves every open popover visible — the user clicks away and the overlay stays up. Since `bds-popover` backs select, dropdown, date-picker, tooltip and search-bar, the defect is visible across all overlays.
- **Input that reveals it:** open the popover, then dispatch `mousedown` on `document.documentElement`.
- **Observed current behavior:** `handleClickOutside()` resolves `target` from `e.composedPath()[0] ?? e.target` and treats `target.contains(this.el)` as "the click fell back to one of our own ancestors" (`bds-popover.tsx:296`, `:306`). `document.documentElement.contains(this.el)` is `true`, so the dismissal branch at `:308-311` is skipped. **On this branch the guard is `target !== null && target !== document.body && target.contains(this.el)` — the `target !== document.documentElement` exclusion added by commit `838b6600` is absent, so the defect is live here.**
- **Recommended contract:** a click whose target is the document root counts as outside the popover and dismisses it exactly like a click on any other outside element — one `bdsClickOut`, visibility flipped to false. Contract fixed by EOA-19598 T33 (acceptance criterion 1).
- **Contract status:** confirmed
- **Why it matters:** without it, the widest area of the page (the gutter) is a dead zone for dismissal; the fix adds `target !== document.documentElement` to the guard.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::dismisses a visible popover when mousedown targets the document root` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here. A test written here fails against current code until `838b6600` lands

### FM-21 | A click on the document body dismisses

- **ID:** FM-21
- **Category:** equivalence
- **Risk:** if the body exclusion were ever dropped or the root exclusion applied too broadly, `document.body.contains(this.el)` would classify a body click as an own-ancestor and the popover would stop dismissing — the same bug class as FM-20 one level down.
- **Input that reveals it:** open the popover, then dispatch `mousedown` on `document.body`.
- **Observed current behavior:** `target !== document.body` excludes the body from the ancestor fallback (`bds-popover.tsx:306`), so the dismissal branch runs.
- **Recommended contract:** a click on `<body>` dismisses, mirroring the pre-existing behaviour that the root exclusion must not regress.
- **Contract status:** confirmed
- **Why it matters:** it is the boundary case that proves the root exclusion is additive, not a rewrite of the ancestor rule.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::dismisses a visible popover when mousedown targets the document body` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here

### FM-22 | A click on an ancestor of the host does not dismiss

- **ID:** FM-22
- **Category:** component-contract-bypass
- **Risk:** dismissing when the click lands on a wrapper the host lives in (a consumer's positioning container, a field container) breaks the guard's original purpose: some browsers report the ancestor as the event target for clicks inside the host's own subtree.
- **Input that reveals it:** render the popover as a sibling of its trigger inside a consumer wrapper, open it, then dispatch `mousedown` on the wrapper.
- **Observed current behavior:** the `target.contains(this.el)` guard keeps the popover open when the target is a non-root, non-body ancestor of the host (`bds-popover.tsx:306`).
- **Recommended contract:** a click on any ancestor of the host other than `<body>`/`<html>` does not dismiss (T33 acceptance criterion 2).
- **Contract status:** confirmed
- **Why it matters:** this is the branch the root/body exclusions had to be added to without weakening.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::keeps a visible popover open when mousedown targets an ancestor of the popover host` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here

### FM-23 | A click inside the trigger does not dismiss

- **ID:** FM-23
- **Category:** component-contract-bypass
- **Risk:** if trigger containment were dropped, pressing on the control that owns the popover would dismiss it before the click completes, making an open popover impossible to interact with from its trigger (and flickering on re-open).
- **Input that reveals it:** open the popover, then dispatch `mousedown` on the trigger element.
- **Observed current behavior:** `clickedInsideTrigger` ORs containment against `listenTarget`, `triggerEl` and `triggerSlot` (`bds-popover.tsx:301-302`), suppressing the dismissal.
- **Recommended contract:** a click inside the trigger does not dismiss (T33 acceptance criterion 2).
- **Contract status:** confirmed
- **Why it matters:** the trigger is the primary interaction surface for `click`/`focus`/`active` activation modes.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::keeps a visible popover open when mousedown targets the trigger` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here

### FM-24 | A click inside the floating content does not dismiss

- **ID:** FM-24
- **Category:** component-contract-bypass
- **Risk:** dismissing on any press inside the panel makes the content unusable — text selection, button presses and menu item clicks would all close the popover first.
- **Input that reveals it:** open the popover, then dispatch `mousedown` on an element inside `.popover-content`.
- **Observed current behavior:** `this.floatingContent.contains(target) || this.floatingContent === target` suppresses the dismissal (`bds-popover.tsx:304`).
- **Recommended contract:** a click inside the floating content does not dismiss through the click-outside path; closing on content click remains governed by `floatingOptions.closeOnClick` (T33 acceptance criterion 2).
- **Contract status:** confirmed
- **Why it matters:** the two dismissal paths (outside vs. `closeOnClick`) must stay independent.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::keeps a visible popover open when mousedown targets the floating content` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here

### FM-25 | `closeOnClickOutside: false` detaches the listener entirely

- **ID:** FM-25
- **Category:** component-contract-bypass
- **Risk:** if the opt-out were only consulted in the dismissal branch (or reached after listener attachment), consumers that manage dismissal themselves — including the document-root case — would still get an unwanted `bdsClickOut` and an unwanted hide.
- **Input that reveals it:** set `floatingOptions.closeOnClickOutside = false` before opening, then dispatch `mousedown` on `document.documentElement` (and on an ordinary outside element).
- **Observed current behavior:** `attachClickOutside()` returns before registering the `mousedown` listener when the option is `false` (`bds-popover.tsx:219-224`), and `detachClickOutside()` returns early for the same reason (`:229-236`). Branches 220 and 230 uncovered.
- **Recommended contract:** with `closeOnClickOutside: false` no `mousedown` listener is attached, so no target dismisses the popover and no `bdsClickOut` is emitted.
- **Contract status:** confirmed
- **Why it matters:** the opt-out must cover every outside target. The existing `basics::Should NOT close when closeOnClickOutside is false and clicking outside` dispatches `click` (not `mousedown`), so it passes even if the option were ignored — it never exercises listener attachment.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.click-outside.spec.ts::keeps a visible popover open and emits nothing on a document-root mousedown when closeOnClickOutside is false` — lives on branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (commit `838b6600`), not yet an ancestor of this branch; no test re-added here; the present `basics` test is still vacuous for this row

### PD-01 | Programmatic `closePopover()` is focus-neutral (caller owns refocus)

- **ID:** PD-01
- **Category:** component-contract-bypass
- **Risk:** a consumer closing the popover programmatically does not get focus moved implicitly — changing the API to restore focus would fight the caller's own focus intent (e.g. `bds-date-picker` moves focus back to the field itself via `closePopoverAndRefocus()` for day-click/Apply/Cancel).
- **Input that reveals it:** `await popoverElement.closePopover()` while open.
- **Observed current behavior:** `closePopover()` calls `this.hide()` only (`bds-popover.tsx:624-627`); focus restoration lives exclusively in `closeFromInside()` and the two Escape paths. (The mixin's `hideFocus()` still blurs an element focused inside the panel — see PD-13.)
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
- **Covered by:** — (no test warranted: intentional no-restore contract; the hide-on-focus-outside behavior itself is FM-11/FM-12)

---

### PD-03 | Non-managed Escape must restore focus to the trigger (nested-popover ordering)

- **ID:** PD-03
- **Category:** race-timing
- **Risk:** a11y — with focus inside a non-`managed` popover nested in its trigger, pressing Escape hides the popover but leaves focus on `<body>`: the trigger's own `KeyboardController` Escape binding fires first (the bubbled `keydown` reaches the trigger before `document`) and hides the popover, so the document-level Escape handler's `isVisible` guard skips its own focus restore.
- **Input that reveals it:** open a non-managed popover nested inside its focusable trigger, move focus into the popover content, press Escape.
- **Observed current behavior:** `setupKeyboard()`'s Escape binding calls `this.hide(); this.restoreFocusToTrigger();` (`bds-popover.tsx:566-572`), so the binding that hides first also restores focus; the document-level handler (`:244-252`) then no-ops on its `isVisible` guard. `stopPropagation` still defaults to `false`, so the event does reach `document`.
- **Recommended contract:** pressing Escape with focus inside a non-managed popover hides the popover **and** returns focus to the trigger (via `restoreFocusToTrigger`, including its descendant fallback).
- **Contract status:** confirmed
- **Why it matters:** focus must not be lost when Escape is pressed with focus inside the popover; because a nested popover's `keydown` bubbles through the trigger first, the trigger's own binding is the only handler positioned to restore focus before the visibility flag flips. This is what the fix changed, so the ordering is a locked contract rather than an open question.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::hides the popover and returns focus to the trigger when Escape is pressed inside the content` (the existing `methods::Should invoke hide() via keydown Escape on the trigger` still covers the hide half only)

---

### PD-04 | `hasHeaderSlot` / `hasFooterSlot` are dead code

- **ID:** PD-04
- **Category:** component-contract-bypass
- **Risk:** none runtime — the getters (`bds-popover.tsx:603-611`) are never referenced in `render()` (which reads the `header`/`footer` props directly) nor anywhere else in the repo.
- **Input that reveals it:** repo-wide grep for `hasHeaderSlot` / `hasFooterSlot`.
- **Observed current behavior:** unreferenced public class getters.
- **Recommended contract:** undecided — deletion candidate vs. keep as a public-ish hook. Deletion of non-`private` class members is a judgment call outside a test-only change (mirrors `bds-popover-coverage-backfill.md` Task 6).
- **Contract status:** pending-decision
- **Why it matters:** writing tests for genuinely dead code would inflate coverage without protecting a consumer contract. They also account for lines 604-611 in the uncovered list.
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
- **Why it matters:** a test for it would only inflate statement/branch coverage of dead code (lines 498-500, branch 497).
- **Covered by:** —

---

### PD-06 | `setAnchorElement(null)` warns but then throws

- **ID:** PD-06
- **Category:** null-empty
- **Risk:** a consumer passing `null`/an invalid anchor gets a warning and then a `TypeError` from `subscribe(null)` (`trigger.setAttribute` on `null`), instead of a clean rejection after the guard; the previous anchor has already been unsubscribed and `triggerSlot` overwritten with `null`, leaving the popover with no working trigger.
- **Input that reveals it:** `await popoverElement.setAnchorElement(null)` (and `undefined`) on a `managed` popover.
- **Observed current behavior:** `setAnchorElement()` logs `Invalid or null anchor element received.` (`bds-popover.tsx:637`) but does not `return`; it proceeds to `unsubscribe(this.triggerSlot)`, assigns `triggerSlot = el`, and calls `subscribe(el)` (`:639-642`). `subscribe(undefined)` early-returns, but `subscribe(null)` does not (it only checks `=== undefined`) and throws.
- **Recommended contract:** an invalid (`null`/`undefined`) anchor is rejected with a warning and the method returns without throwing or mutating the current anchor/subscriptions. **Resolved 2026-10-27:** the warning text and the consumer-facing `Promise<void>` method signature make rejecting-with-warning the only coherent contract; the current fall-through (warn, then crash or silently drop the anchor) cannot be intended. Not a user ruling — flagged for review.
- **Contract status:** confirmed
- **Why it matters:** a consumer re-anchoring from an async lookup that resolves to `null` should not break an open popover. A test for this row fails against current code (`subscribe(null)` throws) — hand off to `frontend-subagent`.
- **Covered by:** — (gap; branch 637 uncovered)

---

### FM-26 | Invalid `behavior` / `activation` / `placement` values do not fall back to defaults

- **ID:** FM-26
- **Category:** equivalence
- **Risk:** an unsupported attribute value (typo, framework passing `undefined`/`''`) leaves the host with an invalid `role`, no activation listener, or an unpositioned panel.
- **Input that reveals it:** `behavior="foo"`, `activation="hover"`, `placement="left-bottom"`; the same values assigned at runtime (the watcher re-validates).
- **Observed current behavior:** `checkPropValues()` (`bds-popover.tsx:105-127`) runs on load via `hooks.onBeforeLoad` and on `behavior`/`activation`/`placement` change, calling `validatePropValue` which resets the prop to `menu` / `click` / `bottom` and emits a `console.warn`. Note `POPOVER_ROLE` includes `tooltip`, which the `behavior` JSDoc omits.
- **Recommended contract:** each invalid value is replaced by its documented default (`menu`, `click`, `bottom`) with a warning, at load and at runtime.
- **Contract status:** confirmed
- **Why it matters:** this is the component's only prop validation; consumers rely on it for graceful degradation.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::replaces invalid behavior, activation and placement values with their defaults at load`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::warns once for each invalid value at load`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::does not warn when every value is valid`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::replaces an invalid behavior assigned at runtime with the default`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::replaces an invalid activation assigned at runtime with the default`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::replaces an invalid placement assigned at runtime with the default`

---

### FM-27 | `width` forms resolve to the documented CSS value

- **ID:** FM-27
- **Category:** equivalence
- **Risk:** a `number` width, `'full'`, and `'auto'` render the wrong inline width.
- **Input that reveals it:** `width="500"`, `width="full"`, `width="auto"`, and the default.
- **Observed current behavior:** `popoverWidth` maps `'full'` → `100%`, `'auto'` → `auto`, otherwise `` `${width}px` `` (`bds-popover.tsx:187-191`); default `320`.
- **Recommended contract:** number → px, `full` → `100%`, `auto` → `auto`, default 320px. Invalid or non-positive numerics are PD-07.
- **Contract status:** confirmed
- **Why it matters:** panel sizing for every consumer.
- **Covered by:** `bds-popover.variants.spec.ts::Should apply numeric width in px`, `::Should apply fit-content when width is auto`, `::Should apply fit-content when width is full` (test names say "fit-content" but assert `auto` / `100%`), `::Should apply a 320px width by default`

---

### FM-28 | Header and footer regions are gated by their props

- **ID:** FM-28
- **Category:** null-empty
- **Risk:** the header/footer chrome (and its slots) render when not requested, or fail to render when requested.
- **Input that reveals it:** `header` / `footer` each true and false; named slots `header-icon`, `header-title`, `footer-helper`, `footer-button`.
- **Observed current behavior:** `{this.header && ...}` and `{this.footer && ...}` (`bds-popover.tsx:682-715`); the arrow is independently gated by `canShowArrow`.
- **Recommended contract:** each region renders only when its prop is true, and not otherwise; slots appear inside their region.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` toggles `header`/`footer` per `calendarType`.
- **Covered by:** `bds-popover.variants.spec.ts::Should render header slot when header is true`, `::Should not render header when header is false`, `::Should render footer slot when footer is true`, `::Should render header-icon slot inside header`, `::Should not render the footer region when footer is false`, `::Should not render the header region inside a footer-only popover`

---

### FM-29 | `disabled` does not block every entry point

- **ID:** FM-29
- **Category:** component-contract-bypass
- **Risk:** a disabled popover opens through a path other than the trigger click — keyboard Enter/Space, `openPopover()`, `togglePopoverFn()`.
- **Input that reveals it:** `disabled` true, then Enter on the trigger; `await openPopover()`; `await togglePopoverFn()`.
- **Observed current behavior:** `hooks.onBeforeShow: () => !this.disabled` (`bds-popover.tsx:202`) vetoes every route through the mixin's `show()`; arrow positioning also skips when disabled (`:378`).
- **Recommended contract:** while `disabled` is true no entry point opens the popover and no `bdsOpen`/`bdsVisibilityUpdate` is emitted. Behavior when `disabled` flips to true while open is PD-07.
- **Contract status:** confirmed
- **Why it matters:** the contract-bypass family — a guard that only covers the click path is not a guard.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::disabled popover › does not open when Enter is pressed on the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::does not open through openPopover`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::does not open through togglePopoverFn`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::emits no open or visibility events when an open is attempted`; click path: `bds-popover.a11y.spec.ts::Should not show popover when disabled`

---

### FM-30 | Consumer callbacks in `floatingOptions` are not honored

- **ID:** FM-30
- **Category:** component-contract-bypass
- **Risk:** a consumer's `floatingOptions.onBeforeShow` / `onBeforeHide` veto, or `onAfterShow` / `onAfterHide` notification, is ignored or fires at the wrong time.
- **Input that reveals it:** `floatingOptions = { onBeforeShow: () => false }` then open; `onBeforeHide: () => false` then close; `onAfterShow` / `onAfterHide` spies.
- **Observed current behavior:** the popover passes `floatingOptions` to `floatingMixin`, whose `show()`/`hide()` AND the hook and prop results (`floating.mixin.ts` `onBeforeShow`/`onBeforeHide`) and call `onAfterShow`/`onAfterHide` on the prop (`:onAfterShow`/`:onAfterHide`). The popover's own `hooks` have no `onBeforeHide`, so only the prop can veto a hide.
- **Recommended contract:** a falsy `onBeforeShow`/`onBeforeHide` keeps the popover in its current state with no events; the after-callbacks fire once per real transition.
- **Contract status:** confirmed
- **Why it matters:** the only supported extension point for consumer-controlled open/close.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::keeps the popover closed and silent when onBeforeShow returns false`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::keeps the popover open and silent when onBeforeHide returns false`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::opens normally when onBeforeShow returns true`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::calls each after-callback once per real transition`

---

### FM-31 | Trigger resolution picks the wrong element

- **ID:** FM-31
- **Category:** equivalence
- **Risk:** the popover anchors to/listens on the wrong node, so clicks do nothing or open the popover from an unrelated area.
- **Input that reveals it:** popover nested in a `<button>`; in a custom wrapper containing `.bds-button` / `input` / `select`; as the only child of a plain `<div>`.
- **Observed current behavior:** `anchoredMixin.onBeforeLoad` resolves `parent.closest('button, input, select') ?? parent.querySelector(ANCHORED_TRIGGERS) ?? parent`, assigns `triggerSlot` only when `isConnected`, then `subscribe()` stamps `part`, `aria-describedby`, `aria-haspopup`, `aria-expanded` (`bds-popover.tsx:399-406`) and resolves `listenTarget` from `closest/querySelector(ANCHORED_TRIGGERS)`.
- **Recommended contract:** nearest native control ancestor, else first anchored-trigger descendant of the parent, else the parent itself; the trigger is stamped with `part="popover-trigger"`.
- **Contract status:** confirmed
- **Why it matters:** every consumer relies on this implicit wiring.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::resolves the nearest native control ancestor as the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::prefers a native control ancestor of the parent over a trigger descendant of the parent`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::falls back to the first anchored trigger descendant of the parent`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::falls back to the parent element when no anchored trigger exists`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::stamps the trigger with the ARIA attributes in the collapsed state`

---

### FM-32 | `aria-expanded` does not mirror visibility

- **ID:** FM-32
- **Category:** component-contract-bypass
- **Risk:** a11y — assistive tech announces the trigger as collapsed while the popover is open (or vice versa).
- **Input that reveals it:** open then close via click, `openPopover()`, Escape, click-outside.
- **Observed current behavior:** `subscribe()` stamps `aria-expanded="false"`; `onAfterShowHandler`/`onAfterHideHandler` call `updateAriaExpanded()` writing `String(this.isVisible)` onto `triggerEl` (`bds-popover.tsx:478-494`); `updateElementAttr` is null-safe so a `managed` popover with no anchor yet does not throw.
- **Recommended contract:** the trigger's `aria-expanded` is `"true"` while open and `"false"` otherwise, for every open/close route.
- **Contract status:** confirmed
- **Why it matters:** WAI-ARIA disclosure/menu-button pattern.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::reports true on the trigger when opened through openPopover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::reports false on the trigger when closed through closePopover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::follows the trigger click on every toggle`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::reports false after Escape closes the popover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::reports false after a click outside closes the popover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::does not throw when a managed popover without an anchor changes visibility`

---

### FM-33 | Switching away from `active` activation leaves un-removable listeners

- **ID:** FM-33
- **Category:** race-timing
- **Risk:** after `activation` changes from `active` (or after `subscribe` runs twice), the trigger still toggles on every click/focus through anonymous listeners, so a click toggles twice (open then immediately close) and the popover appears broken; the same listeners also survive `disconnectedCallback`.
- **Input that reveals it:** `activation="active"`, then set `activation="click"` and click the trigger; or call `setAnchorElement` / flip `managed` twice on an `active` popover.
- **Observed current behavior:** `active` mode registers `() => this.handleFocus()` and `() => this.handleClick()` (`bds-popover.tsx:427-431`), fresh closures that `removeListeners` (`:559-564`) cannot match; the `focus`/`click` modes use stable property handlers that dedupe correctly.
- **Recommended contract:** changing `activation` removes the previous mode's listeners entirely (FM-09's contract); a popover never holds two live click/focus toggles on one trigger; disconnect leaves nothing attached.
- **Contract status:** confirmed
- **Why it matters:** a test for this row fails against current code — real defect, hand off to `frontend-subagent`.
- **Covered by:** — (gap; expected to fail)

---

### FM-34 | Switching `managed` to true does not remove activation wiring

- **ID:** FM-34
- **Category:** component-contract-bypass
- **Risk:** a popover set to `managed` at runtime keeps its click/focus listeners and Enter/Space/Escape keyboard binding, so it still toggles itself while the consumer believes it owns activation.
- **Input that reveals it:** mount non-managed, then set `managed = true`, click the trigger.
- **Observed current behavior:** `onManagedChange()` calls `subscribe()` (which now returns early at `if (this.managed === true) return`) and `setupKeyboard()` (which returns early), but neither detaches what was attached while `managed` was false (`bds-popover.tsx:135-139`, `:408`, `:567`).
- **Recommended contract:** per the `managed` JSDoc ("does not attach any activation listeners … the consumer is responsible"), flipping to true removes the previously attached listeners and detaches the keyboard controller.
- **Contract status:** confirmed
- **Why it matters:** the false-to-true direction of the watcher (FM-09) is uncovered and, by inspection, broken. A test fails against current code — hand off to `frontend-subagent`.
- **Covered by:** — (gap; expected to fail)

---

### FM-35 | `managed` mode attaches no activation or keyboard wiring

- **ID:** FM-35
- **Category:** component-contract-bypass
- **Risk:** a `managed` popover opens from a trigger click or Enter/Space on its own, fighting the consumer's control.
- **Input that reveals it:** `managed="true"`, set an anchor, click it; press Enter/Space on it.
- **Observed current behavior:** `subscribe()` stamps ARIA attributes then returns before adding any listener (`bds-popover.tsx:408`); `setupKeyboard()` returns early (`:567`). The document-level Escape handler still attaches on show (`:244-252`), so an open managed popover still closes on Escape.
- **Recommended contract:** a managed popover is opened/closed only by `openPopover`/`closePopover`/`togglePopoverFn` (and the dismissal gestures after it is open); the anchor still receives `part` and the ARIA attributes.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker`'s Enter/Space gap stems from this boundary (see team memory `bds-popover-managed-mode-skips-keyboardcontroller.md`); the popover's half of that contract is unpinned.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::managed mode › does not open when the trigger is clicked`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::managed mode › does not open when Enter or Space is pressed on the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::managed mode › does not open when the trigger receives focus`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::still stamps the trigger with the part and ARIA attributes`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::opens and closes through the programmatic methods`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::closes an open popover when Escape is pressed anywhere in the document`

---

### FM-36 | Keyboard activation on the trigger

- **ID:** FM-36
- **Category:** equivalence
- **Risk:** Enter/Space do not toggle the popover, Space toggles instead of only opening, or `focus` mode wrongly reacts to Enter/Space.
- **Input that reveals it:** keydown Enter / Space / Escape on the trigger, popover closed and open, in `click` and `focus` modes.
- **Observed current behavior:** `setupKeyboard()` binds Escape (hide + restore focus) and, unless `activation === 'focus'`, `setActivateHandler(() => this.toggle())` for Enter and Space (`bds-popover.tsx:566-579`).
- **Recommended contract:** Enter/Space toggle the popover in `click`/`active` modes and are not bound in `focus` mode; Escape hides.
- **Contract status:** confirmed
- **Why it matters:** primary keyboard path for non-managed consumers.
- **Covered by:** `bds-popover.a11y.spec.ts::Should open popover when Enter key is pressed on trigger`, `bds-popover.methods.spec.ts::Should invoke show() via keydown Enter on the trigger…`, `::…Space…`, `::Should invoke hide() via keydown Escape on the trigger…`, `a11y::Should close popover when Escape key is pressed`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::closes an open popover when Enter is pressed on the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::closes an open popover when Space is pressed on the trigger`; `src/components/overlays/bds-popover/__test__/bds-popover.activation.spec.ts::does not bind Enter or Space to toggle the popover`

---

### FM-37 | Rapid double activation opens then closes once

- **ID:** FM-37
- **Category:** race-timing
- **Risk:** two quick clicks cause a duplicate `showPopover`, leave the popover half-open, or emit duplicate open events.
- **Input that reveals it:** two synchronous `click` events on the trigger.
- **Observed current behavior:** `handleClick` → `toggle()`; `floatingMixin.show()` returns early when already visible, `hide()` when already hidden (`floating.mixin.ts`).
- **Recommended contract:** two clicks yield exactly one open followed by one close.
- **Contract status:** confirmed
- **Why it matters:** double-fire is a classic race for overlay components.
- **Covered by:** `bds-popover.events.spec.ts::should call showPopover only once even if trigger is clicked rapidly` (asserts one show and one hide; the title says "only once" but the closed end state is the contract).

---

### FM-38 | Lifecycle events do not fire exactly once per real transition

- **ID:** FM-38
- **Category:** race-timing
- **Risk:** `bdsOpen`/`bdsClose`/`bdsVisibilityUpdate` fire twice, fire on a no-op (opening an already-open popover, closing an already-closed one), or carry the wrong `visible` value, so consumers desynchronize their own state.
- **Input that reveals it:** `openPopover()` twice; `closePopover()` while closed; open then close; Escape while closed.
- **Observed current behavior:** `showElement`/`hideElement` call `hooks.mounted`/`unmounted` → `emitOpen`/`emitClose` with `visible: this.isVisible` (after the flag flip); `onAfterShow`/`onAfterHide` call `emitVisibilityUpdate` (`bds-popover.tsx:481-494`, `:527-541`). The mixin's `show()`/`hide()` guard on `isVisible`.
- **Recommended contract:** each event fires once per real open/close with `{ element, visible }` matching the new state; redundant calls emit nothing.
- **Contract status:** confirmed
- **Why it matters:** consumers (select, date-picker) drive their own UI from these events.
- **Covered by:** `bds-popover.methods.spec.ts::Should emit bdsOpen when the popover is opened via openPopover()`, `::Should emit bdsVisibilityUpdate when the popover opens`, `::…when the popover closes`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits bdsOpen once with the visible state when the popover opens`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits bdsClose once with the hidden state when the popover closes`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits exactly one visibility update per real transition`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits nothing when opening an already open popover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits nothing when closing an already closed popover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits nothing when Escape is pressed while the popover is closed`

---

### FM-39 | Click inside the content: event, propagation and `closeOnClick`

- **ID:** FM-39
- **Category:** component-contract-bypass
- **Risk:** content clicks leak to the trigger (re-toggling the popover), skip `bdsClickIn`, or close the popover when `closeOnClick` is off (or fail to close it when on).
- **Input that reveals it:** click inside `.popover-content` with `closeOnClick` true / false / unset.
- **Observed current behavior:** the Host `onClick` calls `handleContentClick` → `e.stopPropagation()` then `handleFloatingClick()`, which emits `bdsClickIn` and hides only when `floatingOptions.closeOnClick` is truthy (`bds-popover.tsx:320-331`, `:679`).
- **Recommended contract:** content click emits one `bdsClickIn`, never reaches ancestors, and closes only when `closeOnClick` is true.
- **Contract status:** confirmed
- **Why it matters:** menu/list consumers use `closeOnClick` for item selection.
- **Covered by:** `bds-popover.methods.spec.ts::Should emit bdsClickIn when the popover content is clicked`, `bds-popover.basics.spec.ts::Should close popover when closeOnClick is true and clicking inside content`, `::should NOT close popover when closeOnClick is false and clicking inside content`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::does not let a content click reach the ancestors of the popover`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits one bdsClickIn and keeps the popover open when closeOnClick is not set`; `src/components/overlays/bds-popover/__test__/bds-popover.lifecycle.spec.ts::emits one bdsClickIn and closes the popover when closeOnClick is true`

---

### FM-40 | Footer clicks are excluded from content-click handling

- **ID:** FM-40
- **Category:** component-contract-bypass
- **Risk:** a footer action (e.g. Apply/Cancel) closes the popover via `closeOnClick` before the consumer's own handler decides, or emits a spurious `bdsClickIn`.
- **Input that reveals it:** `footer` true, `closeOnClick` true, click a button slotted in `footer-button`.
- **Observed current behavior:** the footer wrapper has its own `onClick={e => e.stopPropagation()}` (`bds-popover.tsx:711`), so the Host's `handleContentClick` never runs for footer clicks.
- **Recommended contract:** footer clicks never close the popover through `closeOnClick`; the consumer owns closing. Whether `bdsClickIn` should also be suppressed is PD-12.
- **Contract status:** confirmed
- **Why it matters:** `bds-date-picker` Apply/Cancel own their close sequencing (`closePopoverAndRefocus`).
- **Covered by:** `bds-popover.events.spec.ts::Should call hidePopover when footer button triggers closeOnClick` (title contradicts its assertions: it expects zero hides and `aria-hidden="false"`) and `::Should NOT call hidePopover when footer button triggers closeOnClick` (second test uses `closeOnClick: false` and a plain `<button>`). **Gap:** `bdsClickIn` silence for footer clicks is unasserted.

---

### FM-41 | Click-outside emits once and hides (default path)

- **ID:** FM-41
- **Category:** equivalence
- **Risk:** an outside `mousedown` fails to close the popover, emits `bdsClickOut` twice, or fires while the popover is closed.
- **Input that reveals it:** open, `mousedown` on a sibling element, wait one frame.
- **Observed current behavior:** `handleClickOutside` defers one `requestAnimationFrame`, re-checks visibility and containment, then `emitClickOut()` + `hide()` (`bds-popover.tsx:293-313`); the `mousedown` listener is attached on show and removed on hide.
- **Recommended contract:** one `bdsClickOut` and a close per outside press.
- **Contract status:** confirmed
- **Why it matters:** baseline dismissal behavior for every overlay.
- **Covered by:** `bds-popover.basics.spec.ts::Should close popover when clicking outside`, `bds-popover.methods.spec.ts::Should emit bdsClickOut when a click occurs outside the popover and trigger`, `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::ignores outside presses once the popover has closed`. Nested trigger/content presses are FM-23/FM-24 (other branch).

---

### FM-42 | Offset arithmetic with and without the arrow

- **ID:** FM-42
- **Category:** boundary
- **Risk:** the panel sits at the wrong distance from the trigger — overlapping it, or too far away — when `floatingOptions.offset` is set, zero, negative, or the arrow is hidden.
- **Input that reveals it:** `offset` undefined / `0` / `8` / `-4`, each with `hideArrow` false and true.
- **Observed current behavior:** `getOffset(hideArrow, offset, OFFSET)` returns `offset ?? 0` when the arrow is hidden and `11 + offset` (or `11`) otherwise (`getOffset.ts`; `bds-popover.tsx:174`).
- **Recommended contract:** with arrow: `11 + offset`; hidden arrow: `offset` only; default 0 additional offset.
- **Contract status:** confirmed
- **Why it matters:** position is computed from this on every update.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for no custom offset`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a zero offset`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a positive offset`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a negative offset`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for no custom offset and a hidden arrow`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a zero offset and a hidden arrow`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a positive offset and a hidden arrow`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::computes the distance for a negative offset and a hidden arrow` (`it.each` rows)

---

### FM-43 | Arrow rendering follows `hideArrow`

- **ID:** FM-43
- **Category:** boundary
- **Risk:** the arrow renders (or its attribute is set) when hidden, or is missing when allowed.
- **Input that reveals it:** `floatingOptions = {}` and `{ hideArrow: true }`.
- **Observed current behavior:** `canShowArrow` drives both the `.popover-arrow` element and `data-arrow-visible` (`bds-popover.tsx:589-591`, `:677`, `:704-706`).
- **Recommended contract:** arrow element and attribute present by default, absent with `hideArrow`.
- **Contract status:** confirmed
- **Why it matters:** visual contract consumed by the SCSS and `bds-tooltip`-style consumers.
- **Covered by:** `bds-popover.variants.spec.ts::Should show arrow by default`, `::Should hide arrow when hideArrow is true`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::removes the arrow element and its visibility attribute when hideArrow is enabled after the first open`; `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::restores the arrow element when hideArrow is disabled again`

---

### FM-44 | `setAnchorElement` on a non-managed popover must be ignored

- **ID:** FM-44
- **Category:** component-contract-bypass
- **Risk:** a non-managed popover re-anchored by a consumer ends up with its own activation listeners unsubscribed and re-added to the wrong element.
- **Input that reveals it:** `await setAnchorElement(otherEl)` on a popover without `managed`.
- **Observed current behavior:** `if (this.managed === false) return;` (`bds-popover.tsx:636`).
- **Recommended contract:** no-op for non-managed popovers (mirrors `setListenElement`).
- **Contract status:** confirmed
- **Why it matters:** the existing `methods::Should set the part attribute on the new anchor element via setAnchorElement()` uses a non-managed popover, so the `part` it asserts was already stamped at load and the call it names is a no-op — that test passes vacuously and does not cover this row.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.positioning.spec.ts::ignores a new anchor on a popover that is not managed`

---

### FM-45 | Programmatic methods and `getVisibility`

- **ID:** FM-45
- **Category:** equivalence
- **Risk:** `openPopover`/`closePopover`/`togglePopoverFn`/`getVisibility` disagree with the rendered state.
- **Input that reveals it:** call each method from closed and open states.
- **Observed current behavior:** thin async wrappers over `show`/`hide`/`toggle`; `getVisibility` returns `this.isVisible === true` (`bds-popover.tsx:618-657`).
- **Recommended contract:** methods reflect state in `aria-hidden` and in `getVisibility`.
- **Contract status:** confirmed
- **Why it matters:** the public imperative API used by `bds-date-picker`, `bds-select`, `bds-search-bar`.
- **Covered by:** `bds-popover.methods.spec.ts::Should open the popover when openPopover() is called`, `::Should close the popover when closePopover() is called`, `::Should toggle the popover open…`, `::Should toggle the popover closed…`, `::Should return false from getVisibility() when popover is closed`, `::…true… when popover is open`, `::…false… after closing an open popover`.

---

### FM-46 | Host role and `aria-hidden` reflect `behavior` and visibility

- **ID:** FM-46
- **Category:** equivalence
- **Risk:** a11y — the panel exposes the wrong `role` or stays in the accessibility tree while closed.
- **Input that reveals it:** `behavior="menu" | "listbox" | "dialog" | "tooltip"`; closed vs open.
- **Observed current behavior:** Host renders `role={this.behavior}`, `aria-hidden={isVisible ? 'false' : 'true'}`, `popover="manual"` (`bds-popover.tsx:672-679`).
- **Recommended contract:** role equals `behavior`; `aria-hidden` is `"true"` while closed and `"false"` while open.
- **Contract status:** confirmed
- **Why it matters:** screen-reader semantics for every consumer role.
- **Covered by:** `bds-popover.a11y.spec.ts::Should have aria-hidden true when not visible`, `::Should have aria-hidden false when visible`, `::Should have role tooltip on floating content` (asserts the default `menu`); `bds-popover.variants.spec.ts::Should expose role %s when behavior is %s` (`it.each` over menu, listbox, dialog, tooltip)

---

### FM-47 | Popover hides opener-owned focus on close (mixin `hideFocus`)

- **ID:** FM-47
- **Category:** race-timing
- **Risk:** closing while focus is inside the panel blurs the focused element, dropping focus to `<body>`; combined with FM-01/FM-04 the restore must run after the hide.
- **Input that reveals it:** focus an element inside the panel, call `closePopover()` / click outside / close via any route.
- **Observed current behavior:** `anchoredMixin.hideElement()` calls `hideFocus()` which blurs `document.activeElement` when it is inside `floatingContent`, then hides the popover.
- **Recommended contract:** focus never remains inside a hidden panel; ownership of where it goes next is per-route (FM-01/04 restore; FM-05/PD-01/PD-02 neutral; closeOnClick is PD-13).
- **Contract status:** confirmed
- **Why it matters:** ordering between `hide()` and `restoreFocusToTrigger()` is load-bearing.
- **Covered by:** `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::blurs the focused element inside the panel when the popover closes`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::does not blur an element outside the panel when the popover closes`; `src/components/overlays/bds-popover/__test__/bds-popover.dismissal.spec.ts::blurs the focused panel element before restoring focus to the trigger from the close button`

---

### PD-07 | Invalid or non-positive numeric `width`, and `disabled` flipped while open

- **ID:** PD-07
- **Category:** boundary
- **Risk:** `width="abc"` renders `abcpx` (ignored by CSS), `width="0"`/negative render a collapsed or invalid panel; `disabled` flipping to true while visible leaves an open panel the user cannot dismiss via the trigger.
- **Input that reveals it:** `width` of `0`, `-10`, `NaN`, `"abc"`; set `disabled = true` after opening.
- **Observed current behavior:** `popoverWidth` interpolates any non-keyword value (`bds-popover.tsx:187-191`); `disabled` is checked only in `onBeforeShow` (`:202`) and the arrow guard, so an open popover stays open and still hides normally.
- **Recommended contract:** undecided — validate/clamp the width (and fall back to 320) vs. document passthrough; hide on disable vs. leave open.
- **Contract status:** pending-decision
- **Why it matters:** no validation exists today, so any test would pin an accident.
- **Covered by:** —

---

### PD-08 | Focus is restored even when the hide was vetoed or the popover was already closed

- **ID:** PD-08
- **Category:** race-timing
- **Risk:** Escape pressed on the trigger while the popover is closed, or a hide vetoed by `floatingOptions.onBeforeHide`, still calls `restoreFocusToTrigger()` and moves focus.
- **Input that reveals it:** Escape on the trigger with the popover closed; `onBeforeHide: () => false` then Escape / close button.
- **Observed current behavior:** the trigger Escape binding (`bds-popover.tsx:568-571`) and `closeFromInside()` (`:506-509`) call `hide()` then restore unconditionally; only the document-level handler guards on `isVisible` (`:246`).
- **Recommended contract:** undecided — restore only on a real close vs. always.
- **Contract status:** pending-decision
- **Why it matters:** FM-04/PD-03 pin the restore on a real close; the no-op/veto cases would be asserting current incidental behavior. `KeyboardController` also `preventDefault`s the bound Escape, which can swallow the key from a text-field trigger.
- **Covered by:** —

---

### PD-09 | `aria-describedby` points at a non-existent id; `aria-haspopup` ignores `behavior`

- **ID:** PD-09
- **Category:** component-contract-bypass
- **Risk:** a11y — `subscribe()` sets `aria-describedby="popover-content-"` (empty `el.id` is not nullish, so the `?? 'default'` fallback never applies) but nothing in the panel carries that id, so the reference is dangling; `aria-haspopup="true"` is always written regardless of `behavior` (`menu` / `listbox` / `dialog`), where the ARIA value should match.
- **Input that reveals it:** a popover without an `id`; `behavior="dialog"` / `"listbox"`.
- **Observed current behavior:** `bds-popover.tsx:404-405`; the panel content has no `id` (`:707`).
- **Recommended contract:** undecided — generate a stable id and reference the real content element; map `aria-haspopup` from `behavior`; or deliberately drop `aria-describedby`.
- **Contract status:** pending-decision
- **Why it matters:** conflicts with an existing test — `bds-popover.a11y.spec.ts::Should set ariaDescribedBy on trigger element` asserts `'popover-content-'`, i.e. it encodes the dangling value. Not edited; ruling needed on which side is right.
- **Covered by:** —

---

### PD-10 | `activation="active"` on a focusable trigger opens then immediately closes on a pointer click

- **ID:** PD-10
- **Category:** equivalence
- **Risk:** a mouse click on a focusable trigger fires `focus` (opens via `handleFocus`) then `click` (toggles it closed), so the popover flashes open; `active` mode never sets the `isPointerInteraction` guard that `focus` mode uses.
- **Input that reveals it:** `activation="active"`, press the mouse on a `<button>` trigger in Chrome/Firefox (Safari does not focus buttons on click).
- **Observed current behavior:** `bds-popover.tsx:427-431` registers an unguarded focus handler and a toggling click handler on the same target.
- **Recommended contract:** undecided — a pointer click should open and stay open; the JSDoc ("mouse click or focus") does not say which gesture wins. No in-repo consumer uses `active`.
- **Contract status:** pending-decision
- **Why it matters:** real-browser behavior, not reproducible in mock-doc without simulating the focus-then-click order.
- **Covered by:** —

---

### PD-11 | Enter/Space binding on an input-type trigger, and Space keyup double activation

- **ID:** PD-11
- **Category:** component-contract-bypass
- **Risk:** when the trigger is (or contains) a text input (`ANCHORED_TRIGGERS` includes `input`, `.bds-text-field`), the bound Space/Enter `preventDefault`s typing; on a native `<button>` trigger, Space keydown toggles and the native keyup-click may toggle again.
- **Input that reveals it:** type Space inside a text-field trigger; press and release Space on a `<button>` trigger in a real browser.
- **Observed current behavior:** `setActivateHandler(() => this.toggle())` with default `preventDefault: true` and keydown-only triggers (`bds-popover.tsx:573-575`; `KeyboardController` defaults).
- **Recommended contract:** undecided — which trigger types should be exempt; related to team memory `keyboard-triggered-focus-move-double-activation.md`.
- **Contract status:** pending-decision
- **Why it matters:** needs real-browser verification; mock-doc cannot reproduce keyup-synthesised clicks.
- **Covered by:** —

---

### PD-12 | Footer clicks suppress `bdsClickIn`

- **ID:** PD-12
- **Category:** equivalence
- **Risk:** consumers listening to `bdsClickIn` for all "interaction inside the popover" miss footer actions.
- **Input that reveals it:** click a footer button and listen for `bdsClickIn`.
- **Observed current behavior:** the footer `onClick` stops propagation before the Host handler (`bds-popover.tsx:711`), so `bdsClickIn` is not emitted.
- **Recommended contract:** undecided — the stop exists to avoid `closeOnClick` (FM-40); emitting `bdsClickIn` while still not closing is a separate choice.
- **Contract status:** pending-decision
- **Why it matters:** pins or changes the public event contract.
- **Covered by:** —

---

### PD-13 | `closeOnClick` and `bdsClickOut`/focus-outside closes drop focus to `<body>`

- **ID:** PD-13
- **Category:** component-contract-bypass
- **Risk:** a menu item click with `closeOnClick` hides the popover through `hide()` (`bds-popover.tsx:330`); the mixin blurs the focused panel element and nothing restores focus (unlike the close button and Escape), so keyboard users lose their place.
- **Input that reveals it:** focus an item in the panel, activate it with `closeOnClick: true`.
- **Observed current behavior:** no `restoreFocusToTrigger()` on this route; consumers such as `bds-dropdown`/`bds-select` may refocus themselves.
- **Recommended contract:** undecided — restore focus like the close button, or stay focus-neutral like programmatic/outside closes (PD-01/PD-02, FM-05).
- **Contract status:** pending-decision
- **Why it matters:** an a11y regression risk either way; PD-01/PD-02 rulings were made for other routes only.
- **Covered by:** —

---

### PD-14 | `floatingOptions.placement` is accepted by the type but ignored

- **ID:** PD-14
- **Category:** equivalence
- **Risk:** a consumer sets `floatingOptions={{ placement: 'left' }}` per `FloatingPopoverProp` and the panel stays at `bottom`, because `options` reads only the `placement` prop (`bds-popover.tsx:173`).
- **Input that reveals it:** `floatingOptions = { placement: 'left' }` with no `placement` prop.
- **Observed current behavior:** ignored. Existing `bds-popover.variants.spec.ts::Should apply placement from floatingOptions` and `::Should apply right placement from floatingOptions` only assert that the assigned prop reads back — they pass whatever the component does.
- **Recommended contract:** undecided — honor it as an override, or remove it from `FloatingPopoverProp` (it is `Omit<…, 'placement'>` then re-added).
- **Contract status:** pending-decision
- **Why it matters:** the two existing tests are vacuous and encode no behavior.
- **Covered by:** —

---

### PD-15 | Runtime changes to `placement` / `floatingOptions` while open do not reposition

- **ID:** PD-15
- **Category:** race-timing
- **Risk:** `startAutoUpdate` captures `this.options` once at show time, and `placement` only has a validation watcher, so changes made while open take effect on the next open.
- **Input that reveals it:** open, then change `placement` or `floatingOptions.offset`.
- **Observed current behavior:** `bds-popover.tsx:105-127` (watcher validates only); `anchoredMixin.showElement` passes `this.options` once.
- **Recommended contract:** undecided — reposition live vs. apply on next open.
- **Contract status:** pending-decision
- **Why it matters:** none of today's consumers change these while open, so the cost is hypothetical.
- **Covered by:** —

---

### PD-16 | `slotchange` wiring attaches to the internal `<slot>` and can never be detached

- **ID:** PD-16
- **Category:** race-timing
- **Risk:** `handleSlotChange` registers `show`/`hide` focus/blur listeners on `e.target` — the popover's own `<slot>` element, which is never focused — and `handleSlotUpdate` passes new closures on every call, so `previousTrigger` listeners are unremovable; `disconnectedCallback` also bypasses the mixin's `floatingDisconnect`.
- **Input that reveals it:** populate/replace slotted content after mount; remove the popover.
- **Observed current behavior:** `bds-popover.tsx:362-368`; `anchoredMixin.handleSlotChange`/`detachTriggerListeners`.
- **Recommended contract:** undecided — whether the slot wiring is vestigial (candidate for removal) or intended to re-resolve the trigger. FM-16's "new slot target drives open/close" cannot be exercised by a real DOM event today.
- **Contract status:** pending-decision
- **Why it matters:** a test on FM-16 would drive the handler with a synthetic target and pin behavior with no real-browser equivalent.
- **Covered by:** —

---

### PD-17 | Reconnecting (moving) a popover in the DOM loses all wiring

- **ID:** PD-17
- **Category:** race-timing
- **Risk:** `disconnectedCallback` removes trigger listeners, the keyboard controller and document listeners (`bds-popover.tsx:659-667`) but there is no `connectedCallback`, and wiring happens only in `componentDidLoad`; a popover moved by a framework re-parent stays inert.
- **Input that reveals it:** `parent.appendChild(popover)` to a new location, then click the trigger.
- **Observed current behavior:** no re-subscription on reconnect.
- **Recommended contract:** undecided — support moves (add `connectedCallback` re-wiring) vs. document that popovers must be recreated.
- **Contract status:** pending-decision
- **Why it matters:** React/Vue wrappers can re-parent nodes; no spec disconnects a popover at all (FM-17).
- **Covered by:** —

---

### PD-18 | Header close button label is hard-coded English

- **ID:** PD-18
- **Category:** null-empty
- **Risk:** a11y/i18n — the close `bds-button` renders `label="Close"` with no prop or slot to localize its accessible name (`bds-popover.tsx:696`).
- **Input that reveals it:** `header` + `closable` in a non-English product.
- **Observed current behavior:** fixed string.
- **Recommended contract:** undecided — add a prop (e.g. `closeLabel`) vs. leave as is.
- **Contract status:** pending-decision
- **Why it matters:** the `closable` close button is the only visible UI string the popover owns.
- **Covered by:** —

---

## Existing-suite observations (not edited, per catalog rules)

Tests that pass without protecting the behavior their name claims; any fix to them is a separate explicit step:

| Test | Observation |
| --- | --- |
| `a11y::Should have role tooltip on floating content` | Asserts the default `menu` role. |
| `a11y::Should have popover-trigger part on the trigger element` | Asserts only that a `button` exists. |
| `a11y::Should set ariaDescribedBy on trigger element` | Encodes the dangling `popover-content-` value (PD-09). |
| `basics::Should NOT close when closeOnClickOutside is false and clicking outside` | Dispatches `click`, not `mousedown` — passes even if the option is ignored (FM-25). |
| `events::Should call hidePopover when footer button triggers closeOnClick` | Asserts zero hides and the popover still open (FM-40). |
| `methods::Should emit bdsClose (via bdsClickIn alias) when closePopover() is called` | Listens to `bdsClickIn`; `bdsClose` is never asserted (FM-38). |
| `methods::Should set the part attribute on the new anchor element via setAnchorElement()` | Non-managed popover, so the call is a no-op (FM-44). |
| `variants::Should apply placement from floatingOptions` / `::…right placement…` | Assert the assigned prop reads back (PD-14). |
