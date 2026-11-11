---
name: bds-popover-test-harness-patterns
description: Working mock-doc patterns for bds-popover specs — remove() fires disconnectedCallback, blur/focus-outside need defined activeElement plus rAF settle, floatingContent is the host
metadata:
  type: reference
---

- `popover.remove()` runs the component's `disconnectedCallback` in `newSpecPage`; the override skips the mixin's `hide()`, so `isVisible` stays true after removal and leaked document listeners are observable as stray `bdsClickOut`/`hide` calls.
- `floatingContent` is the `<bds-popover>` host itself (`ref` on `<Host>`), so `document.activeElement = host` counts as "inside floating".
- Blur/focus-outside paths: define `document.activeElement` via `Object.defineProperty` (delete in `finally`), then await 3 `requestAnimationFrame`s (the body case schedules a second frame).
- Spy-prove "no deferred work scheduled while closed" with `jest.spyOn(global, 'requestAnimationFrame')` and a direct private-handler call.
- Instance members (`handlePosition`, `setArrowPosition`, `updatePosition`, `subscribe`) are reachable through a typed `rootInstance as unknown as {...}` cast; `jest.spyOn(instance, 'updatePosition').mockResolvedValue(undefined)` stops the real positioning engine.
