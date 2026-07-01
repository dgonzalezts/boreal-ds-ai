---
name: stencil-mock-doc-mouseevent-relatedtarget
description: Stencil's mock-doc MouseEvent/FocusEvent accept relatedTarget directly in the init dict — no Object.defineProperty workaround needed, unlike real browsers/jsdom
metadata:
  type: feedback
---

Stencil's `newSpecPage` runs on `@stencil/core/mock-doc`, not real jsdom. `MockMouseEvent`
and `MockFocusEvent` (in `@stencil/core/mock-doc/index.js`) both just do
`Object.assign(this, eventInitDict)` in their constructor — every field, including
`relatedTarget`, is a plain writable class field, not a read-only accessor.

**Why:** In real browsers and jsdom, `relatedTarget` is read-only on `MouseEvent`, so tests
normally need `Object.defineProperty(event, 'relatedTarget', { value: el })` after
construction. That workaround is unnecessary — and harmless but redundant — in this project's
Jest environment.

**How to apply:** When a spec needs a `mouseleave`/`mouseenter`/`focusout` event with a specific
`relatedTarget`, just pass it straight into the constructor init dict:

```ts
root.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true, relatedTarget: someElement }));
```

Verified while adding `stayOnHover` guard tests for `bds-tooltip`'s `validateHide` (mouseleave
→ `e.relatedTarget` fix, EOA ticket, 2026-07-01). Also confirmed `Node.contains(self)` returns
`true` in mock-doc (matches real DOM spec) — so a `floatingContent.contains(target) ||
floatingContent === target` guard has an unkillable/dead right-hand branch when `target ===
floatingContent`; do not chase that specific mutation survivor with more tests.
