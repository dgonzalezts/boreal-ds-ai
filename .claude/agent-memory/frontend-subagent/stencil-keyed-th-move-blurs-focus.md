---
name: stencil-keyed-th-move-blurs-focus
description: Adding a vdom `key` fixes identity-tracking bugs across reorders but does NOT preserve DOM focus by itself — a focused node still blurs when moved via insertBefore, even when it's the exact same node object reused.
metadata:
  type: project
---

Found and fixed while resolving two QA bugs in `bds-table`'s column drag/drop reorder
(`packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`,
EOA-16000 Task 5).

## Finding 1 — `key` alone does not preserve focus across a reorder

Adding `key={col.colKey}` to a keyed vdom child (Stencil's `<th>` in `renderTh`) correctly
fixes "stale DOM node identity" bugs — e.g. a keyboard handler reading `data-col-key` off
`e.target.closest('th')` no longer reads the WRONG column's data after a state-driven
reorder, because Stencil now moves the physical DOM node by logical key instead of
repatching it positionally.

However, this does NOT mean the browser's focus follows the moved node automatically.
Verified via a minimal raw-DOM repro (no framework involved):

```js
const div = document.createElement('div');
const a = document.createElement('button'), b = ..., c = ...;
div.append(a, b, c);
a.focus();               // focusedBefore === true
div.insertBefore(a, c);  // move the SAME node within the SAME parent
// document.activeElement !== a — a fired a real `blur` event, relatedTarget: null
```

Moving an already-connected, focused element via `insertBefore` blurs it, even though it's
the identical DOM node object and never leaves the document. This is standard Chromium
behavior, not a Stencil bug. So: any Stencil component that relies on `key`-based reordering
to keep keyboard focus on a moved element must **explicitly re-focus it after render** —
`key` guarantees node/state identity, not focus continuity.

Pattern used for the fix: record the colKey that had focus in the event handler (a private
field set right before triggering the state change that causes the reorder), then in
`componentDidRender()` check for that pending field, `querySelector` the new handle for that
colKey, call `.focus()`, and clear the field. `componentDidRender` fires after every render,
so the field is consumed exactly once per triggered move.

## Finding 2 — a `key` fix can silently mask a second, independently-reported bug

A second reported bug (pinned column's `<th>` losing its imperatively-set `style.left`
after ANY reorder, because the recompute's dirty-check didn't include `columnOrder` as a
tracked dependency) turned out to **no longer reproduce** once the `key` fix above was
applied alone — confirmed by toggling each fix off independently against the live dev
server. Root cause: without a `key`, Stencil repatches every `<th>` at each array index
positionally on any reorder (even ones whose logical column didn't move), and that
repatch was what cleared the pinned column's inline style. With the `key` fix, Stencil's
keyed diff correctly recognizes the untouched pinned column and never touches it — so the
style is never cleared in that specific repro.

Do not assume this means the second fix is unnecessary, though: the dirty-check gap is
still real per the architecture (offsets should be recomputed whenever `columnOrder`
changes, not only when `pinnedColKeys`/`columns` change by reference) and could still bite
in scenarios the simple repro didn't cover. Fixed anyway, defense-in-depth.

**Practical takeaway for future two-bug QA reports on the same component**: before assuming
two reported bugs are fully independent, test each fix in isolation against the live app
(toggle one off, rebuild, reproduce) — a fix for bug A can accidentally resolve bug B's
literal repro steps as a side effect, which is worth knowing before reporting both as
"independently verified fixed."
