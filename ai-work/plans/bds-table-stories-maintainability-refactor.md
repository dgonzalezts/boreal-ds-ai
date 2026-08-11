---
ticket: N/A
component: bds-table
status: done
created: 2026-08-05
completed: 2026-08-06
---

# bds-table Storybook stories — maintainability refactor

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

## Context

A documentation review of `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` (cross-referenced against `ai-docs/guidelines/storybook-patterns.md` and `bds-grid.stories.ts` as the cleaner reference implementation) surfaced a class of maintainability issues distinct from content accuracy: duplicated render logic, an inconsistent script-authoring style, JSDoc comments carrying implementation rationale rather than consumer-facing description, and a few event-wiring gaps.

**Already fixed, prior to this plan (informational, not tasks below):**
- All 29 `parameters.docs.source.code` overrides hoisted to top-level `const xyzDocsSource = /* HTML */ \`...\`;` declarations, formatted via Prettier's built-in HTML-embedding pragma instead of hand-typed strings — fixes the single-line/multi-line inconsistency across the file, verified via a whitespace-normalized diff against the pre-change file (zero content loss) plus ESLint.
- Shared `uid(prefix)` helper extracted, replacing 7 duplicated `` `x-${Math.random().toString(36).slice(2, 9)}` `` call sites.
- `ai-docs/guidelines/storybook-patterns.md` and `.agents/skills/documentation-knowledge/SKILL.md` updated with the `/* HTML */`-pragma + top-level-hoist convention (so future components follow it without rediscovering it) and with `ifDefined` documented as a sanctioned alternative to `value || nothing`.

**What this plan addresses:** the remaining findings that require touching story bodies, not just the `docs.source.code` strings — safe to defer independently since none of them affect currently-shipped documentation content, only its maintainability.

**Goal:** Reduce duplicated/drift-prone code in `bds-table.stories.ts` and align its script/JSDoc style with the rest of the codebase, without changing any documented behavior or removing any `docs.source.code` override that's load-bearing (i.e. shows a JS-only prop, an event-listener contract, or hides a Storybook-only workaround — see the guideline section above for why these can't simply be deleted).

**Non-goals:** removing `docs.source.code` overrides wholesale (already evaluated and rejected — see conversation history / the guideline doc); adopting the `unsafeHTML`-based single-template idea (unverified whether embedded `<script>` tags execute through it; would need its own spike before being considered).

---

## Task 1 — Shared logic constants between `docs.source.code` and live `render` scripts

**Problem:** ~15 stories independently write the *same* behavioral JS twice — once inside the hoisted `xyzDocsSource` template's `<script>` block, once inside the story's live `render`'s embedded `<script>`. Today nothing keeps these in sync except manual discipline; this is the exact bug class that shipped once already this session (`WithColumnVisibilityDropdown`'s live script broke while its `docs.source.code` string kept showing the old, working version, undetected until manual QA).

**Fix:** for each affected story, extract the shared JS logic (formatter functions, event listeners, the actual behavioral wiring — not the surrounding IIFE/`componentOnReady()`/id-selection boilerplate, which legitimately differs between the two contexts) into one `const xyzLogic = \`...\`;` string, interpolated into both the docs source template and the live render's script.

**Candidates** (stories with independently-duplicated script logic beyond a single `data = [...]` assignment): `RowClickSelection`, `WithConditionalSelection`, `WithColumnVisibilityDropdown`, `ReorderableColumns`, `ResizableColumns`, `ResizableColumnsVirtualized`, `ResizableRightPinnedColumn`, `RowDetail`, `RowDetailVirtualized`, `WithFilterDrawer`, `BulkDeleteWithUndo`, `BulkEdit`, `BulkCustomAction`, `WithActionsColumn`, `WithAddRow`, `WithServerSideMode`.

**Acceptance criteria:**
- Each candidate story's live behavior is unchanged (verified manually, not just statically).
- The shared logic string appears once per story, referenced from both places.
- No `docs.source.code` override is removed or altered in what it documents — only how its script content is sourced.

**Manual test:** Run `pnpm dev:docs`. For each candidate story, exercise its documented interaction (open dropdown/drawer/dialog, edit, delete, sort, reorder, resize, expand a row) and confirm behavior matches pre-refactor. Then open the Docs panel's "Show code" for the same story and confirm the displayed script still matches what actually runs. Pass: no regressions, snippet accurately reflects live behavior for every candidate.

**Executor:** documentation-subagent

---

## Task 2 — Extract a generalized render helper for single-feature column demos

**Problem:** `WithPinnedColumn`, `GroupedColumns`, `GroupedColumnsWithSizing`, `ReorderableColumns`, `ResizableColumns`, `ResizableColumnsVirtualized`, and `ResizableRightPinnedColumn` each write a fully bespoke `render:` — table scaffolding, `<style>${iconStyles}</style>` wrapper, and `<script>(function(){...})();</script>` IIFE — that differs from its neighbors only in which `bds-table-column` attributes are set and what small script runs afterward. `bds-grid.stories.ts`'s `renderGrid(args, items)` + `createGridItem(...)` split (one generic container renderer + a small per-story item factory) is the precedent to follow.

**Fix:** introduce a shared `renderColumnDemoTable(tableId, columns, options)`-shaped helper (exact signature TBD during implementation — should accept the column list, optional event bindings, and an optional post-render script) that the seven candidate stories call into, replacing their bespoke `render:` bodies.

**Acceptance criteria:**
- All seven stories' rendered output (DOM structure, ids, data) is unchanged.
- Each story's `render:` shrinks to a call into the shared helper plus its column-specific config.
- No behavior change to pinning, grouping, reordering, or resizing.

**Manual test:** Run `pnpm dev:docs`. For each of the seven stories, confirm the Canvas renders identically to before (compare against a screenshot or the pre-refactor branch if needed) and that the feature-specific interaction still works (drag to reorder, drag to resize, scroll to see pinned columns stick, etc.). Pass: no visual or functional regression in any of the seven.

**Executor:** documentation-subagent

**Outcome (2026-08-06): evaluated, no change made.** The 7 candidate stories are structurally heterogeneous — flat vs. grouped columns, present vs. absent event bindings, hardcoded vs. generated data, differing host attributes — in exactly the ways this task's own write-up anticipated. A `renderColumnDemoTable`-style helper covering all of it would need enough optional parameters to become a wider surface than the code it replaces. The fallback idea (wrapping just the shared `<style>${iconStyles}</style>` line) was also rejected: `iconStyles` is used at 35 call sites across the whole file, not just these 7, and several of those other sites interpolate additional CSS after it — extracting a helper for only 7 of 35 identical call sites would create a visible inconsistency rather than remove one. No files touched. If a file-wide `iconStyles` wrapper is still wanted, it should be scoped as its own task covering all 35 sites, not folded into this one.

---

## Task 3 — Normalize embedded `<script>` blocks to ES6 (arrow functions, `const`/`let`)

**Problem:** Some live-render scripts use verbose ES5 `function () {}` syntax (`RowClickSelection`, `RowDetail`, `RowDetailVirtualized`, `WithActionsColumn`) while most of the file already uses arrow functions and `const`/`let` throughout. There's no browser-compatibility reason for the ES5 style — Storybook's target browsers already support ES6+, and the majority of scripts in this same file already assume it.

**Fix:** rewrite the ES5 blocks to match the file's dominant ES6 style. Purely mechanical — same logic, different syntax.

**Acceptance criteria:** no behavior change; every rewritten script still executes identically.

**Manual test:** Run `pnpm dev:docs`. Exercise `RowClickSelection`, `RowDetail`, `RowDetailVirtualized`, and `WithActionsColumn`'s documented interactions (row expand, formatter-rendered buttons, dispatched row actions) and confirm no console errors and identical behavior to before.

**Executor:** documentation-subagent

**Outcome (2026-08-06): done, scope relocated by Task 1.** The 4 named stories' own `render:` bodies were already ES6 (Task 1's shared-logic extraction replaced their inline scripts with references to top-level `const xyzLogic` strings). The actual ES5 `function name() {}` declarations had moved into those extracted constants instead: `rowClickSelectionLogic` (`createViewButton`, `updateRowDetail`), `rowDetailPopulateLogic` (`populateOrderHistory`, shared by `RowDetail` and `RowDetailVirtualized`), `withActionsColumnLogic` (`makeActionButton`, `renderRowActions`, `removeRowById`). Converted all 6 to `const name = (...) => {...}` (arrow-expression body for the one single-statement case, `removeRowById`), matching the file's dominant style. Applied directly (small, mechanical, fully diagnosed — no subagent dispatch needed). Verified via `pnpm --filter @telesign/boreal-docs exec eslint` (clean, zero warnings). The IIFE `(function () { ... })();` wrapper used at the top of nearly every story's live-render script was deliberately left untouched — confirmed (during Task 2's evaluation) to be the file's established convention across ~30+ stories, not an ES5 holdover specific to these 4.

**Manual test result: PASS (2026-08-06, `table-task3-qa`).** All 4 stories exercised live in the browser: `RowClickSelection` (row select, expand + `updateRowDetail` detail text, View button → console log via `createViewButton`), `RowDetail` and `RowDetailVirtualized` (both populate order-history correctly via `populateOrderHistory`), `WithActionsColumn` (Edit/Duplicate/Delete all dispatch and update the results text correctly, Delete actually removes the row via `removeRowById`). Zero new console errors on any of the 4 — only pre-existing, unrelated noise (favicon 404, icon-font CORS block, Lit dev-mode warnings). Task 3 fully closed.

---

## Task 4 — Trim JSDoc comments to consumer-facing description only

**Problem:** Several story JSDoc blocks (`WithPinnedColumn`, `ResizableColumns`, `RowDetailVirtualized`, `ReorderableColumns`, and others) run 5–8 dense sentences carrying implementation rationale (sticky-offset recompute internals, why hover-gating was rejected for touch, throttle-sharing details) that reads as engineering rationale rather than what a consumer needs to decide whether/how to use the feature. `bds-grid.stories.ts`'s stories stay to 1–2 sentences; that's the target style.

**Fix:** for each verbose JSDoc, keep the lead sentence(s) describing what the story demonstrates and how to interact with it; move or drop sentences that only explain *why* an internal implementation choice was made and don't change how a consumer uses the prop.

**Acceptance criteria:** every story keeps a JSDoc (still required by `storybook-patterns.md`); no story's Docs-panel description loses information a consumer actually needs to use the feature correctly (e.g. keep "the ID column is pinnable but not sortable" since that's user-relevant; drop "mirrors the throttled recompute path pinning already uses" since that's not).

**Outcome (2026-08-06): done, with a corrected understanding of what this task actually affects.** A first pass trimmed only the rationale clauses from 7 stories, keeping full behavior-contract prose (prop names, event names, interaction steps). The user then asked for a stricter standard — general description only, no attribute/event names, no step-by-step instructions, no internal mechanism explanations — and all 42 story JSDoc blocks were rewritten to one short sentence each (e.g. `WithSelection`: "Row selection with a checkbox column, including range selection." — down from a 2-paragraph block naming `selectable`, `bdsSelect`, and the shift-click/anchor-reset mechanics).

**Important correction discovered during QA:** `bds-table.stories.ts`'s `meta` has no `tags: ['autodocs']`, and `bds-table.mdx` embeds every story via `<Canvas of={...}>` only — zero `<Description of={...}/>` blocks. Per `ai-docs/guidelines/storybook-patterns.md`'s own "Canvas blocks" section, `<Description>` is the explicit, opt-in mechanism that surfaces a story's JSDoc in the rendered Docs page; `<Canvas>` alone never does. Confirmed independently (grep for both signals) — **the JSDoc text in this file was never rendered anywhere in bds-table's actual published documentation**, before or after this task. `bds-table.mdx`'s own hand-written prose above each `<Canvas>` block is the real, unrelated, untouched published description.

**Decision (user, 2026-08-06):** keep the JSDoc trim as in-repo comment cleanup only — still a legitimate readability win for anyone editing this file directly (matches this repo's own no-verbose-comments philosophy) — and leave `bds-table.mdx` untouched; no `<Description>` blocks added. No manual browser test applies to this task as a result (there is nothing rendered to check). Verified via `pnpm --filter @telesign/boreal-docs exec eslint` (clean) and a scripted check confirming all 42 story exports still have a JSDoc immediately above them.

**Manual test:** Run `pnpm dev:docs`, open each trimmed story's Docs page, and read the rendered description — confirm it's still accurate and sufficient to understand the demonstrated feature at a glance.

**Executor:** documentation-subagent

---

## Task 5 — Wire missing action-logger events on interactive columns

**Problem:** A few stories declare an interactive column (`sortable`, `reorderable`, `resizable`) without binding its corresponding event (`@bdsSort`, `@bdsColumnReorder`, `@bdsColumnResize`) to the shared `args.bdsX?.(...)` action logger — e.g. `WithPinnedColumn`'s `sortable` Name column never wires `@bdsSort`. The feature still works for the end user; only the Storybook Actions panel silently doesn't log it, which is inconsistent with how other stories in the same file handle the same event.

**Fix:** audit every story for a column feature (`sortable`/`reorderable`/`resizable`/`pinnable`) and confirm the matching event is bound to its `args.bdsX` logger consistent with sibling stories; add any missing bindings.

**Acceptance criteria:** every interactive column feature demonstrated in a story logs its corresponding event in the Actions panel.

**Manual test:** Run `pnpm dev:docs`. For each story touched, open the Actions panel, trigger the feature (click to sort, drag to reorder, drag to resize), and confirm an action log entry appears.

**Executor:** documentation-subagent

**Outcome (2026-08-06): done.** Audited every `sortable`/`reorderable`/`resizable` column across the file (`pinnable` has no corresponding event — confirmed via `bds-table.tsx`'s `@Event()` list, so it was excluded from the audit). Found 4 stories with an unwired `sortable` column: `WithPinnedColumn`, `GroupedColumns`, `ReorderableColumns` (already had `@bdsColumnReorder`, was missing `@bdsSort`), and `WithLoadingState` (also required promoting its `render: () =>` to `render: args =>` to get access to the args logger). Added `@bdsSort=${(e) => args.bdsSort?.(e.detail)}` to all 4, matching the existing pattern used elsewhere. `resizable` columns (`ResizableColumns`, `ResizableColumnsVirtualized`, `ResizableRightPinnedColumn`) were already correctly wired — no gap found there. Verified via `pnpm --filter @telesign/boreal-docs exec eslint` (clean).

**Manual test result: PASS (2026-08-06, `table-task5-qa`).** All 4 stories exercised live: clicking each Name/City header logged the expected `bdsSort: { colKey, direction }` payload in the Actions panel and rows visibly re-sorted. `ReorderableColumns`'s pre-existing `bdsColumnReorder` wiring was independently confirmed still intact (mouse-drag simulation doesn't trigger `bds-table`'s native HTML5 drag-and-drop in headless Chromium — QA worked around it with synthetic `DragEvent`s dispatched directly). No regressions, no new console errors.

---

## Task 6 — Fix "No accessible name found" console warning on action-column buttons

**Problem:** `WithActionsColumn`'s `makeActionButton` helper (both the docs-source string and the live render script) sets `btn.setAttribute('aria-label', label)` on the button host itself. `bds-button`'s own accessible-name check (`bds-button.tsx` `checkAccessibleName`) only reads three things: the `label` **prop**, visible default-slot text, or `aria-label`/`aria-labelledby` on the **icon slot's child element** — `aria-label` on the host satisfies none of them, so every icon-only action button (Edit/Duplicate/Delete) logs `[BorealDS Button] No accessible name found...` on every render.

**Fix:** change `btn.setAttribute('aria-label', label)` to `btn.setAttribute('label', label)` in both occurrences (the docs-source template and the live render script). This is `bds-button`'s own blessed pattern for icon-only buttons — the component logs a matching `console.info` confirming correct usage once `label` is set, instead of the `console.warn`.

**Acceptance criteria:** no `[BorealDS Button] No accessible name found` warning anywhere in `WithActionsColumn`'s console output; the three action buttons keep their existing tooltips/accessible names (Edit row / Duplicate row / Delete row).

**Manual test:** Run `pnpm dev:docs`, open `WithActionsColumn`, open the browser console, confirm zero `No accessible name found` warnings (a `console.info` "Icon-only button detected" message per button is expected and fine). Confirm the three action buttons still work (Edit/Duplicate log to the results text, Delete removes the row).

**Executor:** (none — fixed directly, mechanical two-line change already diagnosed)

---

## Task 7 — Fix `bds-table`'s own internal toolbar buttons' accessible-name bug

**Problem:** `bds-table.tsx` (`renderToolbarRight`, ~lines 1988 and 1995) renders its internal Filter and Column-visibility toolbar buttons with `aria-label="Filter"` / `aria-label="Column visibility"` set directly on the `<bds-button>` host. This is the same anti-pattern fixed in Task 6, but in the component itself rather than a story: `bds-button`'s `checkAccessibleName` only reads the `label` **prop**, default-slot text, or `aria-label`/`aria-labelledby` on the icon slot's child — an `aria-label` attribute on the host satisfies none of them. This fires `[BorealDS Button] No accessible name found` on every render of a `filterable`/`columnLayoutToggle` table, in Storybook and in real consumer usage alike.

**Why this is bigger than a 2-line fix:** `bds-button`'s `label` prop is not reflected back to the host's `aria-label` attribute (`bds-button.tsx:251` sets `aria-label={this.label || undefined}` only on the button's own internal native `<button>` element, in Light DOM — `bds-button` has no `shadow: true`). So switching to `label=` (the correct fix) means the host custom element itself no longer carries a directly-queryable `aria-label` attribute, which breaks:

1. `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.toolbar.spec.ts` — 11 existing assertions query `bds-button[aria-label="Filter"]` / `bds-button[aria-label="Column visibility"]` at the host level; all need updating to either assert on the `label` prop/attribute directly, or query the descendant native button (`bds-button button[aria-label="..."]`, valid since `bds-button` is Light DOM).
2. `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` — `WithColumnVisibilityDropdown`'s 4 occurrences (docs-source string + live render) of `table.querySelector('bds-button[aria-label="Column visibility"]')` need the same selector update to keep finding the real button.

**Fix:**
- `bds-table.tsx`: change both `aria-label="Filter"` → `label="Filter"` and `aria-label="Column visibility"` → `label="Column visibility"`.
- `bds-table.toolbar.spec.ts`: update all 11 assertions to match the new query shape.
- `bds-table.stories.ts`: update all 4 `querySelector` calls in `WithColumnVisibilityDropdown` to `bds-button button[aria-label="Column visibility"]`.

**Acceptance criteria:**
- Zero `[BorealDS Button] No accessible name found` warnings from `bds-table`'s own toolbar, in any story with `filterable`/`columnLayoutToggle` set.
- All existing `bds-table.toolbar.spec.ts` tests pass (updated, not skipped).
- `WithColumnVisibilityDropdown` still opens/anchors/refocuses correctly (this story's popover-anchoring logic depends on finding this exact button).
- Coverage/mutation gates unaffected (per `.agents/skills/testing-knowledge`'s two-phase gate) — this is a query-target change, not new logic, so no new tests should be needed, just updated selectors.

**Manual test:** Run `pnpm --filter @telesign/boreal-web-components test` (or the component's spec command) and confirm `bds-table.toolbar.spec.ts` passes. Then run `pnpm dev:docs`, open any story with `filterable`/`columnLayoutToggle` (e.g. `WithFilterDrawer`, `WithColumnVisibilityDropdown`), confirm zero accessible-name warnings in the console, and confirm `WithColumnVisibilityDropdown`'s popover still opens/closes/refocuses correctly (mouse click, and the existing Enter/Space keyboard path).

**Executor:** frontend-subagent (component fix), then testing-subagent (test assertion updates), then documentation-subagent (story selector updates) — three sequential, narrow dispatches given each touches a different specialist's file.

---

## Task 8 — Fix `bds-pagination`'s own accessible-name bug on its 4 nav buttons

**Problem:** Same anti-pattern as Tasks 6 and 7, found in a third, unrelated component: `bds-pagination.tsx`'s `getPaginationControls()` (~lines 421-455) renders its First/Previous/Next/Last-page icon-only buttons with `aria-label="Go to first page"` etc. set directly on the `<bds-button>` host — which `bds-button`'s accessible-name check ignores. Worse, the icon `<i>` children aren't even given `slot="icon"` (they're plain unslotted children), so they don't even reach the icon slot the check would otherwise recognize. Since `bds-pagination` renders on nearly every `bds-table` story via `slot="paginator"`, this is why the warning survived a full dev-server restart after Tasks 6/7 — it isn't a caching issue, it's this separate, previously-undiscovered bug.

**Fix, in `bds-pagination.tsx`:**
- Change all 4 `aria-label="Go to ..."` → `label="Go to ..."` on the `<bds-button>` elements.
- Add `slot="icon"` and `aria-hidden="true"` to each button's `<i>` icon child, matching the established convention already used elsewhere in this codebase (e.g. `bds-table.tsx`'s own toolbar buttons).

**Test impact:** 21 existing assertions across three spec files query `bds-button[aria-label="Go to ..."]` at the host level and will break:
- `bds-pagination.basics.spec.ts` — 9 occurrences
- `bds-pagination.events.spec.ts` — 10 occurrences
- `bds-pagination.a11y.spec.ts` — 2 occurrences

Update all to the new `label`-based query, following whatever convention `testing-subagent` finds already established elsewhere in this codebase for the same kind of `bds-button` host-attribute assertion (Task 7's test fix already surfaced one: querying `bds-button[label="..."]` directly on the host, since `bds-button` itself isn't a registered/hydrated child in these `newSpecPage` tests).

**Acceptance criteria:**
- Zero `[BorealDS Button] No accessible name found` warnings from `bds-pagination`'s own nav buttons, in any story using pagination.
- All `bds-pagination` tests pass (updated, not skipped).
- No visual/functional change to pagination — same icons, same click behavior, same disabled states.

**Manual test:** Run the component test suite and confirm all `bds-pagination` spec files pass. Then, in the browser (after a dev-server restart, since this is a component-source change), open any `bds-table` story with a paginator (e.g. `WithPagination`, `WithRowsPagination`) and confirm zero accessible-name warnings and that pagination navigation still works (first/prev/next/last, disabled states at boundaries).

**Executor:** frontend-subagent (component fix), then testing-subagent (test assertion updates).

---

## Notes on sequencing

Tasks 1–2 are the highest-value, since they remove actual duplicated logic (drift risk); Tasks 3–5 are lower-risk polish. Recommend executing in order, with a confirmation checkpoint after each task per `.agents/rules/plan-execution.md` — do not batch multiple tasks into one commit given the file's history of subtle regressions from seemingly-safe mechanical changes this session (the size-inflation surprise, the indentation bug) and in the prior QA-driven regression (`WithColumnVisibilityDropdown`'s keyboard-nav fix breaking click-to-open entirely).
