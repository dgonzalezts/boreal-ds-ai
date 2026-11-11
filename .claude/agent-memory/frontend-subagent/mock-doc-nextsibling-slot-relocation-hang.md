# mock-doc `nextSibling` + slot relocation can hang `waitForChanges()` forever (EOA-19597 T49)

**Symptom:** under `newSpecPage`, switching a live `bds-search-bar` from `items` mode to `mode="search"` makes
`await page.waitForChanges()` never settle, and a racing `setTimeout(..., 3000)` never fires (a synchronous loop —
`flushAll` in `@stencil/core/internal/testing` spins a promise chain, which starves timers). The slotted-list →
`mode="search"` switch is fine, so it looks component-specific. It is not.

**Root cause (verified):** `putBackInOriginalLocation()` in Stencil's testing runtime (slot-relocation reversal, run
from `removeVnodes` whenever a subtree containing relocated slot children is removed) contains

```js
if (parentElm['s-sr']) { let node = parentElm; while (node = node.nextSibling) { ... } }
```

and `MockNode.prototype.nextSibling` (mock-doc) is

```js
const index = this.parentNode.childNodes.indexOf(this) + 1;
return this.parentNode.childNodes[index] || null;
```

Stencil's testing runtime keeps a *parallel* child list (`__childNodes`) and only patches `nextSibling`/`parentNode`
onto nodes it records as slotted (`patchSlottedNode` → `patchNextSibling`). A node that was never patched falls back
to `MockNode.prototype.nextSibling`, whose `indexOf` returns `-1` because its real position only exists in
`__childNodes`; `-1 + 1 === 0`, so `nextSibling` returns the parent's **first child** instead of `null`. The walk then
cycles `#text → DIV → DIV → DIV → BDS-TYPOGRAPHY → #text → …` over the 5 children of
`.bds-list-menu__content` (the loop starts on the `bds-list-menu` empty-state `bds-typography`, which renders a
`<slot>` and therefore carries `s-sr`), forever. Native DOM cannot produce this: `childNodes`/`parentNode` are always
consistent and `nextSibling` has no index fallback.

**Why `items` mode triggers it and a slotted list does not:** the `items` list (`bds-list-menu` + spacers + window
divs, rendered by the search bar's own vdom) is a descendant of the `bds-select` subtree that gets removed; the
slotted case removes a native `<slot>` instead, with no vdom-owned `bds-list-menu` in the removed subtree — so no
unpatched slot-reference node is walked.

**Diagnosis technique that found it (reusable):** wrap every function *and getter* on the mock-doc prototype chain
(`Object.getPrototypeOf(document.createElement('div'))`) plus the component prototype, count by `Class.member`, and at
a threshold print the top counters **and `new Error().stack`** before throwing — the stack lands inside the loop. A
plain `console.log` after the call never runs. Threshold guard is essential: `jest --testTimeout` cannot fire because
timers are starved.

**Proof it is mock-only:** shimming the getter to `return null` when `parentNode.childNodes.indexOf(this) === -1`
makes the transition complete in one flush with the correct final DOM (`bds-select` gone, `bds-list-menu` gone,
`aria-controls` absent, `aria-autocomplete="none"`, field inside `.bds-search-bar__field-wrap`), and the same
items → `mode="search"` transition was verified in headless Chromium against the built `dist` (302 ms, no page
errors, and switching back to `mode="list"` re-renders the select). Do **not** change production code for this.

**Workaround for a spec that needs the transition:**

```ts
const nextSibling = Object.getOwnPropertyDescriptor(
  Object.getPrototypeOf(document.createElement('div')) as object,
  'nextSibling',
);
```

…then install a getter that returns `null` when the node is absent from `parentNode.childNodes` and otherwise
delegates to the original descriptor's getter (walk the prototype chain until the descriptor is found; restore
afterwards). Keep it local to the spec that needs it — a global `setupFilesAfterEnv` shim would change DOM semantics
for every suite.

Cross-cutting (any light-DOM component with a slot inside a subtree Stencil removes, e.g. `bds-select`'s items list,
`bds-date-picker`'s popover contents) — candidate for team memory.
