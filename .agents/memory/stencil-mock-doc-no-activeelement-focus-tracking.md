# `newSpecPage` mock-doc Does Not Track Focus (`document.activeElement` / `HTMLElement.focus()`)

## The Gap

Stencil's `@stencil/core/mock-doc` (verified on `4.42.1`) implements `HTMLElement.prototype.focus()` as nothing more than dispatching a bubbling `MockFocusEvent('focus')` — it never updates any notion of "the focused element". `MockDocument` has **no `activeElement` getter at all** (only `MockShadowRoot` does, returning `null`), so `document.activeElement` is `undefined` in a `newSpecPage()` spec. Same for `blur()` and `document.body`.

Consequence: `expect(document.activeElement).toBe(someInput)` is meaningless/dead in a spec and will never reflect a real focus move. `element.focus()` is also a no-op for focus state — the only observable side effect is the `focus` event it dispatches.

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
