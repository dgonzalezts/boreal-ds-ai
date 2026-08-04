---
name: resize-testing-false-positives-scoping-and-timing
description: two distinct methodology mistakes that produced false-positive bug reports while QA-testing bds-table column resizing across React/Vue playgrounds — colKey collision and drag-timing flakiness
metadata:
  type: project
---

During EOA-16000 Task 6 (`bds-table` column resizing) QA, two separate testing mistakes produced bug reports that did not hold up on re-verification — worth remembering the exact failure signatures so future sessions recognize them as test artifacts, not product bugs.

**1. `document.querySelector('th[data-col-key="x"]')` silently matches the wrong table.** The React/Vue playgrounds (`examples/react-testapp/src/App.tsx`, `examples/vue-testapp/src/App.vue`) each have multiple `<BdsTable>` scenarios on the same page, several reusing the same `colKey` (e.g. two separate "email" columns, one non-resizable in an earlier scenario, one resizable in the resize scenario). An unscoped `querySelector` returns the *first* DOM match, silently landing on the wrong scenario's non-resizable column — which then correctly no-ops on keyboard/pointer resize (it's genuinely not resizable), producing a completely convincing but false "resize is broken" result. Always scope with `bds-table:has(th[data-col-key="anchor-col"][data-resizable]) th[data-col-key="target-col"]` (anchor on a colKey unique to the scenario) before asserting on resize behavior in a multi-scenario playground.

**2. A single `mouse.move → down → move` drag without an intermediate wait occasionally loses the drag in Playwright**, producing a "0px change" result that looks identical to a genuine broken pointer-capture regression. Confirmed by retrying the *exact* same interaction with a `waitForTimeout(50)` between `mouse.down()` and the subsequent `mouse.move()` — it then reliably applies the resize. Before concluding a pointer-drag interaction is broken, retry once with this pacing before reporting.

Both mistakes independently led to reporting two now-retracted bugs ("keyboard resize no-op on first touch in React/Vue" and, more subtly, an apparent pointer-drag failure) that did not reproduce once re-tested with correct scoping/timing. The real bug found and fixed in this same session was genuine: `currentColumnWidthPx()` in `bds-table.tsx` originally measured a `<col>` element (always a zero-size `getBoundingClientRect()` per CSS 2.1 §17.2.1), not the `<th>` — fixed to read the `<th>` with an `effectiveColumnWidth()` fallback.
