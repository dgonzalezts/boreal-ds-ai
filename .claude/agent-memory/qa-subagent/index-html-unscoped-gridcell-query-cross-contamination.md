---
name: index-html-unscoped-gridcell-query-cross-contamination
description: document.querySelectorAll on the accumulated src/index.html playground can match cells from unrelated bds-date-picker scenarios
metadata:
  type: project
---

`src/index.html` accumulates every task's playground scenarios for the life of a plan (per [[feedback_manual_qa_scenarios_persist]]), so by the time of a later task's QA there can be dozens of `bds-date-picker` instances mounted at once (observed: 36 `bds-calendar-grid`s, 59 `bds-popover`s on one page during EOA-17662 Task 34e-1 QA). Every scenario's calendar grid renders into the light DOM even when its own popover is closed/hidden via CSS — nothing is torn down.

**Why this matters:** an `eval` query like `document.querySelectorAll('[role=gridcell]')` filtered by `aria-label` text (e.g. "September 15th") can silently match a cell in a *different*, closed scenario's grid that happens to show the same calendar month with leftover/preset state — producing wildly inconsistent results between two back-to-back queries that look like a flicker/re-render bug but are actually just querying different elements each time.

**How to apply:** always scope DOM assertions to the specific date-picker under test first — `document.querySelector('#dp-scenario-id').querySelectorAll(...)`, never a bare `document.querySelectorAll(...)`. Playwright's `ref`-based click/hover (from a live accessibility-tree snapshot) is naturally scoped correctly since closed popovers aren't in the accessibility tree — only raw `eval`/`querySelectorAll` calls are at risk.
