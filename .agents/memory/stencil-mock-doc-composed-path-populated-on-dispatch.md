---
name: stencil-mock-doc-composed-path-populated-on-dispatch
description: "mock-doc assigns ev.target before triggering listeners and composedPath() walks up from it, so a dispatched event always exercises composedPath()[0] — a `?? e.target` fallback is unreachable in tests."
---

# mock-doc `composedPath()` is populated once an event is dispatched

Verified against `@stencil/core@4.42.1` `mock-doc/index.js`:

- `dispatchEvent(currentTarget, ev)` assigns `ev.target = currentTarget` **before** triggering listeners.
- `MockEvent.composedPath()` walks up from `this.target`, pushing `#document` and then `defaultView`.

So a listener always observes a populated path. For a guard written as `(e.composedPath()[0] ?? e.target)`, a dispatched-event test exercises the `composedPath()[0]` branch; the `?? e.target` fallback only occurs for a constructed-but-never-dispatched event and cannot be covered. Do not add "cover the fallback" tests, and do not claim fallback coverage.

**Dispatching on the document shell from a spec:** `bubbles: true` is required and sufficient — mock-doc forwards the `parentElement == null && tagName === 'HTML'` case to `ownerDocument`, so document-level listeners fire. `page.doc.documentElement` is the same object identity the component reads as `document.documentElement`, so identity guards such as `target !== document.documentElement` compare correctly.

Related: `dom-documentelement-contains-always-matches.md`, `stencil-mock-doc-no-capture-phase.md`, `stencil-mock-doc-mouseevent-relatedtarget.md` (`Node.contains(self)` is `true` in mock-doc).

**Source:** EOA-19597 T33 (`bds-popover` gutter-click spec).
