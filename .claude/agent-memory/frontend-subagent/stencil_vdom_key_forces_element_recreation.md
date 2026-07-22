---
name: stencil-vdom-key-forces-element-recreation
description: Use a distinct key to force full element teardown/recreate when a <td>/element toggles between imperative ref-appended content and declarative JSX children across renders
metadata:
  type: feedback
---

Stencil's vdom `patch()` only reconciles children it tracked from the previous render's own JSX (`oldVNode.$children$`). If a previous render left an element self-closing (no JSX children) and instead injected content imperatively via a `ref` callback (`el.appendChild(realNode)`), that imperative content is invisible to vdom. On the next render, if the same element now declares real JSX children (e.g. a skeleton `<span>`), Stencil's `addVnodes` path just appends the new children alongside the old imperative ones — it does NOT clear them, producing duplicate/stale content in the DOM.

**Why:** verified directly against `@stencil/core@4.42.1`'s `patch()`/`addVnodes`/`removeVnodes` in `node_modules/.../internal/client/index.js`. `ref` callbacks are queued (`refCallbacksToAttach`) and flushed only after the whole render's children-patch pass completes, so a `ref`-based "clear before append" approach on the *new* branch either runs too late (after `addVnodes` already inserted the sibling) or, if it blanket-clears `innerHTML`, wipes the vdom-inserted content it can't tell apart from the stale imperative content.

**How to apply:** when a single element alternates between "imperative content via ref" and "declarative JSX children" across renders driven by a boolean state (e.g. `loading`), give the element a distinct `key` per branch (e.g. `key={`${col.colKey}-footer-skeleton`}` vs `key={`${col.colKey}-footer`}`). Different keys make `isSameVnode` return false, so Stencil fully destroys the old DOM node (`removeVnodes` → `elm.remove()`, which discards the whole subtree including untracked imperative children) and creates a fresh one via `createElm`, instead of attempting an in-place patch. Applied in `bds-table.tsx`'s `renderFooterCell()` (EOA-15507 Task 5d) to swap between skeleton and real slotted footer content while `loading` toggles.

See also [[stencil-node-relocation-breaks-on-rerender]] — that memory covers the DOM-node-caching side of the same imperative-relocation pattern (`_footerNodes` Map); this one covers the vdom-diffing side.
