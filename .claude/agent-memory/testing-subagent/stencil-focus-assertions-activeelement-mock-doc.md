# Focus assertions in mock-doc: instance spys call through (recursion), `activeElement` is undefined but `body` exists

Three verified facts when asserting focus behavior under `newSpecPage`.

## 1. `jest.spyOn(element, 'focus')` calls through to the real mock `focus()`, which dispatches a bubbling `focus` event — causing recursion

An element whose *host* re-focuses a child `onFocus` (e.g. `bds-text-field`'s Host `onFocus={() => !readOnly && this.el.querySelector('input')?.focus()}`) throws `RangeError` / blows up the call count (observed `1100` calls) when you spy-through `focus` on it or its container. Fix: make the spy a **non-dispatching recorder**:

```ts
const spy = jest.spyOn(element, 'focus').mockImplementation(() => undefined);
```

This is the instance-level analogue of the prototype-level recorder in `.agents/memory/stencil-mock-doc-no-activeelement-focus-tracking.md`. Use it when you only need to know *which* element received focus, not to simulate focus state.

## 2. `document.activeElement` is `undefined`, but `document.body` IS defined

`MockDocument` has no `activeElement` getter (→ `undefined`), but `MockDocument.body` lazily creates and returns a real `<body>` element. The team memory note that `document.body` is also undefined is **inaccurate**.

Consequence inside `bds-popover.evaluateFocusOutside()`: the guard `active !== null && active !== document.body && active.contains(this.el)` does **not** catch `undefined`, so with `activeElement === undefined` it executes `undefined.contains(...)` and **throws**. To exercise the body-fallback path in `handleFocusOutside`, define `activeElement` as `document.body`, not `undefined`:

```ts
Object.defineProperty(document, 'activeElement', { configurable: true, get: () => document.body });
```

That is the real-browser-correct case anyway (a real `activeElement` is never `undefined`).

## 3. Restore `activeElement` in a `finally`

`Object.defineProperty(document, 'activeElement', …)` is global; always `Reflect.deleteProperty(document, 'activeElement')` in `finally` (or restore the prior descriptor) so later specs in the same file see the default `undefined`.

Found writing `bds-popover` focus-restoration + date-picker integration specs (2026-09-28).
