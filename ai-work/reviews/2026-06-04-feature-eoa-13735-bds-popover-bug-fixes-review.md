# Boreal DS — Code Review Report

**Generated:** 2026-06-04
**Branch:** `feature/EOA-13735-update-components-keyboard-navigation`
**Epics:** EOA-13735 (keyboard navigation) · EOA-13426 (popover fixes) · EOA-13922 (keyboard event validation)
**Base ref:** `main`
**Scope:** `bds-popover` component refactor and bug fixes

---

## Summary

|                     |                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------- |
| **Overall quality** | Good — the new event model, keyboard integration, and focus/blur handling are all well-designed       |
| **Recommendation**  | **Hold for fixes** — 3 critical issues must be addressed before merging                              |
| **Critical**        | 3                                                                                                     |
| **Moderate**        | 3                                                                                                     |
| **Minor**           | 6                                                                                                     |

---

## Acceptance Criteria — Status

| # | Criterion | Status |
|---|-----------|--------|
| 1 | onFocus / onBlur parent selection works correctly | ✅ Implemented |
| 2 | Event-based keyboard interactions work beyond key-based activation | ✅ Implemented |
| 3 | Public `closePopover()` method exposed + unit tests | ✅ Implemented |
| 4 | Keydown (Enter/Space/Escape) invokes full show/hide lifecycle | ✅ Implemented |
| 5 | Works correctly when parent has a text field | ✅ Implemented |
| 6 | Correct accessibility role (`tooltip`) when applicable | ⚠️ Supported via prop, test description incorrect |
| 7 | `ariadescribedby` replaced with `aria-describedby` | ✅ Fixed (syntactically) |
| 8 | Positioning calculated relative to parent consistently | ✅ Fixed |

---

## Critical Findings

### C1 — `aria-expanded` is never updated on open or close

**File:** `bds-popover.tsx:385`
**Severity:** Critical (accessibility regression)

`subscribe()` sets `aria-expanded="false"` on the trigger once at subscription time. Neither `onAfterShow` nor `onAfterHide` updates it. Screen readers and automated accessibility tools will always report the trigger as collapsed, regardless of actual popover state. This violates the ARIA `aria-expanded` contract for disclosure widgets.

```ts
// Current — aria-expanded is set once and never updated
trigger.setAttribute('aria-expanded', 'false');
```

**Fix:** Update `aria-expanded` inside the `onAfterShow` and `onAfterHide` hooks (in `bds-popover.tsx`):

```ts
onAfterShow: () => {
  this.triggerEl?.setAttribute('aria-expanded', 'true');
  this.attachClickOutside();
  this.attachFocusOutside();
  this.emitVisibilityUpdate();
},
onAfterHide: () => {
  this.triggerEl?.setAttribute('aria-expanded', 'false');
  this.detachClickOutside();
  this.detachFocusOutside();
  this.emitVisibilityUpdate();
},
```

**Tests needed:** Add to `bds-popover-a11.spec.ts`:
- Assert `aria-expanded="true"` on the trigger after opening
- Assert `aria-expanded="false"` on the trigger after closing

---

### C2 — `ACTIVE` activation mode leaks event listeners

**File:** `bds-popover.tsx:407-409`
**Severity:** Critical (memory leak)

The `ACTIVE` branch of `subscribe()` registers anonymous arrow functions as event listeners:

```ts
// ❌ Current — anonymous functions cannot be removed
target.addEventListener(EVENTS.Focus, () => this.show());
target.addEventListener(EVENTS.Click, () => this.toggle());
```

`disconnectedCallback()` removes listeners by reference (`handlePointerDown`, `handleFocus`, `handleBlur`, `handleClick`). Because the `ACTIVE` mode listeners are anonymous, they are never removed. This accumulates ghost listeners on every re-mount or `activation` prop change.

**Fix:** The named `handleFocus` and `handleClick` arrow properties already exist and do exactly what is needed — use them:

```ts
if (this.activation === POPOVER_TRIGGER_MODE.ACTIVE) {
  target.addEventListener(EVENTS.Focus, this.handleFocus);
  target.addEventListener(EVENTS.Click, this.handleClick);
  return;
}
```

`disconnectedCallback()` already calls `target.removeEventListener(EVENTS.Focus, this.handleFocus)` and `target.removeEventListener(EVENTS.Click, this.handleClick)`, so cleanup requires no further changes.

---

### C3 — `aria-describedby` references a CSS `part` name, not an element `id`

**File:** `bds-popover.tsx:383`
**Severity:** Critical (accessibility — `aria-describedby` links to nothing)

The acceptance criteria (#7) required fixing the misspelled attribute `ariadescribedby` → `aria-describedby`, which was done. However, the value `"popover-content"` points to nothing in the DOM:

```ts
trigger.setAttribute('aria-describedby', 'popover-content');
```

`aria-describedby` must reference an element's `id` attribute. The popover content `<div>` has `part="popover-content"` — not `id="popover-content"`. The accessibility linkage is syntactically valid but semantically broken: screen readers cannot find the referenced element.

**Fix:** Add an `id` to the content div in `render()`. Scope it to the component instance to avoid ID collisions when multiple popovers are on the same page:

```tsx
// In render() — add id to the content div
<div class="popover-content" id={`popover-content-${this.el.id ?? 'default'}`} tabIndex={-1} part="popover-content">
  <slot onSlotchange={this.handleSlotUpdate}></slot>
</div>
```

```ts
// In subscribe() — reference the scoped id
trigger.setAttribute('aria-describedby', `popover-content-${this.el.id ?? 'default'}`);
```

---

## Moderate Findings

### M1 — `onActivationChange` @Watch adds duplicate event listeners

**File:** `bds-popover.tsx:138-141`
**Severity:** Moderate (bug on runtime prop changes)

When the `activation` prop changes at runtime, `this.subscribe(this.triggerSlot)` is called without first removing the existing listeners. A `FOCUS` → `CLICK` transition will leave orphaned `focus`, `blur`, and `mousedown` handlers on the trigger, causing double event firings.

**Fix:** Extract a `private unsubscribe(target: HTMLElement)` method and call it at the top of `onActivationChange`:

```ts
private unsubscribe(target: HTMLElement): void {
  target.removeEventListener(EVENTS.MouseDown, this.handlePointerDown);
  target.removeEventListener(EVENTS.Focus, this.handleFocus);
  target.removeEventListener(EVENTS.Blur, this.handleBlur);
  target.removeEventListener(EVENTS.Click, this.handleClick);
}

@Watch('activation')
onActivationChange() {
  const target = this.listenTarget || this.triggerEl;
  if (target) this.unsubscribe(target);
  this.subscribe(this.triggerSlot);
}
```

---

### M2 — `bdsOpen` fires at mount with `visible: false`

**File:** `bds-popover.tsx:222-223`
**Severity:** Moderate (API semantic mismatch)

`hooks.mounted` is called inside `showElement()` in `anchoredMixin`, which fires every time the popover shows. However, `emitOpen()` emits `{ element: this.el, visible: this.isVisible }`. At the point `mounted()` fires, `isVisible` has already been set to `true` by `showElement()` — so the payload is correct. The concern is that `bdsClose` is emitted from `hooks.unmounted` which fires inside `hideElement()` — also after `isVisible` is set to `false`, so the payload is also correct.

> After reading the mixin, this finding is **downgraded**: the events fire at the right time with the right `visible` value. No action needed on the semantics. The `visible` payload in both `bdsOpen` and `bdsClose` events correctly reflects the final visibility state.

**Residual concern (nit):** The event names `bdsOpen`/`bdsClose` shadow the component DOM lifecycle hooks from the mixin. Consider documenting in JSDoc that these fire on every show/hide cycle (not only on DOM connect/disconnect).

---

### M3 — `setAnchorElement` test does not set `managed="true"`

**File:** `bds-popover-methods.spec.ts:211-228`
**Severity:** Moderate (test is not testing what it claims)

The test at line 211 calls `root.setAnchorElement(trigger)` but the popover HTML is:

```html
<div><button id="trigger">Open</button><bds-popover>Content</bds-popover></div>
```

The method guards with `if (this.managed === false) return` at line 559, so it exits immediately without doing anything. The assertion `expect(trigger.getAttribute('part')).toBe('popover-trigger')` passes only because the initial DOM subscription (which runs on load and finds the nearest `button`) may have already set the `part` attribute on that same button — not because `setAnchorElement` ran.

**Fix:** Add `managed="true"` to the popover in this test:

```ts
html: `<div><button id="trigger">Open</button><bds-popover managed="true">Content</bds-popover></div>`,
```

---

## Minor Findings

### m1 — `getPlacement` getter violates naming convention

**File:** `bds-popover.tsx:519`

Project memory (`component-accessor-naming-conventions.md`) states: *"Getter accessors must not carry a `get` prefix."* Rename to `resolvedPlacement` (since `placement` is already a prop name) or use `this.placement` directly in the `render()` JSX where `data-placement={this.getPlacement}` appears.

---

### m2 — `canShowArrow` has a redundant `|| false`

**File:** `bds-popover.tsx:512-514`

```ts
// ❌ Current — || false is unreachable
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow || false;
}

// ✅ Fix
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow;
}
```

The same pattern was flagged as NIT-2 in the existing `bds-tooltip` review.

---

### m3 — Spanish inline comments in production code

**File:** `bds-popover.tsx:427, 432`

```ts
// Si vino de un click, ignorar — el click lo maneja handleClick
// Resetear siempre en blur para no contaminar el siguiente ciclo
```

Project CLAUDE.md explicitly prohibits inline implementation comments. If the logic genuinely needs explanation, it should be simplified — not commented. Remove both lines.

---

### m4 — Stale and incorrect JSDoc on `keyboardNavigationByRole`

**File:** `bds-popover.tsx:476-479`

The JSDoc reads *"This function is used to set the focus on the element that is currently being hovered over."* (repeated twice). This was clearly copy-pasted from a different method. The getter returns a role-to-strategy map. Remove the JSDoc block or replace with a one-line description.

---

### m5 — a11y test description says "tooltip" but asserts "menu"

**File:** `bds-popover-a11.spec.ts:34`

```ts
// ❌ Current — description contradicts assertion
it('Should have role tooltip on floating content', async () => {
  expect(popover.getAttribute('role')).toBe('menu');
```

Rename to `'Should have default role "menu" on floating content'`.

---

### m6 — `bdsClose` test title is misleading

**File:** `bds-popover-methods.spec.ts:366`

The test title reads `"Should emit bdsClose (via bdsClickIn alias) when closePopover() is called"`, but the test body adds a listener for `bdsClickIn`, clicks inside the content, then calls `closePopover()`. It is verifying that `bdsClickIn` fires on a content click — not that `bdsClose` fires when `closePopover()` is called. These are separate events. Rename to `"Should emit bdsClickIn when the popover content is clicked"`.

---

## What Is Correct

**Focus/blur race condition handling** — The `isPointerInteraction` flag combined with `requestAnimationFrame` in `handleBlur` is the correct pattern for distinguishing pointer-triggered focus from keyboard focus. This prevents the popover from immediately closing when a user clicks the trigger (mousedown → focus → blur race).

**`mousedown` over `click` for outside detection** — `attachClickOutside` switched from listening to `click` to `mousedown`. This fires before focus changes, preventing the blur and click handlers from racing. Correct and intentional.

**Positioning fix (acceptance criterion #8)** — `handlePosition` now uses `this.triggerSlot` directly instead of `this.triggerSlot.parentElement`. The old `parentElement` fallback anchored the popover to the trigger's container, not to the trigger itself, causing misaligned positioning. Fixed correctly.

**`KeyboardController` usage (acceptance criterion #4)** — `setupKeyboard` correctly passes `() => this.hide()` and `() => this.toggle()` (full lifecycle methods) to the keyboard controller — not raw `hidePopover()`/`showPopover()` calls. All registered hooks execute when a key is pressed.

**`ANCHORED_TRIGGERS` lookup (acceptance criterion #5)** — `subscribe()` searches for the interactive sub-element both as an ancestor (`trigger.closest(...)`) and a descendant (`trigger.querySelector(...)`). This correctly handles the text-field-parent case where the real interactive element is nested inside a custom component wrapper.

**`disconnectedCallback` cleanup** — All named event listeners, the `KeyboardController`, click-outside and focus-outside document listeners, and FloatingUI's auto-update are properly removed. No cleanup gaps found.

**Event system** — The five new events (`bdsOpen`, `bdsClose`, `bdsVisibilityUpdate`, `bdsClickIn`, `bdsClickOut`) are all correctly scoped. `bdsVisibilityUpdate` fires on both open and close via `emitVisibilityUpdate()`; `bdsClickIn`/`bdsClickOut` fire on content and outside clicks respectively.

---

## Action Items Summary

| # | Severity | File | Action |
|---|----------|------|--------|
| 1 | 🔴 Critical | `bds-popover.tsx:209-218` | Update `aria-expanded` in `onAfterShow`/`onAfterHide` hooks |
| 2 | 🔴 Critical | `bds-popover-a11.spec.ts` | Add `aria-expanded` open/close tests |
| 3 | 🔴 Critical | `bds-popover.tsx:407-409` | Replace anonymous lambdas with named handlers in `ACTIVE` mode |
| 4 | 🔴 Critical | `bds-popover.tsx:383`, render | Add scoped `id` to content div; update `aria-describedby` value |
| 5 | 🟡 Moderate | `bds-popover.tsx:138-141` | Add `unsubscribe()` and call it in `onActivationChange` |
| 6 | 🟡 Moderate | `bds-popover-methods.spec.ts:211` | Add `managed="true"` to `setAnchorElement` test |
| 7 | 🔵 Minor | `bds-popover.tsx:519` | Rename `getPlacement` → `resolvedPlacement` or remove |
| 8 | 🔵 Minor | `bds-popover.tsx:512` | Remove `\|\| false` from `canShowArrow` |
| 9 | 🔵 Minor | `bds-popover.tsx:427, 432` | Remove Spanish inline comments |
| 10 | 🔵 Minor | `bds-popover.tsx:476` | Remove stale JSDoc from `keyboardNavigationByRole` |
| 11 | 🔵 Minor | `bds-popover-a11.spec.ts:34` | Fix test description from "tooltip" to "menu" |
| 12 | 🔵 Minor | `bds-popover-methods.spec.ts:366` | Fix misleading `bdsClose` test title |

---

**Result: 6 of 8 acceptance criteria fully met · 2 partially met · 3 critical findings · 3 moderate findings · 6 minor findings**
