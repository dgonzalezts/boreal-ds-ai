---
name: bds-popover-html-target-never-dismisses
description: clicking the bare <html> element (page gutter/margin) never closes any bds-popover — the clickFellBackToOwnAncestor guard treats documentElement as an ancestor hit
metadata:
  type: project
---

`bds-popover.tsx`'s `handleClickOutside` skips dismissal when
`target !== document.body && target.contains(this.el)` (`clickFellBackToOwnAncestor`).
`document.documentElement` (the `<html>` element) satisfies that condition for *every* popover, so a
click that lands on `<html>` — e.g. `document.elementFromPoint(30, 15)` in the left page gutter of the
`src/index.html` playground — leaves the popover open with no error and no visual clue.

Found 2026-10-26 verifying `bds-search-bar` T31: `mousedown`/`mouseup` at (30, 15) left the popover
`visible === true` while the same click on any real element (an `<h2>` or `<p>`) dismissed it.

Practical consequences:

- When scripting "click outside" for QA, click a **real element outside the component** (a sibling
  `<p>`/`<h2>` captured via `getBoundingClientRect()`), never a bare corner coordinate. A coordinate
  click on `<html>` is a false negative for dismissal.
- Clicking a non-focusable outside element also moves focus to `BODY`, so blur-driven paths
  (`listenBlurInput` → `resetValueField`, popover `onAfterHide`) are exercised too — that is what
  "blur by clicking outside" needs to test.
- Candidate fix if anyone picks it up: exclude `document.documentElement` in the same way as
  `document.body`.
