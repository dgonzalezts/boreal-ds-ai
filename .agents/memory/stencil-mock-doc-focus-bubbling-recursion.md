# mock-doc `focus()` Bubbles — Listener Recursion Never Fails a Suite

`@stencil/core@4.42.1`'s `mock-doc` implements `MockElement.focus()` as

```js
focus(_options) {
  dispatchEvent(this, new MockFocusEvent("focus", { relatedTarget: null, bubbles: true, cancelable: true, composed: true }));
}
```

so **every** `element.focus()` under `newSpecPage` dispatches a bubbling `focus` event. Real browsers do not bubble `focus` (`focusin` does). Any `onFocus` handler that re-focuses a descendant therefore re-enters itself until `RangeError: Maximum call stack size exceeded`.

## Why it stays invisible

`triggerEventListener` wraps each listener call in `try/catch` and routes the error to `console.error(err)` (`mock-doc/index.js`). A stack overflow inside a Stencil listener is swallowed, one line is printed, and the test still passes. A green suite is therefore **no evidence** that a focus forwarder is non-recursive — grep the suite output for `Maximum call stack size exceeded` instead.

Confirmed on `bds-text-field`: the container `onFocus` forwarded to the inner `input`, producing 4 such lines per `bds-date-picker` run (keyboard + basics specs) while all suites stayed green. Fixed under EOA-19597 T57 with the browser-equivalent guard `event.target === event.currentTarget && ...`. The components that hold text fields (`bds-search-bar`, `bds-date-picker`, `bds-select`) are the ones that surfaced it.

## Patterns

- **Guard:** `e.target === e.currentTarget` reproduces the browser contract (the container is the event target only when the container itself was focused). Equivalent in effect to mocking `bubbles: false`.
- **Counting forwards in a spec:** `jest.spyOn(input, 'focus').mockImplementation(() => undefined)` on the element instance. The spy counts the forwarding call without dispatching mock-doc's bubbling event, so a regression fails a clean assertion (`expected 1, received 2`) instead of silently spawning recursion. Without the `mockImplementation`, the spied call still dispatches and re-enters the handler.
- **Regression proof:** dispatch `new Event('focus', { bubbles: true })` from the inner input and assert the spy count is unchanged — this fails when the target guard is removed, and passes when present.
