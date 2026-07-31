---
name: stencil-mutationobserver-retry-for-late-template-content
description: "bds-table applyCellTemplate silently failed forever when React populates <template>.content after first render; fixed with a one-shot MutationObserver retry keyed per column."
metadata:
  type: project
---

**Bug (EOA-16000, Task 3 QA finding):** `applyCellTemplate` in `bds-table.tsx` read `template.content.firstElementChild` synchronously on the cell's very first render. In React, `<template slot="cell">` authored as JSX children never populates `.content` until the consumer's own `useEffect` runs (see `template-element-content-empty-in-react-vue.md`). `bds-table`'s render always won that race, saw `root === null`, and returned with **nothing cached and no retry scheduled** — the cell stayed empty forever unless something unrelated (e.g. a new `data` array reference) forced a full re-render. Vue's `onMounted` happened to win the race, masking the bug there.

**Fix:** when `content.firstElementChild === null`, attach a one-shot `MutationObserver({ childList: true })` on `template.content` (a `DocumentFragment` — observable like any `Node`) via a new private method `watchForLateTemplateContent(col, template)`. On first mutation it disconnects itself and calls `forceUpdate(this)`, so the next `applyCellTemplate` pass picks up the now-populated template. Pending observers are tracked in `private readonly _pendingTemplateContentObservers = new Map<string, MutationObserver>()` keyed by `col.colKey` to avoid double-attaching, and are all disconnected + the map cleared in `disconnectedCallback()` alongside the existing `_columnObserver`/`resizeObserver` cleanup.

Deliberately **no** dev warning added for this case (unlike the sibling `warnEmptyRowDetailTemplateOnce` for `row-detail`) — an empty template on first read is now an expected, self-correcting transient for React-style late population, not necessarily a developer error.

Compare/contrast: `applyRowDetail` (row-detail slot, Task 2) never had this bug because it reads the template lazily on first user expand-click, by which point the framework's mount effect has long since run.

File: `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx` — `applyCellTemplate` (~line 494), new `watchForLateTemplateContent` method, `disconnectedCallback`.

Verified: `stencil build` clean, existing `bds-table.template-cell.spec.ts` (6/6) and full `bds-table` suite (284/284) pass unchanged — those tests only exercise the synchronous/already-populated path, so a dedicated async-race regression test is still needed (testing-subagent follow-up).

See also [[template-content-empty-in-react-vue]] (root cause background), [[forceUpdate-race-fix]] (sibling forceUpdate pattern from the row-detail EOA-16000 fix).
