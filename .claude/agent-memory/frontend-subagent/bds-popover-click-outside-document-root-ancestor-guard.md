# `bds-popover` click-outside: the document root must count as "outside" (EOA-19597 T33)

## The bug shape

`bds-popover.handleClickOutside` computes an ancestor guard:

```ts
const clickFellBackToOwnAncestor =
  target !== null && target !== document.body && target.contains(this.el);
```

`document.documentElement.contains(this.el)` is always `true` (every rendered element is inside `<html>`), so any
`mousedown` whose target is the document root — i.e. a click on the page gutter / margin / any point outside the
`<body>` box — was classified as "the click fell back to an ancestor that owns us" and never dismissed. Clicks on a
real outside element (`<h2>`, `<p>`, `<div>`) dismissed normally, which is why the hole survived: it needs a hit test
that lands on `<html>`.

Fix: add `target !== document.documentElement` to the same guard. Nothing else changed.

## Why the ancestor branch exists at all

The popover host is always light-DOM inside its consumer, so a click on the consumer's own chrome (`bds-select`'s
wrapper, a `bds-dropdown` host, the wrapper div around a standalone popover) targets a node that *contains*
`this.el`. That must not dismiss — the same reason `document.body` was already excluded. So the guard is
deliberately "any ancestor except the document shell", and the only correct narrow change is to widen "document
shell" from `{body}` to `{body, documentElement}`. Do **not** delete the branch or invert it to a whitelist: that
would dismiss on every click over the owning component's padding.

## `evaluateFocusOutside` — deliberately NOT changed

It carries the same `active !== document.body && active.contains(this.el)` shape, but has no reachable case:
`document.activeElement` resolves to the focused element, else `document.body`, else `null` — it is
`document.documentElement` only for a document with no body (impossible here) or a pathological `tabindex` on
`<html>`. Unlike the gutter click, the gutter case never reaches this path either: blurring to `<body>` fires no
`focusin`, so `handleFocusOutside` is never invoked; the mousedown handler is the only gutter dismissal path. And
when activeElement *is* body the existing guard already dismisses correctly. Left as-is on purpose — changing it
would be an unverifiable behaviour delta, not a fix.

## Null/undefined target semantics (unchanged)

`const target = (e.composedPath()[0] ?? e.target) as HTMLElement`. For a constructed-but-undispatched
`MouseEvent`, mock-doc returns `composedPath() === []` and `target === null`, so `target` is `null` and the
`target !== null` term short-circuits the guard to `false` → the popover dismisses, exactly as before.
`Node.contains(null)` is legal (nullable WebIDL arg → `false`), so `clickedInsideTrigger` / `clickedInsideFloating`
are safe with a null target. `undefined` cannot reach the guard: the handler runs synchronously during dispatch, so
`e.target` is always a Node there — but note `target !== null` would not catch `undefined` (only `!= null` would),
so a future refactor of that line has to keep the null check explicit.

## Verification without a browser

`@stencil/core/mock-doc` reproduces the premise exactly — `createDocument('<div id="root"><bds-select/></div>')`,
then `doc.documentElement.contains(host) === true`, `doc.documentElement === doc.querySelector('html')`, and a
`mousedown` dispatched on `doc.documentElement` yields `composedPath()[0] === doc.documentElement`. Evaluating the
new predicate against `documentElement` → `false`, `body` → `false`, the `#root` wrapper → `true`, the host →
`true`: the fix lands and the ancestor intent survives. No `bds-popover`/`bds-select`/`bds-date-picker` spec encoded
the old "gutter click keeps it open" behaviour, so the whole suite stayed green untouched.

## Consumer blast radius (checked)

`bds-select`, `bds-date-picker`, `bds-dropdown` (`closeOnClickOutside: true`), and `bds-search-bar` (through its
internal `bds-select`) all render the popover light-DOM inside themselves and all attach the listener (the default
is attach-unless-explicitly-`false`), so each gained exactly one new dismissal input: a mousedown whose target is
`<html>`. `bds-tooltip` does **not** use `bds-popover` (it renders its own floating `<div popover="manual">`), so it
is structurally unaffected despite being in the same test gate. On hide, `bds-select`'s `onAfterHide` runs
`resetValueField()` (no-op when `managed`) + `resetChildren()` — the identical path a regular outside click already
takes.

## QA note

A "click on the gutter" only exercises the fix when the hit-test really lands on `<html>` — a full-bleed app root
div (`#root { min-height: 100vh }`) absorbs the click and, containing the popover, correctly still does *not*
dismiss. Reliable repro: click below the end of the page content, or confirm the target first with
`document.addEventListener('mousedown', e => console.log(e.target.tagName), true)`.
