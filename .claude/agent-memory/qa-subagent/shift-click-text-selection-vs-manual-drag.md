---
name: shift-click-text-selection-vs-manual-drag
description: how to correctly verify a preventDefault fix against native text-selection during shift+click range selection
metadata:
  type: feedback
---

When verifying a fix for "shift+click range selection triggers native browser text-selection," the correct repro is the actual shift+click gesture on the interactive controls themselves (e.g. click checkbox A, then shift+click checkbox B) followed by checking `window.getSelection().toString()` is empty. This is what native browsers do on `shift+mousedown` after a prior click: they extend any selection anchor to the new click point, selecting everything in between, unless the mousedown handler calls `preventDefault()`.

**Don't confuse this with a manual click-and-drag across cell text while holding shift** — that's ordinary browser drag-to-select behavior, unrelated to the shift+click-extend gesture, and will select text regardless of any checkbox-scoped `preventDefault()` fix. It is not a regression if it does.

**How to apply:** for `bds-table` (or similar) shift+click range-select QA, script it as: click element A → `keydown Shift` → click element B → `keyup Shift` → `eval "window.getSelection().toString()"` should be `""`. Do not use `mousedown`/`mousemove`/`mouseup` drag sequences for this specific check.
