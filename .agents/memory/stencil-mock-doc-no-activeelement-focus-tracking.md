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
- Patching `focus` to a **non-dispatching** recorder (rather than calling through to the original) avoids recursive focus churn: `bds-text-field`'s host `onFocus` re-focuses its inner `<input>` (`bds-text-field.tsx:416`), so letting the mock dispatch the real `focus` event produces repeated nested `input.focus()` calls.
- Always restore the prototype method and delete the `activeElement` property in a `finally`/`afterEach` — the patch is global and leaks into every later spec in the same file.

## Source

EOA-17662 Task 42 (`bds-date-picker` Escape-key focus return). The component attaches a `KeyboardController` Escape handler that calls `requestAnimationFrame(() => this.bdsInput?.focus())`; the added spec in `bds-date-picker.keyboard.spec.ts` uses the tracker above to assert focus lands on the field's inner `<input>`, not `<body>`.
