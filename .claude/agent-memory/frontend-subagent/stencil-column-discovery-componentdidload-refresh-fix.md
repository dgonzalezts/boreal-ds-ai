---
name: stencil-column-discovery-componentdidload-refresh-fix
description: bds-table's this.el.children is reliably empty inside componentWillLoad in a real browser (lazy-loaded, non-shadow) even for statically-declared children — must re-discover in componentDidLoad too, not rely solely on the later MutationObserver
metadata:
  type: project
---

In `bds-table.tsx`, discovering light-DOM config children (`bds-table-column` / `bds-table-column-group`) via `Array.from(this.el.children)` inside `componentWillLoad()` **always** returns an empty array in a real browser (confirmed 12/12 across every pre-existing playground table, both statically-declared and JS-`appendChild`-populated) — even though `document.readyState === 'complete'` and the full page HTML is already parsed. This is invisible in `@stencil/core/testing`'s `newSpecPage` (mock-doc doesn't replicate the real lazy-loaded custom-element upgrade/slot-relocation timing), so unit tests give false confidence here.

By `componentDidLoad()` time, `this.el.children` is reliably populated (confirmed via `console.log` instrumentation in a real Chromium session). So the original code's `componentWillLoad` query was **always** silently failing, and the table only ever rendered real columns because the `componentDidLoad`-attached `MutationObserver({childList:true})` happened to catch the childre relocation event that Stencil's non-shadow runtime performs sometime between `componentWillLoad` and `componentDidLoad`.

That worked by accident only because every pre-existing playground/story table had at least one *later* childList mutation for the observer to catch (e.g. Task 2/3 stories append a `<template slot="row-detail">` or multiple columns across several ticks). Tables whose children arrive in a single batch with no later mutation (e.g. a table with only statically-declared `<bds-table-column>` children, or a script that does exactly two `appendChild` calls then just sets `.data`) **permanently render an empty header/body** — because by the time `componentDidLoad()` calls `observer.observe(this.el, ...)`, the one-and-only relocation mutation has already happened and can never be retroactively observed.

**Fix:** call the same discovery/refresh routine again as the *first* line of `componentDidLoad()`, before attaching the `MutationObserver`. `componentWillLoad`'s call is still worth keeping (harmless, and correct for any environment where children genuinely are available early), but `componentDidLoad` is the only point empirically guaranteed to see real children — the observer should be reserved for genuinely *later* dynamic changes, not relied on to catch the initial population.

**How to apply:** any future Stencil component doing `Array.from(this.el.children)`-based config discovery in a `shadow: false` component must re-verify in a *real browser* (not just `newSpecPage`), and should treat `componentDidLoad` — not `componentWillLoad` — as the authoritative point where original light-DOM children are guaranteed present. See [[stencil-worktree-missing-dist-dependency]] and [[feedback_slot_relocation_timing]] for related light-DOM timing gotchas in this codebase.

Discovered while implementing EOA-16000 Task 4 (`bds-table-column-group`), when a manual Playwright check of a table with only statically-declared `bds-table-column` children rendered a completely empty `<thead>`/`<tbody>` despite all 2561 Jest/mock-doc unit tests passing.
