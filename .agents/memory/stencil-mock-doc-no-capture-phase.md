---
name: stencil-mock-doc-no-capture-phase
description: "mock-doc's dispatchEvent has no capture-before-target ordering — it always fires the dispatch target first, then ancestors — so a capture-phase interception contract cannot be proven under newSpecPage, only in a browser."
---

# mock-doc has no capture phase

`@stencil/core/mock-doc`'s dispatch fires listeners starting at the node `dispatchEvent()` was called on, then walks up via `parentElement`, treating `{ capture: true }` and bubble-phase listeners identically: always target-first, then ancestors, regardless of the flag.

**Consequences:**

- A component that registers a capture-phase listener on an ancestor so it runs *before* a child's own handler cannot be unit-tested for that ordering. In a spec the child's handler runs first. Two real cases: `bds-search-bar` intercepting ArrowDown on its host before `bds-select`'s bubble handler, and `bds-table` stashing `e.shiftKey` on a capture listener before a `bds-checkbox` click.
- Assert the observable outcome broadly (`toHaveBeenCalled()`), not ordering or exact call counts. For the search bar, a closed popover sees two `openPopover()` calls in mock-doc versus one in a browser.
- The ordering contract itself needs a browser pass. Say so in the task write-up instead of claiming coverage the spec cannot have.

**Workaround for tests that only need the ancestor's capture-derived state:** dispatch on a plain DOM ancestor that has no listener of its own (`.closest()` still matches from there), then dispatch again on the real target to drive its own controller. That compensates for the gap; it does not recreate capture ordering.

Related: `stencil-mock-doc-composed-path-populated-on-dispatch.md`, `stencil-mock-doc-no-activeelement-focus-tracking.md`.

**Source:** EOA-19597 T15/T11 (`bds-search-bar` items-mode keyboard specs; the capture-vs-bubble behaviour was confirmed in Chrome and WebKit).
