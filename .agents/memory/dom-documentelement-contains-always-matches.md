---
name: dom-documentelement-contains-always-matches
description: "document.documentElement.contains(el) is always true, so any 'did the click fall back to an ancestor that owns us?' guard must exclude body AND documentElement — widen the exclusion, never invert the guard."
---

# `document.documentElement.contains(el)` is always `true`

Every rendered element lives inside `<html>`, so an ancestor guard written as `target !== null && target !== document.body && target.contains(this.el)` classifies a click whose hit test lands on the document root (page gutter, margins, any point outside the `<body>` box) as "the click fell back to an ancestor that owns us" — and the overlay never dismisses. Clicks on real outside elements dismiss normally, which is why the hole survives casual testing (EOA-19597 T33, `bds-popover.handleClickOutside`).

**Fix shape:** treat the document shell as `{ body, documentElement }` — add `target !== document.documentElement` beside the existing `body` check.

**Do not invert or delete the ancestor branch.** It exists because the popover is light DOM inside its consumer: a click on the consumer's own chrome (`bds-select`'s wrapper, a `bds-dropdown` host, the wrapper around a standalone popover) targets a node that *contains* `this.el` and must not dismiss. A whitelist rewrite dismisses on every click over the owning component's padding. Widening the exclusion is the only correct narrow change.

**The same predicate elsewhere is not automatically a bug.** `evaluateFocusOutside` carries the same shape but has no reachable document-root case: `activeElement` resolves to the focused element, else `body`, else `null`; a gutter click fires `mousedown`, not `focusin`, so that path is never reached. Left unchanged deliberately — changing it would be an unverifiable behaviour delta, not a fix.

**Verifying in a browser:** confirm the click really targets `<html>` before concluding anything (`document.elementFromPoint(x, y).tagName`, or a capture-phase `mousedown` logger). A full-bleed app root div absorbs the click and correctly still does not dismiss; in the example test apps the gutter is at the **bottom** of the viewport, not the left edge.

**Verifying in a spec:** `page.doc.documentElement` is the same object identity the component reads as `document.documentElement`, and dispatching `new MouseEvent('mousedown', { bubbles: true })` on it reproduces the premise — see `stencil-mock-doc-composed-path-populated-on-dispatch.md`.

Consumers checked: `bds-select`, `bds-date-picker`, `bds-dropdown` and `bds-search-bar` (through its internal `bds-select`) all render the popover light DOM inside themselves and all gain exactly one new dismissal input. `bds-tooltip` renders its own floating `<div popover="manual">` and is structurally unaffected.

Related: `bds-popover-escape-ordering-and-focus-neutral-dismissals.md`, `stencil-mock-doc-mouseevent-relatedtarget.md` (`Node.contains(self)` is `true` in mock-doc).

**Source:** EOA-19597 T33, Chrome and WebKit.
