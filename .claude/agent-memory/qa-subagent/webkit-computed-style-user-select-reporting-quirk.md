---
name: webkit-computed-style-user-select-reporting-quirk
description: getComputedStyle(el).userSelect returns undefined and .webkitUserSelect misreports "text" in Playwright's WebKit driver even when user-select:none is genuinely applied and enforced — verify with a real mouse-drag selection test, not computed-style reads, for this specific property in WebKit
metadata:
  type: project
---

In `playwright-cli --browser=webkit`, reading `getComputedStyle(el).userSelect` on an element styled with plain `user-select: none;` (no vendor prefix in the source SCSS) returns `undefined` — the property is absent from the returned `CSSStyleDeclaration`-like object entirely. Reading `.webkitUserSelect` / `getPropertyValue('-webkit-user-select')` instead returns `"text"` (i.e. selectable), which looks like a real cross-engine styling bug for `bds-calendar-grid`.

It is NOT a real bug: a genuine mouse-down-drag-mouse-up across the element followed by `window.getSelection().toString()` returned an empty string — no text was actually selectable. The browser correctly enforces `user-select: none`; only the devtools-style computed-style property reporting is unreliable for this specific property in this WebKit automation path.

**Why:** Likely a Playwright WebKit driver / JSCore binding quirk in how `-webkit-user-select` is exposed via `getComputedStyle`, not an actual rendering engine behavior. Not confirmed against a bug tracker, just empirically reproduced during EOA-16692 Task 10 cross-browser QA.

**How to apply:** Never conclude a `user-select` regression in WebKit from `getComputedStyle` alone. Always confirm with a real interaction: `mousemove` to one edge → `mousedown` → `mousemove` to the other edge → `mouseup` → read `window.getSelection().toString()` and assert it's empty. Reserve this technique for any future WebKit QA pass that needs to verify `user-select: none` (or generally distrust WebKit-driver computed-style reads for other vendor-prefixed-adjacent properties without a behavioral cross-check).
