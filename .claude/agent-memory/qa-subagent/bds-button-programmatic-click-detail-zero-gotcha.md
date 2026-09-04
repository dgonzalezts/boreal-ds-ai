---
name: bds-button-programmatic-click-detail-zero-gotcha
description: bds-button.handleClick ignores any click event with event.detail === 0, so el.click() / dispatchEvent(new MouseEvent('click')) via playwright-cli eval silently no-ops — must use playwright-cli's own click command (real pointer dispatch) instead.
metadata:
  type: project
---

`bds-button.tsx`'s `handleClick` (line ~186) has `if (event.detail === 0) return;` guarding
against synthetic/untrusted clicks — `event.detail` is the browser's native click-count field,
which is `0` for any script-triggered `HTMLElement.click()` or a hand-constructed
`new MouseEvent('click')` (real pointer clicks get `1`, `2`, `3`... for single/double/triple
click). This means any playground/QA automation that does
`playwright-cli eval "el => el.click()"` against a `bds-button` (or any native `<button>` nested
inside one, since the click bubbles into `bds-button`'s own handler) silently does nothing —
`bdsClick` never emits, no error, no console warning.

**Symptom:** clicking a calendar-grid nav button (`bds-calendar-grid`'s Previous/Next, which
are `bds-button`-wrapped) via `eval("el => el.click()")` appears to do nothing — header text
never changes, no console error. Looks exactly like a real regression until you check
`event.detail`.

**Fix / workaround for QA automation:** don't use `eval(...).click()` on anything that is (or
contains) a `bds-button`. Instead:
- Take a `playwright-cli snapshot` to get a `ref=` for the actual button, then
  `playwright-cli click <ref>` — this dispatches a real pointer-driven click with correct
  `detail`.
- If you must trigger via `eval` (e.g. for an element NOT wrapped by `bds-button`, like the
  plain `bds-text-field` container that opens a `bds-date-picker` popover), dispatch
  `new PointerEvent('click', { bubbles: true, detail: 1 })` explicitly rather than
  `el.click()` — setting `detail: 1` bypasses the guard when a real `playwright-cli click` ref
  isn't practical (e.g. no visible/attached elements before a popover opens).

**Also note:** `playwright-cli click <ref>` may fail with `element is outside of the viewport`
against elements that are technically in the DOM but positioned off the visible page (e.g. a
`bds-popover` anchored to a scrolled-out-of-view trigger). Fix: `el.scrollIntoView({block:
'center'})` on the *trigger* element (not the popover) via `eval` first, then re-snapshot for
fresh refs before clicking.

This is distinct from the existing memory note "`bds-button` swallows native `click`" (which
covers `stopPropagation()`/re-emitting `bdsClick`) — that note is about listening for the wrong
event name; this one is about *triggering* the click in the first place.

**Confirmed to generalize beyond `bds-button` itself (EOA-17362, `bds-color-picker` QA):**
`bds-color-picker`'s own trigger container (`.bds-color-picker__container`, a plain `<div
role="group">`, not a `bds-button`) has the same `event.detail === 0` guard on its click-to-open
handler — `container.click()` via `eval` silently leaves `aria-expanded="false"`, while a real
`playwright-cli click <ref>` (or a real Playwright `locator.click()` inside `run-code`) opens it
correctly every time. Treat this as a repo-wide convention on any element with a
click-to-toggle/open trigger, not just `bds-button` — always reach for a real pointer-dispatched
click first when a JS-triggered `.click()` appears to silently no-op, before assuming a
regression.
