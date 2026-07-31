---
name: feedback_defer_event_to_componentDidRender
description: Deferring an @Event emit that a listener uses to synchronously query freshly-created DOM — queue it and flush from componentDidRender
metadata:
  type: feedback
---

When a state-changing handler (e.g. a row-expand toggle) needs an `@Event` listener to be able to synchronously `querySelector` DOM that a `ref` callback creates on the *next* render (e.g. cloning a `<template>` into a newly-mounted `<tr>`), do not emit the event at the point the state changes. The `ref` callback runs during vdom patch, which happens strictly before `componentDidRender`, so:

1. Push the event detail onto a private array field instead of emitting.
2. Flush the queue (`array.forEach(emit); array.length = 0` via `.splice`) as the last line of `componentDidRender`.

This guarantees any listener that synchronously queries the DOM inside the event handler finds it, without requiring consumers to defer their own logic with `requestAnimationFrame`. Confirmed via Playwright: pre-fix, a listener on `bdsExpand` querying `[data-row-id]` found nothing on the *first* expansion of a row (found it from the second expansion onward, since the detail row stays mounted); post-fix it's found on every expansion including the first. Existing `newSpecPage` unit tests using `await page.waitForChanges()` after `.click()` were unaffected — that helper already flushes through `componentDidRender`.

Reason for the "why bother" check: **verify with a real browser**, not just `newSpecPage` tests — Stencil's mock-doc test harness doesn't reproduce the render-commit-vs-emit-timing gap that real browser patching does, so this class of bug is invisible to the standard test suite. See [[stencil-worktree-missing-dist-dependency]] and other `bds-table` timing memories for the broader pattern of real-browser-only bugs in this component.
