# `newSpecPage` mock-doc Does Not Track Focus (`document.activeElement` / `HTMLElement.focus()`)

## The Gap

Stencil's `@stencil/core/mock-doc` (verified on `4.42.1`) implements `HTMLElement.prototype.focus()` as nothing more than dispatching a bubbling `MockFocusEvent('focus')` (mock-doc `index.js`, `MockElement.focus()`) — it never updates any notion of "the focused element". `MockDocument` has **no `activeElement` getter at all** (only `MockShadowRoot` does, returning `null`), so `document.activeElement` is `undefined` in a `newSpecPage()` spec.

**Correction (2026-09-28):** an earlier revision of this entry also claimed `document.body` is undefined under mock-doc. That is wrong. `document.body` **is** defined — `MockDocument` builds the document element with `head`/`body` eagerly and exposes a real `get body()`; specs freely use `document.body.appendChild(...)`, `document.body.innerHTML = ''`, and compare `document.activeElement === document.body`. Only the *focus-tracking* surface (`document.activeElement`) is absent/`undefined`.

Consequence: `expect(document.activeElement).toBe(someInput)` is meaningless/dead in a spec and will never reflect a real focus move. `element.focus()` is also a no-op for focus state — the only observable side effect is the `focus` event it dispatches.

**Practical trap.** `document.activeElement` is `undefined`, not `null`. A guard written as `active !== null` therefore does **not** catch the mock-doc case (`undefined !== null` is `true`), and a follow-on `active.contains(...)` throws. Focus-restoration and focus-containment code paths must tolerate an `undefined` `activeElement` in spec environments; the established patterns are a local `document.activeElement` installed via `Object.defineProperty` for the duration of the assertion (see `bds-popover-events.spec.ts`'s `focus containment` block), or an instance-level `jest.spyOn(el, 'focus')`. Corollary: with no tracker installed, `document.activeElement !== target` is always `true` after `target.focus()`, so a "focus the target, else focus its first focusable descendant" routine always enters the descendant fallback — which is why a global `activeElement`-updating tracker masks that branch (see `stencil-focus-spy-recursion-and-global-tracker-masking.md`).

## The Workaround

To assert a component returned focus to an element, install a local tracker for the duration of the test:

```ts
const originalFocus = HTMLElement.prototype.focus;
const focusState: { element: Element | null } = { element: null };
HTMLElement.prototype.focus = function (this: HTMLElement) {
  focusState.element = this;
};
Object.defineProperty(document, 'activeElement', { configurable: true, get: () => focusState.element });
try {
  // ...dispatch the key/event under test...
  expect(document.activeElement).toBe(expectedInput);
} finally {
  HTMLElement.prototype.focus = originalFocus;
  Reflect.deleteProperty(document, 'activeElement');
}
```

This mirrors the repo's existing precedent in `src/utils/a11y/keyboard/__test__/focus.spec.ts`, which patches `HTMLElement.prototype.focus` and defines `document.activeElement` via `Object.defineProperty`.

Two gotchas:

- Assigning `this` to a variable trips `@typescript-eslint/no-this-alias`. Either add the `eslint-disable-next-line @typescript-eslint/no-this-alias` directive (as `focus.spec.ts` does) or assign to a member expression of a holder object (`focusState.element = this`) — the latter passes the rule without a disable comment.
- Patching `focus` to a **non-dispatching** recorder (rather than calling through to the original) avoids recursive focus churn from any host-level `onFocus` forwarder, because mock-doc's `focus` event **bubbles** — see "Why the `focus` event bubbles in mock-doc" below. `bds-text-field`'s forwarder since carries a `target === currentTarget` guard, so it no longer recurses, but the general advice stands for other components.
- Always restore the prototype method and delete the `activeElement` property in a `finally`/`afterEach` — the patch is global and leaks into every later spec in the same file.

## Why the `focus` event bubbles in mock-doc (and why real-browser forwarders recurse there)

mock-doc implements `HTMLElement.prototype.focus()` as a dispatch of `MockFocusEvent('focus', { bubbles: true, composed: true })` (`mock-doc/index.cjs`, `MockElement.focus()`). Real browsers dispatch `focus` with `bubbles: false`. So a host-level forwarder written for the browser — the standard "click the container, focus the inner input" pattern — re-enters itself under `newSpecPage`: `input.focus()` → bubbling `focus` reaches the host → host handler calls `input.focus()` again → `RangeError: Maximum call stack size exceeded`.

**The suite stays green.** mock-doc wraps every listener call in `try { … } catch (err) { console.error(err) }`, so the overflow surfaces only as a `console.error` block (plus Jest's own summary of it, so each occurrence prints twice) and never fails an assertion. A passing spec file is not evidence this loop is absent — grep the run output for `Maximum call stack size exceeded`.

**Fix shape (component side):** guard the forwarder so it only acts on a focus whose target *is* the listener's own element — `e.target === e.currentTarget` — which is always true in a real browser (where the handler only ever runs for a genuine host focus) and false for mock-doc's bubbled descendant event. Behaviour in Chrome/Safari/Firefox is unchanged: the host stays `tabindex="-1"`, so clicking container padding or an unassociated label still focuses the host, which still forwards to the inner input. Applied to `bds-text-field` in EOA-19597 T57 (`onFocus={(e: FocusEvent) => e.target === e.currentTarget && !this.readOnly && …}`); verified in headless Chrome that padding/label clicks still land focus on the inner input and that `readOnly` still blocks the forward.

Because `document.activeElement` does not exist under mock-doc, no unit test can assert the real focus move — the guard's browser behaviour has to be confirmed headlessly (a static server over `dist` plus a synthetic click is enough; no `validate:pack`).

## Source

EOA-17662 Task 42 (`bds-date-picker` Escape-key focus return). The component attaches a `KeyboardController` Escape handler that calls `requestAnimationFrame(() => this.bdsInput?.focus())`; the added spec in `bds-date-picker.keyboard.spec.ts` uses the tracker above to assert focus lands on the field's inner `<input>`, not `<body>`.
