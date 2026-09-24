---
name: playwright-ref-click-focus-side-effect
description: playwright-cli click <ref> pre-focuses the target, which falsely closes popovers when the clicked element removes itself from the DOM
metadata:
  type: feedback
---

**`playwright-cli click <ref>` calls `element.focus()` before dispatching the click. When the clicked element is removed from the DOM as a result of that click, the resulting focus-fallback-to-`<body>` fires a `focusout`, and any focus-outside dismissal logic watching `document` will close the container.**

Observed during EOA-17662 Task 39 (banner close button inside `bds-popover`):

| Interaction | Result |
| --- | --- |
| `playwright-cli click <ref>` | popover **closes** (artifact) |
| `mousemove` → `mousedown` → `mouseup` at coordinates | popover **stays open** (correct, matches real users) |

Trace on the close button:
- Real click: `mousedown` → `focusout(INPUT→BODY)` → `focusin(BUTTON)` → `click`. Focus ends on the button; nothing further fires.
- Ref click: same, **plus** `focusout(BUTTON→null)` ~18ms later, immediately followed by the button's DOM removal → `POPOVER_HIDE`.

**Why the real click is fine:** the browser delivers `focusin` to the button as part of the click, and the button is only removed *after* focus has already landed there. The programmatic path's extra `focus()` pre-step creates an intervening removal-then-blur sequence that never occurs for a human hand.

**How to apply:** never judge a **self-removing control** (close/dismiss buttons, anything that unmounts on click) or any **focus/blur-sensitive** behaviour via `playwright-cli click <ref>`. Use coordinate-level mouse events instead:

```
playwright-cli mousemove <x> <y>
playwright-cli mousedown
playwright-cli mouseup
```

Get the centre from `getBoundingClientRect()` via `--raw eval` first. Refs are still fine for controls that persist across the click (day cells, nav buttons, inputs) — verified: programmatically clicking a calendar day cell inside the same popover keeps it open, because that element doesn't delete itself.

**Related:** this is the same hazard class as [[index-html-unscoped-gridcell-query-cross-contamination]] — a `playwright-cli` abstraction not matching real user interaction, producing a bug report that real manual testing contradicts.

**Generalisable tell:** if a QA finding says "X closes/dismisses something unexpectedly" and the user cannot reproduce it by hand, check whether X removes itself from the DOM on click and whether the ref-click path was used. That combination is this artifact.
