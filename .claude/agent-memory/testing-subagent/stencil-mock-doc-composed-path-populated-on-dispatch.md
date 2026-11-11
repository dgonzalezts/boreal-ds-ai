# mock-doc `composedPath()` IS populated once an event is dispatched

## The claim to avoid repeating

`bds-popover.handleClickOutside` resolves its click target as
`(e.composedPath()[0] ?? e.target) as HTMLElement`. It is tempting to assume mock-doc leaves `composedPath()`
empty (it does for a *constructed but never dispatched* `MouseEvent`) and that a click-outside test therefore
only ever exercises the `?? e.target` fallback. That is wrong for anything a listener actually sees.

Verified against `@stencil/core@4.42.1` `mock-doc/index.js`:

- `dispatchEvent(currentTarget, ev)` assigns `ev.target = currentTarget` **before** it triggers listeners.
- `MockEvent.composedPath()` walks up from `this.target`, pushing `#document` and then `defaultView`.

So a listener always observes a populated path. Probe result for
`page.doc.documentElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))`:

```
len=3 first=HTML target=HTML firstIsDocumentElement=true firstIsUndefined=false
```

Consequence: a test written against a dispatched event exercises the **`composedPath()[0]` branch**, not the
`?? e.target` fallback. Say so when a task asks which path a test covers; do not claim fallback coverage you
cannot get, and do not add a "cover the fallback" test — it is unreachable through a real dispatch. (The
`event.ts` doc comment in mock-doc also explains the null/empty case: pre-dispatch only.)

## Dispatching on the document shell from a spec

`bubbles: true` is required and sufficient — mock-doc propagation special-cases `parentElement == null &&
tagName === 'HTML'` and forwards to `ownerDocument`, so a `document`-level listener fires:

```ts
page.doc.documentElement.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
page.doc.body.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
```

`page.doc.documentElement` is the *same object identity* the component reads as `document.documentElement`
(`newSpecPage` installs `page.doc` as the global `document`), so identity-sensitive guards such as
`target !== document.documentElement` compare correctly. Verified on `bds-popover` EOA-19598 T33: the spec
`bds-popover.click-outside.spec.ts` fails on exactly one test when the `document.documentElement` term is
removed from the ancestor guard, and passes with it restored.

## Related

- `.claude/agent-memory/frontend-subagent/bds-popover-click-outside-document-root-ancestor-guard.md` — the fix
  side of the same investigation (guard shape, why the ancestor branch must stay, `evaluateFocusOutside` left
  untouched), reached the same `composedPath()[0] === doc.documentElement` conclusion independently.
- `stencil-mock-doc-mouseevent-relatedtarget.md` — `Node.contains(self) === true`, so `x.contains(t) || x === t`
  guards are partly dead code; useful when reasoning about containment branches next to the ancestor guard.
