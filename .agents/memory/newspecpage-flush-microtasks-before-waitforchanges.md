---
name: newspecpage-flush-microtasks-before-waitforchanges
description: "When a @Method()-returned promise's .then callback mutates @State, drain microtasks BEFORE waitForChanges() — the reverse order silently skips the render."
---

When a component exposes an async `@Method()` and its `.then` callback mutates `@State`, a `newSpecPage()` spec must drain the promise microtask queue **before** `page.waitForChanges()`:

```ts
dispatchKey(cell, KEYBOARD.ArrowRight);
dispatchKeyUp(cell, KEYBOARD.ArrowRight);
await flushMicrotasks();      // lets the .then run and write @State
await page.waitForChanges();  // renders the write
```

`waitForChanges()` alone does not flush microtask-deferred renders. Called first, it flushes the render queue before the `.then` has run, so the `@State` write is never rendered and assertions against the new UI fail. The `waitForChanges()`-then-`flushMicrotasks()` order (correct when the state change is synchronous) is **not** equivalent here.

`flushMicrotasks` is exported from `@/utils` (`src/utils/testing/helpers.ts`); it drains the native Promise queue without advancing real or fake timers, so it works under `jest.useFakeTimers()`.

Concrete case: `bds-date-picker`'s `tryHandOffFocus` calls `focusDate(...).then(moved => … this.applyMonthNavigate(...))`, so the expanded window shift happens in a microtask. `bds-date-picker.keyboard.spec.ts` → `shifts the window and closes the sibling picker when the sibling cannot take focus` uses `flushMicrotasks()` before `waitForChanges()`; the synchronous-shift tests (e.g. `basic`'s `advances the displayed month…`) use the reverse order. Introduced by ADR 0017.
