---
name: listener-leak-verification-cdp-not-addremove
description: counting addEventListener/removeEventListener patches gives false listener leaks in this repo — removal goes through AbortController; enumerate real listeners with CDP DOMDebugger.getEventListeners instead
metadata:
  type: project
---

Do **not** verify "no listener accumulation" by patching `addEventListener`/`removeEventListener` and diffing counts. `KeyboardController` (used by `bds-list-menu`, `bds-select`, `bds-date-picker`, …) registers listeners with `{ signal }` from an `AbortController` and removes them by calling `signal.abort()` — `removeEventListener` is never called. A patch-based count therefore reports a permanent "+1 keydown, +1 pointerdown per destroyed component" that is not a leak at all (verified 2026-10-26 on `bds-search-bar` items mode: patched counting showed 5 leaked pairs over 5 cycles, real enumeration showed zero).

**Correct method** — enumerate the browser's live listener list over CDP via `playwright-cli run-code --filename=…`:

```js
const client = await page.context().newCDPSession(page);
const { result } = await client.send('Runtime.evaluate', { expression: 'document', objectGroup: 'qa' });
const { listeners } = await client.send('DOMDebugger.getEventListeners', { objectId: result.objectId, depth: -1, pierce: true });
```

Group by `type`, snapshot before/after the interaction cycles, diff. Zero diff = no leak. This counts every registration regardless of how it was removed.

`getEventListeners(el)` (the Chrome DevTools console helper) does **not** exist in `page.evaluate` — it is a DevTools-injected function only.
