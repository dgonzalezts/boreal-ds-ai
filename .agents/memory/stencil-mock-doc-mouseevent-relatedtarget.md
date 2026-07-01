# Stencil `mock-doc` `MouseEvent`/`FocusEvent` Accept `relatedTarget` Directly — No `Object.defineProperty` Workaround Needed

`newSpecPage` runs component specs on `@stencil/core/mock-doc`, not real jsdom. `MockMouseEvent`
and `MockFocusEvent` (in `@stencil/core/mock-doc/index.js`) both implement their constructor as
`Object.assign(this, eventInitDict)` — every field, including `relatedTarget`, ends up as a
plain writable class field rather than a read-only accessor.

**Why this matters:** In real browsers and in jsdom, `relatedTarget` is read-only on
`MouseEvent`, so tests normally need a post-construction patch:

```ts
const event = new MouseEvent('mouseleave', { bubbles: true });
Object.defineProperty(event, 'relatedTarget', { value: someElement });
```

That workaround is unnecessary in this project's Jest specs — it is harmless if present, but
redundant. Pass `relatedTarget` straight into the constructor init dict instead:

```ts
root.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true, relatedTarget: someElement }));
```

**Related fact — `Node.contains(self)` returns `true`:** mock-doc honours the DOM spec here, so
`element.contains(element)` is `true`. A guard written as
`floatingContent.contains(target) || floatingContent === target` has a dead right-hand branch
when `target === floatingContent`, because `contains` alone already covers that case. Do not
chase that specific branch as a surviving mutant — it is structurally unkillable, not a test gap.

Discovered while adding `stayOnHover` guard tests for `bds-tooltip`'s `validateHide()`
(`mouseleave` → `e.relatedTarget` fix, 2026-07-01). See also
`.agents/memory/mouseleave-relatedtarget-vs-target.md` for the underlying component bug this test
was written to cover.
